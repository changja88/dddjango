`/private/tmp/dddjango-codex-eval`가 비어 있고 현재 세션이 read-only라 파일을 직접 생성하진 못했습니다. 대신 이 프로젝트에 바로 넣을 수 있는 Django Ninja 공통 에러 응답 표준을 아래처럼 잡으면 됩니다. 기준은 RFC 9457 Problem Details입니다.

**`common/api/errors.py`**

```python
from __future__ import annotations

from typing import Any

from django.conf import settings
from django.http import Http404, JsonResponse
from ninja import NinjaAPI, Schema
from ninja.errors import (
    AuthenticationError,
    AuthorizationError,
    HttpError,
    ValidationError,
)


class ProblemDetail(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str
    code: str | None = None
    errors: list[dict[str, Any]] | None = None


class ApiError(Exception):
    status_code = 400
    title = "Bad Request"
    code = "bad_request"
    type = "about:blank"

    def __init__(self, detail: str, *, errors: list[dict[str, Any]] | None = None):
        self.detail = detail
        self.errors = errors


class ConflictError(ApiError):
    status_code = 409
    title = "Conflict"
    code = "conflict"


class PermissionDeniedError(ApiError):
    status_code = 403
    title = "Forbidden"
    code = "forbidden"


def problem_response(
    request,
    *,
    status: int,
    title: str,
    detail: str,
    type_: str = "about:blank",
    code: str | None = None,
    errors: list[dict[str, Any]] | None = None,
) -> JsonResponse:
    payload = ProblemDetail(
        type=type_,
        title=title,
        status=status,
        detail=detail,
        instance=request.path,
        code=code,
        errors=errors,
    ).model_dump(exclude_none=True)

    return JsonResponse(
        payload,
        status=status,
        content_type="application/problem+json",
    )


def install_error_handlers(api: NinjaAPI) -> None:
    @api.exception_handler(ApiError)
    def handle_api_error(request, exc: ApiError):
        return problem_response(
            request,
            status=exc.status_code,
            title=exc.title,
            detail=exc.detail,
            type_=exc.type,
            code=exc.code,
            errors=exc.errors,
        )

    @api.exception_handler(ValidationError)
    def handle_validation_error(request, exc: ValidationError):
        return problem_response(
            request,
            status=422,
            title="Validation Error",
            detail="Request validation failed.",
            code="validation_error",
            errors=exc.errors,
        )

    @api.exception_handler(AuthenticationError)
    def handle_authentication_error(request, exc: AuthenticationError):
        return problem_response(
            request,
            status=401,
            title="Unauthorized",
            detail="Authentication credentials were missing or invalid.",
            code="unauthorized",
        )

    @api.exception_handler(AuthorizationError)
    def handle_authorization_error(request, exc: AuthorizationError):
        return problem_response(
            request,
            status=403,
            title="Forbidden",
            detail="You do not have permission to perform this action.",
            code="forbidden",
        )

    @api.exception_handler(Http404)
    def handle_not_found(request, exc: Http404):
        return problem_response(
            request,
            status=404,
            title="Not Found",
            detail="The requested resource was not found.",
            code="not_found",
        )

    @api.exception_handler(HttpError)
    def handle_http_error(request, exc: HttpError):
        status_code = getattr(exc, "status_code", 500)

        return problem_response(
            request,
            status=status_code,
            title=str(exc),
            detail=str(exc),
            code="http_error",
        )

    @api.exception_handler(Exception)
    def handle_unexpected_error(request, exc: Exception):
        detail = str(exc) if settings.DEBUG else "An unexpected error occurred."

        return problem_response(
            request,
            status=500,
            title="Internal Server Error",
            detail=detail,
            code="internal_server_error",
        )
```

**`config/api.py` 적용 예시**

```python
from ninja import NinjaAPI

from common.api.errors import install_error_handlers

api = NinjaAPI(title="API", version="1.0.0")
install_error_handlers(api)

# from apps.products.api import router as products_router
# api.add_router("/products/", products_router)
```

**사용 예시**

```python
from common.api.errors import ConflictError

raise ConflictError("이미 사용 중인 이메일입니다.")
```

응답은 항상 이런 형태로 통일됩니다.

```json
{
  "type": "about:blank",
  "title": "Conflict",
  "status": 409,
  "detail": "이미 사용 중인 이메일입니다.",
  "instance": "/api/users/",
  "code": "conflict"
}
```

검증은 실행하지 못했습니다. 현재 워크스페이스에 프로젝트 파일이 없고 read-only 상태입니다.

---
> **관련 스킬 참조:**
> - API 에러 응답 표준화 → **architecture-api** 스킬
> - Django Ninja 예외 처리 구현 → **implementation-django-ninja** 스킬