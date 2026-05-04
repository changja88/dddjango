사용한 스킬: `architecture-api`, `implementation-django-ninja`, `implementation-test`, `implementation-tdd`.

현재 워크스페이스가 read-only라 테스트 파일 생성과 `pytest` 실행은 하지 못했습니다. 아래는 실제 프로젝트에 그대로 옮겨 적용할 수 있는 Django Ninja endpoint pytest 표준입니다.

**[주요 내용]**

표준 원칙:

- API 테스트는 `ninja.testing.TestClient`로 Router 또는 API를 직접 호출한다.
- 테스트 위치는 `tests/isolated/integration/<app>/test_<resource>_api.py`를 기본으로 한다.
- 성공 응답과 실패 응답을 모두 테스트한다: `2xx`, 도메인 오류 `4xx`, 입력 검증 `422`.
- endpoint 테스트의 책임은 HTTP 계약이다: request parsing, status code, response schema, service 호출 경계.
- 비즈니스 규칙은 service 테스트에서 검증하고, endpoint 테스트에서는 service layer를 `create_autospec` 또는 `patch(..., autospec=True)`로 대체한다.
- Mock은 endpoint가 import해서 사용하는 위치를 patch한다. 예: endpoint가 `products.api.create_product`를 호출하면 `products.api.create_product`를 patch한다.
- Repository, Gateway, 외부 API는 service 테스트에서 Fake 또는 Mock으로 대체한다. endpoint 테스트에서 DB/외부 시스템까지 깊게 들어가지 않는다.

**RED 테스트**

```python
# tests/isolated/integration/products/test_product_api.py
from unittest.mock import patch

import pytest
from ninja.testing import TestClient

from products.api import router
from products.services import ProductAlreadyExists, ProductResult


client = TestClient(router)


def test_create_product_valid_payload_returns_201():
    payload = {"name": "Keyboard", "price": 39000}

    with patch("products.api.create_product", autospec=True) as create_product:
        create_product.return_value = ProductResult(id=1, name="Keyboard", price=39000)

        response = client.post("/products", json=payload)

    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "Keyboard", "price": 39000}
    create_product.assert_called_once_with(name="Keyboard", price=39000)


def test_create_product_duplicate_name_returns_409_problem_detail():
    payload = {"name": "Keyboard", "price": 39000}

    with patch("products.api.create_product", autospec=True) as create_product:
        create_product.side_effect = ProductAlreadyExists("Keyboard")

        response = client.post("/products", json=payload)

    assert response.status_code == 409
    assert response.json() == {
        "type": "https://api.example.com/problems/product-already-exists",
        "title": "Product already exists",
        "status": 409,
        "detail": "Product 'Keyboard' already exists.",
    }


def test_create_product_invalid_payload_returns_422():
    response = client.post("/products", json={"name": "", "price": -1})

    assert response.status_code == 422
```

예상 실패 이유:

- `products.api.router`가 아직 없으면 import 단계에서 실패한다.
- `create_product`가 아직 없으면 patch 대상이 없어 실패한다.
- endpoint가 `201`, `409`, `422` 계약을 구현하지 않았으면 assertion이 실패한다.
- 실패 응답이 RFC 9457 Problem Details 형식이 아니면 JSON assertion이 실패한다.

**GREEN 최소 구현**

```python
# products/schemas.py
from ninja import Schema
from pydantic import Field


class ProductCreateIn(Schema):
    name: str = Field(min_length=1)
    price: int = Field(ge=0)


class ProductOut(Schema):
    id: int
    name: str
    price: int


class ProblemDetail(Schema):
    type: str
    title: str
    status: int
    detail: str
```

```python
# products/services.py
from dataclasses import dataclass


class ProductAlreadyExists(Exception):
    pass


@dataclass(frozen=True)
class ProductResult:
    id: int
    name: str
    price: int


def create_product(*, name: str, price: int) -> ProductResult:
    return ProductResult(id=1, name=name, price=price)
```

```python
# products/api.py
from ninja import Router

from products.schemas import ProblemDetail, ProductCreateIn, ProductOut
from products.services import ProductAlreadyExists, create_product

router = Router(tags=["products"])


@router.post("/products", response={201: ProductOut, 409: ProblemDetail})
def create_product_endpoint(request, payload: ProductCreateIn):
    try:
        return 201, create_product(name=payload.name, price=payload.price)
    except ProductAlreadyExists:
        return 409, {
            "type": "https://api.example.com/problems/product-already-exists",
            "title": "Product already exists",
            "status": 409,
            "detail": f"Product '{payload.name}' already exists.",
        }
```

**REFACTOR 기준**

- endpoint 함수는 schema 변환과 service 호출만 담당한다.
- 중복되는 Problem Details 생성은 `api/errors.py` 같은 helper로 이동한다.
- service 테스트는 별도로 작성하고, 거기서는 service를 mock하지 않는다.
- service가 repository를 쓰면 `InMemoryProductRepository` Fake를 우선 사용한다.
- 인증이 있으면 endpoint 테스트에 `client.force_login(...)` 또는 Ninja auth test hook을 별도 fixture로 둔다.
- 목록 endpoint는 반드시 pagination 응답 구조와 빈 목록 케이스를 함께 테스트한다.

**검증 명령**

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/integration/products/test_product_api.py -q
```

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated -q --randomly-seed=random
```

---
> **관련 스킬 참조:**
> - Django Ninja endpoint 구현 → **implementation-django-ninja** 스킬
> - pytest 테스트 품질 개선 → **implementation-test** 스킬
> - Red-Green-Refactor 적용 → **implementation-tdd** 스킬