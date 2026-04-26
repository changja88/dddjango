# 게시판 API (django-ninja-extra + django-ninja-jwt)

## 프로젝트 구조

```
myproject/
├── myproject/
│   ├── api.py
│   ├── settings.py
│   └── urls.py
└── boards/
    ├── __init__.py
    ├── models.py
    ├── schemas.py
    ├── permissions.py
    ├── api.py
    └── tests.py
```

---

## 1. 설치 및 설정

```bash
pip install django-ninja-extra django-ninja-jwt
```

### settings.py

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "ninja_extra",
    "ninja_jwt",
    "boards",
]

NINJA_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}
```

---

## 2. 모델 정의

### boards/models.py

```python
from django.conf import settings
from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
```

---

## 3. 스키마 정의

### boards/schemas.py

```python
from datetime import datetime

from ninja import ModelSchema, Schema

from .models import Post


class PostCreateSchema(Schema):
    title: str
    content: str


class PostUpdateSchema(Schema):
    title: str
    content: str


class PostPatchSchema(Schema):
    title: str | None = None
    content: str | None = None


class PostOutSchema(ModelSchema):
    author_name: str

    class Meta:
        model = Post
        fields = ["id", "title", "content", "created_at", "updated_at"]

    @staticmethod
    def resolve_author_name(obj: Post) -> str:
        return obj.author.username


class PostListSchema(ModelSchema):
    author_name: str

    class Meta:
        model = Post
        fields = ["id", "title", "created_at"]

    @staticmethod
    def resolve_author_name(obj: Post) -> str:
        return obj.author.username
```

---

## 4. 커스텀 Permission

### boards/permissions.py

```python
from django.http import HttpRequest
from ninja_extra.permissions import BasePermission

from .models import Post


class IsPostAuthor(BasePermission):
    """작성자만 수정/삭제 가능"""

    def has_permission(self, request: HttpRequest, controller) -> bool:
        return request.user and request.user.is_authenticated

    def has_object_permission(
        self, request: HttpRequest, controller, obj: Post
    ) -> bool:
        return obj.author == request.user


class IsAdminOrPostAuthor(BasePermission):
    """관리자는 모든 게시물 삭제 가능, 작성자도 자기 게시물 삭제 가능"""

    def has_permission(self, request: HttpRequest, controller) -> bool:
        return request.user and request.user.is_authenticated

    def has_object_permission(
        self, request: HttpRequest, controller, obj: Post
    ) -> bool:
        if request.user.is_staff:
            return True
        return obj.author == request.user
```

---

## 5. 컨트롤러 (API 엔드포인트)

### boards/api.py

```python
from django.http import HttpRequest
from ninja_extra import (
    ControllerBase,
    api_controller,
    http_delete,
    http_get,
    http_patch,
    http_post,
    http_put,
    permissions,
    status,
)
from ninja_extra.controllers.response import Detail
from ninja_extra.pagination import (
    PageNumberPaginationExtra,
    PaginatedResponseSchema,
    paginate,
)
from ninja_jwt.authentication import JWTAuth

from .models import Post
from .permissions import IsAdminOrPostAuthor, IsPostAuthor
from .schemas import (
    PostCreateSchema,
    PostListSchema,
    PostOutSchema,
    PostPatchSchema,
    PostUpdateSchema,
)


@api_controller("/posts", tags=["Posts"], auth=JWTAuth())
class PostController(ControllerBase):

    @http_get(
        "",
        response=PaginatedResponseSchema[PostListSchema],
        permissions=[permissions.AllowAny],
        auth=None,
    )
    @paginate(PageNumberPaginationExtra, page_size=20)
    def list_posts(self, request: HttpRequest):
        return Post.objects.select_related("author").all()

    @http_get(
        "/{post_id}",
        response=PostOutSchema,
        permissions=[permissions.AllowAny],
        auth=None,
    )
    def get_post(self, request: HttpRequest, post_id: int) -> Post:
        return self.get_object_or_exception(
            Post.objects.select_related("author"), id=post_id
        )

    @http_post(
        "",
        response={201: PostOutSchema},
        permissions=[permissions.IsAuthenticated],
    )
    def create_post(
        self, request: HttpRequest, payload: PostCreateSchema
    ) -> tuple[int, Post]:
        post = Post.objects.create(author=request.user, **payload.dict())
        return 201, post

    @http_put(
        "/{post_id}",
        response=PostOutSchema,
        permissions=[IsPostAuthor()],
    )
    def update_post(
        self, request: HttpRequest, post_id: int, payload: PostUpdateSchema
    ) -> Post:
        post = self.get_object_or_exception(Post, id=post_id)
        self.check_object_permissions(post)
        for attr, value in payload.dict().items():
            setattr(post, attr, value)
        post.save()
        return post

    @http_patch(
        "/{post_id}",
        response=PostOutSchema,
        permissions=[IsPostAuthor()],
    )
    def patch_post(
        self, request: HttpRequest, post_id: int, payload: PostPatchSchema
    ) -> Post:
        post = self.get_object_or_exception(Post, id=post_id)
        self.check_object_permissions(post)
        for attr, value in payload.dict(exclude_unset=True).items():
            setattr(post, attr, value)
        post.save()
        return post

    @http_delete(
        "/{post_id}",
        response=Detail(status_code=status.HTTP_204_NO_CONTENT),
        permissions=[IsAdminOrPostAuthor()],
    )
    def delete_post(self, request: HttpRequest, post_id: int):
        post = self.get_object_or_exception(Post, id=post_id)
        self.check_object_permissions(post)
        post.delete()
        return self.create_response("", status_code=status.HTTP_204_NO_CONTENT)
```

---

## 6. API 등록

### myproject/api.py

```python
from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController

from boards.api import PostController

api = NinjaExtraAPI(
    title="Board API",
    version="1.0.0",
)

api.register_controllers(
    NinjaJWTDefaultController,
    PostController,
)
```

### myproject/urls.py

```python
from django.contrib import admin
from django.urls import path

from .api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
```

---

## 7. 에러 핸들링

### myproject/api.py (에러 핸들러 추가)

```python
from django.http import JsonResponse
from ninja.errors import HttpError, ValidationError
from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController

from boards.api import PostController


class ProblemDetail:
    def __init__(
        self,
        title: str,
        status_val: int,
        detail: str,
        instance: str = "",
        type_uri: str = "about:blank",
    ):
        self.type = type_uri
        self.title = title
        self.status = status_val
        self.detail = detail
        self.instance = instance

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "title": self.title,
            "status": self.status,
            "detail": self.detail,
            "instance": self.instance,
        }


api = NinjaExtraAPI(
    title="Board API",
    version="1.0.0",
)


@api.exception_handler(HttpError)
def handle_http_error(request, exc):
    return JsonResponse(
        ProblemDetail(
            title=str(exc),
            status_val=exc.status_code,
            detail=str(exc),
            instance=request.path,
        ).to_dict(),
        status=exc.status_code,
        content_type="application/problem+json",
    )


@api.exception_handler(ValidationError)
def handle_validation_error(request, exc):
    return JsonResponse(
        {
            "type": "about:blank",
            "title": "Validation Error",
            "status": 422,
            "detail": "Request validation failed.",
            "instance": request.path,
            "errors": exc.errors,
        },
        status=422,
        content_type="application/problem+json",
    )


api.register_controllers(
    NinjaJWTDefaultController,
    PostController,
)
```

---

## 8. 테스트

### boards/tests.py

```python
import pytest
from django.contrib.auth import get_user_model
from ninja_extra.testing import TestClient

from .api import PostController
from .models import Post

User = get_user_model()


@pytest.fixture
def client():
    return TestClient(PostController)


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="testpass")


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        username="admin", password="adminpass", is_staff=True
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username="otheruser", password="otherpass"
    )


@pytest.fixture
def post(db, user):
    return Post.objects.create(
        title="Test Post",
        content="Test Content",
        author=user,
    )


@pytest.mark.django_db
class TestPostList:
    def test_list_posts_without_auth(self, client, post):
        response = client.get("")
        assert response.status_code == 200

    def test_list_posts_returns_items(self, client, post):
        response = client.get("")
        data = response.json()
        assert data["count"] >= 1


@pytest.mark.django_db
class TestPostDetail:
    def test_get_post_without_auth(self, client, post):
        response = client.get(f"/{post.id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Test Post"

    def test_get_nonexistent_post(self, client):
        response = client.get("/99999")
        assert response.status_code == 404


@pytest.mark.django_db
class TestPostCreate:
    def test_create_post_authenticated(self, client, user):
        response = client.post(
            "",
            json={"title": "New Post", "content": "New Content"},
            user=user,
        )
        assert response.status_code == 201
        assert response.json()["title"] == "New Post"
        assert response.json()["author_name"] == "testuser"

    def test_create_post_unauthenticated(self, client):
        response = client.post(
            "",
            json={"title": "New Post", "content": "New Content"},
        )
        assert response.status_code == 401


@pytest.mark.django_db
class TestPostUpdate:
    def test_update_own_post(self, client, user, post):
        response = client.put(
            f"/{post.id}",
            json={"title": "Updated Title", "content": "Updated Content"},
            user=user,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    def test_update_other_user_post(self, client, other_user, post):
        response = client.put(
            f"/{post.id}",
            json={"title": "Hacked", "content": "Hacked"},
            user=other_user,
        )
        assert response.status_code == 403

    def test_patch_own_post(self, client, user, post):
        response = client.patch(
            f"/{post.id}",
            json={"title": "Patched Title"},
            user=user,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Patched Title"

    def test_patch_other_user_post(self, client, other_user, post):
        response = client.patch(
            f"/{post.id}",
            json={"title": "Hacked"},
            user=other_user,
        )
        assert response.status_code == 403


@pytest.mark.django_db
class TestPostDelete:
    def test_delete_own_post(self, client, user, post):
        response = client.delete(f"/{post.id}", user=user)
        assert response.status_code == 204
        assert not Post.objects.filter(id=post.id).exists()

    def test_delete_other_user_post(self, client, other_user, post):
        response = client.delete(f"/{post.id}", user=other_user)
        assert response.status_code == 403
        assert Post.objects.filter(id=post.id).exists()

    def test_admin_delete_any_post(self, client, admin_user, post):
        response = client.delete(f"/{post.id}", user=admin_user)
        assert response.status_code == 204
        assert not Post.objects.filter(id=post.id).exists()

    def test_delete_unauthenticated(self, client, post):
        response = client.delete(f"/{post.id}")
        assert response.status_code == 401
```

---

## 엔드포인트 요약

| Method | URL | 인증 | 권한 | 설명 |
|--------|-----|------|------|------|
| POST | `/api/token/pair` | None | AllowAny | JWT 토큰 발급 |
| POST | `/api/token/refresh` | None | AllowAny | Access 토큰 갱신 |
| POST | `/api/token/verify` | None | AllowAny | 토큰 유효성 검증 |
| GET | `/api/posts` | None | AllowAny | 게시물 목록 (페이지네이션) |
| GET | `/api/posts/{id}` | None | AllowAny | 게시물 상세 |
| POST | `/api/posts` | JWT | IsAuthenticated | 게시물 생성 |
| PUT | `/api/posts/{id}` | JWT | IsPostAuthor | 게시물 전체 수정 |
| PATCH | `/api/posts/{id}` | JWT | IsPostAuthor | 게시물 부분 수정 |
| DELETE | `/api/posts/{id}` | JWT | IsAdminOrPostAuthor | 게시물 삭제 |

## 설계 포인트

- **NinjaExtraAPI**: `django-ninja-extra`의 `NinjaExtraAPI`를 사용하여 `@api_controller` 패턴과 `django-ninja-jwt` 호환성을 확보한다.
- **JWTAuth**: 컨트롤러 레벨에서 `auth=JWTAuth()`를 설정하고, 읽기 전용 엔드포인트(목록/상세)는 `auth=None`으로 면제한다.
- **커스텀 Permission**: `IsPostAuthor`는 작성자만 수정/삭제 허용, `IsAdminOrPostAuthor`는 관리자(is_staff)이면 무조건 허용하고 작성자도 자기 게시물을 삭제할 수 있다.
- **객체 레벨 권한**: `has_object_permission`과 `self.check_object_permissions(post)`를 사용하여 객체 단위 권한 검사를 수행한다.
- **Schema 분리**: 생성/수정/부분수정/응답/목록용 스키마를 분리하여 각 용도에 필요한 필드만 노출한다. `ModelSchema`의 `Meta.fields`로 명시적 필드 선택을 적용한다.
- **RFC 9457**: 에러 응답은 `application/problem+json` 형식으로 반환한다.
- **페이지네이션**: 목록 엔드포인트에 `PageNumberPaginationExtra`를 적용하여 `page`, `page_size` 파라미터를 지원한다.
