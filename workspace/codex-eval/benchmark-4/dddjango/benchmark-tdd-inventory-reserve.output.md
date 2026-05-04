빈 워크스페이스이고 현재 세션은 읽기 전용이라 파일 생성, 마이그레이션 생성, pytest 실행은 하지 못했습니다. 아래는 실제 프로젝트에 넣을 TDD 산출물입니다. 순서는 반드시 `RED 테스트 작성 -> 실패 확인 -> GREEN 구현 -> 통과 확인 -> REFACTOR`입니다.

**RED 테스트**

`tests/isolated/integration/test_inventory_reservations.py`

```python
import pytest

from inventory.exceptions import DuplicateReservationError, InsufficientStockError
from inventory.models import InventoryItem, InventoryReservation
from inventory.services import reserve_inventory


pytestmark = pytest.mark.django_db(transaction=True)


def test_reserve_inventory_when_stock_is_enough_creates_reservation_and_decreases_stock():
    # Arrange
    item = InventoryItem.objects.create(sku="SKU-001", available_quantity=10)

    # Act
    reservation = reserve_inventory(item_id=item.id, order_id="ORDER-001", quantity=3)

    # Assert
    item.refresh_from_db()
    assert reservation.item_id == item.id
    assert reservation.order_id == "ORDER-001"
    assert reservation.quantity == 3
    assert item.available_quantity == 7


def test_reserve_inventory_when_stock_is_insufficient_raises_error_and_keeps_stock():
    # Arrange
    item = InventoryItem.objects.create(sku="SKU-002", available_quantity=2)

    # Act / Assert
    with pytest.raises(InsufficientStockError):
        reserve_inventory(item_id=item.id, order_id="ORDER-002", quantity=3)

    item.refresh_from_db()
    assert item.available_quantity == 2
    assert InventoryReservation.objects.count() == 0


def test_reserve_inventory_when_order_already_reserved_raises_duplicate_error():
    # Arrange
    item = InventoryItem.objects.create(sku="SKU-003", available_quantity=10)
    reserve_inventory(item_id=item.id, order_id="ORDER-003", quantity=3)

    # Act / Assert
    with pytest.raises(DuplicateReservationError):
        reserve_inventory(item_id=item.id, order_id="ORDER-003", quantity=2)

    item.refresh_from_db()
    assert item.available_quantity == 7
    assert InventoryReservation.objects.count() == 1
```

**예상 실패**

처음 실행하면 `inventory.models`, `inventory.services`, 도메인 예외가 없어서 실패해야 정상입니다. 이미 존재한다면 정상 예약/재고 부족/중복 예약 동작이 아직 구현되지 않았기 때문에 해당 assertion 또는 예외 기대에서 실패해야 합니다.

**GREEN 최소 구현**

`inventory/models.py`

```python
from django.core.validators import MinValueValidator
from django.db import models


class InventoryItem(models.Model):
    sku = models.CharField(max_length=64, unique=True)
    available_quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)])

    class Meta:
        indexes = [models.Index(fields=["sku"])]

    def __str__(self):
        return self.sku


class InventoryReservation(models.Model):
    item = models.ForeignKey(InventoryItem, on_delete=models.PROTECT)
    order_id = models.CharField(max_length=64)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["item", "order_id"],
                name="unique_inventory_reservation_per_item_order",
            )
        ]
        indexes = [models.Index(fields=["order_id"])]
```

`inventory/exceptions.py`

```python
class InsufficientStockError(Exception):
    pass


class DuplicateReservationError(Exception):
    pass
```

`inventory/services.py`

```python
from django.db import IntegrityError, transaction

from inventory.exceptions import DuplicateReservationError, InsufficientStockError
from inventory.models import InventoryItem, InventoryReservation


@transaction.atomic
def reserve_inventory(*, item_id: int, order_id: str, quantity: int) -> InventoryReservation:
    item = InventoryItem.objects.select_for_update().get(id=item_id)

    if InventoryReservation.objects.filter(item=item, order_id=order_id).exists():
        raise DuplicateReservationError

    if item.available_quantity < quantity:
        raise InsufficientStockError

    item.available_quantity -= quantity
    item.save(update_fields=["available_quantity"])

    try:
        return InventoryReservation.objects.create(
            item=item,
            order_id=order_id,
            quantity=quantity,
        )
    except IntegrityError as exc:
        raise DuplicateReservationError from exc
```

**REFACTOR notes**

예약 유스케이스는 Django 모델에 직접 흩뿌리지 않고 `services.py`에 둡니다. 재고 수량은 `InventoryItem` 애그리거트의 불변식이고, 예약 중복은 DB `UniqueConstraint`와 서비스의 사전 검사로 이중 방어합니다. `select_for_update()`는 같은 재고 row를 잠가 동시 요청이 재고를 동시에 차감하는 위험을 줄입니다.

**검증 명령**

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/integration/test_inventory_reservations.py -q
python manage.py makemigrations inventory
python manage.py migrate
DJANGO_SETTINGS_MODULE=config.settings.test pytest -q
```

---
> **관련 스킬 참조:**
> - Django pytest/TDD 확장 → **implementation-test**, **implementation-tdd** 스킬