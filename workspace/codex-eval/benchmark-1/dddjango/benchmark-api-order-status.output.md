## [주요 내용]

현재 워크스페이스는 읽기 전용이고 `config.toml`도 발견되지 않아 파일 생성이나 실행 검증은 하지 못했습니다. 아래는 `apps/orders` 앱을 가정한 Django Ninja + DDD 구현 예시입니다. 이 프로젝트 정책상 API는 DRF가 아니라 Django Ninja로 작성합니다.

**전략적 설계**

| 구분 | 결정 |
|---|---|
| Bounded Context | `Orders` |
| Aggregate Root | `Order` |
| 보호할 불변식 | 결제 완료는 결제 대기 상태에서만 가능, 취소 요청은 결제 대기/결제 완료에서만 가능, 취소 요청 이후에는 추가 상태 전이 불가 |
| 외부 컨텍스트 참조 | `customer_id`, `payment_id`처럼 ID로만 참조 |
| 도메인 이벤트 | `OrderPaidEvent`, `OrderCancellationRequestedEvent` |

**유비쿼터스 언어**

| 한국어 | 코드 용어 | 금지 동의어 |
|---|---|---|
| 결제 대기 | `PAYMENT_WAITING` | `pending`, `ready`, `created` |
| 결제 완료 | `PAYMENT_COMPLETED` | `paid_done`, `success`, `confirmed` |
| 취소 요청 | `CANCELLATION_REQUESTED` | `cancel`, `canceled`, `refund_requested` |
| 결제 완료 처리 | `complete_payment()` | `update_status()` |
| 취소 요청 | `request_cancellation()` | `change_to_cancel()` |

**상태 전이**

| 현재 상태 | 명령 | 다음 상태 | HTTP |
|---|---|---|---|
| `PAYMENT_WAITING` | 결제 완료 | `PAYMENT_COMPLETED` | `PUT /orders/{order_id}/payment` |
| `PAYMENT_WAITING` | 취소 요청 | `CANCELLATION_REQUESTED` | `PUT /orders/{order_id}/cancellation-request` |
| `PAYMENT_COMPLETED` | 취소 요청 | `CANCELLATION_REQUESTED` | `PUT /orders/{order_id}/cancellation-request` |
| `CANCELLATION_REQUESTED` | 결제 완료/취소 요청 | 충돌 또는 멱등 응답 | `409` 또는 `200` |

```python
# apps/orders/domain/order.py
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID


class OrderDomainError(Exception):
    """주문 도메인 규칙 위반을 표현한다."""


class OrderNotFoundError(OrderDomainError):
    """주문을 찾을 수 없을 때 발생한다."""


class InvalidOrderStatusTransitionError(OrderDomainError):
    """허용되지 않은 주문 상태 전이를 시도할 때 발생한다."""


class OrderStatus(StrEnum):
    PAYMENT_WAITING = "payment_waiting"
    PAYMENT_COMPLETED = "payment_completed"
    CANCELLATION_REQUESTED = "cancellation_requested"


@dataclass(frozen=True, slots=True)
class PaymentReceipt:
    """결제 완료 증빙 값 객체."""

    payment_id: str
    paid_at: datetime

    def __post_init__(self) -> None:
        if not self.payment_id.strip():
            raise OrderDomainError("payment_id는 비어 있을 수 없습니다.")


@dataclass(frozen=True, slots=True)
class CancellationReason:
    """취소 요청 사유 값 객체."""

    value: str

    def __post_init__(self) -> None:
        reason = self.value.strip()
        if len(reason) < 3:
            raise OrderDomainError("취소 사유는 3자 이상이어야 합니다.")


@dataclass(frozen=True, slots=True, kw_only=True)
class DomainEvent:
    """도메인에서 이미 발생한 사실."""

    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class OrderPaidEvent(DomainEvent):
    order_id: UUID
    payment_id: str


@dataclass(frozen=True, slots=True)
class OrderCancellationRequestedEvent(DomainEvent):
    order_id: UUID
    reason: str


@dataclass(slots=True)
class Order:
    """주문 애그리거트 루트.

    Invariants:
    - 결제 완료는 PAYMENT_WAITING 상태에서만 가능하다.
    - 결제 완료는 같은 payment_id로만 멱등 재시도할 수 있다.
    - 취소 요청은 PAYMENT_WAITING 또는 PAYMENT_COMPLETED 상태에서만 가능하다.
    - CANCELLATION_REQUESTED 이후에는 상태를 다시 변경하지 않는다.
    """

    id: UUID
    customer_id: UUID
    status: OrderStatus = OrderStatus.PAYMENT_WAITING
    payment_id: str | None = None
    paid_at: datetime | None = None
    cancellation_reason: str | None = None
    cancellation_requested_at: datetime | None = None
    _domain_events: list[DomainEvent] = field(default_factory=list, init=False)

    def complete_payment(self, receipt: PaymentReceipt) -> None:
        if self.status == OrderStatus.PAYMENT_COMPLETED:
            if self.payment_id == receipt.payment_id:
                return
            raise InvalidOrderStatusTransitionError("이미 다른 결제로 완료된 주문입니다.")

        if self.status != OrderStatus.PAYMENT_WAITING:
            raise InvalidOrderStatusTransitionError("결제 대기 상태에서만 결제 완료가 가능합니다.")

        self.status = OrderStatus.PAYMENT_COMPLETED
        self.payment_id = receipt.payment_id
        self.paid_at = receipt.paid_at
        self._record_event(OrderPaidEvent(order_id=self.id, payment_id=receipt.payment_id))

    def request_cancellation(self, reason: CancellationReason) -> None:
        if self.status == OrderStatus.CANCELLATION_REQUESTED:
            return

        if self.status not in {
            OrderStatus.PAYMENT_WAITING,
            OrderStatus.PAYMENT_COMPLETED,
        }:
            raise InvalidOrderStatusTransitionError("현재 상태에서는 취소 요청이 불가능합니다.")

        self.status = OrderStatus.CANCELLATION_REQUESTED
        self.cancellation_reason = reason.value
        self.cancellation_requested_at = datetime.now(UTC)
        self._record_event(
            OrderCancellationRequestedEvent(order_id=self.id, reason=reason.value)
        )

    def collect_domain_events(self) -> list[DomainEvent]:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events

    def _record_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)


class OrderRepository(ABC):
    """Order 애그리거트 리포지토리 인터페이스."""

    @abstractmethod
    def find_by_id(self, order_id: UUID) -> Order | None:
        ...

    @abstractmethod
    def find_by_id_for_update(self, order_id: UUID) -> Order | None:
        ...

    @abstractmethod
    def save(self, order: Order) -> None:
        ...
```

```python
# apps/orders/models.py
import uuid

from django.db import models


class OrderModel(models.Model):
    class Status(models.TextChoices):
        PAYMENT_WAITING = "payment_waiting", "Payment waiting"
        PAYMENT_COMPLETED = "payment_completed", "Payment completed"
        CANCELLATION_REQUESTED = "cancellation_requested", "Cancellation requested"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id = models.UUIDField(db_index=True)
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PAYMENT_WAITING,
        db_index=True,
    )
    payment_id = models.CharField(max_length=128, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True)
    cancellation_requested_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["customer_id", "-created_at"], name="order_customer_created_idx"),
            models.Index(fields=["status"], name="order_status_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.id} ({self.status})"
```

```python
# apps/orders/infrastructure/repositories.py
from uuid import UUID

from apps.orders.domain.order import Order, OrderRepository, OrderStatus
from apps.orders.models import OrderModel


class DjangoOrderRepository(OrderRepository):
    """Django ORM 기반 Order 리포지토리."""

    def find_by_id(self, order_id: UUID) -> Order | None:
        return self._find(OrderModel.objects, order_id)

    def find_by_id_for_update(self, order_id: UUID) -> Order | None:
        return self._find(OrderModel.objects.select_for_update(), order_id)

    def save(self, order: Order) -> None:
        OrderModel.objects.update_or_create(
            id=order.id,
            defaults={
                "customer_id": order.customer_id,
                "status": order.status.value,
                "payment_id": order.payment_id,
                "paid_at": order.paid_at,
                "cancellation_reason": order.cancellation_reason or "",
                "cancellation_requested_at": order.cancellation_requested_at,
            },
        )

    def _find(self, queryset, order_id: UUID) -> Order | None:
        try:
            model = queryset.get(id=order_id)
        except OrderModel.DoesNotExist:
            return None
        return self._to_domain(model)

    def _to_domain(self, model: OrderModel) -> Order:
        return Order(
            id=model.id,
            customer_id=model.customer_id,
            status=OrderStatus(model.status),
            payment_id=model.payment_id,
            paid_at=model.paid_at,
            cancellation_reason=model.cancellation_reason or None,
            cancellation_requested_at=model.cancellation_requested_at,
        )
```

```python
# apps/orders/application/services.py
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from django.db import transaction

from apps.orders.domain.order import (
    CancellationReason,
    DomainEvent,
    Order,
    OrderNotFoundError,
    OrderRepository,
    PaymentReceipt,
)


class EventBus(Protocol):
    """커밋 이후 도메인 이벤트를 발행한다."""

    def publish_many(self, events: list[DomainEvent]) -> None:
        ...


@dataclass(frozen=True, slots=True)
class CompleteOrderPaymentCommand:
    order_id: UUID
    payment_id: str
    paid_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class RequestOrderCancellationCommand:
    order_id: UUID
    reason: str


class OrderApplicationService:
    """주문 상태 변경 유스케이스를 조율한다."""

    def __init__(self, repository: OrderRepository, event_bus: EventBus) -> None:
        self._repository = repository
        self._event_bus = event_bus

    def complete_payment(self, command: CompleteOrderPaymentCommand) -> Order:
        with transaction.atomic():
            order = self._get_order_for_update(command.order_id)
            order.complete_payment(
                PaymentReceipt(
                    payment_id=command.payment_id,
                    paid_at=command.paid_at or datetime.now(UTC),
                )
            )
            self._repository.save(order)
            events = order.collect_domain_events()
            transaction.on_commit(lambda: self._event_bus.publish_many(events))
            return order

    def request_cancellation(self, command: RequestOrderCancellationCommand) -> Order:
        with transaction.atomic():
            order = self._get_order_for_update(command.order_id)
            order.request_cancellation(CancellationReason(command.reason))
            self._repository.save(order)
            events = order.collect_domain_events()
            transaction.on_commit(lambda: self._event_bus.publish_many(events))
            return order

    def _get_order_for_update(self, order_id: UUID) -> Order:
        order = self._repository.find_by_id_for_update(order_id)
        if order is None:
            raise OrderNotFoundError("주문을 찾을 수 없습니다.")
        return order
```

```python
# apps/orders/api/schemas.py
from datetime import datetime
from uuid import UUID

from ninja import Schema

from apps.orders.domain.order import Order, OrderStatus


class ProblemDetails(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str


class CompletePaymentIn(Schema):
    payment_id: str
    paid_at: datetime | None = None


class CancellationRequestIn(Schema):
    reason: str


class OrderOut(Schema):
    id: UUID
    customer_id: UUID
    status: OrderStatus
    payment_id: str | None = None
    paid_at: datetime | None = None
    cancellation_reason: str | None = None
    cancellation_requested_at: datetime | None = None

    @classmethod
    def from_domain(cls, order: Order) -> "OrderOut":
        return cls(
            id=order.id,
            customer_id=order.customer_id,
            status=order.status,
            payment_id=order.payment_id,
            paid_at=order.paid_at,
            cancellation_reason=order.cancellation_reason,
            cancellation_requested_at=order.cancellation_requested_at,
        )
```

```python
# apps/orders/api/router.py
from uuid import UUID

from ninja import Router
from ninja.security import django_auth

from apps.orders.api.schemas import (
    CancellationRequestIn,
    CompletePaymentIn,
    OrderOut,
    ProblemDetails,
)
from apps.orders.application.services import (
    CompleteOrderPaymentCommand,
    OrderApplicationService,
    RequestOrderCancellationCommand,
)
from apps.orders.domain.order import (
    InvalidOrderStatusTransitionError,
    OrderDomainError,
    OrderNotFoundError,
)
from apps.orders.infrastructure.repositories import DjangoOrderRepository

router = Router(auth=django_auth, tags=["orders"])


class InProcessEventBus:
    def publish_many(self, events: list[object]) -> None:
        for event in events:
            print(event)


def build_order_service() -> OrderApplicationService:
    return OrderApplicationService(
        repository=DjangoOrderRepository(),
        event_bus=InProcessEventBus(),
    )


@router.put(
    "/{order_id}/payment",
    response={200: OrderOut, 404: ProblemDetails, 409: ProblemDetails},
)
def complete_payment(
    request,
    order_id: UUID,
    payload: CompletePaymentIn,
) -> tuple[int, OrderOut | ProblemDetails]:
    service = build_order_service()
    try:
        order = service.complete_payment(
            CompleteOrderPaymentCommand(
                order_id=order_id,
                payment_id=payload.payment_id,
                paid_at=payload.paid_at,
            )
        )
    except OrderNotFoundError as exc:
        return 404, problem(404, "Order not found", str(exc), request.path)
    except InvalidOrderStatusTransitionError as exc:
        return 409, problem(409, "Invalid order status transition", str(exc), request.path)
    return 200, OrderOut.from_domain(order)


@router.put(
    "/{order_id}/cancellation-request",
    response={200: OrderOut, 404: ProblemDetails, 409: ProblemDetails},
)
def request_cancellation(
    request,
    order_id: UUID,
    payload: CancellationRequestIn,
) -> tuple[int, OrderOut | ProblemDetails]:
    service = build_order_service()
    try:
        order = service.request_cancellation(
            RequestOrderCancellationCommand(order_id=order_id, reason=payload.reason)
        )
    except OrderNotFoundError as exc:
        return 404, problem(404, "Order not found", str(exc), request.path)
    except OrderDomainError as exc:
        return 409, problem(409, "Invalid order status transition", str(exc), request.path)
    return 200, OrderOut.from_domain(order)


def problem(status: int, title: str, detail: str, instance: str) -> ProblemDetails:
    return ProblemDetails(
        type=f"https://api.example.com/problems/{title.lower().replace(' ', '-')}",
        title=title,
        status=status,
        detail=detail,
        instance=instance,
    )
```

```python
# apps/orders/api/selectors.py
from uuid import UUID

from apps.orders.models import OrderModel


def get_order_detail(order_id: UUID) -> OrderModel | None:
    return OrderModel.objects.filter(id=order_id).first()
```

```python
# config/api.py
from ninja import NinjaAPI

from apps.orders.api.router import router as orders_router

api = NinjaAPI(title="Order API", version="1.0.0")
api.add_router("/orders", orders_router)
```

```python
# config/urls.py
from django.urls import path

from config.api import api

urlpatterns = [
    path("api/", api.urls),
]
```

검증 명령은 실제 프로젝트에서 아래 순서로 돌리면 됩니다.

```bash
python manage.py makemigrations orders
python manage.py migrate
python manage.py test apps.orders
python manage.py check --deploy
```

PEP 695 제네릭은 이 예시에서 별도 범용 컬렉션/컨테이너 추상화가 없어 사용하지 않았습니다. 핵심은 상태 전이를 `update_status()` 같은 범용 setter로 열지 않고, `complete_payment()`와 `request_cancellation()`이라는 도메인 명령으로만 통과시키는 것입니다.

## [관련 스킬 참조]

---
> **관련 스킬 참조:**
> - 도메인 이벤트/애그리거트 확장 → **architecture-ddd** 스킬
> - 상태 변경 API 오류 형식/버저닝 → **architecture-api** 스킬
> - Django Ninja 테스트와 인증 구성 → **implementation-django-ninja** 스킬
> - 동시성/락/인덱스 검토 → **architecture-db** 스킬