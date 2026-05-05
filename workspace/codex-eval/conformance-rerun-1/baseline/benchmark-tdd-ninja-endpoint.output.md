아래는 “쿠폰 적용” Django Ninja endpoint를 pytest로 TDD하는 예시입니다. 핵심은 endpoint가 도메인 예외를 직접 던지지 않고, 도메인 서비스가 `Result`를 반환하게 만든 뒤 API layer에서 HTTP 응답으로 변환하는 구조입니다.

```python
# app/result.py
from dataclasses import dataclass
from typing import Generic, TypeVar, Literal

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T


@dataclass(frozen=True)
class Err(Generic[E]):
    error: E


Result = Ok[T] | Err[E]
```

```python
# app/domain.py
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class CouponError(StrEnum):
    NOT_FOUND = "coupon_not_found"
    EXPIRED = "coupon_expired"
    MIN_AMOUNT_NOT_MET = "min_amount_not_met"
    ALREADY_USED = "coupon_already_used"


@dataclass(frozen=True)
class ApplyCouponCommand:
    user_id: int
    coupon_code: str
    order_amount: Decimal


@dataclass(frozen=True)
class AppliedCoupon:
    coupon_code: str
    discount_amount: Decimal
    final_amount: Decimal
```

```python
# app/services.py
from decimal import Decimal
from app.domain import ApplyCouponCommand, AppliedCoupon, CouponError
from app.result import Ok, Err, Result


def apply_coupon(command: ApplyCouponCommand) -> Result[AppliedCoupon, CouponError]:
    code = command.coupon_code.strip().upper()

    if code == "MISSING":
        return Err(CouponError.NOT_FOUND)

    if code == "EXPIRED":
        return Err(CouponError.EXPIRED)

    if code == "USED":
        return Err(CouponError.ALREADY_USED)

    if command.order_amount < Decimal("10000"):
        return Err(CouponError.MIN_AMOUNT_NOT_MET)

    discount = Decimal("1000")

    return Ok(
        AppliedCoupon(
            coupon_code=code,
            discount_amount=discount,
            final_amount=command.order_amount - discount,
        )
    )
```

```python
# app/api.py
from decimal import Decimal
from ninja import NinjaAPI, Schema
from pydantic import Field

from app.domain import ApplyCouponCommand, CouponError
from app.result import Ok, Err
from app.services import apply_coupon

api = NinjaAPI()


class ApplyCouponIn(Schema):
    user_id: int = Field(gt=0)
    coupon_code: str = Field(min_length=1, max_length=30)
    order_amount: Decimal = Field(gt=0)


class ApplyCouponOut(Schema):
    coupon_code: str
    discount_amount: Decimal
    final_amount: Decimal


class ErrorOut(Schema):
    code: str
    message: str


ERROR_MESSAGES = {
    CouponError.NOT_FOUND: "Coupon does not exist.",
    CouponError.EXPIRED: "Coupon has expired.",
    CouponError.MIN_AMOUNT_NOT_MET: "Order amount does not meet coupon minimum.",
    CouponError.ALREADY_USED: "Coupon has already been used.",
}


@api.post(
    "/coupons/apply",
    response={
        200: ApplyCouponOut,
        400: ErrorOut,
        404: ErrorOut,
        409: ErrorOut,
    },
)
def apply_coupon_endpoint(request, payload: ApplyCouponIn):
    result = apply_coupon(
        ApplyCouponCommand(
            user_id=payload.user_id,
            coupon_code=payload.coupon_code,
            order_amount=payload.order_amount,
        )
    )

    if isinstance(result, Ok):
        return 200, result.value

    error = result.error

    if error == CouponError.NOT_FOUND:
        return 404, ErrorOut(code=error, message=ERROR_MESSAGES[error])

    if error == CouponError.ALREADY_USED:
        return 409, ErrorOut(code=error, message=ERROR_MESSAGES[error])

    return 400, ErrorOut(code=error, message=ERROR_MESSAGES[error])
```

테스트는 endpoint의 계약을 먼저 고정합니다.

```python
# tests/test_apply_coupon_api.py
import pytest
from ninja.testing import TestClient

from app.api import api

client = TestClient(api)


def test_apply_coupon_success():
    response = client.post(
        "/coupons/apply",
        json={
            "user_id": 1,
            "coupon_code": "WELCOME",
            "order_amount": "12000",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "coupon_code": "WELCOME",
        "discount_amount": "1000",
        "final_amount": "11000",
    }


@pytest.mark.parametrize(
    "payload, field",
    [
        (
            {
                "user_id": 0,
                "coupon_code": "WELCOME",
                "order_amount": "12000",
            },
            "user_id",
        ),
        (
            {
                "user_id": 1,
                "coupon_code": "",
                "order_amount": "12000",
            },
            "coupon_code",
        ),
        (
            {
                "user_id": 1,
                "coupon_code": "WELCOME",
                "order_amount": "0",
            },
            "order_amount",
        ),
    ],
)
def test_apply_coupon_request_schema_validation(payload, field):
    response = client.post("/coupons/apply", json=payload)

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(field in str(error["loc"]) for error in errors)


def test_apply_coupon_not_found_failure_response():
    response = client.post(
        "/coupons/apply",
        json={
            "user_id": 1,
            "coupon_code": "MISSING",
            "order_amount": "12000",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": "coupon_not_found",
        "message": "Coupon does not exist.",
    }


def test_apply_coupon_expired_failure_response():
    response = client.post(
        "/coupons/apply",
        json={
            "user_id": 1,
            "coupon_code": "EXPIRED",
            "order_amount": "12000",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": "coupon_expired",
        "message": "Coupon has expired.",
    }


def test_apply_coupon_already_used_domain_exception_case():
    response = client.post(
        "/coupons/apply",
        json={
            "user_id": 1,
            "coupon_code": "USED",
            "order_amount": "12000",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "code": "coupon_already_used",
        "message": "Coupon has already been used.",
    }


def test_apply_coupon_min_amount_edge_case():
    response = client.post(
        "/coupons/apply",
        json={
            "user_id": 1,
            "coupon_code": "WELCOME",
            "order_amount": "9999",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": "min_amount_not_met",
        "message": "Order amount does not meet coupon minimum.",
    }


def test_apply_coupon_normalizes_coupon_code_edge_case():
    response = client.post(
        "/coupons/apply",
        json={
            "user_id": 1,
            "coupon_code": " welcome ",
            "order_amount": "12000",
        },
    )

    assert response.status_code == 200
    assert response.json()["coupon_code"] == "WELCOME"
```

TDD 흐름은 보통 이렇게 갑니다.

1. `test_apply_coupon_success`를 먼저 작성한다.
2. endpoint, schema, service의 최소 구현으로 통과시킨다.
3. validation 테스트를 추가하고 `Field(gt=0)`, `min_length` 같은 schema 제약을 넣는다.
4. 도메인 실패 케이스를 하나씩 추가한다.
5. service가 exception 대신 `Ok` / `Err`를 반환하게 하여 endpoint의 분기와 응답 계약을 명확히 만든다.

이 구조의 장점은 도메인 로직 테스트와 API contract 테스트를 분리하기 쉽다는 점입니다. endpoint 테스트는 “HTTP 요청이 어떤 상태 코드와 body로 변환되는가”를 검증하고, service 테스트는 별도로 `Result` 반환 규칙만 검증하면 됩니다.