# 주문(Order) 도메인 설계부터 Django Ninja 구현까지

> 운영 모드: **설계 모드**
> DDD 설계 모드 원칙에 따라 전략적 설계 -> 전술적 패턴 순서로 진행한다.

---

## Phase 1: 전략적 설계

전략 설계가 전술 패턴보다 반드시 선행해야 한다. 잘못된 경계 안에서 좋은 전술 패턴을 적용해도 복잡성은 해결되지 않는다 (Vernon, DDD Distilled).

### 1.1 도메인과 서브도메인 식별

주문 도메인이 속한 전자상거래 시스템을 기준으로 서브도메인을 분류한다.

| 서브도메인 | 유형 | 설명 | 솔루션 전략 |
|-----------|------|------|------------|
| **주문(Ordering)** | 핵심(Core) | 주문 접수, 상태 관리, 취소 등 비즈니스의 핵심 흐름 | 사내 구현 필수, DDD 도메인 모델 적용 |
| 결제(Payment) | 핵심(Core) | 결제 처리, 환불 | 사내 구현 또는 PG 연동 |
| 상품 카탈로그(Catalog) | 지원(Supporting) | 상품 정보 CRUD | 간소화된 구현 허용 |
| 배송(Shipping) | 지원(Supporting) | 배송 추적, 배송사 연동 | 외부 API 연동 |
| 재고(Inventory) | 지원(Supporting) | 재고 수량 관리, 차감 | 이벤트 기반 연동 |
| 인증(Auth) | 범용(Generic) | 회원 인증, 권한 관리 | 외부 솔루션/라이브러리 |
| 알림(Notification) | 범용(Generic) | 이메일, SMS 발송 | 외부 서비스 |

### 1.2 바운디드 컨텍스트 경계 정의

같은 용어가 다른 의미로 사용되는 지점이 바운디드 컨텍스트의 경계이다.

**주문(Ordering) 바운디드 컨텍스트의 유비쿼터스 언어:**

| 용어 | 정의 | 비고 |
|------|------|------|
| 주문(Order) | 고객이 상품을 구매하기 위해 접수한 요청 | 애그리거트 루트 |
| 주문항목(OrderLine) | 주문 내 개별 상품의 수량과 금액 | 값 객체 |
| 주문자(Orderer) | 주문을 접수한 회원 | 값 객체 (Member ID 참조) |
| 배송정보(ShippingInfo) | 수령인, 연락처, 배송 주소 | 값 객체 |
| 주문 접수(place) | 신규 주문을 생성하여 결제 대기 상태로 전환 | 커맨드 |
| 주문 확정(confirm) | 결제 완료 후 주문을 준비 상태로 전환 | 커맨드 |
| 주문 출고(ship) | 준비 완료된 주문을 배송 시작 상태로 전환 | 커맨드 |
| 주문 취소(cancel) | 출고 전 주문을 취소 | 커맨드 |

### 1.3 컨텍스트 맵

```
[주문 Ordering] --(OHS/Published Language)--> [결제 Payment]
       |
       |---(도메인 이벤트: OrderPlacedEvent)---> [재고 Inventory] (ACL)
       |
       |---(도메인 이벤트: OrderShippedEvent)--> [배송 Shipping] (ACL)
       |
       |---(도메인 이벤트: OrderConfirmedEvent)-> [알림 Notification] (Conformist)
       |
       <--(ACL)--- [상품 카탈로그 Catalog]
       <--(ACL)--- [인증 Auth]
```

**연동 패턴 선택 근거:**
- 주문 -> 재고: ACL. 재고 컨텍스트가 주문 모델에 오염되지 않도록 충돌 방지 계층을 둔다.
- 주문 -> 결제: OHS + Published Language. 결제는 표준화된 API를 제공한다.
- 카탈로그 -> 주문: ACL. 상품 정보를 주문 컨텍스트의 값 객체(OrderLine)로 변환한다.

---

## Phase 2: 전술적 설계 -- 애그리거트 설계

전략적 설계로 경계를 확정한 후, Vernon의 4가지 규칙에 따라 애그리거트를 설계한다.

### 2.1 애그리거트 식별

**Order 애그리거트** (핵심 애그리거트):

```
Order (애그리거트 루트)
├── OrderLine (값 객체, 1..N)
├── ShippingInfo (값 객체, 1)
├── Orderer (값 객체, 1)
├── OrderStatus (값 객체/열거형)
└── Money (값 객체 -- Shared Kernel)
```

**Vernon의 4가지 규칙 적용:**

| 규칙 | 적용 |
|------|------|
| 규칙 1: 진정한 불변식을 일관성 경계로 보호 | "최소 1개 주문항목 필수", "총액 = 항목 합계", "출고 전만 취소 가능" |
| 규칙 2: 작은 애그리거트 설계 | Order + OrderLine + ShippingInfo만 포함. 리뷰, 재고는 별도 애그리거트 |
| 규칙 3: 다른 애그리거트는 ID로 참조 | `orderer_id: str` (Member 참조), `product_id: str` (Product 참조) |
| 규칙 4: 경계 밖은 결과적 일관성 | 재고 차감, 포인트 적립은 도메인 이벤트로 처리 |

### 2.2 값 객체와 엔티티 분류

| 개념 | 분류 | 근거 |
|------|------|------|
| Order | 엔티티 (애그리거트 루트) | 고유 ID, 라이프사이클 존재 |
| OrderLine | 값 객체 | 식별자 불필요, 상품+수량+가격의 조합으로 동등성 판단, 불변 |
| ShippingInfo | 값 객체 | 수령인+주소의 조합, 불변 |
| Orderer | 값 객체 | 주문 시점의 회원 스냅샷 |
| Address | 값 객체 | 도시+거리+우편번호 조합 |
| Money | 값 객체 (Shared Kernel) | 금액+통화, 불변, 부작용 없는 연산 |
| OrderStatus | 열거형 | 상태 전이 규칙을 캡슐화 |

### 2.3 도메인 모델 코드

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4


# === Shared Kernel ===

@dataclass(frozen=True, slots=True)
class Money:
    """금액 값 객체 -- 부작용 없는 함수, 연산의 닫힘"""
    amount: int
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError(f"금액은 0 이상이어야 합니다: {self.amount}")

    def add(self, other: Money) -> Money:
        self._ensure_same_currency(other)
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def subtract(self, other: Money) -> Money:
        self._ensure_same_currency(other)
        if self.amount - other.amount < 0:
            raise ValueError("결과 금액이 음수입니다")
        return Money(amount=self.amount - other.amount, currency=self.currency)

    def multiply(self, factor: int) -> Money:
        return Money(amount=self.amount * factor, currency=self.currency)

    def _ensure_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise ValueError(f"통화 불일치: {self.currency} != {other.currency}")


@dataclass(frozen=True, slots=True)
class Address:
    """주소 값 객체"""
    city: str
    street: str
    zipcode: str

    def __post_init__(self) -> None:
        if not self.zipcode:
            raise ValueError("우편번호는 필수입니다")


# === 도메인 이벤트 ===

@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class OrderPlacedEvent(DomainEvent):
    order_id: str = ""
    orderer_id: str = ""
    total_amount: int = 0


@dataclass(frozen=True)
class OrderConfirmedEvent(DomainEvent):
    order_id: str = ""
    orderer_id: str = ""


@dataclass(frozen=True)
class OrderShippedEvent(DomainEvent):
    order_id: str = ""


@dataclass(frozen=True)
class OrderCancelledEvent(DomainEvent):
    order_id: str = ""
    reason: str = ""


# === 주문 애그리거트 값 객체들 ===

class OrderStatus(Enum):
    """주문 상태 -- 상태 전이 규칙을 캡슐화"""
    PAYMENT_WAITING = "payment_waiting"
    PREPARING = "preparing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

    @property
    def is_cancellable(self) -> bool:
        return self in (OrderStatus.PAYMENT_WAITING, OrderStatus.PREPARING)

    @property
    def is_shippable(self) -> bool:
        return self == OrderStatus.PREPARING


@dataclass(frozen=True, slots=True)
class Orderer:
    """주문자 값 객체 -- 주문 시점의 회원 정보 스냅샷"""
    member_id: str
    name: str


@dataclass(frozen=True, slots=True)
class OrderLine:
    """주문항목 값 객체 -- 불변, 자기 검증"""
    product_id: str
    product_name: str
    price: Money
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity < 1:
            raise ValueError("수량은 1 이상이어야 합니다")

    @property
    def amounts(self) -> Money:
        """항목 소계 -- 부작용 없는 함수"""
        return self.price.multiply(self.quantity)


@dataclass(frozen=True, slots=True)
class ShippingInfo:
    """배송정보 값 객체"""
    receiver_name: str
    receiver_phone: str
    address: Address


# === 주문 애그리거트 루트 ===

@dataclass
class Order:
    """주문 애그리거트 루트

    불변식:
    - 최소 한 개 이상의 주문항목이 존재해야 한다
    - 총액은 주문항목 합계와 일치해야 한다
    - 상태 전이 규칙을 준수해야 한다
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    orderer: Orderer = None
    order_lines: tuple[OrderLine, ...] = ()
    shipping_info: ShippingInfo = None
    _status: OrderStatus = field(default=OrderStatus.PAYMENT_WAITING)
    _total_amounts: Money = field(default=None, init=False)
    _events: list[DomainEvent] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self._verify_at_least_one_order_line()
        self._calculate_total_amounts()

    # --- 불변식 검증 ---

    def _verify_at_least_one_order_line(self) -> None:
        if not self.order_lines:
            raise ValueError("최소 한 개 이상의 상품을 주문해야 합니다")

    def _calculate_total_amounts(self) -> None:
        total = Money(0)
        for line in self.order_lines:
            total = total.add(line.amounts)
        self._total_amounts = total

    # --- 비즈니스 커맨드 (의도를 드러내는 인터페이스) ---

    def place(self) -> None:
        """주문을 접수한다"""
        if self._status != OrderStatus.PAYMENT_WAITING:
            raise ValueError("결제 대기 상태에서만 접수할 수 있습니다")
        self._status = OrderStatus.PREPARING
        self._raise_event(
            OrderPlacedEvent(
                order_id=self.id,
                orderer_id=self.orderer.member_id,
                total_amount=self._total_amounts.amount,
            )
        )

    def confirm(self) -> None:
        """결제 완료 후 주문을 확정한다"""
        if self._status != OrderStatus.PAYMENT_WAITING:
            raise ValueError("결제 대기 상태에서만 확정할 수 있습니다")
        self._status = OrderStatus.PREPARING
        self._raise_event(
            OrderConfirmedEvent(
                order_id=self.id,
                orderer_id=self.orderer.member_id,
            )
        )

    def ship(self) -> None:
        """주문을 출고한다"""
        if not self._status.is_shippable:
            raise ValueError(f"{self._status.value} 상태에서는 출고할 수 없습니다")
        self._status = OrderStatus.SHIPPED
        self._raise_event(OrderShippedEvent(order_id=self.id))

    def deliver(self) -> None:
        """배송을 완료한다"""
        if self._status != OrderStatus.SHIPPED:
            raise ValueError("출고 상태에서만 배송 완료할 수 있습니다")
        self._status = OrderStatus.DELIVERED

    def cancel(self, reason: str = "") -> None:
        """주문을 취소한다"""
        if not self._status.is_cancellable:
            raise ValueError(f"{self._status.value} 상태에서는 취소할 수 없습니다")
        self._status = OrderStatus.CANCELLED
        self._raise_event(
            OrderCancelledEvent(order_id=self.id, reason=reason)
        )

    def change_shipping_info(self, new_info: ShippingInfo) -> None:
        """배송지를 변경한다 -- 출고 전만 가능"""
        if not self._status.is_cancellable:
            raise ValueError("배송지를 변경할 수 없는 상태입니다")
        self.shipping_info = new_info

    # --- 조회 ---

    @property
    def status(self) -> OrderStatus:
        return self._status

    @property
    def total_amounts(self) -> Money:
        return self._total_amounts

    # --- 이벤트 수집 ---

    def _raise_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def collect_domain_events(self) -> list[DomainEvent]:
        events = list(self._events)
        self._events.clear()
        return events
```

### 2.4 리포지토리 인터페이스 (도메인 계층)

```python
from abc import ABC, abstractmethod
from typing import Optional


class OrderRepository(ABC):
    """주문 리포지토리 인터페이스
    - 애그리거트 단위로 저장/조회한다
    - OrderLine을 위한 별도 리포지토리는 만들지 않는다
    """

    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[Order]:
        ...

    @abstractmethod
    def save(self, order: Order) -> None:
        ...

    @abstractmethod
    def delete(self, order: Order) -> None:
        ...

    @abstractmethod
    def find_by_orderer_id(self, orderer_id: str) -> list[Order]:
        ...
```

### 2.5 응용 서비스 (유스케이스 오케스트레이션)

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class PlaceOrderCommand:
    """주문 접수 커맨드"""
    orderer_id: str
    orderer_name: str
    items: list[dict]  # [{"product_id", "product_name", "price", "quantity"}]
    receiver_name: str
    receiver_phone: str
    city: str
    street: str
    zipcode: str


@dataclass(frozen=True)
class CancelOrderCommand:
    """주문 취소 커맨드"""
    order_id: str
    reason: str = ""


class OrderApplicationService:
    """주문 응용 서비스

    - 비즈니스 로직 없이 흐름 제어와 트랜잭션 관리만 담당
    - 도메인 객체에 위임한다
    """

    def __init__(self, order_repository: OrderRepository):
        self._order_repo = order_repository

    def place_order(self, cmd: PlaceOrderCommand) -> str:
        """주문 접수 유스케이스"""
        order_lines = tuple(
            OrderLine(
                product_id=item["product_id"],
                product_name=item["product_name"],
                price=Money(amount=item["price"]),
                quantity=item["quantity"],
            )
            for item in cmd.items
        )

        order = Order(
            orderer=Orderer(
                member_id=cmd.orderer_id,
                name=cmd.orderer_name,
            ),
            order_lines=order_lines,
            shipping_info=ShippingInfo(
                receiver_name=cmd.receiver_name,
                receiver_phone=cmd.receiver_phone,
                address=Address(
                    city=cmd.city,
                    street=cmd.street,
                    zipcode=cmd.zipcode,
                ),
            ),
        )

        order.place()
        self._order_repo.save(order)
        return order.id

    def cancel_order(self, cmd: CancelOrderCommand) -> None:
        """주문 취소 유스케이스"""
        order = self._order_repo.find_by_id(cmd.order_id)
        if order is None:
            raise ValueError("주문을 찾을 수 없습니다")
        order.cancel(reason=cmd.reason)
        self._order_repo.save(order)

    def confirm_order(self, order_id: str) -> None:
        """주문 확정 유스케이스"""
        order = self._order_repo.find_by_id(order_id)
        if order is None:
            raise ValueError("주문을 찾을 수 없습니다")
        order.confirm()
        self._order_repo.save(order)

    def ship_order(self, order_id: str) -> None:
        """주문 출고 유스케이스"""
        order = self._order_repo.find_by_id(order_id)
        if order is None:
            raise ValueError("주문을 찾을 수 없습니다")
        order.ship()
        self._order_repo.save(order)

    def get_order(self, order_id: str) -> Optional[Order]:
        """주문 조회"""
        return self._order_repo.find_by_id(order_id)

    def get_orders_by_member(self, orderer_id: str) -> list[Order]:
        """회원별 주문 목록 조회"""
        return self._order_repo.find_by_orderer_id(orderer_id)
```

---

## Phase 3: 아키텍처 패턴 선택

**선택: 계층 아키텍처 + DIP (의존성 역전)**

계층+DIP 기반 동기적 흐름을 기본으로 한다. 도메인 계층이 인프라에 의존하지 않도록 인터페이스를 도메인에 정의하고 인프라에서 구현한다.

```
표현(Presentation) -> 응용(Application) -> 도메인(Domain) <- 인프라(Infrastructure)
     [API/Schema]      [Service]         [Model/Event]      [ORM/Repository]
```

**의존성 규칙:**
- `domain/` -- 어디에도 의존하지 않는다. 순수 Python만 사용
- `application/` -- `domain/`에만 의존한다
- `infra_layer/` -- `domain/`과 `application/`에 의존한다 (인터페이스 구현)
- `presentation_layer/` -- `application/`에 의존한다 (유스케이스 호출)

### 3.1 Django + DDD 프로젝트 폴더 구조

```
applications/
└── ordering/                           # Bounded Context: 주문
    ├── domain_layer/                   # 순수 도메인 모델
    │   ├── order/                      # Order 애그리거트
    │   │   ├── __init__.py
    │   │   ├── order.py                # 애그리거트 루트 (Order)
    │   │   ├── order_line.py           # 값 객체 (OrderLine)
    │   │   ├── shipping_info.py        # 값 객체 (ShippingInfo)
    │   │   ├── orderer.py              # 값 객체 (Orderer)
    │   │   └── order_status.py         # 열거형 (OrderStatus)
    │   ├── value_object/
    │   │   └── address.py              # 공유 값 객체
    │   ├── repository/
    │   │   └── order_repo.py           # OrderRepository(ABC)
    │   └── event/
    │       └── order_events.py         # OrderPlacedEvent 등
    │
    ├── application_layer/
    │   ├── order_service.py            # OrderApplicationService
    │   └── event_handlers.py           # 타 도메인 이벤트 핸들러
    │
    ├── infra_layer/
    │   ├── django_ordering/            # Django 앱
    │   │   ├── apps.py
    │   │   ├── models/
    │   │   │   ├── __init__.py
    │   │   │   ├── order_model.py      # OrderModel (ORM)
    │   │   │   └── order_line_model.py # OrderLineModel (ORM)
    │   │   └── admin.py
    │   └── repository/
    │       └── order_repo.py           # DjangoOrderRepository 구현
    │
    ├── presentation_layer/
    │   ├── routers.py                  # 라우터 등록
    │   ├── api/
    │   │   └── order_api.py            # REST API 엔드포인트
    │   └── schema/
    │       ├── order_request.py        # 요청 스키마
    │       └── order_response.py       # 응답 스키마
    │
    └── tests/
        ├── domain/
        │   └── test_order.py
        ├── application/
        │   └── test_order_service.py
        └── api/
            └── test_order_api.py
```

아키텍처 패턴(헥사고날, 클린, CQRS, 이벤트 소싱)에 대한 상세 가이드는 **architecture-implementation-patterns** 스킬을 참조하세요.

---

## Phase 4: DB 스키마 설계

### 4.1 ORM 모델 (인프라 계층)

ORM은 도메인 모델을 임포트해야 하며, 도메인 모델이 ORM에 의존해서는 안 된다 (Cosmic Python).

```python
# infra_layer/django_ordering/models/order_model.py

import uuid
from django.db import models


class OrderModel(models.Model):
    """주문 ORM 모델 -- 인프라 계층"""

    class Status(models.TextChoices):
        PAYMENT_WAITING = "payment_waiting", "결제 대기"
        PREPARING = "preparing", "준비중"
        SHIPPED = "shipped", "출고됨"
        DELIVERED = "delivered", "배송완료"
        CANCELLED = "cancelled", "취소됨"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    orderer_member_id = models.CharField(max_length=100, db_index=True)
    orderer_name = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PAYMENT_WAITING,
    )

    # 배송정보 -- 값 객체를 임베디드 칼럼으로 저장
    receiver_name = models.CharField(max_length=100)
    receiver_phone = models.CharField(max_length=20)
    shipping_city = models.CharField(max_length=100)
    shipping_street = models.CharField(max_length=200)
    shipping_zipcode = models.CharField(max_length=10)

    # 총액
    total_amount = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=3, default="KRW")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "django_ordering"
        db_table = "ordering_order"
        indexes = [
            models.Index(fields=["orderer_member_id"], name="idx_order_orderer"),
            models.Index(fields=["status"], name="idx_order_status"),
            models.Index(fields=["created_at"], name="idx_order_created"),
        ]


class OrderLineModel(models.Model):
    """주문항목 ORM 모델"""

    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(
        OrderModel,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    product_id = models.CharField(max_length=100)
    product_name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()
    currency = models.CharField(max_length=3, default="KRW")
    quantity = models.PositiveIntegerField()
    line_amount = models.PositiveIntegerField()  # price * quantity

    class Meta:
        app_label = "django_ordering"
        db_table = "ordering_order_line"
```

### 4.2 ERD (논리 모델)

```
┌─────────────────────────────┐
│       ordering_order        │
├─────────────────────────────┤
│ PK  id               UUID  │
│     orderer_member_id  VARCHAR(100) │
│     orderer_name       VARCHAR(100) │
│     status             VARCHAR(20)  │
│     receiver_name      VARCHAR(100) │
│     receiver_phone     VARCHAR(20)  │
│     shipping_city      VARCHAR(100) │
│     shipping_street    VARCHAR(200) │
│     shipping_zipcode   VARCHAR(10)  │
│     total_amount       INT UNSIGNED │
│     currency           VARCHAR(3)   │
│     created_at         DATETIME     │
│     updated_at         DATETIME     │
├─────────────────────────────┤
│ IDX idx_order_orderer       │
│ IDX idx_order_status        │
│ IDX idx_order_created       │
└──────────────┬──────────────┘
               │ 1:N
┌──────────────┴──────────────┐
│    ordering_order_line      │
├─────────────────────────────┤
│ PK  id               BIGINT│
│ FK  order_id          UUID  │
│     product_id         VARCHAR(100) │
│     product_name       VARCHAR(200) │
│     price              INT UNSIGNED │
│     currency           VARCHAR(3)   │
│     quantity           INT UNSIGNED │
│     line_amount        INT UNSIGNED │
└─────────────────────────────┘
```

**설계 결정:**
- 값 객체(ShippingInfo, Address, Orderer)는 임베디드 칼럼으로 저장한다 (별도 테이블 불필요).
- OrderLine은 Order 애그리거트의 내부 구성요소이므로 FK로 연결하되, 독립 리포지토리는 두지 않는다.
- Money는 `amount` + `currency` 두 칼럼으로 분리 저장한다.

데이터베이스 스키마 설계(정규화, 인덱스, 트랜잭션)에 대한 상세 가이드는 **architecture-db** 스킬을 참조하세요.

### 4.3 리포지토리 구현 (인프라 계층)

```python
# infra_layer/repository/order_repo.py

from typing import Optional

from applications.ordering.domain_layer.order.order import Order, OrderLine, OrderStatus
from applications.ordering.domain_layer.order.orderer import Orderer
from applications.ordering.domain_layer.order.shipping_info import ShippingInfo
from applications.ordering.domain_layer.repository.order_repo import OrderRepository
from applications.ordering.infra_layer.django_ordering.models import (
    OrderModel,
    OrderLineModel,
)
from applications.shared_kernel.value_object.money import Money
from applications.ordering.domain_layer.value_object.address import Address


class DjangoOrderRepository(OrderRepository):
    """Django ORM 기반 주문 리포지토리 구현체"""

    def find_by_id(self, order_id: str) -> Optional[Order]:
        try:
            orm_order = (
                OrderModel.objects
                .prefetch_related("lines")
                .get(id=order_id)
            )
            return self._to_domain(orm_order)
        except OrderModel.DoesNotExist:
            return None

    def save(self, order: Order) -> None:
        orm_order, _ = OrderModel.objects.update_or_create(
            id=order.id,
            defaults={
                "orderer_member_id": order.orderer.member_id,
                "orderer_name": order.orderer.name,
                "status": order.status.value,
                "receiver_name": order.shipping_info.receiver_name,
                "receiver_phone": order.shipping_info.receiver_phone,
                "shipping_city": order.shipping_info.address.city,
                "shipping_street": order.shipping_info.address.street,
                "shipping_zipcode": order.shipping_info.address.zipcode,
                "total_amount": order.total_amounts.amount,
                "currency": order.total_amounts.currency,
            },
        )
        # OrderLine 재생성 (값 객체이므로 교체 방식)
        OrderLineModel.objects.filter(order=orm_order).delete()
        for line in order.order_lines:
            OrderLineModel.objects.create(
                order=orm_order,
                product_id=line.product_id,
                product_name=line.product_name,
                price=line.price.amount,
                currency=line.price.currency,
                quantity=line.quantity,
                line_amount=line.amounts.amount,
            )

    def delete(self, order: Order) -> None:
        OrderModel.objects.filter(id=order.id).delete()

    def find_by_orderer_id(self, orderer_id: str) -> list[Order]:
        orm_orders = (
            OrderModel.objects
            .filter(orderer_member_id=orderer_id)
            .prefetch_related("lines")
            .order_by("-created_at")
        )
        return [self._to_domain(o) for o in orm_orders]

    def _to_domain(self, orm_order: OrderModel) -> Order:
        """ORM -> 도메인 모델 변환"""
        order_lines = tuple(
            OrderLine(
                product_id=line.product_id,
                product_name=line.product_name,
                price=Money(amount=line.price, currency=line.currency),
                quantity=line.quantity,
            )
            for line in orm_order.lines.all()
        )

        order = object.__new__(Order)
        order.id = str(orm_order.id)
        order.orderer = Orderer(
            member_id=orm_order.orderer_member_id,
            name=orm_order.orderer_name,
        )
        order.order_lines = order_lines
        order.shipping_info = ShippingInfo(
            receiver_name=orm_order.receiver_name,
            receiver_phone=orm_order.receiver_phone,
            address=Address(
                city=orm_order.shipping_city,
                street=orm_order.shipping_street,
                zipcode=orm_order.shipping_zipcode,
            ),
        )
        order._status = OrderStatus(orm_order.status)
        order._total_amounts = Money(
            amount=orm_order.total_amount,
            currency=orm_order.currency,
        )
        order._events = []
        return order
```

---

## Phase 5: REST API 설계

### 5.1 엔드포인트 설계

| Method | Endpoint | 설명 | 요청 Body | 상태 코드 |
|--------|----------|------|----------|----------|
| POST | `/api/orders` | 주문 접수 | PlaceOrderRequest | 201 Created |
| GET | `/api/orders/{order_id}` | 주문 상세 조회 | - | 200 OK |
| GET | `/api/orders?orderer_id={id}` | 회원별 주문 목록 | - | 200 OK |
| POST | `/api/orders/{order_id}/confirm` | 주문 확정 | - | 200 OK |
| POST | `/api/orders/{order_id}/ship` | 주문 출고 | - | 200 OK |
| POST | `/api/orders/{order_id}/cancel` | 주문 취소 | CancelOrderRequest | 200 OK |
| PATCH | `/api/orders/{order_id}/shipping` | 배송지 변경 | UpdateShippingRequest | 200 OK |

**설계 원칙:**
- 상태 변경은 RPC 스타일(`/confirm`, `/ship`, `/cancel`)을 사용한다. 유비쿼터스 언어를 API에도 반영하여 `updateStatus` 대신 의도를 드러내는 동사를 사용한다.
- 조회와 변경을 분리한다 (CQS 원칙).

REST API 설계 원칙(엔드포인트, 상태 코드, 버저닝)에 대한 상세 가이드는 **architecture-api** 스킬을 참조하세요.

---

## Phase 6: Django Ninja 구현

### 6.1 요청/응답 스키마 (표현 계층)

```python
# presentation_layer/schema/order_request.py

from ninja import Schema


class OrderLineRequest(Schema):
    product_id: str
    product_name: str
    price: int
    quantity: int


class PlaceOrderRequest(Schema):
    orderer_id: str
    orderer_name: str
    items: list[OrderLineRequest]
    receiver_name: str
    receiver_phone: str
    city: str
    street: str
    zipcode: str


class CancelOrderRequest(Schema):
    reason: str = ""


class UpdateShippingRequest(Schema):
    receiver_name: str
    receiver_phone: str
    city: str
    street: str
    zipcode: str
```

```python
# presentation_layer/schema/order_response.py

from datetime import datetime
from ninja import Schema


class OrderLineResponse(Schema):
    product_id: str
    product_name: str
    price: int
    quantity: int
    line_amount: int


class ShippingInfoResponse(Schema):
    receiver_name: str
    receiver_phone: str
    city: str
    street: str
    zipcode: str


class OrderResponse(Schema):
    id: str
    orderer_id: str
    orderer_name: str
    status: str
    order_lines: list[OrderLineResponse]
    shipping_info: ShippingInfoResponse
    total_amount: int
    currency: str


class OrderListResponse(Schema):
    orders: list[OrderResponse]
    count: int


class OrderCreatedResponse(Schema):
    order_id: str
    message: str = "주문이 접수되었습니다"


class ErrorResponse(Schema):
    detail: str
```

### 6.2 API 엔드포인트 (표현 계층)

```python
# presentation_layer/api/order_api.py

from ninja import Router
from django.http import HttpRequest

from applications.ordering.application_layer.order_service import (
    OrderApplicationService,
    PlaceOrderCommand,
    CancelOrderCommand,
)
from applications.ordering.infra_layer.repository.order_repo import (
    DjangoOrderRepository,
)
from applications.ordering.presentation_layer.schema.order_request import (
    PlaceOrderRequest,
    CancelOrderRequest,
    UpdateShippingRequest,
)
from applications.ordering.presentation_layer.schema.order_response import (
    OrderResponse,
    OrderListResponse,
    OrderCreatedResponse,
    OrderLineResponse,
    ShippingInfoResponse,
    ErrorResponse,
)

router = Router(tags=["orders"])


def _get_service() -> OrderApplicationService:
    """의존성 조립 -- 간소화된 팩토리"""
    return OrderApplicationService(
        order_repository=DjangoOrderRepository(),
    )


def _to_response(order) -> OrderResponse:
    """도메인 모델 -> 응답 스키마 변환"""
    return OrderResponse(
        id=order.id,
        orderer_id=order.orderer.member_id,
        orderer_name=order.orderer.name,
        status=order.status.value,
        order_lines=[
            OrderLineResponse(
                product_id=line.product_id,
                product_name=line.product_name,
                price=line.price.amount,
                quantity=line.quantity,
                line_amount=line.amounts.amount,
            )
            for line in order.order_lines
        ],
        shipping_info=ShippingInfoResponse(
            receiver_name=order.shipping_info.receiver_name,
            receiver_phone=order.shipping_info.receiver_phone,
            city=order.shipping_info.address.city,
            street=order.shipping_info.address.street,
            zipcode=order.shipping_info.address.zipcode,
        ),
        total_amount=order.total_amounts.amount,
        currency=order.total_amounts.currency,
    )


# --- 주문 접수 ---

@router.post(
    "",
    response={201: OrderCreatedResponse, 400: ErrorResponse},
    summary="주문 접수",
)
def place_order(request: HttpRequest, body: PlaceOrderRequest):
    service = _get_service()
    try:
        order_id = service.place_order(
            PlaceOrderCommand(
                orderer_id=body.orderer_id,
                orderer_name=body.orderer_name,
                items=[
                    {
                        "product_id": item.product_id,
                        "product_name": item.product_name,
                        "price": item.price,
                        "quantity": item.quantity,
                    }
                    for item in body.items
                ],
                receiver_name=body.receiver_name,
                receiver_phone=body.receiver_phone,
                city=body.city,
                street=body.street,
                zipcode=body.zipcode,
            )
        )
        return 201, OrderCreatedResponse(order_id=order_id)
    except ValueError as e:
        return 400, ErrorResponse(detail=str(e))


# --- 주문 조회 ---

@router.get(
    "/{order_id}",
    response={200: OrderResponse, 404: ErrorResponse},
    summary="주문 상세 조회",
)
def get_order(request: HttpRequest, order_id: str):
    service = _get_service()
    order = service.get_order(order_id)
    if order is None:
        return 404, ErrorResponse(detail="주문을 찾을 수 없습니다")
    return 200, _to_response(order)


# --- 회원별 주문 목록 ---

@router.get(
    "",
    response={200: OrderListResponse},
    summary="회원별 주문 목록 조회",
)
def get_orders_by_member(request: HttpRequest, orderer_id: str):
    service = _get_service()
    orders = service.get_orders_by_member(orderer_id)
    return 200, OrderListResponse(
        orders=[_to_response(o) for o in orders],
        count=len(orders),
    )


# --- 주문 확정 ---

@router.post(
    "/{order_id}/confirm",
    response={200: OrderResponse, 400: ErrorResponse, 404: ErrorResponse},
    summary="주문 확정",
)
def confirm_order(request: HttpRequest, order_id: str):
    service = _get_service()
    try:
        service.confirm_order(order_id)
        order = service.get_order(order_id)
        return 200, _to_response(order)
    except ValueError as e:
        if "찾을 수 없습니다" in str(e):
            return 404, ErrorResponse(detail=str(e))
        return 400, ErrorResponse(detail=str(e))


# --- 주문 출고 ---

@router.post(
    "/{order_id}/ship",
    response={200: OrderResponse, 400: ErrorResponse, 404: ErrorResponse},
    summary="주문 출고",
)
def ship_order(request: HttpRequest, order_id: str):
    service = _get_service()
    try:
        service.ship_order(order_id)
        order = service.get_order(order_id)
        return 200, _to_response(order)
    except ValueError as e:
        if "찾을 수 없습니다" in str(e):
            return 404, ErrorResponse(detail=str(e))
        return 400, ErrorResponse(detail=str(e))


# --- 주문 취소 ---

@router.post(
    "/{order_id}/cancel",
    response={200: OrderResponse, 400: ErrorResponse, 404: ErrorResponse},
    summary="주문 취소",
)
def cancel_order(request: HttpRequest, order_id: str, body: CancelOrderRequest):
    service = _get_service()
    try:
        service.cancel_order(
            CancelOrderCommand(order_id=order_id, reason=body.reason)
        )
        order = service.get_order(order_id)
        return 200, _to_response(order)
    except ValueError as e:
        if "찾을 수 없습니다" in str(e):
            return 404, ErrorResponse(detail=str(e))
        return 400, ErrorResponse(detail=str(e))


# --- 배송지 변경 ---

@router.patch(
    "/{order_id}/shipping",
    response={200: OrderResponse, 400: ErrorResponse, 404: ErrorResponse},
    summary="배송지 변경",
)
def update_shipping(
    request: HttpRequest,
    order_id: str,
    body: UpdateShippingRequest,
):
    service = _get_service()
    order = service.get_order(order_id)
    if order is None:
        return 404, ErrorResponse(detail="주문을 찾을 수 없습니다")
    try:
        from applications.ordering.domain_layer.order.shipping_info import ShippingInfo
        from applications.ordering.domain_layer.value_object.address import Address

        new_shipping = ShippingInfo(
            receiver_name=body.receiver_name,
            receiver_phone=body.receiver_phone,
            address=Address(
                city=body.city,
                street=body.street,
                zipcode=body.zipcode,
            ),
        )
        order.change_shipping_info(new_shipping)
        service._order_repo.save(order)
        return 200, _to_response(order)
    except ValueError as e:
        return 400, ErrorResponse(detail=str(e))
```

### 6.3 라우터 등록

```python
# presentation_layer/routers.py

from ninja import NinjaAPI
from applications.ordering.presentation_layer.api.order_api import router as order_router

api = NinjaAPI(title="Ordering API", version="1.0.0")
api.add_router("/orders", order_router)
```

```python
# project/urls.py

from django.urls import path
from applications.ordering.presentation_layer.routers import api

urlpatterns = [
    path("api/", api.urls),
]
```

Django Ninja API(Schema, Router)에 대한 상세 가이드는 **implementation-django-ninja** 스킬을 참조하세요.

---

## 전체 설계 요약

### DDD 원칙 적용 체크리스트

| 체크 | 원칙 | 적용 내용 |
|------|------|----------|
| [x] | 전략 설계 우선 | 서브도메인 분류 -> 바운디드 컨텍스트 경계 -> 컨텍스트 맵 순서로 진행 |
| [x] | 유비쿼터스 언어 반영 | `place()`, `confirm()`, `ship()`, `cancel()` -- 비즈니스 의도를 드러내는 메서드명 |
| [x] | 작은 애그리거트 설계 | Order 루트 + OrderLine/ShippingInfo 값 객체만 포함 |
| [x] | ID로 타 애그리거트 참조 | `orderer.member_id`, `order_line.product_id` |
| [x] | 결과적 일관성 | 재고 차감, 알림 등은 도메인 이벤트로 처리 |
| [x] | 풍부한 도메인 모델 | 상태 전이 규칙, 불변식이 Order 내부에 캡슐화 |
| [x] | 값 객체 우선 | Money, Address, OrderLine 등 불변 값 객체로 설계 |
| [x] | 리포지토리는 애그리거트 단위 | OrderRepository 하나만 제공, OrderLine 별도 리포지토리 없음 |
| [x] | 도메인이 인프라에 무의존 | 도메인 계층에 순수 Python만 사용, ORM은 인프라에 격리 |
| [x] | 응용 서비스는 흐름 제어만 | 비즈니스 로직 없이 도메인 객체에 위임 |

### 상호 참조 스킬 안내

- 아키텍처 패턴(헥사고날, 클린, CQRS, 이벤트 소싱)에 대한 상세 가이드는 **architecture-implementation-patterns** 스킬을 참조하세요.
- 데이터베이스 스키마 설계(정규화, 인덱스, 트랜잭션)에 대한 상세 가이드는 **architecture-db** 스킬을 참조하세요.
- REST API 설계 원칙(엔드포인트 명명, 상태 코드, 버저닝)에 대한 상세 가이드는 **architecture-api** 스킬을 참조하세요.
- Python 컨벤션(타입 힌트, 데이터클래스)에 대한 상세 가이드는 **implementation-python** 스킬을 참조하세요.
- Django 코어(모델, ORM, 설정)에 대한 상세 가이드는 **implementation-django** 스킬을 참조하세요.
- Django Ninja API(Schema, Router)에 대한 상세 가이드는 **implementation-django-ninja** 스킬을 참조하세요.
- 클린 코드 원칙(SOLID, 네이밍)에 대한 상세 가이드는 **implementation-cleancode** 스킬을 참조하세요.
