작업 디렉터리가 비어 있어서 실제 파일 기준 diff는 만들 수 없습니다. 아래는 기존 상품 API 파일을 통째로 대체하는 형태의 패치 제안입니다.

```diff
*** Add File: products/schemas.py
+from datetime import datetime
+from decimal import Decimal
+
+from ninja import Schema
+
+
+class ProductOut(Schema):
+    id: int
+    name: str
+    description: str = ""
+    price: Decimal
+    stock: int
+    is_active: bool
+    created_at: datetime
+    updated_at: datetime
+
+
+class ProductCreateIn(Schema):
+    name: str
+    description: str = ""
+    price: Decimal
+    stock: int = 0
+    is_active: bool = True
+
+
+class ProductUpdateIn(Schema):
+    name: str
+    description: str = ""
+    price: Decimal
+    stock: int
+    is_active: bool
+
+
+class ProductPatchIn(Schema):
+    name: str | None = None
+    description: str | None = None
+    price: Decimal | None = None
+    stock: int | None = None
+    is_active: bool | None = None
*** Add File: products/api.py
+from django.shortcuts import get_object_or_404
+from ninja import Router
+
+from .models import Product
+from .schemas import ProductCreateIn, ProductOut, ProductPatchIn, ProductUpdateIn
+
+router = Router(tags=["products"])
+
+
+@router.get("/products", response=list[ProductOut])
+def list_products(request):
+    return Product.objects.order_by("-id")
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
+@router.put("/products/{product_id}", response=ProductOut)
+def update_product(request, product_id: int, payload: ProductUpdateIn):
+    product = get_object_or_404(Product, id=product_id)
+
+    for field, value in payload.dict().items():
+        setattr(product, field, value)
+
+    product.save()
+    return product
+
+
+@router.patch("/products/{product_id}", response=ProductOut)
+def patch_product(request, product_id: int, payload: ProductPatchIn):
+    product = get_object_or_404(Product, id=product_id)
+
+    for field, value in payload.dict(exclude_unset=True).items():
+        setattr(product, field, value)
+
+    product.save()
+    return product
+
+
+@router.delete("/products/{product_id}", response={204: None})
+def delete_product(request, product_id: int):
+    product = get_object_or_404(Product, id=product_id)
+    product.delete()
+    return 204, None
*** Update File: config/urls.py
@@
 from django.contrib import admin
 from django.urls import path
+from ninja import NinjaAPI
+
+from products.api import router as products_router
+
+api = NinjaAPI()
+api.add_router("", products_router)

 urlpatterns = [
     path("admin/", admin.site.urls),
+    path("api/", api.urls),
 ]
```

의존성이 없다면 추가합니다.

```txt
django-ninja
```

검증 명령은 아래 순서로 돌리면 됩니다.

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py runserver
```

남은 이전 구현 흔적 확인:

```bash
rg "ViewSet|ModelSerializer|DefaultRouter|APIView|api_view"
```