# Django 프로젝트에서 헥사고날 아키텍처 도입 가이드

## 1. 핵심 개념 요약

헥사고날 아키텍처(Ports & Adapters)의 목표는 **비즈니스 로직을 프레임워크(Django)로부터 격리**하는 것이다. 세 가지 영역으로 나뉜다.

| 영역 | 역할 | Django에서의 위치 |
|------|------|-------------------|
| **Domain (코어)** | 비즈니스 규칙, 엔티티 | 순수 Python 클래스 |
| **Ports (인터페이스)** | 코어가 외부와 소통하는 계약 | ABC / Protocol 클래스 |
| **Adapters (구현체)** | 포트의 실제 구현 | Django ORM, View, Serializer 등 |

의존성 방향은 항상 **바깥(Adapter) -> 안쪽(Domain)**으로만 향한다. Domain은 Django를 import하지 않는다.

---

## 2. 프로젝트 디렉터리 구조

```
myproject/
├── manage.py
├── config/                     # Django 설정
│   ├── settings.py
│   ├── urls.py
│   └── di.py                   # 의존성 주입 컨테이너
│
├── order/                      # 바운디드 컨텍스트 (Django app)
│   ├── domain/                 # --- 코어 (순수 Python) ---
│   │   ├── entities.py         # 도메인 엔티티
│   │   ├── value_objects.py    # 값 객체
│   │   ├── exceptions.py       # 도메인 예외
│   │   └── services.py         # 도메인 서비스
│   │
│   ├── ports/                  # --- 포트 (인터페이스) ---
│   │   ├── inbound.py          # Driving ports (Use Case 인터페이스)
│   │   └── outbound.py         # Driven ports (Repository 등 인터페이스)
│   │
│   ├── application/            # --- 유스케이스 구현 ---
│   │   └── use_cases.py        # 포트를 구현하는 애플리케이션 서비스
│   │
│   ├── adapters/               # --- 어댑터 (Django 의존) ---
│   │   ├── inbound/
│   │   │   ├── views.py        # Django View / DRF ViewSet
│   │   │   ├── serializers.py  # DRF Serializer
│   │   │   └── urls.py
│   │   └── outbound/
│   │       ├── repositories.py # Django ORM Repository 구현
│   │       ├── models.py       # Django Model (DB 스키마)
│   │       └── external_api.py # 외부 API 클라이언트
│   │
│   └── apps.py
```

핵심 원칙: `domain/`과 `ports/` 디렉터리에는 Django import가 단 하나도 없어야 한다.

---

## 3. 단계별 구현

### 3.1 도메인 엔티티 (순수 Python)

```python
# order/domain/entities.py
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from order.domain.exceptions import InvalidOrderError


class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


@dataclass
class OrderItem:
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: int

    @property
    def subtotal(self) -> int:
        return self.quantity * self.unit_price


@dataclass
class Order:
    """도메인 엔티티 - Django Model이 아닌 순수 Python 클래스."""

    id: UUID = field(default_factory=uuid4)
    customer_id: UUID = field(default=None)
    items: list[OrderItem] = field(default_factory=list)
    status: OrderStatus = field(default=OrderStatus.PENDING)
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def total_amount(self) -> int:
        return sum(item.subtotal for item in self.items)

    def confirm(self) -> None:
        if self.status != OrderStatus.PENDING:
            raise InvalidOrderError(
                f"PENDING 상태에서만 확정 가능. 현재: {self.status.value}"
            )
        if not self.items:
            raise InvalidOrderError("주문 항목이 비어있습니다.")
        self.status = OrderStatus.CONFIRMED

    def cancel(self) -> None:
        if self.status in (OrderStatus.SHIPPED, OrderStatus.CANCELLED):
            raise InvalidOrderError(
                f"취소 불가능한 상태: {self.status.value}"
            )
        self.status = OrderStatus.CANCELLED
```

```python
# order/domain/exceptions.py
class InvalidOrderError(Exception):
    pass

class OrderNotFoundError(Exception):
    pass
```

### 3.2 포트 정의 (인터페이스)

```python
# order/ports/inbound.py
"""Driving Ports - 외부(View)가 코어를 호출할 때 사용하는 인터페이스."""
from abc import ABC, abstractmethod
from uuid import UUID

from order.domain.entities import Order


class PlaceOrderUseCase(ABC):
    @abstractmethod
    def execute(self, customer_id: UUID, items: list[dict]) -> Order:
        ...


class ConfirmOrderUseCase(ABC):
    @abstractmethod
    def execute(self, order_id: UUID) -> Order:
        ...


class CancelOrderUseCase(ABC):
    @abstractmethod
    def execute(self, order_id: UUID) -> Order:
        ...
```

```python
# order/ports/outbound.py
"""Driven Ports - 코어가 외부 인프라를 사용할 때의 인터페이스."""
from abc import ABC, abstractmethod
from uuid import UUID

from order.domain.entities import Order


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None:
        ...

    @abstractmethod
    def find_by_id(self, order_id: UUID) -> Order | None:
        ...

    @abstractmethod
    def find_by_customer(self, customer_id: UUID) -> list[Order]:
        ...


class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, order_id: UUID, amount: int) -> bool:
        ...


class NotificationService(ABC):
    @abstractmethod
    def send_order_confirmation(self, order: Order) -> None:
        ...
```

### 3.3 애플리케이션 서비스 (유스케이스 구현)

```python
# order/application/use_cases.py
from uuid import UUID, uuid4

from order.domain.entities import Order, OrderItem
from order.domain.exceptions import OrderNotFoundError
from order.ports.inbound import (
    CancelOrderUseCase,
    ConfirmOrderUseCase,
    PlaceOrderUseCase,
)
from order.ports.outbound import (
    NotificationService,
    OrderRepository,
    PaymentGateway,
)


class PlaceOrderService(PlaceOrderUseCase):
    """유스케이스 구현. Outbound 포트를 생성자 주입으로 받는다."""

    def __init__(self, order_repo: OrderRepository):
        self._order_repo = order_repo

    def execute(self, customer_id: UUID, items: list[dict]) -> Order:
        order_items = [
            OrderItem(
                product_id=item["product_id"],
                product_name=item["product_name"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
            )
            for item in items
        ]
        order = Order(customer_id=customer_id, items=order_items)
        self._order_repo.save(order)
        return order


class ConfirmOrderService(ConfirmOrderUseCase):
    def __init__(
        self,
        order_repo: OrderRepository,
        payment_gateway: PaymentGateway,
        notification: NotificationService,
    ):
        self._order_repo = order_repo
        self._payment = payment_gateway
        self._notification = notification

    def execute(self, order_id: UUID) -> Order:
        order = self._order_repo.find_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(f"주문을 찾을 수 없음: {order_id}")

        order.confirm()  # 도메인 규칙 실행

        charged = self._payment.charge(order.id, order.total_amount)
        if not charged:
            raise InvalidOrderError("결제 실패")

        self._order_repo.save(order)
        self._notification.send_order_confirmation(order)
        return order


class CancelOrderService(CancelOrderUseCase):
    def __init__(self, order_repo: OrderRepository):
        self._order_repo = order_repo

    def execute(self, order_id: UUID) -> Order:
        order = self._order_repo.find_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(f"주문을 찾을 수 없음: {order_id}")

        order.cancel()  # 도메인 규칙 실행
        self._order_repo.save(order)
        return order
```

### 3.4 Outbound 어댑터 (Django ORM Repository)

```python
# order/adapters/outbound/models.py
"""Django Model - DB 스키마 정의만 담당."""
import uuid
from django.db import models


class OrderModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    customer_id = models.UUIDField(db_index=True)
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "orders"


class OrderItemModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    order = models.ForeignKey(
        OrderModel, on_delete=models.CASCADE, related_name="items"
    )
    product_id = models.UUIDField()
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    unit_price = models.PositiveIntegerField()

    class Meta:
        db_table = "order_items"
```

```python
# order/adapters/outbound/repositories.py
"""Outbound 어댑터 - Django ORM으로 OrderRepository 포트를 구현."""
from uuid import UUID

from order.adapters.outbound.models import OrderItemModel, OrderModel
from order.domain.entities import Order, OrderItem, OrderStatus
from order.ports.outbound import OrderRepository


class DjangoOrderRepository(OrderRepository):
    """Django ORM <-> 도메인 엔티티 변환을 담당하는 어댑터."""

    def save(self, order: Order) -> None:
        model, _ = OrderModel.objects.update_or_create(
            id=order.id,
            defaults={
                "customer_id": order.customer_id,
                "status": order.status.value,
            },
        )
        # 기존 항목 삭제 후 재생성 (간단한 전략)
        OrderItemModel.objects.filter(order=model).delete()
        OrderItemModel.objects.bulk_create([
            OrderItemModel(
                order=model,
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in order.items
        ])

    def find_by_id(self, order_id: UUID) -> Order | None:
        try:
            model = OrderModel.objects.prefetch_related("items").get(
                id=order_id
            )
        except OrderModel.DoesNotExist:
            return None
        return self._to_entity(model)

    def find_by_customer(self, customer_id: UUID) -> list[Order]:
        models = OrderModel.objects.prefetch_related("items").filter(
            customer_id=customer_id
        )
        return [self._to_entity(m) for m in models]

    @staticmethod
    def _to_entity(model: OrderModel) -> Order:
        """Django Model -> 도메인 엔티티 변환."""
        items = [
            OrderItem(
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in model.items.all()
        ]
        return Order(
            id=model.id,
            customer_id=model.customer_id,
            items=items,
            status=OrderStatus(model.status),
            created_at=model.created_at,
        )
```

### 3.5 Inbound 어댑터 (Django View)

```python
# order/adapters/inbound/views.py
"""Inbound 어댑터 - HTTP 요청을 유스케이스 호출로 변환."""
from uuid import UUID

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from order.domain.exceptions import InvalidOrderError, OrderNotFoundError
from order.ports.inbound import (
    CancelOrderUseCase,
    ConfirmOrderUseCase,
    PlaceOrderUseCase,
)


class PlaceOrderView(APIView):
    """View는 포트(인터페이스)에만 의존한다. 구현체를 모른다."""

    def __init__(self, use_case: PlaceOrderUseCase, **kwargs):
        super().__init__(**kwargs)
        self._use_case = use_case

    def post(self, request: Request) -> Response:
        order = self._use_case.execute(
            customer_id=UUID(request.data["customer_id"]),
            items=request.data["items"],
        )
        return Response(
            {"order_id": str(order.id), "total": order.total_amount},
            status=status.HTTP_201_CREATED,
        )


class ConfirmOrderView(APIView):
    def __init__(self, use_case: ConfirmOrderUseCase, **kwargs):
        super().__init__(**kwargs)
        self._use_case = use_case

    def post(self, request: Request, order_id: str) -> Response:
        try:
            order = self._use_case.execute(UUID(order_id))
        except OrderNotFoundError:
            return Response(
                {"error": "주문을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except InvalidOrderError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        return Response({"order_id": str(order.id), "status": order.status.value})


class CancelOrderView(APIView):
    def __init__(self, use_case: CancelOrderUseCase, **kwargs):
        super().__init__(**kwargs)
        self._use_case = use_case

    def post(self, request: Request, order_id: str) -> Response:
        try:
            order = self._use_case.execute(UUID(order_id))
        except OrderNotFoundError:
            return Response(
                {"error": "주문을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except InvalidOrderError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        return Response({"order_id": str(order.id), "status": order.status.value})
```

### 3.6 의존성 주입 (Composition Root)

```python
# config/di.py
"""
Composition Root - 모든 의존성을 한 곳에서 조립한다.
프로덕션 구현체를 연결하는 유일한 장소.
"""
from order.adapters.outbound.repositories import DjangoOrderRepository
from order.adapters.outbound.external_api import StripePaymentGateway
from order.adapters.outbound.external_api import EmailNotificationService
from order.application.use_cases import (
    CancelOrderService,
    ConfirmOrderService,
    PlaceOrderService,
)


def get_order_repository():
    return DjangoOrderRepository()


def get_place_order_use_case():
    return PlaceOrderService(
        order_repo=get_order_repository(),
    )


def get_confirm_order_use_case():
    return ConfirmOrderService(
        order_repo=get_order_repository(),
        payment_gateway=StripePaymentGateway(),
        notification=EmailNotificationService(),
    )


def get_cancel_order_use_case():
    return CancelOrderService(
        order_repo=get_order_repository(),
    )
```

```python
# order/adapters/inbound/urls.py
from django.urls import path

from config.di import (
    get_cancel_order_use_case,
    get_confirm_order_use_case,
    get_place_order_use_case,
)
from order.adapters.inbound.views import (
    CancelOrderView,
    ConfirmOrderView,
    PlaceOrderView,
)

urlpatterns = [
    path(
        "orders/",
        PlaceOrderView.as_view(use_case=get_place_order_use_case()),
    ),
    path(
        "orders/<str:order_id>/confirm/",
        ConfirmOrderView.as_view(use_case=get_confirm_order_use_case()),
    ),
    path(
        "orders/<str:order_id>/cancel/",
        CancelOrderView.as_view(use_case=get_cancel_order_use_case()),
    ),
]
```

---

## 4. 테스트 전략

헥사고날 아키텍처의 최대 이점은 **도메인 로직을 DB 없이 테스트**할 수 있다는 점이다.

### 4.1 도메인 단위 테스트 (Django 불필요)

```python
# tests/unit/test_order_entity.py
import pytest
from order.domain.entities import Order, OrderItem, OrderStatus
from order.domain.exceptions import InvalidOrderError
from uuid import uuid4


class TestOrder:
    def _make_order_with_items(self) -> Order:
        return Order(
            customer_id=uuid4(),
            items=[
                OrderItem(uuid4(), "상품A", quantity=2, unit_price=10000),
                OrderItem(uuid4(), "상품B", quantity=1, unit_price=5000),
            ],
        )

    def test_total_amount(self):
        order = self._make_order_with_items()
        assert order.total_amount == 25000

    def test_confirm_success(self):
        order = self._make_order_with_items()
        order.confirm()
        assert order.status == OrderStatus.CONFIRMED

    def test_confirm_without_items_raises(self):
        order = Order(customer_id=uuid4(), items=[])
        with pytest.raises(InvalidOrderError, match="비어있습니다"):
            order.confirm()

    def test_cancel_after_shipped_raises(self):
        order = self._make_order_with_items()
        order.status = OrderStatus.SHIPPED
        with pytest.raises(InvalidOrderError, match="취소 불가능"):
            order.cancel()
```

### 4.2 유스케이스 테스트 (Fake 어댑터 사용)

```python
# tests/unit/test_use_cases.py
from uuid import UUID, uuid4

from order.application.use_cases import ConfirmOrderService, PlaceOrderService
from order.domain.entities import Order, OrderItem, OrderStatus
from order.ports.outbound import NotificationService, OrderRepository, PaymentGateway


class FakeOrderRepository(OrderRepository):
    """인메모리 구현 - DB 없이 테스트 가능."""

    def __init__(self):
        self._store: dict[UUID, Order] = {}

    def save(self, order: Order) -> None:
        self._store[order.id] = order

    def find_by_id(self, order_id: UUID) -> Order | None:
        return self._store.get(order_id)

    def find_by_customer(self, customer_id: UUID) -> list[Order]:
        return [o for o in self._store.values() if o.customer_id == customer_id]


class FakePaymentGateway(PaymentGateway):
    def __init__(self, should_succeed: bool = True):
        self.should_succeed = should_succeed
        self.charged_orders: list[UUID] = []

    def charge(self, order_id: UUID, amount: int) -> bool:
        self.charged_orders.append(order_id)
        return self.should_succeed


class FakeNotificationService(NotificationService):
    def __init__(self):
        self.sent: list[Order] = []

    def send_order_confirmation(self, order: Order) -> None:
        self.sent.append(order)


class TestPlaceOrder:
    def test_creates_order_and_persists(self):
        repo = FakeOrderRepository()
        use_case = PlaceOrderService(order_repo=repo)

        order = use_case.execute(
            customer_id=uuid4(),
            items=[
                {
                    "product_id": uuid4(),
                    "product_name": "테스트상품",
                    "quantity": 1,
                    "unit_price": 10000,
                }
            ],
        )

        assert repo.find_by_id(order.id) is not None
        assert order.total_amount == 10000


class TestConfirmOrder:
    def test_confirm_charges_and_notifies(self):
        repo = FakeOrderRepository()
        payment = FakePaymentGateway(should_succeed=True)
        notification = FakeNotificationService()

        order = Order(
            customer_id=uuid4(),
            items=[OrderItem(uuid4(), "상품", 1, 5000)],
        )
        repo.save(order)

        use_case = ConfirmOrderService(repo, payment, notification)
        confirmed = use_case.execute(order.id)

        assert confirmed.status == OrderStatus.CONFIRMED
        assert order.id in payment.charged_orders
        assert len(notification.sent) == 1
```

---

## 5. 의존성 방향 정리

```
                         의존성 방향: 바깥 -> 안쪽

  ┌─────────────────────────────────────────────────────────┐
  │  Adapters (Inbound)           Adapters (Outbound)       │
  │  ┌──────────────┐            ┌────────────────────┐     │
  │  │ Django View   │            │ DjangoOrderRepo    │     │
  │  │ DRF Serializer│            │ StripePayment      │     │
  │  │ Celery Task   │            │ EmailNotification  │     │
  │  └──────┬───────┘            └────────┬───────────┘     │
  │         │                             │                  │
  │         │ 의존                     구현(implements)       │
  │         ▼                             ▼                  │
  │  ┌─────────────────────────────────────────────┐        │
  │  │            Ports (인터페이스)                  │        │
  │  │  ┌────────────────┐  ┌───────────────────┐  │        │
  │  │  │ Inbound Ports  │  │ Outbound Ports    │  │        │
  │  │  │ (Use Cases)    │  │ (Repository 등)   │  │        │
  │  │  └───────┬────────┘  └────────┬──────────┘  │        │
  │  │          │                    ▲              │        │
  │  │          │ 구현            사용(의존)          │        │
  │  │          ▼                    │              │        │
  │  │  ┌────────────────────────────┴─────┐       │        │
  │  │  │    Application Service           │       │        │
  │  │  │    (Use Case 구현체)              │       │        │
  │  │  └──────────────┬───────────────────┘       │        │
  │  │                 │                            │        │
  │  │                 │ 사용                        │        │
  │  │                 ▼                            │        │
  │  │  ┌──────────────────────────────────┐       │        │
  │  │  │         Domain (코어)             │       │        │
  │  │  │  Entity, Value Object, Service   │       │        │
  │  │  │  (순수 Python, Django 의존 없음)    │       │        │
  │  │  └──────────────────────────────────┘       │        │
  │  └─────────────────────────────────────────────┘        │
  └─────────────────────────────────────────────────────────┘
```

**핵심**: Application Service는 Outbound Port(인터페이스)에 의존하지, 구현체(`DjangoOrderRepository`)에 직접 의존하지 않는다. 이것이 **의존성 역전 원칙(DIP)**이다.

---

## 6. 실무 적용 시 주의사항

### Django Model과 도메인 엔티티를 분리하는 이유

| 관점 | Django Model | 도메인 엔티티 |
|------|-------------|--------------|
| 책임 | DB 스키마 매핑, 쿼리 | 비즈니스 규칙 표현 |
| 의존 | `django.db.models` | 없음 (순수 Python) |
| 변경 사유 | 테이블 구조 변경 | 비즈니스 요구사항 변경 |

분리하면 DB 마이그레이션과 비즈니스 로직 변경이 서로 영향을 주지 않는다.

### 점진적 도입 전략

1. **신규 기능부터 적용** -- 기존 코드를 한 번에 리팩터링하지 않는다.
2. **복잡한 도메인 로직이 있는 앱만** -- 단순 CRUD 앱에는 과도한 설계다.
3. **Repository 패턴부터 시작** -- ORM 직접 호출을 Repository로 감싸는 것만으로도 첫 단계로 충분하다.
4. **django-injector 또는 dependency-injector 라이브러리** -- DI 컨테이너가 필요해지면 도입을 검토한다. 초기에는 위의 `di.py`처럼 수동 조립으로 충분하다.

### 흔한 실수

- **Domain에 Django import가 섞이는 것**: `from django.utils import timezone` 같은 코드가 도메인에 들어가면 격리가 깨진다. 표준 라이브러리 `datetime`을 쓴다.
- **Repository에서 도메인 로직을 수행하는 것**: 쿼리셋 필터링은 Repository의 역할이지만, 비즈니스 판단(`if order.status == ...`)은 도메인 엔티티의 메서드여야 한다.
- **어댑터 간 직접 의존**: Inbound 어댑터(View)가 Outbound 어댑터(Repository)를 직접 호출하면 안 된다. 반드시 유스케이스를 통해야 한다.
