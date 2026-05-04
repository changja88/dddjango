`/private/tmp/dddjango-codex-eval` 워크스페이스가 비어 있고 읽기 전용이라 파일 생성/수정과 `pytest` 실행은 못 했습니다. 실행했다고 주장하지 않고, 실제 Django 프로젝트에 바로 옮길 수 있는 TDD 산출물로 정리합니다.

**RED: pytest**

`tests/isolated/integration/inventory/test_inventory_reserve.py`

```python
import pytest

from apps.inventory.models import InventoryReservation, Product
from apps.inventory.services import (
    DuplicateReservation,
    InsufficientStock,
    inventory_reserve,
)


@pytest.fixture
def product(db):
    return Product.objects.create(name="Keyboard", sku="KEY-001", available_stock=10)


@pytest.mark.django_db
def test_inventory_reserve_insufficient_stock_raises(product):
    # Arrange
    quantity = 11

    # Act / Assert
    with pytest.raises(InsufficientStock):
        inventory_reserve(product_id=product.id, order_id="ORDER-001", quantity=quantity)

    product.refresh_from_db()
    assert product.available_stock == 10
    assert InventoryReservation.objects.count() == 0


@pytest.mark.django_db
def test_inventory_reserve_duplicate_order_raises(product):
    # Arrange
    inventory_reserve(product_id=product.id, order_id="ORDER-001", quantity=2)

    # Act / Assert
    with pytest.raises(DuplicateReservation):
        inventory_reserve(product_id=product.id, order_id="ORDER-001", quantity=2)

    product.refresh_from_db()
    assert product.available_stock == 8
    assert InventoryReservation.objects.count() == 1


@pytest.mark.django_db
def test_inventory_reserve_valid_request_creates_reservation(product):
    # Arrange
    quantity = 3

    # Act
    reservation = inventory_reserve(
        product_id=product.id,
        order_id="ORDER-001",
        quantity=quantity,
    )

    # Assert
    product.refresh_from_db()
    assert product.available_stock == 7
    assert reservation.product == product
    assert reservation.order_id == "ORDER-001"
    assert reservation.quantity == 3
```

예상 RED 실패 이유: `apps.inventory.models`, `inventory_reserve`, `InsufficientStock`, `DuplicateReservation`가 아직 없어서 import 단계 또는 호출 단계에서 실패합니다.

**GREEN: 최소 구현**

`apps/inventory/models.py`

```python
from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=120)
    sku = models.CharField(max_length=64, unique=True)
    available_stock = models.PositiveIntegerField(validators=[MinValueValidator(0)])

    class Meta:
        ordering = ["sku"]
        indexes = [models.Index(fields=["sku"])]

    def __str__(self):
        return f"{self.sku} - {self.name}"


class InventoryReservation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=64)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "order_id"],
                name="unique_inventory_reservation_per_order",
            )
        ]

    def __str__(self):
        return f"{self.order_id} / {self.product_id} / {self.quantity}"
```

`apps/inventory/services.py`

```python
from django.db import transaction

from apps.inventory.models import InventoryReservation, Product


class InsufficientStock(Exception):
    pass


class DuplicateReservation(Exception):
    pass


def inventory_reserve(*, product_id: int, order_id: str, quantity: int):
    with transaction.atomic():
        product = Product.objects.select_for_update().get(id=product_id)

        if InventoryReservation.objects.filter(
            product=product,
            order_id=order_id,
        ).exists():
            raise DuplicateReservation

        if product.available_stock < quantity:
            raise InsufficientStock

        product.available_stock -= quantity
        product.save(update_fields=["available_stock"])

        return InventoryReservation.objects.create(
            product=product,
            order_id=order_id,
            quantity=quantity,
        )
```

**REFACTOR 방향**

- 실제 프로젝트에서는 `apps/inventory/selectors.py`에 읽기 전용 조회를 분리합니다.
- 동시 예약이 중요한 경로라서 `transaction.atomic()` + `select_for_update()`는 유지하는 게 맞습니다.
- `quantity <= 0` 검증 케이스를 다음 TDD 사이클로 추가하면 좋습니다.

실행 명령:

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/integration/inventory/test_inventory_reserve.py -q
```

---
> **관련 스킬 참조:**
> - Django 서비스/모델 구현 → **implementation-django** 스킬
> - pytest fixture와 격리 테스트 → **implementation-test** 스킬
> - Red-Green-Refactor 진행 → **implementation-tdd** 스킬