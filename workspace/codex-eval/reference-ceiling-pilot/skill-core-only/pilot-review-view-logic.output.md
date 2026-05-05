**리뷰 결과**

주문 생성 로직을 Django Ninja endpoint/view에 전부 넣는 것은 보통 피하는 게 맞습니다. 주문 생성은 대개 재고 확인, 가격 확정, 쿠폰/포인트, 결제 준비, 중복 요청 방지, 알림 같은 여러 변경 이유가 섞이는 유스케이스라서 endpoint가 금방 Fat View가 됩니다.

예외는 있습니다. 단일 모델에 `Order.objects.create(...)`만 하고, 도메인 불변식도 없고, 외부 부수효과도 없고, 중복 요청 피해도 작은 내부 CRUD라면 view에 남겨도 됩니다. 하지만 “주문 생성”은 보통 그 예외에 속하지 않습니다.

**주요 지적**

[Convention: Fat endpoint] -- Ninja endpoint는 HTTP 경계여야 합니다. 요청 Schema 검증, 인증 사용자 추출, application service 호출, 응답/에러 매핑만 담당하는 것이 좋습니다. 주문 생성 절차를 endpoint에 넣으면 API 형식 변경, 도메인 규칙 변경, 트랜잭션 변경, 알림 변경이 한 함수에 묶입니다.

[DDD: Application Service split] -- application service는 유스케이스 조율 계층입니다. 재고 차감, 주문 생성, 결제 준비, 이벤트 수집 같은 흐름을 묶되, “주문 가능한가”, “총액은 어떻게 확정되는가” 같은 도메인 규칙은 `Order`, `OrderLine`, `Money` 같은 도메인 객체나 모델 메서드 쪽에 둬야 합니다. 서비스가 모든 비즈니스 규칙을 빨아들이면 빈약한 도메인 모델이 됩니다.

[Transaction boundary] -- 주문 생성은 `transaction.atomic()`으로 묶고, 이메일/알림/외부 API 호출은 `transaction.on_commit()` 뒤로 빼야 합니다. 트랜잭션 안에서 알림을 보내면 DB rollback 이후에도 외부 세계에는 “주문됨”이 전파될 수 있습니다.

[Idempotency] -- `POST /orders`는 멱등하지 않은 중요한 엔드포인트라 `Idempotency-Key`가 필요합니다. 클라이언트 재시도, 네트워크 타임아웃, 결제/주문 중복 생성 방지를 위해 서버가 키별 결과를 저장하고 같은 키에는 같은 응답을 돌려줘야 합니다.

[Error contract] -- 에러는 임의 JSON이 아니라 RFC 9457 Problem Details 형태로 고정하는 편이 좋습니다. `409`는 중복/충돌, `422`는 도메인 검증 실패, `401/403`은 인증/인가, 응답 Content-Type은 `application/problem+json`으로 맞춥니다.

**권장 구조 스케치**

```python
# orders/api.py
from django.http import HttpRequest
from ninja import Router, Schema

from orders.application import CreateOrderCommand, create_order
from orders.errors import IdempotencyConflict, OutOfStock
from orders.problem import problem

router = Router(tags=["orders"])


class OrderLineIn(Schema):
    product_id: int
    quantity: int


class CreateOrderIn(Schema):
    lines: list[OrderLineIn]


class OrderOut(Schema):
    id: int
    status: str
    total_amount: str


@router.post("", response={201: OrderOut}, auth=...)
def create_order_endpoint(
    request: HttpRequest,
    payload: CreateOrderIn,
) -> tuple[int, OrderOut]:
    idempotency_key = request.headers.get("Idempotency-Key")
    if not idempotency_key:
        raise problem(
            status=400,
            title="Missing Idempotency-Key",
            detail="Idempotency-Key header is required for order creation.",
        )

    result = create_order(
        CreateOrderCommand(
            customer_id=request.user.id,
            lines=[
                (line.product_id, line.quantity)
                for line in payload.lines
            ],
            idempotency_key=idempotency_key,
        )
    )
    return 201, OrderOut(
        id=result.order_id,
        status=result.status,
        total_amount=str(result.total_amount),
    )
```

```python
# orders/application.py
from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction

from orders.idempotency import IdempotencyStore
from orders.models import Order
from orders.notifications import send_order_created


@dataclass(frozen=True)
class CreateOrderCommand:
    customer_id: int
    lines: list[tuple[int, int]]
    idempotency_key: str


@dataclass(frozen=True)
class CreateOrderResult:
    order_id: int
    status: str
    total_amount: Decimal


def create_order(command: CreateOrderCommand) -> CreateOrderResult:
    cached = IdempotencyStore.get_completed(command.idempotency_key)
    if cached:
        return CreateOrderResult(**cached.response_body)

    with transaction.atomic():
        IdempotencyStore.lock_or_create(
            key=command.idempotency_key,
            request_fingerprint=command,
        )

        order = Order.create_for_customer(
            customer_id=command.customer_id,
            lines=command.lines,
        )
        order.reserve_stock()
        order.confirm()

        order.save()

        result = CreateOrderResult(
            order_id=order.id,
            status=order.status,
            total_amount=order.total_amount,
        )
        IdempotencyStore.mark_completed(
            key=command.idempotency_key,
            response_body=result.__dict__,
        )

        transaction.on_commit(lambda: send_order_created(order.id))

    return result
```

```python
# orders/problem.py
from django.http import JsonResponse
from ninja.errors import HttpError


class ProblemError(HttpError):
    def __init__(self, status: int, title: str, detail: str, type_: str = "about:blank"):
        self.body = {
            "type": type_,
            "title": title,
            "status": status,
            "detail": detail,
        }
        super().__init__(status, detail)


def problem(status: int, title: str, detail: str, type_: str = "about:blank") -> ProblemError:
    return ProblemError(status, title, detail, type_)


def problem_response(error: ProblemError) -> JsonResponse:
    return JsonResponse(
        error.body,
        status=error.status_code,
        content_type="application/problem+json",
    )
```

핵심은 “서비스 레이어를 무조건 만든다”가 아니라, 주문 생성처럼 트랜잭션, 멱등성, 도메인 규칙, 부수효과가 얽힌 유스케이스는 endpoint 밖으로 빼는 게 변경 이유를 제대로 분리한다는 점입니다. Ninja endpoint는 얇게 두고, application service가 유스케이스를 조율하며, 도메인 규칙은 모델/도메인 객체 쪽에 남기는 구성이 가장 무난합니다.

---
> **관련 스킬 참조:**
> - Django Ninja endpoint / Schema / error handling → **implementation-django-ninja** 스킬
> - Django transaction / service layer / on_commit → **implementation-django** 스킬
> - Application Service / Aggregate / Domain Event → **architecture-ddd** 스킬
> - POST idempotency / Problem Details error contract → **architecture-api** 스킬