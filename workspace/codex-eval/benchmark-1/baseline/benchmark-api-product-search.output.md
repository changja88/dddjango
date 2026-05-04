`/private/tmp/dddjango-codex-eval`에는 `config.toml`이나 실제 Django 프로젝트 파일이 없어, 팀 컨벤션 문서 형태로 설계안을 정리합니다.

**상품 검색 API**

```http
GET /api/v1/products
```

상품 목록 검색은 `GET` 쿼리 파라미터 기반으로 통일합니다. 검색 조건은 모두 선택값이며, 조건이 없으면 기본 최신순 목록을 반환합니다.

```python
from typing import Literal
from ninja import Schema, Query
from pydantic import Field


class ProductSearchQuery(Schema):
    q: str | None = Field(None, description="상품명/브랜드/키워드 검색")
    category_id: int | None = None
    brand_id: int | None = None
    min_price: int | None = Field(None, ge=0)
    max_price: int | None = Field(None, ge=0)
    in_stock: bool | None = None
    status: Literal["active", "sold_out", "hidden"] | None = None

    sort: Literal[
        "latest",
        "price_asc",
        "price_desc",
        "popular",
        "rating_desc",
    ] = "latest"

    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
```

**필터 컨벤션**

필터는 명시적인 필드명만 허용합니다.

```http
GET /api/v1/products?q=노트북&category_id=3&min_price=500000&max_price=2000000&in_stock=true
```

권장 규칙:

- `q`: 부분 검색. 상품명, 브랜드명, 태그 등 서비스 정책에 맞는 검색 대상만 포함
- `min_price`, `max_price`: 가격 범위
- `*_id`: FK 필터는 객체명이 아니라 ID 기준
- `in_stock=true`: 재고 있는 상품만
- 알 수 없는 필터는 무시하지 않고 `400` 응답
- `min_price > max_price`는 `400 INVALID_FILTER`

**정렬 컨벤션**

정렬은 `sort` 하나로만 받습니다. 클라이언트가 ORM 필드명을 직접 넘기지 않도록 합니다.

```http
GET /api/v1/products?sort=price_asc
```

서버 매핑 예시:

```python
SORT_MAP = {
    "latest": "-created_at",
    "price_asc": "price",
    "price_desc": "-price",
    "popular": "-sales_count",
    "rating_desc": "-rating",
}
```

기본값은 `latest`입니다. 지원하지 않는 정렬값은 `400 INVALID_SORT`로 응답합니다.

**페이지네이션 컨벤션**

기본은 page-based pagination으로 통일합니다.

```json
{
  "items": [
    {
      "id": 1,
      "name": "상품명",
      "brand_name": "브랜드",
      "price": 12000,
      "discount_price": 9900,
      "thumbnail_url": "https://...",
      "in_stock": true,
      "rating": 4.7
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 134,
    "total_pages": 7,
    "has_next": true,
    "has_previous": false
  }
}
```

응답 스키마 예시:

```python
class ProductListItem(Schema):
    id: int
    name: str
    brand_name: str | None
    price: int
    discount_price: int | None
    thumbnail_url: str | None
    in_stock: bool
    rating: float | None


class PaginationMeta(Schema):
    page: int
    page_size: int
    total_count: int
    total_pages: int
    has_next: bool
    has_previous: bool


class ProductSearchResponse(Schema):
    items: list[ProductListItem]
    pagination: PaginationMeta
```

**에러 응답 표준**

모든 API 에러는 아래 형식으로 통일합니다.

```json
{
  "error": {
    "code": "INVALID_FILTER",
    "message": "min_price는 max_price보다 클 수 없습니다.",
    "details": {
      "field": "min_price"
    }
  }
}
```

표준 코드:

| HTTP | code | 사용 상황 |
|---:|---|---|
| 400 | `INVALID_QUERY` | 쿼리 파라미터 형식 오류 |
| 400 | `INVALID_FILTER` | 필터 조합 오류 |
| 400 | `INVALID_SORT` | 허용하지 않는 정렬값 |
| 400 | `INVALID_PAGINATION` | page/page_size 범위 오류 |
| 401 | `UNAUTHORIZED` | 인증 필요 |
| 403 | `FORBIDDEN` | 권한 없음 |
| 500 | `INTERNAL_ERROR` | 서버 오류 |

Django Ninja 라우터 예시:

```python
@router.get("/products", response={200: ProductSearchResponse})
def search_products(request, query: ProductSearchQuery = Query(...)):
    if query.min_price and query.max_price and query.min_price > query.max_price:
        raise ApiError(
            code="INVALID_FILTER",
            message="min_price는 max_price보다 클 수 없습니다.",
            status_code=400,
            details={"field": "min_price"},
        )

    qs = Product.objects.filter(status="active")

    if query.q:
        qs = qs.filter(name__icontains=query.q)

    if query.category_id:
        qs = qs.filter(category_id=query.category_id)

    if query.brand_id:
        qs = qs.filter(brand_id=query.brand_id)

    if query.min_price is not None:
        qs = qs.filter(price__gte=query.min_price)

    if query.max_price is not None:
        qs = qs.filter(price__lte=query.max_price)

    if query.in_stock is not None:
        qs = qs.filter(stock_quantity__gt=0) if query.in_stock else qs.filter(stock_quantity=0)

    qs = qs.order_by(SORT_MAP[query.sort])

    total_count = qs.count()
    offset = (query.page - 1) * query.page_size
    items = qs[offset : offset + query.page_size]

    return {
        "items": items,
        "pagination": build_pagination(
            page=query.page,
            page_size=query.page_size,
            total_count=total_count,
        ),
    }
```

팀 컨벤션 핵심은 `필터는 명시 필드`, `정렬은 enum`, `페이지네이션은 공통 메타`, `에러는 code/message/details 고정`입니다.