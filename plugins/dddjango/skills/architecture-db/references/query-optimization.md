# 쿼리 최적화 레퍼런스

EXPLAIN ANALYZE 읽기, 스캔/조인 유형, N+1 문제, 일반 원칙.

---

## EXPLAIN ANALYZE 읽기

```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- 출력 예시:
-- Index Scan using idx_email on users
--   (cost=0.42..8.44 rows=1 width=244)
--   (actual time=0.017..0.018 rows=1 loops=1)
--   Buffers: shared hit=4
-- Planning Time: 0.105 ms
-- Execution Time: 0.038 ms
```

| 항목 | 의미 |
|------|------|
| cost (시작..총) | 임의 단위의 예상 비용 (1.0 = 순차 디스크 페이지 1회 읽기) |
| rows | 예상 반환 행 수 |
| actual time | 실제 소요 시간 (ms) |
| Buffers: shared hit/read | 캐시 히트 vs 디스크 읽기 |

**핵심**: 예상 행(rows)과 실제 행(actual rows)이 크게 다르면 `ANALYZE` 실행하여 테이블 통계를 갱신한다.

---

## 스캔 유형

| 유형 | 설명 | 주의 |
|------|------|------|
| **Seq Scan** | 테이블의 모든 행을 순차 읽기 | 대형 테이블에서 경고 신호 |
| **Index Scan** | 인덱스로 행을 하나씩 접근 | 소수 행에 효율적 |
| **Bitmap Heap Scan** | 2단계: 인덱스로 위치 파악 → 물리 순서로 접근 | Index Scan과 Seq Scan 사이 |
| **Index-Only Scan** | 인덱스만으로 데이터 반환 (커버링 인덱스) | 가장 빠른 읽기 |

---

## 조인 유형

| 유형 | 적합한 경우 | 특징 |
|------|-----------|------|
| **Nested Loop** | 작은 외부 집합 + 인덱스된 내부 | 소규모 데이터에 최적 |
| **Hash Join** | 중·대형 비정렬 데이터 | 작은 테이블로 해시 테이블 생성 |
| **Merge Join** | 조인 키로 사전 정렬된 데이터 | 대규모 정렬 데이터에 효율적 |

---

## N+1 문제

1개 쿼리로 N개 부모를 가져온 후, N개 추가 쿼리로 각 부모의 자식을 개별 조회하는 문제. ORM의 lazy loading이 주 원인.

```
-- N+1 발생 (1 + N 쿼리)
SELECT * FROM authors;                          -- 1회
SELECT * FROM books WHERE author_id = 1;        -- N회 반복
SELECT * FROM books WHERE author_id = 2;
...

-- 해결: JOIN 또는 IN 절 (1-2 쿼리)
SELECT * FROM authors a JOIN books b ON a.id = b.author_id;
-- 또는
SELECT * FROM authors;
SELECT * FROM books WHERE author_id IN (1, 2, 3, ...);
```

---

## 일반 원칙

| 원칙 | 설명 |
|------|------|
| SELECT * 회피 | 필요한 컬럼만 지정 (커버링 인덱스 활용 가능) |
| WHERE 절 활용 | 가능한 한 DB 단에서 필터링 (애플리케이션 필터링 회피) |
| LIMIT 사용 | 결과 집합 크기 제한 |
| 서브쿼리 vs JOIN | 대부분 JOIN이 서브쿼리보다 효율적 (옵티마이저 의존) |
