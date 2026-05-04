이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다. 현재 요청에는 구체 리소스/필드가 없고 세션이 읽기 전용이라 파일 수정은 못 했습니다. `config.toml`도 현재 작업 디렉터리에서 찾을 수 없었습니다.

아래는 `products.Product`를 가정한 Django Ninja 대안입니다.

`products/schemas.py`

```python
from ninja import ModelSchema, Schema

from .models import Product


class ProductIn(Schema):
    name: str
    price: int
    is_active: bool = True


class ProductOut(ModelSchema):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "is_active", "created_at"]
```

`products/api.py`

```python
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError

from .models import Product
from .schemas import ProductIn, ProductOut

router = Router(tags=["products"])


@router.get("/", response=list[ProductOut])
def list_products(request) -> list[Product]:
    return list(Product.objects.filter(is_active=True).order_by("-id"))


@router.post("/", response={201: ProductOut})
def create_product(request, payload: ProductIn) -> tuple[int, Product]:
    product = Product.objects.create(**payload.dict())
    return 201, product


@router.get("/{product_id}", response=ProductOut)
def get_product(request, product_id: int) -> Product:
    return get_object_or_404(Product, id=product_id)


@router.patch("/{product_id}", response=ProductOut)
def update_product(request, product_id: int, payload: ProductIn) -> Product:
    product = get_object_or_404(Product, id=product_id)
    for field, value in payload.dict().items():
        setattr(product, field, value)
    product.save(update_fields=["name", "price", "is_active"])
    return product


@router.delete("/{product_id}", response={204: None})
def delete_product(request, product_id: int) -> tuple[int, None]:
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return 204, None
```

`config/api.py`

```python
from ninja import NinjaAPI

from products.api import router as products_router

api = NinjaAPI(title="Project API", version="1.0.0")
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

목록 API가 커질 가능성이 있으면 `@paginate`를 추가하고, 인증이 필요한 API라면 Django Ninja의 `SessionAuth`, `HttpBearer`, `APIKeyHeader` 중 프로젝트 인증 방식에 맞춰 `auth=`로 붙이면 됩니다.

---
> **관련 스킬 참조:**
> - Django Ninja Schema/Router 구현 → **implementation-django-ninja** 스킬