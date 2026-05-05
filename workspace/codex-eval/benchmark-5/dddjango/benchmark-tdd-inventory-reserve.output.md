실행하지 못했습니다. fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 없고 현재 workspace도 비어 있으며 read-only sandbox라 파일 생성, migration, pytest 실행이 불가능했습니다. 아래는 **RED 테스트를 먼저 추가한 뒤**, 그 테스트를 통과시키는 **GREEN 최소 구현**을 붙이는 unified diff입니다.

**RED → 예상 실패**
`inventory.models`, `inventory.services`, 도메인 예외가 없어서 import 단계에서 먼저 실패해야 합니다.

```diff
diff --git a/tests/isolated/integration/test_inventory_reservations.py b/tests/isolated/integration/test_inventory_reservations.py
new file mode 100644
--- /dev/null
+++ b/tests/isolated/integration/test_inventory_reservations.py
@@ -0,0 +1,54 @@
+import pytest
+
+from inventory.models import InventoryItem, InventoryReservation
+from inventory.services import (
+    DuplicateReservationError,
+    InsufficientStockError,
+    inventory_reserve,
+)
+
+
+pytestmark = pytest.mark.django_db
+
+
+def test_inventory_reserve_when_stock_is_available_creates_reservation():
+    # Arrange
+    item = InventoryItem.objects.create(sku="SKU-1", available_quantity=10)
+
+    # Act
+    reservation = inventory_reserve(
+        sku=item.sku,
+        reservation_key="order-1:SKU-1",
+        quantity=3,
+    )
+
+    # Assert
+    item.refresh_from_db()
+    assert reservation.sku == "SKU-1"
+    assert reservation.quantity == 3
+    assert item.available_quantity == 7
+
+
+def test_inventory_reserve_when_stock_is_insufficient_raises_error():
+    # Arrange
+    item = InventoryItem.objects.create(sku="SKU-2", available_quantity=2)
+
+    # Act / Assert
+    with pytest.raises(InsufficientStockError):
+        inventory_reserve(
+            sku=item.sku,
+            reservation_key="order-2:SKU-2",
+            quantity=3,
+        )
+
+    item.refresh_from_db()
+    assert item.available_quantity == 2
+    assert InventoryReservation.objects.count() == 0
+
+
+def test_inventory_reserve_when_same_reservation_key_is_reused_does_not_reserve_twice():
+    """중복 요청이 재고를 두 번 차감하지 않는지 검증한다."""
+    # Arrange
+    item = InventoryItem.objects.create(sku="SKU-3", available_quantity=5)
+
+    # Act
+    first = inventory_reserve(sku=item.sku, reservation_key="order-3:SKU-3", quantity=2)
+    second = inventory_reserve(sku=item.sku, reservation_key="order-3:SKU-3", quantity=2)
+
+    # Assert
+    item.refresh_from_db()
+    assert second.id == first.id
+    assert item.available_quantity == 3
+    assert InventoryReservation.objects.count() == 1
+
+
+def test_inventory_reserve_when_reservation_key_conflicts_with_different_payload_raises_error():
+    # Arrange
+    item = InventoryItem.objects.create(sku="SKU-4", available_quantity=5)
+    inventory_reserve(sku=item.sku, reservation_key="order-4", quantity=2)
+
+    # Act / Assert
+    with pytest.raises(DuplicateReservationError):
+        inventory_reserve(sku=item.sku, reservation_key="order-4", quantity=3)
diff --git a/inventory/models.py b/inventory/models.py
new file mode 100644
--- /dev/null
+++ b/inventory/models.py
@@ -0,0 +1,53 @@
+from django.core.exceptions import ValidationError
+from django.db import models
+from django.db.models import Q
+
+
+class InventoryItem(models.Model):
+    """Aggregate Root: 재고 수량은 음수가 될 수 없다."""
+
+    sku = models.CharField(max_length=64, unique=True)
+    available_quantity = models.PositiveIntegerField()
+    created_at = models.DateTimeField(auto_now_add=True)
+    updated_at = models.DateTimeField(auto_now=True)
+
+    class Meta:
+        ordering = ["sku"]
+        indexes = [models.Index(fields=["sku"], name="idx_inventory_item_sku")]
+        constraints = [
+            models.CheckConstraint(
+                condition=Q(available_quantity__gte=0),
+                name="inventory_available_quantity_gte_0",
+            )
+        ]
+
+    def __str__(self) -> str:
+        return self.sku
+
+    def reserve(self, *, quantity: int) -> None:
+        if quantity <= 0:
+            raise ValidationError("예약 수량은 1 이상이어야 합니다.")
+        if self.available_quantity < quantity:
+            raise ValidationError("재고가 부족합니다.")
+        self.available_quantity -= quantity
+
+
+class InventoryReservation(models.Model):
+    sku = models.CharField(max_length=64)
+    reservation_key = models.CharField(max_length=128, unique=True)
+    quantity = models.PositiveIntegerField()
+    created_at = models.DateTimeField(auto_now_add=True)
+
+    class Meta:
+        ordering = ["-created_at"]
+        indexes = [
+            models.Index(fields=["sku"], name="idx_inventory_reservation_sku"),
+        ]
+        constraints = [
+            models.CheckConstraint(
+                condition=Q(quantity__gt=0),
+                name="inventory_reservation_quantity_gt_0",
+            )
+        ]
+
+    def __str__(self) -> str:
+        return self.reservation_key
diff --git a/inventory/services.py b/inventory/services.py
new file mode 100644
--- /dev/null
+++ b/inventory/services.py
@@ -0,0 +1,51 @@
+from django.core.exceptions import ValidationError
+from django.db import transaction
+
+from inventory.models import InventoryItem, InventoryReservation
+
+
+class InsufficientStockError(Exception):
+    pass
+
+
+class DuplicateReservationError(Exception):
+    pass
+
+
+def inventory_reserve(
+    *,
+    sku: str,
+    reservation_key: str,
+    quantity: int,
+) -> InventoryReservation:
+    with transaction.atomic():
+        existing = InventoryReservation.objects.filter(
+            reservation_key=reservation_key,
+        ).first()
+        if existing is not None:
+            if existing.sku == sku and existing.quantity == quantity:
+                return existing
+            raise DuplicateReservationError("이미 다른 내용으로 처리된 예약입니다.")
+
+        item = InventoryItem.objects.select_for_update().get(sku=sku)
+
+        try:
+            item.reserve(quantity=quantity)
+        except ValidationError as exc:
+            raise InsufficientStockError("재고가 부족합니다.") from exc
+
+        item.save(update_fields=["available_quantity", "updated_at"])
+        return InventoryReservation.objects.create(
+            sku=sku,
+            reservation_key=reservation_key,
+            quantity=quantity,
+        )
```

**REFACTOR 메모**
도메인 규칙은 `InventoryItem.reserve()`에 두고, 트랜잭션/락/중복 키 처리는 서비스에 둡니다. 실제 동시성 검증은 SQLite보다 PostgreSQL 기반 `tests/real/`에서 `select_for_update()` 경합 테스트로 보강하는 편이 정확합니다.

**검증 명령**
```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/integration/test_inventory_reservations.py -q
python manage.py makemigrations inventory
python manage.py check
```

---
> **관련 스킬 참조:**
> - 동시성 재고 검증 → **architecture-db** 스킬
> - Django 서비스/모델 경계 → **implementation-django** 스킬