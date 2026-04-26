# 프로필 이미지 업로드 API

## schemas.py

```python
from ninja import Schema, Field
from pydantic import field_validator


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


class AvatarCropMetadata(Schema):
    crop_x: int = Field(..., ge=0)
    crop_y: int = Field(..., ge=0)
    width: int = Field(..., gt=0)
    height: int = Field(..., gt=0)


class AvatarOut(Schema):
    user_id: int
    url: str
    width: int
    height: int
    file_size: int
    content_type: str


class AvatarUploadOut(Schema):
    user_id: int
    url: str
    message: str


class ErrorOut(Schema):
    detail: str
```

## auth.py

```python
from ninja.security import HttpBearer
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthBearer(HttpBearer):
    def authenticate(self, request, token: str):
        try:
            user = User.objects.get(auth_token__key=token)
            return user
        except User.DoesNotExist:
            return None
```

## api.py

```python
from ninja import Router, File, Form, UploadedFile
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .auth import AuthBearer
from .schemas import (
    AvatarCropMetadata,
    AvatarOut,
    AvatarUploadOut,
    ErrorOut,
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE,
)

User = get_user_model()
router = Router(tags=["avatar"])


def _validate_image_file(file: UploadedFile) -> None:
    if file.size > MAX_FILE_SIZE:
        raise HttpError(413, f"File size exceeds {MAX_FILE_SIZE // (1024 * 1024)}MB limit.")

    extension = file.name.rsplit(".", 1)[-1].lower() if "." in file.name else ""
    if extension not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise HttpError(
            422, f"File type '{extension}' is not allowed. Allowed types: {allowed}."
        )

    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HttpError(422, f"Invalid content type: {file.content_type}.")


def _assert_owner(request, user_id: int) -> None:
    if request.auth.id != user_id:
        raise HttpError(403, "You can only modify your own avatar.")


@router.post(
    "/{user_id}/avatar",
    response={200: AvatarUploadOut, 403: ErrorOut, 413: ErrorOut, 422: ErrorOut},
    auth=AuthBearer(),
)
def upload_avatar(
    request,
    user_id: int,
    metadata: Form[AvatarCropMetadata],
    file: File[UploadedFile],
) -> tuple[int, dict]:
    _assert_owner(request, user_id)
    user = get_object_or_404(User, id=user_id)

    _validate_image_file(file)

    avatar = save_avatar(
        user=user,
        file=file,
        crop_x=metadata.crop_x,
        crop_y=metadata.crop_y,
        width=metadata.width,
        height=metadata.height,
    )

    return 200, {
        "user_id": user.id,
        "url": avatar.url,
        "message": "Avatar uploaded successfully.",
    }


@router.get(
    "/{user_id}/avatar",
    response={200: AvatarOut, 404: ErrorOut},
    auth=AuthBearer(),
)
def get_avatar(request, user_id: int) -> tuple[int, dict]:
    user = get_object_or_404(User, id=user_id)
    avatar = getattr(user, "avatar", None)

    if avatar is None or not avatar.url:
        raise HttpError(404, "Avatar not found.")

    return 200, {
        "user_id": user.id,
        "url": avatar.url,
        "width": avatar.width,
        "height": avatar.height,
        "file_size": avatar.file_size,
        "content_type": avatar.content_type,
    }


@router.delete(
    "/{user_id}/avatar",
    response={204: None, 403: ErrorOut, 404: ErrorOut},
    auth=AuthBearer(),
)
def delete_avatar(request, user_id: int) -> tuple[int, None]:
    _assert_owner(request, user_id)
    user = get_object_or_404(User, id=user_id)
    avatar = getattr(user, "avatar", None)

    if avatar is None or not avatar.url:
        raise HttpError(404, "Avatar not found.")

    delete_avatar_file(user)

    return 204, None


def save_avatar(user, file, crop_x, crop_y, width, height):
    """아바타 저장 로직 (서비스 레이어로 분리 권장)"""
    raise NotImplementedError("Implement avatar save logic with your storage backend.")


def delete_avatar_file(user):
    """아바타 삭제 로직 (서비스 레이어로 분리 권장)"""
    raise NotImplementedError("Implement avatar delete logic with your storage backend.")
```

## urls.py (라우터 등록)

```python
# project/api.py
from ninja import NinjaAPI
from users.api import router as users_router

api = NinjaAPI()
api.add_router("/users", users_router)
```

```python
# project/urls.py
from django.urls import path
from .api import api

urlpatterns = [
    path("api/v1/", api.urls),
]
```

## settings.py (PUT/PATCH 파일 업로드 미들웨어)

```python
MIDDLEWARE = [
    "ninja.compatibility.files.fix_request_files_middleware",
    # ... 기타 미들웨어
]
```

## 엔드포인트 요약

| Method | URL | 인증 | 설명 |
|--------|-----|------|------|
| POST | `/api/v1/users/{user_id}/avatar` | Bearer (본인만) | 이미지 파일 + crop 메타데이터 업로드 |
| GET | `/api/v1/users/{user_id}/avatar` | Bearer | 현재 아바타 정보 조회 |
| DELETE | `/api/v1/users/{user_id}/avatar` | Bearer (본인만) | 아바타 삭제 |

## 적용된 컨벤션

- **Schema Design**: `Schema`로 요청/응답 유효성 검증. `AvatarCropMetadata`에 `Field(..., ge=0)`, `Field(..., gt=0)`으로 입력 제약 조건 명시. 모든 필드를 명시적으로 선언하여 불필요한 노출 방지.
- **Routing**: `Router()`를 사용하여 앱 단위 라우터 구성. `api.add_router()`로 메인 API에 조합. sub-resource URL 3 depth 이내 유지 (`/users/{user_id}/avatar`).
- **Authentication**: `HttpBearer`를 사용한 토큰 기반 인증. operation 수준에서 `auth=AuthBearer()` 적용. `_assert_owner()`로 본인 확인 로직 분리.
- **Input Parsing**: `Form[Schema]` + `File[UploadedFile]` 조합으로 multipart/form-data 처리. path 파라미터(`user_id`)와 form/file 동시 수신.
- **Error Handling**: `HttpError`로 에러 발생. 상태 코드별 다중 응답 스키마 (`response={200: ..., 403: ..., 413: ..., 422: ...}`). tuple 반환 패턴 사용.
- **Response**: 상태 코드별 명시적 응답 스키마 정의. DELETE는 `204: None`으로 빈 응답.
- **Validation**: 파일 크기 제한(5MB), 허용 확장자(jpg, png, webp), content_type 검증을 별도 함수로 분리.
- **Service Layer**: `save_avatar()`, `delete_avatar_file()`을 별도 함수로 분리하여 fat endpoint 방지.
