# Django Ninja 블로그 API

## api.py

```python
from datetime import datetime
from typing import List, Optional

from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Router, Schema, Query
from ninja.security import HttpBearer
from ninja.pagination import paginate, PageNumberPagination
from ninja.errors import HttpError
from pydantic import Field
from enum import Enum

from blog.models import Post  # 모델은 이미 존재한다고 가정


# ──────────────────────────────────────────────
# 인증
# ──────────────────────────────────────────────

class BearerTokenAuth(HttpBearer):
    def authenticate(self, request, token: str):
        from django.contrib.auth.models import User
        from rest_framework.authtoken.models import Token  # or 자체 토큰 모델

        try:
            token_obj = Token.objects.select_related("user").get(key=token)
            return token_obj.user
        except Token.DoesNotExist:
            return None


auth = BearerTokenAuth()


# ──────────────────────────────────────────────
# Enum
# ──────────────────────────────────────────────

class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


# ──────────────────────────────────────────────
# Schema
# ──────────────────────────────────────────────

class ErrorSchema(Schema):
    detail: str
    code: str = "error"


class PostCreateSchema(Schema):
    title: str = Field(..., min_length=1, max_length=200)
    body: str
    category: str = Field(..., min_length=1, max_length=100)
    status: PostStatus = PostStatus.DRAFT


class PostUpdateSchema(Schema):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    body: Optional[str] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[PostStatus] = None


class PostOutSchema(Schema):
    id: int
    title: str
    body: str
    author: str
    category: str
    status: PostStatus
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_author(obj) -> str:
        return obj.author.username


class PostFilterSchema(Schema):
    status: Optional[PostStatus] = None
    category: Optional[str] = None
    author: Optional[str] = None


# ──────────────────────────────────────────────
# API & Router 설정
# ──────────────────────────────────────────────

api = NinjaAPI(
    title="Blog API",
    version="1.0.0",
    description="Django Ninja 블로그 API",
)


# 전역 예외 핸들러 — 표준 에러 응답 형식
@api.exception_handler(HttpError)
def http_error_handler(request, exc: HttpError):
    return api.create_response(
        request,
        {"detail": str(exc), "code": "http_error"},
        status=exc.status_code,
    )


@api.exception_handler(Exception)
def generic_error_handler(request, exc: Exception):
    return api.create_response(
        request,
        {"detail": "Internal server error", "code": "internal_error"},
        status=500,
    )


router = Router(tags=["posts"])


# ──────────────────────────────────────────────
# CRUD 엔드포인트
# ──────────────────────────────────────────────

@router.post("/", response={201: PostOutSchema, 401: ErrorSchema}, auth=auth)
def create_post(request, payload: PostCreateSchema):
    """게시물 생성"""
    post = Post.objects.create(
        title=payload.title,
        body=payload.body,
        author=request.auth,
        category=payload.category,
        status=payload.status.value,
    )
    return 201, post


@router.get("/", response=List[PostOutSchema])
@paginate(PageNumberPagination, page_size=20)
def list_posts(request, filters: PostFilterSchema = Query(...)):
    """게시물 목록 조회 (페이지네이션 포함)"""
    qs = Post.objects.select_related("author").all()

    if filters.status:
        qs = qs.filter(status=filters.status.value)
    if filters.category:
        qs = qs.filter(category=filters.category)
    if filters.author:
        qs = qs.filter(author__username=filters.author)

    return qs.order_by("-created_at")


@router.get("/{post_id}", response={200: PostOutSchema, 404: ErrorSchema})
def get_post(request, post_id: int):
    """게시물 상세 조회"""
    post = get_object_or_404(Post, id=post_id)
    return 200, post


@router.put("/{post_id}", response={200: PostOutSchema, 403: ErrorSchema, 404: ErrorSchema}, auth=auth)
def update_post(request, post_id: int, payload: PostUpdateSchema):
    """게시물 전체/부분 수정"""
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.auth:
        raise HttpError(403, "본인의 게시물만 수정할 수 있습니다.")

    update_data = payload.dict(exclude_unset=True)
    if "status" in update_data and update_data["status"] is not None:
        update_data["status"] = update_data["status"].value

    for attr, value in update_data.items():
        setattr(post, attr, value)

    post.save()
    return 200, post


@router.delete("/{post_id}", response={204: None, 403: ErrorSchema, 404: ErrorSchema}, auth=auth)
def delete_post(request, post_id: int):
    """게시물 삭제"""
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.auth:
        raise HttpError(403, "본인의 게시물만 삭제할 수 있습니다.")

    post.delete()
    return 204, None


# ──────────────────────────────────────────────
# Router 등록
# ──────────────────────────────────────────────

api.add_router("/posts", router)
```

## urls.py (프로젝트 레벨)

```python
from django.urls import path
from blog.api import api

urlpatterns = [
    # ...
    path("api/", api.urls),
]
```

## 참고: 가정한 Post 모델 구조

```python
from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]

    title = models.CharField(max_length=200)
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    category = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
```

## API 엔드포인트 요약

| Method | Path | Auth | 설명 |
|--------|------|------|------|
| POST | `/api/posts/` | Bearer Token | 게시물 생성 |
| GET | `/api/posts/?page=1` | 불필요 | 목록 조회 (페이지네이션) |
| GET | `/api/posts/{id}` | 불필요 | 상세 조회 |
| PUT | `/api/posts/{id}` | Bearer Token | 수정 (본인만) |
| DELETE | `/api/posts/{id}` | Bearer Token | 삭제 (본인만) |

## 필터링 파라미터 (GET /api/posts/)

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `status` | string | `draft` / `published` / `archived` |
| `category` | string | 카테고리명 |
| `author` | string | 작성자 username |
| `page` | int | 페이지 번호 (기본 1) |

## 에러 응답 형식

모든 에러는 아래 형식으로 응답:

```json
{
    "detail": "에러 메시지",
    "code": "error_code"
}
```

## 요청/응답 예시

### 게시물 생성

```bash
curl -X POST http://localhost:8000/api/posts/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "첫 번째 포스트",
    "body": "본문 내용입니다.",
    "category": "기술",
    "status": "draft"
  }'
```

### 목록 조회 (페이지네이션 + 필터)

```bash
curl "http://localhost:8000/api/posts/?status=published&page=2"
```

응답:

```json
{
    "items": [
        {
            "id": 1,
            "title": "첫 번째 포스트",
            "body": "본문 내용입니다.",
            "author": "hyun",
            "category": "기술",
            "status": "published",
            "created_at": "2026-04-04T12:00:00Z",
            "updated_at": "2026-04-04T12:00:00Z"
        }
    ],
    "count": 1
}
```
