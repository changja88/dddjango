fixture를 확인했습니다. 지정 경로 `/Users/hyun/Desktop/dddjango/none`는 없고, 실제 fixture는 `/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop`였습니다. 현재 fixture에는 `Product` 모델은 있지만 DRF `ProductSerializer/ViewSet`은 없고, DRF 예시는 [api_drf.py](/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/shop/orders/api_drf.py:1)의 `OrderSerializer/APIView` 형태입니다. 아래는 그 전제를 명시한 상품 API 마이그레이션 가이드 문서 추가용 unified diff입니다.

```diff
diff --git a/docs/drf-to-ninja-product-api-migration.md b/docs/drf-to-ninja-product-api-migration.md
new file mode 100644
index 0000000..a3a1c6f
--- /dev/null
+++ b/docs/drf-to-ninja-product-api-migration.md
@@ -0,0 +1,148 @@
+# DRF Serializer/ViewSet 상품 API를 Django Ninja Schema/Router로 마이그레이션하기
+
+이 가이드는 기존 DRF `Serializer` / `ViewSet` 기반 상품 API를 Django Ninja의
+`Schema` / `Router` 구조로 옮길 때의 기준 절차를 설명한다.
+
+현재 fixture에는 `Product` 모델은 존재하지만 DRF `ProductViewSet` 구현은 포함되어
+있지 않다. 대신 `shop/orders/api_drf.py`에 DRF `ModelSerializer`와 `APIView`
+예시가 있다. 아래 예시는 일반적인 DRF 상품 API가 있었다고 가정하고, fixture의
+`Product` 모델 구조에 맞춰 작성한다.
+
+## 1. 목표 구조
+
+DRF에서는 보통 다음 구조를 사용한다.
+
+```python
+from rest_framework import serializers, viewsets
+
+from shop.orders.models import Product
+
+
+class ProductSerializer(serializers.ModelSerializer):
+    class Meta:
+        model = Product
+        fields = "__all__"
+
+
+class ProductViewSet(viewsets.ModelViewSet):
+    queryset = Product.objects.all()
+    serializer_class = ProductSerializer
+```
+
+Django Ninja에서는 이를 다음 책임으로 나눈다.
+
+- `Schema`: 요청과 응답 데이터 모양을 명시한다.
+- `Router`: HTTP endpoint와 application 흐름을 연결한다.
+- `urls.py`: `NinjaAPI`에 router를 등록한다.
+
+## 2. 패키지 의존성 교체
+
+DRF를 완전히 제거할 수 있다면 다음 의존성을 제거한다.
+
+```python
+# settings.py
+INSTALLED_APPS = [
+    "django.contrib.auth",
+    "django.contrib.contenttypes",
+    "shop.orders",
+]
+```
+
+그리고 Django Ninja를 설치한다.
+
+```bash
+pip install django-ninja
+```
+
+`django-ninja`는 Django app으로 `INSTALLED_APPS`에 추가하지 않아도 기본적인 API
+구성에 사용할 수 있다.
+
+## 3. Schema 작성
+
+`shop/orders/api_ninja.py`를 만들고 상품 API에 필요한 schema를 먼저 정의한다.
+DRF의 `fields = "__all__"`처럼 모델 필드를 암묵적으로 노출하기보다, 외부 계약으로
+공개할 필드를 명시하는 편이 안전하다.
+
+```python
+from datetime import datetime
+from decimal import Decimal
+from typing import Optional
+
+from ninja import Router, Schema
+
+from shop.orders.models import Product
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
+class ProductCreateIn(Schema):
+    sku: str
+    name: str
+    is_active: bool = True
+    stock_quantity: int = 0
+    price: Decimal
+
+
+class ProductUpdateIn(Schema):
+    sku: Optional[str] = None
+    name: Optional[str] = None
+    is_active: Optional[bool] = None
+    stock_quantity: Optional[int] = None
+    price: Optional[Decimal] = None
+```
+
+## 4. Router 작성
+
+DRF `ModelViewSet`의 기본 동작은 Ninja에서 명시적인 route 함수로 옮긴다.
+각 endpoint가 어떤 입력을 받고 어떤 응답을 반환하는지 드러나므로, 이후 비즈니스
+규칙을 서비스나 모델 메서드로 분리하기도 쉽다.
+
+```python
+from django.shortcuts import get_object_or_404
+from ninja import Router
+
+from shop.orders.models import Product
+
+
+router = Router(tags=["products"])
+
+
+@router.get("/products", response=list[ProductOut])
+def list_products(request):
+    return Product.objects.order_by("id")
+
+
+@router.get("/products/{product_id}", response=ProductOut)
+def get_product(request, product_id: int):
+    return get_object_or_404(Product, id=product_id)
+
+
+@router.post("/products", response={201: ProductOut})
+def create_product(request, payload: ProductCreateIn):
+    product = Product.objects.create(**payload.dict())
+    return 201, product
+
+
+@router.patch("/products/{product_id}", response=ProductOut)
+def update_product(request, product_id: int, payload: ProductUpdateIn):
+    product = get_object_or_404(Product, id=product_id)
+    update_data = payload.dict(exclude_unset=True)
+
+    for field, value in update_data.items():
+        setattr(product, field, value)
+
+    if update_data:
+        product.save(update_fields=list(update_data.keys()))
+
+    return product
+
+
+@router.delete("/products/{product_id}", response={204: None})
+def delete_product(request, product_id: int):
+    product = get_object_or_404(Product, id=product_id)
+    product.delete()
+    return 204, None
+```
+
+## 5. URL 연결
+
+기존 Django URL에 `NinjaAPI`를 추가하고 router를 등록한다.
+
+```python
+from django.urls import path
+from ninja import NinjaAPI
+
+from shop.orders import views
+from shop.orders.api_ninja import router as product_router
+
+
+api = NinjaAPI()
+api.add_router("", product_router)
+
+
+urlpatterns = [
+    path("api/", api.urls),
+    path("orders/<int:order_id>/cancel/", views.cancel_order),
+    path("orders/<int:order_id>/reserve/", views.reserve_inventory),
+]
+```
+
+위 설정을 기준으로 상품 API 경로는 다음과 같다.
+
+- `GET /api/products`
+- `GET /api/products/{product_id}`
+- `POST /api/products`
+- `PATCH /api/products/{product_id}`
+- `DELETE /api/products/{product_id}`
+
+## 6. DRF 코드 제거 기준
+
+Ninja endpoint가 기존 API와 동일한 응답 계약을 제공하고 테스트가 통과하면 다음
+항목을 제거한다.
+
+- `rest_framework` import
+- `ProductSerializer`
+- `ProductViewSet`
+- DRF router 등록 코드
+- `INSTALLED_APPS`의 `rest_framework`, 프로젝트에서 더 이상 쓰지 않는 경우
+
+fixture의 `shop/orders/api_drf.py`처럼 DRF 코드가 주문 API와 섞여 있다면, 상품 API
+마이그레이션과 주문 API 마이그레이션을 분리해서 진행한다. 서로 다른 endpoint의
+응답 계약을 한 번에 바꾸면 회귀 범위가 커진다.
+
+## 7. 테스트 기준
+
+마이그레이션 후 최소한 다음 동작을 검증한다.
+
+- 상품 목록 조회가 생성 순서 또는 명시한 정렬 기준대로 반환된다.
+- 상품 상세 조회가 존재하지 않는 id에 대해 404를 반환한다.
+- 상품 생성 시 `sku`, `name`, `price`가 저장된다.
+- 부분 수정 시 전달한 필드만 변경된다.
+- 삭제 후 상세 조회가 404를 반환한다.
+
+예시:
+
+```python
+import pytest
+from ninja.testing import TestClient
+
+from shop.orders.api_ninja import router
+from shop.orders.models import Product
+
+
+pytestmark = pytest.mark.django_db
+
+
+def test_create_product():
+    client = TestClient(router)
+
+    response = client.post(
+        "/products",
+        json={
+            "sku": "SKU-001",
+            "name": "Keyboard",
+            "price": "120.00",
+            "stock_quantity": 10,
+        },
+    )
+
+    assert response.status_code == 201
+    assert Product.objects.get(sku="SKU-001").name == "Keyboard"
+```
+
+## 8. 마이그레이션 순서
+
+1. 기존 DRF 상품 API의 URL, 요청 필드, 응답 필드, status code를 기록한다.
+2. `ProductOut`, `ProductCreateIn`, `ProductUpdateIn` schema를 만든다.
+3. `api_ninja.py`에 router와 route 함수를 추가한다.
+4. `config/urls.py`에 `NinjaAPI`를 연결한다.
+5. 기존 DRF API와 같은 동작을 검증하는 테스트를 추가한다.
+6. 클라이언트 전환이 끝난 뒤 DRF serializer, viewset, router 등록을 제거한다.
+
+마이그레이션 중에는 `fields = "__all__"`를 그대로 옮기기보다 외부에 공개할 필드를
+명시한다. 모델 필드는 내부 저장 구조이고, schema는 API 계약이므로 변경 이유가
+다르다.
```

테스트는 실행하지 않았습니다. 이번 작업은 read-only 조건에서 fixture를 읽고 문서용 diff를 작성하는 범위였습니다.