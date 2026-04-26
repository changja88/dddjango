# DB Schema Review - Normalization Analysis

## Target Schema

```sql
CREATE TABLE orders (...);
CREATE TABLE product_reviews (...);
```

## Identified Normalization Issues

### 1. 1NF Violation - Repeating Groups in `orders`

`orders` 테이블이 주문, 고객, 상품, 배송, 카테고리 정보를 모두 한 테이블에 담고 있다. 단일 엔티티가 아닌 여러 엔티티의 속성이 혼재되어 있다.

### 2. 2NF Violation - Partial Dependency

`orders` 테이블에서 다음 컬럼들은 주문 ID(PK)가 아닌 다른 엔티티에 종속된다.

| Column | Actual Dependency |
|---|---|
| `customer_name`, `customer_email`, `customer_phone` | customer에 종속 (주문이 아님) |
| `product_name`, `product_price` | product에 종속 (주문이 아님) |
| `category_name`, `category_parent` | category에 종속 (주문이 아님) |
| `shipping_city`, `shipping_zipcode` | shipping address에 종속 (주문이 아님) |

동일 고객이 10번 주문하면 `customer_name`, `customer_email`, `customer_phone`이 10번 중복 저장된다.

### 3. 3NF Violation - Transitive Dependency

- `category_parent`는 `category_name`에 종속되고, `category_name`은 product에 종속된다. 주문 PK와는 이행적 종속 관계이다.
- `shipping_city`와 `shipping_zipcode`는 `shipping_address`에 종속될 수 있는 이행적 종속이다.
- `total_price`는 `product_price * quantity`로 계산 가능한 파생 값(derived attribute)이다. 저장 시 불일치 위험이 있다.

### 4. `product_reviews` 테이블 문제

- `reviewer_name`, `reviewer_email`: 고객 정보의 중복 저장이다. `orders`에 이미 고객 정보가 있고, `order_id`로 참조 가능하다. 별도 users 테이블에서 관리해야 한다.
- `product_name`: `orders` 테이블에 이미 존재하는 값의 중복이다. `order_id` JOIN으로 조회 가능하다. 상품 테이블 분리 후 FK로 참조해야 한다.

## Practical Risks

| Risk | Description |
|---|---|
| Update Anomaly | 고객 이메일 변경 시 해당 고객의 모든 주문 레코드를 업데이트해야 함 |
| Insert Anomaly | 주문 없이는 상품이나 고객 정보를 등록할 수 없음 |
| Delete Anomaly | 주문 삭제 시 해당 상품/고객의 유일한 레코드라면 정보가 소실됨 |
| Data Inconsistency | `product_reviews.product_name`과 `orders.product_name`이 불일치할 수 있음 |
| Storage Waste | 동일 고객/상품 정보가 주문 수만큼 반복 저장됨 |

## Suggested Normalized Schema (3NF)

```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20)
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    parent_id INTEGER REFERENCES categories(id)
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    price DECIMAL(10,2),
    category_id INTEGER REFERENCES categories(id)
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER,
    unit_price DECIMAL(10,2),       -- 주문 시점 가격 snapshot
    order_date TIMESTAMP,
    shipping_address TEXT,
    shipping_city VARCHAR(100),
    shipping_zipcode VARCHAR(10),
    status VARCHAR(20)
);

CREATE TABLE product_reviews (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    customer_id INTEGER REFERENCES customers(id),
    product_id INTEGER REFERENCES products(id),
    rating INTEGER,
    review_text TEXT,
    created_at TIMESTAMP
);
```

### Key Changes

1. **customers** 분리 - 고객 정보 단일 관리, 중복 제거
2. **categories** 분리 - self-referencing FK로 계층 구조 표현 (category_parent 문자열 대체)
3. **products** 분리 - 상품 정보 단일 관리, category FK 연결
4. **orders.total_price 제거** - 파생 값은 `unit_price * quantity`로 계산. 필요 시 generated column이나 view 사용
5. **orders.unit_price 추가** - 주문 시점 가격을 보존 (products.price가 변경되어도 주문 이력 유지)
6. **product_reviews** - reviewer 중복 컬럼 제거, customer_id와 product_id FK로 대체
