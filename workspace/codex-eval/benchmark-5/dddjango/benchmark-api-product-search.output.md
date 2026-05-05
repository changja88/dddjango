fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 존재하지 않아 읽을 파일이 없었습니다. 실제 파일 diff는 만들 수 없으므로, read-only 기준으로 팀 문서에 붙여 넣을 수 있는 Django Ninja 컨벤션과 예시만 제안합니다.

**상품 검색 API 컨벤션**

- 엔드포인트: `GET /api/products/`
- URL은 복수 명사만 사용한다. 검색, 필터, 정렬은 query parameter로 표현한다.
- API 구현은 DRF가 아니라 Django Ninja `Schema`, `FilterSchema`, `Query`, `Router`를 사용한다.
- sync endpoint는 반드시 `request: HttpRequest`를 첫 인자로 받고 명시적 return type을 둔다.
- 목록 응답은 plain `list[Schema]`가 아니라 `items/meta` envelope를 사용한다.
- 정렬 필드는 allow-list로 제한하고 사용자 입력을 그대로 `order_by()`에 넘기지 않는다.
- 페이지네이션은 cursor 기반을 기본으로 한다. cursor는 클라이언트가 해석하지 않는 opaque 문자열로 취급한다.
- validation error와 business error는 RFC 9457 Problem Details 형식으로 통일한다.

```python
# products/api.py
from typing import Literal

from django.http import HttpRequest
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from ninja import FilterSchema, Query, Router, Schema

from products.models import Product

router = Router(tags=["products"])


class ProblemDetail(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str | None = None
    errors: dict[str, list[str]] | None = None


class ProductFilter(FilterSchema):
    q: str | None = None
    category_id: int | None = None
    min_price: int | None = None
    max_price: int | None = None
    in_stock: bool | None = None
    sort: Literal["name", "-name", "price", "-price", "created_at", "-created_at"] = "-created_at"
    limit: int = 20
    cursor: str | None = None


class ProductOut(Schema):
    id: int
    name: str
    price: int
    category_id: int
    stock_quantity: int


class PageMeta(Schema):
    limit: int
    next_cursor: str | None
    has_more: bool


class ProductSearchResponse(Schema):
    items: list[ProductOut]
    meta: PageMeta


def decode_cursor(cursor: str | None) -> int | None:
    if cursor is None:
        return None
    return int(urlsafe_base64_decode(cursor).decode())


def encode_cursor(product_id: int) -> str:
    return urlsafe_base64_encode(str(product_id).encode())


@router.get(
    "/",
    response={200: ProductSearchResponse, 422: ProblemDetail},
)
def search_products(
    request: HttpRequest,
    filters: Query[ProductFilter],
) -> ProductSearchResponse:
    limit = min(max(filters.limit, 1), 100)
    queryset = Product.objects.filter(is_active=True)

    if filters.q:
        queryset = queryset.filter(name__icontains=filters.q)
    if filters.category_id is not None:
        queryset = queryset.filter(category_id=filters.category_id)
    if filters.min_price is not None:
        queryset = queryset.filter(price__gte=filters.min_price)
    if filters.max_price is not None:
        queryset = queryset.filter(price__lte=filters.max_price)
    if filters.in_stock is not None:
        queryset = queryset.filter(stock_quantity__gt=0 if filters.in_stock else 0)

    last_id = decode_cursor(filters.cursor)
    if last_id is not None:
        queryset = queryset.filter(id__gt=last_id)

    rows = list(queryset.order_by(filters.sort, "id")[: limit + 1])
    items = rows[:limit]
    has_more = len(rows) > limit

    return ProductSearchResponse(
        items=items,
        meta=PageMeta(
            limit=limit,
            has_more=has_more,
            next_cursor=encode_cursor(items[-1].id) if has_more and items else None,
        ),
    )
```

**에러 응답 표준**

```json
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Validation failed",
  "status": 422,
  "detail": "요청 파라미터가 올바르지 않습니다.",
  "instance": "/api/products/",
  "errors": {
    "limit": ["100 이하로 입력해야 합니다."]
  }
}
```

팀 규칙:

- 모든 오류는 `type`, `title`, `status`, `detail`, `instance`를 포함한다.
- validation 오류는 `errors: dict[str, list[str]]`를 추가한다.
- 응답 `Content-Type`은 `application/problem+json`으로 맞춘다.
- `400`은 malformed request, `401`은 인증 필요, `403`은 권한 없음, `404`는 리소스 없음, `422`는 검증 실패, `429`는 rate limit으로 고정한다.

**검증 단계**

읽기 전용이라 실행하지 못했습니다. 실제 적용 후에는 아래를 확인하세요.

```bash
python manage.py check
pytest
pytest products/tests/test_product_api.py
```

---
> **관련 스킬 참조:**
> - API 설계/오류/페이지네이션 → **architecture-api** 스킬
> - Django Ninja Schema/Router/Query → **implementation-django-ninja** 스킬