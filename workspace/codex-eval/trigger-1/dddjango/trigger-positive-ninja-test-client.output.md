**주요 내용**

현재 workspace는 비어 있고 sandbox가 read-only라 테스트 파일 생성이나 `pytest` 실행은 할 수 없었습니다. 아래는 이 프로젝트에서 Django Ninja endpoint를 pytest로 테스트할 때의 표준입니다. 이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja `Schema` / `Router` / `ninja.testing.TestClient` 기준으로 작성합니다.

## 1. 테스트 배치 표준

테스트 디렉토리는 실행 환경을 1차 축, 테스트 범위를 2차 축으로 둡니다.

```text
tests/
  conftest.py
  isolated/
    conftest.py
    unit/
    integration/
      conftest.py
      test_products_api.py
  real/
    conftest.py
    integration/
    e2e/
```

- `tests/isolated/`: CI 기본 스위트. Fake, Mock, in-memory DB, testcontainers처럼 통제된 환경만 사용합니다. 네트워크와 시계는 차단/고정합니다.
- `tests/real/`: 실 DB, 실 외부 서비스, stage 환경 같은 운영 동등 인프라 검증용입니다. pre-deploy gate에서만 실행합니다.
- Django isolated 테스트는 운영 settings가 아니라 `config.settings.test`로 실행합니다.
- real 테스트는 `config.settings.test_real` 또는 stage settings로 실행합니다.

`pyproject.toml` 표준:

```toml
[tool.pytest.ini_options]
minversion = "8.0"
DJANGO_SETTINGS_MODULE = "config.settings.test"
testpaths = ["tests/isolated", "tests/real"]
addopts = [
    "-ra",
    "-q",
    "--strict-markers",
    "--strict-config",
    "--tb=short",
]
python_files = ["test_*.py", "*_test.py"]
python_functions = ["test_*"]
markers = [
    "isolated: 통제된/제공된 테스트 환경에서 수행",
    "real: 실제 운영 환경에서 수행",
    "integration: 통합 범위 테스트",
    "e2e: 엔드투엔드 테스트",
    "slow: 느린 테스트",
]
```

`config/settings/test.py`에는 최소한 다음을 둡니다.

```python
from .base import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
```

## 2. Django Ninja endpoint 테스트 원칙

Django Ninja endpoint는 `ninja.testing.TestClient`를 기본으로 테스트합니다.

```python
import pytest
from ninja.testing import TestClient

from apps.products.api import router


@pytest.fixture
def client():
    return TestClient(router)
```

라우터 단위 테스트는 mounted prefix를 제외한 경로를 사용합니다.

```python
response = client.get("/")
```

전체 API 합성까지 검증해야 하면 `Router`가 아니라 `NinjaAPI` 인스턴스를 대상으로 둡니다.

```python
from ninja.testing import TestClient

from config.api import api


@pytest.fixture
def api_client():
    return TestClient(api)
```

## 3. endpoint 테스트에서 반드시 검증할 것

각 endpoint 테스트는 하나의 Act만 가져야 합니다.

```python
def test_list_products_returns_products(client, product_factory):
    product = product_factory(name="Keyboard")

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": product.id,
            "name": "Keyboard",
        }
    ]
```

표준 검증 항목:

- HTTP status code
- response JSON contract
- DB side effect
- 인증/인가 결과
- validation error
- error response 형식
- pagination/filtering contract
- 중요한 read endpoint의 query count

DB 접근 테스트는 명시적으로 표시합니다.

```python
@pytest.mark.django_db
def test_create_product_creates_row(client):
    response = client.post(
        "/",
        json={
            "name": "Keyboard",
            "price": "129.00",
        },
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Keyboard"
    assert Product.objects.count() == 1
```

인증은 Django Ninja 테스트 클라이언트의 `user=` 주입을 사용합니다.

```python
@pytest.mark.django_db
def test_profile_requires_authenticated_user(client, user):
    response = client.get("/profile", user=user)

    assert response.status_code == 200
    assert response.json()["username"] == user.username
```

헤더 기반 인증은 요청별 `headers`로 검증합니다.

```python
def test_bearer_token_auth(client):
    response = client.get(
        "/secure",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
```

validation error는 Django Ninja 기본값인 `422`를 기준으로 확인합니다.

```python
@pytest.mark.django_db
def test_create_product_rejects_missing_name(client):
    response = client.post("/", json={"price": "129.00"})

    assert response.status_code == 422
    assert "detail" in response.json()
```

비동기 endpoint는 `TestAsyncClient`를 사용합니다.

```python
import pytest
from ninja.testing import TestAsyncClient

from apps.products.api import router


@pytest.fixture
def async_client():
    return TestAsyncClient(router)


@pytest.mark.asyncio
async def test_async_endpoint(async_client):
    response = await async_client.get("/async-health")

    assert response.status_code == 200
```

## 4. isolated 환경 conftest 표준

`tests/isolated/conftest.py`:

```python
import socket

import pytest


@pytest.fixture(autouse=True)
def _block_network(monkeypatch):
    def guard(*args, **kwargs):
        raise RuntimeError(
            "tests/isolated/에서는 네트워크 호출이 금지됩니다. "
            "responses/respx로 모킹하거나 testcontainers를 사용하세요."
        )

    monkeypatch.setattr(socket, "socket", guard)


@pytest.fixture(autouse=True)
def _freeze_clock():
    import time_machine

    with time_machine.travel("2025-01-01T00:00:00Z", tick=False):
        yield
```

시간 모킹은 `time-machine`을 기본으로 사용합니다. `freezegun`은 순수 Python 구현인 반면 `time-machine`은 C 확장으로 구현되어 있어 동일 작업에서 100~200배 빠릅니다. 시간 모킹이 많은 테스트 스위트에서는 실행 시간 차이가 실제로 커집니다.

## 5. RED pytest 예시

가정: `apps.products.api.router`에 `POST /` 상품 생성 endpoint를 추가하려는 상황입니다.

`tests/isolated/integration/test_products_api.py`:

```python
import pytest
from ninja.testing import TestClient

from apps.products.api import router
from apps.products.models import Product


@pytest.fixture
def client():
    return TestClient(router)


@pytest.mark.django_db
def test_create_product_returns_created_product(client):
    response = client.post(
        "/",
        json={
            "name": "Keyboard",
            "price": "129.00",
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": Product.objects.get().id,
        "name": "Keyboard",
        "price": "129.00",
    }
    assert Product.objects.count() == 1


@pytest.mark.django_db
def test_create_product_rejects_negative_price(client):
    response = client.post(
        "/",
        json={
            "name": "Keyboard",
            "price": "-1.00",
        },
    )

    assert response.status_code == 422
    assert Product.objects.count() == 0
```

예상 실패 이유:

- `apps.products.api`가 없으면 import error
- `router`가 없으면 import error
- `Product` 모델이 없으면 import error
- `POST /` endpoint가 없으면 404
- price validation이 없으면 negative price 테스트 실패

## 6. GREEN 최소 구현 스케치

`apps/products/schemas.py`:

```python
from decimal import Decimal

from ninja import Schema
from pydantic import field_validator


class ProductCreateSchema(Schema):
    name: str
    price: Decimal

    @field_validator("price")
    @classmethod
    def validate_price(cls, value: Decimal) -> Decimal:
        if value < 0:
            raise ValueError("price must be greater than or equal to 0")
        return value


class ProductOutSchema(Schema):
    id: int
    name: str
    price: Decimal
```

`apps/products/api.py`:

```python
from ninja import Router

from apps.products.models import Product
from apps.products.schemas import ProductCreateSchema, ProductOutSchema

router = Router()


@router.post("/", response={201: ProductOutSchema})
def create_product(request, payload: ProductCreateSchema) -> tuple[int, Product]:
    product = Product.objects.create(
        name=payload.name,
        price=payload.price,
    )
    return 201, product
```

`config/api.py`:

```python
from ninja import NinjaAPI

from apps.products.api import router as products_router

api = NinjaAPI()
api.add_router("/products/", products_router)
```

`config/urls.py`:

```python
from django.urls import path

from config.api import api

urlpatterns = [
    path("api/", api.urls),
]
```

## 7. REFACTOR 방향

테스트가 늘어나면 다음 순서로 정리합니다.

- `client`, `api_client`, `user`, `admin_user` fixture는 `tests/isolated/integration/conftest.py`로 이동
- 모델 생성은 직접 `Product.objects.create()`보다 Factory Boy의 `ProductFactory` 사용
- 외부 결제, 이메일, 검색 API는 `responses` 또는 `respx`로 모킹
- Repository/Gateway 의존성은 무분별한 `MagicMock`보다 `InMemoryProductRepository` 같은 Fake 사용
- Mock을 써야 하면 `spec=` 또는 `create_autospec()`으로 인터페이스를 강제
- 목록 endpoint에는 pagination contract와 `django_assert_num_queries`를 추가
- 경계값은 `price=-1`, `price=0`, `price=1`처럼 mutation testing 관점에서 확인
- 테스트 순서 격리는 `pytest-randomly`로 확인

실행 명령:

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/ -q
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/integration/test_products_api.py -q
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/ --randomly-seed=last
DJANGO_SETTINGS_MODULE=config.settings.test_real pytest tests/real/ -q
```

---
> **관련 스킬 참조:**
> - Django Ninja endpoint 구현/테스트 → **implementation-django-ninja** 스킬
> - pytest fixture/격리/품질 표준 → **implementation-test** 스킬
> - Django settings/pytest-django 기준 → **implementation-django** 스킬