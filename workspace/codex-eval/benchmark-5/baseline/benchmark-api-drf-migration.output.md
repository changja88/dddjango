지정된 fixture path `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았습니다. 대신 fixture로 확인 가능한 [django-shop](/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/README.md)와 [Product 모델](/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/shop/orders/models.py)을 읽고, 읽기 전용 환경에 맞춰 문서 추가용 unified diff로 작성했습니다.

```diff
diff --git a/docs/product-api-drf-to-ninja-migration.md b/docs/product-api-drf-to-ninja-migration.md
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/docs/product-api-drf-to-ninja-migration.md
@@ -0,0 +1,134 @@
+# 상품 API DRF to Django Ninja 마이그레이션 가이드
+
+## 전제
+
+이 프로젝트의 API는 DRF `Serializer`/`ViewSet` 대신 Django Ninja `Schema`/`Router` 구조로 작성한다.
+fixture 기준 `Product` 모델은 `sku`, `name`, `is_active`, `stock_quantity`, `price`, `created_at` 필드를 가진다.
+
+## 책임 매핑
+
+| 기존 책임 | Ninja 전환 위치 |
+|---|---|
+| Serializer 응답 직렬화 | `ProductOut` Schema |
+| Serializer 입력 검증 | `ProductCreateIn`, `ProductUpdateIn` Schema |
+| ViewSet list/retrieve/create/update/delete | `Router`의 메서드별 함수 |
+| get_queryset/filter_queryset | selector 또는 query 함수 |
+| perform_create/perform_update | application service |
+| DRF router 등록 | `NinjaAPI.add_router()` |
+
+핵심은 API 함수가 HTTP 입출력만 담당하게 두는 것이다. 상품 생성, 수정, 재고 규칙 같은 변경 이유가 다른 로직은 service로 분리한다.
+
+## 권장 파일 구조
+
+```text
+shop/orders/
+  api/
+    products.py
+    product_schemas.py
+    product_services.py
+    product_selectors.py
+config/
+  api.py
+  urls.py
+```
+
+작은 fixture라면 `api/products.py` 하나에서 시작해도 된다. 다만 입력/응답 스키마와 쓰기 정책이 늘어나면 위처럼 분리한다.
+
+## Schema 작성
+
+응답 Schema는 `fields = "__all__"`처럼 전체 필드를 노출하지 말고 공개 계약을 명시한다.
+
+```python
+from decimal import Decimal
+from datetime import datetime
+
+from ninja import ModelSchema, Schema
+
+from shop.orders.models import Product
+
+
+class ProductOut(ModelSchema):
+    class Meta:
+        model = Product
+        fields = ["id", "sku", "name", "is_active", "stock_quantity", "price", "created_at"]
+
+
+class ProductCreateIn(Schema):
+    sku: str
+    name: str
+    stock_quantity: int = 0
+    price: Decimal
+
+
+class ProductUpdateIn(Schema):
+    name: str | None = None
+    is_active: bool | None = None
+    stock_quantity: int | None = None
+    price: Decimal | None = None
+
+
+class ProblemDetail(Schema):
+    type: str = "about:blank"
+    title: str
+    status: int
+    detail: str
+```
+
+## Selector와 Service
+
+목록/상세 조회는 selector에 둔다.
+
+```python
+from django.db.models import QuerySet
+from django.shortcuts import get_object_or_404
+
+from shop.orders.models import Product
+
+
+def list_products(*, active_only: bool = True) -> QuerySet[Product]:
+    queryset = Product.objects.order_by("-created_at", "-id")
+    if active_only:
+        queryset = queryset.filter(is_active=True)
+    return queryset
+
+
+def get_product(product_id: int) -> Product:
+    return get_object_or_404(Product, id=product_id)
+```
+
+쓰기 로직은 service에 둔다.
+
+```python
+from django.core.exceptions import ValidationError
+
+from shop.orders.models import Product
+from shop.orders.api.product_schemas import ProductCreateIn, ProductUpdateIn
+
+
+def create_product(payload: ProductCreateIn) -> Product:
+    product = Product(**payload.dict())
+    product.full_clean()
+    product.save()
+    return product
+
+
+def update_product(product: Product, payload: ProductUpdateIn) -> Product:
+    changes = payload.dict(exclude_unset=True)
+    for field, value in changes.items():
+        setattr(product, field, value)
+    product.full_clean()
+    product.save(update_fields=list(changes.keys()))
+    return product
+```
+
+## Router 전환 예시
+
+```python
+from typing import List
+
+from ninja import Query, Router
+from ninja.pagination import paginate
+
+from shop.orders.api.product_schemas import ProductCreateIn, ProductOut, ProductUpdateIn
+from shop.orders.api.product_selectors import get_product, list_products
+from shop.orders.api.product_services import create_product, update_product
+
+router = Router(tags=["products"])
+
+
+@router.get("", response=List[ProductOut])
+@paginate
+def product_list(request, active_only: bool = Query(True)):
+    return list_products(active_only=active_only)
+
+
+@router.get("/{product_id}", response=ProductOut)
+def product_detail(request, product_id: int):
+    return get_product(product_id)
+
+
+@router.post("", response={201: ProductOut})
+def product_create(request, payload: ProductCreateIn):
+    return 201, create_product(payload)
+
+
+@router.patch("/{product_id}", response=ProductOut)
+def product_update(request, product_id: int, payload: ProductUpdateIn):
+    product = get_product(product_id)
+    return update_product(product, payload)
+```
+
+## URL 연결
+
+```python
+# config/api.py
+from ninja import NinjaAPI
+
+from shop.orders.api.products import router as products_router
+
+api = NinjaAPI(title="Shop API")
+api.add_router("/products", products_router)
+```
+
+```python
+# config/urls.py
+from django.urls import path
+
+from config.api import api
+
+urlpatterns = [
+    path("api/", api.urls),
+]
+```
+
+## 전환 순서
+
+1. 기존 상품 API의 응답 필드와 요청 필드를 분리해 `ProductOut`, `ProductCreateIn`, `ProductUpdateIn`을 먼저 만든다.
+2. 기존 `get_queryset` 로직을 selector 함수로 옮긴다.
+3. 기존 `perform_create`, `perform_update`, 재고/가격 검증 로직을 service로 옮긴다.
+4. ViewSet action을 `@router.get/post/patch` 함수로 1:1 대응해 추가한다.
+5. `NinjaAPI.add_router("/products", products_router)`로 새 경로를 연결한다.
+6. 테스트를 새 Ninja 경로 기준으로 통과시킨 뒤 기존 DRF URL 연결과 `rest_framework` 의존성을 제거한다.
+
+## 회귀 테스트 전략
+
+- 목록: 활성 상품만 기본 노출되는지, 정렬과 페이지네이션이 유지되는지 확인한다.
+- 상세: 없는 상품 ID가 404를 반환하는지 확인한다.
+- 생성: `sku`, `price`, `stock_quantity` 검증 실패가 422 또는 팀 표준 오류 응답으로 내려오는지 확인한다.
+- 수정: partial update에서 전달한 필드만 바뀌는지 확인한다.
+- 계약: 기존 클라이언트가 쓰던 응답 필드명이 바뀌지 않았는지 스냅샷 또는 명시 assertion으로 검증한다.
+
+```bash
+python manage.py check
+pytest shop/orders/tests
+```
```

실제 파일은 수정하지 않았고, fixture에는 상품 DRF ViewSet 구현이 없어서 `Product` 모델 기준의 전환 문서로 정리했습니다.