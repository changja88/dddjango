# 대용량 주문 테이블 인덱스 설계

## 테이블 개요

- 월 1,000만 건 적재 (연 1.2억 건)
- 1년 운영 시 약 1.2억 row, 2년 시 2.4억 row 규모

---

## 인덱스 설계

### 인덱스 1: 특정 고객의 최근 주문 조회

**대상 쿼리:**
```sql
SELECT * FROM orders
WHERE customer_id = ? ORDER BY created_at DESC LIMIT 10;
```

**인덱스:**
```sql
CREATE INDEX idx_orders_customer_created
    ON orders (customer_id, created_at DESC);
```

**설계 근거:**
- `customer_id`로 등치 조건 필터 후 `created_at DESC`로 정렬된 상태에서 바로 10건을 읽는다.
- 복합 인덱스의 선두 컬럼이 등치 조건이므로 Index Range Scan 후 LIMIT으로 조기 종료된다.
- `created_at DESC`를 명시하여 역방향 스캔(Backward Index Scan) 없이 순방향으로 읽는다.

---

### 인덱스 2: 상태별 주문 목록 (날짜 범위)

**대상 쿼리:**
```sql
SELECT * FROM orders
WHERE status = ? AND created_at BETWEEN ? AND ?;
```

**인덱스:**
```sql
CREATE INDEX idx_orders_status_created
    ON orders (status, created_at);
```

**설계 근거:**
- `status`(등치) + `created_at`(범위) 순서로 구성하여 두 조건 모두 인덱스에서 처리한다.
- `status` 카디널리티가 낮더라도(약 5~10종) 선두에 두는 것이 범위 조건과 결합 시 유리하다.
- 등치 조건이 선두이므로 `created_at` 범위 스캔이 연속된 리프 페이지에서 이루어진다.

---

### 인덱스 3: 미배송 주문 수 조회

**대상 쿼리:**
```sql
SELECT COUNT(*) FROM orders
WHERE status IN ('confirmed', 'shipped')
  AND created_at < NOW() - INTERVAL '3 days';
```

**인덱스:**
```sql
CREATE INDEX idx_orders_undelivered
    ON orders (status, created_at)
    WHERE status IN ('confirmed', 'shipped');
```

**설계 근거:**
- Partial Index(부분 인덱스)로 `confirmed`, `shipped` 상태만 인덱싱한다.
- 전체 테이블 대비 미배송 주문 비율이 낮으므로(일반적으로 전체의 5~15%) 인덱스 크기가 대폭 줄어든다.
- 인덱스 2(`idx_orders_status_created`)와 컬럼 구성이 동일하지만, Partial Index이므로 스캔 범위가 훨씬 작다.
- `COUNT(*)`만 필요하므로 Index Only Scan이 가능하다.

---

### 인덱스 4: 일별 매출 집계

**대상 쿼리:**
```sql
SELECT DATE(created_at), SUM(total_amount)
FROM orders
GROUP BY DATE(created_at);
```

**인덱스:**
```sql
CREATE INDEX idx_orders_created_amount
    ON orders (created_at, total_amount);
```

**설계 근거:**
- `created_at`과 `total_amount`를 함께 포함하여 Index Only Scan을 유도한다.
- 테이블 힙 접근 없이 인덱스만으로 집계가 가능해진다.
- 실무에서는 이 쿼리를 전체 테이블 대상으로 실행하지 않고 날짜 범위(`WHERE created_at BETWEEN ? AND ?`)를 걸게 되므로, `created_at` 선두 인덱스가 범위 제한에도 효과적이다.

**주의:** 전체 기간 집계 시에는 인덱스가 있어도 대량 스캔이 불가피하다. 아래 "운영 전략"의 Materialized View 활용을 권장한다.

---

### 인덱스 5: 고객별 총 주문 금액

**대상 쿼리:**
```sql
SELECT customer_id, SUM(total_amount)
FROM orders
GROUP BY customer_id;
```

**인덱스:**
```sql
CREATE INDEX idx_orders_customer_amount
    ON orders (customer_id, total_amount);
```

**설계 근거:**
- `customer_id`로 그룹핑하면서 `total_amount`를 포함하여 Index Only Scan을 유도한다.
- 특정 고객 조회(`WHERE customer_id = ?`) 시에는 해당 고객의 인덱스 엔트리만 스캔한다.
- 전체 고객 집계 시에는 Parallel Index Only Scan으로 처리 가능하다.

---

## 최종 인덱스 목록 요약

```sql
-- 1. 고객별 최근 주문 조회
CREATE INDEX idx_orders_customer_created
    ON orders (customer_id, created_at DESC);

-- 2. 상태 + 날짜 범위 조회
CREATE INDEX idx_orders_status_created
    ON orders (status, created_at);

-- 3. 미배송 주문 카운트 (Partial Index)
CREATE INDEX idx_orders_undelivered
    ON orders (status, created_at)
    WHERE status IN ('confirmed', 'shipped');

-- 4. 일별 매출 집계 (Index Only Scan)
CREATE INDEX idx_orders_created_amount
    ON orders (created_at, total_amount);

-- 5. 고객별 총 주문 금액 (Index Only Scan)
CREATE INDEX idx_orders_customer_amount
    ON orders (customer_id, total_amount);
```

| # | 인덱스명 | 컬럼 구성 | 유형 | 대상 쿼리 |
|---|---------|----------|------|----------|
| 1 | `idx_orders_customer_created` | `(customer_id, created_at DESC)` | B-tree | 쿼리 1 |
| 2 | `idx_orders_status_created` | `(status, created_at)` | B-tree | 쿼리 2 |
| 3 | `idx_orders_undelivered` | `(status, created_at)` WHERE partial | Partial B-tree | 쿼리 3 |
| 4 | `idx_orders_created_amount` | `(created_at, total_amount)` | B-tree | 쿼리 4 |
| 5 | `idx_orders_customer_amount` | `(customer_id, total_amount)` | B-tree | 쿼리 5 |

총 5개 인덱스. PK 포함 6개.

---

## 인덱스 크기 추정

월 1,000만 건 기준, 1년(1.2억 row) 운영 시 각 인덱스의 대략적 크기:

| 인덱스 | 엔트리당 크기(추정) | 1.2억 row 시 크기(추정) |
|--------|-------------------|----------------------|
| `idx_orders_customer_created` | ~24 bytes | ~4.5 GB |
| `idx_orders_status_created` | ~20 bytes | ~3.8 GB |
| `idx_orders_undelivered` | ~20 bytes | ~0.4~0.6 GB (부분) |
| `idx_orders_created_amount` | ~24 bytes | ~4.5 GB |
| `idx_orders_customer_amount` | ~24 bytes | ~4.5 GB |

Partial Index(`idx_orders_undelivered`)는 전체의 약 10% 수준으로 유지되어 크기가 매우 작다.

---

## 운영 전략

### 1. 테이블 파티셔닝

월 1,000만 건 규모에서는 시간 기반 파티셔닝이 필수적이다.

```sql
CREATE TABLE orders (
    id BIGSERIAL,
    customer_id BIGINT NOT NULL REFERENCES customers(id),
    status VARCHAR(20) NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    shipped_at TIMESTAMP,
    delivered_at TIMESTAMP,
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- 월별 파티션 생성
CREATE TABLE orders_2026_01 PARTITION OF orders
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE orders_2026_02 PARTITION OF orders
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
-- ...이하 반복 또는 pg_partman으로 자동 생성
```

**파티셔닝 효과:**
- 쿼리 2, 3, 4에서 `created_at` 조건으로 Partition Pruning이 작동하여 불필요한 파티션을 스캔하지 않는다.
- 각 파티션의 인덱스 크기가 작아져 인덱스 유지보수(VACUUM, REINDEX) 부담이 줄어든다.
- 오래된 데이터 아카이빙 시 파티션 단위로 DETACH하면 된다.

### 2. Materialized View (쿼리 4, 5 최적화)

전체 기간 집계 쿼리는 인덱스만으로 한계가 있다. 사전 집계 뷰를 활용한다.

```sql
-- 일별 매출 집계 뷰
CREATE MATERIALIZED VIEW mv_daily_sales AS
SELECT DATE(created_at) AS sale_date,
       COUNT(*) AS order_count,
       SUM(total_amount) AS daily_total
FROM orders
GROUP BY DATE(created_at);

CREATE UNIQUE INDEX idx_mv_daily_sales_date ON mv_daily_sales (sale_date);

-- 고객별 누적 주문 금액 뷰
CREATE MATERIALIZED VIEW mv_customer_totals AS
SELECT customer_id,
       COUNT(*) AS order_count,
       SUM(total_amount) AS total_spent
FROM orders
GROUP BY customer_id;

CREATE UNIQUE INDEX idx_mv_customer_totals ON mv_customer_totals (customer_id);

-- 주기적 갱신 (cron 또는 pg_cron)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_sales;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_customer_totals;
```

### 3. VACUUM/Autovacuum 튜닝

대용량 테이블에서는 기본 autovacuum 설정이 부족하다.

```sql
ALTER TABLE orders SET (
    autovacuum_vacuum_scale_factor = 0.01,      -- 기본 0.2 -> 0.01
    autovacuum_analyze_scale_factor = 0.005,     -- 기본 0.1 -> 0.005
    autovacuum_vacuum_cost_delay = 2             -- 기본 20ms -> 2ms (더 공격적)
);
```

### 4. 인덱스 생성 시 주의사항

운영 중 인덱스 생성 시 반드시 `CONCURRENTLY` 옵션을 사용한다.

```sql
CREATE INDEX CONCURRENTLY idx_orders_customer_created
    ON orders (customer_id, created_at DESC);
```

- `CONCURRENTLY` 없이 생성하면 테이블에 `ACCESS EXCLUSIVE` 락이 걸려 모든 읽기/쓰기가 차단된다.
- 파티션 테이블의 경우 각 파티션에 개별적으로 인덱스를 생성한 후 `ALTER INDEX ATTACH`로 부모에 연결한다.
