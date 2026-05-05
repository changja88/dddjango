이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다. Fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, 현재 workspace도 비어 있어 `orders.Order` 모델이 이미 있다고 가정한 적용 diff입니다.

```diff
diff --git a/orders/schemas.py b/orders/schemas.py
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/orders/schemas.py
@@ -0,0 +1,34 @@
+from decimal import Decimal
+
+from ninja import ModelSchema, Schema
+
+from .models import Order
+
+
+class ProblemDetail(Schema):
+    type: str
+    title: str
+    status: int
+    detail: str
+    instance: str
+
+
+class OrderOut(ModelSchema):
+    class Meta:
+        model = Order
+        fields = ["id", "customer_id", "status", "total_amount", "created_at", "updated_at"]
+
+
+class OrderCreate(Schema):
+    customer_id: int
+    status: str
+    total_amount: Decimal
+
+
+class OrderUpdate(Schema):
+    customer_id: int
+    status: str
+    total_amount: Decimal
+
+
+class OrderPatch(Schema):
+    customer_id: int | None = None
+    status: str | None = None
+    total_amount: Decimal | None = None
diff --git a/orders/api.py b/orders/api.py
new file mode 100644
index 0000000..2222222
--- /dev/null
+++ b/orders/api.py
@@ -0,0 +1,62 @@
+from django.http import HttpRequest
+from django.shortcuts import get_object_or_404
+from ninja import Router
+from ninja.pagination import LimitOffsetPagination, paginate
+
+from .models import Order
+from .schemas import OrderCreate, OrderOut, OrderPatch, OrderUpdate, ProblemDetail
+
+router = Router(tags=["orders"])
+
+
+@router.get("", response=list[OrderOut])
+@paginate(LimitOffsetPagination)
+def list_orders(request: HttpRequest) -> list[Order]:
+    return list(Order.objects.order_by("-created_at"))
+
+
+@router.post("", response={201: OrderOut})
+def create_order(request: HttpRequest, payload: OrderCreate) -> tuple[int, Order]:
+    order = Order.objects.create(**payload.dict())
+    return 201, order
+
+
+@router.get("/{order_id}", response={200: OrderOut, 404: ProblemDetail})
+def get_order(request: HttpRequest, order_id: int) -> Order:
+    return get_object_or_404(Order, id=order_id)
+
+
+@router.put("/{order_id}", response={200: OrderOut, 404: ProblemDetail})
+def update_order(request: HttpRequest, order_id: int, payload: OrderUpdate) -> Order:
+    order = get_object_or_404(Order, id=order_id)
+    for field, value in payload.dict().items():
+        setattr(order, field, value)
+    order.save(update_fields=["customer_id", "status", "total_amount", "updated_at"])
+    return order
+
+
+@router.patch("/{order_id}", response={200: OrderOut, 404: ProblemDetail})
+def patch_order(request: HttpRequest, order_id: int, payload: OrderPatch) -> Order:
+    order = get_object_or_404(Order, id=order_id)
+    changed_fields = []
+    for field, value in payload.dict(exclude_unset=True).items():
+        setattr(order, field, value)
+        changed_fields.append(field)
+    if changed_fields:
+        order.save(update_fields=[*changed_fields, "updated_at"])
+    return order
+
+
+@router.delete("/{order_id}", response={204: None, 404: ProblemDetail})
+def delete_order(request: HttpRequest, order_id: int) -> tuple[int, None]:
+    order = get_object_or_404(Order, id=order_id)
+    order.delete()
+    return 204, None
diff --git a/config/api.py b/config/api.py
new file mode 100644
index 0000000..3333333
--- /dev/null
+++ b/config/api.py
@@ -0,0 +1,24 @@
+from django.http import Http404, HttpRequest, JsonResponse
+from ninja import NinjaAPI
+
+from orders.api import router as orders_router
+
+api = NinjaAPI()
+api.add_router("/orders", orders_router)
+
+
+@api.exception_handler(Http404)
+def handle_not_found(request: HttpRequest, exc: Http404) -> JsonResponse:
+    return JsonResponse(
+        {
+            "type": "about:blank",
+            "title": "Not Found",
+            "status": 404,
+            "detail": "Order not found.",
+            "instance": request.path,
+        },
+        status=404,
+        content_type="application/problem+json",
+    )
diff --git a/config/urls.py b/config/urls.py
new file mode 100644
index 0000000..4444444
--- /dev/null
+++ b/config/urls.py
@@ -0,0 +1,7 @@
+from django.contrib import admin
+from django.urls import path
+
+from .api import api
+
+urlpatterns = [
+    path("admin/", admin.site.urls),
+    path("api/", api.urls),
+]
```

검증은 read-only sandbox라 실행하지 못했습니다. 적용 후 확인 명령은 `python manage.py check`와 `pytest` 또는 `python manage.py test`입니다.

---
> **관련 스킬 참조:**
> - Django Ninja API 구현 → **implementation-django-ninja** 스킬