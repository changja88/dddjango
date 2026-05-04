아래는 fixture를 읽고 맞춘 unified diff입니다. 핵심은 DRF `ModelSerializer`/`APIView` 제거, Django Ninja `Schema`/`Router` 전환, `fields="__all__"` 제거입니다. 응답 필드는 `id`, `status`, `total_amount`, `created_at`만 명시해서 `customer_email`, `paid_at`, `cancelled_at`, `cancel_reason` 노출을 막습니다.

```diff
diff --git a/config/urls.py b/config/urls.py
index 74696ac..f8d8db6 100644
--- a/config/urls.py
+++ b/config/urls.py
@@ -1,9 +1,15 @@
 from django.urls import path
+from ninja import NinjaAPI
 
+from shop.orders.api_drf import router as orders_router
 from shop.orders import views
 
 
+api = NinjaAPI()
+api.add_router("/orders", orders_router)
+
+
 urlpatterns = [
+    path("api/", api.urls),
     path("orders/<int:order_id>/cancel/", views.cancel_order),
     path("orders/<int:order_id>/reserve/", views.reserve_inventory),
 ]
diff --git a/shop/orders/api_drf.py b/shop/orders/api_drf.py
index 9f0c2d0..27e9c44 100644
--- a/shop/orders/api_drf.py
+++ b/shop/orders/api_drf.py
@@ -1,17 +1,24 @@
-from rest_framework import serializers
-from rest_framework.response import Response
-from rest_framework.views import APIView
+from datetime import datetime
+from decimal import Decimal
+
+from django.shortcuts import get_object_or_404
+from ninja import Router, Schema
 
 from shop.orders.models import Order
 
 
-class OrderSerializer(serializers.ModelSerializer):
-    class Meta:
-        model = Order
-        fields = "__all__"
+router = Router(tags=["orders"])
+
+
+class OrderDetailSchema(Schema):
+    id: int
+    status: str
+    total_amount: Decimal
+    created_at: datetime
 
 
-class OrderDetailAPIView(APIView):
-    def get(self, request, order_id):
-        order = Order.objects.get(id=order_id)
-        return Response(OrderSerializer(order).data)
+@router.get("/{order_id}/", response=OrderDetailSchema)
+def get_order(request, order_id: int):
+    return get_object_or_404(
+        Order.objects.only("id", "status", "total_amount", "created_at"),
+        id=order_id,
+    )
```

참고: 파일명을 `api_drf.py` 그대로 둔 최소 diff입니다. 더 깔끔하게 하려면 후속 diff에서 `shop/orders/api.py`로 rename하고 `config/urls.py` import도 `shop.orders.api`로 바꾸는 게 좋습니다.