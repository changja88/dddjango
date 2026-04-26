# Django Ninja - Profile Image Upload API

## Project Structure

```
users/
    __init__.py
    models.py
    schemas.py
    api.py
    services.py
    exceptions.py
    auth.py
```

---

## 1. Models (`users/models.py`)

```python
import uuid
from django.conf import settings
from django.db import models


def avatar_upload_path(instance, filename):
    ext = filename.rsplit(".", 1)[-1].lower()
    return f"avatars/{instance.user_id}/{uuid.uuid4().hex}.{ext}"


class UserAvatar(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="avatar",
        primary_key=True,
    )
    image = models.ImageField(upload_to=avatar_upload_path)
    crop_x = models.IntegerField(default=0)
    crop_y = models.IntegerField(default=0)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    original_filename = models.CharField(max_length=255)
    file_size = models.IntegerField(help_text="File size in bytes")
    content_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_avatars"

    def __str__(self):
        return f"Avatar for user {self.user_id}"
```

---

## 2. Schemas (`users/schemas.py`)

```python
from ninja import Schema
from datetime import datetime


class CropMetadata(Schema):
    crop_x: int = 0
    crop_y: int = 0
    width: int = 0
    height: int = 0


class AvatarOut(Schema):
    user_id: int
    image_url: str
    crop_x: int
    crop_y: int
    width: int
    height: int
    original_filename: str
    file_size: int
    content_type: str
    created_at: datetime
    updated_at: datetime


class ErrorOut(Schema):
    detail: str


class DeleteOut(Schema):
    success: bool
    detail: str
```

---

## 3. Exceptions (`users/exceptions.py`)

```python
class AvatarError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


class FileTooLargeError(AvatarError):
    def __init__(self):
        super().__init__("File size exceeds the 5MB limit.", status_code=413)


class InvalidFileTypeError(AvatarError):
    def __init__(self, content_type: str):
        super().__init__(
            f"File type '{content_type}' is not allowed. "
            f"Allowed types: jpg, png, webp.",
            status_code=415,
        )


class AvatarNotFoundError(AvatarError):
    def __init__(self):
        super().__init__("Avatar not found.", status_code=404)


class PermissionDeniedError(AvatarError):
    def __init__(self):
        super().__init__(
            "You do not have permission to modify this avatar.",
            status_code=403,
        )
```

---

## 4. Auth (`users/auth.py`)

```python
from ninja.security import HttpBearer
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthBearer(HttpBearer):
    def authenticate(self, request, token: str):
        try:
            user = User.objects.get(auth_token=token)
            return user
        except User.DoesNotExist:
            return None
```

---

## 5. Services (`users/services.py`)

```python
import os
from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth import get_user_model

from .models import UserAvatar
from .exceptions import (
    FileTooLargeError,
    InvalidFileTypeError,
    AvatarNotFoundError,
    PermissionDeniedError,
)

User = get_user_model()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


class AvatarService:

    @staticmethod
    def validate_file(file: UploadedFile) -> None:
        if file.size > MAX_FILE_SIZE:
            raise FileTooLargeError()

        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise InvalidFileTypeError(file.content_type)

        ext = file.name.rsplit(".", 1)[-1].lower() if "." in file.name else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise InvalidFileTypeError(ext)

    @staticmethod
    def check_permission(request_user, target_user_id: int) -> None:
        if request_user.id != target_user_id:
            raise PermissionDeniedError()

    @staticmethod
    def upload_avatar(
        user_id: int,
        file: UploadedFile,
        crop_x: int = 0,
        crop_y: int = 0,
        width: int = 0,
        height: int = 0,
    ) -> UserAvatar:
        AvatarService.validate_file(file)

        avatar, _ = UserAvatar.objects.update_or_create(
            user_id=user_id,
            defaults={
                "image": file,
                "crop_x": crop_x,
                "crop_y": crop_y,
                "width": width,
                "height": height,
                "original_filename": file.name,
                "file_size": file.size,
                "content_type": file.content_type,
            },
        )
        return avatar

    @staticmethod
    def get_avatar(user_id: int) -> UserAvatar:
        try:
            return UserAvatar.objects.get(user_id=user_id)
        except UserAvatar.DoesNotExist:
            raise AvatarNotFoundError()

    @staticmethod
    def delete_avatar(user_id: int) -> None:
        try:
            avatar = UserAvatar.objects.get(user_id=user_id)
        except UserAvatar.DoesNotExist:
            raise AvatarNotFoundError()

        if avatar.image:
            if os.path.isfile(avatar.image.path):
                os.remove(avatar.image.path)

        avatar.delete()
```

---

## 6. API Endpoints (`users/api.py`)

```python
from ninja import Router, File, Form
from ninja.files import UploadedFile
from django.http import HttpRequest

from .schemas import AvatarOut, CropMetadata, ErrorOut, DeleteOut
from .services import AvatarService
from .exceptions import AvatarError
from .auth import AuthBearer

router = Router(tags=["Avatar"])
auth = AuthBearer()


def _avatar_to_response(avatar, request: HttpRequest) -> dict:
    return {
        "user_id": avatar.user_id,
        "image_url": request.build_absolute_uri(avatar.image.url),
        "crop_x": avatar.crop_x,
        "crop_y": avatar.crop_y,
        "width": avatar.width,
        "height": avatar.height,
        "original_filename": avatar.original_filename,
        "file_size": avatar.file_size,
        "content_type": avatar.content_type,
        "created_at": avatar.created_at,
        "updated_at": avatar.updated_at,
    }


@router.post(
    "/{user_id}/avatar",
    response={200: AvatarOut, 403: ErrorOut, 413: ErrorOut, 415: ErrorOut},
    auth=auth,
    summary="Upload or update user avatar",
)
def upload_avatar(
    request: HttpRequest,
    user_id: int,
    file: UploadedFile = File(...),
    crop_x: int = Form(0),
    crop_y: int = Form(0),
    width: int = Form(0),
    height: int = Form(0),
):
    """
    Upload a profile image with optional crop metadata.
    Accepts multipart/form-data with an image file and crop parameters.
    Only the user themselves can upload their avatar.
    File size limit: 5MB. Allowed formats: jpg, png, webp.
    """
    try:
        AvatarService.check_permission(request.auth, user_id)
        avatar = AvatarService.upload_avatar(
            user_id=user_id,
            file=file,
            crop_x=crop_x,
            crop_y=crop_y,
            width=width,
            height=height,
        )
        return 200, _avatar_to_response(avatar, request)
    except AvatarError as e:
        return e.status_code, {"detail": e.message}


@router.get(
    "/{user_id}/avatar",
    response={200: AvatarOut, 404: ErrorOut},
    summary="Get user avatar info",
)
def get_avatar(request: HttpRequest, user_id: int):
    """
    Retrieve the current avatar information for a user.
    This endpoint is public and does not require authentication.
    """
    try:
        avatar = AvatarService.get_avatar(user_id)
        return 200, _avatar_to_response(avatar, request)
    except AvatarError as e:
        return e.status_code, {"detail": e.message}


@router.delete(
    "/{user_id}/avatar",
    response={200: DeleteOut, 403: ErrorOut, 404: ErrorOut},
    auth=auth,
    summary="Delete user avatar",
)
def delete_avatar(request: HttpRequest, user_id: int):
    """
    Delete the avatar for a user.
    Only the user themselves can delete their avatar.
    """
    try:
        AvatarService.check_permission(request.auth, user_id)
        AvatarService.delete_avatar(user_id)
        return 200, {"success": True, "detail": "Avatar deleted successfully."}
    except AvatarError as e:
        return e.status_code, {"detail": e.message}
```

---

## 7. URL Configuration (`config/urls.py` or `project/urls.py`)

```python
from ninja import NinjaAPI
from users.api import router as avatar_router

api = NinjaAPI(
    title="User Avatar API",
    version="1.0.0",
)

api.add_router("/v1/users", avatar_router)

urlpatterns = [
    # ... existing urlpatterns ...
    path("api/", api.urls),
]
```

This registers all three endpoints under:
- `POST /api/v1/users/{user_id}/avatar`
- `GET /api/v1/users/{user_id}/avatar`
- `DELETE /api/v1/users/{user_id}/avatar`

---

## 8. Tests (`users/tests.py`)

```python
import io
from PIL import Image
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from ninja.testing import TestClient

from .api import router
from .models import UserAvatar

User = get_user_model()

TEST_MEDIA_ROOT = "/tmp/test_avatars/"


def create_test_image(
    filename="test.png", size=(100, 100), fmt="PNG"
) -> io.BytesIO:
    image = Image.new("RGB", size, color="red")
    buffer = io.BytesIO()
    image.save(buffer, format=fmt)
    buffer.seek(0)
    buffer.name = filename
    return buffer


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class AvatarAPITest(TestCase):
    def setUp(self):
        self.client = TestClient(router)
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", password="testpass123"
        )

    def test_upload_avatar_success(self):
        image = create_test_image()
        response = self.client.post(
            f"/{self.user.id}/avatar",
            data={
                "crop_x": 10,
                "crop_y": 20,
                "width": 200,
                "height": 200,
            },
            FILES={"file": image},
            user=self.user,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["crop_x"], 10)
        self.assertEqual(data["crop_y"], 20)
        self.assertEqual(data["width"], 200)
        self.assertEqual(data["height"], 200)

    def test_upload_avatar_file_too_large(self):
        large_data = b"x" * (5 * 1024 * 1024 + 1)
        buffer = io.BytesIO(large_data)
        buffer.name = "large.png"
        buffer.content_type = "image/png"
        buffer.size = len(large_data)

        response = self.client.post(
            f"/{self.user.id}/avatar",
            FILES={"file": buffer},
            user=self.user,
        )
        self.assertEqual(response.status_code, 413)

    def test_upload_avatar_invalid_type(self):
        buffer = io.BytesIO(b"not an image")
        buffer.name = "file.gif"
        buffer.content_type = "image/gif"
        buffer.size = 12

        response = self.client.post(
            f"/{self.user.id}/avatar",
            FILES={"file": buffer},
            user=self.user,
        )
        self.assertEqual(response.status_code, 415)

    def test_upload_avatar_permission_denied(self):
        image = create_test_image()
        response = self.client.post(
            f"/{self.user.id}/avatar",
            FILES={"file": image},
            user=self.other_user,
        )
        self.assertEqual(response.status_code, 403)

    def test_get_avatar_success(self):
        image = create_test_image()
        self.client.post(
            f"/{self.user.id}/avatar",
            FILES={"file": image},
            user=self.user,
        )
        response = self.client.get(f"/{self.user.id}/avatar")
        self.assertEqual(response.status_code, 200)

    def test_get_avatar_not_found(self):
        response = self.client.get(f"/{self.user.id}/avatar")
        self.assertEqual(response.status_code, 404)

    def test_delete_avatar_success(self):
        image = create_test_image()
        self.client.post(
            f"/{self.user.id}/avatar",
            FILES={"file": image},
            user=self.user,
        )
        response = self.client.delete(
            f"/{self.user.id}/avatar",
            user=self.user,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            UserAvatar.objects.filter(user_id=self.user.id).exists()
        )

    def test_delete_avatar_permission_denied(self):
        image = create_test_image()
        self.client.post(
            f"/{self.user.id}/avatar",
            FILES={"file": image},
            user=self.user,
        )
        response = self.client.delete(
            f"/{self.user.id}/avatar",
            user=self.other_user,
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_avatar_not_found(self):
        response = self.client.delete(
            f"/{self.user.id}/avatar",
            user=self.user,
        )
        self.assertEqual(response.status_code, 404)
```

---

## 9. Django Settings (Required Additions)

```python
# settings.py

INSTALLED_APPS = [
    # ...
    "ninja",
    "users",
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Optional: set max upload size at the Django level as well
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
```

---

## API Usage Examples

### Upload Avatar (multipart/form-data)

```bash
curl -X POST http://localhost:8000/api/v1/users/1/avatar \
  -H "Authorization: Bearer <token>" \
  -F "file=@profile.jpg" \
  -F "crop_x=10" \
  -F "crop_y=20" \
  -F "width=200" \
  -F "height=200"
```

**Response 200:**
```json
{
  "user_id": 1,
  "image_url": "http://localhost:8000/media/avatars/1/abc123.jpg",
  "crop_x": 10,
  "crop_y": 20,
  "width": 200,
  "height": 200,
  "original_filename": "profile.jpg",
  "file_size": 245760,
  "content_type": "image/jpeg",
  "created_at": "2026-04-04T12:00:00Z",
  "updated_at": "2026-04-04T12:00:00Z"
}
```

### Get Avatar

```bash
curl http://localhost:8000/api/v1/users/1/avatar
```

### Delete Avatar

```bash
curl -X DELETE http://localhost:8000/api/v1/users/1/avatar \
  -H "Authorization: Bearer <token>"
```

---

## Design Decisions

| Decision | Rationale |
|---|---|
| `OneToOneField` on User | Each user has at most one avatar; `update_or_create` replaces it on re-upload |
| File validation in service layer | Keeps API layer thin; service is reusable from management commands or Celery tasks |
| Custom exception hierarchy | Maps domain errors to HTTP status codes cleanly (413, 415, 403, 404) |
| `Form()` parameters alongside `File()` | Django Ninja supports mixed multipart/form-data with file + form fields natively |
| GET endpoint is public | Avatar info is typically non-sensitive; only mutation endpoints require auth |
| Physical file deletion on `DELETE` | Prevents orphaned files from accumulating in storage |
| UUID-based filenames in upload path | Avoids filename collisions and prevents enumeration of uploaded files |
