**상품 검색 API 표준**

가정: `products.models.Product`에 `id, name, sku, status, price, category_id, created_at`가 있다. DRF 없이 Django Ninja `Router/Schema/FilterSchema/Query`만 쓴다.

```python
# products/api.py
from decimal import Decimal
from enum import StrEnum

from django.db.models import QuerySet
from django.http import HttpRequest
from ninja import Field, FilterSchema, Query, Router, Schema

from products.models import Product

router = Router(tags=["products"])


class ProductSort(StrEnum):
    newest = "-created_at"
    price_asc = "price"
    price_desc = "-price"
    name_asc = "name"


class ProductOut(Schema):
    id: int
    name: str
    sku: str
    status: str
    price: Decimal
    category_id: int | None


class PageMeta(Schema):
    limit: int
    offset: int
    total: int
    has_more: bool


class ProductSearchResponse(Schema):
    items: list[ProductOut]
    meta: PageMeta


class ProductSearchQuery(FilterSchema):
    q: str | None = Field(None, q=["name__icontains", "sku__icontains"])
    status: str | None = None
    category_id: int | None = None
    min_price: Decimal | None = Field(None, q="price__gte")
    max_price: Decimal | None = Field(None, q="price__lte")
    sort: ProductSort = ProductSort.newest
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)


@router.get("", response={200: ProductSearchResponse})
def search_products(
    request: HttpRequest,
    filters: Query[ProductSearchQuery],
) -> ProductSearchResponse:
    qs: QuerySet[Product] = Product.objects.filter(is_active=True)
    qs = filters.filter(qs)

    ordering = filters.sort.value
    qs = qs.order_by(ordering, "-id")

    total = qs.count()
    rows = list(qs[filters.offset : filters.offset + filters.limit])

    return ProductSearchResponse(
        items=rows,
        meta=PageMeta(
            limit=filters.limit,
            offset=filters.offset,
            total=total,
            has_more=filters.offset + filters.limit < total,
        ),
    )
```

```python
# config/api.py
from django.http import HttpRequest, JsonResponse
from ninja import NinjaAPI, Schema
from ninja.errors import HttpError, ValidationError

from products.api import router as products_router

api = NinjaAPI(title="Commerce API", version="1.0.0")


class ProblemDetail(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str


def problem(
    request: HttpRequest,
    *,
    status: int,
    title: str,
    detail: str,
    type_: str = "about:blank",
) -> JsonResponse:
    return JsonResponse(
        {
            "type": type_,
            "title": title,
            "status": status,
            "detail": detail,
            "instance": request.path,
        },
        status=status,
        content_type="application/problem+json",
    )


@api.exception_handler(ValidationError)
def handle_validation_error(request: HttpRequest, exc: ValidationError) -> JsonResponse:
    return problem(
        request,
        status=422,
        title="Validation Failed",
        detail="Query parameters are invalid.",
        type_="https://api.example.com/problems/validation-failed",
    )


@api.exception_handler(HttpError)
def handle_http_error(request: HttpRequest, exc: HttpError) -> JsonResponse:
    return problem(
        request,
        status=exc.status_code,
        title="HTTP Error",
        detail=str(exc),
    )


api.add_router("/products", products_router)
```

```python
# config/urls.py
from django.urls import path

from config.api import api

urlpatterns = [
    path("api/", api.urls),
]
```

**테스트 전략**

```python
# tests/isolated/products/test_search_products_api.py
import pytest
from ninja.testing import TestClient

from products.api import router
from products.models import Product

pytestmark = pytest.mark.django_db


@pytest.fixture
def client() -> TestClient:
    return TestClient(router)


def test_search_products_returns_items_meta(client: TestClient) -> None:
    Product.objects.create(name="Keyboard", sku="KB-1", status="selling", price=100, is_active=True)

    response = client.get("", {"q": "key", "limit": 10, "offset": 0})

    assert response.status_code == 200
    body = response.json()
    assert body["items"][0]["name"] == "Keyboard"
    assert body["meta"] == {"limit": 10, "offset": 0, "total": 1, "has_more": False}


def test_search_products_rejects_invalid_limit(client: TestClient) -> None:
    response = client.get("", {"limit": 1000})

    assert response.status_code == 422
```

Problem Details의 `application/problem+json`까지 검증하려면 `router` 단독 `TestClient`보다 `config.api.api`를 대상으로 통합 테스트를 둔다.

```bash
python manage.py check
pytest tests/isolated/products/test_search_products_api.py -q
```

인덱스는 실제 검색 조건 기준으로 잡는다: `is_active, status, category_id`, 정렬용 `created_at`, `price`, 필요 시 `name/sku` 검색 인덱스. 정렬은 `ProductSort` allow-list만 허용하고 사용자 입력을 `order_by()`에 직접 넘기지 않는다.

---
> **관련 스킬 참조:**
> - API 설계/오류/페이지네이션 → **architecture-api** 스킬
> - Django Ninja Router/Schema/FilterSchema → **implementation-django-ninja** 스킬
> - 테스트 전략 → **implementation-test** 스킬