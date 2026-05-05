지정된 fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 존재하지 않아 fixture 파일은 읽을 수 없었습니다. 현재 작업 디렉터리에도 Django 소스 파일은 없어, 특정 코드 변경이 아니라 설계 제안으로 답합니다.

**Bounded Context 분리 기준**

커머스에서 `주문`, `결제`, `배송`, `정산`은 단순히 모델 수가 많아서 나누는 것이 아니라, “변경 이유”, “도메인 언어”, “상태 전이”, “외부 의존성”이 다르기 때문에 나누는 것이 적절합니다.

`주문 Order` context는 고객이 무엇을 어떤 조건으로 구매하려는지 관리합니다.

주요 책임:
- 장바구니 또는 주문서 확정
- 주문 항목, 수량, 가격 스냅샷
- 쿠폰/프로모션 적용 결과
- 주문 상태: `CREATED`, `CONFIRMED`, `CANCELLED` 등
- 결제/배송/정산을 직접 수행하지 않고 필요한 이벤트 발행

주문은 “구매 의사와 계약 내용”의 원천입니다. 결제 성공 여부나 송장번호 같은 세부사항을 주문 모델 안에 과하게 넣기 시작하면 context 경계가 흐려집니다.

`결제 Payment` context는 돈을 실제로 승인, 취소, 환불하는 흐름을 담당합니다.

주요 책임:
- PG 승인 요청
- 결제 승인/실패 기록
- 부분 취소, 전체 취소, 환불
- 결제 수단별 처리
- PG webhook 수신
- 결제 상태: `READY`, `AUTHORIZED`, `CAPTURED`, `FAILED`, `CANCELLED`, `REFUNDED`

결제 context는 PG사 SDK, webhook, 승인번호, 거래번호처럼 외부 세부사항이 많습니다. 이 세부사항이 주문 도메인으로 새지 않게 분리하는 것이 중요합니다.

`배송 Shipment` context는 물리적 상품 이동을 담당합니다.

주요 책임:
- 배송 요청 생성
- 출고 지시
- 택배사 송장 등록
- 배송 추적
- 반송/회수
- 배송 상태: `PENDING`, `READY_TO_SHIP`, `SHIPPED`, `DELIVERED`, `RETURNING`, `RETURNED`

배송은 결제와도 다르고 주문과도 다릅니다. 주문은 “무엇을 샀는가”이고, 배송은 “어떻게 보내고 어디까지 갔는가”입니다. 디지털 상품, 예약 상품, 분할 배송이 생기면 이 분리는 더 중요해집니다.

`정산 Settlement` context는 판매자, 플랫폼, PG, 배송비, 쿠폰 비용 부담 주체 사이의 금액 귀속을 담당합니다.

주요 책임:
- 판매자별 정산 대상 집계
- 수수료 계산
- 쿠폰/포인트 비용 배분
- 환불 차감
- 정산 확정
- 지급 요청
- 정산 상태: `DRAFT`, `CALCULATED`, `CONFIRMED`, `PAID`, `ADJUSTED`

정산은 주문 금액을 그대로 복사하는 영역이 아닙니다. 회계적 기준, 마감일, 환불 반영 시점, 판매자 계약 조건이 핵심이므로 별도 context로 보는 것이 좋습니다.

**Context 간 관계**

각 context는 다른 context의 내부 모델을 직접 수정하지 않고, ID와 이벤트 중심으로 연결하는 편이 좋습니다.

예시 흐름:

```text
OrderConfirmed
  -> PaymentRequested

PaymentCaptured
  -> OrderPaymentCompleted
  -> ShipmentRequested

ShipmentDelivered
  -> SettlementEligible

RefundCompleted
  -> OrderRefundReflected
  -> SettlementAdjusted
```

핵심은 `Order`가 `Payment`의 PG 승인 로직을 모르고, `Payment`가 `Shipment`의 송장 정책을 모르며, `Settlement`가 주문 테이블을 직접 해석해서 모든 정책을 재구현하지 않도록 하는 것입니다.

**Django 프로젝트 구조 예시**

작은 팀이나 모놀리식 Django라면 bounded context를 Django app 단위로 나누는 것이 현실적입니다.

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
      handlers.py
      admin.py
      api/
        serializers.py
        views.py
        urls.py
      tests/

    payments/
      models.py
      services.py
      gateways.py
      events.py
      handlers.py
      webhooks.py
      api/
        serializers.py
        views.py
        urls.py
      tests/

    shipments/
      models.py
      services.py
      carriers.py
      events.py
      handlers.py
      api/
        serializers.py
        views.py
        urls.py
      tests/

    settlements/
      models.py
      services.py
      policies.py
      events.py
      handlers.py
      api/
        serializers.py
        views.py
        urls.py
      tests/

    catalog/
      models.py
      selectors.py
      tests/

    customers/
      models.py
      tests/

  common/
    events.py
    money.py
    idempotency.py
    time.py
```

더 DDD 색을 강하게 가져가고 싶다면 app 내부를 이렇게 나눌 수 있습니다.

```text
apps/orders/
  domain/
    models.py
    policies.py
    events.py
  application/
    commands.py
    services.py
    handlers.py
  infrastructure/
    repositories.py
  presentation/
    serializers.py
    views.py
```

다만 처음부터 모든 app에 이 구조를 강제할 필요는 없습니다. 결제처럼 외부 연동과 상태 전이가 복잡한 곳부터 `domain/application/infrastructure`를 나누고, 단순한 app은 `models.py`, `services.py`, `selectors.py` 정도로 시작하는 편이 낫습니다.

**모델 참조 원칙**

권장:

```python
class Payment(models.Model):
    order_id = models.UUIDField()
    amount = models.DecimalField(...)
    status = models.CharField(...)
```

신중히 사용할 것:

```python
class Payment(models.Model):
    order = models.ForeignKey("orders.Order", ...)
```

같은 DB를 쓰는 Django 모놀리스에서는 `ForeignKey`가 편하지만, context 경계를 강하게 유지하려면 최소한 결제 로직이 `order.items`, `order.customer.grade`, `order.coupon.policy`를 타고 들어가 도메인 판단을 하지 않게 해야 합니다. 결제 context에는 결제에 필요한 주문 스냅샷이나 `order_id`만 전달하는 쪽이 더 안정적입니다.

**실무 기준**

처음부터 마이크로서비스로 나누지는 않는 것이 좋습니다. Django 모놀리스 안에서 app 경계, 서비스 계층, 이벤트/핸들러, 명시적 의존 방향을 먼저 잡는 편이 비용 대비 효과가 큽니다.

추천 의존 방향:

```text
orders -> common
payments -> common
shipments -> common
settlements -> common

context 간 직접 import는 최소화
context 간 협력은 command/event 또는 얇은 facade 사용
```

예를 들어 `payments`가 `orders.models.Order`를 직접 가져와 상태를 바꾸기보다는:

```python
# payments/handlers.py
def handle_payment_captured(event):
    publish(OrderPaymentCompleted(order_id=event.order_id))
```

```python
# orders/handlers.py
def handle_order_payment_completed(event):
    order = Order.objects.get(id=event.order_id)
    order.mark_paid()
    order.save(update_fields=["status", "paid_at"])
```

이렇게 각 context가 자기 상태는 자기가 바꾸게 하는 구조가 좋습니다.