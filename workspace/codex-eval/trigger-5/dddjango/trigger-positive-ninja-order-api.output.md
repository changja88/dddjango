**주요 내용**

현재 워크스페이스가 비어 있고 읽기 전용이라 파일 생성은 하지 않았습니다. 아래는 Django Ninja + DDD 기준의 주문 생성 API 설계입니다. DRF는 사용하지 않습니다.

**API 설계**

`POST /api/v1/orders`

헤더:
`Authorization: Bearer <token>`  
`Idempotency-Key: <uuid>`

성공:
`201 Created`  
응답 본문은 생성된 주문 식별자와 상태만 반환합니다. 주문 생성 커맨드는 조회 모델을 반환하지 않고, 상세 조회는 별도 `GET /api/v1/orders/{order_id}`로 분리합니다.

오류는 모두 RFC 9457 Problem Details 형식입니다.

```json
{
  "type": "https://api.example.com/problems/order-conflict",
  "title": "Order conflict",
  "status": 409,
  "detail": "The same Idempotency-Key was already used with different payload.",
  "instance": "/api/v1/orders"
}
```

**바운디드 컨텍스트**

| Context | 역할 | 관계 |
|---|---|---|
| Ordering | 주문 생성, 주문 상태 전이, 주문 불변식 보호 | Core Domain |
| Catalog | 상품명/판매 가능 여부 제공 | Customer-Supplier |
| Inventory | 재고 예약 | Published Language + ACL |
| Payment | 결제 승인 | Published Language + ACL |

유비쿼터스 언어:

| 권장 용어 | 의미 | 금지 동의어 |
|---|---|---|
| Order | 고객이 제출한 구매 의사 | CartSnapshot, PurchaseData |
| OrderLine | 주문 내 개별 상품 명세 | Item, ProductRow |
| Money | 통화가 포함된 금액 | amount_int, price |
| place | 주문을 생성한다 | createRaw, insertOrder |

**권장 파일 구조**

```text
orders/
  domain/
    model/order/entities.py
    model/order/value_objects.py
    model/order/events.py
    repositories.py
  application/
    commands.py
    services.py
    unit_of_work.py
  infrastructure/
    django_repositories.py
  api/
    schemas.py
    router.py
config/
  api.py
  urls.py
```

**도메인 핵심**

```python
# orders/domain/model/order/value_objects.py
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


class CurrencyMismatch(Exception):
    pass


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("amount must be greater than or equal to zero")
        if not self.currency:
            raise ValueError("currency is required")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise CurrencyMismatch()
        return Money(self.amount + other.amount, self.currency)


@dataclass(frozen=True)
class OrderId:
    value: UUID


@dataclass(frozen=True)
class ProductId:
    value: UUID


@dataclass(frozen=True)
class Quantity:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("quantity must be greater than zero")
```

```python
# orders/domain/model/order/entities.py
from dataclasses import dataclass, field
from typing import Iterable
from .events import OrderPlacedEvent
from .value_objects import Money, OrderId, ProductId, Quantity


@dataclass
class OrderLine:
    product_id: ProductId
    quantity: Quantity
    unit_price: Money

    @property
    def line_total(self) -> Money:
        return Money(self.unit_price.amount * self.quantity.value, self.unit_price.currency)


@dataclass
class Order:
    """
    Aggregate Root invariants:
    - order must have at least one line
    - all lines must use the same currency
    - total_amount is derived from lines, not supplied by clients
    """
    id: OrderId
    customer_id: str
    lines: list[OrderLine]
    version: int = 0
    _events: list[object] = field(default_factory=list)

    @classmethod
    def place(cls, order_id: OrderId, customer_id: str, lines: Iterable[OrderLine]) -> "Order":
        order_lines = list(lines)
        if not order_lines:
            raise ValueError("order must have at least one line")

        currency = order_lines[0].unit_price.currency
        if any(line.unit_price.currency != currency for line in order_lines):
            raise ValueError("all order lines must use the same currency")

        order = cls(id=order_id, customer_id=customer_id, lines=order_lines)
        order._record_event(OrderPlacedEvent(order_id=order_id.value, customer_id=customer_id))
        return order

    def _record_event(self, event: object) -> None:
        self._events.append(event)

    def collect_events(self) -> list[object]:
        events = self._events[:]
        self._events.clear()
        return events
```

```python
# orders/domain/repositories.py
from abc import ABC, abstractmethod
from .model.order.entities import Order
from .model.order.value_objects import OrderId


class OrderRepository(ABC):
    @abstractmethod
    def find_by_id(self, order_id: OrderId) -> Order | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, order: Order) -> None:
        raise NotImplementedError
```

**Application Service**

```python
# orders/application/services.py
from uuid import uuid4
from .commands import PlaceOrderCommand
from .unit_of_work import UnitOfWork
from orders.domain.model.order.entities import Order, OrderLine
from orders.domain.model.order.value_objects import Money, OrderId, ProductId, Quantity


class PlaceOrderService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def handle(self, command: PlaceOrderCommand) -> OrderId:
        order_id = OrderId(uuid4())
        lines = [
            OrderLine(
                product_id=ProductId(line.product_id),
                quantity=Quantity(line.quantity),
                unit_price=Money(line.unit_price, line.currency),
            )
            for line in command.lines
        ]

        order = Order.place(order_id, command.customer_id, lines)

        with self.uow:
            self.uow.orders.save(order)
            self.uow.save_idempotency(command.idempotency_key, order_id.value)
            self.uow.commit()

        return order_id
```

Repository는 `commit()`하지 않습니다. 트랜잭션 경계는 Application Service의 Unit of Work가 소유합니다. 동시성은 기본적으로 `version` 기반 낙관적 잠금으로 처리합니다.

**Django Ninja Schema / Router**

```python
# orders/api/schemas.py
from decimal import Decimal
from uuid import UUID
from ninja import Schema


class OrderLineIn(Schema):
    product_id: UUID
    quantity: int
    unit_price: Decimal
    currency: str


class PlaceOrderIn(Schema):
    lines: list[OrderLineIn]


class PlaceOrderOut(Schema):
    order_id: UUID
    status: str
```

```python
# orders/api/router.py
from ninja import Header, Router
from django.http import HttpRequest, HttpResponse
from .schemas import PlaceOrderIn, PlaceOrderOut
from orders.application.commands import PlaceOrderCommand
from orders.application.services import PlaceOrderService

router = Router(tags=["orders"])


@router.post(
    "",
    response={201: PlaceOrderOut},
)
def place_order(
    request: HttpRequest,
    response: HttpResponse,
    payload: PlaceOrderIn,
    idempotency_key: str = Header(alias="Idempotency-Key"),
) -> tuple[int, PlaceOrderOut]:
    service = PlaceOrderService.from_django()
    order_id = service.handle(
        PlaceOrderCommand(
            customer_id=str(request.user.id),
            lines=payload.lines,
            idempotency_key=idempotency_key,
        )
    )
    response["Location"] = f"/api/v1/orders/{order_id.value}"
    return 201, PlaceOrderOut(order_id=order_id.value, status="placed")
```

```python
# config/api.py
from ninja import NinjaAPI
from orders.api.router import router as orders_router

api = NinjaAPI(title="Ordering API", version="1.0")
api.add_router("/v1/orders", orders_router)
```

**검증 단계**

```bash
python manage.py test orders
python manage.py test orders.api
python manage.py runserver
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "Idempotency-Key: 018f7f6a-8dcb-7c01-a9f4-4a2a4df1b7a1" \
  -d '{"lines":[{"product_id":"00000000-0000-0000-0000-000000000001","quantity":2,"unit_price":"12000","currency":"KRW"}]}'
```

---
> **관련 스킬 참조:**
> - 주문 애그리거트/도메인 이벤트 보강 → **architecture-ddd** 스킬
> - Django Ninja 실제 구현/테스트 작성 → **implementation-django-ninja** 스킬
> - Unit of Work/Outbox/ACL 구체화 → **architecture-implementation-patterns** 스킬