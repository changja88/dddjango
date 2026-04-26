# Schema Review & Refactoring

## 1. 현재 스키마 문제점 분석

### 1.1 Polymorphic Association (다형성 연관) 안티패턴

`comments` 테이블의 `parent_type`/`parent_id`와 `taggings` 테이블의 `taggable_type`/`taggable_id`는 **Polymorphic Association** 패턴이다. 이 패턴의 문제점은 다음과 같다.

- **FK 제약 불가** -- `parent_id`가 articles일 수도 있고 videos일 수도 있으므로, 데이터베이스 레벨에서 참조 무결성을 보장할 수 없다. 존재하지 않는 레코드를 가리키는 고아 데이터(orphan)가 발생할 수 있다.
- **JOIN 복잡도 증가** -- 쿼리 시 항상 `WHERE parent_type = 'article'` 같은 조건이 필요하며, 여러 타입을 한 번에 조회하려면 `UNION`이 필요하다.
- **인덱스 효율 저하** -- 복합 인덱스 `(parent_type, parent_id)`를 걸어도, 카디널리티가 낮은 `parent_type` 컬럼이 포함되어 인덱스 효율이 떨어진다.

### 1.2 Foreign Key 제약 누락

- `comments.author_id`, `articles.author_id`, `videos.uploader_id` 모두 FK 제약이 없다. `users` 테이블 자체가 스키마에 정의되어 있지 않다.
- `taggings.tag_id`만 유일하게 FK가 걸려 있으나, 나머지 참조 관계는 전부 누락되어 있다.

### 1.3 인덱스 부재

- 조회에 빈번하게 사용될 FK 컬럼(`author_id`, `tag_id` 등)에 인덱스가 없다.
- `taggable_type`/`taggable_id` 조합 조회에 대한 인덱스도 없다.

### 1.4 기타

- `articles`, `videos`에 `created_at`/`updated_at` 타임스탬프가 없다.
- `taggings`에 동일 태그 중복 부착을 방지하는 UNIQUE 제약이 없다.
- `comments`의 `parent_type`은 자유 문자열이므로 오타나 잘못된 타입이 들어갈 수 있다.

---

## 2. 리팩토링 전략

Polymorphic Association을 제거하기 위해 두 가지 대안 중 **Exclusive Belongs To (전용 FK 컬럼)** 방식을 채택한다.

| 전략 | 설명 | 장단점 |
|---|---|---|
| 전용 FK 컬럼 | 대상 테이블마다 별도 nullable FK 컬럼 | FK 제약 가능, 스키마가 명시적. 컬럼 수 증가 |
| 연결 테이블 분리 | `article_comments`, `video_comments` 등 | 정규화 극대화. 테이블 수 증가 |

대상 타입이 소수(articles, videos)이므로 전용 FK 컬럼 방식이 단순하고 효과적이다. CHECK 제약으로 정확히 하나의 FK만 값을 가지도록 보장한다.

---

## 3. 리팩토링된 스키마

```sql
-- ============================================================
-- 사용자 테이블 (기존 스키마에 누락)
-- ============================================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 콘텐츠 테이블
-- ============================================================
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    body TEXT,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_articles_author_id ON articles(author_id);

CREATE TABLE videos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    url TEXT NOT NULL,
    duration INTEGER,
    uploader_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_videos_uploader_id ON videos(uploader_id);

-- ============================================================
-- 댓글 테이블 (Polymorphic Association 제거)
-- ============================================================
-- parent_type/parent_id 대신, 대상 테이블별 전용 nullable FK 사용.
-- CHECK 제약으로 정확히 하나의 FK만 NOT NULL임을 보장.
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    body TEXT NOT NULL,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_comments_single_parent CHECK (
        (article_id IS NOT NULL)::int + (video_id IS NOT NULL)::int = 1
    )
);

CREATE INDEX idx_comments_article_id ON comments(article_id) WHERE article_id IS NOT NULL;
CREATE INDEX idx_comments_video_id ON comments(video_id) WHERE video_id IS NOT NULL;
CREATE INDEX idx_comments_author_id ON comments(author_id);

-- ============================================================
-- 태그 테이블 (Polymorphic Association 제거)
-- ============================================================
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- taggable_type/taggable_id 대신, 대상 테이블별 전용 연결 테이블 사용.
CREATE TABLE article_tags (
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (article_id, tag_id)
);

CREATE INDEX idx_article_tags_tag_id ON article_tags(tag_id);

CREATE TABLE video_tags (
    video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (video_id, tag_id)
);

CREATE INDEX idx_video_tags_tag_id ON video_tags(tag_id);
```

---

## 4. 변경 사항 요약

| 항목 | Before | After |
|---|---|---|
| Polymorphic FK (comments) | `parent_type` + `parent_id` | `article_id`, `video_id` 전용 FK + CHECK 제약 |
| Polymorphic FK (taggings) | `taggable_type` + `taggable_id` | `article_tags`, `video_tags` 전용 연결 테이블 |
| users 테이블 | 없음 | 추가 |
| FK 제약 | `taggings.tag_id`만 존재 | 모든 참조 컬럼에 FK + ON DELETE CASCADE |
| 인덱스 | 없음 | FK 컬럼 전체에 인덱스 추가 |
| NOT NULL | 대부분 누락 | `title`, `url`, `author_id` 등 필수 컬럼에 적용 |
| 타임스탬프 | `comments`만 존재 | 전 테이블에 `created_at`, `updated_at` 추가 |
| 태그 중복 방지 | 없음 | 복합 PK로 자동 보장 |
| surrogate PK (taggings) | 불필요한 `id` 컬럼 존재 | 복합 PK 사용으로 제거 |

### 핵심 개선 포인트

1. **참조 무결성 보장** -- 모든 관계에 FK 제약이 걸려 있어, 고아 데이터가 원천 차단된다.
2. **쿼리 단순화** -- 타입 분기 조건 없이 직접 JOIN이 가능하다.
3. **인덱스 최적화** -- 부분 인덱스(partial index)를 사용해 nullable FK의 조회 성능을 확보하면서 저장 공간을 절약한다.
4. **확장 시 비용** -- 새로운 콘텐츠 타입 추가 시 `comments`에 FK 컬럼 하나와 CHECK 수정, 태그 연결 테이블 하나를 추가해야 한다. 타입이 10개 이상으로 늘어난다면 연결 테이블 분리 방식으로 comments도 전환하는 것을 검토한다.
