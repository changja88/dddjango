**[주요 내용]**

전제: `orders`는 주문 생성의 핵심 컨텍스트, `catalog/inventory`는 상품/재고 컨텍스트, `payments`는 외부 결제 컨텍스트다. 주문 API는 이 셋을 직접 섞지 않고 `PlaceOrderService`가 포트로 조율한다.

| 용어 | 의미 | 금지 동의어 |
|---|---|---|
| 주문 생성 | 주문을 만들고 결제 대기 상태로 둠 | 결제 완료 |
| 재고 예약 | 결제 전 수량을 잠금/차감 가능한 상태로 확보 | 단순 조회 |
| 결제 준비 | 결제사 payment intent/session 생성 | 결제 승인 |

핵심 경계는 이렇게 둔다.

- `Order` Aggregate Root: 주문 라인, 금액, 상태 불변식 보호. 상품은 `product_id`와 가격 스냅샷으로만 참조한다.
- `Money` Value Object: 통화/금액 검증과 합산.
- `InventoryPort`: 재고 확인과 예약. DB 구현은 `select_for_update()` 또는 조건부 `F()` 업데이트로 race condition을 막는다.
- `PaymentPort`: 결제사 SDK/HTTP 세부사항 격리.
- `IdempotencyStore`: `Idempotency-Key + request_hash` 기준으로 중복 생성 방지.

트랜잭션은 “주문 생성 + 재고 예약 + 멱등성 진행 상태 저장”까지만 묶는다. 외부 결제사 호출은 DB 트랜잭션 안에서 하지 않는다. 커밋 후 `PaymentPort.prepare()`를 호출하고, 짧은 두 번째 트랜잭션에서 payment reference와 멱등성 최종 응답을 저장한다. 결제 준비 실패 응답을 저장해야 하면 `atomic()` 안에서 저장 후 예외를 다시 던지지 말고 명시적 실패 결과로 반환한다.

```python
# apps/orders/domain.py
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise InvalidOrderAmountError


class Order:
    """Aggregate Root.
    Invariants: lines are non-empty, total equals line price snapshots,
    status starts as pending_payment, product aggregates are referenced by ID.
    """

    @classmethod
    def place(cls, customer_id: UUID, lines: list["PricedLine"]) -> "Order":
        if not lines:
            raise EmptyOrderError
        total = sum((line.subtotal for line in lines), Money(Decimal("0")))
        return cls(customer_id=customer_id, lines=lines, total=total)


@dataclass(frozen=True)
class OrderPlacedEvent:
    order_id: UUID
```

```python
# apps/orders/ports.py
from abc import ABC, abstractmethod
from uuid import UUID


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None: ...

    @abstractmethod
    def attach_payment(self, order_id: UUID, payment_id: str) -> None: ...


class InventoryPort(ABC):
    @abstractmethod
    def reserve(self, product_id: UUID, quantity: int) -> "PriceSnapshot": ...


class PaymentPort(ABC):
    @abstractmethod
    def prepare(
        self,
        *,
        order_id: UUID,
        amount: Money,
        idempotency_key: str,
    ) -> "PreparedPayment": ...
```

```python
# apps/orders/application.py
from django.db import transaction


class PlaceOrderService:
    def __init__(
        self,
        orders: OrderRepository,
        inventory: InventoryPort,
        payments: PaymentPort,
        idem: IdempotencyStore,
    ) -> None:
        self.orders = orders
        self.inventory = inventory
        self.payments = payments
        self.idem = idem

    def place(self, *, customer_id, command, idem_key: str) -> "OrderResult":
        request_hash = command.stable_hash()

        with transaction.atomic():
            replay = self.idem.start_or_replay(idem_key, request_hash)
            if replay:
                return replay

            priced_lines = [
                PricedLine.from_snapshot(
                    item.product_id,
                    item.quantity,
                    self.inventory.reserve(item.product_id, item.quantity),
                )
                for item in command.lines
            ]
            order = Order.place(customer_id, priced_lines)
            self.orders.save(order)
            self.idem.mark_processing(idem_key, order.id)

        payment = self.payments.prepare(
            order_id=order.id,
            amount=order.total,
            idempotency_key=f"order:{order.id}:payment",
        )

        result = OrderResult.from_order(order, payment)

        with transaction.atomic():
            self.orders.attach_payment(order.id, payment.payment_id)
            self.idem.complete(idem_key, result)

        return result
```

API는 주문 컬렉션에 `POST /v1/orders`로 둔다. 중요한 POST라 `Idempotency-Key`는 필수다. 같은 키에 다른 payload면 `409 Conflict`, 재고 부족은 도메인 검증 실패로 `422`, 결제사 장애는 `502` 또는 비동기 보상 정책이면 `201 pending_payment` 후 별도 상태 조회로 처리한다.

```python
# apps/orders/api.py
from decimal import Decimal
from typing import Literal
from uuid import UUID

from django.http import HttpRequest
from ninja import Header, Router, Schema

router = Router(tags=["orders"])


class OrderLineIn(Schema):
    product_id: UUID
    quantity: int


class CreateOrderIn(Schema):
    lines: list[OrderLineIn]


class PaymentOut(Schema):
    payment_id: str
    checkout_url: str | None = None


class OrderCreatedOut(Schema):
    order_id: UUID
    status: Literal["pending_payment"]
    total_amount: Decimal
    currency: str
    payment: PaymentOut


class ProblemDetail(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str | None = None


@router.post(
    "",
    response={
        201: OrderCreatedOut,
        200: OrderCreatedOut,
        409: ProblemDetail,
        422: ProblemDetail,
        502: ProblemDetail,
    },
)
def create_order(
    request: HttpRequest,
    payload: CreateOrderIn,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
) -> tuple[int, OrderCreatedOut]:
    command = PlaceOrderCommand.from_schema(payload)
    result = request.services.place_order.place(
        customer_id=request.user.id,
        command=command,
        idem_key=idempotency_key,
    )
    return (200 if result.replayed else 201), OrderCreatedOut.model_validate(result)
```

```python
# config/api.py
from ninja import NinjaAPI
from apps.orders.api import router as orders_router

api = NinjaAPI(version="1.0.0")
api.add_router("/v1/orders", orders_router)
```

검증 포인트는 `Idempotency-Key` 재시도, 같은 키/다른 payload 충돌, 동시 주문의 재고 초과 방지, 결제 준비 실패 시 멱등성 실패 응답 보존이다.

---
> **관련 스킬 참조:**
> - API 오류/멱등성 상세화 → **architecture-api** 스킬
> - Aggregate/Repository 구체화 → **architecture-ddd** 스킬
> - 실제 Django Ninja 구현 → **implementation-django-ninja** 스킬