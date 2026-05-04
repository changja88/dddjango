현재 `/private/tmp/dddjango-codex-eval`은 비어 있고 `config.toml`도 없어 파일로 추가하진 못했습니다. 아래 내용을 저장소 표준으로 두면 됩니다.

**Django Ninja Endpoint Pytest 표준**

1. 기본 원칙
- 엔드포인트 테스트는 `pytest` + `pytest-django`를 표준으로 한다.
- 실제 URL, 미들웨어, 인증까지 검증해야 하는 테스트는 Django `client` fixture를 사용한다.
- 라우터 단위 계약 테스트만 필요하면 `ninja.testing.TestClient`를 사용한다.
- DB 접근 테스트에는 반드시 `@pytest.mark.django_db`를 붙인다.
- 외부 API, 메일, 큐, 파일 스토리지는 mock/fake 처리한다. ORM 자체는 mock하지 않는다.

2. 테스트 위치
```text
app/
  tests/
    test_<resource>_api.py
```

예:
```text
users/tests/test_user_api.py
orders/tests/test_order_api.py
```

3. 테스트 케이스 최소 세트
각 Ninja endpoint는 가능한 범위에서 아래를 검증한다.

- 성공 응답: status code, response body, schema shape
- 입력 검증 실패: `422`
- 인증 실패: `401`
- 권한 실패: `403`
- 리소스 없음: `404`
- DB side effect: 생성/수정/삭제 결과
- 외부 호출 여부: mock 호출 인자

4. 권장 스타일
```python
import pytest

pytestmark = pytest.mark.django_db


def test_create_user_success(client, user_payload):
    response = client.post(
        "/api/users",
        data=user_payload,
        content_type="application/json",
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == user_payload["email"]
    assert "id" in body


def test_create_user_validation_error(client):
    response = client.post(
        "/api/users",
        data={"email": "invalid"},
        content_type="application/json",
    )

    assert response.status_code == 422
```

5. 인증 테스트 표준
```python
pytestmark = pytest.mark.django_db


def test_me_requires_auth(client):
    response = client.get("/api/me")

    assert response.status_code == 401


def test_me_success(auth_client, user):
    response = auth_client.get("/api/me")

    assert response.status_code == 200
    assert response.json()["id"] == user.id
```

`conftest.py` 예시:
```python
import pytest


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client
```

토큰 인증이면:
```python
@pytest.fixture
def auth_client(client, access_token):
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
    return client
```

6. Ninja `TestClient` 사용 기준
라우터 함수의 request/response 계약만 빠르게 검증할 때 사용한다.

```python
import pytest
from ninja.testing import TestClient

from users.api import router

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return TestClient(router)


def test_user_detail(api_client, user):
    response = api_client.get(f"/{user.id}")

    assert response.status_code == 200
    assert response.json()["id"] == user.id
```

단, `TestClient(router)`는 Django URLConf, middleware, 실제 인증 흐름 검증에는 적합하지 않다. 그런 경우 Django `client`를 사용한다.

7. Assertion 규칙
- status code는 항상 첫 번째로 검증한다.
- 응답 body는 필요한 필드를 명시적으로 검증한다.
- 전체 JSON 비교는 응답이 작고 안정적일 때만 사용한다.
- 시간, UUID, 정렬 비보장 필드는 고정 fixture나 부분 검증을 사용한다.
- 생성/수정/삭제 endpoint는 DB 상태를 다시 조회해서 검증한다.

```python
def test_update_order_status(client, order):
    response = client.patch(
        f"/api/orders/{order.id}",
        data={"status": "paid"},
        content_type="application/json",
    )

    assert response.status_code == 200

    order.refresh_from_db()
    assert order.status == "paid"
```

8. Fixture 표준
- 모델 생성은 factory를 우선 사용한다.
- 테스트 안에서 복잡한 객체를 직접 조립하지 않는다.
- 공통 fixture는 앱별 `tests/conftest.py`에 둔다.
- 전역 fixture는 루트 `conftest.py`에만 둔다.

권장:
```python
@pytest.fixture
def user(db, user_factory):
    return user_factory(email="user@example.com")
```

9. 네이밍 규칙
```text
test_<행위>_<조건>_<기대결과>
```

예:
```python
def test_create_order_with_valid_payload_returns_201():
    ...

def test_create_order_without_auth_returns_401():
    ...

def test_get_order_owned_by_other_user_returns_403():
    ...
```

10. 실행 명령
```bash
pytest
pytest users/tests/test_user_api.py
pytest users/tests/test_user_api.py::test_create_user_success
```

이 표준의 핵심은 “실제 API 동작 검증은 Django `client`, 라우터 단위 계약 검증은 Ninja `TestClient`”로 나누는 것입니다.