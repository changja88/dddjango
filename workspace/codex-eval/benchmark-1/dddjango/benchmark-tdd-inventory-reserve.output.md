## [주요 내용]

`/private/tmp/dddjango-codex-eval`은 현재 빈 디렉터리이고 샌드박스가 읽기 전용이라 파일 생성, 코드 수정, pytest 실행은 하지 못했습니다. 아래는 dddjango 지침에 맞춘 RED pytest, 예상 실패 이유, GREEN 최소 구현, REFACTOR 방향입니다. API는 다루지 않았고, 이 프로젝트 규칙상 API를 붙일 경우 DRF가 아니라 Django Ninja를 사용합니다.

**설계 요약:** `InventoryItem`을 재고 애그리거트 루트로 두고, 불변식은 `reserved_quantity <= stock_quantity`와 `reservation_id` 중복 금지입니다. 응용 서비스는 repository에서 애그리거트를 가져와 도메인 메서드 `reserve()`에 위임합니다. PEP 695 제네릭은 이 유스케이스에 필요한 타입 매개변수가 없어 사용하지 않았습니다.

**RED: `tests/isolated/unit/inventory/test_reservation_service.py`**

```python
import pytest

from apps.inventory.application.services import (
    InventoryReservationService,
    ReserveInventoryCommand,
)
from apps.inventory.domain.models import (
    DuplicateReservationError,
    InsufficientInventoryError,
    InventoryItem,
    ReservationRequest,
)
from apps.inventory.domain.repositories import InventoryRepository


class InMemoryInventoryRepository(InventoryRepository):
    """격리 테스트용 재고 repository fake."""

    def __init__(self) -> None:
        self._items: dict[str, InventoryItem] = {}

    def find_by_product_id(self, product_id: str) -> InventoryItem | None:
        return self._items.get(product_id)

    def save(self, item: InventoryItem) -> None:
        self._items[item.product_id] = item

    def clear(self) -> None:
        self._items.clear()


@pytest.fixture
def inventory_repository() -> InMemoryInventoryRepository:
    repository = InMemoryInventoryRepository()
    yield repository
    repository.clear()


def test_reserve_inventory_insufficient_inventory_raises_domain_error(
    inventory_repository: InMemoryInventoryRepository,
) -> None:
    """가용 재고보다 많은 수량 예약을 거절한다."""
    # Arrange
    inventory_repository.save(InventoryItem(product_id="product-1", stock_quantity=3))
    service = InventoryReservationService(inventory_repository)
    command = ReserveInventoryCommand(
        product_id="product-1",
        reservation_id="reservation-1",
        user_id="user-1",
        quantity=4,
    )

    # Act / Assert
    with pytest.raises(InsufficientInventoryError, match="available=3"):
        service.reserve(command)


def test_reserve_inventory_duplicate_reservation_raises_domain_error(
    inventory_repository: InMemoryInventoryRepository,
) -> None:
    """같은 reservation_id로 같은 재고를 다시 예약할 수 없다."""
    # Arrange
    item = InventoryItem(product_id="product-1", stock_quantity=10)
    item.reserve(
        ReservationRequest(
            product_id="product-1",
            reservation_id="reservation-1",
            user_id="user-1",
            quantity=2,
        )
    )
    inventory_repository.save(item)
    service = InventoryReservationService(inventory_repository)
    command = ReserveInventoryCommand(
        product_id="product-1",
        reservation_id="reservation-1",
        user_id="user-1",
        quantity=2,
    )

    # Act / Assert
    with pytest.raises(DuplicateReservationError, match="reservation-1"):
        service.reserve(command)


def test_reserve_inventory_available_inventory_creates_reservation(
    inventory_repository: InMemoryInventoryRepository,
) -> None:
    """가용 재고가 충분하면 예약하고 가용 수량을 차감한다."""
    # Arrange
    inventory_repository.save(InventoryItem(product_id="product-1", stock_quantity=10))
    service = InventoryReservationService(inventory_repository)
    command = ReserveInventoryCommand(
        product_id="product-1",
        reservation_id="reservation-1",
        user_id="user-1",
        quantity=3,
    )

    # Act
    result = service.reserve(command)

    # Assert
    saved_item = inventory_repository.find_by_product_id("product-1")
    assert result.product_id == "product-1"
    assert result.reservation_id == "reservation-1"
    assert result.quantity == 3
    assert saved_item is not None
    assert saved_item.available_quantity == 7
    assert len(saved_item.collect_events()) == 1
```

**예상 RED 실패 이유**

처음 실행하면 `apps.inventory...` 모듈이 없어서 `ModuleNotFoundError`가 나야 합니다. 빈 파일만 만들면 이후에는 `InsufficientInventoryError`, `DuplicateReservationError`, `reserve()` 동작, 결과 타입이 없어서 각 테스트가 실패해야 정상적인 RED입니다.

**GREEN 최소 구현**

`apps/inventory/domain/models.py`

```python
from dataclasses import dataclass, field
from datetime import UTC, datetime


class InventoryReservationError(Exception):
    """재고 예약 도메인 예외의 베이스 클래스."""


class InventoryNotFoundError(InventoryReservationError):
    """예약할 재고를 찾을 수 없을 때 발생한다."""


class InsufficientInventoryError(InventoryReservationError):
    """가용 재고가 예약 수량보다 적을 때 발생한다."""


class DuplicateReservationError(InventoryReservationError):
    """이미 처리한 reservation_id로 다시 예약할 때 발생한다."""


@dataclass(frozen=True, slots=True)
class ReservationRequest:
    """재고 예약 요청 값 객체."""

    product_id: str
    reservation_id: str
    user_id: str
    quantity: int

    def __post_init__(self) -> None:
        if not self.product_id:
            raise InventoryReservationError("product_id is required")
        if not self.reservation_id:
            raise InventoryReservationError("reservation_id is required")
        if not self.user_id:
            raise InventoryReservationError("user_id is required")
        if self.quantity <= 0:
            raise InventoryReservationError("quantity must be positive")


@dataclass(frozen=True, slots=True)
class InventoryReservedEvent:
    """재고가 예약되었음을 나타내는 도메인 이벤트."""

    product_id: str
    reservation_id: str
    user_id: str
    quantity: int
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True)
class InventoryItem:
    """재고 애그리거트 루트.

    Invariants:
    - reserved_quantity는 stock_quantity를 초과할 수 없다.
    - 같은 reservation_id는 같은 재고에서 한 번만 처리된다.
    """

    product_id: str
    stock_quantity: int
    reserved_quantity: int = 0
    _reservation_ids: set[str] = field(default_factory=set, repr=False)
    _domain_events: list[InventoryReservedEvent] = field(default_factory=list, repr=False)

    @property
    def available_quantity(self) -> int:
        return self.stock_quantity - self.reserved_quantity

    def reserve(self, request: ReservationRequest) -> None:
        if request.reservation_id in self._reservation_ids:
            raise DuplicateReservationError(
                f"duplicate reservation_id={request.reservation_id}"
            )
        if request.quantity > self.available_quantity:
            raise InsufficientInventoryError(
                f"insufficient inventory: available={self.available_quantity}, "
                f"requested={request.quantity}"
            )

        self.reserved_quantity += request.quantity
        self._reservation_ids.add(request.reservation_id)
        self._domain_events.append(
            InventoryReservedEvent(
                product_id=request.product_id,
                reservation_id=request.reservation_id,
                user_id=request.user_id,
                quantity=request.quantity,
            )
        )

    def collect_events(self) -> list[InventoryReservedEvent]:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events
```

`apps/inventory/domain/repositories.py`

```python
from abc import ABC, abstractmethod

from apps.inventory.domain.models import InventoryItem


class InventoryRepository(ABC):
    """재고 애그리거트 repository 인터페이스."""

    @abstractmethod
    def find_by_product_id(self, product_id: str) -> InventoryItem | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, item: InventoryItem) -> None:
        raise NotImplementedError
```

`apps/inventory/application/services.py`

```python
from dataclasses import dataclass

from apps.inventory.domain.models import (
    InventoryNotFoundError,
    ReservationRequest,
)
from apps.inventory.domain.repositories import InventoryRepository


@dataclass(frozen=True, slots=True)
class ReserveInventoryCommand:
    """재고 예약 유스케이스 입력 DTO."""

    product_id: str
    reservation_id: str
    user_id: str
    quantity: int


@dataclass(frozen=True, slots=True)
class ReserveInventoryResult:
    """재고 예약 유스케이스 결과."""

    product_id: str
    reservation_id: str
    quantity: int


class InventoryReservationService:
    """재고 예약 유스케이스를 조율하는 응용 서비스."""

    def __init__(self, inventory_repository: InventoryRepository) -> None:
        self._inventory_repository = inventory_repository

    def reserve(self, command: ReserveInventoryCommand) -> ReserveInventoryResult:
        item = self._inventory_repository.find_by_product_id(command.product_id)
        if item is None:
            raise InventoryNotFoundError(f"inventory not found: {command.product_id}")

        item.reserve(
            ReservationRequest(
                product_id=command.product_id,
                reservation_id=command.reservation_id,
                user_id=command.user_id,
                quantity=command.quantity,
            )
        )
        self._inventory_repository.save(item)

        return ReserveInventoryResult(
            product_id=command.product_id,
            reservation_id=command.reservation_id,
            quantity=command.quantity,
        )
```

**pytest 설정**

`pyproject.toml`에는 환경 축을 먼저 둡니다.

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
testpaths = ["tests/isolated", "tests/real"]
python_files = ["test_*.py", "*_test.py"]
python_functions = ["test_*"]
addopts = ["-ra", "-q", "--strict-markers", "--strict-config", "--tb=short"]
markers = [
  "isolated: 통제된 테스트 환경",
  "real: 실제 운영 동등 환경",
  "integration: 통합 범위 테스트",
]
```

Django 프로젝트라면 `config/settings/test.py`에서 `DATABASES`는 SQLite in-memory 또는 testcontainers, `EMAIL_BACKEND`는 locmem, `CACHES`는 LocMemCache, `CELERY_TASK_ALWAYS_EAGER = True`, `CELERY_BROKER_URL = "memory://"`, `PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]`로 분리하세요. isolated 테스트를 운영 settings로 실행하면 안 됩니다.

시간을 고정하는 테스트가 생기면 `tests/isolated/conftest.py`에서 `time-machine`을 쓰는 편이 좋습니다. freezegun은 순수 Python 구현인 반면 time-machine은 C 확장으로 구현되어 있어 동일 작업에서 100~200배 빠름. 시간 모킹이 많은 테스트 스위트에서 실질적인 실행 시간 차이가 발생합니다.

**실행 명령**

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/unit/inventory/test_reservation_service.py -q
pip install pytest-randomly time-machine
pytest --randomly-seed=last tests/isolated/unit/inventory/test_reservation_service.py -q
```

**REFACTOR 방향**

다음 단계에서는 Django ORM repository를 `transaction.atomic()` 안에서 `select_for_update()`로 구현해 동시 예약 레이스를 막고, `reservation_id`에는 DB `UniqueConstraint`를 둡니다. 도메인 이벤트는 같은 트랜잭션에서 Outbox에 저장한 뒤 커밋 후 발행하는 구조가 안전합니다. API가 필요하면 Django Ninja `Schema`/`Router`로 얇게 붙이고, 예약 로직은 지금의 `InventoryReservationService`를 그대로 호출하게 두면 됩니다.

## [관련 스킬 참조]

---
> **관련 스킬 참조:**
> - pytest fixture와 isolated/real 테스트 확장 → **implementation-test** 스킬
> - Django ORM repository, transaction, constraint 구현 → **implementation-django** 스킬
> - 재고 애그리거트와 도메인 이벤트 정교화 → **architecture-ddd** 스킬