**주요 내용**

일반적인 Django 프로젝트라면 먼저 앱 안에 둡니다.

```text
apps/
  orders/
    models.py
    services.py      # 쓰기/Command 유스케이스
    selectors.py     # 읽기/Query 전용
    api.py           # Django Ninja Router가 services/selectors 호출
```

즉 `orders.services.order_confirm()`, `users.services.user_create()`처럼 **도메인 앱별 `services.py`**에 두는 게 가장 실용적입니다. 전역 `services/` 폴더는 금방 잡탕이 되기 쉬워서 피하는 편이 좋습니다.

다만 DDD를 더 강하게 적용하는 구조라면 “서비스”를 둘로 나눠야 합니다.

```text
applications/
  orders/
    domain_layer/
      service/              # 도메인 서비스
    application_layer/
      order_service.py      # 응용 서비스
    infra_layer/
      django_orders/
        models/
    presentation_layer/
      api/
```

구분 기준은 이렇습니다.

`domain_layer/service/`에 둘 것:
여러 애그리거트에 걸친 **순수 도메인 계산/판단**이고, DB/HTTP/Django ORM에 의존하지 않는 무상태 로직입니다. 예: 할인 계산, 정산 규칙, 배정 가능성 판단.

`application_layer/*_service.py` 또는 Django 앱의 `services.py`에 둘 것:
유스케이스를 조율하는 로직입니다. 예: 주문 조회 → 상태 변경 → 저장 → 커밋 후 알림 예약. 트랜잭션, 리포지토리/ORM 호출, `transaction.on_commit()`은 여기에 둡니다.

`selectors.py`에 둘 것:
상태 변경 없는 읽기 전용 쿼리입니다. 예: `order_list()`, `order_detail()`, `available_products()`.

가장 추천하는 시작점은 이겁니다.

```text
apps/orders/
  models.py       # 핵심 불변식과 단일 모델/애그리거트의 도메인 메서드
  services.py     # 쓰기 유스케이스, 트랜잭션, 외부 부수효과 조율
  selectors.py    # 읽기 쿼리
```

서비스 레이어에 모든 비즈니스 로직을 몰아넣지는 않는 게 좋습니다. `order.confirm()`처럼 애그리거트/모델이 스스로 지켜야 하는 상태 전이와 불변식은 모델 쪽에 두고, 서비스는 “무엇을 어떤 순서로 호출할지”만 조율하게 두는 게 유지보수성이 좋습니다.

현재 워크스페이스에는 `config.toml`과 실제 프로젝트 파일이 없어, dddjango 기준의 일반 권장안으로 답했습니다.

---
> **관련 스킬 참조:**
> - 서비스 레이어/셀렉터 배치 → **implementation-django** 스킬
> - 도메인 서비스 vs 응용 서비스 구분 → **architecture-ddd** 스킬
> - 헥사고날/클린 구조로 확장 → **architecture-implementation-patterns** 스킬