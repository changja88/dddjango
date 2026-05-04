현재 작업공간에는 `config.toml`이나 프로젝트 파일이 없어서 코드 기준 진단은 못 했습니다. Django DB 성능을 볼 때는 보통 아래 순서로 보면 됩니다.

1. **느린 쿼리부터 찾기**
   - PostgreSQL이면 `pg_stat_statements` 활성화
   - MySQL이면 slow query log 확인
   - Django 개발 환경에서는 `django-debug-toolbar`로 요청별 SQL 확인

2. **쿼리 실행 계획 확인**
   ```sql
   EXPLAIN ANALYZE SELECT ...;
   ```
   확인할 것:
   - `Seq Scan`이 큰 테이블에서 발생하는지
   - 인덱스를 타는지
   - rows estimate가 실제와 크게 다른지
   - sort/hash join 비용이 큰지

3. **Django ORM 문제 확인**
   흔한 원인:
   - N+1 쿼리
   - `select_related()` 누락
   - `prefetch_related()` 누락
   - 불필요한 `.all()` 후 파이썬에서 필터링
   - pagination 없이 대량 조회
   - `.count()` 반복 호출

   예:
   ```python
   Post.objects.select_related("author").prefetch_related("comments")
   ```

4. **인덱스 확인**
   자주 쓰는 조건에 인덱스가 있는지 봅니다.
   - `WHERE user_id = ?`
   - `WHERE status = ?`
   - `ORDER BY created_at DESC`
   - `WHERE tenant_id = ? AND created_at > ?`

   복합 조건이면 단일 인덱스보다 복합 인덱스가 필요할 수 있습니다.

5. **DB 연결/락 확인**
   느린 게 쿼리 자체가 아니라 대기일 수도 있습니다.
   PostgreSQL 기준:
   ```sql
   SELECT * FROM pg_stat_activity;
   ```

   봐야 할 것:
   - 오래 열린 transaction
   - lock wait
   - idle in transaction
   - connection 수 과다

6. **Django에서 빠르게 계측**
   특정 코드 블록의 쿼리 수 확인:
   ```python
   from django.db import connection

   # 실행 후
   print(len(connection.queries))
   for q in connection.queries:
       print(q["time"], q["sql"])
   ```

운영 DB라면 먼저 “가장 느린 요청/쿼리 TOP 10”을 잡고, 각 쿼리에 대해 `EXPLAIN ANALYZE`를 보는 게 제일 빠릅니다. PostgreSQL인지 MySQL인지, 그리고 느린 API나 ORM 코드가 있으면 그 기준으로 더 구체적으로 봐드릴 수 있습니다.