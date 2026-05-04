아래는 Django Ninja endpoint를 pytest로 TDD하는 최소 예시입니다. 흐름은 `테스트 먼저 작성 -> 실패 확인 -> endpoint 구현 -> 성공`입니다.

**1. 테스트 먼저 작성**

```python
# tests/test_item_api.py
import pytest


@pytest.mark.django_db
def test_create_item_validation_error(client):
    response = client.post(
        "/api/items",
        data={
            "name": "",
            "price": -100,
        },
        content_type="application/json",
    )

    assert response.status_code == 422

    body = response.json()
    assert "detail" in body

    error_fields = {
        tuple(error["loc"]) for error in body["detail"]
    }

    assert ("body", "payload", "name") in error_fields
    assert ("body", "payload", "price") in error_fields


@pytest.mark.django_db
def test_create_item_success(client):
    response = client.post(
        "/api/items",
        data={
            "name": "Keyboard",
            "price": 49000,
        },
        content_type="application/json",
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "name": "Keyboard",
        "price": 49000,
    }
```

**2. endpoint 구현**

```python
# app/api.py
from ninja import NinjaAPI, Schema
from pydantic import Field

api = NinjaAPI()


class ItemCreateIn(Schema):
    name: str = Field(..., min_length=1)
    price: int = Field(..., ge=0)


class ItemOut(Schema):
    id: int
    name: str
    price: int


@api.post("/items", response={201: ItemOut})
def create_item(request, payload: ItemCreateIn):
    # 실제 프로젝트에서는 여기서 ORM 저장
    return 201, {
        "id": 1,
        "name": payload.name,
        "price": payload.price,
    }
```

**3. URL 연결**

```python
# project/urls.py
from django.contrib import admin
from django.urls import path

from app.api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
```

**4. pytest 설정 예시**

```ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = project.settings
python_files = test_*.py
```

핵심은 validation 실패 테스트에서 Django Ninja 기본 동작인 `422`를 기대하고, 성공 테스트에서는 `201`과 response schema에 맞는 JSON을 검증하는 것입니다. 실제 DB 모델이 있다면 `create_item` 안에서 ORM으로 저장한 뒤 반환하고, 성공 테스트에서는 `Item.objects.count()`와 저장된 값까지 함께 검증하면 됩니다.