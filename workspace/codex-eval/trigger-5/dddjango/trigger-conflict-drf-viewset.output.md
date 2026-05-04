이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다.

빈 워크스페이스이고 쓰기 권한이 없어 파일을 직접 만들지는 못했습니다. 아래는 `products.Product` 모델이 이미 있다고 가정한 상품 CRUD API입니다.

**products/schemas.py**
```python
from decimal import Decimal

from ninja import ModelSchema, Schema

from .models import Product


class ProductOut(ModelSchema):
    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "is_active", "created_at", "updated_at"]


class ProductCreateIn(Schema):
    name: str
    description: str = ""
    price: Decimal
    is_active: bool = True


class ProductUpdateIn(Schema):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    is_active: bool | None = None
```

**products/api.py**
```python
from ninja import PatchDict, Router
from ninja.pagination import LimitOffsetPagination, paginate
from django.shortcuts import get_object_or_404

from .models import Product
from .schemas import ProductCreateIn, ProductOut, ProductUpdateIn

router = Router(tags=["products"])


@router.get("", response=list[ProductOut])
@paginate(LimitOffsetPagination)
def list_products(request) -> list[Product]:
    return Product.objects.order_by("-created_at")


@router.get("/{product_id}", response=ProductOut)
def get_product(request, product_id: int) -> Product:
    return get_object_or_404(Product, id=product_id)


@router.post("", response={201: ProductOut})
def create_product(request, payload: ProductCreateIn) -> tuple[int, Product]:
    product = Product.objects.create(**payload.dict())
    return 201, product


@router.patch("/{product_id}", response=ProductOut)
def update_product(request, product_id: int, payload: PatchDict[ProductUpdateIn]) -> Product:
    product = get_object_or_404(Product, id=product_id)

    for field, value in payload.items():
        setattr(product, field, value)

    product.save(update_fields=[*payload.keys(), "updated_at"])
    return product


@router.delete("/{product_id}", response={204: None})
def delete_product(request, product_id: int) -> tuple[int, None]:
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return 204, None
```

**config/api.py**
```python
from ninja import NinjaAPI

from products.api import router as products_router

api = NinjaAPI(title="Product API", version="1.0.0")
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

검증은 이 세션에서 실행하지 못했습니다. 적용 후 아래를 실행하세요.

```bash
python manage.py check
python manage.py test
```

---
> **관련 스킬 참조:**
> - Django Ninja API 구현 → **implementation-django-ninja** 스킬