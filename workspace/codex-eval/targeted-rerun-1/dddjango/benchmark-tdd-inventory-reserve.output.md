현재 workspace가 비어 있고 세션이 read-only라 파일 생성, 마이그레이션 생성, pytest 실행은 하지 못했습니다. 아래는 TDD 순서대로 바로 붙일 수 있는 최소 산출물입니다. 가정: `inventory` 앱, `pytest-django`, `DJANGO_SETTINGS_MODULE=config.settings.test`.

**RED 테스트**

`tests/isolated/integration/test_inventory_reservation.py`

```python
import pytest

from inventory.models import Product, StockReservation
from inventory.services import (
    DuplicateReservationError,
    InsufficientStockError,
    reserve_stock,
)


@pytest.mark.django_db
def test_reserve_stock_when_stock_is_available_creates_reservation():
    product = Product.objects.create(sku="SKU-1", available_quantity=5)

    result = reserve_stock(product_id=product.id, quantity=3, reservation_key="order-1")

    product.refresh_from_db()
    assert result.reservation_id is not None
    assert product.available_quantity == 2
    assert StockReservation.objects.get(id=result.reservation_id).quantity == 3


@pytest.mark.django_db
def test_reserve_stock_when_stock_is_insufficient_raises_error():
    product = Product.objects.create(sku="SKU-1", available_quantity=2)

    with pytest.raises(InsufficientStockError):
        reserve_stock(product_id=product.id, quantity=3, reservation_key="order-1")

    product.refresh_from_db()
    assert product.available_quantity == 2
    assert StockReservation.objects.count() == 0


@pytest.mark.django_db
def test_reserve_stock_when_reservation_key_is_duplicated_raises_error():
    product = Product.objects.create(sku="SKU-1", available_quantity=5)
    reserve_stock(product_id=product.id, quantity=2, reservation_key="order-1")

    with pytest.raises(DuplicateReservationError):
        reserve_stock(product_id=product.id, quantity=2, reservation_key="order-1")

    product.refresh_from_db()
    assert product.available_quantity == 3
    assert StockReservation.objects.count() == 1
```

예상 실패: 아직 `Product`, `StockReservation`, `reserve_stock`, 도메인 예외가 없어서 import 단계부터 실패해야 합니다.

**GREEN 최소 구현**

`inventory/models.py`

```python
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class Product(models.Model):
    sku = models.CharField(max_length=64, unique=True)
    available_quantity = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(available_quantity__gte=0),
                name="product_available_quantity_gte_0",
            ),
        ]

    def __str__(self) -> str:
        return self.sku

    def reserve(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.available_quantity < quantity:
            raise InsufficientStockError("stock is insufficient")
        self.available_quantity -= quantity


class StockReservation(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmed"

    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    reservation_key = models.CharField(max_length=128)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.CONFIRMED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "reservation_key"],
                name="unique_stock_reservation_per_product_key",
            ),
        ]


class InsufficientStockError(Exception):
    pass
```

`inventory/services.py`

```python
from dataclasses import dataclass

from django.db import IntegrityError, transaction

from inventory.models import Product, StockReservation


class InsufficientStockError(Exception):
    pass


class DuplicateReservationError(Exception):
    pass


@dataclass(frozen=True)
class ReservationResult:
    reservation_id: int


def reserve_stock(
    *,
    product_id: int,
    quantity: int,
    reservation_key: str,
) -> ReservationResult:
    with transaction.atomic():
        product = Product.objects.select_for_update().get(id=product_id)

        if StockReservation.objects.filter(
            product=product,
            reservation_key=reservation_key,
        ).exists():
            raise DuplicateReservationError("reservation already exists")

        if product.available_quantity < quantity:
            raise InsufficientStockError("stock is insufficient")

        product.available_quantity -= quantity
        product.save(update_fields=["available_quantity"])

        try:
            reservation = StockReservation.objects.create(
                product=product,
                reservation_key=reservation_key,
                quantity=quantity,
            )
        except IntegrityError as exc:
            raise DuplicateReservationError("reservation already exists") from exc

    return ReservationResult(reservation_id=reservation.id)
```

주의: 위 `Product.reserve()`에서 모델 예외 import 순환을 피하려면 실제 적용 시 예외는 `inventory/exceptions.py`로 분리하세요. 서비스가 트랜잭션과 `select_for_update()`를 담당하고, 모델은 재고 불변식만 다루는 경계가 적절합니다.

**REFACTOR**

- `InsufficientStockError`, `DuplicateReservationError`를 `inventory/exceptions.py`로 이동.
- `Product.reserve(quantity)`를 서비스에서 호출하게 정리해 재고 불변식을 모델에 모음.
- PostgreSQL 기반 테스트에서 `transactional_db`와 스레드/배리어로 동시 예약 2건 중 1건만 성공하는 회귀 테스트 추가.
- 마이그레이션에는 `available_quantity >= 0`, `(product, reservation_key)` unique 제약을 반드시 포함.

**검증 명령**

```bash
python manage.py makemigrations inventory
python manage.py migrate
pytest tests/isolated/integration/test_inventory_reservation.py -q
```

---
> **관련 스킬 참조:**
> - Django 모델/서비스/트랜잭션 → **implementation-django** 스킬
> - pytest와 TDD 사이클 → **implementation-tdd**, **implementation-test** 스킬