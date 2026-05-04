저장소가 비어 있고 `config.toml`도 없어서, 기존 코드에 맞춘 패치 대신 Django Ninja + DDD 기준의 구현 예시로 정리합니다.

핵심은 **상태 전이 규칙을 API나 ORM 모델이 아니라 도메인 엔티티가 소유**하게 두는 것입니다.

```text
orders/
  domain/
    order.py
    repository.py
  application/
    change_order_status.py
  infrastructure/
    models.py
    repositories.py
  presentation/
    schemas.py
    router.py
```

**상태 전이 규칙**

```python
# orders/domain/order.py
from dataclasses import dataclass
from enum import StrEnum


class OrderStatus(StrEnum):
    PENDING_PAYMENT = "pending_payment"      # 결제 대기
    PAID = "paid"                            # 결제 완료
    CANCEL_REQUESTED = "cancel_requested"    # 취소 요청


class InvalidOrderStatusTransition(Exception):
    pass


_ALLOWED_TRANSITIONS = {
    OrderStatus.PENDING_PAYMENT: {
        OrderStatus.PAID,
        OrderStatus.CANCEL_REQUESTED,
    },
    OrderStatus.PAID: {
        OrderStatus.CANCEL_REQUESTED,
    },
    OrderStatus.CANCEL_REQUESTED: set(),
}


@dataclass
class Order:
    id: int
    status: OrderStatus

    def change_status(self, target: OrderStatus) -> None:
        if target == self.status:
            return

        allowed = _ALLOWED_TRANSITIONS[self.status]
        if target not in allowed:
            raise InvalidOrderStatusTransition(
                f"Cannot change order status from {self.status} to {target}"
            )

        self.status = target
```

**Repository Port**

```python
# orders/domain/repository.py
from typing import Protocol

from .order import Order


class OrderRepository(Protocol):
    def get_by_id_for_update(self, order_id: int) -> Order:
        ...

    def save(self, order: Order) -> None:
        ...
```

**Application Use Case**

```python
# orders/application/change_order_status.py
from dataclasses import dataclass

from django.db import transaction

from orders.domain.order import OrderStatus
from orders.domain.repository import OrderRepository


@dataclass(frozen=True)
class ChangeOrderStatusCommand:
    order_id: int
    target_status: OrderStatus


class ChangeOrderStatusUseCase:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    @transaction.atomic
    def execute(self, command: ChangeOrderStatusCommand):
        order = self.repository.get_by_id_for_update(command.order_id)
        order.change_status(command.target_status)
        self.repository.save(order)
        return order
```

**Django ORM Model**

```python
# orders/infrastructure/models.py
from django.db import models


class OrderModel(models.Model):
    class Status(models.TextChoices):
        PENDING_PAYMENT = "pending_payment", "결제 대기"
        PAID = "paid", "결제 완료"
        CANCEL_REQUESTED = "cancel_requested", "취소 요청"

    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING_PAYMENT,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Repository 구현체**

```python
# orders/infrastructure/repositories.py
from django.shortcuts import get_object_or_404

from orders.domain.order import Order, OrderStatus
from .models import OrderModel


class DjangoOrderRepository:
    def get_by_id_for_update(self, order_id: int) -> Order:
        row = get_object_or_404(
            OrderModel.objects.select_for_update(),
            id=order_id,
        )
        return Order(
            id=row.id,
            status=OrderStatus(row.status),
        )

    def save(self, order: Order) -> None:
        OrderModel.objects.filter(id=order.id).update(
            status=order.status.value,
        )
```

**Django Ninja Schema**

```python
# orders/presentation/schemas.py
from ninja import Schema
from pydantic import field_validator

from orders.domain.order import OrderStatus


class ChangeOrderStatusIn(Schema):
    status: OrderStatus


class OrderOut(Schema):
    id: int
    status: OrderStatus
```

**Django Ninja Router**

```python
# orders/presentation/router.py
from ninja import Router
from ninja.errors import HttpError

from orders.application.change_order_status import (
    ChangeOrderStatusCommand,
    ChangeOrderStatusUseCase,
)
from orders.domain.order import InvalidOrderStatusTransition
from orders.infrastructure.repositories import DjangoOrderRepository
from .schemas import ChangeOrderStatusIn, OrderOut


router = Router(tags=["orders"])


@router.patch("/{order_id}/status", response=OrderOut)
def change_order_status(request, order_id: int, payload: ChangeOrderStatusIn):
    use_case = ChangeOrderStatusUseCase(
        repository=DjangoOrderRepository(),
    )

    try:
        order = use_case.execute(
            ChangeOrderStatusCommand(
                order_id=order_id,
                target_status=payload.status,
            )
        )
    except InvalidOrderStatusTransition as exc:
        raise HttpError(409, str(exc))

    return OrderOut(
        id=order.id,
        status=order.status,
    )
```

**프로젝트 라우터 등록**

```python
# api.py
from ninja import NinjaAPI
from orders.presentation.router import router as orders_router

api = NinjaAPI()
api.add_router("/orders", orders_router)
```

예시 요청:

```http
PATCH /orders/1/status
Content-Type: application/json

{
  "status": "paid"
}
```

허용되는 전이:

```text
pending_payment -> paid
pending_payment -> cancel_requested
paid            -> cancel_requested
```

거부되는 전이:

```text
paid              -> pending_payment
cancel_requested  -> paid
cancel_requested  -> pending_payment
```

이 구조에서 Django Ninja는 입출력과 HTTP 오류 변환만 담당하고, 실제 비즈니스 규칙은 `Order.change_status()` 안에 고립됩니다. 그래서 API, Celery, Admin, 배치 작업 어디서 상태를 바꾸더라도 같은 도메인 규칙을 재사용할 수 있습니다.