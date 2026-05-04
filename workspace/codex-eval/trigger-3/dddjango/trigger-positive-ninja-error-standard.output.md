**공통 에러 표준**

워크스페이스가 비어 있고 읽기 전용이라 파일은 생성하지 않았습니다. 아래 코드를 팀 표준으로 복사해 사용하면 됩니다. 핵심은 `DomainError`에는 HTTP 상태나 응답 형식을 넣지 않고, Django Ninja `exception_handler`에서만 RFC 9457 Problem Details로 변환하는 것입니다.

```python
# common/api/errors.py
from dataclasses import dataclass, field
from typing import Any

from django.http import Http404, JsonResponse
from ninja import NinjaAPI, Schema
from ninja.errors import AuthenticationError, AuthorizationError, HttpError, ValidationError


class ProblemDetail(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str


class DomainError(Exception):
    code: str = "domain_error"
    message: str = "Domain rule violated"

    def __init__(self, message: str | None = None, **extra: Any) -> None:
        self.message = message or self.message
        self.extra = extra
        super().__init__(self.message)


@dataclass(frozen=True)
class ProblemMapping:
    status: int
    title: str
    type: str


PROBLEM_MAP: dict[str, ProblemMapping] = {
    "domain_error": ProblemMapping(400, "Bad Request", "https://api.example.com/problems/domain-error"),
    "resource_conflict": ProblemMapping(409, "Conflict", "https://api.example.com/problems/resource-conflict"),
    "unprocessable": ProblemMapping(422, "Unprocessable Entity", "https://api.example.com/problems/unprocessable"),
}


def problem_response(
    request,
    *,
    status: int,
    title: str,
    detail: str,
    type: str = "about:blank",
    **extensions: Any,
) -> JsonResponse:
    body = ProblemDetail(
        type=type,
        title=title,
        status=status,
        detail=detail,
        instance=request.path,
    ).model_dump()
    body.update(extensions)
    return JsonResponse(body, status=status, content_type="application/problem+json")


def register_problem_handlers(api: NinjaAPI) -> None:
    @api.exception_handler(DomainError)
    def handle_domain_error(request, exc: DomainError):
        mapping = PROBLEM_MAP.get(exc.code, PROBLEM_MAP["domain_error"])
        return problem_response(
            request,
            status=mapping.status,
            title=mapping.title,
            detail=exc.message,
            type=mapping.type,
            code=exc.code,
            **exc.extra,
        )

    @api.exception_handler(ValidationError)
    def handle_validation_error(request, exc: ValidationError):
        return problem_response(
            request,
            status=422,
            title="Validation Failed",
            detail="Request validation failed.",
            type="https://api.example.com/problems/validation-failed",
            errors=exc.errors,
        )

    @api.exception_handler(AuthenticationError)
    def handle_authentication_error(request, exc: AuthenticationError):
        return problem_response(request, status=401, title="Unauthorized", detail="Authentication is required.")

    @api.exception_handler(AuthorizationError)
    def handle_authorization_error(request, exc: AuthorizationError):
        return problem_response(request, status=403, title="Forbidden", detail="Permission denied.")

    @api.exception_handler(Http404)
    def handle_not_found(request, exc: Http404):
        return problem_response(request, status=404, title="Not Found", detail="Resource not found.")

    @api.exception_handler(HttpError)
    def handle_http_error(request, exc: HttpError):
        return problem_response(request, status=exc.status_code, title=str(exc), detail=str(exc))

    @api.exception_handler(Exception)
    def handle_unexpected_error(request, exc: Exception):
        return problem_response(
            request,
            status=500,
            title="Internal Server Error",
            detail="An unexpected error occurred.",
        )
```

```python
# config/api.py
from ninja import NinjaAPI

from common.api.errors import register_problem_handlers
from products.api import router as products_router

api = NinjaAPI()
register_problem_handlers(api)

api.add_router("/products/", products_router)
```

```python
# domain/products/exceptions.py
from common.api.errors import DomainError


class ProductAlreadyExists(DomainError):
    code = "resource_conflict"
    message = "Product already exists."
```

```python
# products/api.py
from ninja import Router

from domain.products.exceptions import ProductAlreadyExists

router = Router()


@router.post("/", response={201: dict})
def create_product(request) -> tuple[int, dict]:
    raise ProductAlreadyExists(product_id="sku-123")
```

**검증**

```bash
curl -i -X POST http://localhost:8000/api/products/
```

기대값:

```http
HTTP/1.1 409 Conflict
Content-Type: application/problem+json
```

```json
{
  "type": "https://api.example.com/problems/resource-conflict",
  "title": "Conflict",
  "status": 409,
  "detail": "Product already exists.",
  "instance": "/api/products/",
  "code": "resource_conflict",
  "product_id": "sku-123"
}
```

---
> **관련 스킬 참조:**
> - API 에러 응답 설계 → **architecture-api** 스킬
> - Django Ninja 예외 핸들러 구현 → **implementation-django-ninja** 스킬