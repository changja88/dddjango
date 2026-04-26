# SQL Query Performance Review

---

## Query 1: Orders + Customers JOIN

### 원본 쿼리

```sql
SELECT o.*, c.name, c.email
FROM orders o, customers c
WHERE o.customer_id = c.id
AND o.status = 'pending'
AND o.created_at > '2024-01-01'
ORDER BY o.created_at DESC;
```

### EXPLAIN 분석 결과 요약

| 항목 | 값 |
|---|---|
| 총 실행 시간 | 1,300.8 ms |
| orders 테이블 스캔 | Seq Scan (850.3 ms) |
| customers 테이블 스캔 | Seq Scan (25.5 ms) |
| 정렬 방식 | external merge Disk: 12MB |
| orders 필터 제거 행 수 | 1,962,000 |
| 결과 행 수 | 38,000 |

### 식별된 성능 문제

#### 1. orders 테이블 Full Table Scan (가장 큰 병목)

- orders 테이블에서 **Seq Scan**이 발생하고 있으며 전체 실행 시간의 약 65%를 차지한다.
- 총 2,000,000행(38,000 + 1,962,000) 중 38,000행만 반환한다. **선택도(selectivity)가 약 1.9%** 에 불과하므로 인덱스 스캔이 훨씬 효율적이다.
- `status`와 `created_at` 컬럼에 적절한 인덱스가 없다는 것을 의미한다.

**해결책:**

```sql
-- 복합 인덱스 생성 (status 선행, created_at 후행)
CREATE INDEX idx_orders_status_created_at ON orders (status, created_at DESC);
```

`status`를 선행 컬럼으로 두는 이유: 등호(=) 조건이 범위(<, >) 조건보다 선행해야 인덱스를 효율적으로 탈 수 있다. `created_at DESC`로 지정하면 ORDER BY 정렬도 인덱스에서 처리 가능하다.

#### 2. 디스크 기반 외부 정렬 (External Merge Sort)

- `Sort Method: external merge  Disk: 12MB` -- 정렬이 **메모리에서 처리되지 못하고 디스크로 넘어갔다**.
- `work_mem` 설정이 부족하거나 결과셋이 크기 때문이다.

**해결책:**

```sql
-- 세션 레벨에서 work_mem 증가 (쿼리 실행 전)
SET work_mem = '32MB';

-- 또는 postgresql.conf에서 전역 설정 조정
-- work_mem = '16MB'  (기본값 4MB에서 상향)
```

단, 위의 복합 인덱스를 생성하면 이미 정렬된 순서로 데이터를 읽기 때문에 별도 정렬 자체가 제거될 수 있다.

#### 3. customers 테이블 Seq Scan

- customers 테이블도 Full Scan을 하고 있다(50,000행). 비용은 상대적으로 작지만(25.5ms), `customers.id`에 PK/인덱스가 있다면 Hash Join 대신 Nested Loop + Index Scan이 가능하다.
- 다만 50,000행 전체를 해시로 올리는 비용(45ms)이 크지 않으므로 우선순위는 낮다. `customers.id`에 PK가 이미 있는지 확인할 것.

#### 4. 구식 조인 문법 (암묵적 조인)

- `FROM orders o, customers c WHERE o.customer_id = c.id` 형태는 ANSI-89 스타일이다.
- 성능에는 직접적 영향이 없지만, 명시적 JOIN을 사용하는 것이 가독성과 유지보수에 유리하다.

**개선된 쿼리:**

```sql
SELECT o.*, c.name, c.email
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.status = 'pending'
  AND o.created_at > '2024-01-01'
ORDER BY o.created_at DESC;
```

#### 5. SELECT o.* 사용

- `SELECT o.*`는 orders 테이블의 모든 컬럼을 가져온다. width=280으로 행당 데이터가 크며, 이것이 정렬 시 디스크 사용(12MB)의 원인 중 하나다.
- 실제 필요한 컬럼만 명시하면 I/O와 정렬 비용을 줄일 수 있다.

### Query 1 최종 개선안

```sql
-- 1) 인덱스 생성
CREATE INDEX idx_orders_status_created_at ON orders (status, created_at DESC);

-- 2) 필요 시 커버링 인덱스로 확장 (customer_id를 INCLUDE)
CREATE INDEX idx_orders_status_created_at_covering
ON orders (status, created_at DESC) INCLUDE (customer_id);

-- 3) 개선된 쿼리
SELECT o.id, o.customer_id, o.status, o.created_at, o.total_amount,
       c.name, c.email
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.status = 'pending'
  AND o.created_at > '2024-01-01'
ORDER BY o.created_at DESC;
```

**예상 개선 효과:** Seq Scan -> Index Scan 전환 + 정렬 제거로 실행 시간 1,300ms -> 50~100ms 수준으로 단축 가능.

---

## Query 2: N+1 문제

### 원본 코드

```python
orders = db.execute('SELECT * FROM orders WHERE status = %s', ('pending',))
for order in orders:
    customer = db.execute('SELECT * FROM customers WHERE id = %s', (order['customer_id'],))
    items = db.execute('SELECT * FROM order_items WHERE order_id = %s', (order['id'],))
```

### 식별된 성능 문제

#### 1. 전형적인 N+1 쿼리 문제 (치명적)

- pending 상태의 orders가 N건이면 총 쿼리 수는 **1 + N + N = 2N+1**회다.
- Query 1의 EXPLAIN 기준으로 pending orders가 약 38,000건이라면: **1 + 38,000 + 38,000 = 76,001회의 쿼리**가 실행된다.
- 각 쿼리의 네트워크 라운드트립(보통 0.5~2ms)만 합산해도 **38~152초**가 소요될 수 있다.

#### 2. 필터 조건 부재

- `created_at` 조건 없이 모든 pending orders를 가져온다. 데이터가 누적될수록 성능이 선형으로 악화된다.

#### 3. SELECT * 사용

- 세 쿼리 모두 전체 컬럼을 가져오고 있다. 불필요한 데이터 전송이 발생한다.

### Query 2 개선안

**방법 A: SQL JOIN으로 통합 (권장)**

```python
query = """
    SELECT o.id, o.status, o.created_at, o.total_amount,
           c.name, c.email,
           i.product_id, i.quantity, i.price
    FROM orders o
    JOIN customers c ON o.customer_id = c.id
    JOIN order_items i ON i.order_id = o.id
    WHERE o.status = %s
      AND o.created_at > %s
    ORDER BY o.id, i.id
"""
results = db.execute(query, ('pending', '2024-01-01'))
```

쿼리 1회로 모든 데이터를 가져온다. 단, order_items가 많으면 orders/customers 데이터가 중복 전송되는 단점이 있다.

**방법 B: IN 절 활용 (3회 쿼리)**

```python
# 1회: orders 조회
orders = db.execute(
    'SELECT id, customer_id, status, created_at FROM orders WHERE status = %s AND created_at > %s',
    ('pending', '2024-01-01')
)

order_ids = [o['id'] for o in orders]
customer_ids = list(set(o['customer_id'] for o in orders))

# 2회: customers 일괄 조회
customers = db.execute(
    'SELECT id, name, email FROM customers WHERE id = ANY(%s)',
    (customer_ids,)
)

# 3회: order_items 일괄 조회
items = db.execute(
    'SELECT order_id, product_id, quantity, price FROM order_items WHERE order_id = ANY(%s)',
    (order_ids,)
)

# 애플리케이션에서 매핑
customer_map = {c['id']: c for c in customers}
items_map = defaultdict(list)
for item in items:
    items_map[item['order_id']].append(item)
```

76,001회 -> 3회로 쿼리 수 감소. 데이터 중복 없이 깔끔하게 가져올 수 있다.

**방법 C: ORM 사용 시 Eager Loading**

```python
# SQLAlchemy 예시
orders = (
    session.query(Order)
    .options(
        joinedload(Order.customer),
        subqueryload(Order.items)
    )
    .filter(Order.status == 'pending')
    .filter(Order.created_at > '2024-01-01')
    .all()
)
```

---

## 종합 요약

| 구분 | 문제 | 심각도 | 핵심 해결책 |
|---|---|---|---|
| Query 1 | orders Seq Scan (200만 행 풀스캔) | 높음 | `(status, created_at DESC)` 복합 인덱스 생성 |
| Query 1 | 디스크 기반 외부 정렬 | 중간 | 인덱스로 정렬 제거 / work_mem 증가 |
| Query 1 | SELECT * 과다 컬럼 | 낮음 | 필요 컬럼만 명시 |
| Query 2 | N+1 문제 (76,001회 쿼리) | 치명적 | JOIN 통합 또는 IN 절 배치 조회 |
| Query 2 | 날짜 필터 부재 | 중간 | created_at 조건 추가 |
| 공통 | SELECT * 사용 | 낮음 | 필요 컬럼만 선택 |
