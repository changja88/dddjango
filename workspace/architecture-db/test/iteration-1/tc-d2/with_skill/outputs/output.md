# 콘텐츠 관리 시스템 DB 스키마 설계

## 1. 요구사항 정리

**엔티티 및 속성**

- 콘텐츠 (다형적): Article, Video, Podcast, Photo
- 공통 속성: id, title, author_id, published_at, view_count, status
- 타입별 고유 속성:
  - Article: body, word_count
  - Video: url, duration_seconds, thumbnail_url
  - Podcast: audio_url, duration_seconds, transcript
  - Photo: image_url, width, height, format
- 댓글: 모든 콘텐츠에 연결
- 태그: 모든 콘텐츠에 연결 (N:M)

**주요 쿼리 워크로드**

| # | 쿼리 | 특성 |
|---|------|------|
| Q1 | 전체 콘텐츠 최신순 목록 (타입 무관) | 크로스 타입 조회, ORDER BY published_at DESC |
| Q2 | 특정 타입만 필터링 | 타입 구분자 필터 |
| Q3 | 특정 콘텐츠의 댓글 조회 | 콘텐츠 -> 댓글 1:N |
| Q4 | 인기 콘텐츠 Top 20 (view_count 기준, 타입 무관) | 크로스 타입 조회, ORDER BY view_count DESC LIMIT 20 |

---

## 2. 상속 패턴 비교 및 선택

### 2.1 패턴별 평가

| 기준 | STI | CTI | TPC |
|------|-----|-----|-----|
| **Q1: 전체 최신순 목록** | 단일 테이블 SELECT, 최적 | 부모 테이블만 조회하면 공통 속성 확보, 양호 | 4개 테이블 UNION ALL 필요, 최악 |
| **Q2: 타입 필터링** | WHERE type = 'article', 단순 | WHERE type = 'article' 후 서브타입 JOIN 1회, 양호 | 해당 테이블만 SELECT, 최적 |
| **Q3: 댓글 조회** | FK로 단일 테이블 참조, 최적 | FK로 부모 테이블 참조, 최적 | FK 제약 불가, 다형적 연관 필수, 최악 |
| **Q4: 인기 Top 20** | 단일 테이블 ORDER BY, 최적 | 부모 테이블만 조회, 양호 | 4개 테이블 UNION ALL + 정렬, 최악 |
| **NULL 컬럼 오버헤드** | 타입별 고유 속성이 NULL로 채워짐 | 없음 (타입별 테이블에 분리) | 없음 |
| **데이터 무결성** | NOT NULL 제약 불가 (타입별 속성) | FK + NOT NULL 모두 가능 | FK 제약 불가 (크로스 타입 참조 시) |
| **스키마 확장성** | 새 타입 추가 시 테이블에 컬럼 추가 | 새 서브타입 테이블 추가, 기존 영향 없음 | 독립 테이블 추가, 기존 영향 없음 |

### 2.2 분석

**STI 탈락 사유**: 4개 타입의 공통 속성은 6개(id, title, author_id, published_at, view_count, status)이고, 고유 속성은 Article 2개, Video 3개, Podcast 3개, Photo 4개로 총 12개다. 공통 속성 비율이 6/18 = 33%에 불과하다. STI는 속성의 80% 이상이 공유될 때 적합한 패턴이다. 여기서는 NULL 컬럼이 지나치게 많아지고, 타입별 속성에 NOT NULL 제약을 걸 수 없어 데이터 무결성이 약화된다.

**TPC 탈락 사유**: Q1(전체 최신순), Q4(인기 Top 20)가 핵심 쿼리인데, 두 쿼리 모두 크로스 타입 조회다. TPC에서는 매번 4개 테이블에 UNION ALL을 걸어야 하며, 타입이 추가될 때마다 모든 크로스 타입 쿼리를 수정해야 한다. 댓글/태그에 대한 FK 제약도 불가능하다.

**CTI 선택 사유**:
- Q1, Q4: 부모 테이블(contents)만 조회하면 공통 속성(title, published_at, view_count)을 모두 얻을 수 있다. JOIN 없이 단일 테이블 조회로 충분하다.
- Q2: 부모 테이블에서 type 필터 후, 상세 정보가 필요할 때만 서브타입 테이블과 JOIN 1회.
- Q3: 댓글이 부모 테이블의 PK를 FK로 참조하므로 참조 무결성이 DB 레벨에서 보장된다.
- 타입별 속성에 NOT NULL 제약을 각 서브타입 테이블에서 독립적으로 적용할 수 있다.
- 새 콘텐츠 타입 추가 시 서브타입 테이블만 추가하면 되고, 기존 테이블/쿼리에 영향이 없다.

### 2.3 결론

**CTI (Class Table Inheritance)** 를 선택한다.

---

## 3. 개념적 모델 (ERD)

```
[authors] 1 ---- N [contents]
                      |
                      |-- type = 'article'  --> [articles]
                      |-- type = 'video'    --> [videos]
                      |-- type = 'podcast'  --> [podcasts]
                      |-- type = 'photo'    --> [photos]
                      |
                      | 1
                      |
                      N
                  [comments]
                      |
                      N
                      |
                      1
                  [users] (댓글 작성자)

[contents] N ---- N [tags]  (중간 테이블: content_tags)
```

**관계 정리**

| 관계 | Cardinality | Optionality |
|------|-------------|-------------|
| authors -> contents | 1:N | 작성자 필수, 콘텐츠는 선택 |
| contents -> articles/videos/podcasts/photos | 1:1 | 부모 필수, 서브타입 필수 |
| contents -> comments | 1:N | 콘텐츠 필수, 댓글은 선택 |
| contents <-> tags | N:M | 양쪽 모두 선택 |

---

## 4. 논리적 모델 (정규화된 스키마)

```sql
-- 부모 테이블: 모든 콘텐츠 공통 속성
CREATE TABLE contents (
    id BIGINT PRIMARY KEY,
    type VARCHAR(20) NOT NULL,
    title VARCHAR(500) NOT NULL,
    author_id BIGINT NOT NULL REFERENCES authors(id),
    published_at TIMESTAMP,
    view_count BIGINT NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 서브타입 테이블들: 타입별 고유 속성
CREATE TABLE articles (
    content_id BIGINT PRIMARY KEY REFERENCES contents(id),
    body TEXT NOT NULL,
    word_count INTEGER NOT NULL
);

CREATE TABLE videos (
    content_id BIGINT PRIMARY KEY REFERENCES contents(id),
    url VARCHAR(2000) NOT NULL,
    duration_seconds INTEGER NOT NULL,
    thumbnail_url VARCHAR(2000)
);

CREATE TABLE podcasts (
    content_id BIGINT PRIMARY KEY REFERENCES contents(id),
    audio_url VARCHAR(2000) NOT NULL,
    duration_seconds INTEGER NOT NULL,
    transcript TEXT
);

CREATE TABLE photos (
    content_id BIGINT PRIMARY KEY REFERENCES contents(id),
    image_url VARCHAR(2000) NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    format VARCHAR(20) NOT NULL
);

-- 댓글: contents FK로 참조 무결성 보장
CREATE TABLE comments (
    id BIGINT PRIMARY KEY,
    content_id BIGINT NOT NULL REFERENCES contents(id),
    author_id BIGINT NOT NULL REFERENCES authors(id),
    body TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 태그: N:M 관계 -> 중간 테이블
CREATE TABLE tags (
    id BIGINT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE content_tags (
    content_id BIGINT NOT NULL REFERENCES contents(id),
    tag_id BIGINT NOT NULL REFERENCES tags(id),
    PRIMARY KEY (content_id, tag_id)
);
```

**정규화 검증**

- 1NF: 모든 컬럼이 원자값, 반복 그룹 없음 (태그는 별도 테이블로 분리).
- 2NF: content_tags의 복합키 (content_id, tag_id) 외에 비주요 속성이 없으므로 부분 종속 없음.
- 3NF: 이행 종속 없음. author 정보는 별도 테이블, tag 정보도 별도 테이블.

---

## 5. 물리적 모델 (인덱스 설계)

인덱스는 쿼리 워크로드를 기반으로 설계한다.

```sql
-- Q1: 전체 콘텐츠 최신순 (published 상태만)
-- WHERE status = 'published' ORDER BY published_at DESC
-- 등호 조건(status)을 범위 조건(published_at) 앞에 배치
CREATE INDEX idx_contents_status_published ON contents (status, published_at DESC);

-- Q2: 특정 타입 필터링 + 최신순
-- WHERE type = 'article' AND status = 'published' ORDER BY published_at DESC
CREATE INDEX idx_contents_type_status_published ON contents (type, status, published_at DESC);

-- Q3: 특정 콘텐츠의 댓글 조회 (최신순)
-- WHERE content_id = ? ORDER BY created_at DESC
CREATE INDEX idx_comments_content_created ON comments (content_id, created_at DESC);

-- Q4: 인기 콘텐츠 Top 20
-- WHERE status = 'published' ORDER BY view_count DESC LIMIT 20
-- Q1의 인덱스와 정렬 기준이 다르므로 별도 인덱스 필요
CREATE INDEX idx_contents_status_viewcount ON contents (status, view_count DESC);

-- 댓글 작성자별 조회 (부가 워크로드)
CREATE INDEX idx_comments_author ON comments (author_id);

-- 콘텐츠 작성자별 조회
CREATE INDEX idx_contents_author ON contents (author_id);

-- 태그 이름으로 콘텐츠 조회: content_tags의 역방향 조회
CREATE INDEX idx_content_tags_tag ON content_tags (tag_id);
```

**인덱스 설계 근거**

| 인덱스 | 서비스하는 쿼리 | 설계 원칙 |
|--------|---------------|----------|
| idx_contents_status_published | Q1 | 등호(status) 먼저, 범위(published_at) 뒤에 |
| idx_contents_type_status_published | Q2 | 등호(type, status) 먼저, 범위(published_at) 뒤에 |
| idx_comments_content_created | Q3 | content_id 등호 필터 + created_at 정렬 |
| idx_contents_status_viewcount | Q4 | 등호(status) 먼저, 정렬(view_count) 뒤에 |
| idx_content_tags_tag | 태그별 콘텐츠 | PK (content_id, tag_id)의 역방향 조회 지원 |

---

## 6. 쿼리 예시

### Q1: 전체 콘텐츠 최신순 목록

```sql
SELECT id, type, title, author_id, published_at, view_count
FROM contents
WHERE status = 'published'
ORDER BY published_at DESC
LIMIT 20 OFFSET 0;
```

단일 테이블 조회. `idx_contents_status_published` 인덱스 활용.

### Q2: 특정 타입 필터링 (상세 포함)

```sql
SELECT c.id, c.title, c.published_at, c.view_count,
       a.body, a.word_count
FROM contents c
JOIN articles a ON a.content_id = c.id
WHERE c.type = 'article' AND c.status = 'published'
ORDER BY c.published_at DESC
LIMIT 20;
```

`idx_contents_type_status_published` 인덱스로 부모 테이블 스캔 후, 서브타입 JOIN 1회.

### Q3: 특정 콘텐츠의 댓글 조회

```sql
SELECT id, author_id, body, created_at
FROM comments
WHERE content_id = 42
ORDER BY created_at DESC;
```

`idx_comments_content_created` 인덱스로 Index Scan.

### Q4: 인기 콘텐츠 Top 20

```sql
SELECT id, type, title, author_id, view_count
FROM contents
WHERE status = 'published'
ORDER BY view_count DESC
LIMIT 20;
```

단일 테이블 조회. `idx_contents_status_viewcount` 인덱스 활용.

---

## 7. 설계 요약

| 항목 | 결정 | 근거 |
|------|------|------|
| 상속 패턴 | CTI (Class Table Inheritance) | 공통 속성 33%로 STI 부적합, 크로스 타입 쿼리 빈번해 TPC 부적합 |
| 댓글 연결 | contents(id) FK 직접 참조 | CTI 덕분에 다형적 연관 없이 단일 FK로 해결, 참조 무결성 DB 레벨 보장 |
| 태그 연결 | content_tags 중간 테이블 | N:M 관계의 표준 패턴, contents(id) FK로 참조 무결성 보장 |
| 정규화 수준 | 3NF | 역정규화 불필요 (측정된 성능 이슈 없음) |
| 인덱스 전략 | 쿼리 워크로드 기반 5개 | 등호 조건 먼저, 범위/정렬 조건 뒤에 배치 |
