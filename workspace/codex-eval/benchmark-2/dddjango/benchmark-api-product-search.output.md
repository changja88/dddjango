**상품 검색 API 팀 컨벤션**

가정: `products` 앱, `Product` 모델 기준. API는 DRF 없이 Django Ninja `Schema`/`Router`/`Query`/`FilterSchema`만 사용한다.

**Endpoint**
`GET /api/v1/products`

규칙:
- 컬렉션은 복수 명사: `/products`
- 검색, 필터, 정렬은 query parameter로만 받는다.
- 목록 API는 반드시 페이지네이션을 적용한다.
- 응답 필드는 공개 계약이므로 `ModelSchema` 전체 노출 금지, 명시적 `Schema` 사용.
- 정렬 필드는 enum 또는 allow-list로 제한한다.
- 오류는 모두 RFC 9457 Problem Details 형태로 통일한다.

```python
# products/api.py
from decimal import Decimal
from enum import StrEnum
from typing import Literal

from django.db.models import QuerySet
from ninja import Field, Query, Router, Schema
from ninja.pagination import PageNumberPagination, paginate
from ninja.schema import FilterSchema

from products.models import Product

router = Router(tags=["products"])


class ProductStatus(StrEnum):
    ACTIVE = "active"
    SOLD_OUT = "sold_out"
    HIDDEN = "hidden"


class ProductSort(StrEnum):
    NEWEST = "-created_at"
    PRICE_ASC = "price"
    PRICE_DESC = "-price"
    NAME_ASC = "name"


class ProductFilter(FilterSchema):
    q: str | None = Field(None, q=["name__icontains", "description__icontains"])
    category_id: int | None = Field(None, q="category_id")
    min_price: Decimal | None = Field(None, ge=0, q="price__gte")
    max_price: Decimal | None = Field(None, ge=0, q="price__lte")
    status: ProductStatus | None = Field(None, q="status")
    in_stock: bool | None = Field(None, q="stock__gt")


class ProductOut(Schema):
    id: int
    name: str
    price: Decimal
    status: ProductStatus
    stock: int
    category_id: int
    created_at: str


class ProductListOut(Schema):
    items: list[ProductOut]
    count: int


@router.get("", response=ProductListOut)
@paginate(PageNumberPagination, page_size=20)
def search_products(
    request,
    filters: Query[ProductFilter],
    sort: Query[ProductSort] = ProductSort.NEWEST,
) -> QuerySet[Product]:
    qs = Product.objects.select_related("category").filter(status=ProductStatus.ACTIVE)
    qs = filters.filter(qs)
    return qs.order_by(sort.value, "id")
```

**필터 컨벤션**
- `q`: 자유 검색어. 이름/설명 등 제한된 텍스트 필드만 검색한다.
- `*_id`: 관계 필터는 객체 중첩이 아니라 식별자로 받는다.
- `min_*`, `max_*`: 범위 필터 표준명으로 사용한다.
- `None` 값은 필터에서 제외한다.
- 복잡한 OR/AND 조건은 `FilterSchema`의 `q=` 매핑 또는 selector 함수로 분리한다.

**정렬 컨벤션**
- `sort` 하나만 허용한다.
- 내림차순은 Django ORM과 동일하게 `-field` 값을 사용하되, 외부 계약은 enum으로 제한한다.
- 항상 안정 정렬을 위해 마지막에 `id`를 추가한다.
- 허용 예: `-created_at`, `price`, `-price`, `name`
- 금지 예: 임의 필드명 직접 전달, `order_by(request.GET["sort"])`

**페이지네이션 컨벤션**
- 기본 목록 API는 `PageNumberPagination`, 기본 `page_size=20`.
- 대량 데이터 또는 무한 스크롤은 cursor pagination으로 별도 전환한다.
- 응답 표준:
```json
{
  "items": [],
  "count": 123
}
```
- query 표준:
`?page=1&page_size=20`
- `page_size` 최대값은 서버에서 제한한다. 권장 최대 `100`.

**에러 응답 표준**

모든 오류는 Problem Details 형태로 반환한다.

```python
# config/api.py
from ninja import NinjaAPI
from ninja.errors import ValidationError

api = NinjaAPI(version="1.0.0")


class ProblemDetail(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str | None = None
    errors: list[dict] | None = None


@api.exception_handler(ValidationError)
def validation_errors(request, exc: ValidationError):
    return api.create_response(
        request,
        {
            "type": "https://api.example.com/problems/validation-error",
            "title": "Validation Error",
            "status": 422,
            "detail": "Request validation failed.",
            "instance": request.path,
            "errors": exc.errors,
        },
        status=422,
    )
```

상태 코드 기준:
- `400`: 문법적으로 잘못된 요청
- `401`: 인증 필요
- `403`: 권한 없음
- `404`: 리소스 없음
- `409`: 상태 충돌
- `422`: Schema validation 실패
- `429`: rate limit 초과
- `500`: 서버 오류

**라우터 합성**

```python
# config/api.py
from products.api import router as products_router

api.add_router("/v1/products", products_router)
```

```python
# config/urls.py
from django.urls import path
from config.api import api

urlpatterns = [path("api/", api.urls)]
```

**검증 절차**
- `python manage.py check`
- `python manage.py test products`
- OpenAPI 확인: `/api/docs`
- 검색 쿼리 확인: `/api/v1/products?q=shirt&min_price=10000&sort=-price&page=1`

---
> **관련 스킬 참조:**
> - API 구현 상세화 → **implementation-django-ninja** 스킬