## [주요 내용]

이 프로젝트는 DRF가 아니라 **Django Ninja**를 기준으로 API 표준을 잡는 것이 맞습니다. 표준은 단순합니다: **도메인 계층은 HTTP를 모르고, API 계층만 도메인 예외를 RFC 9457 Problem Details 응답으로 변환합니다.**

### 1. 계층별 책임

| 계층 | 책임 | 금지 |
|---|---|---|
| Domain | 비즈니스 규칙 위반을 도메인 예외로 표현 | `HttpError`, status code, request/response import |
| Application Service | 유스케이스 조율, 트랜잭션, Repository 호출 | HTTP 응답 생성, `JsonResponse` 반환 |
| API Router | 요청/응답 Schema 변환, 인증, 도메인 예외 매핑 | 비즈니스 규칙 직접 구현 |
| Infrastructure | ORM, 외부 API, Repository 구현 | 도메인 예외를 HTTP 예외로 바꾸기 |

핵심 규칙은 이것입니다.

```text
DomainError raise
    -> Application Service는 그대로 전파
        -> Django Ninja exception_handler가 ProblemDetail로 변환
```

### 2. 파일 구조 표준

```text
orders/
  domain/
    exceptions.py
    model/
      order/
        order.py
        value_objects.py
  application/
    services.py
    errors.py
  api/
    schemas.py
    errors.py
    router.py
config/
  api.py
```

`domain/exceptions.py`는 HTTP를 절대 import하지 않습니다.

```python
class DomainError(Exception):
    """비즈니스 규칙 위반을 표현하는 도메인 예외의 기준 클래스."""

    code = "domain_error"
    title = "Domain rule violated"

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class OrderAlreadyPaidError(DomainError):
    code = "order_already_paid"
    title = "Order already paid"


class OrderCannotBeCancelledError(DomainError):
    code = "order_cannot_be_cancelled"
    title = "Order cannot be cancelled"


class InsufficientStockError(DomainError):
    code = "insufficient_stock"
    title = "Insufficient stock"
```

도메인 모델은 예외만 던집니다.

```python
class Order:
    """Order Aggregate Root.

    Invariant:
    - paid 상태의 주문은 다시 결제될 수 없다.
    - shipped 상태의 주문은 취소될 수 없다.
    """

    def pay(self) -> None:
        if self.is_paid:
            raise OrderAlreadyPaidError("이미 결제된 주문입니다.")

        self.status = OrderStatus.PAID

    def cancel(self) -> None:
        if self.is_shipped:
            raise OrderCannotBeCancelledError("배송된 주문은 취소할 수 없습니다.")

        self.status = OrderStatus.CANCELLED
```

### 3. API 에러 응답 표준

모든 API 에러는 RFC 9457 Problem Details 형식으로 반환합니다.

```json
{
  "type": "https://api.example.com/problems/order-already-paid",
  "title": "Order already paid",
  "status": 409,
  "detail": "이미 결제된 주문입니다.",
  "instance": "/api/orders/ord_123/pay",
  "code": "order_already_paid"
}
```

Django Ninja Schema는 공통으로 둡니다.

```python
from ninja import Schema


class ProblemDetail(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    code: str
```

### 4. 도메인 예외와 HTTP 상태 매핑

도메인 예외 클래스 안에 HTTP status를 넣지 않습니다. 매핑은 API 계층에서만 합니다.

```python
from http import HTTPStatus

from orders.domain.exceptions import (
    DomainError,
    InsufficientStockError,
    OrderAlreadyPaidError,
    OrderCannotBeCancelledError,
)

DOMAIN_ERROR_STATUS: dict[type[DomainError], int] = {
    OrderAlreadyPaidError: HTTPStatus.CONFLICT,
    OrderCannotBeCancelledError: HTTPStatus.CONFLICT,
    InsufficientStockError: HTTPStatus.UNPROCESSABLE_ENTITY,
}
```

기준은 이렇게 잡습니다.

| 상황 | 상태 코드 |
|---|---:|
| 중복 생성, 이미 처리됨, 상태 충돌 | `409 Conflict` |
| 요청 문법은 맞지만 비즈니스 의미상 처리 불가 | `422 Unprocessable Entity` |
| 인증 필요 | `401 Unauthorized` |
| 권한 부족 | `403 Forbidden` |
| 리소스 없음 | `404 Not Found` |
| 낙관적 잠금 실패 | `409 Conflict` |
| Rate limit | `429 Too Many Requests` |

### 5. Django Ninja exception_handler 표준

`config/api.py` 또는 공통 API 모듈에서 등록합니다.

```python
from http import HTTPStatus

from django.http import HttpRequest, JsonResponse
from ninja import NinjaAPI
from ninja.errors import ValidationError

from orders.domain.exceptions import DomainError
from orders.api.errors import DOMAIN_ERROR_STATUS
from orders.api.schemas import ProblemDetail

api = NinjaAPI()


def problem_response(
    request: HttpRequest,
    *,
    type_: str,
    title: str,
    status: int,
    detail: str,
    code: str,
) -> JsonResponse:
    return JsonResponse(
        ProblemDetail(
            type=type_,
            title=title,
            status=status,
            detail=detail,
            instance=request.path,
            code=code,
        ).model_dump(),
        status=status,
        content_type="application/problem+json",
    )


@api.exception_handler(DomainError)
def handle_domain_error(request: HttpRequest, exc: DomainError) -> JsonResponse:
    status = DOMAIN_ERROR_STATUS.get(type(exc), HTTPStatus.UNPROCESSABLE_ENTITY)
    problem_type = f"https://api.example.com/problems/{exc.code.replace('_', '-')}"

    return problem_response(
        request,
        type_=problem_type,
        title=exc.title,
        status=status,
        detail=exc.detail,
        code=exc.code,
    )


@api.exception_handler(ValidationError)
def handle_validation_error(request: HttpRequest, exc: ValidationError) -> JsonResponse:
    return problem_response(
        request,
        type_="https://api.example.com/problems/validation-error",
        title="Validation error",
        status=HTTPStatus.UNPROCESSABLE_ENTITY,
        detail="요청 값이 유효하지 않습니다.",
        code="validation_error",
    )
```

### 6. Router 표준

엔드포인트는 HTTP 변환만 담당합니다. 비즈니스 판단은 서비스와 도메인에 둡니다.

```python
from http import HTTPStatus

from ninja import Router

from orders.api.schemas import OrderOut, PayOrderIn, ProblemDetail
from orders.application.services import OrderApplicationService

router = Router(tags=["orders"])


@router.post(
    "/{order_id}/payment",
    response={
        HTTPStatus.OK: OrderOut,
        HTTPStatus.CONFLICT: ProblemDetail,
        HTTPStatus.UNPROCESSABLE_ENTITY: ProblemDetail,
    },
)
def pay_order(request, order_id: str, payload: PayOrderIn) -> OrderOut:
    service = OrderApplicationService()
    order = service.pay_order(order_id=order_id, payment_key=payload.payment_key)
    return OrderOut.model_validate(order)
```

### 7. 클린 코드 기준

도메인 예외 연결 표준은 다음을 강제합니다.

| 기준 | 표준 |
|---|---|
| 의존성 방향 | `domain -> 없음`, `api -> domain`만 허용 |
| 예외 이름 | 유비쿼터스 언어 사용: `OrderCannotBeCancelledError` |
| 예외 메시지 | 사용자에게 보여도 되는 안전한 detail만 포함 |
| HTTP status | API 계층 매핑 테이블에서만 결정 |
| Error code | 클라이언트 분기용 안정 식별자, snake_case |
| Problem type | 문서화 가능한 안정 URI |
| 처리 위치 | `@api.exception_handler()`에 집중 |
| 일반 예외 | 도메인에서 `raise Exception`, `ValueError` 금지 |
| API 라우터 | `try/except DomainError` 반복 금지 |
| 테스트 | 도메인 테스트와 API 매핑 테스트를 분리 |

### 8. 테스트 기준

도메인 테스트는 HTTP를 몰라야 합니다.

```python
import pytest

from orders.domain.exceptions import OrderAlreadyPaidError


def test_paid_order_cannot_be_paid_again(order):
    order.pay()

    with pytest.raises(OrderAlreadyPaidError):
        order.pay()
```

API 테스트는 Problem Details 변환을 검증합니다.

```python
from http import HTTPStatus

from ninja.testing import TestClient

from config.api import api

client = TestClient(api)


def test_domain_error_is_returned_as_problem_detail():
    response = client.post("/orders/order_123/payment", json={"payment_key": "pay_1"})

    assert response.status_code == HTTPStatus.CONFLICT
    assert response["content-type"] == "application/problem+json"

    body = response.json()
    assert body["type"] == "https://api.example.com/problems/order-already-paid"
    assert body["title"] == "Order already paid"
    assert body["status"] == HTTPStatus.CONFLICT
    assert body["code"] == "order_already_paid"
    assert body["instance"] == "/orders/order_123/payment"
```

정리하면, 표준은 **도메인 예외는 비즈니스 언어로, API 응답은 Problem Details로, 매핑은 API 경계에서 한 번만**입니다. 이렇게 잡으면 도메인 모델이 HTTP에 오염되지 않고, 클라이언트는 일관된 에러 계약을 받을 수 있습니다.

---
> **관련 스킬 참조:**
> - API 에러 응답/RFC 9457 → **architecture-api** 스킬
> - Django Ninja exception_handler/Schema/Router → **implementation-django-ninja** 스킬
> - 도메인 예외/애그리거트 불변식 → **architecture-ddd** 스킬
> - 예외 설계와 클린 코드 경계 → **implementation-cleancode** 스킬