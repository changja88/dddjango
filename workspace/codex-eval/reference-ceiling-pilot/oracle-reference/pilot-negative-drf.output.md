이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다.

**RED Tests**

```python
# products/tests/test_product_api.py
from decimal import Decimal

import pytest
from ninja.testing import TestClient

from products.api import router
from products.models import Product

pytestmark = pytest.mark.django_db

client = TestClient(router)


def test_create_product() -> None:
    response = client.post(
        "/",
        json={"name": "Keyboard", "price": "129.00", "stock": 10, "is_active": True},
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Keyboard"
    assert Product.objects.filter(name="Keyboard").exists()


def test_list_products() -> None:
    Product.objects.create(name="Mouse", price=Decimal("49.00"), stock=5)

    response = client.get("/")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Mouse"


def test_get_product() -> None:
    product = Product.objects.create(name="Monitor", price=Decimal("399.00"), stock=2)

    response = client.get(f"/{product.id}")

    assert response.status_code == 200
    assert response.json()["id"] == product.id


def test_update_product() -> None:
    product = Product.objects.create(name="Old", price=Decimal("10.00"), stock=1)

    response = client.put(
        f"/{product.id}",
        json={"name": "New", "price": "20.00", "stock": 3, "is_active": False},
    )

    assert response.status_code == 200
    product.refresh_from_db()
    assert product.name == "New"
    assert product.price == Decimal("20.00")
    assert product.stock == 3
    assert product.is_active is False


def test_delete_product() -> None:
    product = Product.objects.create(name="Cable", price=Decimal("9.00"), stock=20)

    response = client.delete(f"/{product.id}")

    assert response.status_code == 204
    assert not Product.objects.filter(id=product.id).exists()
```

**Schema**

```python
# products/schemas.py
from decimal import Decimal

from ninja import ModelSchema, Schema

from products.models import Product


class ProductIn(Schema):
    name: str
    price: Decimal
    stock: int
    is_active: bool = True


class ProductUpdate(Schema):
    name: str
    price: Decimal
    stock: int
    is_active: bool


class ProductPatch(Schema):
    name: str | None = None
    price: Decimal | None = None
    stock: int | None = None
    is_active: bool | None = None


class ProductOut(ModelSchema):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "stock", "is_active", "created_at", "updated_at"]
```

**Router**

```python
# products/api.py
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from products.models import Product
from products.schemas import ProductIn, ProductOut, ProductPatch, ProductUpdate

router = Router(tags=["products"])


@router.get("/", response=list[ProductOut])
def list_products(request: HttpRequest) -> list[Product]:
    return list(Product.objects.order_by("-created_at"))


@router.post("/", response={201: ProductOut})
def create_product(request: HttpRequest, payload: ProductIn) -> tuple[int, Product]:
    product = Product.objects.create(**payload.dict())
    return 201, product


@router.get("/{product_id}", response=ProductOut)
def get_product(request: HttpRequest, product_id: int) -> Product:
    return get_object_or_404(Product, id=product_id)


@router.put("/{product_id}", response=ProductOut)
def update_product(
    request: HttpRequest,
    product_id: int,
    payload: ProductUpdate,
) -> Product:
    product = get_object_or_404(Product, id=product_id)

    for field, value in payload.dict().items():
        setattr(product, field, value)

    product.save(update_fields=["name", "price", "stock", "is_active", "updated_at"])
    return product


@router.patch("/{product_id}", response=ProductOut)
def patch_product(
    request: HttpRequest,
    product_id: int,
    payload: ProductPatch,
) -> Product:
    product = get_object_or_404(Product, id=product_id)
    changed_fields = []

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(product, field, value)
        changed_fields.append(field)

    if changed_fields:
        product.save(update_fields=[*changed_fields, "updated_at"])

    return product


@router.delete("/{product_id}", response={204: None})
def delete_product(request: HttpRequest, product_id: int) -> tuple[int, None]:
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return 204, None
```

**NinjaAPI.add_router**

```python
# config/api.py
from ninja import NinjaAPI

from products.api import router as products_router

api = NinjaAPI()
api.add_router("/products/", products_router)
```

```python
# config/urls.py
from django.urls import path

from config.api import api

urlpatterns = [
    path("api/", api.urls),
]
```

검증은 이 환경에서 실행하지 않았습니다. 적용 후 다음을 실행하세요.

```bash
python manage.py check
pytest
```

---
> **관련 스킬 참조:**
> - REST URL/상태 코드/페이지네이션 정책 → **architecture-api** 스킬