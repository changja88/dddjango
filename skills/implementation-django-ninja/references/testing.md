# 테스팅 레퍼런스

## 1. TestClient 기본 사용

Django Ninja는 API 테스트를 위한 전용 `TestClient`를 제공한다. `router` 또는 `api` 인스턴스를 인자로 받는다.

```python
from django.test import TestCase
from ninja.testing import TestClient
from myapp.api import router

class HelloTest(TestCase):
    def test_hello(self):
        client = TestClient(router)
        response = client.get("/hello")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"msg": "Hello World"})
```

### 지원하는 HTTP 메서드

```python
client = TestClient(router)

# GET
response = client.get("/items")

# POST (JSON body)
response = client.post("/items", json={"name": "Item1", "price": 100})

# PUT
response = client.put("/items/1", json={"name": "Updated"})

# PATCH
response = client.patch("/items/1", json={"price": 200})

# DELETE
response = client.delete("/items/1")
```

## 2. response.json() vs response.data

응답 데이터에 접근하는 두 가지 방법이 있다.

| 메서드 | 반환 타입 | 설명 |
|---|---|---|
| `response.json()` | JSON 직렬화된 문자열 파싱 결과 | 실제 JSON 직렬화/역직렬화 과정을 거침 |
| `response.data` | Python 객체 | 역직렬화된 Python 네이티브 객체 |

```python
def test_response_access(self):
    client = TestClient(router)
    response = client.get("/hello")

    # 두 방법 모두 동일한 결과
    self.assertEqual(response.json(), {"msg": "Hello World"})
    self.assertEqual(response.data, {"msg": "Hello World"})
```

`response.data`는 datetime, UUID 등 JSON 직렬화가 필요한 타입을 Python 객체 그대로 반환하므로, 타입별 비교가 필요할 때 유용하다.

## 3. 커스텀 요청 속성 주입

키워드 인자를 전달하여 `request` 객체에 속성을 주입할 수 있다.

```python
# 뷰에서 request.company_id 사용
@router.get("/company-data")
def get_company_data(request):
    company_id = request.company_id
    return {"company_id": company_id}

# 테스트에서 속성 주입
def test_company_data(self):
    client = TestClient(router)
    response = client.get("/company-data", company_id=1)
    self.assertEqual(response.json(), {"company_id": 1})
```

## 4. 헤더 설정

클라이언트 인스턴스 생성 시 또는 요청별로 헤더를 설정한다. 요청별 헤더가 클라이언트 헤더를 오버라이드한다.

```python
# 클라이언트 레벨 헤더
client = TestClient(router, headers={"A": "a", "B": "b"})

# 요청 레벨 헤더 (클라이언트 헤더와 병합, 중복 시 오버라이드)
response = client.get("/test-headers", headers={"A": "na", "C": "nc"})
# 최종 헤더: {"A": "na", "B": "b", "C": "nc"}
```

### 헤더를 검증하는 뷰 테스트

```python
@router.get("/check-auth")
def check_auth(request):
    token = request.headers.get("Authorization")
    return {"has_token": token is not None}

def test_auth_header(self):
    client = TestClient(router)
    response = client.get(
        "/check-auth",
        headers={"Authorization": "Bearer test-token"},
    )
    self.assertEqual(response.json(), {"has_token": True})
```

## 5. 쿠키 설정

헤더와 동일한 패턴으로 쿠키를 설정한다.

```python
# 클라이언트 레벨 쿠키
client = TestClient(router, COOKIES={"A": "a", "B": "b"})

# 요청 레벨 쿠키 (클라이언트 쿠키와 병합, 중복 시 오버라이드)
response = client.get("/test-cookies", COOKIES={"A": "na", "C": "nc"})
# 최종 쿠키: {"A": "na", "B": "b", "C": "nc"}
```

## 6. 사용자 인증 테스트

`user` 파라미터로 Django User 객체를 주입하여 인증된 요청을 시뮬레이션한다.

```python
from django.contrib.auth.models import User

@router.get("/profile")
def get_profile(request):
    return {
        "username": request.user.username,
        "is_authenticated": request.user.is_authenticated,
    }

class AuthTest(TestCase):
    def test_authenticated_user(self):
        user = User.objects.create_user(
            username="testuser",
            password="testpass",
        )
        client = TestClient(router)
        response = client.get("/profile", user=user)
        self.assertEqual(response.json(), {
            "username": "testuser",
            "is_authenticated": True,
        })

    def test_anonymous_user(self):
        client = TestClient(router)
        response = client.get("/profile")
        self.assertEqual(response.json()["is_authenticated"], False)
```

## 7. TestAsyncClient

비동기 엔드포인트 테스트에는 `TestAsyncClient`를 사용한다.

```python
from ninja.testing import TestAsyncClient

@router.post("/async-create")
async def async_create(request, data: ItemSchema):
    item = await sync_to_async(Item.objects.create)(**data.dict())
    return {"id": item.id}

# 테스트
class AsyncTest(TestCase):
    async def test_async_create(self):
        client = TestAsyncClient(router)
        response = await client.post(
            "/async-create",
            json={"name": "Async Item", "price": 100},
        )
        self.assertEqual(response.status_code, 200)
```

### TestAsyncClient 사용 시 주의사항

- 테스트 메서드도 `async def`로 선언해야 한다
- Django 4.1+에서는 `django.test.TestCase`가 async 테스트를 지원한다
- 그 이전 버전에서는 `django.test.TransactionTestCase` 사용을 권장한다

## 8. pytest 통합

pytest와 함께 사용할 때의 패턴이다.

### 기본 구조

```python
import pytest
from ninja.testing import TestClient
from myapp.api import router

@pytest.fixture
def client():
    return TestClient(router)

def test_hello(client):
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
```

### DB 접근이 필요한 테스트

```python
import pytest
from django.contrib.auth.models import User
from ninja.testing import TestClient
from myapp.api import router

@pytest.fixture
def client():
    return TestClient(router)

@pytest.fixture
def auth_user(db):
    return User.objects.create_user(
        username="testuser",
        password="testpass",
    )

@pytest.mark.django_db
def test_authenticated_endpoint(client, auth_user):
    response = client.get("/profile", user=auth_user)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
```

### async 테스트 (pytest-asyncio)

```python
import pytest
from ninja.testing import TestAsyncClient
from myapp.api import router

@pytest.fixture
def async_client():
    return TestAsyncClient(router)

@pytest.mark.asyncio
async def test_async_endpoint(async_client):
    response = await async_client.get("/async-endpoint")
    assert response.status_code == 200
```

## 9. 테스트 패턴 요약

| 상황 | 클라이언트 | 메서드 |
|---|---|---|
| 동기 엔드포인트 | `TestClient(router)` | `client.get()`, `client.post()` 등 |
| 비동기 엔드포인트 | `TestAsyncClient(router)` | `await client.get()` 등 |
| 인증 필요 | `client.get(path, user=user)` | user 파라미터 주입 |
| 커스텀 헤더 | `TestClient(router, headers={...})` | 클라이언트 또는 요청 레벨 |
| 커스텀 속성 | `client.get(path, attr=value)` | 키워드 인자로 주입 |
