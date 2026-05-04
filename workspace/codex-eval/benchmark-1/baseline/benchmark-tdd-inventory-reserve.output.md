작업 디렉터리 `/private/tmp/dddjango-codex-eval`가 비어 있고 현재 세션이 읽기 전용이라 파일 생성/수정 및 pytest 실행은 하지 못했습니다. 대신 실제 Django 프로젝트에 바로 옮길 수 있는 TDD 산출물 기준으로 정리합니다.

**RED: pytest**
`tests/isolated/unit/inventory/test_reserve_stock.py`

```python
import pytest

from apps.inventory.exceptions import DuplicateReservation, InsufficientStock
from apps.inventory.models import Product, StockReservation
from apps.inventory.services import reserve_stock


@pytest.fixture
def product(db):
    item = Product.objects.create(sku="SKU-001", stock_quantity=10)
    yield item
    StockReservation.objects.all().delete()
    Product.objects.all().delete()


@pytest.mark.django_db
def test_reserve_stock_when_stock_is_insufficient_raises_error(product):
    # Arrange
    quantity = 11

    # Act / Assert
    with pytest.raises(InsufficientStock):
        reserve_stock(
            product_id=product.id,
            reservation_key="order-1",
            quantity=quantity,
        )

    product.refresh_from_db()
    assert product.stock_quantity == 10
    assert StockReservation.objects.count() == 0


@pytest.mark.django_db
def test_reserve_stock_when_reservation_is_duplicated_raises_error(product):
    # Arrange
    reserve_stock(product_id=product.id, reservation_key="order-1", quantity=3)

    # Act / Assert
    with pytest.raises(DuplicateReservation):
        reserve_stock(
            product_id=product.id,
            reservation_key="order-1",
            quantity=3,
        )

    product.refresh_from_db()
    assert product.stock_quantity == 7
    assert StockReservation.objects.count() == 1


@pytest.mark.django_db
def test_reserve_stock_when_stock_is_available_creates_reservation(product):
    # Arrange
    quantity = 4

    # Act
    reservation = reserve_stock(
        product_id=product.id,
        reservation_key="order-1",
        quantity=quantity,
    )

    # Assert
    product.refresh_from_db()
    assert product.stock_quantity == 6
    assert reservation.product == product
    assert reservation.reservation_key == "order-1"
    assert reservation.quantity == 4
```

예상 실패 이유: `Product`, `StockReservation`, `reserve_stock`, 예외 타입이 아직 없어서 import 또는 동작 검증에서 실패해야 합니다.

**GREEN: 최소 구현**

```python
# apps/inventory/exceptions.py
class InsufficientStock(Exception):
    pass


class DuplicateReservation(Exception):
    pass
```

```python
# apps/inventory/models.py
from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
    sku = models.CharField(max_length=64, unique=True)
    stock_quantity = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=["sku"]),
        ]

    def __str__(self):
        return self.sku


class StockReservation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    reservation_key = models.CharField(max_length=128)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "reservation_key"],
                name="unique_stock_reservation_per_product",
            ),
        ]

    def __str__(self):
        return f"{self.product_id}:{self.reservation_key}"
```

```python
# apps/inventory/services.py
from django.db import transaction

from apps.inventory.exceptions import DuplicateReservation, InsufficientStock
from apps.inventory.models import Product, StockReservation


@transaction.atomic
def reserve_stock(*, product_id: int, reservation_key: str, quantity: int) -> StockReservation:
    product = Product.objects.select_for_update().get(id=product_id)

    if StockReservation.objects.filter(
        product=product,
        reservation_key=reservation_key,
    ).exists():
        raise DuplicateReservation

    if product.stock_quantity < quantity:
        raise InsufficientStock

    product.stock_quantity -= quantity
    product.save(update_fields=["stock_quantity"])

    return StockReservation.objects.create(
        product=product,
        reservation_key=reservation_key,
        quantity=quantity,
    )
```

**REFACTOR 방향**

재고 예약은 동시성 영향을 받으므로 `select_for_update()`와 DB `UniqueConstraint`를 같이 둔 현재 형태가 최소 안전선입니다. 다음 단계에서는 `quantity <= 0` 검증 테스트, 없는 상품 ID 처리, 예약 취소/복구 정책을 추가하면 됩니다.

실행 명령:

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/unit/inventory/test_reserve_stock.py -q
```

실제 실행은 하지 못했습니다. 현재 workspace가 비어 있고 읽기 전용입니다.

---
> **관련 스킬 참조:**
> - Django pytest와 격리 테스트 구조 → **implementation-test** 스킬