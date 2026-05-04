**설계 요약**

| 도메인 용어 | 코드 표현 | 금지 동의어 |
|---|---|---|
| 결제 대기 | `OrderStatus.PAYMENT_WAITING` | `pending`, `ready` |
| 결제 완료 | `order.confirm_payment()` / `PaymentConfirmed` | `charge`, `capture` |
| 취소 요청 | `order.request_cancel()` / `CancelRequested` | `delete`, `rollback` |

API는 동사가 아니라 상태 전이 리소스를 생성하는 형태로 둡니다.

`POST /api/v1/orders/{order_id}/status-transitions`

잘못된 전이는 `409 Conflict`, 요청 값 오류는 `422`, 주문 없음은 `404`로 보고, 오류 본문은 RFC 9457 Problem Details로 맞춥니다.

```python
# orders/domain.py
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class InvalidStateTransition(Exception): ...


@dataclass(frozen=True)
class OrderId:
    value: UUID


class OrderStatus(StrEnum):
    PAYMENT_WAITING = "payment_waiting"
    PAID = "paid"
    CANCEL_REQUESTED = "cancel_requested"


@dataclass(frozen=True)
class PaymentConfirmed:
    order_id: OrderId
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class CancelRequested:
    order_id: OrderId
    occurred_at: datetime = field(default_factory=datetime.now)


class AggregateRoot:
    def __init__(self) -> None:
        self._events: list[object] = []

    def _record_event(self, event: object) -> None:
        self._events.append(event)

    def collect_events(self) -> list[object]:
        events, self._events = self._events, []
        return events


@dataclass
class Order(AggregateRoot):
    """Aggregate Root.
    불변식: 상태 변경은 전이 매트릭스에 있는 경로로만 가능하다.
    """
    id: OrderId
    status: OrderStatus
    version: int = 0

    def __post_init__(self) -> None:
        AggregateRoot.__init__(self)

    def confirm_payment(self) -> None:
        self._transition_to(OrderStatus.PAID)
        self._record_event(PaymentConfirmed(self.id))

    def request_cancel(self) -> None:
        self._transition_to(OrderStatus.CANCEL_REQUESTED)
        self._record_event(CancelRequested(self.id))

    def _transition_to(self, target: OrderStatus) -> None:
        allowed = {
            OrderStatus.PAYMENT_WAITING: {
                OrderStatus.PAID,
                OrderStatus.CANCEL_REQUESTED,
            },
            OrderStatus.PAID: {OrderStatus.CANCEL_REQUESTED},
            OrderStatus.CANCEL_REQUESTED: set(),
        }
        if target not in allowed[self.status]:
            raise InvalidStateTransition(f"{self.status} -> {target}")
        self.status = target


class OrderRepository(Protocol):
    def get(self, order_id: OrderId) -> Order | None: ...
    def save(self, order: Order) -> None: ...
```

```python
# orders/application.py
from dataclasses import dataclass
from django.db import transaction

from .domain import InvalidStateTransition, OrderId, OrderRepository, OrderStatus


@dataclass(frozen=True)
class ChangeOrderStatusCommand:
    order_id: OrderId
    target_status: OrderStatus


class OrderNotFound(Exception): ...


class OrderApplicationService:
    def __init__(self, orders: OrderRepository) -> None:
        self.orders = orders

    def change_status(self, cmd: ChangeOrderStatusCommand):
        with transaction.atomic():
            order = self.orders.get(cmd.order_id)
            if order is None:
                raise OrderNotFound()

            if cmd.target_status == OrderStatus.PAID:
                order.confirm_payment()
            elif cmd.target_status == OrderStatus.CANCEL_REQUESTED:
                order.request_cancel()
            else:
                raise InvalidStateTransition(f"unsupported target: {cmd.target_status}")

            self.orders.save(order)
            events = order.collect_events()

        return order, events
```

`transaction.atomic()`은 “조회 → 도메인 전이 → 저장”을 하나의 원자 단위로 묶기 위해 필요합니다. 같은 주문에 결제 완료와 취소 요청이 동시에 들어올 수 있으므로 저장 시 `version` 조건을 거는 낙관적 잠금을 기본으로 권장합니다. 충돌 빈도가 높은 주문 처리 백오피스라면 repository의 `get()`에서 `select_for_update()` 비관적 락을 선택할 수 있습니다.

```python
# orders/api.py
from uuid import UUID
from ninja import Router, Schema
from ninja.errors import HttpError

from .application import ChangeOrderStatusCommand, OrderApplicationService, OrderNotFound
from .domain import InvalidStateTransition, OrderId, OrderStatus
from .repositories import DjangoOrderRepository

router = Router(tags=["orders"])


class OrderStatusTransitionIn(Schema):
    target_status: OrderStatus


class OrderOut(Schema):
    id: UUID
    status: OrderStatus
    version: int


@router.post("/{order_id}/status-transitions", response=OrderOut)
def change_order_status(request, order_id: UUID, data: OrderStatusTransitionIn) -> OrderOut:
    service = OrderApplicationService(DjangoOrderRepository())
    try:
        order, _events = service.change_status(
            ChangeOrderStatusCommand(
                order_id=OrderId(order_id),
                target_status=data.target_status,
            )
        )
    except OrderNotFound:
        raise HttpError(404, "Order not found")
    except InvalidStateTransition as exc:
        raise HttpError(409, str(exc))

    return OrderOut(id=order.id.value, status=order.status, version=order.version)
```

```python
# config/api.py
from ninja import NinjaAPI
from orders.api import router as orders_router

api = NinjaAPI(version="1.0.0")
api.add_router("/v1/orders", orders_router)
```

```python
# config/urls.py
from django.urls import path
from .api import api

urlpatterns = [path("api/", api.urls)]
```

**검증 단계**

`pytest`에서 `payment_waiting -> paid`, `payment_waiting -> cancel_requested`, `paid -> cancel_requested`는 성공으로 검증하고, `cancel_requested -> paid`는 `409` 또는 `InvalidStateTransition`으로 검증합니다. 동시성은 같은 `version`의 두 요청 중 하나만 저장 성공하도록 repository 테스트를 추가합니다.

---
> **관련 스킬 참조:**
> - API 설계와 오류 형식 → **architecture-api** 스킬
> - 상태 전이와 Aggregate 경계 → **architecture-ddd** 스킬
> - Django Ninja Schema/Router 구현 → **implementation-django-ninja** 스킬