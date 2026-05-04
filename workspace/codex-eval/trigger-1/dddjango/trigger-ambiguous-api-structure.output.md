현재 `/private/tmp/dddjango-codex-eval` 워크스페이스는 비어 있고 읽기 전용이라 실제 파일 생성/수정/실행은 못 했습니다. `AGENTS.md`가 가리키는 `config.toml`도 현재 위치에는 없습니다. 대신 dddjango 지침에 맞춰 **DRF 없이 Django Ninja 기준**으로 바로 적용 가능한 API 구조를 잡으면 아래처럼 가는 게 깔끔합니다.

**권장 구조**
```text
config/
  api.py
  urls.py

common/
  api/
    errors.py

apps/
  products/
    models.py
    schemas.py
    filters.py
    selectors.py
    services.py
    api.py
    tests/
      test_api.py
```

핵심 원칙은 간단합니다.

- `api.py`: HTTP 요청/응답 변환만 담당
- `schemas.py`: 요청/응답 Pydantic Schema
- `filters.py`: 목록 필터링
- `selectors.py`: 조회 쿼리 전용
- `services.py`: 생성/수정/삭제 같은 유스케이스
- `config/api.py`: 앱별 Router 합성
- `common/api/errors.py`: RFC 9457 Problem Details 공통 에러 형식

예시는 `products` 앱 기준입니다.

```python
# apps/products/schemas.py
from datetime import datetime
from decimal import Decimal

from ninja import Schema


class ProblemDetail(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str | None = None


class ProductCreateIn(Schema):
    name: str
    sku: str
    price: Decimal


class ProductUpdateIn(Schema):
    name: str | None = None
    price: Decimal | None = None


class ProductOut(Schema):
    id: int
    name: str
    sku: str
    price: Decimal
    created_at: datetime
```

```python
# apps/products/filters.py
from ninja import Field, FilterSchema


class ProductFilter(FilterSchema):
    q: str | None = Field(None, q=["name__icontains", "sku__icontains"])
    min_price: float | None = Field(None, q="price__gte")
    max_price: float | None = Field(None, q="price__lte")
```

```python
# apps/products/selectors.py
from django.db.models import QuerySet

from .models import Product


def product_list() -> QuerySet[Product]:
    return Product.objects.order_by("-created_at")


def product_get(product_id: int) -> Product:
    return Product.objects.get(id=product_id)
```

```python
# apps/products/services.py
from django.db import IntegrityError, transaction

from .models import Product
from .schemas import ProductCreateIn, ProductUpdateIn


class ProductAlreadyExistsError(Exception):
    pass


@transaction.atomic
def product_create(data: ProductCreateIn) -> Product:
    try:
        return Product.objects.create(
            name=data.name,
            sku=data.sku,
            price=data.price,
        )
    except IntegrityError as exc:
        raise ProductAlreadyExistsError from exc


@transaction.atomic
def product_update(product: Product, data: ProductUpdateIn) -> Product:
    for field, value in data.dict(exclude_unset=True).items():
        setattr(product, field, value)
    product.save(update_fields=[*data.dict(exclude_unset=True).keys(), "updated_at"])
    return product


@transaction.atomic
def product_delete(product: Product) -> None:
    product.delete()
```

```python
# apps/products/api.py
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import LimitOffsetPagination, paginate

from .filters import ProductFilter
from .models import Product
from .schemas import ProblemDetail, ProductCreateIn, ProductOut, ProductUpdateIn
from .selectors import product_get, product_list
from .services import ProductAlreadyExistsError, product_create, product_delete, product_update

router = Router(tags=["products"])


@router.get("", response=list[ProductOut])
@paginate(LimitOffsetPagination)
def list_products(request, filters: ProductFilter = ProductFilter()) -> list[Product]:
    return filters.filter(product_list())


@router.get("/{product_id}", response={200: ProductOut, 404: ProblemDetail})
def get_product(request, product_id: int) -> Product:
    return get_object_or_404(Product, id=product_id)


@router.post("", response={201: ProductOut, 409: ProblemDetail, 422: ProblemDetail})
def create_product(request, payload: ProductCreateIn) -> tuple[int, Product]:
    try:
        return 201, product_create(payload)
    except ProductAlreadyExistsError:
        return 409, ProblemDetail(
            type="https://api.example.com/problems/product-already-exists",
            title="Product already exists",
            status=409,
            detail="A product with the same SKU already exists.",
            instance=request.path,
        )


@router.patch("/{product_id}", response={200: ProductOut, 404: ProblemDetail, 422: ProblemDetail})
def update_product(request, product_id: int, payload: ProductUpdateIn) -> Product:
    product = product_get(product_id)
    return product_update(product, payload)


@router.delete("/{product_id}", response={204: None, 404: ProblemDetail})
def delete_product(request, product_id: int) -> tuple[int, None]:
    product = product_get(product_id)
    product_delete(product)
    return 204, None
```

```python
# config/api.py
from ninja import NinjaAPI

from apps.products.api import router as products_router

api = NinjaAPI(title="Service API", version="1.0.0")
api.add_router("/products", products_router)
```

```python
# config/urls.py
from django.contrib import admin
from django.urls import path

from .api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
```

검증은 현재 샌드박스에서 실행하지 못했습니다. 실제 프로젝트에 반영한 뒤에는 아래 순서로 확인하면 됩니다.

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
pytest apps/products/tests/test_api.py
```

---
> **관련 스킬 참조:**
> - REST URL/상태 코드/에러 형식 → **architecture-api** 스킬
> - Django Ninja Router/Schema/Filter/Pagination 구현 → **implementation-django-ninja** 스킬
> - 서비스/조회 계층 분리와 의존성 방향 → **architecture-implementation-patterns** 스킬