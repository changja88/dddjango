Django Ninja 기준으로 상품 검색 API 팀 컨벤션을 아래처럼 잡겠습니다. 현재 workspace가 비어 있고 read-only라 파일 생성은 하지 않았고, 붙여 넣어 적용할 수 있는 설계/코드 형태로 정리합니다.

**API 표준**

기본 엔드포인트:

```http
GET /api/v1/products/
```

리소스는 복수 명사 `products`만 사용하고, `search-products`, `filter-products` 같은 동사형 URL은 쓰지 않습니다. 검색, 필터, 정렬, 페이지네이션은 모두 query parameter로 표현합니다.

요청 예시:

```http
GET /api/v1/products/?q=keyboard&category_id=12&brand=logitech&min_price=10000&max_price=200000&is_active=true&ordering=-created_at&limit=20&cursor=eyJjcmVhdGVkX2F0Ijoi...
```

**Query Parameter 컨벤션**

필터:

| 파라미터 | 타입 | 의미 |
|---|---:|---|
| `q` | string | 상품명/설명 통합 검색 |
| `category_id` | int | 카테고리 ID |
| `brand` | string | 브랜드명 |
| `min_price` | int | 최소 가격 |
| `max_price` | int | 최대 가격 |
| `is_active` | bool | 판매 가능 여부 |
| `created_from` | datetime | 생성일 시작 |
| `created_to` | datetime | 생성일 종료 |

정렬:

| 파라미터 | 허용값 |
|---|---|
| `ordering` | `created_at`, `-created_at`, `price`, `-price`, `name`, `-name`, `updated_at`, `-updated_at` |

규칙:

- 사용자 입력을 `order_by()`에 직접 넣지 않습니다.
- 반드시 allow-list 또는 Enum으로 제한합니다.
- 기본 정렬은 `-created_at`, 보조 정렬은 `-id`를 붙여 커서 안정성을 확보합니다.
- 가격 필터는 `min_price <= max_price`를 검증합니다.

페이지네이션:

| 파라미터 | 타입 | 기본값 | 제한 |
|---|---:|---:|---:|
| `limit` | int | 20 | 최대 100 |
| `cursor` | string | null | opaque base64 token |

검색 API는 데이터 변경 중 누락/중복 가능성을 줄이기 위해 cursor pagination을 기본으로 둡니다. 관리자 화면처럼 랜덤 페이지 이동이 필요한 API만 별도로 offset/page 방식 사용을 허용합니다.

**응답 Envelope**

목록 응답은 `items/meta` envelope로 통일합니다. Django Ninja의 `@paginate`를 쓰면 내장 응답 형식이 고정되므로, 팀 표준 envelope가 필요하면 직접 슬라이싱하거나 커스텀 paginator를 사용합니다.

```json
{
  "items": [
    {
      "id": 1,
      "name": "MX Keys",
      "brand": "Logitech",
      "price": 129000,
      "currency": "KRW",
      "is_active": true,
      "created_at": "2026-05-05T00:00:00+09:00"
    }
  ],
  "meta": {
    "limit": 20,
    "next_cursor": "eyJjcmVhdGVkX2F0Ijoi...",
    "has_more": true
  }
}
```

**Django Ninja 예시**

`products/schemas.py`

```python
from datetime import datetime
from enum import StrEnum
from typing import Optional

from ninja import Schema


class ProductOrdering(StrEnum):
    created_at = "created_at"
    created_at_desc = "-created_at"
    price = "price"
    price_desc = "-price"
    name = "name"
    name_desc = "-name"
    updated_at = "updated_at"
    updated_at_desc = "-updated_at"


class ProductSearchFilters(Schema):
    q: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    is_active: Optional[bool] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    ordering: ProductOrdering = ProductOrdering.created_at_desc
    limit: int = 20
    cursor: Optional[str] = None


class ProductOut(Schema):
    id: int
    name: str
    brand: Optional[str]
    price: int
    currency: str
    is_active: bool
    created_at: datetime


class ProductListMeta(Schema):
    limit: int
    next_cursor: Optional[str]
    has_more: bool


class ProductListOut(Schema):
    items: list[ProductOut]
    meta: ProductListMeta


class ProblemDetail(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str
```

`products/api.py`

```python
from django.db.models import Q, QuerySet
from ninja import Query, Router
from ninja.responses import codes_4xx

from products.models import Product
from products.schemas import ProblemDetail, ProductListOut, ProductSearchFilters

router = Router(tags=["products"])

ORDERING_MAP = {
    "created_at": ("created_at", "id"),
    "-created_at": ("-created_at", "-id"),
    "price": ("price", "id"),
    "-price": ("-price", "-id"),
    "name": ("name", "id"),
    "-name": ("-name", "-id"),
    "updated_at": ("updated_at", "id"),
    "-updated_at": ("-updated_at", "-id"),
}


@router.get("/", response={200: ProductListOut, codes_4xx: ProblemDetail})
def search_products(
    request,
    filters: Query[ProductSearchFilters],
) -> ProductListOut:
    if filters.limit < 1 or filters.limit > 100:
        return 422, {
            "type": "https://api.example.com/problems/invalid-query",
            "title": "Invalid query parameter",
            "status": 422,
            "detail": "limit must be between 1 and 100.",
            "instance": request.path,
        }

    if (
        filters.min_price is not None
        and filters.max_price is not None
        and filters.min_price > filters.max_price
    ):
        return 422, {
            "type": "https://api.example.com/problems/invalid-query",
            "title": "Invalid query parameter",
            "status": 422,
            "detail": "min_price must be less than or equal to max_price.",
            "instance": request.path,
        }

    queryset = build_product_search_queryset(filters)

    page_items, next_cursor, has_more = paginate_products(
        queryset=queryset,
        limit=filters.limit,
        cursor=filters.cursor,
    )

    return {
        "items": page_items,
        "meta": {
            "limit": filters.limit,
            "next_cursor": next_cursor,
            "has_more": has_more,
        },
    }


def build_product_search_queryset(
    filters: ProductSearchFilters,
) -> QuerySet[Product]:
    queryset = Product.objects.select_related("category")

    if filters.q:
        queryset = queryset.filter(
            Q(name__icontains=filters.q) | Q(description__icontains=filters.q)
        )

    if filters.category_id is not None:
        queryset = queryset.filter(category_id=filters.category_id)

    if filters.brand:
        queryset = queryset.filter(brand__iexact=filters.brand)

    if filters.min_price is not None:
        queryset = queryset.filter(price__gte=filters.min_price)

    if filters.max_price is not None:
        queryset = queryset.filter(price__lte=filters.max_price)

    if filters.is_active is not None:
        queryset = queryset.filter(is_active=filters.is_active)

    if filters.created_from is not None:
        queryset = queryset.filter(created_at__gte=filters.created_from)

    if filters.created_to is not None:
        queryset = queryset.filter(created_at__lte=filters.created_to)

    return queryset.order_by(*ORDERING_MAP[filters.ordering.value])
```

`paginate_products()`는 커서를 base64 JSON으로 인코딩/디코딩하는 유틸로 분리하는 것을 권장합니다. 커서 필드는 정렬 기준과 `id`를 함께 담아야 합니다.

예시 커서 payload:

```json
{
  "ordering": "-created_at",
  "created_at": "2026-05-05T00:00:00+09:00",
  "id": 100
}
```

**에러 응답 표준**

모든 API 에러는 RFC 9457 Problem Details 형식을 사용합니다.

`Content-Type`:

```http
application/problem+json
```

기본 형식:

```json
{
  "type": "https://api.example.com/problems/invalid-query",
  "title": "Invalid query parameter",
  "status": 422,
  "detail": "min_price must be less than or equal to max_price.",
  "instance": "/api/v1/products/"
}
```

상태 코드 컨벤션:

| 코드 | 사용 기준 |
|---:|---|
| 400 | JSON 파싱 실패, 요청 형식 오류 |
| 401 | 인증 없음 |
| 403 | 권한 없음 |
| 404 | 리소스 없음 |
| 409 | 중복/상태 충돌 |
| 422 | 필터 조합, 의미 검증 실패 |
| 429 | Rate limit 초과 |
| 500 | 서버 오류 |

Django Ninja에서는 `@api.exception_handler()`로 validation error, domain error, unexpected error를 Problem Details로 변환하는 전역 핸들러를 둡니다.

**라우터 합성**

`config/api.py`

```python
from ninja import NinjaAPI

from products.api import router as products_router

api = NinjaAPI(version="1.0.0")
api.add_router("/v1/products/", products_router)
```

`config/urls.py`

```python
from django.urls import path

from config.api import api

urlpatterns = [
    path("api/", api.urls),
]
```

---
> **관련 스킬 참조:**
> - API 설계 원칙과 에러 응답 표준 → **architecture-api** 스킬
> - Django Ninja 구현, Schema, Router, Filter, Pagination → **implementation-django-ninja** 스킬