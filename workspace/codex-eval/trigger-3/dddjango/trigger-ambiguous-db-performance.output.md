**주요 내용**

Django + 일반 RDB, 특히 PostgreSQL 계열이라고 가정하고 보면 됩니다. DB가 “느리다”는 말은 보통 3가지 중 하나입니다: 쿼리 자체가 느림, 쿼리 수가 너무 많음, 락/동시성 때문에 대기함.

먼저 순서는 이렇게 잡으세요.

1. **느린 화면/요청을 하나로 좁히기**
   “전체가 느림”으로 보면 안 잡힙니다. 특정 API, 관리자 화면, 배치 작업, 페이지 로딩 중 하나를 고릅니다.

2. **실제 SQL과 쿼리 수 확인**
   Django에서는 로컬에서 `django-debug-toolbar` 또는 로그로 SQL을 봅니다. 특히 같은 패턴의 SELECT가 반복되면 N+1입니다.

   흔한 Django 원인:
   - FK/O2O 접근 반복 → `select_related()`
   - M2M/역참조 반복 → `prefetch_related()`
   - 루프 안에서 `save()` 반복 → `bulk_update()`, `update()`
   - 존재 확인에 전체 로딩 → `exists()`
   - 개수 확인에 `len(queryset)` → `count()`

3. **느린 SQL에 `EXPLAIN ANALYZE` 실행**
   추측으로 인덱스를 추가하지 말고 실행 계획을 봅니다. 확인할 것:
   - `Seq Scan`이 큰 테이블에서 발생하는지
   - 예상 row 수와 실제 row 수가 크게 다른지
   - join 방식이 비정상적으로 비싼지
   - `actual time`, `buffers`, `rows`가 어디서 커지는지

4. **쿼리 워크로드 기준으로 인덱스 설계**
   인덱스는 테이블 기준이 아니라 자주 실행되는 WHERE/JOIN/ORDER BY 기준입니다.

   예:
   ```sql
   WHERE user_id = ? AND status = ? ORDER BY created_at DESC
   ```

   이런 쿼리가 많으면 대략 다음 후보를 봅니다.

   ```sql
   CREATE INDEX ON orders (user_id, status, created_at DESC);
   ```

   복합 인덱스는 보통 동등 조건 컬럼을 앞에, 범위/정렬 컬럼을 뒤에 둡니다.

5. **그래도 느리면 캐시, 마지막에 비정규화**
   순서는 `느린 쿼리 수정 -> 인덱스 -> 캐시 -> 비정규화`입니다. 집계 컬럼, 중복 저장, 테이블 분리는 측정 결과가 있을 때만 합니다.

6. **회귀 방지**
   Django 테스트에 중요한 조회 경로는 `assertNumQueries`를 넣어 N+1 재발을 막으세요.

   ```python
   with self.assertNumQueries(2):
       response = self.client.get("/orders/")
   ```

가장 먼저 필요한 자료는 “느린 요청 하나의 SQL 목록”과 “가장 느린 SQL의 `EXPLAIN ANALYZE` 결과”입니다. 그 두 개가 있으면 인덱스 문제인지, ORM N+1인지, 락/트랜잭션 문제인지 꽤 빠르게 갈라낼 수 있습니다.

---
> **관련 스킬 참조:**
> - 쿼리 실행 계획/인덱스 설계 → **architecture-db** 스킬
> - Django ORM N+1/select_related/prefetch_related 개선 → **implementation-django** 스킬