**주요 내용**

바운디드 컨텍스트는 `Ordering`이 중심이고, `Catalog/Inventory`와 `Payment`는 포트로만 의존합니다. 주문 생성 유스케이스는 “재고 확인 → 금액 계산 → 주문 생성 → 결제 준비”를 조율하지만, 재고 규칙은 `InventoryPort`, 결제 SDK는 `PaymentPort` 뒤에 둡니다.

유비쿼터스 언어:

| 용어 | 의미 | 금지 동의어 |
|---|---|---|
| Order | 결제 전 생성된 주문 애그리거트 | Purchase |
| OrderLine | 상품별 주문 라인 | CartItem |
| Money | 통화 포함 금액 값 객체 | int price |
| PaymentPreparation | 결제 승인 전 준비 결과 | PaymentResult |

핵심 경계:
- Aggregate Root: `Order`
- 불변식: 주문 총액은 주문 라인 합계와 같아야 하고, 빈 주문은 만들 수 없음
- 트랜잭션 경계: 재고 예약, 주문 저장, 멱등성 기록은 하나의 `transaction.atomic()`
- 외부 결제 준비: DB 트랜잭션 밖에서 `PaymentPort.prepare()` 호출. 결제사는 자체 idempotency key를 받게 함
- 멱등성: `Idempotency-Key` 헤더를 `user_id + key + endpoint` 기준으로 unique 처리

```python
# orders/domain.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise InvalidOrderError("amount must be non-negative")


@dataclass(frozen=True)
class OrderLine:
    product_id: int
    quantity: int
    unit_price: Money

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise InvalidOrderError("quantity must be positive")

    def subtotal(self) -> Money:
        return Money(self.unit_price.amount * self.quantity, self.unit_price.currency)


class InvalidOrderError(Exception):
    pass


class InsufficientStockError(Exception):
    pass


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: "Order") -> None: ...


class InventoryPort(ABC):
    @abstractmethod
    def reserve(self, *, product_id: int, quantity: int) -> None: ...


class PaymentPort(ABC):
    @abstractmethod
    def prepare(
        self,
        *,
        order_id: int,
        amount: Money,
        idempotency_key: str,
    ) -> "PaymentPreparation": ...


@dataclass(frozen=True)
class PaymentPreparation:
    provider_payment_id: str
    redirect_url: str
```

```python
# orders/application.py
from dataclasses import dataclass
from django.db import transaction

from orders.domain import InventoryPort, Money, OrderLine, OrderRepository, PaymentPort


@dataclass(frozen=True)
class CreateOrderCommand:
    user_id: int
    lines: list[OrderLine]
    idempotency_key: str


@dataclass(frozen=True)
class CreateOrderResult:
    order_id: int
    total: Money
    payment_id: str
    payment_url: str


class CreateOrderService:
    def __init__(
        self,
        *,
        orders: OrderRepository,
        inventory: InventoryPort,
        payments: PaymentPort,
    ) -> None:
        self.orders = orders
        self.inventory = inventory
        self.payments = payments

    def create(self, command: CreateOrderCommand) -> CreateOrderResult:
        with transaction.atomic():
            existing = IdempotencyRecord.objects.select_for_update().filter(
                user_id=command.user_id,
                key=command.idempotency_key,
                endpoint="orders:create",
            ).first()
            if existing:
                return existing.to_result()

            for line in command.lines:
                self.inventory.reserve(
                    product_id=line.product_id,
                    quantity=line.quantity,
                )

            order = Order.create(user_id=command.user_id, lines=command.lines)
            self.orders.save(order)
            total = order.total()

            idem = IdempotencyRecord.objects.create_pending(
                user_id=command.user_id,
                key=command.idempotency_key,
                endpoint="orders:create",
                order_id=order.id,
            )

        payment = self.payments.prepare(
            order_id=order.id,
            amount=total,
            idempotency_key=command.idempotency_key,
        )

        with transaction.atomic():
            idem.mark_succeeded(
                total=total.amount,
                payment_id=payment.provider_payment_id,
                payment_url=payment.redirect_url,
            )

        return CreateOrderResult(
            order_id=order.id,
            total=total,
            payment_id=payment.provider_payment_id,
            payment_url=payment.redirect_url,
        )
```

```python
# orders/api.py
from decimal import Decimal

from django.http import HttpRequest
from ninja import Router, Schema

from orders.application import CreateOrderCommand, CreateOrderService
from orders.domain import Money, OrderLine

router = Router(tags=["orders"])


class OrderLineIn(Schema):
    product_id: int
    quantity: int


class OrderLineOut(Schema):
    product_id: int
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class CreateOrderIn(Schema):
    lines: list[OrderLineIn]


class CreateOrderOut(Schema):
    order_id: int
    total: Decimal
    currency: str
    payment_id: str
    payment_url: str
    lines: list[OrderLineOut]


@router.post("/", response={201: CreateOrderOut})
def create_order(request: HttpRequest, payload: CreateOrderIn) -> tuple[int, CreateOrderOut]:
    idempotency_key = request.headers["Idempotency-Key"]

    priced_lines = [
        OrderLine(
            product_id=line.product_id,
            quantity=line.quantity,
            unit_price=Money(amount=ProductPriceSelector.get_price(line.product_id)),
        )
        for line in payload.lines
    ]

    result = CreateOrderService(
        orders=DjangoOrderRepository(),
        inventory=DjangoInventoryAdapter(),
        payments=PaymentGatewayAdapter(),
    ).create(
        CreateOrderCommand(
            user_id=request.user.id,
            lines=priced_lines,
            idempotency_key=idempotency_key,
        )
    )

    return 201, CreateOrderOut(
        order_id=result.order_id,
        total=result.total.amount,
        currency=result.total.currency,
        payment_id=result.payment_id,
        payment_url=result.payment_url,
        lines=[],
    )
```

오류 응답은 RFC 9457 Problem Details로 맞춥니다. 예: 재고 부족은 `409 Conflict`, 입력 검증은 `422`, 멱등성 키 누락은 `400`입니다. `Idempotency-Key`가 같은 재시도는 같은 `201` 응답 본문을 반환하고, 같은 키로 다른 payload가 오면 `409`로 막습니다.

```python
# config/api.py
from ninja import NinjaAPI
from orders.api import router as orders_router

api = NinjaAPI(version="1.0.0")
api.add_router("/orders/", orders_router)
```

---
> **관련 스킬 참조:**
> - API 오류 형식/멱등성 세부 설계 → **architecture-api** 스킬
> - 애그리거트/리포지토리/포트 구체화 → **architecture-ddd** 스킬
> - 실제 Django Ninja 라우터/Schema 구현 → **implementation-django-ninja** 스킬