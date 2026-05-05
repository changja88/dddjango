이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다. 워크스페이스가 읽기 전용이고 파일 목록이 비어 있어 실제 적용은 못 했습니다. 아래는 `products.Product` 모델이 `name`, `description`, `price`, `is_active`, `created_at`, `updated_at` 필드를 가진다는 가정의 패치입니다.

```diff
*** Add File: products/api/schemas.py
+from decimal import Decimal
+
+from ninja import ModelSchema, Schema
+
+from products.models import Product
+
+
+class ProductOut(ModelSchema):
+    class Meta:
+        model = Product
+        fields = ["id", "name", "description", "price", "is_active", "created_at", "updated_at"]
+
+
+class ProductCreateIn(Schema):
+    name: str
+    description: str = ""
+    price: Decimal
+    is_active: bool = True
+
+
+class ProductUpdateIn(Schema):
+    name: str | None = None
+    description: str | None = None
+    price: Decimal | None = None
+    is_active: bool | None = None
*** Add File: products/api/router.py
+from django.http import HttpRequest
+from django.shortcuts import get_object_or_404
+from ninja import Router
+from ninja.pagination import LimitOffsetPagination, paginate
+
+from products.api.schemas import ProductCreateIn, ProductOut, ProductUpdateIn
+from products.models import Product
+
+router = Router(tags=["products"])
+
+
+@router.get("", response=list[ProductOut])
+@paginate(LimitOffsetPagination)
+def list_products(request: HttpRequest) -> list[Product]:
+    return list(Product.objects.filter(is_active=True).order_by("-id"))
+
+
+@router.get("/{product_id}", response=ProductOut)
+def get_product(request: HttpRequest, product_id: int) -> Product:
+    return get_object_or_404(Product, id=product_id)
+
+
+@router.post("", response={201: ProductOut})
+def create_product(request: HttpRequest, payload: ProductCreateIn) -> tuple[int, Product]:
+    product = Product.objects.create(**payload.dict())
+    return 201, product
+
+
+@router.patch("/{product_id}", response=ProductOut)
+def update_product(
+    request: HttpRequest,
+    product_id: int,
+    payload: ProductUpdateIn,
+) -> Product:
+    product = get_object_or_404(Product, id=product_id)
+    changes = payload.dict(exclude_unset=True)
+    for field, value in changes.items():
+        setattr(product, field, value)
+    if changes:
+        product.save(update_fields=[*changes.keys(), "updated_at"])
+    return product
+
+
+@router.delete("/{product_id}", response={204: None})
+def delete_product(request: HttpRequest, product_id: int) -> tuple[int, None]:
+    product = get_object_or_404(Product, id=product_id)
+    product.delete()
+    return 204, None
*** Add File: config/api.py
+from ninja import NinjaAPI
+
+from products.api.router import router as products_router
+
+api = NinjaAPI(title="Product API", version="1.0.0")
+api.add_router("/products", products_router)
*** Update File: config/urls.py
@@
+from django.urls import path
+
+from config.api import api
+
 urlpatterns = [
+    path("api/", api.urls),
 ]
```

기존 API 전환 작업은 파일 내용 없이 다음처럼 처리하세요.

```text
- 기존 상품 serializer 파일 삭제 또는 미사용 처리
- 기존 상품 viewset 파일 삭제 또는 미사용 처리
- 기존 router 등록 제거
- URL은 config.api.api + NinjaAPI.add_router("/products", products_router)로만 연결
```

마이그레이션 검증 체크리스트:

```text
- 모델 필드 변경이 없다면 새 migration이 생성되지 않는지 확인
- 모델 필드명이 위 Schema와 다른 경우 Schema 필드 목록을 실제 모델에 맞춤
- updated_at이 auto_now 필드가 아니거나 없으면 update_fields에서 제거
- 가격 DecimalField의 max_digits/decimal_places가 요청 값 검증 요구와 맞는지 확인
- 삭제가 soft delete 정책이면 delete_product를 is_active=False 저장 방식으로 변경
```

검증 명령:

```bash
python manage.py makemigrations --check --dry-run
python manage.py check
pytest
```

---
> **관련 스킬 참조:**
> - API 라우팅/스키마 전환 → **implementation-django-ninja** 스킬