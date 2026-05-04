**[주요 내용]**

현재 `/private/tmp/dddjango-codex-eval`은 파일이 없는 빈 디렉터리이고, 세션이 읽기 전용이라 파일 생성/수정과 pytest 실행을 할 수 없었습니다. 따라서 실행했다고 말하지 않습니다. 아래는 실제 프로젝트에 그대로 옮겨 TDD 순서로 적용할 RED 테스트, 예상 실패, GREEN 구현입니다. 핵심은 **실패 테스트가 구현보다 먼저 나온다**는 점입니다.

**RED: `tests/isolated/inventory/test_inventory_reservation.py`**

```python
import pytest

from apps.inventory.models import Product, Reservation
from apps.inventory.services import (
    DuplicateReservationError,
    InsufficientStockError,
    inventory_reserve,
)


@pytest.mark.django_db
def test_inventory_reserve_when_stock_is_enough_creates_reservation():
    product = Product.objects.create(name="Keyboard", stock_quantity=10)

    reservation = inventory_reserve(
        product_id=product.id,
        quantity=3,
        reservation_key="order-1:keyboard",
    )

    product.refresh_from_db()
    assert reservation.product_id == product.id
    assert reservation.quantity == 3
    assert product.reserved_quantity == 3
    assert product.available_quantity == 7


@pytest.mark.django_db
def test_inventory_reserve_when_stock_is_insufficient_raises_error():
    product = Product.objects.create(name="Mouse", stock_quantity=2)

    with pytest.raises(InsufficientStockError):
        inventory_reserve(
            product_id=product.id,
            quantity=3,
            reservation_key="order-2:mouse",
        )

    assert Reservation.objects.count() == 0


@pytest.mark.django_db
def test_inventory_reserve_when_reservation_key_is_duplicated_does_not_reserve_twice():
    product = Product.objects.create(name="Monitor", stock_quantity=5)

    inventory_reserve(
        product_id=product.id,
        quantity=2,
        reservation_key="order-3:monitor",
    )

    with pytest.raises(DuplicateReservationError):
        inventory_reserve(
            product_id=product.id,
            quantity=2,
            reservation_key="order-3:monitor",
        )

    product.refresh_from_db()
    assert Reservation.objects.count() == 1
    assert product.reserved_quantity == 2
    assert product.available_quantity == 3
```

예상 실패: `Product`, `Reservation`, `inventory_reserve`, 도메인 예외가 아직 없어서 import 또는 AttributeError로 실패해야 합니다.

**GREEN: `apps/inventory/models.py`**

```python
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q


class Product(models.Model):
    name = models.CharField(max_length=120)
    stock_quantity = models.PositiveIntegerField()
    reserved_quantity = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(stock_quantity__gte=F("reserved_quantity")),
                name="inventory_stock_gte_reserved",
            ),
        ]

    @property
    def available_quantity(self) -> int:
        return self.stock_quantity - self.reserved_quantity

    def reserve(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValidationError("예약 수량은 1개 이상이어야 합니다.")
        if self.available_quantity < quantity:
            raise InsufficientStockError("재고가 부족합니다.")
        self.reserved_quantity += quantity


class Reservation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    reservation_key = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "reservation_key"],
                name="uniq_reservation_per_product_key",
            ),
        ]


class InsufficientStockError(Exception):
    pass


class DuplicateReservationError(Exception):
    pass
```

**GREEN: `apps/inventory/services.py`**

```python
from django.db import transaction

from apps.inventory.models import (
    DuplicateReservationError,
    InsufficientStockError,
    Product,
    Reservation,
)


def inventory_reserve(
    *,
    product_id: int,
    quantity: int,
    reservation_key: str,
) -> Reservation:
    with transaction.atomic():
        product = Product.objects.select_for_update().get(id=product_id)

        if Reservation.objects.filter(
            product=product,
            reservation_key=reservation_key,
        ).exists():
            raise DuplicateReservationError("이미 처리된 재고 예약입니다.")

        product.reserve(quantity)
        product.save(update_fields=["reserved_quantity"])

        return Reservation.objects.create(
            product=product,
            quantity=quantity,
            reservation_key=reservation_key,
        )
```

주의: 위 예외를 `models.py`에 두는 것은 최소 GREEN입니다. REFACTOR 단계에서는 `apps/inventory/exceptions.py`로 분리하는 편이 낫습니다.

**REFACTOR 방향**

`Product.reserve()`는 재고 불변식만 담당하고, `inventory_reserve()`는 트랜잭션, row lock, 중복 예약 방지만 담당합니다. 동시성 위험은 `select_for_update()`와 `(product, reservation_key)` 유니크 제약으로 막고, 별도 `TransactionTestCase` 또는 PostgreSQL 기반 isolated integration test에서 동시 요청을 추가 검증하세요.

**검증 명령**

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/inventory/test_inventory_reservation.py -q
python manage.py makemigrations inventory
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/ -q
```

---
> **관련 스킬 참조:**
> - Django pytest/TDD 구현 → **implementation-tdd**, **implementation-test**, **implementation-django** 스킬
> - 재고 예약 동시성/트랜잭션 설계 → **architecture-db**, **architecture-ddd** 스킬