**표준안**

원칙은 하나입니다: **도메인 예외는 HTTP를 모른다. API 어댑터만 HTTP 응답을 만든다.**  
도메인 계층은 “무슨 비즈니스 규칙이 깨졌는가”만 표현하고, Django Ninja 계층은 이를 `RFC 9457 Problem Details`로 변환합니다.

권장 구조:

```text
orders/
  domain/
    exceptions.py
  application/
    services.py
  api/
    router.py
config/
  api.py
  api_errors.py
```

**1. Domain Exception**

```python
# orders/domain/exceptions.py

class DomainError(Exception):
    code = "domain_error"
    message = "Domain rule was violated."

    def __init__(self, message: str | None = None, **params: object) -> None:
        self.detail = message or self.message
        self.params = params
        super().__init__(self.detail)


class OrderAlreadyPaid(DomainError):
    code = "order_already_paid"
    message = "이미 결제된 주문입니다."


class OrderNotCancelable(DomainError):
    code = "order_not_cancelable"
    message = "취소할 수 없는 주문 상태입니다."
```

금지 사항:

```python
# domain 계층에서 금지
raise HttpError(409, "...")
return {"error": "..."}
return None  # 실패 의미로 사용 금지
```

**2. Application Service**

```python
# orders/application/services.py

from orders.domain.exceptions import OrderAlreadyPaid

class PayOrderService:
    def pay(self, order_id: str) -> None:
        order = self._orders.get(order_id)

        if order.is_paid:
            raise OrderAlreadyPaid(order_id=order_id)

        order.pay()
        self._orders.save(order)
```

응용 서비스도 HTTP 상태 코드, `request`, `JsonResponse`, Ninja `Schema`를 알면 안 됩니다.

**3. Problem Details Schema + Mapper**

```python
# config/api_errors.py

from dataclasses import dataclass
from typing import Mapping

from django.http import JsonResponse
from ninja import Schema
from ninja.errors import ValidationError

from orders.domain.exceptions import (
    DomainError,
    OrderAlreadyPaid,
    OrderNotCancelable,
)


class ProblemDetail(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    code: str | None = None


@dataclass(frozen=True)
class ErrorSpec:
    status: int
    type: str
    title: str


DOMAIN_ERROR_MAP: Mapping[type[DomainError], ErrorSpec] = {
    OrderAlreadyPaid: ErrorSpec(
        status=409,
        type="https://api.example.com/problems/order-already-paid",
        title="Order already paid",
    ),
    OrderNotCancelable: ErrorSpec(
        status=422,
        type="https://api.example.com/problems/order-not-cancelable",
        title="Order not cancelable",
    ),
}


def register_exception_handlers(api) -> None:
    @api.exception_handler(DomainError)
    def handle_domain_error(request, exc: DomainError):
        spec = DOMAIN_ERROR_MAP.get(
            type(exc),
            ErrorSpec(
                status=422,
                type="https://api.example.com/problems/domain-rule-violation",
                title="Domain rule violation",
            ),
        )

        body = ProblemDetail(
            type=spec.type,
            title=spec.title,
            status=spec.status,
            detail=exc.detail,
            instance=request.path,
            code=exc.code,
        )

        return JsonResponse(
            body.model_dump(),
            status=spec.status,
            content_type="application/problem+json",
        )

    @api.exception_handler(ValidationError)
    def handle_validation_error(request, exc: ValidationError):
        body = ProblemDetail(
            type="https://api.example.com/problems/request-validation-failed",
            title="Request validation failed",
            status=422,
            detail="요청 값이 올바르지 않습니다.",
            instance=request.path,
            code="request_validation_failed",
        )
        return JsonResponse(
            body.model_dump(),
            status=422,
            content_type="application/problem+json",
        )
```

**4. Ninja API Composition**

```python
# config/api.py

from ninja import NinjaAPI

from config.api_errors import register_exception_handlers
from orders.api.router import router as orders_router

api = NinjaAPI(title="Service API")

register_exception_handlers(api)

api.add_router("/orders", orders_router)
```

**5. Router는 성공 흐름만 담당**

```python
# orders/api/router.py

from ninja import Router

router = Router(tags=["orders"])


@router.post("/{order_id}/payment", response={204: None})
def pay_order(request, order_id: str):
    service = build_pay_order_service()
    service.pay(order_id)
    return 204, None
```

**팀 규칙**

도메인 예외에는 `status`, `response`, `request`, `JsonResponse`, `HttpError`를 넣지 않습니다.  
API 에러 포맷은 `ProblemDetail` 하나로 통일합니다.  
도메인 예외와 HTTP 상태 코드의 연결은 `DOMAIN_ERROR_MAP` 하나만 단일 출처로 둡니다.  
알 수 없는 `DomainError`는 기본적으로 `422`로 처리하고, 중복/동시성/상태 충돌은 명시적으로 `409`에 매핑합니다.  
인증은 `401`, 인가는 `403`, 리소스 없음은 `404`, 요청 스키마 오류는 `422`로 분리합니다.

**검증 절차**

```bash
python manage.py test
python manage.py test orders
python manage.py check
```

API 테스트에서는 최소한 다음을 확인합니다.

```python
def test_domain_error_returns_problem_detail(client):
    response = client.post("/api/orders/ord_1/payment")

    assert response.status_code == 409
    assert response["content-type"] == "application/problem+json"
    assert response.json()["code"] == "order_already_paid"
```

---
> **관련 스킬 참조:**
> - Django Ninja API 에러 처리 → **implementation-django-ninja** 스킬
> - REST Problem Details 표준 → **architecture-api** 스킬
> - 도메인 예외와 계층 분리 → **architecture-ddd**, **implementation-cleancode** 스킬