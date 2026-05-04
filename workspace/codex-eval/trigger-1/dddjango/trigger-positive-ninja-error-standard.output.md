실제 파일 생성은 못 했습니다. 현재 `/private/tmp/dddjango-codex-eval`은 비어 있고, sandbox가 read-only라 코드 작성과 pytest 실행이 불가능했습니다. 대신 이 프로젝트 정책에 맞춰 **DRF 없이 Django Ninja 기준**으로 공통 에러 응답 표준을 바로 붙여 넣을 수 있게 정리합니다.

**표준안**

모든 API 에러는 RFC 9457 Problem Details 형식으로 통일합니다.

```json
{
  "type": "urn:problem:validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "Request validation failed.",
  "instance": "/api/users/",
  "code": "validation_error",
  "errors": [
    {
      "path": "body.email",
      "message": "Input should be a valid email address",
      "code": "invalid"
    }
  ]
}
```

권장 상태 코드는 다음처럼 고정합니다.

```text
400 bad_request
401 authentication_required
403 permission_denied
404 not_found
409 conflict
422 validation_error
429 rate_limited
500 internal_server_error
```

**GREEN 최소 구현**

`config/api_errors.py`

```python
from http import HTTPStatus
from typing import Any

from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import Http404, HttpRequest, JsonResponse
from ninja import NinjaAPI, Schema
from ninja.errors import AuthenticationError, AuthorizationError, HttpError, ValidationError


class ProblemError(Schema):
    path: str
    message: str
    code: str = "invalid"


class ProblemDetail(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    code: str
    errors: list[ProblemError] | None = None


class DomainError(Exception):
    status_code = 400
    code = "bad_request"
    title = "Bad Request"

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class ConflictError(DomainError):
    status_code = 409
    code = "conflict"
    title = "Conflict"


def problem_response(
    request: HttpRequest,
    *,
    status: int,
    code: str,
    detail: str,
    title: str | None = None,
    errors: list[ProblemError] | None = None,
) -> JsonResponse:
    problem = ProblemDetail(
        type=f"urn:problem:{code.replace('_', '-')}",
        title=title or _title_for_status(status),
        status=status,
        detail=detail,
        instance=request.path,
        code=code,
        errors=errors,
    )
    return JsonResponse(
        _schema_dump(problem),
        status=status,
        content_type="application/problem+json",
    )


def install_exception_handlers(api: NinjaAPI) -> None:
    @api.exception_handler(ValidationError)
    def handle_validation_error(request: HttpRequest, exc: ValidationError) -> JsonResponse:
        return problem_response(
            request,
            status=422,
            code="validation_error",
            title="Validation Error",
            detail="Request validation failed.",
            errors=_validation_errors(exc),
        )

    @api.exception_handler(AuthenticationError)
    def handle_authentication_error(request: HttpRequest, exc: AuthenticationError) -> JsonResponse:
        return problem_response(
            request,
            status=401,
            code="authentication_required",
            title="Authentication Required",
            detail="Authentication credentials were missing or invalid.",
        )

    @api.exception_handler(AuthorizationError)
    @api.exception_handler(PermissionDenied)
    def handle_permission_error(request: HttpRequest, exc: Exception) -> JsonResponse:
        return problem_response(
            request,
            status=403,
            code="permission_denied",
            title="Permission Denied",
            detail="You do not have permission to perform this action.",
        )

    @api.exception_handler(Http404)
    def handle_not_found(request: HttpRequest, exc: Http404) -> JsonResponse:
        return problem_response(
            request,
            status=404,
            code="not_found",
            title="Not Found",
            detail="The requested resource was not found.",
        )

    @api.exception_handler(HttpError)
    def handle_http_error(request: HttpRequest, exc: HttpError) -> JsonResponse:
        status = getattr(exc, "status_code", 400)
        return problem_response(
            request,
            status=status,
            code=_code_for_status(status),
            detail=str(exc),
        )

    @api.exception_handler(DomainError)
    def handle_domain_error(request: HttpRequest, exc: DomainError) -> JsonResponse:
        return problem_response(
            request,
            status=exc.status_code,
            code=exc.code,
            title=exc.title,
            detail=exc.detail,
        )

    @api.exception_handler(IntegrityError)
    def handle_integrity_error(request: HttpRequest, exc: IntegrityError) -> JsonResponse:
        return problem_response(
            request,
            status=409,
            code="conflict",
            title="Conflict",
            detail="The request conflicts with the current resource state.",
        )

    @api.exception_handler(Exception)
    def handle_unexpected_error(request: HttpRequest, exc: Exception) -> JsonResponse:
        return problem_response(
            request,
            status=500,
            code="internal_server_error",
            title="Internal Server Error",
            detail="An unexpected error occurred.",
        )


def _validation_errors(exc: ValidationError) -> list[ProblemError]:
    errors = getattr(exc, "errors", None)
    if not errors:
        return []

    return [
        ProblemError(
            path=".".join(str(part) for part in error.get("loc", [])),
            message=str(error.get("msg", "Invalid value.")),
            code=str(error.get("type", "invalid")),
        )
        for error in errors
    ]


def _schema_dump(schema: Schema) -> dict[str, Any]:
    if hasattr(schema, "model_dump"):
        return schema.model_dump(exclude_none=True)
    return schema.dict(exclude_none=True)


def _title_for_status(status: int) -> str:
    try:
        return HTTPStatus(status).phrase
    except ValueError:
        return "Error"


def _code_for_status(status: int) -> str:
    return {
        400: "bad_request",
        401: "authentication_required",
        403: "permission_denied",
        404: "not_found",
        409: "conflict",
        422: "validation_error",
        429: "rate_limited",
    }.get(status, "internal_server_error" if status >= 500 else "bad_request")
```

`config/api.py`

```python
from ninja import NinjaAPI

from config.api_errors import install_exception_handlers
from products.api import router as products_router

api = NinjaAPI(title="Project API", version="1.0.0")
install_exception_handlers(api)

api.add_router("/products/", products_router)
```

`config/urls.py`

```python
from django.urls import path

from config.api import api

urlpatterns = [
    path("api/", api.urls),
]
```

**RED 테스트 예시**

`tests/isolated/api/test_problem_details.py`

```python
from django.http import Http404
from ninja import NinjaAPI
from ninja.testing import TestClient

from config.api_errors import ConflictError, install_exception_handlers


def test_api_error_validation_error_returns_problem_details():
    api = NinjaAPI()
    install_exception_handlers(api)

    @api.post("/items")
    def create_item(request, quantity: int):
        return {"quantity": quantity}

    client = TestClient(api)

    response = client.post("/items", json={"quantity": "invalid"})

    assert response.status_code == 422
    assert response["content-type"] == "application/problem+json"
    assert response.json()["type"] == "urn:problem:validation-error"
    assert response.json()["code"] == "validation_error"
    assert response.json()["errors"]


def test_api_error_not_found_returns_problem_details():
    api = NinjaAPI()
    install_exception_handlers(api)

    @api.get("/items/{item_id}")
    def get_item(request, item_id: int):
        raise Http404

    client = TestClient(api)

    response = client.get("/items/1")

    assert response.status_code == 404
    assert response.json()["code"] == "not_found"
    assert response.json()["instance"] == "/items/1"


def test_api_error_domain_conflict_returns_problem_details():
    api = NinjaAPI()
    install_exception_handlers(api)

    @api.post("/orders")
    def create_order(request):
        raise ConflictError("Order already exists.")

    client = TestClient(api)

    response = client.post("/orders")

    assert response.status_code == 409
    assert response.json()["code"] == "conflict"
    assert response.json()["detail"] == "Order already exists."
```

예상 RED 실패 이유: `config.api_errors` 모듈, `install_exception_handlers`, `ConflictError`가 아직 없기 때문에 import 또는 assertion 단계에서 실패해야 합니다.

**REFACTOR 방향**

도메인별 예외는 각 앱의 `exceptions.py`에 두고 `DomainError`를 상속시키면 됩니다. 예를 들어 `orders.exceptions.OrderAlreadyPaidError(status_code=409, code="order_already_paid")`처럼 문제 유형을 안정적인 `code`로 관리하면 클라이언트가 문자열 메시지 대신 `code`에 의존할 수 있습니다.

실행 명령은 실제 프로젝트에서 다음처럼 두면 됩니다.

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/api/test_problem_details.py -q
```

---
> **관련 스킬 참조:**
> - API 오류 형식/RFC 9457 → **architecture-api** 스킬
> - Django Ninja 예외 핸들러/Schema/Router → **implementation-django-ninja** 스킬
> - pytest RED-GREEN-REFACTOR → **implementation-tdd** 스킬