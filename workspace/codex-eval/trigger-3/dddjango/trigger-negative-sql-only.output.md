PostgreSQL 기준 월별 매출 집계 SQL 예시입니다.

```sql
SELECT
  date_trunc('month', ordered_at)::date AS sales_month,
  COUNT(*) AS order_count,
  SUM(total_amount) AS total_sales
FROM orders
WHERE ordered_at >= DATE '2025-01-01'
  AND ordered_at <  DATE '2026-01-01'
GROUP BY date_trunc('month', ordered_at)
ORDER BY sales_month;
```

예상 테이블 구조:

```sql
orders(
  id,
  ordered_at timestamp,
  total_amount numeric
)
```

취소/환불 주문을 제외해야 한다면:

```sql
SELECT
  date_trunc('month', ordered_at)::date AS sales_month,
  COUNT(*) AS order_count,
  SUM(total_amount) AS total_sales
FROM orders
WHERE ordered_at >= DATE '2025-01-01'
  AND ordered_at <  DATE '2026-01-01'
  AND status = 'paid'
GROUP BY date_trunc('month', ordered_at)
ORDER BY sales_month;
```

월 표시를 `YYYY-MM` 문자열로 보고 싶으면:

```sql
SELECT
  to_char(date_trunc('month', ordered_at), 'YYYY-MM') AS sales_month,
  SUM(total_amount) AS total_sales
FROM orders
GROUP BY date_trunc('month', ordered_at)
ORDER BY date_trunc('month', ordered_at);
```