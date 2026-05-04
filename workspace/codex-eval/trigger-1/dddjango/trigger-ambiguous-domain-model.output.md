**주요 내용**

도메인 모델은 먼저 “데이터 구조”가 아니라 “비즈니스 언어와 규칙의 경계”로 나누는 게 좋습니다. 순서는 이렇습니다.

1. **하위 도메인부터 나눈다**
   비즈니스가 하는 일을 핵심/지원/범용으로 분류합니다.

| 하위 도메인 유형 | 기준 | 설계 강도 |
|---|---|---|
| 핵심 Core | 경쟁력의 원천, 자주 바뀜, 규칙이 복잡함 | 가장 정교한 도메인 모델 |
| 지원 Supporting | 업무 보조, CRUD 성격이 강함 | 단순한 모델로 충분 |
| 범용 Generic | 인증, 결제 PG 연동, 알림처럼 흔한 문제 | 외부 솔루션/라이브러리 우선 |

2. **바운디드 컨텍스트를 찾는다**
   같은 단어가 다른 의미로 쓰이면 컨텍스트를 나눕니다.

예를 들어 이커머스라면 `상품`이라는 말도 컨텍스트마다 다릅니다.

| 컨텍스트 | “상품”의 의미 |
|---|---|
| 카탈로그 | 전시할 이름, 이미지, 설명, 카테고리 |
| 재고 | 보관 위치, 가용 수량, 예약 수량 |
| 주문 | 주문 라인에 담긴 구매 대상 |
| 정산 | 매출/수수료 계산 대상 |

이 네 개를 하나의 `Product` 모델로 합치면 금방 거대한 모델이 됩니다. 반대로 각 컨텍스트 안에서는 자기 언어로 모델링해야 합니다.

3. **애그리거트는 불변식 기준으로 나눈다**
   애그리거트는 “함께 저장하고 함께 규칙을 지켜야 하는 최소 단위”입니다. 테이블 관계 기준으로 크게 묶지 않는 게 중요합니다.

예시:

| 바운디드 컨텍스트 | 애그리거트 루트 | 보호할 불변식 |
|---|---|---|
| 주문 | `Order` | 취소된 주문은 결제 확정 불가, 주문 총액은 주문 라인 합계와 일치 |
| 결제 | `Payment` | 승인된 결제는 중복 승인 불가, 환불액은 승인액 초과 불가 |
| 재고 | `InventoryItem` 또는 `StockReservation` | 예약 수량은 가용 수량 초과 불가 |
| 배송 | `Shipment` | 출고 전 배송 완료 불가 |
| 카탈로그 | `CatalogProduct` | 판매 가능 상품은 필수 전시 정보가 있어야 함 |

핵심 규칙은 이겁니다.

- 애그리거트는 작게 유지합니다.
- 다른 애그리거트는 객체 참조가 아니라 ID로 참조합니다.
- 한 트랜잭션에서 여러 애그리거트를 억지로 수정하지 않습니다.
- 컨텍스트/애그리거트 간 후속 작업은 도메인 이벤트로 연결합니다.

4. **유비쿼터스 언어 사전을 먼저 만든다**

| 용어 | 의미 | 쓰는 컨텍스트 | 금지 동의어 |
|---|---|---|---|
| 주문 접수 | 고객의 구매 의사가 확정되어 주문이 생성된 상태 | 주문 | 생성, 등록, insert |
| 결제 승인 | PG 또는 결제 수단에서 금액 승인이 완료된 상태 | 결제 | 결제 성공, charge success |
| 재고 예약 | 주문을 위해 판매 가능 수량을 임시 점유한 상태 | 재고 | 차감, 홀딩 |
| 출고 | 물류에서 상품이 창고를 떠난 상태 | 배송 | 배송 시작, 상태 변경 |

이 표가 코드 이름으로 이어져야 합니다. `update_status()`보다 `confirm_payment()`, `reserve_stock()`, `ship()` 같은 메서드가 낫습니다.

간단한 전술 모델은 이런 방향입니다.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID


class DomainError(Exception):
    pass


class OrderCannotBeConfirmed(DomainError):
    pass


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("amount must be non-negative")
        if not self.currency:
            raise ValueError("currency is required")


@dataclass(frozen=True)
class OrderId:
    value: UUID


@dataclass(frozen=True)
class OrderConfirmedEvent:
    order_id: OrderId
    total_amount: Money


@dataclass
class Order:
    """
    Aggregate Root.

    Invariants:
    - confirmed order cannot be confirmed again
    - total_amount must equal the sum of order lines
    - cancelled order cannot be confirmed
    """
    id: OrderId
    total_amount: Money
    status: str = "draft"
    _events: list[object] = field(default_factory=list)

    def confirm(self) -> None:
        if self.status != "draft":
            raise OrderCannotBeConfirmed("draft order only can be confirmed")

        self.status = "confirmed"
        self._events.append(
            OrderConfirmedEvent(
                order_id=self.id,
                total_amount=self.total_amount,
            )
        )

    def collect_events(self) -> list[object]:
        events = self._events[:]
        self._events.clear()
        return events


class OrderRepository(ABC):
    @abstractmethod
    def find_by_id(self, order_id: OrderId) -> Order | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, order: Order) -> None:
        raise NotImplementedError


class OrderApplicationService:
    def __init__(self, orders: OrderRepository) -> None:
        self.orders = orders

    def confirm_order(self, order_id: OrderId) -> None:
        order = self.orders.find_by_id(order_id)
        if order is None:
            raise DomainError("order not found")

        order.confirm()
        self.orders.save(order)
```

실무적으로는 이렇게 시작하면 됩니다.

1. 주요 유스케이스를 이벤트 형태로 적습니다: `OrderPlaced`, `PaymentApproved`, `StockReserved`, `ShipmentDispatched`.
2. 이벤트를 책임지는 업무 영역별로 묶습니다.
3. 같은 용어가 다른 뜻을 가지는 곳을 바운디드 컨텍스트 경계로 삼습니다.
4. 각 컨텍스트 안에서 “반드시 즉시 지켜야 하는 규칙”을 기준으로 애그리거트를 정합니다.
5. Django 앱이나 DB 테이블은 그 다음에 맞춥니다. 모델 경계를 Django `models.py` 구조에서 먼저 찾으면 도메인이 금방 테이블 중심으로 흐릅니다.

참고로 현재 작업 디렉터리에서는 AGENTS가 가리킨 `config.toml`을 찾지 못했습니다. 그래서 로컬 dddjango DDD 스킬 기준으로 답했습니다.

---
> **관련 스킬 참조:**
> - 바운디드 컨텍스트/애그리거트 상세 설계 → **architecture-ddd** 스킬
> - Django 프로젝트 구조와 Repository/UoW 배치 → **architecture-implementation-patterns** 스킬
> - DB 테이블/인덱스/트랜잭션 설계 → **architecture-db** 스킬