아래 내용을 `docs/api-response-standard.md` 같은 팀 문서로 바로 넣으면 됩니다. Django Ninja 공식 문서 기준으로 `@paginate`/`PaginationBase`와 `api.exception_handler`를 사용합니다. 참고: [Django Ninja Pagination](https://django-ninja.dev/guides/response/pagination/), [Handling errors](https://django-ninja.dev/guides/errors/).

## Django Ninja API Response Convention

### 1. Pagination 표준

목록 API는 모두 동일한 page 기반 응답을 사용한다.

요청:

```http
GET /api/users?page=1&page_size=20
```

응답:

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 0,
  "total_pages": 0,
  "has_next": false,
  "has_previous": false
}
```

규칙:

- 목록 응답 필드는 항상 `items`를 사용한다.
- `page`는 1부터 시작한다.
- 기본 `page_size`는 `20`, 최대값은 `100`으로 제한한다.
- 정렬은 API 내부에서 명시한다. 페이지네이션 클래스가 임의 정렬을 만들지 않는다.
- QuerySet을 반환하는 목록 API는 `@paginate(StandardPagePagination)`을 붙인다.
- 무한 스크롤이 필요한 API만 별도 cursor pagination을 사용하고, 일반 목록에는 섞지 않는다.

예시 코드:

```python
# common/api/pagination.py

from math import ceil
from typing import Any, List

from ninja import Field, Schema
from ninja.pagination import PaginationBase


class StandardPagePagination(PaginationBase):
    class Input(Schema):
        page: int = Field(1, ge=1)
        page_size: int = Field(20, ge=1, le=100)

    class Output(Schema):
        items: List[Any]
        page: int
        page_size: int
        total: int
        total_pages: int
        has_next: bool
        has_previous: bool

    items_attribute = "items"

    def paginate_queryset(self, queryset, pagination, **params):
        page = pagination.page
        page_size = pagination.page_size
        offset = (page - 1) * page_size

        try:
            total = queryset.count()
        except TypeError:
            total = len(queryset)

        total_pages = ceil(total / page_size) if total else 0

        return {
            "items": queryset[offset : offset + page_size],
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        }
```

사용 예시:

```python
# users/api.py

from typing import List

from ninja import Router
from ninja.pagination import paginate

from common.api.pagination import StandardPagePagination
from users.models import User
from users.schemas import UserOut

router = Router()


@router.get("/users", response=List[UserOut])
@paginate(StandardPagePagination)
def list_users(request):
    return User.objects.order_by("-id")
```

---

### 2. Error Response 표준

모든 에러 응답은 아래 형식을 따른다.

```json
{
  "error": {
    "code": "validation_error",
    "message": "요청 값이 올바르지 않습니다.",
    "details": []
  },
  "request_id": "optional-request-id"
}
```

규칙:

- 에러 본문 최상위 필드는 항상 `error`다.
- `code`는 클라이언트가 분기 처리할 수 있는 안정적인 snake_case 문자열이다.
- `message`는 사용자 또는 클라이언트 개발자가 이해할 수 있는 짧은 문장이다.
- `details`는 검증 실패처럼 필드 단위 정보가 있을 때만 채운다.
- 500 에러는 내부 예외 메시지를 노출하지 않는다.
- 도메인/비즈니스 에러는 `ApiError`를 상속해서 명시적으로 던진다.
- view 함수 안에서 임의 dict로 에러를 직접 만들지 않는다.

예시 코드:

```python
# common/api/errors.py

import logging
from typing import Any, Dict, List, Optional

from django.http import Http404
from ninja import NinjaAPI, Schema
from ninja.errors import (
    AuthenticationError,
    AuthorizationError,
    HttpError,
    ValidationError,
)

logger = logging.getLogger(__name__)


class ErrorDetail(Schema):
    loc: Optional[List[Any]] = None
    message: str
    type: Optional[str] = None


class ErrorObject(Schema):
    code: str
    message: str
    details: List[ErrorDetail] = []


class ErrorResponse(Schema):
    error: ErrorObject
    request_id: Optional[str] = None


class ApiError(Exception):
    status_code = 400
    code = "bad_request"
    message = "잘못된 요청입니다."

    def __init__(
        self,
        message: Optional[str] = None,
        *,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[List[Dict[str, Any]]] = None,
    ):
        self.message = message or self.message
        self.code = code or self.code
        self.status_code = status_code or self.status_code
        self.details = details or []


def error_body(
    request,
    *,
    code: str,
    message: str,
    details: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or [],
        },
        "request_id": request.headers.get("X-Request-ID"),
    }


def register_error_handlers(api: NinjaAPI) -> None:
    @api.exception_handler(ApiError)
    def handle_api_error(request, exc: ApiError):
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
    def handle_validation_error(request, exc: ValidationError):
        details = [
            {
                "loc": item.get("loc"),
                "message": item.get("msg", "Invalid value"),
                "type": item.get("type"),
            }
            for item in exc.errors
        ]

        return api.create_response(
            request,
            error_body(
                request,
                code="validation_error",
                message="요청 값이 올바르지 않습니다.",
                details=details,
            ),
            status=422,
        )

    @api.exception_handler(AuthenticationError)
    def handle_authentication_error(request, exc):
        return api.create_response(
            request,
            error_body(
                request,
                code="authentication_failed",
                message="인증이 필요합니다.",
            ),
            status=401,
        )

    @api.exception_handler(AuthorizationError)
    def handle_authorization_error(request, exc):
        return api.create_response(
            request,
            error_body(
                request,
                code="permission_denied",
                message="권한이 없습니다.",
            ),
            status=403,
        )

    @api.exception_handler(Http404)
    def handle_not_found(request, exc):
        return api.create_response(
            request,
            error_body(
                request,
                code="not_found",
                message="요청한 리소스를 찾을 수 없습니다.",
            ),
            status=404,
        )

    @api.exception_handler(HttpError)
    def handle_http_error(request, exc: HttpError):
        return api.create_response(
            request,
            error_body(
                request,
                code="http_error",
                message=str(exc),
            ),
            status=exc.status_code,
        )

    @api.exception_handler(Exception)
    def handle_unexpected_error(request, exc: Exception):
        logger.exception("Unhandled API error")

        return api.create_response(
            request,
            error_body(
                request,
                code="internal_server_error",
                message="서버 오류가 발생했습니다.",
            ),
            status=500,
        )
```

API 초기화 예시:

```python
# project/api.py

from ninja import NinjaAPI

from common.api.errors import register_error_handlers

api = NinjaAPI(title="Project API")

register_error_handlers(api)
```

도메인 에러 예시:

```python
# orders/errors.py

from common.api.errors import ApiError


class OrderAlreadyCanceled(ApiError):
    status_code = 409
    code = "order_already_canceled"
    message = "이미 취소된 주문입니다."
```

사용 예시:

```python
if order.is_canceled:
    raise OrderAlreadyCanceled()
```

### 3. 팀 체크리스트

- 목록 API는 `items/page/page_size/total/total_pages/has_next/has_previous` 형식을 사용한다.
- 목록 API는 반드시 명시적 `order_by()`를 가진 QuerySet을 반환한다.
- 에러 응답은 항상 `{"error": ..., "request_id": ...}` 형식이다.
- 비즈니스 예외는 `ApiError` 하위 클래스로 정의한다.
- validation/auth/not_found/500은 전역 exception handler에서 처리한다.
- view 함수에서 `return 400, {...}` 형태의 임의 에러 응답을 만들지 않는다.
- 500 응답에는 원본 exception 메시지, stack trace, SQL, 환경변수 값을 노출하지 않는다.