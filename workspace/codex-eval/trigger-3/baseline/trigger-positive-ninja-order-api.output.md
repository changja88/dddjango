현재 `/private/tmp/dddjango-codex-eval` 디렉터리는 비어 있고 `config.toml`도 없어 실제 파일 수정은 못 했습니다. 대신 Django Ninja 기반 주문 생성 API를 DDD 구조로 설계하면 아래처럼 잡는 게 적절합니다.

**권장 구조**

```text
orders/
  domain/
    entities.py
    value_objects.py
    repositories.py
    services.py
    exceptions.py
  application/
    commands.py
    use_cases.py
    ports.py
  infrastructure/
    django_models.py
    repositories.py
  api/
    schemas.py
    router.py
```

**도메인 계층**

```python
# orders/domain/value_objects.py
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "KRW"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("금액은 음수일 수 없습니다.")


@dataclass(frozen=True)
class OrderItem:
    product_id: int
    quantity: int
    unit_price: Money

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("수량은 1개 이상이어야 합니다.")

    @property
    def total_price(self) -> Money:
        return Money(self.unit_price.amount * self.quantity, self.unit_price.currency)
```

```python
# orders/domain/entities.py
from dataclasses import dataclass, field
from decimal import Decimal
from .value_objects import Money, OrderItem


@dataclass
class Order:
    customer_id: int
    items: list[OrderItem]
    id: int | None = None
    status: str = "CREATED"

    def __post_init__(self):
        if not self.items:
            raise ValueError("주문 항목이 필요합니다.")

    @property
    def total_price(self) -> Money:
        total = sum((item.total_price.amount for item in self.items), Decimal("0"))
        return Money(total)
```

```python
# orders/domain/repositories.py
from typing import Protocol
from .entities import Order


class OrderRepository(Protocol):
    def save(self, order: Order) -> Order:
        ...
```

**애플리케이션 계층**

```python
# orders/application/commands.py
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class CreateOrderItemCommand:
    product_id: int
    quantity: int
    unit_price: Decimal


@dataclass(frozen=True)
class CreateOrderCommand:
    customer_id: int
    items: list[CreateOrderItemCommand]
```

```python
# orders/application/use_cases.py
from orders.domain.entities import Order
from orders.domain.value_objects import Money, OrderItem
from orders.domain.repositories import OrderRepository
from .commands import CreateOrderCommand


class CreateOrderUseCase:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    def execute(self, command: CreateOrderCommand) -> Order:
        order = Order(
            customer_id=command.customer_id,
            items=[
                OrderItem(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=Money(item.unit_price),
                )
                for item in command.items
            ],
        )

        return self.order_repository.save(order)
```

**인프라 계층**

```python
# orders/infrastructure/django_models.py
from django.db import models


class OrderModel(models.Model):
    customer_id = models.BigIntegerField()
    status = models.CharField(max_length=30)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItemModel(models.Model):
    order = models.ForeignKey(OrderModel, related_name="items", on_delete=models.CASCADE)
    product_id = models.BigIntegerField()
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
```

```python
# orders/infrastructure/repositories.py
from django.db import transaction
from orders.domain.entities import Order
from orders.infrastructure.django_models import OrderModel, OrderItemModel


class DjangoOrderRepository:
    @transaction.atomic
    def save(self, order: Order) -> Order:
        order_model = OrderModel.objects.create(
            customer_id=order.customer_id,
            status=order.status,
            total_price=order.total_price.amount,
        )

        OrderItemModel.objects.bulk_create([
            OrderItemModel(
                order=order_model,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price.amount,
            )
            for item in order.items
        ])

        order.id = order_model.id
        return order
```

**Django Ninja API 계층**

```python
# orders/api/schemas.py
from decimal import Decimal
from ninja import Schema


class CreateOrderItemIn(Schema):
    product_id: int
    quantity: int
    unit_price: Decimal


class CreateOrderIn(Schema):
    customer_id: int
    items: list[CreateOrderItemIn]


class OrderOut(Schema):
    id: int
    customer_id: int
    status: str
    total_price: Decimal
```

```python
# orders/api/router.py
from ninja import Router
from orders.application.commands import CreateOrderCommand, CreateOrderItemCommand
from orders.application.use_cases import CreateOrderUseCase
from orders.infrastructure.repositories import DjangoOrderRepository
from .schemas import CreateOrderIn, OrderOut

router = Router(tags=["orders"])


@router.post("/", response={201: OrderOut})
def create_order(request, payload: CreateOrderIn):
    use_case = CreateOrderUseCase(order_repository=DjangoOrderRepository())

    order = use_case.execute(
        CreateOrderCommand(
            customer_id=payload.customer_id,
            items=[
                CreateOrderItemCommand(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
                for item in payload.items
            ],
        )
    )

    return 201, OrderOut(
        id=order.id,
        customer_id=order.customer_id,
        status=order.status,
        total_price=order.total_price.amount,
    )
```

핵심은 API가 ORM 모델을 직접 만들지 않고, `CreateOrderUseCase`를 호출한다는 점입니다. 주문 생성 규칙은 `domain`에 두고, 트랜잭션과 Django ORM 저장은 `infrastructure`가 담당하게 분리합니다.