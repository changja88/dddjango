이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다.

현재 workspace는 `config.toml`도 없고 읽기 전용이라 파일 생성/수정 및 테스트 실행은 못 했습니다. 아래는 `products` 앱에 `Product` 모델이 이미 있다고 가정한 RED 테스트와 Django Ninja 구현입니다.

**RED Tests**

`products/tests/test_product_api.py`

```python
from decimal import Decimal

import pytest
from django.test import RequestFactory
from ninja import NinjaAPI
from ninja.testing import TestClient

from products.api import router
from products.models import Product


@pytest.fixture
def client():
    api = NinjaAPI()
    api.add_router("/products/", router)
    return TestClient(api)


@pytest.mark.django_db
def test_list_products_returns_products(client):
    Product.objects.create(
        name="Keyboard",
        description="Mechanical keyboard",
        price=Decimal("129000.00"),
        stock=5,
        is_active=True,
    )

    response = client.get("/products/")

    assert response.status_code == 200
    data = response.json()
    results = data["items"] if "items" in data else data["results"]
    assert results[0]["name"] == "Keyboard"


@pytest.mark.django_db
def test_create_product(client):
    response = client.post(
        "/products/",
        json={
            "name": "Mouse",
            "description": "Wireless mouse",
            "price": "59000.00",
            "stock": 10,
            "is_active": True,
        },
    )

    assert response.status_code == 201
    assert Product.objects.filter(name="Mouse").exists()


@pytest.mark.django_db
def test_update_product(client):
    product = Product.objects.create(
        name="Old",
        description="Old description",
        price=Decimal("1000.00"),
        stock=1,
        is_active=True,
    )

    response = client.patch(
        f"/products/{product.id}/",
        json={"name": "New", "stock": 3},
    )

    assert response.status_code == 200
    product.refresh_from_db()
    assert product.name == "New"
    assert product.stock == 3


@pytest.mark.django_db
def test_delete_product(client):
    product = Product.objects.create(
        name="Delete me",
        description="",
        price=Decimal("1000.00"),
        stock=1,
        is_active=True,
    )

    response = client.delete(f"/products/{product.id}/")

    assert response.status_code == 204
    assert not Product.objects.filter(id=product.id).exists()
```

**Schema**

`products/schemas.py`

```python
from decimal import Decimal
from typing import Optional

from ninja import ModelSchema, Schema

from products.models import Product


class ProductOut(ModelSchema):
    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "stock", "is_active"]


class ProductCreate(Schema):
    name: str
    description: str = ""
    price: Decimal
    stock: int
    is_active: bool = True


class ProductUpdate(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    is_active: Optional[bool] = None


class ProblemDetail(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
```

**Router**

`products/api.py`

```python
from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError
from ninja.pagination import LimitOffsetPagination, paginate

from products.models import Product
from products.schemas import ProductCreate, ProductOut, ProductUpdate

router = Router(tags=["products"])


@router.get("/", response=List[ProductOut])
@paginate(LimitOffsetPagination)
def list_products(request):
    return Product.objects.order_by("-id")


@router.get("/{product_id}/", response=ProductOut)
def get_product(request, product_id: int) -> Product:
    return get_object_or_404(Product, id=product_id)


@router.post("/", response={201: ProductOut})
def create_product(request, payload: ProductCreate) -> tuple[int, Product]:
    product = Product.objects.create(**payload.dict())
    return 201, product


@router.patch("/{product_id}/", response=ProductOut)
def update_product(request, product_id: int, payload: ProductUpdate) -> Product:
    product = get_object_or_404(Product, id=product_id)

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(product, field, value)

    product.save(update_fields=list(payload.dict(exclude_unset=True).keys()))
    return product


@router.delete("/{product_id}/", response={204: None})
def delete_product(request, product_id: int) -> tuple[int, None]:
    deleted, _ = Product.objects.filter(id=product_id).delete()
    if deleted == 0:
        raise HttpError(404, "Product not found")
    return 204, None
```

**API 합성**

`config/api.py`

```python
from ninja import NinjaAPI
from ninja.errors import HttpError

from products.api import router as products_router
from products.schemas import ProblemDetail

api = NinjaAPI()


@api.exception_handler(HttpError)
def http_error_handler(request, exc: HttpError):
    return api.create_response(
        request,
        {
            "type": "about:blank",
            "title": exc.message,
            "status": exc.status_code,
            "detail": exc.message,
        },
        status=exc.status_code,
    )


api.add_router("/products/", products_router)
```

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

실행 확인은 이 순서로 하면 됩니다.

```bash
pytest products/tests/test_product_api.py
```

처음에는 라우터/스키마가 없어서 RED로 실패해야 하고, 위 구현을 추가한 뒤 다시 실행하면 GREEN이 되어야 합니다.

---
> **관련 스킬 참조:**
> - Django 모델/마이그레이션 → **implementation-django** 스킬