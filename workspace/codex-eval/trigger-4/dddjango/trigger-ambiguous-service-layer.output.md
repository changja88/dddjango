도메인이 복잡해지는 Django 앱이라고 가정하겠습니다. 한 가지 확인할 점은 “서비스 레이어”가 단순 CRUD 분리인지, DDD식 유스케이스 조율인지입니다.

**주요 내용**

**Django라면** 우선 앱 내부에 둡니다.

```text
apps/
  orders/
    models.py
    services.py      # 쓰기 유스케이스: order_confirm, order_cancel
    selectors.py     # 읽기 전용 쿼리
```

서비스를 `project/services/` 같은 공용 루트에 모으는 건 보통 피하는 게 좋습니다. 앱 경계가 흐려지고, 시간이 지나면 모든 도메인이 섞인 절차형 레이어가 되기 쉽습니다.

DDD를 적용한다면 한 단계 더 나눕니다.

```text
apps/
  orders/
    domain/
      entities.py
      value_objects.py
      services.py        # 도메인 서비스: 정말 엔티티에 둘 수 없는 규칙만
      events.py
    application/
      services.py        # 유스케이스 조율
      selectors.py       # 읽기 전용
    models.py            # Django ORM 영속성 모델
```

기준은 이렇게 잡으면 됩니다.

- 비즈니스 불변식은 가능한 한 모델/엔티티/값 객체에 둡니다.
- 여러 모델을 한 트랜잭션에서 조율하거나 외부 API, 이메일, 알림을 다루면 `application/services.py`에 둡니다.
- 순수 조회는 `selectors.py`로 분리합니다.
- 트랜잭션 커밋 후 실행돼야 하는 부수 효과는 `transaction.on_commit()`으로 처리합니다.
- 도메인 서비스는 “어느 엔티티의 책임도 아닌 도메인 규칙”일 때만 둡니다. 남발하면 빈약한 도메인 모델이 됩니다.

실무적으로는 처음부터 과하게 `domain/application/infrastructure`를 나누기보다, 단순 Django 앱이면 `services.py`/`selectors.py`로 시작하고, 규칙과 유스케이스가 커질 때 DDD 구조로 확장하는 편이 낫습니다.

참고로 현재 작업 디렉터리에서 `config.toml`은 찾지 못했습니다.

---
> **관련 스킬 참조:**
> - 서비스 레이어 위치와 Django 구조 → **implementation-django** 스킬
> - 도메인 서비스와 응용 서비스 구분 → **architecture-ddd** 스킬