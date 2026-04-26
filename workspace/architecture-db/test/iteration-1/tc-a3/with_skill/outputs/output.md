# sales_report 테이블 정규화 분석

## 1. 원본 테이블 분석

```sql
CREATE TABLE sales_report (
    id SERIAL PRIMARY KEY,
    sale_date DATE,
    salesperson_name VARCHAR(100),
    salesperson_dept VARCHAR(50),
    dept_manager VARCHAR(100),
    customer_name VARCHAR(100),
    customer_city VARCHAR(100),
    customer_region VARCHAR(50),
    product_name VARCHAR(200),
    product_category VARCHAR(100),
    unit_price DECIMAL(10,2),
    quantity INTEGER,
    discount_rate DECIMAL(3,2),
    total_amount DECIMAL(10,2),
    tax_amount DECIMAL(10,2),
    net_amount DECIMAL(10,2)
);
```

## 2. 함수적 종속 식별

원본 테이블에서 다음과 같은 함수적 종속이 존재한다.

```
salesperson_name -> salesperson_dept          (영업사원이 결정되면 부서가 결정됨)
salesperson_dept -> dept_manager              (부서가 결정되면 부서장이 결정됨)
salesperson_name -> dept_manager              (이행 종속: 사원 -> 부서 -> 부서장)

customer_name -> customer_city                (고객이 결정되면 도시가 결정됨)
customer_city -> customer_region              (도시가 결정되면 지역이 결정됨)
customer_name -> customer_region              (이행 종속: 고객 -> 도시 -> 지역)

product_name -> product_category              (상품이 결정되면 카테고리가 결정됨)
product_name -> unit_price                    (상품이 결정되면 단가가 결정됨)

(id) -> {sale_date, salesperson_name, customer_name, product_name, quantity, discount_rate}
(quantity, unit_price, discount_rate) -> total_amount, tax_amount, net_amount  (파생 속성)
```

## 3. 정규화 위반 진단

### 3NF 위반 -- 이행 종속

| 종속 경로 | 위반 유형 | 문제 |
|-----------|-----------|------|
| salesperson_name -> salesperson_dept -> dept_manager | 이행 종속 (3NF 위반) | 부서장 변경 시 모든 해당 매출 행을 갱신해야 함 (갱신 이상) |
| customer_name -> customer_city -> customer_region | 이행 종속 (3NF 위반) | 지역 분류 변경 시 다수 행 갱신 필요 (갱신 이상) |
| id -> product_name -> product_category | 이행 종속 (3NF 위반) | 카테고리 변경 시 불일치 위험 |
| id -> product_name -> unit_price | 이행 종속 (3NF 위반) | 가격 변경 시 과거 매출 데이터 오염 위험 |

### 파생 컬럼 중복

`total_amount`, `tax_amount`, `net_amount`는 `quantity * unit_price * (1 - discount_rate)` 등으로 계산 가능한 파생 값이다. 정규화 원칙상 제거 대상이지만, 역정규화 판단에서 다시 검토한다.

## 4. 정규화 결과 -- 3NF

정규화 대상: 3NF까지 수행한다. BCNF 위반은 현재 구조에서 발견되지 않으므로 3NF가 최종 목표다.

### 4.1 개념적 모델 (엔티티 관계)

```
[부서] 1 --- N [영업사원]
[영업사원] 1 --- N [매출]
[고객] 1 --- N [매출]
[지역] 1 --- N [도시]
[도시] 1 --- N [고객]
[상품] N --- 1 [카테고리]
[상품] 1 --- N [매출]
```

### 4.2 정규화된 스키마

```sql
-- 지역 (customer_city -> customer_region 이행 종속 제거)
CREATE TABLE regions (
    region_id SERIAL PRIMARY KEY,
    region_name VARCHAR(50) NOT NULL UNIQUE
);

-- 도시 (customer_city -> customer_region 분리)
CREATE TABLE cities (
    city_id SERIAL PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    region_id INTEGER NOT NULL REFERENCES regions(region_id),
    UNIQUE (city_name, region_id)
);

-- 고객
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    city_id INTEGER NOT NULL REFERENCES cities(city_id)
);

-- 부서 (salesperson_dept -> dept_manager 이행 종속 제거)
CREATE TABLE departments (
    dept_id SERIAL PRIMARY KEY,
    dept_name VARCHAR(50) NOT NULL UNIQUE,
    manager_name VARCHAR(100) NOT NULL
);

-- 영업사원
CREATE TABLE salespersons (
    salesperson_id SERIAL PRIMARY KEY,
    salesperson_name VARCHAR(100) NOT NULL,
    dept_id INTEGER NOT NULL REFERENCES departments(dept_id)
);

-- 상품 카테고리
CREATE TABLE product_categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
);

-- 상품 (product_name -> product_category 이행 종속 제거)
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category_id INTEGER NOT NULL REFERENCES product_categories(category_id),
    unit_price DECIMAL(10,2) NOT NULL
);

-- 매출 (핵심 트랜잭션 테이블)
CREATE TABLE sales (
    sale_id SERIAL PRIMARY KEY,
    sale_date DATE NOT NULL,
    salesperson_id INTEGER NOT NULL REFERENCES salespersons(salesperson_id),
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    discount_rate DECIMAL(3,2) NOT NULL DEFAULT 0.00,
    sale_unit_price DECIMAL(10,2) NOT NULL
);
```

### 4.3 변경 사항 요약

```
[Before]
단일 테이블 sales_report (16개 컬럼, 모든 속성이 하나의 테이블에 혼재)

[After]
7개 테이블로 분리: regions, cities, customers, departments,
salespersons, product_categories, products, sales

[Reason] 3NF 이행 종속 제거 -- 영업사원->부서->부서장, 고객->도시->지역,
상품->카테고리의 이행 종속을 제거하여 갱신/삽입/삭제 이상을 방지한다.
```

### 4.4 설계 결정 설명

**sale_unit_price를 sales 테이블에 포함한 이유:**
products.unit_price는 현재 단가이고, 매출 시점의 단가는 변할 수 있다. 매출 기록은 거래 시점의 가격을 보존해야 하므로 `sale_unit_price`를 sales 테이블에 별도로 저장한다. 이것은 역정규화가 아니라 서로 다른 사실(현재 가격 vs 거래 시점 가격)을 기록하는 것이다.

**total_amount, tax_amount, net_amount를 제거한 이유:**
이 세 컬럼은 `quantity * sale_unit_price * (1 - discount_rate)` 등으로 계산 가능한 파생 값이다. 정규화 원칙에 따라 제거하되, 아래 역정규화 판단에서 재검토한다.

## 5. 역정규화 판단

### 5.1 조회 워크로드 분석

사용자가 명시한 두 가지 빈번한 쿼리 패턴:

| # | 패턴 | 필요한 JOIN | 예상 비용 |
|---|------|------------|----------|
| 1 | 월별 매출 조회 | sales + products + customers + salespersons | 4-way JOIN |
| 2 | 영업사원별 실적 집계 | sales + salespersons + (departments) | 2~3-way JOIN, SUM 집계 |

### 5.2 역정규화 결정

스킬 원칙에 따라 최적화 순서는 **슬로우 쿼리 최적화 -> 인덱스 -> 캐시 -> 역정규화**이다. 바로 역정규화하지 않고, 먼저 인덱스로 해결 가능한지 평가한다.

#### 인덱스로 충분히 해결 가능한 부분

```sql
-- 패턴 1: 월별 매출 조회 (sale_date 범위 검색)
CREATE INDEX idx_sales_date ON sales (sale_date);

-- 패턴 2: 영업사원별 실적 집계 (등호 조건 + 범위 조건)
CREATE INDEX idx_sales_person_date ON sales (salesperson_id, sale_date);

-- FK 컬럼 인덱스 (JOIN 성능)
CREATE INDEX idx_sales_customer ON sales (customer_id);
CREATE INDEX idx_sales_product ON sales (product_id);
```

위 인덱스만으로 두 조회 패턴 모두 Index Scan 또는 Index-Only Scan이 가능하다.

#### 역정규화를 적용하는 부분: 파생 컬럼 (total_amount)

**적용 기법**: 파생 컬럼 추가

```sql
ALTER TABLE sales ADD COLUMN total_amount DECIMAL(10,2)
    GENERATED ALWAYS AS (quantity * sale_unit_price * (1 - discount_rate)) STORED;
```

**판단 근거:**
- 월별 매출 집계, 영업사원별 실적 집계 모두 `SUM(quantity * sale_unit_price * (1 - discount_rate))`를 매번 계산해야 한다.
- 집계 대상 행이 수만~수십만 행이 될 수 있으므로, 행마다 곱셈/뺄셈을 반복하는 것은 실질적인 비용이다.
- `GENERATED ALWAYS AS ... STORED` 컬럼은 데이터 정합성을 DB가 보장하므로 동기화 문제가 없다.
- 이것은 역정규화 기법 중 "파생 컬럼 추가"에 해당하지만, GENERATED 컬럼을 사용하면 대가(동기화 복잡도)를 최소화할 수 있다.

#### 역정규화를 적용하지 않는 부분

| 후보 | 판단 | 이유 |
|------|------|------|
| tax_amount, net_amount | 적용하지 않음 | 세금 계산 로직은 비즈니스 규칙 변경이 잦으므로 애플리케이션 레이어에서 처리. 필요 시 total_amount와 동일하게 GENERATED 컬럼으로 추가 가능 |
| 영업사원명을 sales에 병합 | 적용하지 않음 | `idx_sales_person_date` 인덱스 + salespersons JOIN으로 충분. 병합 시 이름 변경 갱신 이상 발생 |
| 부서명을 sales에 병합 | 적용하지 않음 | 부서 테이블은 소규모(수십~수백 건)이므로 JOIN 비용 무시 가능 |
| 고객 지역을 sales에 병합 | 적용하지 않음 | 지역별 집계가 빈번하다는 요건 없음. 인덱스로 충분 |

## 6. 최종 물리 스키마

```sql
-- 지역
CREATE TABLE regions (
    region_id SERIAL PRIMARY KEY,
    region_name VARCHAR(50) NOT NULL UNIQUE
);

-- 도시
CREATE TABLE cities (
    city_id SERIAL PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    region_id INTEGER NOT NULL REFERENCES regions(region_id),
    UNIQUE (city_name, region_id)
);

-- 고객
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    city_id INTEGER NOT NULL REFERENCES cities(city_id)
);

-- 부서
CREATE TABLE departments (
    dept_id SERIAL PRIMARY KEY,
    dept_name VARCHAR(50) NOT NULL UNIQUE,
    manager_name VARCHAR(100) NOT NULL
);

-- 영업사원
CREATE TABLE salespersons (
    salesperson_id SERIAL PRIMARY KEY,
    salesperson_name VARCHAR(100) NOT NULL,
    dept_id INTEGER NOT NULL REFERENCES departments(dept_id)
);

-- 상품 카테고리
CREATE TABLE product_categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
);

-- 상품
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category_id INTEGER NOT NULL REFERENCES product_categories(category_id),
    unit_price DECIMAL(10,2) NOT NULL
);

-- 매출 (역정규화: total_amount 파생 컬럼 포함)
CREATE TABLE sales (
    sale_id SERIAL PRIMARY KEY,
    sale_date DATE NOT NULL,
    salesperson_id INTEGER NOT NULL REFERENCES salespersons(salesperson_id),
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    discount_rate DECIMAL(3,2) NOT NULL DEFAULT 0.00,
    sale_unit_price DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) GENERATED ALWAYS AS
        (quantity * sale_unit_price * (1 - discount_rate)) STORED
);

-- 인덱스: 월별 매출 조회
CREATE INDEX idx_sales_date ON sales (sale_date);

-- 인덱스: 영업사원별 실적 집계 (등호 + 범위 순서)
CREATE INDEX idx_sales_person_date ON sales (salesperson_id, sale_date);

-- 인덱스: FK JOIN 최적화
CREATE INDEX idx_sales_customer ON sales (customer_id);
CREATE INDEX idx_sales_product ON sales (product_id);
```

## 7. 결정 요약

| 항목 | 결정 | 근거 |
|------|------|------|
| 정규화 수준 | 3NF | 이행 종속 3건 제거. BCNF 위반 없음 |
| 역정규화 | total_amount 파생 컬럼 1건만 적용 | 빈번한 집계 연산 비용 절감. GENERATED 컬럼으로 정합성 보장 |
| 테이블 병합 | 적용하지 않음 | 인덱스 + FK JOIN으로 충분. 병합 시 갱신 이상 위험 |
| 인덱스 | 4개 | 월별 조회(sale_date), 사원별 집계(salesperson_id, sale_date), FK 2개 |
