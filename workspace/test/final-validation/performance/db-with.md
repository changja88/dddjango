# 주문-상품-카테고리 DB 스키마 설계

## 개념적 모델 (ERD)

```
[Category] 1---N [Category]         (자기참조: 상위 카테고리)
[Category] 1---N [Product]          (카테고리에 상품이 속함)
[Customer] 1---N [Order]            (고객이 주문함)
[Order]    1---N [OrderItem]        (주문에 여러 주문항목)
[Product]  1---N [OrderItem]        (상품이 여러 주문항목에 포함)
```

핵심 관계:
- Customer : Order = 1:N (고객은 여러 주문 가능, 주문은 반드시 고객이 있어야 함)
- Order : OrderItem = 1:N (주문은 여러 항목 포함)
- Product : OrderItem = 1:N (상품은 여러 주문항목에 포함)
- Category : Product = 1:N (카테고리에 여러 상품 소속)
- Category : Category = 1:N (자기참조, 계층 구조)

Order와 Product의 관계는 N:M이지만, 주문 시점의 가격/수량을 기록해야 하므로
OrderItem을 중간 테이블로 사용하여 1:N + N:1로 분해한다.

## 논리적 모델 (정규화된 스키마)

```sql
CREATE TABLE customers (
    customer_id BIGINT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    category_id BIGINT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id BIGINT REFERENCES categories(category_id),
    depth SMALLINT NOT NULL DEFAULT 0
);

CREATE TABLE products (
    product_id BIGINT PRIMARY KEY,
    category_id BIGINT NOT NULL REFERENCES categories(category_id),
    name VARCHAR(200) NOT NULL,
    price DECIMAL(12, 2) NOT NULL CHECK (price >= 0),
    stock_quantity INT NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(customer_id),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    total_amount DECIMAL(14, 2) NOT NULL CHECK (total_amount >= 0),
    ordered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    order_item_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(order_id),
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(12, 2) NOT NULL CHECK (unit_price >= 0)
);
```

## 정규화 수준 분석

이 스키마는 **3NF**를 충족한다.

| 정규형 | 충족 여부 | 근거 |
|--------|:---------:|------|
| **1NF** | O | 모든 컬럼이 원자값, 각 행이 PK로 고유 식별, 반복 그룹 없음 |
| **2NF** | O | 모든 비주요 속성이 전체 기본키에 완전 함수 종속 (대리키 사용으로 부분 종속 불가) |
| **3NF** | O | 이행 종속 없음 (예: 카테고리명은 categories에, 상품명은 products에 분리) |

의도적 비정규화 포인트:
- `orders.total_amount`: 파생 컬럼으로, 주문 조회 시마다 order_items를 집계하는 비용을 피한다. 주문 생성 트랜잭션 내에서 계산하여 동기화한다.
- `order_items.unit_price`: 주문 시점의 가격을 스냅샷으로 보관한다. products.price가 변경되어도 과거 주문 금액이 변하지 않아야 하므로 이것은 비정규화가 아닌 비즈니스 요구사항이다.

카테고리 계층은 **Adjacency List** 패턴을 적용했다. 카테고리 트리는 빈번한 구조 변경(추가/이동)이 발생하고 깊이가 보통 3~4단계로 제한되므로, 단순하고 갱신이 쉬운 Adjacency List가 적합하다. 하위 트리 조회는 `WITH RECURSIVE` CTE로 처리한다.

## 물리적 모델 (인덱싱 전략)

인덱스 설계는 테이블 구조가 아닌 쿼리 워크로드를 따른다. 아래는 예상되는 주요 쿼리 패턴에 대응하는 인덱스다.

```sql
-- 1. 고객의 주문 이력 조회 (customer_id = ? ORDER BY ordered_at DESC)
CREATE INDEX idx_orders_customer_date ON orders (customer_id, ordered_at DESC);

-- 2. 주문 상태별 필터링 (status = ? AND ordered_at > ?)
--    등호 조건(status)을 범위 조건(ordered_at)보다 앞에 배치
CREATE INDEX idx_orders_status_date ON orders (status, ordered_at);

-- 3. 주문항목 -> 주문 JOIN (order_id로 빈번한 조인)
CREATE INDEX idx_order_items_order ON order_items (order_id);

-- 4. 주문항목 -> 상품 JOIN
CREATE INDEX idx_order_items_product ON order_items (product_id);

-- 5. 카테고리별 상품 목록 (category_id = ? AND status = 'active')
CREATE INDEX idx_products_category_status ON products (category_id, status);

-- 6. 카테고리 계층 탐색 (parent_id로 자식 조회)
CREATE INDEX idx_categories_parent ON categories (parent_id);

-- 7. 활성 상품만 대상으로 하는 부분 인덱스 (상품 검색 최적화)
CREATE INDEX idx_products_active_name ON products (name)
    WHERE status = 'active';
```

인덱스 설계 근거:

| 인덱스 | 패턴 | 근거 |
|--------|------|------|
| `idx_orders_customer_date` | 복합 인덱스 | 고객별 최신 주문 조회에 등호+정렬 최적화 |
| `idx_orders_status_date` | 복합 인덱스 | 등호 조건을 범위 조건보다 앞에 배치하여 B+Tree 탐색 효율화 |
| `idx_order_items_order` | FK 인덱스 | 주문 상세 조회 시 order_id JOIN 가속 |
| `idx_order_items_product` | FK 인덱스 | 상품별 판매 이력 조회 가속 |
| `idx_products_category_status` | 복합 인덱스 | 카테고리 페이지에서 활성 상품 필터링 |
| `idx_categories_parent` | FK 인덱스 | 계층 탐색 CTE 가속 |
| `idx_products_active_name` | 부분 인덱스 | 비활성 상품 제외로 인덱스 크기 절감, 활성 상품 검색 가속 |

## 트랜잭션 격리 수준

| 트랜잭션 | 권장 격리 수준 | 근거 |
|----------|:--------------:|------|
| **주문 생성** (재고 차감 + 주문/항목 삽입 + 총액 계산) | **Read Committed** | 대부분의 OLTP에 적합한 기본 격리 수준. 재고 차감의 동시성 제어는 행 수준 잠금(`SELECT ... FOR UPDATE`)으로 처리하여 격리 수준을 올리지 않고도 정합성을 확보한다. |
| **주문 조회** (고객 주문 이력, 주문 상세) | **Read Committed** | 단순 읽기 작업으로 높은 격리 수준 불필요. |
| **재고 일괄 조정** (배치 처리) | **Repeatable Read** | 일관된 스냅샷에서 재고를 읽고 조정해야 하므로 Non-Repeatable Read 방지 필요. 직렬화 실패 시 재시도 로직을 구현한다. |
| **정산/매출 리포트** (집계 쿼리) | **Repeatable Read** | 리포트 실행 중 데이터 변경이 결과에 영향을 주지 않도록 일관된 스냅샷 보장. |
| **결제 처리** (금액 확정 + 결제 상태 변경) | **Serializable** | 금융 정확성이 최우선. 동시 결제로 인한 이중 차감 방지. 반드시 재시도 로직을 구현한다. |

주문 생성 트랜잭션 예시:

```sql
BEGIN;  -- Read Committed

SELECT stock_quantity FROM products WHERE product_id = 101 FOR UPDATE;
-- 행 잠금으로 동시 재고 차감 방지

UPDATE products SET stock_quantity = stock_quantity - 2 WHERE product_id = 101;

INSERT INTO orders (order_id, customer_id, status, total_amount, ordered_at)
VALUES (1001, 501, 'pending', 59800.00, CURRENT_TIMESTAMP);

INSERT INTO order_items (order_item_id, order_id, product_id, quantity, unit_price)
VALUES (10001, 1001, 101, 2, 29900.00);

COMMIT;
```

---
> **관련 스킬 참조:**
> - [Django ORM으로 이 스키마를 구현하기 (모델, QuerySet, select_related)] → **implementation-django** 스킬
> - [도메인 모델 설계 (주문 애그리거트, 바운디드 컨텍스트 경계)] → **architecture-ddd** 스킬
> - [주문/상품 REST API 엔드포인트 설계 (페이지네이션, 상태 코드)] → **architecture-api** 스킬
