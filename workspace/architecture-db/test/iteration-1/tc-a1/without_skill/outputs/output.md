# 온라인 서점 데이터베이스 스키마 설계

## 1. ERD (Entity-Relationship Diagram)

```
+----------------+       +-------------------+       +----------------+
|    member      |       |    book_order     |       |     book       |
|----------------|       |-------------------|       |----------------|
| PK member_id   |<--+   | PK order_id       |   +-->| PK book_id     |
|    name        |   |   |    order_number   |   |   |    title       |
|    email       |   |   |    order_date     |   |   |    author      |
|    joined_at   |   +---| FK member_id      |   |   |    publisher   |
|    grade       |       |    address        |   |   |    price       |
|    created_at  |       |    total_amount   |   |   |    stock       |
|    updated_at  |       |    status         |   |   |    isbn        |
+-------+--------+       |    created_at     |   |   |    published_at|
        |                 |    updated_at     |   |   |    description |
        |                 +---------+---------+   |   |    created_at  |
        |                           |             |   |    updated_at  |
        |                           |             |   +-------+--------+
        |                 +---------+---------+   |           |
        |                 |   order_item      |   |           |
        |                 |-------------------|   |           |
        |                 | PK order_item_id  |   |           |
        |                 | FK order_id       |---+           |
        |                 | FK book_id        |---+           |
        |                 |    quantity       |               |
        |                 |    unit_price    |               |
        |                 +-------------------+               |
        |                                                     |
        |                 +-------------------+               |
        |                 |     review        |               |
        |                 |-------------------|               |
        |                 | PK review_id      |               |
        +---------------->| FK member_id      |               |
                          | FK book_id        |<--------------+
                          |    rating         |
                          |    content        |
                          |    created_at     |
                          |    updated_at     |
                          +-------------------+

+-------------------+       +---------------------+
|    category       |       |  book_category      |
|-------------------|       |---------------------|
| PK category_id    |<------| FK category_id      |
| FK parent_id (self)|      | FK book_id          |-----> book
|    name           |       | PK (category_id,    |
|    depth          |       |     book_id)         |
|    sort_order     |       +---------------------+
|    created_at     |
+-------------------+
```

### 관계 요약

| 관계 | 카디널리티 | 설명 |
|------|-----------|------|
| member : book_order | 1 : N | 회원 한 명이 여러 주문 가능 |
| book_order : order_item | 1 : N | 주문 하나에 여러 주문 항목 |
| book : order_item | 1 : N | 도서 하나가 여러 주문 항목에 포함 |
| member : review | 1 : N | 회원 한 명이 여러 리뷰 작성 가능 |
| book : review | 1 : N | 도서 하나에 여러 리뷰 |
| category : category | 1 : N (self) | 자기참조로 계층 구조 표현 |
| book : category | M : N | 도서는 여러 카테고리에 속할 수 있음 (book_category 중간 테이블) |

---

## 2. 테이블 정의 (DDL)

### 2.1 member (회원)

```sql
CREATE TABLE member (
    member_id    BIGINT       NOT NULL AUTO_INCREMENT,
    name         VARCHAR(50)  NOT NULL,
    email        VARCHAR(100) NOT NULL,
    password     VARCHAR(255) NOT NULL,
    grade        VARCHAR(20)  NOT NULL DEFAULT 'NORMAL',
    joined_at    DATE         NOT NULL,
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_member PRIMARY KEY (member_id),
    CONSTRAINT uq_member_email UNIQUE (email),
    CONSTRAINT chk_member_grade CHECK (grade IN ('NORMAL', 'SILVER', 'GOLD', 'VIP'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 2.2 book (도서)

```sql
CREATE TABLE book (
    book_id      BIGINT        NOT NULL AUTO_INCREMENT,
    title        VARCHAR(200)  NOT NULL,
    author       VARCHAR(100)  NOT NULL,
    publisher    VARCHAR(100)  NOT NULL,
    price        DECIMAL(10,0) NOT NULL,
    stock        INT           NOT NULL DEFAULT 0,
    isbn         VARCHAR(13)   NOT NULL,
    published_at DATE          NULL,
    description  TEXT          NULL,
    created_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_book PRIMARY KEY (book_id),
    CONSTRAINT uq_book_isbn UNIQUE (isbn),
    CONSTRAINT chk_book_price CHECK (price >= 0),
    CONSTRAINT chk_book_stock CHECK (stock >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 2.3 category (카테고리 - 계층 구조)

```sql
CREATE TABLE category (
    category_id  BIGINT      NOT NULL AUTO_INCREMENT,
    parent_id    BIGINT      NULL,
    name         VARCHAR(50) NOT NULL,
    depth        TINYINT     NOT NULL DEFAULT 0,
    sort_order   INT         NOT NULL DEFAULT 0,
    created_at   DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_category PRIMARY KEY (category_id),
    CONSTRAINT fk_category_parent FOREIGN KEY (parent_id)
        REFERENCES category (category_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- depth: 0 = 대분류, 1 = 중분류, 2 = 소분류
```

### 2.4 book_category (도서-카테고리 매핑)

```sql
CREATE TABLE book_category (
    book_id      BIGINT NOT NULL,
    category_id  BIGINT NOT NULL,

    CONSTRAINT pk_book_category PRIMARY KEY (book_id, category_id),
    CONSTRAINT fk_bc_book FOREIGN KEY (book_id)
        REFERENCES book (book_id) ON DELETE CASCADE,
    CONSTRAINT fk_bc_category FOREIGN KEY (category_id)
        REFERENCES category (category_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 2.5 book_order (주문)

```sql
CREATE TABLE book_order (
    order_id     BIGINT        NOT NULL AUTO_INCREMENT,
    order_number VARCHAR(20)   NOT NULL,
    member_id    BIGINT        NOT NULL,
    order_date   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    address      VARCHAR(500)  NOT NULL,
    total_amount DECIMAL(12,0) NOT NULL,
    status       VARCHAR(20)   NOT NULL DEFAULT 'ORDERED',
    created_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_book_order PRIMARY KEY (order_id),
    CONSTRAINT uq_order_number UNIQUE (order_number),
    CONSTRAINT fk_order_member FOREIGN KEY (member_id)
        REFERENCES member (member_id) ON DELETE RESTRICT,
    CONSTRAINT chk_order_status CHECK (
        status IN ('ORDERED', 'PAID', 'SHIPPING', 'DELIVERED', 'CANCELLED', 'RETURNED')
    ),
    CONSTRAINT chk_order_amount CHECK (total_amount >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 2.6 order_item (주문 항목)

```sql
CREATE TABLE order_item (
    order_item_id BIGINT        NOT NULL AUTO_INCREMENT,
    order_id      BIGINT        NOT NULL,
    book_id       BIGINT        NOT NULL,
    quantity      INT           NOT NULL,
    unit_price    DECIMAL(10,0) NOT NULL,

    CONSTRAINT pk_order_item PRIMARY KEY (order_item_id),
    CONSTRAINT fk_oi_order FOREIGN KEY (order_id)
        REFERENCES book_order (order_id) ON DELETE CASCADE,
    CONSTRAINT fk_oi_book FOREIGN KEY (book_id)
        REFERENCES book (book_id) ON DELETE RESTRICT,
    CONSTRAINT chk_oi_quantity CHECK (quantity > 0),
    CONSTRAINT chk_oi_price CHECK (unit_price >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 2.7 review (리뷰)

```sql
CREATE TABLE review (
    review_id   BIGINT   NOT NULL AUTO_INCREMENT,
    member_id   BIGINT   NOT NULL,
    book_id     BIGINT   NOT NULL,
    rating      TINYINT  NOT NULL,
    content     TEXT     NULL,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_review PRIMARY KEY (review_id),
    CONSTRAINT fk_review_member FOREIGN KEY (member_id)
        REFERENCES member (member_id) ON DELETE CASCADE,
    CONSTRAINT fk_review_book FOREIGN KEY (book_id)
        REFERENCES book (book_id) ON DELETE CASCADE,
    CONSTRAINT uq_review_member_book UNIQUE (member_id, book_id),
    CONSTRAINT chk_review_rating CHECK (rating BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 3. 정규화 분석

### 3.1 제1정규형 (1NF) 충족

모든 컬럼이 원자값(atomic value)만 저장한다.

| 설계 결정 | 설명 |
|-----------|------|
| author 컬럼 | 공저자 관리가 필요하면 별도 author 테이블로 분리 가능. 현 설계에서는 단일 문자열로 처리 |
| address 컬럼 | 배송지를 단일 문자열로 저장. 우편번호/시/구 분리가 필요하면 정규화 대상 |

### 3.2 제2정규형 (2NF) 충족

모든 비키 속성이 기본키 전체에 완전 함수 종속한다.

| 테이블 | 분석 |
|--------|------|
| order_item | PK가 order_item_id(단일 컬럼)이므로 부분 종속 없음 |
| book_category | PK가 (book_id, category_id) 복합키이며, 추가 비키 속성이 없으므로 부분 종속 없음 |

### 3.3 제3정규형 (3NF) 충족

이행적 함수 종속이 존재하지 않는다.

| 설계 결정 | 설명 |
|-----------|------|
| order_item.unit_price | 주문 시점의 단가를 별도 저장. book.price에 종속시키지 않음 (가격 변동 이력 보존) |
| book_order.total_amount | 반정규화 항목. order_item의 SUM(quantity * unit_price)에서 유도 가능하나, 조회 성능을 위해 중복 저장. 애플리케이션 레벨에서 일관성 보장 필요 |
| category.depth | parent_id 체인에서 유도 가능하나, 계층 쿼리 성능을 위해 반정규화 |

### 3.4 반정규화 항목 정리

| 컬럼 | 사유 | 일관성 보장 방법 |
|------|------|----------------|
| book_order.total_amount | 주문 조회 시 매번 SUM 집계 회피 | 주문 항목 변경 시 트리거 또는 애플리케이션 로직으로 재계산 |
| category.depth | 계층 깊이 조회 빈도 높음 | 카테고리 이동 시 depth 재계산 |

---

## 4. 키 설계

### 4.1 기본키 (Primary Key)

| 테이블 | PK | 타입 | 전략 |
|--------|----|------|------|
| member | member_id | BIGINT AUTO_INCREMENT | 대리키 (Surrogate Key) |
| book | book_id | BIGINT AUTO_INCREMENT | 대리키 |
| category | category_id | BIGINT AUTO_INCREMENT | 대리키 |
| book_category | (book_id, category_id) | 복합키 | 자연 복합키 |
| book_order | order_id | BIGINT AUTO_INCREMENT | 대리키 |
| order_item | order_item_id | BIGINT AUTO_INCREMENT | 대리키 |
| review | review_id | BIGINT AUTO_INCREMENT | 대리키 |

**설계 근거:**
- 대부분의 테이블에서 AUTO_INCREMENT BIGINT 대리키를 사용하여 JOIN 성능 최적화
- book_category는 매핑 테이블이므로 복합 자연키가 적합
- order_item은 같은 주문에서 동일 도서가 포함될 수 있으나 별도 행으로 관리하므로 대리키 사용

### 4.2 후보키 / 유니크 제약조건

| 테이블 | 유니크 컬럼 | 설명 |
|--------|------------|------|
| member | email | 자연키 후보. 로그인 식별자 |
| book | isbn | 국제 표준 도서번호. 도서 고유 식별 |
| book_order | order_number | 외부 노출용 주문번호 (UUID 또는 날짜 기반 채번) |
| review | (member_id, book_id) | 한 회원이 한 도서에 하나의 리뷰만 작성 가능 |

### 4.3 외래키 (Foreign Key) 및 참조 동작

| FK | 참조 테이블 | ON DELETE | ON UPDATE | 사유 |
|----|-----------|-----------|-----------|------|
| book_order.member_id | member | RESTRICT | CASCADE | 주문이 있는 회원은 삭제 불가 |
| order_item.order_id | book_order | CASCADE | CASCADE | 주문 삭제 시 항목도 함께 삭제 |
| order_item.book_id | book | RESTRICT | CASCADE | 주문 항목이 있는 도서는 삭제 불가 |
| review.member_id | member | CASCADE | CASCADE | 회원 탈퇴 시 리뷰도 삭제 |
| review.book_id | book | CASCADE | CASCADE | 도서 삭제 시 리뷰도 삭제 |
| category.parent_id | category | RESTRICT | CASCADE | 하위 카테고리가 있으면 상위 삭제 불가 |
| book_category.book_id | book | CASCADE | CASCADE | 도서 삭제 시 매핑도 삭제 |
| book_category.category_id | category | CASCADE | CASCADE | 카테고리 삭제 시 매핑도 삭제 |

---

## 5. 인덱스 전략

### 5.1 인덱스 설계표

```sql
-- =========================================
-- member
-- =========================================
-- PK 클러스터드 인덱스: member_id (자동 생성)
-- UQ 인덱스: email (UNIQUE 제약조건에 의해 자동 생성)
CREATE INDEX idx_member_grade ON member (grade);
-- 용도: 등급별 회원 조회, 등급별 통계

CREATE INDEX idx_member_joined_at ON member (joined_at);
-- 용도: 기간별 가입 회원 조회

-- =========================================
-- book
-- =========================================
-- PK 클러스터드 인덱스: book_id (자동 생성)
-- UQ 인덱스: isbn (UNIQUE 제약조건에 의해 자동 생성)
CREATE INDEX idx_book_title ON book (title);
-- 용도: 제목 검색 (LIKE 'keyword%' 패턴)

CREATE INDEX idx_book_author ON book (author);
-- 용도: 저자 검색

CREATE INDEX idx_book_publisher ON book (publisher);
-- 용도: 출판사 검색

CREATE INDEX idx_book_price ON book (price);
-- 용도: 가격 범위 필터링

-- =========================================
-- category
-- =========================================
-- PK 클러스터드 인덱스: category_id (자동 생성)
CREATE INDEX idx_category_parent ON category (parent_id, sort_order);
-- 용도: 특정 부모 아래의 하위 카테고리를 정렬 순서대로 조회

CREATE INDEX idx_category_depth ON category (depth);
-- 용도: 특정 깊이의 카테고리 전체 조회 (대분류/중분류/소분류)

-- =========================================
-- book_category
-- =========================================
-- PK 클러스터드 인덱스: (book_id, category_id) (자동 생성)
CREATE INDEX idx_bc_category_book ON book_category (category_id, book_id);
-- 용도: 특정 카테고리의 도서 목록 조회 (커버링 인덱스)

-- =========================================
-- book_order
-- =========================================
-- PK 클러스터드 인덱스: order_id (자동 생성)
-- UQ 인덱스: order_number (UNIQUE 제약조건에 의해 자동 생성)
CREATE INDEX idx_order_member_date ON book_order (member_id, order_date DESC);
-- 용도: 회원별 최근 주문 목록

CREATE INDEX idx_order_status ON book_order (status);
-- 용도: 주문 상태별 조회 (배송 처리 등)

CREATE INDEX idx_order_date ON book_order (order_date);
-- 용도: 기간별 주문 통계, 관리자 조회

-- =========================================
-- order_item
-- =========================================
-- PK 클러스터드 인덱스: order_item_id (자동 생성)
CREATE INDEX idx_oi_order ON order_item (order_id);
-- 용도: 주문별 항목 조회 (FK 인덱스)

CREATE INDEX idx_oi_book ON order_item (book_id);
-- 용도: 도서별 판매 이력 조회

-- =========================================
-- review
-- =========================================
-- PK 클러스터드 인덱스: review_id (자동 생성)
-- UQ 인덱스: (member_id, book_id) (UNIQUE 제약조건에 의해 자동 생성)
CREATE INDEX idx_review_book_rating ON review (book_id, rating);
-- 용도: 도서별 리뷰 목록 + 평균 별점 (커버링 인덱스)

CREATE INDEX idx_review_created ON review (created_at DESC);
-- 용도: 최신 리뷰 조회
```

### 5.2 인덱스 전략 요약

| 전략 | 적용 대상 | 설명 |
|------|----------|------|
| 커버링 인덱스 | idx_bc_category_book, idx_review_book_rating | SELECT 대상 컬럼이 인덱스에 포함되어 테이블 접근 없이 처리 |
| 복합 인덱스 정렬 | idx_order_member_date | (member_id, order_date DESC)로 회원별 최근 주문을 인덱스 스캔만으로 정렬 |
| FK 인덱스 | idx_oi_order, idx_oi_book, idx_category_parent | FK 컬럼에 인덱스를 명시하여 JOIN 성능과 ON DELETE 성능 보장 |
| 선택도 기반 판단 | grade, status | 카디널리티가 낮지만 특정 값 필터링 빈도가 높아 인덱스 유지 |

### 5.3 풀텍스트 검색 (선택 사항)

도서 제목/설명에 대한 키워드 검색이 빈번하면 FULLTEXT 인덱스 추가를 고려한다.

```sql
ALTER TABLE book ADD FULLTEXT INDEX ft_book_search (title, description);
-- 용도: SELECT * FROM book WHERE MATCH(title, description) AGAINST('키워드' IN BOOLEAN MODE);
```

규모가 커지면 Elasticsearch 등 외부 검색 엔진 도입을 권장한다.

---

## 6. 카테고리 계층 구조 상세

### 인접 리스트 모델 (Adjacency List)

현 설계는 `parent_id` 자기참조 방식(인접 리스트)을 채택한다.

```
대분류 (depth=0)    중분류 (depth=1)       소분류 (depth=2)
+----------+       +-------------+       +-----------------+
| 문학      |------>| 한국 소설    |------>| 현대 소설        |
|          |       |             |       | 고전 소설        |
|          |       | 외국 소설    |------>| 영미 소설        |
|          |       |             |       | 일본 소설        |
+----------+       +-------------+       +-----------------+
| 과학      |------>| 물리학       |------>| 양자역학         |
|          |       | 생물학       |       | 상대성 이론      |
+----------+       +-------------+       +-----------------+
```

### 계층 쿼리 예시

```sql
-- MySQL 8.0+ : 재귀 CTE로 특정 카테고리의 모든 하위 카테고리 조회
WITH RECURSIVE category_tree AS (
    -- 앵커: 시작 카테고리
    SELECT category_id, name, parent_id, depth
    FROM category
    WHERE category_id = 1  -- '문학' 대분류

    UNION ALL

    -- 재귀: 하위 카테고리 탐색
    SELECT c.category_id, c.name, c.parent_id, c.depth
    FROM category c
    INNER JOIN category_tree ct ON c.parent_id = ct.category_id
)
SELECT * FROM category_tree;

-- 특정 카테고리(하위 포함)에 속한 도서 조회
WITH RECURSIVE category_tree AS (
    SELECT category_id FROM category WHERE category_id = 1
    UNION ALL
    SELECT c.category_id
    FROM category c
    INNER JOIN category_tree ct ON c.parent_id = ct.category_id
)
SELECT DISTINCT b.*
FROM book b
INNER JOIN book_category bc ON b.book_id = bc.book_id
INNER JOIN category_tree ct ON bc.category_id = ct.category_id;
```

### 대안 모델 비교

| 모델 | 장점 | 단점 | 적합 상황 |
|------|------|------|----------|
| 인접 리스트 (현재) | 구현 간단, 삽입/이동 용이 | 전체 경로 조회에 재귀 필요 | 깊이가 3 이하로 고정, 변경 빈번 |
| 경로 열거 (Path Enumeration) | 경로 조회 빠름 | 경로 문자열 관리 복잡 | 조회 위주, 변경 적음 |
| 중첩 집합 (Nested Set) | 하위 트리 조회 매우 빠름 | 삽입/삭제 시 전체 재정렬 | 읽기 위주, 변경 극히 드묾 |
| 클로저 테이블 (Closure Table) | 모든 조상/후손 관계 즉시 조회 | 별도 테이블 필요, 저장공간 증가 | 깊이 가변, 빈번한 계층 쿼리 |

대분류/중분류/소분류 3단계 고정 구조에서는 인접 리스트 모델이 충분하다. 계층이 깊어지거나 변경이 잦아지면 클로저 테이블로 전환을 고려한다.

---

## 7. 주요 쿼리 패턴과 인덱스 활용

| 쿼리 패턴 | 사용 인덱스 | 비고 |
|-----------|------------|------|
| 회원 로그인 (email 조회) | uq_member_email | 유니크 인덱스 |
| 도서 검색 (제목) | idx_book_title | prefix 매칭 또는 FULLTEXT |
| 카테고리별 도서 목록 | idx_bc_category_book + PK(book) | 커버링 인덱스로 book_id 획득 후 JOIN |
| 회원 주문 내역 | idx_order_member_date | 최신순 정렬 포함 |
| 주문 상세 조회 | PK(book_order) + idx_oi_order | 주문 -> 주문항목 JOIN |
| 도서별 리뷰/평점 | idx_review_book_rating | 커버링 인덱스로 AVG(rating) 계산 가능 |
| 관리자: 상태별 주문 | idx_order_status | 배송 처리 대상 조회 |
| 베스트셀러 집계 | idx_oi_book | book_id별 SUM(quantity) |
