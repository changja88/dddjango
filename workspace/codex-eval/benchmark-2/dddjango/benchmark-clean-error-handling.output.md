**표준 원칙**

도메인 예외는 HTTP를 몰라야 합니다. 즉 `status_code`, `response`, `request`, `HttpError`를 domain/service 계층에 넣지 않습니다. 도메인은 “무슨 비즈니스 규칙이 깨졌는가”만 표현하고, API 계층이 Django Ninja exception handler에서 RFC 9457 Problem Details 응답으로 변환합니다.

권장 구조:

```text
orders/
  domain/errors.py
  services.py
  api/schemas.py
  api/router.py
config/
  api.py
```

**1. Domain Exception**

```python
# orders/domain/errors.py
from dataclasses import dataclass


class DomainError(Exception):
    code = "domain_error"
    message = "Domain rule was violated."


@dataclass(frozen=True)
class OrderNotPayable(DomainError):
    order_id: str
    reason: str

    code = "order_not_payable"
    message = "Order cannot be paid."


@dataclass(frozen=True)
class OrderAlreadyCancelled(DomainError):
    order_id: str

    code = "order_already_cancelled"
    message = "Order is already cancelled."
```

도메인 예외는 검색 가능한 `code`, 운영자가 이해할 `message`, 디버깅용 컨텍스트만 가집니다. HTTP 상태는 없습니다.

**2. API Error Schema**

```python
# orders/api/schemas.py
from ninja import Schema


class ProblemDetails(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str | None = None
    code: str
```

**3. Transport Mapping**

```python
# config/api.py
from dataclasses import asdict, is_dataclass

from django.http import HttpRequest, HttpResponse
from ninja import NinjaAPI
from ninja.errors import ValidationError

from orders.domain.errors import (
    DomainError,
    OrderAlreadyCancelled,
    OrderNotPayable,
)
from orders.api.router import router as orders_router

api = NinjaAPI(title="Service API")


DOMAIN_ERROR_STATUS: dict[type[DomainError], int] = {
    OrderNotPayable: 409,
    OrderAlreadyCancelled: 409,
}


def problem_response(
    request: HttpRequest,
    exc: DomainError,
    status: int,
) -> HttpResponse:
    context = asdict(exc) if is_dataclass(exc) else {}

    return api.create_response(
        request,
        {
            "type": f"https://api.example.com/problems/{exc.code}",
            "title": exc.message,
            "status": status,
            "detail": exc.message,
            "instance": request.path,
            "code": exc.code,
            "context": context,
        },
        status=status,
    )


@api.exception_handler(DomainError)
def handle_domain_error(request: HttpRequest, exc: DomainError) -> HttpResponse:
    status = DOMAIN_ERROR_STATUS.get(type(exc), 400)
    return problem_response(request, exc, status)


@api.exception_handler(ValidationError)
def handle_validation_error(
    request: HttpRequest,
    exc: ValidationError,
) -> HttpResponse:
    return api.create_response(
        request,
        {
            "type": "https://api.example.com/problems/validation-error",
            "title": "Validation failed.",
            "status": 422,
            "detail": "Request payload is invalid.",
            "instance": request.path,
            "code": "validation_error",
            "errors": exc.errors,
        },
        status=422,
    )


api.add_router("/orders/", orders_router)
```

팀 표준으로는 `DOMAIN_ERROR_STATUS`만 API 계층에서 관리합니다. 새 도메인 예외가 생기면 도메인 파일에 예외를 추가하고, API mapping에 상태 코드만 연결합니다.

**4. Router는 try/except 하지 않음**

```python
# orders/api/router.py
from ninja import Router

from orders.api.schemas import ProblemDetails
from orders.services import pay_order

router = Router(tags=["orders"])


@router.post(
    "/{order_id}/payments",
    response={204: None, 409: ProblemDetails, 422: ProblemDetails},
)
def pay_order_api(request, order_id: str) -> tuple[int, None]:
    pay_order(order_id=order_id)
    return 204, None
```

엔드포인트에서 `OrderNotPayable`을 잡지 않습니다. 잡기 시작하면 transport 정책이 여러 router로 흩어집니다.

**검증 기준**

```bash
pytest orders/tests/test_domain_errors.py
pytest orders/tests/test_order_api_errors.py
python manage.py check
```

필수 테스트:

```python
def test_domain_errors_do_not_import_django_or_ninja():
    import orders.domain.errors as errors

    assert "ninja" not in errors.__dict__
    assert "django" not in errors.__dict__


def test_order_not_payable_returns_problem_details(client):
    response = client.post("/api/orders/order-1/payments", json={})

    assert response.status_code == 409
    assert response.json()["code"] == "order_not_payable"
    assert response.json()["type"].endswith("/order_not_payable")
```

이 표준의 핵심은 “도메인은 예외를 던지고, API는 표현한다”입니다. DRF 없이 Django Ninja `Schema`, `Router`, `exception_handler`만 사용합니다.