**주요 내용**

읽기 전용 환경이라 테스트 파일 생성과 `pytest` 실행은 하지 못했습니다. 또한 지시된 `config.toml`은 현재 경로에 없었습니다. 아래는 Django Ninja endpoint 테스트 표준입니다.

**표준**

테스트 위치는 기본적으로 `tests/isolated/integration/api/test_<resource>_api.py`에 둡니다. endpoint 테스트는 “HTTP 계약”을 검증합니다: status code, response schema, validation error, auth/error mapping. 비즈니스 규칙 자체는 service unit test에서 검증합니다.

Service layer mocking 기준:

- endpoint 테스트에서는 service를 mock해도 됩니다. 목적은 Router, Schema, status code, error mapping 검증입니다.
- service 내부 로직, repository, domain rule을 검증하는 테스트에서는 service를 mock하지 않습니다.
- 외부 시스템 gateway만 mock합니다. repository는 가능하면 `InMemoryFake`를 씁니다.
- mock은 `create_autospec()` 또는 `Mock(spec=...)`를 사용합니다.
- patch 위치는 “정의된 곳”이 아니라 “endpoint 모듈에서 import해 쓰는 이름”입니다.

**RED 테스트 예시**

```python
# tests/isolated/integration/api/test_products_api.py
from unittest.mock import create_autospec

import pytest
from ninja.testing import TestClient

from products.api import router
from products.schemas import ProductOut
from products.services import ProductService


@pytest.fixture
def client():
    return TestClient(router)


@pytest.fixture
def product_service(monkeypatch):
    service = create_autospec(ProductService, instance=True)
    monkeypatch.setattr("products.api.product_service", service)
    return service


def test_get_product_existing_id_returns_200(client, product_service):
    product_service.get.return_value = ProductOut(id=1, name="Keyboard", price=39000)

    response = client.get("/1")

    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Keyboard", "price": 39000}
    product_service.get.assert_called_once_with(product_id=1)


def test_get_product_missing_id_returns_404_problem_detail(client, product_service):
    product_service.get.return_value = None

    response = client.get("/404")

    assert response.status_code == 404
    assert response.json() == {
        "type": "https://example.com/problems/product-not-found",
        "title": "Product not found",
        "status": 404,
        "detail": "Product 404 was not found",
        "instance": "/products/404",
    }


def test_create_product_valid_payload_returns_201(client, product_service):
    product_service.create.return_value = ProductOut(
        id=1,
        name="Keyboard",
        price=39000,
    )

    response = client.post("/",
        json={"name": "Keyboard", "price": 39000},
    )

    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "Keyboard", "price": 39000}


def test_create_product_invalid_payload_returns_422(client, product_service):
    response = client.post("/", json={"name": "", "price": -1})

    assert response.status_code == 422
    product_service.create.assert_not_called()
```

**예상 실패 이유**

RED 단계에서는 `products.api.router`, `ProductService`, `ProductIn`, `ProductOut`, `ProblemDetail` 또는 status mapping이 아직 없어서 import error나 assertion failure가 발생해야 합니다. 특히 실패 응답이 기본 `{"detail": ...}` 형태라면 RFC 9457 Problem Details 표준에 맞지 않아 실패합니다.

**GREEN 최소 구현**

```python
# products/schemas.py
from ninja import Schema
from pydantic import Field


class ProductIn(Schema):
    name: str = Field(min_length=1)
    price: int = Field(gt=0)


class ProductOut(Schema):
    id: int
    name: str
    price: int


class ProblemDetail(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str
```

```python
# products/services.py
from products.schemas import ProductIn, ProductOut


class ProductService:
    def get(self, *, product_id: int) -> ProductOut | None:
        raise NotImplementedError

    def create(self, *, data: ProductIn) -> ProductOut:
        raise NotImplementedError
```

```python
# products/api.py
from ninja import Router

from products.schemas import ProductIn, ProductOut, ProblemDetail
from products.services import ProductService

router = Router()
product_service = ProductService()


@router.get("/{product_id}", response={200: ProductOut, 404: ProblemDetail})
def get_product(request, product_id: int):
    product = product_service.get(product_id=product_id)
    if product is None:
        return 404, ProblemDetail(
            type="https://example.com/problems/product-not-found",
            title="Product not found",
            status=404,
            detail=f"Product {product_id} was not found",
            instance=f"/products/{product_id}",
        )
    return product


@router.post("/", response={201: ProductOut})
def create_product(request, payload: ProductIn):
    return 201, product_service.create(data=payload)
```

**REFACTOR 기준**

- 반복되는 Problem Details 생성은 `api_errors.py`의 함수로 추출합니다.
- service mock fixture는 `tests/isolated/conftest.py`로 올립니다.
- endpoint 테스트는 schema/status/error mapping까지만 검증하고, service 규칙은 `tests/isolated/unit/services/`에서 실제 객체나 fake repository로 검증합니다.
- 인증이 붙는 endpoint는 성공, 401, 403을 별도 테스트로 분리합니다.
- 목록 endpoint는 pagination envelope와 empty result를 반드시 포함합니다.

**검증 명령**

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/integration/api/test_products_api.py -q
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated -q
```

---
> **관련 스킬 참조:**
> - Django Ninja endpoint 구현 → **implementation-django-ninja** 스킬
> - pytest fixture/mock 표준 → **implementation-test** 스킬
> - Red-Green-Refactor 적용 → **implementation-tdd** 스킬