작업 디렉터리는 비어 있고 읽기 전용이라 파일을 직접 추가하진 못했습니다. 아래는 팀 컨벤션 문서나 `common/api/` 모듈로 바로 넣을 수 있는 Django Ninja pagination/error response 표준안입니다. Django Ninja 공식 문서 기준으로 `@paginate`, `PaginationBase`, `api.exception_handler`, `api.create_response`를 사용합니다. 참고: [Pagination](https://django-ninja.dev/guides/response/pagination/), [Handling errors](https://django-ninja.dev/guides/errors/)

**응답 표준**
성공 목록 응답은 항상 아래 형태를 사용합니다.

```json
{
  "count": 123,
  "page": 1,
  "page_size": 20,
  "total_pages": 7,
  "next": "/api/users?page=2&page_size=20",
  "previous": null,
  "results": []
}
```

에러 응답은 항상 아래 형태를 사용합니다.

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "요청 값이 올바르지 않습니다.",
    "details": [
      {
        "field": "body.email",
        "message": "Input should be a valid email address",
        "type": "value_error"
      }
    ],
    "trace_id": "01HX..."
  }
}
```

**규칙**
- 목록 API는 기본적으로 `page`, `page_size` 기반 페이지네이션을 쓴다.
- `page`는 1부터 시작한다.
- 기본 `page_size`는 `20`, 최대값은 `100`으로 제한한다.
- 목록 필드는 `results`로 고정한다. `items`, `data`, `objects`를 섞어 쓰지 않는다.
- validation 실패는 `422`, 인증 실패는 `401`, 권한 실패는 `403`, 미존재 리소스는 `404`를 쓴다.
- 서버 내부 오류는 `500`이며 운영 환경에서는 내부 exception 메시지를 노출하지 않는다.
- 모든 에러는 `error.code`를 클라이언트 분기 기준으로 사용한다. `message`는 사용자 표시용 문구다.
- `trace_id`는 요청 추적용이다. 미들웨어에서 넣어도 되고 없으면 handler에서 생성한다.

**예시 코드: `common/api/pagination.py`**

```python
from math import ceil
from typing import Any, List, Optional

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from ninja import Field, Schema
from ninja.pagination import PaginationBase


DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


class StandardPageNumberPagination(PaginationBase):
    items_attribute = "results"

    class Input(Schema):
        page: int = Field(1, ge=1)
        page_size: int = Field(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE)

    class Output(Schema):
        count: int
        page: int
        page_size: int
        total_pages: int
        next: Optional[str]
        previous: Optional[str]
        results: List[Any]

    def paginate_queryset(self, queryset, pagination: Input, **params):
        request = params["request"]

        paginator = Paginator(queryset, pagination.page_size)

        try:
            page_obj = paginator.page(pagination.page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages or 1)

        return {
            "count": paginator.count,
            "page": page_obj.number,
            "page_size": pagination.page_size,
            "total_pages": ceil(paginator.count / pagination.page_size)
            if paginator.count
            else 0,
            "next": self._page_url(request, page_obj.next_page_number(), pagination.page_size)
            if page_obj.has_next()
            else None,
            "previous": self._page_url(
                request,
                page_obj.previous_page_number(),
                pagination.page_size,
            )
            if page_obj.has_previous()
            else None,
            "results": list(page_obj.object_list),
        }

    def _page_url(self, request, page: int, page_size: int) -> str:
        query = request.GET.copy()
        query["page"] = str(page)
        query["page_size"] = str(page_size)
        return f"{request.path}?{query.urlencode()}"
```

**예시 코드: `common/api/errors.py`**

```python
from dataclasses import dataclass
from typing import Any, Optional
from uuid import uuid4

from django.conf import settings
from django.http import Http404
from ninja import NinjaAPI
from ninja.errors import (
    AuthenticationError,
    AuthorizationError,
    HttpError,
    ValidationError,
)


@dataclass
class ApiError(Exception):
    code: str
    message: str
    status_code: int = 400
    details: Optional[list[dict[str, Any]]] = None


def get_trace_id(request) -> str:
    return getattr(request, "trace_id", None) or request.headers.get("X-Request-ID") or str(uuid4())


def error_body(
    request,
    *,
    code: str,
    message: str,
    details: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or [],
            "trace_id": get_trace_id(request),
        }
    }


def normalize_validation_errors(exc: ValidationError) -> list[dict[str, Any]]:
    normalized = []

    for item in exc.errors:
        loc = item.get("loc", [])
        normalized.append(
            {
                "field": ".".join(str(part) for part in loc),
                "message": item.get("msg", "Invalid value"),
                "type": item.get("type", "validation_error"),
            }
        )

    return normalized


def register_exception_handlers(api: NinjaAPI) -> None:
    @api.exception_handler(ApiError)
    def api_error_handler(request, exc: ApiError):
        return api.create_response(
            request,
            error_body(
                request,
                code=exc.code,
                message=exc.message,
                details=exc.details,
            ),
            status=exc.status_code,
        )

    @api.exception_handler(ValidationError)
    def validation_error_handler(request, exc: ValidationError):
        return api.create_response(
            request,
            error_body(
                request,
                code="VALIDATION_ERROR",
                message="요청 값이 올바르지 않습니다.",
                details=normalize_validation_errors(exc),
            ),
            status=422,
        )

    @api.exception_handler(AuthenticationError)
    def authentication_error_handler(request, exc: AuthenticationError):
        return api.create_response(
            request,
            error_body(
                request,
                code="UNAUTHENTICATED",
                message="인증이 필요합니다.",
            ),
            status=401,
        )

    @api.exception_handler(AuthorizationError)
    def authorization_error_handler(request, exc: AuthorizationError):
        return api.create_response(
            request,
            error_body(
                request,
                code="FORBIDDEN",
                message="접근 권한이 없습니다.",
            ),
            status=403,
        )

    @api.exception_handler(Http404)
    def not_found_handler(request, exc: Http404):
        return api.create_response(
            request,
            error_body(
                request,
                code="NOT_FOUND",
                message="요청한 리소스를 찾을 수 없습니다.",
            ),
            status=404,
        )

    @api.exception_handler(HttpError)
    def http_error_handler(request, exc: HttpError):
        return api.create_response(
            request,
            error_body(
                request,
                code=f"HTTP_{exc.status_code}",
                message=str(exc.message),
            ),
            status=exc.status_code,
        )

    @api.exception_handler(Exception)
    def unexpected_error_handler(request, exc: Exception):
        message = str(exc) if settings.DEBUG else "서버 오류가 발생했습니다."

        return api.create_response(
            request,
            error_body(
                request,
                code="INTERNAL_SERVER_ERROR",
                message=message,
            ),
            status=500,
        )
```

**예시 코드: `api.py`**

```python
from ninja import NinjaAPI

from common.api.errors import register_exception_handlers

api = NinjaAPI(title="Service API")

register_exception_handlers(api)
```

**사용 예시**

```python
from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router, Schema
from ninja.pagination import paginate

from common.api.errors import ApiError
from common.api.pagination import StandardPageNumberPagination
from users.models import User

router = Router()


class UserOut(Schema):
    id: int
    email: str
    name: str


@router.get("/users", response=List[UserOut])
@paginate(StandardPageNumberPagination)
def list_users(request):
    return User.objects.order_by("-id")


@router.get("/users/{user_id}", response=UserOut)
def get_user(request, user_id: int):
    return get_object_or_404(User, id=user_id)


@router.post("/users/{user_id}/deactivate")
def deactivate_user(request, user_id: int):
    user = get_object_or_404(User, id=user_id)

    if not user.is_active:
        raise ApiError(
            code="USER_ALREADY_INACTIVE",
            message="이미 비활성화된 사용자입니다.",
            status_code=409,
        )

    user.is_active = False
    user.save(update_fields=["is_active"])
    return {"ok": True}
```

**권장 설정**

```python
# settings.py

NINJA_PAGINATION_CLASS = "common.api.pagination.StandardPageNumberPagination"
NINJA_PAGINATION_PER_PAGE = 20
NINJA_PAGINATION_MAX_PER_PAGE_SIZE = 100
```

핵심은 클라이언트가 `results`와 `error.code`만 믿고 일관되게 처리할 수 있게 만드는 것입니다. 팀 컨벤션으로는 “목록은 무조건 표준 paginator, 실패는 무조건 표준 error envelope”만 강제해도 API 품질이 크게 안정됩니다.