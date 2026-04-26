# Data Mapper 패턴에서의 테이블 스키마 정규화와 인덱스 설계

> 운영 모드: **설계**

## 핵심 답변

Data Mapper 패턴의 가장 큰 이점은 도메인 모델과 테이블 스키마가 **독립적으로 진화**할 수 있다는 것이다. 이 독립성 덕분에 테이블 스키마는 **관계형 데이터베이스의 원칙에 충실하게** 설계하면 된다. 도메인 객체의 구조에 스키마를 맞출 필요가 없다.

---

## 1. Data Mapper가 스키마 설계에 주는 자유도

Active Record에서는 모델 클래스와 테이블이 1:1로 강결합되므로, 객체 구조가 곧 테이블 구조가 된다. 반면 Data Mapper에서는 별도의 매핑 레이어가 도메인 객체와 DB 행 사이의 변환을 담당한다.

```
도메인 모델 (in-memory 객체)
       |
   Data Mapper ── 도메인 <-> DB 변환
       |
테이블 스키마 (관계형 원칙에 따라 독립 설계)
```

이것이 의미하는 바는 명확하다.

- **도메인 모델**: 비즈니스 로직 표현에 최적화. 값 객체, 컬렉션, 상속 등 객체지향 구조를 자유롭게 사용.
- **테이블 스키마**: 데이터 무결성과 쿼리 성능에 최적화. 정규화 수준, 인덱스 전략, 파티셔닝 등 관계형 원칙을 충실히 적용.
- **매핑 레이어**: 이 두 세계 사이의 임피던스 불일치를 해소.

따라서 "Data Mapper를 쓰는데 정규화는 어디까지?"라는 질문에 대한 답은: **Data Mapper를 안 쓸 때와 동일한 기준으로 정규화한다.** Data Mapper는 영속성 추상화 패턴이지 스키마 설계 패턴이 아니다.

---

## 2. 정규화 수준 결정 기준

### 2.1 기본 원칙: 먼저 정규화하고, 측정된 성능이 요구할 때만 비정규화한다

각 정규형은 특정 이상 현상을 순차적으로 제거한다.

| 정규형 | 조건 | 제거하는 문제 |
|--------|------|-------------|
| **1NF** | 모든 컬럼이 원자값, 행이 고유 식별 가능, 반복 그룹 없음 | 중첩/반복 데이터 |
| **2NF** | 1NF + 부분 종속 제거 (비주요 속성이 전체 복합키에 종속) | 복합키의 일부에만 종속하는 속성 |
| **3NF** | 2NF + 이행 종속 제거 (비주요 속성이 다른 비주요 속성에 종속 불가) | A->B->C에서 A->C 이행 종속 |
| **BCNF** | 3NF + 모든 함수적 종속 X->Y에서 X가 슈퍼키 | 후보키가 아닌 결정자 |

**실무 지침**: 대부분의 OLTP 시스템에서는 3NF까지 정규화하면 충분하다. BCNF는 복합키가 많고 후보키 간 교차 종속이 있는 특수한 경우에만 검토한다.

### 2.2 Data Mapper 환경에서의 정규화 적용 예시

도메인에 `Order` 애그리거트가 있고, 내부에 `ShippingAddress` 값 객체와 `OrderLine` 컬렉션을 포함한다고 가정한다.

**도메인 모델** (객체지향적 구조):
```python
@dataclass
class ShippingAddress:
    street: str
    city: str
    zip_code: str

@dataclass
class OrderLine:
    product_id: str
    quantity: int
    unit_price: Money

@dataclass
class Order:
    id: OrderId
    customer_id: CustomerId
    shipping_address: ShippingAddress
    lines: list[OrderLine]
    status: OrderStatus
```

**테이블 스키마** (관계형 원칙에 따른 설계):
```sql
-- 3NF 준수: 각 테이블이 하나의 주제만 담당
CREATE TABLE orders (
    id           BIGINT PRIMARY KEY,
    customer_id  BIGINT NOT NULL REFERENCES customers(id),
    -- 값 객체는 같은 테이블에 임베드 (별도 식별자가 없으므로)
    ship_street  VARCHAR(200) NOT NULL,
    ship_city    VARCHAR(100) NOT NULL,
    ship_zip     VARCHAR(20)  NOT NULL,
    status       VARCHAR(20)  NOT NULL,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- 1:N 관계는 별도 테이블로 분리 (1NF: 반복 그룹 제거)
CREATE TABLE order_lines (
    id           BIGINT PRIMARY KEY,
    order_id     BIGINT NOT NULL REFERENCES orders(id),
    product_id   BIGINT NOT NULL REFERENCES products(id),
    quantity     INT    NOT NULL CHECK (quantity > 0),
    unit_price   NUMERIC(12,2) NOT NULL
);
```

Data Mapper가 이 차이를 해소한다. 도메인의 `ShippingAddress` 값 객체는 `orders` 테이블의 컬럼들로 펼쳐지고, `lines` 컬렉션은 `order_lines` 테이블에서 조회하여 리스트로 조립된다. 도메인 모델은 스키마 구조를 전혀 알 필요가 없다.

### 2.3 비정규화 판단 기준

비정규화는 최후의 수단이다. 다음 순서를 반드시 먼저 시도한다.

```
1. 슬로우 쿼리 최적화    <- 가장 먼저 (비용 최소)
2. 인덱스 적용           <- 읽기 up, 쓰기 down 트레이드오프
3. 애플리케이션 캐시 활용  <- DB 부하 감소
4. 역정규화              <- 최후의 보루
```

비정규화를 적용하더라도 Data Mapper가 있으므로 **도메인 모델에는 영향이 없다**. 예를 들어 읽기 성능을 위해 `orders` 테이블에 `total_amount` 파생 컬럼을 추가해도, Data Mapper만 수정하면 도메인의 `Order` 클래스는 변경할 필요가 없다. 이것이 Data Mapper의 핵심 이점인 **스키마 유연성**이다.

---

## 3. 인덱스 설계

### 3.1 인덱스 설계 원칙: 테이블 구조가 아닌 쿼리 워크로드를 따른다

인덱스는 테이블이 어떻게 생겼는지가 아니라, **어떤 쿼리가 실행되는지**에 따라 설계한다.

### 3.2 복합 인덱스 컬럼 순서

**등호(=) 조건 컬럼을 범위 조건 컬럼보다 앞에 배치한다.**

```sql
-- 쿼리: WHERE status = 'active' AND created_at > '2024-01-01'

-- 좋음: 등호 컬럼 먼저
CREATE INDEX idx_orders_status_created ON orders (status, created_at);

-- 나쁨: 범위 컬럼이 먼저 -> status 필터에 인덱스 활용 불가
CREATE INDEX idx_orders_created_status ON orders (created_at, status);
```

**최좌선 접두사 규칙**: 인덱스 (A, B, C)는 (A), (A, B), (A, B, C) 필터 쿼리에 사용 가능하지만, (B)나 (C) 단독으로는 사용 불가하다. 가장 많은 쿼리를 서비스할 수 있도록 순서를 정한다.

### 3.3 커버링 인덱스

쿼리에 필요한 모든 컬럼을 인덱스에 포함하면, 힙 테이블 접근 없이 인덱스만으로 데이터를 반환한다.

```sql
-- 쿼리: SELECT email FROM users WHERE status = 'active'
-- 커버링 인덱스: 테이블 접근 불필요
CREATE INDEX idx_users_status_email ON users (status) INCLUDE (email);
```

### 3.4 부분 인덱스

WHERE 절로 행의 부분 집합만 인덱싱한다. 작은 인덱스 = 적은 저장소 + 빠른 스캔 + 저렴한 유지보수.

```sql
-- soft-delete 패턴: 활성 레코드에만 유니크 제약
CREATE UNIQUE INDEX uq_email_active ON users (email) WHERE deleted_at IS NULL;
```

### 3.5 Data Mapper 환경에서의 인덱스 설계 실무

Data Mapper 패턴에서 Repository는 도메인 의도를 표현하는 메서드를 제공한다 (`get`, `add`, `find_by_status` 등). 이 Repository 메서드들이 내부적으로 실행하는 SQL 쿼리가 곧 인덱스 설계의 입력이 된다.

```python
# Repository 인터페이스 (도메인 계층)
class AbstractOrderRepository(ABC):
    @abstractmethod
    def get(self, order_id: OrderId) -> Order | None: ...

    @abstractmethod
    def find_by_customer(self, customer_id: CustomerId) -> list[Order]: ...

    @abstractmethod
    def find_pending_before(self, cutoff: datetime) -> list[Order]: ...
```

위 인터페이스로부터 도출되는 인덱스 설계:

```sql
-- get(order_id): PK 인덱스로 충분 (자동 생성)

-- find_by_customer(customer_id): FK 컬럼에 인덱스
CREATE INDEX idx_orders_customer ON orders (customer_id);

-- find_pending_before(cutoff): 등호 조건 먼저, 범위 조건 뒤
CREATE INDEX idx_orders_status_created ON orders (status, created_at);
```

| 인덱스 설계 원칙 | 설명 |
|------|------|
| 높은 카디널리티 우선 | boolean, gender 같은 저카디널리티 컬럼은 인덱싱 효과 낮음 |
| 읽기/쓰기 비율 고려 | 읽기 중심이면 인덱스 추가, 쓰기 중심이면 인덱스 최소화 |
| 미사용 인덱스 감사 | 정기적으로 사용되지 않는 인덱스 확인 후 삭제 |
| 인덱스의 근본 트레이드오프 | 읽기 성능을 올리고 쓰기 성능을 희생시킨다. 모든 INSERT/UPDATE/DELETE는 관련된 모든 인덱스를 갱신해야 한다 |

---

## 4. 책임 분리 요약

Data Mapper 패턴을 적용하면 각 관심사의 책임이 명확히 분리된다.

| 관심사 | 책임 위치 | 최적화 기준 |
|--------|----------|------------|
| 도메인 모델 | 도메인 계층 | 비즈니스 로직 표현 |
| 객체-행 변환 | Data Mapper (인프라 계층) | 임피던스 불일치 해소 |
| 테이블 정규화 | 물리 스키마 | 데이터 무결성 (갱신/삽입/삭제 이상 방지) |
| 인덱스 설계 | 물리 스키마 | 쿼리 워크로드 성능 |
| 트랜잭션 경계 | Unit of Work | 일관성 보장 |
| 컬렉션 추상화 | Repository | 도메인 의도 표현 |

```
Service Layer
  |
  v
Unit of Work ──── 트랜잭션 경계 관리 (commit / rollback)
  |
  +-- Repository ──── 컬렉션 추상화 (add / get / list)
  |       |
  |       v
  |   Data Mapper ──── 도메인 <-> DB 변환
  |       |
  |       v
  |   Identity Map ──── 중복 로드 방지
  |
  v
Database (정규화된 스키마 + 쿼리 기반 인덱스)
```

결론적으로, Data Mapper는 "도메인 모델을 스키마 제약으로부터 해방"하는 패턴이다. 스키마 설계는 Data Mapper의 존재 여부와 무관하게 관계형 데이터베이스의 정규화 이론과 쿼리 워크로드 기반 인덱스 원칙을 그대로 따르면 된다. Data Mapper가 있기 때문에 스키마를 변경해도 도메인에 영향이 없고, 도메인을 변경해도 스키마에 영향이 없다 -- 이것이 Persistence Ignorance의 본질이다.

---

데이터베이스 스키마의 정규화, 인덱스, 쿼리 최적화에 대한 상세 가이드는 **architecture-db** 스킬을 참조하세요.

도메인 모델 설계(애그리거트, 값 객체, 바운디드 컨텍스트)에 대한 상세 가이드는 **architecture-ddd** 스킬을 참조하세요.

Django ORM에서의 영속성 패턴 적용(QuerySet, select_related, 마이그레이션)에 대한 상세 가이드는 **implementation-django** 스킬을 참조하세요.
