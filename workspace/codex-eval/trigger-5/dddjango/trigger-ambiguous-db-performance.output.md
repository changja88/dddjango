맥락이 불명확합니다. 우선 “특정 화면/API가 느린 Django 앱의 RDB 성능 문제”라고 가정하고 보겠습니다.

**주요 내용**

먼저 추측하지 말고 느린 지점을 고정하세요.

1. 느린 요청/배치/쿼리를 특정합니다.
   - APM, DB slow query log, Django Debug Toolbar, 로그 타이밍으로 “어떤 쿼리”가 느린지 봅니다.
   - 전체 DB가 느린지, 특정 엔드포인트만 느린지 분리합니다.

2. `EXPLAIN ANALYZE`로 실행 계획을 봅니다.
   - `Seq Scan`이 큰 테이블에서 발생하는지
   - 예상 rows와 실제 rows가 크게 다른지
   - 조인 방식이 비정상적으로 비싼지
   - `actual time`, `buffers`, sort/hash 비용이 큰지 확인합니다.

3. 인덱스는 쿼리 기준으로 봅니다.
   - `WHERE`, `JOIN`, `ORDER BY`에 자주 쓰는 컬럼부터 확인합니다.
   - 복합 인덱스는 보통 `동등 조건 컬럼 → 범위 조건 컬럼 → 정렬 컬럼` 순서가 유리합니다.
   - 삭제/비활성 데이터가 많은 조건이면 부분 인덱스도 후보입니다.

4. N+1을 먼저 의심합니다.
   - 쿼리 하나가 느린 게 아니라 “작은 쿼리가 수백 번”이면 인덱스보다 접근 패턴 문제입니다.

**Django라면**

- FK/O2O 접근: `select_related()`
- M2M/역방향 FK: `prefetch_related()` 또는 `Prefetch()`
- 존재 확인: `if qs:` 대신 `qs.exists()`
- 개수 확인: `len(qs)` 대신 `qs.count()`
- 루프 안 `save()` 반복: `bulk_update()`, `update()`
- 변경 필드만 저장: `save(update_fields=[...])`
- 회귀 방지: 테스트에 `assertNumQueries` 추가

최적화 순서는 보통 `느린 쿼리 식별 → 쿼리/접근 패턴 수정 → 인덱스 → 캐시 → 비정규화`입니다. 캐시나 비정규화는 측정 없이 먼저 넣으면 원인 은폐와 데이터 불일치 위험이 큽니다.

---
> **관련 스킬 참조:**
> - 쿼리 실행 계획/인덱스 설계 → **architecture-db** 스킬
> - Django ORM N+1 및 QuerySet 최적화 → **implementation-django** 스킬