# 온라인 서점 데이터베이스 스키마 설계

---

## 1. 개념적 데이터 모델링 (ERD)

### 1.1 엔티티 식별

| 엔티티 | 핵심 속성 |
|--------|----------|
| Member | name, email, joined_at, grade |
| Book | title, author, publisher, price, stock_quantity |
| Order | order_number, ordered_at, shipping_address, total_amount, status |
| OrderItem | quantity, unit_price |
| Review | rating, content, created_at |
| Category | name, depth |

### 1.2 관계 및 Cardinality

```
Member (1) ----< (N) Order           회원은 여러 주문을 가진다
Order  (1) ----< (N) OrderItem       주문은 여러 주문 항목을 가진다
Book   (1) ----< (N) OrderItem       도서는 여러 주문 항목에 포함된다
Member (1) ----< (N) Review          회원은 여러 리뷰를 작성한다
Book   (1) ----< (N) Review          도서는 여러 리뷰를 가진다
Book   (N) >----< (N) Category       도서는 여러 카테고리에 속하고,
                                     카테고리도 여러 도서를 가진다 (M:N)
Category (1) ----< (N) Category      카테고리는 자기참조 계층 구조를 가진다
```

### 1.3 Optionality

| 관계 | 좌측 | 우측 | 설명 |
|------|------|------|------|
| Member - Order | 필수 | 선택 | 주문에는 반드시 회원이 있어야 하지만, 회원은 주문이 없을 수 있다 |
| Order - OrderItem | 필수 | 필수 | 주문에는 최소 1개 항목이 있어야 한다 |
| Book - OrderItem | 필수 | 선택 | 주문 항목에는 반드시 도서가 있어야 하지만, 도서는 주문되지 않을 수 있다 |
| Member - Review | 필수 | 선택 | 리뷰에는 반드시 작성자가 있어야 하지만, 회원은 리뷰를 작성하지 않을 수 있다 |
| Book - Review | 필수 | 선택 | 리뷰에는 반드시 도서가 있어야 하지만, 도서는 리뷰가 없을 수 있다 |
| Category (parent-child) | 선택 | 선택 | 최상위 카테고리는 부모가 없다 |

### 1.4 ERD 다이어그램

```
┌──────────────┐         ┌──────────────────┐         ┌──────────────┐
│   Member     │         │     Order        │         │  OrderItem   │
├──────────────┤         ├──────────────────┤         ├──────────────┤
│ PK member_id │───1:N──>│ PK order_id      │───1:N──>│ PK item_id   │
│    name      │         │ FK member_id     │         │ FK order_id  │
│    email (UQ)│         │    order_number  │         │ FK book_id   │
│    joined_at │         │    ordered_at    │         │    quantity   │
│    grade     │         │    shipping_addr │         │    unit_price │
└──────┬───────┘         │    total_amount  │         └──────────────┘
       │                 │    status        │                │
       │                 └──────────────────┘                │
       │                                                     │
       │ 1:N                                            N:1  │
       v                                                     v
┌──────────────┐                                   ┌──────────────┐
│   Review     │                                   │    Book      │
├──────────────┤                                   ├──────────────┤
│ PK review_id │                              ┌───>│ PK book_id   │
│ FK member_id │                              │    │    title     │
│ FK book_id   │──────────────────────────N:1──┘    │    author    │
│    rating    │                                   │    publisher │
│    content   │                                   │    price     │
│    created_at│                                   │    stock_qty │
└──────────────┘                                   └──────┬───────┘
                                                          │
                                                     N:M  │
                                                          v
                                                  ┌──────────────┐
                              ┌──────────────┐    │ BookCategory │
                              │  Category    │    ├──────────────┤
                              ├──────────────┤    │ FK book_id   │
                              │ PK cat_id    │<───│ FK cat_id    │
                              │ FK parent_id │    └──────────────┘
                              │    name      │
                              │    depth     │
                              └──────────────┘
                              (self-referencing)
```

---

## 2. 논리적 데이터 모델링 (정규화 & 키 설계)

### 2.1 키 설계

모든 테이블에 surrogate key(BIGINT AUTO INCREMENT)를 기본키로 사용한다. 자연키 후보가 존재하는 경우에도 surrogate key를 채택하고, 자연키에는 UNIQUE 제약을 건다.

| 테이블 | PK (Surrogate) | 자연키 후보 / UNIQUE 제약 |
|--------|----------------|-------------------------|
| member | member_id | email (UNIQUE) |
| book | book_id | ISBN 등이 있다면 UNIQUE |
| order | order_id | order_number (UNIQUE) |
| order_item | item_id | (order_id, book_id) UNIQUE |
| review | review_id | (member_id, book_id) UNIQUE -- 1인 1리뷰 정책 |
| category | category_id | (parent_id, name) UNIQUE -- 같은 부모 아래 동명 카테고리 방지 |
| book_category | (book_id, category_id) 복합 PK | -- |

### 2.2 정규화 검증

**1NF 검증**: 모든 컬럼이 원자값이다. shipping_address는 단일 텍스트 필드로 저장한다(주소 검색이 필요하면 별도 테이블로 분리 가능하나, 현재 요구사항에서는 불필요).

**2NF 검증**: 복합키를 사용하는 book_category 테이블에서 추가 속성이 없으므로 부분 종속이 발생하지 않는다. order_item의 unit_price는 주문 시점의 가격 스냅샷이므로 book_id가 아니라 해당 주문 항목 자체에 종속된다 -- 2NF 위반이 아니다.

**3NF 검증**: 이행 종속을 확인한다.
- member 테이블의 grade는 member_id에 직접 종속 -- 이행 종속 없음.
- order 테이블의 total_amount는 파생 가능한 값(SUM(quantity * unit_price))이지만, 주문 확정 시점의 스냅샷으로서 order_id에 직접 종속되므로 역정규화에 해당하지 않는다. 할인, 쿠폰 등 복합 계산이 개입되므로 주문 테이블에 보존하는 것이 실용적이다.

모든 테이블이 3NF를 만족한다.

### 2.3 M:N 관계 해소

도서-카테고리 간 M:N 관계는 book_category 교차 테이블로 해소한다. 이 테이블은 (book_id, category_id) 복합 기본키를 사용하며 추가 속성이 없으므로 정규형 위반이 없다.

### 2.4 카테고리 계층 구조

대분류 > 중분류 > 소분류의 3단계 계층이 요구된다. 계층 패턴 선택 기준:

- 카테고리는 비교적 작은 트리 (수백~수천 개)
- 카테고리 변경(추가/이동)은 드물고, 읽기가 매우 빈번하다
- 특정 카테고리의 하위 카테고리 전체 조회가 필요하다

**선택: Adjacency List + depth 컬럼**

3단계 고정 계층이고 트리 크기가 작으므로, 가장 단순한 Adjacency List로 충분하다. depth 컬럼을 추가하여 대/중/소분류를 명시적으로 구분하고, 하위 트리 조회는 WITH RECURSIVE CTE로 처리한다. 트리가 커지거나 복잡한 조상/자손 쿼리가 빈번해지면 Closure Table로 전환을 고려한다.

---

## 3. 물리적 데이터 모델링 (DDL)

```sql
-- ============================================================
-- 회원
-- ============================================================
CREATE TABLE member (
    member_id    BIGINT       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    email        VARCHAR(255) NOT NULL,
    joined_at    DATE         NOT NULL DEFAULT CURRENT_DATE,
    grade        VARCHAR(20)  NOT NULL DEFAULT 'NORMAL',
    CONSTRAINT uq_member_email UNIQUE (email),
    CONSTRAINT ck_member_grade CHECK (grade IN ('NORMAL','SILVER','GOLD','VIP'))
);

-- ============================================================
-- 카테고리 (Adjacency List)
-- ============================================================
CREATE TABLE category (
    category_id  BIGINT       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    parent_id    BIGINT       REFERENCES category(category_id),
    depth        SMALLINT     NOT NULL DEFAULT 0,
    CONSTRAINT uq_category_parent_name UNIQUE (parent_id, name),
    CONSTRAINT ck_category_depth CHECK (depth BETWEEN 0 AND 2)
);

-- ============================================================
-- 도서
-- ============================================================
CREATE TABLE book (
    book_id        BIGINT        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title          VARCHAR(500)  NOT NULL,
    author         VARCHAR(200)  NOT NULL,
    publisher      VARCHAR(200)  NOT NULL,
    price          NUMERIC(10,2) NOT NULL,
    stock_quantity INT           NOT NULL DEFAULT 0,
    CONSTRAINT ck_book_price CHECK (price >= 0),
    CONSTRAINT ck_book_stock CHECK (stock_quantity >= 0)
);

-- ============================================================
-- 도서-카테고리 (M:N 교차 테이블)
-- ============================================================
CREATE TABLE book_category (
    book_id      BIGINT NOT NULL REFERENCES book(book_id),
    category_id  BIGINT NOT NULL REFERENCES category(category_id),
    PRIMARY KEY (book_id, category_id)
);

-- ============================================================
-- 주문
-- ============================================================
CREATE TABLE "order" (
    order_id         BIGINT        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    member_id        BIGINT        NOT NULL REFERENCES member(member_id),
    order_number     VARCHAR(30)   NOT NULL,
    ordered_at       TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    shipping_address TEXT          NOT NULL,
    total_amount     NUMERIC(12,2) NOT NULL,
    status           VARCHAR(20)   NOT NULL DEFAULT 'PENDING',
    CONSTRAINT uq_order_number UNIQUE (order_number),
    CONSTRAINT ck_order_status CHECK (status IN ('PENDING','PAID','SHIPPED','DELIVERED','CANCELLED')),
    CONSTRAINT ck_order_total CHECK (total_amount >= 0)
);

-- ============================================================
-- 주문 항목
-- ============================================================
CREATE TABLE order_item (
    item_id    BIGINT        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id   BIGINT        NOT NULL REFERENCES "order"(order_id),
    book_id    BIGINT        NOT NULL REFERENCES book(book_id),
    quantity   INT           NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    CONSTRAINT uq_order_item UNIQUE (order_id, book_id),
    CONSTRAINT ck_item_quantity CHECK (quantity > 0),
    CONSTRAINT ck_item_price CHECK (unit_price >= 0)
);

-- ============================================================
-- 리뷰
-- ============================================================
CREATE TABLE review (
    review_id  BIGINT    GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    member_id  BIGINT    NOT NULL REFERENCES member(member_id),
    book_id    BIGINT    NOT NULL REFERENCES book(book_id),
    rating     SMALLINT  NOT NULL,
    content    TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_review_member_book UNIQUE (member_id, book_id),
    CONSTRAINT ck_review_rating CHECK (rating BETWEEN 1 AND 5)
);
```

---

## 4. 인덱스 전략

인덱스 설계는 쿼리 워크로드를 기반으로 한다. 온라인 서점의 주요 접근 패턴을 분석하고, 각 패턴에 맞는 인덱스를 설계한다.

### 4.1 예상 쿼리 워크로드

| # | 접근 패턴 | 빈도 | 조건 유형 |
|---|----------|------|----------|
| Q1 | 도서 제목 검색 | 매우 높음 | LIKE 'keyword%' |
| Q2 | 카테고리별 도서 목록 | 높음 | 등호 (category_id) |
| Q3 | 도서 상세 + 리뷰 목록 | 높음 | 등호 (book_id) + 정렬 (created_at DESC) |
| Q4 | 회원 주문 내역 조회 | 높음 | 등호 (member_id) + 정렬 (ordered_at DESC) |
| Q5 | 주문번호로 주문 조회 | 높음 | 등호 (order_number) -- UNIQUE 인덱스 이미 존재 |
| Q6 | 주문 상태별 필터 | 보통 | 등호 (status) + 범위 (ordered_at) |
| Q7 | 도서별 평균 별점 집계 | 보통 | 등호 (book_id) + 집계 (AVG(rating)) |
| Q8 | 카테고리 하위 트리 조회 | 보통 | 등호 (parent_id) |
| Q9 | 저자별 도서 목록 | 보통 | 등호/LIKE (author) |

### 4.2 인덱스 설계

```sql
-- ============================================================
-- FK 인덱스 (JOIN 키에 인덱스가 없으면 성능 저하)
-- PK와 UNIQUE 제약에 의해 자동 생성되는 인덱스를 제외하고,
-- FK 컬럼에 명시적으로 인덱스를 생성한다.
-- ============================================================
CREATE INDEX idx_order_member          ON "order"(member_id);
CREATE INDEX idx_order_item_order      ON order_item(order_id);
CREATE INDEX idx_order_item_book       ON order_item(book_id);
CREATE INDEX idx_review_book           ON review(book_id);
CREATE INDEX idx_review_member         ON review(member_id);
CREATE INDEX idx_book_category_cat     ON book_category(category_id);
CREATE INDEX idx_category_parent       ON category(parent_id);

-- ============================================================
-- 쿼리 워크로드 기반 인덱스
-- ============================================================

-- Q1: 도서 제목 검색 (prefix LIKE)
CREATE INDEX idx_book_title ON book(title varchar_pattern_ops);

-- Q3: 도서별 리뷰 목록 (최신순 정렬)
-- 커버링 인덱스: book_id(등호) -> created_at(정렬) + rating(SELECT)
CREATE INDEX idx_review_book_date ON review(book_id, created_at DESC)
    INCLUDE (rating, member_id);

-- Q4: 회원 주문 내역 (최신순 정렬)
-- 복합 인덱스: member_id(등호) -> ordered_at(범위/정렬)
CREATE INDEX idx_order_member_date ON "order"(member_id, ordered_at DESC);

-- Q6: 주문 상태별 필터 (등호 + 범위)
-- 등호 조건(status)을 범위 조건(ordered_at) 앞에 배치
CREATE INDEX idx_order_status_date ON "order"(status, ordered_at DESC);

-- Q7: 도서별 평균 별점 집계
-- 커버링 인덱스: 테이블 룩업 없이 집계 가능
CREATE INDEX idx_review_book_rating ON review(book_id) INCLUDE (rating);

-- Q9: 저자별 도서 목록
CREATE INDEX idx_book_author ON book(author);
```

### 4.3 인덱스 설계 근거 정리

| 인덱스 | 쿼리 | 설계 원칙 |
|--------|------|----------|
| idx_order_member_date | Q4 | 복합 인덱스 컬럼 순서: 등호(member_id) -> 범위/정렬(ordered_at) |
| idx_order_status_date | Q6 | 등호(status) 컬럼을 범위(ordered_at) 컬럼보다 앞에 배치 |
| idx_review_book_date | Q3 | 커버링 인덱스: INCLUDE로 SELECT 컬럼 포함하여 테이블 룩업 제거 |
| idx_review_book_rating | Q7 | 커버링 인덱스: 집계에 필요한 rating을 INCLUDE하여 Index-Only Scan 유도 |
| FK 인덱스들 | JOIN | FK 컬럼에 인덱스가 없으면 JOIN 시 Seq Scan 발생 |

### 4.4 인덱스를 생성하지 않은 이유

| 대상 | 사유 |
|------|------|
| member.grade | 카디널리티가 매우 낮다(4개 값). 인덱싱 효과가 미미하다. |
| member.joined_at | 가입일 기준 검색이 빈번하지 않다. 필요 시 추가한다. |
| order.total_amount | 금액 범위 검색이 주요 패턴이 아니다. 필요 시 추가한다. |
| book.price | 가격 범위 필터가 빈번해지면 추가를 고려한다. |

---

## 5. 설계 요약

### 5.1 테이블 목록

| # | 테이블 | 역할 | PK |
|---|--------|------|-----|
| 1 | member | 회원 정보 | member_id (surrogate) |
| 2 | book | 도서 정보 | book_id (surrogate) |
| 3 | category | 카테고리 계층 (Adjacency List) | category_id (surrogate) |
| 4 | book_category | 도서-카테고리 M:N 교차 | (book_id, category_id) 복합 PK |
| 5 | order | 주문 정보 | order_id (surrogate) |
| 6 | order_item | 주문 항목 (주문-도서 연결) | item_id (surrogate) |
| 7 | review | 도서 리뷰 | review_id (surrogate) |

### 5.2 핵심 설계 결정

| 결정 | 근거 |
|------|------|
| Surrogate key 채택 | 모든 테이블에 자연키 대신 BIGINT 인조키 사용. 자연키(email, order_number)에는 UNIQUE 제약 |
| order_item.unit_price 보존 | 주문 시점의 가격 스냅샷. 도서 가격 변경이 과거 주문에 영향을 주지 않도록 분리 |
| order.total_amount 보존 | 할인/쿠폰 등 복합 계산이 개입되므로 주문 확정 시점의 최종 금액을 저장 |
| Adjacency List for category | 3단계 고정 계층, 소규모 트리, 변경 드묾. 가장 단순한 패턴으로 충분 |
| review에 (member_id, book_id) UNIQUE | 1인 1리뷰 비즈니스 규칙을 DB 레벨에서 강제 |
| 등호-범위 순서의 복합 인덱스 | 최좌선 접두사 규칙 + 등호 조건 우선 배치 원칙 적용 |
| 커버링 인덱스 활용 | 리뷰 목록/집계 쿼리에서 테이블 룩업 I/O 제거 |
