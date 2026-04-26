# CMS 다형적 콘텐츠 DB 스키마 설계

## 1. 패턴 비교 분석

### 1.1 STI (Single Table Inheritance)

하나의 테이블에 모든 콘텐츠 타입의 컬럼을 통합한다. `type` 디스크리미네이터 컬럼으로 행의 실제 타입을 구분한다.

```
contents
├── id, type, title, author_id, published_at, view_count, status  (공통)
├── body, word_count                                               (Article)
├── url, duration_seconds, thumbnail_url                           (Video)
├── audio_url, transcript                                          (Podcast)
└── image_url, width, height, format                               (Photo)
```

| 항목 | 평가 |
|------|------|
| 전체 콘텐츠 최신순 조회 | 단일 테이블 SELECT -- 최적 |
| 특정 타입 필터링 | `WHERE type = ?` -- 최적 |
| 인기 콘텐츠 Top 20 | `ORDER BY view_count DESC LIMIT 20` -- 최적 |
| 댓글/태그 연결 | FK 하나로 충분 -- 최적 |
| NULL 컬럼 낭비 | 타입별 고유 컬럼이 NULL로 남음 -- 비효율 |
| 스키마 변경 영향 | 한 타입에 컬럼 추가 시 전체 테이블에 영향 |
| 타입별 NOT NULL 제약 | DB 수준에서 불가, 애플리케이션 레벨 검증 필요 |

### 1.2 CTI (Class Table Inheritance)

공통 속성을 부모 테이블에, 타입 고유 속성을 자식 테이블에 분리한다.

```
contents (부모)         articles       videos         podcasts       photos
├── id                  ├── content_id ├── content_id ├── content_id ├── content_id
├── type                ├── body       ├── url        ├── audio_url  ├── image_url
├── title               └── word_count ├── duration   ├── duration   ├── width
├── author_id                          ├── thumbnail  └── transcript ├── height
├── published_at                       └── url                       └── format
├── view_count
└── status
```

| 항목 | 평가 |
|------|------|
| 전체 콘텐츠 최신순 조회 | 부모 테이블만 조회하면 충분 -- 우수 |
| 특정 타입 필터링 + 상세 | JOIN 1회 필요 -- 양호 |
| 인기 콘텐츠 Top 20 | 부모 테이블만 조회 -- 우수 |
| 댓글/태그 연결 | 부모 테이블 FK -- 우수 |
| NULL 컬럼 낭비 | 없음 -- 최적 |
| 스키마 변경 영향 | 해당 자식 테이블만 변경 -- 최적 |
| 타입별 NOT NULL 제약 | 자식 테이블에서 DB 수준 제약 가능 -- 최적 |
| 상세 조회 비용 | 부모+자식 JOIN 필요 -- 약간의 추가 비용 |

### 1.3 TPC (Table Per Concrete class)

각 콘텐츠 타입별로 완전히 독립된 테이블을 만든다. 공통 속성이 모든 테이블에 중복된다.

```
articles                videos                 podcasts               photos
├── id                  ├── id                 ├── id                 ├── id
├── title               ├── title              ├── title              ├── title
├── author_id           ├── author_id          ├── author_id          ├── author_id
├── published_at        ├── published_at       ├── published_at       ├── published_at
├── view_count          ├── view_count         ├── view_count         ├── view_count
├── status              ├── status             ├── status             ├── status
├── body                ├── url                ├── audio_url          ├── image_url
└── word_count          ├── duration_seconds   ├── duration_seconds   ├── width
                        └── thumbnail_url      └── transcript         ├── height
                                                                      └── format
```

| 항목 | 평가 |
|------|------|
| 전체 콘텐츠 최신순 조회 | 4개 테이블 UNION ALL + 정렬 -- 최악 |
| 특정 타입 필터링 | 단일 테이블 조회 -- 최적 |
| 인기 콘텐츠 Top 20 | UNION ALL 후 정렬 -- 최악 |
| 댓글/태그 연결 | polymorphic FK (commentable_type + commentable_id) 필요 -- 복잡 |
| NULL 컬럼 낭비 | 없음 -- 최적 |
| 스키마 변경 영향 | 공통 속성 변경 시 4개 테이블 동시 수정 -- 최악 |
| 타입별 NOT NULL 제약 | DB 수준 제약 가능 -- 최적 |
| FK 무결성 | DB 수준 댓글/태그 FK 불가능 -- 최악 |

### 1.4 요구사항 적합도 종합

| 쿼리 요구사항 | STI | CTI | TPC |
|---------------|-----|-----|-----|
| 전체 최신순 목록 (타입 무관) | ★★★ | ★★★ | ★ |
| 특정 타입 필터링 | ★★★ | ★★☆ | ★★★ |
| 특정 콘텐츠의 댓글 조회 | ★★★ | ★★★ | ★★ |
| 인기 Top 20 (타입 무관) | ★★★ | ★★★ | ★ |
| 데이터 무결성 | ★★ | ★★★ | ★★ |
| 확장성 (새 타입 추가) | ★★ | ★★★ | ★★ |

### 1.5 결정: CTI (Class Table Inheritance)

**CTI를 선택한다.** 근거는 다음과 같다:

1. **자주 사용하는 4가지 쿼리 모두에서 우수한 성능을 보인다.** 전체 목록, 인기순 정렬, 댓글 조회는 부모 테이블만으로 처리 가능하고, 타입 필터링은 JOIN 1회로 해결된다. TPC의 UNION ALL 문제가 없다.
2. **데이터 무결성을 DB 수준에서 보장한다.** 자식 테이블에 NOT NULL 제약을 걸 수 있어 STI의 NULL 허용 문제가 없다. 댓글/태그 FK도 부모 테이블을 참조하면 된다.
3. **확장에 유리하다.** 새 콘텐츠 타입 추가 시 자식 테이블만 생성하면 되며, 기존 테이블에 영향을 주지 않는다.
4. **STI 대비 저장 공간이 효율적이다.** 타입별 고유 컬럼의 NULL 낭비가 없고, 특히 transcript 같은 대용량 텍스트 컬럼이 있는 경우 차이가 크다.

STI가 쿼리 단순성에서는 약간 우세하지만, 4개 타입에 걸친 고유 컬럼이 총 9개(body, word_count, url, duration_seconds, thumbnail_url, audio_url, transcript, image_url, width, height, format)로 상당히 많고, transcript 같은 대용량 텍스트가 포함되어 있어 NULL 낭비와 행 크기 문제가 심각하다.

---

## 2. 최종 스키마 (CTI 기반)

### 2.1 ERD

```
                        ┌─────────────┐
                        │   authors   │
                        ├─────────────┤
                        │ id (PK)     │
                        │ name        │
                        │ email       │
                        └──────┬──────┘
                               │ 1
                               │
                               │ N
┌──────────┐           ┌───────┴───────┐           ┌──────────┐
│   tags   │           │   contents    │           │ comments │
├──────────┤           ├───────────────┤           ├──────────┤
│ id (PK)  │◄── N:M ──│ id (PK)       │──── 1:N ──►│ id (PK)  │
│ name     │           │ type          │           │content_id│
│ slug     │           │ title         │           │author_id │
└──────────┘           │ author_id(FK) │           │ body     │
      │                │ published_at  │           │created_at│
      │                │ view_count    │           └──────────┘
      │                │ status        │
      │                │ created_at    │
      │                │ updated_at    │
      │                └───┬───┬───┬───┘
      │                    │   │   │
      │         ┌──────────┘   │   └──────────┐
      │         │              │              │
      │    ┌────┴────┐   ┌────┴────┐   ┌─────┴─────┐   ┌─────────┐
      │    │articles │   │ videos  │   │ podcasts  │   │ photos  │
      │    ├─────────┤   ├─────────┤   ├───────────┤   ├─────────┤
      │    │content_id│  │content_id│  │content_id │   │content_id│
      │    │body     │   │url      │   │audio_url  │   │image_url│
      │    │word_cnt │   │duration │   │duration   │   │width    │
      │    └─────────┘   │thumbnail│   │transcript │   │height   │
      │                  └─────────┘   └───────────┘   │format   │
      │                                                └─────────┘
      │
 ┌────┴──────────┐
 │content_tags   │
 ├───────────────┤
 │content_id(FK) │
 │tag_id (FK)    │
 └───────────────┘
```

### 2.2 DDL

```sql
-- =====================================================
-- 부모 테이블: 모든 콘텐츠의 공통 속성
-- =====================================================
CREATE TABLE contents (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    type            VARCHAR(20)  NOT NULL,          -- 'article','video','podcast','photo'
    title           VARCHAR(500) NOT NULL,
    author_id       BIGINT       NOT NULL,
    status          VARCHAR(20)  NOT NULL DEFAULT 'draft',  -- draft, published, archived
    view_count      BIGINT       NOT NULL DEFAULT 0,
    published_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT fk_contents_author
        FOREIGN KEY (author_id) REFERENCES authors(id),
    CONSTRAINT chk_contents_type
        CHECK (type IN ('article', 'video', 'podcast', 'photo')),
    CONSTRAINT chk_contents_status
        CHECK (status IN ('draft', 'published', 'archived'))
);

-- =====================================================
-- 자식 테이블: 타입별 고유 속성
-- =====================================================
CREATE TABLE articles (
    content_id  BIGINT PRIMARY KEY,
    body        TEXT         NOT NULL,
    word_count  INT          NOT NULL DEFAULT 0,

    CONSTRAINT fk_articles_content
        FOREIGN KEY (content_id) REFERENCES contents(id) ON DELETE CASCADE
);

CREATE TABLE videos (
    content_id      BIGINT        PRIMARY KEY,
    url             VARCHAR(2048) NOT NULL,
    duration_seconds INT          NOT NULL,
    thumbnail_url   VARCHAR(2048),

    CONSTRAINT fk_videos_content
        FOREIGN KEY (content_id) REFERENCES contents(id) ON DELETE CASCADE
);

CREATE TABLE podcasts (
    content_id       BIGINT        PRIMARY KEY,
    audio_url        VARCHAR(2048) NOT NULL,
    duration_seconds INT           NOT NULL,
    transcript       TEXT,

    CONSTRAINT fk_podcasts_content
        FOREIGN KEY (content_id) REFERENCES contents(id) ON DELETE CASCADE
);

CREATE TABLE photos (
    content_id  BIGINT        PRIMARY KEY,
    image_url   VARCHAR(2048) NOT NULL,
    width       INT           NOT NULL,
    height      INT           NOT NULL,
    format      VARCHAR(20)   NOT NULL,     -- jpeg, png, webp, avif

    CONSTRAINT fk_photos_content
        FOREIGN KEY (content_id) REFERENCES contents(id) ON DELETE CASCADE,
    CONSTRAINT chk_photos_format
        CHECK (format IN ('jpeg', 'png', 'webp', 'avif', 'gif', 'svg'))
);

-- =====================================================
-- 댓글 테이블
-- =====================================================
CREATE TABLE comments (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    content_id  BIGINT       NOT NULL,
    author_id   BIGINT       NOT NULL,
    body        TEXT         NOT NULL,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT fk_comments_content
        FOREIGN KEY (content_id) REFERENCES contents(id) ON DELETE CASCADE,
    CONSTRAINT fk_comments_author
        FOREIGN KEY (author_id) REFERENCES authors(id)
);

-- =====================================================
-- 태그 & 연결 테이블
-- =====================================================
CREATE TABLE tags (
    id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name  VARCHAR(100) NOT NULL,
    slug  VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE content_tags (
    content_id  BIGINT NOT NULL,
    tag_id      BIGINT NOT NULL,

    PRIMARY KEY (content_id, tag_id),

    CONSTRAINT fk_content_tags_content
        FOREIGN KEY (content_id) REFERENCES contents(id) ON DELETE CASCADE,
    CONSTRAINT fk_content_tags_tag
        FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- =====================================================
-- 참조용 authors 테이블
-- =====================================================
CREATE TABLE authors (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name       VARCHAR(200) NOT NULL,
    email      VARCHAR(320) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT now()
);
```

### 2.3 인덱스 전략

```sql
-- =======================================================
-- 쿼리 1: 전체 콘텐츠 최신순 목록
-- =======================================================
-- published 상태 콘텐츠를 published_at DESC로 페이지네이션
CREATE INDEX idx_contents_published_latest
    ON contents (published_at DESC)
    WHERE status = 'published';

-- =======================================================
-- 쿼리 2: 특정 타입 필터링
-- =======================================================
-- type + published_at 복합 인덱스로 타입별 최신순 조회 커버
CREATE INDEX idx_contents_type_published
    ON contents (type, published_at DESC)
    WHERE status = 'published';

-- =======================================================
-- 쿼리 3: 특정 콘텐츠의 댓글 조회
-- =======================================================
-- content_id로 댓글 조회 + 시간순 정렬
CREATE INDEX idx_comments_content_created
    ON comments (content_id, created_at DESC);

-- =======================================================
-- 쿼리 4: 인기 콘텐츠 Top 20
-- =======================================================
-- view_count DESC 인덱스 (published만)
CREATE INDEX idx_contents_popular
    ON contents (view_count DESC)
    WHERE status = 'published';

-- =======================================================
-- 보조 인덱스
-- =======================================================
-- 작성자별 콘텐츠 조회
CREATE INDEX idx_contents_author
    ON contents (author_id, created_at DESC);

-- 태그별 콘텐츠 조회 (역방향 조인용)
CREATE INDEX idx_content_tags_tag
    ON content_tags (tag_id);

-- 태그 이름 검색
CREATE INDEX idx_tags_name
    ON tags (name);

-- 댓글 작성자별 조회
CREATE INDEX idx_comments_author
    ON comments (author_id, created_at DESC);
```

---

## 3. 쿼리 예시

### 3.1 전체 콘텐츠 최신순 목록

```sql
-- 공통 정보만 필요할 때 (목록 화면)
SELECT c.id, c.type, c.title, c.published_at, c.view_count,
       a.name AS author_name
  FROM contents c
  JOIN authors a ON a.id = c.author_id
 WHERE c.status = 'published'
 ORDER BY c.published_at DESC
 LIMIT 20 OFFSET 0;
```

부모 테이블만 조회하므로 JOIN 없이 `idx_contents_published_latest` 인덱스를 탄다.

### 3.2 특정 타입 필터링 + 상세 정보

```sql
-- Video 목록 + 상세 정보
SELECT c.id, c.title, c.published_at, c.view_count,
       v.url, v.duration_seconds, v.thumbnail_url,
       a.name AS author_name
  FROM contents c
  JOIN videos v ON v.content_id = c.id
  JOIN authors a ON a.id = c.author_id
 WHERE c.type = 'video'
   AND c.status = 'published'
 ORDER BY c.published_at DESC
 LIMIT 20;
```

`idx_contents_type_published` 인덱스로 타입 필터링 후, 자식 테이블은 PK로 JOIN하므로 비용이 매우 낮다.

### 3.3 특정 콘텐츠의 댓글 조회

```sql
SELECT cm.id, cm.body, cm.created_at,
       a.name AS author_name
  FROM comments cm
  JOIN authors a ON a.id = cm.author_id
 WHERE cm.content_id = 42
 ORDER BY cm.created_at DESC
 LIMIT 50;
```

`idx_comments_content_created` 인덱스를 통해 content_id 필터링과 created_at 정렬을 동시에 처리한다.

### 3.4 인기 콘텐츠 Top 20

```sql
SELECT c.id, c.type, c.title, c.view_count,
       a.name AS author_name
  FROM contents c
  JOIN authors a ON a.id = c.author_id
 WHERE c.status = 'published'
 ORDER BY c.view_count DESC
 LIMIT 20;
```

`idx_contents_popular` 인덱스로 정렬 없이 상위 20건을 바로 가져온다.

### 3.5 콘텐츠 상세 조회 (타입별 동적 JOIN)

```sql
-- 콘텐츠 ID와 타입을 알 때 상세 조회
-- 애플리케이션에서 type에 따라 적절한 쿼리 실행
SELECT c.*, v.url, v.duration_seconds, v.thumbnail_url
  FROM contents c
  JOIN videos v ON v.content_id = c.id
 WHERE c.id = 42;
```

또는 타입을 모를 때 LEFT JOIN으로 한 번에 조회할 수도 있다:

```sql
SELECT c.*,
       ar.body, ar.word_count,
       vi.url AS video_url, vi.duration_seconds AS video_duration, vi.thumbnail_url,
       po.audio_url, po.duration_seconds AS podcast_duration, po.transcript,
       ph.image_url, ph.width, ph.height, ph.format
  FROM contents c
  LEFT JOIN articles ar ON ar.content_id = c.id AND c.type = 'article'
  LEFT JOIN videos vi   ON vi.content_id = c.id AND c.type = 'video'
  LEFT JOIN podcasts po ON po.content_id = c.id AND c.type = 'podcast'
  LEFT JOIN photos ph   ON ph.content_id = c.id AND c.type = 'photo'
 WHERE c.id = 42;
```

---

## 4. 운영 고려사항

### 4.1 타입-자식 테이블 일관성 보장

CTI의 핵심 과제는 `contents.type = 'video'`인 행이 반드시 `videos` 자식 행을 가져야 한다는 점이다. DB 수준에서 이를 강제하는 방법:

```sql
-- 삽입 시 트랜잭션으로 원자성 보장
BEGIN;
  INSERT INTO contents (type, title, author_id, status)
       VALUES ('video', 'Sample Video', 1, 'draft')
    RETURNING id;
  -- 반환된 id를 사용
  INSERT INTO videos (content_id, url, duration_seconds)
       VALUES (currval('contents_id_seq'), 'https://...', 300);
COMMIT;
```

추가 안전장치로 트리거를 설정할 수 있다:

```sql
-- 자식 행 없이 부모만 남아있는 고아 레코드 탐지
CREATE OR REPLACE FUNCTION check_content_child_exists()
RETURNS TRIGGER AS $$
BEGIN
    -- 삽입 후 약간의 유예 (같은 트랜잭션 내 자식 삽입 허용)
    -- 트랜잭션 커밋 시점에 DEFERRED CONSTRAINT로 검증
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

실무에서는 ORM(SQLAlchemy, Django ORM 등)의 모델 계층에서 부모+자식 동시 삽입을 강제하는 것이 더 일반적이다.

### 4.2 updated_at 자동 갱신

```sql
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_contents_updated_at
    BEFORE UPDATE ON contents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_comments_updated_at
    BEFORE UPDATE ON comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

### 4.3 view_count 동시성 처리

view_count가 높은 빈도로 갱신될 경우, 직접 UPDATE는 row lock 경합이 발생한다. 대안:

```sql
-- 방법 1: 별도 카운터 테이블 + 주기적 병합
CREATE TABLE content_view_log (
    content_id  BIGINT NOT NULL,
    viewed_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 방법 2: Redis 등 외부 카운터 사용 후 주기적으로 DB 동기화
-- 방법 3: PostgreSQL Advisory Lock 활용
SELECT pg_advisory_xact_lock(content_id);
UPDATE contents SET view_count = view_count + 1 WHERE id = content_id;
```

### 4.4 페이지네이션 전략

대규모 데이터에서 `OFFSET`은 성능이 저하된다. Keyset(커서) 페이지네이션을 권장한다:

```sql
-- 최신순 커서 페이지네이션
SELECT c.id, c.type, c.title, c.published_at, c.view_count
  FROM contents c
 WHERE c.status = 'published'
   AND (c.published_at, c.id) < (:last_published_at, :last_id)
 ORDER BY c.published_at DESC, c.id DESC
 LIMIT 20;
```
