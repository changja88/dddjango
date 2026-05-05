사용 스킬: `dddjango:implementation-tdd` → `implementation-test` → `architecture-api` → `implementation-django-ninja`.

현재 워크스페이스가 read-only라서 파일 생성이나 `pytest` 실행은 하지 못했습니다. 아래는 실제 프로젝트에 옮겨 실행할 수 있는 RED 테스트, 예상 실패, GREEN 구현, REFACTOR 메모입니다. 에러 응답은 **Problem Details** 형식과 `application/problem+json`을 사용하고, 목록 성공 응답이 필요할 때는 `items`/`meta` envelope를 사용합니다.

가정: `POST /api/reservations` 엔드포인트가 상품 예약을 생성한다. 수량은 `1..10`, 같은 `Idempotency-Key`는 중복 요청으로 처리한다.

**RED 테스트**
`tests/isolated/integration/test_reservation_api.py`

```python
import pytest
from ninja.testing import TestClient

from reservations.api import router


@pytest.fixture
def client() -> TestClient:
    return TestClient(router)


def test_create_reservation_valid_payload_returns_created(client: TestClient) -> None:
    # Arrange
    payload = {"product_id": "P-001", "quantity": 2}

    # Act
    response = client.post(
        "/reservations",
        json=payload,
        headers={"Idempotency-Key": "req-001"},
    )

    # Assert
    assert response.status_code == 201
    assert response.json() == {
        "reservation_id": "res_req-001",
        "product_id": "P-001",
        "quantity": 2,
        "status": "reserved",
    }


@pytest.mark.parametrize(
    ("payload", "field"),
    [
        ({"product_id": "", "quantity": 1}, "product_id"),
        ({"product_id": "P-001", "quantity": 0}, "quantity"),
        ({"product_id": "P-001", "quantity": 11}, "quantity"),
    ],
)
def test_create_reservation_invalid_payload_returns_problem_details(
    client: TestClient,
    payload: dict[str, object],
    field: str,
) -> None:
    # Arrange

    # Act
    response = client.post(
        "/reservations",
        json=payload,
        headers={"Idempotency-Key": "req-invalid"},
    )

    # Assert
    assert response.status_code == 422
    assert response["Content-Type"].startswith("application/problem+json")
    body = response.json()
    assert body["type"] == "https://api.example.com/problems/validation-error"
    assert body["title"] == "Validation error"
    assert body["status"] == 422
    assert field in body["detail"]


def test_create_reservation_missing_idempotency_key_returns_problem_details(
    client: TestClient,
) -> None:
    # Arrange
    payload = {"product_id": "P-001", "quantity": 1}

    # Act
    response = client.post("/reservations", json=payload)

    # Assert
    assert response.status_code == 400
    assert response["Content-Type"].startswith("application/problem+json")
    assert response.json() == {
        "type": "https://api.example.com/problems/missing-idempotency-key",
        "title": "Missing Idempotency-Key",
        "status": 400,
        "detail": "Idempotency-Key header is required.",
    }


def test_create_reservation_out_of_stock_domain_exception_returns_conflict(
    client: TestClient,
) -> None:
    # Arrange
    payload = {"product_id": "SOLD-OUT", "quantity": 1}

    # Act
    response = client.post(
        "/reservations",
        json=payload,
        headers={"Idempotency-Key": "req-sold-out"},
    )

    # Assert
    assert response.status_code == 409
    assert response["Content-Type"].startswith("application/problem+json")
    assert response.json() == {
        "type": "https://api.example.com/problems/out-of-stock",
        "title": "Out of stock",
        "status": 409,
        "detail": "Product SOLD-OUT does not have enough stock.",
    }


def test_create_reservation_duplicate_idempotency_key_returns_same_success(
    client: TestClient,
) -> None:
    # Arrange
    payload = {"product_id": "P-001", "quantity": 1}
    headers = {"Idempotency-Key": "req-duplicate"}

    # Act
    first_response = client.post("/reservations", json=payload, headers=headers)
    second_response = client.post("/reservations", json=payload, headers=headers)

    # Assert
    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert second_response.json() == first_response.json()
```

**예상 실패 이유**

처음에는 `reservations.api`, `ReservationCreateIn`, 도메인 예외, `CreateReservationResult`, 서비스 함수, validation exception handler가 없어서 import error 또는 404/500으로 실패해야 합니다. 특히 validation 실패는 Django Ninja 기본 응답이 Problem Details가 아니므로 커스텀 handler를 추가하기 전에는 `Content-Type`과 body shape assertion이 실패합니다.

**GREEN 최소 구현**
`reservations/domain.py`

```python
from dataclasses import dataclass


class ReservationDomainError(Exception):
    pass


class OutOfStock(ReservationDomainError):
    def __init__(self, product_id: str) -> None:
        self.product_id = product_id
        super().__init__(f"Product {product_id} does not have enough stock.")


@dataclass(frozen=True)
class CreateReservationResult:
    reservation_id: str
    product_id: str
    quantity: int
    status: str
```

`reservations/services.py`

```python
from reservations.domain import CreateReservationResult, OutOfStock

_RESERVATIONS_BY_KEY: dict[str, CreateReservationResult] = {}


def create_reservation(
    *,
    product_id: str,
    quantity: int,
    idempotency_key: str,
) -> CreateReservationResult:
    existing = _RESERVATIONS_BY_KEY.get(idempotency_key)
    if existing is not None:
        return existing

    if product_id == "SOLD-OUT":
        raise OutOfStock(product_id)

    result = CreateReservationResult(
        reservation_id=f"res_{idempotency_key}",
        product_id=product_id,
        quantity=quantity,
        status="reserved",
    )
    _RESERVATIONS_BY_KEY[idempotency_key] = result
    return result
```

`reservations/api.py`

```python
from django.http import HttpRequest, HttpResponse
from ninja import Router, Schema
from ninja.errors import ValidationError
from pydantic import Field

from reservations.domain import OutOfStock
from reservations.services import create_reservation

router = Router()


class ProblemDetail(Schema):
    type: str
    title: str
    status: int
    detail: str


class ReservationCreateIn(Schema):
    product_id: str = Field(min_length=1)
    quantity: int = Field(ge=1, le=10)


class ReservationOut(Schema):
    reservation_id: str
    product_id: str
    quantity: int
    status: str


def problem_response(
    request: HttpRequest,
    *,
    status: int,
    type_: str,
    title: str,
    detail: str,
) -> HttpResponse:
    response = router.api.create_response(
        request,
        {"type": type_, "title": title, "status": status, "detail": detail},
        status=status,
    )
    response["Content-Type"] = "application/problem+json"
    return response


@router.api.exception_handler(ValidationError)
def validation_error_handler(request: HttpRequest, exc: ValidationError) -> HttpResponse:
    return problem_response(
        request,
        status=422,
        type_="https://api.example.com/problems/validation-error",
        title="Validation error",
        detail=str(exc),
    )


@router.api.exception_handler(OutOfStock)
def out_of_stock_handler(request: HttpRequest, exc: OutOfStock) -> HttpResponse:
    return problem_response(
        request,
        status=409,
        type_="https://api.example.com/problems/out-of-stock",
        title="Out of stock",
        detail=str(exc),
    )


@router.post(
    "/reservations",
    response={201: ReservationOut, 400: ProblemDetail, 409: ProblemDetail, 422: ProblemDetail},
)
def create_reservation_endpoint(
    request: HttpRequest,
    payload: ReservationCreateIn,
) -> tuple[int, ReservationOut] | HttpResponse:
    idempotency_key = request.headers.get("Idempotency-Key")
    if not idempotency_key:
        return problem_response(
            request,
            status=400,
            type_="https://api.example.com/problems/missing-idempotency-key",
            title="Missing Idempotency-Key",
            detail="Idempotency-Key header is required.",
        )

    result = create_reservation(
        product_id=payload.product_id,
        quantity=payload.quantity,
        idempotency_key=idempotency_key,
    )
    return 201, ReservationOut(
        reservation_id=result.reservation_id,
        product_id=result.product_id,
        quantity=result.quantity,
        status=result.status,
    )
```

API 합성 예시는 이렇게 둡니다.

`config/api.py`

```python
from ninja import NinjaAPI

from reservations.api import router as reservations_router

api = NinjaAPI()
api.add_router("", reservations_router)
```

`config/urls.py`

```python
from django.urls import path

from config.api import api

urlpatterns = [
    path("api/", api.urls),
]
```

목록 응답이 있는 엔드포인트라면 성공 응답은 Problem Details가 아니라 `items`/`meta` envelope를 씁니다.

```python
class ReservationListOut(Schema):
    items: list[ReservationOut]
    meta: dict[str, int]
```

예시 shape:

```json
{
  "items": [],
  "meta": {"limit": 20, "offset": 0, "total": 0}
}
```

**REFACTOR 방향**

지금 GREEN 구현의 `_RESERVATIONS_BY_KEY`는 테스트를 통과시키는 최소 fake입니다. 실제 프로젝트에서는 `ReservationRepository` 경계를 만들고, isolated 테스트에서는 `InMemoryReservationRepository`, 운영에서는 Django ORM repository로 교체합니다.

`OutOfStock` 같은 도메인 예외는 API 상태 코드와 분리해서 도메인 계층에 둡니다. API 계층은 예외를 Problem Details로 번역만 합니다.

멱등성 처리는 DB unique constraint와 transaction으로 보호해야 합니다. 실패 응답을 저장해야 하는 요구가 있다면 `transaction.atomic()` 안에서 실패 상태를 저장한 뒤 예외를 다시 raise하지 말고, 명시적 Result Type으로 반환해 rollback으로 기록이 사라지지 않게 합니다.

테스트 디렉터리는 `tests/isolated/integration/`에 API 테스트를 두고, 운영 인프라를 쓰는 테스트는 `tests/real/integration/`로 분리합니다. `tests/isolated/`는 `config.settings.test`에서 locmem cache, locmem email, in-memory DB 또는 testcontainers DB, eager celery를 쓰도록 분리하는 편이 안전합니다.

**pytest 명령**

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/integration/test_reservation_api.py -q
python manage.py check
```

시간 의존 테스트가 추가되면 `time-machine`을 기본으로 쓰세요. `freezegun`은 순수 Python 구현인 반면 `time-machine`은 C 확장으로 구현되어 있어 동일 작업에서 100~200배 빠릅니다. 시간 모킹이 많은 테스트 스위트에서는 실행 시간 차이가 실제로 커집니다.

---
> **관련 스킬 참조:**
> - Django Ninja API 구현 → **implementation-django-ninja** 스킬
> - pytest 테스트 구조와 fixture → **implementation-test** 스킬
> - Red-Green-Refactor 진행 → **implementation-tdd** 스킬
> - REST 상태 코드와 Problem Details → **architecture-api** 스킬