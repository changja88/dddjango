**주요 내용**

프로젝트 파일이 없는 읽기 전용 환경이라 pytest를 실제로 실행하지는 못했습니다. 아래는 `products` 앱이 있다고 가정한 Django Ninja TDD 예시입니다. 이 프로젝트 정책상 DRF가 아니라 Django Ninja `Schema`/`Router`로 작성합니다.

### RED: 실패하는 pytest 먼저

`tests/isolated/integration/products/test_create_product_api.py`

```python
import pytest
from ninja.testing import TestClient

from products.api import router
from products.models import Product


@pytest.fixture
def client() -> TestClient:
    return TestClient(router)


@pytest.mark.django_db
def test_create_product_rejects_invalid_request_schema(client: TestClient) -> None:
    response = client.post(
        "/",
        json={
            "name": "",
            "price_cents": 0,
        },
    )

    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.django_db
def test_create_product_returns_created_product(client: TestClient) -> None:
    response = client.post(
        "/",
        json={
            "name": "Mechanical Keyboard",
            "price_cents": 12900,
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": Product.objects.get().id,
        "name": "Mechanical Keyboard",
        "price_cents": 12900,
        "is_active": True,
    }
```

예상 실패 이유:

- `products.api.router`가 아직 없어서 import 실패
- `Product` 모델이 없으면 import 실패
- 엔드포인트가 없으면 404
- 요청 `Schema`가 없으면 빈 이름/0원 가격 검증 실패를 잡지 못함
- 성공 응답 `response={201: ProductOut}`가 없으면 200 또는 다른 응답 모양이 나옴

### GREEN: 최소 구현

`products/models.py`

```python
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=120)
    price_cents = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name
```

`products/schemas.py`

```python
from ninja import Schema
from pydantic import Field


class ProductCreateIn(Schema):
    name: str = Field(..., min_length=1, max_length=120)
    price_cents: int = Field(..., gt=0)


class ProductOut(Schema):
    id: int
    name: str
    price_cents: int
    is_active: bool
```

`products/api.py`

```python
from django.http import HttpRequest
from ninja import Router

from products.models import Product
from products.schemas import ProductCreateIn, ProductOut

router = Router(tags=["products"])


@router.post("/", response={201: ProductOut})
def create_product(
    request: HttpRequest,
    payload: ProductCreateIn,
) -> tuple[int, Product]:
    product = Product.objects.create(
        name=payload.name,
        price_cents=payload.price_cents,
    )
    return 201, product
```

`config/api.py`

```python
from ninja import NinjaAPI

from products.api import router as products_router

api = NinjaAPI()
api.add_router("/products", products_router)
```

`config/urls.py`

```python
from django.urls import path

from config.api import api

urlpatterns = [
    path("api/", api.urls),
]
```

실제 API 경로는 `POST /api/products`입니다. 테스트에서는 `TestClient(router)`를 직접 쓰기 때문에 라우터 내부 경로인 `"/"`로 호출합니다.

### REFACTOR 방향

그린 상태가 된 뒤에는 다음 순서로 정리합니다.

- 생성 로직이 커지면 `products/services.py`의 `product_create(...)` 함수로 분리
- 중복 이름, 재고 정책, 가격 정책 같은 도메인 규칙은 모델 제약조건 또는 서비스에서 명시
- 검증 실패 응답을 전 API에서 통일하려면 Django Ninja exception handler로 RFC 9457 Problem Details 형식 적용
- 테스트 데이터가 늘어나면 `ProductFactory`를 도입하고 `client` fixture는 `tests/isolated/conftest.py`로 이동

실행 명령:

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/integration/products/test_create_product_api.py -q
```

마이그레이션이 필요한 경우:

```bash
python manage.py makemigrations products
python manage.py migrate
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/integration/products/test_create_product_api.py -q
```

---
> **관련 스킬 참조:**
> - Django Ninja endpoint/schema/router 테스트 → **implementation-django-ninja** 스킬
> - pytest 구조와 isolated 테스트 환경 → **implementation-test** 스킬
> - Red-Green-Refactor 진행 → **implementation-tdd** 스킬