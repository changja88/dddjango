작업 디렉터리가 비어 있고 `config.toml`도 현재 경로에 없어 실제 파일 수정은 못 했습니다. 대신 Django Ninja + DDD 기준으로 바로 적용 가능한 구현 예시를 정리합니다.

**상태 전이**
```text
PAYMENT_PENDING -> PAID
PAYMENT_PENDING -> CANCEL_REQUESTED
PAID            -> CANCEL_REQUESTED
```

`CANCEL_REQUESTED -> PAID` 같은 역전이는 막는 것이 안전합니다.

**권장 구조**
```text
orders/
  domain/
    order.py
    exceptions.py
  application/
    change_order_status.py
  infrastructure/
    models.py
    repositories.py
  presentation/
    api.py
```

**Domain**
```python
# orders/domain/order.py
from dataclasses import dataclass
from enum import StrEnum


class OrderStatus(StrEnum):
    PAYMENT_PENDING = "payment_pending"
    PAID = "paid"
    CANCEL_REQUESTED = "cancel_requested"


ALLOWED_TRANSITIONS = {
    OrderStatus.PAYMENT_PENDING: {
        OrderStatus.PAID,
        OrderStatus.CANCEL_REQUESTED,
    },
    OrderStatus.PAID: {
        OrderStatus.CANCEL_REQUESTED,
    },
    OrderStatus.CANCEL_REQUESTED: set(),
}


class InvalidOrderStatusTransition(Exception):
    pass


@dataclass
class Order:
    id: int
    status: OrderStatus

    def change_status(self, next_status: OrderStatus) -> None:
        if next_status == self.status:
            return

        allowed = ALLOWED_TRANSITIONS[self.status]

        if next_status not in allowed:
            raise InvalidOrderStatusTransition(
                f"Cannot change order status from {self.status} to {next_status}"
            )

        self.status = next_status
```

**Django Model**
```python
# orders/infrastructure/models.py
from django.db import models


class OrderModel(models.Model):
    class Status(models.TextChoices):
        PAYMENT_PENDING = "payment_pending", "Payment pending"
        PAID = "paid", "Paid"
        CANCEL_REQUESTED = "cancel_requested", "Cancel requested"

    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PAYMENT_PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Repository**
```python
# orders/infrastructure/repositories.py
from orders.domain.order import Order, OrderStatus
from orders.infrastructure.models import OrderModel


class DjangoOrderRepository:
    def get_for_update(self, order_id: int) -> Order:
        model = OrderModel.objects.select_for_update().get(id=order_id)

        return Order(
            id=model.id,
            status=OrderStatus(model.status),
        )

    def save(self, order: Order) -> None:
        OrderModel.objects.filter(id=order.id).update(status=order.status.value)
```

**Application Service**
```python
# orders/application/change_order_status.py
from dataclasses import dataclass

from django.db import transaction

from orders.domain.order import OrderStatus


@dataclass
class ChangeOrderStatusCommand:
    order_id: int
    status: OrderStatus


class ChangeOrderStatusService:
    def __init__(self, order_repository):
        self.order_repository = order_repository

    @transaction.atomic
    def execute(self, command: ChangeOrderStatusCommand):
        order = self.order_repository.get_for_update(command.order_id)
        order.change_status(command.status)
        self.order_repository.save(order)
        return order
```

`select_for_update()`와 `transaction.atomic`을 같이 쓰는 이유는 동시에 결제 완료와 취소 요청이 들어오는 경쟁 상황을 막기 위해서입니다.

**Django Ninja API**
```python
# orders/presentation/api.py
from ninja import Router, Schema
from django.shortcuts import get_object_or_404

from orders.application.change_order_status import (
    ChangeOrderStatusCommand,
    ChangeOrderStatusService,
)
from orders.domain.order import OrderStatus, InvalidOrderStatusTransition
from orders.infrastructure.models import OrderModel
from orders.infrastructure.repositories import DjangoOrderRepository

router = Router(tags=["orders"])


class ChangeOrderStatusIn(Schema):
    status: OrderStatus


class OrderOut(Schema):
    id: int
    status: OrderStatus


@router.patch("/{order_id}/status", response={200: OrderOut, 400: dict, 404: dict})
def change_order_status(request, order_id: int, payload: ChangeOrderStatusIn):
    if not OrderModel.objects.filter(id=order_id).exists():
        return 404, {"detail": "Order not found"}

    service = ChangeOrderStatusService(
        order_repository=DjangoOrderRepository(),
    )

    try:
        order = service.execute(
            ChangeOrderStatusCommand(
                order_id=order_id,
                status=payload.status,
            )
        )
    except InvalidOrderStatusTransition as exc:
        return 400, {"detail": str(exc)}

    return 200, OrderOut(id=order.id, status=order.status)
```

**root API 연결**
```python
# config/api.py 또는 urls.py 근처
from ninja import NinjaAPI
from orders.presentation.api import router as orders_router

api = NinjaAPI()
api.add_router("/orders", orders_router)
```

요청 예시는 다음과 같습니다.

```http
PATCH /api/orders/1/status
Content-Type: application/json

{
  "status": "paid"
}
```

```http
PATCH /api/orders/1/status
Content-Type: application/json

{
  "status": "cancel_requested"
}
```

핵심은 상태 전이 규칙을 API나 Django Model에 두지 않고 `Order` 도메인 객체 안에 둔다는 점입니다. API는 입력과 응답만 담당하고, Application Service는 트랜잭션과 유스케이스 흐름을 담당하며, Repository는 Django ORM 접근을 격리합니다.