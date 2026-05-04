주문 도메인에서는 보통 **`Order`를 aggregate root**로 둡니다.

`Order` aggregate 안에는 대개 `OrderItem`이 포함됩니다.

```text
Order  Aggregate Root
 └── OrderItem
 └── OrderItem
 └── OrderItem
```

이유는 `OrderItem`이 독립적인 생명주기를 갖기보다 주문에 종속되기 때문입니다. 상품 수량 변경, 가격 계산, 총액 계산, 주문 취소 가능 여부 같은 불변식은 `Order`가 책임지고, 외부에서는 `OrderItem`을 직접 수정하지 않고 반드시 `Order`를 통해 변경해야 합니다.

예를 들면:

```python
order.add_item(product_id, quantity, price)
order.change_item_quantity(item_id, quantity)
order.cancel()
```

반면 **`Payment`와 `Shipment`는 별도 aggregate root로 두는 편이 낫습니다.**

```text
Order Aggregate
 └── OrderItem

Payment Aggregate

Shipment Aggregate
```

`Payment`는 결제 승인, 실패, 환불, 부분 취소, PG사 거래 ID 같은 자체 상태와 생명주기가 있습니다. 주문과 강하게 연결되지만, 결제는 외부 결제 시스템과 비동기적으로 진행될 수 있고 상태 전이가 주문과 완전히 같지 않습니다.

`Shipment`도 마찬가지입니다. 출고 준비, 배송 시작, 배송 완료, 반송, 송장 번호 같은 별도 상태를 가지며 물류 시스템과 연동될 수 있습니다. 주문이 생성되었다고 배송 aggregate가 즉시 같은 트랜잭션 안에서 완성되어야 하는 것도 아닙니다.

따라서 추천 boundary는 다음과 같습니다.

```text
Order
- id
- customer_id
- status
- items
- total_amount
- shipping_address
- place()
- add_item()
- cancel()
- mark_paid()
- request_shipment()

OrderItem
- product_id
- quantity
- unit_price
- subtotal

Payment
- id
- order_id
- amount
- status
- approve()
- fail()
- refund()

Shipment
- id
- order_id
- status
- tracking_number
- ship()
- deliver()
- return()
```

핵심 기준은 **트랜잭션 일관성이 필요한 것만 같은 aggregate 안에 둔다**는 점입니다.

- `Order`와 `OrderItem`: 같은 aggregate
- `Payment`: 별도 aggregate, `order_id`로 참조
- `Shipment`: 별도 aggregate, `order_id`로 참조

`Order`는 결제나 배송 객체를 직접 소유하기보다, 결제 완료나 배송 시작 같은 결과를 이벤트나 명령을 통해 반영하는 구조가 좋습니다.

```text
OrderPlaced
 → PaymentRequested

PaymentApproved
 → Order.mark_paid()
 → ShipmentRequested

ShipmentStarted
 → Order.mark_shipping()
```

정리하면, 이 도메인에서는 **`Order`가 주문 aggregate의 root이고, `OrderItem`은 그 내부 엔티티이며, `Payment`와 `Shipment`는 각각 별도 aggregate root**로 잡는 것이 가장 일반적이고 확장에 안전한 설계입니다.