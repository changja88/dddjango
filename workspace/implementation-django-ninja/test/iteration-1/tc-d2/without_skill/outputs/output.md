# Django Ninja Extra - Board API Implementation

django-ninja-extra의 `@api_controller` 패턴을 사용한 게시판 CRUD API 구현.
JWT 인증(django-ninja-jwt) 및 커스텀 Permission 기반 권한 제어 포함.

---

## 1. 프로젝트 설정

### 1-1. 패키지 설치

```bash
pip install django-ninja-extra django-ninja-jwt
```

### 1-2. settings.py

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "ninja_extra",
    "ninja_jwt",
    # local
    "boards",
]

NINJA_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}
```

### 1-3. urls.py (프로젝트 루트)

```python
from django.contrib import admin
from django.urls import path
from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController

api = NinjaExtraAPI(
    title="Board API",
    version="1.0.0",
)

# JWT 인증 엔드포인트 자동 등록 (/api/token/pair, /api/token/refresh, /api/token/verify)
api.register_controllers(NinjaJWTDefaultController)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
```

---

## 2. 게시판 앱 구조

```
boards/
    __init__.py
    models.py
    schemas.py
    permissions.py
    controllers.py
```

---

## 3. Model

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

## 4. Schema

### boards/schemas.py

```python
from datetime import datetime
from ninja import Schema


class PostCreateSchema(Schema):
    title: str
    content: str


class PostUpdateSchema(Schema):
    title: str | None = None
    content: str | None = None


class PostResponseSchema(Schema):
    id: int
    title: str
    content: str
    author_id: int
    author_username: str
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_author_username(obj) -> str:
        return obj.author.username


class MessageSchema(Schema):
    message: str
```

---

## 5. Custom Permission

### boards/permissions.py

```python
from ninja_extra.permissions import BasePermission


class IsAuthor(BasePermission):
    """게시물 작성자만 허용하는 Permission."""

    message = "You do not have permission. Only the author can perform this action."

    def has_permission(self, request, controller) -> bool:
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, controller, obj) -> bool:
        return obj.author_id == request.user.id


class IsAuthorOrAdmin(BasePermission):
    """작성자 또는 관리자(is_staff)에게 허용하는 Permission.

    - 수정: 작성자만 가능
    - 삭제: 작성자 또는 관리자 가능
    이 Permission은 삭제 엔드포인트 전용으로, 작성자이거나 관리자이면 통과.
    """

    message = "You do not have permission. Only the author or an admin can perform this action."

    def has_permission(self, request, controller) -> bool:
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, controller, obj) -> bool:
        return obj.author_id == request.user.id or request.user.is_staff
```

---

## 6. Controller

### boards/controllers.py

```python
from django.shortcuts import get_object_or_404
from ninja_extra import api_controller, ControllerBase, http_get, http_post, http_patch, http_delete
from ninja_extra.permissions import IsAuthenticated
from ninja_jwt.authentication import JWTAuth

from boards.models import Post
from boards.schemas import (
    PostCreateSchema,
    PostUpdateSchema,
    PostResponseSchema,
    MessageSchema,
)
from boards.permissions import IsAuthor, IsAuthorOrAdmin


@api_controller("/posts", tags=["Posts"])
class PostController(ControllerBase):
    """게시판 CRUD API Controller."""

    # ------------------------------------------------------------------
    # 목록 조회 (인증 불필요)
    # ------------------------------------------------------------------
    @http_get(
        "",
        response=list[PostResponseSchema],
        summary="게시물 목록 조회",
    )
    def list_posts(self):
        posts = Post.objects.select_related("author").all()
        return posts

    # ------------------------------------------------------------------
    # 단건 조회 (인증 불필요)
    # ------------------------------------------------------------------
    @http_get(
        "/{int:post_id}",
        response=PostResponseSchema,
        summary="게시물 상세 조회",
    )
    def get_post(self, post_id: int):
        post = get_object_or_404(
            Post.objects.select_related("author"),
            id=post_id,
        )
        return post

    # ------------------------------------------------------------------
    # 생성 (JWT 인증 필요)
    # ------------------------------------------------------------------
    @http_post(
        "",
        response={201: PostResponseSchema},
        auth=JWTAuth(),
        permissions=[IsAuthenticated],
        summary="게시물 작성",
    )
    def create_post(self, payload: PostCreateSchema):
        post = Post.objects.create(
            title=payload.title,
            content=payload.content,
            author=self.context.request.user,
        )
        # select_related를 위해 재조회
        post = Post.objects.select_related("author").get(id=post.id)
        return 201, post

    # ------------------------------------------------------------------
    # 수정 (작성자만 가능)
    # ------------------------------------------------------------------
    @http_patch(
        "/{int:post_id}",
        response=PostResponseSchema,
        auth=JWTAuth(),
        permissions=[IsAuthor],
        summary="게시물 수정 (작성자만)",
    )
    def update_post(self, post_id: int, payload: PostUpdateSchema):
        post = get_object_or_404(Post, id=post_id)

        # object-level permission 체크
        self.check_object_permissions(post)

        update_data = payload.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(post, field, value)
        post.save()

        post = Post.objects.select_related("author").get(id=post.id)
        return post

    # ------------------------------------------------------------------
    # 삭제 (작성자 또는 관리자)
    # ------------------------------------------------------------------
    @http_delete(
        "/{int:post_id}",
        response={204: None},
        auth=JWTAuth(),
        permissions=[IsAuthorOrAdmin],
        summary="게시물 삭제 (작성자 또는 관리자)",
    )
    def delete_post(self, post_id: int):
        post = get_object_or_404(Post, id=post_id)

        # object-level permission 체크
        self.check_object_permissions(post)

        post.delete()
        return 204, None
```

---

## 7. Controller 등록

컨트롤러를 API에 등록하려면 `urls.py`에서 import하거나 `auto_discover=True`를 사용한다.

### 방법 A: urls.py에서 명시적 등록

```python
# project/urls.py
from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController
from boards.controllers import PostController

api = NinjaExtraAPI(title="Board API", version="1.0.0")

api.register_controllers(
    NinjaJWTDefaultController,
    PostController,
)
```

### 방법 B: auto_discover 사용

```python
# project/urls.py
api = NinjaExtraAPI(title="Board API", version="1.0.0", auto_discover=True)
```

`auto_discover=True`로 설정하면 `INSTALLED_APPS`에 등록된 앱의 `controllers.py`를 자동 탐색한다.

---

## 8. API 엔드포인트 요약

| Method | Endpoint | 설명 | 인증 | 권한 |
|--------|----------|------|------|------|
| POST | `/api/token/pair` | JWT 토큰 발급 | - | - |
| POST | `/api/token/refresh` | JWT 토큰 갱신 | - | - |
| POST | `/api/token/verify` | JWT 토큰 검증 | - | - |
| GET | `/api/posts` | 게시물 목록 조회 | 불필요 | - |
| GET | `/api/posts/{id}` | 게시물 상세 조회 | 불필요 | - |
| POST | `/api/posts` | 게시물 작성 | JWT | IsAuthenticated |
| PATCH | `/api/posts/{id}` | 게시물 수정 | JWT | IsAuthor |
| DELETE | `/api/posts/{id}` | 게시물 삭제 | JWT | IsAuthorOrAdmin |

---

## 9. 사용 예시

### 9-1. JWT 토큰 발급

```bash
curl -X POST http://localhost:8000/api/token/pair \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

응답:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIs...",
  "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

### 9-2. 게시물 작성

```bash
curl -X POST http://localhost:8000/api/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"title": "첫 번째 게시물", "content": "안녕하세요!"}'
```

### 9-3. 게시물 목록 조회

```bash
curl http://localhost:8000/api/posts
```

### 9-4. 게시물 수정 (작성자만)

```bash
curl -X PATCH http://localhost:8000/api/posts/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"title": "수정된 제목"}'
```

### 9-5. 게시물 삭제 (작성자 또는 관리자)

```bash
curl -X DELETE http://localhost:8000/api/posts/1 \
  -H "Authorization: Bearer <access_token>"
```

---

## 10. 핵심 설계 결정 사항

### Permission 분리

| Permission 클래스 | 용도 | 적용 대상 |
|-------------------|------|-----------|
| `IsAuthor` | 작성자 본인만 허용 | 수정(PATCH) |
| `IsAuthorOrAdmin` | 작성자 또는 `is_staff=True`인 관리자 허용 | 삭제(DELETE) |

두 Permission 모두 `has_permission`에서 인증 여부를 확인하고, `has_object_permission`에서 객체 수준 권한을 검증한다. 컨트롤러의 `self.check_object_permissions(post)` 호출을 통해 object-level permission이 실행된다.

### Partial Update

`PostUpdateSchema`에서 모든 필드를 `Optional`로 선언하고, `payload.dict(exclude_unset=True)`로 클라이언트가 보낸 필드만 업데이트한다. 보내지 않은 필드는 기존 값을 유지한다.

### select_related

`PostResponseSchema`에서 `author_username`을 resolve하기 위해 `author` FK를 참조하므로, N+1 쿼리 방지를 위해 `select_related("author")`를 사용한다.
