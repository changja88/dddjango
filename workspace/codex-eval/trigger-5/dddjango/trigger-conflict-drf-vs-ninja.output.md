**주요 내용**

이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다.

현재 워크스페이스가 읽기 전용이고 대상 API 상세가 없어 파일 수정은 하지 않았습니다. 아래는 `products.Product(id, name, price, is_active)` 기준의 Django Ninja 대안입니다.

`products/schemas.py`

```python
from decimal import Decimal

from ninja import ModelSchema, Schema

from .models import Product


class ProductIn(Schema):
    name: str
    price: Decimal
    is_active: bool = True


class ProductPatch(Schema):
    name: str | None = None
    price: Decimal | None = None
    is_active: bool | None = None


class ProductOut(ModelSchema):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "is_active"]
```

`products/api.py`

```python
from django.db.models import QuerySet
from django.http import Http404, HttpRequest
from ninja import Router

from .models import Product
from .schemas import ProductIn, ProductOut, ProductPatch

router = Router(tags=["products"])


def get_product_or_404(product_id: int) -> Product:
    try:
        return Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        raise Http404("Product not found")


@router.get("", response=list[ProductOut])
def list_products(request: HttpRequest) -> QuerySet[Product]:
    return Product.objects.all()


@router.post("", response={201: ProductOut})
def create_product(request: HttpRequest, payload: ProductIn) -> tuple[int, Product]:
    product = Product.objects.create(**payload.model_dump())
    return 201, product


@router.get("/{product_id}", response=ProductOut)
def retrieve_product(request: HttpRequest, product_id: int) -> Product:
    return get_product_or_404(product_id)


@router.patch("/{product_id}", response=ProductOut)
def update_product(
    request: HttpRequest,
    product_id: int,
    payload: ProductPatch,
) -> Product:
    product = get_product_or_404(product_id)
    updates = payload.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(product, field, value)

    if updates:
        product.save(update_fields=list(updates.keys()))

    return product


@router.delete("/{product_id}", response={204: None})
def delete_product(request: HttpRequest, product_id: int) -> tuple[int, None]:
    product = get_product_or_404(product_id)
    product.delete()
    return 204, None
```

`config/api.py`

```python
from ninja import NinjaAPI

from products.api import router as products_router

api = NinjaAPI()
api.add_router("/products", products_router)
```

`config/urls.py`

```python
from django.urls import path

from .api import api

urlpatterns = [
    path("api/", api.urls),
]
```

검증은 실행하지 못했습니다. 적용 후에는 다음을 돌리면 됩니다.

```bash
python manage.py check
pytest
```

---
> **관련 스킬 참조:**
> - REST API 설계 → **architecture-api** 스킬
> - Django Ninja 구현 → **implementation-django-ninja** 스킬