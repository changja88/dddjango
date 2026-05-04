implementation-tdd / implementation-test 지침을 적용했습니다. Read-only sandbox라 파일 수정과 pytest 실행은 하지 못했습니다. 아래는 fixture를 읽은 뒤 제안하는 RED 테스트 우선 + GREEN 최소 구현 unified diff입니다.

**RED / GREEN Diff**
```diff
diff --git a/shop/orders/tests.py b/shop/orders/tests.py
index 5d7c0c1..c314c22 100644
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
@@ -14,3 +18,34 @@ class OrderModelTests(TestCase):
         order.cancel(reason="customer request", actor_email="ops@example.com")
 
         self.assertEqual(order.status, Order.STATUS_CANCELLED)
+
+
+@pytest.mark.django_db
+def test_order_apply_coupon_with_valid_coupon_reduces_total_amount():
+    order = Order.objects.create(
+        customer_email="buyer@example.com",
+        total_amount=Decimal("100.00"),
+    )
+    coupon = Coupon.objects.create(
+        code="WELCOME15",
+        discount_amount=Decimal("15.00"),
+    )
+
+    order.apply_coupon(coupon)
+
+    order.refresh_from_db()
+    assert order.total_amount == Decimal("85.00")
+    assert CouponRedemption.objects.filter(order=order, coupon=coupon).exists()
+
+
+@pytest.mark.django_db
+def test_order_apply_coupon_with_used_coupon_raises_error():
+    first_order = Order.objects.create(
+        customer_email="first@example.com",
+        total_amount=Decimal("100.00"),
+    )
+    second_order = Order.objects.create(
+        customer_email="second@example.com",
+        total_amount=Decimal("50.00"),
+    )
+    coupon = Coupon.objects.create(code="ONCE", discount_amount=Decimal("10.00"))
+    first_order.apply_coupon(coupon)
+
+    with pytest.raises(ValueError, match="coupon has already been used"):
+        second_order.apply_coupon(coupon)
+
+    second_order.refresh_from_db()
+    assert second_order.total_amount == Decimal("50.00")
+    assert CouponRedemption.objects.filter(coupon=coupon).count() == 1
diff --git a/shop/orders/models.py b/shop/orders/models.py
index 55d0b12..2f05d7e 100644
--- a/shop/orders/models.py
+++ b/shop/orders/models.py
@@ -1,4 +1,6 @@
+from decimal import Decimal
+
+from django.db import IntegrityError, models, transaction
-from django.db import models
 from django.utils import timezone
 
 
@@ -21,6 +23,19 @@ class Order(models.Model):
         self.cancelled_at = timezone.now()
         self.save(update_fields=["status", "cancel_reason", "cancelled_at"])
 
+    def apply_coupon(self, coupon: "Coupon") -> None:
+        discount_amount = min(
+            Decimal(str(self.total_amount)),
+            coupon.discount_amount,
+        )
+
+        with transaction.atomic():
+            try:
+                CouponRedemption.objects.create(
+                    order=self,
+                    coupon=coupon,
+                    discount_amount=discount_amount,
+                )
+            except IntegrityError as exc:
+                raise ValueError("coupon has already been used") from exc
+            self.total_amount = Decimal(str(self.total_amount)) - discount_amount
+            self.save(update_fields=["total_amount"])
+
 
 class Product(models.Model):
     sku = models.CharField(max_length=64, unique=True)
@@ -41,3 +56,17 @@ class Reservation(models.Model):
     quantity = models.PositiveIntegerField()
     idempotency_key = models.CharField(max_length=128)
     created_at = models.DateTimeField(auto_now_add=True)
+
+
+class Coupon(models.Model):
+    code = models.CharField(max_length=64, unique=True)
+    discount_amount = models.DecimalField(max_digits=12, decimal_places=2)
+    is_active = models.BooleanField(default=True)
+    created_at = models.DateTimeField(auto_now_add=True)
+
+
+class CouponRedemption(models.Model):
+    order = models.ForeignKey(Order, on_delete=models.PROTECT)
+    coupon = models.OneToOneField(Coupon, on_delete=models.PROTECT)
+    discount_amount = models.DecimalField(max_digits=12, decimal_places=2)
+    redeemed_at = models.DateTimeField(auto_now_add=True)
```

**RED**
`test_order_apply_coupon_with_valid_coupon_reduces_total_amount`는 `Coupon`이 없어서 import 단계에서 실패해야 합니다. 두 번째 테스트는 동일 쿠폰 재사용 방지 정책과 두 번째 주문의 `total_amount`가 바뀌지 않는지를 검증합니다.

**GREEN**
최소 구현은 `Coupon`, `CouponRedemption`, `Order.apply_coupon()`입니다. `CouponRedemption.coupon`을 `OneToOneField`로 두어 쿠폰 1회 사용을 DB 제약으로 막고, `transaction.atomic()`으로 할인 저장과 사용 기록을 한 단위로 묶습니다.

**REFACTOR**
그린 이후에는 `Order` 모델이 할인 정책까지 갖는 비대함을 줄이기 위해 `CouponService`로 분리하고, 활성 쿠폰 검증과 만료일 정책을 별도 테스트로 확장하는 편이 좋습니다.

**실행 명령**
```bash
cd /Users/hyun/Desktop/dddjango/evals/fixtures/django-shop
DJANGO_SETTINGS_MODULE=config.settings pytest shop/orders/tests.py -q
```

---
> **관련 스킬 참조:**
> - pytest/TDD 구현 검증 → **implementation-test**, **implementation-tdd** 스킬