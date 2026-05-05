**[주요 내용]**

리팩터링 목표는 “서비스가 HTTP 모양의 결과를 만들지 않게” 하는 것입니다. 성공은 명시적 DTO로 반환하고, 실패는 도메인 예외로 올립니다. API는 그 예외를 RFC 9457 Problem Details로만 변환합니다.

```python
# orders/domain/exceptions.py
class DomainError(Exception):
    code = "domain_error"

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class ProductOutOfStock(DomainError):
    code = "product_out_of_stock"


class InvalidOrderState(DomainError):
    code = "invalid_order_state"
```

```python
# orders/application/services.py
from dataclasses import dataclass
from orders.domain.exceptions import ProductOutOfStock, InvalidOrderState

@dataclass(frozen=True)
class PlaceOrderResult:
    order_id: int
    status: str

class StockPolicy:
    def ensure_can_reserve(self, quantity: int, available: int) -> None:
        if quantity <= 0:
            raise InvalidOrderState("quantity must be positive")
        if available < quantity:
            raise ProductOutOfStock("not enough stock")

class OrderApplicationService:
    def __init__(self, repo, stock_policy: StockPolicy) -> None:
        self.repo = repo
        self.stock_policy = stock_policy

    def place_order(self, product_id: int, quantity: int) -> PlaceOrderResult:
        product = self.repo.get_product(product_id)
        self.stock_policy.ensure_can_reserve(quantity, product.available)

        order = self.repo.create_order(product_id=product_id, quantity=quantity)
        self.repo.reserve_stock(product_id=product_id, quantity=quantity)
        return PlaceOrderResult(order_id=order.id, status=order.status)
```

```python
# orders/api/schemas.py
from ninja import Schema

class PlaceOrderIn(Schema):
    product_id: int
    quantity: int

class OrderOut(Schema):
    order_id: int
    status: str

class ProblemDetail(Schema):
    type: str
    title: str
    status: int
    detail: str
```

```python
# config/api.py
from django.http import HttpRequest, JsonResponse
from ninja import NinjaAPI

from orders.domain.exceptions import DomainError, ProductOutOfStock, InvalidOrderState
from orders.api import router as orders_router

api = NinjaAPI()
api.add_router("/orders/", orders_router)

ERROR_MAP = {
    ProductOutOfStock: (409, "Out of stock", "https://example.com/problems/out-of-stock"),
    InvalidOrderState: (422, "Invalid order state", "https://example.com/problems/invalid-order-state"),
}

@api.exception_handler(DomainError)
def handle_domain_error(request: HttpRequest, exc: DomainError) -> JsonResponse:
    status, title, type_url = ERROR_MAP.get(
        type(exc),
        (400, "Domain error", "https://example.com/problems/domain-error"),
    )
    return JsonResponse(
        {"type": type_url, "title": title, "status": status, "detail": exc.detail},
        status=status,
        content_type="application/problem+json",
    )
```

```python
# orders/api.py
from django.http import HttpRequest
from ninja import Router

from orders.api.schemas import OrderOut, PlaceOrderIn, ProblemDetail
from orders.application.services import OrderApplicationService, StockPolicy

router = Router()

@router.post("", response={201: OrderOut, 409: ProblemDetail, 422: ProblemDetail})
def place_order(request: HttpRequest, payload: PlaceOrderIn) -> tuple[int, OrderOut]:
    service = OrderApplicationService(repo=order_repo(), stock_policy=StockPolicy())
    result = service.place_order(payload.product_id, payload.quantity)
    return 201, OrderOut(order_id=result.order_id, status=result.status)
```

Before/After 핵심은 이겁니다.

```python
# before
result = place_order(...)
if result is None:
    return 404, {"error": "not_found"}
if result == "OUT_OF_STOCK":
    return 409, {"error": result}
return result

# after
result = service.place_order(...)
return 201, OrderOut(...)
```

`if`가 많아지는 이유는 API가 도메인 판단까지 묻고 있기 때문입니다. 수량 검증, 재고 예약 가능 여부, 상태 전이 가능 여부는 `StockPolicy` 같은 정책 객체나 Aggregate 메서드 안에서 guard clause로 끝내고, API는 성공 DTO 조립과 예외 변환만 맡깁니다.

테스트는 세 층으로 나눕니다.

```python
# tests/isolated/unit/orders/test_stock_policy.py
import pytest
from orders.application.services import StockPolicy
from orders.domain.exceptions import ProductOutOfStock

def test_stock_policy_quantity_exceeds_available_raises_domain_error():
    policy = StockPolicy()

    with pytest.raises(ProductOutOfStock):
        policy.ensure_can_reserve(quantity=3, available=1)
```

```python
# tests/isolated/integration/orders/test_order_api.py
def test_place_order_out_of_stock_returns_problem_detail(client):
    response = client.post("/api/orders/", json={"product_id": 1, "quantity": 99})

    assert response.status_code == 409
    assert response["content-type"].startswith("application/problem+json")
    assert response.json()["type"].endswith("/out-of-stock")
```

검증 단계:

```bash
python manage.py check
pytest tests/isolated/unit/orders -q
pytest tests/isolated/integration/orders/test_order_api.py -q
```

실제 실행은 하지 않았습니다. 현재 요청은 코드베이스 수정이 아니라 리팩터링 방향 제시로 처리했습니다.

---
> **관련 스킬 참조:**
> - Django Ninja 예외 처리와 Router 구성 → **implementation-django-ninja** 스킬
> - 도메인 예외와 application service 경계 → **architecture-ddd** 스킬
> - 테스트 구조와 RED/GREEN/REFACTOR 적용 → **implementation-test**, **implementation-tdd** 스킬