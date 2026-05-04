이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다.

읽기 전용 환경이라 파일을 직접 생성하지는 못했습니다. `products.Product` 모델이 이미 있다고 가정하면 아래처럼 붙이면 됩니다.

**products/schemas.py**
```python
from ninja import ModelSchema

from .models import Product


class ProductOut(ModelSchema):
    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "stock", "is_active", "created_at", "updated_at"]


class ProductCreateIn(ModelSchema):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "stock", "is_active"]


class ProductUpdateIn(ModelSchema):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "stock", "is_active"]


class ProductPatchIn(ModelSchema):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "stock", "is_active"]
        fields_optional = "__all__"
```

**products/api.py**
```python
from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import LimitOffsetPagination, paginate

from .models import Product
from .schemas import ProductCreateIn, ProductOut, ProductPatchIn, ProductUpdateIn

router = Router(tags=["products"])


@router.get("", response=List[ProductOut])
@paginate(LimitOffsetPagination)
def list_products(request):
    return Product.objects.order_by("-id")


@router.post("", response={201: ProductOut})
def create_product(request, payload: ProductCreateIn):
    product = Product.objects.create(**payload.dict())
    return 201, product


@router.get("/{product_id}", response=ProductOut)
def get_product(request, product_id: int):
    return get_object_or_404(Product, id=product_id)


@router.put("/{product_id}", response=ProductOut)
def update_product(request, product_id: int, payload: ProductUpdateIn):
    product = get_object_or_404(Product, id=product_id)

    for field, value in payload.dict().items():
        setattr(product, field, value)

    product.save()
    return product


@router.patch("/{product_id}", response=ProductOut)
def patch_product(request, product_id: int, payload: ProductPatchIn):
    product = get_object_or_404(Product, id=product_id)

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(product, field, value)

    product.save()
    return product


@router.delete("/{product_id}", response={204: None})
def delete_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return 204, None
```

**config/api.py**
```python
from ninja import NinjaAPI

from products.api import router as products_router

api = NinjaAPI()
api.add_router("/products", products_router)
```

**config/urls.py**
```python
from django.urls import path

from .api import api

urlpatterns = [
    path("api/", api.urls),
]
```

엔드포인트는 `GET /api/products`, `POST /api/products`, `GET /api/products/{product_id}`, `PUT/PATCH/DELETE /api/products/{product_id}` 형태입니다. 목록 API는 `limit`/`offset` 페이지네이션을 지원합니다.

---
> **관련 스킬 참조:**
> - Django Ninja API 구현 → **implementation-django-ninja** 스킬