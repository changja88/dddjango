현재 `/private/tmp/dddjango-codex-eval`은 비어 있고 세션이 read-only라 파일을 직접 생성하진 못했습니다. 아래는 팀 표준으로 그대로 복사해 쓸 수 있는 Django Ninja 공통 에러 응답 기준입니다.

**표준**
모든 API 에러는 RFC 9457 Problem Details 형식으로 반환합니다.

```json
{
  "type": "https://api.example.com/problems/resource-not-found",
  "title": "Resource Not Found",
  "status": 404,
  "detail": "Requested resource was not found.",
  "instance": "/api/v1/orders/1"
}
```

도메인 계층은 HTTP 상태 코드를 알지 않고, API 계층의 exception handler가 도메인 예외를 Problem Details로 변환합니다.

```python
# common/domain_errors.py

class DomainError(Exception):
    code = "domain_error"
    message = "Domain rule was violated."

    def __init__(self, message: str | None = None, **context: object) -> None:
        self.message = message or self.message
        self.context = context
        super().__init__(self.message)


class ResourceNotFound(DomainError):
    code = "resource_not_found"
    message = "Requested resource was not found."


class ConflictError(DomainError):
    code = "conflict"
    message = "Resource conflict occurred."


class PermissionDeniedByPolicy(DomainError):
    code = "permission_denied"
    message = "You do not have permission to perform this action."
```

```python
# common/api_errors.py

from typing import Any

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404, JsonResponse
from ninja import NinjaAPI, Schema
from ninja.errors import (
    AuthenticationError,
    AuthorizationError,
    HttpError,
    ValidationError,
)

from common.domain_errors import (
    ConflictError,
    DomainError,
    PermissionDeniedByPolicy,
    ResourceNotFound,
)


class ProblemDetail(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str
    code: str | None = None


DOMAIN_ERROR_MAP: dict[type[DomainError], tuple[int, str, str]] = {
    ResourceNotFound: (404, "Resource Not Found", "resource-not-found"),
    ConflictError: (409, "Conflict", "conflict"),
    PermissionDeniedByPolicy: (403, "Forbidden", "forbidden"),
    DomainError: (422, "Unprocessable Entity", "domain-error"),
}


def problem_response(
    request,
    *,
    status: int,
    title: str,
    detail: str,
    problem_type: str = "about:blank",
    code: str | None = None,
    extra: dict[str, Any] | None = None,
) -> JsonResponse:
    body = ProblemDetail(
        type=problem_type,
        title=title,
        status=status,
        detail=detail,
        instance=request.path,
        code=code,
    ).dict(exclude_none=True)

    if extra:
        body.update(extra)

    return JsonResponse(
        body,
        status=status,
        content_type="application/problem+json",
    )


def problem_type(slug: str) -> str:
    return f"https://api.example.com/problems/{slug}"


def register_exception_handlers(api: NinjaAPI) -> None:
    @api.exception_handler(DomainError)
    def handle_domain_error(request, exc: DomainError):
        status, title, slug = DOMAIN_ERROR_MAP.get(type(exc), DOMAIN_ERROR_MAP[DomainError])
        return problem_response(
            request,
            status=status,
            title=title,
            detail=exc.message,
            problem_type=problem_type(slug),
            code=exc.code,
            extra=exc.context,
        )

    @api.exception_handler(ValidationError)
    def handle_validation_error(request, exc: ValidationError):
        return problem_response(
            request,
            status=422,
            title="Validation Failed",
            detail="Request validation failed.",
            problem_type=problem_type("validation-failed"),
            code="validation_failed",
            extra={"invalid_params": exc.errors},
        )

    @api.exception_handler(AuthenticationError)
    def handle_authentication_error(request, exc: AuthenticationError):
        return problem_response(
            request,
            status=401,
            title="Unauthorized",
            detail="Authentication is required.",
            problem_type=problem_type("unauthorized"),
            code="unauthorized",
        )

    @api.exception_handler(AuthorizationError)
    @api.exception_handler(PermissionDenied)
    def handle_authorization_error(request, exc):
        return problem_response(
            request,
            status=403,
            title="Forbidden",
            detail="You do not have permission to perform this action.",
            problem_type=problem_type("forbidden"),
            code="forbidden",
        )

    @api.exception_handler(Http404)
    @api.exception_handler(ObjectDoesNotExist)
    def handle_not_found(request, exc):
        return problem_response(
            request,
            status=404,
            title="Not Found",
            detail="Requested resource was not found.",
            problem_type=problem_type("not-found"),
            code="not_found",
        )

    @api.exception_handler(HttpError)
    def handle_http_error(request, exc: HttpError):
        return problem_response(
            request,
            status=exc.status_code,
            title=str(exc),
            detail=str(exc),
            problem_type=problem_type("http-error"),
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
            problem_type=problem_type("internal-server-error"),
            code="internal_server_error",
        )
```

```python
# config/api.py

from ninja import NinjaAPI

from common.api_errors import register_exception_handlers

api = NinjaAPI(title="Project API", version="1.0.0")

register_exception_handlers(api)
```

사용 예시는 도메인/서비스 계층에서 이렇게 HTTP를 모르는 예외만 던지는 방식입니다.

```python
from common.domain_errors import ConflictError, ResourceNotFound

def cancel_order(order_id: int) -> None:
    order = find_order(order_id)
    if order is None:
        raise ResourceNotFound("Order was not found.", order_id=order_id)

    if order.is_shipped:
        raise ConflictError("Shipped orders cannot be canceled.", order_id=order_id)
```

검증은 실행하지 못했습니다. 현재 워크스페이스가 비어 있고 read-only입니다.

---
> **관련 스킬 참조:**
> - Django Ninja exception handler 구현 → **implementation-django-ninja** 스킬
> - RFC 9457 에러 응답 설계 → **architecture-api** 스킬