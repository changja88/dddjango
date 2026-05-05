[주요 내용]

`/Users/hyun/Desktop/dddjango/none`는 존재하지 않고, 현재 workspace도 비어 있어 파일 수정과 pytest 실행은 못 했습니다. 아래는 테스트가 먼저 실패하는 RED diff와, 그 테스트를 통과시키는 최소 GREEN 구현입니다. `select_for_update()`로 재고 행을 잠가 중복/동시 예약 시 이중 차감 위험을 줄이고, 도메인 불변식은 `StockItem.reserve()`에 둡니다.

```diff
diff --git a/tests/isolated/integration/test_inventory_reservation.py b/tests/isolated/integration/test_inventory_reservation.py
new file mode 100644
--- /dev/null
+++ b/tests/isolated/integration/test_inventory_reservation.py
@@ -0,0 +1,48 @@
+import pytest
+
+from inventory.models import Reservation, StockItem
+from inventory.services import InsufficientStock, inventory_reserve
+
+
+@pytest.fixture
+def stock_item(db):
+    item = StockItem.objects.create(sku="SKU-001", available_quantity=10)
+    yield item
+
+
+@pytest.mark.django_db
+def test_inventory_reserve_available_stock_creates_reservation(stock_item):
+    # Arrange
+    quantity = 3
+
+    # Act
+    reservation = inventory_reserve(
+        stock_item_id=stock_item.id,
+        quantity=quantity,
+        reservation_key="order-1:SKU-001",
+    )
+
+    # Assert
+    stock_item.refresh_from_db()
+    assert stock_item.available_quantity == 7
+    assert reservation.quantity == 3
+    assert Reservation.objects.count() == 1
+
+
+@pytest.mark.django_db
+def test_inventory_reserve_insufficient_stock_raises_and_keeps_stock(stock_item):
+    # Arrange
+    quantity = 11
+
+    # Act / Assert
+    with pytest.raises(InsufficientStock, match="재고 부족"):
+        inventory_reserve(
+            stock_item_id=stock_item.id,
+            quantity=quantity,
+            reservation_key="order-2:SKU-001",
+        )
+
+    stock_item.refresh_from_db()
+    assert stock_item.available_quantity == 10
+    assert Reservation.objects.count() == 0
+
+
+@pytest.mark.django_db
+def test_inventory_reserve_duplicate_key_returns_existing_without_decrementing(stock_item):
+    # Arrange
+    first = inventory_reserve(
+        stock_item_id=stock_item.id,
+        quantity=4,
+        reservation_key="order-3:SKU-001",
+    )
+
+    # Act
+    second = inventory_reserve(
+        stock_item_id=stock_item.id,
+        quantity=4,
+        reservation_key="order-3:SKU-001",
+    )
+
+    # Assert
+    stock_item.refresh_from_db()
+    assert second.id == first.id
+    assert stock_item.available_quantity == 6
+    assert Reservation.objects.count() == 1
diff --git a/inventory/models.py b/inventory/models.py
new file mode 100644
--- /dev/null
+++ b/inventory/models.py
@@ -0,0 +1,54 @@
+from django.db import models
+
+
+class StockItem(models.Model):
+    sku = models.CharField(max_length=64, unique=True)
+    available_quantity = models.PositiveIntegerField(default=0)
+
+    class Meta:
+        ordering = ["sku"]
+        constraints = [
+            models.CheckConstraint(
+                check=models.Q(available_quantity__gte=0),
+                name="inventory_stock_available_quantity_non_negative",
+            ),
+        ]
+
+    def __str__(self) -> str:
+        return self.sku
+
+    def reserve(self, *, quantity: int) -> None:
+        """Invariant: available_quantity must never become negative."""
+        if quantity <= 0:
+            raise InvalidReservationQuantity("예약 수량은 1 이상이어야 합니다.")
+        if self.available_quantity < quantity:
+            raise InsufficientStock("재고 부족")
+        self.available_quantity -= quantity
+
+
+class Reservation(models.Model):
+    stock_item = models.ForeignKey(
+        StockItem,
+        on_delete=models.PROTECT,
+        related_name="reservations",
+    )
+    reservation_key = models.CharField(max_length=128, unique=True)
+    quantity = models.PositiveIntegerField()
+    created_at = models.DateTimeField(auto_now_add=True)
+
+    class Meta:
+        ordering = ["-created_at", "id"]
+        constraints = [
+            models.CheckConstraint(
+                check=models.Q(quantity__gt=0),
+                name="inventory_reservation_quantity_positive",
+            ),
+        ]
+
+    def __str__(self) -> str:
+        return self.reservation_key
+
+
+class InventoryError(Exception):
+    pass
+
+
+class InvalidReservationQuantity(InventoryError):
+    pass
+
+
+class InsufficientStock(InventoryError):
+    pass
diff --git a/inventory/services.py b/inventory/services.py
new file mode 100644
--- /dev/null
+++ b/inventory/services.py
@@ -0,0 +1,34 @@
+from django.db import transaction
+
+from inventory.models import (
+    InsufficientStock,
+    InvalidReservationQuantity,
+    Reservation,
+    StockItem,
+)
+
+
+def inventory_reserve(
+    *,
+    stock_item_id: int,
+    quantity: int,
+    reservation_key: str,
+) -> Reservation:
+    with transaction.atomic():
+        stock_item = StockItem.objects.select_for_update().get(pk=stock_item_id)
+
+        existing = Reservation.objects.filter(
+            reservation_key=reservation_key,
+            stock_item=stock_item,
+            quantity=quantity,
+        ).first()
+        if existing is not None:
+            return existing
+
+        stock_item.reserve(quantity=quantity)
+        stock_item.save(update_fields=["available_quantity"])
+
+        return Reservation.objects.create(
+            stock_item=stock_item,
+            quantity=quantity,
+            reservation_key=reservation_key,
+        )
+
+
+__all__ = ["InsufficientStock", "InvalidReservationQuantity", "inventory_reserve"]
```

RED 예상 실패: `inventory` 앱, `StockItem`, `Reservation`, `inventory_reserve`, 예외 타입이 없어서 import 단계부터 실패합니다.

검증은 실행하지 못했습니다. 실제 프로젝트에서는 다음 순서로 확인하세요.

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/integration/test_inventory_reservation.py -q
python manage.py makemigrations inventory
python manage.py migrate
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/integration/test_inventory_reservation.py -q
```

---
> **관련 스킬 참조:**
> - Django 모델/서비스 경계와 pytest TDD → **implementation-django**, **implementation-test**, **implementation-tdd** 스킬