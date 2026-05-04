커머스에서 bounded context는 “데이터 테이블 묶음”보다 **비즈니스 언어, 상태 전이, 책임 주체, 외부 의존성**이 달라지는 지점으로 나누는 게 좋습니다.

**나누는 기준**

| Context | 핵심 책임 | 소유 상태 | 외부와의 관계 |
|---|---|---|---|
| 주문 | 고객이 무엇을 어떤 조건으로 구매하려는가 | 주문 생성, 주문 라인, 주문 상태, 취소/반품 요청 | 결제 승인 요청, 배송 요청, 재고 차감 요청 |
| 결제 | 돈을 받을 수 있는가 | 결제 시도, 승인, 실패, 취소, 환불 | PG/VAN/간편결제 연동 |
| 배송 | 상품을 어떻게 전달할 것인가 | 배송 요청, 송장, 출고, 배송 상태 | WMS, 택배사, 물류 시스템 |
| 정산 | 누구에게 얼마를 지급할 것인가 | 매출 확정, 수수료, 정산금, 지급 상태 | 회계, 판매자, 세금계산서, PG 정산 데이터 |

핵심은 각 context가 **자기 상태의 진실 공급원**이어야 한다는 점입니다. 예를 들어 주문이 `payment_status`를 직접 세밀하게 관리하기보다는, 결제 context의 이벤트를 받아 `PAID`, `PAYMENT_FAILED` 같은 주문 관점의 상태로 반영하는 식이 낫습니다.

**경계 예시**

주문 context는 다음 질문에 답합니다.

- 이 주문은 유효한가?
- 어떤 상품을 몇 개 샀는가?
- 주문을 취소할 수 있는가?
- 결제 완료 후 배송 요청을 해야 하는가?

결제 context는 다음 질문에 답합니다.

- 결제 승인이 되었는가?
- 어떤 PG 거래번호를 갖는가?
- 부분 취소/환불 가능한가?
- 결제 실패 원인은 무엇인가?

배송 context는 다음 질문에 답합니다.

- 출고 가능한가?
- 송장이 발급되었는가?
- 배송 중/완료 상태인가?
- 합배송, 분할배송, 교환배송이 필요한가?

정산 context는 다음 질문에 답합니다.

- 이 거래는 정산 대상인가?
- 판매자에게 얼마를 지급해야 하는가?
- PG 수수료, 플랫폼 수수료, 쿠폰 비용은 누가 부담하는가?
- 정산 확정/보류/지급 완료 상태인가?

**Django 프로젝트 구조 예시**

```text
commerce/
  config/
    settings.py
    urls.py

  apps/
    ordering/
      models.py
      services.py
      selectors.py
      events.py
      handlers.py
      urls.py
      views.py
      tests/

    payments/
      models.py
      services.py
      gateways/
        base.py
        toss.py
        nicepay.py
      events.py
      handlers.py
      urls.py
      views.py
      tests/

    shipping/
      models.py
      services.py
      carriers/
        base.py
        cj.py
        hanjin.py
      events.py
      handlers.py
      tests/

    settlements/
      models.py
      services.py
      policies.py
      events.py
      handlers.py
      tests/

    catalog/
      models.py
      services.py

    inventory/
      models.py
      services.py

  common/
    events/
      bus.py
      outbox.py
    db/
      models.py
    money.py
```

**모델 소유권 예시**

```text
ordering
  Order
  OrderLine
  OrderCancellation
  OrderReturnRequest

payments
  Payment
  PaymentAttempt
  PaymentTransaction
  Refund

shipping
  Shipment
  ShipmentItem
  TrackingEvent
  DeliveryAddressSnapshot

settlements
  Settlement
  SettlementLine
  SellerPayout
  FeePolicySnapshot
```

**Context 간 직접 참조는 최소화**

Django에서는 외래키를 막 걸기 쉽지만, bounded context를 유지하려면 다른 context의 모델을 직접 조작하지 않는 편이 좋습니다.

예를 들어 `payments.Payment`가 `ordering.Order`를 FK로 강하게 물기보다:

```python
class Payment(models.Model):
    order_id = models.UUIDField()
    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=30)
    pg_transaction_id = models.CharField(max_length=100, blank=True)
```

처럼 `order_id`만 참조하고, 주문 상세가 필요하면 ordering의 service/query API를 통해 가져오는 방식이 경계가 더 명확합니다.

**흐름 예시**

```text
OrderPlaced
  -> payments: 결제 준비 생성

PaymentApproved
  -> ordering: 주문을 결제 완료로 변경
  -> shipping: 배송 요청 생성

ShipmentDelivered
  -> ordering: 구매 확정 후보 상태 반영
  -> settlements: 정산 대상 생성

RefundCompleted
  -> ordering: 환불 완료 반영
  -> settlements: 정산 차감 또는 조정 생성
```

**실무 기준으로 추천하는 분리 수준**

초기 Django 서비스라면 처음부터 마이크로서비스로 나누기보다, **모듈러 모놀리스**로 시작하는 게 좋습니다.

- Django app 단위로 bounded context 분리
- DB는 하나를 쓰되 context 간 테이블 직접 조인 최소화
- 다른 context 접근은 `services.py`, `selectors.py`, event handler를 통해 수행
- PG, 택배사, 회계 연동은 각 context 내부 adapter로 격리
- 상태 변경은 service layer에서만 수행

이렇게 시작하면 나중에 트래픽, 조직, 장애 격리 필요성이 커졌을 때 `payments`, `shipping`, `settlements`를 독립 서비스로 떼어내기 쉽습니다.