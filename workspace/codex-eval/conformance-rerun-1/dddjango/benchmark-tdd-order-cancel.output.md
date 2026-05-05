읽기 전용 워크스페이스라 파일 생성과 pytest 실행은 실행하지 못했습니다. 아래는 실제 프로젝트에 옮겨서 `RED → GREEN → REFACTOR` 순서로 진행할 수 있는 최소 흐름입니다.

**RED: 실패 테스트 먼저**

`tests/isolated/unit/orders/test_cancel_order.py`

```python
import pytest

from apps.orders.domain import Order, OrderStatus
from apps.orders.services import CancelOrderResult, InMemoryOrderRepository, cancel_order


@pytest.mark.parametrize(
    ("status", "refund_required"),
    [
        (OrderStatus.PENDING, False),
        (OrderStatus.PAID, True),
    ],
)
def test_cancel_order_cancelable_status_returns_success(status, refund_required):
    # Arrange
    repo = InMemoryOrderRepository([Order(id=1, status=status)])

    # Act
    result = cancel_order(order_id=1, repository=repo)

    # Assert
    assert result == CancelOrderResult.success(
        order_id=1,
        status=OrderStatus.CANCELED,
        refund_required=refund_required,
    )
    assert repo.get(1).status == OrderStatus.CANCELED


@pytest.mark.parametrize(
    "status",
    [OrderStatus.SHIPPED, OrderStatus.DELIVERED],
)
def test_cancel_order_uncancelable_status_returns_failure(status):
    # Arrange
    repo = InMemoryOrderRepository([Order(id=1, status=status)])

    # Act
    result = cancel_order(order_id=1, repository=repo)

    # Assert
    assert result == CancelOrderResult.failure(
        order_id=1,
        code="ORDER_NOT_CANCELABLE",
        message=f"{status.value} order cannot be canceled",
    )
    assert repo.get(1).status == status


def test_cancel_order_already_canceled_returns_idempotent_success():
    # Arrange
    repo = InMemoryOrderRepository([Order(id=1, status=OrderStatus.CANCELED)])

    # Act
    result = cancel_order(order_id=1, repository=repo)

    # Assert
    assert result == CancelOrderResult.success(
        order_id=1,
        status=OrderStatus.CANCELED,
        already_canceled=True,
    )


def test_cancel_order_missing_order_returns_not_found_failure():
    # Arrange
    repo = InMemoryOrderRepository([])

    # Act
    result = cancel_order(order_id=404, repository=repo)

    # Assert
    assert result == CancelOrderResult.failure(
        order_id=404,
        code="ORDER_NOT_FOUND",
        message="order not found",
    )
```

예상 실패: `apps.orders.domain`, `Order`, `OrderStatus`, `cancel_order`, `CancelOrderResult`, `InMemoryOrderRepository`가 아직 없어서 import 단계에서 실패해야 합니다.

**GREEN: 최소 구현**

`apps/orders/domain.py`

```python
from dataclasses import dataclass
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELED = "canceled"


class OrderCancellationError(Exception):
    pass


class OrderNotCancelable(OrderCancellationError):
    pass


@dataclass
class Order:
    """Aggregate Root. 주문 취소 가능 상태와 상태 전이를 보호한다."""

    id: int
    status: OrderStatus

    def cancel(self) -> bool:
        if self.status == OrderStatus.CANCELED:
            return False

        if self.status not in {OrderStatus.PENDING, OrderStatus.PAID}:
            raise OrderNotCancelable(
                f"{self.status.value} order cannot be canceled"
            )

        refund_required = self.status == OrderStatus.PAID
        self.status = OrderStatus.CANCELED
        return refund_required
```

`apps/orders/services.py`

```python
from dataclasses import dataclass
from typing import Protocol

from apps.orders.domain import Order, OrderNotCancelable, OrderStatus


class OrderRepository(Protocol):
    def get(self, order_id: int) -> Order | None: ...
    def save(self, order: Order) -> None: ...


@dataclass(frozen=True)
class CancelOrderResult:
    ok: bool
    order_id: int
    status: OrderStatus | None = None
    code: str | None = None
    message: str | None = None
    refund_required: bool = False
    already_canceled: bool = False

    @classmethod
    def success(
        cls,
        order_id: int,
        status: OrderStatus,
        refund_required: bool = False,
        already_canceled: bool = False,
    ) -> "CancelOrderResult":
        return cls(
            ok=True,
            order_id=order_id,
            status=status,
            refund_required=refund_required,
            already_canceled=already_canceled,
        )

    @classmethod
    def failure(
        cls,
        order_id: int,
        code: str,
        message: str,
    ) -> "CancelOrderResult":
        return cls(ok=False, order_id=order_id, code=code, message=message)


class InMemoryOrderRepository:
    def __init__(self, orders: list[Order]):
        self.orders = {order.id: order for order in orders}

    def get(self, order_id: int) -> Order | None:
        return self.orders.get(order_id)

    def save(self, order: Order) -> None:
        self.orders[order.id] = order


def cancel_order(order_id: int, repository: OrderRepository) -> CancelOrderResult:
    order = repository.get(order_id)
    if order is None:
        return CancelOrderResult.failure(
            order_id=order_id,
            code="ORDER_NOT_FOUND",
            message="order not found",
        )

    if order.status == OrderStatus.CANCELED:
        return CancelOrderResult.success(
            order_id=order.id,
            status=OrderStatus.CANCELED,
            already_canceled=True,
        )

    try:
        refund_required = order.cancel()
    except OrderNotCancelable as exc:
        return CancelOrderResult.failure(
            order_id=order.id,
            code="ORDER_NOT_CANCELABLE",
            message=str(exc),
        )

    repository.save(order)
    return CancelOrderResult.success(
        order_id=order.id,
        status=order.status,
        refund_required=refund_required,
    )
```

**REFACTOR 방향**

1. Django ORM 어댑터 추가: `DjangoOrderRepository`에서 `select_for_update()`로 주문을 잠그고, 응용 서비스는 `transaction.atomic()` 안에서 호출합니다.
2. `OrderStatus`는 Django 모델에서는 `TextChoices`, 도메인에서는 Enum으로 유지하거나 변환 계층을 둡니다.
3. 환불은 주문 애그리거트 내부에서 외부 결제 SDK를 직접 호출하지 않고 `OrderCanceledEvent` 발행 후 `transaction.on_commit()`에서 처리합니다.
4. API가 필요하면 DRF가 아니라 Django Ninja router에서 `CancelOrderResult`를 응답 schema로 변환합니다.
5. 테스트는 이후 `tests/isolated/integration/orders/test_cancel_order_repository.py`로 ORM repository 저장/락 경계를 추가합니다.

실행 명령:

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/unit/orders/test_cancel_order.py -q
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated -q
```

---
> **관련 스킬 참조:**
> - Django API 엔드포인트 추가 → **implementation-django-ninja** 스킬