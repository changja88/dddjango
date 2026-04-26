# Django DDD 프로젝트 설계 -- Inventory & Order 도메인

## 1. 전체 파일 트리

```
project_root/
├── manage.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── inventory/                          # 재고 관리 Bounded Context
│   ├── __init__.py
│   ├── domain/                         # 도메인 계층
│   │   ├── __init__.py
│   │   ├── entities.py                 # Product, Warehouse, Stock 엔티티
│   │   ├── value_objects.py            # Quantity, SKU 등 값 객체
│   │   ├── aggregates.py              # Stock 애그리거트 루트
│   │   ├── events.py                  # StockDepleted, GoodsReceived 등 도메인 이벤트
│   │   ├── exceptions.py             # InsufficientStock 등 도메인 예외
│   │   └── repositories.py           # 리포지토리 인터페이스 (ABC)
│   │
│   ├── application/                   # 애플리케이션 계층
│   │   ├── __init__.py
│   │   ├── services.py               # InventoryService (입고/출고 유스케이스)
│   │   ├── commands.py               # ReceiveGoods, ReleaseGoods 커맨드
│   │   ├── queries.py                # GetStockLevel 등 조회 DTO
│   │   └── event_handlers.py         # 도메인 이벤트 핸들러
│   │
│   ├── infrastructure/               # 인프라스트럭처 계층
│   │   ├── __init__.py
│   │   ├── models.py                 # Django ORM 모델
│   │   ├── repositories.py           # 리포지토리 구현체
│   │   ├── admin.py                  # Django Admin 설정
│   │   └── migrations/               # Django 마이그레이션
│   │       └── __init__.py
│   │
│   ├── interfaces/                   # 인터페이스 계층 (진입점)
│   │   ├── __init__.py
│   │   ├── urls.py                   # URL 라우팅
│   │   ├── views.py                  # API 뷰 (REST)
│   │   └── serializers.py            # DRF 시리얼라이저
│   │
│   └── apps.py                       # Django AppConfig
│
├── order/                             # 주문 Bounded Context
│   ├── __init__.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities.py               # Order, OrderItem 엔티티
│   │   ├── value_objects.py          # Money, OrderStatus 등 값 객체
│   │   ├── aggregates.py            # Order 애그리거트 루트
│   │   ├── events.py                # OrderCreated, OrderCancelled 도메인 이벤트
│   │   ├── exceptions.py           # InvalidOrderState 등 도메인 예외
│   │   └── repositories.py         # 리포지토리 인터페이스 (ABC)
│   │
│   ├── application/
│   │   ├── __init__.py
│   │   ├── services.py             # OrderService (주문 생성 유스케이스)
│   │   ├── commands.py             # CreateOrder, CancelOrder 커맨드
│   │   ├── queries.py              # GetOrder 등 조회 DTO
│   │   └── event_handlers.py       # 도메인 이벤트 핸들러
│   │
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── models.py               # Django ORM 모델
│   │   ├── repositories.py         # 리포지토리 구현체
│   │   ├── admin.py
│   │   └── migrations/
│   │       └── __init__.py
│   │
│   ├── interfaces/
│   │   ├── __init__.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── serializers.py
│   │
│   └── apps.py
│
└── shared/                            # 공유 커널
    ├── __init__.py
    ├── domain/
    │   ├── __init__.py
    │   ├── base_entity.py            # 엔티티 베이스 클래스
    │   ├── base_aggregate.py         # 애그리거트 루트 베이스 클래스
    │   ├── base_value_object.py      # 값 객체 베이스 클래스
    │   └── events.py                 # DomainEvent 베이스, EventBus 인터페이스
    └── infrastructure/
        ├── __init__.py
        └── event_bus.py              # EventBus 구현체 (Django signals 기반)
```

---

## 2. 각 파일의 역할

### config/
| 파일 | 역할 |
|------|------|
| `settings.py` | Django 프로젝트 설정. `INSTALLED_APPS`에 `inventory`, `order` 등록 |
| `urls.py` | 루트 URL 설정. 각 도메인의 `interfaces/urls.py`를 include |

### shared/ (공유 커널)
| 파일 | 역할 |
|------|------|
| `domain/base_entity.py` | 모든 엔티티의 베이스 클래스. `id`, `created_at`, `updated_at` 공통 필드 정의 |
| `domain/base_aggregate.py` | 애그리거트 루트 베이스. 도메인 이벤트 수집/발행 메커니즘 포함 |
| `domain/base_value_object.py` | 값 객체 베이스. 동등성 비교, 불변성 보장 |
| `domain/events.py` | `DomainEvent` 베이스 클래스, `EventBus` 인터페이스 정의 |
| `infrastructure/event_bus.py` | Django signals 기반 이벤트 버스 구현체 |

### inventory/ (재고 관리 도메인)

**domain/ -- 도메인 계층** (비즈니스 규칙, 프레임워크 무관)
| 파일 | 역할 |
|------|------|
| `entities.py` | `Product`(상품), `Warehouse`(창고), `Stock`(재고) 순수 도메인 엔티티 |
| `value_objects.py` | `Quantity`(수량), `SKU`(상품코드) 등 불변 값 객체 |
| `aggregates.py` | `Stock`을 루트로 하는 애그리거트. 입고/출고 비즈니스 규칙 캡슐화 |
| `events.py` | `GoodsReceived`(입고), `GoodsReleased`(출고), `StockDepleted`(재고부족) 이벤트 |
| `exceptions.py` | `InsufficientStockError` 등 도메인 고유 예외 |
| `repositories.py` | `StockRepository`, `ProductRepository` 추상 인터페이스 (ABC) |

**application/ -- 애플리케이션 계층** (유스케이스 오케스트레이션)
| 파일 | 역할 |
|------|------|
| `services.py` | `InventoryService` -- 입고/출고 유스케이스 조율. 트랜잭션 경계 |
| `commands.py` | `ReceiveGoodsCommand`, `ReleaseGoodsCommand` 등 커맨드 DTO |
| `queries.py` | `StockLevelQuery`, `StockLevelResult` 등 조회 DTO |
| `event_handlers.py` | 도메인 이벤트 반응 핸들러 (예: 재고 부족 시 알림 트리거) |

**infrastructure/ -- 인프라 계층** (기술 구현)
| 파일 | 역할 |
|------|------|
| `models.py` | Django ORM 모델. 도메인 엔티티와 DB 테이블 간 매핑 |
| `repositories.py` | 리포지토리 인터페이스의 Django ORM 구현체 |
| `admin.py` | Django Admin 페이지 등록 |

**interfaces/ -- 인터페이스 계층** (외부 진입점)
| 파일 | 역할 |
|------|------|
| `urls.py` | `/api/inventory/` 하위 URL 패턴 |
| `views.py` | REST API 엔드포인트. Application Service 호출 |
| `serializers.py` | 요청/응답 직렬화 (DRF Serializer) |

### order/ (주문 도메인)

**domain/**
| 파일 | 역할 |
|------|------|
| `entities.py` | `Order`(주문), `OrderItem`(주문항목) 순수 도메인 엔티티 |
| `value_objects.py` | `Money`(금액), `OrderStatus`(주문상태 enum) 값 객체 |
| `aggregates.py` | `Order`를 루트로 하는 애그리거트. 주문항목 추가, 상태 전이 규칙 |
| `events.py` | `OrderCreated`(주문생성), `OrderCancelled`(주문취소) 이벤트 |
| `exceptions.py` | `InvalidOrderStateError` 등 도메인 예외 |
| `repositories.py` | `OrderRepository` 추상 인터페이스 |

**application/**
| 파일 | 역할 |
|------|------|
| `services.py` | `OrderService` -- 주문 생성 시 재고 차감 연계 오케스트레이션 |
| `commands.py` | `CreateOrderCommand`, `CancelOrderCommand` DTO |
| `queries.py` | `GetOrderQuery`, `OrderDetailResult` DTO |
| `event_handlers.py` | `OrderCreated` 이벤트 수신하여 후속 처리 (예: 알림) |

**infrastructure/, interfaces/** -- inventory와 동일한 구조적 역할

---

## 3. 핵심 코드 스켈레톤

### 3.1 공유 커널 -- 베이스 클래스

```python
# shared/domain/events.py
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class DomainEvent:
    """모든 도메인 이벤트의 베이스 클래스."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_on: datetime = field(default_factory=datetime.utcnow)


class EventBus(ABC):
    """이벤트 버스 인터페이스. 인프라 계층에서 구현."""

    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        ...

    @abstractmethod
    def subscribe(self, event_type: type[DomainEvent], handler: callable) -> None:
        ...
```

```python
# shared/domain/base_aggregate.py
from __future__ import annotations

from typing import List

from shared.domain.events import DomainEvent


class AggregateRoot:
    """애그리거트 루트 베이스 클래스.

    도메인 이벤트를 내부에 수집하고, 리포지토리가 영속화 후 발행한다.
    """

    def __init__(self) -> None:
        self._domain_events: List[DomainEvent] = []

    def register_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def collect_events(self) -> List[DomainEvent]:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events
```

---

### 3.2 Inventory 도메인 -- 애그리거트 루트

```python
# inventory/domain/aggregates.py
from __future__ import annotations

from shared.domain.base_aggregate import AggregateRoot
from inventory.domain.events import GoodsReceived, GoodsReleased, StockDepleted
from inventory.domain.exceptions import InsufficientStockError
from inventory.domain.value_objects import Quantity


class Stock(AggregateRoot):
    """재고 애그리거트 루트.

    Product + Warehouse 조합별 재고 수량을 관리한다.
    입고/출고 비즈니스 규칙을 캡슐화한다.
    """

    LOW_STOCK_THRESHOLD = 10

    def __init__(
        self,
        stock_id: str,
        product_id: str,
        warehouse_id: str,
        quantity: Quantity,
    ) -> None:
        super().__init__()
        self.stock_id = stock_id
        self.product_id = product_id
        self.warehouse_id = warehouse_id
        self.quantity = quantity

    def receive(self, amount: Quantity) -> None:
        """상품 입고. 재고 수량을 증가시킨다."""
        self.quantity = self.quantity.add(amount)
        self.register_event(
            GoodsReceived(
                stock_id=self.stock_id,
                product_id=self.product_id,
                warehouse_id=self.warehouse_id,
                amount=amount.value,
            )
        )

    def release(self, amount: Quantity) -> None:
        """상품 출고. 재고가 부족하면 예외를 발생시킨다."""
        if not self.quantity.is_sufficient(amount):
            raise InsufficientStockError(
                product_id=self.product_id,
                requested=amount.value,
                available=self.quantity.value,
            )

        self.quantity = self.quantity.subtract(amount)
        self.register_event(
            GoodsReleased(
                stock_id=self.stock_id,
                product_id=self.product_id,
                warehouse_id=self.warehouse_id,
                amount=amount.value,
            )
        )

        if self.quantity.value <= self.LOW_STOCK_THRESHOLD:
            self.register_event(
                StockDepleted(
                    stock_id=self.stock_id,
                    product_id=self.product_id,
                    remaining=self.quantity.value,
                )
            )
```

---

### 3.3 Inventory 도메인 -- 이벤트 클래스

```python
# inventory/domain/events.py
from dataclasses import dataclass

from shared.domain.events import DomainEvent


@dataclass(frozen=True)
class GoodsReceived(DomainEvent):
    """상품이 창고에 입고되었을 때 발생하는 이벤트."""
    stock_id: str = ""
    product_id: str = ""
    warehouse_id: str = ""
    amount: int = 0


@dataclass(frozen=True)
class GoodsReleased(DomainEvent):
    """상품이 창고에서 출고되었을 때 발생하는 이벤트."""
    stock_id: str = ""
    product_id: str = ""
    warehouse_id: str = ""
    amount: int = 0


@dataclass(frozen=True)
class StockDepleted(DomainEvent):
    """재고가 임계치 이하로 떨어졌을 때 발생하는 이벤트.

    이 이벤트를 구독하여 재고 부족 알림을 보낼 수 있다.
    """
    stock_id: str = ""
    product_id: str = ""
    remaining: int = 0
```

---

### 3.4 Inventory 도메인 -- 리포지토리 인터페이스

```python
# inventory/domain/repositories.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, List

from inventory.domain.aggregates import Stock


class StockRepository(ABC):
    """Stock 애그리거트의 리포지토리 인터페이스.

    도메인 계층에서 정의하고, 인프라 계층에서 구현한다.
    """

    @abstractmethod
    def find_by_id(self, stock_id: str) -> Optional[Stock]:
        ...

    @abstractmethod
    def find_by_product_and_warehouse(
        self, product_id: str, warehouse_id: str
    ) -> Optional[Stock]:
        ...

    @abstractmethod
    def save(self, stock: Stock) -> None:
        """Stock을 저장하고, 수집된 도메인 이벤트를 발행한다."""
        ...

    @abstractmethod
    def find_low_stock(self, threshold: int) -> List[Stock]:
        ...


class ProductRepository(ABC):
    """Product 조회용 리포지토리 인터페이스."""

    @abstractmethod
    def find_by_id(self, product_id: str) -> Optional[object]:
        ...

    @abstractmethod
    def exists(self, product_id: str) -> bool:
        ...
```

---

### 3.5 Order 도메인 -- 애그리거트 루트

```python
# order/domain/aggregates.py
from __future__ import annotations

from typing import List

from shared.domain.base_aggregate import AggregateRoot
from order.domain.entities import OrderItem
from order.domain.events import OrderCreated, OrderCancelled
from order.domain.exceptions import InvalidOrderStateError
from order.domain.value_objects import OrderStatus, Money


class Order(AggregateRoot):
    """주문 애그리거트 루트.

    주문항목(OrderItem)을 자식 엔티티로 포함한다.
    외부에서는 반드시 Order를 통해서만 OrderItem에 접근한다.
    """

    def __init__(
        self,
        order_id: str,
        customer_id: str,
        items: List[OrderItem] | None = None,
    ) -> None:
        super().__init__()
        self.order_id = order_id
        self.customer_id = customer_id
        self._items: List[OrderItem] = items or []
        self._status: OrderStatus = OrderStatus.DRAFT

    @property
    def items(self) -> tuple[OrderItem, ...]:
        return tuple(self._items)

    @property
    def status(self) -> OrderStatus:
        return self._status

    @property
    def total_amount(self) -> Money:
        total = sum(item.subtotal.amount for item in self._items)
        if not self._items:
            return Money(amount=0, currency="KRW")
        return Money(amount=total, currency=self._items[0].subtotal.currency)

    def add_item(
        self,
        item_id: str,
        product_id: str,
        quantity: int,
        unit_price: Money,
    ) -> None:
        if self._status != OrderStatus.DRAFT:
            raise InvalidOrderStateError(
                f"Cannot add items to order in {self._status.value} state"
            )
        item = OrderItem(
            item_id=item_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )
        self._items.append(item)

    def place(self) -> None:
        """주문을 확정한다. OrderCreated 이벤트를 발행한다."""
        if self._status != OrderStatus.DRAFT:
            raise InvalidOrderStateError(
                f"Cannot place order in {self._status.value} state"
            )
        if not self._items:
            raise InvalidOrderStateError("Cannot place order with no items")

        self._status = OrderStatus.PLACED
        self.register_event(
            OrderCreated(
                order_id=self.order_id,
                customer_id=self.customer_id,
                items=[
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                    }
                    for item in self._items
                ],
                total_amount=self.total_amount.amount,
            )
        )

    def cancel(self) -> None:
        """주문을 취소한다. OrderCancelled 이벤트를 발행한다."""
        if self._status not in (OrderStatus.DRAFT, OrderStatus.PLACED):
            raise InvalidOrderStateError(
                f"Cannot cancel order in {self._status.value} state"
            )
        self._status = OrderStatus.CANCELLED
        self.register_event(
            OrderCancelled(
                order_id=self.order_id,
                items=[
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                    }
                    for item in self._items
                ],
            )
        )
```

---

### 3.6 Order 도메인 -- 이벤트 클래스

```python
# order/domain/events.py
from dataclasses import dataclass, field
from typing import List, Dict

from shared.domain.events import DomainEvent


@dataclass(frozen=True)
class OrderCreated(DomainEvent):
    """주문이 확정되었을 때 발생하는 이벤트.

    Inventory 도메인이 이 이벤트를 구독하여 재고를 차감한다.
    """
    order_id: str = ""
    customer_id: str = ""
    items: List[Dict[str, object]] = field(default_factory=list)
    total_amount: int = 0


@dataclass(frozen=True)
class OrderCancelled(DomainEvent):
    """주문이 취소되었을 때 발생하는 이벤트.

    Inventory 도메인이 이 이벤트를 구독하여 재고를 복원한다.
    """
    order_id: str = ""
    items: List[Dict[str, object]] = field(default_factory=list)
```

---

### 3.7 Order 도메인 -- 리포지토리 인터페이스

```python
# order/domain/repositories.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, List

from order.domain.aggregates import Order


class OrderRepository(ABC):
    """Order 애그리거트의 리포지토리 인터페이스."""

    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[Order]:
        ...

    @abstractmethod
    def find_by_customer(self, customer_id: str) -> List[Order]:
        ...

    @abstractmethod
    def save(self, order: Order) -> None:
        """Order를 저장하고, 수집된 도메인 이벤트를 발행한다."""
        ...

    @abstractmethod
    def next_id(self) -> str:
        """새 주문 ID를 생성한다."""
        ...
```

---

### 3.8 도메인 간 연계 -- OrderCreated 이벤트 핸들러 (Inventory 측)

```python
# inventory/application/event_handlers.py
from inventory.application.services import InventoryService
from inventory.domain.value_objects import Quantity
from order.domain.events import OrderCreated, OrderCancelled


class InventoryEventHandlers:
    """Order 도메인 이벤트를 구독하여 재고를 조정하는 핸들러.

    도메인 간 결합은 이벤트를 통해 느슨하게 유지한다.
    Order -> (OrderCreated 이벤트) -> Inventory 재고 차감
    Order -> (OrderCancelled 이벤트) -> Inventory 재고 복원
    """

    def __init__(self, inventory_service: InventoryService) -> None:
        self._inventory_service = inventory_service

    def handle_order_created(self, event: OrderCreated) -> None:
        """주문 생성 시 각 주문항목에 대해 재고를 차감한다."""
        for item in event.items:
            self._inventory_service.release_goods(
                product_id=item["product_id"],
                quantity=Quantity(item["quantity"]),
            )

    def handle_order_cancelled(self, event: OrderCancelled) -> None:
        """주문 취소 시 각 주문항목에 대해 재고를 복원한다."""
        for item in event.items:
            self._inventory_service.receive_goods(
                product_id=item["product_id"],
                quantity=Quantity(item["quantity"]),
            )
```

---

## 4. 계층 간 의존성 규칙

```
interfaces  -->  application  -->  domain  <--  infrastructure
(views)          (services)        (entities,    (ORM models,
                                    events,       repo 구현체)
                                    repo ABC)
```

- **domain**: 어떤 계층에도 의존하지 않는다. 순수 Python만 사용한다.
- **application**: domain에만 의존한다. 리포지토리는 인터페이스(ABC)로 주입받는다.
- **infrastructure**: domain의 인터페이스를 구현한다. Django ORM에 의존한다.
- **interfaces**: application 계층의 서비스를 호출한다. Django REST Framework에 의존한다.

## 5. 도메인 간 통신 방식

Order 도메인과 Inventory 도메인은 **도메인 이벤트**를 통해 통신한다.

1. `Order.place()` 호출 시 `OrderCreated` 이벤트가 애그리거트 내부에 수집된다.
2. `OrderRepository.save()`가 영속화 후 `EventBus.publish()`를 통해 이벤트를 발행한다.
3. `InventoryEventHandlers.handle_order_created()`가 이벤트를 수신하여 재고를 차감한다.
4. 재고 차감 결과 임계치 이하가 되면 `StockDepleted` 이벤트가 발생하여 알림이 트리거된다.

이 구조를 통해 두 도메인은 직접 참조 없이 이벤트만으로 느슨하게 결합된다.
