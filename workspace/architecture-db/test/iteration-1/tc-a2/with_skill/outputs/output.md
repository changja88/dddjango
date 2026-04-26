# Schema Review: orders / product_reviews

## Review Findings

### 1. 정규화 위반

```
[3NF 위반 — 고객 정보 이행 종속] — orders 테이블에 customer_name, customer_email,
customer_phone이 직접 포함되어 있다. 고객은 여러 주문을 할 수 있으므로
id -> customer_email -> customer_name, customer_phone 이행 종속이 발생한다.
동일 고객이 10건 주문하면 이름/이메일/전화번호가 10번 중복 저장된다.
고객 전화번호가 변경되면 모든 주문 행을 갱신해야 하며, 누락 시 데이터 불일치가 발생한다
(갱신 이상). 고객 정보를 별도 customers 테이블로 분리해야 한다.
```

```
[3NF 위반 — 상품 정보 이행 종속] — orders 테이블에 product_name, product_price가
직접 포함되어 있다. 동일 상품이 여러 주문에 걸쳐 반복 저장된다.
상품 가격이나 이름이 변경되면 모든 관련 주문 행을 갱신해야 한다 (갱신 이상).
상품 정보를 별도 products 테이블로 분리해야 한다.
단, 주문 시점의 가격은 주문 테이블에 스냅샷으로 보관하는 것이 비즈니스적으로 올바르다
(역정규화가 아니라 도메인 요구사항).
```

```
[3NF 위반 — 카테고리 정보 이행 종속] — category_name, category_parent가 orders
테이블에 포함되어 있다. 카테고리는 상품에 종속되고, 상품은 주문에 종속되므로
id -> product -> category_name -> category_parent 이중 이행 종속이 발생한다.
카테고리를 별도 테이블로 분리하고, 상품 테이블에서 FK로 참조해야 한다.
```

```
[3NF 위반 — 배송 주소 이행 종속] — shipping_address, shipping_city, shipping_zipcode가
orders 테이블에 있다. shipping_zipcode -> shipping_city 함수적 종속이 존재할 수 있다
(우편번호가 도시를 결정). 동일 고객의 반복 주문 시 주소가 중복 저장된다.
주소를 별도 addresses 테이블로 분리하거나, 고객 테이블에 기본 주소를 두고
주문별 배송 주소는 스냅샷으로 보관하는 방안을 고려해야 한다.
```

```
[2NF 위반 — product_reviews의 product_name 부분 종속] — product_reviews 테이블에
product_name이 중복 저장되어 있다. 이 값은 order_id를 통해 orders에서 이미 조회
가능하다. 상품명이 변경되면 orders와 product_reviews 양쪽 모두 갱신해야 하며,
두 테이블 간 불일치가 발생할 수 있다.
```

```
[3NF 위반 — product_reviews의 리뷰어 정보 이행 종속] — reviewer_name, reviewer_email이
product_reviews에 직접 저장되어 있다. 리뷰어가 고객과 동일 인물이라면 orders의
customer_name, customer_email과 중복이며, 별도 인물이더라도 동일 리뷰어가 여러
리뷰를 작성하면 이름/이메일이 반복 저장된다 (갱신 이상).
```

### 2. 파생 컬럼 문제

```
[역정규화 — total_price 파생 컬럼] — total_price = product_price * quantity로
계산 가능한 파생 값이다. 별도 저장 시 product_price나 quantity가 변경될 때
total_price와의 동기화가 깨질 수 있다. 정규화 원칙상 계산 가능한 값은
저장하지 않는 것이 기본이며, 성능상 필요한 경우에만 파생 컬럼으로 추가하되
트리거 등으로 동기화를 보장해야 한다.
```

### 3. 계층 구조 패턴 부재

```
[계층 구조 패턴 미적용 — category_parent] — category_parent가 VARCHAR로 부모
카테고리의 이름을 저장하고 있다. 카테고리는 본질적으로 트리 구조(계층 데이터)이므로,
Adjacency List(parent_id FK), Materialized Path, 또는 Closure Table 패턴 중
적절한 것을 적용해야 한다. 현재 방식은 참조 무결성이 없고, 2단계 이상의 계층을
표현할 수 없다.
```

### 4. 누락된 외래 키 제약

```
[참조 무결성 — FK 제약 누락] — orders 테이블에 고객, 상품, 카테고리에 대한
FK 제약이 전혀 없다. 테이블 분리 후에도 FK를 명시하지 않으면 DB 수준에서
참조 무결성을 보장할 수 없다. 또한 cascading rule(ON DELETE, ON UPDATE)에 대한
정책도 정의되어 있지 않다.
```

### 5. 인덱스 부재

```
[인덱스 — 자주 조회되는 컬럼에 인덱스 없음] — 현재 PK 외에 어떤 인덱스도
정의되어 있지 않다. 정규화 후 분리된 테이블의 FK 컬럼, 그리고 자주 필터링될
가능성이 높은 컬럼들(order_date, status, customer_email 등)에 인덱스가 필요하다.
다만 인덱스는 실제 쿼리 워크로드를 확인한 후 설계하는 것이 원칙이다.
```

---

## Review Checklist 결과

| 항목 | 결과 |
|------|------|
| Missing or inappropriate primary keys | OK -- 양쪽 테이블 모두 SERIAL PK 존재 |
| Normalization violations (1NF-3NF) | **위반** -- 3NF 위반 다수 (고객, 상품, 카테고리, 주소, 리뷰어 정보 이행 종속), 2NF 위반 (product_reviews의 product_name 중복) |
| Missing indexes on frequently queried columns or JOIN keys | **위반** -- PK 외 인덱스 전무. FK 컬럼, status, order_date 등에 인덱스 필요 |
| Composite index with wrong column ordering | N/A -- 인덱스 자체가 없음 |
| N+1 query patterns in the access layer | N/A -- 쿼리/액세스 레이어 미제공 |
| Wrong isolation level for the use case | N/A -- 트랜잭션 레이어 미제공 |
| Hierarchical data stored without an appropriate pattern | **위반** -- category_parent가 VARCHAR로 저장, 계층 패턴 미적용 |
| Polymorphic associations without referential integrity strategy | OK -- 다형적 연관 해당 없음 |
| Premature denormalization (before measuring performance) | **위반** -- total_price 파생 컬럼이 정당한 사유 없이 포함 |
| Missing foreign key constraints or cascading rules | **위반** -- 고객/상품/카테고리 FK 제약 없음, cascading rule 미정의 |

---

## 요약

이 스키마는 전형적인 **비정규화된 단일 테이블 설계**이다. 가장 심각한 문제는 다수의 3NF 위반으로, 고객/상품/카테고리/주소 정보가 모두 orders 테이블에 직접 내장되어 있어 대규모 데이터에서 갱신 이상(update anomaly), 삽입 이상(insert anomaly), 삭제 이상(delete anomaly)이 불가피하다.

정규화 우선 순위:
1. **customers** 테이블 분리 (customer_name, customer_email, customer_phone)
2. **products** 테이블 분리 (product_name, product_price)
3. **categories** 테이블 분리 + 계층 패턴 적용 (category_name, parent_id FK)
4. **addresses** 테이블 분리 또는 주문별 배송 주소 스냅샷 전략 결정
5. **product_reviews**에서 product_name, reviewer_name, reviewer_email 제거 (FK 참조로 대체)
6. total_price 파생 컬럼 제거 또는 동기화 전략 수립
