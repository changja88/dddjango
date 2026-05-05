**주요 내용**

바운디드 컨텍스트는 이렇게 나눈다.

| Context | 책임 | 소유 모델 |
|---|---|---|
| Ordering | 주문 생성, 주문 금액 계산, 주문 상태 | `Order` aggregate |
| Catalog | 상품명, 판매가 조회 | `ProductSnapshot` 조회/port |
| Inventory | 재고 확인/예약 | `InventoryPort` |
| Payments | 결제 준비/승인 | `PaymentPort` |

유비쿼터스 언어는 `place order`, `reserve stock`, `calculate total`, `prepare payment`로 고정한다. 금지 동의어는 `create cart order`, `hold inventory`, `make payment`다. 결제 준비는 결제 승인/캡처가 아니므로 `pay()`나 `charge()`로 부르지 않는다.

REST 리소스는 명사 기준이다.

| Method | Path | 의미 | 성공 |
|---|---|---|---|
| `POST` | `/v1/orders` | 주문 생성 + 재고 예약 + 결제 준비 | `201 Created` |
| `GET` | `/v1/orders/{order_id}` | 주문 조회 | `200 OK` |
| `GET` | `/v1/orders?status=&created_from=&created_to=&sort=-created_at&cursor=` | 목록 | `200 OK` |

`POST /v1/orders`는 `Idempotency-Key` 헤더 필수다. 같은 사용자, 같은 키, 같은 요청 본문이면 기존 결과를 반환하고, 같은 키에 다른 본문이면 `409 Conflict`다.

```python
# orders/domain.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise InvalidOrder("amount must be non-negative")


@dataclass(frozen=True)
class OrderLine:
    product_id: UUID
    product_name: str
    unit_price: Money
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise InvalidOrder("quantity must be positive")

    @property
    def subtotal(self) -> Money:
        return Money(self.unit_price.amount * self.quantity)


@dataclass(frozen=True)
class OrderPlacedEvent:
    order_id: UUID
    customer_id: UUID
    total_amount: Money


class Order:
    """Aggregate Root.

    Invariants:
    - 주문 항목은 1개 이상이어야 한다.
    - 주문 총액은 모든 OrderLine subtotal 합계와 일치해야 한다.
    - Order는 Product/Inventory/Payment aggregate를 객체로 참조하지 않고 ID/port로만 협력한다.
    """

    @classmethod
    def place(cls, *, customer_id: UUID, lines: list[OrderLine]) -> "Order":
        if not lines:
            raise InvalidOrder("order must contain at least one line")
        total = Money(sum(line.subtotal.amount for line in lines))
        return cls(customer_id=customer_id, lines=lines, total_amount=total)


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None: ...

    @abstractmethod
    def find_by_id(self, order_id: UUID) -> Order | None: ...


class InventoryPort(ABC):
    @abstractmethod
    def reserve(self, *, order_id: UUID, items: list[tuple[UUID, int]]) -> None: ...


class PaymentPort(ABC):
    @abstractmethod
    def prepare(
        self, *, order_id: UUID, amount: Money, idempotency_key: str
    ) -> "PaymentPreparation": ...
```

트랜잭션 경계는 DB 일관성과 외부 결제를 분리한다.

1. `transaction.atomic()` 안에서 멱등성 키 잠금, 상품 스냅샷 조회, 재고 예약, 주문 저장을 끝낸다.
2. 커밋 이후 `PaymentPort.prepare()`를 호출한다. 결제사는 같은 `Idempotency-Key`를 받아야 한다.
3. 결제 준비 성공/실패 결과는 별도 짧은 트랜잭션으로 주문/멱등성 레코드에 저장한다.
4. 결제 포트 장애는 주문 생성 전체를 롤백하지 않는다. 주문은 `PAYMENT_PREPARING` 또는 `PAYMENT_PREPARE_FAILED`로 남기고 클라이언트에는 `503` 또는 재조회 가능한 상태를 준다.

```python
# orders/application.py
from dataclasses import dataclass
from django.db import transaction


@dataclass(frozen=True)
class PlaceOrderCommand:
    customer_id: UUID
    items: list[tuple[UUID, int]]
    idempotency_key: str
    request_hash: str


class PlaceOrderService:
    def place(self, cmd: PlaceOrderCommand) -> "PlaceOrderResult":
        with transaction.atomic():
            idem = self.idempotency_repo.lock_or_create(
                key=cmd.idempotency_key,
                customer_id=cmd.customer_id,
                request_hash=cmd.request_hash,
            )
            if idem.is_completed:
                return idem.result
            if idem.has_different_request(cmd.request_hash):
                raise IdempotencyConflict()

            snapshots = self.catalog.products_for_order(cmd.items)
            lines = [
                OrderLine(p.id, p.name, Money(p.price), qty)
                for p, qty in snapshots
            ]
            order = Order.place(customer_id=cmd.customer_id, lines=lines)

            self.inventory.reserve(order_id=order.id, items=cmd.items)
            self.orders.save(order)
            idem.mark_order_created(order.id)

        payment = self.payment.prepare(
            order_id=order.id,
            amount=order.total_amount,
            idempotency_key=cmd.idempotency_key,
        )
        self.payment_results.mark_ready(order.id, payment, cmd.idempotency_key)
        return PlaceOrderResult.from_order(order, payment)
```

Django Ninja의 요청/응답 스키마와 에러 계약은 분리한다.

```python
# orders/api.py
from uuid import UUID
from django.http import HttpRequest
from ninja import Header, Router, Schema
from ninja.security import django_auth

router = Router(auth=django_auth, tags=["orders"])


class OrderItemIn(Schema):
    product_id: UUID
    quantity: int


class PlaceOrderIn(Schema):
    items: list[OrderItemIn]
    shipping_address_id: UUID


class PaymentPreparationOut(Schema):
    provider: str
    payment_key: str
    checkout_url: str
    expires_at: str


class PlaceOrderOut(Schema):
    id: UUID
    status: str
    total_amount: str
    currency: str
    payment: PaymentPreparationOut


class ProblemDetail(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str | None = None


@router.post(
    "",
    response={201: PlaceOrderOut, 409: ProblemDetail, 422: ProblemDetail, 503: ProblemDetail},
)
def place_order(
    request: HttpRequest,
    payload: PlaceOrderIn,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
):
    result = place_order_service.place(
        PlaceOrderCommand(
            customer_id=request.user.id,
            items=[(item.product_id, item.quantity) for item in payload.items],
            idempotency_key=idempotency_key,
            request_hash=hash_payload(payload),
        )
    )
    return 201, result
```

대표 에러는 RFC 9457 Problem Details로 고정한다.

| 상황 | Status | `type` |
|---|---:|---|
| 같은 멱등성 키에 다른 요청 | `409` | `/problems/idempotency-conflict` |
| 재고 부족 | `422` | `/problems/insufficient-stock` |
| 판매 중지/없는 상품 | `422` 또는 `404` | `/problems/product-unavailable` |
| 결제 준비 포트 장애 | `503` | `/problems/payment-unavailable` |

목록 API 표준은 `cursor`, `limit`, `status`, `created_from`, `created_to`, `sort`를 사용한다. `sort`는 `created_at`, `-created_at`, `total_amount`, `-total_amount` allow-list만 허용하고, 응답은 `items/meta` 또는 Django Ninja `CursorPagination` 중 하나로 통일한다.

---
> **관련 스킬 참조:**
> - API 상태 코드/에러/멱등성 → **architecture-api** 스킬
> - Aggregate/Repository/Application Service → **architecture-ddd** 스킬
> - Django Ninja Schema/Router 구현 → **implementation-django-ninja** 스킬
> - 트랜잭션/on_commit/서비스 레이어 → **implementation-django** 스킬