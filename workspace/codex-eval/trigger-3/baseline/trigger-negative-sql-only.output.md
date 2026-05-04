PostgreSQL에서 월별 매출 집계는 보통 `date_trunc('month', ...)`를 씁니다.

```sql
SELECT
  date_trunc('month', ordered_at)::date AS sales_month,
  SUM(total_amount) AS monthly_sales
FROM orders
WHERE status = 'paid'
GROUP BY date_trunc('month', ordered_at)
ORDER BY sales_month;
```

예시 컬럼 기준:

- `orders`: 주문 테이블
- `ordered_at`: 주문 일시
- `total_amount`: 주문 금액
- `status = 'paid'`: 결제 완료 주문만 집계

월을 `YYYY-MM` 문자열로 보고 싶으면:

```sql
SELECT
  to_char(date_trunc('month', ordered_at), 'YYYY-MM') AS sales_month,
  SUM(total_amount) AS monthly_sales
FROM orders
WHERE status = 'paid'
GROUP BY date_trunc('month', ordered_at)
ORDER BY date_trunc('month', ordered_at);
```