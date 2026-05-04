이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다. 현재 워크스페이스는 비어 있고 읽기 전용이라 실제 코드 실행/검증은 하지 못했지만, 기존 `Serializer`/`ViewSet` 상품 API를 `Schema`/`Router` 구조로 옮기는 기준 가이드는 아래처럼 잡으면 됩니다.

**마이그레이션 원칙**

| 기존 DRF 개념 | Django Ninja 전환 |
|---|---|
| `Serializer`, `ModelSerializer` | `Schema` 또는 `ModelSchema` |
| `ViewSet` | 앱별 `Router()` + `@router.get/post/patch/delete` |
| DRF router | `NinjaAPI.add_router()` |
| `permission_classes` | Ninja `auth=` 또는 `Router(auth=...)` |
| serializer validation | Pydantic Schema 검증 |
| paginated list | `@paginate(...)` |
| custom error response | RFC 9457 Problem Details |

URL은 리소스 중심으로 유지합니다. 상품 목록은 `GET /api/products`, 상세는 `GET /api/products/{product_id}`, 생성은 `POST /api/products`, 수정은 `PATCH /api/products/{product_id}`, 삭제는 `DELETE /api/products/{product_id}` 형태가 좋습니다.

**권장 파일 구조**

```text
apps/products/
  models.py
  api/
    schemas.py
    filters.py
    selectors.py
    services.py
    router.py
config/
  api.py
  urls.py
```

`schemas.py`는 입력/출력을 분리합니다. 응답 Schema에 모든 모델 필드를 노출하지 말고 공개할 필드만 명시합니다.

```python
from decimal import Decimal

from ninja import ModelSchema, Schema

from apps.products.models import Product


class ProductOut(ModelSchema):
    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "status", "stock_quantity"]


class ProductCreateIn(Schema):
    name: str
    description: str = ""
    price: Decimal
    stock_quantity: int


class ProductPatchIn(Schema):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    stock_quantity: int | None = None


class ProblemDetail(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str = ""
```

목록 조회는 selector로 분리해 엔드포인트가 HTTP 변환만 담당하게 합니다.

```python
# apps/products/api/selectors.py
from django.db.models import QuerySet

from apps.products.models import Product


def product_list() -> QuerySet[Product]:
    return Product.objects.order_by("-id")


def product_get(product_id: int) -> Product:
    return Product.objects.get(id=product_id)
```

필터링은 `FilterSchema`로 옮깁니다. 단일 검색어만 두지 말고 상품 API에서 실제 필요한 다중 필드를 명시합니다.

```python
# apps/products/api/filters.py
from pydantic import Field
from ninja import FilterSchema


class ProductFilter(FilterSchema):
    q: str | None = Field(None, q=["name__icontains", "description__icontains"])
    status: str | None = None
    min_price: float | None = Field(None, q="price__gte")
    max_price: float | None = Field(None, q="price__lte")
```

쓰기 로직은 service로 뺍니다. 재고, 가격 정책, 상태 변경 같은 비즈니스 규칙이 엔드포인트에 들어가면 다시 fat endpoint가 됩니다.

```python
# apps/products/api/services.py
from apps.products.models import Product
from apps.products.api.schemas import ProductCreateIn, ProductPatchIn


def product_create(data: ProductCreateIn) -> Product:
    return Product.objects.create(**data.model_dump())


def product_update(product: Product, data: ProductPatchIn) -> Product:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    product.full_clean()
    product.save(update_fields=list(data.model_dump(exclude_unset=True).keys()))
    return product
```

라우터는 `ViewSet` 대신 HTTP 메서드별 함수로 분리합니다.

```python
# apps/products/api/router.py
from typing import List

from django.shortcuts import get_object_or_404
from ninja import Query, Router
from ninja.pagination import CursorPagination, paginate

from apps.products.models import Product
from apps.products.api.filters import ProductFilter
from apps.products.api.schemas import (
    ProblemDetail,
    ProductCreateIn,
    ProductOut,
    ProductPatchIn,
)
from apps.products.api.selectors import product_list
from apps.products.api.services import product_create, product_update

router = Router(tags=["products"])


@router.get("", response=List[ProductOut])
@paginate(CursorPagination, page_size=50)
def list_products(request, filters: Query[ProductFilter]):
    return filters.filter(product_list())


@router.get("/{product_id}", response={200: ProductOut, 404: ProblemDetail})
def get_product(request, product_id: int):
    return get_object_or_404(Product, id=product_id)


@router.post("", response={201: ProductOut, 409: ProblemDetail, 422: ProblemDetail})
def create_product(request, payload: ProductCreateIn):
    product = product_create(payload)
    return 201, product


@router.patch("/{product_id}", response={200: ProductOut, 404: ProblemDetail, 422: ProblemDetail})
def patch_product(request, product_id: int, payload: ProductPatchIn):
    product = get_object_or_404(Product, id=product_id)
    return product_update(product, payload)


@router.delete("/{product_id}", response={204: None, 404: ProblemDetail})
def delete_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return 204, None
```

최상위 API 합성은 `config/api.py`에서 합니다. 문자열 경로보다 실제 router 객체 import를 권장합니다.

```python
# config/api.py
from ninja import NinjaAPI

from apps.products.api.router import router as products_router

api = NinjaAPI(title="Product API", version="1.0.0")
api.add_router("/products", products_router)
```

```python
# config/urls.py
from django.urls import path

from config.api import api

urlpatterns = [
    path("api/", api.urls),
]
```

**체크리스트**

1. `Serializer`는 `ProductOut`, `ProductCreateIn`, `ProductPatchIn`으로 분리합니다.
2. `ViewSet` action은 `@router.get/post/patch/delete` 함수로 나눕니다.
3. 목록 API에는 페이지네이션을 반드시 붙입니다.
4. 응답 Schema는 민감 필드와 내부 관리 필드를 제외합니다.
5. `fields = "__all__"`에 해당하는 자동 전체 노출은 금지합니다.
6. 비즈니스 규칙은 `services.py`, 읽기 쿼리는 `selectors.py`에 둡니다.
7. 오류 응답은 `ProblemDetail` 형식으로 통일합니다.
8. 인증이 필요하면 DRF permission이 아니라 `Router(auth=...)` 또는 엔드포인트 `auth=...`를 사용합니다.

검증은 실제 프로젝트에서 다음 흐름으로 잡으면 됩니다.

```bash
pytest apps/products/tests/test_product_api.py
python manage.py check
python manage.py spectacular --validate  # 사용 중인 OpenAPI 검증 도구가 있다면 해당 명령으로 대체
```

---
> **관련 스킬 참조:**
> - REST URL/상태 코드/페이지네이션 설계 → **architecture-api** 스킬
> - Django Ninja Schema/Router/API 테스트 구현 → **implementation-django-ninja** 스킬
> - QuerySet/selectors/services 구조화 → **implementation-django** 스킬