사용 스킬: `implementation-tdd`, `implementation-test`, `implementation-django`, `architecture-ddd`.

현재 `/private/tmp/dddjango-codex-eval`은 빈 workspace이고 샌드박스가 read-only라 테스트 파일 생성, 구현 파일 수정, `pytest` 실행은 하지 못했습니다. 아래는 실제 Django 프로젝트에 옮겨서 진행할 수 있는 TDD 흐름입니다.

**RED: 실패 테스트**

파일 위치 예시: `tests/isolated/unit/orders/test_cancel_order.py`

```python
import pytest

from apps.orders.application import CancelOrderCommand, OrderApplicationService
from apps.orders.domain import (
    CannotCancelOrderError,
    Order,
    OrderCanceledEvent,
    OrderId,
    OrderRepository,
    OrderStatus,
)


class InMemoryOrderRepository(OrderRepository):
    def __init__(self, orders=None):
        self.orders = {order.id: order for order in orders or []}

    def find_by_id(self, order_id: OrderId) -> Order | None:
        return self.orders.get(order_id)

    def save(self, order: Order) -> None:
        self.orders[order.id] = order


def test_cancel_order_paid_order_changes_status_to_canceled():
    # Arrange
    order = Order(id=OrderId("order-1"), status=OrderStatus.PAID)
    repository = InMemoryOrderRepository([order])
    service = OrderApplicationService(order_repository=repository)

    # Act
    service.cancel_order(CancelOrderCommand(order_id="order-1"))

    # Assert
    saved_order = repository.find_by_id(OrderId("order-1"))
    assert saved_order.status == OrderStatus.CANCELED
    assert saved_order.collect_events() == [
        OrderCanceledEvent(order_id=OrderId("order-1"))
    ]


def test_cancel_order_shipped_order_raises_cannot_cancel_order_error():
    # Arrange
    order = Order(id=OrderId("order-2"), status=OrderStatus.SHIPPED)
    repository = InMemoryOrderRepository([order])
    service = OrderApplicationService(order_repository=repository)

    # Act / Assert
    with pytest.raises(CannotCancelOrderError, match="배송 중인 주문은 취소할 수 없습니다"):
        service.cancel_order(CancelOrderCommand(order_id="order-2"))
```

예상 실패 이유:

- `apps.orders.application` 모듈이 아직 없음
- `CancelOrderCommand`, `OrderApplicationService`가 아직 없음
- `Order`, `OrderId`, `OrderStatus`, `OrderRepository`, `OrderCanceledEvent`, `CannotCancelOrderError`가 아직 없음
- 즉, 테스트는 “주문 취소”라는 원하는 API를 먼저 고정하고 실패해야 합니다.

**GREEN: 최소 구현**

파일 위치 예시: `apps/orders/domain.py`

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum


class OrderStatus(StrEnum):
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELED = "canceled"


class OrderNotFoundError(Exception):
    pass


class CannotCancelOrderError(Exception):
    pass


@dataclass(frozen=True)
class OrderId:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("order id is required")


@dataclass(frozen=True)
class OrderCanceledEvent:
    order_id: OrderId


@dataclass
class Order:
    """Aggregate Root.

    Invariant:
    - 배송 중이거나 이미 취소된 주문은 취소할 수 없다.
    """

    id: OrderId
    status: OrderStatus
    _events: list[object] = field(default_factory=list)

    def cancel(self) -> None:
        if self.status == OrderStatus.SHIPPED:
            raise CannotCancelOrderError("배송 중인 주문은 취소할 수 없습니다")
        if self.status == OrderStatus.CANCELED:
            raise CannotCancelOrderError("이미 취소된 주문입니다")

        self.status = OrderStatus.CANCELED
        self._events.append(OrderCanceledEvent(order_id=self.id))

    def collect_events(self) -> list[object]:
        events = self._events[:]
        self._events.clear()
        return events


class OrderRepository(ABC):
    @abstractmethod
    def find_by_id(self, order_id: OrderId) -> Order | None:
        ...

    @abstractmethod
    def save(self, order: Order) -> None:
        ...
```

파일 위치 예시: `apps/orders/application.py`

```python
from dataclasses import dataclass

from apps.orders.domain import OrderId, OrderNotFoundError, OrderRepository


@dataclass(frozen=True)
class CancelOrderCommand:
    order_id: str


class OrderApplicationService:
    def __init__(self, order_repository: OrderRepository):
        self._order_repository = order_repository

    def cancel_order(self, command: CancelOrderCommand) -> None:
        order_id = OrderId(command.order_id)
        order = self._order_repository.find_by_id(order_id)

        if order is None:
            raise OrderNotFoundError("주문을 찾을 수 없습니다")

        order.cancel()
        self._order_repository.save(order)
```

이 단계에서는 “테스트를 통과시키는 데 필요한 만큼”만 구현합니다. Django ORM 모델, API, 결제 취소, 재고 복구, 알림 발송은 아직 넣지 않습니다.

**REFACTOR 방향**

그린 상태를 확인한 뒤에만 아래 순서로 정리합니다.

1. 도메인 계층 정리  
   `Order.cancel()`은 주문 애그리거트의 핵심 불변식입니다. `if order.status ...` 같은 외부 분기는 만들지 않고, 취소 가능 여부는 애그리거트 내부에서 보호합니다.

2. Django 영속성 어댑터 추가  
   `OrderRepository` ABC는 도메인 계층에 두고, Django ORM 구현체는 인프라 계층에 둡니다. 도메인 모델이 Django ORM을 import하지 않게 유지합니다.

3. 트랜잭션과 부수효과 분리  
   실제 결제 취소, 쿠폰 복구, 이메일 발송은 `transaction.on_commit()` 이후 처리합니다. 주문 상태 변경 트랜잭션이 커밋되기 전에 외부 API를 먼저 호출하지 않습니다.

4. 테스트 구조 확장  
   isolated 테스트는 `tests/isolated/unit/orders/`에 두고, 실제 DB나 외부 서비스 검증은 `tests/real/`로 분리합니다.

`pyproject.toml` 예시:

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
testpaths = ["tests/isolated", "tests/real"]
python_files = ["test_*.py", "*_test.py"]
```

Django isolated 테스트 설정은 운영 settings가 아니라 `config/settings/test.py`를 사용합니다. 이 설정에서는 SQLite in-memory 또는 testcontainers DB, locmem email backend, LocMemCache, `CELERY_TASK_ALWAYS_EAGER = true`, `CELERY_BROKER_URL = "memory://"`, 빠른 password hasher를 사용해 외부 의존성을 차단합니다.

실행 명령:

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/unit/orders/test_cancel_order.py -q
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated -q
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated --randomly-seed=last -q
```

시간 의존 규칙이 추가되면 `freezegun`보다 `time-machine`을 우선 사용하세요. `freezegun`은 순수 Python 구현인 반면 `time-machine`은 C 확장으로 구현되어 있어 동일 작업에서 100~200배 빠르고, 시간 모킹이 많은 테스트 스위트에서 실행 시간 차이가 커집니다.

---
> **관련 스킬 참조:**
> - pytest fixture/fake repository 개선 → **implementation-test** 스킬
> - Django ORM repository 구현 → **implementation-django** 스킬
> - 애그리거트/도메인 이벤트 확장 → **architecture-ddd** 스킬