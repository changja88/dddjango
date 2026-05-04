## [주요 내용]

현재 `/private/tmp/dddjango-codex-eval` 워크스페이스에는 `config.toml`이나 Django 프로젝트 파일이 없어 기존 코드에 맞춘 파일 수정/실행은 불가능했습니다. 아래 설계는 Django 5.x + Django Ninja + DDD/헥사고날 구조를 전제로 한 주문 생성 API 설계안입니다. 이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다.

**접근안**

| 접근 | 설명 | 판단 |
|---|---|---|
| 추천: DDD + Application Service + Repository/UoW | 주문 생성이 재고, 결제, 배송으로 확장될 수 있으므로 도메인 규칙과 트랜잭션 경계를 분리 | 기본안 |
| 단순 Layered Service | 초기 CRUD에는 빠르지만 주문/결제/재고 불변식이 커지면 서비스가 비대해짐 | MVP 한정 |
| CQRS/Saga/Outbox 풀세트 | 결제, 재고, 배송이 비동기 통합이면 적합 | 첫 구현에서는 Outbox만 준비하고 Saga는 결제 도입 시 적용 |

**Bounded Context / Context Map**

| Context | 책임 | 관계 라벨 |
|---|---|---|
| `orders` | 주문 접수, 주문 상태 전이, 주문 총액 스냅샷 | 중심 BC |
| `catalog` | 상품명/판매가 제공 | Customer-Supplier: `orders`가 상품 스냅샷 소비 |
| `inventory` | 재고 예약/해제/확정 | Published Language: `OrderPlaced` → 재고 예약 |
| `payments` | 결제 승인/실패 | ACL + Published Language: PG 어휘를 `PaymentConfirmed`로 번역 |
| `fulfillment` | 출고/배송 요청 | Published Language: `FulfillmentRequested` 소비 |

**Ubiquitous Language**

| 도메인 용어 | 정의 | 코드 표현 | 금지 동의어 |
|---|---|---|---|
| 주문 접수 | 고객의 주문 의사가 시스템에 기록됨 | `Order.place()` / `OrderPlaced` | `create_order`, `insert_order` |
| 주문 항목 | 주문 시점의 상품명, 단가, 수량 스냅샷 | `OrderLine` | `cart_item`, `product_row` |
| 결제 확인 | 결제 BC가 주문 결제 완료를 통보한 사건 | `order.confirm_payment()` / `PaymentConfirmed` | `charge`, `payment_token` |
| 출고 요청 | 결제 완료 후 배송 준비를 요청함 | `FulfillmentRequested` | `shipping_start` |
| 보상 취소 | 후속 단계 실패로 주문을 무효화 | `OrderCancelledForCompensation` | `rollback`, `undo` |

**API**

`POST /api/orders`

Headers:
`Authorization: Bearer <token>`  
`Idempotency-Key: <uuid-v4>`

Request body:

```json
{
  "customer_id": "cus_123",
  "items": [
    {"product_id": "prd_1", "quantity": 2}
  ],
  "shipping_address": {
    "receiver_name": "홍길동",
    "receiver_phone": "010-1234-5678",
    "zipcode": "06236",
    "address1": "서울시 강남구 테헤란로",
    "address2": "10층"
  }
}
```

Response:
`201 Created` + `Location: /api/orders/{order_id}`

```json
{
  "order_id": "ord_123",
  "status": "payment_waiting",
  "total_amount": {"amount": 30000, "currency": "KRW"}
}
```

Errors는 RFC 9457 Problem Details로 통일합니다. 대표적으로 `401` 인증 없음, `403` 고객 불일치, `409` 멱등성 키 충돌 또는 낙관적 잠금 충돌, `422` 상품 판매 불가/수량 오류를 사용합니다.

**파일 구조**

```text
apps/orders/
  domain/
    shared/
      aggregate_root.py
      money.py
      identifiers.py
    model/order/
      root.py
      value_objects.py
      events.py
      repository.py
    events/
      internal/order_placed.py
      published_language/order_created_v1.py
  application/
    commands/place_order.py
    unit_of_work.py
  adapters/
    driving/api/schemas.py
    driving/api/router.py
    driven/persistence/django_order_repository.py
  composition.py
```

**핵심 도메인 모델 스켈레톤**

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

class CurrencyMismatch(Exception): ...
class EmptyOrderError(Exception): ...
class InvalidQuantityError(Exception): ...
class ConcurrencyError(Exception): ...

@dataclass(frozen=True, slots=True)
class Money:
    """INV-1: amount >= 0. INV-2: 서로 다른 통화는 연산 불가."""
    amount: int
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("금액은 0 이상이어야 합니다")
        if not self.currency:
            raise ValueError("통화 코드는 필수입니다")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise CurrencyMismatch(f"{self.currency} != {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, quantity: int) -> "Money":
        if quantity <= 0:
            raise InvalidQuantityError("수량은 1 이상이어야 합니다")
        return Money(self.amount * quantity, self.currency)

@dataclass(frozen=True, slots=True)
class OrderId:
    value: str

@dataclass(frozen=True, slots=True)
class CustomerId:
    value: str

@dataclass(frozen=True, slots=True)
class ProductId:
    value: str

@dataclass(frozen=True, slots=True)
class OrderLine:
    product_id: ProductId
    product_name: str
    quantity: int
    unit_price: Money

    @property
    def subtotal(self) -> Money:
        return self.unit_price * self.quantity
```

```python
class OrderStatus(StrEnum):
    PAYMENT_WAITING = "payment_waiting"
    PAID = "paid"
    FULFILLMENT_REQUESTED = "fulfillment_requested"
    CANCELLED = "cancelled"

@dataclass(frozen=True, slots=True)
class OrderPlaced:
    order_id: OrderId
    customer_id: CustomerId
    total_amount: Money
    occurred_at: datetime = field(default_factory=datetime.now)

class AggregateRoot:
    def __init__(self) -> None:
        self._domain_events: list[object] = []

    def _record_event(self, event: object) -> None:
        self._domain_events.append(event)

    def collect_events(self) -> list[object]:
        events, self._domain_events = self._domain_events, []
        return events

@dataclass
class Order(AggregateRoot):
    """Aggregate Root.
    INV-1: 주문 항목은 1개 이상.
    INV-2: 총액은 주문 항목 subtotal 합계.
    INV-3: 상태 변경은 place/confirm_payment/request_fulfillment/cancel만 허용.
    """
    id: OrderId
    customer_id: CustomerId
    lines: list[OrderLine]
    status: OrderStatus = OrderStatus.PAYMENT_WAITING
    version: int = 0

    def __post_init__(self) -> None:
        AggregateRoot.__init__(self)
        if not self.lines:
            raise EmptyOrderError("주문 항목은 1개 이상이어야 합니다")

    @property
    def total_amount(self) -> Money:
        total = Money(0, self.lines[0].unit_price.currency)
        for line in self.lines:
            total += line.subtotal
        return total

    def place(self) -> None:
        self._record_event(OrderPlaced(self.id, self.customer_id, self.total_amount))
```

**Application Service / Repository**

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

class OrderRepository(ABC):
    @abstractmethod
    def find_by_id(self, order_id: OrderId) -> Order | None: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...

@dataclass(frozen=True, slots=True)
class PlaceOrderCommand:
    customer_id: str
    items: list[dict[str, object]]
    idempotency_key: str

class OrderApplicationService:
    def __init__(self, uow: "UnitOfWork", product_reader: "ProductReader") -> None:
        self._uow = uow
        self._product_reader = product_reader

    def place_order(self, command: PlaceOrderCommand) -> OrderId:
        with self._uow:
            if cached := self._uow.idempotency_keys.find(command.idempotency_key):
                return cached.resource_id

            lines = self._build_lines(command.items)
            order = Order(OrderId.new(), CustomerId(command.customer_id), lines)
            order.place()

            self._uow.orders.save(order)
            self._uow.idempotency_keys.remember(command.idempotency_key, order.id)
            self._uow.commit()

        for event in order.collect_events():
            self._uow.event_bus.dispatch(event)
        return order.id
```

Repository 내부에서는 `commit()`을 호출하지 않습니다. 트랜잭션 경계는 Application Service/UoW가 소유합니다. 저장 시에는 `version` 조건으로 UPDATE하고 실패하면 `ConcurrencyError`를 발생시키는 낙관적 잠금을 기본으로 둡니다.

**Django Ninja 연결**

```python
from ninja import Router, Schema
from ninja.security import django_auth

router = Router(tags=["orders"], auth=django_auth)

class OrderItemIn(Schema):
    product_id: str
    quantity: int

class ShippingAddressIn(Schema):
    receiver_name: str
    receiver_phone: str
    zipcode: str
    address1: str
    address2: str = ""

class PlaceOrderIn(Schema):
    customer_id: str
    items: list[OrderItemIn]
    shipping_address: ShippingAddressIn

class MoneyOut(Schema):
    amount: int
    currency: str

class PlaceOrderOut(Schema):
    order_id: str
    status: str
    total_amount: MoneyOut

@router.post("", response={201: PlaceOrderOut})
def place_order(request, payload: PlaceOrderIn) -> tuple[int, PlaceOrderOut]:
    command = PlaceOrderCommand(
        customer_id=payload.customer_id,
        items=[item.model_dump() for item in payload.items],
        idempotency_key=request.headers["Idempotency-Key"],
    )
    result = build_order_application_service().place_order(command)
    return 201, PlaceOrderOut(
        order_id=result.value,
        status="payment_waiting",
        total_amount=MoneyOut(amount=0, currency="KRW"),
    )
```

`config/api.py`에서는 문자열이 아니라 router 객체를 합성합니다.

```python
from ninja import NinjaAPI
from apps.orders.adapters.driving.api.router import router as orders_router

api = NinjaAPI(version="1.0.0")
api.add_router("/orders", orders_router)
```

**멱등성 / 이벤트 발행**

주문 생성은 중복이 치명적인 POST이므로 `Idempotency-Key`가 필수입니다. 멱등성은 `도메인 상태 검사 / Dedup 테이블 / PG idempotency-key`를 구분해 적용합니다. 주문 생성은 Dedup 테이블, 결제 요청은 PG idempotency-key, 상태 전이 재시도는 도메인 상태 검사를 사용합니다.

Outbox는 at-least-once delivery를 보장합니다. 컨슈머는 `event_id` 기반 dedup 또는 도메인 상태 검사로 멱등성을 처리해야 합니다. 같은 프로세스 내 알림 정도는 `transaction.on_commit`, BC 경계를 넘는 재고/결제/배송 통합 이벤트는 Outbox를 선택합니다.

---
> **관련 스킬 참조:**
> - 도메인 모델 세부화 → **architecture-ddd** 스킬
> - Django Ninja 구현 → **implementation-django-ninja** 스킬
> - 트랜잭션/UoW/Outbox 구현 → **architecture-implementation-patterns** 스킬