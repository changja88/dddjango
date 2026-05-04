**공통 에러 표준**

아래 표준은 `DomainError`가 HTTP를 모르고, Django Ninja transport 계층만 `ProblemDetail` 응답으로 변환하는 구조입니다. 팀 공통 코드로 복사해서 `config/api.py`에서 설치하면 됩니다.

```python
# common/errors/domain.py
class DomainError(Exception):
    code = "domain_error"
    message = "요청을 처리할 수 없습니다."

    def __init__(self, message: str | None = None, *, code: str | None = None):
        self.message = message or self.message
        self.code = code or self.code
        super().__init__(self.message)


class NotFoundError(DomainError):
    code = "not_found"
    message = "리소스를 찾을 수 없습니다."


class ConflictError(DomainError):
    code = "conflict"
    message = "이미 처리되었거나 충돌하는 요청입니다."


class PermissionDeniedError(DomainError):
    code = "permission_denied"
    message = "이 작업을 수행할 권한이 없습니다."
```

```python
# common/errors/api.py
from http import HTTPStatus
from typing import Any

from django.http import HttpRequest
from ninja import NinjaAPI, Schema
from ninja.errors import HttpError, ValidationError

from common.errors.domain import (
    ConflictError,
    DomainError,
    NotFoundError,
    PermissionDeniedError,
)


class ProblemDetail(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    code: str
    errors: dict[str, Any] | None = None


DOMAIN_STATUS = {
    NotFoundError: HTTPStatus.NOT_FOUND,
    ConflictError: HTTPStatus.CONFLICT,
    PermissionDeniedError: HTTPStatus.FORBIDDEN,
}


def problem_payload(
    request: HttpRequest,
    *,
    status: HTTPStatus,
    code: str,
    detail: str,
    errors: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "type": f"https://api.example.com/problems/{code}",
        "title": status.phrase,
        "status": status.value,
        "detail": detail,
        "instance": request.path,
        "code": code,
    }
    if errors:
        payload["errors"] = errors
    return payload


def install_error_handlers(api: NinjaAPI) -> None:
    @api.exception_handler(DomainError)
    def handle_domain_error(request: HttpRequest, exc: DomainError):
        status = DOMAIN_STATUS.get(type(exc), HTTPStatus.UNPROCESSABLE_ENTITY)
        return api.create_response(
            request,
            problem_payload(request, status=status, code=exc.code, detail=exc.message),
            status=status.value,
        )

    @api.exception_handler(ValidationError)
    def handle_validation_error(request: HttpRequest, exc: ValidationError):
        return api.create_response(
            request,
            problem_payload(
                request,
                status=HTTPStatus.UNPROCESSABLE_ENTITY,
                code="validation_error",
                detail="요청 값이 올바르지 않습니다.",
                errors={"fields": exc.errors},
            ),
            status=422,
        )

    @api.exception_handler(HttpError)
    def handle_http_error(request: HttpRequest, exc: HttpError):
        status = HTTPStatus(exc.status_code)
        return api.create_response(
            request,
            problem_payload(
                request,
                status=status,
                code="http_error",
                detail=str(exc.message),
            ),
            status=exc.status_code,
        )
```

```python
# config/api.py
from ninja import NinjaAPI

from common.errors.api import ProblemDetail, install_error_handlers
from products.api import router as products_router

api = NinjaAPI(title="Service API")
install_error_handlers(api)

api.add_router("/products/", products_router)
```

```python
# products/api.py
from ninja import Router

from common.errors.api import ProblemDetail
from common.errors.domain import NotFoundError

router = Router(tags=["products"])


@router.get(
    "/{product_id}",
    response={200: dict, 404: ProblemDetail, 422: ProblemDetail},
)
def get_product(request, product_id: int) -> dict:
    product = None
    if product is None:
        raise NotFoundError("상품을 찾을 수 없습니다.", code="product_not_found")
    return {"id": product_id}
```

핵심 규칙은 다음입니다.

`DomainError` 계층에는 `status_code`, `request`, `response`를 넣지 않습니다. 도메인은 실패 의미만 표현하고, HTTP 상태 코드와 RFC 9457 `ProblemDetail` 변환은 `install_error_handlers()`에서만 담당합니다.

엔드포인트는 Django Ninja `Router`와 `Schema`를 사용하고, `response={404: ProblemDetail, 422: ProblemDetail}`처럼 문서화 가능한 다중 응답 스키마를 명시합니다.

검증 단계:

```bash
python manage.py check
python manage.py test
curl -i http://localhost:8000/api/products/999
```

기대 응답은 `application/json` 본문에 `type`, `title`, `status`, `detail`, `instance`, `code`가 포함되고, 도메인 예외 메시지가 HTTP 구현 세부사항 없이 `detail`로 변환되는 것입니다.

---
> **관련 스킬 참조:**
> - API 오류 응답 설계 → **architecture-api** 스킬
> - Django Ninja 예외 처리 구현 → **implementation-django-ninja** 스킬