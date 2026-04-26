# Schema Review & Refactoring: Comments, Articles, Videos, Tags

## Part 1 -- Review

### Review Checklist

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

### Findings

```
[Polymorphic Association without Referential Integrity] — comments 테이블의
(parent_type, parent_id) 조합은 전형적인 다형적 연관 패턴이다.
DB 레벨에서 FK 제약을 강제할 수 없으므로 parent_id에 존재하지 않는
articles/videos/photos ID가 들어와도 DB가 이를 차단하지 못한다.
데이터 무결성이 애플리케이션 코드에 전적으로 의존하게 되어,
버그나 직접 SQL 실행 시 고아 레코드가 누적된다.
```

```
[Polymorphic Association without Referential Integrity] — taggings 테이블의
(taggable_type, taggable_id) 역시 동일한 다형적 연관 문제를 갖는다.
tag_id에만 FK가 걸려 있고, taggable_id는 어떤 테이블도 참조하지 않는다.
```

```
[Missing Foreign Key Constraints] — comments.author_id, articles.author_id,
videos.uploader_id 모두 FK 제약이 없다. 존재하지 않는 사용자 ID를
삽입해도 DB가 이를 차단하지 못하며, 사용자 삭제 시 고아 레코드가 발생한다.
```

```
[Missing Indexes on JOIN Keys] — comments.parent_id, comments.author_id,
taggings.tag_id, taggings.taggable_id, articles.author_id, videos.uploader_id에
인덱스가 전혀 없다. FK 조인과 WHERE 필터 시 풀 테이블 스캔이 발생하여
데이터가 증가할수록 성능이 급격히 저하된다.
```

```
[Missing Composite Index] — comments 테이블에서 "특정 글의 모든 댓글 조회"는
WHERE parent_type = ? AND parent_id = ? 형태의 쿼리가 빈번하다.
두 컬럼을 묶은 복합 인덱스가 없으면 타입 필터 후 다시 풀 스캔이 필요하다.
taggings 테이블의 (taggable_type, taggable_id)도 동일하다.
```

```
[Normalization] — 스키마 자체의 정규화 위반(2NF, 3NF)은 관찰되지 않는다.
각 테이블의 비주요 속성은 해당 PK에 완전 함수적으로 종속되어 있다.
```

### Summary

이 스키마의 가장 큰 문제는 두 곳의 다형적 연관(comments, taggings)에서 참조 무결성이 전혀 보장되지 않는 점이다. 그 다음으로 전반적인 FK 제약 부재와 인덱스 부재가 데이터 무결성과 조회 성능 모두를 위협한다.

---

## Part 2 -- Refactoring

다형적 연관을 Exclusive FK 패턴(각 부모 타입별 nullable FK 컬럼)으로 전환하여 DB 레벨에서 참조 무결성을 확보한다. 부모 타입이 3개 이하이고 향후 대폭 늘어날 가능성이 낮은 상황에서는, 이 방식이 다형적 연관의 무결성 문제를 해결하는 가장 직관적인 전략이다.

### Refactoring Checklist

- [x] Missing PK -- 해당 없음 (SERIAL PK 존재)
- [x] Normalization violation -- 해당 없음 (위반 없음)
- [x] Missing index -- ADD index based on query workload
- [x] Wrong composite index order -- 해당 없음 (기존 복합 인덱스 없음)
- [x] N+1 queries -- 해당 없음 (스키마 레벨에서 판단 불가, 인덱스 추가로 대응)
- [x] Wrong isolation level -- 해당 없음 (스키마에 명시 없음)
- [x] Poor hierarchy representation -- 해당 없음 (계층 데이터 없음)
- [x] Broken referential integrity -- ADD constraints, change polymorphic pattern
- [x] Premature denormalization -- 해당 없음 (역정규화 없음)
- [x] Seq Scan on large table -- ADD covering or partial index

---

### Change 1: users 테이블 추가

```
[Before]
-- users 테이블 없음. comments.author_id, articles.author_id,
-- videos.uploader_id가 참조할 대상이 존재하지 않음.

[After]
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

[Reason] FK 제약 대상 -- FK 참조의 대상 테이블이 반드시 존재해야
참조 무결성을 강제할 수 있다. author_id, uploader_id가 실존하는
사용자를 가리키도록 보장하기 위해 users 테이블을 추가한다.
```

---

### Change 2: comments 다형적 연관을 Exclusive FK 패턴으로 전환

```
[Before]
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    body TEXT NOT NULL,
    parent_type VARCHAR(50),  -- 'Article', 'Video', 'Photo'
    parent_id INTEGER,
    author_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

[After]
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    body TEXT NOT NULL,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT chk_comments_one_parent CHECK (
        (article_id IS NOT NULL)::int +
        (video_id IS NOT NULL)::int
        = 1
    )
);

[Reason] Polymorphic Association -> Exclusive FK -- parent_type/parent_id
조합은 DB 레벨에서 FK 제약을 강제할 수 없다. 각 부모 타입별로
nullable FK 컬럼을 두고, CHECK 제약으로 정확히 하나만 NOT NULL이
되도록 강제하면 DB 레벨에서 참조 무결성이 보장된다. 부모 타입이
소수일 때 가장 단순하고 효과적인 패턴이다.
Photo 타입은 현재 photos 테이블이 존재하지 않아 제외했다.
필요 시 photos 테이블 생성 후 photo_id FK 컬럼을 추가하면 된다.
```

---

### Change 3: taggings 다형적 연관을 Exclusive FK 패턴으로 전환

```
[Before]
CREATE TABLE taggings (
    id SERIAL PRIMARY KEY,
    tag_id INTEGER REFERENCES tags(id),
    taggable_type VARCHAR(50),  -- 'Article', 'Video'
    taggable_id INTEGER
);

[After]
CREATE TABLE taggings (
    id SERIAL PRIMARY KEY,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    CONSTRAINT chk_taggings_one_parent CHECK (
        (article_id IS NOT NULL)::int +
        (video_id IS NOT NULL)::int
        = 1
    ),
    CONSTRAINT uq_tag_article UNIQUE (tag_id, article_id),
    CONSTRAINT uq_tag_video UNIQUE (tag_id, video_id)
);

[Reason] Polymorphic Association -> Exclusive FK -- comments와 동일한
이유로 Exclusive FK 패턴을 적용한다. 추가로 동일 태그의 중복 연결을
방지하기 위해 UNIQUE 제약을 건다. tag_id에도 NOT NULL과 ON DELETE
CASCADE를 명시하여 고아 레코드를 방지한다.
```

---

### Change 4: articles, videos 테이블에 FK 제약 추가

```
[Before]
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300),
    body TEXT,
    author_id INTEGER
);

CREATE TABLE videos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300),
    url TEXT,
    duration INTEGER,
    uploader_id INTEGER
);

[After]
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    body TEXT,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE videos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    url TEXT NOT NULL,
    duration INTEGER,
    uploader_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
);

[Reason] Missing FK Constraints -- author_id와 uploader_id에 FK
제약이 없으면 존재하지 않는 사용자를 참조할 수 있다. NOT NULL 제약을
추가하여 작성자/업로더 없는 콘텐츠 생성을 방지하고, ON DELETE CASCADE로
사용자 삭제 시 관련 콘텐츠가 함께 정리되도록 한다. title은 콘텐츠의
필수 속성이므로 NOT NULL을, videos.url은 영상의 핵심 정보이므로
NOT NULL을 추가한다.
```

---

### Change 5: 인덱스 추가

```
[Before]
-- 인덱스 없음

[After]
-- comments: 특정 글/영상의 댓글 조회 (가장 빈번한 쿼리 패턴)
CREATE INDEX idx_comments_article_id ON comments (article_id);
CREATE INDEX idx_comments_video_id ON comments (video_id);
CREATE INDEX idx_comments_author_id ON comments (author_id);
CREATE INDEX idx_comments_created_at ON comments (created_at);

-- articles: 작성자별 글 조회
CREATE INDEX idx_articles_author_id ON articles (author_id);

-- videos: 업로더별 영상 조회
CREATE INDEX idx_videos_uploader_id ON videos (uploader_id);

-- taggings: 태그별 콘텐츠 조회, 콘텐츠별 태그 조회
CREATE INDEX idx_taggings_tag_id ON taggings (tag_id);
CREATE INDEX idx_taggings_article_id ON taggings (article_id);
CREATE INDEX idx_taggings_video_id ON taggings (video_id);

[Reason] Missing Indexes on JOIN/FK Keys -- FK 컬럼과 자주 조회되는
컬럼에 인덱스가 없으면 모든 JOIN과 WHERE 필터가 Sequential Scan으로
실행된다. FK 컬럼에 인덱스를 추가하면 JOIN 성능이 향상되고, 부모
레코드 삭제 시 CASCADE 대상을 찾는 속도도 빨라진다. comments.created_at
인덱스는 "최신순 댓글 조회" 패턴을 지원한다.
```

---

## Refactored Full Schema

```sql
-- =============================================
-- Users
-- =============================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================================
-- Articles
-- =============================================
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    body TEXT,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_articles_author_id ON articles (author_id);

-- =============================================
-- Videos
-- =============================================
CREATE TABLE videos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    url TEXT NOT NULL,
    duration INTEGER,
    uploader_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_videos_uploader_id ON videos (uploader_id);

-- =============================================
-- Comments (Exclusive FK pattern)
-- =============================================
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    body TEXT NOT NULL,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT chk_comments_one_parent CHECK (
        (article_id IS NOT NULL)::int +
        (video_id IS NOT NULL)::int
        = 1
    )
);

CREATE INDEX idx_comments_article_id ON comments (article_id);
CREATE INDEX idx_comments_video_id ON comments (video_id);
CREATE INDEX idx_comments_author_id ON comments (author_id);
CREATE INDEX idx_comments_created_at ON comments (created_at);

-- =============================================
-- Tags
-- =============================================
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- =============================================
-- Taggings (Exclusive FK pattern)
-- =============================================
CREATE TABLE taggings (
    id SERIAL PRIMARY KEY,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    CONSTRAINT chk_taggings_one_parent CHECK (
        (article_id IS NOT NULL)::int +
        (video_id IS NOT NULL)::int
        = 1
    ),
    CONSTRAINT uq_tag_article UNIQUE (tag_id, article_id),
    CONSTRAINT uq_tag_video UNIQUE (tag_id, video_id)
);

CREATE INDEX idx_taggings_tag_id ON taggings (tag_id);
CREATE INDEX idx_taggings_article_id ON taggings (article_id);
CREATE INDEX idx_taggings_video_id ON taggings (video_id);
```
