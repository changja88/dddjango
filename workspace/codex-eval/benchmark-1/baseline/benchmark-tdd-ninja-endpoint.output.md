현재 디렉터리에 `config.toml`이나 Django 프로젝트 파일이 없어서, 바로 붙여 넣어 쓸 수 있는 일반적인 Django Ninja + pytest TDD 예시로 보여드릴게요.

아래 예시는 “상품 생성 API”를 TDD로 만든다고 가정합니다.

**1. 실패하는 테스트부터 작성**

```python
# tests/test_product_api.py
import pytest
from ninja.testing import TestClient

from myapp.api import api


client = TestClient(api)


@pytest.mark.django_db
def test_create_product_validation_error():
    response = client.post(
        "/products",
        json={
            "name": "",
            "price": -100,
        },
    )

    assert response.status_code == 422

    errors = response.json()["detail"]
    assert any(error["loc"] == ["body", "payload", "name"] for error in errors)
    assert any(error["loc"] == ["body", "payload", "price"] for error in errors)


@pytest.mark.django_db
def test_create_product_success():
    response = client.post(
        "/products",
        json={
            "name": "Keyboard",
            "price": 120000,
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "name": "Keyboard",
        "price": 120000,
    }
```

**2. 최소 구현 추가**

```python
# myapp/models.py
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
```

```python
# myapp/api.py
from ninja import NinjaAPI, Schema
from pydantic import Field

from myapp.models import Product


api = NinjaAPI()


class ProductCreateRequest(Schema):
    name: str = Field(..., min_length=1)
    price: int = Field(..., gt=0)


class ProductResponse(Schema):
    id: int
    name: str
    price: int


@api.post("/products", response={201: ProductResponse})
def create_product(request, payload: ProductCreateRequest):
    product = Product.objects.create(
        name=payload.name,
        price=payload.price,
    )

    return 201, product
```

**3. URL 연결**

```python
# project/urls.py
from django.contrib import admin
from django.urls import path

from myapp.api import api


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
```

**4. 실행**

```bash
pytest
```

핵심 흐름은 이렇습니다.

1. `422 validation error` 테스트를 먼저 작성한다.
2. `201 success response` 테스트를 작성한다.
3. Ninja `Schema`에 `min_length`, `gt` 같은 검증 조건을 둔다.
4. endpoint는 검증을 통과한 payload만 받아 DB에 저장한다.
5. 테스트가 통과할 만큼만 구현한다.

참고로 `ninja.testing.TestClient(api)`를 쓰면 Django URL 라우팅 전체를 띄우지 않고 Ninja API 객체 단위로 빠르게 테스트할 수 있습니다. 실제 `/api/products` 경로까지 포함한 통합 테스트가 필요하면 Django의 `client.post("/api/products", ...)`를 쓰는 방식으로 바꾸면 됩니다.