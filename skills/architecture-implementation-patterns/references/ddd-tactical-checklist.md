# DDD 전술 체크리스트 — 구현 시 자주 빠뜨리는 8개 항목

이 reference는 헥사고날·Repository·UoW·ACL을 적용할 때 함께 빠지기 쉬운
DDD 전술 패턴의 **구현 스켈레톤**을 모은 것이다. 깊은 도메인 모델링 이론은
`architecture-ddd`의 references에 있고, 여기는 "코드 작성 직전에 한 번 훑어
빠뜨림을 막는" 용도다.

응답 작성 직전 이 8개 체크리스트를 모두 검토한다. 누락된 항목은 즉시 보강한다.

---

## 1. Ubiquitous Language 사전을 응답에 포함하라

도메인 코드를 제시하면서 용어집을 빠뜨리면, 외부 SDK 어휘
(`payment_token`, `charge.id`, `ZITEM_CD`)가 도메인 필드명에 침투해도
독자가 알아채지 못한다. 응답 첫 또는 마지막 섹션에 다음 형식의 표를 둔다.

```markdown
## Ubiquitous Language

| 도메인 용어 | 정의 | 코드 표현 | 금지 동의어 (외부 어휘) |
|---|---|---|---|
| 결제 승인 (Payment Approval) | PG사가 결제를 확정한 사건 | `PaymentConfirmed` 이벤트, `order.confirm_payment()` | `charge`, `Settlement`, `payment_token` |
| 가용 재고 (Available Stock) | 주문 가능한 수량 | `StockItem.available: Quantity` | `free_stock`, `ZQTY_AVAIL` |
| 보상 취소 (Compensating Cancellation) | 시스템 오류로 인한 자동 무효화 | `OrderCancelledForCompensation` | `Rollback`, `Undo` |
```

> 깊은 내용: `architecture-ddd/references/knowledge-crunching.md`,
> `supple-design.md`

---

## 2. AggregateRoot 추상 베이스 + collect_events

`Aggregate Root`라고 부르면서 `_record_event`/`collect_events` 메커니즘이
없으면, 도메인 이벤트가 흩어진 함수 호출(`event_bus.publish(...)`)로 발행되어
트랜잭션 경계와 어긋난다. 이 문제는 모든 BC에 공통이므로 추상 베이스로 추출한다.

```python
# domain/shared/aggregate_root.py
from typing import TypeVar

E = TypeVar("E")  # DomainEvent

class AggregateRoot:
    """모든 Aggregate Root의 공통 베이스. 이벤트 수집·디스패치 메커니즘만 가진다."""
    def __init__(self) -> None:
        self._domain_events: list = []

    def _record_event(self, event) -> None:
        self._domain_events.append(event)

    def collect_events(self) -> list:
        events, self._domain_events = self._domain_events, []
        return events
```

```python
# 사용
class Order(AggregateRoot):
    def confirm_payment(self, payment_id: PaymentId) -> None:
        self.status = self.status.transition_to(OrderStatus.PAID)
        self._record_event(PaymentConfirmed(...))   # ← 이벤트는 여기서 기록
```

```python
# Command Handler에서 commit 후 디스패치
class ConfirmPaymentHandler:
    def handle(self, cmd):
        with self._uow:
            order = self._uow.orders.get(cmd.order_id)
            order.confirm_payment(cmd.payment_id)
            self._uow.commit()                       # 1. DB commit
        for event in order.collect_events():         # 2. 그 후 dispatch
            self._event_bus.dispatch(event)
```

> 깊은 내용: `architecture-ddd/references/aggregates.md`, `domain-events.md`

---

## 3. Aggregate 라이프사이클 메서드를 셋트로 완성하라

상태 변경 메서드 하나만 두면 ("reserve만 있고 release/commit 없음")
실세계의 워크플로(주문 취소, 배송 출고 확정)에서 도메인이 끊긴다.
한 Aggregate가 가질 수 있는 라이프사이클 메서드를 한 번에 점검한다.

| 도메인 | 셋트로 가져야 할 메서드 |
|---|---|
| StockItem (재고) | `reserve()` / `release()` / `commit()` — 예약·반환·확정 |
| Order (주문) | `place()` / `confirm_payment()` / `request_fulfillment()` / `cancel()` |
| Payment (결제) | `request()` / `approve()` / `fail()` / `refund()` |
| Subscription (구독) | `start()` / `pause()` / `resume()` / `cancel()` / `expire()` |

```python
# inventory 예시 — 라이프사이클 셋트 완성
@dataclass
class StockItem(AggregateRoot):
    code: ProductCode
    available: Quantity
    reserved: Quantity
    committed: Quantity   # 출고 확정된 수량 (감사용)

    def reserve(self, qty: Quantity, order_id: str) -> None:
        if self.available.value < qty.value:
            raise InsufficientStockError(...)
        self.available -= qty
        self.reserved += qty
        self._record_event(StockReserved(self.code, qty, order_id))

    def release(self, qty: Quantity, order_id: str) -> None:
        """주문 취소 — 예약을 가용으로 되돌림."""
        if self.reserved.value < qty.value:
            raise InvalidStockReleaseError(...)
        self.reserved -= qty
        self.available += qty
        self._record_event(StockReleased(self.code, qty, order_id))

    def commit(self, qty: Quantity, order_id: str) -> None:
        """배송 출고 확정 — 예약을 실물 감소로 확정."""
        if self.reserved.value < qty.value:
            raise InvalidStockCommitError(...)
        self.reserved -= qty
        self.committed += qty
        self._record_event(StockCommitted(self.code, qty, order_id))
```

---

## 4. Domain Event vs Integration Event 분리를 명시하라

내부 이벤트(BC 안에서 동기 핸들러로 처리)와 통합 이벤트(BC 경계를 넘는 비동기
계약)를 한 폴더 / 한 모듈에 섞으면, 내부 데이터 구조가 외부 계약으로 누출된다.

```
domain/
  events/
    internal/                       # BC 내부 — 자유롭게 변경 가능
      payment_confirmed.py
      fulfillment_requested.py
    published_language/             # BC 외부 계약 — 호환성 의무
      order_confirmed_v1.py         # event_type, schema_version, 필드 동결
```

| 구분 | Domain Event (internal) | Integration Event (published) |
|---|---|---|
| 위치 | `domain/events/internal/` | `domain/events/published_language/` 또는 `application/integration_events/` |
| 처리 시점 | 동일 트랜잭션 내 또는 직후 | **반드시 트랜잭션 commit 후** |
| 인프라 | In-memory dispatcher | Outbox + Message Bus |
| 필드 변경 | 자유 | 호환성 의무 — V2 신설 후 V1 병행 |
| 내부 구현 노출 | OK | **금지** (PG 식별자, 내부 status 등 제외) |

```python
# domain/events/internal/payment_confirmed.py — 자유 변경
@dataclass(frozen=True)
class PaymentConfirmed:
    order_id: OrderId
    payment_id: PaymentId
    amount: Money

# domain/events/published_language/order_confirmed_v1.py — 동결
@dataclass(frozen=True)
class OrderConfirmedV1:
    event_id: str
    event_type: str = "order.confirmed.v1"
    schema_version: str = "1.0"
    occurred_at: datetime
    order_id: str
    customer_id: str
    total_amount_krw: int
    # payment_id 같은 내부 식별자 노출 금지
```

> 깊은 내용: `architecture-implementation-patterns/references/integration.md` 2장,
> `architecture-ddd/references/domain-events.md`

---

## 5. Saga / Process Manager의 책임 — Command 발행만

Saga가 결제 PG를 직접 호출하면 (`Saga.step → PaymentGateway.charge()`)
재시도/장애 복구 시 책임이 흩어진다. Saga는 Command를 발행하기만 하고,
외부 호출은 Command Handler가 담당한다.

```python
# 안티패턴 — Saga가 외부 시스템 직접 호출
class OrderFulfillmentSaga:
    def step_request_payment(self):
        self.payment_gateway.charge(...)      # ← Saga가 외부 I/O 책임

# 올바른 패턴 — Saga는 Command만 발행
class OrderFulfillmentSaga:
    def step_request_payment(self):
        self.dispatch(RequestPaymentCommand(order_id, amount))

class RequestPaymentHandler:
    def handle(self, cmd):
        result = self.payment_gateway.charge(...)   # ← Handler가 외부 호출
        self.dispatch(PaymentConfirmedEvent(...) if result.ok else PaymentFailedEvent(...))
```

또한 Saga 상태(SagaState)는 **DB에 영속화**해야 서버 재시작 시 복구 가능.

```python
class SagaStateORM(models.Model):
    saga_id = models.UUIDField(primary_key=True)
    order_id = models.UUIDField(db_index=True)
    saga_type = models.CharField(max_length=100)
    current_state = models.CharField(max_length=50)
    context = models.JSONField()             # 각 step 결과 스냅샷
    updated_at = models.DateTimeField(auto_now=True)
```

---

## 6. Outbox at-least-once + 컨슈머 멱등성

Outbox 패턴은 "이벤트 발행 신뢰성"을 보장하지만 "중복 처리 안 됨"은 보장하지
않는다. **Outbox = at-least-once delivery**. 컨슈머는 반드시 멱등성을 처리한다.

```
[발행 측 — Outbox]
  1. Aggregate 변경 + Outbox INSERT를 같은 트랜잭션에서 commit
  2. Outbox Relay가 polling으로 미발행 row를 메시지 버스로 발행
  3. 발행 성공 시 published=true 마킹
  → 메시지 버스 ↔ Relay 사이 장애 시 중복 발행 가능 (at-least-once)

[수신 측 — 컨슈머 멱등성]
  옵션 A: event_id를 ProcessedEvent 테이블에 INSERT (UNIQUE 위반 시 무시)
  옵션 B: 도메인 상태 검사 (이미 PAID면 무시)
  옵션 C: 둘 다 적용 (critical path)
```

응답에 Outbox 패턴을 제시할 때는 반드시 다음 한 줄을 포함한다:
> "Outbox는 at-least-once delivery를 보장한다. 컨슈머는 event_id 기반 dedup
> 또는 도메인 상태 검사로 멱등성을 처리해야 한다."

---

## 7. 멱등성 패턴 3중 적용을 일관되게

`integration.md`의 분류표(도메인 상태검사 / Dedup 테이블 / PG idempotency-key)를
모든 비멱등 경로에 일관되게 적용한다. "결제는 멱등성 처리, 재고는 빠뜨림"
같은 비대칭이 자주 발생한다.

| 경로 | 적용해야 할 멱등성 패턴 |
|---|---|
| Webhook 수신 (PG 결제 확인) | Dedup 테이블 + 도메인 상태 검사 + (PG가 같은 키로 재요청 시) idempotency-key |
| 외부 API 호출 (PG 결제 요청) | PG idempotency-key 헤더 + 응답 캐싱 |
| Saga step 재시도 | Dedup 테이블 (saga_step_id) |
| 사용자 더블 클릭 (주문 생성) | Idempotency-Key 헤더(클라이언트) + Dedup 테이블 |
| Aggregate 상태 전이 Command | 도메인 상태 검사 |

---

## 8. transaction.on_commit vs Outbox 선택 기준

Django `transaction.on_commit`은 트랜잭션 커밋 후 콜백을 실행하는 **단일
프로세스 내 메커니즘**이다. Outbox는 **별도 프로세스 + 메시지 버스**가 있는
영속 메커니즘이다. 잘못 선택하면 손실 또는 과잉 엔지니어링이 된다.

| 상황 | 선택 |
|---|---|
| 같은 프로세스 내에서 즉시 처리, 손실되어도 재시도 가능 (이메일 알림) | `transaction.on_commit` |
| BC 경계를 넘는 메시지, 손실 절대 불가 (결제 → 배송) | **Outbox + 메시지 버스** |
| 단일 프로세스이지만 워커 풀로 분리 (이미지 변환) | Celery + `transaction.on_commit`으로 enqueue |
| 외부 시스템에 통합 이벤트 발행 | **Outbox** |

```python
# 안티패턴 — 통합 이벤트를 on_commit으로 발행 (프로세스 죽으면 손실)
def confirm_payment(order):
    order.confirm_payment()
    transaction.on_commit(
        lambda: kafka.send("order.confirmed", order.to_event())  # ← 손실 가능
    )

# 올바른 패턴 — Outbox INSERT를 같은 트랜잭션에서
def confirm_payment(order):
    order.confirm_payment()
    Outbox.objects.create(
        topic="order.confirmed",
        payload=OrderConfirmedV1.from_order(order).to_dict(),
    )
    # COMMIT 후 별도 Relay 프로세스가 polling으로 발행
```

---

## 9. Value Object 풀세트 — 코드 정의 필수

VO를 "추출됐다", "Money로 표현"이라고 말로만 하면 부족하다. 다음 3종 VO는
응답에 **실제 클래스 코드**로 정의되어야 한다 (개념 언급만으로는 빠짐 처리).

### 9-1. Money VO — 별도 클래스 + currency mismatch

```python
# domain/shared/money.py — 다른 클래스에 currency 필드만 추가하지 말고 별도 VO로
@dataclass(frozen=True)
class Money:
    """
    [Value Object — 금액과 통화의 불가분 쌍]
    INV-1: amount는 0 이상 (음수 금액 금지)
    INV-2: 통화가 다른 Money끼리 연산 불가
    """
    amount: int       # 최소 단위(원), 소수점 없음
    currency: str     # ISO 4217 코드 ("KRW", "USD")

    def __post_init__(self) -> None:
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


class CurrencyMismatch(Exception):
    """서로 다른 통화의 Money 연산 시 발생."""
```

**금지 패턴**: `Price` 클래스에 `currency: str` 필드만 추가. 통화 검증
로직 없음. 이는 Money VO 추출이 아니다.

### 9-2. 도메인 ID VO — frozen dataclass

`int` PK를 코드 곳곳에 노출하지 말고 `OrderId`, `PaymentId`, `CustomerId`
같은 ID VO로 추출한다.

```python
# domain/shared/identifiers.py
@dataclass(frozen=True)
class OrderId:
    value: str        # UUID 권장

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("OrderId는 비어있을 수 없습니다")


@dataclass(frozen=True)
class PaymentId:
    value: str
```

이렇게 분리하면 `def get(order_id: int)` 대신 `def get(order_id: OrderId)`로
시그니처가 자기 문서화된다.

### 9-3. OrderLine 같은 명세 VO — frozen dataclass

```python
@dataclass(frozen=True)
class OrderLine:
    """주문 항목 — 변경되지 않는 명세 단위."""
    product_id: ProductId
    product_name: str       # 스냅샷 (현재 Product 변경 무관)
    quantity: int
    unit_price: Money

    @property
    def subtotal(self) -> Money:
        return self.unit_price * self.quantity
```

> 깊은 내용: `architecture-ddd/references/value-objects-entities.md`

---

## 10. 동시성 제어 — 낙관적 잠금이 기본

비관적 잠금(`SELECT FOR UPDATE`)만 쓰면 ERP/외부 DB 시나리오에서
deadlock·lock contention이 발생한다. 응답에는 **낙관적 잠금**(version 필드 또는
expected_value 가드)을 기본으로 제시하고, 비관적 잠금은 의도적 선택 + 근거를
명시할 때만 사용한다.

```python
# domain/model/<aggregate>/root.py
@dataclass
class StockItem(AggregateRoot):
    code: ProductCode
    available: Quantity
    reserved: Quantity
    version: int = 0           # ← 낙관적 잠금용

# adapters/driven/persistence/erp_stock_repository.py
class ErpStockRepository(StockRepository):
    def save(self, stock: StockItem) -> None:
        # 같은 version으로만 UPDATE 성공. 다른 트랜잭션이 먼저 갱신했으면 실패.
        updated = self._db.execute(
            """
            UPDATE TB_INV_MASTER
               SET ZQTY_AVAIL = :available,
                   ZQTY_RSVD  = :reserved,
                   VERSION    = VERSION + 1
             WHERE ZITEM_CD   = :code
               AND VERSION    = :version
            """,
            {
                "available": stock.available.value,
                "reserved": stock.reserved.value,
                "code": stock.code.value,
                "version": stock.version,
            },
        )
        if updated == 0:
            raise ConcurrencyError(
                f"StockItem {stock.code.value} 동시 수정 충돌 — 재시도 필요"
            )


class ConcurrencyError(Exception):
    """낙관적 잠금 충돌 — 클라이언트는 재조회 후 재시도해야 함."""
```

**선택 기준:**

| 상황 | 권장 |
|---|---|
| 충돌 빈도가 낮음 (대부분의 비즈니스 케이스) | **낙관적 잠금** + 클라이언트 재시도 |
| 충돌 빈도가 매우 높음 (재고가 1개뿐인 핫 아이템) | 비관적 잠금 + 의도적 선택 명시 |
| 분산 트랜잭션 / Saga | 낙관적 잠금 + 보상 트랜잭션 |
| 외부 DB(ERP)에 직접 쓰기 | 낙관적 잠금 (외부 DB lock은 신뢰성·성능 문제) |

> Reference: `persistence.md`의 "트랜잭션 경계의 위치" 섹션과 함께 적용.

---

## 11. 응답 작성 직전 최종 체크 (요약)

응답을 사용자에게 제시하기 전에 다음 11개 항목을 모두 확인한다.

- [ ] Ubiquitous Language 사전 표가 응답에 포함됨 (금지 동의어 컬럼 포함)
- [ ] `AggregateRoot` 추상 베이스 + `_record_event`/`collect_events` 코드가 있음
- [ ] Aggregate 라이프사이클 메서드가 셋트로 완성됨 (예: reserve/release/commit)
- [ ] Domain Event(internal)와 Integration Event(published_language)가 폴더로 분리됨
- [ ] Saga가 Command만 발행하고 외부 I/O는 Handler에서 수행함
- [ ] Outbox 제시 시 at-least-once + 컨슈머 멱등성 한 줄이 있음
- [ ] 멱등성 패턴 3중 적용이 모든 비멱등 경로에 일관되게 적용됨
- [ ] `transaction.on_commit` vs Outbox 선택 기준이 명시됨
- [ ] 파일 트리가 의미군 묶음 (`domain/model/<aggregate>/`) — `hexagonal.md` 참조
- [ ] **Money VO + 도메인 ID VO + OrderLine VO가 실제 클래스 코드로 정의됨**
      (개념 언급만 또는 다른 클래스에 currency 필드 추가는 fail)
- [ ] **낙관적 잠금(version 필드 + ConcurrencyError)이 기본**으로 제시되고
      비관적 잠금은 의도적 선택 + 근거를 명시할 때만 사용
- [ ] **Context Map의 각 BC 간 관계에 유형 라벨이 붙어 있음** —
      Customer-Supplier / Conformist / Published Language / ACL / Shared Kernel /
      Open Host Service / Partnership 중 어떤 관계인지 명시. 단순 BC 목록 나열은 fail
- [ ] **원전 인용이 패턴별로 다양화됨** — Evans/Vernon만 반복하지 말고:
      Hexagonal→Cockburn (2005), Clean→R. Martin (2012),
      Layered/Repository/UoW/Data Mapper/Identity Map→Fowler (2002),
      CQRS→Greg Young, ACL/BC/Aggregate→Evans (2003), Onion→Palermo (2008)
- [ ] **Repository 내부 `conn.commit()` 완전 제거** — Application Service가 UoW
      `commit()`을 호출하므로 Repository.save는 staging만 한다. Repository 내부에
      commit이 잔존하면 다중 Aggregate 트랜잭션이 깨진다 (`persistence.md` 참조)
- [ ] **멱등성 3중 분류는 정확한 명칭 사용** — "도메인 상태 검사 / Dedup 테이블 /
      PG idempotency-key" 세 항목명을 그대로 사용한다. "낙관적 잠금"은 동시성
      제어이지 멱등성 패턴이 아니므로 3중 분류에 섞지 말 것
- [ ] **리팩터링 모드: 원본의 모든 함수가 별도 Before/After/Reason 블록으로 처리됨** —
      예: `get_stock`, `reserve_stock`, `sync_product_info` 셋 모두 별도 블록.
      "흡수됐다"는 말로 한 함수를 빠뜨리는 것은 fail

---

> **참고**: 이 체크리스트는 깊은 이론을 다시 작성한 것이 아니라, 구현 응답에서
> 자주 빠지는 항목의 코드 스켈레톤만 모은 것이다. 도메인 모델링·전략적 DDD의
> 깊은 이해는 다음에서:
> - `architecture-ddd/references/aggregates.md`
> - `architecture-ddd/references/value-objects-entities.md`
> - `architecture-ddd/references/domain-events.md`
> - `architecture-ddd/references/bounded-context.md`
> - `architecture-ddd/references/knowledge-crunching.md`
> - `architecture-ddd/references/supple-design.md`
