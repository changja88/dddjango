**주요 내용**

현재 워크스페이스가 read-only라 파일 생성과 pytest 실행은 하지 못했습니다. 아래는 실제 프로젝트에 그대로 옮겨 TDD로 진행할 수 있는 Django Ninja 예시입니다. `TestClient(router)` 방식은 빠른 isolated endpoint test에 적합하고, 실제 URL 조합까지 검증하려면 Django `client.post("/api/products/")` 테스트를 별도로 추가하세요.

**RED: endpoint 테스트 먼저**

```python
# tests/isolated/api/test_products_api.py
import pytest
from ninja.testing import TestClient

from products.api import router


class FakeProductService:
    def __init__(self):
        self.called_with = None

    def create_product(self, command):
        self.called_with = command
        return {"id": 1, "name": command.name, "price": command.price}


@pytest.fixture
def product_service(monkeypatch):
    service = FakeProductService()
    monkeypatch.setattr("products.api.product_service", service)
    return service


@pytest.fixture
def client():
    return TestClient(router)


def test_create_product_invalid_request_returns_422(client, product_service):
    # Arrange
    payload = {"name": "", "price": -100}

    # Act
    response = client.post("/", json=payload)

    # Assert
    assert response.status_code == 422
    assert product_service.called_with is None

    errors = response.json()["detail"]
    assert any("name" in error["loc"] for error in errors)
    assert any("price" in error["loc"] for error in errors)


def test_create_product_valid_request_returns_created_product(client, product_service):
    # Arrange
    payload = {"name": "Keyboard", "price": 120000}

    # Act
    response = client.post("/", json=payload)

    # Assert
    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "name": "Keyboard",
        "price": 120000,
    }
    assert product_service.called_with.name == "Keyboard"
    assert product_service.called_with.price == 120000
```

**예상 실패**

처음에는 `products.api`, `router`, `product_service`, `ProductCreateSchema`가 없어서 import 실패합니다. 그 다음 구현 후에는 schema 제약이 없으면 422 테스트가 실패하고, `response={201: ...}` 또는 status code가 없으면 성공 응답 테스트가 실패합니다.

**GREEN: 최소 구현**

```python
# products/schemas.py
from ninja import Schema
from pydantic import Field


class ProductCreateSchema(Schema):
    name: str = Field(min_length=1, max_length=100)
    price: int = Field(gt=0)


class ProductResponseSchema(Schema):
    id: int
    name: str
    price: int
```

```python
# products/services.py
from dataclasses import dataclass


@dataclass(frozen=True)
class CreateProductCommand:
    name: str
    price: int


class ProductService:
    def create_product(self, command: CreateProductCommand) -> dict:
        # 실제 프로젝트에서는 Product.objects.create(...) 또는 repository 호출
        product = {
            "id": 1,
            "name": command.name,
            "price": command.price,
        }
        return product


product_service = ProductService()
```

```python
# products/api.py
from ninja import Router

from products.schemas import ProductCreateSchema, ProductResponseSchema
from products.services import CreateProductCommand, product_service

router = Router(tags=["products"])


@router.post("/", response={201: ProductResponseSchema})
def create_product(request, payload: ProductCreateSchema):
    command = CreateProductCommand(name=payload.name, price=payload.price)
    return 201, product_service.create_product(command)
```

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

**REFACTOR 방향**

endpoint는 HTTP/schema 변환만 담당하고, 생성 유스케이스는 `ProductService`로 둡니다. DB가 들어가면 `ProductRepository` Protocol과 `DjangoProductRepository`를 분리하고, service 테스트는 `InMemoryProductRepository`로 검증하세요. endpoint 테스트는 위처럼 validation 실패와 성공 응답만 얇게 유지하는 편이 리팩터링 내성이 좋습니다.

**실행 명령**

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/api/test_products_api.py -q
```

전체 URL까지 확인하려면 별도 테스트에서 Django pytest client로 실행합니다.

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/api/test_products_api.py tests/isolated/integration/test_products_urls.py -q
```

---
> **관련 스킬 참조:**
> - Django Ninja endpoint/service 설계 → **implementation-django-ninja** 스킬
> - pytest fixture와 isolated test 구조 → **implementation-test** 스킬