아래는 PostgreSQL에서 월별 매출을 집계하는 기본 SQL 예시입니다.

```sql
SELECT
    date_trunc('month', order_date)::date AS month,
    SUM(amount) AS total_sales
FROM orders
GROUP BY date_trunc('month', order_date)
ORDER BY month;
```

예시 컬럼 가정:

- `orders`: 주문 테이블
- `order_date`: 주문일
- `amount`: 매출 금액

월을 `YYYY-MM` 형식으로 보고 싶다면:

```sql
SELECT
    to_char(date_trunc('month', order_date), 'YYYY-MM') AS month,
    SUM(amount) AS total_sales
FROM orders
GROUP BY date_trunc('month', order_date)
ORDER BY date_trunc('month', order_date);
```

취소 주문 제외 같은 조건이 있으면 보통 이렇게 붙입니다.

```sql
SELECT
    to_char(date_trunc('month', order_date), 'YYYY-MM') AS month,
    SUM(amount) AS total_sales
FROM orders
WHERE status <> 'cancelled'
GROUP BY date_trunc('month', order_date)
ORDER BY date_trunc('month', order_date);
```