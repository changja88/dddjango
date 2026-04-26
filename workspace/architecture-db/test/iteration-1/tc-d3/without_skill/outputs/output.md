# DB 스키마 계층 구조 및 상속 패턴 분석

## 1. 카테고리: Nested Set 모델의 부적합

### 문제
Nested Set은 **읽기 최적화** 모델이다. 하위 카테고리 조회(`WHERE lft BETWEEN parent.lft AND parent.rgt`)는 빠르지만, **삽입/이동 시 lft, rgt 값을 대량으로 재계산**해야 한다.

- 일 10회 이상 추가/이동이 발생하는 상황에서 Nested Set은 비효율적
- 노드 삽입 시 해당 노드 우측의 모든 lft/rgt 값을 +2 갱신해야 함 (최악의 경우 전체 행 UPDATE)
- 이동은 더 심각: 삭제 후 재삽입에 준하는 연산 필요
- 동시성 문제: 재계산 중 테이블 락 또는 정합성 깨짐 위험

### 권장
50개 카테고리, 최대 3단계라면 다음이 더 적합하다:

| 모델 | 쓰기 | 읽기 | 적합 상황 |
|------|------|------|-----------|
| **Adjacency List** (`parent_id`) | O(1) | 재귀 CTE 필요 | 쓰기 빈번, 깊이 얕음 |
| **Materialized Path** (`path = '1/3/7'`) | O(1) | LIKE 쿼리 | 쓰기 빈번, 읽기도 합리적 |
| Nested Set (현재) | O(n) | O(1) | 거의 변경 없는 대규모 트리 |

3단계, 50개 규모에서 쓰기가 빈번하므로 **Adjacency List + 재귀 CTE** 또는 **Materialized Path**가 적합하다.

### 추가 누락 사항
- `lft`, `rgt`에 **인덱스가 없음** (조회 성능 저하)
- `depth` 또는 `parent_id` 컬럼 없음 (단계별 조회 불가)
- `UNIQUE` 제약 없음 (lft, rgt 정합성 보장 수단 부재)

---

## 2. 콘텐츠: Concrete Table Inheritance의 근본적 한계

### 문제
`articles`와 `videos`가 완전히 독립된 테이블이면서 동일한 컬럼(`title`, `author_id`, `published_at`, `view_count`)을 중복 보유한다.

**"전체 콘텐츠 최신순 조회"가 자주 사용되는 쿼리인데, Concrete Table Inheritance에서는 이것이 구조적으로 어렵다:**

```sql
-- 현재 구조에서 전체 콘텐츠 조회 방법
SELECT id, title, published_at, 'article' AS type FROM articles
UNION ALL
SELECT id, title, published_at, 'video' AS type FROM videos
ORDER BY published_at DESC;
```

- `UNION ALL`은 **인덱스를 활용한 정렬이 불가능** (각 테이블 결과를 합친 후 재정렬)
- 콘텐츠 타입이 추가될 때마다 UNION 절 추가 필요 (확장성 없음)
- `id`가 테이블별로 독립이므로 **콘텐츠를 범용적으로 참조할 수 없음** (article id=1과 video id=1이 공존)
- 공통 컬럼 변경 시 모든 테이블을 동시에 수정해야 함

### 권장: Single Table Inheritance 또는 Shared PK 패턴

**방법 A: Single Table Inheritance** (콘텐츠 타입이 적고 공통 컬럼이 많을 때)

```sql
CREATE TABLE contents (
    id SERIAL PRIMARY KEY,
    type VARCHAR(20) NOT NULL,  -- 'article', 'video'
    title VARCHAR(300),
    body TEXT,                   -- article 전용
    url TEXT,                    -- video 전용
    duration INTEGER,            -- video 전용
    author_id INTEGER,
    published_at TIMESTAMP,
    view_count INTEGER DEFAULT 0
);
CREATE INDEX idx_contents_published ON contents(published_at DESC);
CREATE INDEX idx_contents_type ON contents(type);
```

**방법 B: Class Table Inheritance (Shared PK)** (타입별 고유 컬럼이 많을 때)

```sql
CREATE TABLE contents (
    id SERIAL PRIMARY KEY,
    type VARCHAR(20) NOT NULL,
    title VARCHAR(300),
    author_id INTEGER,
    published_at TIMESTAMP,
    view_count INTEGER DEFAULT 0
);

CREATE TABLE article_details (
    content_id INTEGER PRIMARY KEY REFERENCES contents(id),
    body TEXT
);

CREATE TABLE video_details (
    content_id INTEGER PRIMARY KEY REFERENCES contents(id),
    url TEXT,
    duration INTEGER
);
```

현재 스키마의 경우 고유 컬럼이 1-2개뿐이므로 **방법 A(Single Table)가 가장 단순하고 효율적**이다.

---

## 3. 댓글: 다형성 참조(Polymorphic FK)의 안티패턴

### 문제
```sql
article_id INTEGER REFERENCES articles(id),
video_id INTEGER REFERENCES videos(id),
```

이 설계는 **Polymorphic Association** 안티패턴이다:

- 한 댓글이 `article_id`와 `video_id`를 **동시에 가질 수 있음** (무결성 위반 가능)
- 둘 다 `NULL`일 수도 있음 (고아 댓글)
- 콘텐츠 타입 추가 시 `comments` 테이블에 FK 컬럼을 계속 추가해야 함
- `CHECK (num_nonnulls(article_id, video_id) = 1)` 같은 제약이 없어 **DB 레벨 무결성 보장 불가**
- 특정 콘텐츠의 댓글 조회 시 어떤 FK 컬럼을 사용할지 애플리케이션이 분기해야 함

### 권장
콘텐츠를 통합하면(위 2번 참조) 자연스럽게 해결된다:

```sql
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    content_id INTEGER NOT NULL REFERENCES contents(id),
    body TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_comments_content ON comments(content_id);
CREATE INDEX idx_comments_created ON comments(created_at DESC);
```

만약 Concrete Table을 유지해야 한다면 최소한:

```sql
-- CHECK 제약으로 정확히 하나만 NOT NULL 보장
ALTER TABLE comments ADD CONSTRAINT chk_single_parent
    CHECK (num_nonnulls(article_id, video_id) = 1);
```

---

## 4. 카테고리-콘텐츠 간 관계 누락

스키마에 카테고리와 콘텐츠를 연결하는 관계가 **아예 없다**. "특정 카테고리의 하위 카테고리 조회"는 가능하지만, **해당 카테고리에 속한 콘텐츠 조회**가 불가능하다.

```sql
-- 필요한 연결 테이블 (다대다)
CREATE TABLE content_categories (
    content_id INTEGER NOT NULL REFERENCES contents(id),
    category_id INTEGER NOT NULL REFERENCES categories(id),
    PRIMARY KEY (content_id, category_id)
);
CREATE INDEX idx_cc_category ON content_categories(category_id);
```

---

## 5. 기타 누락 사항

| 항목 | 문제 |
|------|------|
| `author_id` FK 없음 | `REFERENCES users(id)` 누락, 무결성 보장 불가 |
| `NOT NULL` 부재 | `title`, `body`, `published_at` 등 필수 컬럼에 NOT NULL 없음 |
| `created_at` 불일치 | `comments`에만 존재, `articles`/`videos`에는 없음 (감사 추적 불가) |
| `updated_at` 없음 | 수정 이력 추적 불가 |
| `published_at` 인덱스 없음 | 최신순 조회가 주요 쿼리인데 인덱스 미설정 |

---

## 요약: 문제 심각도

| 우선순위 | 문제 | 영향 |
|----------|------|------|
| **HIGH** | Concrete Table에서 전체 콘텐츠 통합 조회 비효율 | 주요 쿼리 성능 저하, 확장성 없음 |
| **HIGH** | 댓글의 다형성 FK 안티패턴 | 데이터 무결성 위반 가능 |
| **HIGH** | 카테고리-콘텐츠 관계 누락 | 핵심 기능 불가 |
| **MEDIUM** | Nested Set의 쓰기 빈번 환경 부적합 | 카테고리 변경 시 성능 저하, 락 경합 |
| **LOW** | 인덱스, NOT NULL, FK 등 누락 | 점진적 성능/무결성 문제 |
