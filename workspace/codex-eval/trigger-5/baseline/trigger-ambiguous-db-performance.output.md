**주요 내용**

DB 성능은 “느린 느낌”부터 바로 인덱스 추가로 가지 말고, 먼저 느린 쿼리를 특정해야 합니다. 순서는 보통 이렇게 봅니다.

1. 슬로우 쿼리부터 잡기  
   PostgreSQL이면 `pg_stat_statements`, MySQL이면 slow query log를 켜고 호출 횟수, 평균 시간, 총 소요 시간이 큰 쿼리를 봅니다.

2. 해당 쿼리에 `EXPLAIN ANALYZE` 붙이기  
   봐야 할 핵심은:
   - `actual time`: 실제 오래 걸리는 구간
   - `rows` 예상치와 실제 row 차이
   - `Seq Scan`: 큰 테이블 전체 스캔 여부
   - `Buffers: shared read`: 디스크 읽기가 많은지
   - 조인 방식: `Nested Loop`가 큰 데이터에서 반복되는지

3. ORM 사용 중이면 N+1 확인  
   Django라면 특히 `select_related`, `prefetch_related` 누락이 흔합니다. “목록 1번 조회 후 각 row마다 추가 쿼리” 패턴이 있는지 Django Debug Toolbar나 query logging으로 봅니다.

4. 인덱스는 쿼리 기준으로 설계  
   테이블 컬럼을 보고 막 추가하지 말고, 실제 `WHERE`, `JOIN`, `ORDER BY` 조건 기준으로 봐야 합니다. 복합 인덱스는 보통 `=` 조건 컬럼을 앞에, 범위 조건 `>`, `<`, `BETWEEN` 컬럼을 뒤에 둡니다.

5. 그래도 느리면 다음 단계  
   쿼리 수정 → 인덱스 → 캐시 → 비정규화 순서가 안전합니다. 비정규화는 마지막입니다.

예를 들어 PostgreSQL이면 첫 진단은 이런 식입니다.

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT ...
```

그리고 Django라면 뷰/API 단위로 실제 실행 SQL 수와 시간을 먼저 확인하세요. “한 요청에 쿼리 200개”면 DB 자체보다 ORM 접근 패턴 문제가 먼저입니다.

참고로 현재 `/private/tmp/dddjango-codex-eval`에는 프로젝트 파일이 보이지 않아서 구체적인 쿼리나 모델까지는 못 봤습니다. 느린 API, 쿼리, 모델, 또는 `EXPLAIN ANALYZE` 결과를 주면 병목을 바로 짚을 수 있습니다.

---
> **관련 스킬 참조:**
> - 쿼리 실행 계획, 인덱스, N+1 진단 → **architecture-db** 스킬