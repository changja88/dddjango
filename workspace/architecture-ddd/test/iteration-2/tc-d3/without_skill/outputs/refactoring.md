# 주문-재고-배송 연동: 결과적 일관성 기반 리팩토링

## 1. 문제 분석

원본 코드의 `complete_order`는 하나의 메서드에서 4개의 바운디드 컨텍스트(주문, 재고, 배송, 결제)를 동기적으로 직접 조작한다.

```python
def complete_order(self, order_id):
    order = self.order_repo.find_by_id(order_id)
    order.status = "completed"
    self.order_repo.save(order)

    for item in order.items:
        inventory = self.inventory_repo.find_by_product_id(item.product_id)
        inventory.quantity -= item.quantity
        self.inventory_repo.save(inventory)

    shipping = Shipping(order_id=order.id, address=order.shipping_address, items=order.items)
    self.shipping_repo.save(shipping)

    payment = self.payment_repo.find_by_order_id(order_id)
    payment.status = "captured"
    self.payment_repo.save(payment)
```

**핵심 문제점:**

| 문제 | 설명 |
|------|------|
| 강결합 | OrderService가 inventory_repo, shipping_repo, payment_repo를 직접 의존 |
| 트랜잭션 범위 과대 | 4개 Aggregate를 하나의 논리적 트랜잭션에서 변경 |
| 부분 실패 미처리 | 배송 생성이 실패하면 이미 차감된 재고를 복구할 방법이 없음 |
| 확장 불가 | 새로운 후속 작업(포인트 적립, 알림 발송 등) 추가 시 OrderService 수정 필요 |

## 2. 리팩토링 원칙

**결과적 일관성(Eventual Consistency)**: 트랜잭션 하나에서는 하나의 Aggregate만 변경하고, 나머지는 도메인 이벤트를 통해 비동기로 반응하게 만든다.

- 하나의 트랜잭션 = 하나의 Aggregate 변경
- Aggregate 간 연동은 도메인 이벤트로 분리
- 각 후속 처리는 독립적으로 실패/재시도 가능

## 3. 리팩토링 결과

### 3.1 도메인 이벤트 정의

```python
from dataclasses import dataclass, field
from typing import List
from datetime import datetime
import uuid


@dataclass(frozen=True)
class DomainEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class OrderCompleted(DomainEvent):
    order_id: str = ""
    items: tuple = ()           # ((product_id, quantity), ...)
    shipping_address: str = ""
```

### 3.2 Order Aggregate -- 이벤트를 발행하는 유일한 트랜잭션 주체

```python
class Order:
    def __init__(self, id, items, shipping_address, status="pending"):
        self.id = id
        self.items = items
        self.shipping_address = shipping_address
        self.status = status
        self._events: list[DomainEvent] = []

    def complete(self):
        if self.status != "pending":
            raise InvalidOrderStateError(
                f"Cannot complete order in '{self.status}' state"
            )
        self.status = "completed"
        self._events.append(
            OrderCompleted(
                order_id=self.id,
                items=tuple((i.product_id, i.quantity) for i in self.items),
                shipping_address=self.shipping_address,
            )
        )

    def collect_events(self) -> list[DomainEvent]:
        events = list(self._events)
        self._events.clear()
        return events
```

### 3.3 OrderService -- 단일 Aggregate만 변경, 이벤트 발행 위임

```python
class OrderService:
    def __init__(self, order_repo, event_publisher):
        self.order_repo = order_repo
        self.event_publisher = event_publisher

    def complete_order(self, order_id: str) -> None:
        order = self.order_repo.find_by_id(order_id)
        order.complete()
        self.order_repo.save(order)

        for event in order.collect_events():
            self.event_publisher.publish(event)
```

**변경 전 vs 변경 후:**

- 의존성: `order_repo, inventory_repo, shipping_repo, payment_repo` --> `order_repo, event_publisher`
- 트랜잭션 범위: Order, Inventory, Shipping, Payment 동시 변경 --> Order만 변경
- 비즈니스 로직 위치: Service 메서드 내 절차적 코드 --> Order Aggregate 내 `complete()` 메서드

### 3.4 각 바운디드 컨텍스트의 이벤트 핸들러

```python
class InventoryEventHandler:
    """재고 컨텍스트: OrderCompleted 이벤트에 반응하여 재고 차감"""

    def __init__(self, inventory_repo):
        self.inventory_repo = inventory_repo

    def handle_order_completed(self, event: OrderCompleted) -> None:
        for product_id, quantity in event.items:
            inventory = self.inventory_repo.find_by_product_id(product_id)
            inventory.decrease(quantity)
            self.inventory_repo.save(inventory)


class ShippingEventHandler:
    """배송 컨텍스트: OrderCompleted 이벤트에 반응하여 배송 요청 생성"""

    def __init__(self, shipping_repo):
        self.shipping_repo = shipping_repo

    def handle_order_completed(self, event: OrderCompleted) -> None:
        shipping = Shipping(
            order_id=event.order_id,
            address=event.shipping_address,
            items=event.items,
        )
        self.shipping_repo.save(shipping)


class PaymentEventHandler:
    """결제 컨텍스트: OrderCompleted 이벤트에 반응하여 결제 확정"""

    def __init__(self, payment_repo):
        self.payment_repo = payment_repo

    def handle_order_completed(self, event: OrderCompleted) -> None:
        payment = self.payment_repo.find_by_order_id(event.order_id)
        payment.capture()
        self.payment_repo.save(payment)
```

### 3.5 이벤트 퍼블리셔 및 핸들러 등록

```python
class EventPublisher:
    def __init__(self):
        self._handlers: dict[type, list] = {}

    def subscribe(self, event_type: type, handler) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers.get(type(event), []):
            handler(event)


# 조립 (Composition Root)
event_publisher = EventPublisher()

inventory_handler = InventoryEventHandler(inventory_repo)
shipping_handler = ShippingEventHandler(shipping_repo)
payment_handler = PaymentEventHandler(payment_repo)

event_publisher.subscribe(OrderCompleted, inventory_handler.handle_order_completed)
event_publisher.subscribe(OrderCompleted, shipping_handler.handle_order_completed)
event_publisher.subscribe(OrderCompleted, payment_handler.handle_order_completed)

order_service = OrderService(order_repo, event_publisher)
```

## 4. 결과적 일관성이 보장되는 구조

```
[OrderService.complete_order()]
    |
    |-- (1) Order.complete()           # Order Aggregate 상태 변경
    |-- (2) order_repo.save(order)     # 트랜잭션 커밋
    |-- (3) event_publisher.publish()  # OrderCompleted 이벤트 발행
            |
            |---> InventoryEventHandler   # 독립 트랜잭션으로 재고 차감
            |---> ShippingEventHandler    # 독립 트랜잭션으로 배송 생성
            |---> PaymentEventHandler     # 독립 트랜잭션으로 결제 확정
```

각 핸들러는 독립적인 트랜잭션 경계를 갖기 때문에:

- **부분 실패 격리**: 배송 생성이 실패해도 주문 완료와 재고 차감은 영향받지 않는다.
- **독립 재시도**: 실패한 핸들러만 이벤트를 기반으로 재시도할 수 있다.
- **확장 용이**: 포인트 적립, 알림 발송 등 새로운 후속 작업은 핸들러를 추가 등록하면 되며 OrderService를 수정할 필요가 없다(OCP 준수).

## 5. 프로덕션 수준으로 강화할 때 고려할 사항

| 관심사 | 방법 |
|--------|------|
| 이벤트 유실 방지 | Transactional Outbox 패턴 -- Order 저장과 이벤트 저장을 같은 DB 트랜잭션에 묶고, 별도 릴레이가 메시지 브로커로 발행 |
| 비동기 처리 | 메시지 브로커(Kafka, RabbitMQ 등)를 통해 핸들러를 별도 프로세스/서비스로 분리 |
| 멱등성 보장 | `event_id`를 기반으로 핸들러에서 중복 처리를 방지 |
| 보상 트랜잭션 | 핸들러 실패 시 보상 이벤트(InventoryDecreaseFailed 등)를 발행하여 역방향 복구 |
