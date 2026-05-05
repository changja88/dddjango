**[주요 내용]**

Fixture path `/Users/hyun/Desktop/dddjango/none`는 존재하지 않아 읽을 fixture 파일이 없었습니다. 따라서 주어진 도메인 객체 기준으로 aggregate boundary를 잡습니다.

결론부터 말하면 기본 설계는 다음이 적절합니다.

| 객체 | 권장 역할 | 이유 |
|---|---|---|
| `Order` | Aggregate Root | 주문 생성, 품목 변경, 주문 확정, 취소 같은 주문 불변식을 보호 |
| `OrderItem` | Order 내부 Entity 또는 Value Object | 주문 총액, 최소 1개 품목, 수량/가격 불변식이 Order와 같은 트랜잭션에서 지켜져야 함 |
| `Payment` | 별도 Aggregate Root 후보 | 승인/매입/취소/환불/PG 재시도/idempotency 등 주문과 다른 생명주기와 실패 모델을 가짐 |
| `Shipment` | 별도 Aggregate Root 후보 | 송장 발급, 출고, 배송중, 배송완료, 반송 등 물류 생명주기가 주문과 다름 |

`Order`의 consistency boundary는 “주문 자체가 항상 말이 되는가”입니다.

- 주문에는 최소 1개 이상의 `OrderItem`이 있어야 한다.
- 주문 총액은 `OrderItem`들의 합과 일치해야 한다.
- 확정된 주문의 품목/가격은 임의로 바뀌면 안 된다.
- 취소 가능한 상태에서만 취소된다.
- 배송 시작 후 배송지 변경은 제한된다.

이 규칙들은 한 트랜잭션 안에서 즉시 일관성이 필요하므로 `Order` aggregate 내부에 둡니다.

반대로 `Payment`를 `Order` 내부에 넣으면 경계가 과해집니다. 결제는 보통 다음 불변식을 가집니다.

- 같은 결제 요청은 idempotency key로 중복 승인되면 안 된다.
- 승인 금액과 매입 금액의 관계를 지켜야 한다.
- 환불 가능 금액은 결제 금액을 넘으면 안 된다.
- PG 장애/지연/웹훅 재전송을 견뎌야 한다.

이 규칙은 `OrderItem` 합계와는 다른 이유로 바뀝니다. 그래서 `Payment(order_id=...)`처럼 `Order`를 ID로 참조하고, `PaymentPaidEvent` 같은 이벤트로 `Order` 상태를 갱신하는 편이 낫습니다.

`Shipment`도 마찬가지입니다.

- 송장번호는 배송 단위에서 유일해야 한다.
- 출고 후에는 주소 변경이 제한된다.
- 배송완료 후에는 다시 출고 상태로 돌아갈 수 없다.
- 택배사/물류 시스템의 상태와 동기화해야 한다.

따라서 `Shipment(order_id=...)` 별도 aggregate로 두고, `OrderPaidEvent`를 받아 배송 준비를 만들거나, `ShipmentDeliveredEvent`로 주문의 표시 상태를 갱신합니다.

핵심 구조는 이 정도면 충분합니다.

```python
@dataclass
class Order:
    """Aggregate Root.

    Consistency boundary:
    - at least one item
    - total equals sum of order lines
    - item changes are blocked after confirmation
    - cancellation follows order state rules
    """
    id: OrderId
    items: list[OrderItem]
    status: OrderStatus

    def confirm(self) -> None:
        if not self.items:
            raise EmptyOrderError()
        self.status = OrderStatus.CONFIRMED
        self._record_event(OrderConfirmedEvent(order_id=self.id))


@dataclass(frozen=True)
class OrderItem:
    product_id: ProductId
    unit_price: Money
    quantity: int
```

```python
@dataclass
class Payment:
    """Separate Aggregate Root. References Order by ID only."""
    id: PaymentId
    order_id: OrderId
    amount: Money
    status: PaymentStatus


@dataclass
class Shipment:
    """Separate Aggregate Root. References Order by ID only."""
    id: ShipmentId
    order_id: OrderId
    status: ShipmentStatus
```

Django에서는 `orders.models.Order`, `payments.models.Payment`, `shipments.models.Shipment`처럼 모델 파일이나 앱을 나눌 수 있지만, 이것이 곧 도메인 aggregate boundary를 의미하지는 않습니다. Django model 배치는 저장/조회/마이그레이션 편의의 문제이고, domain object의 책임은 “어떤 불변식을 어떤 트랜잭션 경계에서 보호하는가”로 결정해야 합니다.

권장 bounded context는 다음입니다.

| Context | Aggregate Root | 관계 |
|---|---|---|
| Ordering | `Order` | 주문 언어의 중심 |
| Payment | `Payment` | Ordering과 Published Language 이벤트로 통합 |
| Fulfillment/Shipping | `Shipment` | Ordering/Payment 이벤트를 소비 |
| External PG/Carrier | 외부 모델 | Payment/Shipment 쪽 ACL 필요 |

검증은 다음 테스트로 잡으면 됩니다.

- `Order`는 빈 품목으로 확정할 수 없다.
- 확정 후 `OrderItem` 변경이 막힌다.
- `PaymentPaidEvent` 수신 전에는 배송 생성이 되지 않는다.
- `Payment` 실패가 `Order` 내부 객체 변경 실패로 전파되지 않고 이벤트/상태로 반영된다.
- `Shipment` 배송완료가 결제 aggregate를 직접 수정하지 않는다.

---
> **관련 스킬 참조:**
> - Aggregate/Bounded Context 구체화 → **architecture-ddd** 스킬