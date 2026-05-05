**주요 내용**

읽기 전용 workspace라 파일 생성/pytest 실행은 하지 못했습니다. 아래는 실제 프로젝트에 옮겨 넣는 TDD 예시입니다. 예시는 `POST /reservations`가 재고를 예약하는 API이며, validation 실패, 성공, edge case, 도메인 예외, 명시적 `Result Type`을 포함합니다.

**RED: endpoint test 먼저**

```python
# tests/isolated/api/test_reservations_api.py
import pytest
from ninja.testing import TestClient

from apps.inventory.api import api


@pytest.fixture
def client() -> TestClient:
    return TestClient(api)


def test_create_reservation_invalid_quantity_returns_422(client: TestClient):
    # Arrange
    payload = {"product_id": 1, "quantity": 0}

    # Act
    response = client.post("/reservations", json=payload)

    # Assert
    assert response.status_code == 422


def test_create_reservation_unknown_product_returns_problem_detail(client: TestClient):
    # Arrange
    payload = {"product_id": 999, "quantity": 1}

    # Act
    response = client.post("/reservations", json=payload)

    # Assert
    assert response.status_code == 404
    assert response["content-type"] == "application/problem+json"
    assert response.json()["type"] == "https://api.example.com/problems/product-not-found"


def test_create_reservation_out_of_stock_returns_problem_detail(client: TestClient):
    # Arrange
    payload = {"product_id": 1, "quantity": 11}

    # Act
    response = client.post("/reservations", json=payload)

    # Assert
    assert response.status_code == 409
    assert response.json()["type"] == "https://api.example.com/problems/out-of-stock"


def test_create_reservation_success_returns_result(client: TestClient):
    # Arrange
    payload = {"product_id": 1, "quantity": 2}

    # Act
    response = client.post("/reservations", json=payload)

    # Assert
    assert response.status_code == 201
    assert response.json() == {
        "product_id": 1,
        "reserved_quantity": 2,
        "remaining_quantity": 8,
    }
```

**예상 실패 이유**

처음에는 `apps.inventory.api`, `ReservationIn`, `ReservationOut`, 도메인 예외, `reserve_stock()`이 없으므로 import 또는 404/409 처리에서 실패해야 합니다. 이 실패가 RED입니다.

**GREEN: 최소 구현**

```python
# apps/inventory/domain.py
from dataclasses import dataclass


class InventoryDomainError(Exception):
    pass


class ProductNotFound(InventoryDomainError):
    pass


class OutOfStock(InventoryDomainError):
    pass


@dataclass(frozen=True)
class ReserveStockResult:
    product_id: int
    reserved_quantity: int
    remaining_quantity: int


STOCKS: dict[int, int] = {1: 10}


def reserve_stock(product_id: int, quantity: int) -> ReserveStockResult:
    if product_id not in STOCKS:
        raise ProductNotFound

    current_quantity = STOCKS[product_id]
    if quantity > current_quantity:
        raise OutOfStock

    remaining_quantity = current_quantity - quantity
    STOCKS[product_id] = remaining_quantity

    return ReserveStockResult(
        product_id=product_id,
        reserved_quantity=quantity,
        remaining_quantity=remaining_quantity,
    )
```

```python
# apps/inventory/api.py
from django.http import HttpRequest, JsonResponse
from ninja import NinjaAPI, Router, Schema
from pydantic import Field

from apps.inventory.domain import OutOfStock, ProductNotFound, reserve_stock


class ReservationIn(Schema):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=100)


class ReservationOut(Schema):
    product_id: int
    reserved_quantity: int
    remaining_quantity: int


class ProblemDetail(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str


api = NinjaAPI()
router = Router()


@api.exception_handler(ProductNotFound)
def handle_product_not_found(request: HttpRequest, exc: ProductNotFound) -> JsonResponse:
    return JsonResponse(
        {
            "type": "https://api.example.com/problems/product-not-found",
            "title": "Product not found",
            "status": 404,
            "detail": "The requested product does not exist.",
            "instance": request.path,
        },
        status=404,
        content_type="application/problem+json",
    )


@api.exception_handler(OutOfStock)
def handle_out_of_stock(request: HttpRequest, exc: OutOfStock) -> JsonResponse:
    return JsonResponse(
        {
            "type": "https://api.example.com/problems/out-of-stock",
            "title": "Out of stock",
            "status": 409,
            "detail": "Requested quantity exceeds available stock.",
            "instance": request.path,
        },
        status=409,
        content_type="application/problem+json",
    )


@router.post("", response={201: ReservationOut})
def create_reservation(
    request: HttpRequest,
    payload: ReservationIn,
) -> tuple[int, ReservationOut]:
    result = reserve_stock(payload.product_id, payload.quantity)
    return 201, ReservationOut(
        product_id=result.product_id,
        reserved_quantity=result.reserved_quantity,
        remaining_quantity=result.remaining_quantity,
    )


api.add_router("/reservations", router)
```

**REFACTOR notes**

`STOCKS`는 GREEN용 fake입니다. 다음 단계에서 `InventoryRepository`를 도메인/애플리케이션 계층의 포트로 분리하고, Django ORM 구현체는 adapter로 둡니다. `reserve_stock()`은 transaction 경계 안에서 호출하고, 동시성은 `version` 필드나 조건부 `UPDATE`로 보호합니다. Validation 실패도 RFC 9457로 통일하려면 `ninja.errors.ValidationError` 핸들러를 추가해 422 Problem Detail로 변환합니다.

**실행 명령**

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/api/test_reservations_api.py -q
python manage.py check
```

---
> **관련 스킬 참조:**
> - Django Ninja endpoint 테스트 → **implementation-django-ninja** 스킬
> - pytest RED/GREEN/REFACTOR → **implementation-tdd** 스킬