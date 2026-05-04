**표준안**

원칙은 하나입니다: **domain exception은 HTTP를 몰라야 하고, Django Ninja API 경계에서만 RFC 9457 Problem Details로 번역한다.**

권장 구조:

```text
apps/orders/domain/exceptions.py      # 순수 도메인 예외
apps/orders/application/services.py   # use case 조율
config/api/errors.py                  # domain -> API error 변환
config/api.py                         # NinjaAPI + exception_handler 등록
```

**1. Domain Exception 표준**

도메인 예외에는 `status_code`, `response`, `HttpError` 같은 API 개념을 넣지 않습니다.

```python
# apps/orders/domain/exceptions.py
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DomainError(Exception):
    code: str
    message: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OrderAlreadyPaidError(DomainError):
    def __init__(self, order_id: str):
        super().__init__(
            code="order_already_paid",
            message="Order is already paid.",
            context={"order_id": order_id},
        )


@dataclass(frozen=True)
class OrderNotFoundError(DomainError):
    def __init__(self, order_id: str):
        super().__init__(
            code="order_not_found",
            message="Order was not found.",
            context={"order_id": order_id},
        )
```

도메인 계층에서는 이렇게만 사용합니다.

```python
if order.is_paid:
    raise OrderAlreadyPaidError(order_id=order.id)
```

**2. API Problem Details 표준**

모든 API 에러 응답은 이 형식을 사용합니다.

```json
{
  "type": "https://api.example.com/problems/order-already-paid",
  "title": "Order Already Paid",
  "status": 409,
  "detail": "Order is already paid.",
  "instance": "/api/orders/ord_123/payments",
  "code": "order_already_paid"
}
```

필수 필드:

```text
type      문제 유형의 안정적인 URI
title     문제 유형의 짧은 이름
status    HTTP status code
detail    이번 발생에 대한 설명
instance  요청 path
code      클라이언트 분기용 안정적인 에러 코드
```

`context`는 필요한 경우 확장 필드로 노출하되, 개인정보/내부 상태/스택 정보는 제외합니다.

**3. Domain -> HTTP 매핑 표준**

```python
# config/api/errors.py
from dataclasses import dataclass
from typing import Any

from django.http import JsonResponse
from ninja import Schema
from ninja.errors import ValidationError

from apps.orders.domain.exceptions import DomainError


class ProblemDetail(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    code: str | None = None


@dataclass(frozen=True)
class ErrorMapping:
    status: int
    title: str
    type: str


DOMAIN_ERROR_MAPPINGS: dict[str, ErrorMapping] = {
    "order_not_found": ErrorMapping(
        status=404,
        title="Order Not Found",
        type="https://api.example.com/problems/order-not-found",
    ),
    "order_already_paid": ErrorMapping(
        status=409,
        title="Order Already Paid",
        type="https://api.example.com/problems/order-already-paid",
    ),
}


def problem_response(
    *,
    request,
    status: int,
    title: str,
    detail: str,
    type_: str = "about:blank",
    code: str | None = None,
    extra: dict[str, Any] | None = None,
) -> JsonResponse:
    body = {
        "type": type_,
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.path,
    }

    if code:
        body["code"] = code

    if extra:
        body.update(extra)

    return JsonResponse(
        body,
        status=status,
        content_type="application/problem+json",
    )


def handle_domain_error(request, exc: DomainError) -> JsonResponse:
    mapping = DOMAIN_ERROR_MAPPINGS.get(
        exc.code,
        ErrorMapping(
            status=422,
            title="Domain Rule Violation",
            type="https://api.example.com/problems/domain-rule-violation",
        ),
    )

    return problem_response(
        request=request,
        status=mapping.status,
        title=mapping.title,
        detail=exc.message,
        type_=mapping.type,
        code=exc.code,
        extra=exc.context,
    )


def handle_validation_error(request, exc: ValidationError) -> JsonResponse:
    return problem_response(
        request=request,
        status=422,
        title="Validation Failed",
        detail="Request validation failed.",
        type_="https://api.example.com/problems/validation-failed",
        code="validation_failed",
        extra={"errors": exc.errors},
    )
```

**4. Django Ninja 등록 표준**

```python
# config/api.py
from ninja import NinjaAPI
from ninja.errors import ValidationError

from apps.orders.domain.exceptions import DomainError
from config.api.errors import handle_domain_error, handle_validation_error

api = NinjaAPI()

api.add_exception_handler(DomainError, handle_domain_error)
api.add_exception_handler(ValidationError, handle_validation_error)
```

데코레이터를 써도 됩니다.

```python
@api.exception_handler(DomainError)
def domain_error_handler(request, exc):
    return handle_domain_error(request, exc)
```

**5. 상태 코드 기준**

```text
400  요청 형식 자체가 잘못됨
401  인증 필요
403  인증은 됐지만 권한 없음
404  조회 대상 리소스 없음
409  현재 리소스 상태와 충돌함
422  문법은 맞지만 도메인 규칙상 처리 불가
429  Rate limit 초과
500  예상하지 못한 서버 오류
```

도메인 예외 매핑 기준:

```text
NotFound 계열             -> 404
AlreadyExists / Duplicate -> 409
InvalidStateTransition    -> 409
BusinessRuleViolation     -> 422
Permission domain rule    -> 403
외부 의존성 일시 실패       -> 503, 단 domain exception보다는 application/infrastructure exception 권장
```

**6. 금지 규칙**

```text
도메인 계층에서 HttpError raise 금지
도메인 예외에 status_code 필드 금지
엔드포인트마다 try/except로 중복 변환 금지
문자열 메시지만 보고 status 결정 금지
Exception, ValueError를 도메인 규칙 표현에 사용 금지
스택트레이스, 내부 클래스명, DB 제약명 응답 노출 금지
```

**7. 엔드포인트 사용 예**

```python
# apps/orders/api.py
from ninja import Router

from apps.orders.application.services import OrderApplicationService
from apps.orders.api.schemas import PayOrderIn, OrderOut

router = Router()


@router.post("/{order_id}/payments", response={200: OrderOut})
def pay_order(request, order_id: str, payload: PayOrderIn) -> OrderOut:
    service = OrderApplicationService()
    order = service.pay_order(order_id=order_id, amount=payload.amount)
    return OrderOut.from_domain(order)
```

엔드포인트는 도메인 예외를 잡지 않습니다. 예외는 전역 핸들러가 Problem Details로 변환합니다.

**최종 기준**

Domain:

```text
비즈니스 언어로 예외를 정의한다.
HTTP를 모른다.
code/message/context만 가진다.
```

Application:

```text
use case를 조율한다.
도메인 예외를 삼키지 않는다.
```

API:

```text
DomainError를 한 곳에서 Problem Details로 번역한다.
status/type/title/code 매핑을 중앙화한다.
모든 에러 응답 형식을 통일한다.
```

---
> **관련 스킬 참조:**
> - API 에러 응답 설계 → **architecture-api** 스킬
> - 도메인 예외 모델링 → **architecture-ddd** 스킬
> - Django Ninja 예외 핸들러 구현 → **implementation-django-ninja** 스킬