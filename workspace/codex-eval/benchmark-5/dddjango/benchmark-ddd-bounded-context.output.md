**[주요 내용]**

지정된 fixture path(`/Users/hyun/Desktop/dddjango/none`)는 존재하지 않아 읽을 fixture 파일이 없었습니다. 아래는 코드 변경이 아니라 설계 제안입니다.

커머스에서 `주문`, `결제`, `배송`, `정산`은 테이블 기준이 아니라 **업무 언어와 변경 이유**로 나누는 게 맞습니다. 같은 `상태`, `금액`, `취소`라는 단어를 써도 의미와 책임자가 다르면 다른 bounded context로 봅니다.

| Context | 책임 | 자주 바뀌는 이유 | 대표 언어 | 금지할 혼용 |
|---|---|---|---|---|
| 주문 | 고객의 구매 의사, 주문 라인, 주문 확정/취소 | 프로모션, 주문 정책, 클레임 정책 | Order, OrderLine, Confirmed, Cancelled | 결제 승인번호, 운송장번호를 주문 규칙으로 직접 사용 |
| 결제 | 승인, 매입, 환불, PG 연동 | PG 정책, 결제수단, 환불 규칙 | Payment, Authorization, Capture, Refund | 주문 상태를 결제 상태처럼 사용 |
| 배송 | 출고, 송장, 배송 상태 추적 | 물류사, 창고, 출고 정책 | Shipment, Fulfillment, Tracking | 결제 완료 여부를 배송 내부 상태로 저장 |
| 정산 | 판매자 지급액, 수수료, 지급 보류/확정 | 수수료율, 세금, 지급 주기, 회계 정책 | Settlement, Payable, Fee, Payout | 결제 금액을 곧바로 정산 금액으로 간주 |

핵심 기준은 다음입니다.

1. **주문 Context**
   주문은 “고객이 무엇을 어떤 조건으로 사기로 했는가”를 보호합니다. Aggregate Root는 `Order`이고, 불변식은 “확정된 주문의 라인 금액 합계와 주문 총액이 일치해야 한다”, “취소 불가 상태에서는 취소할 수 없다”입니다. 결제 성공은 주문 내부 규칙의 입력일 뿐, PG 응답 구조가 주문 모델로 들어오면 안 됩니다.

2. **결제 Context**
   결제는 “돈을 실제로 승인/매입/환불했는가”를 다룹니다. Aggregate Root는 `Payment`입니다. 외부 PG 용어는 ACL에서 정화하고, 내부에는 `authorize()`, `capture()`, `refund()` 같은 결제 언어만 둡니다.

3. **배송 Context**
   배송은 “상품을 준비하고 운송사에 넘기고 추적하는 과정”입니다. Aggregate Root는 `Shipment` 또는 출고 복잡도가 크면 `Fulfillment`입니다. 배송은 주문 전체 객체를 참조하지 않고 `OrderId`, 배송 대상, 품목 snapshot만 받습니다.

4. **정산 Context**
   정산은 결제와 분리해야 합니다. 결제는 고객 돈의 흐름이고, 정산은 판매자/플랫폼 간 지급 계산입니다. Aggregate Root는 `Settlement` 또는 판매자별 지급 단위인 `Payout`입니다.

Context 간 통합은 직접 모델 import가 아니라 **Published Language + Integration Event + 필요 시 ACL**로 둡니다.

```text
OrderConfirmedEvent
  -> Payment Context: 결제 생성/승인 요청

PaymentCapturedEvent
  -> Order Context: 주문 결제완료 반영
  -> Shipping Context: 출고 준비 가능
  -> Settlement Context: 정산 후보 생성

ShipmentDeliveredEvent
  -> Order Context: 배송완료 반영
  -> Settlement Context: 구매확정/지급 가능 조건 평가

RefundCompletedEvent
  -> Order Context: 취소/환불 상태 반영
  -> Settlement Context: 지급 차감 또는 정산 취소
```

Django 구조는 bounded context와 app을 **무조건 1:1로 강제하지 않습니다**. Django app은 migration, admin, 배포 단위 성격도 있으므로 팀 규모와 변경 빈도에 맞춥니다. 다만 도메인 경계는 패키지 구조로 명확히 드러냅니다.

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
        commands.py
        services.py
      infra/django_orm/
        models.py
        repositories.py
      api/
        router.py
        selectors.py

    payments/
      domain/
      application/
      infra/
        pg_acl/
        django_orm/
      api/

    shipping/
      domain/
      application/
      infra/
      api/

    settlements/
      domain/
      application/
      infra/
      api/

    integration/
      outbox/
      event_handlers.py
      published_language.py
```

작게 시작한다면 `apps.commerce` 하나의 Django app 안에 네 context 패키지를 두고, migration이 커지거나 팀/배포 경계가 갈라질 때 `orders`, `payments`, `shipping`, `settlements`를 별도 Django app으로 분리해도 됩니다. 중요한 것은 Django app 개수보다 **도메인 import 방향과 통합 방식**입니다.

검증 기준은 간단합니다.

```bash
python manage.py test
python manage.py check
python manage.py makemigrations --check --dry-run
```

추가로 구조 리뷰 시에는 `orders.domain`이 `payments.infra.pg_acl`이나 Django ORM 모델을 직접 import하지 않는지 확인해야 합니다.

---
> **관련 스킬 참조:**
> - 바운디드 컨텍스트/컨텍스트 맵 상세화 → **architecture-ddd** 스킬
> - Outbox, ACL, Repository, UoW 설계 → **architecture-implementation-patterns** 스킬
> - Django 앱/서비스/selector 구조 구체화 → **implementation-django** 스킬