맥락이 불명확합니다. 우선 “Django 프로젝트에서 DDD를 일부 적용하고, 서비스 레이어는 유스케이스 조율용”이라는 전제로 답하겠습니다.

**주요 내용**

**Django라면** 보통 앱 단위로 둡니다.

```text
apps/
  orders/
    models.py
    services.py      # 쓰기 유스케이스
    selectors.py     # 읽기 전용 쿼리
```

규모가 커지면 이렇게 나눕니다.

```text
apps/
  orders/
    services/
      __init__.py
      checkout.py
      cancel_order.py
    selectors.py
```

서비스 레이어에는 “한 요청/유스케이스를 조율하는 로직”을 둡니다. 예를 들면 주문 생성, 결제 확정, 취소 처리처럼 여러 모델을 갱신하거나, 트랜잭션이 필요하거나, 이메일/외부 API 같은 부수효과가 끼는 경우입니다. 부수효과는 `transaction.on_commit()`으로 트랜잭션 커밋 뒤 실행하는 편이 좋습니다.

반대로 단일 모델의 불변식이나 상태 전이는 가능하면 모델 메서드나 도메인 객체에 둡니다. 예를 들어 `order.cancel()` 같은 규칙은 서비스가 직접 필드를 만지는 것보다 도메인 메서드가 표현력이 좋습니다. 서비스는 `order.cancel()`을 호출하고 저장, 트랜잭션, 알림을 조율하는 쪽입니다.

DDD 관점에서는 이름을 더 엄밀히 구분합니다.

```text
domain/
  models.py
  services.py        # 도메인 서비스: 엔티티/값 객체에 넣기 어려운 순수 도메인 규칙
  repositories.py    # Repository 인터페이스

application/
  services.py        # 애플리케이션 서비스: 유스케이스 조율

infrastructure/
  django/
    repositories.py  # Django ORM 구현체
```

실무적으로 Django와 DDD를 과하게 분리하지 않는다면, 앱 내부의 `services.py`를 애플리케이션 서비스로 보고 시작해도 충분합니다. 핵심은 “서비스 레이어를 둔다”가 아니라 “비즈니스 규칙, 유스케이스 조율, 읽기 쿼리, 외부 부수효과를 섞지 않는다”입니다.

제 추천은 이렇습니다: 작은 앱은 `models.py`의 도메인 메서드 + `services.py` 함수로 시작하고, 읽기 로직은 `selectors.py`로 분리하세요. 경계가 커지고 테스트/의존성 관리가 부담되기 시작하면 그때 `application/`, `domain/`, `infrastructure/`로 분리하면 됩니다.

---
> **관련 스킬 참조:**
> - 서비스 레이어와 Django 구조 → **implementation-django** 스킬
> - 애플리케이션 서비스와 도메인 서비스 구분 → **architecture-ddd** 스킬