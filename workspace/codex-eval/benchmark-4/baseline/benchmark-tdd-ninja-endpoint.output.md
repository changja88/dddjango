현재 workspace가 비어 있고 읽기 전용이라 파일을 만들지는 못했습니다. 아래는 Django Ninja에서 “테스트 먼저 작성 → endpoint 구현” 흐름으로 바로 적용할 수 있는 최소 예시입니다.

**1. 실패/성공 테스트 먼저 작성**

```python
# tests/test_users_api.py
import pytest
from ninja.testing import TestClient

from app.api import router


@pytest.fixture
def client():
    return TestClient(router)


def test_create_user_validates_request_schema(client):
    response = client.post(
        "/users",
        json={
            "email": "not-an-email",
            "name": "",
            "age": 12,
        },
    )

    assert response.status_code == 422

    body = response.json()
    assert "detail" in body

    errors = str(body["detail"])
    assert "email" in errors
    assert "name" in errors
    assert "age" in errors


def test_create_user_returns_success_response(client):
    response = client.post(
        "/users",
        json={
            "email": "user@example.com",
            "name": "Kim",
            "age": 20,
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "email": "user@example.com",
        "name": "Kim",
        "age": 20,
    }
```

처음에는 `app.api`가 없거나 endpoint가 없어서 테스트가 실패합니다.

**2. 테스트를 통과시키는 최소 구현**

```python
# app/api.py
from ninja import Router, Schema, Field
from pydantic import EmailStr


router = Router()


class CreateUserRequest(Schema):
    email: EmailStr
    name: str = Field(..., min_length=1)
    age: int = Field(..., ge=18)


class UserResponse(Schema):
    id: int
    email: str
    name: str
    age: int


@router.post("/users", response={201: UserResponse})
def create_user(request, payload: CreateUserRequest):
    return 201, {
        "id": 1,
        "email": payload.email,
        "name": payload.name,
        "age": payload.age,
    }
```

**3. 프로젝트 API에 router 연결**

```python
# project/api.py
from ninja import NinjaAPI

from app.api import router as users_router


api = NinjaAPI()
api.add_router("", users_router)
```

```python
# project/urls.py
from django.urls import path

from project.api import api


urlpatterns = [
    path("api/", api.urls),
]
```

테스트 실행:

```bash
pytest
```

핵심은 `TestClient`로 실제 HTTP 요청처럼 `json` payload를 보내고, 잘못된 schema는 `422`, 정상 요청은 `201`과 response schema 형태를 검증하는 것입니다. `EmailStr`를 쓰면 환경에 따라 `email-validator` 패키지가 필요할 수 있습니다.