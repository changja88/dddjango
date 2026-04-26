# products 테이블 쿼리 최적화

## 현황 분석

- 테이블: `products` (200만 행)
- 현재 인덱스: PK(`id`)만 존재
- 3개 쿼리 모두 Seq Scan 발생 (3~5초 소요)
- 공통 패턴: `is_active = true` 필터가 모든 쿼리에 등장

## 리팩토링

### 쿼리 1: 카테고리별 활성 상품 목록

```sql
-- 쿼리
SELECT id, name, price
FROM products
WHERE category_id = 42
AND is_active = true
ORDER BY price ASC;
```

**[Before]**
인덱스 없음 -- Seq Scan, 200만 행 전체 스캔 후 정렬 (3초)

**[After]**
```sql
CREATE INDEX idx_products_category_active_price
ON products (category_id, is_active, price)
INCLUDE (name);
```

**[Reason]**

- **등호 조건을 범위 조건보다 앞에 배치**: `category_id = 42`(등호)와 `is_active = true`(등호)를 앞에, `price`(ORDER BY = 범위 스캔)를 뒤에 배치한다. B+Tree의 최좌선 접두사 규칙에 따라 (category_id, is_active)로 정확히 필터링한 후, price의 정렬 순서를 그대로 활용하여 별도 sort 연산을 제거한다.
- **커버링 인덱스**: SELECT 절에 필요한 `name`을 INCLUDE로 포함하여 테이블 룩업 없이 Index-Only Scan으로 처리한다. `id`는 PK이므로 인덱스 리프 노드에 자동 포함된다.
- **예상 효과**: Seq Scan + Sort --> Index-Only Scan (sort 제거). 3초 --> 수 ms.

---

### 쿼리 2: 재고 부족 알림

```sql
-- 쿼리
SELECT id, name, stock
FROM products
WHERE stock < 10
AND is_active = true;
```

**[Before]**
인덱스 없음 -- Seq Scan, 200만 행 전체 스캔 (5초)

**[After]**
```sql
CREATE INDEX idx_products_active_low_stock
ON products (is_active, stock)
INCLUDE (name)
WHERE is_active = true;
```

**[Reason]**

- **부분 인덱스 (Partial Index)**: `is_active = true`인 행만 인덱싱한다. 비활성 상품이 상당수라면 인덱스 크기가 크게 줄어든다. 작은 인덱스 = 적은 저장소, 빠른 스캔, 저렴한 유지보수.
- **등호 조건을 범위 조건보다 앞에 배치**: `is_active`(등호, 부분 인덱스 WHERE 절로 처리)가 먼저, `stock`(범위: `< 10`)이 뒤에 온다. 부분 인덱스의 WHERE 절이 `is_active = true`를 이미 필터링하므로, 인덱스 내부에서는 `stock` 컬럼의 B+Tree 탐색만으로 `stock < 10` 조건을 처리한다.
- **커버링 인덱스**: `name`을 INCLUDE로 포함하여 Index-Only Scan을 가능하게 한다.
- **예상 효과**: Seq Scan --> Index-Only Scan (부분 인덱스). 5초 --> 수 ms.

---

### 쿼리 3: 가격 범위 검색

```sql
-- 쿼리
SELECT id, name, price, category_id
FROM products
WHERE price BETWEEN 10000 AND 50000
AND is_active = true
AND category_id IN (1, 2, 3, 4, 5)
ORDER BY price;
```

**[Before]**
인덱스 없음 -- Seq Scan, 200만 행 전체 스캔 후 정렬 (4초)

**[After]**
```sql
CREATE INDEX idx_products_active_category_price
ON products (is_active, category_id, price)
INCLUDE (name)
WHERE is_active = true;
```

**[Reason]**

- **등호 조건을 범위 조건보다 앞에 배치**: `is_active = true`(등호)와 `category_id IN (...)`(등호, IN은 옵티마이저가 등호 목록으로 처리)를 앞에, `price BETWEEN`(범위)를 뒤에 배치한다. 이렇게 하면 인덱스에서 (is_active, category_id) 조합으로 정확히 필터링한 후, price 범위를 B+Tree의 sibling 포인터를 따라 효율적으로 스캔한다.
- **부분 인덱스**: `WHERE is_active = true` 조건으로 비활성 행을 인덱스에서 제외하여 크기를 줄인다.
- **커버링 인덱스**: `name`을 INCLUDE로 포함하여 Index-Only Scan을 가능하게 한다. `id`(PK), `category_id`, `price`는 인덱스 키에 이미 포함되어 있다.
- **ORDER BY price 최적화**: `category_id IN (1,2,3,4,5)`는 옵티마이저가 각 category_id별로 인덱스 스캔 후 merge하므로, price 순서가 인덱스에 의해 보장되어 별도 sort가 제거되거나 최소화된다.
- **예상 효과**: Seq Scan + Sort --> Index-Only Scan (Bitmap 또는 merge 방식). 4초 --> 수 ms.

---

## 최종 인덱스 목록

```sql
-- 쿼리 1: 카테고리별 활성 상품 목록
CREATE INDEX idx_products_category_active_price
ON products (category_id, is_active, price)
INCLUDE (name);

-- 쿼리 2: 재고 부족 알림
CREATE INDEX idx_products_active_low_stock
ON products (is_active, stock)
INCLUDE (name)
WHERE is_active = true;

-- 쿼리 3: 가격 범위 검색
CREATE INDEX idx_products_active_category_price
ON products (is_active, category_id, price)
INCLUDE (name)
WHERE is_active = true;
```

## 인덱스 통합 검토

| 인덱스 | 대상 쿼리 | 통합 가능 여부 |
|--------|----------|--------------|
| `idx_products_category_active_price` | 쿼리 1 | 쿼리 3과 키 구조가 유사하나, 쿼리 1은 부분 인덱스 없이 전체 행 대상이고 쿼리 3은 부분 인덱스이므로 별도 유지 |
| `idx_products_active_low_stock` | 쿼리 2 | stock 범위 조건은 다른 쿼리와 공유 불가, 단독 유지 |
| `idx_products_active_category_price` | 쿼리 3 | 쿼리 1과 병합 시 부분 인덱스를 포기해야 하므로 별도 유지가 효율적 |

3개 인덱스 모두 독립적 역할을 가지며, 쓰기 부하 증가분(INSERT/UPDATE/DELETE 시 3개 인덱스 갱신)은 200만 행 테이블의 읽기 성능 개선에 비해 수용 가능한 수준이다.

## 적용 후 검증

인덱스 생성 후 반드시 `EXPLAIN ANALYZE`로 실행 계획을 확인한다:

```sql
-- 각 쿼리에 대해 확인
EXPLAIN ANALYZE <쿼리>;
```

확인 포인트:
- Seq Scan이 Index Scan 또는 Index-Only Scan으로 변경되었는지
- 예상 행(rows)과 실제 행(actual rows)이 크게 차이나면 `ANALYZE products;` 실행
- Sort 노드가 제거되었는지 (쿼리 1, 3)
