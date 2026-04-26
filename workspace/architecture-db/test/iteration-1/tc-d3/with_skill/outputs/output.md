# 스키마 리뷰: 계층 구조와 상속 패턴

## Review Checklist

- [x] Missing or inappropriate primary keys
- [x] Normalization violations (1NF-3NF) without documented justification
- [x] Missing indexes on frequently queried columns or JOIN keys
- [x] Composite index with wrong column ordering
- [x] N+1 query patterns in the access layer
- [x] Wrong isolation level for the use case
- [x] Hierarchical data stored without an appropriate pattern
- [x] Polymorphic associations without referential integrity strategy
- [x] Premature denormalization (before measuring performance)
- [x] Missing foreign key constraints or cascading rules

---

## 핵심 문제 요약

이 스키마에는 두 가지 구조적 문제가 있다.

1. **계층 패턴 부적합** -- 쓰기가 빈번한 카테고리에 Nested Set을 사용하고 있다.
2. **상속 패턴 부적합** -- 공통 속성이 많은 콘텐츠에 Concrete Table Inheritance를 사용하여, 전체 콘텐츠 조회가 불가능하고 댓글의 참조 무결성이 깨져 있다.

---

## Finding 1: Nested Set은 쓰기 빈번 환경에 부적합

[Hierarchy Pattern -- 쓰기 비용] -- Nested Set은 INSERT/이동 시 lft, rgt 값을 대규모 재작성해야 하므로 쓰기가 비싸다. 일 10회 이상 추가/이동이 발생하는 환경에서 Nested Set을 사용하면 매 변경마다 다수의 행을 UPDATE해야 하며, 동시성 문제(잠금 경합)도 발생한다.

**현재 조건 분석:**
- 카테고리 50개, 최대 3단계 -- 작고 얕은 트리
- 일 10회 이상 추가/이동 -- 빈번한 쓰기
- "특정 카테고리의 하위 카테고리 조회" -- 하위 트리 조회 필요

**권장**: Adjacency List. 작고 단순한 트리에 빈번한 갱신이 있는 경우 선택 가이드가 명확히 권장하는 패턴이다. 최대 3단계이므로 CTE 재귀의 깊이가 얕아 성능 문제가 없다. 카테고리 50개 수준이면 CTE 비용이 무시할 만하다.

---

## Finding 2: Concrete Table Inheritance로 인한 스키마 중복과 전체 조회 불가

[Inheritance Pattern -- TPC 한계] -- articles와 videos가 title, author_id, published_at, view_count를 완전히 중복 정의하고 있다. 공통 속성이 4개(title, author_id, published_at, view_count)이고 videos의 고유 속성은 duration 1개뿐이므로, 속성의 80% 이상을 공유한다. 이 비율에서는 TPC가 아닌 STI 또는 CTI가 적합하다.

**실질적 피해:**
- "전체 콘텐츠 최신순 조회"가 주요 쿼리인데, TPC에서는 UNION ALL이 필수다. 콘텐츠 타입이 늘어날 때마다 UNION에 테이블을 추가해야 하며, UNION 결과에 대한 인덱스 활용이 불가능하다.
- 스키마 변경(예: 새 공통 컬럼 추가) 시 모든 구체 테이블을 동일하게 수정해야 한다.

---

## Finding 3: 댓글 테이블의 다형적 연관 -- 참조 무결성 부재

[Polymorphic Association -- FK 제약 불가] -- comments 테이블이 article_id와 video_id를 별도 FK로 두고 "하나만 NOT NULL" 규칙을 주석으로만 명시하고 있다. 이 설계에는 두 가지 문제가 있다.

1. **DB 레벨 제약 없음**: 두 FK가 모두 NULL이거나 모두 NOT NULL인 행이 삽입될 수 있다. CHECK 제약이 없으므로 데이터 무결성이 애플리케이션 코드에 전적으로 의존한다.
2. **확장성 문제**: 콘텐츠 타입이 추가될 때마다 comments 테이블에 새 FK 컬럼을 추가해야 한다(photo_id, podcast_id 등). 이는 NULL 컬럼의 증가와 CHECK 제약의 복잡도를 기하급수적으로 높인다.

---

## Finding 4: 인덱스 완전 부재

[Index Design -- 쿼리 워크로드 기반 인덱스] -- 주요 쿼리가 두 가지(전체 콘텐츠 최신순 조회, 하위 카테고리 조회)임에도 인덱스가 하나도 정의되어 있지 않다.

현재 스키마에서 최소한 필요한 인덱스:
- `categories(lft)`, `categories(rgt)` -- Nested Set의 BETWEEN 조회 지원 (패턴 변경 시 불필요)
- `articles(published_at)`, `videos(published_at)` -- 최신순 정렬
- `comments(article_id)`, `comments(video_id)` -- FK 컬럼의 조회/JOIN 지원

---

## Finding 5: 카테고리와 콘텐츠 간 관계 부재

스키마에 카테고리와 콘텐츠(articles, videos)를 연결하는 FK나 관계 테이블이 없다. "특정 카테고리의 하위 카테고리 조회"가 주요 쿼리로 명시되어 있으므로, 카테고리별 콘텐츠 조회도 필요할 가능성이 높다. 현재 구조에서는 이 쿼리를 실행할 방법 자체가 없다.

---

## Finding 6: Missing foreign key constraints

- `articles.author_id`와 `videos.author_id`가 FK 제약 없이 선언되어 있다. 참조 대상 테이블(users 등)이 존재한다면 FK 제약이 필요하다.
- 댓글의 CASCADE 규칙이 정의되어 있지 않다. 콘텐츠 삭제 시 댓글 처리 정책(CASCADE, SET NULL, RESTRICT)이 명시되지 않았다.

---

## 개선 방향 요약

| # | 현재 | 권장 | 이유 |
|---|------|------|------|
| 1 | Nested Set (categories) | **Adjacency List** | 쓰기 빈번, 트리 작고 얕음 |
| 2 | Concrete Table (articles, videos) | **Class Table Inheritance** 또는 **Single Table** | 속성 80%+ 공유, 전체 조회 필요 |
| 3 | 별도 FK 컬럼 (comments) | **공통 부모 테이블의 단일 FK** | CTI 전환 시 contents.id 하나로 참조 가능 |
| 4 | 인덱스 없음 | 쿼리 워크로드 기반 인덱스 추가 | published_at 정렬, FK 조회 지원 |

**CTI로 전환할 경우의 구조 예시:**

```sql
-- 카테고리: Adjacency List
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id INTEGER REFERENCES categories(id)
);
CREATE INDEX idx_categories_parent ON categories(parent_id);

-- 콘텐츠: Class Table Inheritance
CREATE TABLE contents (
    id SERIAL PRIMARY KEY,
    type VARCHAR(20) NOT NULL,
    title VARCHAR(300) NOT NULL,
    author_id INTEGER NOT NULL,
    published_at TIMESTAMP,
    view_count INTEGER DEFAULT 0,
    category_id INTEGER REFERENCES categories(id)
);
CREATE INDEX idx_contents_published ON contents(published_at DESC);
CREATE INDEX idx_contents_category ON contents(category_id);

CREATE TABLE articles (
    content_id INTEGER PRIMARY KEY REFERENCES contents(id),
    body TEXT
);

CREATE TABLE videos (
    content_id INTEGER PRIMARY KEY REFERENCES contents(id),
    url TEXT NOT NULL,
    duration INTEGER
);

-- 댓글: 단일 FK로 참조 무결성 확보
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    body TEXT NOT NULL,
    content_id INTEGER NOT NULL REFERENCES contents(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_comments_content ON comments(content_id);
```

이 구조에서는:
- "전체 콘텐츠 최신순 조회"가 contents 테이블 단일 쿼리로 해결된다.
- "하위 카테고리 조회"가 CTE 한 번으로 해결되며 쓰기 비용이 없다.
- 댓글이 DB 레벨 FK로 참조 무결성을 보장한다.
- 콘텐츠 타입 추가 시 새 하위 테이블만 만들면 되며, comments 테이블 변경이 불필요하다.
