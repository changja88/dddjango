# TestClient와 API 검증

Django Ninja `TestClient` API test acceptance criteria와 verification reporting을 다룰 때 이 reference를 읽는다. 상세 pytest fixture와 test-double mechanics는 `implementation-test`, TDD workflow는 `implementation-tdd`가 맡는다.

## 테스트할 항목

- valid/invalid payload의 request schema validation
- list/detail/create/update/delete operation의 response schema field와 type
- success, validation error, auth error, conflict, rate limit, async acceptance의 status code와 header
- error의 Problem Details shape
- `401`과 `403`을 포함한 authentication/authorization behavior
- maximum page size와 stable ordering을 포함한 pagination/filtering behavior
- risky POST endpoint의 idempotency replay, conflict behavior, concurrent duplicate request handling
- DRF-to-Ninja compatibility: URL, method, field, status, auth, pagination, error, OpenAPI difference
- endpoint shape 변경이 client에 중요할 때 OpenAPI generation 또는 schema diff artifact

Django Ninja `TestClient` 사용 예:

```python
from ninja.testing import TestClient

client = TestClient(orders_router)


def test_create_order_returns_created():
    response = client.post("/", json={"sku": "A-1", "quantity": 1})

    assert response.status_code == 201
    assert response.json()["status"] == "pending"
```

## Test 경계

- business rule은 가능한 domain/service layer에서 테스트한다.
- API test는 HTTP contract, auth/permission wiring, serialization, error mapping, compatibility에 사용한다.
- 더 빠른 domain/service test가 rule을 더 명확히 표현할 수 있는데 domain behavior를 API test 안에만 숨기지 않는다.
- model, transaction, migration behavior test는 `implementation-django`와 맞춘다.

## Verification reporting

- focused pytest path, TestClient test run, OpenAPI generation command, schema comparison command처럼 실제 실행한 command를 정확히 보고한다.
- test를 실행하지 않았으면 `Not run`과 이유를 말한다.
- command output 또는 검토한 artifact 없이 endpoint, schema, OpenAPI, compatibility check가 통과했다고 주장하지 않는다.
- Skill/reference loading command는 implementation verification이 아니므로 user-facing check로 보고하지 않는다.
