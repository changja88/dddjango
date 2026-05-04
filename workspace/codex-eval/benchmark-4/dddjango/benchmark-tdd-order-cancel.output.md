`/private/tmp/dddjango-codex-eval`은 읽기 전용이고 파일이 비어 있어 pytest를 실제 실행하지 못했습니다. 아래는 그대로 프로젝트에 옮겨 적용할 수 있는 TDD 흐름입니다. `config.toml`도 없어 프로젝트별 설정은 확인하지 못했습니다.

**RED: 실패 테스트 먼저**

`tests/isolated/unit/orders/test_cancel_order.py`

```python
from datetime import datetime, timezone

import pytest

from apps.orders.domain import (
    AlreadyCanceledError,
    CannotCancelOrderError,
    Order,
    OrderStatus,
)


def test_order_cancel_when_paid_changes_status_and_records_cancelled_at():
    # Arrange
    now = datetime(2026, 5, 5, 10, 0, tzinfo=timezone.utc)
    order = Order(id=1, status=OrderStatus.PAID)

    # Act
    order.cancel(now=now)

    # Assert
    assert order.status == OrderStatus.CANCELED
    assert order.cancelled_at == now
    assert order.events == ["OrderCanceledEvent"]


@pytest.mark.parametrize(
    "status",
    [
        OrderStatus.SHIPPED,
        OrderStatus.DELIVERED,
    ],
)
def test_order_cancel_when_not_cancelable_status_raises(status):
    # Arrange
    order = Order(id=1, status=status)

    # Act / Assert
    with pytest.raises(CannotCancelOrderError):
        order.cancel(now=datetime.now(timezone.utc))


def test_order_cancel_when_already_canceled_raises_already_canceled_error():
    # Arrange
    order = Order(id=1, status=OrderStatus.CANCELED)

    # Act / Assert
    with pytest.raises(AlreadyCanceledError):
        order.cancel(now=datetime.now(timezone.utc))
```

**예상 실패**

처음에는 `apps.orders.domain` 모듈, `Order`, `OrderStatus`, 예외 클래스, `cancel()` 메서드가 없어서 `ModuleNotFoundError` 또는 `ImportError`로 실패해야 합니다. 이것이 RED입니다.

**GREEN: 테스트만 통과시키는 최소 구현**

`apps/orders/domain.py`

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class CannotCancelOrderError(Exception):
    pass


class AlreadyCanceledError(Exception):
    pass


class OrderStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELED = "canceled"


@dataclass
class Order:
    """Aggregate Root: 주문 취소 가능 상태 불변식을 보호한다."""

    id: int
    status: OrderStatus
    cancelled_at: datetime | None = None
    events: list[str] = field(default_factory=list)

    def cancel(self, *, now: datetime) -> None:
        if self.status == OrderStatus.CANCELED:
            raise AlreadyCanceledError

        if self.status not in {OrderStatus.PENDING, OrderStatus.PAID}:
            raise CannotCancelOrderError

        self.status = OrderStatus.CANCELED
        self.cancelled_at = now
        self.events.append("OrderCanceledEvent")
```

이 구현은 의도적으로 작습니다. DB 저장, API, 권한, 환불 연동은 아직 넣지 않습니다. 현재 RED 테스트가 요구한 상태 전이와 edge case만 만족시키는 GREEN입니다.

**REFACTOR 방향**

1. `events: list[str]`를 문자열 대신 `@dataclass(frozen=True) class OrderCanceledEvent`로 변경합니다.
2. Django 모델이 이미 있다면 `OrderStatus`는 `models.TextChoices`로 옮기고, 도메인 규칙은 모델의 `cancel()` 또는 도메인 서비스로 유지합니다.
3. 저장까지 포함하는 유스케이스가 필요해지면 `OrderRepository` Protocol/ABC와 `CancelOrderService`를 추가하고, 테스트는 `InMemoryOrderRepository` Fake로 작성합니다.
4. 환불, 재고 복구, 알림 같은 부수효과는 `transaction.on_commit()` 이후 이벤트 핸들러에서 처리합니다.
5. 다음 RED 테스트로 “존재하지 않는 주문 취소”, “권한 없는 사용자 취소”, “배송 준비 중 상태 정책”을 추가해 바깥쪽 유스케이스로 확장합니다.

**pytest 명령**

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/unit/orders/test_cancel_order.py -q
```

순수 도메인 테스트로 Django 설정이 필요 없다면:

```bash
pytest tests/isolated/unit/orders/test_cancel_order.py -q
```

---
> **관련 스킬 참조:**
> - Django pytest/TDD 흐름 → **implementation-tdd**, **implementation-test**, **implementation-django** 스킬