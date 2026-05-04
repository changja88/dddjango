이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다.

현재 `/private/tmp/dddjango-codex-eval`에서 `config.toml`을 찾지 못했고, 세션이 read-only라 파일을 직접 만들지는 못했습니다. 아래는 `products.Product` 모델이 있다고 가정한 Django Ninja 대안입니다.

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
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import LimitOffsetPagination, paginate

from .models import Product
from .schemas import ProductIn, ProductOut

router = Router(tags=["products"])


@router.get("/", response=list[ProductOut])
@paginate(LimitOffsetPagination)
def list_products(request) -> QuerySet[Product]:
    return Product.objects.order_by("-id")


@router.get("/{product_id}", response=ProductOut)
def get_product(request, product_id: int) -> Product:
    return get_object_or_404(Product, id=product_id)


@router.post("/", response={201: ProductOut})
def create_product(request, payload: ProductIn) -> tuple[int, Product]:
    product = Product.objects.create(**payload.dict())
    return 201, product


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

api = NinjaAPI()
api.add_router("/products/", products_router)
```

`config/urls.py`

```python
from django.urls import path

from .api import api

urlpatterns = [
    path("api/", api.urls),
]
```

검증은 실행하지 못했습니다. 적용 후에는 프로젝트에서 `python manage.py check`와 관련 API 테스트를 실행하면 됩니다.

---
> **관련 스킬 참조:**
> - API 설계 원칙 → **architecture-api** 스킬
> - Django Ninja 구현 → **implementation-django-ninja** 스킬