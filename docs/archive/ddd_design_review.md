# DDD 관점 아키텍처 설계 리뷰 및 보완점

> 대상 문서: 전자상거래 주문 처리 아키텍처 설계 (Order Bounded Context)  
> 리뷰 기준: Domain-Driven Design (Evans, Vernon, Young)

---

## 총평

헥사고날 아키텍처, Ports & Adapters, ACL, CQRS 수준 1, Outbox + 오케스트레이션 Saga의 선택 근거가 명확하고, 패턴 복잡도를 요구사항에 맞게 조정한 판단은 **DDD에서 가장 중요한 원칙인 "전략적 설계가 전술적 설계보다 먼저"** 를 따른다. 다만 **전략적 DDD(Bounded Context 지도, Ubiquitous Language)와 전술적 DDD(Aggregate 불변식, 도메인 서비스, 상태 전이 모델)의 핵심 artifact가 누락**되어, 설계의 타당성을 팀이 공유하고 구현체가 설계 의도를 따르는지 검증하기 어렵다. 아래에 항목별로 보완점을 기술한다.

---

## 1. 전략적 DDD 누락 — Ubiquitous Language

### 문제

설계 전체에 걸쳐 `OrderPlaced`, `PaymentConfirmed`, `order.confirm_payment()` 같은 용어가 혼용되지만, **도메인 전문가와 개발자가 동의한 언어(Ubiquitous Language) 사전이 없다.** 결과적으로:

- "주문 확인"이 `OrderConfirmed`인지 `PaymentConfirmed` 이후 상태인지 불명확
- `cancel`이 "고객 취소"인지 "시스템 취소(배송 실패 보상)"인지 코드에서 구분 불가
- 외부(토스, CJ) 용어가 ACL 없이 내부로 유입될 위험

### 보완 — Ubiquitous Language 사전 (예시)

| 도메인 용어 | 정의 | 금지 동의어 |
|---|---|---|
| **주문(Order)** | 고객이 구매 의사를 표명한 요청의 집합. 결제 전·후 모두 포함 | Purchase, Request |
| **주문 항목(OrderLine)** | 주문에 포함된 단일 상품과 수량의 쌍 | Item, CartItem |
| **결제 승인(PaymentApproval)** | PG사가 결제 금액을 확정하여 통보한 사건 | PaymentConfirmation, Settlement |
| **주문 확정(OrderFulfillment)** | 결제 승인 완료 후 배송 처리가 시작된 상태 | OrderConfirmed, OrderCompleted |
| **고객 취소(CustomerCancellation)** | 배송 출고 전 고객 요청에 의한 주문 무효화 | Cancel, OrderCancel |
| **보상 취소(CompensatingCancellation)** | 배송 실패 등 시스템 오류로 인한 자동 무효화 | Rollback, Undo |

> **Rule:** 코드의 클래스명·메서드명·이벤트명은 이 사전의 용어와 1:1 대응해야 한다. ACL Translator는 외부 시스템의 용어를 이 사전의 용어로 변환하는 유일한 장소다.

---

## 2. 전략적 DDD 누락 — Context Map

### 문제

설계 문서에 BC 목록(`src/orders/`, `src/shipping/`)은 언급되지만, **BC 간 관계 유형과 통합 방향(Context Map)이 없다.** BC 간 관계 유형은 팀 구조·코드 결합도·이벤트 계약 강도에 직접 영향을 준다.

### 보완 — Context Map

```
┌─────────────────────────────────────────────────────────────────┐
│                         모놀리스 경계                              │
│                                                                  │
│  ┌──────────────┐   Published Language    ┌──────────────────┐  │
│  │   Order BC   │ ──OrderConfirmedV1────► │   Shipping BC    │  │
│  │  (Upstream)  │                         │  (Downstream /   │  │
│  │              │ ◄──DeliveryStatusV1───  │  Conformist)     │  │
│  └──────┬───────┘                         └──────────────────┘  │
│         │                                                        │
└─────────┼──────────────────────────────────────────────────────-┘
          │ ACL (Anti-Corruption Layer)
          ▼
  ┌───────────────┐         ┌──────────────────┐
  │  토스페이먼츠   │         │   CJ대한통운      │
  │  (External /  │         │  (External /     │
  │   Conformist) │         │   Conformist)    │
  └───────────────┘         └──────────────────┘
```

| 관계 | 유형 | 함의 |
|---|---|---|
| Order BC → Shipping BC | **Published Language (Upstream/Downstream)** | Order BC가 계약(이벤트 스키마)을 소유. Shipping BC는 계약에 순응. 분리 시 계약 그대로 유지 |
| Order BC → 토스페이먼츠 | **Conformist + ACL** | 외부 API 변경에 취약하므로 ACL 필수. 도메인은 Toss 스키마를 모름 |
| Order BC → CJ대한통운 | **Conformist + ACL** | 동일 |

> **분리 준비 관점:** Order가 Upstream이므로, Shipping BC 분리 후에도 OrderConfirmedV1 이벤트 스키마는 Order가 소유하고 버전 관리한다.

---

## 3. 전술적 DDD — Aggregate 설계 불충분

### 문제

`Order`가 Aggregate Root임을 명시하지만 **불변식(Invariants)이 정의되지 않았다.** DDD에서 Aggregate의 존재 이유는 불변식 보호다. 불변식 없는 Aggregate는 단순 데이터 클래스다.

또한 `OrderLine`을 Entity로 분류했는데, **Entity와 Value Object 판단 기준**이 적용되지 않았다.

### 보완 — Order Aggregate 불변식 명세

```python
# domain/model/order.py — 불변식을 주석으로 반드시 명시
class Order:
    """
    [Aggregate Root]

    [불변식 — 이 클래스가 항상 보장해야 하는 규칙]
    INV-1: 총액(total_amount)은 항상 sum(OrderLine.subtotal)과 일치한다.
    INV-2: PAID 이후 OrderLine 수량은 변경 불가하다.
    INV-3: 총액이 0원 이하인 주문은 생성될 수 없다.
    INV-4: 동일 order_id에 대해 결제는 한 번만 승인될 수 있다 (멱등성).
    INV-5: CANCELLED 또는 DELIVERED 상태에서 상태 전이는 불가하다 (terminal state).

    [Aggregate 경계]
    - Order, OrderLine만 포함. ShippingAddress는 VO.
    - Product 정보는 스냅샷(product_id, product_name, unit_price)으로만 보관.
      Product BC의 변경이 이 Aggregate를 오염시키지 않는다.
    """
```

### 보완 — OrderLine은 Value Object 재검토

| 판단 기준 | OrderLine |
|---|---|
| 고유 식별자가 있는가? | 없음 (order_id + sequence 조합이면 VO 특성에 가까움) |
| 생애주기가 독립적인가? | Order에 종속 |
| 동일성이 값으로 판단되는가? | product_id + quantity + unit_price 조합으로 동일성 판단 가능 |
| **결론** | **OrderLine은 Value Object**로 재분류 권장. 수량 변경 시 교체(replace)로 처리 |

---

## 4. 전술적 DDD — 상태 전이 모델 누락

### 문제

`OrderStatus`가 "VO, 상태 전이 규칙" 주석만 있고 **허용 전이 매트릭스가 없다.** 상태 전이 오류는 도메인 불변식 위반이므로 도메인 레이어에서 예외를 발생시켜야 하는데, 어떤 전이가 유효한지 정의가 없으면 검증이 불가능하다.

### 보완 — 상태 전이 다이어그램 및 규칙

```
[PENDING_PAYMENT]
    │
    ├─ place() ──────────────────────────────► [AWAITING_PAYMENT]
    │
[AWAITING_PAYMENT]
    │
    ├─ confirm_payment()  ───────────────────► [PAID]
    ├─ fail_payment()     ───────────────────► [PAYMENT_FAILED]
    ├─ expire()           ───────────────────► [EXPIRED]
    │
[PAID]
    │
    ├─ request_fulfillment() ────────────────► [FULFILLMENT_REQUESTED]
    ├─ cancel() (고객 취소, 배송 전) ──────────► [CANCELLATION_REQUESTED]
    │
[FULFILLMENT_REQUESTED]
    │
    ├─ confirm_shipment() ───────────────────► [SHIPPED]
    ├─ fail_shipment()    ───────────────────► [FULFILLMENT_FAILED]  → 보상 트랜잭션
    │
[SHIPPED] ──────────────────────────────────► (terminal)
[PAYMENT_FAILED] ────────────────────────────► (terminal)
[EXPIRED] ───────────────────────────────────► (terminal)
[CANCELLED] ─────────────────────────────────► (terminal)
```

```python
# domain/model/order_status.py
class OrderStatus(Enum):
    AWAITING_PAYMENT = "AWAITING_PAYMENT"
    PAID = "PAID"
    FULFILLMENT_REQUESTED = "FULFILLMENT_REQUESTED"
    SHIPPED = "SHIPPED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    FULFILLMENT_FAILED = "FULFILLMENT_FAILED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

    ALLOWED_TRANSITIONS: ClassVar[dict] = {
        AWAITING_PAYMENT: {PAID, PAYMENT_FAILED, EXPIRED},
        PAID:             {FULFILLMENT_REQUESTED, CANCELLED},
        FULFILLMENT_REQUESTED: {SHIPPED, FULFILLMENT_FAILED},
        # terminal states — 전이 없음
    }

    def transition_to(self, next_status: "OrderStatus") -> "OrderStatus":
        allowed = self.ALLOWED_TRANSITIONS.get(self, set())
        if next_status not in allowed:
            raise InvalidStateTransition(
                f"{self.value} → {next_status.value} 전이는 허용되지 않음"
            )
        return next_status
```

---

## 5. 전술적 DDD — 도메인 서비스 누락

### 문제

**단일 Aggregate 안에 캡슐화하기 어려운 도메인 로직**이 어디에 위치하는지 명시되지 않았다. 도메인 서비스 없이는 이 로직이 Application 계층으로 흘러들어 도메인이 빈약(Anemic Domain)해진다.

### 보완 — 도메인 서비스 식별

```
domain/
└── services/
    ├── order_pricing_service.py    # 복잡한 가격 산정 (쿠폰, 배송비, 세금 조합)
    │                               # Order 단독으로 계산 불가능한 경우
    ├── order_cancellation_policy.py # 취소 가능 여부 정책 (배송 출고 기준 시간 등)
    │                               # 정책이 외부 조건(현재 배송 상태)에 의존할 때
    └── refund_calculator.py        # 부분 취소 환불 금액 계산 규칙
```

```python
# domain/services/order_cancellation_policy.py
class OrderCancellationPolicy:
    """
    [Domain Service]
    취소 가능 여부는 Order 상태 + 배송 진행 상태의 조합으로 결정된다.
    Order Aggregate만으로는 판단 불가 → Domain Service로 추출.
    """
    def can_cancel(self, order: Order, shipping_status: DeliveryStatus) -> bool:
        if order.status in (OrderStatus.SHIPPED, OrderStatus.CANCELLED):
            return False
        if shipping_status == DeliveryStatus.IN_TRANSIT:
            return False
        return True
```

> **Rule (Evans):** 도메인 서비스는 Entity나 VO의 자연스러운 메서드가 되지 않는 연산을 담는다. Stateless이어야 한다.

---

## 6. Saga — DDD Process Manager 관점 보완

### 문제

`order_fulfillment_saga.py`가 `application/sagas/`에 위치하는데, **Saga의 상태(SagaState)가 영속화되는 방법과 실패 복구 지점(Checkpoint)**이 설계에 없다. 서버 재시작 시 진행 중인 Saga가 어디서부터 재개되는지 불명확하다.

또한 Saga가 "결제 PG 호출"(외부 I/O)을 직접 수행하는데, **DDD에서 Saga(Process Manager)는 이벤트를 보내고 Command를 발행하는 역할만 한다.** 실제 외부 호출은 Command Handler가 담당해야 한다.

### 보완 — SagaState 영속화 및 책임 분리

```python
# application/sagas/order_fulfillment_saga.py

class OrderFulfillmentSagaState(Enum):
    STARTED = "STARTED"
    PAYMENT_REQUESTED = "PAYMENT_REQUESTED"
    PAYMENT_CONFIRMED = "PAYMENT_CONFIRMED"
    SHIPMENT_REQUESTED = "SHIPMENT_REQUESTED"
    COMPLETED = "COMPLETED"
    COMPENSATING = "COMPENSATING"  # 보상 트랜잭션 진행 중
    FAILED = "FAILED"

# adapters/driven/persistence/saga_orm.py
class SagaStateORM(models.Model):
    saga_id = models.UUIDField(primary_key=True)
    order_id = models.UUIDField(db_index=True)
    saga_type = models.CharField(max_length=100)
    current_state = models.CharField(max_length=50)
    context = models.JSONField()           # 각 step 결과 스냅샷
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Saga의 역할 재정의 (Command 발행만, 직접 호출 금지):**

```
[Before — 잘못된 패턴]
Saga.step_request_payment()
    └─ PaymentGateway.charge()   ← Saga가 외부 시스템 직접 호출 (책임 혼재)

[After — DDD Process Manager 패턴]
Saga.step_request_payment()
    └─ dispatch(RequestPaymentCommand(order_id, amount))
         └─ RequestPaymentCommandHandler
              └─ PaymentGateway.charge()   ← Handler가 외부 호출, 결과를 이벤트로 발행
```

---

## 7. 도메인 이벤트 발행 메커니즘 불명확

### 문제

`domain/events/internal.py`에 이벤트 클래스가 정의되지만, **Aggregate가 이벤트를 어떻게 등록하고, Application 계층이 이를 어떻게 수집·디스패치하는지** 구체적 메커니즘이 없다. Django signals를 쓰는지, 커스텀 이벤트 버스를 쓰는지 불명확하다.

### 보완 — 도메인 이벤트 수집 패턴 (Collect-and-Dispatch)

```python
# domain/model/aggregate_root.py  ← 신규 추가
class AggregateRoot:
    """모든 Aggregate Root의 기반 클래스."""
    def __init__(self):
        self._domain_events: list[DomainEvent] = []

    def _record_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def collect_events(self) -> list[DomainEvent]:
        events, self._domain_events = self._domain_events, []
        return events

# domain/model/order.py
class Order(AggregateRoot):
    def confirm_payment(self, payment_id: PaymentId) -> None:
        self.status = self.status.transition_to(OrderStatus.PAID)
        self._record_event(PaymentConfirmed(
            order_id=self.id,
            payment_id=payment_id,
            amount=self.total_amount,
            occurred_at=now()
        ))

# application/commands/confirm_payment_handler.py
class ConfirmPaymentCommandHandler:
    def handle(self, cmd: ConfirmPaymentCommand) -> None:
        with self.uow:
            order = self.uow.orders.get(cmd.order_id)
            order.confirm_payment(cmd.payment_id)
            self.uow.commit()
            # 커밋 후 이벤트 디스패치 (동기 핸들러 연결)
            for event in order.collect_events():
                self.event_dispatcher.dispatch(event)
```

> **Django signals 사용 금지:** signals는 도메인과 인프라의 결합을 만든다. 이벤트 디스패치는 Application 계층이 명시적으로 제어해야 한다.

---

## 8. 통합 이벤트 Published Language — 스키마 미정의

### 문제

`OrderConfirmedV1`이 Published Language라고 명시되었지만 **실제 필드·타입·버전 진화 정책**이 없다. 외부 계약(Published Language)은 API 스펙과 동일하게 명세되어야 한다.

### 보완 — 통합 이벤트 스키마 명세

```python
# domain/events/integration.py

@dataclass(frozen=True)
class OrderConfirmedV1:
    """
    [Published Language — 외부 계약]
    이 이벤트의 필드명·타입은 하위 호환성을 보장한다.
    Breaking change는 OrderConfirmedV2로 신버전을 발행하고
    일정 기간 V1/V2를 병행 발행한 후 V1 폐기.

    schema_version: "1.0"
    owner_context: "order"
    consumers: ["shipping", "notification", "analytics"]
    """
    # --- 필수 메타 ---
    event_id: str          # UUID, 멱등성 키
    event_type: str        # "order.confirmed.v1" (고정)
    schema_version: str    # "1.0"
    occurred_at: datetime  # ISO 8601 UTC

    # --- 페이로드 ---
    order_id: str          # UUID
    customer_id: str       # UUID
    total_amount: int      # 원(KRW) 정수, 소수점 없음
    currency: str          # "KRW"
    shipping_address: ShippingAddressPayload
    order_lines: list[OrderLinePayload]

    # --- 절대 포함하지 않는 것 ---
    # payment_pg_transaction_id  ← 내부 구현 노출 금지
    # internal_order_status      ← 도메인 내부 상태 노출 금지

@dataclass(frozen=True)
class ShippingAddressPayload:
    recipient_name: str
    phone: str
    postal_code: str
    street_address: str
    detail_address: str

@dataclass(frozen=True)
class OrderLinePayload:
    product_id: str
    product_name: str      # 스냅샷 — 현재 상품명
    quantity: int
    unit_price: int        # 원(KRW)
    subtotal: int          # quantity * unit_price
```

---

## 9. 멱등성 설계 불완전

### 문제

"모든 Command Handler는 `command_id` 기반 dedup 테이블 또는 도메인 상태 검사로 중복 처리 방지"라고 언급되지만, **두 방법 중 어느 것을 언제 쓰는지 기준이 없다.** 특히 Webhook 기반 결제 확인은 중복 수신이 빈번하므로 설계가 필수다.

### 보완 — 멱등성 레이어 설계

| 구분 | 방법 | 적용 대상 |
|---|---|---|
| **도메인 상태 검사** | `if order.status != AWAITING_PAYMENT: return` | Order 상태 전이 Command (confirm_payment, cancel) |
| **Dedup 테이블** | `ProcessedCommand(command_id, processed_at)` INSERT 중복 시 ignore | 외부에서 재전송되는 Webhook Command, Saga step |
| **PG idempotency-key** | Toss API 헤더 `Idempotency-Key: {order_id}` | 결제 요청 재시도 |

```python
# adapters/driven/persistence/processed_command_orm.py
class ProcessedCommandORM(models.Model):
    """
    외부 Command의 멱등성 보장용 dedup 테이블.
    UoW 트랜잭션 내에서 INSERT — 중복 시 IntegrityError → 무시.
    """
    command_id = models.UUIDField(primary_key=True)
    command_type = models.CharField(max_length=100)
    processed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "processed_commands"
```

---

## 10. Product/Inventory BC와의 관계 미정의

### 문제

`OrderLine`에 `product_id`, `unit_price`가 있지만 **주문 생성 시 재고 확인(Stock Check)을 어디서 어떻게 수행하는지** 완전히 누락되어 있다. 이는 두 BC 간 경계 설계의 핵심이다.

### 보완 — Product/Inventory BC 연동 전략

**Option A (권장 — 읽기 전용 조회 후 주문):**

```
PlaceOrderCommandHandler
  1. ProductQueryService.get_snapshots(product_ids)
     → 현재 가격·재고 조회 (읽기 전용, Inventory BC의 Query Model)
  2. Order.place(order_lines_with_snapshot)
     → 가격 스냅샷을 Order 내부에 저장 (이 시점 이후 가격 변동 무관)
  3. ReserveStockCommand → Inventory BC
     → Outbox를 통해 재고 예약 이벤트 발행
  4. Inventory BC가 StockReservedV1 또는 StockInsufficientV1 이벤트 발행
  5. Order Saga가 응답 수신 후 결제 진행 또는 주문 실패 처리
```

**Context Map 추가:**

```
Order BC ──ReserveStockCommand──► Inventory BC (Customer/Supplier)
Order BC ◄──StockReservedV1────── Inventory BC
```

---

## 11. 모놀리스 → 마이크로서비스 전환 — 데이터 전략 누락

### 문제

"분리 시점에 바뀌는 것" 표에 도메인 코드 변경 없음은 맞지만, **분리 전환 기간 중 공유 DB에서 별도 DB로 데이터 소유권을 이전하는 전략**이 없다. 실전에서 가장 어려운 부분이다.

### 보완 — 데이터 분리 로드맵

```
[Phase 0 — 현재]
  단일 DB, Order 테이블과 Shipping 테이블이 같은 DB
  Cross-table JOIN 쿼리 존재 가능성 → 점진 제거 필요

[Phase 1 — 논리적 분리]
  같은 DB, 다른 스키마(schema/prefix)
  Cross-table JOIN 완전 금지 (lint/CI로 강제)
  BC 간 통신은 오직 통합 이벤트만

[Phase 2 — 물리적 분리 준비]
  Shipping BC를 별도 프로세스로 배포 (DB는 아직 공유)
  ShippingGateway 어댑터를 HTTP 클라이언트로 교체
  이중 쓰기(Dual Write) 기간 운영

[Phase 3 — 완전 분리]
  Shipping DB 분리
  Order DB의 shipping 관련 데이터 마이그레이션
  읽기 일관성은 이벤트 프로젝션으로 대체
```

---

## 12. 테스트 전략 누락

### 문제

DDD의 핵심 장점 중 하나는 **도메인 로직을 DB·HTTP 없이 단위 테스트 가능**한 것이다. 이 장점을 살리는 테스트 피라미드가 없다.

### 보완 — 테스트 피라미드

```
tests/
├── domain/                          # [빠름, DB/HTTP 없음] 불변식·상태 전이 검증
│   ├── test_order_aggregate.py      # Order 불변식 단위 테스트
│   ├── test_order_status.py         # 상태 전이 매트릭스 전체 테스트
│   └── test_money_vo.py             # Money VO 연산 테스트
├── application/                     # [중간] 인메모리 Fake 사용
│   ├── test_place_order_handler.py  # FakeOrderRepository, FakePaymentGateway
│   └── test_saga.py                 # Saga 상태 전이 테스트
└── integration/                     # [느림] 실제 DB, 외부 Mock
    ├── test_django_repository.py    # DjangoOrderRepository ↔ 실제 DB
    └── test_toss_adapter.py         # TossPaymentAdapter ↔ Wiremock
```

```python
# tests/application/test_place_order_handler.py
def test_place_order_assigns_awaiting_payment_status():
    # Arrange
    repo = FakeOrderRepository()
    uow = FakeUnitOfWork(orders=repo)
    handler = PlaceOrderCommandHandler(uow=uow)

    cmd = PlaceOrderCommand(
        customer_id=CustomerId("c-001"),
        lines=[OrderLineCommand(product_id="p-001", quantity=2, unit_price=Money(10000, "KRW"))],
        shipping_address=sample_address()
    )

    # Act
    order_id = handler.handle(cmd)

    # Assert
    saved_order = repo.get(order_id)
    assert saved_order.status == OrderStatus.AWAITING_PAYMENT
    assert len(saved_order.collect_events()) == 1
    assert isinstance(saved_order.collect_events()[0], OrderPlaced)
```

---

## 13. 기타 보완 사항 (소항목)

### 13-1. `OrderRepository.save()` 변경 감지 전략

Django ORM은 변경 감지(Dirty Tracking)가 없으므로 `save()`에서 항상 전체 필드 UPDATE가 발생한다. 성능 최적화가 필요한 경우 **버전 필드(Optimistic Lock)** 를 명시적으로 설계해야 한다.

```python
# domain/model/order.py
class Order(AggregateRoot):
    version: int = 0  # Optimistic Locking용

# adapters/driven/persistence/django_order_repository.py
def save(self, order: Order) -> None:
    updated = OrderORM.objects.filter(
        id=order.id, version=order.version  # 충돌 감지
    ).update(..., version=order.version + 1)
    if updated == 0:
        raise ConcurrencyConflict(f"Order {order.id} 동시 수정 충돌")
```

### 13-2. `Money` Value Object — 통화 혼합 방지

```python
# domain/model/money.py
@dataclass(frozen=True)
class Money:
    amount: int     # 최소 단위(원), 소수점 없음
    currency: str   # "KRW"

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise CurrencyMismatch(f"{self.currency} + {other.currency} 불가")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, quantity: int) -> "Money":
        if quantity < 0:
            raise ValueError("수량은 0 이상이어야 합니다")
        return Money(self.amount * quantity, self.currency)
```

### 13-3. Query 모델 갱신 시점 명시

CQRS 수준 1에서 `order_summary_view`의 갱신을 **언제 트리거**하는지 명시 필요. 수준 1에서는 Write 트랜잭션 내 동기 갱신이 가장 단순하다.

```
[Write 트랜잭션 내]
  1. OrderORM UPDATE
  2. OrderSummaryView UPSERT   ← 동일 atomic() 블록 내
  3. Outbox INSERT
  4. COMMIT

→ 조회 측 뷰가 항상 최신 (수준 1의 장점)
→ 수준 2(별도 DB) 전환 시 이 부분을 이벤트 프로젝션으로 교체
```

---

## 요약 — 보완 우선순위

| 우선순위 | 항목 | 이유 |
|---|---|---|
| **P0 (즉시)** | Aggregate 불변식 명세 | 없으면 도메인 레이어의 존재 의의 없음 |
| **P0 (즉시)** | 상태 전이 매트릭스 + InvalidStateTransition | 버그 방지의 핵심 |
| **P0 (즉시)** | 도메인 이벤트 수집 메커니즘 (AggregateRoot 기반) | Django signals 의존 방지 |
| **P1 (설계 중)** | Ubiquitous Language 사전 | 팀 커뮤니케이션 기반 |
| **P1 (설계 중)** | Context Map | BC 간 계약·팀 구조 결정 |
| **P1 (설계 중)** | SagaState 영속화 + Process Manager 책임 분리 | 장애 복구 설계 |
| **P1 (설계 중)** | OrderConfirmedV1 스키마 명세 | Published Language 계약 |
| **P2 (구현 전)** | 도메인 서비스 식별 | Anemic Domain 방지 |
| **P2 (구현 전)** | 멱등성 Dedup 테이블 설계 | Webhook 중복 처리 |
| **P2 (구현 전)** | 테스트 피라미드 | DDD 장점 실현 |
| **P3 (분리 준비)** | 데이터 분리 로드맵 | Shipping 분리 시 가장 어려운 부분 |
| **P3 (분리 준비)** | Product/Inventory BC 연동 전략 | 재고 확인 설계 |
