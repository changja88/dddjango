**리뷰 결과**

서비스 레이어 없이 Django Ninja view에 주문 생성 로직을 전부 넣는 것은, “장바구니 한 줄 저장” 수준의 매우 얇은 CRUD가 아니라면 권장하지 않습니다. 주문 생성은 보통 재고 차감, 가격 확정, 쿠폰/포인트, 결제 준비, 중복 요청 방지, 알림/이벤트 발행이 묶이는 유스케이스라서 Ninja endpoint가 비대해지기 쉽습니다.

[Convention: Fat endpoint] -- Django Ninja endpoint는 HTTP 경계여야 합니다. `Schema`로 입력을 받고, 인증/헤더를 확인한 뒤, application service를 호출하고 응답 스키마로 반환하는 정도가 적절합니다. 주문 생성 규칙을 view에 넣으면 CLI, admin action, batch, webhook 재처리 같은 다른 진입점에서 같은 규칙을 재사용하기 어렵습니다.

[DDD: Application Service] -- 서비스 레이어는 “도메인 로직을 전부 넣는 곳”이 아니라 유스케이스 오케스트레이션 계층입니다. 가격 계산, 주문 가능 상태, 수량 검증 같은 핵심 규칙은 `Order`, `OrderLine`, `Money` 같은 도메인 모델/값 객체나 모델 메서드에 두고, 서비스는 트랜잭션, 저장 순서, 외부 포트 호출, 이벤트 예약을 조율해야 합니다.

[Transaction Boundary] -- 주문 생성은 하나의 명확한 `transaction.atomic()` 경계가 필요합니다. 재고나 멱등성 레코드는 DB unique constraint, `select_for_update()`, 상태 전이로 보호해야 하고, 이메일/알림/외부 API/메시지 발행은 반드시 `transaction.on_commit()` 이후로 밀어야 합니다. 트랜잭션 안에서 외부 호출을 하면 롤백과 부수효과가 어긋납니다.

[API Contract] -- 중요한 `POST /orders`에는 `Idempotency-Key` 처리가 필요합니다. 같은 키로 재시도하면 기존 결과를 반환하거나, 다른 payload면 `409 Conflict`를 반환해야 합니다. 오류 응답은 임의 JSON 대신 RFC 9457 Problem Details 형태로 통일하는 편이 클라이언트 구현에 좋습니다.

**권장 구조**

```python
# orders/schemas.py
from decimal import Decimal
from ninja import Schema


class OrderLineIn(Schema):
    product_id: int
    quantity: int


class OrderCreateIn(Schema):
    lines: list[OrderLineIn]
    coupon_code: str | None = None


class OrderOut(Schema):
    id: int
    status: str
    total_amount: Decimal
```

```python
# orders/errors.py
class OrderError(Exception):
    status_code = 400
    title = "Order error"

    def __init__(self, detail: str):
        self.detail = detail


class DuplicateIdempotencyKey(OrderError):
    status_code = 409
    title = "Idempotency conflict"


class OutOfStock(OrderError):
    status_code = 409
    title = "Out of stock"
```

```python
# orders/services.py
from dataclasses import dataclass
from django.db import transaction

from .errors import DuplicateIdempotencyKey, OutOfStock
from .models import IdempotencyRecord, Order, Product
from .events import publish_order_created


@dataclass(frozen=True)
class CreateOrderCommand:
    user_id: int
    lines: list[dict]
    coupon_code: str | None
    idempotency_key: str


def create_order(command: CreateOrderCommand) -> Order:
    with transaction.atomic():
        idem, created = IdempotencyRecord.objects.select_for_update().get_or_create(
            user_id=command.user_id,
            key=command.idempotency_key,
            defaults={"request_hash": hash_payload(command)},
        )

        if not created:
            if idem.request_hash != hash_payload(command):
                raise DuplicateIdempotencyKey("Same key was used with a different payload.")
            return idem.order

        order = Order.objects.create_pending(user_id=command.user_id)

        for line in command.lines:
            product = Product.objects.select_for_update().get(pk=line["product_id"])
            if product.stock < line["quantity"]:
                raise OutOfStock(f"Product {product.id} is out of stock.")

            product.decrease_stock(line["quantity"])
            product.save(update_fields=["stock"])
            order.add_line(product=product, quantity=line["quantity"])

        order.apply_coupon(command.coupon_code)
        order.confirm_pricing()
        order.save()

        idem.order = order
        idem.save(update_fields=["order"])

        transaction.on_commit(lambda: publish_order_created(order.id))

        return order
```

```python
# orders/api.py
from django.http import HttpRequest
from ninja import Router, Header
from ninja.security import django_auth

from .errors import OrderError
from .schemas import OrderCreateIn, OrderOut
from .services import CreateOrderCommand, create_order

router = Router(auth=django_auth)


@router.post("/orders", response={201: OrderOut})
def create_order_endpoint(
    request: HttpRequest,
    payload: OrderCreateIn,
    idempotency_key: str = Header(alias="Idempotency-Key"),
) -> tuple[int, OrderOut]:
    order = create_order(
        CreateOrderCommand(
            user_id=request.user.id,
            lines=[line.dict() for line in payload.lines],
            coupon_code=payload.coupon_code,
            idempotency_key=idempotency_key,
        )
    )
    return 201, order
```

```python
# config/api.py
from ninja import NinjaAPI
from orders.api import router as orders_router
from orders.errors import OrderError

api = NinjaAPI()


@api.exception_handler(OrderError)
def order_error_handler(request, exc: OrderError):
    return api.create_response(
        request,
        {
            "type": f"https://api.example.com/problems/{exc.title.lower().replace(' ', '-')}",
            "title": exc.title,
            "status": exc.status_code,
            "detail": exc.detail,
            "instance": request.path,
        },
        status=exc.status_code,
    )


api.add_router("", orders_router)
```

핵심은 “서비스 레이어를 무조건 만들자”가 아니라, 주문 생성처럼 트랜잭션과 도메인 규칙, 부수효과, 멱등성이 얽힌 유스케이스는 endpoint에 두지 말자는 것입니다. Ninja view는 얇게, application service는 유스케이스 조율, 도메인 모델은 불변식 보호, `on_commit`은 커밋 후 부수효과 처리로 나누는 쪽이 유지보수와 테스트 모두에서 낫습니다.

---
> **관련 스킬 참조:**
> - Django Ninja Schema/Router/API 오류 처리 → **implementation-django-ninja** 스킬
> - 서비스 레이어와 transaction.on_commit → **implementation-django** 스킬
> - 애그리거트/애플리케이션 서비스 경계 → **architecture-ddd** 스킬
> - POST 멱등성과 Problem Details 오류 계약 → **architecture-api** 스킬