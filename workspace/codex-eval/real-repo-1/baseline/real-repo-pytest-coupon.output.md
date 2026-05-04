`config.toml`은 작업 디렉터리에 없어 읽지 못했습니다. fixture 파일은 확인했고, 아래는 직접 수정 대신 적용 가능한 unified diff입니다.

```diff
diff --git a/shop/orders/models.py b/shop/orders/models.py
index 5e77a4d..3f1e0a1 100644
--- a/shop/orders/models.py
+++ b/shop/orders/models.py
@@ -1,4 +1,7 @@
-from django.db import models
+from decimal import Decimal
+
+from django.db import models, transaction
 from django.utils import timezone
 
 
@@ -22,6 +25,25 @@ class Order(models.Model):
         self.cancelled_at = timezone.now()
         self.save(update_fields=["status", "cancel_reason", "cancelled_at"])
 
+    def apply_coupon(self, coupon: "Coupon", actor_email: str = "") -> None:
+        with transaction.atomic():
+            if CouponRedemption.objects.filter(order=self, coupon=coupon).exists():
+                raise ValueError("coupon already applied to this order")
+
+            current_total = Decimal(str(self.total_amount))
+            discount_amount = Decimal(str(coupon.discount_amount))
+            self.total_amount = max(Decimal("0.00"), current_total - discount_amount)
+            self.save(update_fields=["total_amount"])
+            CouponRedemption.objects.create(
+                order=self,
+                coupon=coupon,
+                actor_email=actor_email,
+            )
+
+
+class Coupon(models.Model):
+    code = models.CharField(max_length=64, unique=True)
+    discount_amount = models.DecimalField(max_digits=12, decimal_places=2)
+    created_at = models.DateTimeField(auto_now_add=True)
+
 
 class Product(models.Model):
     sku = models.CharField(max_length=64, unique=True)
@@ -40,3 +62,15 @@ class Reservation(models.Model):
     quantity = models.PositiveIntegerField()
     idempotency_key = models.CharField(max_length=128)
     created_at = models.DateTimeField(auto_now_add=True)
+
+
+class CouponRedemption(models.Model):
+    order = models.ForeignKey(Order, on_delete=models.PROTECT)
+    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT)
+    actor_email = models.EmailField(blank=True)
+    created_at = models.DateTimeField(auto_now_add=True)
+
+    class Meta:
+        constraints = [
+            models.UniqueConstraint(fields=["order", "coupon"], name="unique_coupon_per_order"),
+        ]
diff --git a/shop/orders/tests.py b/shop/orders/tests.py
index cf2f2b0..3469196 100644
--- a/shop/orders/tests.py
+++ b/shop/orders/tests.py
@@ -1,6 +1,10 @@
+from decimal import Decimal
+
+import pytest
 from django.test import TestCase
 
-from shop.orders.models import Order
+from shop.orders.models import Coupon, CouponRedemption, Order
 
 
 class OrderModelTests(TestCase):
@@ -14,3 +18,32 @@ class OrderModelTests(TestCase):
         order.cancel(reason="customer request", actor_email="ops@example.com")
 
         self.assertEqual(order.status, Order.STATUS_CANCELLED)
+
+
+@pytest.mark.django_db
+def test_apply_coupon_discounts_order_total_amount():
+    order = Order.objects.create(
+        customer_email="buyer@example.com",
+        total_amount=Decimal("100.00"),
+    )
+    coupon = Coupon.objects.create(
+        code="WELCOME10",
+        discount_amount=Decimal("10.00"),
+    )
+
+    order.apply_coupon(coupon, actor_email="ops@example.com")
+
+    order.refresh_from_db()
+    assert order.total_amount == Decimal("90.00")
+    assert CouponRedemption.objects.filter(order=order, coupon=coupon).count() == 1
+
+
+@pytest.mark.django_db
+def test_apply_coupon_rejects_duplicate_use_on_same_order():
+    order = Order.objects.create(
+        customer_email="buyer@example.com",
+        total_amount=Decimal("100.00"),
+    )
+    coupon = Coupon.objects.create(code="SAVE15", discount_amount=Decimal("15.00"))
+
+    order.apply_coupon(coupon)
+    with pytest.raises(ValueError, match="coupon already applied"):
+        order.apply_coupon(coupon)
+
+    order.refresh_from_db()
+    assert order.total_amount == Decimal("85.00")
+    assert CouponRedemption.objects.filter(order=order, coupon=coupon).count() == 1
```

RED: 먼저 `pytest.mark.django_db` 테스트 2개를 추가해 `Order.total_amount` 차감과 같은 주문의 같은 쿠폰 재사용 실패를 검증합니다.

GREEN: `Coupon`, `CouponRedemption`, `Order.apply_coupon()`을 추가해 할인액을 총액에서 차감하고 주문-쿠폰 unique constraint로 중복 사용을 막습니다.

REFACTOR: 현재는 fixture에 맞춘 최소 모델 로직입니다. 실제 앱이면 쿠폰 유효기간, 최소 주문금액, 사용 한도, 동시성 오류 메시지 정리를 서비스 계층으로 분리하는 단계가 다음입니다.