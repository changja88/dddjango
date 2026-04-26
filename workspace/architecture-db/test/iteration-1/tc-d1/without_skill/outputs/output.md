# 상품 카테고리 트리 설계

## 1. 요구사항 정리

| 항목 | 값 |
|---|---|
| 최대 깊이 | 5단계 |
| 현재 규모 | ~1,000 노드 |
| 예상 최대 규모 | ~5,000 노드 |
| 주요 읽기 쿼리 | 하위 카테고리 전체 조회, 조상 경로 조회(breadcrumb) |
| 쓰기 빈도 | 카테고리 이동 월 1-2회 |
| 읽기:쓰기 비율 | 100:1 |

## 2. 후보 패턴 비교

### 2.1 Adjacency List (인접 리스트)

```sql
CREATE TABLE category (
    id         BIGINT PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    parent_id  BIGINT REFERENCES category(id),
    depth      SMALLINT NOT NULL DEFAULT 0
);
CREATE INDEX idx_category_parent ON category(parent_id);
```

**하위 전체 조회**: 재귀 CTE 필요 (PostgreSQL `WITH RECURSIVE`, MySQL 8+ `WITH RECURSIVE`)
```sql
WITH RECURSIVE descendants AS (
    SELECT id, name, parent_id, depth FROM category WHERE id = :target
    UNION ALL
    SELECT c.id, c.name, c.parent_id, c.depth
    FROM category c JOIN descendants d ON c.parent_id = d.id
)
SELECT * FROM descendants;
```

**조상 조회**: 역방향 재귀 CTE
```sql
WITH RECURSIVE ancestors AS (
    SELECT id, name, parent_id, depth FROM category WHERE id = :target
    UNION ALL
    SELECT c.id, c.name, c.parent_id, c.depth
    FROM category c JOIN ancestors a ON c.id = a.parent_id
)
SELECT * FROM ancestors ORDER BY depth;
```

| 평가 항목 | 점수 | 설명 |
|---|---|---|
| 하위 전체 조회 | **C** | 재귀 CTE, 깊이 5 = 최대 5번 조인. 5,000건에선 수용 가능하나 최적은 아님 |
| 조상 조회 | **B** | 재귀 CTE지만 최대 5번으로 제한되어 빠름 |
| 카테고리 이동 | **A** | `UPDATE category SET parent_id = :new WHERE id = :target` 단일 행 갱신 |
| 구조 단순성 | **A** | 가장 직관적, FK 무결성 보장 |
| 확장성 (5K) | **B** | 재귀 CTE 비용이 선형 증가 |

---

### 2.2 Materialized Path (경로 구체화)

```sql
CREATE TABLE category (
    id    BIGINT PRIMARY KEY,
    name  VARCHAR(255) NOT NULL,
    path  VARCHAR(500) NOT NULL,  -- 예: '/1/5/23/102/'
    depth SMALLINT NOT NULL DEFAULT 0
);
CREATE INDEX idx_category_path ON category(path);            -- LIKE 'prefix%' 지원
CREATE INDEX idx_category_path_gin ON category USING gin(path);  -- PostgreSQL 선택사항
```

**하위 전체 조회**: prefix 매칭
```sql
SELECT * FROM category WHERE path LIKE CONCAT(:target_path, '%');
```

**조상 조회**: 애플리케이션에서 path를 파싱하여 IN 쿼리
```sql
-- path = '/1/5/23/102/' -> ancestor ids = [1, 5, 23]
SELECT * FROM category WHERE id IN (1, 5, 23) ORDER BY depth;
```

**카테고리 이동**: 자신 + 모든 하위 노드의 path 일괄 갱신
```sql
UPDATE category
SET path = REPLACE(path, :old_prefix, :new_prefix)
WHERE path LIKE CONCAT(:old_prefix, '%');
```

| 평가 항목 | 점수 | 설명 |
|---|---|---|
| 하위 전체 조회 | **A** | 단일 인덱스 스캔, 매우 빠름 |
| 조상 조회 | **A** | path 파싱 후 IN 쿼리, 매우 빠름 |
| 카테고리 이동 | **B** | 자신 + 하위 모두 갱신 필요. 월 1-2회이므로 수용 가능 |
| 구조 단순성 | **B** | path 문자열 관리 필요, FK 무결성 없음 |
| 확장성 (5K) | **A** | LIKE prefix 검색은 B-tree 인덱스 활용 가능, 5K 여유 |

---

### 2.3 Nested Set

```sql
CREATE TABLE category (
    id    BIGINT PRIMARY KEY,
    name  VARCHAR(255) NOT NULL,
    lft   INT NOT NULL,
    rgt   INT NOT NULL,
    depth SMALLINT NOT NULL DEFAULT 0
);
CREATE INDEX idx_category_lft_rgt ON category(lft, rgt);
```

**하위 전체 조회**:
```sql
SELECT * FROM category WHERE lft BETWEEN :parent_lft AND :parent_rgt;
```

**조상 조회**:
```sql
SELECT * FROM category WHERE lft < :target_lft AND rgt > :target_rgt ORDER BY depth;
```

**카테고리 이동**: 이동 대상 서브트리의 lft/rgt 재계산 + 기존 위치/새 위치의 gap 조정 -> 대규모 UPDATE

| 평가 항목 | 점수 | 설명 |
|---|---|---|
| 하위 전체 조회 | **A** | 단일 range scan |
| 조상 조회 | **A** | 단일 range scan |
| 카테고리 이동 | **D** | 전체 트리의 lft/rgt 재계산, 최악의 경우 전체 행 갱신 |
| 구조 단순성 | **C** | lft/rgt 개념이 비직관적, 디버깅 어려움 |
| 확장성 (5K) | **B** | 읽기는 우수하나 쓰기 시 잠금 범위가 넓음 |

---

### 2.4 Closure Table (클로저 테이블)

```sql
CREATE TABLE category (
    id    BIGINT PRIMARY KEY,
    name  VARCHAR(255) NOT NULL
);

CREATE TABLE category_closure (
    ancestor_id   BIGINT NOT NULL REFERENCES category(id),
    descendant_id BIGINT NOT NULL REFERENCES category(id),
    depth         SMALLINT NOT NULL DEFAULT 0,
    PRIMARY KEY (ancestor_id, descendant_id)
);
CREATE INDEX idx_closure_desc ON category_closure(descendant_id, depth);
CREATE INDEX idx_closure_anc  ON category_closure(ancestor_id, depth);
```

**하위 전체 조회**:
```sql
SELECT c.* FROM category c
JOIN category_closure cc ON c.id = cc.descendant_id
WHERE cc.ancestor_id = :target;
```

**조상 조회**:
```sql
SELECT c.* FROM category c
JOIN category_closure cc ON c.id = cc.ancestor_id
WHERE cc.descendant_id = :target
ORDER BY cc.depth;
```

**카테고리 이동**: 클로저 행 삭제 + 재삽입
```sql
-- 1) 이동 대상 서브트리의 기존 조상 관계 삭제 (자기 자신 관계 제외)
DELETE FROM category_closure
WHERE descendant_id IN (
    SELECT descendant_id FROM category_closure WHERE ancestor_id = :target
)
AND ancestor_id IN (
    SELECT ancestor_id FROM category_closure WHERE descendant_id = :target AND ancestor_id != :target
);

-- 2) 새 부모의 조상들과 서브트리의 모든 노드에 대해 새 관계 삽입
INSERT INTO category_closure (ancestor_id, descendant_id, depth)
SELECT a.ancestor_id, d.descendant_id, a.depth + d.depth + 1
FROM category_closure a
CROSS JOIN category_closure d
WHERE a.descendant_id = :new_parent_id
AND d.ancestor_id = :target;
```

| 평가 항목 | 점수 | 설명 |
|---|---|---|
| 하위 전체 조회 | **A** | 단순 JOIN, 인덱스 활용 |
| 조상 조회 | **A** | 단순 JOIN, 인덱스 활용 |
| 카테고리 이동 | **C** | DELETE + INSERT 필요, Nested Set보다는 낫지만 복잡 |
| 구조 단순성 | **B** | 별도 테이블 관리, 관계 행 수가 많음 |
| 확장성 (5K) | **B** | 클로저 행 수 = 노드 x 평균깊이. 5,000 x 3(평균) = ~15,000행. 관리 가능 |

---

## 3. 종합 비교 매트릭스

| 패턴 | 하위 조회 | 조상 조회 | 이동 | 단순성 | 5K 확장 | **종합** |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Adjacency List | C | B | A | A | B | B |
| **Materialized Path** | **A** | **A** | **B** | **B** | **A** | **A** |
| Nested Set | A | A | D | C | B | C+ |
| Closure Table | A | A | C | B | B | A- |

## 4. 최적 선택: Materialized Path + Adjacency List 하이브리드

### 선택 근거

1. **읽기 최적화가 핵심** -- 100:1 비율에서 읽기 성능이 지배적이며, Materialized Path의 하위 조회(`LIKE prefix%`)와 조상 조회(path 파싱 + IN)가 가장 효율적이다.
2. **쓰기 비용이 수용 가능** -- 카테고리 이동이 월 1-2회로 극히 드물다. path 일괄 갱신 비용이 사실상 무시할 수 있다.
3. **5,000건에서도 여유** -- Closure Table은 별도 테이블에 ~15,000행이 필요하지만, Materialized Path는 추가 테이블 없이 컬럼 하나로 해결된다.
4. **parent_id 유지로 무결성 보강** -- Materialized Path 단독의 약점(FK 무결성 없음)을 parent_id로 보완한다.

### 최종 스키마

```sql
CREATE TABLE category (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    parent_id  BIGINT REFERENCES category(id) ON DELETE RESTRICT,
    path       VARCHAR(500) NOT NULL,   -- '/1/5/23/102/'
    depth      SMALLINT NOT NULL DEFAULT 0,
    sort_order INT NOT NULL DEFAULT 0,
    is_active  BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 핵심 인덱스
CREATE INDEX idx_category_parent   ON category(parent_id);
CREATE INDEX idx_category_path     ON category(path varchar_pattern_ops);  -- prefix LIKE 지원 (PostgreSQL)
CREATE INDEX idx_category_depth    ON category(depth);
CREATE INDEX idx_category_active   ON category(is_active) WHERE is_active = TRUE;

-- 유니크 제약: 같은 부모 아래 이름 중복 방지
CREATE UNIQUE INDEX idx_category_parent_name ON category(parent_id, name);
```

### 주요 쿼리 구현

#### (1) 특정 카테고리의 모든 하위 카테고리 조회
```sql
-- category id=23, path='/1/5/23/' 일 때
SELECT * FROM category
WHERE path LIKE '/1/5/23/%'
  AND is_active = TRUE
ORDER BY depth, sort_order;
```
- 인덱스 스캔 1회, O(결과 수)

#### (2) 빵 부스러기(조상) 조회
```sql
-- path='/1/5/23/102/' -> 조상 id 배열: [1, 5, 23]
SELECT * FROM category
WHERE id IN (1, 5, 23, 102)
ORDER BY depth;
```
- PK 인덱스로 즉시 조회, 최대 5행

#### (3) 직접 자식만 조회
```sql
SELECT * FROM category
WHERE parent_id = :id AND is_active = TRUE
ORDER BY sort_order;
```

#### (4) 카테고리 이동 (부모 변경)
```sql
BEGIN;

-- 1. 이동 대상의 새 path 계산
-- 기존: path='/1/5/23/', 새 부모 path='/1/10/', 새 path='/1/10/23/'

-- 2. 대상 + 모든 하위 노드의 path 일괄 갱신
UPDATE category
SET path = REPLACE(path, '/1/5/23/', '/1/10/23/'),
    depth = depth + (:new_depth - :old_depth),
    updated_at = NOW()
WHERE path LIKE '/1/5/23/%';

-- 3. 대상 노드의 parent_id 갱신
UPDATE category
SET parent_id = :new_parent_id,
    updated_at = NOW()
WHERE id = 23;

COMMIT;
```
- 월 1-2회 발생, 서브트리 크기만큼 갱신. 5,000건 기준 최악에도 수천 행 갱신이 수 ms 이내

### 애플리케이션 레이어 유틸리티

```python
class CategoryPath:
    """Materialized Path 유틸리티"""

    @staticmethod
    def build_path(parent_path: str, category_id: int) -> str:
        """부모 path에 자신의 id를 추가하여 path 생성"""
        return f"{parent_path}{category_id}/"

    @staticmethod
    def parse_ancestor_ids(path: str) -> list[int]:
        """path에서 조상 id 목록 추출 (breadcrumb용)"""
        parts = path.strip("/").split("/")
        return [int(p) for p in parts if p]

    @staticmethod
    def get_parent_path(path: str) -> str:
        """자신을 제외한 부모의 path 반환"""
        parts = path.strip("/").split("/")
        if len(parts) <= 1:
            return "/"
        return "/" + "/".join(parts[:-1]) + "/"

    @staticmethod
    def validate_depth(path: str, max_depth: int = 5) -> bool:
        """깊이 제한 검증"""
        depth = len(path.strip("/").split("/"))
        return depth <= max_depth
```

### 캐싱 전략

읽기:쓰기 = 100:1 이므로 캐싱 효과가 극대화된다.

```
[요청] --> [Application Cache] --> [DB]
              |
              +-- 키: "cat:children:{id}"    TTL: 1시간    (하위 카테고리)
              +-- 키: "cat:ancestors:{id}"   TTL: 1시간    (breadcrumb)
              +-- 키: "cat:tree:full"        TTL: 30분     (전체 트리, 5K면 메모리 적재 가능)
```

- 카테고리 변경 시 관련 캐시 키를 무효화
- 전체 트리를 메모리에 올려도 5,000건 x ~200바이트 = ~1MB로 무시할 수준

### 데이터 정합성 보호

```sql
-- 트리거: path와 parent_id 정합성 검증
CREATE OR REPLACE FUNCTION check_category_path() RETURNS TRIGGER AS $$
BEGIN
    -- depth 제한 검사
    IF NEW.depth > 5 THEN
        RAISE EXCEPTION 'Category depth cannot exceed 5 (current: %)', NEW.depth;
    END IF;

    -- 순환 참조 방지: 자기 자신을 조상으로 가질 수 없음
    IF NEW.parent_id IS NOT NULL AND NEW.path LIKE '%/' || NEW.parent_id || '/%' THEN
        IF POSITION('/' || NEW.id || '/' IN NEW.path) <
           POSITION('/' || NEW.parent_id || '/' IN NEW.path) THEN
            RAISE EXCEPTION 'Circular reference detected';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_category_path_check
    BEFORE INSERT OR UPDATE ON category
    FOR EACH ROW EXECUTE FUNCTION check_category_path();
```

## 5. 결론

| 결정 | 내용 |
|---|---|
| **선택 패턴** | Materialized Path + Adjacency List 하이브리드 |
| **핵심 이유** | 읽기 100:1 비율에서 LIKE prefix 검색이 가장 빠르고, 월 1-2회 이동 비용은 무시 가능 |
| **기각: Nested Set** | 읽기는 동등하나 이동 비용이 과도하고 구조가 비직관적 |
| **기각: Closure Table** | 읽기 우수하나 별도 테이블 관리 오버헤드가 5K 규모에서 불필요 |
| **기각: 단순 Adjacency List** | 재귀 CTE 비용이 읽기 우선 요구사항에 부적합 |
