주문 목록 화면이 느려졌어. PostgreSQL에서 아래 쿼리를 자주 실행해.

```sql
SELECT id, customer_id, status, created_at
FROM orders
WHERE tenant_id = 42
  AND status = 'PAID'
  AND created_at >= '2026-01-01'
ORDER BY created_at DESC
LIMIT 50;
```

현재 `EXPLAIN ANALYZE` 요약은 다음과 같아.

```text
Seq Scan on orders  (cost=0.00..185000.00 rows=1200 width=48)
  (actual time=12.3..1480.5 rows=742000 loops=1)
  Filter: ((tenant_id = 42) AND (status = 'PAID') AND (created_at >= '2026-01-01'))
  Rows Removed by Filter: 8900000
Planning Time: 0.9 ms
Execution Time: 1485.2 ms
```

어떤 순서로 원인을 판단하고 index 또는 query 변경을 검토할지 알려줘. 운영 중인 큰 테이블이라 index 생성과 rollback/forward-fix 위험도 같이 다뤄줘. 단, 캐시나 역정규화부터 시작하는 답은 원하지 않아.
