아래는 Django Ninja + DDD 기준의 “주문 상태 변경 API” 설계 예시입니다. 핵심은 API가 상태 전이 규칙을 직접 알지 않고, 애플리케이션 서비스가 유스케이스를 조율하며, 상태 전이 규칙은 도메인 Aggregate 안에 두는 구조입니다.

**상태 전이 규칙**

```text
PAYMENT_WAITING  -> PAID
PAYMENT_WAITING  -> CANCEL_REQUESTED
PAID             -> CANCEL_REQUESTED
CANCEL_REQUESTED -> 변경 불가
```

## 디렉터리 예시

```text
orders/
  domain/
    order.py
    repository.py
    exceptions.py
  application/
    change_order_status.py
  infrastructure/
    django_models.py
    django_repository.py
  interfaces/
    api.py
```

## Domain

```python
# orders/domain/order.py
from dataclasses import dataclass
from enum import StrEnum


class OrderStatus(StrEnum):
    PAYMENT_WAITING = "PAYMENT_WAITING"
    PAID = "PAID"
    CANCEL_REQUESTED = "CANCEL_REQUESTED"


class InvalidOrderStatusTransition(Exception):
    pass


@dataclass
class Order:
    id: int
    status: OrderStatus

    def mark_as_paid(self) -> None:
        if self.status != OrderStatus.PAYMENT_WAITING:
            raise InvalidOrderStatusTransition(
                f"{self.status} 상태에서는 결제 완료로 변경할 수 없습니다."
            )

        self.status = OrderStatus.PAID

    def request_cancel(self) -> None:
        if self.status not in {
            OrderStatus.PAYMENT_WAITING,
            OrderStatus.PAID,
        }:
            raise InvalidOrderStatusTransition(
                f"{self.status} 상태에서는 취소 요청할 수 없습니다."
            )

        self.status = OrderStatus.CANCEL_REQUESTED
```

```python
# orders/domain/repository.py
from abc import ABC, abstractmethod

from orders.domain.order import Order


class OrderRepository(ABC):
    @abstractmethod
    def get_by_id(self, order_id: int) -> Order:
        raise NotImplementedError

    @abstractmethod
    def save(self, order: Order) -> None:
        raise NotImplementedError
```

## Application Service

```python
# orders/application/change_order_status.py
from dataclasses import dataclass
from enum import StrEnum

from orders.domain.order import Order, OrderStatus
from orders.domain.repository import OrderRepository


class OrderStatusCommand(StrEnum):
    PAY = "PAY"
    REQUEST_CANCEL = "REQUEST_CANCEL"


@dataclass(frozen=True)
class ChangeOrderStatusInput:
    order_id: int
    command: OrderStatusCommand


@dataclass(frozen=True)
class ChangeOrderStatusOutput:
    order_id: int
    status: OrderStatus


class ChangeOrderStatusUseCase:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    def execute(self, data: ChangeOrderStatusInput) -> ChangeOrderStatusOutput:
        order = self.order_repository.get_by_id(data.order_id)

        match data.command:
            case OrderStatusCommand.PAY:
                order.mark_as_paid()
            case OrderStatusCommand.REQUEST_CANCEL:
                order.request_cancel()

        self.order_repository.save(order)

        return ChangeOrderStatusOutput(
            order_id=order.id,
            status=order.status,
        )
```

## Infrastructure

```python
# orders/infrastructure/django_models.py
from django.db import models


class OrderModel(models.Model):
    class Status(models.TextChoices):
        PAYMENT_WAITING = "PAYMENT_WAITING", "결제 대기"
        PAID = "PAID", "결제 완료"
        CANCEL_REQUESTED = "CANCEL_REQUESTED", "취소 요청"

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PAYMENT_WAITING,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

```python
# orders/infrastructure/django_repository.py
from django.shortcuts import get_object_or_404

from orders.domain.order import Order, OrderStatus
from orders.domain.repository import OrderRepository
from orders.infrastructure.django_models import OrderModel


class DjangoOrderRepository(OrderRepository):
    def get_by_id(self, order_id: int) -> Order:
        row = get_object_or_404(OrderModel, id=order_id)

        return Order(
            id=row.id,
            status=OrderStatus(row.status),
        )

    def save(self, order: Order) -> None:
        OrderModel.objects.filter(id=order.id).update(
            status=order.status.value,
        )
```

## Django Ninja API

```python
# orders/interfaces/api.py
from ninja import Router, Schema
from django.db import transaction
from django.http import HttpRequest

from orders.application.change_order_status import (
    ChangeOrderStatusInput,
    ChangeOrderStatusUseCase,
    OrderStatusCommand,
)
from orders.domain.order import InvalidOrderStatusTransition
from orders.infrastructure.django_repository import DjangoOrderRepository

router = Router(tags=["orders"])


class ChangeOrderStatusRequest(Schema):
    command: OrderStatusCommand


class OrderStatusResponse(Schema):
    order_id: int
    status: str


class ErrorResponse(Schema):
    message: str


@router.patch(
    "/orders/{order_id}/status",
    response={
        200: OrderStatusResponse,
        400: ErrorResponse,
        404: ErrorResponse,
    },
)
def change_order_status(
    request: HttpRequest,
    order_id: int,
    payload: ChangeOrderStatusRequest,
):
    use_case = ChangeOrderStatusUseCase(
        order_repository=DjangoOrderRepository(),
    )

    try:
        with transaction.atomic():
            result = use_case.execute(
                ChangeOrderStatusInput(
                    order_id=order_id,
                    command=payload.command,
                )
            )

    except InvalidOrderStatusTransition as exc:
        return 400, ErrorResponse(message=str(exc))

    return 200, OrderStatusResponse(
        order_id=result.order_id,
        status=result.status.value,
    )
```

## URL 등록

```python
# api.py 또는 project-level urls.py
from ninja import NinjaAPI
from orders.interfaces.api import router as orders_router

api = NinjaAPI()
api.add_router("", orders_router)
```

## 요청 예시

결제 완료 처리:

```http
PATCH /orders/1/status
Content-Type: application/json

{
  "command": "PAY"
}
```

취소 요청:

```http
PATCH /orders/1/status
Content-Type: application/json

{
  "command": "REQUEST_CANCEL"
}
```

이 구조에서 중요한 점은 `Order.mark_as_paid()`와 `Order.request_cancel()`이 상태 전이의 단일 진실 공급원이라는 점입니다. API, Django Model, Repository는 도메인 규칙을 직접 판단하지 않습니다.