# Orders 테이블 인덱스 설계

## 테이블 분석

월 1,000만 건 적재되는 대용량 주문 테이블이다. 연간 약 1.2억 건이므로 인덱스 설계가 성능에 직접적인 영향을 미친다.

**기존 인덱스**: `id`에 PRIMARY KEY (B+Tree 자동 생성)

**컬럼 카디널리티 분석**:

| 컬럼 | 카디널리티 | 비고 |
|------|-----------|------|
| `id` | 매우 높음 | PK, 유니크 |
| `customer_id` | 높음 | 고객 수에 비례 |
| `status` | 매우 낮음 (5종) | 단독 인덱싱 비효율, 복합 인덱스의 등호 조건 선행 컬럼으로 활용 |
| `total_amount` | 높음 | 집계 대상 |
| `created_at` | 높음 | 시간 기반 범위 조건, 정렬 조건 |

---

## 쿼리별 인덱스 설계

### Q1. 특정 고객의 최근 주문 10건

```sql
SELECT * FROM orders
WHERE customer_id = ?
ORDER BY created_at DESC
LIMIT 10;
```

**인덱스**:

```sql
CREATE INDEX idx_orders_customer_created
    ON orders (customer_id, created_at DESC);
```

**설계 근거**:
- `customer_id`가 등호(=) 조건이므로 선행 컬럼에 배치한다.
- `created_at DESC`를 후행 컬럼으로 두어 해당 고객의 주문이 이미 시간 역순으로 정렬된 상태가 된다.
- B+Tree의 리프 노드가 sibling 포인터로 연결되어 있으므로, `customer_id` 일치 후 리프 노드를 순차 탐색하여 상위 10건만 반환한다.
- `LIMIT 10`이므로 인덱스 스캔 후 즉시 종료되어 매우 빠르다.

---

### Q2. 상태별 주문 목록 (날짜 범위)

```sql
SELECT * FROM orders
WHERE status = ?
AND created_at BETWEEN ? AND ?;
```

**인덱스**:

```sql
CREATE INDEX idx_orders_status_created
    ON orders (status, created_at);
```

**설계 근거**:
- `status`가 등호(=) 조건, `created_at`이 범위(BETWEEN) 조건이다. 등호 조건 컬럼을 범위 조건 컬럼보다 앞에 배치하는 원칙을 따른다.
- 만약 `(created_at, status)` 순서로 만들면 `created_at` 범위 스캔 이후 `status` 필터에 인덱스를 활용할 수 없다.
- `status`로 먼저 좁히면(5종 중 1종 = 약 20%), 그 안에서 `created_at` 범위를 B+Tree sibling 포인터로 효율적으로 스캔한다.

---

### Q3. 미배송 주문 수

```sql
SELECT COUNT(*) FROM orders
WHERE status IN ('confirmed', 'shipped')
AND created_at < NOW() - INTERVAL '3 days';
```

**인덱스**:

```sql
CREATE INDEX idx_orders_undelivered
    ON orders (status, created_at)
    WHERE status IN ('confirmed', 'shipped');
```

**설계 근거**:
- 부분 인덱스(Partial Index)를 사용한다. 전체 주문 중 'confirmed'와 'shipped' 상태는 일부분이다. 대부분의 주문은 'delivered'이므로 전체 테이블을 인덱싱하는 것은 낭비다.
- 부분 인덱스는 저장 공간이 작고, 스캔 범위가 좁으며, INSERT/UPDATE 시 인덱스 유지 비용도 낮다.
- `COUNT(*)`만 반환하므로 `status`와 `created_at`만 인덱스에 있으면 Index-Only Scan이 가능하다.
- Q2의 `idx_orders_status_created`로도 이 쿼리를 서비스할 수 있다. 부분 인덱스가 더 효율적이지만, 인덱스 수를 줄이고 싶다면 Q2 인덱스로 대체 가능하다. 운영 후 EXPLAIN ANALYZE로 판단한다.

---

### Q4. 일별 매출 집계

```sql
SELECT DATE(created_at), SUM(total_amount)
FROM orders
GROUP BY DATE(created_at);
```

**인덱스**:

```sql
CREATE INDEX idx_orders_created_amount
    ON orders (created_at, total_amount);
```

**설계 근거**:
- `created_at`으로 정렬된 인덱스가 있으면 `GROUP BY DATE(created_at)`에서 정렬 비용을 절감할 수 있다.
- `total_amount`를 후행 컬럼에 포함하면 커버링 인덱스(Index-Only Scan)가 되어 힙 테이블 접근 없이 집계가 가능하다.
- 단, `DATE(created_at)` 함수 적용 시 옵티마이저에 따라 인덱스 활용이 제한될 수 있다. 이 경우 expression index(`CREATE INDEX ... ON orders (DATE(created_at), total_amount)`)를 고려한다.
- 이 쿼리가 전체 테이블을 대상으로 실행된다면 Seq Scan이 더 효율적일 수 있다. 날짜 범위 조건(`WHERE created_at BETWEEN ? AND ?`)이 추가되는 실 사용 패턴이라면 인덱스 효과가 극대화된다.

---

### Q5. 고객별 총 주문 금액

```sql
SELECT customer_id, SUM(total_amount)
FROM orders
GROUP BY customer_id;
```

**인덱스**:

```sql
CREATE INDEX idx_orders_customer_amount
    ON orders (customer_id, total_amount);
```

**설계 근거**:
- `customer_id`로 정렬된 인덱스가 있으면 `GROUP BY customer_id`에서 정렬 비용을 절감한다.
- `total_amount`를 포함하여 커버링 인덱스를 구성하면 Index-Only Scan으로 힙 테이블 접근을 제거한다.
- Q1의 `idx_orders_customer_created`는 `total_amount`를 포함하지 않으므로 이 쿼리에는 별도 인덱스가 필요하다.
- Q4와 마찬가지로, 전체 테이블 대상 집계라면 Seq Scan이 선택될 수 있다. 특정 고객 집합(`WHERE customer_id IN (...)`)에 대한 집계라면 인덱스 효과가 크다.

---

## 최종 인덱스 요약

```sql
-- PK (자동 생성)
-- PRIMARY KEY (id)

-- Q1: 특정 고객의 최근 주문
CREATE INDEX idx_orders_customer_created
    ON orders (customer_id, created_at DESC);

-- Q2: 상태별 주문 목록 (날짜 범위)
CREATE INDEX idx_orders_status_created
    ON orders (status, created_at);

-- Q3: 미배송 주문 수 (부분 인덱스)
CREATE INDEX idx_orders_undelivered
    ON orders (status, created_at)
    WHERE status IN ('confirmed', 'shipped');

-- Q4: 일별 매출 집계 (커버링 인덱스)
CREATE INDEX idx_orders_created_amount
    ON orders (created_at, total_amount);

-- Q5: 고객별 총 주문 금액 (커버링 인덱스)
CREATE INDEX idx_orders_customer_amount
    ON orders (customer_id, total_amount);
```

총 5개 인덱스 + PK = 6개.

---

## 인덱스 수와 쓰기 비용 트레이드오프

월 1,000만 건이 INSERT되는 테이블이므로, 인덱스가 많을수록 쓰기 비용이 증가한다. 모든 INSERT/UPDATE/DELETE는 관련된 모든 인덱스를 갱신해야 한다.

**인덱스 병합 검토**:

| 병합 후보 | 판단 |
|-----------|------|
| Q2 `(status, created_at)` + Q3 부분 인덱스 | Q3 부분 인덱스는 Q2 인덱스의 부분집합이다. Q3 쿼리의 실행 빈도가 낮다면 Q2 인덱스만으로 커버하고 Q3을 제거할 수 있다. 반대로 Q3이 모니터링 대시보드 등에서 매우 빈번하게 실행된다면 부분 인덱스를 유지한다. |
| Q1 `(customer_id, created_at DESC)` + Q5 `(customer_id, total_amount)` | 선행 컬럼은 같지만 후행 컬럼의 목적이 다르다 (정렬 vs 커버링). 하나로 병합할 수 없다. |

**운영 후 최적화 전략**:

1. 위 5개 인덱스를 모두 생성한 후, `pg_stat_user_indexes` 등을 통해 인덱스 사용률을 모니터링한다.
2. 사용 빈도가 낮은 인덱스는 제거하여 쓰기 비용을 줄인다.
3. Q4, Q5는 전체 테이블 집계이므로 실제 실행 계획에서 Index-Only Scan이 선택되는지 EXPLAIN ANALYZE로 확인한다. Seq Scan이 선택된다면 해당 인덱스의 존재 가치를 재평가한다.

---

## 추가 고려사항: 파티셔닝

월 1,000만 건 규모에서는 `created_at` 기준 Range Partitioning(월별 또는 분기별)을 검토할 수 있다. 파티셔닝은 인덱스 설계와 직접적으로 관련된다:

- 각 파티션에 로컬 인덱스가 생성되어 인덱스 크기가 작아진다.
- 날짜 범위 조건 쿼리(Q2, Q3, Q4)에서 파티션 프루닝으로 스캔 대상이 줄어든다.
- 오래된 데이터 아카이빙 시 파티션 단위로 DROP/DETACH가 가능하다.

파티셔닝은 인덱스 설계 이후의 단계이며, 인덱스만으로 성능이 충분하지 않을 때 도입한다(최적화 순서: slow query fix -> index -> cache -> denormalize).
