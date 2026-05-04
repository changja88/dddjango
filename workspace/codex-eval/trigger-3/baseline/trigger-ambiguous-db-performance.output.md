현재 `/private/tmp/dddjango-codex-eval`에는 프로젝트 파일이나 `config.toml`이 없어서 코드 기준 진단은 못 했습니다. Django DB 성능은 보통 아래 순서로 보면 됩니다.

1. **느린 요청/쿼리부터 잡기**
   - 개발 환경: `django-debug-toolbar`
   - 운영 환경: DB slow query log, APM, Django query logging
   - 확인할 것: 쿼리 수, 총 DB 시간, 반복되는 동일 쿼리, N+1

2. **N+1 확인**
   - ORM에서 반복문 안에 FK/M2M 접근이 있으면 의심합니다.
   - 해결:
     ```python
     queryset = Post.objects.select_related("author")
     queryset = Post.objects.prefetch_related("comments")
     ```

3. **실행 계획 확인**
   - Django:
     ```python
     print(queryset.explain())
     ```
   - PostgreSQL이면:
     ```sql
     EXPLAIN ANALYZE SELECT ...
     ```
   - `Seq Scan`, 예상보다 큰 row count, 느린 sort/join이 보이면 인덱스나 쿼리 구조를 봐야 합니다.

4. **인덱스 점검**
   자주 쓰는 조건에 인덱스가 있는지 봅니다.
   - `WHERE user_id = ?`
   - `WHERE status = ? AND created_at >= ?`
   - `ORDER BY created_at DESC`
   - FK는 보통 인덱스가 있지만, 복합 조건은 별도 인덱스가 필요할 수 있습니다.

5. **쿼리 수 줄이기**
   - `.only()`, `.defer()`로 큰 컬럼 제외
   - `.values()` / `.values_list()`로 필요한 필드만 조회
   - `count()` 남발, 페이지네이션 offset 과다, 불필요한 annotation 확인

6. **DB 자체 상태 확인**
   PostgreSQL 기준:
   ```sql
   SELECT * FROM pg_stat_activity;
   SELECT * FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 20;
   ```
   MySQL 기준:
   ```sql
   SHOW FULL PROCESSLIST;
   SHOW VARIABLES LIKE 'slow_query_log';
   ```

가장 빠른 출발점은 “느린 화면 하나”를 골라서 **쿼리 개수, 가장 느린 쿼리, 실행 계획**을 보는 것입니다. 프로젝트 파일을 넣어주면 ORM 코드 기준으로 어디가 병목인지 직접 짚어볼 수 있습니다.