주문 도메인에서는 보통 **`Order`를 Aggregate Root**로 둡니다.

`OrderItem`, `Payment`, `Shipment`는 각각 성격에 따라 `Order` 내부 엔티티로 둘 수도 있고, 별도 Aggregate로 분리할 수도 있습니다. 핵심 기준은 **하나의 트랜잭션 안에서 반드시 함께 일관성을 지켜야 하는가**입니다.

**추천 Aggregate Boundary**

```text
Order Aggregate
- Order  (Aggregate Root)
- OrderItem
```

그리고 보통은 아래처럼 분리합니다.

```text
Payment Aggregate
- Payment  (Aggregate Root)

Shipment Aggregate
- Shipment (Aggregate Root)
```

즉, 기본적으로는:

- `Order`는 주문의 생명주기와 주문 항목을 관리
- `OrderItem`은 `Order` 없이 독립적으로 존재하지 않으므로 `Order` 내부 엔티티
- `Payment`는 결제 승인, 실패, 환불 등 별도 상태와 외부 결제 시스템 연동을 가지므로 별도 Aggregate
- `Shipment`는 출고, 배송 시작, 배송 완료, 반송 등 별도 상태와 물류 시스템 연동을 가지므로 별도 Aggregate

**왜 `Order`가 Aggregate Root인가**

주문의 핵심 불변식은 보통 `Order`가 책임집니다.

예를 들어:

- 주문이 확정되기 전까지만 상품 수량을 변경할 수 있다
- 주문 총액은 `OrderItem`들의 합계와 일치해야 한다
- 취소된 주문은 결제 요청을 할 수 없다
- 주문 상태에 따라 결제나 배송 요청 가능 여부가 달라진다

이런 규칙은 `Order`가 중심이 되어 판단해야 하므로 `Order`가 Aggregate Root가 됩니다.

**`Payment`, `Shipment`를 Order 내부에 넣지 않는 이유**

결제와 배송은 주문과 강하게 연결되어 있지만, 상태 변화 주기가 다릅니다.

예를 들어 결제는:

```text
READY -> AUTHORIZED -> CAPTURED -> FAILED -> REFUNDED
```

배송은:

```text
READY -> PICKED -> SHIPPED -> DELIVERED -> RETURNED
```

처럼 각각 독립적인 워크플로우가 있습니다. 외부 PG사, 물류사와도 연동됩니다. 이걸 모두 `Order` Aggregate 안에 넣으면 `Order`가 너무 커지고, 결제/배송 이벤트마다 주문 전체를 잠그거나 저장해야 해서 복잡도가 올라갑니다.

그래서 보통은 `Order`가 직접 `Payment` 객체를 소유하기보다 `paymentId`, `shipmentId` 또는 `orderId`로 느슨하게 연결합니다.

**정리**

가장 무난한 설계는 이렇습니다.

```text
Order Aggregate
- Order
- OrderItem

Payment Aggregate
- Payment

Shipment Aggregate
- Shipment
```

`Order`는 주문 자체의 상태와 주문 항목의 일관성을 책임지고, `Payment`와 `Shipment`는 각각 독립 Aggregate로 두되 `orderId`를 통해 주문과 연결하는 방식이 실무적으로 가장 안정적입니다.