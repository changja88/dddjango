# 상품 카테고리 트리 설계

## 1. 요구사항 정리

| 항목 | 내용 |
|------|------|
| 최대 깊이 | 5단계 (대분류 > 중분류 > 소분류 > 세분류 > 최세분류) |
| 현재 규모 | ~1,000 노드 |
| 목표 규모 | ~5,000 노드 |
| 주요 쿼리 | 하위 트리 조회, 조상 조회 (breadcrumb) |
| 구조 변경 빈도 | 월 1-2회 (카테고리 이동) |
| 읽기:쓰기 비율 | 100:1 |

## 2. 패턴 비교 분석

### 2.1 비교표

| 패턴 | INSERT | 이동(부모 변경) | 하위 트리 조회 | 조상 조회 | 저장 공간 |
|------|--------|----------------|--------------|----------|----------|
| **Adjacency List** | O(1) | O(1) | 재귀 CTE 필요 | 재귀 CTE 필요 | 최소 |
| **Nested Set** | O(N) left/right 재작성 | O(N) | O(1) BETWEEN | O(1) | 최소 |
| **Materialized Path** | O(1) | O(K) 하위 경로 갱신 | O(1) LIKE 'path%' | O(1) 경로 분할 | 보통 |
| **Closure Table** | O(D) 조상 수만큼 | O(S) 서브트리 크기 | O(1) | O(1) | 높음 |

*N = 전체 노드 수, K = 이동 대상 서브트리 크기, D = 깊이, S = 서브트리 크기*

### 2.2 요구사항 대비 패턴별 적합도 평가

#### Adjacency List

- 하위 트리 조회: WITH RECURSIVE CTE가 필요하다. 5,000 노드, 깊이 5면 CTE가 최대 5회 재귀하므로 성능 자체는 허용 범위이지만, 쿼리 빈도가 매우 높아 매번 재귀를 실행하는 것은 비효율적이다.
- 조상 조회: 역시 CTE가 필요하다. breadcrumb은 페이지 로드마다 호출되는 고빈도 쿼리이므로 CTE 반복은 부담이다.
- 이동: parent_id 하나만 갱신하면 되므로 가장 간단하다.
- **결론: 읽기 100:1 환경에서 모든 읽기에 재귀가 필요한 것이 약점.**

#### Nested Set

- 하위 트리 조회: `WHERE lft BETWEEN parent.lft AND parent.rgt` 단일 쿼리로 처리. 매우 빠르다.
- 조상 조회: `WHERE lft < node.lft AND rgt > node.rgt` 단일 쿼리로 처리. 매우 빠르다.
- 이동: left/right 값을 전체적으로 재계산해야 한다. 5,000 노드일 때 이동 한 번에 수천 행 UPDATE가 발생한다. 월 1-2회라면 운영 부담이 크다.
- **결론: 읽기 성능은 최고이나 이동 비용이 지나치게 높다. 트리가 사실상 불변인 경우에만 적합.**

#### Materialized Path

- 하위 트리 조회: `WHERE path LIKE '/electronics/phones/%'` 단일 쿼리. path에 인덱스를 걸면 전방 일치(prefix match)로 B+Tree 인덱스를 활용한다.
- 조상 조회: path 문자열을 분할하면 모든 조상 ID를 즉시 얻을 수 있다. 애플리케이션 레벨에서 O(depth) 처리.
- 이동: 이동 대상 노드와 그 하위 노드의 path를 갱신해야 한다. 하위 노드 수만큼 UPDATE가 발생하지만, 5,000 노드에서 한 서브트리가 통상 수십~수백 개이므로 월 1-2회 수행은 충분히 수용 가능하다.
- 깊이 5단계, ID를 포함한 path 길이가 고정적이므로 path 컬럼 크기를 예측 가능하다.
- **결론: 읽기/쓰기 균형이 가장 우수. 이 요구사항에 최적.**

#### Closure Table

- 하위 트리 조회: `WHERE ancestor_id = X` 단일 쿼리. 매우 빠르다.
- 조상 조회: `WHERE descendant_id = X` 단일 쿼리. 매우 빠르다.
- 이동: 서브트리의 모든 closure 레코드를 삭제하고 재삽입해야 한다. Materialized Path보다 복잡하다.
- 저장 공간: 5,000 노드, 평균 깊이 3이면 closure 행이 약 15,000~20,000 건. 관리 가능하지만 불필요한 오버헤드이다.
- **결론: 읽기 성능은 우수하나, 이 규모와 깊이에서는 Materialized Path 대비 복잡도와 저장 비용만 높아지고 실질적 이점이 없다.**

### 2.3 최종 선택: Materialized Path

| 평가 기준 | Materialized Path 적합도 |
|-----------|-------------------------|
| 하위 트리 조회 (고빈도) | LIKE prefix 단일 쿼리, 인덱스 활용 가능 |
| 조상 조회 (고빈도, breadcrumb) | path 분할로 즉시 획득, DB 쿼리 불필요 |
| 카테고리 이동 (월 1-2회) | 서브트리 path 갱신, 허용 가능한 비용 |
| 규모 (1K -> 5K) | 추가 테이블 없이 단일 컬럼으로 관리 |
| 구현 복잡도 | 직관적, CTE나 별도 테이블 불필요 |

---

## 3. 물리 스키마

```sql
CREATE TABLE categories (
    id          BIGINT       PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    parent_id   BIGINT       REFERENCES categories(id),
    path        VARCHAR(500) NOT NULL,
    depth       SMALLINT     NOT NULL,
    sort_order  INTEGER      NOT NULL DEFAULT 0,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### path 설계

- 형식: `/{id}/{id}/{id}/.../{자기자신id}/`
- 예시: 대분류(1) > 중분류(5) > 소분류(23) 이면 path = `/1/5/23/`
- 루트 노드: path = `/1/`, depth = 1
- 최대 길이: 5단계 x (최대 4자리 ID + 슬래시) + 앞뒤 슬래시 = 약 30자. 5,000개 이후 ID가 5자리여도 40자 이내. VARCHAR(500)은 충분한 여유.

### parent_id를 함께 두는 이유

Materialized Path가 주 패턴이지만 parent_id도 유지한다. 이유:

1. 직속 자식 조회(`WHERE parent_id = X`)가 path LIKE보다 빠르고 정확하다.
2. FK 제약으로 참조 무결성을 보장한다.
3. path가 손상되었을 때 parent_id로 복구할 수 있다.

---

## 4. 인덱스 설계

```sql
CREATE INDEX idx_categories_path ON categories (path varchar_pattern_ops);

CREATE INDEX idx_categories_parent_id ON categories (parent_id);

CREATE INDEX idx_categories_depth ON categories (depth);
```

### 인덱스 설계 근거

| 인덱스 | 대상 쿼리 | 근거 |
|--------|----------|------|
| `idx_categories_path` | 하위 트리 조회 (`WHERE path LIKE '/1/5/%'`) | B+Tree에서 LIKE prefix 검색을 활용하려면 `varchar_pattern_ops` 연산자 클래스가 필요하다. 전방 일치 패턴을 범위 스캔으로 변환한다. |
| `idx_categories_parent_id` | 직속 자식 조회 (`WHERE parent_id = X`) | FK 컬럼이자 빈번한 등호 조건. |
| `idx_categories_depth` | 특정 단계 카테고리 목록 (`WHERE depth = 2`) | 관리 화면에서 특정 레벨만 필터링할 때 사용. |

---

## 5. 주요 쿼리

### 5.1 특정 카테고리의 모든 하위 카테고리 조회

```sql
SELECT id, name, path, depth
FROM categories
WHERE path LIKE '/1/5/%'
  AND is_active = TRUE
ORDER BY path, sort_order;
```

카테고리 id=5의 path가 `/1/5/`일 때, 그 하위 노드는 모두 `/1/5/`로 시작한다. `idx_categories_path` 인덱스가 prefix 범위 스캔을 수행한다.

### 5.2 특정 카테고리의 모든 조상 조회 (breadcrumb)

```sql
-- 애플리케이션에서 path를 분할하여 조상 ID를 추출
-- path = '/1/5/23/' -> 조상 ID 목록: [1, 5, 23]

SELECT id, name, depth
FROM categories
WHERE id IN (1, 5, 23)
ORDER BY depth;
```

path 문자열을 분할하면 재귀 쿼리 없이 한 번의 `IN` 쿼리로 breadcrumb 전체를 가져온다. PK 인덱스로 직접 조회하므로 매우 빠르다.

### 5.3 카테고리 이동 (부모 변경)

```sql
-- 카테고리 id=23 (현재 path='/1/5/23/')을 id=8 (path='/2/8/') 아래로 이동

BEGIN;

-- 1. 대상 노드와 모든 하위 노드의 path를 갱신
UPDATE categories
SET path = REPLACE(path, '/1/5/', '/2/8/'),
    depth = depth + (2 - 2),  -- 새 부모 깊이 - 기존 부모 깊이
    updated_at = CURRENT_TIMESTAMP
WHERE path LIKE '/1/5/23/%'
   OR path = '/1/5/23/';

-- 2. 대상 노드의 parent_id 갱신
UPDATE categories
SET parent_id = 8,
    updated_at = CURRENT_TIMESTAMP
WHERE id = 23;

COMMIT;
```

월 1-2회 발생하며, 서브트리 크기가 통상 수십~수백 건이므로 운영에 문제가 없다.

---

## 6. 규모 확장 시 고려 사항

| 시점 | 대응 |
|------|------|
| 5,000 노드 도달 | 현재 설계로 충분. path 인덱스의 prefix 스캔은 노드 수에 비례하지 않고 서브트리 크기에 비례한다. |
| 10,000+ 노드 | 하위 트리 조회 결과가 수천 건이면 페이지네이션을 추가한다. |
| breadcrumb 초고빈도 | path 파싱 결과를 애플리케이션 캐시(Redis 등)에 저장한다. 카테고리 변경 빈도가 극히 낮으므로 캐시 무효화 부담이 거의 없다. |
| 카테고리 이동이 주 단위로 증가 | 현재 설계로 문제없다. 일 단위로 증가하면 그때 Closure Table 전환을 검토한다. |
