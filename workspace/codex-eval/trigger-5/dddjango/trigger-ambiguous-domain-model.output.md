맥락이 불명확합니다. 우선 “비즈니스 규칙이 있는 Django 백엔드”라고 가정하면, 도메인 모델은 DB 테이블 기준이 아니라 **업무 언어와 일관성 경계** 기준으로 나누는 게 좋습니다.

**[주요 내용]**

먼저 바운디드 컨텍스트부터 나누세요. 같은 단어가 문맥마다 다른 의미를 가지면 컨텍스트를 분리합니다. 예를 들어 커머스라면 `주문`, `결제`, `배송`, `재고`, `정산`은 같은 테이블로 연결되어 보여도 서로 다른 규칙과 언어를 가질 가능성이 큽니다.

그다음 각 컨텍스트 안에서 애그리거트를 작게 잡습니다. 기준은 “한 트랜잭션 안에서 반드시 같이 지켜야 하는 불변식”입니다.

예시:

| 컨텍스트 | Aggregate Root | 보호할 불변식 |
|---|---|---|
| 주문 | `Order` | 주문 확정 후 라인 변경 금지, 총액 일관성 |
| 결제 | `Payment` | 승인/취소/환불 상태 전이 규칙 |
| 배송 | `Shipment` | 출고 후 주소 변경 금지 |
| 재고 | `StockReservation` | 예약 수량이 가용 수량 초과 불가 |

다른 애그리거트는 객체 참조가 아니라 ID로 참조하세요. 예를 들어 `Order`가 `Payment` 객체를 직접 들고 있기보다 `payment_id` 또는 도메인 이벤트 `OrderConfirmedEvent`로 연결하는 식입니다. 컨텍스트 간 변경은 즉시 동기 호출보다 도메인 이벤트와 최종 일관성을 우선 검토합니다.

값 객체도 적극적으로 분리하세요. `amount: int`, `currency: str`, `address: str`처럼 흩어진 원시 타입은 `Money`, `Address`, `OrderId`, `Quantity` 같은 불변 값 객체로 만들면 규칙이 모델 내부에 들어갑니다.

**Django라면** Django app을 무조건 도메인 하나당 하나로 자르기보다, 바운디드 컨텍스트 단위로 시작하는 편이 낫습니다.

```text
orders/
  domain/
    model/order/
    events.py
    repositories.py
  application/
  infrastructure/
    django_models.py
```

Django ORM 모델은 영속성 모델로 두고, 핵심 규칙은 `domain` 안의 엔티티/값 객체/도메인 서비스에 둡니다. 단순 CRUD라면 이 구조를 과하게 적용하지 말고, 규칙이 복잡한 핵심 컨텍스트에만 먼저 적용하세요.

---
> **관련 스킬 참조:**
> - 도메인 경계/애그리거트 설계 → **architecture-ddd** 스킬
> - Django 계층 분리/Repository/UoW → **architecture-implementation-patterns** 스킬