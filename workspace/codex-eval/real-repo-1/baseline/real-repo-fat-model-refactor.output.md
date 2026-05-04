아래는 읽기 전용 환경 기준으로 제안하는 unified diff입니다. 핵심은 `Order.cancel()`의 use-case 규칙과 저장 책임을 `shop/orders/services.py`의 application service로 옮기고, 모델은 상태 전이용 최소 메서드만 갖게 하는 것입니다.

```diff
diff --git a/shop/orders/models.py b/shop/orders/models.py
index 4d6f7f1..8d2f0b4 100644
--- a/shop/orders/models.py
+++ b/shop/orders/models.py
@@ -1,5 +1,4 @@
 from django.db import models
-from django.utils import timezone
 
 
 class Order(models.Model):
@@ -16,18 +15,14 @@ class Order(models.Model):
     cancel_reason = models.TextField(blank=True)
     created_at = models.DateTimeField(auto_now_add=True)
 
-    def cancel(self, reason: str, actor_email: str) -> None:
+    def mark_cancelled(self, *, cancel_reason: str, cancelled_at) -> None:
         if self.status == self.STATUS_SHIPPED:
             raise ValueError("shipped orders cannot be cancelled")
-        if self.status == self.STATUS_CANCELLED:
-            return
-        if not reason:
+        if not cancel_reason:
             raise ValueError("cancel reason is required")
+
         self.status = self.STATUS_CANCELLED
-        self.cancel_reason = f"{reason} by {actor_email}"
-        self.cancelled_at = timezone.now()
-        self.save(update_fields=["status", "cancel_reason", "cancelled_at"])
+        self.cancel_reason = cancel_reason
+        self.cancelled_at = cancelled_at
 
 
 class Product(models.Model):
diff --git a/shop/orders/services.py b/shop/orders/services.py
new file mode 100644
index 0000000..f2d2e0c
--- /dev/null
+++ b/shop/orders/services.py
@@ -0,0 +1,27 @@
+from django.db import transaction
+from django.utils import timezone
+
+from shop.orders.models import Order
+
+
+def cancel_order(*, order_id: int, reason: str, actor_email: str) -> Order:
+    if not reason:
+        raise ValueError("cancel reason is required")
+
+    with transaction.atomic():
+        order = Order.objects.select_for_update().get(id=order_id)
+
+        if order.status == Order.STATUS_CANCELLED:
+            return order
+        if order.status == Order.STATUS_SHIPPED:
+            raise ValueError("shipped orders cannot be cancelled")
+
+        order.mark_cancelled(
+            cancel_reason=f"{reason} by {actor_email}",
+            cancelled_at=timezone.now(),
+        )
+        order.save(update_fields=["status", "cancel_reason", "cancelled_at"])
+
+    return order
diff --git a/shop/orders/views.py b/shop/orders/views.py
index 90d85bb..e6e79c8 100644
--- a/shop/orders/views.py
+++ b/shop/orders/views.py
@@ -5,6 +5,7 @@ from django.http import JsonResponse
 from django.views.decorators.http import require_POST
 
 from shop.orders.models import Order, Product, Reservation
+from shop.orders.services import cancel_order as cancel_order_service
 
 
 @require_POST
@@ -12,8 +13,8 @@ def cancel_order(request, order_id):
     payload = json.loads(request.body or "{}")
-    order = Order.objects.get(id=order_id)
-    order.cancel(
+    order = cancel_order_service(
+        order_id=order_id,
         reason=payload.get("reason", ""),
         actor_email=payload.get("actor_email", "system@example.com"),
     )
diff --git a/shop/orders/tests.py b/shop/orders/tests.py
index 4ad8e70..b7fdd25 100644
--- a/shop/orders/tests.py
+++ b/shop/orders/tests.py
@@ -1,15 +1,86 @@
-from django.test import TestCase
+import pytest
+from django.utils import timezone
 
 from shop.orders.models import Order
+from shop.orders.services import cancel_order
 
+pytestmark = pytest.mark.django_db
 
-class OrderModelTests(TestCase):
-    def test_cancel_sets_status(self):
-        order = Order.objects.create(
-            customer_email="buyer@example.com",
-            total_amount="100.00",
-        )
 
-        order.cancel(reason="customer request", actor_email="ops@example.com")
+def test_order_model_marks_cancelled_without_saving():
+    order = Order.objects.create(
+        customer_email="buyer@example.com",
+        total_amount="100.00",
+    )
+    cancelled_at = timezone.now()
 
-        self.assertEqual(order.status, Order.STATUS_CANCELLED)
+    order.mark_cancelled(
+        cancel_reason="customer request by ops@example.com",
+        cancelled_at=cancelled_at,
+    )
+
+    assert order.status == Order.STATUS_CANCELLED
+    assert order.cancel_reason == "customer request by ops@example.com"
+    assert order.cancelled_at == cancelled_at
+
+    order.refresh_from_db()
+    assert order.status == Order.STATUS_PENDING
+    assert order.cancel_reason == ""
+    assert order.cancelled_at is None
+
+
+def test_order_model_rejects_shipped_cancel_transition():
+    order = Order.objects.create(
+        customer_email="buyer@example.com",
+        total_amount="100.00",
+        status=Order.STATUS_SHIPPED,
+    )
+
+    with pytest.raises(ValueError, match="shipped orders cannot be cancelled"):
+        order.mark_cancelled(
+            cancel_reason="customer request by ops@example.com",
+            cancelled_at=timezone.now(),
+        )
+
+
+def test_cancel_order_sets_status_reason_and_timestamp():
+    order = Order.objects.create(
+        customer_email="buyer@example.com",
+        total_amount="100.00",
+    )
+
+    cancelled = cancel_order(
+        order_id=order.id,
+        reason="customer request",
+        actor_email="ops@example.com",
+    )
+
+    assert cancelled.status == Order.STATUS_CANCELLED
+    assert cancelled.cancel_reason == "customer request by ops@example.com"
+    assert cancelled.cancelled_at is not None
+
+    order.refresh_from_db()
+    assert order.status == Order.STATUS_CANCELLED
+    assert order.cancel_reason == "customer request by ops@example.com"
+    assert order.cancelled_at is not None
+
+
+def test_cancel_order_requires_reason():
+    order = Order.objects.create(
+        customer_email="buyer@example.com",
+        total_amount="100.00",
+    )
+
+    with pytest.raises(ValueError, match="cancel reason is required"):
+        cancel_order(order_id=order.id, reason="", actor_email="ops@example.com")
+
+    order.refresh_from_db()
+    assert order.status == Order.STATUS_PENDING
+
+
+def test_cancel_order_is_idempotent_for_already_cancelled_orders():
+    cancelled_at = timezone.now()
+    order = Order.objects.create(
+        customer_email="buyer@example.com",
+        total_amount="100.00",
+        status=Order.STATUS_CANCELLED,
+        cancel_reason="original by ops@example.com",
+        cancelled_at=cancelled_at,
+    )
+
+    cancelled = cancel_order(
+        order_id=order.id,
+        reason="new reason",
+        actor_email="other@example.com",
+    )
+
+    assert cancelled.cancel_reason == "original by ops@example.com"
+    assert cancelled.cancelled_at == cancelled_at
```

테스트는 실행하지 않았습니다. 현재 환경이 read-only라 파일 적용 없이 diff만 제안했습니다.