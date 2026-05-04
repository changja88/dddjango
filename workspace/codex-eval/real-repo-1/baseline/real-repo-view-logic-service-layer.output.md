아래는 적용 제안 diff입니다. `reserve_inventory` view는 JSON/body/header를 application input으로 변환하고, service 결과/예외를 HTTP 응답으로 변환하는 역할만 남깁니다.

```diff
diff --git a/shop/orders/services.py b/shop/orders/services.py
new file mode 100644
index 0000000..5e8a7e0
--- /dev/null
+++ b/shop/orders/services.py
@@ -0,0 +1,35 @@
+from dataclasses import dataclass
+
+from django.db import transaction
+
+from shop.orders.models import Order, Product, Reservation
+
+
+@dataclass(frozen=True)
+class InsufficientStock:
+    available: int
+
+
+class InsufficientStockError(Exception):
+    def __init__(self, available: int):
+        self.stock = InsufficientStock(available=available)
+        super().__init__("not enough stock")
+
+
+def reserve_inventory_for_order(
+    *,
+    order_id: int,
+    product_id: int,
+    quantity: int,
+    idempotency_key: str,
+) -> Reservation:
+    with transaction.atomic():
+        product = Product.objects.select_for_update().get(id=product_id)
+        order = Order.objects.select_for_update().get(id=order_id)
+
+        if product.stock_quantity < quantity:
+            raise InsufficientStockError(available=product.stock_quantity)
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
index 0d43c8b..a3a4d4f 100644
--- a/shop/orders/views.py
+++ b/shop/orders/views.py
@@ -1,10 +1,10 @@
 import json
 
-from django.db import transaction
 from django.http import JsonResponse
 from django.views.decorators.http import require_POST
 
-from shop.orders.models import Order, Product, Reservation
+from shop.orders.models import Order
+from shop.orders.services import InsufficientStockError, reserve_inventory_for_order
 
 
 @require_POST
@@ -24,24 +24,17 @@ def reserve_inventory(request, order_id):
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
+        reservation = reserve_inventory_for_order(
+            order_id=order_id,
+            product_id=product_id,
             quantity=quantity,
             idempotency_key=idempotency_key,
         )
+    except InsufficientStockError as exc:
+        return JsonResponse(
+            {"error": "not_enough_stock", "available": exc.stock.available},
+            status=409,
+        )
 
     return JsonResponse({"reservation_id": reservation.id}, status=201)
```

테스트는 실행하지 않았습니다. 현재 환경이 read-only라 fixture 파일을 수정하거나 테스트 DB/캐시 생성이 필요한 검증은 수행하지 않았습니다.