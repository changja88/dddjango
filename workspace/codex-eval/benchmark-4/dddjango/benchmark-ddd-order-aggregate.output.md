**주요 내용**

권장 기본안은 `Order`를 주문 컨텍스트의 Aggregate Root로 두고, `OrderItem`은 `Order` 내부 구성요소로 둡니다. `Payment`, `Shipment`는 무조건 `Order` 내부에 넣지 말고, 각각 독립 라이프사이클과 외부 시스템 통합이 있으면 별도 Aggregate Root로 분리합니다.

| 도메인 용어 | 정의 | 코드 표현 | 금지 동의어 |
|---|---|---|---|
| 주문 | 고객이 상품 구매 의사를 확정한 거래 | `Order` | `Purchase`, `Cart` 혼용 |
| 주문 항목 | 주문 안의 상품/수량/단가 명세 | `OrderItem` 또는 `OrderLine` | DB row 관점의 `LineModel` |
| 결제 승인 | 결제 컨텍스트가 금액 지불을 승인한 사건 | `PaymentApproved` | PG 어휘 `charge`, `payment_token` |
| 배송 출고 | 배송 컨텍스트가 물류 출고를 확정한 사건 | `ShipmentDispatched` | 택배사 raw status |

Aggregate 경계는 객체 관계가 아니라 **강한 일관성으로 함께 지켜야 하는 불변식**으로 잡습니다.

`Order`가 보호할 불변식:

- 주문은 최소 1개 이상의 `OrderItem`을 가진다.
- 주문 총액은 주문 항목 합계와 일치한다.
- 결제 완료 후에는 상품/수량/가격을 임의 변경할 수 없다.
- 취소 가능 여부는 주문 상태로 판단한다.
- 결제/배송 객체를 직접 소유하지 않고 `payment_id`, `shipment_id` 또는 상태 스냅샷만 가진다.

```python
class Order(AggregateRoot):
    """Aggregate Root: Ordering context

    Invariants:
    - items must not be empty
    - total_amount == sum(item.amount)
    - items cannot change after payment is confirmed
    - payment/shipment are referenced by id, not owned objects
    """

    def confirm_payment(self, payment_id: PaymentId, paid_amount: Money) -> None:
        if paid_amount != self.total_amount:
            raise PaymentAmountMismatch()
        if self.status != OrderStatus.PAYMENT_PENDING:
            raise InvalidOrderState()
        self.payment_id = payment_id
        self.status = OrderStatus.PAID
        self._record_event(OrderPaymentConfirmed(self.id, payment_id))
```

`OrderItem`은 보통 Aggregate Root가 아닙니다. 주문 밖에서 독립적으로 조회, 변경, 삭제되는 생명주기가 없고, “주문 총액/수량/변경 가능 여부” 같은 불변식이 `Order`를 통해 보호되기 때문입니다. `OrderItem`에 고유 ID가 있어도 그것만으로 Root가 되지는 않습니다.

`Payment`는 다음 조건이면 별도 Aggregate Root입니다.

- 승인, 실패, 취소, 환불, 부분 환불 같은 자체 상태 전이가 있다.
- PG/Toss/Stripe 같은 외부 시스템과 idempotency, 재시도, 장애 복구가 필요하다.
- 결제 내역 감사, 정산, 환불 정책이 주문과 다른 팀/모델 언어를 가진다.

즉 `Payment`의 불변식은 `Order`가 아니라 `Payment`가 지킵니다.

```python
class Payment(AggregateRoot):
    """Aggregate Root: Payment context

    Invariants:
    - approved amount cannot exceed requested amount
    - approved payment cannot be approved again
    - refund cannot exceed approved amount
    """
```

`Shipment`도 다음 조건이면 별도 Aggregate Root입니다.

- 배송 요청, 피킹, 패킹, 출고, 배송중, 배송완료, 반송 같은 자체 라이프사이클이 있다.
- 창고/WMS/택배사 연동이 있다.
- 송장, 배송지 변경 제한, 재배송, 부분 배송 같은 규칙이 주문과 분리된다.

```python
class Shipment(AggregateRoot):
    """Aggregate Root: Fulfillment/Shipment context

    Invariants:
    - only paid orders can be prepared for shipment
    - dispatched shipment cannot change address
    - delivered shipment cannot be cancelled
    """
```

따라서 전체 관계는 이렇게 보는 게 안전합니다.

```text
Ordering BC
  Order AR
    - OrderItem child entity/value object
    - payment_id: PaymentId | None
    - shipment_id: ShipmentId | None

Payment BC
  Payment AR

Fulfillment/Shipment BC
  Shipment AR
```

컨텍스트 간 일관성은 한 트랜잭션에 다 넣지 말고 이벤트로 맞춥니다.

```text
OrderPlaced -> RequestPayment
PaymentApproved -> Order.confirm_payment(...)
OrderPaymentConfirmed -> RequestShipment
ShipmentDispatched -> Order.mark_shipped(...)
```

Django에서는 `orders/models.py` 안에 `Order`, `OrderItem`, `Payment`, `Shipment` 모델이 같이 있다고 해서 같은 Aggregate라는 뜻이 아닙니다. ORM 모델 배치는 저장 구조이고, Aggregate Root는 도메인 규칙과 트랜잭션 경계의 문제입니다. 같은 Django app/DB에 있어도 `OrderRepository`, `PaymentRepository`, `ShipmentRepository`는 Aggregate 단위로 분리하는 편이 낫습니다.

검증 기준:

- 한 유스케이스에서 반드시 동시에 변경해야 하는 객체만 같은 Aggregate에 둔다.
- `Order` 저장 시 `Payment`, `Shipment` 전체 객체를 같이 저장해야 한다면 경계가 너무 큰지 점검한다.
- 다른 Aggregate는 객체 참조가 아니라 ID로 참조한다.
- 결제/배송 실패 보상은 동기 트랜잭션보다 도메인 이벤트, Outbox, 멱등 컨슈머로 처리한다.

---
> **관련 스킬 참조:**
> - Aggregate/Bounded Context 세부 설계 → **architecture-ddd** 스킬
> - Repository, Outbox, 이벤트 연동 구조 → **architecture-implementation-patterns** 스킬
> - Django model/app 배치와 ORM 구현 → **implementation-django** 스킬