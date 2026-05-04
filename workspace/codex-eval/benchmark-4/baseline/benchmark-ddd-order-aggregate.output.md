주문 도메인에서는 보통 **`Order`를 aggregate root**로 둡니다.

`OrderItem`은 독립 생명주기가 거의 없고, 주문 없이는 의미가 약합니다. 따라서 `Order` aggregate 내부의 엔티티로 두는 게 자연스럽습니다.

```text
Order Aggregate
- Order              <- Aggregate Root
- OrderItem          <- 내부 Entity
```

`Payment`, `Shipment`는 경우에 따라 다르지만, 일반적으로는 **별도 aggregate root**로 분리하는 쪽이 더 좋습니다.

```text
Order Aggregate
- Order
- OrderItem

Payment Aggregate
- Payment

Shipment Aggregate
- Shipment
```

이유는 `Payment`와 `Shipment`가 주문과 강하게 연결되어 있긴 해도, 각각 별도의 상태 흐름과 외부 시스템 연동을 갖기 때문입니다.

예를 들어:

- `Payment`: 승인 요청, 승인 완료, 실패, 취소, 환불
- `Shipment`: 배송 준비, 출고, 배송 중, 배송 완료, 반송

이 상태 변화들은 주문의 내부 불변식이라기보다는 결제/배송 도메인의 독립적인 프로세스입니다. 그래서 `Order` 안에 모두 넣으면 aggregate가 너무 커지고, 결제나 배송 변경 때마다 주문 aggregate를 잠그거나 로드해야 해서 경합이 커집니다.

핵심 불변식은 이렇게 나누는 게 좋습니다.

```text
Order
- 주문 항목이 없으면 주문할 수 없다
- 주문 총액은 OrderItem 합계와 일치해야 한다
- 주문 취소 가능 여부를 판단한다

Payment
- 결제 금액은 주문 금액과 일치해야 한다
- 승인된 결제만 취소/환불할 수 있다

Shipment
- 결제 완료 전에는 출고할 수 없다
- 배송 완료 후에는 배송지를 변경할 수 없다
```

aggregate 간 참조는 객체 참조보다 ID 참조를 권장합니다.

```text
Payment.orderId
Shipment.orderId
```

정리하면:

```text
Aggregate Root:
- Order
- Payment
- Shipment

Order 내부:
- OrderItem
```

단, 아주 단순한 CRUD성 쇼핑몰이고 결제/배송 상태가 거의 없다면 `Payment`, `Shipment`를 `Order` 내부 값 객체나 하위 엔티티로 둘 수도 있습니다. 하지만 실무적으로 확장 가능성을 고려하면 **Order, Payment, Shipment를 각각 aggregate로 분리하고, OrderItem만 Order 내부에 두는 설계**가 가장 안정적입니다.