**주요 내용**

Fixture 기준 제안 diff입니다. Django Ninja `Router/Schema`만 사용하고, `FilterSchema + Query`, 정렬 allow-list, `items/meta` envelope, `HttpRequest`, 명시 return type, `application/problem+json` 검증을 포함했습니다.

```diff
diff --git a/config/api.py b/config/api.py
new file mode 100644
index 0000000..1f6e5b8
--- /dev/null
+++ b/config/api.py
@@ -0,0 +1,32 @@
+from django.http import HttpRequest, JsonResponse
+from ninja import NinjaAPI, Schema
+from ninja.errors import ValidationError
+
+from shop.orders.api import router as products_router
+
+
+api = NinjaAPI(title="Shop API", version="1.0.0")
+api.add_router("/products/", products_router)
+
+
+class ProblemDetail(Schema):
+    type: str
+    title: str
+    status: int
+    detail: str
+    instance: str
+    errors: list[dict]
+
+
+@api.exception_handler(ValidationError)
+def validation_error_handler(
+    request: HttpRequest,
+    exc: ValidationError,
+) -> JsonResponse:
+    return JsonResponse(
+        ProblemDetail(
+            type="https://example.com/problems/validation-error",
+            title="Validation Error",
+            status=422,
+            detail="Request parameters failed validation.",
+            instance=request.path,
+            errors=exc.errors,
+        ).dict(),
+        status=422,
+        content_type="application/problem+json",
+    )
diff --git a/config/urls.py b/config/urls.py
index 1b614d6..f3a8b23 100644
--- a/config/urls.py
+++ b/config/urls.py
@@ -1,9 +1,11 @@
 from django.urls import path
 
+from config.api import api
 from shop.orders import views
 
 
 urlpatterns = [
+    path("api/", api.urls),
     path("orders/<int:order_id>/cancel/", views.cancel_order),
     path("orders/<int:order_id>/reserve/", views.reserve_inventory),
 ]
diff --git a/shop/orders/api.py b/shop/orders/api.py
new file mode 100644
index 0000000..a2c88f0
--- /dev/null
+++ b/shop/orders/api.py
@@ -0,0 +1,76 @@
+from datetime import datetime
+from decimal import Decimal
+from typing import Annotated, Literal
+
+from django.db.models import Q
+from django.http import HttpRequest
+from ninja import Field, FilterLookup, FilterSchema, Query, Router, Schema
+
+from shop.orders.models import Product
+
+
+router = Router(tags=["products"])
+
+ProductSort = Literal[
+    "created_at",
+    "-created_at",
+    "price",
+    "-price",
+    "name",
+    "-name",
+    "sku",
+    "-sku",
+]
+
+SORT_ORDERING = {
+    "created_at": "created_at",
+    "-created_at": "-created_at",
+    "price": "price",
+    "-price": "-price",
+    "name": "name",
+    "-name": "-name",
+    "sku": "sku",
+    "-sku": "-sku",
+}
+
+
+class ProductFilterSchema(FilterSchema):
+    search: Annotated[
+        str | None,
+        FilterLookup(["sku__icontains", "name__icontains"]),
+    ] = None
+    is_active: bool | None = None
+    min_price: Annotated[Decimal | None, FilterLookup("price__gte")] = None
+    max_price: Annotated[Decimal | None, FilterLookup("price__lte")] = None
+    in_stock: bool | None = None
+
+    def filter_in_stock(self, value: bool) -> Q:
+        if value:
+            return Q(stock_quantity__gt=0)
+        return Q(stock_quantity=0)
+
+
+class ProductListQuery(Schema):
+    limit: int = Field(20, ge=1, le=100)
+    offset: int = Field(0, ge=0)
+    sort: ProductSort = "-created_at"
+
+
+class ProductOut(Schema):
+    id: int
+    sku: str
+    name: str
+    is_active: bool
+    stock_quantity: int
+    price: Decimal
+    created_at: datetime
+
+
+class ProductListMeta(Schema):
+    limit: int
+    offset: int
+    total: int
+    sort: ProductSort
+
+
+class ProductListEnvelope(Schema):
+    items: list[ProductOut]
+    meta: ProductListMeta
+
+
+@router.get("", response=ProductListEnvelope)
+def list_products(
+    request: HttpRequest,
+    filters: Query[ProductFilterSchema],
+    pagination: Query[ProductListQuery],
+) -> ProductListEnvelope:
+    queryset = filters.filter(Product.objects.all())
+    queryset = queryset.order_by(SORT_ORDERING[pagination.sort], "id")
+    total = queryset.count()
+    items = list(queryset[pagination.offset : pagination.offset + pagination.limit])
+    return {
+        "items": items,
+        "meta": {
+            "limit": pagination.limit,
+            "offset": pagination.offset,
+            "total": total,
+            "sort": pagination.sort,
+        },
+    }
diff --git a/shop/orders/tests.py b/shop/orders/tests.py
index 3460b38..585a0cf 100644
--- a/shop/orders/tests.py
+++ b/shop/orders/tests.py
@@ -1,6 +1,6 @@
 from django.test import TestCase
 
-from shop.orders.models import Order
+from shop.orders.models import Order, Product
 
 
 class OrderModelTests(TestCase):
@@ -14,3 +14,34 @@ class OrderModelTests(TestCase):
         order.cancel(reason="customer request", actor_email="ops@example.com")
 
         self.assertEqual(order.status, Order.STATUS_CANCELLED)
+
+
+class ProductListApiTests(TestCase):
+    def test_list_products_filters_sorts_and_wraps_response(self):
+        Product.objects.create(
+            sku="HAT-001",
+            name="Wool Hat",
+            is_active=True,
+            stock_quantity=3,
+            price="19.00",
+        )
+        Product.objects.create(
+            sku="MUG-001",
+            name="Coffee Mug",
+            is_active=True,
+            stock_quantity=0,
+            price="9.00",
+        )
+
+        response = self.client.get(
+            "/api/products/",
+            {"search": "hat", "in_stock": "true", "sort": "price"},
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertEqual(response.json()["items"][0]["sku"], "HAT-001")
+        self.assertEqual(response.json()["meta"]["total"], 1)
+
+    def test_invalid_query_returns_problem_json(self):
+        response = self.client.get("/api/products/", {"limit": "0"})
+
+        self.assertEqual(response.status_code, 422)
+        self.assertEqual(response["Content-Type"], "application/problem+json")
+        self.assertEqual(response.json()["status"], 422)
```

검증은 read-only sandbox라 실행하지 않았습니다. 적용 후 fixture 루트에서 실행하세요:

```bash
python manage.py check
python manage.py test
```

---
> **관련 스킬 참조:**
> - Django Ninja API 구현 → **implementation-django-ninja** 스킬