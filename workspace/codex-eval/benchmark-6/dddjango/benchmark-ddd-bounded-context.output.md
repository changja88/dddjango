**[주요 내용]**

Fixture 확인 결과: `/Users/hyun/Desktop/dddjango/none` 경로가 존재하지 않아 읽을 fixture 파일은 없었습니다. 따라서 파일 변경 diff는 없고, 설계 제안으로 답합니다.

커머스의 bounded context는 Django app 수나 테이블 기준이 아니라 **업무 언어와 변경 이유**로 나누는 것이 맞습니다.

| Context | 나누는 기준 | 주요 언어 | Aggregate Root / 핵심 불변식 | 대표 이벤트 |
|---|---|---|---|---|
| 주문 | 구매 의사, 주문 생성/취소/반품 요청 규칙이 바뀔 때 | Order, OrderLine, OrderTotal, Cancellation | `Order`: 확정된 주문 금액/상품 스냅샷은 임의 변경 불가 | `OrderPlaced`, `OrderCancelled` |
| 결제 | PG 연동, 승인/매입/환불/멱등성 정책이 바뀔 때 | Payment, Authorization, Capture, Refund | `Payment`: 승인 금액을 초과해 매입/환불 불가 | `PaymentAuthorized`, `PaymentCaptured`, `PaymentRefunded` |
| 배송 | 출고, 송장, 배송 상태, 물류사 연동 규칙이 바뀔 때 | Shipment, Fulfillment, TrackingNumber | `Shipment`: 출고 전에는 배송완료 불가, 송장번호는 물류사 범위에서 유일 | `ShipmentRequested`, `ShipmentDispatched`, `ShipmentDelivered` |
| 정산 | 판매자 지급, 수수료, 보류금, 세금계산 기준이 바뀔 때 | Settlement, Payout, Commission, Holdback | `Settlement`: 결제/환불/수수료 합산 결과가 지급액과 일치 | `SettlementCalculated`, `PayoutRequested` |

금지할 동의어도 정해야 합니다. 예를 들어 주문 context에서 `paid_order`로 결제 상태를 직접 말하지 않고 `payment_confirmed` 같은 외부 상태 반영 이벤트로만 다룹니다. 결제 context에서는 `order_total` 대신 `payable_amount`, 정산 context에서는 `sales_amount`와 `settlement_amount`를 구분합니다.

Django 구조는 bounded context와 app을 무조건 1:1로 강제하지 않습니다. 독립 배포/팀/마이그레이션 경계가 강하면 app을 나누고, 초기에는 하나의 Django app 안에서도 context별 패키지 경계를 둘 수 있습니다.

```text
config/
apps/
  commerce/
    orders/
      domain/
        model/order/
        events.py
        repositories.py
      application/
        place_order.py
        cancel_order.py
      infrastructure/
        django_models.py
        repositories.py
      api/
        routers.py
        selectors.py

    payments/
      domain/
        model/payment/
        events.py
        repositories.py
        ports.py          # PG 역할 인터페이스
      application/
        authorize_payment.py
        refund_payment.py
      infrastructure/
        django_models.py
        pg_toss_acl.py
        repositories.py

    shipping/
      domain/
        model/shipment/
        events.py
      application/
        request_shipment.py
      infrastructure/
        django_models.py
        carrier_acl.py

    settlements/
      domain/
        model/settlement/
        events.py
      application/
        calculate_settlement.py
      infrastructure/
        django_models.py
```

context 간 통합은 직접 FK 탐색이나 서비스 직접 호출보다 **통합 이벤트 + published language**를 기본으로 둡니다.

| From | To | 관계 유형 | 통합 방식 |
|---|---|---|---|
| 주문 | 결제 | Customer-Supplier | `OrderPlaced` → 결제 command 생성 |
| 결제 | 배송 | Published Language | `PaymentCaptured` → 배송 요청 |
| 결제 | 정산 | Published Language | `PaymentCaptured`, `PaymentRefunded`를 정산 입력으로 사용 |
| 배송 | 주문 | Published Language | `ShipmentDelivered`로 주문 조회 상태 갱신 |
| 결제/배송 외부사 | 내부 context | ACL | Toss/Stripe/택배사 SDK 어휘를 내부 모델로 번역 |

단일 DB 안에서는 `transaction.on_commit()`으로 이벤트 발행을 시작할 수 있습니다. 결제, 배송, 정산처럼 재시도와 장애 격리가 중요한 경계는 Outbox를 두고 at-least-once 발행과 consumer 멱등성을 전제로 둡니다.

검증 단계는 다음이 핵심입니다.

```bash
python manage.py test apps.commerce
python manage.py makemigrations --check --dry-run
python manage.py check
```

추가로 import 규칙 테스트를 두어 `orders.domain`이 `payments.infrastructure`를 import하지 못하게 막고, context map에 정의된 이벤트만 경계를 넘는지 확인합니다.

---
> **관련 스킬 참조:**
> - bounded context / context map 세분화 → **architecture-ddd** 스킬
> - Outbox / ACL / Repository 구조화 → **architecture-implementation-patterns** 스킬
> - Django app/package 구조와 테스트 배치 → **implementation-django** 스킬