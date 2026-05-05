이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다.

아래는 `products.models.Product`가 이미 있고, `sku`가 `unique=True`라고 가정한 상품 CRUD API입니다. 현재 워크스페이스가 비어 있고 읽기 전용이라 파일 생성과 테스트 실행은 하지 못했습니다.

**RED Tests**

`products/tests/test_product_api.py`

```python
import pytest
from ninja.testing import TestClient

from config.api import api
from products.models import Product


@pytest.fixture
def client() -> TestClient:
    return TestClient(api)


@pytest.mark.django_db
def test_list_products_filters_and_paginates(client: TestClient) -> None:
    Product.objects.create(
        name="Notebook",
        sku="NOTE-001",
        description="Portable computer",
        price="1200.00",
        stock=5,
        is_active=True,
    )
    Product.objects.create(
        name="Archived phone",
        sku="PHONE-OLD",
        description="Inactive item",
        price="300.00",
        stock=0,
        is_active=False,
    )

    response = client.get("/products/?q=note&is_active=true&limit=10&offset=0&sort=name")

    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["total"] == 1
    assert body["items"][0]["sku"] == "NOTE-001"


@pytest.mark.django_db
def test_create_product_returns_201(client: TestClient) -> None:
    response = client.post(
        "/products/",
        json={
            "name": "Keyboard",
            "sku": "KEY-001",
            "description": "Mechanical keyboard",
            "price": "89.90",
            "stock": 20,
            "is_active": True,
        },
    )

    assert response.status_code == 201
    assert response.json()["sku"] == "KEY-001"
    assert Product.objects.filter(sku="KEY-001").exists()


@pytest.mark.django_db
def test_duplicate_sku_returns_problem_details(client: TestClient) -> None:
    Product.objects.create(
        name="Keyboard",
        sku="KEY-001",
        description="Original",
        price="89.90",
        stock=20,
        is_active=True,
    )

    response = client.post(
        "/products/",
        json={
            "name": "Duplicate Keyboard",
            "sku": "KEY-001",
            "description": "Duplicate",
            "price": "99.90",
            "stock": 10,
            "is_active": True,
        },
    )

    assert response.status_code == 409
    assert response["content-type"].startswith("application/problem+json")
    assert response.json()["status"] == 409
```

**Schemas**

`products/schemas.py`

```python
from decimal import Decimal

from ninja import Field, FilterSchema, ModelSchema, Schema

from products.models import Product


class ProblemDetail(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str = ""


class ProductOut(ModelSchema):
    class Meta:
        model = Product
        fields = ["id", "name", "sku", "description", "price", "stock", "is_active", "created_at", "updated_at"]


class ProductIn(Schema):
    name: str
    sku: str
    description: str = ""
    price: Decimal
    stock: int = 0
    is_active: bool = True


class ProductPatch(Schema):
    name: str | None = None
    sku: str | None = None
    description: str | None = None
    price: Decimal | None = None
    stock: int | None = None
    is_active: bool | None = None


class ProductFilter(FilterSchema):
    q: str | None = Field(None, q=["name__icontains", "description__icontains", "sku__icontains"])
    is_active: bool | None = None
    min_price: Decimal | None = Field(None, q="price__gte")
    max_price: Decimal | None = Field(None, q="price__lte")


class PageMeta(Schema):
    total: int
    limit: int
    offset: int


class ProductListResponse(Schema):
    items: list[ProductOut]
    meta: PageMeta
```

**Router**

`products/api.py`

```python
from enum import Enum

from django.db import IntegrityError
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from ninja import Query, Router

from products.models import Product
from products.schemas import (
    PageMeta,
    ProblemDetail,
    ProductFilter,
    ProductIn,
    ProductListResponse,
    ProductOut,
    ProductPatch,
)

router = Router(tags=["products"])


class ProductSort(str, Enum):
    CREATED_AT_DESC = "-created_at"
    CREATED_AT_ASC = "created_at"
    NAME_ASC = "name"
    PRICE_ASC = "price"
    PRICE_DESC = "-price"


def problem_response(request: HttpRequest, status: int, title: str, detail: str) -> JsonResponse:
    return JsonResponse(
        ProblemDetail(
            title=title,
            status=status,
            detail=detail,
            instance=request.path,
        ).dict(),
        status=status,
        content_type="application/problem+json",
    )


@router.get("/", response=ProductListResponse)
def list_products(
    request: HttpRequest,
    filters: Query[ProductFilter],
    limit: int = 20,
    offset: int = 0,
    sort: ProductSort = ProductSort.CREATED_AT_DESC,
) -> ProductListResponse:
    safe_limit = min(max(limit, 1), 100)
    safe_offset = max(offset, 0)

    queryset = filters.filter(Product.objects.all()).order_by(sort.value)
    total = queryset.count()
    items = list(queryset[safe_offset : safe_offset + safe_limit])

    return ProductListResponse(
        items=items,
        meta=PageMeta(total=total, limit=safe_limit, offset=safe_offset),
    )


@router.post("/", response={201: ProductOut, 409: ProblemDetail, 422: ProblemDetail})
def create_product(request: HttpRequest, payload: ProductIn) -> tuple[int, Product] | JsonResponse:
    try:
        product = Product.objects.create(**payload.dict())
    except IntegrityError:
        return problem_response(
            request,
            409,
            "Duplicate product",
            "A product with the same unique value already exists.",
        )

    return 201, product


@router.get("/{product_id}", response={200: ProductOut, 404: ProblemDetail})
def get_product(request: HttpRequest, product_id: int) -> Product:
    return get_object_or_404(Product, id=product_id)


@router.patch("/{product_id}", response={200: ProductOut, 404: ProblemDetail, 409: ProblemDetail, 422: ProblemDetail})
def update_product(request: HttpRequest, product_id: int, payload: ProductPatch) -> Product | JsonResponse:
    product = get_object_or_404(Product, id=product_id)

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(product, field, value)

    try:
        product.save()
    except IntegrityError:
        return problem_response(
            request,
            409,
            "Duplicate product",
            "A product with the same unique value already exists.",
        )

    return product


@router.delete("/{product_id}", response={204: None, 404: ProblemDetail})
def delete_product(request: HttpRequest, product_id: int) -> tuple[int, None]:
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return 204, None
```

**API Composition**

`config/api.py`

```python
from django.http import Http404, HttpRequest, JsonResponse
from ninja import NinjaAPI
from ninja.errors import HttpError, ValidationError

from products.api import router as products_router
from products.schemas import ProblemDetail

api = NinjaAPI(title="Product API")
api.add_router("/products/", products_router)


def problem_detail(request: HttpRequest, status: int, title: str, detail: str) -> JsonResponse:
    return JsonResponse(
        ProblemDetail(
            title=title,
            status=status,
            detail=detail,
            instance=request.path,
        ).dict(),
        status=status,
        content_type="application/problem+json",
    )


@api.exception_handler(Http404)
def handle_404(request: HttpRequest, exc: Http404) -> JsonResponse:
    return problem_detail(request, 404, "Not Found", "The requested resource was not found.")


@api.exception_handler(HttpError)
def handle_http_error(request: HttpRequest, exc: HttpError) -> JsonResponse:
    return problem_detail(request, exc.status_code, str(exc), str(exc))


@api.exception_handler(ValidationError)
def handle_validation_error(request: HttpRequest, exc: ValidationError) -> JsonResponse:
    return problem_detail(request, 422, "Validation Error", "Request validation failed.")
```

**URLs**

`config/urls.py`

```python
from django.contrib import admin
from django.urls import path

from config.api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
```

검증은 이 세션에서 실행하지 못했습니다. 적용 후에는 아래를 실행하세요.

```bash
python manage.py check
pytest products/tests/test_product_api.py
```

---
> **관련 스킬 참조:**
> - Django core models/migrations → **implementation-django** 스킬