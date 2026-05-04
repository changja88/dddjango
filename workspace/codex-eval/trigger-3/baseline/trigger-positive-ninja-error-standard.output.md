**주요 내용**

현재 `/private/tmp/dddjango-codex-eval`은 비어 있고, 샌드박스가 읽기 전용이라 파일 생성은 차단되었습니다. 그래서 실제 적용은 못 했고, Django Ninja 공통 에러 응답 표준을 아래 구조로 잡으면 됩니다.

표준은 RFC 9457 Problem Details입니다.

```json
{
  "type": "about:blank",
  "title": "Validation Failed",
  "status": 422,
  "detail": "Request validation failed.",
  "instance": "/api/orders/",
  "errors": []
}
```

권장 파일 구성:

```text
core/api/errors.py
config/api.py
config/urls.py
```

핵심 구현:

```python
# core/api/errors.py
from collections.abc import Mapping
from typing import Any

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, JsonResponse
from ninja import Schema
from ninja.errors import AuthenticationError, AuthorizationError, HttpError, ValidationError

PROBLEM_JSON = "application/problem+json"


class ProblemDetail(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str


class APIError(Exception):
    status_code = 400
    type = "about:blank"
    title = "Bad Request"

    def __init__(self, detail: str, *, extra: Mapping[str, Any] | None = None) -> None:
        self.detail = detail
        self.extra = dict(extra or {})
        super().__init__(detail)


class ConflictError(APIError):
    status_code = 409
    title = "Conflict"


def problem_response(request: HttpRequest, *, status: int, title: str, detail: str, type: str = "about:blank", extra: Mapping[str, Any] | None = None) -> JsonResponse:
    body = ProblemDetail(type=type, title=title, status=status, detail=detail, instance=request.path).model_dump()
    body.update(extra or {})
    return JsonResponse(body, status=status, content_type=PROBLEM_JSON)


def register_problem_handlers(api) -> None:
    @api.exception_handler(APIError)
    def handle_api_error(request: HttpRequest, exc: APIError) -> JsonResponse:
        return problem_response(request, type=exc.type, title=exc.title, status=exc.status_code, detail=exc.detail, extra=exc.extra)

    @api.exception_handler(ValidationError)
    def handle_validation_error(request: HttpRequest, exc: ValidationError) -> JsonResponse:
        return problem_response(request, type="https://api.example.com/problems/validation-failed", title="Validation Failed", status=422, detail="Request validation failed.", extra={"errors": exc.errors})

    @api.exception_handler(AuthenticationError)
    def handle_auth_error(request: HttpRequest, exc: AuthenticationError) -> JsonResponse:
        return problem_response(request, title="Unauthorized", status=401, detail=str(exc) or "Authentication failed.")

    @api.exception_handler(AuthorizationError)
    @api.exception_handler(PermissionDenied)
    def handle_forbidden(request: HttpRequest, exc: Exception) -> JsonResponse:
        return problem_response(request, title="Forbidden", status=403, detail=str(exc) or "Permission denied.")

    @api.exception_handler(Http404)
    def handle_not_found(request: HttpRequest, exc: Http404) -> JsonResponse:
        return problem_response(request, title="Not Found", status=404, detail=str(exc) or "The requested resource was not found.")

    @api.exception_handler(HttpError)
    def handle_http_error(request: HttpRequest, exc: HttpError) -> JsonResponse:
        return problem_response(request, title="HTTP Error", status=exc.status_code, detail=str(exc))

    @api.exception_handler(Exception)
    def handle_unexpected_error(request: HttpRequest, exc: Exception) -> JsonResponse:
        detail = str(exc) if settings.DEBUG else "An unexpected error occurred."
        return problem_response(request, title="Internal Server Error", status=500, detail=detail)
```

연결:

```python
# config/api.py
from ninja import NinjaAPI

from core.api.errors import register_problem_handlers

api = NinjaAPI()
register_problem_handlers(api)
```

```python
# config/urls.py
from django.urls import path

from config.api import api

urlpatterns = [
    path("api/", api.urls),
]
```

검증은 실행하지 못했습니다. 현재 워크스페이스가 비어 있고 쓰기 권한도 차단되어 있습니다.

---
> **관련 스킬 참조:**
> - 공통 API 에러 응답과 RFC 9457 표준화 → **architecture-api** 스킬
> - Django Ninja exception_handler 구현 → **implementation-django-ninja** 스킬