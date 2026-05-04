현재 `/private/tmp/dddjango-codex-eval` 디렉터리는 비어 있고, 세션이 읽기 전용이라 파일 생성은 할 수 없습니다. 대신 바로 저장해서 사용할 수 있는 표준안을 정리했습니다.

**Django Ninja Endpoint Pytest 표준**

```md
# Django Ninja Endpoint Test Standard

## 기본 원칙

- Django Ninja endpoint는 가능하면 `TestClient(router_or_api)`로 테스트한다.
- HTTP 상태 코드, 응답 JSON, DB side effect를 함께 검증한다.
- 인증, 권한, validation error, not found, success path를 분리해서 테스트한다.
- endpoint 내부 구현 함수는 mock하지 않고, 외부 I/O만 mock한다.
- 테스트명은 `test_<조건>__<기대결과>` 형식을 사용한다.

## 권장 도구

- `pytest`
- `pytest-django`
- `django-ninja`의 `TestClient`
- `model_bakery` 또는 `factory_boy`
- `pytest-mock`

## 파일 구조

```text
app/
  api.py
  models.py
  tests/
    test_api_<resource>.py
    factories.py
```

## 기본 예시

```python
import pytest
from ninja.testing import TestClient

from app.api import router
from app.models import Book

pytestmark = pytest.mark.django_db

client = TestClient(router)


def test_create_book__returns_201_and_creates_book():
    response = client.post(
        "/books",
        json={
            "title": "Clean Architecture",
            "author": "Robert C. Martin",
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": Book.objects.get().id,
        "title": "Clean Architecture",
        "author": "Robert C. Martin",
    }

    assert Book.objects.count() == 1
```

## 인증 테스트

```python
def test_get_me__without_auth_returns_401():
    response = client.get("/me")

    assert response.status_code == 401


def test_get_me__with_auth_returns_current_user(user):
    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {user.token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == user.id
```

## Validation Error 테스트

```python
def test_create_book__invalid_payload_returns_422():
    response = client.post(
        "/books",
        json={
            "title": "",
        },
    )

    assert response.status_code == 422

    body = response.json()
    assert "detail" in body
```

## Not Found 테스트

```python
def test_get_book__missing_book_returns_404():
    response = client.get("/books/999999")

    assert response.status_code == 404
```

## Mock 기준

외부 API, 메일, 큐, 파일 스토리지만 mock한다.

```python
def test_create_order__sends_email(mocker, user):
    send_email = mocker.patch("orders.services.send_order_email")

    response = client.post("/orders", json={"item_id": 1})

    assert response.status_code == 201
    send_email.assert_called_once()
```

## Fixture 기준

- 반복되는 DB 객체는 fixture 또는 factory로 만든다.
- 테스트 본문 안에서는 endpoint 입력과 검증에 집중한다.

```python
@pytest.fixture
def book():
    return Book.objects.create(
        title="Domain-Driven Design",
        author="Eric Evans",
    )
```

## 필수 커버리지

각 endpoint는 최소 다음 케이스를 가진다.

- 성공 응답
- request schema validation 실패
- 인증 실패
- 권한 실패
- 대상 리소스 없음
- DB 변경 여부
- 외부 side effect 호출 여부

## 금지사항

- endpoint 테스트에서 Django view internals를 직접 호출하지 않는다.
- `response.json()` 전체 구조가 중요한 경우를 제외하고 과도한 snapshot 테스트를 피한다.
- 테스트 간 DB 상태를 공유하지 않는다.
- 단순히 status code만 검증하고 끝내지 않는다.
```

이 표준은 `docs/testing/django-ninja-pytest.md` 또는 팀 규칙이면 `AGENTS.md`/`CONTRIBUTING.md`에 넣는 게 적절합니다.