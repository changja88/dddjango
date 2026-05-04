**주요 내용**

기본 경계는 이렇게 잡는 것을 권합니다.

| 객체 | Aggregate Root 여부 | 이유 |
|---|---:|---|
| `Order` | 예 | 주문 생성, 품목, 총액, 주문 상태 전이의 일관성 경계 |
| `OrderItem` | 아니오 | `Order` 없이는 독립 생명주기가 약함. 보통 `Order` 내부 엔티티 또는 값 객체 |
| `Payment` | 기본은 별도 root | 승인, 실패, 재시도, 취소, 환불은 결제 컨텍스트의 생명주기 |
| `Shipment` | 기본은 별도 root | 출고, 송장, 배송중, 반품, 배송사 연동은 배송/풀필먼트 컨텍스트의 생명주기 |

즉, `Order` aggregate 안에는 `OrderItem`만 넣는 것을 기본값으로 둡니다. `Payment`, `Shipment`는 무조건 `Order` 내부에 넣지 않습니다. 둘은 보통 `order_id`로 `Order`를 참조하는 별도 aggregate root입니다.

```python
class Order:
    """
    Aggregate Root.

    Invariants:
    - 주문은 최소 1개 이상의 OrderItem을 가진다.
    - total_amount는 OrderItem 금액 합계와 일치한다.
    - 결제 완료 이후에는 주문 품목을 임의 변경할 수 없다.
    - 취소/확정/배송 요청 같은 상태 전이는 Order를 통해서만 수행한다.
    """
```

`OrderItem`은 “주문 당시의 상품명, 단가, 수량”을 보존하는 주문 라인입니다. 상품 카탈로그의 `Product`를 직접 참조하지 말고 `product_id`, `product_name`, `unit_price`, `quantity` 같은 주문 시점 스냅샷을 갖는 편이 안전합니다. 라인별 취소, 라인별 배송, 라인별 환불처럼 독립 상태가 필요하면 `OrderItem`은 내부 엔티티가 됩니다. 그런 생명주기가 없으면 값 객체로 충분합니다.

`Payment`를 `Order` 안에 넣어도 되는 경우는 제한적입니다. 예를 들어 “무통장 입금 여부만 기록한다”, “결제 실패/재시도/환불/부분취소가 없다”, “결제 시스템과 별도 팀/외부 PG 연동이 없다”처럼 결제가 주문의 단순 속성일 때입니다. 하지만 일반 커머스에서는 결제 승인, capture, cancel, refund, webhook, PG idempotency가 있어서 `Payment`를 별도 aggregate root로 두는 편이 맞습니다.

`Shipment`도 마찬가지입니다. “배송지 문자열 하나와 배송 요청 여부” 정도라면 `Order` 내부의 `ShippingInfo` 값 객체로 둘 수 있습니다. 하지만 송장번호, 배송사, 출고 작업, 분할 배송, 배송 추적, 반품/교환이 들어오면 `Shipment`는 별도 aggregate root입니다.

권장 흐름은 이벤트로 연결합니다.

| 발생 이벤트 | 후속 처리 |
|---|---|
| `OrderPlacedEvent` | 결제 요청 생성 |
| `PaymentPaidEvent` | `Order.mark_paid()` 호출 |
| `OrderReadyForShipmentEvent` | 배송 생성 |
| `ShipmentDispatchedEvent` | `Order.mark_shipped()` 또는 조회 모델 갱신 |
| `ShipmentDeliveredEvent` | `Order.mark_delivered()` 또는 배송 컨텍스트에서 완료 |

중요한 점은 `Order`, `Payment`, `Shipment`를 같은 DB 트랜잭션에서 항상 함께 바꾸려 하지 않는 것입니다. aggregate boundary는 consistency boundary입니다. `Order` 저장과 `Payment` 저장을 하나의 거대한 트랜잭션으로 묶으면 경계가 커지고, 외부 PG/webhook/배송사 연동이 들어올 때 모델이 쉽게 무너집니다. 경계 밖 일관성은 도메인 이벤트와 outbox, 또는 `transaction.on_commit()` 이후 핸들러로 맞춥니다.

Django에서는 `orders/models.py` 안에 `Order`, `OrderItem`, `Payment`, `Shipment` 모델이 같이 있다고 해서 같은 aggregate라는 뜻이 아닙니다. Django model 배치는 영속성/앱 구조의 문제이고, domain object의 책임과 aggregate boundary는 비즈니스 불변식 기준으로 판단해야 합니다. 같은 Django app에 있어도 `OrderRepository`, `PaymentRepository`, `ShipmentRepository`는 aggregate 단위로 나뉘는 것이 자연스럽습니다.

최종 추천은 다음입니다.

```text
Ordering Context
- Aggregate Root: Order
- 내부 구성: OrderItem, ShippingInfo, Money
- 참조: payment_id 없음 또는 payment_status 스냅샷 정도만 보유

Payment Context
- Aggregate Root: Payment
- 참조: order_id

Fulfillment/Shipping Context
- Aggregate Root: Shipment
- 참조: order_id
```

---
> **관련 스킬 참조:**
> - Django 모델/Repository 배치 → **implementation-django** 스킬
> - Outbox, UoW, 이벤트 연동 → **architecture-implementation-patterns** 스킬