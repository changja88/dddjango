# 주문 서비스 헥사고날 아키텍처 설계

## 1. 아키텍처 개요

헥사고날 아키텍처(Ports and Adapters)는 도메인 로직을 외부 인프라로부터 완전히 격리하여, 비즈니스 규칙이 프레임워크나 데이터베이스에 의존하지 않도록 설계하는 패턴이다.

```
              [외부 세계 - Driving Side]
                       |
            +----- Inbound Adapter -----+
            |  (REST API, gRPC, CLI)    |
            +---------------------------+
                       |
              [ Inbound Port (Interface) ]
                       |
            +---------------------------+
            |                           |
            |     Application Service   |
            |     (Use Case Orchestrator)|
            |                           |
            |   +-------------------+   |
            |   |   Domain Model    |   |
            |   |  (Entity, VO,     |   |
            |   |   Domain Service) |   |
            |   +-------------------+   |
            |                           |
            +---------------------------+
                       |
             [ Outbound Port (Interface) ]
                       |
            +----- Outbound Adapter ----+
            | (DB, Message Broker, API) |
            +---------------------------+
                       |
              [외부 세계 - Driven Side]
```

## 2. 패키지 구조

```
order_service/
|
+-- domain/                      # 핵심 도메인 계층 (의존성 없음)
|   +-- model/
|   |   +-- order.py             # Order 엔티티 (애그리거트 루트)
|   |   +-- order_item.py        # OrderItem 엔티티
|   |   +-- value_objects.py     # Money, OrderStatus, Address 등
|   |   +-- events.py            # 도메인 이벤트
|   +-- service/
|   |   +-- order_domain_service.py   # 도메인 서비스
|   |   +-- pricing_policy.py         # 가격 정책
|   +-- exception.py             # 도메인 예외
|
+-- application/                 # 애플리케이션 계층 (유스케이스)
|   +-- port/
|   |   +-- inbound/
|   |   |   +-- create_order_use_case.py
|   |   |   +-- cancel_order_use_case.py
|   |   |   +-- get_order_query.py
|   |   |   +-- update_order_status_use_case.py
|   |   +-- outbound/
|   |       +-- order_repository_port.py
|   |       +-- payment_port.py
|   |       +-- inventory_port.py
|   |       +-- notification_port.py
|   |       +-- event_publisher_port.py
|   +-- service/
|       +-- order_application_service.py
|       +-- order_query_service.py
|
+-- adapter/                     # 어댑터 계층 (외부 연결)
|   +-- inbound/
|   |   +-- rest/
|   |   |   +-- order_controller.py
|   |   |   +-- dto/
|   |   |       +-- request.py
|   |   |       +-- response.py
|   |   +-- grpc/
|   |   |   +-- order_grpc_service.py
|   |   +-- event/
|   |       +-- order_event_handler.py
|   +-- outbound/
|       +-- persistence/
|       |   +-- order_repository_adapter.py
|       |   +-- order_orm_model.py
|       |   +-- order_mapper.py
|       +-- payment/
|       |   +-- payment_adapter.py
|       +-- inventory/
|       |   +-- inventory_adapter.py
|       +-- notification/
|       |   +-- notification_adapter.py
|       +-- messaging/
|           +-- kafka_event_publisher.py
|
+-- config/
    +-- dependency_injection.py   # DI 컨테이너 설정
```

## 3. 도메인 모델

### 3.1 Value Objects

```python
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal


class OrderStatus(Enum):
    CREATED = "CREATED"
    CONFIRMED = "CONFIRMED"
    PAID = "PAID"
    PREPARING = "PREPARING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "KRW"

    def add(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError(f"통화 단위 불일치: {self.currency} != {other.currency}")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def multiply(self, factor: int) -> Money:
        return Money(amount=self.amount * factor, currency=self.currency)

    def is_positive(self) -> bool:
        return self.amount > 0


@dataclass(frozen=True)
class Address:
    street: str
    city: str
    zip_code: str
    detail: str = ""


@dataclass(frozen=True)
class OrderId:
    value: str


@dataclass(frozen=True)
class CustomerId:
    value: str


@dataclass(frozen=True)
class ProductId:
    value: str
```

### 3.2 Order 엔티티 (애그리거트 루트)

```python
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from uuid import uuid4

from domain.model.value_objects import (
    OrderId, CustomerId, OrderStatus, Money, Address
)
from domain.model.order_item import OrderItem
from domain.model.events import (
    OrderCreatedEvent, OrderCancelledEvent, OrderStatusChangedEvent
)
from domain.exception import (
    InvalidOrderStateError, EmptyOrderError
)


@dataclass
class Order:
    """주문 애그리거트 루트"""
    id: OrderId
    customer_id: CustomerId
    items: List[OrderItem]
    shipping_address: Address
    status: OrderStatus
    total_amount: Money
    created_at: datetime
    updated_at: datetime
    _domain_events: List = field(default_factory=list, repr=False)

    @staticmethod
    def create(
        customer_id: CustomerId,
        items: List[OrderItem],
        shipping_address: Address,
    ) -> Order:
        if not items:
            raise EmptyOrderError("주문 항목이 비어 있습니다.")

        total = Money(amount=0)
        for item in items:
            total = total.add(item.subtotal())

        now = datetime.utcnow()
        order = Order(
            id=OrderId(value=str(uuid4())),
            customer_id=customer_id,
            items=items,
            shipping_address=shipping_address,
            status=OrderStatus.CREATED,
            total_amount=total,
            created_at=now,
            updated_at=now,
        )
        order._domain_events.append(
            OrderCreatedEvent(order_id=order.id, customer_id=customer_id, total=total)
        )
        return order

    def confirm(self) -> None:
        if self.status != OrderStatus.CREATED:
            raise InvalidOrderStateError(
                f"주문 확인 불가: 현재 상태 {self.status.value}"
            )
        self._change_status(OrderStatus.CONFIRMED)

    def mark_as_paid(self) -> None:
        if self.status != OrderStatus.CONFIRMED:
            raise InvalidOrderStateError(
                f"결제 완료 처리 불가: 현재 상태 {self.status.value}"
            )
        self._change_status(OrderStatus.PAID)

    def cancel(self, reason: str) -> None:
        if self.status in (OrderStatus.SHIPPED, OrderStatus.DELIVERED):
            raise InvalidOrderStateError(
                f"취소 불가: 현재 상태 {self.status.value}"
            )
        self._change_status(OrderStatus.CANCELLED)
        self._domain_events.append(
            OrderCancelledEvent(order_id=self.id, reason=reason)
        )

    def _change_status(self, new_status: OrderStatus) -> None:
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.utcnow()
        self._domain_events.append(
            OrderStatusChangedEvent(
                order_id=self.id, old_status=old_status, new_status=new_status
            )
        )

    def pull_domain_events(self) -> List:
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
```

### 3.3 도메인 이벤트

```python
from dataclasses import dataclass
from domain.model.value_objects import OrderId, CustomerId, Money, OrderStatus


@dataclass(frozen=True)
class OrderCreatedEvent:
    order_id: OrderId
    customer_id: CustomerId
    total: Money


@dataclass(frozen=True)
class OrderCancelledEvent:
    order_id: OrderId
    reason: str


@dataclass(frozen=True)
class OrderStatusChangedEvent:
    order_id: OrderId
    old_status: OrderStatus
    new_status: OrderStatus
```

## 4. 포트 정의

### 4.1 인바운드 포트 (Driving Ports)

인바운드 포트는 외부에서 도메인으로 들어오는 요청을 정의하는 인터페이스이다. 유스케이스 단위로 분리하여 인터페이스 분리 원칙(ISP)을 준수한다.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from decimal import Decimal

from domain.model.value_objects import OrderId, OrderStatus


# ──────────────────────────────────────────
# Command (상태 변경)
# ──────────────────────────────────────────

@dataclass(frozen=True)
class CreateOrderCommand:
    customer_id: str
    items: List[CreateOrderItemCommand]
    street: str
    city: str
    zip_code: str
    address_detail: str = ""


@dataclass(frozen=True)
class CreateOrderItemCommand:
    product_id: str
    product_name: str
    quantity: int
    unit_price: Decimal


class CreateOrderUseCase(ABC):
    """주문 생성 유스케이스"""
    @abstractmethod
    def execute(self, command: CreateOrderCommand) -> OrderId:
        ...


@dataclass(frozen=True)
class CancelOrderCommand:
    order_id: str
    reason: str


class CancelOrderUseCase(ABC):
    """주문 취소 유스케이스"""
    @abstractmethod
    def execute(self, command: CancelOrderCommand) -> None:
        ...


@dataclass(frozen=True)
class UpdateOrderStatusCommand:
    order_id: str
    new_status: str


class UpdateOrderStatusUseCase(ABC):
    """주문 상태 변경 유스케이스"""
    @abstractmethod
    def execute(self, command: UpdateOrderStatusCommand) -> None:
        ...


# ──────────────────────────────────────────
# Query (조회 전용)
# ──────────────────────────────────────────

@dataclass(frozen=True)
class OrderResponse:
    order_id: str
    customer_id: str
    status: str
    total_amount: Decimal
    currency: str
    items: List[OrderItemResponse]
    created_at: str


@dataclass(frozen=True)
class OrderItemResponse:
    product_id: str
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class GetOrderQuery(ABC):
    """단일 주문 조회"""
    @abstractmethod
    def execute(self, order_id: str) -> Optional[OrderResponse]:
        ...


class ListOrdersByCustomerQuery(ABC):
    """고객별 주문 목록 조회"""
    @abstractmethod
    def execute(
        self, customer_id: str, status: Optional[OrderStatus] = None
    ) -> List[OrderResponse]:
        ...
```

### 4.2 아웃바운드 포트 (Driven Ports)

아웃바운드 포트는 도메인이 외부 인프라에 요청하는 계약을 정의한다. 도메인 계층은 이 인터페이스에만 의존하며, 구체적인 구현은 알지 못한다.

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.model.order import Order
from domain.model.value_objects import OrderId, CustomerId, Money, ProductId


class OrderRepositoryPort(ABC):
    """주문 영속성 포트"""

    @abstractmethod
    def save(self, order: Order) -> None:
        """주문을 저장하거나 갱신한다."""
        ...

    @abstractmethod
    def find_by_id(self, order_id: OrderId) -> Optional[Order]:
        """주문 ID로 주문을 조회한다."""
        ...

    @abstractmethod
    def find_by_customer_id(
        self, customer_id: CustomerId
    ) -> List[Order]:
        """고객 ID로 주문 목록을 조회한다."""
        ...

    @abstractmethod
    def delete(self, order_id: OrderId) -> None:
        """주문을 삭제한다."""
        ...


class PaymentPort(ABC):
    """결제 처리 포트"""

    @abstractmethod
    def process_payment(
        self, order_id: OrderId, customer_id: CustomerId, amount: Money
    ) -> str:
        """결제를 처리하고 결제 ID를 반환한다."""
        ...

    @abstractmethod
    def refund(self, payment_id: str, amount: Money) -> bool:
        """결제를 환불한다."""
        ...


class InventoryPort(ABC):
    """재고 관리 포트"""

    @abstractmethod
    def check_availability(
        self, product_id: ProductId, quantity: int
    ) -> bool:
        """재고 가용 여부를 확인한다."""
        ...

    @abstractmethod
    def reserve(
        self, product_id: ProductId, quantity: int, order_id: OrderId
    ) -> bool:
        """주문을 위해 재고를 예약한다."""
        ...

    @abstractmethod
    def release(
        self, product_id: ProductId, quantity: int, order_id: OrderId
    ) -> None:
        """예약된 재고를 해제한다."""
        ...


class NotificationPort(ABC):
    """알림 발송 포트"""

    @abstractmethod
    def send_order_confirmation(
        self, customer_id: CustomerId, order_id: OrderId
    ) -> None:
        ...

    @abstractmethod
    def send_order_cancellation(
        self, customer_id: CustomerId, order_id: OrderId, reason: str
    ) -> None:
        ...

    @abstractmethod
    def send_shipping_notification(
        self, customer_id: CustomerId, order_id: OrderId
    ) -> None:
        ...


class EventPublisherPort(ABC):
    """도메인 이벤트 발행 포트"""

    @abstractmethod
    def publish(self, event: object) -> None:
        """도메인 이벤트를 외부 메시지 브로커에 발행한다."""
        ...

    @abstractmethod
    def publish_all(self, events: List[object]) -> None:
        """여러 도메인 이벤트를 일괄 발행한다."""
        ...
```

## 5. 애플리케이션 서비스 (유스케이스 구현)

애플리케이션 서비스는 인바운드 포트를 구현하고, 아웃바운드 포트를 주입받아 유스케이스를 오케스트레이션한다.

```python
from domain.model.order import Order
from domain.model.order_item import OrderItem
from domain.model.value_objects import (
    OrderId, CustomerId, ProductId, Money, Address
)
from application.port.inbound.create_order_use_case import (
    CreateOrderUseCase, CreateOrderCommand
)
from application.port.inbound.cancel_order_use_case import (
    CancelOrderUseCase, CancelOrderCommand
)
from application.port.outbound.order_repository_port import OrderRepositoryPort
from application.port.outbound.payment_port import PaymentPort
from application.port.outbound.inventory_port import InventoryPort
from application.port.outbound.notification_port import NotificationPort
from application.port.outbound.event_publisher_port import EventPublisherPort


class OrderApplicationService(CreateOrderUseCase, CancelOrderUseCase):
    """주문 관련 커맨드를 처리하는 애플리케이션 서비스"""

    def __init__(
        self,
        order_repository: OrderRepositoryPort,
        payment_port: PaymentPort,
        inventory_port: InventoryPort,
        notification_port: NotificationPort,
        event_publisher: EventPublisherPort,
    ):
        self._order_repository = order_repository
        self._payment = payment_port
        self._inventory = inventory_port
        self._notification = notification_port
        self._event_publisher = event_publisher

    def execute(self, command: CreateOrderCommand) -> OrderId:
        """주문 생성 유스케이스"""

        # 1. 도메인 객체 생성
        customer_id = CustomerId(value=command.customer_id)
        items = [
            OrderItem(
                product_id=ProductId(value=item.product_id),
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=Money(amount=item.unit_price),
            )
            for item in command.items
        ]
        address = Address(
            street=command.street,
            city=command.city,
            zip_code=command.zip_code,
            detail=command.address_detail,
        )

        # 2. 재고 확인
        for item in items:
            available = self._inventory.check_availability(
                item.product_id, item.quantity
            )
            if not available:
                raise ValueError(
                    f"재고 부족: {item.product_name} (요청: {item.quantity})"
                )

        # 3. 도메인 모델을 통한 주문 생성
        order = Order.create(
            customer_id=customer_id,
            items=items,
            shipping_address=address,
        )

        # 4. 재고 예약
        for item in items:
            self._inventory.reserve(item.product_id, item.quantity, order.id)

        # 5. 영속화
        self._order_repository.save(order)

        # 6. 도메인 이벤트 발행
        events = order.pull_domain_events()
        self._event_publisher.publish_all(events)

        # 7. 알림 발송
        self._notification.send_order_confirmation(customer_id, order.id)

        return order.id

    def execute(self, command: CancelOrderCommand) -> None:
        """주문 취소 유스케이스"""

        order_id = OrderId(value=command.order_id)
        order = self._order_repository.find_by_id(order_id)
        if order is None:
            raise ValueError(f"주문을 찾을 수 없습니다: {command.order_id}")

        # 1. 도메인 로직으로 취소 처리
        order.cancel(reason=command.reason)

        # 2. 재고 해제
        for item in order.items:
            self._inventory.release(item.product_id, item.quantity, order.id)

        # 3. 영속화
        self._order_repository.save(order)

        # 4. 도메인 이벤트 발행
        events = order.pull_domain_events()
        self._event_publisher.publish_all(events)

        # 5. 취소 알림
        self._notification.send_order_cancellation(
            order.customer_id, order.id, command.reason
        )
```

> **참고**: 실제 구현에서는 `CreateOrderUseCase`와 `CancelOrderUseCase`를 별도 클래스로 분리하는 것이 ISP에 더 충실하다. 위 코드는 전체 흐름을 한눈에 보여주기 위한 예시이다.

## 6. 어댑터 구현

### 6.1 인바운드 어댑터 (REST Controller)

```python
from dataclasses import asdict
from decimal import Decimal

from django.http import JsonResponse
from django.views import View

from application.port.inbound.create_order_use_case import (
    CreateOrderUseCase, CreateOrderCommand, CreateOrderItemCommand
)
from application.port.inbound.cancel_order_use_case import (
    CancelOrderUseCase, CancelOrderCommand
)
from application.port.inbound.get_order_query import (
    GetOrderQuery
)

import json


class OrderController(View):
    """REST API 인바운드 어댑터 (Django 기반)"""

    def __init__(
        self,
        create_order_use_case: CreateOrderUseCase,
        cancel_order_use_case: CancelOrderUseCase,
        get_order_query: GetOrderQuery,
    ):
        super().__init__()
        self._create_order = create_order_use_case
        self._cancel_order = cancel_order_use_case
        self._get_order = get_order_query

    def post(self, request) -> JsonResponse:
        """POST /orders - 주문 생성"""
        body = json.loads(request.body)

        command = CreateOrderCommand(
            customer_id=body["customer_id"],
            items=[
                CreateOrderItemCommand(
                    product_id=item["product_id"],
                    product_name=item["product_name"],
                    quantity=item["quantity"],
                    unit_price=Decimal(str(item["unit_price"])),
                )
                for item in body["items"]
            ],
            street=body["address"]["street"],
            city=body["address"]["city"],
            zip_code=body["address"]["zip_code"],
            address_detail=body["address"].get("detail", ""),
        )

        order_id = self._create_order.execute(command)
        return JsonResponse(
            {"order_id": order_id.value, "status": "CREATED"},
            status=201,
        )

    def get(self, request, order_id: str) -> JsonResponse:
        """GET /orders/<order_id> - 주문 조회"""
        result = self._get_order.execute(order_id)
        if result is None:
            return JsonResponse(
                {"error": "주문을 찾을 수 없습니다"}, status=404
            )
        return JsonResponse(asdict(result), status=200)

    def delete(self, request, order_id: str) -> JsonResponse:
        """DELETE /orders/<order_id> - 주문 취소"""
        body = json.loads(request.body)
        command = CancelOrderCommand(
            order_id=order_id,
            reason=body.get("reason", "고객 요청에 의한 취소"),
        )
        self._cancel_order.execute(command)
        return JsonResponse({"status": "CANCELLED"}, status=200)
```

### 6.2 아웃바운드 어댑터 - 영속성 (Django ORM)

```python
from typing import Optional, List

from django.db import models

from domain.model.order import Order
from domain.model.value_objects import (
    OrderId, CustomerId, OrderStatus, Money, Address, ProductId
)
from domain.model.order_item import OrderItem
from application.port.outbound.order_repository_port import OrderRepositoryPort


# ── ORM 모델 ──

class OrderOrmModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    customer_id = models.CharField(max_length=36, db_index=True)
    status = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="KRW")
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    address_detail = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "orders"


class OrderItemOrmModel(models.Model):
    order = models.ForeignKey(
        OrderOrmModel, on_delete=models.CASCADE, related_name="items"
    )
    product_id = models.CharField(max_length=36)
    product_name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "order_items"


# ── 매퍼 ──

class OrderMapper:
    """도메인 모델 <-> ORM 모델 변환"""

    @staticmethod
    def to_domain(orm: OrderOrmModel) -> Order:
        items = [
            OrderItem(
                product_id=ProductId(value=item_orm.product_id),
                product_name=item_orm.product_name,
                quantity=item_orm.quantity,
                unit_price=Money(amount=item_orm.unit_price),
            )
            for item_orm in orm.items.all()
        ]
        return Order(
            id=OrderId(value=orm.id),
            customer_id=CustomerId(value=orm.customer_id),
            items=items,
            shipping_address=Address(
                street=orm.street,
                city=orm.city,
                zip_code=orm.zip_code,
                detail=orm.address_detail,
            ),
            status=OrderStatus(orm.status),
            total_amount=Money(amount=orm.total_amount, currency=orm.currency),
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    @staticmethod
    def to_orm(order: Order) -> OrderOrmModel:
        return OrderOrmModel(
            id=order.id.value,
            customer_id=order.customer_id.value,
            status=order.status.value,
            total_amount=order.total_amount.amount,
            currency=order.total_amount.currency,
            street=order.shipping_address.street,
            city=order.shipping_address.city,
            zip_code=order.shipping_address.zip_code,
            address_detail=order.shipping_address.detail,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )


# ── 어댑터 ──

class DjangoOrderRepositoryAdapter(OrderRepositoryPort):
    """Django ORM 기반 주문 리포지토리 어댑터"""

    def __init__(self):
        self._mapper = OrderMapper()

    def save(self, order: Order) -> None:
        orm_order = self._mapper.to_orm(order)
        orm_order.save()

        # 기존 아이템 삭제 후 재생성 (upsert 전략)
        OrderItemOrmModel.objects.filter(order_id=order.id.value).delete()
        for item in order.items:
            OrderItemOrmModel.objects.create(
                order_id=order.id.value,
                product_id=item.product_id.value,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price.amount,
            )

    def find_by_id(self, order_id: OrderId) -> Optional[Order]:
        try:
            orm = OrderOrmModel.objects.prefetch_related("items").get(
                id=order_id.value
            )
            return self._mapper.to_domain(orm)
        except OrderOrmModel.DoesNotExist:
            return None

    def find_by_customer_id(self, customer_id: CustomerId) -> List[Order]:
        orms = OrderOrmModel.objects.prefetch_related("items").filter(
            customer_id=customer_id.value
        )
        return [self._mapper.to_domain(orm) for orm in orms]

    def delete(self, order_id: OrderId) -> None:
        OrderOrmModel.objects.filter(id=order_id.value).delete()
```

### 6.3 아웃바운드 어댑터 - 결제 (외부 API)

```python
import requests
from domain.model.value_objects import OrderId, CustomerId, Money
from application.port.outbound.payment_port import PaymentPort


class ExternalPaymentAdapter(PaymentPort):
    """외부 PG사 연동 어댑터"""

    def __init__(self, base_url: str, api_key: str):
        self._base_url = base_url
        self._api_key = api_key

    def process_payment(
        self, order_id: OrderId, customer_id: CustomerId, amount: Money
    ) -> str:
        response = requests.post(
            f"{self._base_url}/payments",
            json={
                "order_id": order_id.value,
                "customer_id": customer_id.value,
                "amount": str(amount.amount),
                "currency": amount.currency,
            },
            headers={"Authorization": f"Bearer {self._api_key}"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()["payment_id"]

    def refund(self, payment_id: str, amount: Money) -> bool:
        response = requests.post(
            f"{self._base_url}/payments/{payment_id}/refund",
            json={
                "amount": str(amount.amount),
                "currency": amount.currency,
            },
            headers={"Authorization": f"Bearer {self._api_key}"},
            timeout=10,
        )
        return response.status_code == 200
```

### 6.4 아웃바운드 어댑터 - 이벤트 발행 (Kafka)

```python
import json
from dataclasses import asdict
from typing import List

from kafka import KafkaProducer

from application.port.outbound.event_publisher_port import EventPublisherPort


class KafkaEventPublisherAdapter(EventPublisherPort):
    """Kafka 기반 도메인 이벤트 발행 어댑터"""

    def __init__(self, bootstrap_servers: str, topic: str):
        self._topic = topic
        self._producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(
                v, default=str
            ).encode("utf-8"),
        )

    def publish(self, event: object) -> None:
        event_data = {
            "event_type": type(event).__name__,
            "payload": asdict(event) if hasattr(event, "__dataclass_fields__") else str(event),
        }
        self._producer.send(self._topic, value=event_data)
        self._producer.flush()

    def publish_all(self, events: List[object]) -> None:
        for event in events:
            self.publish(event)
```

## 7. 의존성 주입 설정

```python
from adapter.outbound.persistence.order_repository_adapter import (
    DjangoOrderRepositoryAdapter,
)
from adapter.outbound.payment.payment_adapter import ExternalPaymentAdapter
from adapter.outbound.inventory.inventory_adapter import HttpInventoryAdapter
from adapter.outbound.notification.notification_adapter import (
    EmailNotificationAdapter,
)
from adapter.outbound.messaging.kafka_event_publisher import (
    KafkaEventPublisherAdapter,
)
from application.service.order_application_service import OrderApplicationService
from adapter.inbound.rest.order_controller import OrderController

from django.conf import settings


def create_order_controller() -> OrderController:
    """의존성을 조립하여 컨트롤러를 생성한다."""

    # 아웃바운드 어댑터 인스턴스화
    order_repo = DjangoOrderRepositoryAdapter()
    payment = ExternalPaymentAdapter(
        base_url=settings.PAYMENT_API_URL,
        api_key=settings.PAYMENT_API_KEY,
    )
    inventory = HttpInventoryAdapter(
        base_url=settings.INVENTORY_API_URL,
    )
    notification = EmailNotificationAdapter(
        smtp_host=settings.EMAIL_HOST,
    )
    event_publisher = KafkaEventPublisherAdapter(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        topic="order-events",
    )

    # 애플리케이션 서비스 (유스케이스 구현체)
    app_service = OrderApplicationService(
        order_repository=order_repo,
        payment_port=payment,
        inventory_port=inventory,
        notification_port=notification,
        event_publisher=event_publisher,
    )

    # 인바운드 어댑터 (컨트롤러)
    return OrderController(
        create_order_use_case=app_service,
        cancel_order_use_case=app_service,
        get_order_query=app_service,
    )
```

## 8. 인바운드/아웃바운드 포트 요약

| 구분 | 포트 이름 | 역할 | 어댑터 예시 |
|------|-----------|------|-------------|
| **Inbound** | `CreateOrderUseCase` | 주문 생성 명령 진입점 | REST Controller, gRPC Service |
| **Inbound** | `CancelOrderUseCase` | 주문 취소 명령 진입점 | REST Controller, Event Handler |
| **Inbound** | `UpdateOrderStatusUseCase` | 주문 상태 변경 진입점 | REST Controller, Message Consumer |
| **Inbound** | `GetOrderQuery` | 단건 주문 조회 | REST Controller |
| **Inbound** | `ListOrdersByCustomerQuery` | 고객별 주문 목록 조회 | REST Controller |
| **Outbound** | `OrderRepositoryPort` | 주문 영속성 (저장/조회/삭제) | Django ORM, SQLAlchemy, In-Memory |
| **Outbound** | `PaymentPort` | 결제 처리 및 환불 | PG사 REST API, Mock |
| **Outbound** | `InventoryPort` | 재고 확인 및 예약/해제 | 재고 서비스 HTTP Client |
| **Outbound** | `NotificationPort` | 알림 발송 (이메일, SMS, 푸시) | SMTP, Firebase, Slack Webhook |
| **Outbound** | `EventPublisherPort` | 도메인 이벤트 외부 발행 | Kafka Producer, RabbitMQ |

## 9. 의존성 방향 규칙

```
Inbound Adapter  -->  Inbound Port (interface)
                            |
                            v
                    Application Service
                            |
                            v
                      Domain Model  (의존성 없음, 순수 Python)
                            ^
                            |
                    Application Service
                            |
                            v
                    Outbound Port (interface)
                            ^
                            |
                    Outbound Adapter  -->  외부 인프라
```

핵심 규칙:

1. **도메인 계층은 어떤 외부 의존성도 갖지 않는다.** 순수 Python 클래스로만 구성한다.
2. **애플리케이션 계층은 도메인 계층에만 의존한다.** 아웃바운드 포트는 추상 클래스(ABC)이며 구체 구현을 알지 못한다.
3. **어댑터 계층은 안쪽 계층에 의존한다.** 인바운드 어댑터는 인바운드 포트를 호출하고, 아웃바운드 어댑터는 아웃바운드 포트를 구현한다.
4. **의존성 역전 원칙(DIP)** 을 통해 모든 의존성 화살표가 안쪽(도메인)을 향한다.

## 10. 테스트 전략

헥사고날 아키텍처의 가장 큰 이점은 테스트 용이성이다.

```python
# 아웃바운드 포트의 인메모리 구현 (테스트용)
class InMemoryOrderRepository(OrderRepositoryPort):
    def __init__(self):
        self._store: dict[str, Order] = {}

    def save(self, order: Order) -> None:
        self._store[order.id.value] = order

    def find_by_id(self, order_id: OrderId) -> Optional[Order]:
        return self._store.get(order_id.value)

    def find_by_customer_id(self, customer_id: CustomerId) -> List[Order]:
        return [
            o for o in self._store.values()
            if o.customer_id == customer_id
        ]

    def delete(self, order_id: OrderId) -> None:
        self._store.pop(order_id.value, None)


class StubPaymentPort(PaymentPort):
    def process_payment(self, order_id, customer_id, amount) -> str:
        return "test-payment-id-001"

    def refund(self, payment_id, amount) -> bool:
        return True


class StubInventoryPort(InventoryPort):
    def __init__(self, available: bool = True):
        self._available = available

    def check_availability(self, product_id, quantity) -> bool:
        return self._available

    def reserve(self, product_id, quantity, order_id) -> bool:
        return True

    def release(self, product_id, quantity, order_id) -> None:
        pass


# 유스케이스 단위 테스트
def test_create_order_success():
    repo = InMemoryOrderRepository()
    service = OrderApplicationService(
        order_repository=repo,
        payment_port=StubPaymentPort(),
        inventory_port=StubInventoryPort(available=True),
        notification_port=StubNotificationPort(),
        event_publisher=StubEventPublisher(),
    )

    command = CreateOrderCommand(
        customer_id="customer-001",
        items=[
            CreateOrderItemCommand(
                product_id="prod-001",
                product_name="키보드",
                quantity=1,
                unit_price=Decimal("150000"),
            )
        ],
        street="테헤란로 123",
        city="서울",
        zip_code="06234",
    )

    order_id = service.execute(command)

    saved_order = repo.find_by_id(order_id)
    assert saved_order is not None
    assert saved_order.status == OrderStatus.CREATED
    assert saved_order.total_amount.amount == Decimal("150000")


def test_create_order_fails_when_out_of_stock():
    service = OrderApplicationService(
        order_repository=InMemoryOrderRepository(),
        payment_port=StubPaymentPort(),
        inventory_port=StubInventoryPort(available=False),
        notification_port=StubNotificationPort(),
        event_publisher=StubEventPublisher(),
    )

    command = CreateOrderCommand(
        customer_id="customer-001",
        items=[
            CreateOrderItemCommand(
                product_id="prod-001",
                product_name="키보드",
                quantity=100,
                unit_price=Decimal("150000"),
            )
        ],
        street="테헤란로 123",
        city="서울",
        zip_code="06234",
    )

    with pytest.raises(ValueError, match="재고 부족"):
        service.execute(command)
```

테스트 계층별 전략:

| 계층 | 테스트 방법 | 특징 |
|------|------------|------|
| **도메인** | 순수 단위 테스트 | 외부 의존성 없음, 가장 빠름 |
| **애플리케이션** | 스텁/페이크 포트로 단위 테스트 | 유스케이스 로직 검증 |
| **어댑터** | 통합 테스트 | 실제 DB/API와 연동 검증 |
| **전체** | E2E 테스트 | 모든 계층을 실제 구현체로 결합 |
