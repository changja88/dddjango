커머스에서 bounded context를 나눌 때 핵심 기준은 “데이터 테이블 기준”이 아니라 **업무 의사결정 책임과 상태 변경의 소유권**입니다. 주문, 결제, 배송, 정산은 서로 강하게 연결되지만, 각자 바꾸는 상태와 사용하는 언어가 다릅니다.

참고로 지시된 `config.toml`은 현재 `/private/tmp/dddjango-codex-eval`에서 찾을 수 없었습니다.

**분리 기준**

| Context | 핵심 책임 | 소유 상태 | 외부에 노출할 이벤트/명령 |
|---|---|---|---|
| 주문 | 고객이 무엇을 얼마에 구매하기로 했는가 | 주문 생성, 주문 상품, 주문 금액, 주문 상태 | `OrderPlaced`, `OrderCancelled` |
| 결제 | 돈을 실제로 승인/취소/환불했는가 | 결제 승인, 결제 실패, 취소, 환불, PG 거래 ID | `PaymentApproved`, `PaymentFailed`, `PaymentRefunded` |
| 배송 | 물건을 어디까지 보냈는가 | 배송지, 출고, 운송장, 배송 상태 | `ShipmentCreated`, `ShipmentDelivered` |
| 정산 | 판매자/파트너에게 얼마를 지급해야 하는가 | 정산 금액, 수수료, 지급 예정/완료 상태 | `SettlementCalculated`, `SettlementPaid` |

**중요한 경계 원칙**

1. 주문은 결제 테이블을 직접 수정하지 않습니다.  
   주문은 “결제 요청”을 만들거나 결제 context에 명령을 보냅니다.

2. 결제는 주문 상품 상세를 소유하지 않습니다.  
   결제는 `order_id`, 결제 금액, 결제 수단, PG 응답을 관리합니다.

3. 배송은 결제 승인 여부를 직접 계산하지 않습니다.  
   `PaymentApproved` 이벤트 이후 출고 가능 상태로 전환하는 식이 좋습니다.

4. 정산은 주문/결제/배송 원장을 직접 바꾸지 않습니다.  
   이미 발생한 이벤트를 기준으로 정산 데이터를 생성합니다.

5. context 간 참조는 FK보다 ID 참조를 우선 고려합니다.  
   같은 DB를 쓰더라도 `Payment.order_id`는 Django FK가 아니라 문자열/UUID 필드로 두는 편이 경계를 지키기 쉽습니다.

**Django 프로젝트 구조 예시**

```text
commerce/
  config/
    settings.py
    urls.py
    celery.py

  apps/
    orders/
      models.py
      services.py
      selectors.py
      events.py
      handlers.py
      api.py
      admin.py
      tests/

    payments/
      models.py
      services.py
      selectors.py
      events.py
      handlers.py
      gateways/
        base.py
        toss.py
        nicepay.py
      api.py
      tests/

    shipments/
      models.py
      services.py
      selectors.py
      events.py
      handlers.py
      carriers/
        base.py
        cj.py
        hanjin.py
      api.py
      tests/

    settlements/
      models.py
      services.py
      selectors.py
      events.py
      handlers.py
      calculators.py
      api.py
      tests/

    catalog/
      models.py
      selectors.py

    customers/
      models.py
      selectors.py

    shared/
      event_bus.py
      outbox.py
      money.py
      ids.py
```

**모델 소유권 예시**

```python
# apps/orders/models.py
class Order(models.Model):
    id = models.UUIDField(primary_key=True)
    customer_id = models.UUIDField()
    status = models.CharField(max_length=30)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)


class OrderLine(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_id = models.UUIDField()
    product_name = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()
```

```python
# apps/payments/models.py
class Payment(models.Model):
    id = models.UUIDField(primary_key=True)
    order_id = models.UUIDField(db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=30)
    pg_transaction_id = models.CharField(max_length=100, blank=True)
```

```python
# apps/shipments/models.py
class Shipment(models.Model):
    id = models.UUIDField(primary_key=True)
    order_id = models.UUIDField(db_index=True)
    status = models.CharField(max_length=30)
    recipient_name = models.CharField(max_length=100)
    address = models.TextField()
    tracking_number = models.CharField(max_length=100, blank=True)
```

```python
# apps/settlements/models.py
class Settlement(models.Model):
    id = models.UUIDField(primary_key=True)
    seller_id = models.UUIDField(db_index=True)
    order_id = models.UUIDField(db_index=True)
    payment_id = models.UUIDField(db_index=True)
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    fee_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payout_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=30)
```

**흐름 예시**

```text
1. orders.services.place_order()
   -> Order 생성
   -> OrderPlaced 이벤트 발행

2. payments.handlers.on_order_placed()
   -> Payment 생성 또는 결제 대기 상태 생성

3. payments.services.approve_payment()
   -> PG 승인
   -> PaymentApproved 이벤트 발행

4. shipments.handlers.on_payment_approved()
   -> Shipment 생성
   -> 출고 준비

5. settlements.handlers.on_shipment_delivered()
   또는 on_payment_approved()
   -> 정산 대상 생성
```

실무적으로는 처음부터 마이크로서비스로 나누기보다, Django 안에서는 **앱 단위 모듈러 모놀리스**로 시작하는 게 좋습니다. DB는 하나를 쓰더라도 각 context가 자기 모델만 직접 쓰고, 다른 context와는 `service`, `event`, `id reference`로만 통신하게 만들면 나중에 서비스 분리도 훨씬 쉬워집니다.