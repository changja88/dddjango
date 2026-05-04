**주요 내용**

권장 경계는 `Order` 하나에 `Payment`, `Shipment`까지 모두 넣는 방식이 아니라, **작은 애그리거트 3개**로 나누는 것입니다.

| 객체 | 권장 역할 | Aggregate Root 여부 | 이유 |
|---|---:|---:|---|
| `Order` | 주문의 의사결정 중심 | 예 | 주문 항목, 주문 금액, 주문 상태 같은 주문 불변식을 보호 |
| `OrderItem` | 주문 내부 구성요소 | 아니오 | 단독 생명주기보다 `Order` 안에서 의미가 있음 |
| `Payment` | 결제 생명주기 | 예 | 승인, 실패, 취소, 환불은 주문과 다른 속도와 규칙으로 변함 |
| `Shipment` | 배송 생명주기 | 예 | 출고, 운송장, 배송중, 배송완료는 물류 컨텍스트의 독립 상태 |

따라서 기본 모델은 이렇게 잡는 게 좋습니다.

```text
Order Aggregate
- Root: Order
- 내부: OrderItem 또는 OrderLine
- 참조: payment_id 없음 또는 Payment는 order_id로 Order를 참조
- 보호 불변식:
  - 주문에는 최소 1개 이상의 item이 있어야 한다
  - total_amount는 item 합계와 일치해야 한다
  - 결제 완료/출고 이후에는 item을 변경할 수 없다

Payment Aggregate
- Root: Payment
- 참조: order_id
- 보호 불변식:
  - 승인된 금액보다 많이 capture/refund 할 수 없다
  - 성공/실패/취소/환불 상태 전이가 유효해야 한다
  - 같은 payment request는 idempotent 해야 한다

Shipment Aggregate
- Root: Shipment
- 참조: order_id
- 보호 불변식:
  - 결제 완료 전 출고할 수 없다
  - 출고 후 배송지를 임의 변경할 수 없다
  - 배송완료 후 취소/운송장 변경이 불가능하다
```

핵심은 **트랜잭션 일관성이 반드시 필요한 규칙만 같은 애그리거트 안에 둔다**는 점입니다. `OrderItem`은 주문 총액 계산, 주문 가능 여부, 주문 취소 가능 여부와 함께 즉시 일관성이 필요하므로 `Order` 내부에 둡니다. 반면 `Payment`와 `Shipment`는 외부 PG, 물류사, 재시도, 실패 복구, 웹훅, 상태 동기화가 얽히기 때문에 `Order` 안에 직접 포함하면 애그리거트가 너무 커집니다.

`Order`가 `Payment`나 `Shipment` 객체를 직접 들고 있으면 다음 문제가 생깁니다.

```text
Order
 ├─ items
 ├─ payment
 └─ shipment
```

이 구조는 “주문 조회/수정”마다 결제와 배송까지 같은 일관성 경계로 묶습니다. 결제 실패 재시도, 부분 환불, 배송 상태 갱신 같은 작업이 모두 `Order` 락과 트랜잭션에 묶일 수 있어 변경 충돌과 복잡도가 커집니다. DDD 관점에서는 Vernon의 “작은 애그리거트” 규칙을 위반하기 쉽습니다.

더 나은 구조는 이렇습니다.

```text
Order
 └─ OrderItem[]

Payment
 └─ order_id

Shipment
 └─ order_id
```

애그리거트 간 연결은 객체 참조가 아니라 **ID 참조**로 둡니다. 그리고 상태 전파는 도메인 이벤트로 처리합니다.

```text
OrderPlaced
  -> PaymentRequested

PaymentPaid
  -> Order.mark_paid()
  -> ShipmentRequested

ShipmentShipped
  -> Order.mark_shipped()

ShipmentDelivered
  -> Order.mark_delivered()
```

예를 들어 `PaymentPaid` 이벤트가 발생하면 응용 서비스나 이벤트 핸들러가 `OrderRepository`에서 `Order`를 다시 로드하고 `order.mark_paid()`를 호출합니다. 이때 `Payment`가 `Order` 객체를 직접 수정하지 않습니다.

간단한 도메인 스케치는 다음 정도가 적절합니다.

```python
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("금액은 0 이상이어야 합니다")
        if not self.currency:
            raise ValueError("통화는 필수입니다")


@dataclass(frozen=True)
class OrderItem:
    product_id: UUID
    name: str
    unit_price: Money
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("수량은 1 이상이어야 합니다")


@dataclass(frozen=True)
class OrderPaid:
    order_id: UUID
    payment_id: UUID
    paid_amount: Money
    occurred_at: datetime


@dataclass
class Order:
    """Aggregate Root: 주문 항목, 주문 금액, 주문 상태의 즉시 일관성을 보호한다.

    Invariants:
    - 주문은 최소 1개 이상의 OrderItem을 가진다.
    - total_amount는 OrderItem 합계와 일치해야 한다.
    - 결제 완료 이후에는 주문 항목을 변경할 수 없다.
    """

    id: UUID
    customer_id: UUID
    items: list[OrderItem]
    status: str = "placed"
    _events: list[object] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.items:
            raise ValueError("주문에는 최소 1개 이상의 상품이 필요합니다")

    def mark_paid(self, payment_id: UUID, paid_amount: Money) -> None:
        if self.status != "placed":
            raise ValueError("접수된 주문만 결제 완료 처리할 수 있습니다")
        if paid_amount != self.total_amount:
            raise ValueError("결제 금액이 주문 금액과 일치하지 않습니다")

        self.status = "paid"
        self._events.append(
            OrderPaid(
                order_id=self.id,
                payment_id=payment_id,
                paid_amount=paid_amount,
                occurred_at=datetime.now(),
            )
        )

    @property
    def total_amount(self) -> Money:
        total = sum(
            item.unit_price.amount * item.quantity
            for item in self.items
        )
        return Money(amount=Decimal(total), currency="KRW")
```

Repository와 응용 서비스는 애그리거트를 직접 연결하지 않고 유스케이스를 조율하는 역할만 맡깁니다.

```python
class OrderRepository(Protocol):
    def find_by_id(self, order_id: UUID) -> Order: ...
    def save(self, order: Order) -> None: ...


class PaymentRepository(Protocol):
    def save(self, payment: "Payment") -> None: ...


class OrderApplicationService:
    def __init__(self, orders: OrderRepository):
        self.orders = orders

    def mark_order_paid(
        self,
        order_id: UUID,
        payment_id: UUID,
        paid_amount: Money,
    ) -> None:
        order = self.orders.find_by_id(order_id)
        order.mark_paid(payment_id, paid_amount)
        self.orders.save(order)
```

`OrderItem`은 대부분 값 객체로 충분합니다. 다만 다음 요구사항이 강하면 `OrderItem`을 `Order` 내부 엔티티로 승격할 수 있습니다.

| 경우 | 모델링 |
|---|---|
| 상품명, 단가, 수량만 있고 주문 안에서만 의미 있음 | `OrderItem` 값 객체 |
| 주문 라인별 부분 취소, 부분 환불, 개별 배송 추적이 필요함 | `OrderLine` 내부 엔티티 |
| 상품 옵션 단위로 독립 배송/교환/반품 프로세스가 있음 | `FulfillmentLine`, `ReturnRequest` 같은 별도 애그리거트 검토 |

유비쿼터스 언어는 이렇게 고정하는 편이 좋습니다.

| 권장 용어 | 의미 | 금지/주의 동의어 |
|---|---|---|
| `Order` | 고객이 확정한 주문 | `Cart`, `Checkout`, `Purchase` 혼용 금지 |
| `OrderItem` 또는 `OrderLine` | 주문 당시 확정된 상품 라인 | `ProductItem`, `Goods`, `LineData` |
| `Payment` | 결제 시도와 결제 결과의 생명주기 | `Billing`, `PayInfo`, `Transaction` 혼용 주의 |
| `Shipment` | 출고 이후 배송 생명주기 | `Delivery`, `ShippingInfo` 혼용 주의 |
| `ShippingInfo` | 수령자/주소 값 객체 | `Shipment`와 혼동 금지 |

정리하면, **주문 자체의 일관성은 `Order`가 책임지고, 결제와 배송은 각각 `Payment`, `Shipment`를 Aggregate Root로 분리**하는 것이 가장 안정적입니다. `Order`는 “주문이 어떤 상태인가”를 표현하되, 결제 처리와 배송 처리의 내부 규칙까지 소유하지 않습니다.

---
> **관련 스킬 참조:**
> - Django 모델/ORM 구현 → **implementation-django** 스킬
> - Django Ninja API 설계 → **implementation-django-ninja** 스킬
> - 트랜잭션/DB 경계 설계 → **architecture-db** 스킬