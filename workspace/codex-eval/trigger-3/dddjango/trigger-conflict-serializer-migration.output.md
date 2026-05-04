이 프로젝트 정책상 DRF `Serializer`는 사용하지 않고 Django Ninja `Schema`로 요청 검증을 작성합니다.

Django Ninja에서는 “serializer 클래스” 역할을 `Schema`가 합니다. 요청 바디에 붙이면 타입 변환, 필수값 검사, 길이/범위 검증, OpenAPI 문서 생성까지 같이 처리됩니다.

```python
# products/schemas.py
from decimal import Decimal

from ninja import Field, Schema


class ProductCreateIn(Schema):
    name: str = Field(..., min_length=1, max_length=120)
    price: Decimal = Field(..., gt=0)
    sku: str | None = Field(None, max_length=40)


class ProductOut(Schema):
    id: int
    name: str
    price: Decimal
    sku: str | None
```

```python
# products/api.py
from ninja import Router

from .models import Product
from .schemas import ProductCreateIn, ProductOut

router = Router(tags=["products"])


@router.post("/", response={201: ProductOut})
def create_product(request, payload: ProductCreateIn):
    product = Product.objects.create(
        name=payload.name,
        price=payload.price,
        sku=payload.sku,
    )
    return 201, product
```

```python
# config/api.py
from ninja import NinjaAPI

from products.api import router as products_router

api = NinjaAPI()
api.add_router("/products/", products_router)
```

```python
# config/urls.py
from django.urls import path

from .api import api

urlpatterns = [
    path("api/", api.urls),
]
```

PATCH 검증이 필요하면 별도 입력 스키마를 두는 편이 명확합니다.

```python
# products/schemas.py
from decimal import Decimal

from ninja import Field, Schema


class ProductUpdateIn(Schema):
    name: str | None = Field(None, min_length=1, max_length=120)
    price: Decimal | None = Field(None, gt=0)
    sku: str | None = Field(None, max_length=40)
```

```python
@router.patch("/{product_id}", response=ProductOut)
def update_product(request, product_id: int, payload: ProductUpdateIn):
    product = Product.objects.get(id=product_id)

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(product, field, value)

    product.save(update_fields=list(payload.dict(exclude_unset=True).keys()))
    return product
```

핵심은 `Serializer`를 새로 만들지 말고, 요청용 `SomethingCreateIn` / `SomethingUpdateIn`, 응답용 `SomethingOut`처럼 `Schema`를 분리하는 것입니다. 모델 기반 응답 스키마가 필요하면 `ModelSchema`를 쓰되 `fields = "__all__"`은 피하고 노출할 필드를 명시하세요.

---
> **관련 스킬 참조:**
> - Django Ninja 요청/응답 구현 → **implementation-django-ninja** 스킬