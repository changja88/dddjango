**주요 내용**

현재 워크스페이스가 `read-only`라 테스트 파일 생성이나 `pytest` 실행은 하지 못했습니다. 아래는 실제 프로젝트에 옮겨 실행할 수 있는 TDD 흐름입니다.

전제 도메인 규칙은 이렇게 둡니다.

| 상태 | 취소 결과 |
|---|---|
| `PLACED` | 취소 가능 |
| `PAID` | 취소 가능, 이후 환불 연계 가능 |
| `PREPARING` | 취소 불가 |
| `SHIPPED` | 취소 불가 |
| `DELIVERED` | 취소 불가 |
| `CANCELLED` | 멱등 처리, 이미 취소됨 |
| 주문 없음 | `NOT_FOUND` |

## 1. RED 실패 테스트

`tests/isolated/unit/test_cancel_order.py`

```python
import pytest

from orders.application import CancelOrderApplicationService
from orders.domain import (
    CancelOrderResultKind,
    InMemoryOrderRepository,
    Order,
    OrderId,
    OrderStatus,
)


@pytest.fixture
def repository():
    repo = InMemoryOrderRepository()
    yield repo
    repo.clear()


@pytest.mark.parametrize("status", [OrderStatus.PLACED, OrderStatus.PAID])
def test_cancel_order_cancellable_status_returns_cancelled_result(repository, status):
    # Arrange
    order = Order(id=OrderId("order-1"), status=status)
    repository.save(order)
    service = CancelOrderApplicationService(repository)

    # Act
    result = service.cancel(OrderId("order-1"), reason="customer_request")

    # Assert
    assert result.kind == CancelOrderResultKind.CANCELLED
    assert result.order_id == OrderId("order-1")
    assert result.order_status == OrderStatus.CANCELLED
    assert result.is_success is True
    assert repository.get(OrderId("order-1")).status == OrderStatus.CANCELLED
    assert [event.order_id for event in result.events] == [OrderId("order-1")]


@pytest.mark.parametrize(
    "status",
    [OrderStatus.PREPARING, OrderStatus.SHIPPED, OrderStatus.DELIVERED],
)
def test_cancel_order_non_cancellable_status_returns_not_cancellable_result(repository, status):
    # Arrange
    order = Order(id=OrderId("order-1"), status=status)
    repository.save(order)
    service = CancelOrderApplicationService(repository)

    # Act
    result = service.cancel(OrderId("order-1"), reason="customer_request")

    # Assert
    assert result.kind == CancelOrderResultKind.NOT_CANCELLABLE
    assert result.order_status == status
    assert result.is_success is False
    assert result.events == ()
    assert repository.get(OrderId("order-1")).status == status


def test_cancel_order_cancelled_status_returns_already_cancelled_result(repository):
    # Arrange
    order = Order(id=OrderId("order-1"), status=OrderStatus.CANCELLED)
    repository.save(order)
    service = CancelOrderApplicationService(repository)

    # Act
    result = service.cancel(OrderId("order-1"), reason="duplicate_request")

    # Assert
    assert result.kind == CancelOrderResultKind.ALREADY_CANCELLED
    assert result.order_status == OrderStatus.CANCELLED
    assert result.is_success is True
    assert result.events == ()


def test_cancel_order_missing_order_returns_not_found_result(repository):
    # Arrange
    service = CancelOrderApplicationService(repository)

    # Act
    result = service.cancel(OrderId("missing-order"), reason="customer_request")

    # Assert
    assert result.kind == CancelOrderResultKind.NOT_FOUND
    assert result.order_id == OrderId("missing-order")
    assert result.order_status is None
    assert result.is_success is False
    assert result.events == ()
```

예상 실패 이유:

```text
ModuleNotFoundError: No module named 'orders'
```

또는 최소 파일만 있는 상태라면 다음이 실패해야 정상입니다.

```text
ImportError: cannot import name 'CancelOrderApplicationService'
AttributeError: 'Order' object has no attribute 'cancel'
AssertionError: result.kind ...
```

## 2. GREEN 최소 구현

`orders/domain.py`

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum


class OrderStatus(StrEnum):
    PLACED = "placed"
    PAID = "paid"
    PREPARING = "preparing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class CancelOrderResultKind(StrEnum):
    CANCELLED = "cancelled"
    ALREADY_CANCELLED = "already_cancelled"
    NOT_CANCELLABLE = "not_cancellable"
    NOT_FOUND = "not_found"


@dataclass(frozen=True)
class OrderId:
    value: str

    def __post_init__(self):
        if not self.value.strip():
            raise ValueError("order_id must not be blank")


@dataclass(frozen=True)
class OrderCancelledEvent:
    order_id: OrderId
    reason: str


@dataclass(frozen=True)
class CancelOrderResult:
    kind: CancelOrderResultKind
    order_id: OrderId
    order_status: OrderStatus | None
    events: tuple[OrderCancelledEvent, ...] = ()

    @property
    def is_success(self) -> bool:
        return self.kind in {
            CancelOrderResultKind.CANCELLED,
            CancelOrderResultKind.ALREADY_CANCELLED,
        }


class Order:
    """
    Aggregate Root.

    Invariants:
    - CANCELLED 주문은 다시 취소 이벤트를 만들지 않는다.
    - PREPARING, SHIPPED, DELIVERED 주문은 주문 취소 유스케이스로 취소할 수 없다.
    - 취소 가능한 상태는 PLACED, PAID뿐이다.
    """

    _CANCELLABLE_STATUSES = {OrderStatus.PLACED, OrderStatus.PAID}

    def __init__(self, id: OrderId, status: OrderStatus):
        self.id = id
        self.status = status

    def cancel(self, reason: str) -> CancelOrderResult:
        if self.status == OrderStatus.CANCELLED:
            return CancelOrderResult(
                kind=CancelOrderResultKind.ALREADY_CANCELLED,
                order_id=self.id,
                order_status=self.status,
            )

        if self.status not in self._CANCELLABLE_STATUSES:
            return CancelOrderResult(
                kind=CancelOrderResultKind.NOT_CANCELLABLE,
                order_id=self.id,
                order_status=self.status,
            )

        self.status = OrderStatus.CANCELLED
        event = OrderCancelledEvent(order_id=self.id, reason=reason)

        return CancelOrderResult(
            kind=CancelOrderResultKind.CANCELLED,
            order_id=self.id,
            order_status=self.status,
            events=(event,),
        )


class OrderRepository(ABC):
    @abstractmethod
    def get(self, order_id: OrderId) -> Order | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, order: Order) -> None:
        raise NotImplementedError


class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self._orders: dict[OrderId, Order] = {}

    def get(self, order_id: OrderId) -> Order | None:
        return self._orders.get(order_id)

    def save(self, order: Order) -> None:
        self._orders[order.id] = order

    def clear(self) -> None:
        self._orders.clear()
```

`orders/application.py`

```python
from orders.domain import (
    CancelOrderResult,
    CancelOrderResultKind,
    OrderId,
    OrderRepository,
)


class CancelOrderApplicationService:
    def __init__(self, repository: OrderRepository):
        self._repository = repository

    def cancel(self, order_id: OrderId, reason: str) -> CancelOrderResult:
        order = self._repository.get(order_id)

        if order is None:
            return CancelOrderResult(
                kind=CancelOrderResultKind.NOT_FOUND,
                order_id=order_id,
                order_status=None,
            )

        result = order.cancel(reason)

        if result.kind == CancelOrderResultKind.CANCELLED:
            self._repository.save(order)

        return result
```

이 단계의 핵심은 “정확한 최종 구조”가 아니라 실패 테스트를 통과시키는 최소 동작입니다. `bool`, `tuple`, `dict`, 문자열 에러코드 대신 `CancelOrderResult`와 `CancelOrderResultKind`를 명시적으로 반환하게 한 점이 중요합니다.

## 3. REFACTOR 방향

그린 상태가 된 뒤에만 아래를 분리합니다.

1. `InMemoryOrderRepository`는 테스트 더블이므로 `tests/isolated/fakes.py`나 `tests/isolated/conftest.py`로 이동합니다. 도메인 계층에는 `OrderRepository` 계약만 남깁니다.

2. `ValueError`는 도메인 예외로 교체합니다.

```python
class InvalidOrderIdError(ValueError):
    pass
```

3. `reason`은 문자열 대신 값 객체로 올립니다.

```python
@dataclass(frozen=True)
class CancelReason:
    value: str

    def __post_init__(self):
        if not self.value.strip():
            raise InvalidCancelReasonError("cancel reason must not be blank")
```

4. `PAID` 취소 후 환불이 필요하다면 주문 애그리거트가 환불 게이트웨이를 직접 호출하지 않습니다. `OrderCancelledEvent`를 발행하고 애플리케이션 서비스나 이벤트 핸들러가 환불 유스케이스로 넘깁니다.

5. Django 적용 시 트랜잭션 경계는 애플리케이션 서비스에 둡니다.

```python
from django.db import transaction

class CancelOrderApplicationService:
    @transaction.atomic
    def cancel(self, order_id: OrderId, reason: CancelReason) -> CancelOrderResult:
        ...
```

6. 상태 전이가 늘어나면 `Order.cancel()`의 조건문을 먼저 유지합니다. 같은 변경 축이 반복되어 복잡해질 때만 정책 객체나 상태 전이 테이블로 분리합니다.

## 4. 다음 RED로 추가할 edge case

```python
def test_cancel_order_blank_order_id_raises_invalid_order_id_error():
    # Arrange / Act / Assert
    with pytest.raises(ValueError):
        OrderId("")


def test_cancel_order_blank_reason_returns_validation_failure_result(repository):
    # 이 테스트를 추가하려면 CancelReason 값 객체와
    # VALIDATION_FAILED result kind를 먼저 설계 대상으로 삼는다.
    ...


def test_cancel_order_paid_status_records_refund_required_event(repository):
    # PAID 취소가 환불을 요구한다면 OrderCancelledEvent 외에
    # RefundRequestedEvent를 추가할지 별도 유스케이스 이벤트로 둘지 결정한다.
    ...
```

권장 실행 명령:

```bash
pytest tests/isolated/unit/test_cancel_order.py -q
pytest tests/isolated -q
pytest tests/isolated --randomly-seed=1 -q
```

---

> **관련 스킬 참조:**
> - Django ORM 저장소 구현과 transaction 적용 → **implementation-django** 스킬
> - Django Ninja 취소 API 엔드포인트 설계/테스트 → **implementation-django-ninja** 스킬
> - 주문 상태 전이와 애그리거트 경계 확장 → **architecture-ddd** 스킬