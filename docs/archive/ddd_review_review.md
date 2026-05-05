# DDD 관점 아키텍처 리뷰 — ERP 재고 리팩터링 결과 검토

> 대상 프롬프트: `inventory/services.py` 레거시 ERP 재고 관리 Before/After/Reason 리팩터링  
> 대상 결과물: `OrderService.confirm_order()` 아키텍처 리뷰  
> 리뷰 기준: Domain-Driven Design (Evans, Vernon), Hexagonal Architecture (Cockburn)

---

## 0. 최우선 지적 — 이번에도 결과물이 프롬프트에 답하지 않음

세 번의 작업 결과물에서 두 번째와 세 번째가 정확히 **도메인이 뒤바뀌었다.**

| 회차 | 프롬프트 | 결과물 |
|---|---|---|
| 2번째 | `OrderService` 아키텍처 리뷰 | `inventory/` ERP 리팩터링 |
| **3번째 (이번)** | `inventory/services.py` ERP 리팩터링 | `OrderService` 아키텍처 리뷰 |

결과물 자체(OrderService 리뷰)는 DDD 관점에서 상당히 올바르지만, **프롬프트가 요청한 Before/After/Reason 형식의 ERP 재고 리팩터링 코드가 전혀 없다.** 아래에서 두 가지를 모두 다룬다.

---

## 파트 1. 결과물(OrderService 리뷰)의 DDD 관점 보완점

결과물은 문제 식별을 잘 했다. 그러나 DDD 설계 원칙 관점에서 누락된 artifact와 개념이 있다.

---

### 1-1. Order Aggregate 설계 완전 누락

#### 문제

결과물이 "OrderModel(인프라 계층 ORM 클래스)이 도메인 객체로 사용된다"는 문제를 올바르게 지적했지만, **Order가 Aggregate Root로서 어떻게 설계되어야 하는지 아무것도 없다.** Repository Port만 제안하고 Aggregate 내부(불변식, 상태 전이, 구성 Entity/VO)를 설계하지 않으면 리뷰가 절반이다.

```python
# [결과물의 개선 방향 — 불충분]
# "OrderRepository Port를 정의하라" 만 언급. Aggregate 자체가 없음.
```

#### 보완 — Order Aggregate 핵심 설계

```python
# order/domain/model/order.py
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class AggregateRoot:
    def __init__(self):
        self._events: list = []

    def _record(self, event) -> None:
        self._events.append(event)

    def collect_events(self) -> list:
        e, self._events = self._events, []
        return e


@dataclass
class Order(AggregateRoot):
    """
    [Aggregate Root]

    [불변식 — 항상 보장되어야 하는 규칙]
    INV-1: total_amount는 sum(line.subtotal for line in lines)와 일치한다.
    INV-2: PAID 이후 OrderLine 수량·단가는 변경 불가하다.
    INV-3: 총액 0원 이하의 주문은 생성될 수 없다.
    INV-4: 동일 order_id에 대해 결제 승인은 한 번만 가능하다(멱등).
    INV-5: CANCELLED / DELIVERED는 terminal state — 추가 전이 불가.

    [Aggregate 경계]
    포함: Order, OrderLine(VO로 재분류)
    제외: User, Product — ID 참조만 보관. 스냅샷(단가) 저장.
    """
    id: OrderId
    customer_id: CustomerId
    lines: list[OrderLine]
    status: OrderStatus
    total_amount: Money
    version: int = 0   # 낙관적 잠금

    def confirm_payment(self, payment_id: PaymentId) -> None:
        """결제 승인 — INV-4: 이미 PAID면 무시(멱등)."""
        if self.status == OrderStatus.PAID:
            return   # 멱등: 재처리 안전
        self.status = self.status.transition_to(OrderStatus.PAID)
        self._record(PaymentConfirmed(
            order_id=self.id,
            payment_id=payment_id,
            amount=self.total_amount,
        ))

    def request_fulfillment(self) -> None:
        """배송 요청 — PAID → FULFILLMENT_REQUESTED."""
        self.status = self.status.transition_to(OrderStatus.FULFILLMENT_REQUESTED)
        self._record(FulfillmentRequested(order_id=self.id))

    def cancel(self, reason: CancellationReason) -> None:
        """고객 취소 — PAID 이전에만 허용."""
        self.status = self.status.transition_to(OrderStatus.CANCELLED)
        self._record(OrderCancelled(order_id=self.id, reason=reason))
```

---

### 1-2. 상태 전이 규칙 미정의

#### 문제

결과물이 `order.status = "confirmed"` 직접 할당을 문제로 지적했지만, **어떤 전이가 유효하고 어떤 것이 InvalidStateTransition인지 설계가 없다.** "OrderStatus VO"를 언급하지도 않았다.

#### 보완 — OrderStatus VO + 전이 매트릭스

```python
# order/domain/model/order_status.py
from enum import Enum
from typing import ClassVar


class OrderStatus(Enum):
    AWAITING_PAYMENT       = "AWAITING_PAYMENT"
    PAID                   = "PAID"
    FULFILLMENT_REQUESTED  = "FULFILLMENT_REQUESTED"
    SHIPPED                = "SHIPPED"
    DELIVERED              = "DELIVERED"
    CANCELLED              = "CANCELLED"
    PAYMENT_FAILED         = "PAYMENT_FAILED"

    _TRANSITIONS: ClassVar[dict] = {}  # 아래에서 초기화

    def transition_to(self, target: "OrderStatus") -> "OrderStatus":
        allowed = _ALLOWED_TRANSITIONS.get(self, set())
        if target not in allowed:
            raise InvalidStateTransition(
                f"{self.value} → {target.value} 전이는 허용되지 않습니다"
            )
        return target


_ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.AWAITING_PAYMENT: {
        OrderStatus.PAID,
        OrderStatus.PAYMENT_FAILED,
        OrderStatus.CANCELLED,
    },
    OrderStatus.PAID: {
        OrderStatus.FULFILLMENT_REQUESTED,
        OrderStatus.CANCELLED,
    },
    OrderStatus.FULFILLMENT_REQUESTED: {
        OrderStatus.SHIPPED,
        OrderStatus.CANCELLED,   # 출고 전 취소
    },
    OrderStatus.SHIPPED: {
        OrderStatus.DELIVERED,
    },
    # terminal: DELIVERED, CANCELLED, PAYMENT_FAILED — 전이 없음
}
```

---

### 1-3. 도메인 이벤트 설계 없음

#### 문제

결과물 체크리스트에 "도메인 이벤트가 통합 이벤트로 직접 노출되지 않는가 — FAIL"이라고 명시했지만, **어떤 도메인 이벤트가 있어야 하는지 단 하나도 설계하지 않았다.** 체크리스트 지적만 있고 설계가 없으면 팀이 어디서부터 시작해야 할지 알 수 없다.

#### 보완 — 도메인 이벤트 목록

```python
# order/domain/events/internal.py  ← BC 내부용
@dataclass(frozen=True)
class OrderPlaced:
    """주문이 생성되어 결제 대기 상태가 된 사건."""
    order_id: OrderId
    customer_id: CustomerId
    total_amount: Money
    occurred_at: datetime = field(default_factory=datetime.utcnow)

@dataclass(frozen=True)
class PaymentConfirmed:
    """PG사가 결제를 승인한 사건."""
    order_id: OrderId
    payment_id: PaymentId
    amount: Money
    occurred_at: datetime = field(default_factory=datetime.utcnow)

@dataclass(frozen=True)
class FulfillmentRequested:
    """배송 처리를 요청한 사건 (Saga step 트리거)."""
    order_id: OrderId
    occurred_at: datetime = field(default_factory=datetime.utcnow)

@dataclass(frozen=True)
class OrderCancelled:
    order_id: OrderId
    reason: CancellationReason
    occurred_at: datetime = field(default_factory=datetime.utcnow)


# order/domain/events/integration.py  ← BC 간 Published Language
@dataclass(frozen=True)
class OrderConfirmedV1:
    """
    [Published Language — 외부 계약]
    Shipping BC, Notification BC가 소비.
    필드명·타입 변경 시 V2를 신설하고 V1 병행 발행 후 폐기.
    """
    event_id: str
    event_type: str = "order.confirmed.v1"
    schema_version: str = "1.0"
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    # 페이로드
    order_id: str
    customer_id: str
    total_amount_krw: int
    shipping_address: ShippingAddressPayload
    lines: list[OrderLinePayload]
```

---

### 1-4. Saga 설계 제안 미흡

#### 문제

결과물이 "결제는 idempotency key + 도메인 상태머신으로, 배송/이메일은 Outbox에 적재"라고 언급했지만, **Saga(결제→배송) 흐름이 구체화되지 않았다.** 오케스트레이션 vs 코레오그래피 선택도 없다. 팀이 이 지침만으로는 구현을 시작할 수 없다.

#### 보완 — Order Fulfillment Saga 흐름

```
[오케스트레이션 방식 선택 이유]
- 결제 BC, 배송 BC에 걸친 흐름을 Order BC가 소유·추적해야 함
- 장애 시 어느 step에서 실패했는지 단일 지점에서 확인 가능

[Saga Step 시퀀스]

Step 1: PlaceOrderCommand
  └─ Order 생성 (status=AWAITING_PAYMENT)
  └─ OrderPlaced 이벤트 기록
  └─ UoW.commit()

Step 2: RequestPaymentCommand (Saga 트리거)
  └─ PaymentGateway.charge(order_id, amount, idempotency_key=order_id)
     ├─ 성공: ConfirmPaymentCommand 디스패치
     └─ 실패: FailPaymentCommand 디스패치

Step 3: ConfirmPaymentCommand (Webhook 또는 Saga에서)
  └─ order.confirm_payment(payment_id)
  └─ OrderConfirmedV1 → Outbox INSERT (같은 트랜잭션)
  └─ UoW.commit()

Step 4: NotifyShippingCommand (Outbox Relay가 발행한 이벤트 소비)
  └─ ShippingGateway.create_shipment(order)
     ├─ 성공: 완료
     └─ 실패: CompensateCommand (CancelOrder + RefundPayment)
```

---

### 1-5. Money Value Object 누락

#### 문제

결과물이 `order.total_amount`를 단순 정수로 다루는 문제를 **전혀 지적하지 않았다.** 통화 정보가 없는 금액은 KRW인지 USD인지 알 수 없어 혼합 연산 위험이 있다. Stripe API 호출 시 `currency="krw"`가 하드코딩된 것이 이 문제의 증상이다.

#### 보완 — Money VO

```python
# order/domain/model/money.py
@dataclass(frozen=True)
class Money:
    """
    [Value Object — 금액과 통화의 불가분 쌍]
    INV: amount는 0 이상. 통화가 다른 Money끼리 연산 불가.
    """
    amount: int    # 최소 단위(원), 소수점 없음
    currency: str  # "KRW"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError(f"금액은 0 이상이어야 합니다: {self.amount}")
        if not self.currency:
            raise ValueError("통화 코드는 필수입니다")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise CurrencyMismatch(f"{self.currency} + {other.currency} 불가")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, quantity: int) -> "Money":
        if quantity < 0:
            raise ValueError("수량은 0 이상이어야 합니다")
        return Money(self.amount * quantity, self.currency)

# 올바른 PaymentGateway Port — currency가 Money에 내포됨
class PaymentGateway(ABC):
    @abstractmethod
    def charge(
        self,
        order_id: OrderId,
        amount: Money,             # ← currency가 Money에 포함. "krw" 하드코딩 없음
        payment_method: PaymentMethod,
        idempotency_key: str,
    ) -> PaymentResult: ...
```

---

### 1-6. Port 인터페이스 코드 없음

#### 문제

결과물이 Port 목록을 표 형식으로만 제시했다. 이름·메서드·반환 타입이 DDD 관점에서 올바른지 검증하려면 실제 인터페이스 코드가 필요하다.

#### 보완 — 모든 Port 인터페이스 코드

```python
# order/application/ports/driven/payment_gateway.py
class PaymentGateway(ABC):
    """
    도메인 의도: "결제를 승인하라"
    도메인 어휘 사용. Stripe 어휘(charges.create, source) 노출 금지.
    """
    @abstractmethod
    def charge(
        self,
        order_id: OrderId,
        amount: Money,
        payment_method: PaymentMethod,
        idempotency_key: str,       # 멱등성 필수
    ) -> PaymentResult: ...

    @abstractmethod
    def refund(
        self,
        payment_id: PaymentId,
        amount: Money,
        reason: RefundReason,
    ) -> RefundResult: ...


# order/application/ports/driven/order_notifier.py
class OrderNotifier(ABC):
    """
    도메인 의도: "주문 확정을 고객에게 알려라"
    이메일·SMS·푸시 구분을 도메인이 알 필요 없음.
    """
    @abstractmethod
    def notify_confirmed(self, order: Order) -> None: ...

    @abstractmethod
    def notify_cancelled(self, order: Order, reason: CancellationReason) -> None: ...


# order/application/ports/driven/shipping_gateway.py
class ShippingGateway(ABC):
    """
    도메인 의도: "배송 처리를 시작하라"
    HTTP URL, JSON 키 이름은 도메인이 알 필요 없음.
    """
    @abstractmethod
    def create_shipment(self, order: Order) -> ShipmentId: ...

    @abstractmethod
    def cancel_shipment(self, shipment_id: ShipmentId) -> None: ...


# order/application/ports/driven/order_repository.py
class OrderRepository(ABC):
    """Aggregate(Order) 단위 컬렉션 추상화. OrderLine 별도 Repository 금지."""
    @abstractmethod
    def get(self, order_id: OrderId) -> Order | None: ...

    @abstractmethod
    def add(self, order: Order) -> None: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...
```

---

### 1-7. Ubiquitous Language 분석 없음

#### 문제

`confirm_order`, `payment_token`, `payment_id` 같은 용어가 도메인 언어인지 기술 언어인지 **분석이 없다.** 특히 `payment_token`은 Stripe 어휘가 도메인 모델 필드명으로 침투한 전형적인 Conformist 오염이다.

#### 보완 — 용어 정화 목록

| 현재 코드 용어 | 오염 출처 | 도메인 용어 | 이유 |
|---|---|---|---|
| `payment_token` | Stripe SDK 어휘 | `payment_method: PaymentMethod` | PG사 교체 시 도메인 변경 발생 |
| `charge.id` | Stripe 응답 필드 | `payment_id: PaymentId` | 내부 식별자와 외부 식별자 분리 |
| `source` (Stripe param) | Stripe API 파라미터 | `payment_method` | 도메인 의도로 표현 |
| `confirm_order` | 기술 동사 | `confirm_payment()` | "무엇을 확인"하는지 명확화 |
| `"confirmed"` (문자열) | 매직 스트링 | `OrderStatus.PAID` | 오타 방지, 전이 규칙 캡슐화 |
| `order.shipping_address` (dict) | JSON 스키마 | `ShippingAddress(VO)` | 주소 유효성 검증 도메인으로 |

---

### 1-8. Before/After/Reason 코드 없음

#### 문제

프롬프트가 명시적으로 **Before/After/Reason 형식**을 요청했는데, 결과물은 순수 분석 문서다. 분석 → 리팩터링 코드로 연결되지 않으면 팀이 바로 구현에 착수할 수 없다.

#### 보완 — 핵심 Before/After 예시 (2개)

**[Before/After 1] 도메인 → 인프라 의존 제거**

```python
# [Before] order/domain/order_service.py
import requests
from stripe import Stripe
from order.infrastructure.models import OrderModel

class OrderService:
    def confirm_order(self, order_id: int) -> dict:
        order = OrderModel.objects.get(id=order_id)
        stripe = Stripe(api_key="sk_live_xxx")
        charge = stripe.charges.create(...)
        order.status = "confirmed"
        order.save()
        requests.post("http://shipping-service/api/shipments", ...)
        return {"order_id": ..., "items": list(order.items.values(...))}
```

```python
# [After] order/application/commands/confirm_payment_handler.py
class ConfirmPaymentCommandHandler:
    """
    Application Service — Port만 알고 어댑터 구현은 모른다.
    도메인 import만 있고, requests/stripe/ORM import 없음.
    """
    def __init__(
        self,
        uow: UnitOfWork,
        # Notifier는 이벤트 핸들러로 처리 (직접 주입 불필요)
    ) -> None:
        self._uow = uow

    def handle(self, cmd: ConfirmPaymentCommand) -> None:
        with self._uow:
            order = self._uow.orders.get(cmd.order_id)
            order.confirm_payment(cmd.payment_id)
            self._uow.outbox.append(
                OrderConfirmedV1.from_order(order)
            )
            self._uow.commit()
        # 커밋 후 이벤트 디스패치 (이메일·배송은 비동기)
        for event in order.collect_events():
            self._event_bus.dispatch(event)
```

```
[Reason]
- 도메인 계층(order/domain/)에서 모든 외부 import 제거.
- PaymentGateway, ShippingGateway Port가 Adapter를 숨김.
- 이메일·배송은 OrderConfirmedV1 이벤트를 Outbox에 적재 후 비동기 처리.
  → 결제 성공 후 배송 API 실패 시 주문 상태가 깨지지 않음.
- Command Handler는 void 반환 (CQS).
```

**[Before/After 2] CQS 분리**

```python
# [Before] — Command가 조회 데이터를 반환
def confirm_order(self, order_id: int) -> dict:
    ...
    return {
        "order_id": order.id,
        "status": order.status,
        "items": list(order.items.values("name", "quantity", "price")),
    }
```

```python
# [After 1] Command — void
class ConfirmPaymentCommandHandler:
    def handle(self, cmd: ConfirmPaymentCommand) -> None:
        ...  # 반환값 없음

# [After 2] Query — 별도 서비스
class OrderQueryService:
    def __init__(self, db: Connection) -> None:
        self._db = db   # ORM이 아닌 DB 직접 접근 허용 (Read side)

    def find_by_id(self, order_id: OrderId) -> OrderDetailDTO | None:
        """도메인 모델/리포지토리를 거치지 않는다. 읽기 최적화 SQL."""
        row = self._db.execute(
            """
            SELECT o.id, o.status, o.total_amount,
                   i.name, i.quantity, i.price
            FROM orders o
            JOIN order_lines i ON i.order_id = o.id
            WHERE o.id = %s
            """,
            [str(order_id)],
        ).fetchall()
        if not row:
            return None
        return OrderDetailDTO.from_rows(row)
```

```
[Reason]
- Meyer CQS: 상태 변경(Command)과 데이터 반환(Query)을 분리.
- Read side는 도메인 모델을 우회하여 DB를 직접 조회 → 성능 최적화.
- Command 완료 후 클라이언트가 GET /orders/{id}를 호출하여 최신 상태 조회.
```

---

## 파트 2. 원래 프롬프트에 대한 답 (ERP 재고 리팩터링)

결과물이 누락한 실제 요청 내용을 핵심만 정리한다.

---

### 2-1. 변경 1: 도메인 모델 + Value Objects

```python
# [Before]
def get_stock(product_code: str) -> int:
    conn = cx_Oracle.connect("erp_user/pass@erp-db:1521/ERPDB")
    cursor.execute("SELECT ZQTY_AVAIL FROM TB_INV_MASTER WHERE ZITEM_CD = :1", [product_code])
    return row[0] if row else 0

def reserve_stock(product_code: str, quantity: int) -> bool:
    ...
    return affected > 0   # Command가 bool 반환 (CQS 위반)
```

```python
# [After] inventory/domain/model.py
@dataclass(frozen=True)
class ProductCode:
    value: str
    def __post_init__(self):
        if not self.value.strip():
            raise ValueError("ProductCode는 비어있을 수 없습니다")

@dataclass(frozen=True)
class Quantity:
    value: int
    def __post_init__(self):
        if self.value < 0:
            raise ValueError("수량은 0 이상이어야 합니다")

@dataclass
class StockItem(AggregateRoot):
    """
    [Aggregate Root]
    INV-1: available은 항상 0 이상.
    INV-2: reserved는 available을 초과할 수 없다.
    """
    code: ProductCode
    available: Quantity
    reserved: Quantity = field(default_factory=lambda: Quantity(0))
    version: int = 0   # 낙관적 잠금

    def reserve(self, qty: Quantity, order_id: str) -> None:
        """재고 예약 — INV-1, INV-2 보장."""
        if self.available.value < qty.value:
            raise InsufficientStockError(self.code, qty, self.available)
        self.available = Quantity(self.available.value - qty.value)
        self.reserved = Quantity(self.reserved.value + qty.value)
        self._record(StockReserved(self.code, qty, order_id))

    def release(self, qty: Quantity, order_id: str) -> None:
        """주문 취소 시 예약→가용 반환."""
        if self.reserved.value < qty.value:
            raise InvalidStockReleaseError(self.code, qty, self.reserved)
        self.reserved = Quantity(self.reserved.value - qty.value)
        self.available = Quantity(self.available.value + qty.value)
        self._record(StockReleased(self.code, qty, order_id))
```

```
[Reason]
- str/int 원시 타입에 숨어있던 도메인 개념(상품코드, 수량)을 VO로 추출.
- reserve() 성공 후 StockReserved 이벤트 기록 → Order Saga와 통합 가능.
- release()를 추가하여 재고 라이프사이클 완성 (기존 코드는 예약 취소 불가).
- reserve_stock()의 bool 반환 제거 → CQS 준수 (실패는 예외로 표현).
```

### 2-2. 변경 2: Port 정의

```python
# [Before] Port 없음. 함수가 cx_Oracle을 직접 import.

# [After] inventory/domain/ports.py
class StockRepository(ABC):
    @abstractmethod
    def get(self, code: ProductCode) -> StockItem | None: ...
    @abstractmethod
    def save(self, item: StockItem) -> None: ...

class ProductCatalog(ABC):
    @abstractmethod
    def fetch(self, code: ProductCode) -> Product | None: ...
```

```
[Reason]
- 도메인이 자신이 필요로 하는 대화를 Port로 소유(소유권 역전).
- cx_Oracle이 Port 뒤로 격리됨 → ERP 교체 시 Adapter만 교체.
```

### 2-3. 변경 3: ACL (Facade + Adapter + Translator)

```python
# [Before] 도메인 코드에 ERP 어휘 직접 노출
cursor.execute("SELECT ZQTY_AVAIL FROM TB_INV_MASTER WHERE ZITEM_CD = :1", [product_code])

# [After] inventory/infrastructure/erp/translator.py
class ErpTranslator:
    @staticmethod
    def to_stock_item(row: tuple, code: ProductCode) -> StockItem:
        return StockItem(code=code, available=Quantity(int(row[0])))

# [After] inventory/infrastructure/erp/repository.py
class ErpStockRepository(StockRepository):
    def get(self, code: ProductCode) -> StockItem | None:
        with self._client.cursor() as cursor:
            cursor.execute(
                "SELECT ZQTY_AVAIL FROM TB_INV_MASTER WHERE ZITEM_CD = :1",
                [code.value],
            )
            row = cursor.fetchone()
        return self._translator.to_stock_item(row, code) if row else None
```

```
[Reason]
- ERP 스키마(ZQTY_AVAIL, TB_INV_MASTER, ZITEM_CD)가 Translator 한 곳에 집중.
- ERP 교체 시 Translator + Adapter만 변경, 도메인 코드 무변경.
- Connection 자원 관리가 ErpOracleClient.cursor() 하나로 통합
  → connect/close 반복 누락 위험 제거.
```

### 2-4. 변경 4: UoW — 트랜잭션 경계를 Application Service로

```python
# [Before] Repository 내부에서 commit (트랜잭션 경계 분산)
def reserve_stock(...) -> bool:
    conn = cx_Oracle.connect(...)
    cursor.execute("UPDATE TB_INV_MASTER ...", [...])
    conn.commit()   # Repository가 commit 소유 — 안티패턴

# [After] Application Service가 트랜잭션 경계 소유
class StockReservationService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def reserve(self, code: ProductCode, qty: Quantity, order_id: str) -> None:
        with self._uow:
            stock = self._uow.stock.get(code)
            if stock is None:
                raise StockNotFoundError(code.value)
            stock.reserve(qty, order_id)   # 도메인 불변식 검증
            self._uow.stock.save(stock)
            self._uow.commit()             # Application Service가 commit
        # 커밋 후 도메인 이벤트 디스패치
        for event in stock.collect_events():
            self._event_bus.dispatch(event)
```

```
[Reason]
- 트랜잭션 경계가 Use Case(Application Service)에 있어야
  미래에 다중 Aggregate 트랜잭션으로 확장 가능.
- 실패 시 rollback이 보장됨 (기존 코드는 UPDATE 후 commit 사이 예외 시 미정의).
- 커밋 후 이벤트 디스패치 → Order BC의 Saga가 StockReserved를 수신.
```

### 2-5. 변경 5: Composition Root

```python
# [Before] 자격증명 하드코딩, 함수마다 별도 연결
conn = cx_Oracle.connect("erp_user/pass@erp-db:1521/ERPDB")

# [After] inventory/composition.py
from functools import lru_cache
from django.conf import settings

@lru_cache(maxsize=1)
def _erp_client() -> ErpOracleClient:
    return ErpOracleClient(
        dsn=settings.ERP_DSN,
        user=settings.ERP_USER,
        password=settings.ERP_PASSWORD,
        pool_min=2, pool_max=10,  # Connection Pool
    )

def build_stock_reservation_service() -> StockReservationService:
    return StockReservationService(
        uow=ErpUnitOfWork(client=_erp_client())
    )
```

```
[Reason]
- 자격증명이 Django settings / 환경변수로 외부화.
- lru_cache로 Connection Pool을 프로세스 단위로 공유
  → 함수마다 새 연결 생성 비용 제거.
- 테스트에서 FakeUnitOfWork 주입으로 ERP 없이 도메인 테스트 가능.
```

---

## 종합 보완 우선순위

### 결과물(OrderService 리뷰) 보완

| 우선순위 | 항목 | 이유 |
|---|---|---|
| **P0** | Order Aggregate 불변식 + 상태 전이 설계 | 문제 식별만 있고 해법이 없음 |
| **P0** | 도메인 이벤트 목록 (`PaymentConfirmed`, `FulfillmentRequested`) | 체크리스트 FAIL인데 설계 없음 |
| **P0** | Before/After/Reason 리팩터링 코드 | 프롬프트 요구 형식 미충족 |
| **P1** | Port 인터페이스 실제 코드 | 표 형식으로만 제시 |
| **P1** | Saga 흐름 구체화 (Step별 Command/Event) | "Outbox 사용" 수준에서 멈춤 |
| **P1** | Money VO 지적 | `total_amount` 통화 정보 누락 미언급 |
| **P2** | Ubiquitous Language 용어 정화 목록 | payment_token 오염 미언급 |
| **P2** | OrderStatus VO + 전이 매트릭스 | 전이 규칙 없이 불변식 보호 불가 |

### 원래 프롬프트(ERP 재고) 대응

결과물이 완전 누락했으므로 파트 2의 5개 변경(도메인 모델, Port, ACL, UoW, Composition Root)을 Before/After/Reason으로 작성 필요. 추가로 아래 두 항목이 더 필요하다:

| 추가 항목 | 이유 |
|---|---|
| `release()` + `commit()` 메서드 | 재고 라이프사이클 완성 (기존 코드에 취소/확정 없음) |
| Order ↔ Inventory 통합 전략 | StockReserved 이벤트를 Order Saga가 어떻게 소비하는지 |
