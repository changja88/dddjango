# DDD 관점 아키텍처 리뷰 — OrderService 코드 리뷰 결과 검토

> 대상 프롬프트: `OrderService.confirm_order()` 코드 아키텍처 리뷰  
> 대상 결과물: 레거시 ERP 통합 재고 코드 리팩터링 (`inventory/`)  
> 리뷰 기준: Domain-Driven Design (Evans, Vernon), Hexagonal Architecture (Cockburn)

---

## 0. 최우선 지적 — 결과물이 프롬프트에 답하지 않음

이것이 이 리뷰에서 가장 중요한 문제다.

| 항목 | 프롬프트 요구 | 결과물이 실제로 한 것 |
|---|---|---|
| **대상 코드** | `order/domain/order_service.py`의 `OrderService.confirm_order()` | `inventory/services.py`의 재고 코드 |
| **도메인** | 주문(Order) BC | 재고(Inventory) BC |
| **외부 시스템** | Stripe(결제), 이메일, 배송 서비스 | ERP Oracle DB |
| **핵심 문제** | 결제·이메일·배송이 단일 메서드에 결합 | ERP 직접 호출 결합 |

결과물 자체(ERP 재고 리팩터링)는 DDD 관점에서 상당 부분 올바르지만, **주문 처리 코드의 실제 문제를 전혀 다루지 않았다.** 아래에서 두 가지를 모두 다룬다.

1. 원래 프롬프트(OrderService)가 요구하는 DDD 리뷰
2. 결과물(Inventory ERP)의 DDD 보완점

---

## 파트 1. 원래 프롬프트에 대한 DDD 리뷰 (누락된 부분)

### 1-1. `OrderService.confirm_order()`의 핵심 문제 목록

```python
class OrderService:
    def confirm_order(self, order_id: int) -> dict:
        order = OrderModel.objects.select_related('user').get(id=order_id)  # [문제 A]
        stripe = Stripe(api_key="sk_live_xxx")                              # [문제 B]
        charge = stripe.charges.create(...)                                 # [문제 C]
        order.status = "confirmed"                                           # [문제 D]
        order.save()                                                         # [문제 E]
        send_confirmation_email(...)                                         # [문제 F]
        requests.post("http://shipping-service/api/shipments", ...)         # [문제 G]
        return {"order_id": ..., "status": ..., "items": ...}               # [문제 H]
```

| 코드 위치 | 문제 | DDD/설계 원칙 위반 |
|---|---|---|
| A | ORM Model이 도메인 레이어에 직접 노출 | 도메인이 인프라(Django ORM)에 의존 — DIP 위반 |
| B | API Key 하드코딩 | 보안 위반. Composition Root 부재 |
| C | 결제 PG 직접 호출 | ACL 없음. 도메인이 외부 시스템 어휘(`stripe.charges`)를 직접 사용 |
| D | `order.status = "confirmed"` 직접 할당 | 불변식 없는 Anemic Domain. 상태 전이 규칙 없음 |
| E | `order.save()` | Repository 패턴 없음. ORM이 도메인 객체 역할을 겸함 |
| F | `send_confirmation_email()` | 도메인 이벤트 없이 부수효과를 Use Case에서 직접 호출 |
| G | `requests.post(...)` 직접 호출 | ACL 없음. 배송 시스템 URL이 도메인 코드에 하드코딩 |
| H | Command가 상세 데이터를 반환 | CQS 위반. 쓰기가 읽기를 겸함 |

### 1-2. OrderService가 해야 했던 DDD 구조

```
[요청한 리뷰의 올바른 답변 구조]

order/
├── domain/
│   ├── model/
│   │   ├── order.py              # Order Aggregate Root — 불변식, 상태 전이
│   │   ├── order_status.py       # OrderStatus VO — 전이 규칙 캡슐화
│   │   └── money.py              # Money VO
│   ├── events/
│   │   ├── internal.py           # OrderConfirmed, PaymentApproved
│   │   └── integration.py        # OrderConfirmedV1 (Published Language)
│   └── ports/
│       ├── order_repository.py   # OrderRepository (Aggregate 단위)
│       ├── payment_gateway.py    # PaymentGateway.charge() — Stripe 어휘 없음
│       └── shipping_gateway.py   # ShippingGateway.create_shipment()
├── application/
│   └── commands/
│       └── confirm_order_handler.py  # Use Case: 조율만, 인프라 모름
└── adapters/
    ├── payment/
    │   ├── stripe_payment_adapter.py # PaymentGateway 구현
    │   └── stripe_translator.py      # Stripe 응답 → 도메인 VO
    └── shipping/
        └── http_shipping_adapter.py  # ShippingGateway 구현
```

### 1-3. 결제·이메일·배송 결합의 DDD 해법

`confirm_order`가 결제 → 이메일 → 배송을 순차로 직접 호출하는 것은 **Saga 없는 분산 트랜잭션** 시도다. 결제 성공 후 배송 API 실패 시 롤백이 없다.

```python
# 올바른 Application Service (Command Handler)
class ConfirmOrderCommandHandler:
    def handle(self, cmd: ConfirmOrderCommand) -> None:
        with self.uow:
            order = self.uow.orders.get(cmd.order_id)
            # 1. 도메인 메서드 — 불변식 검증 포함
            order.confirm_payment(cmd.payment_token)
            # 2. Outbox에 통합 이벤트 삽입 (같은 트랜잭션)
            self.uow.outbox.append(OrderConfirmedV1.from_order(order))
            self.uow.commit()
        # 이메일·배송 알림은 이벤트 핸들러가 비동기로 처리
        # → 실패해도 주문 상태는 이미 PAID로 확정됨
```

---

## 파트 2. 결과물(Inventory ERP 리팩터링)의 DDD 보완점

결과물이 올바르게 적용한 부분은 인정하되, DDD 관점에서 누락되거나 미흡한 점을 항목별로 기술한다.

---

### 2-1. Aggregate 경계와 불변식 미정의

#### 문제

`StockItem`이 Aggregate Root로 언급되지만 **불변식이 명시되지 않았다.** `reserve()` 메서드가 음수 검사를 하지만 이것이 불변식인지 전처리인지 불분명하다.

또한 `StockItem`이 "상품 단위"인지 "창고별 상품 단위"인지 Aggregate 경계가 불명확하다.

```python
# [Before — 현재 코드]
@dataclass
class StockItem:
    code: ProductCode
    available: Quantity

    def reserve(self, qty: Quantity) -> None:
        if self.available.value < qty.value:
            raise InsufficientStockError(...)
        self.available = Quantity(self.available.value - qty.value)
```

#### 보완 — AggregateRoot 기반 + 불변식 명세

```python
# inventory/domain/aggregate_root.py
class AggregateRoot:
    def __init__(self):
        self._domain_events: list[DomainEvent] = []

    def _record_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def collect_events(self) -> list[DomainEvent]:
        events, self._domain_events = self._domain_events, []
        return events


# inventory/domain/model.py
@dataclass
class StockItem(AggregateRoot):
    """
    [Aggregate Root — 상품 1종 × 창고 1곳의 재고 단위]

    [불변식]
    INV-1: available은 항상 0 이상이다 (음수 재고 불가).
    INV-2: reserved는 available을 초과할 수 없다.
    INV-3: 동일 StockItem에 대한 예약은 낙관적 잠금(version)으로 직렬화된다.

    [Aggregate 경계]
    StockItem 하나 = 하나의 ProductCode + 하나의 WarehouseId.
    다중 창고 시나리오에서 warehouse_id가 식별자에 포함된다.
    """
    code: ProductCode
    warehouse_id: WarehouseId   # ← 창고 개념 추가
    available: Quantity
    reserved: Quantity = field(default_factory=lambda: Quantity(0))
    version: int = 0            # ← 낙관적 잠금

    def reserve(self, qty: Quantity) -> None:
        """INV-1, INV-2 보장. 성공 시 StockReserved 이벤트 기록."""
        if self.available.value < qty.value:
            raise InsufficientStockError(self.code, qty, self.available)
        self.available = Quantity(self.available.value - qty.value)
        self.reserved = Quantity(self.reserved.value + qty.value)
        self._record_event(StockReserved(
            product_code=self.code,
            warehouse_id=self.warehouse_id,
            quantity=qty,
        ))

    def release(self, qty: Quantity) -> None:
        """주문 취소 시 예약 재고를 가용 재고로 되돌린다."""
        if self.reserved.value < qty.value:
            raise InvalidStockReleaseError(self.code, qty, self.reserved)
        self.reserved = Quantity(self.reserved.value - qty.value)
        self.available = Quantity(self.available.value + qty.value)
        self._record_event(StockReleased(
            product_code=self.code,
            warehouse_id=self.warehouse_id,
            quantity=qty,
        ))

    def commit(self, qty: Quantity) -> None:
        """배송 출고 확정 시 예약 재고를 실물 감소로 확정한다."""
        if self.reserved.value < qty.value:
            raise InvalidStockCommitError(self.code, qty, self.reserved)
        self.reserved = Quantity(self.reserved.value - qty.value)
        self._record_event(StockCommitted(
            product_code=self.code,
            warehouse_id=self.warehouse_id,
            quantity=qty,
        ))
```

---

### 2-2. 도메인 이벤트 완전 누락

#### 문제

`StockItem.reserve()`가 재고를 차감하지만 **아무런 도메인 이벤트도 발행하지 않는다.** 이벤트 없이는:

- Order BC가 재고 예약 성공 여부를 Saga로 수신할 수 없다
- 재고 소진 알림, 감사 로그, 통계 집계가 불가능하다
- Inventory BC가 분리될 때 Order BC와 통합할 Published Language가 없다

#### 보완 — 도메인 이벤트 정의

```python
# inventory/domain/events.py
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass(frozen=True)
class DomainEvent:
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class StockReserved(DomainEvent):
    """
    [도메인 이벤트 — Inventory BC 내부]
    재고가 성공적으로 예약된 사건.
    Order BC의 Saga가 이 이벤트를 받아 결제 단계로 진행한다.
    """
    product_code: ProductCode
    warehouse_id: WarehouseId
    quantity: Quantity
    order_id: str             # ← 어느 주문의 예약인지 추적


@dataclass(frozen=True)
class StockExhausted(DomainEvent):
    """가용 재고가 0이 된 사건. 상품 담당자에게 알림 트리거."""
    product_code: ProductCode
    warehouse_id: WarehouseId


@dataclass(frozen=True)
class StockReleased(DomainEvent):
    """주문 취소로 예약 재고가 반환된 사건."""
    product_code: ProductCode
    warehouse_id: WarehouseId
    quantity: Quantity
    order_id: str
```

---

### 2-3. Ubiquitous Language 부재 — 재고 용어 혼재

#### 문제

결과물에서 "재고 예약(reserve)"이라는 용어를 쓰지만 **비즈니스에서 쓰는 재고 용어와의 매핑이 없다.** 일반적으로 재고 도메인에는 세 가지 재고 상태가 공존한다.

#### 보완 — 재고 Ubiquitous Language 사전

| 도메인 용어 | 정의 | 코드 상 표현 | 금지 동의어 |
|---|---|---|---|
| **가용 재고(Available Stock)** | 현재 주문 가능한 수량 | `StockItem.available` | free_stock, stock |
| **예약 재고(Reserved Stock)** | 주문 완료됐으나 배송 출고 미완료 수량 | `StockItem.reserved` | pending_stock |
| **실물 재고(Physical Stock)** | 창고에 실제 존재하는 수량 = available + reserved | 계산값 | total_stock |
| **재고 예약(Reserve)** | 주문 확정 시 가용→예약으로 이동 | `StockItem.reserve()` | allocate, lock |
| **재고 반환(Release)** | 주문 취소 시 예약→가용으로 복귀 | `StockItem.release()` | cancel, unlock |
| **재고 확정(Commit)** | 배송 출고 완료 시 예약 수량 소멸 | `StockItem.commit()` | deduct, consume |

> `reserve_stock`이라는 함수명은 `reserve()`로 간소화하는 것이 맞지만, 반드시 `release()`와 `commit()`도 함께 설계해야 재고 라이프사이클이 완성된다. 현재 결과물에는 release/commit이 없다.

---

### 2-4. Unit of Work 미적용의 트랜잭션 문제

#### 문제

결과물에서 UoW를 "나중에 도입"한다고 했지만, **현재 구조의 `ErpStockRepository.save()`가 내부에서 `conn.commit()`을 직접 호출한다.** 이는 세 가지 문제를 만든다.

```python
# [현재 코드 — 문제]
def save(self, stock: StockItem) -> None:
    with self._client.cursor() as (cursor, conn):
        cursor.execute("UPDATE TB_INV_MASTER ...", [...])
        conn.commit()   # ← Repository가 트랜잭션 경계를 소유 — 안티패턴
```

1. **Repository가 트랜잭션 경계를 소유한다** — DDD에서 트랜잭션 경계는 Use Case(Application Service) 수준에서 결정되어야 한다.
2. **다중 Aggregate 업데이트 불가** — 예약 시 `StockItem`과 `StockReservation` 두 Aggregate를 원자적으로 갱신해야 할 때 구조적으로 불가능하다.
3. **테스트에서 트랜잭션 롤백 불가** — 각 save가 즉시 commit하므로 테스트 격리가 어렵다.

#### 보완 — ERP 컨텍스트의 UoW (제한적 적용)

```python
# inventory/domain/ports.py
class UnitOfWork(ABC):
    stock: StockRepository

    @abstractmethod
    def __enter__(self) -> "UnitOfWork": ...

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...


# inventory/infrastructure/erp/unit_of_work.py
class ErpUnitOfWork(UnitOfWork):
    """ERP Oracle 트랜잭션 경계를 Application Service 수준으로 끌어올린다."""
    def __init__(self, client: ErpOracleClient) -> None:
        self._client = client

    def __enter__(self):
        self._conn = self._client.get_connection()
        self.stock = ErpStockRepository(self._conn, ErpTranslator())
        return self

    def commit(self) -> None:
        self._conn.commit()
        # 커밋 후 도메인 이벤트 디스패치
        for event in self._collect_events():
            self._event_dispatcher.dispatch(event)

    def rollback(self) -> None:
        self._conn.rollback()


# inventory/application/services.py
class StockReservationService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def reserve(self, code: ProductCode, qty: Quantity, order_id: str) -> None:
        with self._uow:               # ← 트랜잭션 경계가 Use Case에 있음
            stock = self._uow.stock.get(code)
            if stock is None:
                raise StockNotFoundError(code.value)
            stock.reserve(qty)
            self._uow.stock.save(stock)
            self._uow.commit()        # ← 커밋 책임이 Application Service에 있음
```

---

### 2-5. `ProductSyncService` — CQS 위반 및 용어 문제

#### 문제

```python
class ProductSyncService:
    def sync(self, code: ProductCode) -> Product:  # ← Command인데 값 반환
        product = self._catalog.fetch(code)
        ...
        return product  # ← CQS 위반
```

`sync`라는 이름이 **기술적 동작(동기화)**을 표현한다. DDD에서 메서드명은 도메인 행위를 표현해야 한다. 또한 `sync()`가 Product를 반환하는 것은 CQS 위반이다 — 이것이 Command라면 반환값이 없어야 한다.

#### 보완

```python
# 의도 1: ERP에서 상품 정보를 우리 BC로 "가져오는" 것이 목적이라면
class ImportProductFromErpCommandHandler:
    """Command Handler — 반환값 없음."""
    def handle(self, cmd: ImportProductCommand) -> None:
        product = self._catalog.fetch(cmd.product_code)
        if product is None:
            raise ProductNotFoundInErpError(cmd.product_code)
        self._product_repo.add(product)   # 우리 BC의 로컬 저장소에 저장
        # → 이후 조회는 우리 DB에서 수행

# 의도 2: ERP를 Read-through로 조회하는 것이 목적이라면
class ErpProductQueryService:
    """Query Service — 상태 변경 없음."""
    def get_product(self, code: ProductCode) -> Product:
        return self._catalog.fetch(code)
```

---

### 2-6. Composition Root — Connection Pool 문제

#### 문제

```python
# [현재 코드]
def build_stock_query_service() -> StockQueryService:
    client = ErpOracleClient(...)     # ← 호출마다 새 client 생성

def build_stock_reservation_service() -> StockReservationService:
    client = ErpOracleClient(...)     # ← 또 다른 client 생성 (별도 Pool)
```

각 빌더 함수가 독립적인 `ErpOracleClient`를 생성하므로, 요청마다 Oracle Connection이 개별 생성·소멸된다. ERP Oracle은 Connection 비용이 크다.

#### 보완 — 싱글턴 Client + Connection Pool

```python
# inventory/composition.py
from functools import lru_cache

@lru_cache(maxsize=1)
def _get_erp_client() -> ErpOracleClient:
    """프로세스 생애주기 동안 단일 Client(Connection Pool) 공유."""
    return ErpOracleClient(
        dsn=settings.ERP_DSN,
        user=settings.ERP_USER,
        password=settings.ERP_PASSWORD,
        pool_min=2,
        pool_max=10,         # ← Connection Pool 설정
    )

def build_stock_reservation_service() -> StockReservationService:
    return StockReservationService(
        uow=ErpUnitOfWork(client=_get_erp_client())
    )
```

---

### 2-7. `StockRepository.save()` — ERP 직접 쓰기의 아키텍처 결정 누락

#### 문제

결과물이 ERP Oracle DB에 직접 UPDATE를 수행하는데, **이 결정의 타당성과 위험이 문서에 없다.** 레거시 ERP에 직접 쓰기를 허용하면:

- ERP 스키마 변경 시 우리 코드가 데이터를 오염시킬 수 있다
- ERP가 자체적으로 재고 검증 프로시저를 갖고 있을 경우 우회가 된다
- ERP 감사 로그에 우리 시스템의 변경이 기록되지 않을 수 있다

#### 보완 — 아키텍처 결정 기록(ADR) 필요

```markdown
## ADR-001: ERP Oracle DB 직접 쓰기 허용 여부

### 상황
재고 예약 시 ERP의 TB_INV_MASTER 테이블을 직접 UPDATE해야 하는가?

### 선택지
A. **ERP API 사용** — ERP가 제공하는 재고 예약 API 호출
B. **ERP DB 직접 쓰기** — TB_INV_MASTER에 직접 UPDATE (현재 선택)
C. **자체 DB에 재고 복제** — ERP 데이터를 우리 DB에 동기화 후 우리 DB에 쓰기

### 결정: B (이유 명시 필요)
- ERP가 API를 제공하지 않는 경우에만 B를 선택
- ERP DBA 승인 필요
- ERP 스키마 변경 알림 프로세스 수립 필요

### 위험 완화
- ErpTranslator를 통해 변경 영향을 한 곳에 집중
- ErpStockRepository의 테스트를 ERP 스키마와 연동하여 회귀 감지
```

---

### 2-8. 테스트 전략 미흡

#### 문제

결과물 끝에 "Fake 어댑터로 테스트 가능"이라고 언급하지만 **실제 테스트 구조가 없다.**

#### 보완 — Fake 어댑터 + 테스트 예시

```python
# tests/fakes.py
class FakeStockRepository(StockRepository):
    def __init__(self):
        self._store: dict[ProductCode, StockItem] = {}

    def get(self, code: ProductCode) -> StockItem | None:
        return self._store.get(code)

    def save(self, stock: StockItem) -> None:
        self._store[stock.code] = stock


class FakeUnitOfWork(UnitOfWork):
    committed = False

    def __init__(self):
        self.stock = FakeStockRepository()

    def __enter__(self): return self
    def commit(self): self.committed = True
    def rollback(self): pass


# tests/application/test_stock_reservation.py
def test_reserve_decrements_available_and_records_event():
    # Arrange
    uow = FakeUnitOfWork()
    code = ProductCode("PROD-001")
    uow.stock.save(StockItem(
        code=code,
        warehouse_id=WarehouseId("WH-01"),
        available=Quantity(10),
    ))
    service = StockReservationService(uow=uow)

    # Act
    service.reserve(code, Quantity(3), order_id="ORD-001")

    # Assert
    stock = uow.stock.get(code)
    assert stock.available == Quantity(7)
    assert stock.reserved == Quantity(3)
    assert uow.committed
    events = stock.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], StockReserved)
    assert events[0].quantity == Quantity(3)

def test_reserve_raises_when_insufficient():
    uow = FakeUnitOfWork()
    code = ProductCode("PROD-001")
    uow.stock.save(StockItem(code=code, warehouse_id=WarehouseId("WH-01"), available=Quantity(2)))
    service = StockReservationService(uow=uow)

    with pytest.raises(InsufficientStockError):
        service.reserve(code, Quantity(5), order_id="ORD-001")
    assert not uow.committed   # 실패 시 커밋 안 됨
```

---

### 2-9. Order BC와 Inventory BC의 통합 전략 누락

#### 문제

결과물이 Inventory BC를 독립적으로 설계했지만, **Order BC와 어떻게 통합하는지 전혀 언급이 없다.** 주문 처리(`OrderService.confirm_order`)의 핵심 흐름이 재고 예약을 필요로 하는데, 이 BC 간 통합 설계가 빠져 있다.

#### 보완 — Order ↔ Inventory 통합 전략

```
[통합 방식 결정]

Option A — Synchronous (단순, 현재 모놀리스에 적합):
  OrderFulfillmentSaga
    └─ StockReservationService.reserve(product_code, qty, order_id)
       (같은 프로세스 내 직접 호출, 동기)

Option B — Async Event (향후 분리 대비):
  Order BC: ReserveStockCommand → Outbox
  Inventory BC: StockReservationCommandHandler 소비
               → StockReserved or StockInsufficientV1 이벤트 발행
  Order Saga: 이벤트 수신 후 결제 단계 진행

[Context Map 추가 필요]
Order BC ──ReserveStockCommand──► Inventory BC (Customer/Supplier)
Order BC ◄──StockReservedV1─────── Inventory BC
Order BC ◄──StockInsufficientV1─── Inventory BC
```

---

## 종합 보완 우선순위

### 파트 1 (누락된 OrderService 리뷰) — 전부 재작성 필요

원래 프롬프트(OrderService)에 대한 답변이 없으므로, 최소한 다음을 포함해야 한다:

1. `confirm_order` 메서드의 8가지 문제 진단
2. Order Aggregate Root 설계 (불변식, 상태 전이)
3. PaymentGateway, ShippingGateway ACL 설계
4. Outbox + Saga로 결제→배송 분리
5. CQS 적용 (Command는 void, 조회는 별도 Query)

### 파트 2 (Inventory 결과물 보완)

| 우선순위 | 항목 | 이유 |
|---|---|---|
| **P0** | 도메인 이벤트(`StockReserved`, `StockReleased`) | Order Saga와 통합 불가 |
| **P0** | `release()` + `commit()` 메서드 추가 | 재고 라이프사이클 불완전 |
| **P0** | UoW 트랜잭션 경계를 Application Service로 이동 | Repository 내부 commit 제거 |
| **P1** | AggregateRoot 기반 + 불변식 명세 | DDD 핵심 artifact |
| **P1** | Ubiquitous Language 사전 | 팀 공유 언어 |
| **P1** | Order ↔ Inventory 통합 전략 | BC 간 협력 설계 없음 |
| **P2** | Connection Pool 통합 | 운영 안정성 |
| **P2** | `ProductSyncService` CQS 위반 수정 | 원칙 일관성 |
| **P2** | 테스트 Fake 어댑터 구현 | DDD 장점 실현 |
| **P3** | ERP 직접 쓰기 ADR 문서화 | 아키텍처 결정 이력 |
