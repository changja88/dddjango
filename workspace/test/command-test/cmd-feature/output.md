# 주문(Order) 기능 설계 및 구현

> 요청: 주문 생성, 조회, 확정, 취소 기능
> TDD: No
> 적용 스킬: architecture-ddd, architecture-implementation-patterns, architecture-db, architecture-api, implementation-django-ninja, implementation-cleancode, implementation-python, implementation-django

---

## Phase 1: 도메인 설계 (architecture-ddd Design 모드)

### 1.1 서브도메인 분류

| 서브도메인 | 유형 | 설명 |
|-----------|------|------|
| 주문(Ordering) | Core | 주문 생성, 확정, 취소 -- 비즈니스 핵심 프로세스 |
| 상품(Catalog) | Supporting | 주문에 포함될 상품 정보 제공 |
| 회원(Identity) | Generic | 주문자 식별 및 인증 |

### 1.2 바운디드 컨텍스트

**주문(Ordering) 바운디드 컨텍스트** -- 이번 기능의 범위

컨텍스트 맵:
- Ordering --> Identity: Customer-Supplier (회원 ID만 참조)
- Ordering --> Catalog: Customer-Supplier (상품 ID, 이름, 가격을 스냅샷으로 보관)

### 1.3 유비쿼터스 언어

| 용어 | 정의 |
|------|------|
| 주문(Order) | 고객이 하나 이상의 상품을 구매하기 위해 생성하는 거래 단위 |
| 주문 항목(OrderLine) | 주문에 포함된 개별 상품의 수량과 가격 |
| 주문 생성(place) | 고객이 주문을 접수하는 행위 |
| 주문 확정(confirm) | 관리자 또는 시스템이 주문을 확정하는 행위 |
| 주문 취소(cancel) | 주문을 무효화하는 행위 |
| 주문 상태(OrderStatus) | PLACED, CONFIRMED, CANCELLED |
| 총 금액(total_amount) | 주문 항목 금액의 합계 |

### 1.4 애그리거트 설계

**Order 애그리거트** (루트: Order)

구성요소:
- `Order` -- 애그리거트 루트 (엔티티)
- `OrderLine` -- 값 객체 (상품 스냅샷 + 수량)
- `OrderStatus` -- 값 객체 (열거형)
- `Money` -- 공유 값 객체 (Shared Kernel)

설계 규칙 (Vernon의 4가지 규칙 적용):
1. **불변식 보호**: 주문은 최소 1개 항목 필수, 총 금액은 항상 항목 합계와 일치
2. **작은 애그리거트**: Order + OrderLine + Status만 포함
3. **ID 참조**: orderer_id(회원), product_id(상품)는 ID로만 참조
4. **결과적 일관성**: 주문 확정/취소 시 도메인 이벤트 발행

### 1.5 도메인 이벤트

| 이벤트 | 발생 시점 | 용도 |
|--------|----------|------|
| `OrderPlacedEvent` | 주문 생성 시 | 재고 확인, 알림 등 |
| `OrderConfirmedEvent` | 주문 확정 시 | 결제 처리, 배송 준비 등 |
| `OrderCancelledEvent` | 주문 취소 시 | 재고 복원, 환불 등 |

### 1.6 도메인 모델 코드

```python
# applications/ordering/domain_layer/order/order_status.py
from enum import Enum


class OrderStatus(Enum):
    PLACED = "placed"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

    @property
    def is_cancellable(self) -> bool:
        return self == OrderStatus.PLACED

    @property
    def is_confirmable(self) -> bool:
        return self == OrderStatus.PLACED
```

```python
# applications/shared_kernel/value_object/money.py
from dataclasses import dataclass, replace


@dataclass(frozen=True, slots=True)
class Money:
    """금액 값 객체"""

    amount: int
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError(f"금액은 0 이상이어야 합니다: {self.amount}")

    def add(self, other: "Money") -> "Money":
        self._ensure_same_currency(other)
        return replace(self, amount=self.amount + other.amount)

    def multiply(self, factor: int) -> "Money":
        return replace(self, amount=self.amount * factor)

    def _ensure_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError(f"통화 불일치: {self.currency} != {other.currency}")
```

```python
# applications/ordering/domain_layer/order/order_line.py
from dataclasses import dataclass

from applications.shared_kernel.value_object.money import Money


@dataclass(frozen=True, slots=True)
class OrderLine:
    """주문 항목 값 객체 -- 주문 시점의 상품 스냅샷"""

    product_id: str
    product_name: str
    price: Money
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity < 1:
            raise ValueError("수량은 1 이상이어야 합니다")

    @property
    def line_amount(self) -> Money:
        return self.price.multiply(self.quantity)
```

```python
# applications/ordering/domain_layer/event/order_events.py
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class OrderPlacedEvent:
    order_id: str
    orderer_id: str
    total_amount: int
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class OrderConfirmedEvent:
    order_id: str
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class OrderCancelledEvent:
    order_id: str
    reason: str = ""
    occurred_at: datetime = field(default_factory=datetime.now)
```

```python
# applications/ordering/domain_layer/order/order.py
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from applications.shared_kernel.value_object.money import Money

from .order_line import OrderLine
from .order_status import OrderStatus
from ..event.order_events import (
    OrderCancelledEvent,
    OrderConfirmedEvent,
    OrderPlacedEvent,
)


@dataclass
class Order:
    """주문 애그리거트 루트

    - 모든 상태 변경은 이 루트를 통해서만 수행한다
    - 다른 애그리거트(회원, 상품)는 ID로만 참조한다
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    orderer_id: str = ""
    order_lines: list[OrderLine] = field(default_factory=list)
    _status: OrderStatus = field(default=OrderStatus.PLACED)
    _total_amount: Money = field(default_factory=lambda: Money(0))
    created_at: datetime = field(default_factory=datetime.now)
    _events: list = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        self._verify_at_least_one_line()
        self._calculate_total_amount()

    def _verify_at_least_one_line(self) -> None:
        if not self.order_lines:
            raise ValueError("최소 한 개의 주문 항목이 필요합니다")

    def _calculate_total_amount(self) -> None:
        total = Money(0)
        for line in self.order_lines:
            total = total.add(line.line_amount)
        self._total_amount = total

    @property
    def status(self) -> OrderStatus:
        return self._status

    @property
    def total_amount(self) -> Money:
        return self._total_amount

    def place(self) -> None:
        """주문 접수 -- 생성 직후 호출"""
        self._events.append(
            OrderPlacedEvent(
                order_id=self.id,
                orderer_id=self.orderer_id,
                total_amount=self._total_amount.amount,
            )
        )

    def confirm(self) -> None:
        """주문 확정"""
        if not self._status.is_confirmable:
            raise ValueError(
                f"{self._status.value} 상태에서는 확정할 수 없습니다"
            )
        self._status = OrderStatus.CONFIRMED
        self._events.append(OrderConfirmedEvent(order_id=self.id))

    def cancel(self, reason: str = "") -> None:
        """주문 취소"""
        if not self._status.is_cancellable:
            raise ValueError(
                f"{self._status.value} 상태에서는 취소할 수 없습니다"
            )
        self._status = OrderStatus.CANCELLED
        self._events.append(
            OrderCancelledEvent(order_id=self.id, reason=reason)
        )

    def collect_domain_events(self) -> list:
        events = list(self._events)
        self._events.clear()
        return events
```

```python
# applications/ordering/domain_layer/repository/order_repo.py
from abc import ABC, abstractmethod

from ..order.order import Order


class OrderRepository(ABC):
    """주문 리포지토리 인터페이스 -- 애그리거트 단위"""

    @abstractmethod
    def find_by_id(self, order_id: str) -> Order | None: ...

    @abstractmethod
    def find_by_orderer_id(self, orderer_id: str) -> list[Order]: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...
```

---

## Phase 2: 아키텍처 선택 (architecture-implementation-patterns Design 모드)

### 2.1 복잡도 평가

주문 기능은 명확한 비즈니스 규칙(상태 전이, 불변식)이 있으나, 외부 통합이 제한적이다. 단순 CRUD를 넘어서지만 다수의 외부 시스템 연동은 없다.

**선택: 레이어드 아키텍처 + DIP**

헥사고날까지는 불필요하지만, 도메인 모델이 인프라에 의존하지 않도록 DIP를 적용한다. 리포지토리 인터페이스를 도메인 계층에 정의하고 인프라 계층에서 구현한다.

### 2.2 의존성 방향

```
Presentation (API) --> Application (서비스) --> Domain (모델, 리포지토리 인터페이스)
                                                       ^
                                                       |
                                             Infrastructure (Django ORM 구현)
```

도메인 계층은 Django ORM에 의존하지 않는다. 인프라 계층이 도메인의 리포지토리 인터페이스를 구현한다.

### 2.3 프로젝트 폴더 구조

```
applications/
├── shared_kernel/
│   └── value_object/
│       └── money.py                     # Money 값 객체
│
└── ordering/                            # Bounded Context
    ├── domain_layer/
    │   ├── order/                       # Order 애그리거트
    │   │   ├── order.py                 # 애그리거트 루트
    │   │   ├── order_line.py            # OrderLine 값 객체
    │   │   └── order_status.py          # OrderStatus 열거형
    │   ├── repository/
    │   │   └── order_repo.py            # OrderRepository ABC
    │   └── event/
    │       └── order_events.py          # 도메인 이벤트
    │
    ├── application_layer/
    │   └── order_service.py             # 응용 서비스 (유스케이스 조율)
    │
    ├── infra_layer/
    │   ├── django_ordering/             # Django 앱
    │   │   ├── apps.py
    │   │   └── models/
    │   │       ├── __init__.py
    │   │       └── order_model.py       # ORM 모델
    │   └── repository/
    │       └── order_repo.py            # DjangoOrderRepository
    │
    ├── presentation_layer/
    │   ├── routers.py                   # 라우터 등록
    │   ├── api/
    │   │   └── order_api.py             # 주문 엔드포인트
    │   └── schema/
    │       └── order_schema.py          # 요청/응답 스키마
    │
    └── tests/
        ├── domain/
        ├── application/
        ├── infra/
        └── api/
```

---

## Phase 3: DB 스키마 설계 (architecture-db Design 모드)

### 3.1 개념적 모델 (ERD)

```
[Order] 1 --- N [OrderLineItem]
   |
   |-- id (PK, UUID)
   |-- orderer_id (FK to users, NOT NULL)
   |-- status (VARCHAR, NOT NULL)
   |-- total_amount (INTEGER, NOT NULL)
   |-- currency (VARCHAR, NOT NULL, DEFAULT 'KRW')
   |-- created_at (TIMESTAMP, NOT NULL)
   |-- updated_at (TIMESTAMP, NOT NULL)

[OrderLineItem]
   |-- id (PK, BigAutoField)
   |-- order_id (FK to Order, NOT NULL)
   |-- product_id (VARCHAR, NOT NULL)
   |-- product_name (VARCHAR, NOT NULL)
   |-- price (INTEGER, NOT NULL)
   |-- quantity (INTEGER, NOT NULL)
```

### 3.2 정규화 수준

3NF를 적용한다:
- `total_amount`는 파생 컬럼이지만, 주문 이후 상품 가격이 변경되더라도 주문 시점 금액을 보존해야 하므로 의도적 비정규화(스냅샷)이다.
- `product_name`, `price`는 주문 시점의 스냅샷으로, 상품 테이블과의 이행 종속이 아니다.

### 3.3 인덱스 전략

| 인덱스 | 컬럼 | 근거 |
|--------|------|------|
| `idx_order_orderer_status` | (orderer_id, status) | "내 주문 목록" 조회 -- 등호 조건 우선 |
| `idx_order_status_created` | (status, created_at) | "상태별 주문 목록" 관리자 조회 |
| `idx_orderline_order` | (order_id) | FK 조인 최적화 |

### 3.4 Django ORM 모델

```python
# applications/ordering/infra_layer/django_ordering/models/order_model.py
from django.conf import settings
from django.db import models


class OrderStatus(models.TextChoices):
    PLACED = "placed", "접수됨"
    CONFIRMED = "confirmed", "확정됨"
    CANCELLED = "cancelled", "취소됨"


class OrderModel(models.Model):
    """주문 ORM 모델"""

    id = models.UUIDField(primary_key=True)
    orderer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PLACED,
        db_index=False,  # 복합 인덱스 사용
    )
    total_amount = models.PositiveIntegerField()
    currency = models.CharField(max_length=3, default="KRW")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["orderer", "status"],
                name="idx_order_orderer_status",
            ),
            models.Index(
                fields=["status", "created_at"],
                name="idx_order_status_created",
            ),
        ]

    def __str__(self) -> str:
        return f"Order({self.id}, {self.status})"


class OrderLineItemModel(models.Model):
    """주문 항목 ORM 모델"""

    order = models.ForeignKey(
        OrderModel,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    product_id = models.CharField(max_length=100)
    product_name = models.CharField(max_length=255)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()

    class Meta:
        db_table = "order_line_items"
        indexes = [
            models.Index(fields=["order"], name="idx_orderline_order"),
        ]

    def __str__(self) -> str:
        return f"OrderLine({self.product_name} x {self.quantity})"
```

---

## Phase 4: REST API 설계 (architecture-api Design 모드)

### 4.1 리소스 및 URL 구조

| 메서드 | URL | 설명 | 상태 코드 |
|--------|-----|------|----------|
| `POST` | `/api/v1/orders` | 주문 생성 | 201 Created |
| `GET` | `/api/v1/orders` | 주문 목록 조회 | 200 OK |
| `GET` | `/api/v1/orders/{order_id}` | 주문 상세 조회 | 200 OK |
| `POST` | `/api/v1/orders/{order_id}/confirm` | 주문 확정 | 200 OK |
| `POST` | `/api/v1/orders/{order_id}/cancel` | 주문 취소 | 200 OK |

> confirm/cancel은 단순 PATCH가 아니라 비즈니스 의미가 있는 행위이므로 POST + 행위 URL을 사용한다. 이는 REST 원칙의 실용적 예외이다.

### 4.2 요청/응답 설계

**POST /api/v1/orders (주문 생성)**

요청:
```json
{
  "items": [
    {
      "product_id": "prod-001",
      "product_name": "상품A",
      "price": 10000,
      "quantity": 2
    }
  ]
}
```

응답 (201):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "orderer_id": "user-123",
  "status": "placed",
  "total_amount": 20000,
  "lines": [
    {
      "product_id": "prod-001",
      "product_name": "상품A",
      "price": 10000,
      "quantity": 2,
      "line_amount": 20000
    }
  ],
  "created_at": "2026-04-05T10:00:00Z"
}
```

**GET /api/v1/orders (주문 목록)**

쿼리 파라미터: `?status=placed&limit=20&offset=0`

응답 (200):
```json
{
  "items": [
    {
      "id": "550e8400-...",
      "status": "placed",
      "total_amount": 20000,
      "created_at": "2026-04-05T10:00:00Z"
    }
  ],
  "count": 42
}
```

**POST /api/v1/orders/{order_id}/cancel (주문 취소)**

요청:
```json
{
  "reason": "고객 변심"
}
```

### 4.3 에러 응답 (RFC 9457)

```json
{
  "type": "https://api.example.com/probs/order-not-cancellable",
  "title": "Order cannot be cancelled",
  "status": 409,
  "detail": "confirmed 상태에서는 취소할 수 없습니다",
  "instance": "/api/v1/orders/550e8400-.../cancel"
}
```

| 상황 | 상태 코드 |
|------|----------|
| 주문 생성 성공 | 201 Created |
| 조회 성공 | 200 OK |
| 확정/취소 성공 | 200 OK |
| 존재하지 않는 주문 | 404 Not Found |
| 상태 전이 불가 | 409 Conflict |
| 유효성 검증 실패 | 422 Unprocessable Entity |

### 4.4 페이지네이션

목록 엔드포인트에 LimitOffset 페이지네이션을 적용한다. 기본값: limit=20, offset=0.

---

## Phase 5: Django Ninja 구현 (implementation-django-ninja Writing 모드)

### 5.1 Schema 정의

```python
# applications/ordering/presentation_layer/schema/order_schema.py
from datetime import datetime

from ninja import Schema


class OrderLineIn(Schema):
    """주문 항목 입력 스키마"""

    product_id: str
    product_name: str
    price: int
    quantity: int


class OrderCreateIn(Schema):
    """주문 생성 요청"""

    items: list[OrderLineIn]


class OrderCancelIn(Schema):
    """주문 취소 요청"""

    reason: str = ""


class OrderLineOut(Schema):
    """주문 항목 응답"""

    product_id: str
    product_name: str
    price: int
    quantity: int
    line_amount: int


class OrderOut(Schema):
    """주문 상세 응답"""

    id: str
    orderer_id: str
    status: str
    total_amount: int
    lines: list[OrderLineOut]
    created_at: datetime


class OrderListOut(Schema):
    """주문 목록 항목 응답"""

    id: str
    status: str
    total_amount: int
    created_at: datetime
```

### 5.2 응용 서비스

```python
# applications/ordering/application_layer/order_service.py
from django.db import transaction

from ..domain_layer.order.order import Order
from ..domain_layer.order.order_line import OrderLine
from ..domain_layer.repository.order_repo import OrderRepository
from applications.shared_kernel.value_object.money import Money


class OrderApplicationService:
    """주문 응용 서비스 -- 유스케이스 조율만 담당, 비즈니스 로직 없음"""

    def __init__(self, order_repository: OrderRepository) -> None:
        self._order_repo = order_repository

    @transaction.atomic
    def place_order(
        self,
        orderer_id: str,
        items: list[dict],
    ) -> Order:
        """주문 생성"""
        order_lines = [
            OrderLine(
                product_id=item["product_id"],
                product_name=item["product_name"],
                price=Money(amount=item["price"]),
                quantity=item["quantity"],
            )
            for item in items
        ]
        order = Order(orderer_id=orderer_id, order_lines=order_lines)
        order.place()
        self._order_repo.save(order)
        return order

    def get_order(self, order_id: str) -> Order | None:
        """주문 단건 조회"""
        return self._order_repo.find_by_id(order_id)

    def list_orders(self, orderer_id: str) -> list[Order]:
        """주문자별 목록 조회"""
        return self._order_repo.find_by_orderer_id(orderer_id)

    @transaction.atomic
    def confirm_order(self, order_id: str) -> Order:
        """주문 확정"""
        order = self._order_repo.find_by_id(order_id)
        if order is None:
            raise ValueError("주문을 찾을 수 없습니다")
        order.confirm()
        self._order_repo.save(order)
        return order

    @transaction.atomic
    def cancel_order(self, order_id: str, reason: str = "") -> Order:
        """주문 취소"""
        order = self._order_repo.find_by_id(order_id)
        if order is None:
            raise ValueError("주문을 찾을 수 없습니다")
        order.cancel(reason=reason)
        self._order_repo.save(order)
        return order
```

### 5.3 리포지토리 구현

```python
# applications/ordering/infra_layer/repository/order_repo.py
from uuid import UUID

from ..django_ordering.models.order_model import (
    OrderLineItemModel,
    OrderModel,
)
from ...domain_layer.order.order import Order
from ...domain_layer.order.order_line import OrderLine
from ...domain_layer.order.order_status import OrderStatus
from ...domain_layer.repository.order_repo import (
    OrderRepository as OrderRepositoryABC,
)
from applications.shared_kernel.value_object.money import Money


class DjangoOrderRepository(OrderRepositoryABC):
    """Django ORM 기반 주문 리포지토리"""

    def find_by_id(self, order_id: str) -> Order | None:
        try:
            orm_order = (
                OrderModel.objects
                .prefetch_related("lines")
                .get(id=UUID(order_id))
            )
            return self._to_domain(orm_order)
        except OrderModel.DoesNotExist:
            return None

    def find_by_orderer_id(self, orderer_id: str) -> list[Order]:
        orm_orders = (
            OrderModel.objects
            .filter(orderer_id=orderer_id)
            .prefetch_related("lines")
            .order_by("-created_at")
        )
        return [self._to_domain(o) for o in orm_orders]

    def save(self, order: Order) -> None:
        orm_order, created = OrderModel.objects.update_or_create(
            id=UUID(order.id),
            defaults={
                "orderer_id": order.orderer_id,
                "status": order.status.value,
                "total_amount": order.total_amount.amount,
                "currency": order.total_amount.currency,
            },
        )
        if created:
            OrderLineItemModel.objects.bulk_create([
                OrderLineItemModel(
                    order=orm_order,
                    product_id=line.product_id,
                    product_name=line.product_name,
                    price=line.price.amount,
                    quantity=line.quantity,
                )
                for line in order.order_lines
            ])

    def _to_domain(self, orm_order: OrderModel) -> Order:
        order_lines = [
            OrderLine(
                product_id=line.product_id,
                product_name=line.product_name,
                price=Money(amount=line.price),
                quantity=line.quantity,
            )
            for line in orm_order.lines.all()
        ]
        order = object.__new__(Order)
        order.id = str(orm_order.id)
        order.orderer_id = str(orm_order.orderer_id)
        order.order_lines = order_lines
        order._status = OrderStatus(orm_order.status)
        order._total_amount = Money(
            amount=orm_order.total_amount,
            currency=orm_order.currency,
        )
        order.created_at = orm_order.created_at
        order._events = []
        return order
```

### 5.4 Router 및 엔드포인트

```python
# applications/ordering/presentation_layer/api/order_api.py
from django.http import JsonResponse
from ninja import Router
from ninja.errors import HttpError
from ninja.pagination import LimitOffsetPagination, paginate

from ..schema.order_schema import (
    OrderCancelIn,
    OrderCreateIn,
    OrderLineOut,
    OrderListOut,
    OrderOut,
)
from ...application_layer.order_service import OrderApplicationService
from ...infra_layer.repository.order_repo import DjangoOrderRepository

router = Router(tags=["orders"])

_order_service = OrderApplicationService(
    order_repository=DjangoOrderRepository(),
)


def _to_order_out(order) -> dict:
    """도메인 Order를 응답 dict로 변환"""
    return {
        "id": order.id,
        "orderer_id": order.orderer_id,
        "status": order.status.value,
        "total_amount": order.total_amount.amount,
        "lines": [
            {
                "product_id": line.product_id,
                "product_name": line.product_name,
                "price": line.price.amount,
                "quantity": line.quantity,
                "line_amount": line.line_amount.amount,
            }
            for line in order.order_lines
        ],
        "created_at": order.created_at,
    }


@router.post("/", response={201: OrderOut})
def create_order(request, payload: OrderCreateIn):
    """주문 생성"""
    order = _order_service.place_order(
        orderer_id=str(request.auth.id),
        items=[item.dict() for item in payload.items],
    )
    return 201, _to_order_out(order)


@router.get("/", response=list[OrderListOut])
@paginate(LimitOffsetPagination, page_size=20)
def list_orders(request, status: str | None = None):
    """주문 목록 조회"""
    orders = _order_service.list_orders(
        orderer_id=str(request.auth.id),
    )
    if status:
        orders = [o for o in orders if o.status.value == status]
    return [
        {
            "id": o.id,
            "status": o.status.value,
            "total_amount": o.total_amount.amount,
            "created_at": o.created_at,
        }
        for o in orders
    ]


@router.get("/{order_id}", response=OrderOut)
def get_order(request, order_id: str):
    """주문 상세 조회"""
    order = _order_service.get_order(order_id)
    if order is None:
        raise HttpError(404, "주문을 찾을 수 없습니다")
    return _to_order_out(order)


@router.post("/{order_id}/confirm", response=OrderOut)
def confirm_order(request, order_id: str):
    """주문 확정"""
    try:
        order = _order_service.confirm_order(order_id)
    except ValueError as e:
        return JsonResponse(
            {
                "type": "about:blank",
                "title": "Order cannot be confirmed",
                "status": 409,
                "detail": str(e),
                "instance": request.path,
            },
            status=409,
            content_type="application/problem+json",
        )
    return _to_order_out(order)


@router.post("/{order_id}/cancel", response=OrderOut)
def cancel_order(request, order_id: str, payload: OrderCancelIn):
    """주문 취소"""
    try:
        order = _order_service.cancel_order(
            order_id, reason=payload.reason
        )
    except ValueError as e:
        return JsonResponse(
            {
                "type": "about:blank",
                "title": "Order cannot be cancelled",
                "status": 409,
                "detail": str(e),
                "instance": request.path,
            },
            status=409,
            content_type="application/problem+json",
        )
    return _to_order_out(order)
```

### 5.5 라우터 등록

```python
# applications/ordering/presentation_layer/routers.py
from ninja import Router

from .api.order_api import router as order_router

router = Router()
router.add_router("/orders", order_router)
```

```python
# config/api.py (프로젝트 메인)
from ninja import NinjaAPI

from applications.ordering.presentation_layer.routers import (
    router as ordering_router,
)

api = NinjaAPI(version="1.0.0")
api.add_router("/v1/", ordering_router)
```

```python
# config/urls.py
from django.urls import path

from .api import api

urlpatterns = [
    path("api/", api.urls),
]
```

---

## 설계 결정 요약

| 결정 | 선택 | 근거 |
|------|------|------|
| 아키텍처 | Layered + DIP | 복잡도에 비해 헥사고날은 과도, 순수 레이어드는 결합도 높음 |
| 상태 관리 | Enum + 도메인 메서드 | 상태 전이 규칙을 애그리거트 내부에 캡슐화 |
| 가격 저장 | 주문 시점 스냅샷 | 상품 가격 변경과 주문 금액 분리 |
| total_amount | 파생 컬럼 (의도적 비정규화) | 조회 성능 + 스냅샷 보존 |
| 페이지네이션 | LimitOffset | 주문 목록은 최신순 조회가 주 패턴, 데이터 크기 적절 |
| 에러 형식 | RFC 9457 | API 에러 응답 표준화 |
| confirm/cancel URL | POST + 행위 경로 | PATCH 상태 변경보다 비즈니스 의도가 명확 |

---

> **관련 스킬 참조:**
> - [도메인 모델 변경/확장] --> **architecture-ddd** 스킬
> - [아키텍처 패턴 변경 (헥사고날 전환 등)] --> **architecture-implementation-patterns** 스킬
> - [DB 인덱스 튜닝, 쿼리 최적화] --> **architecture-db** 스킬
> - [API 버저닝, 인증, Rate Limiting] --> **architecture-api** 스킬
> - [Django Ninja 인증, 필터링, 비동기] --> **implementation-django-ninja** 스킬
> - [Django ORM 최적화, 마이그레이션] --> **implementation-django** 스킬
> - [타입 힌트, 데코레이터, async] --> **implementation-python** 스킬
> - [SOLID, 리팩토링, 디자인 패턴] --> **implementation-cleancode** 스킬
