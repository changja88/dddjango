아래는 “유저 생성” Django Ninja endpoint를 pytest로 TDD하는 작은 예시입니다. 핵심은 endpoint 테스트가 다음을 모두 고정하게 만드는 것입니다.

- 요청 schema validation
- 실패 응답
- 성공 응답
- edge case
- 도메인 예외
- Result Type 기반 흐름

## 예시 구조

```text
users/
  api.py
  schemas.py
  service.py
  result.py
  exceptions.py
  tests/
    test_create_user_api.py
```

## 1. 테스트부터 작성

```python
# users/tests/test_create_user_api.py

import pytest
from ninja.testing import TestClient

from users.api import router


@pytest.fixture
def client():
    return TestClient(router)


def test_create_user_success(client, monkeypatch):
    def fake_create_user(command):
        return {
            "id": 1,
            "email": command.email,
            "nickname": command.nickname,
        }

    monkeypatch.setattr("users.api.create_user", fake_create_user)

    response = client.post(
        "/users",
        json={
            "email": "tester@example.com",
            "nickname": "tester",
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "email": "tester@example.com",
        "nickname": "tester",
    }


def test_create_user_request_validation_fails(client):
    response = client.post(
        "/users",
        json={
            "email": "not-an-email",
            "nickname": "tester",
        },
    )

    assert response.status_code == 422


def test_create_user_missing_required_field(client):
    response = client.post(
        "/users",
        json={
            "email": "tester@example.com",
        },
    )

    assert response.status_code == 422


def test_create_user_duplicate_email(client, monkeypatch):
    from users.result import Err
    from users.exceptions import DuplicateEmail

    def fake_create_user(command):
        return Err(DuplicateEmail(command.email))

    monkeypatch.setattr("users.api.create_user", fake_create_user)

    response = client.post(
        "/users",
        json={
            "email": "tester@example.com",
            "nickname": "tester",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "DUPLICATE_EMAIL",
        "message": "Email already exists.",
    }


def test_create_user_rejects_blank_nickname(client):
    response = client.post(
        "/users",
        json={
            "email": "tester@example.com",
            "nickname": "",
        },
    )

    assert response.status_code == 422


def test_create_user_rejects_too_long_nickname(client):
    response = client.post(
        "/users",
        json={
            "email": "tester@example.com",
            "nickname": "a" * 31,
        },
    )

    assert response.status_code == 422
```

## 2. Result Type

```python
# users/result.py

from dataclasses import dataclass
from typing import Generic, TypeVar, Union

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T


@dataclass(frozen=True)
class Err(Generic[E]):
    error: E


Result = Union[Ok[T], Err[E]]
```

## 3. 도메인 예외

```python
# users/exceptions.py

class DomainError(Exception):
    code = "DOMAIN_ERROR"
    message = "Domain error."


class DuplicateEmail(DomainError):
    code = "DUPLICATE_EMAIL"
    message = "Email already exists."

    def __init__(self, email: str):
        self.email = email
        super().__init__(self.message)
```

## 4. Schema

```python
# users/schemas.py

from ninja import Schema
from pydantic import EmailStr, Field


class CreateUserRequest(Schema):
    email: EmailStr
    nickname: str = Field(min_length=1, max_length=30)


class CreateUserResponse(Schema):
    id: int
    email: EmailStr
    nickname: str


class ErrorResponse(Schema):
    code: str
    message: str
```

## 5. Service

```python
# users/service.py

from dataclasses import dataclass

from users.exceptions import DuplicateEmail
from users.result import Err, Ok, Result


@dataclass(frozen=True)
class CreateUserCommand:
    email: str
    nickname: str


def create_user(command: CreateUserCommand) -> Result[dict, DuplicateEmail]:
    # 실제 구현에서는 ORM 조회/저장이 들어간다.
    # 예:
    # if User.objects.filter(email=command.email).exists():
    #     return Err(DuplicateEmail(command.email))
    #
    # user = User.objects.create(...)
    # return Ok(user)

    return Ok(
        {
            "id": 1,
            "email": command.email,
            "nickname": command.nickname,
        }
    )
```

## 6. API Endpoint

```python
# users/api.py

from ninja import Router

from users.exceptions import DuplicateEmail
from users.result import Err, Ok
from users.schemas import CreateUserRequest, CreateUserResponse, ErrorResponse
from users.service import CreateUserCommand, create_user

router = Router()


@router.post(
    "/users",
    response={
        201: CreateUserResponse,
        409: ErrorResponse,
    },
)
def create_user_endpoint(request, payload: CreateUserRequest):
    result = create_user(
        CreateUserCommand(
            email=payload.email,
            nickname=payload.nickname,
        )
    )

    if isinstance(result, Ok):
        return 201, result.value

    if isinstance(result, Err) and isinstance(result.error, DuplicateEmail):
        return 409, {
            "code": result.error.code,
            "message": result.error.message,
        }

    return 500, {
        "code": "INTERNAL_ERROR",
        "message": "Unexpected error.",
    }
```

## TDD 흐름

1. 성공 테스트 작성
   `201`과 응답 body를 먼저 고정합니다.

2. validation 테스트 작성
   잘못된 email, 누락 필드, 빈 nickname, 길이 초과 같은 request schema 책임을 테스트합니다.

3. 도메인 실패 테스트 작성
   중복 email 같은 비즈니스 실패를 service mock으로 `Err(DuplicateEmail(...))` 반환하게 만듭니다.

4. endpoint 구현
   endpoint는 request schema를 command로 바꾸고, service의 `Result`를 HTTP 응답으로 매핑하는 정도만 담당합니다.

5. service 테스트는 별도로 작성
   ORM 조회, 중복 판단, 저장 성공 여부는 endpoint 테스트가 아니라 service/domain 테스트에서 검증하는 편이 좋습니다.

핵심은 endpoint 테스트에서 “Django Ninja가 schema validation을 해주는지”와 “도메인 결과가 HTTP status/body로 올바르게 변환되는지”를 분리해서 보는 것입니다.