**주요 내용**

Django에서 “주문 완료 후 domain event 발행”은 `post_save` 시그널보다 **Order Aggregate가 이벤트를 기록하고, Application Service가 트랜잭션 경계에서 저장/Outbox 적재를 조율하는 구조**가 DDD 기준에 맞습니다. 핵심은 도메인 모델이 Django ORM, Celery, Kafka, 이메일 같은 인프라를 전혀 모르도록 하는 것입니다.

**전략적 경계**

| Bounded Context | 책임 | 관계 |
|---|---|---|
| Ordering | 주문 생성, 결제 확정 반영, 주문 완료 상태 전이 | Fulfillment에 `Published Language`로 통합 이벤트 발행 |
| Payment | PG 승인/실패 처리 | Ordering과 `Customer-Supplier`, PG와는 `ACL` |
| Fulfillment | 출고 요청, 배송 준비 | Ordering의 `OrderCompletedV1`을 구독 |
| Inventory | 재고 예약/확정 | Ordering/Fulfillment와 이벤트 기반 최종 일관성 |

**Ubiquitous Language**

| 도메인 용어 | 정의 | 코드 표현 | 금지 동의어 |
|---|---|---|---|
| 주문 완료 | 결제 확정 후 주문이 이행 가능한 상태가 된 사실 | `OrderCompleted`, `order.complete()` | `paid_order`, `checkout_done` |
| 결제 확정 | PG 승인 결과가 주문에 반영된 사실 | `PaymentConfirmed`, `order.confirm_payment()` | `charge`, `payment_token` |
| 주문 금액 | 주문 항목 합계의 통화 포함 금액 | `Money` | `price_int`, `amount_only` |
| 주문 항목 | 주문 시점 상품/수량/단가 스냅샷 | `OrderLine` | `cart_item`, `product_row` |

추천 파일 구조는 다음처럼 도메인과 인프라를 분리합니다.

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
  application/
    complete_order.py
    integration_events.py
  infrastructure/
    persistence/
      django_order_repository.py
      models.py
      outbox.py
```

도메인 계층 예시는 이렇게 둡니다.

```python
# apps/orders/domain/shared/aggregate_root.py
class AggregateRoot:
    def __init__(self) -> None:
        self._domain_events: list[object] = []

    def _record_event(self, event: object) -> None:
        self._domain_events.append(event)

    def collect_events(self) -> list[object]:
        events, self._domain_events = self._domain_events, []
        return events
```

```python
# apps/orders/domain/shared/money.py
from dataclasses import dataclass


class CurrencyMismatch(Exception):
    pass


@dataclass(frozen=True)
class Money:
    amount: int
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("amount must be non-negative")
        if not self.currency:
            raise ValueError("currency is required")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise CurrencyMismatch(f"{self.currency} != {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, quantity: int) -> "Money":
        if quantity < 0:
            raise ValueError("quantity must be non-negative")
        return Money(self.amount * quantity, self.currency)
```

```python
# apps/orders/domain/shared/identifiers.py
from dataclasses import dataclass


@dataclass(frozen=True)
class OrderId:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("OrderId is required")


@dataclass(frozen=True)
class CustomerId:
    value: str


@dataclass(frozen=True)
class PaymentId:
    value: str


@dataclass(frozen=True)
class ProductId:
    value: str
```

```python
# apps/orders/domain/model/order/value_objects.py
from dataclasses import dataclass

from apps.orders.domain.shared.identifiers import ProductId
from apps.orders.domain.shared.money import Money


@dataclass(frozen=True)
class OrderLine:
    product_id: ProductId
    product_name: str
    quantity: int
    unit_price: Money

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")

    @property
    def subtotal(self) -> Money:
        return self.unit_price * self.quantity
```

```python
# apps/orders/domain/model/order/events.py
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from apps.orders.domain.shared.identifiers import CustomerId, OrderId, PaymentId
from apps.orders.domain.shared.money import Money


@dataclass(frozen=True)
class PaymentConfirmed:
    order_id: OrderId
    payment_id: PaymentId
    amount: Money
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class OrderCompleted:
    order_id: OrderId
    customer_id: CustomerId
    total_amount: Money
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=datetime.now)
```

```python
# apps/orders/domain/model/order/root.py
from dataclasses import dataclass
from enum import StrEnum

from apps.orders.domain.model.order.events import OrderCompleted, PaymentConfirmed
from apps.orders.domain.model.order.value_objects import OrderLine
from apps.orders.domain.shared.aggregate_root import AggregateRoot
from apps.orders.domain.shared.identifiers import CustomerId, OrderId, PaymentId
from apps.orders.domain.shared.money import Money


class InvalidOrderState(Exception):
    pass


class OrderStatus(StrEnum):
    PLACED = "placed"
    PAYMENT_CONFIRMED = "payment_confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Order(AggregateRoot):
    """
    Aggregate Root: Order

    INV-1: 주문 항목은 1개 이상이어야 한다.
    INV-2: 완료된 주문은 다시 완료될 수 없다.
    INV-3: 취소된 주문은 완료될 수 없다.
    INV-4: 다른 Aggregate는 ID로만 참조한다.
    """
    id: OrderId
    customer_id: CustomerId
    lines: list[OrderLine]
    status: OrderStatus = OrderStatus.PLACED
    version: int = 0

    def __post_init__(self) -> None:
        AggregateRoot.__init__(self)
        if not self.lines:
            raise ValueError("order must have at least one line")

    @property
    def total_amount(self) -> Money:
        total = Money(0, self.lines[0].unit_price.currency)
        for line in self.lines:
            total = total + line.subtotal
        return total

    def confirm_payment(self, payment_id: PaymentId, paid_amount: Money) -> None:
        if self.status == OrderStatus.COMPLETED:
            return
        if self.status == OrderStatus.CANCELLED:
            raise InvalidOrderState("cancelled order cannot be completed")
        if paid_amount != self.total_amount:
            raise ValueError("paid amount does not match order total")

        self.status = OrderStatus.PAYMENT_CONFIRMED
        self._record_event(PaymentConfirmed(self.id, payment_id, paid_amount))
        self.complete()

    def complete(self) -> None:
        if self.status != OrderStatus.PAYMENT_CONFIRMED:
            raise InvalidOrderState("payment must be confirmed first")

        self.status = OrderStatus.COMPLETED
        self._record_event(
            OrderCompleted(
                order_id=self.id,
                customer_id=self.customer_id,
                total_amount=self.total_amount,
            )
        )

    def cancel(self) -> None:
        if self.status == OrderStatus.COMPLETED:
            raise InvalidOrderState("completed order cannot be cancelled")
        self.status = OrderStatus.CANCELLED
```

Repository 인터페이스는 도메인 계층이 소유합니다.

```python
# apps/orders/domain/model/order/repository.py
from abc import ABC, abstractmethod

from apps.orders.domain.model.order.root import Order
from apps.orders.domain.shared.identifiers import OrderId


class ConcurrencyError(Exception):
    pass


class OrderRepository(ABC):
    @abstractmethod
    def find_by_id(self, order_id: OrderId) -> Order | None:
        ...

    @abstractmethod
    def save(self, order: Order) -> None:
        ...
```

Application Service는 유스케이스와 트랜잭션을 조율합니다. BC 경계를 넘는 이벤트는 `transaction.on_commit()`으로 직접 Kafka/Celery 발행하지 말고, 주문 변경과 같은 트랜잭션에 Outbox row를 저장합니다.

```python
# apps/orders/application/complete_order.py
from dataclasses import dataclass

from django.db import transaction

from apps.orders.application.integration_events import OrderCompletedV1
from apps.orders.domain.model.order.events import OrderCompleted
from apps.orders.domain.model.order.repository import OrderRepository
from apps.orders.domain.shared.identifiers import OrderId, PaymentId
from apps.orders.domain.shared.money import Money
from apps.orders.infrastructure.persistence.outbox import OutboxMessage


@dataclass(frozen=True)
class CompleteOrderCommand:
    order_id: str
    payment_id: str
    paid_amount: int
    currency: str = "KRW"


class CompleteOrderService:
    def __init__(self, orders: OrderRepository) -> None:
        self.orders = orders

    def complete(self, command: CompleteOrderCommand) -> None:
        with transaction.atomic():
            order = self.orders.find_by_id(OrderId(command.order_id))
            if order is None:
                raise ValueError("order not found")

            order.confirm_payment(
                payment_id=PaymentId(command.payment_id),
                paid_amount=Money(command.paid_amount, command.currency),
            )
            self.orders.save(order)

            for event in order.collect_events():
                if isinstance(event, OrderCompleted):
                    integration_event = OrderCompletedV1.from_domain(event)
                    OutboxMessage.objects.create_from_event(integration_event)
```

통합 이벤트는 내부 도메인 이벤트와 분리합니다. 내부 이벤트는 자유롭게 바꿀 수 있지만, 통합 이벤트는 외부 계약이므로 버전과 스키마를 고정합니다.

```python
# apps/orders/application/integration_events.py
from dataclasses import asdict, dataclass
from datetime import datetime

from apps.orders.domain.model.order.events import OrderCompleted


@dataclass(frozen=True)
class OrderCompletedV1:
    event_id: str
    event_type: str
    schema_version: str
    occurred_at: datetime
    order_id: str
    customer_id: str
    total_amount_krw: int

    @classmethod
    def from_domain(cls, event: OrderCompleted) -> "OrderCompletedV1":
        return cls(
            event_id=event.event_id,
            event_type="order.completed.v1",
            schema_version="1.0",
            occurred_at=event.occurred_at,
            order_id=event.order_id.value,
            customer_id=event.customer_id.value,
            total_amount_krw=event.total_amount.amount,
        )

    def to_dict(self) -> dict:
        return asdict(self)
```

```python
# apps/orders/infrastructure/persistence/outbox.py
from django.db import models


class OutboxMessageManager(models.Manager):
    def create_from_event(self, event) -> "OutboxMessage":
        return self.create(
            event_id=event.event_id,
            event_type=event.event_type,
            schema_version=event.schema_version,
            payload=event.to_dict(),
        )


class OutboxMessage(models.Model):
    event_id = models.UUIDField(unique=True)
    event_type = models.CharField(max_length=120, db_index=True)
    schema_version = models.CharField(max_length=20)
    payload = models.JSONField()
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = OutboxMessageManager()

    class Meta:
        indexes = [
            models.Index(fields=["event_type", "published_at"]),
            models.Index(fields=["created_at"]),
        ]
```

Repository 구현에서는 낙관적 잠금을 기본으로 둡니다. `version`이 맞을 때만 update하고, 실패하면 재조회 후 재시도하게 합니다.

```python
# infrastructure repository 핵심 아이디어
updated = OrderModel.objects.filter(
    id=order.id.value,
    version=order.version,
).update(
    status=order.status,
    version=order.version + 1,
)

if updated == 0:
    raise ConcurrencyError("order was modified by another transaction")
```

선택 기준은 이렇게 잡으면 됩니다.

| 상황 | 권장 방식 |
|---|---|
| 주문 완료 후 같은 프로세스에서 이메일 발송 | `transaction.on_commit()`으로 Celery enqueue |
| 주문 완료를 배송/재고/정산 BC에 전달 | Outbox + Message Bus |
| 외부 PG webhook 중복 수신 | Dedup 테이블 + 도메인 상태 검사 |
| PG 결제 요청 재시도 | PG idempotency-key |

Outbox는 at-least-once delivery를 보장한다. 컨슈머는 event_id 기반 dedup 또는 도메인 상태 검사로 멱등성을 처리해야 한다.

정리하면, 흐름은 다음입니다.

```text
Django Ninja API 또는 View
  -> CompleteOrderService
    -> OrderRepository.find_by_id()
    -> order.confirm_payment()
       -> PaymentConfirmed 기록
       -> OrderCompleted 기록
    -> OrderRepository.save()
    -> OutboxMessage INSERT
  -> DB COMMIT
Outbox Relay
  -> message bus publish(order.completed.v1)
Fulfillment/Inventory/Loyalty Consumer
  -> Dedup 테이블 또는 도메인 상태 검사
  -> 각 BC의 Command Handler 실행
```

`post_save` 시그널은 같은 앱의 주문 완료 로직에는 피하는 게 좋습니다. 이벤트 발행 시점과 트랜잭션 경계가 숨어서, 장애 시 이벤트 유실이나 중복 발행을 추적하기 어려워집니다. DDD 기준에서는 Aggregate가 “발생한 사실”을 기록하고, Application Service가 저장과 발행 준비를 명시적으로 조율하는 쪽이 더 견고합니다.

---
> **관련 스킬 참조:**
> - Django 구현/API 엔드포인트화 → **implementation-django-ninja** 스킬
> - Outbox Relay, 메시지 브로커, UoW 상세화 → **architecture-implementation-patterns** 스킬
> - pytest/TDD로 주문 완료 이벤트 검증 → **implementation-tdd** 스킬