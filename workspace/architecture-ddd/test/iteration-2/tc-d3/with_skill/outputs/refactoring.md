# 주문-재고-배송 연동: 결과적 일관성 기반 리팩토링

## 진단 요약

기존 `OrderService.complete_order`는 하나의 트랜잭션에서 4개의 애그리거트(Order, Inventory, Shipping, Payment)를 동시에 수정한다. Vernon의 애그리거트 설계 규칙 4가지를 모두 위반하고 있으며, 빈혈 도메인 모델 안티패턴도 확인된다.

---

## 리팩토링 1: 빈혈 도메인 모델 -> 풍부한 도메인 모델

[Before]

```python
def complete_order(self, order_id):
    order = self.order_repo.find_by_id(order_id)
    order.status = "completed"       # 외부에서 직접 상태 변경
    self.order_repo.save(order)
```

[After]

```python
@dataclass
class Order:
    id: str
    orderer_id: str
    items: List[OrderLineItem] = field(default_factory=list)
    shipping_address: str = ""
    _status: OrderStatus = field(default=OrderStatus.PLACED)
    _events: List[DomainEvent] = field(default_factory=list)

    def complete(self) -> None:
        """주문 완료 -- 비즈니스 규칙을 애그리거트 안에서 보호한다"""
        if self._status != OrderStatus.PLACED:
            raise ValueError(
                f"{self._status.value} 상태에서는 완료 처리할 수 없습니다"
            )
        self._status = OrderStatus.COMPLETED
        self._events.append(
            OrderCompletedEvent(
                order_id=self.id,
                items=[
                    {"product_id": item.product_id, "quantity": item.quantity}
                    for item in self.items
                ],
                shipping_address=self.shipping_address,
            )
        )

    def collect_domain_events(self) -> List[DomainEvent]:
        events = list(self._events)
        self._events.clear()
        return events
```

[Reason] 빈혈 도메인 모델 -> 풍부한 도메인 모델 -- 상태 전이 규칙(`PLACED`에서만 `COMPLETED`로 전환 가능)은 비즈니스 불변식이므로 엔티티 안에 캡슐화해야 한다. 서비스가 `order.status = "completed"`처럼 직접 상태를 변경하면, 상태 전이 규칙이 서비스 계층에 분산되어 어디서든 잘못된 전이가 발생할 수 있다.

---

## 리팩토링 2: 하나의 트랜잭션에서 여러 애그리거트 수정 -> 도메인 이벤트 + 결과적 일관성

[Before]

```python
class OrderService:
    def __init__(self, order_repo, inventory_repo, shipping_repo, payment_repo):
        self.order_repo = order_repo
        self.inventory_repo = inventory_repo
        self.shipping_repo = shipping_repo
        self.payment_repo = payment_repo

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

[After]

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List, Type
from uuid import uuid4


# ============================================================
# 도메인 이벤트
# ============================================================

@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class OrderCompletedEvent(DomainEvent):
    """주문 완료 시 발행 -- 재고, 배송, 결제가 이 이벤트를 구독한다"""
    order_id: str = ""
    items: List[dict] = field(default_factory=list)
    shipping_address: str = ""


# ============================================================
# 값 객체
# ============================================================

class OrderStatus(Enum):
    PLACED = "placed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class OrderLineItem:
    product_id: str
    quantity: int


# ============================================================
# 애그리거트: Order (루트)
# ============================================================

@dataclass
class Order:
    """주문 애그리거트

    - 자신의 불변식(상태 전이 규칙)만 보호한다.
    - 재고, 배송, 결제는 별도 애그리거트이므로 이벤트로 통신한다.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    orderer_id: str = ""
    items: List[OrderLineItem] = field(default_factory=list)
    shipping_address: str = ""
    _status: OrderStatus = field(default=OrderStatus.PLACED)
    _events: List[DomainEvent] = field(default_factory=list)

    def complete(self) -> None:
        if self._status != OrderStatus.PLACED:
            raise ValueError(
                f"{self._status.value} 상태에서는 완료 처리할 수 없습니다"
            )
        self._status = OrderStatus.COMPLETED
        self._events.append(
            OrderCompletedEvent(
                order_id=self.id,
                items=[
                    {"product_id": item.product_id, "quantity": item.quantity}
                    for item in self.items
                ],
                shipping_address=self.shipping_address,
            )
        )

    def collect_domain_events(self) -> List[DomainEvent]:
        events = list(self._events)
        self._events.clear()
        return events


# ============================================================
# 애그리거트: Inventory, Shipping, Payment (각각 독립)
# ============================================================

@dataclass
class Inventory:
    """재고 애그리거트 -- Order와 ID로만 연결된다"""
    id: str = field(default_factory=lambda: str(uuid4()))
    product_id: str = ""
    quantity: int = 0

    def decrease(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("차감 수량은 0보다 커야 합니다")
        if self.quantity < amount:
            raise ValueError(
                f"재고 부족: 현재 {self.quantity}, 요청 {amount}"
            )
        self.quantity -= amount


@dataclass
class Shipping:
    """배송 애그리거트 -- Order를 ID로 참조한다"""
    id: str = field(default_factory=lambda: str(uuid4()))
    order_id: str = ""
    address: str = ""
    items: List[dict] = field(default_factory=list)


@dataclass
class Payment:
    """결제 애그리거트 -- Order를 ID로 참조한다"""
    id: str = field(default_factory=lambda: str(uuid4()))
    order_id: str = ""
    _status: str = "authorized"

    def capture(self) -> None:
        if self._status != "authorized":
            raise ValueError(
                f"{self._status} 상태에서는 캡처할 수 없습니다"
            )
        self._status = "captured"


# ============================================================
# 이벤트 버스 (인프라)
# ============================================================

class EventBus:
    def __init__(self):
        self._handlers: Dict[Type[DomainEvent], List[Callable]] = {}

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers.get(type(event), []):
            handler(event)


# ============================================================
# 이벤트 핸들러 (각 바운디드 컨텍스트 별도 트랜잭션)
# ============================================================

class InventoryEventHandler:
    """재고 컨텍스트 -- 주문 완료 이벤트를 구독하여 재고를 차감한다"""

    def __init__(self, inventory_repo):
        self._inventory_repo = inventory_repo

    def handle_order_completed(self, event: OrderCompletedEvent) -> None:
        for item in event.items:
            inventory = self._inventory_repo.find_by_product_id(
                item["product_id"]
            )
            inventory.decrease(item["quantity"])
            self._inventory_repo.save(inventory)


class ShippingEventHandler:
    """배송 컨텍스트 -- 주문 완료 이벤트를 구독하여 배송을 생성한다"""

    def __init__(self, shipping_repo):
        self._shipping_repo = shipping_repo

    def handle_order_completed(self, event: OrderCompletedEvent) -> None:
        shipping = Shipping(
            order_id=event.order_id,
            address=event.shipping_address,
            items=event.items,
        )
        self._shipping_repo.save(shipping)


class PaymentEventHandler:
    """결제 컨텍스트 -- 주문 완료 이벤트를 구독하여 결제를 캡처한다"""

    def __init__(self, payment_repo):
        self._payment_repo = payment_repo

    def handle_order_completed(self, event: OrderCompletedEvent) -> None:
        payment = self._payment_repo.find_by_order_id(event.order_id)
        payment.capture()
        self._payment_repo.save(payment)


# ============================================================
# 응용 서비스 (유스케이스 조율)
# ============================================================

class CompleteOrderService:
    """주문 완료 응용 서비스

    - 주문 애그리거트만 직접 수정한다 (하나의 트랜잭션).
    - 재고/배송/결제는 도메인 이벤트를 통해 결과적 일관성으로 처리한다.
    """

    def __init__(self, order_repo, event_bus: EventBus):
        self._order_repo = order_repo
        self._event_bus = event_bus

    def execute(self, order_id: str) -> None:
        # 1. 주문 애그리거트 조회 및 상태 전이
        order = self._order_repo.find_by_id(order_id)
        if order is None:
            raise ValueError("주문을 찾을 수 없습니다")
        order.complete()
        self._order_repo.save(order)

        # 2. 수집된 도메인 이벤트를 발행 -- 결과적 일관성
        for event in order.collect_domain_events():
            self._event_bus.publish(event)


# ============================================================
# 조립 (Composition Root)
# ============================================================

def bootstrap(order_repo, inventory_repo, shipping_repo, payment_repo):
    """이벤트 핸들러를 이벤트 버스에 등록한다"""
    event_bus = EventBus()

    inventory_handler = InventoryEventHandler(inventory_repo)
    shipping_handler = ShippingEventHandler(shipping_repo)
    payment_handler = PaymentEventHandler(payment_repo)

    event_bus.subscribe(
        OrderCompletedEvent, inventory_handler.handle_order_completed
    )
    event_bus.subscribe(
        OrderCompletedEvent, shipping_handler.handle_order_completed
    )
    event_bus.subscribe(
        OrderCompletedEvent, payment_handler.handle_order_completed
    )

    return CompleteOrderService(order_repo, event_bus)
```

[Reason] Vernon 규칙 4 (결과적 일관성) + 규칙 1 (불변식 경계) -- 기존 코드는 하나의 트랜잭션에서 Order, Inventory, Shipping, Payment 4개의 애그리거트를 동시에 수정한다. 이는 Vernon의 규칙 1("하나의 트랜잭션에서는 하나의 애그리거트만 수정한다")을 위반하며, 규칙 4("일관성 경계 밖에서는 결과적 일관성을 사용하라")도 위반한다. 리팩토링 후에는 `CompleteOrderService`가 Order 애그리거트만 수정하고, 나머지는 `OrderCompletedEvent`를 통해 각자의 트랜잭션에서 독립적으로 처리한다.

---

## 리팩토링 3: 직접 상태 변경 -> 값 객체 + 캡슐화된 도메인 로직

[Before]

```python
inventory.quantity -= item.quantity

payment.status = "captured"
```

[After]

```python
# Inventory 애그리거트
def decrease(self, amount: int) -> None:
    if amount <= 0:
        raise ValueError("차감 수량은 0보다 커야 합니다")
    if self.quantity < amount:
        raise ValueError(
            f"재고 부족: 현재 {self.quantity}, 요청 {amount}"
        )
    self.quantity -= amount


# Payment 애그리거트
def capture(self) -> None:
    if self._status != "authorized":
        raise ValueError(
            f"{self._status} 상태에서는 캡처할 수 없습니다"
        )
    self._status = "captured"
```

[Reason] 빈혈 도메인 모델 -> 풍부한 도메인 모델 -- `inventory.quantity -= item.quantity`는 재고 부족 검증 없이 음수가 될 수 있고, `payment.status = "captured"`는 이미 캡처된 결제를 중복 캡처할 수 있다. 비즈니스 규칙(재고 부족 방지, 상태 전이 제약)을 각 애그리거트 안에 캡슐화하면, 어떤 서비스에서 호출하든 불변식이 보호된다.

---

## 리팩토링 4: 직접 객체 참조 -> ID 참조

[Before]

```python
class OrderService:
    def __init__(self, order_repo, inventory_repo, shipping_repo, payment_repo):
        # 4개 리포지토리에 모두 의존 -- 강결합
```

[After]

```python
class CompleteOrderService:
    def __init__(self, order_repo, event_bus: EventBus):
        # 주문 리포지토리와 이벤트 버스에만 의존 -- 느슨한 결합

class Shipping:
    order_id: str = ""   # Order 객체가 아닌 ID로 참조
```

[Reason] Vernon 규칙 3 (ID 참조) -- 기존 `OrderService`는 4개의 리포지토리에 직접 의존하여 Order, Inventory, Shipping, Payment가 강결합되어 있었다. 리팩토링 후에는 `CompleteOrderService`가 주문 리포지토리에만 의존하고, 다른 애그리거트와는 이벤트(ID 기반 데이터 포함)로만 통신한다. Shipping 등의 애그리거트도 Order 객체를 직접 참조하지 않고 `order_id`로만 연결한다.

---

## 적용된 리팩토링 체크리스트

- [x] 빈혈 도메인 모델 -> 풍부한 도메인 모델로 비즈니스 로직 이동
- [x] 큰 애그리거트 -> 작은 애그리거트로 분리 + 도메인 이벤트로 연결
- [x] 직접 참조 -> ID 참조로 변경
- [x] 서비스의 비즈니스 로직 -> 엔티티/값 객체의 메서드로 이동
- [x] 동기 호출 -> 도메인 이벤트 + 결과적 일관성으로 변경
- [ ] 원시 타입 -> 값 객체로 추출 (해당 없음: 제공된 코드에 금액/주소 등의 원시 타입이 명시적으로 드러나지 않아 생략)
- [ ] 모호한 경계 -> 바운디드 컨텍스트 분리 (해당 없음: 주문/재고/배송/결제가 이미 별도 엔티티로 존재하여 컨텍스트 분리보다 이벤트 기반 분리로 충분)
