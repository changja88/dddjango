# Query Performance Review

---

## Query 1: orders + customers JOIN

### EXPLAIN ANALYZE 분석

| 항목 | 값 | 판정 |
|------|------|------|
| 총 실행 시간 | 1,300.8 ms | 느림 |
| orders Seq Scan 시간 | 850.3 ms (전체의 65%) | 병목 지점 |
| 스캔 행 / 반환 행 | 2,000,000 / 38,000 (98% 폐기) | 매우 비효율적 |
| Sort Method | external merge Disk: 12MB | 메모리 부족으로 디스크 정렬 |

### 발견 사항

```
[Seq Scan on Large Table] — orders 테이블에서 200만 행을 순차 스캔하여
38,000행만 반환한다. 전체 행의 98%를 필터로 폐기하고 있으며, 이것이 전체
실행 시간의 65%를 차지하는 핵심 병목이다.
```

EXPLAIN 결과에서 `Rows Removed by Filter: 1,962,000`이 이를 명확히 보여준다. `status = 'pending'` (등호 조건)과 `created_at > '2024-01-01'` (범위 조건)에 대한 인덱스가 없어 Full Table Scan이 발생하고 있다.

```
[Disk Sort] — Sort Method가 "external merge Disk: 12MB"로 표시된다.
work_mem이 부족하여 38,000행의 정렬이 메모리가 아닌 디스크에서 수행되고 있다.
디스크 I/O로 인해 정렬 단계에서만 약 270ms(1250.3 - 980.5)가 소요된다.
```

```
[SELECT * 사용] — orders와 customers 모두 SELECT *로 전체 컬럼을 가져온다.
불필요한 컬럼까지 읽으면 I/O가 증가하고, 커버링 인덱스를 활용할 수 없다.
필요한 컬럼만 명시적으로 지정해야 한다.
```

```
[구식 JOIN 구문] — FROM orders o, customers c WHERE ... 형태의 암시적 조인을
사용하고 있다. 명시적 JOIN 구문(INNER JOIN ... ON)을 사용해야 가독성과
유지보수성이 향상되며, 실수로 cross join이 발생하는 것을 방지할 수 있다.
```

### 권장 인덱스

복합 인덱스에서 등호(=) 조건 컬럼을 범위 조건 컬럼보다 앞에 배치하는 원칙을 적용한다.

```sql
-- 등호 컬럼(status) 먼저, 범위 컬럼(created_at) 뒤에 배치
CREATE INDEX idx_orders_status_created ON orders (status, created_at);
```

이 인덱스가 적용되면:
- `status = 'pending'`으로 등호 매칭 후, `created_at > '2024-01-01'`을 범위 스캔
- Seq Scan이 Index Scan 또는 Bitmap Heap Scan으로 전환
- 200만 행 전체 스캔 대신 38,000행에 직접 접근
- 인덱스가 `created_at`으로 이미 정렬되어 있으므로 별도 Sort 단계가 제거되거나 대폭 경감

### 개선된 쿼리

```sql
SELECT o.id, o.customer_id, o.status, o.created_at, o.total_amount,
       c.name, c.email
FROM orders o
INNER JOIN customers c ON o.customer_id = c.id
WHERE o.status = 'pending'
  AND o.created_at > '2024-01-01'
ORDER BY o.created_at DESC;
```

변경 내용:
1. `SELECT *` 제거 -- 필요한 컬럼만 명시
2. 암시적 조인을 명시적 `INNER JOIN ... ON`으로 변경
3. 인덱스 `idx_orders_status_created`와 함께 사용 시, Seq Scan 제거 및 디스크 정렬 해소 기대

---

## Query 2: N+1 문제

### 발견 사항

```
[N+1 Query Pattern] — 전형적인 1 + 2N 쿼리 패턴이다. pending 주문이
1,000건이면 총 2,001개의 쿼리가 실행된다:
  - 1회: SELECT * FROM orders WHERE status = 'pending'
  - N회: SELECT * FROM customers WHERE id = ?  (주문마다 1회)
  - N회: SELECT * FROM order_items WHERE order_id = ?  (주문마다 1회)
각 쿼리의 네트워크 왕복 시간과 파싱 비용이 누적되어 심각한 성능 저하를
초래한다.
```

```
[SELECT * 사용] — 세 쿼리 모두 SELECT *를 사용하여 불필요한 컬럼까지
가져오고 있다. 필요한 컬럼만 명시해야 한다.
```

### 해결 방법: JOIN으로 통합

N+1 패턴을 단일 JOIN 쿼리 또는 최소한의 배치 쿼리(IN 절)로 변환해야 한다.

**방법 A: 단일 JOIN 쿼리 (권장)**

```python
query = """
    SELECT o.id AS order_id, o.status, o.created_at,
           c.id AS customer_id, c.name, c.email,
           oi.id AS item_id, oi.product_name, oi.quantity, oi.price
    FROM orders o
    INNER JOIN customers c ON o.customer_id = c.id
    INNER JOIN order_items oi ON o.id = oi.order_id
    WHERE o.status = %s
"""
results = db.execute(query, ('pending',))
```

하나의 쿼리로 모든 데이터를 가져온다. 다만 주문-아이템 간 1:N 관계로 인해 주문 데이터가 아이템 수만큼 중복되므로, 애플리케이션에서 그룹핑 처리가 필요하다.

**방법 B: 배치 쿼리 (2-3회)**

```python
# 1회: 주문 조회
orders = db.execute(
    'SELECT id, customer_id, status, created_at FROM orders WHERE status = %s',
    ('pending',)
)

customer_ids = list(set(o['customer_id'] for o in orders))
order_ids = [o['id'] for o in orders]

# 2회: 고객 일괄 조회
customers = db.execute(
    'SELECT id, name, email FROM customers WHERE id IN %s',
    (tuple(customer_ids),)
)

# 3회: 주문 아이템 일괄 조회
items = db.execute(
    'SELECT order_id, product_name, quantity, price FROM order_items WHERE order_id IN %s',
    (tuple(order_ids),)
)
```

총 3회 쿼리로 고정. 주문이 1,000건이든 10,000건이든 쿼리 수가 변하지 않는다.

### 관련 인덱스 확인

N+1 해소와 별개로, 배치 쿼리 방식을 택하더라도 다음 인덱스가 존재하는지 확인해야 한다:

```sql
-- orders.customer_id에 FK 인덱스 (JOIN 및 IN 절 성능)
CREATE INDEX idx_orders_customer_id ON orders (customer_id);

-- order_items.order_id에 FK 인덱스 (JOIN 및 IN 절 성능)
CREATE INDEX idx_order_items_order_id ON order_items (order_id);

-- orders.status에 인덱스 (pending 필터링)
-- Query 1의 복합 인덱스가 이미 있다면 별도 생성 불필요
CREATE INDEX idx_orders_status ON orders (status);
```

---

## Review Checklist

| 항목 | 결과 |
|------|------|
| Missing or inappropriate primary keys | 해당 없음 (스키마 미제공) |
| Normalization violations (1NF-3NF) | 해당 없음 (스키마 미제공) |
| Missing indexes on frequently queried columns or JOIN keys | **문제 발견** -- orders 테이블에 (status, created_at) 복합 인덱스 누락, FK 인덱스 미확인 |
| Composite index with wrong column ordering | 해당 사항 있음 -- 권장 인덱스에서 등호 컬럼 우선 배치 적용 |
| N+1 query patterns in the access layer | **문제 발견** -- Query 2에서 1 + 2N 패턴 확인 |
| Wrong isolation level for the use case | 해당 없음 (트랜잭션 컨텍스트 미제공) |
| Hierarchical data without appropriate pattern | 해당 없음 |
| Polymorphic associations without referential integrity | 해당 없음 |
| Premature denormalization | 해당 없음 |
| Missing foreign key constraints or cascading rules | 해당 없음 (스키마 미제공으로 확인 불가) |

---

## 요약

| 문제 | 심각도 | 핵심 원인 | 해결책 |
|------|--------|-----------|--------|
| Query 1 Seq Scan (200만 행) | 높음 | 인덱스 부재 | `(status, created_at)` 복합 인덱스 추가 |
| Query 1 Disk Sort | 중간 | work_mem 부족 + 인덱스 부재 | 인덱스 추가로 정렬 제거, 필요시 work_mem 조정 |
| Query 1 SELECT * | 낮음 | 불필요한 컬럼 조회 | 필요 컬럼만 명시 |
| Query 2 N+1 (1 + 2N 쿼리) | 높음 | 루프 내 개별 쿼리 | JOIN 또는 IN 절 배치 쿼리로 전환 |
| Query 2 SELECT * | 낮음 | 불필요한 컬럼 조회 | 필요 컬럼만 명시 |
