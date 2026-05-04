작업 디렉터리에는 `config.toml`이 없어 별도 팀 지침은 확인하지 못했습니다. 아래는 Django Ninja 기준으로 바로 팀 컨벤션 문서에 넣을 수 있는 형태의 설계안입니다.

**상품 검색 API 컨벤션**

기본 원칙:

- 검색 API는 `GET /api/v1/products` 단일 엔드포인트를 사용한다.
- 필터는 query parameter로 표현한다.
- 정렬은 `sort` 하나로 통일한다.
- 페이지네이션은 `page`, `page_size` 기반 offset pagination을 기본으로 한다.
- 응답은 항상 동일한 envelope 구조를 사용한다.
- 에러 응답은 `code`, `message`, `details`를 포함한다.

```http
GET /api/v1/products?q=keyboard&category_id=12&min_price=10000&max_price=50000&brand=logitech&is_active=true&sort=-created_at&page=1&page_size=20
```

**Query Parameters**

```python
from typing import Literal
from ninja import Schema, Query
from pydantic import Field


class ProductSearchQuery(Schema):
    q: str | None = Field(None, description="상품명/설명 통합 검색어")

    category_id: int | None = None
    brand: str | None = None
    min_price: int | None = Field(None, ge=0)
    max_price: int | None = Field(None, ge=0)
    is_active: bool | None = None
    in_stock: bool | None = None

    sort: Literal[
        "created_at",
        "-created_at",
        "price",
        "-price",
        "name",
        "-name",
        "sales_count",
        "-sales_count",
    ] = "-created_at"

    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
```

**필터 컨벤션**

필터 이름은 명확한 도메인 이름을 사용한다.

권장:

```text
category_id
brand
min_price
max_price
is_active
in_stock
```

비권장:

```text
cat
brandName
price_from
available
```

범위 필터는 `min_`, `max_` prefix를 사용한다.

```http
?min_price=10000&max_price=50000
```

boolean 필터는 `is_`, `has_`, `in_` 계열을 사용한다.

```http
?is_active=true&in_stock=false
```

검색어는 `q`로 통일한다.

```http
?q=무선 키보드
```

**정렬 컨벤션**

정렬은 `sort` parameter 하나만 사용한다.

- 오름차순: `price`
- 내림차순: `-price`

```http
?sort=price
?sort=-created_at
```

허용된 정렬 필드만 서버에서 whitelist로 처리한다.

```python
SORT_MAP = {
    "created_at": "created_at",
    "-created_at": "-created_at",
    "price": "price",
    "-price": "-price",
    "name": "name",
    "-name": "-name",
    "sales_count": "sales_count",
    "-sales_count": "-sales_count",
}
```

**페이지네이션 응답**

응답 구조는 `items`와 `meta`를 분리한다.

```json
{
  "items": [
    {
      "id": 1,
      "name": "무선 키보드",
      "price": 39000,
      "brand": "Logitech",
      "thumbnail_url": "https://example.com/product.jpg",
      "is_active": true,
      "stock_count": 12,
      "created_at": "2026-05-04T10:00:00+09:00"
    }
  ],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total_count": 145,
    "total_pages": 8,
    "has_next": true,
    "has_previous": false
  }
}
```

Django Ninja schema 예시:

```python
from datetime import datetime
from ninja import Schema


class ProductOut(Schema):
    id: int
    name: str
    price: int
    brand: str | None
    thumbnail_url: str | None
    is_active: bool
    stock_count: int
    created_at: datetime


class PaginationMeta(Schema):
    page: int
    page_size: int
    total_count: int
    total_pages: int
    has_next: bool
    has_previous: bool


class ProductSearchResponse(Schema):
    items: list[ProductOut]
    meta: PaginationMeta
```

**Endpoint 구현 예시**

```python
import math
from django.db.models import Q
from ninja import Router, Query

router = Router(tags=["Products"])


@router.get("", response={200: ProductSearchResponse})
def search_products(request, params: ProductSearchQuery = Query(...)):
    qs = Product.objects.all()

    if params.q:
        qs = qs.filter(
            Q(name__icontains=params.q) |
            Q(description__icontains=params.q)
        )

    if params.category_id is not None:
        qs = qs.filter(category_id=params.category_id)

    if params.brand:
        qs = qs.filter(brand__iexact=params.brand)

    if params.min_price is not None:
        qs = qs.filter(price__gte=params.min_price)

    if params.max_price is not None:
        qs = qs.filter(price__lte=params.max_price)

    if params.is_active is not None:
        qs = qs.filter(is_active=params.is_active)

    if params.in_stock is not None:
        qs = qs.filter(stock_count__gt=0 if params.in_stock else 0)

    qs = qs.order_by(SORT_MAP[params.sort], "id")

    total_count = qs.count()
    offset = (params.page - 1) * params.page_size
    items = qs[offset:offset + params.page_size]

    total_pages = math.ceil(total_count / params.page_size) if total_count else 0

    return {
        "items": items,
        "meta": {
            "page": params.page,
            "page_size": params.page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": params.page < total_pages,
            "has_previous": params.page > 1,
        },
    }
```

**에러 응답 표준**

모든 에러는 아래 구조를 따른다.

```json
{
  "error": {
    "code": "INVALID_QUERY_PARAMETER",
    "message": "요청 파라미터가 올바르지 않습니다.",
    "details": [
      {
        "field": "page_size",
        "message": "page_size는 1 이상 100 이하이어야 합니다."
      }
    ]
  }
}
```

Schema:

```python
class ErrorDetail(Schema):
    field: str | None = None
    message: str


class ErrorResponse(Schema):
    code: str
    message: str
    details: list[ErrorDetail] = []
```

HTTP status별 에러 코드:

```text
400 INVALID_QUERY_PARAMETER
400 INVALID_FILTER_RANGE
401 UNAUTHORIZED
403 FORBIDDEN
404 PRODUCT_NOT_FOUND
422 VALIDATION_ERROR
429 RATE_LIMITED
500 INTERNAL_SERVER_ERROR
```

필터 범위 검증 예시:

```python
from ninja.errors import HttpError

if (
    params.min_price is not None
    and params.max_price is not None
    and params.min_price > params.max_price
):
    raise HttpError(400, "INVALID_FILTER_RANGE")
```

**팀 규칙 요약**

- 검색 엔드포인트는 collection resource에 `GET`으로 둔다.
- query parameter는 snake_case만 사용한다.
- 검색어는 항상 `q`를 사용한다.
- 범위 필터는 `min_`, `max_` prefix를 사용한다.
- 정렬은 `sort` 하나로 통일하고, 내림차순은 `-field`로 표현한다.
- 기본 정렬은 `-created_at`이다.
- 페이지네이션은 `page`, `page_size`를 사용한다.
- `page_size` 최대값은 `100`으로 제한한다.
- 응답은 `{ items, meta }` 구조를 사용한다.
- 에러는 `{ error: { code, message, details } }` 구조를 사용한다.
- DB 필드명을 그대로 외부에 노출하지 말고, 허용된 필터와 정렬 필드만 whitelist로 처리한다.