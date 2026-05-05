지정된 `/Users/hyun/Desktop/dddjango/none` 경로는 없어서 읽을 수 없었습니다. 대신 확인 가능한 fixture인 `/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop`의 파일들을 읽고, 읽기 전용 환경에 맞춰 적용용 unified diff로 작성했습니다.

```diff
diff --git a/shop/orders/test_inventory_reservation.py b/shop/orders/test_inventory_reservation.py
new file mode 100644
index 0000000..31c3d2a
--- /dev/null
+++ b/shop/orders/test_inventory_reservation.py
@@ -0,0 +1,85 @@
+import pytest
+
+from shop.orders.models import Order, Product, Reservation
+from shop.orders.services import InsufficientStock, reserve_inventory
+
+
+pytestmark = pytest.mark.django_db
+
+
+@pytest.fixture
+def order():
+    return Order.objects.create(
+        customer_email="buyer@example.com",
+        total_amount="100.00",
+    )
+
+
+@pytest.fixture
+def product():
+    return Product.objects.create(
+        sku="SKU-001",
+        name="Test product",
+        stock_quantity=5,
+        price="10.00",
+    )
+
+
+def test_reserve_inventory_creates_reservation_and_decreases_stock(order, product):
+    reservation = reserve_inventory(
+        order_id=order.id,
+        product_id=product.id,
+        quantity=3,
+        idempotency_key="reserve-1",
+    )
+
+    product.refresh_from_db()
+
+    assert reservation.order == order
+    assert reservation.product == product
+    assert reservation.quantity == 3
+    assert reservation.idempotency_key == "reserve-1"
+    assert product.stock_quantity == 2
+
+
+def test_reserve_inventory_rejects_when_stock_is_not_enough(order, product):
+    product.stock_quantity = 2
+    product.save(update_fields=["stock_quantity"])
+
+    with pytest.raises(InsufficientStock) as error:
+        reserve_inventory(
+            order_id=order.id,
+            product_id=product.id,
+            quantity=3,
+            idempotency_key="reserve-1",
+        )
+
+    product.refresh_from_db()
+
+    assert error.value.available == 2
+    assert product.stock_quantity == 2
+    assert Reservation.objects.count() == 0
+
+
+def test_reserve_inventory_is_idempotent_for_duplicate_reservation(order, product):
+    first_reservation = reserve_inventory(
+        order_id=order.id,
+        product_id=product.id,
+        quantity=3,
+        idempotency_key="reserve-1",
+    )
+
+    duplicate_reservation = reserve_inventory(
+        order_id=order.id,
+        product_id=product.id,
+        quantity=3,
+        idempotency_key="reserve-1",
+    )
+
+    product.refresh_from_db()
+
+    assert duplicate_reservation.id == first_reservation.id
+    assert product.stock_quantity == 2
+    assert Reservation.objects.count() == 1
diff --git a/shop/orders/models.py b/shop/orders/models.py
index 3b8f3d7..af73b61 100644
--- a/shop/orders/models.py
+++ b/shop/orders/models.py
@@ -44,3 +44,10 @@ class Reservation(models.Model):
     quantity = models.PositiveIntegerField()
     idempotency_key = models.CharField(max_length=128)
     created_at = models.DateTimeField(auto_now_add=True)
+
+    class Meta:
+        constraints = [
+            models.UniqueConstraint(
+                fields=["product", "order", "idempotency_key"],
+                name="unique_reservation_idempotency_key_per_order_product",
+            )
+        ]
diff --git a/shop/orders/services.py b/shop/orders/services.py
new file mode 100644
index 0000000..a7d66bb
--- /dev/null
+++ b/shop/orders/services.py
@@ -0,0 +1,50 @@
+from django.db import transaction
+
+from shop.orders.models import Order, Product, Reservation
+
+
+class InsufficientStock(Exception):
+    def __init__(self, available: int):
+        self.available = available
+        super().__init__("not enough stock")
+
+
+def reserve_inventory(
+    *,
+    order_id: int,
+    product_id: int,
+    quantity: int,
+    idempotency_key: str,
+) -> Reservation:
+    if quantity <= 0:
+        raise ValueError("quantity must be positive")
+
+    with transaction.atomic():
+        product = Product.objects.select_for_update().get(id=product_id)
+        order = Order.objects.select_for_update().get(id=order_id)
+
+        existing_reservation = (
+            Reservation.objects.select_for_update()
+            .filter(
+                product=product,
+                order=order,
+                idempotency_key=idempotency_key,
+            )
+            .first()
+        )
+        if existing_reservation is not None:
+            return existing_reservation
+
+        if product.stock_quantity < quantity:
+            raise InsufficientStock(available=product.stock_quantity)
+
+        product.stock_quantity -= quantity
+        product.save(update_fields=["stock_quantity"])
+
+        return Reservation.objects.create(
+            product=product,
+            order=order,
+            quantity=quantity,
+            idempotency_key=idempotency_key,
+        )
diff --git a/shop/orders/views.py b/shop/orders/views.py
index b8f9222..d672bd1 100644
--- a/shop/orders/views.py
+++ b/shop/orders/views.py
@@ -1,10 +1,10 @@
 import json
 
-from django.db import transaction
 from django.http import JsonResponse
 from django.views.decorators.http import require_POST
 
-from shop.orders.models import Order, Product, Reservation
+from shop.orders.models import Order
+from shop.orders.services import InsufficientStock, reserve_inventory as reserve_order_inventory
 
 
 @require_POST
@@ -25,23 +25,18 @@ def reserve_inventory(request, order_id):
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
-            quantity=quantity,
-            idempotency_key=idempotency_key,
+    try:
+        reservation = reserve_order_inventory(
+            order_id=order_id,
+            product_id=product_id,
+            quantity=quantity,
+            idempotency_key=idempotency_key,
+        )
+    except InsufficientStock as error:
+        return JsonResponse(
+            {"error": "not_enough_stock", "available": error.available},
+            status=409,
         )
 
     return JsonResponse({"reservation_id": reservation.id}, status=201)
```

검증은 실행하지 못했습니다. 현재 샌드박스가 read-only라 테스트 파일을 실제로 추가해 `pytest`를 돌릴 수 없습니다.