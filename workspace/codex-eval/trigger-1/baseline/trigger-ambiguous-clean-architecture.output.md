`/private/tmp/dddjango-codex-eval`을 확인했지만 현재 디렉터리는 비어 있고, `.git` 저장소도 아닙니다. 또한 세션 권한이 `read-only`라서 파일 생성/수정은 할 수 없습니다. 그래서 실제 리팩터링 적용은 진행할 수 없었습니다.

클린 아키텍처로 정리할 때의 기본 Django 구조는 이렇게 잡는 게 적절합니다:

```text
apps/
  orders/
    domain/
      model/
        order/
          entities.py
          value_objects.py
          events.py
          exceptions.py
      repositories.py
    application/
      services.py
      commands.py
      queries.py
      unit_of_work.py
    infrastructure/
      django_models.py
      repositories.py
      unit_of_work.py
    api/
      schemas.py
      routers.py
      selectors.py
```

핵심 방향은 다음입니다.

- `domain`: Django ORM, HTTP, 외부 SDK를 import하지 않음
- `application`: 유스케이스 조율, 트랜잭션 경계, 포트 사용
- `infrastructure`: Django ORM Repository, 외부 API Adapter 구현
- `api`: Django Ninja Router/Schema, 입력 검증과 응답 변환
- Repository 인터페이스는 사용하는 쪽인 `domain` 또는 `application`이 소유
- Repository 구현체는 `infrastructure`에 둠
- 비즈니스 규칙은 서비스 함수가 아니라 Aggregate/Value Object 안으로 이동

실제 코드가 있는 경로를 제공하거나 현재 작업 디렉터리에 파일이 들어오면, 기존 구조를 읽고 의존성 방향을 맞춰 실제 파일 단위로 재배치하겠습니다.

---
> **관련 스킬 참조:**
> - 클린/헥사고날 구조 적용 → **architecture-implementation-patterns** 스킬
> - Django 계층 구조와 서비스 레이어 → **implementation-django** 스킬