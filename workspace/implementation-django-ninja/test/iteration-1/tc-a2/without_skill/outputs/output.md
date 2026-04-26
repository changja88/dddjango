# Django Ninja 상품 목록 API (FilterSchema + 커서 기반 페이지네이션)

## 1. Model 정의

```python
# products/models.py
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "categories"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, db_index=True)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
```

## 2. Schema 정의

```python
# products/schemas.py
import base64
import json
from datetime import datetime
from decimal import Decimal
from typing import Optional

from ninja import FilterSchema, Field, Schema
from pydantic import field_validator


# ── Filter Schema ──────────────────────────────────────────────

class ProductFilterSchema(FilterSchema):
    """상품 목록 필터링을 위한 FilterSchema."""

    # 카테고리 필터 (다중 선택)
    category_ids: Optional[list[int]] = Field(
        None,
        q="category_id__in",
        description="필터링할 카테고리 ID 목록",
    )

    # 가격 범위 필터
    price_min: Optional[Decimal] = Field(
        None,
        q="price__gte",
        description="최소 가격",
    )
    price_max: Optional[Decimal] = Field(
        None,
        q="price__lte",
        description="최대 가격",
    )

    # 이름 검색 (부분 일치)
    name: Optional[str] = Field(
        None,
        q="name__icontains",
        description="상품명 부분 일치 검색",
    )

    # 재고 유무 필터
    in_stock: Optional[bool] = Field(
        None,
        description="재고 유무 (true: 재고 있음, false: 재고 없음)",
    )

    def custom_expression(self):
        """in_stock 필드를 커스텀 Q 표현식으로 변환."""
        from django.db.models import Q

        q = Q()
        if self.in_stock is True:
            q &= Q(stock__gt=0)
        elif self.in_stock is False:
            q &= Q(stock=0)
        return q


# ── Sorting ────────────────────────────────────────────────────

SORT_OPTIONS = {
    "price_asc": "price",
    "price_desc": "-price",
    "name_asc": "name",
    "name_desc": "-name",
    "newest": "-created_at",
    "oldest": "created_at",
}


# ── Cursor Pagination ─────────────────────────────────────────

def encode_cursor(values: dict) -> str:
    """커서 값을 base64 문자열로 인코딩."""
    raw = json.dumps(values, default=str)
    return base64.urlsafe_b64encode(raw.encode()).decode()


def decode_cursor(cursor: str) -> dict:
    """base64 커서 문자열을 딕셔너리로 디코딩."""
    raw = base64.urlsafe_b64decode(cursor.encode()).decode()
    return json.loads(raw)


# ── Response Schemas ───────────────────────────────────────────

class CategoryOut(Schema):
    id: int
    name: str


class ProductOut(Schema):
    id: int
    name: str
    price: Decimal
    stock: int
    category: CategoryOut
    created_at: datetime
    updated_at: datetime


class CursorInfo(Schema):
    next_cursor: Optional[str] = None
    has_next: bool


class ProductListResponse(Schema):
    items: list[ProductOut]
    cursor: CursorInfo
    count: int
```

## 3. API 엔드포인트

```python
# products/api.py
from typing import Optional

from django.db.models import QuerySet
from ninja import Query, Router

from .models import Product
from .schemas import (
    SORT_OPTIONS,
    CursorInfo,
    ProductFilterSchema,
    ProductListResponse,
    ProductOut,
    decode_cursor,
    encode_cursor,
)

router = Router(tags=["Products"])

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def _apply_cursor(
    qs: QuerySet,
    cursor: str | None,
    sort_field: str,
) -> QuerySet:
    """커서 기반으로 queryset에 WHERE 조건을 추가."""
    if cursor is None:
        return qs

    decoded = decode_cursor(cursor)
    value = decoded["v"]
    pk = decoded["pk"]

    is_desc = sort_field.startswith("-")
    field = sort_field.lstrip("-")

    if is_desc:
        # 내림차순: 커서 값보다 작거나, 같으면 pk가 더 큰 것
        from django.db.models import Q

        qs = qs.filter(
            Q(**{f"{field}__lt": value})
            | Q(**{field: value, "pk__gt": pk})
        )
    else:
        # 오름차순: 커서 값보다 크거나, 같으면 pk가 더 큰 것
        from django.db.models import Q

        qs = qs.filter(
            Q(**{f"{field}__gt": value})
            | Q(**{field: value, "pk__gt": pk})
        )

    return qs


def _build_cursor(product: Product, sort_field: str) -> str:
    """마지막 항목에서 다음 커서를 생성."""
    field = sort_field.lstrip("-")
    value = getattr(product, field)
    return encode_cursor({"v": value, "pk": product.pk})


@router.get(
    "/",
    response=ProductListResponse,
    summary="상품 목록 조회",
    description="필터, 정렬, 커서 기반 페이지네이션을 지원하는 상품 목록 API",
)
def list_products(
    request,
    filters: ProductFilterSchema = Query(...),
    sort: str = Query("newest", description="정렬 기준: price_asc, price_desc, name_asc, name_desc, newest, oldest"),
    cursor: Optional[str] = Query(None, description="다음 페이지 커서"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="페이지 크기 (1~100)"),
):
    # 1) 기본 queryset + select_related
    qs = Product.objects.select_related("category").all()

    # 2) FilterSchema 적용
    qs = filters.filter(qs)

    # 3) 정렬
    sort_field = SORT_OPTIONS.get(sort, "-created_at")
    qs = qs.order_by(sort_field, "pk")  # tie-breaker로 pk 사용

    # 4) 커서 적용
    qs = _apply_cursor(qs, cursor, sort_field)

    # 5) 페이지네이션 (page_size + 1로 다음 페이지 존재 여부 확인)
    items = list(qs[: page_size + 1])
    has_next = len(items) > page_size
    items = items[:page_size]

    # 6) 다음 커서 생성
    next_cursor = None
    if has_next and items:
        next_cursor = _build_cursor(items[-1], sort_field)

    return ProductListResponse(
        items=[ProductOut.from_orm(item) for item in items],
        cursor=CursorInfo(
            next_cursor=next_cursor,
            has_next=has_next,
        ),
        count=len(items),
    )
```

## 4. URL 등록

```python
# products/urls.py  (or project-level api.py)
from ninja import NinjaAPI

from products.api import router as products_router

api = NinjaAPI(
    title="Product API",
    version="1.0.0",
)

api.add_router("/products", products_router)
```

```python
# config/urls.py
from django.urls import path
from products.urls import api

urlpatterns = [
    path("api/", api.urls),
]
```

## 5. 사용 예시

### 기본 조회 (최신순 20개)
```
GET /api/products/
```

### 카테고리 다중 필터 + 가격 범위
```
GET /api/products/?category_ids=1&category_ids=3&price_min=10000&price_max=50000
```

### 이름 검색 + 재고 있는 상품만
```
GET /api/products/?name=키보드&in_stock=true
```

### 가격 낮은 순 정렬 + 페이지 크기 지정
```
GET /api/products/?sort=price_asc&page_size=10
```

### 다음 페이지 (커서 사용)
```
GET /api/products/?sort=price_asc&page_size=10&cursor=eyJ2IjogIjI1MDAwLjAwIiwgInBrIjogNDJ9
```

### 복합 필터 조합
```
GET /api/products/?category_ids=2&category_ids=5&price_min=5000&name=마우스&in_stock=true&sort=price_desc&page_size=15
```

## 6. 응답 예시

```json
{
  "items": [
    {
      "id": 42,
      "name": "무선 키보드 MK-200",
      "price": "25000.00",
      "stock": 150,
      "category": {
        "id": 1,
        "name": "키보드"
      },
      "created_at": "2026-04-01T09:30:00Z",
      "updated_at": "2026-04-03T14:20:00Z"
    },
    {
      "id": 38,
      "name": "기계식 키보드 PRO",
      "price": "89000.00",
      "stock": 45,
      "category": {
        "id": 1,
        "name": "키보드"
      },
      "created_at": "2026-03-28T11:00:00Z",
      "updated_at": "2026-04-02T08:15:00Z"
    }
  ],
  "cursor": {
    "next_cursor": "eyJ2IjogIjg5MDAwLjAwIiwgInBrIjogMzh9",
    "has_next": true
  },
  "count": 2
}
```

## 설계 요약

| 요구사항 | 구현 방식 |
|---|---|
| 카테고리 다중 필터 | `FilterSchema` - `category_id__in` |
| 가격 범위 필터 | `FilterSchema` - `price__gte`, `price__lte` |
| 이름 부분 검색 | `FilterSchema` - `name__icontains` |
| 재고 유무 필터 | `FilterSchema` - `custom_expression()` |
| 정렬 | `SORT_OPTIONS` 딕셔너리 매핑 + `order_by` |
| 커서 페이지네이션 | base64 인코딩 커서, `page_size + 1` 패턴 |
