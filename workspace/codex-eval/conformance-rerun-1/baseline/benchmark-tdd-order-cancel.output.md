아래는 `pytest`와 TDD로 “주문 취소” 기능을 구현하는 흐름 예시입니다. 핵심은 **상태 전이 규칙을 먼저 테스트로 고정**하고, 실패 테스트 → 최소 구현 → 리팩터링 순서로 확장하는 것입니다.

**도메인 규칙**
주문 상태 예시:

```python
from enum import Enum


class OrderStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    PREPARING = "preparing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELED = "canceled"
```

취소 가능 상태:

```text
PENDING   -> 취소 가능
PAID      -> 취소 가능
PREPARING -> 정책에 따라 가능/불가, 여기서는 불가
SHIPPED   -> 불가
DELIVERED -> 불가
CANCELED  -> 이미 취소됨
```

명시적 Result Type:

```python
from dataclasses import dataclass
from typing import Generic, TypeVar, Literal

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True)
class Result(Generic[T, E]):
    ok: bool
    value: T | None = None
    error: E | None = None

    @classmethod
    def success(cls, value: T) -> "Result[T, E]":
        return cls(ok=True, value=value)

    @classmethod
    def failure(cls, error: E) -> "Result[T, E]":
        return cls(ok=False, error=error)


CancelError = Literal[
    "ORDER_NOT_CANCELABLE",
    "ORDER_ALREADY_CANCELED",
]
```

---

**1. 실패 테스트부터 작성**

```python
# tests/test_order_cancel.py

from order import Order, OrderStatus


def test_cancel_pending_order():
    order = Order(status=OrderStatus.PENDING)

    result = order.cancel()

    assert result.ok is True
    assert order.status == OrderStatus.CANCELED


def test_cancel_paid_order():
    order = Order(status=OrderStatus.PAID)

    result = order.cancel()

    assert result.ok is True
    assert order.status == OrderStatus.CANCELED


def test_cannot_cancel_shipped_order():
    order = Order(status=OrderStatus.SHIPPED)

    result = order.cancel()

    assert result.ok is False
    assert result.error == "ORDER_NOT_CANCELABLE"
    assert order.status == OrderStatus.SHIPPED


def test_cannot_cancel_delivered_order():
    order = Order(status=OrderStatus.DELIVERED)

    result = order.cancel()

    assert result.ok is False
    assert result.error == "ORDER_NOT_CANCELABLE"
    assert order.status == OrderStatus.DELIVERED


def test_cancel_already_canceled_order_is_explicit_failure():
    order = Order(status=OrderStatus.CANCELED)

    result = order.cancel()

    assert result.ok is False
    assert result.error == "ORDER_ALREADY_CANCELED"
    assert order.status == OrderStatus.CANCELED
```

처음에는 `Order`, `cancel`, `Result`가 없으므로 테스트가 실패합니다. 이 실패는 정상입니다.

---

**2. 최소 구현**

```python
# order.py

from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar, Literal

T = TypeVar("T")
E = TypeVar("E")


class OrderStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    PREPARING = "preparing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELED = "canceled"


CancelError = Literal[
    "ORDER_NOT_CANCELABLE",
    "ORDER_ALREADY_CANCELED",
]


@dataclass(frozen=True)
class Result(Generic[T, E]):
    ok: bool
    value: T | None = None
    error: E | None = None

    @classmethod
    def success(cls, value: T) -> "Result[T, E]":
        return cls(ok=True, value=value)

    @classmethod
    def failure(cls, error: E) -> "Result[T, E]":
        return cls(ok=False, error=error)


@dataclass
class Order:
    status: OrderStatus

    def cancel(self) -> Result["Order", CancelError]:
        if self.status == OrderStatus.CANCELED:
            return Result.failure("ORDER_ALREADY_CANCELED")

        if self.status not in {OrderStatus.PENDING, OrderStatus.PAID}:
            return Result.failure("ORDER_NOT_CANCELABLE")

        self.status = OrderStatus.CANCELED
        return Result.success(self)
```

여기까지는 테스트를 통과시키는 최소 구현입니다.

---

**3. 상태별 Edge Case 추가**

상태별 테스트를 명시적으로 고정합니다.

```python
import pytest
from order import Order, OrderStatus


@pytest.mark.parametrize("status", [
    OrderStatus.PENDING,
    OrderStatus.PAID,
])
def test_cancelable_statuses(status):
    order = Order(status=status)

    result = order.cancel()

    assert result.ok is True
    assert order.status == OrderStatus.CANCELED


@pytest.mark.parametrize("status", [
    OrderStatus.PREPARING,
    OrderStatus.SHIPPED,
    OrderStatus.DELIVERED,
])
def test_non_cancelable_statuses(status):
    order = Order(status=status)

    result = order.cancel()

    assert result.ok is False
    assert result.error == "ORDER_NOT_CANCELABLE"
    assert order.status == status
```

추가로 고려할 edge case:

```text
PENDING   -> 취소 성공
PAID      -> 취소 성공, 환불 프로세스 필요 가능
PREPARING -> 정책에 따라 갈림. 출고 준비 전이면 가능할 수도 있음
SHIPPED   -> 취소 불가, 반품 플로우로 유도
DELIVERED -> 취소 불가, 반품/환불 플로우로 유도
CANCELED  -> 중복 취소. idempotent success로 볼지 explicit failure로 볼지 정책 필요
```

이 예시는 `CANCELED`를 명시적 실패로 처리합니다.

---

**4. 리팩터링 방향**

취소 가능 상태가 `cancel()` 안에 박혀 있으므로 정책으로 분리할 수 있습니다.

```python
CANCELABLE_STATUSES = {
    OrderStatus.PENDING,
    OrderStatus.PAID,
}


@dataclass
class Order:
    status: OrderStatus

    def cancel(self) -> Result["Order", CancelError]:
        if self.status == OrderStatus.CANCELED:
            return Result.failure("ORDER_ALREADY_CANCELED")

        if not self.is_cancelable():
            return Result.failure("ORDER_NOT_CANCELABLE")

        self.status = OrderStatus.CANCELED
        return Result.success(self)

    def is_cancelable(self) -> bool:
        return self.status in CANCELABLE_STATUSES
```

다음 단계에서 복잡도가 커지면 이런 식으로 확장합니다.

```text
단순 상태 규칙만 있음
-> Order.is_cancelable() 유지

결제 상태, 배송 상태, 환불 정책이 얽힘
-> CancelPolicy 분리

DB 저장, 이벤트 발행, 환불 요청이 필요함
-> Order.cancel()은 상태 전이만 담당
-> CancelOrderService가 저장소, 결제, 이벤트를 조율

실패 사유가 늘어남
-> 문자열 Literal 대신 Enum 또는 전용 Error dataclass 사용
```

예를 들어 서비스 계층은 이렇게 둘 수 있습니다.

```python
@dataclass
class CancelOrderService:
    orders: OrderRepository

    def cancel(self, order_id: str) -> Result[Order, CancelError]:
        order = self.orders.get(order_id)
        result = order.cancel()

        if not result.ok:
            return result

        self.orders.save(order)
        return Result.success(order)
```

핵심 TDD 흐름은 다음 순서입니다.

```text
1. PENDING 주문 취소 테스트 작성 -> 실패
2. 최소 Order.cancel() 구현 -> 성공
3. PAID 취소 테스트 추가 -> 실패 또는 성공 확인
4. SHIPPED/DELIVERED 취소 불가 테스트 추가 -> 최소 조건 추가
5. CANCELED 중복 취소 테스트 추가 -> 명시적 실패 처리
6. 상태별 parametrized test로 정리
7. cancelable 상태 규칙을 is_cancelable 또는 정책 객체로 리팩터링
8. 서비스 계층이 필요해질 때 저장, 환불, 이벤트 발행을 분리
```

이렇게 가면 테스트가 주문 취소 정책의 문서 역할을 하고, `Result`가 성공/실패를 예외 없이 명시적으로 드러냅니다.