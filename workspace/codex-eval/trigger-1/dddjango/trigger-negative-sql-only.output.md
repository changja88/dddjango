**주요 내용**

가장 기본적인 PostgreSQL 월별 매출 집계는 `date_trunc('month', ...)`를 쓰면 됩니다.

```sql
SELECT
    date_trunc('month', paid_at)::date AS sales_month,
    COUNT(*) AS order_count,
    SUM(total_amount) AS total_sales
FROM orders
WHERE status = 'paid'
GROUP BY 1
ORDER BY 1;
```

기간 조건을 넣는다면 인덱스를 잘 타도록 반열린 구간을 권장합니다.

```sql
SELECT
    date_trunc('month', paid_at)::date AS sales_month,
    COUNT(*) AS order_count,
    SUM(total_amount) AS total_sales
FROM orders
WHERE status = 'paid'
  AND paid_at >= TIMESTAMPTZ '2025-01-01 00:00:00+09'
  AND paid_at <  TIMESTAMPTZ '2026-01-01 00:00:00+09'
GROUP BY 1
ORDER BY 1;
```

`paid_at`이 `timestamptz`이고 한국 시간 기준 월별 집계가 필요하면 이렇게 명시합니다.

```sql
SELECT
    date_trunc('month', paid_at AT TIME ZONE 'Asia/Seoul')::date AS sales_month,
    COUNT(*) AS order_count,
    SUM(total_amount) AS total_sales
FROM orders
WHERE status = 'paid'
GROUP BY 1
ORDER BY 1;
```

해당 쿼리가 자주 실행된다면 다음 인덱스를 고려할 수 있습니다.

```sql
CREATE INDEX idx_orders_paid_paid_at
ON orders (paid_at)
WHERE status = 'paid';
```

---
> **관련 스킬 참조:**
> - 쿼리 성능 최적화와 인덱스 설계 → **architecture-db** 스킬