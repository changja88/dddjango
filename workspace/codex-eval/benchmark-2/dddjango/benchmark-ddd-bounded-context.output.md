**[주요 내용]**

커머스의 주문, 결제, 배송, 정산은 “업무 언어가 달라지는가”와 “변경 이유가 독립적인가”를 기준으로 나누는 것이 좋습니다. Django app 구조는 이 경계를 드러내는 수단일 뿐이고, bounded context와 반드시 1:1일 필요는 없습니다.

| Context | 핵심 업무 언어 | 변경 이유 | Aggregate Root 예 | 금지 동의어 |
|---|---|---|---|---|
| 주문 | 주문접수, 주문확정, 주문취소, 주문라인 | 주문 상태 정책, 취소 가능 조건, 쿠폰/가격 확정 규칙 변경 | `Order` | 결제완료=주문완료 |
| 결제 | 승인, 매입, 결제확정, 환불, PG 거래 | PG API, 재시도, 부분환불, 결제수단 정책 변경 | `Payment` | PG `charge_id`를 도메인 ID로 직접 사용 |
| 배송 | 출고지시, 송장, 집화, 배송완료, 반송 | 택배사 연동, 출고 SLA, 배송 추적 상태 변경 | `Shipment` | 주문상태를 배송상태처럼 사용 |
| 정산 | 매출확정, 수수료, 지급, 차감, 정산주기 | 회계 기준, 수수료 정책, 셀러 지급 정책 변경 | `Settlement` | 결제금액=정산금액 |

분리 기준은 다음처럼 잡습니다.

1. **주문 Context**
   고객의 구매 의사를 확정하고 주문 라인, 가격 스냅샷, 취소 가능성을 관리합니다. 결제가 실패해도 주문은 “결제대기” 상태로 존재할 수 있으므로 결제와 같은 모델이 아닙니다.

2. **결제 Context**
   외부 PG와의 승인, 매입, 취소, 환불을 다룹니다. PG의 용어는 ACL에서 번역하고, 주문 Context에는 `PaymentConfirmed` 같은 발행된 언어로만 알립니다.

3. **배송 Context**
   주문이 아니라 “출고 가능한 물품 묶음”과 “운송 상태”를 관리합니다. 한 주문이 여러 배송으로 나뉘거나, 여러 주문이 묶음 출고될 수 있으면 반드시 주문과 분리해야 합니다.

4. **정산 Context**
   결제 성공이 곧 정산 확정은 아닙니다. 환불, 수수료, 프로모션 부담 주체, 지급 보류, 세금계산 기준 때문에 결제와 변경 이유가 다릅니다.

Context 간 통합은 동기 FK 직접 참조보다 이벤트와 명시적 계약을 우선합니다.

| 흐름 | 관계 유형 | 통합 방식 |
|---|---|---|
| 주문 → 결제 | Customer-Supplier | 주문이 `RequestPayment` command를 결제 application service에 요청 |
| 결제 → 주문 | Published Language | `PaymentConfirmed`, `PaymentFailed`, `PaymentRefunded` integration event |
| 주문 → 배송 | Published Language | 주문 확정 후 `OrderReadyForFulfillment` 발행 |
| 배송 → 주문 | Published Language | `ShipmentDelivered`, `ShipmentReturned` 발행 |
| 결제 → 정산 | Published Language | `PaymentCaptured`, `RefundCompleted`를 정산 언어로 변환 |
| 외부 PG/택배사 | ACL | Toss/CJ 용어를 내부 `Payment`, `Shipment` 언어로 번역 |

Django 구조 예시는 두 가지가 실용적입니다.

```text
config/
  settings/
apps/
  commerce/                         # 하나의 Django app, 여러 BC 패키지
    ordering/
      domain/model/order/
      application/commands/
      application/queries/
      adapters/driving/api/
      adapters/driven/orm/
    payments/
      domain/model/payment/
      application/commands/
      adapters/driven/toss/
        adapter.py
        translator.py               # PG ACL
    fulfillment/
      domain/model/shipment/
      application/commands/
      adapters/driven/carriers/cj/
        adapter.py
        translator.py               # 배송사 ACL
    settlements/
      domain/model/settlement/
      application/commands/
      adapters/driven/orm/
    integration/
      outbox/
      published_language/
```

이 구조는 한 팀이 모놀리스로 운영하고, migrations/admin을 한 앱에서 관리하고 싶을 때 적합합니다. bounded context는 `ordering`, `payments`, `fulfillment`, `settlements` 패키지로 나누되 Django app은 하나일 수 있습니다.

분리가 더 강하게 필요하면 아래처럼 Django app도 나눕니다.

```text
apps/
  orders/
  payments/
  shipments/
  settlements/
```

이 방식은 팀 소유권, 배포 계획, 데이터 소유권이 이미 갈라졌을 때 적합합니다. 단, 단순히 “DDD니까 app을 4개 만든다”는 이유만으로 나누면 Django admin, migration, 테스트 fixture 관리 비용이 먼저 늘어납니다.

검증 질문은 이 정도면 충분합니다.

- “주문완료”가 주문팀, 결제팀, 배송팀에서 같은 뜻인가?
- 결제 환불 정책 변경이 주문 모델 수정을 요구하는가?
- 배송 상태 추가가 주문 상태 enum 변경으로 번지는가?
- 정산 금액 재계산이 결제 거래 원장을 수정하게 만드는가?
- 이벤트를 재처리해도 멱등하게 동작하는가?
- 외부 PG/택배사 필드명이 도메인 모델 안으로 들어오지 않는가?

---
> **관련 스킬 참조:**
> - Django Ninja API 설계 → **implementation-django-ninja** 스킬
> - DB 트랜잭션/Outbox/인덱스 설계 → **architecture-db** 스킬