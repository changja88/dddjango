이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다. 아래는 `Serializer`와 `APIView` 의도를 각각 Django Ninja `Schema`와 `Router` 엔드포인트로 바꾼 예제입니다.

가정: `products` 앱에 `Product` 모델이 있고 `id`, `name`, `price`, `is_active` 필드가 있습니다.

`products/schemas.py`

```python
from decimal import Decimal

from ninja import Schema


class ProductIn(Schema):
    name: str
    price: Decimal
    is_active: bool = True


class ProductOut(Schema):
    id: int
    name: str
    price: Decimal
    is_active: bool
```

`products/api.py`

```python
from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router

from .models import Product
from .schemas import ProductIn, ProductOut

router = Router(tags=["products"])


@router.get("/", response=List[ProductOut])
def list_products(request) -> list[Product]:
    return list(Product.objects.order_by("-id"))


@router.post("/", response={201: ProductOut})
def create_product(request, payload: ProductIn) -> tuple[int, Product]:
    product = Product.objects.create(**payload.dict())
    return 201, product


@router.get("/{product_id}", response=ProductOut)
def get_product(request, product_id: int) -> Product:
    return get_object_or_404(Product, id=product_id)
```

`config/api.py`

```python
from ninja import NinjaAPI

from products.api import router as products_router

api = NinjaAPI(title="Example API")
api.add_router("/products/", products_router)
```

`config/urls.py`

```python
from django.contrib import admin
from django.urls import path

from .api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
```

요청하신 `Serializer` 역할은 `ProductIn`/`ProductOut`이 맡고, `APIView` 역할은 `@router.get`, `@router.post` 엔드포인트 함수들이 맡습니다.

---
> **관련 스킬 참조:**
> - Django Ninja API 구현 → **implementation-django-ninja** 스킬