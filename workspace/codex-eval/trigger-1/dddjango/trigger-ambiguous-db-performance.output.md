**주요 내용**

DB가 느릴 때는 “느린 것 같다”에서 바로 인덱스나 캐시로 가지 말고, 먼저 느린 쿼리를 특정해야 합니다. 순서는 보통 이렇습니다.

1. 느린 요청/작업을 먼저 좁힙니다.
   - 어떤 API, 화면, 배치, 관리자 기능이 느린지
   - 평균이 느린지, p95/p99만 튀는지
   - DB CPU, I/O, lock wait, connection pool 중 어디가 병목인지

2. 실제 SQL을 봅니다.
   - Django라면 개발 환경에서 `django-debug-toolbar`, `django-silk`로 쿼리 수와 시간을 봅니다.
   - 운영 DB는 slow query log, `pg_stat_statements` 같은 집계로 상위 쿼리를 봅니다.
   - Django ORM 코드에서는 `str(queryset.query)` 또는 로그 설정으로 실제 SQL을 확인합니다.

3. `EXPLAIN ANALYZE`를 봅니다.
   확인할 핵심은 네 가지입니다.
   - `Seq Scan`: 큰 테이블에서 전체 스캔 중인지
   - `actual time`: 실제 어느 단계가 오래 걸리는지
   - `rows` 예상치와 실제 rows 차이: 통계가 틀렸는지
   - `Buffers: shared hit/read`: 메모리 캐시인지 디스크 읽기인지

   PostgreSQL이면 예를 들어:

   ```sql
   EXPLAIN (ANALYZE, BUFFERS)
   SELECT ...
   ```

4. Django ORM의 N+1을 먼저 의심합니다.
   가장 흔한 병목입니다.

   ```python
   # 나쁨: book마다 author 조회
   books = Book.objects.all()
   for book in books:
       book.author.name

   # 좋음: FK/O2O는 select_related
   books = Book.objects.select_related("author")
   ```

   관계별 기준은 단순합니다.
   - `ForeignKey`, `OneToOneField` → `select_related()`
   - `ManyToManyField`, reverse FK → `prefetch_related()`
   - 조건부 프리페치 → `Prefetch()`

5. 인덱스는 쿼리 기준으로 추가합니다.
   테이블 구조가 아니라 실제 `WHERE`, `JOIN`, `ORDER BY` 패턴을 보고 설계해야 합니다.

   ```python
   class Meta:
       indexes = [
           models.Index(fields=["status", "-created_at"], name="idx_status_created"),
       ]
   ```

   복합 인덱스는 보통 동등 조건을 먼저, 범위/정렬 조건을 뒤에 둡니다.

   ```sql
   -- WHERE status = 'paid' AND created_at >= ...
   -- 좋음
   CREATE INDEX idx_orders_status_created_at
   ON orders (status, created_at);
   ```

6. ORM 사용 습관도 확인합니다.
   - 존재 여부: `if queryset:` 대신 `queryset.exists()`
   - 개수: `len(queryset)` 대신 `queryset.count()`
   - 대량 수정: 루프 안 `save()` 대신 `update()`, `bulk_update()`
   - 카운터/재고/잔액: Python 연산 대신 `F()` 표현식
   - 필요한 컬럼만: 경우에 따라 `values()`, `values_list()`, `only()`

7. 캐시는 마지막 쪽입니다.
   캐시는 느린 쿼리와 인덱스를 본 다음 적용하는 게 맞습니다. 무효화 전략 없이 캐시부터 넣으면 오래된 데이터 버그가 생깁니다.

바로 시작하려면 이 3개를 먼저 뽑아주세요.

```bash
# 1. 느린 엔드포인트/작업명
# 2. 해당 Django ORM 코드 또는 SQL
# 3. EXPLAIN ANALYZE 결과
```

Django 프로젝트라면 성능 회귀 방지용 테스트도 같이 두는 게 좋습니다.

```python
def test_book_list_query_count(django_assert_num_queries):
    with django_assert_num_queries(2):
        list(Book.objects.select_related("author").prefetch_related("tags"))
```

핵심 순서는 **느린 쿼리 특정 → N+1 제거 → EXPLAIN ANALYZE → 인덱스 → 캐시 → 비정규화**입니다. 비정규화는 최후의 수단으로 두는 게 안전합니다.

---
> **관련 스킬 참조:**
> - DB 쿼리/인덱스/EXPLAIN 분석 → **architecture-db** 스킬
> - Django ORM, `select_related`, `prefetch_related`, 성능 테스트 → **implementation-django** 스킬