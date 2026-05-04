아래처럼 작성하면 됩니다. `orders` 테이블에 `created_at`, `amount`, `status`가 있다고 가정했습니다.

```sql
SELECT
  date_trunc('month', created_at)::date AS month,
  SUM(amount) AS total_sales
FROM orders
WHERE status = 'paid'
GROUP BY date_trunc('month', created_at)
ORDER BY month;
```

결과 예시:

```text
month       | total_sales
------------+------------
2026-01-01  | 1250000
2026-02-01  | 980000
2026-03-01  | 1430000
```

월을 `YYYY-MM` 문자열로 보고 싶으면:

```sql
SELECT
  to_char(date_trunc('month', created_at), 'YYYY-MM') AS month,
  SUM(amount) AS total_sales
FROM orders
WHERE status = 'paid'
GROUP BY date_trunc('month', created_at)
ORDER BY date_trunc('month', created_at);
```