**주요 내용**

상품 검색 API는 컬렉션 리소스 기준으로 `GET /api/v1/products`만 둔다. 검색, 필터, 정렬, 페이지네이션은 모두 query parameter로 받는다. DRF는 사용하지 않고 Django Ninja `Schema` / `FilterSchema` / `Router` / `Query` 기준으로 통일한다.

**팀 컨벤션**

- URL: `GET /api/v1/products`
- 검색: `q`
- 필터: `category_id`, `brand_id`, `min_price`, `max_price`, `status`, `in_stock`
- 정렬: `sort` allow-list만 허용. 사용자 입력을 `order_by()`에 직접 넘기지 않는다.
- 페이지네이션: 커서 기반. 응답은 항상 `items/meta` envelope.
- 에러: 모든 API 에러는 RFC 9457 Problem Details 형식.
- validation error: `422` + `invalid_params` 배열로 통일.
- 목록 응답에는 `has_more`, `next_cursor`, `limit`을 포함한다.

```python
# products/api.py
from decimal import Decimal
from enum import StrEnum
from typing import Literal

from django.db.models import QuerySet
from ninja import Field, FilterSchema, Query, Router, Schema

from products.models import Product

router = Router(tags=["products"])


class ProductSort(StrEnum):
    RELEVANCE = "relevance"
    NEWEST = "-created_at"
    PRICE_ASC = "price"
    PRICE_DESC = "-price"


class ProductSearchQuery(FilterSchema):
    q: str | None = Field(None, q=["name__icontains", "description__icontains"])
    category_id: int | None = Field(None, q="category_id")
    brand_id: int | None = Field(None, q="brand_id")
    min_price: Decimal | None = Field(None, q="price__gte")
    max_price: Decimal | None = Field(None, q="price__lte")
    status: Literal["active", "sold_out", "hidden"] | None = Field(None, q="status")
    in_stock: bool | None = None
    sort: ProductSort = ProductSort.RELEVANCE
    limit: int = Field(20, ge=1, le=100)
    cursor: str | None = None


class ProductOut(Schema):
    id: int
    name: str
    price: Decimal
    brand_name: str | None
    thumbnail_url: str | None
    status: str


class PageMeta(Schema):
    limit: int
    has_more: bool
    next_cursor: str | None


class ProductSearchResponse(Schema):
    items: list[ProductOut]
    meta: PageMeta


SORT_MAP = {
    ProductSort.RELEVANCE: ("-score", "-id"),
    ProductSort.NEWEST: ("-created_at", "-id"),
    ProductSort.PRICE_ASC: ("price", "id"),
    ProductSort.PRICE_DESC: ("-price", "-id"),
}


def encode_cursor(product: Product) -> str:
    return str(product.id)


def apply_cursor(qs: QuerySet[Product], cursor: str | None) -> QuerySet[Product]:
    if cursor is None:
        return qs
    return qs.filter(id__lt=int(cursor))


@router.get("", response={200: ProductSearchResponse})
def search_products(
    request,
    params: Query[ProductSearchQuery],
) -> ProductSearchResponse:
    qs = (
        Product.objects.select_related("brand")
        .filter(is_deleted=False)
    )

    qs = params.filter(qs)

    if params.in_stock is not None:
        qs = qs.filter(stock_quantity__gt=0) if params.in_stock else qs.filter(stock_quantity=0)

    qs = apply_cursor(qs, params.cursor)
    qs = qs.order_by(*SORT_MAP[params.sort])

    rows = list(qs[: params.limit + 1])
    items = rows[: params.limit]

    return ProductSearchResponse(
        items=[
            ProductOut(
                id=p.id,
                name=p.name,
                price=p.price,
                brand_name=p.brand.name if p.brand_id else None,
                thumbnail_url=p.thumbnail_url,
                status=p.status,
            )
            for p in items
        ],
        meta=PageMeta(
            limit=params.limit,
            has_more=len(rows) > params.limit,
            next_cursor=encode_cursor(items[-1]) if len(rows) > params.limit else None,
        ),
    )
```

**에러 응답 표준**

```json
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Validation failed",
  "status": 422,
  "detail": "One or more query parameters are invalid.",
  "instance": "/api/v1/products",
  "invalid_params": [
    {"name": "limit", "reason": "Input should be less than or equal to 100"}
  ]
}
```

```python
# config/api.py
from ninja import NinjaAPI
from ninja.errors import ValidationError
from products.api import router as products_router

api = NinjaAPI(version="1.0.0")


@api.exception_handler(ValidationError)
def validation_errors(request, exc):
    return api.create_response(
        request,
        {
            "type": "https://api.example.com/problems/validation-error",
            "title": "Validation failed",
            "status": 422,
            "detail": "One or more request parameters are invalid.",
            "instance": request.path,
            "invalid_params": [
                {"name": ".".join(map(str, e["loc"])), "reason": e["msg"]}
                for e in exc.errors
            ],
        },
        status=422,
    )


api.add_router("/v1/products", products_router)
```

**검증 기준**

- `GET /api/v1/products?limit=101` → `422` Problem Details.
- `sort=unknown` → `422`.
- `limit` 기본값은 `20`, 최대 `100`.
- 응답은 항상 `{items, meta}`.
- 상품 목록 쿼리는 `select_related("brand")` 기준으로 N+1이 없어야 한다.

---
> **관련 스킬 참조:**
> - API 설계 원칙 → **architecture-api** 스킬
> - Django Ninja 구현 → **implementation-django-ninja** 스킬