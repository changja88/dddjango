**주요 내용**

DDD 기준으로는 “주문 완료 후 이벤트를 발행한다”가 아니라, **Order 애그리거트가 완료 상태 전이를 수행하면서 `OrderCompletedEvent`를 기록하고, 응용 서비스가 트랜잭션 경계에서 이벤트 발행을 조율**하는 구조가 좋습니다.

핵심 원칙은 이렇습니다.

| 구분 | 권장 |
|---|---|
| Aggregate Root | `Order` |
| 보호할 불변식 | 결제 완료된 주문만 완료 가능, 이미 완료/취소된 주문은 다시 완료 불가 |
| Domain Event | `OrderCompletedEvent`처럼 과거형 |
| 금지 동의어 | `OrderCompleteEvent`, `CompleteOrderEvent`, `order_done`, `status update` |
| 발행 위치 | 도메인 모델 내부 직접 publish 금지. 이벤트는 기록만 |
| 실제 publish | `OrderApplicationService` + `transaction.on_commit()` 또는 Outbox |

권장 폴더 구조는 다음처럼 나눕니다.

```text
applications/orders/
├── domain_layer/
│   ├── order/
│   │   ├── order.py
│   │   └── money.py
│   ├── event/
│   │   └── order_events.py
│   └── repository/
│       └── order_repo.py
├── application_layer/
│   └── order_service.py
└── infra_layer/
    ├── repository/
    │   └── django_order_repo.py
    ├── event_bus/
    │   └── django_event_bus.py
    └── django_orders/
        └── models/
            └── order_model.py
```

도메인 이벤트는 프레임워크에 의존하지 않는 순수 객체로 둡니다.

```python
# applications/orders/domain_layer/event/order_events.py
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class OrderCompletedEvent(DomainEvent):
    order_id: UUID
    customer_id: UUID
    total_amount: int
```

값 객체는 불변으로 만들고 검증을 내부에 둡니다.

```python
# applications/orders/domain_layer/order/money.py
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount: int

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise InvalidMoneyError("금액은 0 이상이어야 합니다")


class InvalidMoneyError(Exception):
    pass
```

`Order` 애그리거트는 상태 변경과 이벤트 기록만 담당합니다. DB 저장, 메시지 브로커 publish, Django signal 호출은 하지 않습니다.

```python
# applications/orders/domain_layer/order/order.py
from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID

from applications.orders.domain_layer.event.order_events import OrderCompletedEvent
from applications.orders.domain_layer.order.money import Money


class OrderStatus(Enum):
    PAYMENT_WAITING = "payment_waiting"
    PAID = "paid"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderCannotBeCompletedError(Exception):
    pass


@dataclass
class Order:
    """Order Aggregate Root.

    불변식:
    - PAID 상태의 주문만 완료할 수 있다.
    - COMPLETED 또는 CANCELLED 주문은 다시 완료할 수 없다.
    - 다른 애그리거트(Customer, Payment, Inventory)는 객체 참조가 아닌 ID로만 참조한다.
    """

    id: UUID
    customer_id: UUID
    total_amount: Money
    status: OrderStatus
    _domain_events: list[object] = field(default_factory=list, init=False)

    def complete(self) -> None:
        if self.status != OrderStatus.PAID:
            raise OrderCannotBeCompletedError(
                "결제 완료된 주문만 완료 처리할 수 있습니다"
            )

        self.status = OrderStatus.COMPLETED
        self._record_event(
            OrderCompletedEvent(
                order_id=self.id,
                customer_id=self.customer_id,
                total_amount=self.total_amount.amount,
            )
        )

    def _record_event(self, event: object) -> None:
        self._domain_events.append(event)

    def collect_domain_events(self) -> list[object]:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events
```

리포지토리 인터페이스는 도메인 계층에 둡니다.

```python
# applications/orders/domain_layer/repository/order_repo.py
from abc import ABC, abstractmethod
from uuid import UUID

from applications.orders.domain_layer.order.order import Order


class OrderRepository(ABC):
    @abstractmethod
    def find_by_id(self, order_id: UUID) -> Order | None:
        ...

    @abstractmethod
    def save(self, order: Order) -> None:
        ...
```

응용 서비스는 트랜잭션을 열고, 애그리거트를 가져오고, 도메인 메서드를 호출하고, 저장 후 커밋 이후 이벤트를 발행합니다.

```python
# applications/orders/application_layer/order_service.py
from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from applications.orders.domain_layer.repository.order_repo import OrderRepository


@dataclass(frozen=True)
class CompleteOrderCommand:
    order_id: UUID


class OrderNotFoundError(Exception):
    pass


class OrderApplicationService:
    def __init__(self, order_repo: OrderRepository, event_bus: "EventBus"):
        self._order_repo = order_repo
        self._event_bus = event_bus

    def complete_order(self, command: CompleteOrderCommand) -> None:
        with transaction.atomic():
            order = self._order_repo.find_by_id(command.order_id)
            if order is None:
                raise OrderNotFoundError("주문을 찾을 수 없습니다")

            order.complete()
            self._order_repo.save(order)

            events = order.collect_domain_events()
            transaction.on_commit(lambda: self._publish(events))

    def _publish(self, events: list[object]) -> None:
        for event in events:
            self._event_bus.publish(event)
```

단, 외부 메시지 브로커, 이메일, 포인트 적립, 재고 차감처럼 **유실되면 안 되는 후속 작업**이 있다면 `on_commit()`만으로 끝내지 말고 Outbox 패턴을 쓰는 편이 안전합니다.

```text
transaction.atomic()
├── order.complete()
├── order_repo.save(order)
└── outbox_repo.save_all(order.collect_domain_events())

별도 worker
└── unpublished outbox 읽기 → broker publish → published 처리
```

정리하면, Django에서는 `post_save` signal로 “주문 상태가 completed면 이벤트 발행” 같은 구조를 피하는 게 좋습니다. 같은 앱 내부 흐름은 보이지 않는 signal보다 `OrderApplicationService.complete_order()`에서 명시적으로 조율하고, 도메인 이벤트는 애그리거트 내부에서 “기록”만 하게 두는 구조가 DDD에 더 맞습니다.

---
> **관련 스킬 참조:**
> - Outbox/트랜잭션 신뢰성 설계 → **architecture-implementation-patterns** 스킬