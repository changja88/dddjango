사용 스킬: `implementation-tdd` → `architecture-ddd` → `architecture-implementation-patterns` → `implementation-test` 순서로 적용했습니다. 현재 workspace가 read-only라 파일 생성과 pytest 실행은 못 했습니다. 아래는 그대로 `tests/isolated/unit/...`와 도메인 모듈에 옮겨 RED부터 시작할 수 있는 설계입니다.

**주요 내용**

| 도메인 용어 | 정의 | 코드 표현 | 금지 동의어 |
|---|---|---|---|
| 예약 요청 | 특정 상품 수량을 예약하려는 명령 | `ReserveStockCommand` | `payload`, `input_data` |
| 요청 식별자 | 클라이언트 재시도 멱등 키 | `RequestId` | `uuid`, `token` |
| 가용 재고 | 예약 가능한 수량 | `StockItem.available` | `free_stock` |
| 예약 결과 | 같은 요청 식별자로 반복 반환될 결정 | `ReservationResult` | `response dict` |

**RED**

```python
# tests/isolated/unit/inventory/test_reserve_stock.py
import pytest

from inventory.application.reserve_stock import ReserveStockService
from inventory.domain.model.stock import ProductId, Quantity, RequestId
from inventory.tests.fakes import InMemoryStockRepository


def test_reserve_stock_same_request_id_returns_same_result():
    repo = InMemoryStockRepository.with_stock("SKU-1", available=5)
    service = ReserveStockService(repo)

    first = service.reserve(
        product_id=ProductId("SKU-1"),
        quantity=Quantity(3),
        request_id=RequestId("req-1"),
    )
    retry = service.reserve(
        product_id=ProductId("SKU-1"),
        quantity=Quantity(3),
        request_id=RequestId("req-1"),
    )

    assert retry == first
    assert repo.reservation_count() == 1
    assert repo.get_stock(ProductId("SKU-1")).available == Quantity(2)


def test_reserve_stock_insufficient_stock_does_not_create_reservation():
    repo = InMemoryStockRepository.with_stock("SKU-1", available=2)
    service = ReserveStockService(repo)

    result = service.reserve(
        product_id=ProductId("SKU-1"),
        quantity=Quantity(3),
        request_id=RequestId("req-2"),
    )

    assert result.status == "insufficient_stock"
    assert result.reservation_id is None
    assert repo.reservation_count() == 0
    assert repo.get_stock(ProductId("SKU-1")).available == Quantity(2)


def test_reserve_stock_same_failed_request_id_returns_same_failure_after_restock():
    repo = InMemoryStockRepository.with_stock("SKU-1", available=2)
    service = ReserveStockService(repo)

    first = service.reserve(ProductId("SKU-1"), Quantity(3), RequestId("req-3"))
    repo.add_stock(ProductId("SKU-1"), Quantity(10))
    retry = service.reserve(ProductId("SKU-1"), Quantity(3), RequestId("req-3"))

    assert retry == first
    assert retry.status == "insufficient_stock"
    assert repo.reservation_count() == 0


def test_reserve_stock_concurrent_update_conflict_is_not_silently_overwritten():
    repo = InMemoryStockRepository.with_stock("SKU-1", available=5)
    stale = repo.get_stock(ProductId("SKU-1"))
    fresh = repo.get_stock(ProductId("SKU-1"))

    stale.reserve(Quantity(4), RequestId("req-a"))
    repo.save(stale)

    fresh.reserve(Quantity(3), RequestId("req-b"))

    with pytest.raises(repo.ConcurrencyError):
        repo.save(fresh)
```

예상 실패: `ReserveStockService`, 값 객체, repository port, fake repository, 동시성 예외가 아직 없으므로 import/attribute error 또는 미구현 실패가 나야 정상입니다.

**GREEN**

```python
# inventory/domain/model/stock.py
from dataclasses import dataclass
from uuid import uuid4


class InsufficientStockError(Exception):
    pass


@dataclass(frozen=True)
class ProductId:
    value: str


@dataclass(frozen=True)
class RequestId:
    value: str


@dataclass(frozen=True)
class Quantity:
    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("quantity must be positive")


@dataclass(frozen=True)
class ReservationResult:
    request_id: RequestId
    status: str
    reservation_id: str | None


@dataclass
class StockItem:
    """Aggregate Root.
    Invariants:
    - available never goes below zero.
    - reservation is created only after available stock is reduced.
    - version guards lost updates at repository boundary.
    """

    product_id: ProductId
    available: Quantity
    version: int = 0

    def reserve(self, quantity: Quantity, request_id: RequestId) -> ReservationResult:
        if self.available.value < quantity.value:
            raise InsufficientStockError

        self.available = Quantity(self.available.value - quantity.value)
        return ReservationResult(
            request_id=request_id,
            status="reserved",
            reservation_id=str(uuid4()),
        )
```

```python
# inventory/application/reserve_stock.py
from inventory.domain.model.stock import (
    InsufficientStockError,
    ProductId,
    Quantity,
    RequestId,
    ReservationResult,
)


class ReserveStockService:
    def __init__(self, stocks):
        self._stocks = stocks

    def reserve(
        self,
        product_id: ProductId,
        quantity: Quantity,
        request_id: RequestId,
    ) -> ReservationResult:
        previous = self._stocks.find_result_by_request_id(request_id)
        if previous:
            return previous

        stock = self._stocks.get_stock(product_id)

        try:
            result = stock.reserve(quantity, request_id)
            self._stocks.save(stock)
            self._stocks.save_result(result)
            self._stocks.save_reservation(result)
            return result
        except InsufficientStockError:
            result = ReservationResult(request_id, "insufficient_stock", None)
            self._stocks.save_result(result)
            return result
```

Repository port는 도메인/애플리케이션이 소유합니다.

```python
# inventory/domain/ports.py
from typing import Protocol

class StockRepository(Protocol):
    def find_result_by_request_id(self, request_id): ...
    def get_stock(self, product_id): ...
    def save(self, stock): ...
    def save_result(self, result): ...
    def save_reservation(self, result): ...
```

Django adapter를 붙일 때 transaction 경계는 도메인이 아니라 adapter/UoW에 둡니다. `transaction.atomic()` 안에서 `request_id` unique idempotency row, `product_id` stock row, `version` 조건부 update를 함께 처리해야 합니다. 부족 결과도 idempotency result로 저장하되 reservation row는 만들지 않습니다.

**REFACTOR**

다음 그린 이후 정리합니다: fake repository를 fixture로 이동, `status` 문자열을 enum으로 교체, `ReservationId` VO 추가, `save_result`와 `save_reservation` 순서를 UoW로 묶기, Django adapter에서 `UniqueConstraint(request_id)`와 낙관적 잠금 `WHERE version = old_version` 적용.

실행 명령:

```bash
pytest tests/isolated/unit/inventory/test_reserve_stock.py -q
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/unit/inventory -q
```

---
> **관련 스킬 참조:**
> - Django ORM adapter / transaction 붙이기 → **implementation-django** 스킬
> - DB unique constraint / optimistic locking 설계 → **architecture-db** 스킬