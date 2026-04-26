# D14: implementation-django-ninja 테스팅 (pytest + Router)

## 프롬프트

> Django Ninja API 엔드포인트 테스트를 작성하고 싶어. pytest로 Router 테스트는 어떻게 해?

## 스킬 판정

- **진입 스킬**: implementation-django-ninja (Django Ninja 테스트, API 엔드포인트 테스트 요청)
- **위임 대상**: 없음 (Django Ninja TestClient는 본 스킬 범위)
- **최종 스킬**: implementation-django-ninja
- **모드**: Writing (테스트 코드 작성)

SKILL.md 설명: "test API endpoints"가 트리거 조건에 명시되어 있으며, 섹션 8 "테스팅"이 TestClient, pytest 통합, async 테스트를 다룬다. 참조 파일 `references/testing.md`를 로딩한다.

---

## 응답

Django Ninja는 미들웨어를 우회하는 전용 `TestClient`를 제공한다. pytest와 조합할 때의 핵심 패턴을 정리한다.

### 1. 기본 구조: fixture로 TestClient 생성

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

`TestClient`는 `router`(Router 인스턴스) 또는 `api`(NinjaAPI 인스턴스) 모두 받을 수 있다. Router 단위 테스트를 작성할 때는 `TestClient(router)`를, 글로벌 예외 핸들러나 인증 설정까지 포함해서 테스트할 때는 `TestClient(api)`를 사용한다.

### 2. HTTP 메서드별 요청

```python
def test_crud_operations(client):
    # POST -- JSON body
    response = client.post("/items", json={"name": "Widget", "price": 1500})
    assert response.status_code == 201

    item_id = response.json()["id"]

    # GET -- 단건 조회
    response = client.get(f"/items/{item_id}")
    assert response.json()["name"] == "Widget"

    # PATCH -- 부분 수정
    response = client.patch(f"/items/{item_id}", json={"price": 2000})
    assert response.json()["price"] == 2000

    # DELETE
    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 204
```

### 3. DB 접근이 필요한 테스트

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

`user` 파라미터로 Django User 객체를 주입하면, `request.user`에 해당 사용자가 설정된다. 인증 클래스(HttpBearer 등)의 실제 토큰 검증을 우회하므로, 인증 자체를 테스트하려면 헤더를 직접 설정해야 한다.

### 4. 헤더와 쿠키 설정

```python
@pytest.fixture
def auth_client():
    return TestClient(router, headers={"Authorization": "Bearer test-token"})


def test_with_custom_headers(auth_client):
    response = auth_client.get("/protected")
    assert response.status_code == 200


def test_per_request_header_override(client):
    # 요청별 헤더가 클라이언트 헤더를 오버라이드한다
    response = client.get(
        "/check-auth",
        headers={"Authorization": "Bearer specific-token"},
    )
    assert response.json()["has_token"] is True
```

쿠키도 동일한 패턴이다. `TestClient(router, COOKIES={...})`로 클라이언트 레벨, `client.get(path, COOKIES={...})`로 요청 레벨에서 설정한다.

### 5. 커스텀 요청 속성 주입

미들웨어가 주입하는 커스텀 속성을 테스트에서 직접 주입할 수 있다.

```python
# 뷰: request.tenant_id를 사용
@router.get("/tenant-data")
def get_tenant_data(request) -> dict:
    return {"tenant_id": request.tenant_id}


# 테스트: 키워드 인자로 속성 주입
def test_tenant_data(client):
    response = client.get("/tenant-data", tenant_id=42)
    assert response.json() == {"tenant_id": 42}
```

`TestClient`는 미들웨어를 우회하기 때문에, 미들웨어가 `request`에 붙이는 속성은 이 방식으로 직접 주입해야 한다.

### 6. response.json() vs response.data

```python
def test_response_data_types(client):
    response = client.get("/item/1")

    # json() -- JSON 직렬화/역직렬화를 거친 결과 (문자열 기반)
    assert response.json()["created_at"] == "2026-04-06T00:00:00"

    # data -- Python 네이티브 객체 그대로
    from datetime import datetime
    assert isinstance(response.data["created_at"], datetime)
```

datetime, UUID 등 JSON 직렬화가 필요한 타입을 비교할 때는 `response.data`가 Python 객체를 그대로 반환하므로 타입 안전한 비교가 가능하다.

### 7. async 엔드포인트 테스트

```python
import pytest
from ninja.testing import TestAsyncClient
from myapp.api import router


@pytest.fixture
def async_client():
    return TestAsyncClient(router)


@pytest.mark.asyncio
async def test_async_endpoint(async_client):
    response = await async_client.get("/async-items")
    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_async_create(async_client):
    response = await async_client.post(
        "/async-items",
        json={"name": "Async Widget", "price": 3000},
    )
    assert response.status_code == 201
```

async 뷰에는 `TestAsyncClient`를 사용하고, 테스트 메서드도 `async def`로 선언한다. `pytest-asyncio` 패키지가 필요하다.

### 정리: 상황별 선택

| 상황 | 클라이언트 | 핵심 패턴 |
|------|-----------|-----------|
| 동기 엔드포인트 | `TestClient(router)` | `client.get()`, `client.post()` |
| 비동기 엔드포인트 | `TestAsyncClient(router)` | `await client.get()` + `@pytest.mark.asyncio` |
| 인증 필요 | `TestClient(router)` | `client.get(path, user=user)` |
| 헤더/쿠키 필요 | `TestClient(router, headers={...})` | 클라이언트 또는 요청 레벨 설정 |
| 커스텀 속성 | `TestClient(router)` | `client.get(path, attr=value)` |
| DB 접근 | `@pytest.mark.django_db` | `db` fixture 의존 |

---

> **관련 스킬 참조:**
> - [pytest fixture 설계, conftest 계층, 테스트 구조] -> **implementation-test** 스킬
> - [TDD Red-Green-Refactor 워크플로우] -> **implementation-tdd** 스킬
> - [Django 모델 테스트, TestCase vs TransactionTestCase] -> **implementation-django** 스킬
> - [async 뷰 패턴, ASGI 서버 구성] -> **implementation-django-ninja** 스킬 (async-support 참조)
> - [API 설계 원칙, 상태 코드 선택] -> **architecture-api** 스킬
