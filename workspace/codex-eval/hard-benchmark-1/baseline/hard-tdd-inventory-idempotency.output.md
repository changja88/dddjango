작업 디렉터리가 비어 있고 현재 세션은 읽기 전용이라 파일을 만들지는 못했습니다. 아래처럼 시작하면 됩니다. 핵심은 도메인 서비스가 Django를 모르고, 저장/조회는 `InventoryReservationRepository` port에만 의존하게 두는 구조입니다.

**1. 테스트 먼저**

`tests/test_reserve_inventory.py`

```python
import pytest

from inventory.domain import (
    InsufficientStock,
    InventoryReservationRepository,
    Reservation,
    ReservationService,
)


class FakeReservationRepository(InventoryReservationRepository):
    def __init__(self, stocks=None, reservations=None):
        self.stocks = stocks or {}
        self.reservations = reservations or {}
        self.saved = []

    def find_by_request_id(self, request_id: str):
        return self.reservations.get(request_id)

    def available_stock(self, sku: str) -> int:
        return self.stocks.get(sku, 0)

    def save(self, reservation: Reservation) -> Reservation:
        self.saved.append(reservation)
        self.reservations[reservation.request_id] = reservation
        self.stocks[reservation.sku] -= reservation.quantity
        return reservation


def test_reserve_stock_creates_reservation():
    repo = FakeReservationRepository(stocks={"SKU-1": 10})
    service = ReservationService(repo)

    reservation = service.reserve(
        request_id="req-1",
        sku="SKU-1",
        quantity=3,
    )

    assert reservation.request_id == "req-1"
    assert reservation.sku == "SKU-1"
    assert reservation.quantity == 3
    assert repo.available_stock("SKU-1") == 7
    assert repo.saved == [reservation]


def test_retry_with_same_request_id_returns_same_result_without_creating_again():
    existing = Reservation(
        request_id="req-1",
        sku="SKU-1",
        quantity=3,
    )
    repo = FakeReservationRepository(
        stocks={"SKU-1": 10},
        reservations={"req-1": existing},
    )
    service = ReservationService(repo)

    reservation = service.reserve(
        request_id="req-1",
        sku="SKU-1",
        quantity=3,
    )

    assert reservation == existing
    assert repo.saved == []


def test_insufficient_stock_does_not_create_reservation():
    repo = FakeReservationRepository(stocks={"SKU-1": 2})
    service = ReservationService(repo)

    with pytest.raises(InsufficientStock):
        service.reserve(
            request_id="req-1",
            sku="SKU-1",
            quantity=3,
        )

    assert repo.reservations == {}
    assert repo.saved == []
    assert repo.available_stock("SKU-1") == 2
```

**2. 최소 도메인 구현**

`inventory/domain.py`

```python
from dataclasses import dataclass
from typing import Protocol


class InsufficientStock(Exception):
    pass


@dataclass(frozen=True)
class Reservation:
    request_id: str
    sku: str
    quantity: int


class InventoryReservationRepository(Protocol):
    def find_by_request_id(self, request_id: str) -> Reservation | None:
        ...

    def available_stock(self, sku: str) -> int:
        ...

    def save(self, reservation: Reservation) -> Reservation:
        ...


class ReservationService:
    def __init__(self, repository: InventoryReservationRepository):
        self.repository = repository

    def reserve(self, request_id: str, sku: str, quantity: int) -> Reservation:
        existing = self.repository.find_by_request_id(request_id)
        if existing is not None:
            return existing

        if self.repository.available_stock(sku) < quantity:
            raise InsufficientStock

        reservation = Reservation(
            request_id=request_id,
            sku=sku,
            quantity=quantity,
        )
        return self.repository.save(reservation)
```

나중에 Django DB를 붙일 때는 이 port를 구현하는 adapter만 만들면 됩니다. 특히 실제 DB 구현에서는 `find_by_request_id`와 재고 차감/예약 저장이 transaction 안에서 처리되어야 하고, 동시성 때문에 단순 조회 후 저장이 아니라 조건부 update나 row lock을 써야 합니다. 도메인 테스트는 그대로 유지하고, Django adapter 테스트만 별도로 추가하면 됩니다.