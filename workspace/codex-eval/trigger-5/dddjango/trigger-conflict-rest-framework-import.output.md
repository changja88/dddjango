이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다.

아래는 DRF의 `Serializer` + `APIView` 역할을 Django Ninja의 `Schema` + `Router`로 바꾼 예제입니다. `products` 앱에 `Product` 모델이 있다고 가정합니다.

**products/schemas.py**
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

**products/api.py**
```python
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from .models import Product
from .schemas import ProductIn, ProductOut

router = Router(tags=["products"])


@router.get("", response=list[ProductOut])
def list_products(request: HttpRequest) -> list[Product]:
    return list(Product.objects.order_by("-id"))


@router.post("", response={201: ProductOut})
def create_product(request: HttpRequest, payload: ProductIn) -> tuple[int, Product]:
    product = Product.objects.create(
        name=payload.name,
        price=payload.price,
        is_active=payload.is_active,
    )
    return 201, product


@router.get("/{product_id}", response=ProductOut)
def get_product(request: HttpRequest, product_id: int) -> Product:
    return get_object_or_404(Product, id=product_id)
```

**config/api.py**
```python
from ninja import NinjaAPI

from products.api import router as products_router

api = NinjaAPI(title="Example API")
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

결과 엔드포인트는 다음처럼 동작합니다.

```text
GET  /api/products
POST /api/products
GET  /api/products/{product_id}
```

검증은 실행하지 않았습니다. 현재 워크스페이스가 읽기 전용이고, `config.toml`도 존재하지 않아 파일 생성이나 테스트 실행 없이 예제 코드만 제공했습니다.

---
> **관련 스킬 참조:**
> - Django Ninja API 구현 → **implementation-django-ninja** 스킬