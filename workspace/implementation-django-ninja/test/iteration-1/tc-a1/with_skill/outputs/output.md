# Blog API with Django Ninja

## api.py

```python
from typing import List, Optional

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Router, Schema, ModelSchema, PatchDict, Field
from ninja.errors import HttpError, ValidationError
from ninja.pagination import paginate, PageNumberPagination
from ninja.security import HttpBearer

from .models import Post


# ── Authentication ────────────────────────────────────────────────


class BearerAuth(HttpBearer):
    def authenticate(self, request, token: str):
        from django.contrib.auth.models import User

        try:
            user = User.objects.get(auth_token__key=token)
            return user
        except User.DoesNotExist:
            return None


# ── Error Handling (RFC 9457 Problem Details) ─────────────────────


class ProblemDetail(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str = ""


api = NinjaAPI(title="Blog API", version="1.0.0", auth=BearerAuth())


@api.exception_handler(HttpError)
def handle_http_error(request, exc: HttpError):
    return JsonResponse(
        ProblemDetail(
            title=str(exc),
            status=exc.status_code,
            detail=str(exc),
            instance=request.path,
        ).dict(),
        status=exc.status_code,
        content_type="application/problem+json",
    )


@api.exception_handler(ValidationError)
def handle_validation_error(request, exc: ValidationError):
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


@api.exception_handler(Exception)
def handle_generic_error(request, exc: Exception):
    return JsonResponse(
        ProblemDetail(
            title="Internal Server Error",
            status=500,
            detail="An unexpected error occurred.",
            instance=request.path,
        ).dict(),
        status=500,
        content_type="application/problem+json",
    )


# ── Schemas ───────────────────────────────────────────────────────


class PostIn(Schema):
    title: str = Field(..., max_length=200)
    body: str
    author_id: int
    category: str = Field(..., max_length=100)
    status: str = Field("draft", pattern="^(draft|published|archived)$")


class PostOut(Schema):
    id: int
    title: str
    body: str
    author_id: int
    category: str
    status: str
    created_at: str
    updated_at: str


class PostPatch(Schema):
    title: str = Field(None, max_length=200)
    body: Optional[str] = None
    category: str = Field(None, max_length=100)
    status: str = Field(None, pattern="^(draft|published|archived)$")


# ── Router ────────────────────────────────────────────────────────

router = Router(tags=["posts"])


@router.get("/", response=List[PostOut])
@paginate(PageNumberPagination, page_size=20)
def list_posts(request, status: Optional[str] = None, category: Optional[str] = None):
    qs = Post.objects.all()
    if status:
        qs = qs.filter(status=status)
    if category:
        qs = qs.filter(category=category)
    return qs


@router.get("/{post_id}", response=PostOut)
def get_post(request, post_id: int):
    return get_object_or_404(Post, id=post_id)


@router.post("/", response={201: PostOut})
def create_post(request, payload: PostIn):
    post = Post.objects.create(**payload.dict())
    return 201, post


@router.patch("/{post_id}", response=PostOut)
def update_post(request, post_id: int, payload: PatchDict[PostPatch]):
    post = get_object_or_404(Post, id=post_id)
    for attr, value in payload.items():
        setattr(post, attr, value)
    post.save()
    return post


@router.delete("/{post_id}", response={204: None})
def delete_post(request, post_id: int):
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    return 204, None


api.add_router("/posts/", router)
```

## Design Decisions

### Schema

- `PostIn` -- 생성 시 입력 스키마. `status` 필드에 `pattern` 정규식을 적용하여 `draft|published|archived` 값만 허용한다.
- `PostOut` -- 응답 스키마. 명시적으로 필요한 필드만 선언하여 민감 데이터 노출을 방지한다.
- `PostPatch` -- 부분 수정 스키마. `PatchDict[PostPatch]`를 사용하여 실제 제공된 필드만 포함하는 딕셔너리를 받는다. `exclude_unset`을 직접 다룰 필요가 없다.

### Authentication

- `HttpBearer`를 상속한 `BearerAuth` 클래스를 사용한다. `Authorization: Bearer <token>` 헤더를 통해 토큰을 검증한다.
- `NinjaAPI(auth=BearerAuth())`로 글로벌 수준에 적용하여 모든 엔드포인트에 인증이 기본 적용된다.
- 인증이 필요 없는 엔드포인트는 `auth=None`으로 개별 면제할 수 있다.

### Pagination

- `@paginate(PageNumberPagination, page_size=20)` 데코레이터로 목록 조회에 페이지네이션을 적용한다.
- 요청 예시: `/api/posts/?page=2&page_size=10`
- 뷰 함수는 전체 QuerySet을 반환하고, 실제 슬라이싱은 페이지네이터가 처리한다.

### Error Handling

- 모든 에러 응답은 RFC 9457 Problem Details 형식을 따른다. `Content-Type: application/problem+json`.
- `HttpError`, `ValidationError`, 기타 `Exception` 세 가지 핸들러를 등록하여 모든 에러 경로를 커버한다.
- `ProblemDetail` 스키마로 에러 응답 구조를 표준화한다: `type`, `title`, `status`, `detail`, `instance`.

### Routing

- `Router(tags=["posts"])`로 블로그 라우터를 분리하고, `api.add_router("/posts/", router)`로 메인 API에 연결한다.
- CRUD 엔드포인트 URL 구조:
  - `GET /posts/` -- 목록 조회 (페이지네이션, 필터링)
  - `GET /posts/{post_id}` -- 단건 조회
  - `POST /posts/` -- 생성 (201 반환)
  - `PATCH /posts/{post_id}` -- 부분 수정
  - `DELETE /posts/{post_id}` -- 삭제 (204 반환)

### urls.py Registration

```python
# myproject/urls.py
from django.urls import path
from .api import api

urlpatterns = [
    path("api/", api.urls),
]
```
