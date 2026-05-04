현재 작업 디렉터리 `/private/tmp/dddjango-codex-eval`은 비어 있고, 세션도 `read-only`라 파일을 만들 수 없습니다.

또한 로컬 `config.toml`의 Django 지침이 **DRF Serializer/ViewSet 사용 금지, Django Ninja 사용**을 명시하고 있어서 `ModelSerializer`/`ViewSet` 구현은 제공할 수 없습니다. 대신 같은 상품 CRUD API는 아래처럼 Django Ninja로 작성하는 방향이 지침에 맞습니다.

```python
# apps/products/api/schemas.py
from decimal import Decimal

from ninja import ModelSchema, Schema

from apps.products.models import Product


class ProductIn(Schema):
    name: str
    price: Decimal
    stock: int


class ProductOut(ModelSchema):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "stock", "created_at", "updated_at"]
```

```python
# apps/products/api/router.py
from django.shortcuts import get_object_or_404
from ninja import Router

from apps.products.api.schemas import ProductIn, ProductOut
from apps.products.models import Product

router = Router(tags=["products"])


@router.get("/products", response=list[ProductOut])
def list_products(request):
    return Product.objects.order_by("-created_at")


@router.post("/products", response={201: ProductOut})
def create_product(request, payload: ProductIn):
    product = Product.objects.create(**payload.dict())
    return 201, product


@router.get("/products/{product_id}", response=ProductOut)
def get_product(request, product_id: int):
    return get_object_or_404(Product, id=product_id)


@router.put("/products/{product_id}", response=ProductOut)
def update_product(request, product_id: int, payload: ProductIn):
    product = get_object_or_404(Product, id=product_id)

    for field, value in payload.dict().items():
        setattr(product, field, value)

    product.save(update_fields=["name", "price", "stock", "updated_at"])
    return product


@router.delete("/products/{product_id}", response={204: None})
def delete_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return 204, None
```

DRF를 반드시 써야 한다면 현재 프로젝트 지침과 충돌하므로 `config.toml`의 DRF 금지 규칙을 먼저 바꿔야 합니다.

---
> **관련 스킬 참조:**
> - Django API 구현 → **implementation-django-ninja** 스킬