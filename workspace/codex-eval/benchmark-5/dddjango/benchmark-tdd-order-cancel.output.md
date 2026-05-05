Fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 존재하지 않아 파일을 읽을 수 없었습니다. 또한 현재 sandbox가 read-only라 파일 생성/수정과 `pytest` 실행은 하지 못했습니다. 아래는 실제 프로젝트에 적용할 수 있는 TDD 흐름용 unified diff 예시입니다.

**RED: 실패 테스트 먼저**

```diff
diff --git a/tests/isolated/orders/test_order_cancel.py b/tests/isolated/orders/test_order_cancel.py
new file mode 100644
--- /dev/null
+++ b/tests/isolated/orders/test_order_cancel.py
@@ -0,0 +1,59 @@
+import pytest
+
+from apps.orders.models import Order
+from apps.orders.services import cancel_order
+from apps.orders.exceptions import OrderAlreadyCanceledError, OrderCannotBeCanceledError
+
+
+pytestmark = pytest.mark.django_db
+
+
+def create_order(status: str) -> Order:
+    return Order.objects.create(status=status)
+
+
+def test_cancel_order_when_paid_changes_status_to_canceled():
+    # Arrange
+    order = create_order(Order.Status.PAID)
+
+    # Act
+    canceled_order = cancel_order(order.id)
+
+    # Assert
+    order.refresh_from_db()
+    assert canceled_order.status == Order.Status.CANCELED
+    assert order.status == Order.Status.CANCELED
+
+
+def test_cancel_order_when_pending_changes_status_to_canceled():
+    # Arrange
+    order = create_order(Order.Status.PENDING)
+
+    # Act
+    canceled_order = cancel_order(order.id)
+
+    # Assert
+    assert canceled_order.status == Order.Status.CANCELED
+
+
+@pytest.mark.parametrize(
+    "status",
+    [Order.Status.SHIPPED, Order.Status.DELIVERED],
+)
+def test_cancel_order_when_fulfillment_started_raises_cannot_be_canceled(status):
+    # Arrange
+    order = create_order(status)
+
+    # Act / Assert
+    with pytest.raises(OrderCannotBeCanceledError):
+        cancel_order(order.id)
+
+
+def test_cancel_order_when_already_canceled_raises_already_canceled():
+    # Arrange
+    order = create_order(Order.Status.CANCELED)
+
+    # Act / Assert
+    with pytest.raises(OrderAlreadyCanceledError):
+        cancel_order(order.id)
```

예상 실패: `Order.Status.CANCELED`, `cancel_order`, 도메인 예외, `Order.cancel()`이 아직 없어서 import 또는 attribute 에러가 나야 합니다.

**GREEN: 최소 구현**

```diff
diff --git a/apps/orders/exceptions.py b/apps/orders/exceptions.py
new file mode 100644
--- /dev/null
+++ b/apps/orders/exceptions.py
@@ -0,0 +1,6 @@
+class OrderCannotBeCanceledError(Exception):
+    pass
+
+
+class OrderAlreadyCanceledError(Exception):
+    pass
diff --git a/apps/orders/models.py b/apps/orders/models.py
--- a/apps/orders/models.py
+++ b/apps/orders/models.py
@@ -1,3 +1,28 @@
 from django.db import models
+
+from apps.orders.exceptions import OrderAlreadyCanceledError, OrderCannotBeCanceledError
+
+
+class Order(models.Model):
+    """Aggregate Root. 주문 취소 가능 상태 불변식을 보호한다."""
+
+    class Status(models.TextChoices):
+        PENDING = "pending", "Pending"
+        PAID = "paid", "Paid"
+        SHIPPED = "shipped", "Shipped"
+        DELIVERED = "delivered", "Delivered"
+        CANCELED = "canceled", "Canceled"
+
+    status = models.CharField(
+        max_length=20,
+        choices=Status.choices,
+        default=Status.PENDING,
+    )
+
+    def cancel(self) -> None:
+        if self.status == self.Status.CANCELED:
+            raise OrderAlreadyCanceledError
+        if self.status in {self.Status.SHIPPED, self.Status.DELIVERED}:
+            raise OrderCannotBeCanceledError
+
+        self.status = self.Status.CANCELED
diff --git a/apps/orders/services.py b/apps/orders/services.py
new file mode 100644
--- /dev/null
+++ b/apps/orders/services.py
@@ -0,0 +1,13 @@
+from django.db import transaction
+
+from apps.orders.models import Order
+
+
+@transaction.atomic
+def cancel_order(order_id: int) -> Order:
+    order = Order.objects.select_for_update().get(id=order_id)
+    order.cancel()
+    order.save(update_fields=["status"])
+    return order
```

**REFACTOR 방향**

- `cancel()` 규칙은 서비스가 아니라 `Order` Aggregate Root 안에 유지합니다.
- 결제 환불, 재고 복구, 알림은 `OrderCanceledEvent`를 기록한 뒤 `transaction.on_commit()`에서 처리합니다.
- 테스트 데이터가 늘어나면 `create_order()`를 `tests/isolated/orders/conftest.py` fixture 또는 factory로 이동합니다.
- 조회 전용 로직은 `selectors.py`, 상태 변경 유스케이스는 `services.py`로 분리합니다.

**검증 명령**

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/orders/test_order_cancel.py -q
```

실행은 하지 못했습니다. 실제 프로젝트에서는 먼저 위 RED 테스트만 추가해 실패를 확인한 뒤, GREEN 구현을 붙여 같은 명령으로 통과를 확인하면 됩니다.

---
> **관련 스킬 참조:**
> - Django pytest TDD와 상태별 edge case 검증 → **implementation-tdd**, **implementation-test** 스킬