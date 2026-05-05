현재 `/private/tmp/dddjango-codex-eval` 디렉터리는 비어 있고, 세션 권한이 `read-only`라 파일 생성은 할 수 없습니다. 대신 바로 구현 가능한 DDD 기준 설계를 제안합니다.

**구조**

```text
orders/
  api.py                  # Django Ninja HTTP 진입점
  schemas.py              # 요청/응답 DTO
  application/
    create_order.py       # 주문 생성 유스케이스
    ports.py              # Repository, PaymentGateway 인터페이스
  domain/
    models.py             # Order, OrderLine, Money
    services.py           # 재고 확인, 금액 계산 도메인 서비스
    exceptions.py
  infrastructure/
    django_models.py      # Django ORM 모델
    repositories.py       # ORM 구현체
    payment_gateway.py    # 결제 준비 구현체
```

**핵심 흐름**

1. API는 요청 검증만 한다.
2. Application Service가 트랜잭션을 잡고 유스케이스를 조율한다.
3. Domain은 주문 금액 계산과 재고 규칙을 책임진다.
4. Infrastructure는 DB 조회/저장, 외부 결제 API 호출을 담당한다.

예시 코드:

```python
# orders/domain/models.py
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    amount: Decimal

    def __add__(self, other: "Money") -> "Money":
        return Money(self.amount + other.amount)


@dataclass(frozen=True)
class OrderLine:
    product_id: int
    product_name: str
    unit_price: Money
    quantity: int

    def subtotal(self) -> Money:
        return Money(self.unit_price.amount * self.quantity)


@dataclass
class Order:
    user_id: int
    lines: list[OrderLine]
    total_amount: Money
    payment_id: str | None = None

    @classmethod
    def create(cls, user_id: int, lines: list[OrderLine]) -> "Order":
        total = Money(sum((line.subtotal().amount for line in lines), Decimal("0")))
        return cls(user_id=user_id, lines=lines, total_amount=total)
```

```python
# orders/application/ports.py
from typing import Protocol
from orders.domain.models import Order


class ProductRepository(Protocol):
    def get_orderable_products(self, product_ids: list[int]) -> list:
        ...


class OrderRepository(Protocol):
    def save(self, order: Order) -> Order:
        ...


class PaymentGateway(Protocol):
    def prepare_payment(self, order: Order) -> str:
        ...
```

```python
# orders/application/create_order.py
from dataclasses import dataclass
from django.db import transaction

from orders.domain.models import OrderLine, Money, Order
from orders.domain.exceptions import OutOfStockError, ProductNotFoundError


@dataclass(frozen=True)
class CreateOrderItemCommand:
    product_id: int
    quantity: int


@dataclass(frozen=True)
class CreateOrderCommand:
    user_id: int
    items: list[CreateOrderItemCommand]


class CreateOrderUseCase:
    def __init__(self, product_repository, order_repository, payment_gateway):
        self.product_repository = product_repository
        self.order_repository = order_repository
        self.payment_gateway = payment_gateway

    @transaction.atomic
    def execute(self, command: CreateOrderCommand) -> Order:
        product_ids = [item.product_id for item in command.items]
        products = self.product_repository.get_orderable_products(product_ids)
        product_map = {product.id: product for product in products}

        lines = []

        for item in command.items:
            product = product_map.get(item.product_id)
            if product is None:
                raise ProductNotFoundError(item.product_id)

            if product.stock_quantity < item.quantity:
                raise OutOfStockError(product.id)

            lines.append(
                OrderLine(
                    product_id=product.id,
                    product_name=product.name,
                    unit_price=Money(product.price),
                    quantity=item.quantity,
                )
            )

        order = Order.create(user_id=command.user_id, lines=lines)
        order.payment_id = self.payment_gateway.prepare_payment(order)

        return self.order_repository.save(order)
```

```python
# orders/api.py
from ninja import Router
from orders.schemas import CreateOrderRequest, CreateOrderResponse
from orders.application.create_order import (
    CreateOrderCommand,
    CreateOrderItemCommand,
    CreateOrderUseCase,
)
from orders.infrastructure.repositories import DjangoProductRepository, DjangoOrderRepository
from orders.infrastructure.payment_gateway import PaymentGatewayClient

router = Router(tags=["orders"])


@router.post("", response={201: CreateOrderResponse})
def create_order(request, payload: CreateOrderRequest):
    use_case = CreateOrderUseCase(
        product_repository=DjangoProductRepository(),
        order_repository=DjangoOrderRepository(),
        payment_gateway=PaymentGatewayClient(),
    )

    order = use_case.execute(
        CreateOrderCommand(
            user_id=request.user.id,
            items=[
                CreateOrderItemCommand(
                    product_id=item.product_id,
                    quantity=item.quantity,
                )
                for item in payload.items
            ],
        )
    )

    return 201, CreateOrderResponse(
        order_id=order.id,
        total_amount=order.total_amount.amount,
        payment_id=order.payment_id,
    )
```

```python
# orders/schemas.py
from decimal import Decimal
from ninja import Schema


class CreateOrderItemRequest(Schema):
    product_id: int
    quantity: int


class CreateOrderRequest(Schema):
    items: list[CreateOrderItemRequest]


class CreateOrderResponse(Schema):
    order_id: int
    total_amount: Decimal
    payment_id: str
```

중요한 설계 포인트는 `api.py`가 재고 확인, 금액 계산, 결제 준비 규칙을 직접 알지 않게 하는 것입니다. API는 DTO 변환만 하고, 주문 생성의 실제 흐름은 `CreateOrderUseCase`가 담당합니다. 금액 계산은 `Order`와 `OrderLine` 안에 두어 도메인 규칙이 흩어지지 않게 합니다.

파일 쓰기 권한이 열리면 이 구조로 Django 앱과 테스트까지 바로 스캐폴딩할 수 있습니다.