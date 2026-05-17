# Skill Hierarchy

이 문서는 trigger 우선순위가 아니라 workflow composition map이다.

implementation skill은 바닥 스킬이다. 단순 CRUD, 단일 파일 수정, 이미 도메인 판단이 끝난 작은 구현에서는 implementation skill로 직접 들어갈 수 있다.

도메인 규칙, 상태 전이, 정책, 불변식, bounded context가 불명확한 작업은 implementation보다 `architecture-ddd` 판단이 먼저다.

- `dddjango`
  - `source-reference-audit`
  - `workflow-dddjango-subagents`
    - `architecture-ddd`
      - `architecture-implementation-patterns`
      - `architecture-db`
      - `architecture-api`
      - `implementation-django`
      - `implementation-django-ninja`
      - `implementation-django-web`
      - `implementation-tdd`
      - `implementation-test`
      - `implementation-cleancode`
      - `implementation-python`
    - `architecture-implementation-patterns`
      - `architecture-db`
      - `architecture-api`
      - `implementation-django`
      - `implementation-django-ninja`
      - `implementation-django-web`
      - `implementation-test`
      - `implementation-cleancode`
      - `implementation-python`
    - `architecture-db`
      - `implementation-django`
      - `implementation-test`
      - `implementation-cleancode`
      - `implementation-python`
    - `architecture-api`
      - `implementation-django-ninja`
      - `implementation-test`
      - `implementation-cleancode`
      - `implementation-python`
    - `implementation-django`
    - `implementation-django-ninja`
    - `implementation-django-web`
    - `implementation-tdd`
    - `implementation-test`
    - `implementation-cleancode`
    - `implementation-python`
