**상품 검색 API 팀 컨벤션**

전제: `products.Product` 모델은 `id, name, slug, price, category_id, status, is_active, created_at`을 가진다. API는 DRF 없이 Django Ninja `Schema / FilterSchema / Router / Query`만 사용한다.

**Endpoint**

```http
GET /api/v1/products
```

규칙:
- 컬렉션은 복수 명사: `/products`
- 검색/필터/정렬/페이지네이션은 query parameter만 사용
- 기본 정렬은 최신순: `-created_at,-id`
- 사용자 입력 sort 값을 `order_by()`에 직접 넘기지 않고 allow-list로 매핑
- 공개 상품 검색은 cursor pagination을 기본으로 한다
- 에러는 모두 `application/problem+json`의 RFC 9457 Problem Details 형식

**Query 표준**

| Query | 예시 | 규칙 |
|---|---|---|
| `q` | `q=keyboard` | 상품명/slug 검색 |
| `category_id` | `category_id=10` | 단일 카테고리 |
| `min_price` / `max_price` | `min_price=10000` | 금액 범위 |
| `status` | `status=on_sale` | enum 값만 허용 |
| `sort` | `sort=price` | `relevance`, `price`, `-price`, `newest`만 허용 |
| `cursor` | `cursor=...` | Django Ninja CursorPagination 토큰 |
| `page_size` | `page_size=40` | 기본 20, 최대 100 |

**schemas.py**

```python
from decimal import Decimal
from typing import Literal

from ninja import FilterSchema, ModelSchema, Schema
from pydantic import Field

from products.models import Product


ProductSort = Literal["relevance", "price", "-price", "newest"]
ProductStatus = Literal["on_sale", "sold_out", "hidden"]


class ProductSearchQuery(FilterSchema):
    q: str | None = Field(None, max_length=100)
    category_id: int | None = None
    min_price: Decimal | None = Field(None, ge=0)
    max_price: Decimal | None = Field(None, ge=0)
    status: ProductStatus | None = None
    sort: ProductSort = "newest"


class ProductOut(ModelSchema):
    class Meta:
        model = Product
        fields = ["id", "name", "slug", "price", "category_id", "status"]


class ProblemDetail(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str
    errors: list[dict] | None = None
```

**api.py**

```python
from typing import list

from django.db.models import Q, QuerySet
from ninja import Query, Router
from ninja.pagination import CursorPagination, paginate

from products.models import Product
from products.schemas import ProblemDetail, ProductOut, ProductSearchQuery

router = Router(tags=["products"])

SORT_MAP = {
    "relevance": ("-created_at", "-id"),
    "newest": ("-created_at", "-id"),
    "price": ("price", "id"),
    "-price": ("-price", "-id"),
}


def search_products(filters: ProductSearchQuery) -> QuerySet[Product]:
    qs = Product.objects.filter(is_active=True).select_related("category")

    if filters.q:
        qs = qs.filter(Q(name__icontains=filters.q) | Q(slug__icontains=filters.q))
    if filters.category_id:
        qs = qs.filter(category_id=filters.category_id)
    if filters.min_price is not None:
        qs = qs.filter(price__gte=filters.min_price)
    if filters.max_price is not None:
        qs = qs.filter(price__lte=filters.max_price)
    if filters.status:
        qs = qs.filter(status=filters.status)

    return qs.order_by(*SORT_MAP[filters.sort])


@router.get(
    "",
    response={200: list[ProductOut], 422: ProblemDetail},
)
@paginate(CursorPagination, page_size=20, max_page_size=100)
def list_products(request, filters: Query[ProductSearchQuery]):
    return search_products(filters)
```

**config/api.py**

```python
from ninja import NinjaAPI

from products.api import router as products_router

api = NinjaAPI(title="Commerce API", version="1.0.0")
api.add_router("/v1/products", products_router)
```

**Validation Error 표준**

Django Ninja 기본 validation error도 Problem Details로 변환한다.

```python
from django.http import JsonResponse
from ninja.errors import ValidationError

from config.api import api


@api.exception_handler(ValidationError)
def validation_error_handler(request, exc):
    return JsonResponse(
        {
            "type": "https://api.example.com/problems/validation-error",
            "title": "Validation Error",
            "status": 422,
            "detail": "Request validation failed.",
            "instance": request.path,
            "errors": exc.errors,
        },
        status=422,
        content_type="application/problem+json",
    )
```

**검증 절차**

```bash
python manage.py test products
python manage.py check
curl 'http://localhost:8000/api/v1/products?q=keyboard&sort=-price&page_size=20'
curl 'http://localhost:8000/api/v1/products?min_price=-1' -i
```

두 번째 `curl`은 `422`와 `application/problem+json`을 반환해야 한다.

---
> **관련 스킬 참조:**
> - API 설계/오류/페이지네이션 → **architecture-api** 스킬
> - Django Ninja Schema/Router/Query 구현 → **implementation-django-ninja** 스킬