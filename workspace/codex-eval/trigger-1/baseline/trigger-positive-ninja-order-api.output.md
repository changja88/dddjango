**주요 내용**

현재 `/private/tmp/dddjango-codex-eval`은 비어 있고 읽기 전용이라 파일 생성/실행은 못 했습니다. 아래는 Django Ninja + DDD 기준으로 바로 옮길 수 있는 주문 생성 API 설계입니다.

**전략적 설계**

| 항목 | 설계 |
|---|---|
| Bounded Context | `orders` 주문 컨텍스트 |
| Aggregate Root | `Order` |
| Value Objects | `Money`, `OrderLine`, `ShippingAddress` |
| 외부 Aggregate 참조 | `customer_id`, `product_id`처럼 ID로만 참조 |
| 주요 불변식 | 주문 라인은 1개 이상, 수량은 1 이상, 금액은 음수 불가 |
| Domain Event | `OrderCreatedEvent` |
| API Resource | `POST /api/v1/orders` |
| 성공 상태 | `201 Created` |
| 오류 형식 | RFC 9457 Problem Details |

금지 동의어:

| 유비쿼터스 언어 | 사용 | 금지 |
|---|---|---|
| Order | 주문 Aggregate | Purchase, Transaction |
| OrderLine | 주문 상품 라인 | Item, CartItem |
| place/create order | 주문 생성 | insert order |
| ShippingAddress | 배송지 | AddressInfo |

**권장 구조**

```text
apps/orders/
  domain/
    models.py
    events.py
    exceptions.py
    repositories.py
  application/
    commands.py
    services.py
  infrastructure/
    models.py
    repositories.py
  api/
    schemas.py
    router.py
config/
  api.py
  urls.py
```

**도메인 계층**

```python
# apps/orders/domain/models.py
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from .events import DomainEvent, OrderCreatedEvent
from .exceptions import InvalidOrderError


@dataclass(frozen=True)
class Money:
    amount: int
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise InvalidOrderError("금액은 음수일 수 없습니다.")


@dataclass(frozen=True)
class OrderLine:
    product_id: str
    product_name: str
    unit_price: Money
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity < 1:
            raise InvalidOrderError("주문 수량은 1 이상이어야 합니다.")

    @property
    def subtotal(self) -> Money:
        return Money(self.unit_price.amount * self.quantity, self.unit_price.currency)


@dataclass(frozen=True)
class ShippingAddress:
    receiver_name: str
    receiver_phone: str
    postal_code: str
    address1: str
    address2: str = ""


@dataclass
class Order:
    """Aggregate Root.

    불변식:
    - 주문은 최소 하나 이상의 OrderLine을 가진다.
    - OrderLine, ShippingAddress 변경은 Order를 통해서만 수행한다.
    - Customer/Product는 객체 참조가 아니라 ID로만 참조한다.
    """

    id: str
    customer_id: str
    lines: list[OrderLine]
    shipping_address: ShippingAddress
    created_at: datetime
    _domain_events: list[DomainEvent] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        customer_id: str,
        lines: list[OrderLine],
        shipping_address: ShippingAddress,
    ) -> "Order":
        if not lines:
            raise InvalidOrderError("최소 한 개 이상의 상품을 주문해야 합니다.")

        order = cls(
            id=str(uuid4()),
            customer_id=customer_id,
            lines=lines,
            shipping_address=shipping_address,
            created_at=datetime.now(),
        )
        order._record_event(
            OrderCreatedEvent(
                order_id=order.id,
                customer_id=customer_id,
                total_amount=order.total_amount.amount,
            )
        )
        return order

    @property
    def total_amount(self) -> Money:
        return Money(sum(line.subtotal.amount for line in self.lines))

    def _record_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def collect_events(self) -> list[DomainEvent]:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events
```

```python
# apps/orders/domain/events.py
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class OrderCreatedEvent(DomainEvent):
    order_id: str = ""
    customer_id: str = ""
    total_amount: int = 0
```

```python
# apps/orders/domain/repositories.py
from abc import ABC, abstractmethod

from .models import Order


class OrderRepository(ABC):
    @abstractmethod
    def find_by_id(self, order_id: str) -> Order | None:
        ...

    @abstractmethod
    def save(self, order: Order) -> None:
        ...
```

```python
# apps/orders/domain/exceptions.py
class OrderDomainError(Exception):
    pass


class InvalidOrderError(OrderDomainError):
    pass
```

**응용 서비스**

```python
# apps/orders/application/commands.py
from dataclasses import dataclass


@dataclass(frozen=True)
class CreateOrderLineCommand:
    product_id: str
    product_name: str
    unit_price: int
    quantity: int


@dataclass(frozen=True)
class CreateShippingAddressCommand:
    receiver_name: str
    receiver_phone: str
    postal_code: str
    address1: str
    address2: str = ""


@dataclass(frozen=True)
class CreateOrderCommand:
    customer_id: str
    lines: list[CreateOrderLineCommand]
    shipping_address: CreateShippingAddressCommand
```

```python
# apps/orders/application/services.py
from django.db import transaction

from apps.orders.domain.models import Money, Order, OrderLine, ShippingAddress
from apps.orders.domain.repositories import OrderRepository

from .commands import CreateOrderCommand


class OrderApplicationService:
    def __init__(self, order_repository: OrderRepository) -> None:
        self._order_repository = order_repository

    @transaction.atomic
    def create_order(self, command: CreateOrderCommand) -> Order:
        order = Order.create(
            customer_id=command.customer_id,
            lines=[
                OrderLine(
                    product_id=line.product_id,
                    product_name=line.product_name,
                    unit_price=Money(line.unit_price),
                    quantity=line.quantity,
                )
                for line in command.lines
            ],
            shipping_address=ShippingAddress(**command.shipping_address.__dict__),
        )

        self._order_repository.save(order)

        events = order.collect_events()
        transaction.on_commit(lambda: self._publish_events(events))

        return order

    def _publish_events(self, events: list[object]) -> None:
        # Outbox 또는 event bus 연동 지점
        pass
```

**Django Ninja API**

```python
# apps/orders/api/schemas.py
from datetime import datetime

from ninja import Schema


class OrderLineIn(Schema):
    product_id: str
    product_name: str
    unit_price: int
    quantity: int


class ShippingAddressIn(Schema):
    receiver_name: str
    receiver_phone: str
    postal_code: str
    address1: str
    address2: str = ""


class CreateOrderIn(Schema):
    customer_id: str
    lines: list[OrderLineIn]
    shipping_address: ShippingAddressIn


class OrderLineOut(Schema):
    product_id: str
    product_name: str
    unit_price: int
    quantity: int
    subtotal: int


class OrderOut(Schema):
    id: str
    customer_id: str
    lines: list[OrderLineOut]
    total_amount: int
    created_at: datetime
```

```python
# apps/orders/api/router.py
from ninja import Router

from apps.orders.application.commands import (
    CreateOrderCommand,
    CreateOrderLineCommand,
    CreateShippingAddressCommand,
)
from apps.orders.application.services import OrderApplicationService
from apps.orders.domain.exceptions import OrderDomainError
from apps.orders.infrastructure.repositories import DjangoOrderRepository

from .schemas import CreateOrderIn, OrderOut

router = Router(tags=["orders"])


@router.post("", response={201: OrderOut})
def create_order(request, payload: CreateOrderIn) -> tuple[int, dict]:
    service = OrderApplicationService(DjangoOrderRepository())
    order = service.create_order(
        CreateOrderCommand(
            customer_id=payload.customer_id,
            lines=[
                CreateOrderLineCommand(
                    product_id=line.product_id,
                    product_name=line.product_name,
                    unit_price=line.unit_price,
                    quantity=line.quantity,
                )
                for line in payload.lines
            ],
            shipping_address=CreateShippingAddressCommand(
                **payload.shipping_address.dict()
            ),
        )
    )

    return 201, {
        "id": order.id,
        "customer_id": order.customer_id,
        "lines": [
            {
                "product_id": line.product_id,
                "product_name": line.product_name,
                "unit_price": line.unit_price.amount,
                "quantity": line.quantity,
                "subtotal": line.subtotal.amount,
            }
            for line in order.lines
        ],
        "total_amount": order.total_amount.amount,
        "created_at": order.created_at,
    }
```

```python
# config/api.py
from ninja import NinjaAPI
from ninja.errors import ValidationError

from apps.orders.api.router import router as orders_router
from apps.orders.domain.exceptions import OrderDomainError

api = NinjaAPI(version="1.0.0")
api.add_router("/v1/orders", orders_router)


@api.exception_handler(OrderDomainError)
def order_domain_error_handler(request, exc: OrderDomainError):
    return api.create_response(
        request,
        {
            "type": "https://example.com/problems/invalid-order",
            "title": "Invalid order",
            "status": 422,
            "detail": str(exc),
            "instance": request.path,
        },
        status=422,
    )


@api.exception_handler(ValidationError)
def validation_error_handler(request, exc: ValidationError):
    return api.create_response(
        request,
        {
            "type": "https://example.com/problems/validation-error",
            "title": "Validation error",
            "status": 422,
            "detail": "요청 본문을 처리할 수 없습니다.",
            "instance": request.path,
            "errors": exc.errors,
        },
        status=422,
    )
```

```python
# config/urls.py
from django.urls import path

from .api import api

urlpatterns = [
    path("api/", api.urls),
]
```

핵심 포인트는 API 라우터가 주문 생성 유스케이스만 호출하고, 비즈니스 규칙은 `Order.create()`와 값 객체에 둔다는 점입니다. Django ORM 모델은 `infrastructure`에 두고, 도메인 모델이 Django를 import하지 않게 유지하는 구조가 DDD 경계를 가장 깔끔하게 지킵니다.

검증은 실행하지 못했습니다. 현재 워크스페이스가 비어 있고 read-only입니다.

---
> **관련 스킬 참조:**
> - DB 모델/마이그레이션 설계 → **architecture-db** 스킬
> - Django ORM 리포지토리 구현 → **implementation-django** 스킬
> - API 테스트 작성 → **implementation-test** 스킬