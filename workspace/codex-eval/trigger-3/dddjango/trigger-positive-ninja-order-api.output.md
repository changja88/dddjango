**주요 내용**

주문 생성은 `Ordering` 바운디드 컨텍스트의 `Order` 애그리거트 생성 유스케이스로 둡니다. API는 얇게 유지하고, Django Ninja `Router`는 요청 검증과 응용 서비스 호출만 담당합니다.

| 도메인 용어 | 정의 | 코드 표현 | 금지 동의어 |
|---|---|---|---|
| 주문 | 고객이 상품 구매를 요청한 거래 | `Order` | `OrderModel` 중심 설계 |
| 주문 접수 | 주문 애그리거트가 생성된 사건 | `OrderPlaced` | `create_order_event` |
| 주문 항목 | 주문 시점의 상품/가격/수량 스냅샷 | `OrderLine` | `cart_item`, `sku_row` |
| 금액 | 통화가 포함된 금전 값 | `Money` | `int amount` 단독 |

컨텍스트 맵은 `Ordering -> Inventory`는 Customer-Supplier 또는 이벤트 기반 ACL, `Ordering -> Payment`는 ACL + Published Language로 둡니다. PG의 `charge`, `payment_token` 같은 외부 어휘는 주문 도메인에 넣지 않습니다.

권장 구조:

```text
ordering/
  domain/model/order/{root.py,value_objects.py,events.py}
  domain/ports/driven/order_repository.py
  application/commands/place_order.py
  adapters/driving/api.py
  adapters/driven/django_order_repository.py
```

핵심 도메인 모델:

```python
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

class DomainError(Exception): ...
class EmptyOrderError(DomainError): ...
class CurrencyMismatch(DomainError): ...

@dataclass(frozen=True)
class OrderId:
    value: UUID

@dataclass(frozen=True)
class Money:
    amount: int
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise DomainError("금액은 0 이상이어야 합니다")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise CurrencyMismatch()
        return Money(self.amount + other.amount, self.currency)

@dataclass(frozen=True)
class OrderLine:
    product_id: UUID
    product_name: str
    unit_price: Money
    quantity: int

    def subtotal(self) -> Money:
        if self.quantity <= 0:
            raise DomainError("수량은 1 이상이어야 합니다")
        return Money(self.unit_price.amount * self.quantity, self.unit_price.currency)

@dataclass(frozen=True)
class OrderPlaced:
    order_id: OrderId
    customer_id: UUID
    occurred_at: datetime = field(default_factory=datetime.now)

class AggregateRoot:
    def __init__(self) -> None:
        self._events: list[object] = []

    def _record_event(self, event: object) -> None:
        self._events.append(event)

    def collect_events(self) -> list[object]:
        events, self._events = self._events, []
        return events

class Order(AggregateRoot):
    """Aggregate Root.
    불변식: 주문 항목은 1개 이상, 총액은 항목 합계, 다른 Aggregate는 ID로만 참조.
    """

    def __init__(self, customer_id: UUID, lines: list[OrderLine]) -> None:
        super().__init__()
        if not lines:
            raise EmptyOrderError()
        self.id = OrderId(uuid4())
        self.customer_id = customer_id
        self.lines = tuple(lines)
        self.total = sum((line.subtotal() for line in lines), Money(0))
        self.version = 0
        self._record_event(OrderPlaced(self.id, customer_id))
```

포트와 응용 서비스:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order, idempotency_key: str) -> None: ...

@dataclass(frozen=True)
class PlaceOrderCommand:
    customer_id: UUID
    lines: list[OrderLine]
    idempotency_key: str

class PlaceOrderService:
    def __init__(self, orders: OrderRepository) -> None:
        self.orders = orders

    def handle(self, cmd: PlaceOrderCommand) -> OrderId:
        order = Order(customer_id=cmd.customer_id, lines=cmd.lines)
        self.orders.save(order, cmd.idempotency_key)
        return order.id
```

Django Ninja API:

```python
from uuid import UUID
from ninja import Header, Router, Schema
from django.http import HttpResponse

router = Router(tags=["orders"])

class OrderLineIn(Schema):
    product_id: UUID
    product_name: str
    unit_price: int
    quantity: int

class PlaceOrderIn(Schema):
    customer_id: UUID
    lines: list[OrderLineIn]

class OrderCreatedOut(Schema):
    order_id: UUID

@router.post("/orders", response={201: OrderCreatedOut})
def place_order(
    request,
    payload: PlaceOrderIn,
    response: HttpResponse,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
) -> tuple[int, OrderCreatedOut]:
    cmd = PlaceOrderCommand(
        customer_id=payload.customer_id,
        lines=[
            OrderLine(i.product_id, i.product_name, Money(i.unit_price), i.quantity)
            for i in payload.lines
        ],
        idempotency_key=idempotency_key,
    )
    order_id = place_order_service().handle(cmd)
    response["Location"] = f"/api/v1/orders/{order_id.value}"
    return 201, OrderCreatedOut(order_id=order_id.value)
```

REST 계약은 `POST /api/v1/orders`, 성공 `201 Created`, `Location` 헤더, 중복 방지를 위한 `Idempotency-Key` 필수입니다. 도메인 예외는 Ninja `@api.exception_handler()`에서 RFC 9457 `application/problem+json`으로 변환합니다. 재고 차감이나 결제 요청은 같은 트랜잭션에서 직접 처리하지 말고 `OrderPlaced` 이후 핸들러/Outbox로 연결합니다. Outbox는 at-least-once delivery이므로 컨슈머는 event_id dedup 또는 도메인 상태 검사로 멱등성을 처리해야 합니다.

검증은 `ninja.testing.TestClient`로 `Idempotency-Key` 누락, 빈 `lines`, 정상 생성 시 `201`과 `Location` 헤더를 확인하면 됩니다. 현재 워크스페이스는 읽기 전용이고 `config.toml`도 없어 파일 생성이나 테스트 실행은 하지 않았습니다.

---
> **관련 스킬 참조:**
> - API 상세 구현 → **implementation-django-ninja** 스킬
> - 주문 애그리거트/이벤트 심화 → **architecture-ddd** 스킬