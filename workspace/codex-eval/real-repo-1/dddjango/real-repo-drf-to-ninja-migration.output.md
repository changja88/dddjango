이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다. 읽기 전용 환경이라 파일은 수정하지 않았고, 아래 unified diff를 제안합니다.

```diff
diff --git a/shop/orders/api_drf.py b/shop/orders/api_drf.py
index 7d7c2a1..8a4b2c9 100644
--- a/shop/orders/api_drf.py
+++ b/shop/orders/api_drf.py
@@ -1,17 +1,35 @@
-from rest_framework import serializers
-from rest_framework.response import Response
-from rest_framework.views import APIView
+from datetime import datetime
+from decimal import Decimal
+
+from django.http import HttpRequest
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
+    paid_at: datetime | None
+    created_at: datetime
 
 
-class OrderDetailAPIView(APIView):
-    def get(self, request, order_id):
-        order = Order.objects.get(id=order_id)
-        return Response(OrderSerializer(order).data)
+@router.get("/{order_id}", response=OrderDetailSchema)
+def get_order(request: HttpRequest, order_id: int) -> OrderDetailSchema:
+    order = get_object_or_404(Order, id=order_id)
+    return OrderDetailSchema(
+        id=order.id,
+        status=order.status,
+        total_amount=order.total_amount,
+        paid_at=order.paid_at,
+        created_at=order.created_at,
+    )
```

핵심 변경점:
- `rest_framework`, `ModelSerializer`, `APIView`, `Response`를 제거했습니다.
- Django Ninja `Router`와 `Schema`로 전환했습니다.
- `fields = "__all__"`를 없애고 응답 필드를 명시했습니다.
- `customer_email`, `cancel_reason`, `cancelled_at`처럼 노출 위험이 있는 필드는 응답에서 제외했습니다.
- sync endpoint에 `request: HttpRequest`와 명시적 반환 타입 `-> OrderDetailSchema`를 추가했습니다.

검증은 읽기 전용이라 실행하지 않았습니다. 적용 후에는 fixture 루트에서 아래를 확인하면 됩니다.

```bash
python manage.py check
python manage.py test
```

---
> **관련 스킬 참조:**
> - Django Ninja API 구현/검증 → **implementation-django-ninja** 스킬