현재 세션은 읽기 전용이라 파일 생성과 `pytest` 실행은 하지 못했습니다. 아래는 그대로 프로젝트에 옮겨서 RED → GREEN → REFACTOR 순서로 진행할 수 있는 Django Ninja TDD 예시입니다. API는 DRF 없이 `Schema`, `Router`, `TestClient`를 사용하고, endpoint는 검증/HTTP 변환만, 생성 로직은 service가 맡습니다.

**RED 테스트**
`tests/isolated/products/test_product_api.py`

```python
import pytest
from ninja.testing import TestClient

from products import api


@pytest.fixture
def client():
    return TestClient(api.router)


def test_create_product_invalid_payload_returns_422(client, monkeypatch):
    # Arrange
    called = False

    def fake_create_product(*args, **kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr(api, "product_create", fake_create_product)

    # Act
    response = client.post(
        "/",
        json={"name": "", "price_cents": 0},
    )

    # Assert
    assert response.status_code == 422
    assert called is False
    assert "detail" in response.json()


def test_create_product_valid_payload_returns_created_product(client, monkeypatch):
    # Arrange
    def fake_create_product(*, name: str, price_cents: int):
        assert name == "Keyboard"
        assert price_cents == 12900
        return {
            "id": 1,
            "name": name,
            "price_cents": price_cents,
        }

    monkeypatch.setattr(api, "product_create", fake_create_product)

    # Act
    response = client.post(
        "/",
        json={"name": "Keyboard", "price_cents": 12900},
    )

    # Assert
    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "name": "Keyboard",
        "price_cents": 12900,
    }
```

**예상 실패**

처음에는 `products.api`, `router`, `product_create`, 요청/응답 schema가 없어서 import 또는 route resolution 단계에서 실패해야 정상입니다. 구현 후에도 validation이 422가 아니거나 성공 응답이 201이 아니면 테스트가 endpoint 계약을 제대로 잡아냅니다.

**GREEN 최소 구현**
`products/schemas.py`

```python
from ninja import Schema
from pydantic import Field


class ProductCreateIn(Schema):
    name: str = Field(..., min_length=1)
    price_cents: int = Field(..., gt=0)


class ProductOut(Schema):
    id: int
    name: str
    price_cents: int
```

`products/services.py`

```python
def product_create(*, name: str, price_cents: int) -> dict:
    return {
        "id": 1,
        "name": name,
        "price_cents": price_cents,
    }
```

`products/api.py`

```python
from ninja import Router

from products.schemas import ProductCreateIn, ProductOut
from products.services import product_create

router = Router()


@router.post("/", response={201: ProductOut})
def create_product(request, payload: ProductCreateIn):
    return 201, product_create(
        name=payload.name,
        price_cents=payload.price_cents,
    )
```

실제 API 합성 위치:

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

endpoint test는 `Ninja TestClient`로 schema validation, status code, response contract만 검증합니다. DB 저장, 중복 상품명 검사, 재고 정책 같은 비즈니스 규칙은 `products.services.product_create`의 별도 service test로 분리하는 편이 좋습니다. service가 Django ORM을 사용하게 되면 `@pytest.mark.django_db`를 service test에만 붙이고, 위 endpoint test는 monkeypatch로 빠르게 유지합니다.

실행 명령:

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/products/test_product_api.py -q
```

전체 isolated 테스트:

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated -q
```

---
> **관련 스킬 참조:**
> - Django Ninja endpoint 구현 → **implementation-django-ninja** 스킬
> - pytest 구조와 fixture 개선 → **implementation-test** 스킬
> - service 책임 분리와 도메인 규칙 설계 → **architecture-ddd** 스킬