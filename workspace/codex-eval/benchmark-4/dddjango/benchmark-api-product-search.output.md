**상품 검색 API 팀 컨벤션**

기본 엔드포인트는 명사형 컬렉션으로 고정한다.

`GET /api/v1/products?q=phone&category_id=3&min_price=10000&max_price=500000&in_stock=true&sort=-price&limit=20&offset=0`

규칙:
- API는 DRF 없이 Django Ninja `Schema`, `FilterSchema`, `Router`만 사용한다.
- 목록 응답은 항상 `items/meta` envelope를 사용한다. 커스텀 envelope를 쓰므로 `@paginate`와 섞지 않는다.
- `sort`는 allow-list Enum으로만 받는다. 사용자 입력을 `order_by()`에 직접 넘기지 않는다.
- `limit` 기본값은 `20`, 최대값은 `100`, `offset`은 `0` 이상이다.
- 대용량/무한 스크롤 상품 목록은 cursor 방식으로 별도 확장한다. 일반 검색 결과 화면은 offset 기반을 표준으로 둔다.
- 모든 오류는 RFC 9457 Problem Details, `Content-Type: application/problem+json`으로 반환한다.
- validation error는 422로 통일하고 `invalid_params` 확장 필드를 사용한다.

```python
# products/api.py
from decimal import Decimal
from enum import Enum
from typing import Annotated

from django.db.models import QuerySet
from django.http import HttpRequest, JsonResponse
from ninja import FilterLookup, FilterSchema, Query, Router, Schema
from pydantic import Field, model_validator

from products.models import Product

router = Router(tags=["products"])


class ProductSort(str, Enum):
    relevance = "relevance"
    newest = "newest"
    price_asc = "price"
    price_desc = "-price"


class ProductFilter(FilterSchema):
    q: Annotated[
        str | None,
        FilterLookup(["name__icontains", "description__icontains"]),
    ] = Field(default=None, min_length=2, max_length=100)
    category_id: Annotated[int | None, FilterLookup("category_id")] = None
    brand_id: Annotated[int | None, FilterLookup("brand_id")] = None
    min_price: Annotated[Decimal | None, FilterLookup("price__gte")] = None
    max_price: Annotated[Decimal | None, FilterLookup("price__lte")] = None
    in_stock: Annotated[bool | None, FilterLookup("stock_quantity__gt")] = None

    @model_validator(mode="after")
    def validate_price_range(self):
        if self.min_price and self.max_price and self.min_price > self.max_price:
            raise ValueError("min_price must be less than or equal to max_price")
        return self


class ProductSearchQuery(Schema):
    sort: ProductSort = ProductSort.relevance
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ProductOut(Schema):
    id: int
    name: str
    price: Decimal
    thumbnail_url: str | None
    brand_name: str | None
    in_stock: bool


class PageMeta(Schema):
    limit: int
    offset: int
    total: int
    has_more: bool


class ProductSearchResponse(Schema):
    items: list[ProductOut]
    meta: PageMeta


SORT_MAP = {
    ProductSort.relevance: ("-updated_at", "-id"),
    ProductSort.newest: ("-created_at", "-id"),
    ProductSort.price_asc: ("price", "id"),
    ProductSort.price_desc: ("-price", "-id"),
}


@router.get("", response=ProductSearchResponse)
def search_products(
    request: HttpRequest,
    filters: Query[ProductFilter],
    params: Query[ProductSearchQuery],
) -> ProductSearchResponse:
    qs: QuerySet[Product] = Product.objects.select_related("brand").filter(is_active=True)
    qs = filters.filter(qs).order_by(*SORT_MAP[params.sort])

    total = qs.count()
    rows = qs[params.offset : params.offset + params.limit]

    return ProductSearchResponse(
        items=[
            ProductOut(
                id=p.id,
                name=p.name,
                price=p.price,
                thumbnail_url=p.thumbnail_url,
                brand_name=p.brand.name if p.brand_id else None,
                in_stock=p.stock_quantity > 0,
            )
            for p in rows
        ],
        meta=PageMeta(
            limit=params.limit,
            offset=params.offset,
            total=total,
            has_more=params.offset + params.limit < total,
        ),
    )
```

```python
# config/api.py
from django.http import JsonResponse
from ninja import NinjaAPI
from ninja.errors import ValidationError

from products.api import router as products_router

api = NinjaAPI(version="1.0.0")
api.add_router("/products", products_router)


@api.exception_handler(ValidationError)
def validation_error_handler(request, exc):
    errors_value = getattr(exc, "errors", [])
    errors = errors_value() if callable(errors_value) else errors_value

    return JsonResponse(
        {
            "type": "https://api.example.com/problems/validation-error",
            "title": "Validation Failed",
            "status": 422,
            "detail": "Request validation failed.",
            "instance": request.path,
            "invalid_params": [
                {
                    "name": ".".join(str(part) for part in err.get("loc", [])),
                    "reason": err.get("msg", "Invalid value."),
                }
                for err in errors
            ],
        },
        status=422,
        content_type="application/problem+json",
    )
```

검증 기준:
- `python manage.py check`
- `pytest`
- 검색 API 테스트에서 정상 응답은 `items/meta` 구조를 assert한다.
- 잘못된 `limit`, `sort`, 가격 범위 요청은 422와 `application/problem+json`, `invalid_params`를 assert한다.

---
> **관련 스킬 참조:**
> - API URL/오류/페이지네이션 설계 → **architecture-api** 스킬
> - Django Ninja Schema/Router/Filter 구현 → **implementation-django-ninja** 스킬