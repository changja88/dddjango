현재 워크스페이스가 비어 있고 읽기 전용이라 파일 생성은 못 했습니다. 아래는 `orders` 바운디드 컨텍스트 기준으로 바로 적용할 수 있는 DDD + Django Ninja 설계입니다.

**주요 내용**

전략적 경계는 이렇게 잡는 게 좋습니다.

| Context | 책임 | 관계 |
|---|---|---|
| `orders` | 주문 생성, 주문 상태, 주문 금액 불변식 | 핵심/지원 도메인 |
| `catalog` | 상품명, 판매가 조회 | `orders`가 상품 스냅샷만 사용 |
| `inventory` | 재고 예약/차감 | `OrderCreatedEvent` 구독 |
| `payment` | 결제 승인 | 주문 생성 이후 별도 흐름 |

유비쿼터스 언어:

| 용어 | 의미 | 금지 동의어 |
|---|---|---|
| `Order` | 주문 애그리거트 루트 | `Purchase`, `Deal` |
| `OrderLine` | 주문 상품 라인 | `Item`, `ProductRow` |
| `Orderer` | 주문자 식별자 | `User`, `Member` 직접 참조 |
| `ShippingAddress` | 배송지 값 객체 | `AddressDict` |
| `OrderCreatedEvent` | 주문 생성 완료 사실 | `CreateOrderEvent` |

추천 구조:

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

핵심 도메인 모델:

```python
# apps/orders/domain/models.py
from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4

from .events import OrderCreatedEvent
from .exceptions import EmptyOrderError, InvalidMoneyError, InvalidQuantityError


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise InvalidMoneyError("금액은 0 이상이어야 합니다.")


@dataclass(frozen=True)
class OrderLine:
    product_id: UUID
    product_name: str
    unit_price: Money
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise InvalidQuantityError("주문 수량은 1 이상이어야 합니다.")

    @property
    def total_price(self) -> Money:
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
    """Order 애그리거트 루트.

    불변식:
    - 주문은 최소 1개 이상의 OrderLine을 가진다.
    - OrderLine 수량은 1 이상이다.
    - 주문 총액은 모든 OrderLine 합계와 일치한다.
    - 외부 애그리거트는 ID로만 참조한다.
    """

    id: UUID
    orderer_id: UUID
    lines: list[OrderLine]
    shipping_address: ShippingAddress
    _domain_events: list[object] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        orderer_id: UUID,
        lines: list[OrderLine],
        shipping_address: ShippingAddress,
    ) -> "Order":
        if not lines:
            raise EmptyOrderError("최소 1개 이상의 상품을 주문해야 합니다.")

        order = cls(
            id=uuid4(),
            orderer_id=orderer_id,
            lines=lines,
            shipping_address=shipping_address,
        )
        order._record_event(
            OrderCreatedEvent(order_id=order.id, orderer_id=order.orderer_id)
        )
        return order

    @property
    def total_amount(self) -> Money:
        amount = sum((line.total_price.amount for line in self.lines), Decimal("0"))
        return Money(amount)

    def _record_event(self, event: object) -> None:
        self._domain_events.append(event)

    def collect_events(self) -> list[object]:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events
```

```python
# apps/orders/domain/events.py
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class OrderCreatedEvent:
    order_id: UUID
    orderer_id: UUID
    occurred_at: datetime = field(default_factory=datetime.now)
```

```python
# apps/orders/domain/repositories.py
from abc import ABC, abstractmethod
from uuid import UUID

from .models import Order


class OrderRepository(ABC):
    @abstractmethod
    def find_by_id(self, order_id: UUID) -> Order | None:
        ...

    @abstractmethod
    def save(self, order: Order, *, idempotency_key: str | None = None) -> None:
        ...

    @abstractmethod
    def find_by_idempotency_key(self, key: str) -> Order | None:
        ...
```

응용 서비스는 유스케이스만 조율합니다.

```python
# apps/orders/application/services.py
from django.db import transaction

from apps.orders.domain.models import Money, Order, OrderLine, ShippingAddress
from apps.orders.domain.repositories import OrderRepository

from .commands import CreateOrderCommand


class CreateOrderService:
    def __init__(self, orders: OrderRepository) -> None:
        self.orders = orders

    @transaction.atomic
    def create(self, command: CreateOrderCommand) -> Order:
        if command.idempotency_key:
            existing = self.orders.find_by_idempotency_key(command.idempotency_key)
            if existing:
                return existing

        order = Order.create(
            orderer_id=command.orderer_id,
            lines=[
                OrderLine(
                    product_id=item.product_id,
                    product_name=item.product_name,
                    unit_price=Money(item.unit_price),
                    quantity=item.quantity,
                )
                for item in command.items
            ],
            shipping_address=ShippingAddress(**command.shipping_address),
        )
        self.orders.save(order, idempotency_key=command.idempotency_key)

        events = order.collect_events()
        transaction.on_commit(lambda: publish_order_events(events))
        return order
```

Django Ninja API는 표현 계층에만 둡니다.

```python
# apps/orders/api/router.py
from uuid import UUID

from ninja import Header, Router
from ninja.security import django_auth

from apps.orders.application.commands import CreateOrderCommand, CreateOrderItem
from apps.orders.application.services import CreateOrderService
from apps.orders.infrastructure.repositories import DjangoOrderRepository

from .schemas import CreateOrderIn, OrderCreatedOut, ProblemDetails

router = Router(tags=["orders"], auth=django_auth)


@router.post(
    "/",
    response={201: OrderCreatedOut, 409: ProblemDetails, 422: ProblemDetails},
)
def create_order(
    request,
    payload: CreateOrderIn,
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
) -> tuple[int, OrderCreatedOut]:
    service = CreateOrderService(DjangoOrderRepository())
    order = service.create(
        CreateOrderCommand(
            orderer_id=UUID(str(request.user.id)),
            items=[CreateOrderItem(**item.model_dump()) for item in payload.items],
            shipping_address=payload.shipping_address.model_dump(),
            idempotency_key=idempotency_key,
        )
    )
    return 201, OrderCreatedOut(
        id=order.id,
        total_amount=order.total_amount.amount,
        currency=order.total_amount.currency,
    )
```

```python
# apps/orders/api/schemas.py
from decimal import Decimal
from uuid import UUID

from ninja import Schema


class CreateOrderItemIn(Schema):
    product_id: UUID
    product_name: str
    unit_price: Decimal
    quantity: int


class ShippingAddressIn(Schema):
    receiver_name: str
    receiver_phone: str
    postal_code: str
    address1: str
    address2: str = ""


class CreateOrderIn(Schema):
    items: list[CreateOrderItemIn]
    shipping_address: ShippingAddressIn


class OrderCreatedOut(Schema):
    id: UUID
    total_amount: Decimal
    currency: str


class ProblemDetails(Schema):
    type: str
    title: str
    status: int
    detail: str
    instance: str | None = None
```

라우터 합성:

```python
# config/api.py
from ninja import NinjaAPI

from apps.orders.api.router import router as orders_router

api = NinjaAPI(title="Commerce API", version="1.0.0")
api.add_router("/orders/", orders_router)
```

```python
# config/urls.py
from django.urls import path

from .api import api

urlpatterns = [
    path("api/", api.urls),
]
```

API 계약은 `POST /api/orders/`가 맞습니다. URL에 `create-order` 같은 동사를 넣지 않고, 성공은 `201 Created`, 입력 검증은 `422`, 중복 멱등성 충돌은 상황에 따라 `409`를 사용합니다. 중요한 주문 생성 POST라서 `Idempotency-Key` 헤더를 받도록 설계했습니다.

---
> **관련 스킬 참조:**
> - DB 모델/인덱스/마이그레이션 설계 → **architecture-db** 스킬
> - Django ORM 리포지토리 구현 → **implementation-django** 스킬
> - Django Ninja 에러 핸들러/테스트 작성 → **implementation-django-ninja** 스킬