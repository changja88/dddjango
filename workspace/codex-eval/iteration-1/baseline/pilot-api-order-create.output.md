현재 `/private/tmp/dddjango-codex-eval` 디렉터리는 비어 있고 읽기 전용이라 실제 파일 생성은 못 했습니다. 대신 바로 구현 가능한 DDD 기준 설계를 정리합니다.

**권장 구조**

```text
orders/
  api/
    schemas.py
    views.py
  application/
    commands.py
    services.py
    ports.py
  domain/
    models.py
    value_objects.py
    repositories.py
    services.py
    exceptions.py
  infrastructure/
    django_models.py
    repositories.py
    payment_gateway.py
```

핵심 흐름은 API가 직접 재고/결제/DB를 만지지 않고, `CreateOrderService`라는 application service가 유스케이스를 조율하는 방식입니다.

```text
Django Ninja API
 -> CreateOrderService
 -> ProductRepository: 상품/재고 조회
 -> OrderPricingService: 주문 금액 계산
 -> PaymentGateway: 결제 준비
 -> OrderRepository: 주문 저장
```

**Domain**

```python
# orders/domain/value_objects.py
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "KRW"

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("currency mismatch")
        return Money(self.amount + other.amount, self.currency)

    def multiply(self, quantity: int) -> "Money":
        return Money(self.amount * quantity, self.currency)
```

```python
# orders/domain/models.py
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from .value_objects import Money


@dataclass
class OrderLine:
    product_id: UUID
    product_name: str
    unit_price: Money
    quantity: int

    @property
    def subtotal(self) -> Money:
        return self.unit_price.multiply(self.quantity)


@dataclass
class Order:
    id: UUID
    customer_id: UUID
    lines: list[OrderLine]
    total_amount: Money
    payment_id: str | None = None
    status: str = "PAYMENT_PENDING"

    @classmethod
    def create(cls, customer_id: UUID, lines: list[OrderLine]) -> "Order":
        total = Money(0)
        for line in lines:
            total += line.subtotal

        return cls(
            id=uuid4(),
            customer_id=customer_id,
            lines=lines,
            total_amount=total,
        )
```

```python
# orders/domain/exceptions.py
class InsufficientStockError(Exception):
    pass


class ProductNotFoundError(Exception):
    pass
```

**Domain Service**

```python
# orders/domain/services.py
from .exceptions import InsufficientStockError
from .models import OrderLine


class OrderPricingService:
    def build_order_lines(self, products_by_id, requested_items) -> list[OrderLine]:
        lines = []

        for item in requested_items:
            product = products_by_id.get(item.product_id)
            if product is None:
                raise ValueError(f"product not found: {item.product_id}")

            if product.stock_quantity < item.quantity:
                raise InsufficientStockError(
                    f"insufficient stock: {product.id}"
                )

            lines.append(
                OrderLine(
                    product_id=product.id,
                    product_name=product.name,
                    unit_price=product.price,
                    quantity=item.quantity,
                )
            )

        return lines
```

**Application Layer**

```python
# orders/application/commands.py
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateOrderItemCommand:
    product_id: UUID
    quantity: int


@dataclass(frozen=True)
class CreateOrderCommand:
    customer_id: UUID
    items: list[CreateOrderItemCommand]
```

```python
# orders/application/ports.py
from typing import Protocol
from uuid import UUID
from orders.domain.models import Order


class ProductRepository(Protocol):
    def find_by_ids_for_update(self, product_ids: list[UUID]):
        ...


class OrderRepository(Protocol):
    def save(self, order: Order) -> None:
        ...


class PaymentGateway(Protocol):
    def prepare_payment(self, order: Order) -> str:
        ...
```

```python
# orders/application/services.py
from django.db import transaction

from orders.domain.models import Order
from orders.domain.services import OrderPricingService
from .commands import CreateOrderCommand
from .ports import ProductRepository, OrderRepository, PaymentGateway


class CreateOrderService:
    def __init__(
        self,
        product_repository: ProductRepository,
        order_repository: OrderRepository,
        payment_gateway: PaymentGateway,
        pricing_service: OrderPricingService,
    ):
        self.product_repository = product_repository
        self.order_repository = order_repository
        self.payment_gateway = payment_gateway
        self.pricing_service = pricing_service

    @transaction.atomic
    def execute(self, command: CreateOrderCommand) -> Order:
        product_ids = [item.product_id for item in command.items]

        products = self.product_repository.find_by_ids_for_update(product_ids)
        products_by_id = {product.id: product for product in products}

        lines = self.pricing_service.build_order_lines(
            products_by_id=products_by_id,
            requested_items=command.items,
        )

        order = Order.create(
            customer_id=command.customer_id,
            lines=lines,
        )

        payment_id = self.payment_gateway.prepare_payment(order)
        order.payment_id = payment_id

        self.order_repository.save(order)

        return order
```

**Django Ninja API**

```python
# orders/api/schemas.py
from decimal import Decimal
from uuid import UUID
from ninja import Schema


class CreateOrderItemIn(Schema):
    product_id: UUID
    quantity: int


class CreateOrderIn(Schema):
    customer_id: UUID
    items: list[CreateOrderItemIn]


class CreateOrderOut(Schema):
    order_id: UUID
    status: str
    total_amount: Decimal
    currency: str
    payment_id: str
```

```python
# orders/api/views.py
from ninja import Router
from orders.application.commands import CreateOrderCommand, CreateOrderItemCommand
from orders.application.services import CreateOrderService
from orders.domain.exceptions import InsufficientStockError

router = Router(tags=["orders"])


@router.post("/", response={201: CreateOrderOut, 400: dict})
def create_order(request, payload: CreateOrderIn):
    service: CreateOrderService = request.app.state.create_order_service

    try:
        order = service.execute(
            CreateOrderCommand(
                customer_id=payload.customer_id,
                items=[
                    CreateOrderItemCommand(
                        product_id=item.product_id,
                        quantity=item.quantity,
                    )
                    for item in payload.items
                ],
            )
        )
    except InsufficientStockError as exc:
        return 400, {"message": str(exc)}

    return 201, CreateOrderOut(
        order_id=order.id,
        status=order.status,
        total_amount=order.total_amount.amount,
        currency=order.total_amount.currency,
        payment_id=order.payment_id,
    )
```

**구현 포인트**

재고 확인은 `select_for_update()` 기반 repository에서 처리하는 게 좋습니다. 주문 생성 중 동시에 같은 상품을 주문해도 재고 검증과 차감이 원자적으로 처리되어야 하기 때문입니다.

결제 준비는 domain이 아니라 application/infrastructure 관심사입니다. domain의 `Order`는 결제 게이트웨이를 몰라야 하고, application service가 `PaymentGateway.prepare_payment(order)`를 호출해 `payment_id` 또는 `payment_session_id`를 주문에 연결합니다.

실서비스라면 다음도 추가하는 게 좋습니다.

```text
- 재고 차감은 결제 준비 전/후 정책 결정 필요
- 결제 실패 시 주문 상태 PAYMENT_FAILED 처리
- 외부 결제 호출은 DB transaction 밖으로 빼고 outbox/saga 적용 검토
- 주문 금액 재계산 방지를 위해 주문 라인에 상품명/단가 스냅샷 저장
- idempotency_key로 중복 주문 생성 방지
```

가장 현실적인 흐름은 `주문 생성 -> 재고 예약 -> 금액 확정 -> 결제 준비 -> PAYMENT_PENDING 주문 저장`입니다. 결제가 완료되면 별도 webhook/API에서 `PAID`로 전이시키는 구조가 DDD와 운영 안정성 측면에서 가장 깔끔합니다.