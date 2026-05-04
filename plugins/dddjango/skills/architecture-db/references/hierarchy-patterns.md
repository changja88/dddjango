# 계층 구조 패턴 레퍼런스

조직도, 카테고리 트리, 댓글 스레드 등 계층 구조를 RDB에 표현하는 4가지 패턴.

---

## 패턴 비교

| 패턴 | INSERT | 이동 | 하위 트리 조회 | 조상 조회 | 저장 공간 |
|------|--------|------|--------------|---------|----------|
| **Adjacency List** | 쉬움 | 쉬움 | 재귀/CTE 필요 | 재귀/CTE 필요 | 최소 |
| **Nested Set** | 비쌈 (left/right 재작성) | 비쌈 | 단일 쿼리 (BETWEEN) | 단일 쿼리 | 최소 |
| **Materialized Path** | 쉬움 | 보통 (경로 갱신) | LIKE 'path%' | 경로 분할 | 보통 |
| **Closure Table** | 보통 (모든 경로 삽입) | 보통 | 단일 쿼리 | 단일 쿼리 | 높음 |

---

## Adjacency List (인접 리스트)

가장 단순한 패턴. 각 행에 parent_id를 저장한다.

```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    parent_id INTEGER REFERENCES categories(id)
);

-- 하위 트리 조회: WITH RECURSIVE (CTE)
WITH RECURSIVE subtree AS (
    SELECT id, name, parent_id FROM categories WHERE id = 1
    UNION ALL
    SELECT c.id, c.name, c.parent_id
    FROM categories c JOIN subtree s ON c.parent_id = s.id
)
SELECT * FROM subtree;
```

---

## Closure Table (폐쇄 테이블)

모든 조상-자손 쌍을 별도 테이블에 저장한다. 가장 유연하며 복잡한 계층 쿼리에 적합.

```sql
CREATE TABLE node_closure (
    ancestor_id INTEGER REFERENCES nodes(id),
    descendant_id INTEGER REFERENCES nodes(id),
    depth INTEGER,
    PRIMARY KEY (ancestor_id, descendant_id)
);

-- 트리 A -> B -> C일 때 저장되는 행:
-- (A, A, 0), (A, B, 1), (A, C, 2), (B, B, 0), (B, C, 1), (C, C, 0)

-- A의 모든 자손 조회 (재귀 불필요)
SELECT descendant_id FROM node_closure WHERE ancestor_id = 'A';

-- C의 모든 조상 조회
SELECT ancestor_id FROM node_closure WHERE descendant_id = 'C' AND depth > 0;
```

---

## 선택 가이드

| 상황 | 권장 패턴 |
|------|----------|
| 작은/단순 트리, 빈번한 갱신 | Adjacency List |
| 깊은 계층, 복잡한 조상/자손 쿼리 | Closure Table |
| 읽기 중심, 안정적 트리 | Nested Set |
| 단순 트리, 보통 수준 갱신 | Materialized Path |
