# 느린 쿼리 최적화 결과

## 현재 상태 분석

- 테이블: `products` (200만 행)
- 기존 인덱스: PK (`id`) 단일 인덱스
- 모든 쿼리가 Seq Scan 발생 (전체 테이블 풀 스캔)

## 권장 인덱스

### 인덱스 1 -- 쿼리 1용 (카테고리별 활성 상품 목록)

```sql
CREATE INDEX idx_products_category_active_price
ON products (category_id, is_active, price);
```

**대상 쿼리:**
```sql
SELECT id, name, price
FROM products
WHERE category_id = 42
AND is_active = true
ORDER BY price ASC;
```

**설계 근거:**
- `category_id`를 선두 컬럼으로 배치: 등호 조건(`= 42`)이므로 B-Tree에서 정확한 범위를 즉시 좁힘
- `is_active`를 두 번째로 배치: 등호 조건(`= true`)으로 추가 필터링
- `price`를 마지막으로 배치: `ORDER BY price ASC`에 대해 별도 정렬(Sort) 단계 제거. 인덱스 자체가 이미 정렬된 상태이므로 Index Scan만으로 정렬 완료
- **예상 실행 계획**: Seq Scan + Sort -> Index Scan (정렬 제거)
- **예상 시간**: 3초 -> 10~50ms

---

### 인덱스 2 -- 쿼리 2용 (재고 부족 알림)

```sql
CREATE INDEX idx_products_stock_active
ON products (is_active, stock)
WHERE is_active = true AND stock < 100;
```

**대상 쿼리:**
```sql
SELECT id, name, stock
FROM products
WHERE stock < 10
AND is_active = true;
```

**설계 근거:**
- **Partial Index** 사용: `is_active = true AND stock < 100` 조건으로 인덱스 크기를 대폭 축소. 200만 행 중 재고 100 미만인 활성 상품만 인덱싱하므로 인덱스 크기가 매우 작음
- 임계값을 `stock < 100`으로 여유 있게 설정: 현재 쿼리는 `stock < 10`이지만, 향후 재고 기준이 변경(예: 20, 50)되더라도 인덱스 재생성 불필요
- `is_active`를 선두에 배치하고 `stock`을 후속으로: Partial Index의 WHERE 절이 `is_active = true`를 이미 필터링하므로, 실질적으로 `stock` 범위 스캔만 수행
- **예상 실행 계획**: Seq Scan -> Index Scan (Partial Index, 극소량 스캔)
- **예상 시간**: 5초 -> 5~20ms

---

### 인덱스 3 -- 쿼리 3용 (가격 범위 검색)

```sql
CREATE INDEX idx_products_active_category_price
ON products (is_active, category_id, price);
```

**대상 쿼리:**
```sql
SELECT id, name, price, category_id
FROM products
WHERE price BETWEEN 10000 AND 50000
AND is_active = true
AND category_id IN (1, 2, 3, 4, 5)
ORDER BY price;
```

**설계 근거:**
- `is_active`를 선두에 배치: 등호 조건(`= true`)으로 전체 범위를 먼저 좁힘
- `category_id`를 두 번째로 배치: `IN (1, 2, 3, 4, 5)`는 옵티마이저가 내부적으로 5개의 등호 조건으로 분해. 각 category_id에 대해 B-Tree에서 정확한 위치를 찾음
- `price`를 마지막으로 배치: 각 `(is_active, category_id)` 조합 내에서 `price BETWEEN` 범위 스캔 수행. 또한 `ORDER BY price`와 결합하여 정렬 비용 감소
- **예상 실행 계획**: Seq Scan + Sort -> Bitmap Index Scan 또는 Index Scan (category별 5회). PostgreSQL 옵티마이저가 5개 category에 대해 BitmapOr로 병합 후 정렬하거나, Merge Append로 처리
- **예상 시간**: 4초 -> 20~80ms

---

## 인덱스 통합 가능성 검토

인덱스 1과 인덱스 3의 통합 여부를 검토한다.

| 항목 | 인덱스 1 `(category_id, is_active, price)` | 인덱스 3 `(is_active, category_id, price)` |
|---|---|---|
| 쿼리 1 지원 | 최적 (등호 -> 등호 -> 정렬) | 가능하지만 차선 |
| 쿼리 3 지원 | 차선 (IN 조건이 선두가 아님) | 최적 (등호 -> IN -> 범위+정렬) |

**결론: 통합하지 않는다.** 컬럼 순서가 다르기 때문에 하나로 합치면 한쪽 쿼리가 반드시 차선 경로를 탄다. 200만 행 규모에서 인덱스 2개의 저장 비용(각 수십 MB)은 쿼리 성능 저하 대비 무시할 수 있다.

---

## 최종 적용 스크립트

```sql
-- 운영 환경에서는 CONCURRENTLY 옵션으로 락 없이 생성
-- (동시 트랜잭션 차단 방지)

-- 쿼리 1: 카테고리별 활성 상품 + 가격순 정렬
CREATE INDEX CONCURRENTLY idx_products_category_active_price
ON products (category_id, is_active, price);

-- 쿼리 2: 재고 부족 알림 (Partial Index)
CREATE INDEX CONCURRENTLY idx_products_stock_active
ON products (is_active, stock)
WHERE is_active = true AND stock < 100;

-- 쿼리 3: 가격 범위 + 다중 카테고리 검색
CREATE INDEX CONCURRENTLY idx_products_active_category_price
ON products (is_active, category_id, price);
```

## 추가 고려사항

### name 컬럼의 Covering Index 적용 여부

세 쿼리 모두 `SELECT` 절에 `name`을 포함한다. 현재 설계에서는 인덱스에서 조건을 필터링한 후 테이블 힙(Heap)으로 돌아가 `name`을 가져오는 Heap Fetch가 발생한다. `INCLUDE (name)`으로 Covering Index를 만들면 Index-Only Scan이 가능하지만, 다음 이유로 기본 권장에서는 제외한다.

- `name`은 `VARCHAR(200)`이므로 인덱스 크기가 2~3배 증가
- 200만 행 기준으로 인덱스가 수백 MB에 달할 수 있음
- 조건 필터링 후 실제 반환 행 수가 적다면 Heap Fetch 비용은 미미

만약 쿼리 결과 행 수가 수만 건 이상으로 많고 Heap Fetch가 병목이라면 아래처럼 변경을 고려한다.

```sql
-- 예시: 인덱스 1에 name을 INCLUDE로 추가
CREATE INDEX idx_products_category_active_price_covering
ON products (category_id, is_active, price)
INCLUDE (name);
```

### VACUUM/ANALYZE

인덱스 생성 후 반드시 통계를 갱신한다.

```sql
ANALYZE products;
```

### 검증 방법

각 쿼리 앞에 `EXPLAIN (ANALYZE, BUFFERS)`를 붙여 실행 계획이 기대대로 변경되었는지 확인한다.

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, name, price
FROM products
WHERE category_id = 42
AND is_active = true
ORDER BY price ASC;
-- 기대: Index Scan using idx_products_category_active_price
-- Sort 단계 없음
```
