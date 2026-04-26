# 주문 Aggregate의 물리적 테이블 매핑: 정규화 수준과 인덱스 전략

## 전제: DDD 도메인 모델 구조

참조 자료의 주문 Aggregate 구조를 기준으로 한다.

```
Order (Aggregate Root)
  ├── id: str (식별자)
  ├── orderer_id: str (Member Aggregate를 ID로 참조 -- Vernon 규칙 3)
  ├── order_lines: List[OrderLineItem] (값 객체 컬렉션)
  │     ├── product_id: str
  │     ├── product_name: str
  │     ├── price: Money (값 객체)
  │     └── quantity: int
  ├── shipping_info: ShippingInfo (값 객체)
  │     ├── receiver_name: str
  │     ├── receiver_phone: str
  │     └── address: Address (값 객체)
  │           ├── city: str
  │           ├── street: str
  │           └── zipcode: str
  ├── status: OrderStatus (enum)
  └── total_amounts: Money (파생 값)
```

---

## 1. 정규화 수준 결정

### 1.1 기본 원칙: 3NF를 기본으로 하되, Aggregate 경계를 존중한다

정규화의 기본 원칙은 "먼저 정규화하고, 측정된 성능이 요구할 때만 비정규화한다"이다. 주문 Aggregate에 3NF를 적용하면 다음과 같이 매핑된다.

```sql
-- 1. 주문 테이블 (Aggregate Root)
CREATE TABLE orders (
    id              VARCHAR(36)  PRIMARY KEY,
    orderer_id      VARCHAR(36)  NOT NULL,       -- Member Aggregate FK (ID 참조)
    status          VARCHAR(20)  NOT NULL DEFAULT 'payment_waiting',
    total_amount    INTEGER      NOT NULL,
    total_currency  VARCHAR(3)   NOT NULL DEFAULT 'KRW',

    -- ShippingInfo 값 객체: 임베디드 매핑 (Aggregate 내부이므로 같은 테이블)
    receiver_name   VARCHAR(100) NOT NULL,
    receiver_phone  VARCHAR(20)  NOT NULL,
    address_city    VARCHAR(50)  NOT NULL,
    address_street  VARCHAR(200) NOT NULL,
    address_zipcode VARCHAR(10)  NOT NULL,

    created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. 주문 항목 테이블 (Aggregate 내부 값 객체 컬렉션)
CREATE TABLE order_line_items (
    id              BIGSERIAL    PRIMARY KEY,    -- 대리키 (컬렉션 관리용)
    order_id        VARCHAR(36)  NOT NULL REFERENCES orders(id),
    product_id      VARCHAR(36)  NOT NULL,       -- Product Aggregate FK (ID 참조)
    product_name    VARCHAR(200) NOT NULL,        -- 주문 시점 스냅샷
    price_amount    INTEGER      NOT NULL,
    price_currency  VARCHAR(3)   NOT NULL DEFAULT 'KRW',
    quantity        INTEGER      NOT NULL CHECK (quantity > 0),
    line_amount     INTEGER      NOT NULL         -- 파생 컬럼 (price * quantity)
);
```

### 1.2 매핑 결정의 근거

| 도메인 개념 | 테이블 매핑 방식 | 정규화 수준 | 근거 |
|------------|----------------|------------|------|
| `Order` (Root) | `orders` 테이블 | 3NF | Aggregate Root는 독립 테이블. 모든 속성이 PK에 완전 함수 종속 |
| `ShippingInfo` (값 객체) | `orders`에 임베디드 | 3NF 유지 | 1:1 관계의 값 객체는 별도 테이블 불필요. JOIN 제거 |
| `Address` (값 객체) | `orders`에 접두사로 임베디드 | 3NF 유지 | ShippingInfo의 구성요소. `address_` 접두사로 네임스페이스 분리 |
| `OrderLineItem` (값 객체 컬렉션) | `order_line_items` 테이블 | 3NF | 1:N 관계이므로 별도 테이블 필수. 반복 그룹 제거 (1NF) |
| `Money` (값 객체) | 컬럼 쌍으로 임베디드 | 3NF 유지 | `amount` + `currency` 두 컬럼으로 펼침 |
| `product_name` | `order_line_items`에 중복 저장 | 의도적 비정규화 | 주문 시점 상품명 스냅샷. 상품명 변경이 과거 주문에 영향 불가 |
| `total_amount` | `orders`에 저장 | 파생 컬럼 | 빈번한 조회 vs 재계산 비용. 동기화는 Aggregate 내부 불변식이 보장 |
| `line_amount` | `order_line_items`에 저장 | 파생 컬럼 | price * quantity 계산 결과 캐싱. Aggregate가 일관성 보장 |

### 1.3 정규화에서 핵심 판단 포인트

**값 객체의 임베디드 vs 별도 테이블 결정 기준:**

```
1:1 값 객체 (ShippingInfo, Address, Money)
  -> Aggregate Root 테이블에 컬럼으로 임베디드
  -> JOIN 불필요, 3NF 위반 아님 (해당 Order에만 종속)

1:N 값 객체 컬렉션 (OrderLineItem)
  -> 별도 테이블 분리 필수
  -> 1NF: 반복 그룹 제거
  -> 2NF: 모든 비주요 속성이 전체 키에 종속

N:M 관계
  -> 중간 테이블(매핑 테이블) 필요
```

**`product_name` 비정규화는 정당한가?**

이것은 일반적인 비정규화가 아니라 도메인 요구사항이다. 주문 시점의 상품명을 기록해야 하므로, Product 테이블과 JOIN해서 가져오면 현재 상품명이 반환되어 비즈니스 요구사항을 위반한다. 이것은 "이벤트 시점 스냅샷" 패턴이며, 3NF 위반이 아니라 서로 다른 사실을 기록하는 것이다.

### 1.4 과도한 정규화의 함정: Aggregate 경계를 깨지 말 것

```sql
-- 나쁜 예: ShippingInfo를 별도 테이블로 분리
CREATE TABLE shipping_info (
    id         BIGSERIAL    PRIMARY KEY,
    order_id   VARCHAR(36)  UNIQUE NOT NULL REFERENCES orders(id),
    receiver_name  VARCHAR(100),
    ...
);
-- 문제: Aggregate 내부 값 객체에 대해 불필요한 JOIN 발생
-- 문제: ShippingInfo에 독립적인 ID를 부여하면 값 객체의 정체성 없음 원칙 위반

-- 좋은 예: Aggregate Root에 임베디드
-- orders 테이블에 receiver_name, receiver_phone, address_* 컬럼으로 포함
```

DDD에서 Aggregate는 트랜잭션 경계이다. Aggregate 내부 구성요소를 지나치게 정규화하여 별도 테이블로 분리하면, 하나의 트랜잭션에서 여러 테이블을 UPDATE해야 하는 불필요한 복잡성이 생긴다. **1:1 값 객체는 임베디드가 원칙**이다.

---

## 2. 인덱스 전략

### 2.1 인덱스 설계의 기본 원칙

인덱스는 테이블 구조가 아닌 **쿼리 워크로드**를 따른다. 먼저 주문 시스템의 핵심 쿼리 패턴을 식별한 후 인덱스를 설계한다.

### 2.2 주문 시스템 핵심 쿼리 패턴과 인덱스

```sql
-- ============================================================
-- orders 테이블 인덱스
-- ============================================================

-- Q1: 특정 회원의 주문 목록 (마이페이지) -- 가장 빈번
-- SELECT * FROM orders WHERE orderer_id = ? ORDER BY created_at DESC
CREATE INDEX idx_orders_orderer_created
    ON orders (orderer_id, created_at DESC);
-- 근거: 등호(orderer_id) 먼저, 범위/정렬(created_at) 나중
--       최좌선 접두사 규칙에 의해 orderer_id 단독 조회도 지원

-- Q2: 상태별 주문 조회 (관리자 화면, 배치 처리)
-- SELECT * FROM orders WHERE status = ? AND created_at > ? ORDER BY created_at
CREATE INDEX idx_orders_status_created
    ON orders (status, created_at);
-- 근거: 등호(status) 먼저, 범위(created_at) 나중

-- Q3: 미처리 주문만 조회 (부분 인덱스)
-- SELECT * FROM orders WHERE status = 'payment_waiting'
CREATE INDEX idx_orders_payment_waiting
    ON orders (created_at)
    WHERE status = 'payment_waiting';
-- 근거: 전체 주문 중 미결제 주문은 소수. 부분 인덱스로 크기와 유지비용 절감

-- ============================================================
-- order_line_items 테이블 인덱스
-- ============================================================

-- Q4: 주문 상세 조회 (주문 ID로 항목 로딩)
-- SELECT * FROM order_line_items WHERE order_id = ?
CREATE INDEX idx_line_items_order
    ON order_line_items (order_id);
-- 근거: Repository가 Aggregate를 로딩할 때 order_id로 JOIN/조회
--       FK에 대한 인덱스는 DELETE CASCADE 성능에도 필수

-- Q5: 특정 상품의 주문 이력 (상품 분석)
-- SELECT * FROM order_line_items WHERE product_id = ?
CREATE INDEX idx_line_items_product
    ON order_line_items (product_id);
-- 근거: 상품별 판매 통계, 상품 삭제 전 참조 확인 등
```

### 2.3 인덱스 설계 결정 요약

| 인덱스 | 유형 | 대상 쿼리 | 핵심 설계 원칙 |
|--------|------|----------|--------------|
| `idx_orders_orderer_created` | 복합 인덱스 | 회원별 주문 목록 | 등호 -> 범위 순서, 최좌선 접두사 |
| `idx_orders_status_created` | 복합 인덱스 | 상태별 주문 관리 | 등호 -> 범위 순서 |
| `idx_orders_payment_waiting` | 부분 인덱스 | 미결제 주문 처리 | 소수 행만 인덱싱, 유지비용 절감 |
| `idx_line_items_order` | 단일 인덱스 | Aggregate 로딩 | FK 인덱스, JOIN 성능 |
| `idx_line_items_product` | 단일 인덱스 | 상품별 분석 | 역방향 조회 지원 |

### 2.4 인덱스를 만들지 않는 것에 대한 판단

| 후보 | 결정 | 이유 |
|------|------|------|
| `orders(created_at)` 단독 | 불필요 | `idx_orders_status_created`와 `idx_orders_orderer_created`가 커버. 단독 시간 범위 검색은 드물고, 필요시 RDBMS가 기존 인덱스를 bitmap scan으로 조합 가능 |
| `orders(total_amount)` | 불필요 | 금액 범위 검색은 OLAP 성격. OLTP에서 빈번하지 않음 |
| `order_line_items(product_name)` | 불필요 | 상품명 검색은 Product 테이블에서 수행. 주문 내 스냅샷 검색은 비정상 패턴 |
| `orders(status)` 단독 | 불필요 | 저카디널리티(4-5개 값). `idx_orders_status_created` 복합 인덱스가 최좌선 접두사로 커버 |

### 2.5 읽기/쓰기 비율에 따른 조정

```
주문 생성 (INSERT) 대비 주문 조회 (SELECT) 비율:
  - 일반적 커머스: 읽기 >> 쓰기 (10:1 ~ 100:1)
  -> 인덱스를 충분히 추가해도 쓰기 성능 저하가 체감되지 않음

쓰기 집중 시나리오 (대량 주문 유입, 배치 상태 변경):
  -> 부분 인덱스 활용으로 인덱스 유지 비용 최소화
  -> 불필요한 인덱스 정기 감사 (pg_stat_user_indexes 등)
```

---

## 3. 트랜잭션 경계와 격리 수준

### 3.1 Aggregate = 트랜잭션 경계

Vernon 규칙 1에 따라 하나의 트랜잭션에서 하나의 Aggregate만 수정한다. 주문 생성 시 `orders` INSERT와 `order_line_items` INSERT는 같은 트랜잭션에 포함된다(같은 Aggregate 내부).

```python
# Repository 구현: Aggregate 단위로 저장
class SqlOrderRepository(OrderRepository):
    def save(self, order: Order) -> None:
        with self._session.begin():  # 단일 트랜잭션
            self._session.execute(
                insert(orders_table).values(...)
            )
            for line in order.order_lines:
                self._session.execute(
                    insert(order_line_items_table).values(...)
                )
```

### 3.2 격리 수준 권장

| 유스케이스 | 격리 수준 | 근거 |
|-----------|----------|------|
| 주문 생성/수정 | Read Committed | 대부분의 OLTP에 적합. 각 SQL 문이 최신 커밋 데이터를 읽음 |
| 결제 처리 | Serializable + 재시도 | 정확성 최우선. 동일 주문 중복 결제 방지 |
| 주문 목록 조회 | Read Committed | 약간의 비일관성 허용 가능 |

---

## 4. 최종 물리 스키마 (완성본)

```sql
-- ============================================================
-- 주문 Aggregate 물리 스키마
-- ============================================================

CREATE TABLE orders (
    -- Aggregate Root 식별자
    id              VARCHAR(36)  PRIMARY KEY,

    -- 타 Aggregate 참조 (Vernon 규칙 3: ID로만 참조)
    orderer_id      VARCHAR(36)  NOT NULL,

    -- 주문 상태
    status          VARCHAR(20)  NOT NULL DEFAULT 'payment_waiting',

    -- 총액 (파생 컬럼 -- Aggregate 불변식이 일관성 보장)
    total_amount    INTEGER      NOT NULL,
    total_currency  VARCHAR(3)   NOT NULL DEFAULT 'KRW',

    -- ShippingInfo 값 객체 (임베디드)
    receiver_name   VARCHAR(100) NOT NULL,
    receiver_phone  VARCHAR(20)  NOT NULL,

    -- Address 값 객체 (임베디드, 접두사로 네임스페이스 분리)
    address_city    VARCHAR(50)  NOT NULL,
    address_street  VARCHAR(200) NOT NULL,
    address_zipcode VARCHAR(10)  NOT NULL,

    -- 감사 컬럼
    created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- 제약 조건
    CONSTRAINT chk_order_status CHECK (
        status IN ('payment_waiting', 'preparing', 'shipped', 'delivered', 'cancelled')
    ),
    CONSTRAINT chk_total_amount CHECK (total_amount >= 0)
);

CREATE TABLE order_line_items (
    -- 대리키 (값 객체에 식별자가 없으므로 DB 관리용)
    id              BIGSERIAL    PRIMARY KEY,

    -- Aggregate Root 참조
    order_id        VARCHAR(36)  NOT NULL,

    -- 상품 정보 (주문 시점 스냅샷)
    product_id      VARCHAR(36)  NOT NULL,
    product_name    VARCHAR(200) NOT NULL,
    price_amount    INTEGER      NOT NULL,
    price_currency  VARCHAR(3)   NOT NULL DEFAULT 'KRW',
    quantity        INTEGER      NOT NULL,
    line_amount     INTEGER      NOT NULL,

    -- 제약 조건
    CONSTRAINT fk_line_items_order
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    CONSTRAINT chk_quantity CHECK (quantity > 0),
    CONSTRAINT chk_price CHECK (price_amount >= 0),
    CONSTRAINT chk_line_amount CHECK (line_amount >= 0)
);

-- ============================================================
-- 인덱스
-- ============================================================

-- 회원별 주문 목록 (등호 -> 정렬)
CREATE INDEX idx_orders_orderer_created
    ON orders (orderer_id, created_at DESC);

-- 상태별 주문 관리 (등호 -> 범위)
CREATE INDEX idx_orders_status_created
    ON orders (status, created_at);

-- 미결제 주문 처리 (부분 인덱스)
CREATE INDEX idx_orders_payment_waiting
    ON orders (created_at)
    WHERE status = 'payment_waiting';

-- Aggregate 로딩 (FK 인덱스)
CREATE INDEX idx_line_items_order
    ON order_line_items (order_id);

-- 상품별 주문 분석
CREATE INDEX idx_line_items_product
    ON order_line_items (product_id);
```

---

## 5. 핵심 결정 요약

| 결정 | 선택 | 트레이드오프 |
|------|------|------------|
| 정규화 수준 | 3NF 기본 | JOIN 비용 vs 데이터 무결성. 3NF가 균형점 |
| 1:1 값 객체 매핑 | 임베디드 (같은 테이블) | 컬럼 수 증가 vs JOIN 제거 + Aggregate 경계 유지 |
| 1:N 값 객체 매핑 | 별도 테이블 | JOIN 필요하지만 1NF 준수 필수 |
| product_name 스냅샷 | 의도적 비정규화 | 저장 공간 vs 주문 시점 데이터 보존 (도메인 요구사항) |
| total_amount 파생 컬럼 | 저장 | 동기화 위험 vs 빈번한 집계 쿼리 성능. Aggregate 불변식이 보장 |
| 복합 인덱스 순서 | 등호 컬럼 -> 범위 컬럼 | B+Tree 최좌선 접두사 규칙 준수 |
| 미결제 주문 인덱스 | 부분 인덱스 | 인덱스 크기 절감. 활성 주문만 인덱싱 |
| 격리 수준 | Read Committed (기본) | 동시성 vs 일관성. 결제는 Serializable |

---

## 스킬 위임 안내

- 도메인 모델 설계(Aggregate 설계 규칙, 값 객체/엔티티 구분, 바운디드 컨텍스트)에 대한 상세 가이드는 **architecture-ddd** 스킬을 참조하세요.
- 아키텍처 패턴(헥사고날, 클린, CQRS, Repository + UoW 구현)에 대한 상세 가이드는 **architecture-implementation-patterns** 스킬을 참조하세요.
- Django ORM 코드(QuerySet, select_related, 마이그레이션)에 대한 상세 가이드는 **implementation-django** 스킬을 참조하세요.
- EXPLAIN ANALYZE를 활용한 쿼리 최적화와 N+1 문제 해결에 대한 상세 가이드는 **architecture-db** 스킬의 쿼리 최적화 섹션을 참조하세요.
