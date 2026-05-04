커머스에서 `주문`, `결제`, `배송`, `정산` bounded context를 나누는 기준은 “테이블 주제”가 아니라 **비즈니스 의사결정 책임과 상태 전이의 주인**입니다.

**권장 분리 기준**

`주문 Order`
- 고객이 무엇을, 얼마에, 어떤 조건으로 구매하려 했는가를 책임집니다.
- 장바구니 확정, 주문 생성, 주문 취소 요청, 주문 상태 관리가 핵심입니다.
- 결제 승인 여부나 송장 번호 자체를 직접 처리하지 않고, 그 결과를 반영합니다.
- 예: `Order`, `OrderLine`, `OrderStatus`, `ShippingAddressSnapshot`, `PriceSnapshot`

`결제 Payment`
- 돈을 받는 행위와 PG/VAN/간편결제 연동을 책임집니다.
- 승인, 실패, 취소, 환불, 부분 환불, 결제 수단별 처리를 관리합니다.
- 주문 금액을 참조할 수는 있지만 주문 도메인의 상세 규칙을 소유하지 않습니다.
- 예: `Payment`, `PaymentAttempt`, `Refund`, `PaymentTransaction`

`배송 Fulfillment / Delivery`
- 상품을 어떻게 출고하고 고객에게 전달할지를 책임집니다.
- 출고 요청, 재고 할당, 송장 등록, 배송 추적, 배송 완료를 관리합니다.
- 주문이 “배송 대상”을 제공하면 배송 context가 fulfillment 단위를 생성합니다.
- 예: `Shipment`, `ShipmentItem`, `Carrier`, `TrackingEvent`

`정산 Settlement`
- 돈을 누구에게 얼마만큼 지급하거나 회계 처리할지를 책임집니다.
- 판매자 정산, 수수료, PG 수수료, 쿠폰 부담 주체, 환불 차감, 지급 보류를 다룹니다.
- 결제 성공 이벤트와 배송 완료/구매 확정 이벤트를 기반으로 정산 데이터를 만듭니다.
- 예: `Settlement`, `SettlementLine`, `Payout`, `Commission`

**핵심 원칙**

각 context는 자기 상태의 최종 판단자가 되어야 합니다.

예를 들어 주문이 결제 테이블을 직접 수정하면 안 됩니다. 주문은 `PaymentCompleted`, `PaymentFailed`, `RefundCompleted` 같은 결과를 받아 자신의 상태를 바꿉니다.

반대로 결제 context도 주문 상태를 직접 판단하지 않습니다. 결제는 “10,000원 승인 성공”을 알릴 뿐, 주문이 `PAID`가 될지 `PARTIALLY_PAID`가 될지는 주문 context가 결정합니다.

**Django 프로젝트 구조 예시**

```text
commerce/
  config/
    settings.py
    urls.py

  apps/
    orders/
      models.py
      services.py
      selectors.py
      events.py
      tasks.py
      api/
        views.py
        serializers.py
        urls.py
      tests/

    payments/
      models.py
      services.py
      gateways/
        base.py
        toss.py
        nicepay.py
      events.py
      webhooks.py
      api/
        views.py
        serializers.py
        urls.py
      tests/

    deliveries/
      models.py
      services.py
      carriers/
        base.py
        cj.py
        hanjin.py
      events.py
      tasks.py
      api/
        views.py
        serializers.py
        urls.py
      tests/

    settlements/
      models.py
      services.py
      calculators.py
      events.py
      tasks.py
      api/
        views.py
        serializers.py
        urls.py
      tests/

    catalog/
      models.py

    customers/
      models.py

    shared/
      events.py
      money.py
      idempotency.py
```

**의존 방향 예시**

```text
orders
  -> catalog 조회
  -> customers 조회
  -> payments에는 명령 요청만 보냄

payments
  -> orders의 주문 금액 snapshot 참조 또는 payment request 참조
  -> PG 연동
  -> PaymentCompleted 이벤트 발행

deliveries
  -> OrderPaid 또는 FulfillmentRequested 이벤트 구독
  -> ShipmentCreated, Delivered 이벤트 발행

settlements
  -> PaymentCompleted, RefundCompleted, Delivered/PurchaseConfirmed 이벤트 구독
  -> 정산 예정/확정/지급 처리
```

**이벤트 예시**

```python
# apps/orders/events.py
@dataclass(frozen=True)
class OrderPlaced:
    order_id: str
    customer_id: str
    total_amount: int


@dataclass(frozen=True)
class OrderPaid:
    order_id: str
    payment_id: str
    paid_amount: int
```

```python
# apps/payments/events.py
@dataclass(frozen=True)
class PaymentCompleted:
    payment_id: str
    order_id: str
    amount: int
    method: str
```

**실무적으로 추천하는 시작점**

초기 Django 프로젝트라면 물리적으로 DB까지 완전히 분리하기보다는, 먼저 `app` 단위로 bounded context를 나누고 다음 규칙을 강제하는 게 현실적입니다.

1. 다른 context의 모델을 직접 수정하지 않는다.
2. cross-context 변경은 `service` 또는 event handler를 통해서만 한다.
3. 외부 API 연동은 해당 context 안에 둔다.
4. 금액, 주소, 상품명은 주문 시점 snapshot을 저장한다.
5. 정산은 주문 테이블에서 즉석 계산하지 말고 별도 정산 ledger를 만든다.

이렇게 나누면 주문 변경, PG 교체, 배송사 추가, 정산 정책 변경이 서로 덜 얽힙니다.