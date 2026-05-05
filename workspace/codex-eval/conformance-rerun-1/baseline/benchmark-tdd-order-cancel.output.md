아래는 `pytest`와 TDD로 “주문 취소” 기능을 구현하는 흐름 예시입니다. 핵심은 먼저 상태별 실패 테스트를 만들고, 최소 구현으로 통과시킨 뒤, `Result Type`을 명시해 예외 흐름을 도메인 결과로 드러내는 방식입니다.

**1. 도메인 규칙 정의**

주문 취소 가능 상태:

```python
class OrderStatus:
    PENDING = "pending"
    PAID = "paid"
    PREPARING = "preparing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
```

취소 규칙 예시:

- `PENDING`: 취소 가능
- `PAID`: 취소 가능, 환불 필요
- `PREPARING`: 정책에 따라 취소 가능 또는 불가
- `SHIPPED`: 취소 불가
- `DELIVERED`: 취소 불가
- `CANCELLED`: 이미 취소됨

**2. 명시적 Result Type**

예외를 바로 던지기보다, 성공/실패를 명확히 표현합니다.

```python
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Result(Generic[T]):
    ok: bool
    value: T | None = None
    error: str | None = None

    @classmethod
    def success(cls, value: T):
        return cls(ok=True, value=value)

    @classmethod
    def failure(cls, error: str):
        return cls(ok=False, error=error)
```

도메인 에러 코드는 문자열보다 상수나 Enum이 더 좋습니다.

```python
class CancelOrderError:
    ALREADY_CANCELLED = "already_cancelled"
    NOT_CANCELLABLE = "not_cancellable"
```

**3. 실패 테스트 먼저 작성**

```python
import pytest

from orders.domain import Order, OrderStatus, CancelOrderError


def test_pending_order_can_be_cancelled():
    order = Order(status=OrderStatus.PENDING)

    result = order.cancel()

    assert result.ok is True
    assert order.status == OrderStatus.CANCELLED


def test_paid_order_can_be_cancelled_and_requires_refund():
    order = Order(status=OrderStatus.PAID)

    result = order.cancel()

    assert result.ok is True
    assert order.status == OrderStatus.CANCELLED
    assert result.value.refund_required is True


@pytest.mark.parametrize(
    "status",
    [
        OrderStatus.SHIPPED,
        OrderStatus.DELIVERED,
    ],
)
def test_shipped_or_delivered_order_cannot_be_cancelled(status):
    order = Order(status=status)

    result = order.cancel()

    assert result.ok is False
    assert result.error == CancelOrderError.NOT_CANCELLABLE
    assert order.status == status


def test_cancelled_order_cannot_be_cancelled_again():
    order = Order(status=OrderStatus.CANCELLED)

    result = order.cancel()

    assert result.ok is False
    assert result.error == CancelOrderError.ALREADY_CANCELLED
    assert order.status == OrderStatus.CANCELLED
```

이 시점에서는 `Order.cancel()`이 없거나 미구현이므로 테스트는 실패해야 합니다.

**4. 최소 구현**

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class CancelOrderResult:
    refund_required: bool


class OrderStatus:
    PENDING = "pending"
    PAID = "paid"
    PREPARING = "preparing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class CancelOrderError:
    ALREADY_CANCELLED = "already_cancelled"
    NOT_CANCELLABLE = "not_cancellable"


class Order:
    def __init__(self, status: str):
        self.status = status

    def cancel(self) -> Result[CancelOrderResult]:
        if self.status == OrderStatus.CANCELLED:
            return Result.failure(CancelOrderError.ALREADY_CANCELLED)

        if self.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            return Result.failure(CancelOrderError.NOT_CANCELLABLE)

        refund_required = self.status == OrderStatus.PAID
        self.status = OrderStatus.CANCELLED

        return Result.success(
            CancelOrderResult(refund_required=refund_required)
        )
```

이 구현은 테스트를 통과시키는 최소 수준입니다.

**5. 상태별 Edge Case 추가**

다음 테스트를 추가하면서 정책을 더 명확히 합니다.

```python
def test_preparing_order_cancellation_policy_is_explicit():
    order = Order(status=OrderStatus.PREPARING)

    result = order.cancel()

    assert result.ok is False
    assert result.error == CancelOrderError.NOT_CANCELLABLE
    assert order.status == OrderStatus.PREPARING
```

또는 준비 중 주문을 취소 가능하게 할 수도 있습니다. 중요한 점은 `PREPARING`을 암묵적으로 “기타 취소 가능 상태”에 포함하지 않는 것입니다.

```python
def test_unknown_status_cannot_be_cancelled():
    order = Order(status="unknown")

    result = order.cancel()

    assert result.ok is False
    assert result.error == CancelOrderError.NOT_CANCELLABLE
    assert order.status == "unknown"
```

이 테스트를 추가하면 기존 최소 구현은 `unknown`도 취소해버리므로 실패합니다.

**6. 리팩터링 방향**

취소 가능 상태를 명시적으로 분리합니다.

```python
class Order:
    CANCELLABLE_STATUSES = {
        OrderStatus.PENDING,
        OrderStatus.PAID,
    }

    REFUND_REQUIRED_STATUSES = {
        OrderStatus.PAID,
    }

    def __init__(self, status: str):
        self.status = status

    def cancel(self) -> Result[CancelOrderResult]:
        if self.status == OrderStatus.CANCELLED:
            return Result.failure(CancelOrderError.ALREADY_CANCELLED)

        if self.status not in self.CANCELLABLE_STATUSES:
            return Result.failure(CancelOrderError.NOT_CANCELLABLE)

        refund_required = self.status in self.REFUND_REQUIRED_STATUSES
        self.status = OrderStatus.CANCELLED

        return Result.success(
            CancelOrderResult(refund_required=refund_required)
        )
```

리팩터링 후 다시 테스트를 실행합니다.

```bash
pytest
```

**7. 다음 리팩터링 후보**

- 상태 문자열을 `Enum`으로 변경
- `CancelOrderError`도 `Enum`으로 변경
- 환불 생성이 필요하다면 `Order.cancel()`이 직접 결제 SDK를 호출하지 않게 분리
- DB 저장은 도메인 객체가 아니라 application service에서 처리
- “취소 요청자 권한”, “취소 가능 시간”, “부분 배송”, “환불 실패”는 별도 정책 객체로 분리

예를 들면 application service는 이렇게 둘 수 있습니다.

```python
class CancelOrderService:
    def __init__(self, order_repository):
        self.order_repository = order_repository

    def cancel(self, order_id: int) -> Result[CancelOrderResult]:
        order = self.order_repository.get(order_id)

        result = order.cancel()
        if not result.ok:
            return result

        self.order_repository.save(order)
        return result
```

도메인 규칙은 `Order.cancel()` 안에 두고, 저장소나 외부 결제 연동 같은 세부사항은 바깥으로 밀어내는 구조입니다.