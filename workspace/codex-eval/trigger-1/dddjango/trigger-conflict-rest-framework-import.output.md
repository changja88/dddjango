이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다. 따라서 `from rest_framework...`, `Serializer`, `APIView` 예제 대신 같은 역할을 하는 `Schema`와 `Router` 예제를 제공합니다.

읽기 전용 빈 워크스페이스라 파일 생성과 실행 검증은 하지 못했습니다. 아래 코드는 `products` 앱에 `Product` 모델이 있다고 가정한 붙여 넣기용 예제입니다.

**apps/products/api/schemas.py**
```python
from decimal import Decimal

from ninja import ModelSchema, Schema

from apps.products.models import Product


class ProductCreateSchema(Schema):
    name: str
    price: Decimal
    description: str = ""


class ProductOutSchema(ModelSchema):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "description", "created_at"]
```

**apps/products/api/selectors.py**
```python
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from apps.products.models import Product


def product_list() -> QuerySet[Product]:
    return Product.objects.order_by("-created_at")


def product_get(product_id: int) -> Product:
    return get_object_or_404(Product, id=product_id)
```

**apps/products/services.py**
```python
from apps.products.models import Product


def product_create(*, name: str, price, description: str = "") -> Product:
    return Product.objects.create(
        name=name,
        price=price,
        description=description,
    )
```

**apps/products/api/router.py**
```python
from ninja import Router
from ninja.security import SessionAuth

from apps.products.api.schemas import ProductCreateSchema, ProductOutSchema
from apps.products.api.selectors import product_get, product_list
from apps.products.services import product_create

router = Router(tags=["products"], auth=SessionAuth())


@router.get("", response=list[ProductOutSchema])
def list_products(request) -> list:
    return list(product_list())


@router.get("/{product_id}", response=ProductOutSchema)
def get_product(request, product_id: int) -> ProductOutSchema:
    return product_get(product_id)


@router.post("", response={201: ProductOutSchema})
def create_product(request, payload: ProductCreateSchema) -> tuple[int, object]:
    product = product_create(
        name=payload.name,
        price=payload.price,
        description=payload.description,
    )
    return 201, product
```

**config/api.py**
```python
from ninja import NinjaAPI

from apps.products.api.router import router as products_router

api = NinjaAPI(title="Project API")
api.add_router("/products", products_router)
```

**config/urls.py**
```python
from django.urls import path

from config.api import api

urlpatterns = [
    path("api/", api.urls),
]
```

DRF 기준으로 보면 매핑은 이렇게 보면 됩니다.

`Serializer` → `ProductCreateSchema`, `ProductOutSchema`  
`APIView.get()` → `@router.get(...)`  
`APIView.post()` → `@router.post(...)`  
`permission_classes` → `Router(..., auth=SessionAuth())`

실행 검증은 이 환경이 읽기 전용이고 프로젝트 파일이 없어 수행하지 못했습니다. 실제 프로젝트에서는 보통 아래처럼 확인합니다.

```bash
python manage.py check
pytest
python manage.py runserver
```

---
> **관련 스킬 참조:**
> - Django Ninja API 구현 → **implementation-django-ninja** 스킬