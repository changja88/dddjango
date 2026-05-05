**주요 내용**

결론부터 말하면, “주문 생성 로직을 전부 Django Ninja view에 넣는 것”은 대부분의 주문 도메인에서는 비권장입니다. 아주 단순한 CRUD 수준이라면 view 안의 짧은 transaction script도 허용될 수 있지만, 주문 생성은 보통 재고 확인, 가격 확정, 쿠폰/포인트, 결제 준비, 멱등성, 알림, 이벤트 발행, 실패 응답 계약이 얽히기 쉽습니다. 이 경우 Ninja endpoint는 얇은 HTTP 경계로 두고, 유스케이스 조율은 application service로 빼는 편이 낫습니다.

[Convention: Fat endpoint] -- Django Ninja endpoint가 주문 생성 규칙, ORM 저장, 재고 차감, 외부 알림, 에러 매핑을 모두 처리하면 HTTP 입출력과 애플리케이션 흐름이 결합됩니다. endpoint는 `Schema` 검증, 인증된 사용자 추출, 헤더 읽기, service 호출, 응답 매핑까지만 담당하는 경계가 적절합니다.

[DDD: application service split] -- 주문 생성은 “주문을 만든다”는 유스케이스입니다. application service는 트랜잭션을 열고, idempotency key를 확인하고, aggregate/model 메서드를 호출하고, repository/ORM 저장을 조율합니다. 단, 가격 계산, 주문 가능 여부, 상태 전이 같은 도메인 규칙은 가능하면 `Order`, `OrderLine`, `Money` 같은 모델/값 객체 쪽에 둡니다. 서비스가 모든 비즈니스 규칙을 먹어버리면 빈약한 도메인 모델로 흐릅니다.

[Transaction boundary] -- 외부 이메일, 알림, 웹훅, 메시지 발행은 `transaction.atomic()` 내부에서 바로 실행하면 안 됩니다. DB 커밋이 롤백되어도 외부 부수효과는 되돌릴 수 없습니다. 커밋 성공 후 실행되어야 하므로 `transaction.on_commit()`으로 분리해야 합니다.

[Idempotency] -- `POST /orders`는 기본적으로 멱등하지 않습니다. 주문 생성은 중복 요청 비용이 크므로 `Idempotency-Key`를 받는 편이 안전합니다. 같은 사용자와 같은 key에 대해 이미 성공한 결과가 있으면 기존 주문 응답을 재사용하고, 진행 중이거나 payload fingerprint가 다르면 `409 Conflict`로 계약을 고정하는 식이 좋습니다.

[Error contract] -- view/service 곳곳에서 임의 JSON을 반환하지 말고 RFC 9457 Problem Details 형태로 맞추는 게 낫습니다. 예: `type`, `title`, `status`, `detail`, `instance`. 재고 부족은 보통 `422`, 멱등성 충돌은 `409`, 인증 누락은 `401`, 권한 없음은 `403`처럼 일관되게 매핑합니다.

작게 잡으면 이런 형태가 적당합니다.

```python
# orders/api/schemas.py
from ninja import Schema


class CreateOrderIn(Schema):
    product_id: int
    quantity: int


class OrderOut(Schema):
    id: int
    status: str
    total_amount: str


class ProblemDetails(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str
```

```python
# orders/api/router.py
from django.http import HttpRequest
from ninja import Router

from orders.api.schemas import CreateOrderIn, OrderOut, ProblemDetails
from orders.services import (
    IdempotencyConflict,
    InsufficientStock,
    create_order,
)

router = Router(tags=["orders"])


def problem(
    *,
    status: int,
    title: str,
    detail: str,
    instance: str,
    type_: str = "about:blank",
) -> ProblemDetails:
    return ProblemDetails(
        type=type_,
        title=title,
        status=status,
        detail=detail,
        instance=instance,
    )


@router.post(
    "",
    response={201: OrderOut, 409: ProblemDetails, 422: ProblemDetails},
)
def create_order_endpoint(
    request: HttpRequest,
    payload: CreateOrderIn,
) -> tuple[int, OrderOut | ProblemDetails]:
    try:
        order = create_order(
            user=request.user,
            product_id=payload.product_id,
            quantity=payload.quantity,
            idempotency_key=request.headers.get("Idempotency-Key"),
            request_path=request.path,
        )
    except IdempotencyConflict as exc:
        return 409, problem(
            status=409,
            title="Idempotency conflict",
            detail=str(exc),
            instance=request.path,
        )
    except InsufficientStock as exc:
        return 422, problem(
            status=422,
            title="Insufficient stock",
            detail=str(exc),
            instance=request.path,
        )

    return 201, OrderOut(
        id=order.id,
        status=order.status,
        total_amount=str(order.total_amount),
    )
```

```python
# orders/services.py
from django.db import transaction

from orders.models import IdempotencyRecord, Order, Product
from orders.notifications import send_order_created_notification


class InsufficientStock(Exception):
    pass


class IdempotencyConflict(Exception):
    pass


@transaction.atomic
def create_order(
    *,
    user,
    product_id: int,
    quantity: int,
    idempotency_key: str | None,
    request_path: str,
) -> Order:
    if idempotency_key:
        existing = IdempotencyRecord.objects.find_completed(
            user=user,
            key=idempotency_key,
        )
        if existing:
            return existing.order

    product = Product.objects.select_for_update().get(id=product_id)

    if product.stock < quantity:
        raise InsufficientStock("Requested quantity exceeds available stock.")

    order = Order.create(
        user=user,
        product=product,
        quantity=quantity,
    )

    product.reserve(quantity)
    product.save(update_fields=["stock"])
    order.save()

    if idempotency_key:
        IdempotencyRecord.objects.create_completed(
            user=user,
            key=idempotency_key,
            order=order,
        )

    transaction.on_commit(
        lambda: send_order_created_notification(order_id=order.id)
    )

    return order
```

핵심은 “서비스 레이어를 무조건 만들자”가 아니라, 주문 생성처럼 트랜잭션, 멱등성, 도메인 규칙, 부수효과, 에러 계약이 같이 움직이는 유스케이스는 view에 두면 변경 이유가 섞인다는 점입니다. Ninja endpoint는 얇게 유지하고, application service가 유스케이스를 조율하며, 실제 불변식은 도메인 모델/값 객체가 지키는 구조가 더 오래 버팁니다.

---
> **관련 스킬 참조:**
> - Django Ninja Schema/Router, 에러 응답, 멱등성 → **implementation-django-ninja** 스킬
> - 서비스 레이어, `transaction.on_commit`, ORM 트랜잭션 → **implementation-django** 스킬
> - 애그리거트, application service, 도메인 규칙 위치 → **architecture-ddd** 스킬
> - 상태 코드, Problem Details, POST 멱등성 → **architecture-api** 스킬