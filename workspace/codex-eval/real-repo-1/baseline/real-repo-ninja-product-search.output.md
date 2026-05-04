아래 diff는 fixture를 직접 수정하지 않고, `shop/orders/models.py`의 `Product` 기준으로 Django Ninja Product 검색/목록 API를 추가하는 제안입니다. `FilterSchema`/`Query` 사용은 Django Ninja 공식 filtering 문서, validation handler는 공식 error handling 문서를 기준으로 맞췄습니다: https://django-ninja.dev/guides/input/filtering/ , https://django-ninja.dev/guides/errors/

```diff
diff --git a/config/urls.py b/config/urls.py
index 2b7db87..a898c70 100644
--- a/config/urls.py
+++ b/config/urls.py
@@ -1,9 +1,11 @@
 from django.urls import path
 
+from shop.orders.api_ninja import api
 from shop.orders import views
 
 
 urlpatterns = [
+    path("api/", api.urls),
     path("orders/<int:order_id>/cancel/", views.cancel_order),
     path("orders/<int:order_id>/reserve/", views.reserve_inventory),
 ]
diff --git a/shop/orders/api_ninja.py b/shop/orders/api_ninja.py
new file mode 100644
index 0000000..dd11826
--- /dev/null
+++ b/shop/orders/api_ninja.py
@@ -0,0 +1,119 @@
+import json
+from datetime import datetime
+from decimal import Decimal
+from typing import Annotated, Literal
+
+from django.db.models import Q, QuerySet
+from django.http import HttpRequest, HttpResponse
+from ninja import Field, FilterLookup, FilterSchema, NinjaAPI, Query, Schema
+from ninja.errors import ValidationError
+
+from shop.orders.models import Product
+
+
+ProductOrdering = Literal[
+    "created_at",
+    "-created_at",
+    "name",
+    "-name",
+    "price",
+    "-price",
+    "sku",
+    "-sku",
+]
+
+PRODUCT_ORDERING_ALLOW_LIST: dict[ProductOrdering, str] = {
+    "created_at": "created_at",
+    "-created_at": "-created_at",
+    "name": "name",
+    "-name": "-name",
+    "price": "price",
+    "-price": "-price",
+    "sku": "sku",
+    "-sku": "-sku",
+}
+
+
+class ProductFilter(FilterSchema):
+    q: Annotated[
+        str | None,
+        FilterLookup(["sku__icontains", "name__icontains"]),
+    ] = None
+    is_active: bool | None = None
+    in_stock: bool | None = None
+    min_price: Annotated[Decimal | None, FilterLookup("price__gte")] = None
+    max_price: Annotated[Decimal | None, FilterLookup("price__lte")] = None
+
+    def filter_in_stock(self, value: bool | None) -> Q:
+        if value is None:
+            return Q()
+        if value:
+            return Q(stock_quantity__gt=0)
+        return Q(stock_quantity=0)
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
+class ListMeta(Schema):
+    page: int
+    page_size: int
+    total: int
+
+
+class ProductListEnvelope(Schema):
+    items: list[ProductOut]
+    meta: ListMeta
+
+
+class ProblemDetail(Schema):
+    type: str
+    title: str
+    status: int
+    detail: str
+    errors: list[dict]
+
+
+api = NinjaAPI(title="Shop API", urls_namespace="shop-api")
+
+
+@api.exception_handler(ValidationError)
+def validation_errors(request: HttpRequest, exc: ValidationError) -> HttpResponse:
+    problem = {
+        "type": "https://example.com/problems/validation-error",
+        "title": "Validation failed",
+        "status": 422,
+        "detail": "One or more query parameters are invalid.",
+        "errors": getattr(exc, "errors", []),
+    }
+    return HttpResponse(
+        json.dumps(problem, default=str),
+        status=422,
+        content_type="application/problem+json",
+    )
+
+
+def serialize_product(product: Product) -> ProductOut:
+    return ProductOut(
+        id=product.id,
+        sku=product.sku,
+        name=product.name,
+        is_active=product.is_active,
+        stock_quantity=product.stock_quantity,
+        price=product.price,
+        created_at=product.created_at,
+    )
+
+
+@api.get("/products", response={200: ProductListEnvelope, 422: ProblemDetail})
+def list_products(
+    request: HttpRequest,
+    filters: Query[ProductFilter],
+    ordering: ProductOrdering = Query("-created_at"),
+    page: int = Query(1, ge=1),
+    page_size: int = Query(20, ge=1, le=100),
+) -> ProductListEnvelope:
+    queryset: QuerySet[Product] = filters.filter(Product.objects.all())
+    queryset = queryset.order_by(PRODUCT_ORDERING_ALLOW_LIST[ordering], "id")
+
+    total = queryset.count()
+    offset = (page - 1) * page_size
+    products = queryset[offset : offset + page_size]
+
+    return ProductListEnvelope(
+        items=[serialize_product(product) for product in products],
+        meta=ListMeta(page=page, page_size=page_size, total=total),
+    )
diff --git a/shop/orders/tests.py b/shop/orders/tests.py
index 67e94d1..a1848c2 100644
--- a/shop/orders/tests.py
+++ b/shop/orders/tests.py
@@ -1,6 +1,6 @@
 from django.test import TestCase
 
-from shop.orders.models import Order
+from shop.orders.models import Order, Product
 
 
 class OrderModelTests(TestCase):
@@ -14,3 +14,52 @@ class OrderModelTests(TestCase):
         order.cancel(reason="customer request", actor_email="ops@example.com")
 
         self.assertEqual(order.status, Order.STATUS_CANCELLED)
+
+
+class ProductListAPITests(TestCase):
+    def test_lists_products_with_filter_sort_and_envelope(self):
+        Product.objects.create(
+            sku="MUG-001",
+            name="Coffee Mug",
+            is_active=True,
+            stock_quantity=5,
+            price="12.00",
+        )
+        Product.objects.create(
+            sku="TEE-001",
+            name="T-Shirt",
+            is_active=True,
+            stock_quantity=0,
+            price="20.00",
+        )
+        Product.objects.create(
+            sku="MUG-002",
+            name="Archived Mug",
+            is_active=False,
+            stock_quantity=10,
+            price="10.00",
+        )
+
+        response = self.client.get(
+            "/api/products",
+            {
+                "q": "mug",
+                "is_active": "true",
+                "in_stock": "true",
+                "ordering": "price",
+                "page": "1",
+                "page_size": "10",
+            },
+        )
+
+        self.assertEqual(response.status_code, 200)
+        payload = response.json()
+        self.assertEqual(payload["meta"], {"page": 1, "page_size": 10, "total": 1})
+        self.assertEqual(len(payload["items"]), 1)
+        self.assertEqual(payload["items"][0]["sku"], "MUG-001")
+
+    def test_validation_errors_use_problem_json(self):
+        response = self.client.get(
+            "/api/products",
+            {"ordering": "status", "page": "0"},
+        )
+
+        self.assertEqual(response.status_code, 422)
+        self.assertTrue(response["Content-Type"].startswith("application/problem+json"))
+        self.assertEqual(response.json()["status"], 422)
+        self.assertEqual(response.json()["title"], "Validation failed")
```