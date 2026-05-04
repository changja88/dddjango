읽기 전용 세션이고 `/private/tmp/dddjango-codex-eval`은 비어 있어서 파일 생성은 못 했습니다. 아래 내용을 `docs/testing/django-ninja-pytest-standard.md` 같은 문서로 두면 됩니다.

**Django Ninja Endpoint Pytest 표준**

1. 테스트 위치

```text
tests/
  conftest.py
  isolated/
    conftest.py
    integration/
      test_<app>_api.py
  real/
    integration/
      test_<external_flow>.py
```

- 기본 API endpoint 테스트는 `tests/isolated/integration/`에 둔다.
- `tests/isolated/`는 `DJANGO_SETTINGS_MODULE=config.settings.test`로 실행한다.
- 실 DB, 실 외부 API, stage 환경 검증은 `tests/real/`에만 둔다.
- 평면 `tests/unit`, `tests/integration` 구조는 사용하지 않는다.

2. pytest 설정

```toml
[tool.pytest.ini_options]
minversion = "8.0"
DJANGO_SETTINGS_MODULE = "config.settings.test"
testpaths = ["tests/isolated", "tests/real"]
addopts = [
    "-ra",
    "-q",
    "--strict-markers",
    "--strict-config",
    "--tb=short",
]
python_files = ["test_*.py", "*_test.py"]
python_functions = ["test_*"]
markers = [
    "isolated: 통제된 테스트 환경",
    "real: 실제 운영 또는 stage 환경",
    "integration: 통합 테스트",
    "e2e: 엔드투엔드 테스트",
    "slow: 느린 테스트",
]
xfail_strict = true
filterwarnings = ["error"]
```

3. 공통 fixture

```python
# tests/isolated/integration/conftest.py
import pytest
from ninja.testing import TestClient

from orders.api import router as orders_router


@pytest.fixture
def api_client():
    return TestClient(orders_router)


@pytest.fixture
def authenticated_user(db):
    from tests.factories import UserFactory

    return UserFactory()
```

4. endpoint 테스트 기본 형식

```python
import pytest

from orders.models import Order
from tests.factories import OrderFactory


@pytest.mark.django_db
def test_get_order_existing_order_returns_order_detail(api_client, authenticated_user):
    # Arrange
    order = OrderFactory(user=authenticated_user)

    # Act
    response = api_client.get(f"/{order.id}", user=authenticated_user)

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "id": order.id,
        "status": order.status,
        "total_price": str(order.total_price),
    }
```

표준 규칙:

- 테스트명은 `test_<대상>_<조건>_<기대결과>` 형식으로 쓴다.
- 하나의 테스트에는 하나의 Act만 둔다.
- Arrange, Act, Assert 주석을 유지한다.
- DB 접근이 있으면 `@pytest.mark.django_db`를 명시한다.
- 요청/응답은 실제 HTTP 의미를 검증한다: status code, response body, DB state.
- 구현 세부사항 함수 호출 여부보다 사용자 관찰 가능한 결과를 우선 검증한다.

5. 인증 테스트

```python
@pytest.mark.django_db
def test_get_my_profile_authenticated_user_returns_profile(api_client, authenticated_user):
    response = api_client.get("/me", user=authenticated_user)

    assert response.status_code == 200
    assert response.json()["id"] == authenticated_user.id


@pytest.mark.django_db
def test_get_my_profile_anonymous_user_returns_401(api_client):
    response = api_client.get("/me")

    assert response.status_code == 401
```

6. 생성 endpoint 테스트

```python
@pytest.mark.django_db
def test_create_order_valid_payload_creates_order(api_client, authenticated_user):
    payload = {
        "product_id": 1,
        "quantity": 2,
    }

    response = api_client.post("/orders", json=payload, user=authenticated_user)

    assert response.status_code == 201
    assert Order.objects.count() == 1
    assert response.json()["quantity"] == 2
```

7. validation/error 테스트

```python
@pytest.mark.django_db
def test_create_order_missing_product_id_returns_422(api_client, authenticated_user):
    response = api_client.post(
        "/orders",
        json={"quantity": 2},
        user=authenticated_user,
    )

    assert response.status_code == 422
    assert "detail" in response.json()
```

8. 목록 endpoint 테스트

```python
@pytest.mark.django_db
def test_list_orders_authenticated_user_returns_only_own_orders(api_client, authenticated_user):
    own_order = OrderFactory(user=authenticated_user)
    OrderFactory()

    response = api_client.get("/orders", user=authenticated_user)

    assert response.status_code == 200
    assert response.json()["items"] == [
        {
            "id": own_order.id,
            "status": own_order.status,
        }
    ]
```

목록 endpoint 표준:

- 페이지네이션 응답 구조를 검증한다.
- 다른 사용자의 데이터가 섞이지 않는지 검증한다.
- 정렬 기준이 API 계약이면 순서까지 검증한다.
- N+1 위험이 있는 목록은 쿼리 수 테스트를 추가한다.

9. 쿼리 수 회귀 테스트

```python
@pytest.mark.django_db
def test_list_orders_multiple_orders_uses_constant_queries(
    api_client,
    authenticated_user,
    django_assert_num_queries,
):
    OrderFactory.create_batch(5, user=authenticated_user)

    with django_assert_num_queries(3):
        response = api_client.get("/orders", user=authenticated_user)

    assert response.status_code == 200
```

10. 외부 의존성 표준

- 핵심 도메인 로직은 mock하지 않는다.
- 결제, 이메일, HTTP API 같은 외부 의존성만 mock 또는 fake로 대체한다.
- HTTP 호출은 `responses` 또는 `respx`를 사용한다.
- 시간 의존 테스트는 `time-machine`으로 고정한다.
- raw `MagicMock` 남발 대신 `create_autospec` 또는 InMemory Fake를 사용한다.

실행 명령:

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated -q
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/integration/test_orders_api.py -q
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated -m "not slow" -q
```

---
> **관련 스킬 참조:**
> - Django Ninja endpoint 구현/리뷰 → **implementation-django-ninja** 스킬
> - pytest fixture와 테스트 품질 → **implementation-test** 스킬
> - Red-Green-Refactor 방식 적용 → **implementation-tdd** 스킬