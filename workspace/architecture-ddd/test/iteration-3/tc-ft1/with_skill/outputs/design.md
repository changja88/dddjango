# 재고 관리(Inventory) + 주문(Order) 도메인 DDD 설계

## 1. 전략 설계

### 1.1 하위 도메인 분류

| 하위 도메인 | 유형 | 근거 |
|------------|------|------|
| 재고 관리(Inventory) | Core | 실시간 재고 추적, 입출고 관리, 재고 부족 알림은 비즈니스 경쟁력의 핵심이다 |
| 주문(Order) | Core | 주문 생성과 처리는 비즈니스 수익 흐름의 중심이다 |

### 1.2 바운디드 컨텍스트

두 도메인은 서로 다른 유비쿼터스 언어를 사용한다.

- **재고 컨텍스트**: "상품(Product)", "창고(Warehouse)", "재고(Stock)", "입고(receive)", "출고(release)", "재고 부족(stock shortage)"
- **주문 컨텍스트**: "주문(Order)", "주문항목(OrderItem)", "주문 생성(place)", "주문 취소(cancel)"

"상품"이라는 용어가 양쪽에 등장하지만 의미가 다르다. 재고 컨텍스트에서 상품은 창고에 보관되는 물리적 단위이고, 주문 컨텍스트에서 상품은 주문 항목의 참조 대상일 뿐이다. 따라서 두 개의 바운디드 컨텍스트로 분리한다.

### 1.3 컨텍스트 맵

```
[주문 컨텍스트] ----(Customer-Supplier)----> [재고 컨텍스트]
                  주문 생성 시 재고 차감 요청
                  (도메인 이벤트를 통한 결과적 일관성)
```

- **관계**: Customer-Supplier (주문이 Customer/다운스트림, 재고가 Supplier/업스트림)
- **통합 방식**: 주문 컨텍스트에서 `OrderPlacedEvent`를 발행하면, 재고 컨텍스트의 이벤트 핸들러가 구독하여 재고를 차감한다.
- **결과적 일관성**: 주문과 재고 차감은 서로 다른 애그리거트이므로, 도메인 이벤트를 통한 결과적 일관성을 적용한다 (Vernon 규칙 4).

---

## 2. 전술 설계

### 2.1 재고 컨텍스트 애그리거트 설계

| 애그리거트 | 루트 엔티티 | 내부 구성요소 | 근거 |
|-----------|-----------|-------------|------|
| Product | Product | -- | 상품 정보(이름, SKU, 단위)는 독립적인 라이프사이클을 가진다 |
| Warehouse | Warehouse | -- | 창고 정보(이름, 위치)는 독립적으로 관리된다 |
| Stock | Stock | -- | 재고는 특정 상품+창고 조합의 수량을 추적하며, 입출고 불변식을 보호한다 |

**설계 근거 (Vernon 규칙 2: 작은 애그리거트):**
- Product, Warehouse, Stock을 하나의 거대 애그리거트로 묶지 않는다.
- Stock은 `product_id`와 `warehouse_id`로 다른 애그리거트를 ID 참조한다 (Vernon 규칙 3).
- Stock의 불변식: "재고 수량은 0 미만이 될 수 없다"는 Stock 애그리거트 내에서 보호한다.

### 2.2 주문 컨텍스트 애그리거트 설계

| 애그리거트 | 루트 엔티티 | 내부 구성요소 | 근거 |
|-----------|-----------|-------------|------|
| Order | Order | OrderItem (값 객체) | 주문과 주문항목은 반드시 함께 일관성을 유지해야 한다. "최소 1개 항목" 불변식은 Order가 보호한다 |

**설계 근거:**
- OrderItem은 값 객체로 설계한다. 주문항목은 자체 라이프사이클이 없고, 속성 조합(product_id + quantity + price)으로 동등성을 판단한다.
- OrderItem을 위한 별도 리포지토리는 만들지 않는다. Order 리포지토리가 Order와 함께 저장/조회한다.

### 2.3 도메인 이벤트

| 이벤트 | 발행자 | 구독자 | 목적 |
|--------|-------|-------|------|
| `OrderPlacedEvent` | Order (주문 컨텍스트) | 재고 컨텍스트 이벤트 핸들러 | 주문 생성 시 재고 차감 |
| `OrderCancelledEvent` | Order (주문 컨텍스트) | 재고 컨텍스트 이벤트 핸들러 | 주문 취소 시 재고 복원 |
| `StockDepletedEvent` | Stock (재고 컨텍스트) | 알림 서비스 | 재고 부족 시 알림 발송 |
| `StockReceivedEvent` | Stock (재고 컨텍스트) | (로깅/감사) | 입고 이력 추적 |
| `StockReleasedEvent` | Stock (재고 컨텍스트) | (로깅/감사) | 출고 이력 추적 |

---

## 3. 프로젝트 폴더 구조

```
applications/
├── shared_kernel/
│   ├── __init__.py
│   └── value_object/
│       ├── __init__.py
│       └── money.py                        # Money 값 객체 (공통)
│
├── inventory/                              # 재고 바운디드 컨텍스트
│   ├── __init__.py
│   ├── domain_layer/
│   │   ├── __init__.py
│   │   ├── product/                        # Product 애그리거트
│   │   │   ├── __init__.py
│   │   │   └── product.py                  # 애그리거트 루트
│   │   ├── warehouse/                      # Warehouse 애그리거트
│   │   │   ├── __init__.py
│   │   │   └── warehouse.py                # 애그리거트 루트
│   │   ├── stock/                          # Stock 애그리거트
│   │   │   ├── __init__.py
│   │   │   ├── stock.py                    # 애그리거트 루트 (입고/출고 비즈니스 로직)
│   │   │   └── quantity.py                 # Quantity 값 객체
│   │   ├── value_object/
│   │   │   ├── __init__.py
│   │   │   └── sku.py                      # SKU 값 객체 (여러 애그리거트에서 공유)
│   │   ├── repository/
│   │   │   ├── __init__.py
│   │   │   ├── product_repo.py             # ProductRepository(ABC)
│   │   │   ├── warehouse_repo.py           # WarehouseRepository(ABC)
│   │   │   └── stock_repo.py               # StockRepository(ABC)
│   │   ├── event/
│   │   │   ├── __init__.py
│   │   │   └── stock_events.py             # StockReceivedEvent, StockReleasedEvent, StockDepletedEvent
│   │   └── service/
│   │       ├── __init__.py
│   │       └── stock_deduction/
│   │           ├── __init__.py
│   │           └── stock_deduction_service.py  # 재고 차감 도메인 서비스 (여러 Stock에 걸친 차감 로직)
│   │
│   ├── application_layer/
│   │   ├── __init__.py
│   │   ├── inventory_service.py            # 입고/출고 유스케이스 조율
│   │   └── event_handlers.py               # OrderPlacedEvent, OrderCancelledEvent 구독 핸들러
│   │
│   ├── infra_layer/
│   │   ├── __init__.py
│   │   ├── django_inventory/               # Django 앱
│   │   │   ├── __init__.py
│   │   │   ├── apps.py
│   │   │   ├── admin.py
│   │   │   └── models/
│   │   │       ├── __init__.py             # 모델 re-export
│   │   │       ├── product_model.py        # ProductModel (ORM)
│   │   │       ├── warehouse_model.py      # WarehouseModel (ORM)
│   │   │       └── stock_model.py          # StockModel (ORM)
│   │   ├── repository/
│   │   │   ├── __init__.py
│   │   │   ├── product_repo.py             # DjangoProductRepository
│   │   │   ├── warehouse_repo.py           # DjangoWarehouseRepository
│   │   │   └── stock_repo.py              # DjangoStockRepository
│   │   └── event_bus/
│   │       ├── __init__.py
│   │       └── signal_event_bus.py         # Django signals 기반 이벤트 버스
│   │
│   ├── presentation_layer/
│   │   ├── __init__.py
│   │   ├── routers.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── product_api.py
│   │   │   ├── warehouse_api.py
│   │   │   └── stock_api.py
│   │   └── schema/
│   │       ├── __init__.py
│   │       ├── product_schema.py
│   │       ├── warehouse_schema.py
│   │       └── stock_schema.py
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── domain/                         # 순수 도메인 로직 테스트
│       │   ├── __init__.py
│       │   ├── test_stock.py
│       │   └── test_product.py
│       ├── application/                    # 서비스 로직 테스트 (mock repo)
│       │   ├── __init__.py
│       │   └── test_inventory_service.py
│       ├── infra/                          # 리포지토리 CRUD 테스트
│       │   ├── __init__.py
│       │   └── test_stock_repo.py
│       └── api/                            # HTTP 요청/응답 테스트
│           ├── __init__.py
│           └── test_stock_api.py
│
└── ordering/                               # 주문 바운디드 컨텍스트
    ├── __init__.py
    ├── domain_layer/
    │   ├── __init__.py
    │   ├── order/                          # Order 애그리거트
    │   │   ├── __init__.py
    │   │   ├── order.py                    # 애그리거트 루트 (주문 생성/취소 비즈니스 로직)
    │   │   ├── order_item.py               # OrderItem 값 객체
    │   │   └── order_status.py             # OrderStatus 값 객체 (Enum)
    │   ├── repository/
    │   │   ├── __init__.py
    │   │   └── order_repo.py               # OrderRepository(ABC)
    │   └── event/
    │       ├── __init__.py
    │       └── order_events.py             # OrderPlacedEvent, OrderCancelledEvent
    │
    ├── application_layer/
    │   ├── __init__.py
    │   └── order_service.py                # 주문 생성/취소 유스케이스 조율
    │
    ├── infra_layer/
    │   ├── __init__.py
    │   ├── django_ordering/                # Django 앱
    │   │   ├── __init__.py
    │   │   ├── apps.py
    │   │   ├── admin.py
    │   │   └── models/
    │   │       ├── __init__.py             # 모델 re-export
    │   │       ├── order_model.py          # OrderModel (ORM)
    │   │       └── order_item_model.py     # OrderItemModel (ORM)
    │   ├── repository/
    │   │   ├── __init__.py
    │   │   └── order_repo.py              # DjangoOrderRepository
    │   └── event_bus/
    │       ├── __init__.py
    │       └── signal_event_bus.py         # Django signals 기반 이벤트 버스
    │
    ├── presentation_layer/
    │   ├── __init__.py
    │   ├── routers.py
    │   ├── api/
    │   │   ├── __init__.py
    │   │   └── order_api.py
    │   └── schema/
    │       ├── __init__.py
    │       └── order_schema.py
    │
    └── tests/
        ├── __init__.py
        ├── conftest.py
        ├── domain/
        │   ├── __init__.py
        │   └── test_order.py
        ├── application/
        │   ├── __init__.py
        │   └── test_order_service.py
        ├── infra/
        │   ├── __init__.py
        │   └── test_order_repo.py
        └── api/
            ├── __init__.py
            └── test_order_api.py
```

### 각 파일의 역할

#### shared_kernel/

| 파일 | 역할 |
|------|------|
| `value_object/money.py` | 금액을 표현하는 공통 값 객체. 두 컨텍스트 모두에서 사용한다. 도메인 로직은 포함하지 않는다. |

#### inventory/ (재고 바운디드 컨텍스트)

**domain_layer/ -- 순수 도메인 모델 (Django ORM/signals 의존 금지)**

| 파일 | 역할 |
|------|------|
| `product/product.py` | Product 애그리거트 루트. 상품명, SKU, 단위 등 상품 고유 속성을 관리한다. |
| `warehouse/warehouse.py` | Warehouse 애그리거트 루트. 창고명, 위치 등 창고 고유 속성을 관리한다. |
| `stock/stock.py` | Stock 애그리거트 루트. 특정 상품+창고 조합의 재고 수량을 관리한다. `receive()`(입고)와 `release()`(출고) 비즈니스 메서드를 통해 불변식("수량 >= 0")을 보호한다. 재고 부족 시 `StockDepletedEvent`를 발행한다. |
| `stock/quantity.py` | Quantity 값 객체. 수량을 표현하며, 음수 불가 불변식을 자체 검증한다. |
| `value_object/sku.py` | SKU 값 객체. 상품 식별 코드의 형식 규칙을 캡슐화한다. |
| `repository/product_repo.py` | ProductRepository 인터페이스 (ABC). |
| `repository/warehouse_repo.py` | WarehouseRepository 인터페이스 (ABC). |
| `repository/stock_repo.py` | StockRepository 인터페이스 (ABC). product_id+warehouse_id로 조회하는 메서드를 정의한다. |
| `event/stock_events.py` | StockReceivedEvent, StockReleasedEvent, StockDepletedEvent 도메인 이벤트 클래스들. |
| `service/stock_deduction/stock_deduction_service.py` | 여러 Stock 애그리거트에 걸친 재고 차감 로직을 수행하는 도메인 서비스. 주문 항목이 여러 창고에 분산되어 있을 때 차감 순서를 결정한다. |

**application_layer/ -- 유스케이스 조율**

| 파일 | 역할 |
|------|------|
| `inventory_service.py` | 입고/출고 유스케이스를 조율한다. 리포지토리에서 애그리거트를 조회하고, 도메인 메서드를 호출하고, 저장한다. 비즈니스 로직은 직접 구현하지 않는다. |
| `event_handlers.py` | 주문 컨텍스트의 `OrderPlacedEvent`를 구독하여 재고 차감을 트리거한다. `OrderCancelledEvent`를 구독하여 재고를 복원한다. |

**infra_layer/ -- 프레임워크 의존**

| 파일 | 역할 |
|------|------|
| `django_inventory/apps.py` | Django 앱 설정. `INSTALLED_APPS`에 등록하는 진입점. |
| `django_inventory/models/product_model.py` | ProductModel ORM 모델. `Model` 접미사를 사용한다. 도메인 엔티티와의 변환 책임을 가진다. |
| `django_inventory/models/warehouse_model.py` | WarehouseModel ORM 모델. |
| `django_inventory/models/stock_model.py` | StockModel ORM 모델. product, warehouse FK와 수량 필드를 가진다. |
| `repository/product_repo.py` | DjangoProductRepository -- ProductRepository(ABC) 구현체. ORM과 도메인 모델 간 변환을 수행한다. |
| `repository/warehouse_repo.py` | DjangoWarehouseRepository -- WarehouseRepository(ABC) 구현체. |
| `repository/stock_repo.py` | DjangoStockRepository -- StockRepository(ABC) 구현체. |
| `event_bus/signal_event_bus.py` | 도메인 이벤트를 Django signals로 변환하여 디스패치한다. |

**presentation_layer/ -- API 인터페이스**

| 파일 | 역할 |
|------|------|
| `routers.py` | 재고 도메인의 URL 라우터 등록. |
| `api/product_api.py` | 상품 CRUD API 엔드포인트. |
| `api/warehouse_api.py` | 창고 CRUD API 엔드포인트. |
| `api/stock_api.py` | 입고/출고 API 엔드포인트. |
| `schema/` | 요청/응답 스키마 정의. |

#### ordering/ (주문 바운디드 컨텍스트)

**domain_layer/**

| 파일 | 역할 |
|------|------|
| `order/order.py` | Order 애그리거트 루트. 주문 생성, 취소 비즈니스 로직을 캡슐화한다. "최소 1개 주문항목" 불변식을 보호한다. |
| `order/order_item.py` | OrderItem 값 객체. 주문 항목의 상품 참조, 수량, 가격을 표현한다. |
| `order/order_status.py` | OrderStatus 열거형 값 객체. 상태 전이 규칙을 캡슐화한다. |
| `repository/order_repo.py` | OrderRepository 인터페이스 (ABC). OrderItem은 별도 리포지토리 없이 Order와 함께 관리된다. |
| `event/order_events.py` | OrderPlacedEvent, OrderCancelledEvent 도메인 이벤트 클래스들. |

**application_layer/**

| 파일 | 역할 |
|------|------|
| `order_service.py` | 주문 생성/취소 유스케이스를 조율한다. Order 애그리거트를 생성하고, 리포지토리에 저장하고, 도메인 이벤트를 수집하여 디스패치한다. |

**infra_layer/**

| 파일 | 역할 |
|------|------|
| `django_ordering/models/order_model.py` | OrderModel ORM 모델. |
| `django_ordering/models/order_item_model.py` | OrderItemModel ORM 모델. OrderModel에 FK로 연결된다. |
| `repository/order_repo.py` | DjangoOrderRepository -- OrderRepository(ABC) 구현체. Order와 OrderItem을 함께 저장/조회한다. |
| `event_bus/signal_event_bus.py` | 도메인 이벤트를 Django signals로 변환하여 디스패치한다. |

---

## 4. 핵심 파일 코드 스켈레톤

### 4.1 Stock 애그리거트 루트 (`inventory/domain_layer/stock/stock.py`)

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List
from uuid import uuid4

from applications.inventory.domain_layer.stock.quantity import Quantity
from applications.inventory.domain_layer.event.stock_events import (
    StockDepletedEvent,
    StockReceivedEvent,
    StockReleasedEvent,
)


@dataclass
class Stock:
    """Stock 애그리거트 루트

    - 특정 상품(product_id) + 창고(warehouse_id) 조합의 재고를 관리한다
    - Product, Warehouse는 ID로만 참조한다 (Vernon 규칙 3)
    - 불변식: 재고 수량은 0 미만이 될 수 없다
    - 재고 부족 임계값 이하일 때 StockDepletedEvent를 발행한다
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    product_id: str = ""
    warehouse_id: str = ""
    _quantity: Quantity = field(default_factory=lambda: Quantity(0))
    _low_stock_threshold: int = 10
    _events: List = field(default_factory=list)

    @property
    def quantity(self) -> int:
        return self._quantity.value

    def receive(self, amount: int) -> None:
        """입고 -- 재고 수량을 증가시킨다"""
        if amount <= 0:
            raise ValueError("입고 수량은 0보다 커야 합니다")

        self._quantity = self._quantity.add(amount)

        self._events.append(
            StockReceivedEvent(
                stock_id=self.id,
                product_id=self.product_id,
                warehouse_id=self.warehouse_id,
                amount=amount,
                resulting_quantity=self._quantity.value,
            )
        )

    def release(self, amount: int) -> None:
        """출고 -- 재고 수량을 감소시킨다

        불변식: 출고 후 재고가 0 미만이 되면 안 된다.
        재고가 임계값 이하로 떨어지면 StockDepletedEvent를 발행한다.
        """
        if amount <= 0:
            raise ValueError("출고 수량은 0보다 커야 합니다")
        if amount > self._quantity.value:
            raise ValueError(
                f"재고 부족: 현재 {self._quantity.value}개, "
                f"요청 {amount}개"
            )

        self._quantity = self._quantity.subtract(amount)

        self._events.append(
            StockReleasedEvent(
                stock_id=self.id,
                product_id=self.product_id,
                warehouse_id=self.warehouse_id,
                amount=amount,
                resulting_quantity=self._quantity.value,
            )
        )

        if self._quantity.value <= self._low_stock_threshold:
            self._events.append(
                StockDepletedEvent(
                    stock_id=self.id,
                    product_id=self.product_id,
                    warehouse_id=self.warehouse_id,
                    remaining_quantity=self._quantity.value,
                    threshold=self._low_stock_threshold,
                )
            )

    def has_sufficient_stock(self, required: int) -> bool:
        """요청 수량만큼의 재고가 있는지 확인한다"""
        return self._quantity.value >= required

    def collect_domain_events(self) -> List:
        """수집된 도메인 이벤트를 반환하고 내부 리스트를 비운다"""
        events = list(self._events)
        self._events.clear()
        return events
```

### 4.2 Quantity 값 객체 (`inventory/domain_layer/stock/quantity.py`)

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Quantity:
    """수량 값 객체

    - 불변(frozen=True)이며, 연산 시 새 객체를 반환한다
    - 음수 불가 불변식을 자체 검증한다
    """

    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError(f"수량은 0 이상이어야 합니다: {self.value}")

    def add(self, amount: int) -> Quantity:
        return Quantity(value=self.value + amount)

    def subtract(self, amount: int) -> Quantity:
        return Quantity(value=self.value - amount)
```

### 4.3 재고 도메인 이벤트 (`inventory/domain_layer/event/stock_events.py`)

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class StockReceivedEvent:
    """입고 완료 이벤트 -- 상품이 창고에 입고되었음을 나타낸다"""

    stock_id: str = ""
    product_id: str = ""
    warehouse_id: str = ""
    amount: int = 0
    resulting_quantity: int = 0
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class StockReleasedEvent:
    """출고 완료 이벤트 -- 상품이 창고에서 출고되었음을 나타낸다"""

    stock_id: str = ""
    product_id: str = ""
    warehouse_id: str = ""
    amount: int = 0
    resulting_quantity: int = 0
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class StockDepletedEvent:
    """재고 부족 이벤트 -- 재고가 임계값 이하로 떨어졌음을 나타낸다

    구독자(알림 서비스 등)가 이 이벤트를 받아 알림을 발송한다.
    """

    stock_id: str = ""
    product_id: str = ""
    warehouse_id: str = ""
    remaining_quantity: int = 0
    threshold: int = 0
    occurred_at: datetime = field(default_factory=datetime.now)
```

### 4.4 StockRepository 인터페이스 (`inventory/domain_layer/repository/stock_repo.py`)

```python
from abc import ABC, abstractmethod
from typing import List, Optional

from applications.inventory.domain_layer.stock.stock import Stock


class StockRepository(ABC):
    """Stock 리포지토리 인터페이스

    - 애그리거트 단위로 저장/조회한다
    - 인프라 계층에서 DjangoStockRepository로 구현한다
    """

    @abstractmethod
    def find_by_id(self, stock_id: str) -> Optional[Stock]:
        ...

    @abstractmethod
    def find_by_product_and_warehouse(
        self, product_id: str, warehouse_id: str
    ) -> Optional[Stock]:
        """특정 상품+창고 조합의 재고를 조회한다"""
        ...

    @abstractmethod
    def find_by_product_id(self, product_id: str) -> List[Stock]:
        """특정 상품의 모든 창고 재고를 조회한다"""
        ...

    @abstractmethod
    def save(self, stock: Stock) -> None:
        ...

    @abstractmethod
    def delete(self, stock: Stock) -> None:
        ...
```

### 4.5 Order 애그리거트 루트 (`ordering/domain_layer/order/order.py`)

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List
from uuid import uuid4

from applications.ordering.domain_layer.order.order_item import OrderItem
from applications.ordering.domain_layer.order.order_status import OrderStatus
from applications.ordering.domain_layer.event.order_events import (
    OrderCancelledEvent,
    OrderPlacedEvent,
)


@dataclass
class Order:
    """Order 애그리거트 루트

    - OrderItem(값 객체)을 내부 구성요소로 포함한다
    - 불변식: 최소 1개 이상의 주문항목이 있어야 한다
    - 모든 상태 변경은 Order를 통해서만 수행한다
    - Product는 product_id로만 참조한다 (Vernon 규칙 3)
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    orderer_id: str = ""
    items: List[OrderItem] = field(default_factory=list)
    _status: OrderStatus = field(default=OrderStatus.PLACED)
    _events: List = field(default_factory=list)

    def __post_init__(self) -> None:
        self._verify_at_least_one_item()
        self._calculate_total_amount()

    def _verify_at_least_one_item(self) -> None:
        if not self.items:
            raise ValueError("최소 한 개 이상의 주문항목이 필요합니다")

    def _calculate_total_amount(self) -> None:
        self._total_amount = sum(item.subtotal for item in self.items)

    @property
    def status(self) -> OrderStatus:
        return self._status

    @property
    def total_amount(self) -> int:
        return self._total_amount

    def place(self) -> None:
        """주문 확정 -- OrderPlacedEvent를 발행하여 재고 차감을 트리거한다

        결과적 일관성: 재고 차감은 이벤트 핸들러에서 별도 트랜잭션으로
        처리한다 (Vernon 규칙 4).
        """
        if self._status != OrderStatus.PLACED:
            raise ValueError(
                f"{self._status.value} 상태에서는 주문을 확정할 수 없습니다"
            )

        self._status = OrderStatus.CONFIRMED

        self._events.append(
            OrderPlacedEvent(
                order_id=self.id,
                orderer_id=self.orderer_id,
                items=[
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                    }
                    for item in self.items
                ],
                total_amount=self._total_amount,
            )
        )

    def cancel(self) -> None:
        """주문 취소 -- OrderCancelledEvent를 발행하여 재고 복원을 트리거한다"""
        if not self._status.is_cancellable:
            raise ValueError(
                f"{self._status.value} 상태에서는 주문을 취소할 수 없습니다"
            )

        self._status = OrderStatus.CANCELLED

        self._events.append(
            OrderCancelledEvent(
                order_id=self.id,
                items=[
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                    }
                    for item in self.items
                ],
            )
        )

    def collect_domain_events(self) -> List:
        """수집된 도메인 이벤트를 반환하고 내부 리스트를 비운다"""
        events = list(self._events)
        self._events.clear()
        return events
```

### 4.6 OrderItem 값 객체 (`ordering/domain_layer/order/order_item.py`)

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OrderItem:
    """주문 항목 값 객체

    - 불변(frozen=True)이며, 속성 조합으로 동등성을 판단한다
    - Product를 ID로만 참조한다 (Vernon 규칙 3)
    - 자체 라이프사이클이 없으므로 값 객체로 설계한다
    """

    product_id: str
    product_name: str
    quantity: int
    unit_price: int

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("주문 수량은 0보다 커야 합니다")
        if self.unit_price < 0:
            raise ValueError("단가는 0 이상이어야 합니다")

    @property
    def subtotal(self) -> int:
        return self.quantity * self.unit_price
```

### 4.7 OrderStatus 값 객체 (`ordering/domain_layer/order/order_status.py`)

```python
from enum import Enum


class OrderStatus(Enum):
    """주문 상태 열거형 -- 상태 전이 규칙을 캡슐화한다"""

    PLACED = "placed"
    CONFIRMED = "confirmed"
    SHIPPING = "shipping"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

    @property
    def is_cancellable(self) -> bool:
        """취소 가능 여부 -- PLACED와 CONFIRMED 상태에서만 취소할 수 있다"""
        return self in (OrderStatus.PLACED, OrderStatus.CONFIRMED)
```

### 4.8 주문 도메인 이벤트 (`ordering/domain_layer/event/order_events.py`)

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class OrderPlacedEvent:
    """주문 확정 이벤트

    재고 컨텍스트의 이벤트 핸들러가 구독하여 재고를 차감한다.
    items에 각 주문항목의 product_id와 quantity를 포함한다.
    """

    order_id: str = ""
    orderer_id: str = ""
    items: List[dict] = field(default_factory=list)
    total_amount: int = 0
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class OrderCancelledEvent:
    """주문 취소 이벤트

    재고 컨텍스트의 이벤트 핸들러가 구독하여 재고를 복원한다.
    """

    order_id: str = ""
    items: List[dict] = field(default_factory=list)
    occurred_at: datetime = field(default_factory=datetime.now)
```

### 4.9 OrderRepository 인터페이스 (`ordering/domain_layer/repository/order_repo.py`)

```python
from abc import ABC, abstractmethod
from typing import List, Optional

from applications.ordering.domain_layer.order.order import Order


class OrderRepository(ABC):
    """Order 리포지토리 인터페이스

    - Order 애그리거트 단위로 저장/조회한다
    - OrderItem을 위한 별도 리포지토리는 만들지 않는다
    """

    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[Order]:
        ...

    @abstractmethod
    def find_by_orderer_id(self, orderer_id: str) -> List[Order]:
        ...

    @abstractmethod
    def save(self, order: Order) -> None:
        ...

    @abstractmethod
    def delete(self, order: Order) -> None:
        ...
```

### 4.10 재고 컨텍스트 이벤트 핸들러 (`inventory/application_layer/event_handlers.py`)

```python
from applications.inventory.domain_layer.repository.stock_repo import (
    StockRepository,
)
from applications.ordering.domain_layer.event.order_events import (
    OrderCancelledEvent,
    OrderPlacedEvent,
)


class InventoryEventHandler:
    """주문 컨텍스트의 도메인 이벤트를 구독하여 재고를 관리한다

    - 타 도메인의 application_layer 서비스만 import 허용이지만,
      이벤트 클래스는 Published Language로서 import를 허용한다
    - 각 핸들러는 별도 트랜잭션에서 실행된다 (결과적 일관성)
    """

    def __init__(self, stock_repo: StockRepository) -> None:
        self._stock_repo = stock_repo

    def handle_order_placed(self, event: OrderPlacedEvent) -> None:
        """주문 확정 시 재고 차감 -- 별도 트랜잭션에서 결과적 일관성으로 처리"""
        for item in event.items:
            stocks = self._stock_repo.find_by_product_id(item["product_id"])
            remaining = item["quantity"]

            for stock in stocks:
                if remaining <= 0:
                    break
                available = min(remaining, stock.quantity)
                stock.release(available)
                self._stock_repo.save(stock)
                remaining -= available

            if remaining > 0:
                raise ValueError(
                    f"재고 부족: product_id={item['product_id']}, "
                    f"부족 수량={remaining}"
                )

    def handle_order_cancelled(self, event: OrderCancelledEvent) -> None:
        """주문 취소 시 재고 복원 -- 보상 트랜잭션"""
        for item in event.items:
            stocks = self._stock_repo.find_by_product_id(item["product_id"])
            if stocks:
                stocks[0].receive(item["quantity"])
                self._stock_repo.save(stocks[0])
```

---

## 5. 설계 결정 요약

| 결정 사항 | 적용 원칙 | 근거 |
|----------|----------|------|
| 재고/주문을 별도 바운디드 컨텍스트로 분리 | 전략 설계 우선 | "상품"의 의미가 두 컨텍스트에서 다르다. 유비쿼터스 언어의 경계가 바운디드 컨텍스트 경계이다. |
| Stock, Product, Warehouse를 각각 독립 애그리거트로 설계 | Vernon 규칙 2 (작은 애그리거트) | 하나의 거대 애그리거트로 묶으면 입고 시 Product 전체를 로딩해야 하는 성능 문제가 발생한다. |
| Stock이 product_id, warehouse_id로 참조 | Vernon 규칙 3 (ID 참조) | 직접 객체 참조 대신 ID 참조로 결합도를 낮추고, 로딩 시간과 메모리 사용을 줄인다. |
| OrderItem을 값 객체로 설계 | 값 객체 우선 원칙 | 자체 라이프사이클이 없고, 속성 조합으로 식별하며, 불변이다. |
| 주문 확정 시 재고 차감을 도메인 이벤트로 연동 | Vernon 규칙 4 (결과적 일관성) | Order와 Stock은 서로 다른 애그리거트이므로, 같은 트랜잭션에서 수정하지 않는다. |
| 재고 부족 알림을 StockDepletedEvent로 구현 | 도메인 이벤트 패턴 | Stock 애그리거트는 알림 전송을 몰라도 되며, 이벤트 구독자가 처리한다. |
| OrderItem 별도 리포지토리 없음 | 애그리거트 단위 리포지토리 | OrderItem은 Order 애그리거트의 내부 구성요소이므로 OrderRepository가 함께 관리한다. |
| 비즈니스 로직은 엔티티/값 객체 내부에 위치 | 풍부한 도메인 모델 (빈혈 모델 안티패턴 회피) | `stock.receive()`, `stock.release()`, `order.place()`, `order.cancel()` 등 비즈니스 의도를 드러내는 메서드명을 사용한다. |
| Django 앱은 infra_layer 내부에 배치 | DDD + Django 구조 규칙 | 도메인 모델이 프레임워크에 의존하지 않도록, Django ORM은 인프라 계층에 격리한다. |
