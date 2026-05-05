**[주요 내용]**

Fixture 확인 결과 `/Users/hyun/Desktop/dddjango/none` 경로가 존재하지 않아 읽을 fixture 파일은 없었습니다. 따라서 코드 diff 없이 도메인 설계 판단만 제시합니다.

결론부터 말하면 기본 후보는 다음이 가장 보수적입니다.

| 객체 | Aggregate Root 판단 | 이유 |
|---|---:|---|
| `Order` | Root | 주문 생성, 품목, 총액, 주문 상태 전이의 일관성 경계 |
| `OrderItem` | `Order` 내부 구성요소 | 주문 총액, 최소 1개 품목, 가격 스냅샷 같은 불변식이 `Order`와 함께 보장됨 |
| `Payment` | 별도 Root 가능성이 높음 | 결제 승인, 실패, 환불, PG 연동, 재시도, 멱등성은 주문과 다른 lifecycle |
| `Shipment` | 별도 Root 가능성이 높음 | 배송 준비, 출고, 송장, carrier 상태, 부분배송은 주문과 다른 lifecycle |

핵심은 “객체 그래프”가 아니라 “강한 일관성이 필요한 범위”입니다. `Order` 안에 `Payment`, `Shipment`를 무조건 넣으면 주문 조회/수정 때 결제와 배송 lifecycle까지 함께 잠기고, 결제 재시도나 배송 추적 같은 변경 이유가 주문 aggregate에 섞입니다.

`Order` aggregate가 직접 지켜야 할 불변식은 이 정도입니다.

- 주문은 최소 1개 이상의 `OrderItem`을 가진다.
- 주문 총액은 주문 품목의 가격 스냅샷과 수량으로 계산된다.
- 결제 완료 전/후, 배송 요청 전/후에 가능한 상태 전이가 다르다.
- 주문 취소 가능 여부는 주문 상태 기준으로 판단한다.
- 외부 aggregate는 객체 참조가 아니라 ID나 이벤트 결과로만 연결한다.

예를 들면 `Payment`가 승인되면 `Order`를 직접 들고 바꾸는 게 아니라, Payment 컨텍스트가 `PaymentApproved`를 발행하고 주문 컨텍스트가 이를 받아 `order.confirm_payment(payment_id, amount)` 같은 도메인 행위로 반영합니다.

```python
class Order(AggregateRoot):
    """Aggregate Root.

    Invariants:
    - item은 최소 1개 이상이어야 한다.
    - total은 OrderItem 가격 스냅샷 합계와 일치해야 한다.
    - 결제 확인 전에는 fulfillment를 요청할 수 없다.
    - 배송 요청 이후에는 일반 취소가 불가능하다.
    """

    def confirm_payment(self, payment_id: PaymentId, paid_amount: Money) -> None:
        if paid_amount != self.total:
            raise PaymentAmountMismatch
        self.payment_id = payment_id
        self.status = OrderStatus.PAID
        self._record_event(OrderPaid(order_id=self.id, payment_id=payment_id))

    def request_fulfillment(self) -> None:
        if self.status != OrderStatus.PAID:
            raise OrderNotPaid
        self.status = OrderStatus.FULFILLMENT_REQUESTED
        self._record_event(FulfillmentRequested(order_id=self.id))
```

`Payment`를 `Order` 내부로 넣어도 되는 경우는 제한적입니다. 예를 들어 “결제”가 실제 PG 결제가 아니라 주문 화면의 단순 결제상태 플래그이고, 환불/부분취소/재시도/정산/멱등성 요구가 없다면 `Order.payment_status` 정도로 충분할 수 있습니다. 하지만 실제 결제 도메인이라면 `Payment`는 별도 aggregate root가 맞습니다.

`Shipment`도 마찬가지입니다. 배송지가 주문 생성 시점의 값 객체일 뿐이면 `ShippingAddress`는 `Order` 내부 값 객체입니다. 그러나 송장 생성, 출고 지시, carrier tracking, 부분 배송, 배송 실패/재배송이 있다면 `Shipment`는 별도 root입니다.

Django에서는 `Order`, `OrderItem`, `Payment`, `Shipment`가 각각 model 파일이나 table로 나뉘는지와 aggregate boundary를 혼동하면 안 됩니다. DB FK 배치는 저장 구조이고, aggregate root는 “어떤 객체를 통해 상태 변경을 허용할지”의 도메인 규칙입니다. Django 모델을 쓰더라도 `OrderRepository.save(order)`는 주문 aggregate 단위 저장을 의미하고, `PaymentRepository.save(payment)`는 결제 aggregate 단위 저장을 의미해야 합니다.

추천 경계는 다음입니다.

```text
Ordering Context
- Aggregate Root: Order
- 내부: OrderItem, ShippingAddress, Money
- 외부 참조: payment_id, shipment_id
- 이벤트: OrderPlaced, OrderPaid, FulfillmentRequested, OrderCancelled

Payment Context
- Aggregate Root: Payment
- 이벤트: PaymentApproved, PaymentFailed, PaymentRefunded

Fulfillment/Shipping Context
- Aggregate Root: Shipment
- 이벤트: ShipmentCreated, ShipmentDispatched, ShipmentDelivered
```

검증 기준은 간단합니다.

1. 한 비즈니스 명령이 반드시 한 트랜잭션에서 같이 바꿔야 하는 객체만 같은 aggregate에 둡니다.
2. `Order` 저장 시 `Payment`, `Shipment` 전체 객체를 같이 저장해야 한다면 경계가 너무 큽니다.
3. `PaymentApproved`, `ShipmentDispatched` 같은 과거형 이벤트로 `Order` 상태가 따라가도 되는 규칙이면 별도 aggregate가 맞습니다.
4. 결제/배송 실패 시 주문과 완전한 즉시 일관성이 필요하지 않다면 domain event + eventual consistency를 사용합니다.

---
> **관련 스킬 참조:**
> - aggregate boundary / bounded context 상세화 → **architecture-ddd** 스킬
> - Django model 배치와 repository/UoW 설계 → **implementation-django**, **architecture-implementation-patterns** 스킬