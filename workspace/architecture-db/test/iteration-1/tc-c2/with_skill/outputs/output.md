# EXPLAIN ANALYZE 해석 및 최적화 제안

## 1. 실행 계획 요약

| 노드 | 예상 행 | 실제 행 | 실제 시간 (ms) | 비고 |
|------|---------|---------|---------------|------|
| Seq Scan on **users** | 50,000 | 50,000 | 50.8 | `created_at > '2024-01-01'` 필터, 30,000행 제거 |
| Hash (users 해시 테이블 생성) | 50,000 | 50,000 | 75.3 | Memory 3,500kB |
| Seq Scan on **orders** | 2,000,000 | 2,000,000 | 1,800.5 | **전체 테이블 풀 스캔** |
| Hash Right Join | 500,000 | 480,000 | 3,200.8 | 조인 결과 |
| HashAggregate | 20,000 | 18,500 | 4,450.8 | GROUP BY + HAVING, 31,500행 제거 |
| Sort (top-N heapsort) | 20 | 20 | 4,500.2 | ORDER BY DESC, Memory 27kB |
| Limit | 20 | 20 | 4,500.3 | 최종 결과 |

**총 실행 시간: 4,502.5 ms (약 4.5초)**

---

## 2. 병목 지점 분석

### 병목 1 (최대): orders 테이블 Seq Scan -- 전체 시간의 약 40%

```
Seq Scan on orders o (cost=0.00..55000.00 rows=2,000,000 width=16)
  (actual time=0.05..1800.5 rows=2,000,000 loops=1)
```

[Seq Scan on large table] -- 200만 행 전체를 순차 스캔한다. orders 테이블에 `user_id` 컬럼에 대한 인덱스가 없거나, 있더라도 옵티마이저가 전체 행을 읽어야 하므로 Seq Scan을 선택한 것이다. 이 노드 하나가 1,800ms를 소비하며 전체 실행 시간의 약 40%를 차지한다.

### 병목 2: Hash Right Join -- 전체 시간의 약 31%

```
Hash Right Join (cost=3500.00..74000.00 rows=500000 width=24)
  (actual time=80.5..3200.8 rows=480000 loops=1)
```

[조인 비용] -- 50,000명의 users와 2,000,000건의 orders를 Hash Join으로 결합하여 480,000행을 생성한다. 조인 자체에 약 1,400ms(3200.8 - 1800.5)가 소요된다. 조인 입력이 줄어들면 이 비용도 비례하여 감소한다.

### 병목 3: HashAggregate + HAVING 필터 -- 약 1,250ms

```
HashAggregate (cost=84000.00..84500.00 rows=20000 width=52)
  (actual time=4200.5..4450.8 rows=18500 loops=1)
  Rows Removed by Filter: 31,500
```

[불필요한 집계 후 제거] -- 50,000명 전원에 대해 집계를 수행한 뒤 HAVING으로 31,500행을 버린다. 즉 전체 집계 작업의 63%가 최종 결과에 기여하지 않는다.

### 병목 4 (경미): users 테이블 Seq Scan

```
Seq Scan on users u (cost=0.00..3000.00 rows=50000 width=16)
  (actual time=0.03..50.8 rows=50000 loops=1)
  Filter: (created_at > '2024-01-01')
  Rows Removed by Filter: 30,000
```

[Seq Scan on filtered column] -- 80,000행 중 30,000행을 필터로 제거하여 50,000행을 반환한다. 50.8ms로 상대적으로 빠르지만, `created_at` 인덱스를 추가하면 30,000행의 불필요한 읽기를 제거할 수 있다.

---

## 3. 최적화 제안

최적화 순서: 슬로우 쿼리 최적화 -> 인덱스 적용 -> 캐시 -> 역정규화

### 개선 1: orders.user_id 인덱스 추가 (가장 큰 효과)

```sql
-- [Before]
-- orders 테이블에 user_id 인덱스 없음 -> 200만 행 Seq Scan

-- [After]
CREATE INDEX idx_orders_user_id ON orders (user_id);
```

[Reason] Seq Scan on large table -- 200만 행 풀 스캔을 제거한다. 인덱스가 있으면 옵티마이저가 Nested Loop + Index Scan 또는 더 효율적인 Hash Join을 선택할 수 있다. 조인에 필요한 행만 인덱스를 통해 접근하므로 I/O가 대폭 감소한다.

### 개선 2: users.created_at 인덱스 추가

```sql
-- [Before]
-- users 테이블 Seq Scan으로 80,000행 읽은 후 30,000행 필터 제거

-- [After]
CREATE INDEX idx_users_created_at ON users (created_at);
```

[Reason] Seq Scan on filtered column -- `created_at > '2024-01-01'` 조건으로 37.5%(30,000/80,000)의 행을 제거하고 있다. 인덱스를 추가하면 Index Scan 또는 Bitmap Heap Scan으로 전환되어 불필요한 행 읽기를 건너뛸 수 있다.

### 개선 3: 커버링 인덱스로 확장

```sql
-- [Before]
CREATE INDEX idx_orders_user_id ON orders (user_id);

-- [After]
CREATE INDEX idx_orders_user_id_covering ON orders (user_id) INCLUDE (total_amount);
```

[Reason] 커버링 인덱스 -- 쿼리가 orders 테이블에서 `user_id`, `id`(COUNT), `total_amount`(SUM)만 사용한다. `total_amount`를 INCLUDE로 포함하면 Index-Only Scan이 가능해져 힙 테이블 접근(랜덤 I/O)을 완전히 제거한다. 이것이 가장 빠른 읽기 유형이다.

### 개선 4: 쿼리 리팩터링 -- 서브쿼리로 조기 필터링

```sql
-- [Before]
SELECT u.name, COUNT(o.id) as order_count, SUM(o.total_amount) as total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at > '2024-01-01'
GROUP BY u.id, u.name
HAVING SUM(o.total_amount) > 100000
ORDER BY total_spent DESC
LIMIT 20;

-- [After]
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

[Reason] 불필요한 집계 후 제거 -- 두 가지 개선이 동시에 적용된다:

1. **LEFT JOIN -> INNER JOIN**: `HAVING SUM(total_amount) > 100000` 조건은 주문이 없는 사용자를 이미 제거하므로 LEFT JOIN이 불필요하다. INNER JOIN으로 변경하면 옵티마이저가 더 효율적인 실행 계획을 세울 수 있다.
2. **서브쿼리에서 조기 집계**: orders를 먼저 user_id별로 집계하고 HAVING으로 필터링한 뒤, 그 결과만 users와 조인한다. 이렇게 하면 조인 입력 행이 480,000 -> 18,500으로 대폭 감소한다.

### 개선 5: SELECT에 필요한 컬럼만 명시 (이미 적용됨, 확인)

[SELECT * 회피] -- 현재 쿼리는 이미 `u.name`, `COUNT(o.id)`, `SUM(o.total_amount)`만 선택하고 있어 이 원칙은 이미 준수되고 있다.

---

## 4. 예상 개선 효과

| 개선 사항 | 예상 시간 절감 | 근거 |
|----------|--------------|------|
| `idx_orders_user_id` 인덱스 | ~1,500ms | 200만 행 Seq Scan 제거 |
| `idx_users_created_at` 인덱스 | ~30ms | 30,000행 불필요 읽기 제거 |
| 커버링 인덱스 (INCLUDE total_amount) | ~500ms 추가 절감 | 힙 테이블 랜덤 I/O 제거 |
| 쿼리 리팩터링 (조기 집계 + INNER JOIN) | ~1,000ms | 조인 입력 행 96% 감소 |
| **합산 예상** | **~3,000ms 절감** | **4,500ms -> ~1,500ms 이하** |

---

## 5. 적용 우선순위

```
1. idx_orders_user_id 인덱스 생성          -- 즉시, 가장 큰 효과
2. 쿼리 리팩터링 (INNER JOIN + 서브쿼리)    -- 코드 변경만으로 큰 효과
3. 커버링 인덱스로 확장 (INCLUDE)           -- 추가 I/O 제거
4. idx_users_created_at 인덱스 생성         -- 부가적 효과
```

인덱스 추가 시 쓰기 성능(INSERT/UPDATE/DELETE)에 대한 트레이드오프를 고려해야 한다. orders 테이블이 읽기 중심이라면 인덱스 추가의 이점이 크고, 쓰기가 매우 빈번하다면 벤치마크 후 결정한다.
