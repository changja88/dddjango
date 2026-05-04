PostgreSQL에서 월별 매출 집계는 보통 `date_trunc('month', ...)`를 사용합니다.

```sql
SELECT
  date_trunc('month', ordered_at)::date AS month,
  SUM(total_amount) AS monthly_sales
FROM orders
WHERE status = 'paid'
GROUP BY date_trunc('month', ordered_at)
ORDER BY month;
```

예시 가정:

- 테이블: `orders`
- 주문일 컬럼: `ordered_at`
- 매출 금액 컬럼: `total_amount`
- 결제 완료 상태만 집계: `status = 'paid'`

월을 `YYYY-MM` 문자열로 보고 싶다면:

```sql
SELECT
  to_char(date_trunc('month', ordered_at), 'YYYY-MM') AS month,
  SUM(total_amount) AS monthly_sales
FROM orders
WHERE status = 'paid'
GROUP BY date_trunc('month', ordered_at)
ORDER BY date_trunc('month', ordered_at);
```