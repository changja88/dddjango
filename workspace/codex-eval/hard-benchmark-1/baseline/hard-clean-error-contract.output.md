현재 디렉터리에 코드가 없어서 실제 패치 대신, Django Ninja 기준의 리팩터링 방향을 예시로 정리합니다.

핵심 방향은 이겁니다.

`service -> dict | None | "ERROR_CODE"` 구조를 버리고, application service는 성공 시 명시적인 결과 객체를 반환하고 실패 시 도메인/application 예외를 던지게 만듭니다. API layer는 성공 응답 조립만 맡고, 실패 응답은 Ninja exception handler가 일관되게 변환합니다.

```text
app/
  domain/
    exceptions.py
  application/
    services.py
    dto.py
  api/
    router.py
    schemas.py
    exception_handlers.py
  tests/
    application/
    api/
```

예외는 문자열 코드 대신 타입으로 표현합니다.

```python
# domain/exceptions.py

class DomainError(Exception):
    code = "domain_error"
    status_code = 400

    def __init__(self, message: str | None = None):
        self.message = message or self.code
        super().__init__(self.message)


class OrderNotFound(DomainError):
    code = "order_not_found"
    status_code = 404


class OrderAlreadyPaid(DomainError):
    code = "order_already_paid"
    status_code = 409
```

application service는 HTTP를 모르게 둡니다. `JsonResponse`, Ninja `Schema`, status code 같은 API 세부사항을 반환하지 않습니다.

```python
# application/services.py

from app.domain.exceptions import OrderAlreadyPaid, OrderNotFound
from app.application.dto import PayOrderResult


class PayOrderService:
    def __init__(self, order_repository, payment_gateway):
        self.order_repository = order_repository
        self.payment_gateway = payment_gateway

    def execute(self, order_id: int) -> PayOrderResult:
        order = self.order_repository.get_by_id(order_id)

        if order is None:
            raise OrderNotFound()

        if order.is_paid:
            raise OrderAlreadyPaid()

        payment = self.payment_gateway.pay(order.total_price)
        order.mark_paid(payment.transaction_id)
        self.order_repository.save(order)

        return PayOrderResult(
            order_id=order.id,
            transaction_id=payment.transaction_id,
        )
```

```python
# application/dto.py

from dataclasses import dataclass


@dataclass(frozen=True)
class PayOrderResult:
    order_id: int
    transaction_id: str
```

API 코드는 성공 흐름만 남깁니다.

```python
# api/router.py

from ninja import Router
from app.api.schemas import PayOrderResponse
from app.application.services import PayOrderService

router = Router()


@router.post("/orders/{order_id}/pay", response={200: PayOrderResponse})
def pay_order(request, order_id: int):
    service = PayOrderService(
        order_repository=request.app_state.order_repository,
        payment_gateway=request.app_state.payment_gateway,
    )

    result = service.execute(order_id)

    return PayOrderResponse(
        order_id=result.order_id,
        transaction_id=result.transaction_id,
    )
```

Django Ninja의 exception handler에서 도메인 예외를 API 응답으로 바꿉니다.

```python
# api/exception_handlers.py

from ninja import NinjaAPI
from app.domain.exceptions import DomainError


def register_exception_handlers(api: NinjaAPI) -> None:
    @api.exception_handler(DomainError)
    def handle_domain_error(request, exc: DomainError):
        return api.create_response(
            request,
            {
                "code": exc.code,
                "message": exc.message,
            },
            status=exc.status_code,
        )
```

```python
# api/__init__.py 또는 urls.py

from ninja import NinjaAPI
from app.api.exception_handlers import register_exception_handlers

api = NinjaAPI()
register_exception_handlers(api)
```

테스트는 세 층으로 나누는 게 좋습니다.

서비스 테스트는 HTTP 없이 도메인/application 동작만 봅니다.

```python
def test_pay_order_raises_when_order_not_found(order_repository, payment_gateway):
    service = PayOrderService(order_repository, payment_gateway)

    with pytest.raises(OrderNotFound):
        service.execute(order_id=1)


def test_pay_order_returns_result(order_repository, payment_gateway, unpaid_order):
    order_repository.add(unpaid_order)

    service = PayOrderService(order_repository, payment_gateway)

    result = service.execute(order_id=unpaid_order.id)

    assert result.order_id == unpaid_order.id
    assert result.transaction_id
```

API 테스트는 예외가 응답으로 잘 변환되는지만 봅니다.

```python
def test_pay_order_returns_404_when_order_not_found(client):
    response = client.post("/api/orders/999/pay")

    assert response.status_code == 404
    assert response.json() == {
        "code": "order_not_found",
        "message": "order_not_found",
    }
```

리팩터링 순서는 작게 가는 게 안전합니다.

1. 기존 문자열 에러코드별로 예외 클래스를 만든다.
2. 서비스 하나를 골라 `None | str` 반환을 `raise DomainError`로 바꾼다.
3. API의 `if result is None`, `if result == "..."` 분기를 제거한다.
4. Ninja exception handler를 등록한다.
5. 기존 API 테스트는 status/body 기준으로 유지하고, service 테스트는 예외 발생 기준으로 바꾼다.
6. 같은 패턴을 다른 service로 반복 적용한다.

중요한 기준은 application service가 “요청 실패”를 반환값으로 숨기지 않는 것입니다. 실패는 예외 타입으로 드러내고, HTTP 표현은 API 경계에서 한 번만 처리하면 API 코드의 조건문이 크게 줄어듭니다.