# 쇼핑몰 주문 도메인 설계 -- 바운디드 컨텍스트부터 Django Ninja API까지

## 1. 서브도메인 식별과 분류

전략적 설계가 전술적 패턴보다 선행한다(Vernon, DDD Distilled). 먼저 쇼핑몰의 주문과 관련된 서브도메인을 식별하고, 유형별로 분류하여 투자 우선순위를 결정한다.

| 서브도메인 | 유형 | 근거 | 솔루션 전략 |
|-----------|------|------|------------|
| 주문 처리 (Ordering) | Core | 주문 흐름이 쇼핑몰의 핵심 경쟁력. 비즈니스 규칙이 복잡하고 변동이 잦음 | 사내 구현, DDD 전술 패턴 적용 |
| 결제 (Payment) | Core | 결제 정책(할인, 쿠폰, 포인트)이 차별화 요소 | 사내 구현, 외부 PG 연동은 ACL로 격리 |
| 재고 (Inventory) | Supporting | CRUD 수준의 재고 증감. 주문 확정 시 차감, 취소 시 복원 | 사내 구현, 단순한 도메인 모델 |
| 배송 (Shipping) | Supporting | 배송 상태 추적과 배송지 관리. 물류사 연동은 외부 | 사내 구현, 외부 물류 API는 ACL |
| 카탈로그 (Catalog) | Supporting | 상품 정보 관리. 주문에서는 상품 ID와 가격 스냅샷만 참조 | 사내 구현, CRUD 중심 |
| 인증/권한 (Identity) | Generic | 로그인, 회원 관리. 모든 쇼핑몰이 동일 | 외부 솔루션 또는 표준 라이브러리 |
| 알림 (Notification) | Generic | 이메일, SMS, 푸시 알림 발송 | 외부 서비스 활용 |

## 2. 바운디드 컨텍스트 식별

"하위 도메인은 발견하고, 바운디드 컨텍스트는 설계한다." 같은 용어가 다른 의미로 사용되는 지점이 바운디드 컨텍스트의 경계다.

### 2.1 컨텍스트 경계와 유비쿼터스 언어

| 바운디드 컨텍스트 | 핵심 유비쿼터스 언어 | 같은 용어, 다른 의미 |
|-----------------|-------------------|-------------------|
| **주문 (Ordering)** | 주문(Order), 주문항목(OrderLine), 주문자(Orderer), 접수(place), 취소(cancel), 출고(ship) | "상품" = 주문 시점의 가격 스냅샷 (OrderLineItem) |
| **결제 (Payment)** | 결제(Payment), 환불(Refund), 결제수단(PaymentMethod), 승인(approve), 취소(cancel) | "취소" = 결제 승인 취소 (PG 연동) |
| **재고 (Inventory)** | 재고(Stock), SKU, 차감(decrease), 복원(restore), 가용재고(available) | "상품" = SKU 단위의 재고 수량 |
| **배송 (Shipping)** | 배송(Delivery), 배송지(ShippingAddress), 운송장(TrackingNumber), 발송(dispatch) | "취소" = 배송 중단 요청 |
| **카탈로그 (Catalog)** | 상품(Product), 카테고리(Category), 가격(Price), 옵션(Option) | "상품" = 판매 가능한 전체 정보 |
| **회원 (Identity)** | 회원(Member), 인증(Authentication), 등급(Grade) | "회원" = 로그인 자격 증명 |

### 2.2 컨텍스트 맵

```
[Ordering] <--- Customer-Supplier ---> [Payment]
    |                                       |
    | Domain Event                    Domain Event
    v                                       v
[Inventory]                           [Notification]

[Ordering] <--- Customer-Supplier ---> [Shipping]

[Ordering] ---- ACL ----> [Catalog]  (가격 스냅샷 조회)

[Payment]  ---- ACL ----> [External PG]  (PG사 API)

[Shipping] ---- ACL ----> [External Logistics]  (물류사 API)

[Identity]  ---- OHS ----> [Ordering, Payment, ...]  (회원 정보 제공)
```

**연동 패턴 결정:**

| 관계 | 패턴 | 근거 |
|------|------|------|
| Ordering -> Payment | Customer-Supplier | 주문이 결제를 요청하고, 결제 결과를 수신 |
| Ordering -> Inventory | Domain Event + 최종 일관성 | 주문 확정 이벤트로 재고 차감. 별도 트랜잭션 |
| Ordering -> Shipping | Customer-Supplier | 주문 출고 시 배송 생성 요청 |
| Ordering -> Catalog | ACL | 카탈로그의 상품 모델을 주문의 OrderLineItem으로 변환 |
| Payment -> External PG | ACL | PG사의 외부 모델이 내부 결제 도메인을 오염하지 않도록 차단 |
| Identity -> 전체 | OHS + Published Language | 회원 정보를 공개 인터페이스로 다수 컨텍스트에 제공 |

## 3. 애그리거트 설계

Vernon의 4가지 규칙을 적용한다: (1) 진정한 불변식을 일관성 경계로 보호, (2) 작은 애그리거트 설계, (3) 다른 애그리거트는 ID로만 참조, (4) 경계 간 업데이트에는 최종 일관성 사용.

### 3.1 Ordering 컨텍스트

```python
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List
from uuid import uuid4


# --- 값 객체 ---

@dataclass(frozen=True)
class Money:
    amount: int
    currency: str = "KRW"

    def add(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError(f"통화 불일치: {self.currency} != {other.currency}")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def multiply(self, factor: int) -> Money:
        return Money(amount=self.amount * factor, currency=self.currency)


@dataclass(frozen=True)
class Address:
    city: str
    street: str
    zipcode: str


@dataclass(frozen=True)
class ShippingInfo:
    receiver_name: str
    receiver_phone: str
    address: Address


@dataclass(frozen=True)
class OrderLineItem:
    """주문 시점의 상품 가격 스냅샷 -- 값 객체"""
    product_id: str       # Catalog 애그리거트를 ID로 참조 (규칙 3)
    product_name: str
    price: Money
    quantity: int

    @property
    def amounts(self) -> Money:
        return self.price.multiply(self.quantity)


class OrderStatus(Enum):
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


# --- 도메인 이벤트 ---

@dataclass(frozen=True)
class OrderPlacedEvent:
    order_id: str
    orderer_id: str
    total_amount: int
    occurred_at: datetime


@dataclass(frozen=True)
class OrderCancelledEvent:
    order_id: str
    reason: str
    occurred_at: datetime


# --- 애그리거트 루트 ---

@dataclass
class Order:
    """주문 애그리거트

    불변식:
    - 최소 한 개의 주문항목이 존재해야 한다
    - 총 금액은 주문항목 금액의 합과 일치해야 한다
    - 상태 전이 규칙을 위반할 수 없다
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    orderer_id: str = ""            # Member 애그리거트를 ID로 참조 (규칙 3)
    order_lines: List[OrderLineItem] = field(default_factory=list)
    shipping_info: ShippingInfo = None
    _status: OrderStatus = field(default=OrderStatus.PAYMENT_WAITING)
    _total_amounts: Money = field(default=Money(0))
    _events: List = field(default_factory=list)

    def __post_init__(self):
        self._verify_at_least_one_order_line()
        self._calculate_total_amounts()

    def _verify_at_least_one_order_line(self) -> None:
        if not self.order_lines:
            raise ValueError("최소 한 종류 이상의 상품을 주문해야 합니다")

    def _calculate_total_amounts(self) -> None:
        total = Money(0)
        for line in self.order_lines:
            total = total.add(line.amounts)
        self._total_amounts = total

    def place(self) -> None:
        """주문을 접수한다 -- 유비쿼터스 언어: '접수'"""
        if self._status != OrderStatus.PAYMENT_WAITING:
            raise ValueError("결제 대기 상태에서만 접수할 수 있습니다")
        self._status = OrderStatus.PREPARING
        self._events.append(
            OrderPlacedEvent(
                order_id=self.id,
                orderer_id=self.orderer_id,
                total_amount=self._total_amounts.amount,
                occurred_at=datetime.now(),
            )
        )

    def cancel(self, reason: str) -> None:
        """주문을 취소한다 -- updateStatus() 대신 비즈니스 의도를 드러내는 이름"""
        if not self._status.is_cancellable:
            raise ValueError(f"{self._status.value} 상태에서는 취소할 수 없습니다")
        self._status = OrderStatus.CANCELLED
        self._events.append(
            OrderCancelledEvent(
                order_id=self.id, reason=reason, occurred_at=datetime.now()
            )
        )

    def ship(self) -> None:
        """주문을 출고한다"""
        if not self._status.is_shippable:
            raise ValueError("준비 상태에서만 출고할 수 있습니다")
        self._status = OrderStatus.SHIPPED

    def change_shipping_info(self, new_info: ShippingInfo) -> None:
        if self._status != OrderStatus.PAYMENT_WAITING:
            raise ValueError("결제 대기 상태에서만 배송지를 변경할 수 있습니다")
        self.shipping_info = new_info

    def collect_domain_events(self) -> List:
        events = list(self._events)
        self._events.clear()
        return events
```

### 3.2 Payment 컨텍스트

```python
@dataclass
class Payment:
    """결제 애그리거트

    불변식:
    - 결제 금액은 0보다 커야 한다
    - 승인된 결제만 환불할 수 있다
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    order_id: str = ""       # Order 애그리거트를 ID로 참조 (규칙 3)
    amount: Money = Money(0)
    _status: PaymentStatus = PaymentStatus.PENDING
    _events: List = field(default_factory=list)

    def approve(self) -> None:
        """결제를 승인한다"""
        if self._status != PaymentStatus.PENDING:
            raise ValueError("대기 상태에서만 승인할 수 있습니다")
        self._status = PaymentStatus.APPROVED
        self._events.append(
            PaymentApprovedEvent(payment_id=self.id, order_id=self.order_id)
        )

    def refund(self, reason: str) -> None:
        """결제를 환불한다"""
        if self._status != PaymentStatus.APPROVED:
            raise ValueError("승인된 결제만 환불할 수 있습니다")
        self._status = PaymentStatus.REFUNDED
```

### 3.3 Inventory 컨텍스트

```python
@dataclass
class Stock:
    """재고 애그리거트 -- 지원 서브도메인이므로 단순하게 유지

    불변식:
    - 가용 재고는 0 이상이어야 한다
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    product_id: str = ""     # Catalog의 Product를 ID로 참조 (규칙 3)
    _available: int = 0

    def decrease(self, quantity: int) -> None:
        """재고를 차감한다 -- OrderPlacedEvent 핸들러에서 호출"""
        if self._available < quantity:
            raise ValueError("재고가 부족합니다")
        self._available -= quantity

    def restore(self, quantity: int) -> None:
        """재고를 복원한다 -- OrderCancelledEvent 핸들러에서 호출"""
        self._available += quantity
```

### 3.4 애그리거트 간 관계 요약

```
Order (Ordering)
  |-- orderer_id -----> Member (Identity)     [ID 참조]
  |-- product_id -----> Product (Catalog)     [ID 참조, 가격 스냅샷]
  |
  |== OrderPlacedEvent ==> Stock.decrease()   [최종 일관성, 규칙 4]
  |== OrderPlacedEvent ==> Payment.create()   [최종 일관성, 규칙 4]
  |== OrderCancelledEvent => Stock.restore()  [최종 일관성, 규칙 4]
  |== OrderCancelledEvent => Payment.refund() [최종 일관성, 규칙 4]

Payment (Payment)
  |-- order_id -------> Order (Ordering)      [ID 참조]
  |
  |== PaymentApprovedEvent => Order.place()   [최종 일관성, 규칙 4]
```

## 4. 도메인 서비스와 응용 서비스

```python
# --- 도메인 서비스: 여러 애그리거트에 걸친 무상태 로직 ---

class DiscountCalculationService:
    """할인 계산 도메인 서비스

    여러 애그리거트(주문항목, 쿠폰, 회원등급)의 데이터를 사용하여
    할인 금액을 계산한다. 애그리거트는 이 서비스를 모른다.
    """

    def calculate_discount(
        self,
        order_lines: List[OrderLineItem],
        coupons: List[Coupon],
        member_grade: MemberGrade,
    ) -> Money:
        coupon_discount = Money(0)
        for coupon in coupons:
            coupon_discount = coupon_discount.add(coupon.discount_amount)
        grade_discount = self._calculate_grade_discount(member_grade, order_lines)
        return coupon_discount.add(grade_discount)


# --- 응용 서비스: 유스케이스 오케스트레이션, 비즈니스 로직 없음 ---

class PlaceOrderService:
    """주문 접수 응용 서비스

    비즈니스 로직을 직접 구현하지 않으며, 도메인 객체에 위임한다.
    트랜잭션 관리와 흐름 제어만 담당한다.
    """

    def __init__(
        self,
        order_repo: OrderRepository,
        product_repo: ProductRepository,
        discount_service: DiscountCalculationService,
    ):
        self._order_repo = order_repo
        self._product_repo = product_repo
        self._discount_service = discount_service

    def execute(self, cmd: PlaceOrderCommand) -> str:
        order_lines = self._build_order_lines(cmd.items)
        shipping_info = self._build_shipping_info(cmd.shipping_address)

        order = Order(
            orderer_id=cmd.orderer_id,
            order_lines=order_lines,
            shipping_info=shipping_info,
        )

        self._order_repo.save(order)
        return order.id
```

## 5. Django 프로젝트 구조

```
applications/
├── shared_kernel/
│   ├── value_object/
│   │   └── money.py                    # Money 값 객체 (공유)
│   └── schema/
│       └── error.py                    # ErrorOut 공통 스키마
│
├── ordering/                            # Bounded Context: 주문
│   ├── domain_layer/
│   │   ├── order/                       # Order 애그리거트 폴더
│   │   │   ├── order.py                 # 애그리거트 루트 (불변식, 비즈니스 메서드)
│   │   │   ├── order_line_item.py       # OrderLineItem 값 객체
│   │   │   ├── order_status.py          # OrderStatus 값 객체
│   │   │   └── shipping_info.py         # ShippingInfo 값 객체
│   │   ├── value_object/
│   │   │   └── address.py               # Address 값 객체
│   │   ├── repository/
│   │   │   └── order_repo.py            # class OrderRepository(ABC)
│   │   ├── event/
│   │   │   └── order_events.py          # OrderPlacedEvent, OrderCancelledEvent
│   │   └── service/
│   │       └── discount/
│   │           └── discount_service.py  # DiscountCalculationService
│   │
│   ├── application_layer/
│   │   ├── place_order_service.py       # 주문 접수 유스케이스
│   │   ├── cancel_order_service.py      # 주문 취소 유스케이스
│   │   └── event_handlers.py            # PaymentApprovedEvent 구독 핸들러
│   │
│   ├── infra_layer/
│   │   ├── django_ordering/             # Django 앱 (django_ 접두사)
│   │   │   ├── apps.py
│   │   │   └── models/
│   │   │       ├── __init__.py
│   │   │       └── order_model.py       # OrderModel (ORM -> domain 변환 책임)
│   │   ├── repository/
│   │   │   └── order_repo.py            # DjangoOrderRepository(OrderRepository)
│   │   └── event_bus/
│   │       └── signal_event_bus.py
│   │
│   ├── presentation_layer/
│   │   ├── routers.py                   # ordering_router 등록
│   │   ├── api/
│   │   │   └── order_api.py             # Django Ninja Router
│   │   └── schema/
│   │       ├── order_request.py         # PlaceOrderIn, CancelOrderIn
│   │       └── order_response.py        # OrderOut, OrderListOut
│   │
│   └── tests/
│       ├── domain/                      # 순수 도메인 로직 테스트
│       ├── application/                 # 서비스 로직 테스트
│       ├── infra/                       # 리포지토리 CRUD 테스트
│       └── api/                         # HTTP 요청/응답 테스트
│
├── payment/                             # Bounded Context: 결제
│   ├── domain_layer/
│   ├── application_layer/
│   ├── infra_layer/
│   │   └── pg_adapter/                  # PG사 ACL (외부 모델 오염 차단)
│   └── presentation_layer/
│
├── inventory/                           # Bounded Context: 재고
│   ├── domain_layer/
│   ├── application_layer/
│   │   └── event_handlers.py            # OrderPlacedEvent -> Stock.decrease()
│   ├── infra_layer/
│   └── presentation_layer/
│
└── shipping/                            # Bounded Context: 배송
    ├── domain_layer/
    ├── application_layer/
    ├── infra_layer/
    │   └── logistics_adapter/           # 물류사 ACL
    └── presentation_layer/
```

## 6. Django Ninja API까지의 구현 로드맵

전략 설계 -> 전술 패턴 -> 인프라 구현 -> API 노출 순서를 따른다.

### Phase 1: 전략 설계 (1~2주)

| 단계 | 산출물 | 핵심 활동 |
|------|--------|----------|
| 1-1. 도메인 지식 탐구 | 유비쿼터스 언어 용어집 | 도메인 전문가와 반복적 대화. 용어의 의미가 달라지는 지점을 포착 |
| 1-2. 서브도메인 분류 | 서브도메인 맵 (Core/Supporting/Generic) | 위 섹션 1의 표 완성. 투자 우선순위 결정 |
| 1-3. 바운디드 컨텍스트 설계 | 컨텍스트 맵 | 위 섹션 2의 컨텍스트 경계와 연동 패턴 확정 |
| 1-4. 이벤트 스토밍 | 도메인 이벤트 흐름도 | 주문 접수 -> 결제 승인 -> 재고 차감 -> 배송 생성 흐름을 포스트잇으로 시각화 |

### Phase 2: 전술 설계 -- 핵심 도메인 모델 (2~3주)

| 단계 | 산출물 | 핵심 활동 |
|------|--------|----------|
| 2-1. 값 객체 정의 | Money, Address, ShippingInfo, OrderLineItem | `@dataclass(frozen=True)`로 불변 보장. 자기 검증 로직 포함 |
| 2-2. 애그리거트 설계 | Order, Payment, Stock, Delivery | Vernon의 4가지 규칙 적용. 작게 유지하고 ID로만 참조 |
| 2-3. 도메인 이벤트 정의 | OrderPlacedEvent, PaymentApprovedEvent 등 | 과거형 명명. 애그리거트 간 최종 일관성의 매개체 |
| 2-4. 도메인 서비스 | DiscountCalculationService | 여러 애그리거트에 걸친 무상태 도메인 로직 |
| 2-5. 리포지토리 인터페이스 | OrderRepository(ABC), PaymentRepository(ABC) | 도메인 계층에 인터페이스만 정의. 구현은 Phase 3 |
| 2-6. 도메인 단위 테스트 | test_order.py, test_payment.py | 순수 Python, 외부 의존 없음. 불변식과 상태 전이 검증 |

### Phase 3: 인프라 계층 구현 (2~3주)

| 단계 | 산출물 | 핵심 활동 |
|------|--------|----------|
| 3-1. DB 스키마 설계 | Django ORM 모델 (OrderModel 등) | 애그리거트 경계를 테이블 구조에 반영. 정규화와 인덱스 설계 |
| 3-2. 리포지토리 구현 | DjangoOrderRepository | ORM -> domain, domain -> ORM 변환 메서드 구현. DIP 준수 |
| 3-3. 이벤트 버스 구현 | SignalEventBus | Django signals 기반 인프로세스 이벤트 디스패치 |
| 3-4. ACL 구현 | PGAnticorruptionLayer | 외부 PG사의 응답 모델을 내부 Payment 도메인으로 변환 |
| 3-5. 응용 서비스 구현 | PlaceOrderService, CancelOrderService | 유스케이스 오케스트레이션. 트랜잭션 관리. 도메인에 위임 |
| 3-6. 통합 테스트 | test_django_order_repo.py | 리포지토리 CRUD, ORM 변환 정확성 검증 |

### Phase 4: Django Ninja API 노출 (1~2주)

| 단계 | 산출물 | 핵심 활동 |
|------|--------|----------|
| 4-1. Schema 정의 | PlaceOrderIn, OrderOut | Django Ninja Schema로 요청/응답 DTO 정의. 도메인 모델과 분리 |
| 4-2. Router 구현 | order_api.py | 엔드포인트별 Router 정의. 응용 서비스에 위임 |
| 4-3. 에러 핸들링 | 도메인 예외 -> HTTP 상태 코드 매핑 | ValueError -> 400, NotFound -> 404 등 |
| 4-4. API 통합 | routers.py | 도메인별 라우터를 NinjaAPI 인스턴스에 등록 |
| 4-5. API 테스트 | test_order_api.py | HTTP 요청/응답, 상태 코드, 인증 검증 |

### Phase 5: 안정화 (1주)

| 단계 | 산출물 | 핵심 활동 |
|------|--------|----------|
| 5-1. 이벤트 흐름 E2E 테스트 | 주문 -> 결제 -> 재고 전체 흐름 검증 | 컨텍스트 간 이벤트 전파와 최종 일관성 검증 |
| 5-2. 리뷰 | DDD 체크리스트 점검 | 바운디드 컨텍스트 경계, 애그리거트 크기, ID 참조, 빈약한 모델 여부 |

---

> **관련 스킬 참조:**
> - [DB 스키마 설계 (Phase 3-1의 정규화, 인덱스, 트랜잭션 전략)] -> **architecture-db** 스킬
> - [헥사고날/클린 아키텍처, CQRS, Repository+UoW 구현 패턴] -> **architecture-implementation-patterns** 스킬
> - [REST API 설계 원칙 (엔드포인트 네이밍, 상태 코드, 버저닝)] -> **architecture-api** 스킬
> - [Django Ninja Router, Schema, 에러 핸들링 구현] -> **implementation-django-ninja** 스킬
> - [Django ORM 모델, settings, migration 구성] -> **implementation-django** 스킬
> - [Python 타입 힌트, dataclass, Enum 컨벤션] -> **implementation-python** 스킬
> - [SOLID 원칙, 네이밍, 함수 설계] -> **implementation-cleancode** 스킬
