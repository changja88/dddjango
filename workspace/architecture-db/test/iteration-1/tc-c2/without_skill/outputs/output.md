# EXPLAIN ANALYZE 결과 해석

## 실행 요약

| 항목 | 값 |
|---|---|
| 총 실행 시간 | **4,502.5 ms (약 4.5초)** |
| 계획 시간 | 1.2 ms |
| users 테이블 행 수 | 80,000 (필터 후 50,000) |
| orders 테이블 행 수 | 2,000,000 |
| JOIN 결과 행 수 | 480,000 |
| 최종 반환 행 수 | 20 |

---

## 실행 계획 단계별 분석

### 1단계: users 테이블 스캔 (50.8ms)

```
Seq Scan on users u (actual time=0.03..50.8 rows=50000 loops=1)
  Filter: (created_at > '2024-01-01')
  Rows Removed by Filter: 30000
```

- **Sequential Scan** 수행 -- 인덱스를 사용하지 않고 전체 테이블을 순차 탐색
- 80,000행 중 30,000행을 필터로 제거하고 50,000행 반환
- 소요 시간 자체는 50.8ms로 크지 않음
- 그러나 `created_at` 컬럼에 인덱스가 없어서 Seq Scan이 발생하고 있음

### 2단계: orders 테이블 스캔 (1,800.5ms) -- 첫 번째 병목

```
Seq Scan on orders o (actual time=0.05..1800.5 rows=2000000 loops=1)
```

- **200만 행 전체를 Sequential Scan** -- 가장 큰 병목 지점
- 전체 실행 시간(4,502ms)의 약 **40%** 를 차지
- orders 테이블에 `user_id` 인덱스가 없어서 전체 테이블 스캔이 발생

### 3단계: Hash Right Join (3,200.8ms) -- 두 번째 병목

```
Hash Right Join (actual time=80.5..3200.8 rows=480000 loops=1)
  Hash Cond: (o.user_id = u.id)
```

- users 해시 테이블 구축(75.3ms) 자체는 빠르지만, orders 200만 행과의 JOIN에서 3,200ms 소요
- JOIN 결과 480,000행 생성
- orders Seq Scan(1,800ms) + 해시 매칭 비용이 합산된 시간

### 4단계: HashAggregate (4,200.5ms ~ 4,450.8ms)

```
HashAggregate (actual time=4200.5..4450.8 rows=18500 loops=1)
  Rows Removed by Filter: 31500
```

- 480,000행을 GROUP BY하여 50,000 그룹 생성
- HAVING 조건으로 31,500 그룹 제거, 18,500행 남음
- 메모리 사용량 4,097kB -- 메모리 내에서 처리되어 디스크 스필은 없음

### 5단계: Sort + Limit (4,500.2ms)

```
Sort Method: top-N heapsort  Memory: 27kB
```

- top-N heapsort로 상위 20개만 효율적으로 추출
- 메모리 27kB로 매우 가벼움 -- 이 단계는 문제 없음

---

## 병목 지점 정리

| 순위 | 병목 | 원인 | 소요 시간 |
|---|---|---|---|
| 1 | **orders 테이블 Seq Scan** | `user_id` 인덱스 부재로 200만 행 전체 스캔 | ~1,800ms |
| 2 | **Hash Right Join** | 대량 Seq Scan 결과와의 JOIN 비용 | ~3,200ms (누적) |
| 3 | **users 테이블 Seq Scan** | `created_at` 인덱스 부재 | ~50ms |

---

## 개선 방안

### 1. orders.user_id에 인덱스 생성 (최우선)

```sql
CREATE INDEX idx_orders_user_id ON orders (user_id);
```

- orders 200만 행 전체 Seq Scan을 Index Scan 또는 Nested Loop + Index Lookup으로 전환
- JOIN 비용을 대폭 절감 (예상 효과: 실행 시간 50~70% 감소)

### 2. users.created_at에 인덱스 생성

```sql
CREATE INDEX idx_users_created_at ON users (created_at);
```

- users 테이블 Seq Scan(80,000행)을 Index Scan(50,000행 직접 접근)으로 전환
- 현재 50ms로 병목은 아니지만, 데이터가 늘어나면 효과가 커짐

### 3. 복합 인덱스로 커버링 인덱스 구성 (고급)

```sql
-- orders: user_id와 집계 대상 컬럼을 포함하는 커버링 인덱스
CREATE INDEX idx_orders_user_id_covering ON orders (user_id) INCLUDE (id, total_amount);

-- users: created_at 필터 + 필요 컬럼 포함
CREATE INDEX idx_users_created_at_covering ON users (created_at) INCLUDE (id, name);
```

- 테이블 heap 접근 없이 인덱스만으로 쿼리를 처리하는 Index Only Scan이 가능해짐
- I/O를 추가로 절감

### 4. 쿼리 구조 개선 -- 서브쿼리로 먼저 집계

```sql
SELECT u.name, sub.order_count, sub.total_spent
FROM users u
INNER JOIN (
    SELECT user_id,
           COUNT(id) as order_count,
           SUM(total_amount) as total_spent
    FROM orders
    GROUP BY user_id
    HAVING SUM(total_amount) > 100000
) sub ON u.id = sub.user_id
WHERE u.created_at > '2024-01-01'
ORDER BY sub.total_spent DESC
LIMIT 20;
```

- orders를 먼저 집계한 뒤 users와 JOIN하면 JOIN 대상 행 수가 크게 줄어듦
- 다만 LEFT JOIN 의미가 바뀌므로(HAVING 조건에 의해 주문 없는 사용자는 이미 제외됨), 원래 쿼리 의도와 동일한 결과를 반환하는지 확인 필요

### 5. 파티셔닝 고려 (데이터가 계속 증가하는 경우)

```sql
-- orders 테이블을 날짜 기준으로 파티셔닝
CREATE TABLE orders (
    id BIGINT,
    user_id BIGINT,
    total_amount NUMERIC,
    created_at TIMESTAMP
) PARTITION BY RANGE (created_at);
```

- 200만 행이 더 커질 경우, 파티셔닝으로 스캔 범위를 물리적으로 제한

---

## 예상 개선 효과

| 적용 방안 | 예상 실행 시간 | 개선율 |
|---|---|---|
| 현재 | 4,502ms | - |
| 인덱스 1+2 적용 | 500~800ms | ~80% 감소 |
| 인덱스 1+2 + 커버링 인덱스 | 200~400ms | ~90% 감소 |
| 인덱스 + 쿼리 구조 개선 | 100~300ms | ~95% 감소 |

핵심 조치는 `orders.user_id` 인덱스 생성이며, 이것 하나만으로도 가장 큰 병목인 200만 행 Seq Scan을 제거하여 실행 시간을 대폭 줄일 수 있다.
