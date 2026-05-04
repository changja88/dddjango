현재 `/private/tmp/dddjango-codex-eval` 작업 디렉터리는 비어 있고, 세션 권한이 읽기 전용이라 파일을 직접 만들 수는 없었습니다. 대신 이 프로젝트 정책에 맞춰 Django Ninja 기준의 깔끔한 API 구조를 잡으면 아래처럼 가는 게 좋습니다.

**권장 구조**
```text
config/
  api.py
  urls.py

apps/
  products/
    models.py
    schemas.py
    api.py
    selectors.py
    services.py
```

**config/api.py**
```python
from ninja import NinjaAPI

from apps.products.api import router as products_router

api = NinjaAPI(
    title="Service API",
    version="1.0.0",
)

api.add_router("/v1/products", products_router, tags=["products"])
```

**config/urls.py**
```python
from django.urls import path

from config.api import api

urlpatterns = [
    path("api/", api.urls),
]
```

**apps/products/schemas.py**
```python
from ninja import ModelSchema, Schema

from apps.products.models import Product


class ProblemDetail(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str = ""


class ProductOut(ModelSchema):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "is_active", "created_at"]


class ProductCreateIn(Schema):
    name: str
    price: int


class ProductUpdateIn(Schema):
    name: str | None = None
    price: int | None = None
    is_active: bool | None = None
```

**apps/products/selectors.py**
```python
from django.shortcuts import get_object_or_404

from apps.products.models import Product


def product_list():
    return Product.objects.filter(is_active=True).order_by("-created_at")


def product_get(product_id: int) -> Product:
    return get_object_or_404(Product, id=product_id)
```

**apps/products/services.py**
```python
from apps.products.models import Product
from apps.products.schemas import ProductCreateIn, ProductUpdateIn


def product_create(data: ProductCreateIn) -> Product:
    return Product.objects.create(**data.dict())


def product_update(product: Product, data: ProductUpdateIn) -> Product:
    for field, value in data.dict(exclude_unset=True).items():
        setattr(product, field, value)
    product.save(update_fields=[*data.dict(exclude_unset=True).keys()])
    return product
```

**apps/products/api.py**
```python
from typing import List

from ninja import Router
from ninja.pagination import CursorPagination, paginate

from apps.products.schemas import ProductCreateIn, ProductOut, ProductUpdateIn
from apps.products.selectors import product_get, product_list
from apps.products.services import product_create, product_update

router = Router()


@router.get("", response=List[ProductOut])
@paginate(CursorPagination)
def list_products(request):
    return product_list()


@router.get("/{product_id}", response=ProductOut)
def get_product(request, product_id: int):
    return product_get(product_id)


@router.post("", response={201: ProductOut})
def create_product(request, payload: ProductCreateIn):
    product = product_create(payload)
    return 201, product


@router.patch("/{product_id}", response=ProductOut)
def update_product(request, product_id: int, payload: ProductUpdateIn):
    product = product_get(product_id)
    return product_update(product, payload)


@router.delete("/{product_id}", response={204: None})
def delete_product(request, product_id: int):
    product = product_get(product_id)
    product.delete()
    return 204, None
```

핵심은 `config/api.py`에서 API 합성만 하고, 앱별 `api.py`는 라우팅만, `schemas.py`는 입출력 계약만, `selectors.py`는 조회 쿼리, `services.py`는 변경 로직을 맡기는 구조입니다. URL은 `/api/v1/products`처럼 버전과 복수 명사 기반으로 잡고, 목록은 반드시 페이지네이션을 붙이는 쪽이 좋습니다.

검증은 실행하지 못했습니다. 현재 워크스페이스가 비어 있고 읽기 전용입니다.

---
> **관련 스킬 참조:**
> - REST URL/상태 코드/오류 형식 → **architecture-api** 스킬
> - Django Ninja Router/Schema/API 구현 → **implementation-django-ninja** 스킬