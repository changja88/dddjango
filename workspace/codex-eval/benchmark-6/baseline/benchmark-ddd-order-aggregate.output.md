Fixture path `/Users/hyun/Desktop/dddjango/none`는 현재 환경에 존재하지 않았고, 작업 디렉터리도 비어 있어 읽을 fixture 파일이 없었습니다.

주문 도메인에서는 보통 `Order`를 aggregate root로 둡니다.

```text
Order Aggregate
- Order  <-- aggregate root
  - OrderItem
```

`OrderItem`은 주문 없이는 독립적인 생명주기가 약하므로 `Order` 내부 엔티티로 두는 것이 자연스럽습니다. 수량 변경, 상품 추가/삭제, 주문 총액 계산, 주문 취소 가능 여부 같은 불변식은 `Order`가 책임지는 편이 좋습니다.

`Payment`와 `Shipment`는 별도 aggregate로 두는 쪽이 더 안전합니다.

```text
Payment Aggregate
- Payment

Shipment Aggregate
- Shipment
```

이유는 `Payment`와 `Shipment`가 각각 다른 변경 이유와 생명주기를 갖기 때문입니다. 결제는 승인, 실패, 취소, 환불처럼 결제 시스템/PG와의 상태 전이가 중심이고, 배송은 출고, 배송중, 배송완료, 반송처럼 물류 흐름이 중심입니다. 이 둘을 `Order` aggregate 안에 넣으면 주문 변경 시 결제/배송 상태까지 같은 트랜잭션 경계로 묶이기 쉬워지고, aggregate가 과하게 커집니다.

따라서 권장 boundary는 다음과 같습니다.

```text
Order
- 주문 생성
- 주문 항목 관리
- 주문 금액 계산
- 주문 취소 정책
- paymentId, shipmentId 같은 참조 ID만 보관 가능

Payment
- 결제 승인/실패/취소/환불
- orderId로 주문 참조

Shipment
- 배송 준비/출고/배송완료/반송
- orderId로 주문 참조
```

핵심 규칙은 `Order`가 주문의 root이고, `OrderItem`은 그 내부에 둔다. `Payment`, `Shipment`는 `Order`를 ID로 참조하는 별도 aggregate로 분리한다는 것입니다. 단, “결제가 완료되어야 주문 확정 가능” 같은 흐름은 aggregate 내부 직접 참조보다 도메인 서비스, 애플리케이션 서비스, 도메인 이벤트로 조율하는 편이 좋습니다.