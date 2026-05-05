이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다.

**RED Tests**

```python
# products/tests/test_product_api.py
from decimal import Decimal

import pytest
from ninja.testing import TestClient

from config.api import api
from products.models import Product

client = TestClient(api)


@pytest.mark.django_db
def test_create_product() -> None:
    response = client.post(
        "/products/",
        json={
            "name": "Keyboard",
            "price": "129.00",
            "description": "Mechanical keyboard",
            "is_active": True,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == Product.objects.get(name="Keyboard").id
    assert body["name"] == "Keyboard"
    assert Decimal(str(body["price"])) == Decimal("129.00")
    assert body["description"] == "Mechanical keyboard"
    assert body["is_active"] is True


@pytest.mark.django_db
def test_list_products() -> None:
    Product.objects.create(name="Keyboard", price=Decimal("129.00"), is_active=True)
    Product.objects.create(name="Mouse", price=Decimal("49.00"), is_active=False)

    response = client.get("/products/")

    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == ["Keyboard", "Mouse"]


@pytest.mark.django_db
def test_get_product() -> None:
    product = Product.objects.create(
        name="Keyboard",
        price=Decimal("129.00"),
        description="Mechanical keyboard",
        is_active=True,
    )

    response = client.get(f"/products/{product.id}/")

    assert response.status_code == 200
    assert response.json()["id"] == product.id
    assert response.json()["name"] == "Keyboard"


@pytest.mark.django_db
def test_update_product() -> None:
    product = Product.objects.create(name="Keyboard", price=Decimal("129.00"))

    response = client.put(
        f"/products/{product.id}/",
        json={
            "name": "Keyboard Pro",
            "price": "159.00",
            "description": "Updated keyboard",
            "is_active": True,
        },
    )

    assert response.status_code == 200
    product.refresh_from_db()
    assert product.name == "Keyboard Pro"
    assert product.price == Decimal("159.00")


@pytest.mark.django_db
def test_delete_product() -> None:
    product = Product.objects.create(name="Keyboard", price=Decimal("129.00"))

    response = client.delete(f"/products/{product.id}/")

    assert response.status_code == 204
    assert not Product.objects.filter(id=product.id).exists()
```

**Django Ninja Code**

```python
# products/schemas.py
from decimal import Decimal

from ninja import Schema
from pydantic import Field


class ProductIn(Schema):
    name: str = Field(..., max_length=120)
    price: Decimal = Field(..., ge=0)
    description: str = ""
    is_active: bool = True


class ProductOut(Schema):
    id: int
    name: str
    price: Decimal
    description: str
    is_active: bool
```

```python
# products/api.py
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from products.models import Product
from products.schemas import ProductIn, ProductOut

router = Router(tags=["products"])


@router.get("/", response=list[ProductOut])
def list_products(request: HttpRequest) -> list[Product]:
    return list(Product.objects.order_by("id"))


@router.post("/", response={201: ProductOut})
def create_product(request: HttpRequest, payload: ProductIn) -> tuple[int, Product]:
    product = Product.objects.create(**payload.dict())
    return 201, product


@router.get("/{product_id}/", response=ProductOut)
def get_product(request: HttpRequest, product_id: int) -> Product:
    return get_object_or_404(Product, id=product_id)


@router.put("/{product_id}/", response=ProductOut)
def update_product(
    request: HttpRequest,
    product_id: int,
    payload: ProductIn,
) -> Product:
    product = get_object_or_404(Product, id=product_id)

    for field, value in payload.dict().items():
        setattr(product, field, value)

    product.save(update_fields=["name", "price", "description", "is_active"])
    return product


@router.delete("/{product_id}/", response={204: None})
def delete_product(request: HttpRequest, product_id: int) -> tuple[int, None]:
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return 204, None
```

```python
# config/api.py
from ninja import NinjaAPI

from products.api import router as products_router

api = NinjaAPI(title="Product API")

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

위 코드는 `products.models.Product`에 `name`, `price`, `description`, `is_active` 필드가 있다고 가정합니다. 현재 세션은 읽기 전용이라 파일 생성과 테스트 실행은 하지 못했습니다. 적용 후 검증은 아래로 진행하세요.

```bash
python manage.py check
pytest products/tests/test_product_api.py
```

---
> **관련 스킬 참조:**
> - Django 모델/마이그레이션 → **implementation-django** 스킬