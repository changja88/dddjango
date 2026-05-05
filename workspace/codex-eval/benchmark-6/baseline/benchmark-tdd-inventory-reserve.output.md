지정하신 `/Users/hyun/Desktop/dddjango/none` 경로는 존재하지 않아 읽을 수 없었습니다. 대신 접근 가능한 fixture인 `/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop`의 파일들을 먼저 읽고, 읽기 전용 샌드박스 조건에 맞춰 적용용 unified diff로 작성했습니다.

```diff
diff --git a/shop/orders/tests.py b/shop/orders/tests.py
index 31dfb6f..2b9de22 100644
--- a/shop/orders/tests.py
+++ b/shop/orders/tests.py
@@ -1,16 +1,96 @@
-from django.test import TestCase
+import json
 
-from shop.orders.models import Order
+import pytest
 
+from shop.orders.models import Order, Product, Reservation
 
-class OrderModelTests(TestCase):
-    def test_cancel_sets_status(self):
-        order = Order.objects.create(
-            customer_email="buyer@example.com",
-            total_amount="100.00",
-        )
 
-        order.cancel(reason="customer request", actor_email="ops@example.com")
+pytestmark = pytest.mark.django_db
 
-        self.assertEqual(order.status, Order.STATUS_CANCELLED)
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
+        stock_quantity=10,
+        price="25.00",
+    )
+
+
+def test_cancel_sets_status(order):
+    order.cancel(reason="customer request", actor_email="ops@example.com")
+
+    assert order.status == Order.STATUS_CANCELLED
+
+
+def test_reserve_inventory_with_available_stock_creates_reservation(
+    client,
+    order,
+    product,
+):
+    response = client.post(
+        f"/orders/{order.id}/reserve/",
+        data=json.dumps({"product_id": product.id, "quantity": 3}),
+        content_type="application/json",
+        HTTP_IDEMPOTENCY_KEY="reserve-1",
+    )
+
+    assert response.status_code == 201
+    payload = response.json()
+    reservation = Reservation.objects.get(id=payload["reservation_id"])
+    product.refresh_from_db()
+
+    assert product.stock_quantity == 7
+    assert reservation.order == order
+    assert reservation.product == product
+    assert reservation.quantity == 3
+    assert reservation.idempotency_key == "reserve-1"
+
+
+def test_reserve_inventory_with_insufficient_stock_does_not_create_reservation(
+    client,
+    order,
+    product,
+):
+    response = client.post(
+        f"/orders/{order.id}/reserve/",
+        data=json.dumps({"product_id": product.id, "quantity": 11}),
+        content_type="application/json",
+        HTTP_IDEMPOTENCY_KEY="reserve-1",
+    )
+
+    product.refresh_from_db()
+
+    assert response.status_code == 409
+    assert response.json() == {"error": "not_enough_stock", "available": 10}
+    assert product.stock_quantity == 10
+    assert Reservation.objects.count() == 0
+
+
+def test_reserve_inventory_with_duplicate_key_returns_existing_reservation(
+    client,
+    order,
+    product,
+):
+    first_response = client.post(
+        f"/orders/{order.id}/reserve/",
+        data=json.dumps({"product_id": product.id, "quantity": 3}),
+        content_type="application/json",
+        HTTP_IDEMPOTENCY_KEY="reserve-1",
+    )
+    second_response = client.post(
+        f"/orders/{order.id}/reserve/",
+        data=json.dumps({"product_id": product.id, "quantity": 3}),
+        content_type="application/json",
+        HTTP_IDEMPOTENCY_KEY="reserve-1",
+    )
+
+    product.refresh_from_db()
+
+    assert first_response.status_code == 201
+    assert second_response.status_code == 200
+    assert second_response.json() == first_response.json()
+    assert product.stock_quantity == 7
+    assert Reservation.objects.count() == 1
diff --git a/shop/orders/services.py b/shop/orders/services.py
new file mode 100644
index 0000000..c59e1f4
--- /dev/null
+++ b/shop/orders/services.py
@@ -0,0 +1,70 @@
+from dataclasses import dataclass
+
+from django.db import transaction
+
+from shop.orders.models import Order, Product, Reservation
+
+
+class InsufficientStock(Exception):
+    def __init__(self, available: int) -> None:
+        self.available = available
+        super().__init__("not enough stock")
+
+
+class DuplicateReservation(Exception):
+    def __init__(self, reservation: Reservation) -> None:
+        self.reservation = reservation
+        super().__init__("idempotency key already used for another reservation")
+
+
+@dataclass(frozen=True)
+class ReservationResult:
+    reservation: Reservation
+    created: bool
+
+
+def reserve_inventory(
+    *,
+    order_id: int,
+    product_id: int,
+    quantity: int,
+    idempotency_key: str,
+) -> ReservationResult:
+    if quantity <= 0:
+        raise ValueError("quantity must be positive")
+
+    with transaction.atomic():
+        order = Order.objects.select_for_update().get(id=order_id)
+
+        if idempotency_key:
+            existing = (
+                Reservation.objects.select_for_update()
+                .filter(order=order, idempotency_key=idempotency_key)
+                .first()
+            )
+            if existing is not None:
+                if existing.product_id != product_id or existing.quantity != quantity:
+                    raise DuplicateReservation(existing)
+                return ReservationResult(reservation=existing, created=False)
+
+        product = Product.objects.select_for_update().get(id=product_id)
+        if product.stock_quantity < quantity:
+            raise InsufficientStock(available=product.stock_quantity)
+
+        product.stock_quantity -= quantity
+        product.save(update_fields=["stock_quantity"])
+        reservation = Reservation.objects.create(
+            product=product,
+            order=order,
+            quantity=quantity,
+            idempotency_key=idempotency_key,
+        )
+
+    return ReservationResult(reservation=reservation, created=True)
diff --git a/shop/orders/views.py b/shop/orders/views.py
index e653717..72cbad5 100644
--- a/shop/orders/views.py
+++ b/shop/orders/views.py
@@ -1,11 +1,14 @@
 import json
 
-from django.db import transaction
 from django.http import JsonResponse
 from django.views.decorators.http import require_POST
 
-from shop.orders.models import Order, Product, Reservation
+from shop.orders.models import Order
+from shop.orders.services import (
+    DuplicateReservation,
+    InsufficientStock,
+    reserve_inventory as reserve_inventory_service,
+)
 
 
 @require_POST
@@ -23,25 +26,26 @@ def reserve_inventory(request, order_id):
     product_id = payload["product_id"]
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
+        result = reserve_inventory_service(
+            order_id=order_id,
+            product_id=product_id,
+            quantity=quantity,
+            idempotency_key=idempotency_key,
         )
+    except InsufficientStock as exc:
+        return JsonResponse(
+            {"error": "not_enough_stock", "available": exc.available},
+            status=409,
+        )
+    except DuplicateReservation as exc:
+        return JsonResponse(
+            {
+                "error": "duplicate_reservation",
+                "reservation_id": exc.reservation.id,
+            },
+            status=409,
+        )
 
-    return JsonResponse({"reservation_id": reservation.id}, status=201)
+    status = 201 if result.created else 200
+    return JsonResponse({"reservation_id": result.reservation.id}, status=status)
```

테스트는 실행하지 못했습니다. 현재 세션이 읽기 전용이고 대상 fixture 경로도 직접 수정 가능한 위치로 제공되지 않았습니다.