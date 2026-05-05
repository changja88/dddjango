지정된 fixture path `/Users/hyun/Desktop/dddjango/none`는 존재하지 않아 읽을 fixture 파일은 없었습니다. 대신 인접 저장소의 DDD/Django 지침을 확인했고, 아래는 코드 변경 없이 설계 제안으로 정리합니다.

**[주요 내용]**

커머스에서 `주문`, `결제`, `배송`, `정산`은 단순 기능 메뉴가 아니라 **변경 이유, 언어, 일관성 경계, 외부 의존성**이 다르기 때문에 별도 bounded context로 나누는 것이 적절합니다.

| Bounded Context | 핵심 책임 | 주요 변경 이유 | 대표 모델 |
|---|---|---|---|
| 주문 Order | 고객의 구매 의사, 주문 항목, 주문 상태 전이 관리 | 주문 정책, 취소 가능 조건, 주문 금액 확정 방식 변경 | `Order`, `OrderLine`, `OrderStatus` |
| 결제 Payment | 결제 승인, 실패, 취소, 환불 요청 관리 | PG 연동, 승인/취소/환불 규칙, 멱등성 정책 변경 | `Payment`, `PaymentApproval`, `Refund` |
| 배송 Shipping | 출고 요청, 운송장, 배송 상태 추적 | 택배사 연동, 출고 정책, 배송 상태 매핑 변경 | `Shipment`, `TrackingNumber`, `DeliveryStatus` |
| 정산 Settlement | 판매자/플랫폼 정산 금액 계산, 지급 상태 관리 | 수수료 정책, 지급 주기, 세금/보류금 정책 변경 | `Settlement`, `Payout`, `Commission` |

나누는 핵심 기준은 다음입니다.

1. **같은 단어가 다른 의미를 가지는가**
   예를 들어 `완료`는 주문에서는 “주문 처리 종료”, 결제에서는 “승인 완료”, 배송에서는 “배송 완료”, 정산에서는 “지급 완료”입니다. 같은 상태명을 공유하면 모델이 쉽게 오염됩니다.

2. **트랜잭션으로 반드시 같이 바뀌어야 하는가**
   주문 생성과 주문 항목 확정은 한 Aggregate 안에서 강한 일관성이 필요합니다. 반면 결제 승인, 배송 요청, 정산 생성은 이벤트 기반 최종 일관성으로 연결하는 편이 낫습니다.

3. **외부 시스템 변화가 어디로 들어오는가**
   PG사 용어는 결제 BC의 ACL에서 번역하고, 택배사 용어는 배송 BC의 ACL에서 번역해야 합니다. 주문 도메인이 `TossPaymentStatus`나 `CJTrackingCode`를 알면 경계가 무너진 것입니다.

4. **팀 또는 운영 책임이 분리될 수 있는가**
   결제 장애 대응, 배송 클레임, 정산 검증은 운영 지표와 장애 대응 방식이 다릅니다. 운영 책임이 다르면 bounded context도 분리 후보입니다.

권장 Context Map은 다음과 같습니다.

```text
Order BC
  ├─ publishes OrderPlaced / OrderCancelled
  ▼
Payment BC
  ├─ publishes PaymentApproved / PaymentFailed / RefundCompleted
  ▼
Order BC
  ├─ publishes OrderPaid
  ▼
Shipping BC
  ├─ publishes ShipmentRequested / ShipmentDispatched / Delivered
  ▼
Settlement BC
```

외부 시스템과의 관계는 이렇게 둡니다.

| 관계 | 패턴 | 설명 |
|---|---|---|
| Payment BC ↔ PG사 | ACL | PG사의 승인/취소/환불 용어를 내부 결제 모델로 번역 |
| Shipping BC ↔ 택배사 | ACL | 택배사 배송 상태 코드를 내부 `DeliveryStatus`로 번역 |
| Order BC → Payment BC | Published Language | 주문은 결제 요청 이벤트/커맨드 계약만 알고 결제 내부 모델은 모름 |
| Shipping BC → Settlement BC | Domain Event | 배송 완료 또는 구매 확정 이후 정산 후보 생성 |

Django 프로젝트 구조 예시는 다음처럼 bounded context를 Django app 단위로 분리하는 방식을 추천합니다.

```text
commerce/
  config/
    settings.py
    urls.py

  orders/
    domain/
      models/
        order.py
        order_line.py
        order_status.py
      events.py
      exceptions.py
      repositories.py
    application/
      commands.py
      services.py
      event_handlers.py
    infrastructure/
      django_models.py
      repositories.py
      outbox.py
    interfaces/
      api.py
      schemas.py
    apps.py

  payments/
    domain/
      models/
        payment.py
        refund.py
      events.py
      exceptions.py
      repositories.py
    application/
      services.py
      event_handlers.py
    infrastructure/
      django_models.py
      repositories.py
      pg_client.py
      pg_translator.py
    interfaces/
      api.py
      schemas.py
    apps.py

  shipping/
    domain/
      models/
        shipment.py
        delivery_status.py
      events.py
      exceptions.py
      repositories.py
    application/
      services.py
      event_handlers.py
    infrastructure/
      django_models.py
      courier_client.py
      courier_translator.py
      repositories.py
    interfaces/
      api.py
      schemas.py
    apps.py

  settlements/
    domain/
      models/
        settlement.py
        payout.py
        commission.py
      events.py
      exceptions.py
      repositories.py
    application/
      services.py
      event_handlers.py
    infrastructure/
      django_models.py
      repositories.py
    interfaces/
      api.py
      schemas.py
    apps.py

  shared_kernel/
    money.py
    ids.py
    clock.py

  messaging/
    event_bus.py
    outbox_dispatcher.py
```

중요한 점은 `shared_kernel`을 작게 유지하는 것입니다. `Money`, `OrderId`, `PaymentId`, `Clock` 같은 기술적/값 객체 수준만 공유하고, `OrderStatus`, `PaymentStatus`, `DeliveryStatus` 같은 도메인 상태는 공유하지 않는 편이 좋습니다.

예를 들어 주문 BC는 결제 모델을 직접 참조하지 않고 이벤트만 받아 상태를 바꿉니다.

```python
# orders/application/event_handlers.py

def handle_payment_approved(event: PaymentApproved) -> None:
    order = order_repository.get(event.order_id)
    order.mark_paid(payment_id=event.payment_id)
    order_repository.save(order)
```

반대로 결제 BC도 주문 내부 구조를 모릅니다.

```python
# payments/application/services.py

def approve_payment(command: ApprovePaymentCommand) -> None:
    payment = payment_repository.get(command.payment_id)
    payment.approve(
        approved_amount=command.approved_amount,
        approved_at=command.approved_at,
    )
    payment_repository.save(payment)
```

초기에는 물리적으로 하나의 Django 프로젝트와 하나의 DB를 써도 됩니다. 다만 코드 경계는 처음부터 BC별 app으로 나누고, 다른 BC의 Django model을 직접 import하지 않는 규칙을 두는 것이 좋습니다. BC 간 연결은 `domain event`, `application service`, `published schema`를 통해서만 허용합니다.

---
> **관련 스킬 참조:**
> - Django app / ORM 구현 구조 → **implementation-django** 스킬
> - 이벤트 기반 통합, Outbox, Saga → **architecture-implementation-patterns** 스킬
> - 테이블 경계와 FK 설계 → **architecture-db** 스킬