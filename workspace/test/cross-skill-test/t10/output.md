# T10: architecture-db -> implementation-django

**Task:** "인덱스 전략 후 Django ORM select_related/Prefetch 코드 작성법은?"

**Source Skill:** architecture-db

## [주요 내용]

architecture-db 스킬은 인덱스 전략(B+Tree, 복합 인덱스, 커버링 인덱스)을 다루지만,
Django ORM 코드(select_related, Prefetch)는 **이 스킬의 범위 밖**이다.

SKILL.md 위임 규칙에 따른 판단:
- "Django ORM 코드(QuerySet, select_related, 마이그레이션, PostgreSQL 기능)에 대해서는 implementation-django에 위임한다."

이 스킬이 제공할 수 있는 부분:
1. 쿼리 워크로드 기반 인덱스 설계 (동등 조건 > 범위 조건)
2. N+1 문제 탐지와 해결 방향 (JOIN 또는 배치 로딩)
3. EXPLAIN ANALYZE 출력 해석
- (섹션 3: `references/index-and-performance.md`, 섹션 5: `references/query-optimization.md` 참조)

Django ORM의 `select_related()` (FK/O2O), `prefetch_related()` (M2M/역방향),
`Prefetch()` 객체 사용법은 **implementation-django**로 위임한다.

---
> **관련 스킬 참조:**
> - Django ORM select_related/prefetch_related 패턴 -> **implementation-django** 스킬
> - PostgreSQL 특수 인덱스 (GIN, GiST) -> **implementation-django** 스킬
