현재 평가 디렉터리에는 `config.toml`, `manage.py` 같은 프로젝트 파일이 없어 실행/적용은 하지 못했습니다. 이 프로젝트 정책은 DRF가 아니라 **Django Ninja** 기준이므로, 아래는 Django Ninja로 바로 옮길 수 있는 팀 컨벤션 초안입니다.

**상품 검색 API 설계**

기본 리소스는 `products`입니다. 검색도 별도 동사 URL을 만들지 않고 컬렉션 조회의 쿼리 파라미터로 표현합니다.

```http
GET /api/v1/products
GET /api/v1/products/{product_id}
```

`/products/search`, `/search-products`는 사용하지 않습니다. 검색은 다음처럼 호출합니다.

```http
GET /api/v1/products?q=keyboard&category_id=10&min_price=10000&max_price=50000&sort=-relevance,-created_at&limit=20&cursor=...
```

**쿼리 파라미터 컨벤션**

필터는 `snake_case`를 사용하고, 범위 조건은 `min_`, `max_`, `*_after`, `*_before` 형태로 통일합니다.

| 파라미터 | 타입 | 의미 |
|---|---:|---|
| `q` | string | 상품명, 브랜드명, SKU 등 통합 검색어 |
| `category_id` | int | 카테고리 필터 |
| `brand_id` | int | 브랜드 필터 |
| `seller_id` | int | 판매자 필터 |
| `min_price` | int | 최소 판매가 |
| `max_price` | int | 최대 판매가 |
| `in_stock` | bool | 재고 보유 여부 |
| `status` | string | `active`, `sold_out`, `hidden` 등 |
| `created_after` | datetime | 등록일 시작 |
| `created_before` | datetime | 등록일 종료 |
| `sort` | string | 정렬 필드 목록 |
| `limit` | int | 페이지 크기 |
| `cursor` | string | 다음 페이지 커서 |

검색어 `q`는 최소 2자 이상을 권장합니다. 빈 문자열은 필터링하지 않고 무시하거나 `422`로 처리하되, 팀에서는 **명시적 오류가 디버깅에 유리하므로 422 권장**입니다.

**정렬 컨벤션**

`sort`는 쉼표 구분 목록을 사용합니다. `-` prefix는 내림차순입니다.

```http
sort=-relevance,-created_at
sort=price
sort=-price,name
```

허용 정렬 필드는 화이트리스트로 제한합니다.

| 정렬값 | 의미 |
|---|---|
| `relevance` | 검색 관련도, `q`가 있을 때만 허용 |
| `price` | 가격 오름차순 |
| `-price` | 가격 내림차순 |
| `created_at` | 오래된순 |
| `-created_at` | 최신순 |
| `name` | 이름순 |

기본 정렬은 다음을 권장합니다.

```text
q 있음: -relevance,-created_at,-id
q 없음: -created_at,-id
```

항상 마지막에 `id` 또는 `-id`를 tie-breaker로 붙여 커서 페이지네이션이 흔들리지 않게 합니다.

**페이지네이션 컨벤션**

상품 검색은 데이터 변동이 잦고 결과 수가 커질 수 있으므로 기본은 **cursor pagination**으로 둡니다. 관리자 화면처럼 임의 페이지 이동이 필요한 경우에만 별도 admin API에서 offset/page number를 씁니다.

요청:

```http
GET /api/v1/products?limit=20&cursor=eyJjcmVhdGVkX2F0Ijoi...
```

응답:

```json
{
  "items": [
    {
      "id": 123,
      "name": "Wireless Keyboard",
      "brand_name": "Acme",
      "price": 39000,
      "currency": "KRW",
      "in_stock": true,
      "thumbnail_url": "https://cdn.example.com/products/123.jpg"
    }
  ],
  "next_cursor": "eyJjcmVhdGVkX2F0Ijoi...",
  "has_more": true
}
```

팀 기본값:

```text
default limit: 20
max limit: 100
cursor: opaque base64 token
stable ordering: 정렬 필드 + id
```

**Django Ninja 스키마 예시**

```python
from datetime import datetime
from typing import Annotated, Literal

from django.db.models import Q, QuerySet
from ninja import FilterSchema, Schema
from ninja.filter_schema import FilterLookup
from pydantic import Field


ProductStatus = Literal["active", "sold_out", "hidden"]
ProductSort = Literal[
    "relevance",
    "-relevance",
    "price",
    "-price",
    "created_at",
    "-created_at",
    "name",
]


class ProductOut(Schema):
    id: int
    name: str
    brand_name: str | None = None
    price: int
    currency: str = "KRW"
    in_stock: bool
    thumbnail_url: str | None = None


class ProductFilter(FilterSchema):
    q: str | None = Field(default=None, min_length=2, max_length=100)
    category_id: Annotated[int | None, FilterLookup("category_id")] = None
    brand_id: Annotated[int | None, FilterLookup("brand_id")] = None
    seller_id: Annotated[int | None, FilterLookup("seller_id")] = None
    min_price: Annotated[int | None, FilterLookup("price__gte")] = None
    max_price: Annotated[int | None, FilterLookup("price__lte")] = None
    in_stock: Annotated[bool | None, FilterLookup("stock_quantity__gt")] = None
    status: Annotated[ProductStatus | None, FilterLookup("status")] = None
    created_after: Annotated[datetime | None, FilterLookup("created_at__gte")] = None
    created_before: Annotated[datetime | None, FilterLookup("created_at__lte")] = None

    def filter_q(self, value: str) -> Q:
        return (
            Q(name__icontains=value)
            | Q(brand__name__icontains=value)
            | Q(sku__icontains=value)
        )


class ProductSearchPage(Schema):
    items: list[ProductOut]
    next_cursor: str | None = None
    has_more: bool
```

**Router 형태**

```python
from typing import Annotated

from ninja import Query, Router
from ninja.errors import HttpError

router = Router(tags=["products"])

ALLOWED_SORTS = {
    "relevance",
    "-relevance",
    "price",
    "-price",
    "created_at",
    "-created_at",
    "name",
}


@router.get("", response={200: ProductSearchPage})
def list_products(
    request,
    filters: Query[ProductFilter],
    sort: str = "-created_at",
    limit: int = 20,
    cursor: str | None = None,
) -> ProductSearchPage:
    if limit < 1 or limit > 100:
        raise HttpError(422, "limit must be between 1 and 100")

    sort_fields = [field.strip() for field in sort.split(",") if field.strip()]
    invalid_sorts = [field for field in sort_fields if field not in ALLOWED_SORTS]
    if invalid_sorts:
        raise HttpError(422, f"Unsupported sort field: {', '.join(invalid_sorts)}")

    if any(field.lstrip("-") == "relevance" for field in sort_fields) and not filters.q:
        raise HttpError(422, "relevance sort requires q")

    queryset = Product.objects.select_related("brand", "category")
    queryset = filters.filter(queryset)
    queryset = apply_product_sort(queryset, sort_fields, has_query=bool(filters.q))
    items, next_cursor, has_more = paginate_products(queryset, limit=limit, cursor=cursor)

    return ProductSearchPage(items=items, next_cursor=next_cursor, has_more=has_more)
```

**에러 응답 표준**

모든 API 에러는 RFC 9457 Problem Details 형식으로 통일합니다. `Content-Type`은 `application/problem+json`입니다.

```json
{
  "type": "https://api.example.com/problems/invalid-query-parameter",
  "title": "Invalid query parameter",
  "status": 422,
  "detail": "Unsupported sort field: popularity",
  "instance": "/api/v1/products",
  "code": "INVALID_QUERY_PARAMETER",
  "errors": [
    {
      "field": "sort",
      "message": "Allowed values are relevance, -relevance, price, -price, created_at, -created_at, name"
    }
  ]
}
```

상태 코드 기준:

| 상황 | 코드 |
|---|---:|
| 인증 없음 | `401` |
| 권한 없음 | `403` |
| 상품 없음 | `404` |
| 잘못된 쿼리 파라미터 | `422` |
| 지원하지 않는 정렬값 | `422` |
| 커서 파싱 실패/만료 | `422` |
| Rate limit 초과 | `429` |
| 서버 오류 | `500` |

Ninja 전역 핸들러는 이런 형태를 권장합니다.

```python
from django.http import JsonResponse
from ninja import Schema
from ninja.errors import HttpError, ValidationError


class ProblemDetail(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str
    code: str | None = None


def problem_response(request, *, status: int, title: str, detail: str, code: str):
    return JsonResponse(
        ProblemDetail(
            type=f"https://api.example.com/problems/{code.lower().replace('_', '-')}",
            title=title,
            status=status,
            detail=detail,
            instance=request.path,
            code=code,
        ).model_dump(),
        status=status,
        content_type="application/problem+json",
    )


@api.exception_handler(HttpError)
def handle_http_error(request, exc: HttpError):
    return problem_response(
        request,
        status=exc.status_code,
        title="Request failed",
        detail=str(exc),
        code="REQUEST_FAILED",
    )


@api.exception_handler(ValidationError)
def handle_validation_error(request, exc: ValidationError):
    return problem_response(
        request,
        status=422,
        title="Validation failed",
        detail="Request parameters are invalid.",
        code="VALIDATION_FAILED",
    )
```

**DDD 관점**

상품 검색은 `Catalog` 바운디드 컨텍스트의 읽기 유스케이스로 둡니다. 검색 API는 상품 상태를 바꾸지 않으므로 도메인 애그리거트를 직접 조작하지 않고, `ProductSearchQueryService` 또는 read repository가 QuerySet/read model을 조립하는 구조가 적합합니다.

유비쿼터스 언어는 다음처럼 고정합니다.

| 권장 용어 | 의미 | 금지 동의어 |
|---|---|---|
| `Product` | 판매 가능한 상품 | `Item`, `Goods` 혼용 |
| `Catalog` | 상품 탐색/노출 컨텍스트 | `Shop`, `Inventory` 혼용 |
| `in_stock` | 구매 가능한 재고 있음 | `available`, `has_stock` 혼용 |
| `price` | 현재 판매가 | `amount`, `cost` 혼용 |
| `status` | 노출/판매 상태 | `state`, `visibility` 혼용 |

---
> **관련 스킬 참조:**
> - API 설계 원칙/오류/페이지네이션 → **architecture-api** 스킬
> - Django Ninja Router/Schema/FilterSchema 구현 → **implementation-django-ninja** 스킬
> - 상품 도메인 경계/유비쿼터스 언어 → **architecture-ddd** 스킬