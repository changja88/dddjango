`config.toml`은 현재 경로에 없고, 워크스페이스도 read-only/empty 상태라 파일 생성이나 pytest 실행은 하지 못했습니다. 아래는 그대로 프로젝트에 옮겨 적용할 수 있는 RED → GREEN → REFACTOR 흐름입니다.

**RED 테스트**

`tests/isolated/unit/orders/test_cancel_order.py`

```python
import pytest

from apps.orders.domain import (
    CannotCancelOrderError,
    Order,
    OrderCanceledEvent,
    OrderStatus,
)


def test_order_cancel_when_pending_marks_order_canceled():
    # Arrange
    order = Order(id=1, status=OrderStatus.PENDING)

    # Act
    events = order.cancel()

    # Assert
    assert order.status == OrderStatus.CANCELED
    assert events == [OrderCanceledEvent(order_id=1, refund_required=False)]


def test_order_cancel_when_paid_marks_order_canceled_and_requires_refund():
    # Arrange
    order = Order(id=1, status=OrderStatus.PAID)

    # Act
    events = order.cancel()

    # Assert
    assert order.status == OrderStatus.CANCELED
    assert events == [OrderCanceledEvent(order_id=1, refund_required=True)]


@pytest.mark.parametrize(
    "status",
    [
        OrderStatus.SHIPPED,
        OrderStatus.DELIVERED,
        OrderStatus.CANCELED,
    ],
)
def test_order_cancel_when_not_cancelable_raises_error(status):
    # Arrange
    order = Order(id=1, status=status)

    # Act / Assert
    with pytest.raises(CannotCancelOrderError):
        order.cancel()
```

예상 실패: `apps.orders.domain` 모듈, `Order`, `OrderStatus`, `OrderCanceledEvent`, `CannotCancelOrderError`, `cancel()`이 아직 없어서 import 또는 attribute 단계에서 실패해야 합니다.

**GREEN 최소 구현**

`apps/orders/domain.py`

```python
from dataclasses import dataclass
from enum import StrEnum


class OrderStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELED = "canceled"


class CannotCancelOrderError(Exception):
    pass


@dataclass(frozen=True)
class OrderCanceledEvent:
    order_id: int
    refund_required: bool


@dataclass
class Order:
    """Aggregate Root. 취소 가능 상태에서만 CANCELED로 전이한다."""

    id: int
    status: OrderStatus

    def cancel(self) -> list[OrderCanceledEvent]:
        if self.status == OrderStatus.PENDING:
            self.status = OrderStatus.CANCELED
            return [OrderCanceledEvent(order_id=self.id, refund_required=False)]

        if self.status == OrderStatus.PAID:
            self.status = OrderStatus.CANCELED
            return [OrderCanceledEvent(order_id=self.id, refund_required=True)]

        raise CannotCancelOrderError(
            f"Order {self.id} cannot be canceled from {self.status}"
        )
```

**REFACTOR 방향**

1. `can_cancel()` 같은 getter성 분기보다 `order.cancel()`에 규칙을 둡니다. 외부 서비스가 `if order.status == ...`로 판단하면 도메인 규칙이 흩어집니다.

2. Django ORM 모델을 바로 애그리거트로 쓸지, 순수 도메인 객체와 ORM 모델을 분리할지 결정합니다. 초기에는 Django 모델 메서드 `cancel()`로 시작해도 되지만, 결제 환불/재고 복구/알림이 붙으면 application service로 조율을 분리합니다.

3. 다음 테스트는 응용 서비스로 확장합니다: `OrderRepository` fake, `PaymentGateway` fake를 두고 “PAID 주문 취소 시 트랜잭션 커밋 후 환불 요청 이벤트가 발행된다”를 검증합니다.

4. 이미 취소된 주문을 에러로 볼지, 멱등 성공으로 볼지 정책을 확정해야 합니다. API 재시도까지 고려하면 application service 레벨에서 멱등키를 처리하는 편이 낫습니다.

실행 명령:

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/unit/orders/test_cancel_order.py -q
```

---
> **관련 스킬 참조:**
> - Django 서비스/API 연결 → **implementation-django** / **implementation-django-ninja** 스킬