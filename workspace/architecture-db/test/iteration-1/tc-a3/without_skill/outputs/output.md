# sales_report 테이블 정규화 분석

## 1. 원본 테이블 함수 종속성 분석

원본 `sales_report` 테이블에서 식별되는 함수 종속성(FD)은 다음과 같다.

| 함수 종속성 | 설명 |
|---|---|
| `salesperson_name -> salesperson_dept` | 영업사원이 결정되면 소속 부서가 결정됨 |
| `salesperson_dept -> dept_manager` | 부서가 결정되면 부서장이 결정됨 (이행적 종속) |
| `salesperson_name -> dept_manager` | 이행적 종속: 사원 -> 부서 -> 부서장 |
| `customer_name -> customer_city, customer_region` | 고객이 결정되면 도시/지역이 결정됨 |
| `customer_city -> customer_region` | 도시가 결정되면 지역이 결정됨 (이행적 종속) |
| `product_name -> product_category, unit_price` | 상품이 결정되면 카테고리와 단가가 결정됨 |
| `{id} -> quantity, discount_rate` | 판매 건별 고유 속성 |
| `(unit_price, quantity, discount_rate) -> total_amount, tax_amount, net_amount` | 계산 파생 컬럼 |

## 2. 정규화 단계별 진행

### 2-1. 제1정규형 (1NF) -- 원본이 이미 충족

원본 테이블은 모든 컬럼이 원자값(atomic value)이므로 1NF을 만족한다.

### 2-2. 제2정규형 (2NF) -- 원본이 이미 충족

기본키가 `id` 단일 컬럼이므로 부분 종속이 존재하지 않는다. 2NF을 만족한다.

### 2-3. 제3정규형 (3NF) -- 이행적 종속 제거 필요

다음 이행적 종속이 존재하여 3NF을 위반한다.

- `id -> salesperson_name -> salesperson_dept -> dept_manager`
- `id -> customer_name -> customer_city -> customer_region`
- `id -> product_name -> product_category, unit_price`

### 2-4. 정규화 결론: 3NF까지 정규화

BCNF 이상의 정규화는 이 스키마에서 실익이 없다. 3NF이면 갱신 이상(update anomaly)을 충분히 제거할 수 있고, 실무 OLTP 환경에서도 3NF가 표준적 목표이다.

---

## 3. 3NF 정규화 결과 스키마

```sql
-- ============================================
-- 지역 테이블 (도시 -> 지역 이행적 종속 분리)
-- ============================================
CREATE TABLE regions (
    region_id SERIAL PRIMARY KEY,
    region_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE cities (
    city_id SERIAL PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    region_id INTEGER NOT NULL REFERENCES regions(region_id),
    UNIQUE (city_name, region_id)
);

-- ============================================
-- 부서 테이블 (부서 -> 부서장 종속 분리)
-- ============================================
CREATE TABLE departments (
    dept_id SERIAL PRIMARY KEY,
    dept_name VARCHAR(50) NOT NULL UNIQUE,
    dept_manager VARCHAR(100)
);

-- ============================================
-- 영업사원 테이블
-- ============================================
CREATE TABLE salespersons (
    salesperson_id SERIAL PRIMARY KEY,
    salesperson_name VARCHAR(100) NOT NULL,
    dept_id INTEGER NOT NULL REFERENCES departments(dept_id)
);

CREATE INDEX idx_salespersons_dept ON salespersons(dept_id);

-- ============================================
-- 고객 테이블
-- ============================================
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    city_id INTEGER NOT NULL REFERENCES cities(city_id)
);

CREATE INDEX idx_customers_city ON customers(city_id);

-- ============================================
-- 상품 테이블
-- ============================================
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    product_category VARCHAR(100) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL
);

CREATE INDEX idx_products_category ON products(product_category);

-- ============================================
-- 판매 트랜잭션 테이블 (팩트 테이블)
-- ============================================
CREATE TABLE sales (
    sale_id SERIAL PRIMARY KEY,
    sale_date DATE NOT NULL,
    salesperson_id INTEGER NOT NULL REFERENCES salespersons(salesperson_id),
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    discount_rate DECIMAL(3,2) NOT NULL DEFAULT 0.00,
    total_amount DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2) NOT NULL,
    net_amount DECIMAL(10,2) NOT NULL
);

CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_sales_salesperson ON sales(salesperson_id);
CREATE INDEX idx_sales_customer ON sales(customer_id);
CREATE INDEX idx_sales_product ON sales(product_id);
-- 월별 매출 조회 빈번 -> 연-월 복합 인덱스
CREATE INDEX idx_sales_year_month ON sales(DATE_TRUNC('month', sale_date));
```

### ERD 관계 요약

```
regions 1 --- * cities
cities  1 --- * customers
departments 1 --- * salespersons

salespersons 1 --- * sales
customers    1 --- * sales
products     1 --- * sales
```

---

## 4. 파생 컬럼(total_amount, tax_amount, net_amount) 처리 판단

`total_amount`, `tax_amount`, `net_amount`는 다음과 같이 계산 가능한 파생 컬럼이다.

```
total_amount = unit_price * quantity * (1 - discount_rate)
tax_amount   = total_amount * tax_rate
net_amount   = total_amount - tax_amount
```

엄밀한 정규화에서는 이 세 컬럼을 제거하고 조회 시 계산해야 한다. 그러나 아래 이유로 **역정규화하여 유지하는 것을 권장**한다.

| 판단 근거 | 설명 |
|---|---|
| 조회 빈도 | 월별 매출, 영업사원별 실적 집계에서 매번 SUM/계산이 필요 |
| 계산 비용 | 대량 데이터 집계 시 매 행마다 곱셈/뺄셈은 성능 부담 |
| 시점 고정 | 판매 시점의 금액을 확정값으로 기록해야 함 (단가/세율 변경 가능성) |
| 감사 추적 | 금융/매출 데이터는 계산 결과를 확정 저장하는 것이 실무 관행 |

따라서 `sales` 테이블에 `total_amount`, `tax_amount`, `net_amount`를 그대로 유지한다.

---

## 5. 역정규화 판단

주어진 조건: **월별 매출 조회가 매우 빈번하고, 영업사원별 실적 집계도 자주 수행**

### 5-1. 역정규화가 필요하지 않은 부분

| 항목 | 이유 |
|---|---|
| `departments`, `regions`, `cities` | 소규모 마스터 테이블이므로 JOIN 비용이 극히 낮음 |
| `customers`, `products` | 적절한 인덱스만으로 JOIN 성능 확보 가능 |

### 5-2. 역정규화를 권장하는 부분

#### (A) 월별 매출 집계 요약 테이블 (Materialized View 또는 Summary Table)

월별 매출 조회가 매우 빈번하므로, 매 조회마다 `sales` 전체를 스캔하는 대신 사전 집계 테이블을 둔다.

```sql
CREATE TABLE monthly_sales_summary (
    summary_id SERIAL PRIMARY KEY,
    sale_year INTEGER NOT NULL,
    sale_month INTEGER NOT NULL,
    salesperson_id INTEGER NOT NULL REFERENCES salespersons(salesperson_id),
    total_sales_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    total_tax_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    total_net_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    sale_count INTEGER NOT NULL DEFAULT 0,
    UNIQUE (sale_year, sale_month, salesperson_id)
);

CREATE INDEX idx_monthly_summary_period
    ON monthly_sales_summary(sale_year, sale_month);
CREATE INDEX idx_monthly_summary_sp
    ON monthly_sales_summary(salesperson_id);
```

이 테이블은 다음 중 하나의 방식으로 유지한다.
- **트리거 기반**: `sales` INSERT/UPDATE/DELETE 시 자동 갱신
- **배치 기반**: 일별/시간별 배치 작업으로 재집계
- **Materialized View**: `REFRESH MATERIALIZED VIEW`로 갱신 (PostgreSQL)

#### (B) sales 테이블에 salesperson_name 역정규화는 하지 않는다

영업사원 이름을 `sales`에 중복 저장하면 조회 시 JOIN을 줄일 수 있지만, `salespersons` 테이블이 소규모이고 인덱스 JOIN이 충분히 빠르므로 갱신 이상 위험 대비 이점이 적다.

---

## 6. 최종 정리

| 항목 | 결정 |
|---|---|
| 정규화 수준 | **3NF** (BCNF 이상 불필요) |
| 파생 컬럼 (금액) | **역정규화 유지** -- 시점 고정, 집계 성능, 감사 추적 |
| 월별 집계 | **역정규화 권장** -- `monthly_sales_summary` 요약 테이블 추가 |
| 마스터 테이블 JOIN | **역정규화 불필요** -- 소규모 테이블, 인덱스로 충분 |
| 인덱스 전략 | `sale_date`, `salesperson_id` 중심 인덱스 구성 |

### 최종 테이블 목록 (7개)

1. `regions` -- 지역 마스터
2. `cities` -- 도시 마스터
3. `departments` -- 부서 마스터
4. `salespersons` -- 영업사원 마스터
5. `customers` -- 고객 마스터
6. `products` -- 상품 마스터
7. `sales` -- 판매 트랜잭션 (팩트)
8. `monthly_sales_summary` -- 월별 집계 (역정규화 요약 테이블)
