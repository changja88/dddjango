읽은 근거: `/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/shop/orders/models.py`, `views.py`, `tests.py`, `README.md`. 읽기 전용 sandbox라 파일 수정과 pytest 실행은 하지 못했습니다.

Ubiquitous Language: `Order` = 주문 Aggregate Root, `Cancellation Reason` = 취소 사유, `Actor Email` = 취소 수행자 감사 정보. 금지할 동의어는 `rollback`, `undo`, `admin_note`입니다.

RED 예상 실패: 현재는 `CancelOrderService`, `CancelOrderCommand`, `CancelReasonRequired`, `Order.mark_cancelled()`가 없어서 새 pytest가 import/attribute 단계에서 실패합니다. GREEN 최소 구현은 아래 diff입니다.

```diff
diff --git a/shop/orders/models.py b/shop/orders/models.py
index 5e1a111..a8f3b21 100644
--- a/shop/orders/models.py
+++ b/shop/orders/models.py
@@ -1,5 +1,8 @@
 from django.db import models
-from django.utils import timezone
+
+
+class OrderCannotBeCancelled(ValueError):
+    pass
 
 
 class Order(models.Model):
@@ -16,17 +19,14 @@ class Order(models.Model):
     cancel_reason = models.TextField(blank=True)
     created_at = models.DateTimeField(auto_now_add=True)
 
-    def cancel(self, reason: str, actor_email: str) -> None:
+    def mark_cancelled(self, cancel_reason: str, cancelled_at) -> None:
+        """Order aggregate invariant: shipped orders cannot become cancelled."""
         if self.status == self.STATUS_SHIPPED:
-            raise ValueError("shipped orders cannot be cancelled")
+            raise OrderCannotBeCancelled("shipped orders cannot be cancelled")
         if self.status == self.STATUS_CANCELLED:
             return
-        if not reason:
-            raise ValueError("cancel reason is required")
         self.status = self.STATUS_CANCELLED
-        self.cancel_reason = f"{reason} by {actor_email}"
-        self.cancelled_at = timezone.now()
-        self.save(update_fields=["status", "cancel_reason", "cancelled_at"])
+        self.cancel_reason = cancel_reason
+        self.cancelled_at = cancelled_at
 
 
 class Product(models.Model):
diff --git a/shop/orders/services.py b/shop/orders/services.py
new file mode 100644
index 0000000..f8c9320
--- /dev/null
+++ b/shop/orders/services.py
@@ -0,0 +1,42 @@
+from dataclasses import dataclass
+
+from django.db import transaction
+from django.utils import timezone
+
+from shop.orders.models import Order
+
+
+class CancelReasonRequired(ValueError):
+    pass
+
+
+@dataclass(frozen=True)
+class CancelOrderCommand:
+    order_id: int
+    reason: str
+    actor_email: str
+
+
+class CancelOrderService:
+    """Application service for the order cancellation use case."""
+
+    def cancel(self, command: CancelOrderCommand) -> Order:
+        with transaction.atomic():
+            order = Order.objects.select_for_update().get(id=command.order_id)
+            if order.status == Order.STATUS_CANCELLED:
+                return order
+
+            cancel_reason = self._build_cancel_reason(
+                reason=command.reason,
+                actor_email=command.actor_email,
+            )
+            order.mark_cancelled(
+                cancel_reason=cancel_reason,
+                cancelled_at=timezone.now(),
+            )
+            order.save(update_fields=["status", "cancel_reason", "cancelled_at"])
+            return order
+
+    def _build_cancel_reason(self, reason: str, actor_email: str) -> str:
+        reason = reason.strip()
+        if not reason:
+            raise CancelReasonRequired("cancel reason is required")
+
+        actor_email = actor_email.strip() or "system@example.com"
+        return f"{reason} by {actor_email}"
diff --git a/shop/orders/views.py b/shop/orders/views.py
index a9ad153..8d6b4e0 100644
--- a/shop/orders/views.py
+++ b/shop/orders/views.py
@@ -5,6 +5,7 @@ from django.views.decorators.http import require_POST
 
 from shop.orders.models import Order, Product, Reservation
+from shop.orders.services import CancelOrderCommand, CancelOrderService
 
 
 @require_POST
@@ -12,8 +13,9 @@ def cancel_order(request, order_id):
     payload = json.loads(request.body or "{}")
-    order = Order.objects.get(id=order_id)
-    order.cancel(
+    order = CancelOrderService().cancel(
+        CancelOrderCommand(
+            order_id=order_id,
             reason=payload.get("reason", ""),
             actor_email=payload.get("actor_email", "system@example.com"),
-    )
+        )
+    )
     return JsonResponse({"id": order.id, "status": order.status})
diff --git a/shop/orders/tests.py b/shop/orders/tests.py
index 9bf6c42..bf58936 100644
--- a/shop/orders/tests.py
+++ b/shop/orders/tests.py
@@ -1,16 +1,82 @@
-from django.test import TestCase
+import pytest
+from django.utils import timezone
 
-from shop.orders.models import Order
+from shop.orders.models import Order, OrderCannotBeCancelled
+from shop.orders.services import (
+    CancelOrderCommand,
+    CancelOrderService,
+    CancelReasonRequired,
+)
 
 
-class OrderModelTests(TestCase):
-    def test_cancel_sets_status(self):
-        order = Order.objects.create(
-            customer_email="buyer@example.com",
-            total_amount="100.00",
-        )
+@pytest.fixture
+def order():
+    return Order.objects.create(
+        customer_email="buyer@example.com",
+        total_amount="100.00",
+    )
 
-        order.cancel(reason="customer request", actor_email="ops@example.com")
 
-        self.assertEqual(order.status, Order.STATUS_CANCELLED)
+@pytest.mark.django_db
+def test_cancel_order_service_pending_order_cancels_with_audit_reason(order):
+    service = CancelOrderService()
+
+    cancelled_order = service.cancel(
+        CancelOrderCommand(
+            order_id=order.id,
+            reason="customer request",
+            actor_email="ops@example.com",
+        )
+    )
+
+    order.refresh_from_db()
+    assert cancelled_order.id == order.id
+    assert order.status == Order.STATUS_CANCELLED
+    assert order.cancel_reason == "customer request by ops@example.com"
+    assert order.cancelled_at is not None
+
+
+@pytest.mark.django_db
+def test_cancel_order_service_already_cancelled_is_idempotent_without_reason():
+    cancelled_at = timezone.now()
+    order = Order.objects.create(
+        customer_email="buyer@example.com",
+        total_amount="100.00",
+        status=Order.STATUS_CANCELLED,
+        cancel_reason="existing reason by ops@example.com",
+        cancelled_at=cancelled_at,
+    )
+
+    CancelOrderService().cancel(
+        CancelOrderCommand(order_id=order.id, reason="", actor_email="")
+    )
+
+    order.refresh_from_db()
+    assert order.status == Order.STATUS_CANCELLED
+    assert order.cancel_reason == "existing reason by ops@example.com"
+    assert order.cancelled_at == cancelled_at
+
+
+@pytest.mark.django_db
+def test_cancel_order_service_pending_order_requires_reason(order):
+    service = CancelOrderService()
+
+    with pytest.raises(CancelReasonRequired, match="cancel reason is required"):
+        service.cancel(
+            CancelOrderCommand(
+                order_id=order.id,
+                reason=" ",
+                actor_email="ops@example.com",
+            )
+        )
+
+
+@pytest.mark.django_db
+def test_order_mark_cancelled_rejects_shipped_invariant(order):
+    order.status = Order.STATUS_SHIPPED
+
+    with pytest.raises(OrderCannotBeCancelled, match="shipped orders"):
+        order.mark_cancelled("customer request by ops@example.com", timezone.now())
+
+
+@pytest.mark.django_db
+def test_order_mark_cancelled_does_not_persist_itself(order):
+    order.mark_cancelled("customer request by ops@example.com", timezone.now())
+
+    persisted_order = Order.objects.get(id=order.id)
+    assert persisted_order.status == Order.STATUS_PENDING
```

검증 명령:

```bash
cd /Users/hyun/Desktop/dddjango/evals/fixtures/django-shop
DJANGO_SETTINGS_MODULE=config.settings pytest shop/orders/tests.py -q
```

REFACTOR notes: 지금은 fixture 규모에 맞춰 Django ORM과 `transaction.atomic()`을 application service의 UoW 경계로 사용했습니다. 다음 단계에서 주문/재고 취소 연동이 생기면 `OrderRepository`와 domain event/outbox를 분리하는 편이 맞습니다.

---
> **관련 스킬 참조:**
> - Django service layer / pytest fixture 정리 → **implementation-django** 스킬