`/private/tmp/dddjango-codex-eval`은 현재 비어 있고 읽기 전용이라 파일 생성은 하지 않았습니다. 아래는 `Product` 모델이 있다는 전제로 정리한 Django Ninja 팀 컨벤션 설계안입니다.

**상품 검색 API**
```http
GET /api/v1/products
```

목록 리소스이므로 URL은 복수 명사 `products`를 사용하고, 검색/필터/정렬/페이지네이션은 모두 query parameter로 처리합니다.

예시:
```http
GET /api/v1/products?q=keyboard&category_id=10&min_price=10000&max_price=90000&in_stock=true&sort=-created_at&limit=20&cursor=...
```

**Query 컨벤션**
| 파라미터 | 설명 |
|---|---|
| `q` | 상품명, 설명, SKU 등 통합 검색어 |
| `category_id` | 카테고리 단일 필터 |
| `brand_id` | 브랜드 단일 필터 |
| `min_price`, `max_price` | 가격 범위 |
| `in_stock` | 재고 보유 여부 |
| `is_active` | 판매 노출 여부 |
| `created_from`, `created_to` | 등록일 범위 |
| `sort` | allow-list 기반 정렬 |
| `limit` | 페이지 크기, 기본 20, 최대 100 |
| `cursor` | 다음 페이지 커서 |

정렬 값은 반드시 allow-list로 제한합니다. 사용자 입력을 그대로 `order_by()`에 넣지 않습니다.

허용 정렬:
```text
created_at
-created_at
price
-price
name
-name
popularity
-popularity
```

**응답 Envelope**
검색 API는 Django Ninja 내장 `@paginate` 대신 팀 표준 envelope를 직접 사용합니다. `@paginate`와 커스텀 `items/meta` 응답을 섞지 않는 것이 컨벤션입니다.

```json
{
  "items": [
    {
      "id": 1,
      "name": "Keyboard",
      "slug": "keyboard",
      "price": "39000.00",
      "currency": "KRW",
      "thumbnail_url": "https://example.com/image.jpg",
      "in_stock": true,
      "created_at": "2026-05-05T10:00:00+09:00"
    }
  ],
  "meta": {
    "limit": 20,
    "next_cursor": "eyJjcmVhdGVkX2F0IjoiLi4uIiwiaWQiOjF9",
    "has_more": true
  }
}
```

**Django Ninja 스키마 예시**
```python
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Optional

from ninja import FilterSchema, Schema
from pydantic import Field


class ProductSort(StrEnum):
    created_at = "created_at"
    created_at_desc = "-created_at"
    price = "price"
    price_desc = "-price"
    name = "name"
    name_desc = "-name"
    popularity = "popularity"
    popularity_desc = "-popularity"


class ProductSearchQuery(FilterSchema):
    q: Optional[str] = Field(default=None, min_length=1, max_length=100)
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    min_price: Optional[Decimal] = Field(default=None, ge=0)
    max_price: Optional[Decimal] = Field(default=None, ge=0)
    in_stock: Optional[bool] = None
    is_active: Optional[bool] = True
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    sort: ProductSort = ProductSort.created_at_desc
    limit: int = Field(default=20, ge=1, le=100)
    cursor: Optional[str] = None


class ProductOut(Schema):
    id: int
    name: str
    slug: str
    price: Decimal
    currency: str
    thumbnail_url: Optional[str] = None
    in_stock: bool
    created_at: datetime


class PageMeta(Schema):
    limit: int
    next_cursor: Optional[str] = None
    has_more: bool


class ProductSearchOut(Schema):
    items: list[ProductOut]
    meta: PageMeta
```

**라우터 예시**
```python
from django.db.models import Q
from ninja import Query, Router

router = Router(tags=["products"])


@router.get("", response={200: ProductSearchOut})
def search_products(request, filters: Query[ProductSearchQuery]) -> ProductSearchOut:
    qs = Product.objects.all()

    if filters.q:
        qs = qs.filter(
            Q(name__icontains=filters.q)
            | Q(description__icontains=filters.q)
            | Q(sku__icontains=filters.q)
        )

    if filters.category_id is not None:
        qs = qs.filter(category_id=filters.category_id)
    if filters.brand_id is not None:
        qs = qs.filter brand_id=filters.brand_id)
    if filters.min_price is not None:
        qs = qs.filter(price__gte=filters.min_price)
    if filters.max_price is not None:
        qs = qs.filter(price__lte=filters.max_price)
    if filters.in_stock is not None:
        qs = qs.filter(stock_quantity__gt=0 if filters.in_stock else 0)
    if filters.is_active is not None:
        qs = qs.filter(is_active=filters.is_active)

    qs = qs.order_by(filters.sort.value, "-id")

    items, next_cursor, has_more = paginate_by_cursor(qs, filters.cursor, filters.limit)

    return ProductSearchOut(
        items=items,
        meta=PageMeta(
            limit=filters.limit,
            next_cursor=next_cursor,
            has_more=has_more,
        ),
    )
```

위 예시의 `brand_id` 라인은 실제 코드에서는 아래처럼 수정되어야 합니다.

```python
qs = qs.filter(brand_id=filters.brand_id)
```

**에러 응답 표준**
모든 API 에러는 RFC 9457 Problem Details 형식을 사용합니다.

Content-Type:
```http
application/problem+json
```

기본 형식:
```json
{
  "type": "https://api.example.com/problems/invalid-query",
  "title": "Invalid Query Parameter",
  "status": 422,
  "detail": "One or more query parameters are invalid.",
  "instance": "/api/v1/products",
  "invalid_params": [
    {
      "name": "sort",
      "reason": "Unsupported sort field."
    }
  ]
}
```

상태 코드 컨벤션:
| 상태 코드 | 사용 기준 |
|---|---|
| `200` | 검색 성공 |
| `400` | cursor 디코딩 실패 등 요청 형식 오류 |
| `401` | 인증 필요 |
| `403` | 권한 부족 |
| `404` | 단건 상품 없음 |
| `409` | 상태 충돌 |
| `422` | query/body 검증 실패 |
| `429` | rate limit 초과 |
| `500` | 서버 내부 오류 |

**조립 구조**
```python
# config/api.py
from ninja import NinjaAPI
from products.api import router as products_router

api = NinjaAPI(title="Commerce API", version="1.0.0")
api.add_router("/v1/products", products_router)
```

```python
# config/urls.py
from django.urls import path
from config.api import api

urlpatterns = [
    path("api/", api.urls),
]
```

---
> **관련 스킬 참조:**
> - API 리소스/상태 코드/버저닝 → **architecture-api** 스킬
> - Django Ninja Schema/Router/FilterSchema 구현 → **implementation-django-ninja** 스킬