**주요 내용**

설계 기준은 `Ordering` 바운디드 컨텍스트 안의 `Order` 애그리거트입니다. API는 상태값을 직접 바꾸지 않고, Django Ninja `Router`가 요청을 받고 `OrderApplicationService`가 유스케이스를 조율하며, 실제 전이 규칙은 도메인 모델이 보유합니다.

| 용어 | 의미 | 금지 동의어 |
|---|---|---|
| `PAYMENT_PENDING` | 결제 대기 | waiting, ready |
| `PAID` | 결제 완료 | confirmed, completed |
| `CANCEL_REQUESTED` | 취소 요청 | canceled, refunding |

전이 규칙:

```text
PAYMENT_PENDING -> PAID
PAYMENT_PENDING -> CANCEL_REQUESTED
PAID            -> CANCEL_REQUESTED
CANCEL_REQUESTED -> 전이 불가
```

API는 명사 기반 리소스로 둡니다.

```text
PATCH /api/v1/orders/{order_id}/status
200 OK
409 Conflict: 허용되지 않는 상태 전이
404 Not Found: 주문 없음
422 Unprocessable Entity: 요청 검증 실패
```

**도메인 계층**

```python
# orders/domain.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum


class OrderStatus(StrEnum):
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAID = "PAID"
    CANCEL_REQUESTED = "CANCEL_REQUESTED"


class InvalidStateTransition(Exception):
    pass


@dataclass(frozen=True)
class OrderId:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("order_id must be positive")


@dataclass(frozen=True)
class OrderStatusChangedEvent:
    order_id: OrderId
    previous_status: OrderStatus
    current_status: OrderStatus


class Order:
    """Invariant: status changes only through transition methods."""

    def __init__(self, order_id: OrderId, status: OrderStatus) -> None:
        self.id = order_id
        self.status = status
        self._events: list[OrderStatusChangedEvent] = []

    def confirm_payment(self) -> None:
        self._transition_to(OrderStatus.PAID)

    def request_cancellation(self) -> None:
        self._transition_to(OrderStatus.CANCEL_REQUESTED)

    def _transition_to(self, next_status: OrderStatus) -> None:
        allowed = {
            OrderStatus.PAYMENT_PENDING: {
                OrderStatus.PAID,
                OrderStatus.CANCEL_REQUESTED,
            },
            OrderStatus.PAID: {OrderStatus.CANCEL_REQUESTED},
            OrderStatus.CANCEL_REQUESTED: set(),
        }
        if next_status not in allowed[self.status]:
            raise InvalidStateTransition(f"{self.status} -> {next_status}")

        previous = self.status
        self.status = next_status
        self._events.append(OrderStatusChangedEvent(self.id, previous, next_status))

    def collect_events(self) -> list[OrderStatusChangedEvent]:
        events = self._events[:]
        self._events.clear()
        return events


class OrderRepository(ABC):
    @abstractmethod
    def get(self, order_id: OrderId) -> Order:
        raise NotImplementedError

    @abstractmethod
    def save(self, order: Order) -> None:
        raise NotImplementedError
```

**Django ORM 어댑터 + 서비스**

```python
# orders/models.py
from django.db import models


class OrderModel(models.Model):
    class Status(models.TextChoices):
        PAYMENT_PENDING = "PAYMENT_PENDING"
        PAID = "PAID"
        CANCEL_REQUESTED = "CANCEL_REQUESTED"

    status = models.CharField(max_length=32, choices=Status, db_index=True)
    version = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
```

```python
# orders/application.py
from django.db import transaction

from .domain import OrderId, OrderRepository, OrderStatus


class OrderApplicationService:
    def __init__(self, repository: OrderRepository) -> None:
        self.repository = repository

    @transaction.atomic
    def change_status(self, order_id: int, next_status: OrderStatus) -> None:
        order = self.repository.get(OrderId(order_id))

        if next_status == OrderStatus.PAID:
            order.confirm_payment()
        elif next_status == OrderStatus.CANCEL_REQUESTED:
            order.request_cancellation()
        else:
            raise ValueError("unsupported target status")

        self.repository.save(order)
```

```python
# orders/repository.py
from django.shortcuts import get_object_or_404

from .domain import Order, OrderId, OrderRepository, OrderStatus
from .models import OrderModel


class DjangoOrderRepository(OrderRepository):
    def get(self, order_id: OrderId) -> Order:
        row = get_object_or_404(
            OrderModel.objects.select_for_update(),
            id=order_id.value,
        )
        return Order(OrderId(row.id), OrderStatus(row.status))

    def save(self, order: Order) -> None:
        OrderModel.objects.filter(id=order.id.value).update(status=order.status)
```

`transaction.atomic()`은 읽기-검증-쓰기 전체를 하나의 트랜잭션으로 묶기 위해 필요합니다. 동시에 같은 주문을 결제 완료와 취소 요청으로 바꾸는 요청이 들어오면 전이 검증이 깨질 수 있으므로, 이 예시는 `select_for_update()`로 해당 주문 행을 잠급니다. 충돌 빈도가 낮고 재시도 UX가 가능하면 `version` 기반 낙관적 잠금으로 바꾸는 것이 기본 선택입니다.

**Django Ninja API**

```python
# orders/api.py
from ninja import Router, Schema
from ninja.errors import HttpError

from .application import OrderApplicationService
from .domain import InvalidStateTransition, OrderStatus
from .repository import DjangoOrderRepository

router = Router(tags=["orders"])


class OrderStatusChangeIn(Schema):
    status: OrderStatus


class OrderStatusOut(Schema):
    id: int
    status: OrderStatus


@router.patch("/{order_id}/status", response={200: OrderStatusOut})
def change_order_status(
    request,
    order_id: int,
    payload: OrderStatusChangeIn,
) -> OrderStatusOut:
    service = OrderApplicationService(DjangoOrderRepository())

    try:
        service.change_status(order_id, payload.status)
    except InvalidStateTransition as exc:
        raise HttpError(409, str(exc))

    return OrderStatusOut(id=order_id, status=payload.status)
```

```python
# config/api.py
from ninja import NinjaAPI
from orders.api import router as orders_router

api = NinjaAPI()
api.add_router("/v1/orders", orders_router)
```

```python
# config/urls.py
from django.urls import path
from .api import api

urlpatterns = [path("api/", api.urls)]
```

**검증 단계**

```bash
python manage.py makemigrations orders
python manage.py migrate
python manage.py test orders
python manage.py check
```

추가 테스트는 `PAYMENT_PENDING -> PAID`, `PAYMENT_PENDING -> CANCEL_REQUESTED`, `PAID -> CANCEL_REQUESTED`는 성공, `CANCEL_REQUESTED -> PAID`는 `409 Conflict`인지 확인하면 됩니다.

---
> **관련 스킬 참조:**
> - 상태 전이/애그리거트 설계 → **architecture-ddd** 스킬
> - Django Ninja Schema/Router 구현 → **implementation-django-ninja** 스킬