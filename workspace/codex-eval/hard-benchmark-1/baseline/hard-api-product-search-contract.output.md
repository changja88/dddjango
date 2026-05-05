아래는 팀 표준 문서로 바로 붙여 넣을 수 있는 Django Ninja 전용 상품 검색 API 기준안입니다. DRF는 사용하지 않습니다.

공식 문서 기준:
Django Ninja는 `FilterSchema`, `Query`, custom exception handler, `TestClient`, custom pagination을 지원합니다. 참고: [Filtering](https://django-ninja.dev/guides/input/filtering/), [Pagination](https://django-ninja.dev/guides/response/pagination/), [Errors](https://django-ninja.dev/guides/errors/), [Testing](https://django-ninja.dev/guides/testing/). Problem Details는 RFC 9457 형식을 따릅니다: [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457).

```md
# 상품 검색 API 표준

## 기본 원칙

- API framework는 Django Ninja만 사용한다.
- DRF serializer, viewset, pagination, filter backend는 사용하지 않는다.
- 검색 응답은 항상 `items`와 `meta`를 가진다.
- 클라이언트 입력 오류는 RFC 9457 Problem Details 형식으로 응답한다.
- 정렬 필드는 allowlist로 제한한다.
- 기본 조회 대상은 판매 가능한 활성 상품이다.
- 필터, 정렬, 페이지네이션은 view 내부에 흩뿌리지 않고 Query Schema와 helper로 분리한다.

## Endpoint

`GET /api/products`

## Query Parameters

| name | type | default | rule |
| --- | --- | --- | --- |
| `q` | string | null | 상품명, SKU, 브랜드명 부분 검색 |
| `category_id` | int | null | 카테고리 ID 일치 |
| `brand_id` | int | null | 브랜드 ID 일치 |
| `min_price` | decimal | null | 가격 이상 |
| `max_price` | decimal | null | 가격 이하 |
| `in_stock` | bool | null | true면 재고 1개 이상 |
| `sort` | string | `relevance` | `relevance`, `newest`, `price_asc`, `price_desc`, `name_asc` |
| `page` | int | 1 | 1 이상 |
| `page_size` | int | 20 | 1 이상 100 이하 |

## Response

```json
{
  "items": [
    {
      "id": 1,
      "sku": "P-001",
      "name": "Basic T-Shirt",
      "brand_name": "Acme",
      "category_name": "Top",
      "price": "19900.00",
      "currency": "KRW",
      "is_in_stock": true,
      "created_at": "2026-05-05T10:00:00+09:00"
    }
  ],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 135,
    "total_pages": 7,
    "has_next": true,
    "has_previous": false
  }
}
```

## Problem Details Error Response

```json
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "Request query parameters are invalid.",
  "instance": "/api/products",
  "errors": [
    {
      "loc": ["query", "page_size"],
      "message": "Input should be less than or equal to 100",
      "code": "less_than_equal"
    }
  ]
}
```
```

```python
# products/api.py

from __future__ import annotations

from decimal import Decimal
from enum import Enum
from math import ceil
from typing import Annotated

from django.db.models import QuerySet
from django.http import Http404, JsonResponse
from ninja import Field, FilterLookup, FilterSchema, Query, Router, Schema
from ninja.errors import HttpError, ValidationError

from .models import Product


router = Router(tags=["products"])


class ProblemError(Schema):
    loc: list[str | int]
    message: str
    code: str


class ProblemDetails(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    errors: list[ProblemError] = []


class ProductSort(str, Enum):
    relevance = "relevance"
    newest = "newest"
    price_asc = "price_asc"
    price_desc = "price_desc"
    name_asc = "name_asc"


class ProductFilter(FilterSchema):
    q: Annotated[
        str | None,
        FilterLookup(["name__icontains", "sku__icontains", "brand__name__icontains"]),
    ] = None
    category_id: int | None = None
    brand_id: int | None = None
    min_price: Annotated[Decimal | None, FilterLookup("price__gte")] = None
    max_price: Annotated[Decimal | None, FilterLookup("price__lte")] = None

    in_stock: bool | None = None

    def filter_in_stock(self, value: bool):
        if value:
            return {"stock_quantity__gt": 0}
        return {"stock_quantity": 0}


class ProductSearchQuery(Schema):
    filters: ProductFilter = Query(...)
    sort: ProductSort = ProductSort.relevance
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class ProductOut(Schema):
    id: int
    sku: str
    name: str
    brand_name: str | None
    category_name: str | None
    price: Decimal
    currency: str
    is_in_stock: bool
    created_at: str

    @staticmethod
    def resolve_brand_name(obj):
        return obj.brand.name if obj.brand_id else None

    @staticmethod
    def resolve_category_name(obj):
        return obj.category.name if obj.category_id else None

    @staticmethod
    def resolve_is_in_stock(obj):
        return obj.stock_quantity > 0


class PageMeta(Schema):
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool


class ProductSearchResponse(Schema):
    items: list[ProductOut]
    meta: PageMeta


SORT_MAP = {
    ProductSort.relevance: ("-is_featured", "-created_at", "-id"),
    ProductSort.newest: ("-created_at", "-id"),
    ProductSort.price_asc: ("price", "id"),
    ProductSort.price_desc: ("-price", "-id"),
    ProductSort.name_asc: ("name", "id"),
}


def apply_product_sort(queryset: QuerySet[Product], sort: ProductSort) -> QuerySet[Product]:
    return queryset.order_by(*SORT_MAP[sort])


def paginate_queryset(queryset: QuerySet[Product], page: int, page_size: int):
    total = queryset.count()
    total_pages = ceil(total / page_size) if total else 0
    offset = (page - 1) * page_size

    return {
        "items": queryset[offset : offset + page_size],
        "meta": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1 and total_pages > 0,
        },
    }


@router.get(
    "",
    response={
        200: ProductSearchResponse,
        422: ProblemDetails,
        400: ProblemDetails,
        404: ProblemDetails,
    },
)
def search_products(request, query: ProductSearchQuery = Query(...)):
    queryset = (
        Product.objects.filter(is_active=True)
        .select_related("brand", "category")
    )

    queryset = query.filters.filter(queryset)
    queryset = apply_product_sort(queryset, query.sort)

    return paginate_queryset(queryset, query.page, query.page_size)
```

`filter_in_stock`에서 `dict` 대신 `Q(...)`를 쓰는 편이 더 명확하면 아래처럼 바꿉니다.

```python
from django.db.models import Q

def filter_in_stock(self, value: bool):
    return Q(stock_quantity__gt=0) if value else Q(stock_quantity=0)
```

```python
# api.py 또는 urls.py

from django.http import Http404, JsonResponse
from ninja import NinjaAPI
from ninja.errors import HttpError, ValidationError

from products.api import router as products_router


api = NinjaAPI(title="Commerce API")
api.add_router("/products", products_router)


def problem_response(request, *, status: int, title: str, detail: str, type_: str, errors=None):
    return JsonResponse(
        {
            "type": type_,
            "title": title,
            "status": status,
            "detail": detail,
            "instance": request.path,
            "errors": errors or [],
        },
        status=status,
        content_type="application/problem+json",
    )


@api.exception_handler(ValidationError)
def validation_errors(request, exc: ValidationError):
    errors = [
        {
            "loc": error.get("loc", []),
            "message": error.get("msg", "Invalid value."),
            "code": error.get("type", "validation_error"),
        }
        for error in exc.errors
    ]

    return problem_response(
        request,
        status=422,
        title="Validation Error",
        detail="Request query parameters are invalid.",
        type_="https://api.example.com/problems/validation-error",
        errors=errors,
    )


@api.exception_handler(HttpError)
def http_errors(request, exc: HttpError):
    return problem_response(
        request,
        status=exc.status_code,
        title="HTTP Error",
        detail=str(exc),
        type_="https://api.example.com/problems/http-error",
    )


@api.exception_handler(Http404)
def not_found(request, exc: Http404):
    return problem_response(
        request,
        status=404,
        title="Not Found",
        detail="The requested resource was not found.",
        type_="https://api.example.com/problems/not-found",
    )
```

```python
# urls.py

from django.urls import path

from .api import api

urlpatterns = [
    path("api/", api.urls),
]
```

## 테스트 전략

```md
# 상품 검색 API 테스트 전략

## 우선순위

1. 응답 계약 테스트
2. 필터 테스트
3. 정렬 테스트
4. 페이지네이션 meta 테스트
5. Problem Details 오류 테스트
6. 쿼리 수 회귀 테스트

## 테스트 기준

- `items`와 `meta` 키가 항상 존재해야 한다.
- `meta.total`은 필터 적용 후 전체 개수다.
- `page_size`는 최대 100을 넘을 수 없다.
- 정렬은 allowlist 값만 허용한다.
- 잘못된 query parameter는 422와 `application/problem+json`으로 응답한다.
- 브랜드/카테고리 출력 때문에 N+1 query가 생기지 않아야 한다.
```

```python
# products/tests/test_product_search_api.py

from decimal import Decimal

from django.test import TestCase
from ninja.testing import TestClient

from products.api import router
from products.models import Brand, Category, Product


class ProductSearchApiTests(TestCase):
    def setUp(self):
        self.client = TestClient(router)

        brand = Brand.objects.create(name="Acme")
        category = Category.objects.create(name="Top")

        Product.objects.create(
            sku="P-001",
            name="Basic T-Shirt",
            brand=brand,
            category=category,
            price=Decimal("19900.00"),
            currency="KRW",
            stock_quantity=10,
            is_active=True,
            is_featured=True,
        )
        Product.objects.create(
            sku="P-002",
            name="Premium Hoodie",
            brand=brand,
            category=category,
            price=Decimal("59000.00"),
            currency="KRW",
            stock_quantity=0,
            is_active=True,
        )
        Product.objects.create(
            sku="P-003",
            name="Hidden Product",
            brand=brand,
            category=category,
            price=Decimal("1000.00"),
            currency="KRW",
            stock_quantity=1,
            is_active=False,
        )

    def test_search_returns_items_and_meta(self):
        response = self.client.get("")

        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.json())
        self.assertIn("meta", response.json())
        self.assertEqual(response.json()["meta"]["total"], 2)

    def test_q_filter_searches_name(self):
        response = self.client.get("", {"q": "hoodie"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["meta"]["total"], 1)
        self.assertEqual(response.json()["items"][0]["sku"], "P-002")

    def test_in_stock_filter(self):
        response = self.client.get("", {"in_stock": "true"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["meta"]["total"], 1)
        self.assertEqual(response.json()["items"][0]["sku"], "P-001")

    def test_price_sort_ascending(self):
        response = self.client.get("", {"sort": "price_asc"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["sku"] for item in response.json()["items"]],
            ["P-001", "P-002"],
        )

    def test_pagination_meta(self):
        response = self.client.get("", {"page": 1, "page_size": 1})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["meta"]["total"], 2)
        self.assertEqual(response.json()["meta"]["total_pages"], 2)
        self.assertTrue(response.json()["meta"]["has_next"])
        self.assertFalse(response.json()["meta"]["has_previous"])

    def test_invalid_page_size_returns_problem_details(self):
        response = self.client.get("", {"page_size": 101})

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response["content-type"], "application/problem+json")
        self.assertEqual(response.json()["title"], "Validation Error")
        self.assertEqual(response.json()["status"], 422)
        self.assertTrue(response.json()["errors"])

    def test_invalid_sort_returns_problem_details(self):
        response = self.client.get("", {"sort": "random"})

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["title"], "Validation Error")
```

## 운영 표준

```md
# 운영 규칙

- 검색 API의 기본 정렬은 `relevance`다.
- `relevance`는 당장 검색 점수 엔진이 없으면 `is_featured`, `created_at`, `id` 순으로 정의한다.
- 정렬 필드는 DB index와 함께 검토한다.
- `page_size` 최대값은 100으로 고정한다.
- 외부 클라이언트가 쓰는 응답 필드는 삭제하지 않는다.
- 새 필터를 추가할 때는 반드시 다음 테스트를 추가한다.
  - 필터 적용 결과
  - 필터 미지정 시 기존 결과 보존
  - 잘못된 값에 대한 422 응답
- N+1 가능성이 있는 출력 필드는 `select_related` 또는 `prefetch_related`를 endpoint queryset에 명시한다.
```

주의할 점 하나: Django Ninja의 기본 `@paginate`도 쓸 수 있지만, 팀 응답 표준이 `items/meta`로 고정되어 있다면 위처럼 명시적 pagination helper를 두는 편이 응답 계약을 통제하기 쉽습니다.