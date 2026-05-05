이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다. 지정 fixture `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, 현재 workspace도 비어 있어 실제 파일을 수정하거나 테스트하지 못했습니다. 아래 diff는 `orders.Order` 모델이 이미 있고 필드가 `id/status/total_price/created_at/updated_at`라고 가정한 Django Ninja 대안입니다.

```diff
diff --git a/config/api.py b/config/api.py
new file mode 100644
--- /dev/null
+++ b/config/api.py
@@ -0,0 +1,35 @@
+from django.http import Http404, HttpRequest, JsonResponse
+from ninja import NinjaAPI, Schema
+from ninja.errors import HttpError
+
+from orders.api import router as orders_router
+
+
+class ProblemDetail(Schema):
+    type: str = "about:blank"
+    title: str
+    status: int
+    detail: str
+    instance: str
+
+
+api = NinjaAPI(version="1.0.0")
+
+
+def problem_response(
+    request: HttpRequest,
+    status: int,
+    title: str,
+    detail: str,
+) -> JsonResponse:
+    return JsonResponse(
+        ProblemDetail(title=title, status=status, detail=detail, instance=request.path).dict(),
+        status=status,
+        content_type="application/problem+json",
+    )
+
+
+@api.exception_handler(Http404)
+def handle_not_found(request: HttpRequest, exc: Http404) -> JsonResponse:
+    return problem_response(request, 404, "Not Found", str(exc) or "Resource not found.")
+
+
+@api.exception_handler(HttpError)
+def handle_http_error(request: HttpRequest, exc: HttpError) -> JsonResponse:
+    return problem_response(request, exc.status_code, str(exc), str(exc))
+
+
+api.add_router("/orders", orders_router, tags=["orders"])
diff --git a/config/urls.py b/config/urls.py
new file mode 100644
--- /dev/null
+++ b/config/urls.py
@@ -0,0 +1,8 @@
+from django.contrib import admin
+from django.urls import path
+
+from config.api import api
+
+urlpatterns = [
+    path("admin/", admin.site.urls),
+    path("api/", api.urls),
+]
diff --git a/orders/schemas.py b/orders/schemas.py
new file mode 100644
--- /dev/null
+++ b/orders/schemas.py
@@ -0,0 +1,33 @@
+from decimal import Decimal
+
+from ninja import ModelSchema, Schema
+
+from orders.models import Order
+
+
+class OrderOutSchema(ModelSchema):
+    class Meta:
+        model = Order
+        fields = ["id", "status", "total_price", "created_at", "updated_at"]
+
+
+class OrderCreateSchema(Schema):
+    status: str
+    total_price: Decimal
+
+
+class OrderUpdateSchema(Schema):
+    status: str | None = None
+    total_price: Decimal | None = None
diff --git a/orders/api.py b/orders/api.py
new file mode 100644
--- /dev/null
+++ b/orders/api.py
@@ -0,0 +1,56 @@
+from django.db.models import QuerySet
+from django.http import HttpRequest
+from django.shortcuts import get_object_or_404
+from ninja import Router
+from ninja.pagination import LimitOffsetPagination, paginate
+
+from orders.models import Order
+from orders.schemas import OrderCreateSchema, OrderOutSchema, OrderUpdateSchema
+
+
+router = Router()
+
+
+@router.get("", response=list[OrderOutSchema])
+@paginate(LimitOffsetPagination)
+def list_orders(request: HttpRequest) -> QuerySet[Order]:
+    return Order.objects.order_by("-created_at", "-id")
+
+
+@router.get("/{order_id}", response=OrderOutSchema)
+def get_order(request: HttpRequest, order_id: int) -> Order:
+    return get_object_or_404(Order, id=order_id)
+
+
+@router.post("", response={201: OrderOutSchema})
+def create_order(request: HttpRequest, payload: OrderCreateSchema) -> tuple[int, Order]:
+    order = Order.objects.create(
+        status=payload.status,
+        total_price=payload.total_price,
+    )
+    return 201, order
+
+
+@router.patch("/{order_id}", response=OrderOutSchema)
+def update_order(
+    request: HttpRequest,
+    order_id: int,
+    payload: OrderUpdateSchema,
+) -> Order:
+    order = get_object_or_404(Order, id=order_id)
+    update_data = payload.dict(exclude_unset=True)
+
+    for field, value in update_data.items():
+        setattr(order, field, value)
+
+    if update_data:
+        order.save(update_fields=[*update_data.keys(), "updated_at"])
+
+    return order
+
+
+@router.delete("/{order_id}", response={204: None})
+def delete_order(request: HttpRequest, order_id: int) -> tuple[int, None]:
+    order = get_object_or_404(Order, id=order_id)
+    order.delete()
+    return 204, None
```

검증은 read-only sandbox와 빈 fixture 때문에 실행하지 못했습니다. 적용 후 실행할 명령은 다음입니다.

```bash
python manage.py check
python manage.py test
```

---
> **관련 스킬 참조:**
> - Django Ninja API 구현 → **implementation-django-ninja** 스킬