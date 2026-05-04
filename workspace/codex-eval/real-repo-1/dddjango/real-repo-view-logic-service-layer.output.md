Fixture 파일을 읽고, `reserve_inventory`의 DB/비즈니스 처리를 `shop.orders.services.order_reserve_inventory()`로 분리하는 patch입니다. `transaction.atomic()` 경계는 service에 있고, view는 payload/header 파싱과 JSON 응답 변환만 담당합니다.

```diff
diff --git a/shop/orders/services.py b/shop/orders/services.py
new file mode 100644
index 0000000..3f3b1b4
--- /dev/null
+++ b/shop/orders/services.py
@@ -0,0 +1,42 @@
+from dataclasses import dataclass
+
+from django.db import transaction
+
+from shop.orders.models import Order, Product, Reservation
+
+
+class NotEnoughStock(Exception):
+    def __init__(self, *, available: int) -> None:
+        self.available = available
+        super().__init__("not enough stock")
+
+
+@dataclass(frozen=True)
+class InventoryReservationResult:
+    reservation_id: int
+
+
+def order_reserve_inventory(
+    *,
+    order_id: int,
+    product_id: int,
+    quantity: int,
+    idempotency_key: str,
+) -> InventoryReservationResult:
+    with transaction.atomic():
+        product = Product.objects.select_for_update().get(id=product_id)
+        order = Order.objects.select_for_update().get(id=order_id)
+
+        if product.stock_quantity < quantity:
+            raise NotEnoughStock(available=product.stock_quantity)
+
+        product.stock_quantity -= quantity
+        product.save(update_fields=["stock_quantity"])
+
+        reservation = Reservation.objects.create(
+            product=product,
+            order=order,
+            quantity=quantity,
+            idempotency_key=idempotency_key,
+        )
+
+    return InventoryReservationResult(reservation_id=reservation.id)
diff --git a/shop/orders/views.py b/shop/orders/views.py
index 09d9a35..19f9af0 100644
--- a/shop/orders/views.py
+++ b/shop/orders/views.py
@@ -1,10 +1,10 @@
 import json
 
-from django.db import transaction
 from django.http import JsonResponse
 from django.views.decorators.http import require_POST
 
-from shop.orders.models import Order, Product, Reservation
+from shop.orders.models import Order
+from shop.orders.services import NotEnoughStock, order_reserve_inventory
 
 
 @require_POST
@@ -24,24 +24,18 @@ def reserve_inventory(request, order_id):
     quantity = int(payload["quantity"])
     idempotency_key = request.headers.get("Idempotency-Key", "")
 
-    with transaction.atomic():
-        product = Product.objects.select_for_update().get(id=product_id)
-        order = Order.objects.select_for_update().get(id=order_id)
-        if product.stock_quantity < quantity:
-            return JsonResponse(
-                {"error": "not_enough_stock", "available": product.stock_quantity},
-                status=409,
-            )
-        product.stock_quantity -= quantity
-        product.save(update_fields=["stock_quantity"])
-        reservation = Reservation.objects.create(
-            product=product,
-            order=order,
+    try:
+        result = order_reserve_inventory(
+            order_id=order_id,
+            product_id=product_id,
             quantity=quantity,
             idempotency_key=idempotency_key,
         )
+    except NotEnoughStock as exc:
+        return JsonResponse(
+            {"error": "not_enough_stock", "available": exc.available},
+            status=409,
+        )
 
-    return JsonResponse({"reservation_id": reservation.id}, status=201)
+    return JsonResponse({"reservation_id": result.reservation_id}, status=201)
diff --git a/shop/orders/tests.py b/shop/orders/tests.py
index 8a25b45..99ed73f 100644
--- a/shop/orders/tests.py
+++ b/shop/orders/tests.py
@@ -1,6 +1,9 @@
+import json
+
 from django.test import TestCase
 
-from shop.orders.models import Order
+from shop.orders.models import Order, Product, Reservation
+from shop.orders.services import NotEnoughStock, order_reserve_inventory
 
 
 class OrderModelTests(TestCase):
@@ -15,3 +18,63 @@ class OrderModelTests(TestCase):
         order.cancel(reason="customer request", actor_email="ops@example.com")
 
         self.assertEqual(order.status, Order.STATUS_CANCELLED)
+
+
+class InventoryReservationServiceTests(TestCase):
+    def setUp(self):
+        self.order = Order.objects.create(
+            customer_email="buyer@example.com",
+            total_amount="100.00",
+        )
+        self.product = Product.objects.create(
+            sku="SKU-1",
+            name="Widget",
+            stock_quantity=5,
+            price="10.00",
+        )
+
+    def test_order_reserve_inventory_decrements_stock_and_creates_reservation(self):
+        result = order_reserve_inventory(
+            order_id=self.order.id,
+            product_id=self.product.id,
+            quantity=2,
+            idempotency_key="request-1",
+        )
+
+        self.product.refresh_from_db()
+        reservation = Reservation.objects.get(id=result.reservation_id)
+        self.assertEqual(self.product.stock_quantity, 3)
+        self.assertEqual(reservation.order, self.order)
+        self.assertEqual(reservation.product, self.product)
+        self.assertEqual(reservation.quantity, 2)
+
+    def test_order_reserve_inventory_raises_when_stock_is_insufficient(self):
+        with self.assertRaises(NotEnoughStock) as error:
+            order_reserve_inventory(
+                order_id=self.order.id,
+                product_id=self.product.id,
+                quantity=10,
+                idempotency_key="request-2",
+            )
+
+        self.product.refresh_from_db()
+        self.assertEqual(error.exception.available, 5)
+        self.assertEqual(self.product.stock_quantity, 5)
+        self.assertEqual(Reservation.objects.count(), 0)
+
+    def test_reserve_inventory_view_returns_created_response(self):
+        response = self.client.post(
+            f"/orders/{self.order.id}/reserve/",
+            data=json.dumps({"product_id": self.product.id, "quantity": 2}),
+            content_type="application/json",
+            HTTP_IDEMPOTENCY_KEY="request-3",
+        )
+
+        self.assertEqual(response.status_code, 201)
+        self.assertEqual(response.json()["reservation_id"], Reservation.objects.get().id)
+
+    def test_reserve_inventory_view_returns_conflict_for_insufficient_stock(self):
+        response = self.client.post(
+            f"/orders/{self.order.id}/reserve/",
+            data=json.dumps({"product_id": self.product.id, "quantity": 10}),
+            content_type="application/json",
+        )
+
+        self.assertEqual(response.status_code, 409)
+        self.assertEqual(response.json(), {"error": "not_enough_stock", "available": 5})
```

Verification command:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 manage.py test shop.orders
```

I attempted it in the fixture, but this sandbox cannot complete verification because `django` is not installed: `ModuleNotFoundError: No module named 'django'`.

---
> **관련 스킬 참조:**
> - 서비스 레이어와 트랜잭션 경계 → **implementation-django** 스킬