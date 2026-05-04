이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다.

아래는 DRF `Serializer` + `APIView` 역할을 Django Ninja `Schema` + `Router`로 바꾼 예제입니다. `products.Product` 모델이 있다고 가정합니다.

**products/schemas.py**
```python
from ninja import ModelSchema, Schema

from .models import Product


class ProductCreateSchema(Schema):
    name: str
    price: int
    is_active: bool = True


class ProductSchema(ModelSchema):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "is_active", "created_at"]
```

**products/api.py**
```python
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from .models import Product
from .schemas import ProductCreateSchema, ProductSchema

router = Router(tags=["products"])


@router.get("/", response=list[ProductSchema])
def list_products(request: HttpRequest) -> list[Product]:
    return list(Product.objects.order_by("-created_at"))


@router.get("/{product_id}/", response=ProductSchema)
def get_product(request: HttpRequest, product_id: int) -> Product:
    return get_object_or_404(Product, id=product_id)


@router.post("/", response={201: ProductSchema})
def create_product(request: HttpRequest, payload: ProductCreateSchema) -> tuple[int, Product]:
    product = Product.objects.create(**payload.dict())
    return 201, product
```

**config/api.py**
```python
from ninja import NinjaAPI

from products.api import router as products_router

api = NinjaAPI(title="Example API", version="1.0.0")
api.add_router("/products/", products_router)
```

**config/urls.py**
```python
from django.contrib import admin
from django.urls import path

from .api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
```

검증은 이 환경에서 실행하지 않았습니다. 적용 후 아래를 실행하세요.

```bash
python manage.py check
pytest
```

---
> **관련 스킬 참조:**
> - Django Ninja API 구현 → **implementation-django-ninja** 스킬