# 주문 애그리거트 RDB 매핑: 정규화와 인덱스 전략

## 테이블 설계

주문 애그리거트의 구성요소를 RDB에 매핑할 때, DDD의 애그리거트 경계와 정규화
원칙을 동시에 만족시켜야 한다. 핵심 원칙은 두 가지다:

1. **애그리거트 루트가 테이블의 중심이다** -- Order가 루트이므로 `orders` 테이블이
   진입점이 되고, 내부 구성요소(OrderLineItem, ShippingInfo)는 종속 테이블로
   매핑한다.
2. **다른 애그리거트는 ID로만 참조한다** (Vernon 규칙 3) -- Member, Product 등
   외부 애그리거트는 FK가 아닌 ID 컬럼으로만 참조하여 결합도를 낮춘다.

### 정규화 전략

3NF를 기본으로 적용한다. 먼저 정규화하고, 측정된 성능이 요구할 때만 비정규화한다.

```sql
-- ============================================================
-- 1. 주문 (애그리거트 루트)
-- ============================================================
CREATE TABLE orders (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    orderer_id      UUID        NOT NULL,       -- Member 애그리거트 ID 참조 (FK 아님)
    status          VARCHAR(20) NOT NULL DEFAULT 'payment_waiting',
    total_amount    INTEGER     NOT NULL,        -- Money 값 객체 (amount)
    total_currency  VARCHAR(3)  NOT NULL DEFAULT 'KRW',  -- Money 값 객체 (currency)
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT chk_order_status CHECK (
        status IN ('payment_waiting', 'preparing', 'shipped', 'delivered', 'cancelled')
    ),
    CONSTRAINT chk_total_amount CHECK (total_amount >= 0)
);

-- ============================================================
-- 2. 주문 항목 (애그리거트 내부 값 객체 컬렉션)
--    Order와 1:N 관계. OrderLineItem은 Order 없이 존재하지 않는다.
-- ============================================================
CREATE TABLE order_line_items (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id        UUID        NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id      UUID        NOT NULL,       -- Product 애그리거트 ID 참조 (FK 아님)
    product_name    VARCHAR(200) NOT NULL,       -- 주문 시점 스냅샷 (비정규화 아님)
    price_amount    INTEGER     NOT NULL,        -- Money 값 객체
    price_currency  VARCHAR(3)  NOT NULL DEFAULT 'KRW',
    quantity        INTEGER     NOT NULL,
    line_amount     INTEGER     NOT NULL,        -- price_amount * quantity (파생값)

    CONSTRAINT chk_quantity CHECK (quantity > 0),
    CONSTRAINT chk_price CHECK (price_amount >= 0)
);

-- ============================================================
-- 3. 배송 정보 (애그리거트 내부 값 객체)
--    Order와 1:1 관계. 별도 테이블로 분리하는 이유:
--    - ShippingInfo는 개념적으로 독립된 값 객체 (Address 포함)
--    - orders 테이블의 컬럼 수를 줄여 주요 쿼리 경량화
--    - 배송 정보 변경이 빈번할 때 orders 행 갱신 범위 최소화
-- ============================================================
CREATE TABLE order_shipping_info (
    order_id        UUID        PRIMARY KEY REFERENCES orders(id) ON DELETE CASCADE,
    receiver_name   VARCHAR(100) NOT NULL,
    receiver_phone  VARCHAR(20) NOT NULL,
    city            VARCHAR(100) NOT NULL,       -- Address 값 객체 임베딩
    street          VARCHAR(200) NOT NULL,
    zipcode         VARCHAR(10) NOT NULL
);
```

**정규화 판단 근거:**

| 설계 결정 | 정규형 관점 | 근거 |
|-----------|------------|------|
| `product_name`을 order_line_items에 저장 | 비정규화가 아님 | 주문 시점의 상품명 스냅샷이다. Product의 현재 이름과 독립된 값이므로 함수적 종속이 다르다 |
| `line_amount` 파생 컬럼 | 의도적 비정규화 (파생 컬럼) | 주문 조회 시 매번 계산을 피하기 위함. 단, INSERT/UPDATE 시 애플리케이션에서 동기화 보장 필요 |
| ShippingInfo 별도 테이블 | 3NF 유지 | Address 값 객체를 orders에 인라인할 수 있으나, 개념적 윤곽에 따라 분리하면 orders 테이블 경량화 가능 |
| `orderer_id`에 FK 미설정 | DDD 원칙 | Vernon 규칙 3 -- 다른 애그리거트는 ID로만 참조. 외래키 제약은 애그리거트 간 결합을 높이고, 독립 배포/분리를 어렵게 만든다 |

> **ShippingInfo 인라인 vs 별도 테이블**: 배송 정보 변경이 거의 없고 주문 조회
> 시 항상 함께 필요하다면, orders 테이블에 컬럼으로 인라인하는 것이 더 단순하다
> (JOIN 제거). 이것은 트레이드오프이며 쿼리 패턴에 따라 결정한다.

### 인덱스 전략

인덱스 설계는 테이블 구조가 아닌 쿼리 워크로드를 따른다. 주문 도메인의 대표적
쿼리 패턴을 기준으로 설계한다.

```sql
-- ============================================================
-- orders 인덱스
-- ============================================================

-- 1) 특정 회원의 주문 목록 (내 주문 조회) -- 가장 빈번한 쿼리
--    WHERE orderer_id = ? ORDER BY created_at DESC
--    등호 조건(orderer_id)을 범위 조건(created_at)보다 앞에 배치
CREATE INDEX idx_orders_orderer_created
    ON orders (orderer_id, created_at DESC);

-- 2) 상태별 주문 조회 (관리자 대시보드)
--    WHERE status = ? AND created_at > ?
CREATE INDEX idx_orders_status_created
    ON orders (status, created_at);

-- 3) 미결제 주문 처리 (배치 작업) -- 부분 인덱스
--    전체 주문 중 payment_waiting은 소수이므로 부분 인덱스가 효율적
CREATE INDEX idx_orders_payment_waiting
    ON orders (created_at)
    WHERE status = 'payment_waiting';

-- ============================================================
-- order_line_items 인덱스
-- ============================================================

-- 4) 주문별 항목 조회 -- FK에 대한 인덱스
--    애그리거트 로딩 시 order_id로 항목을 함께 가져옴
CREATE INDEX idx_line_items_order
    ON order_line_items (order_id);

-- 5) 상품별 주문 내역 (통계/분석 쿼리)
--    WHERE product_id = ?
CREATE INDEX idx_line_items_product
    ON order_line_items (product_id);
```

**인덱스 설계 판단 근거:**

| 인덱스 | 패턴 | 근거 |
|--------|------|------|
| `idx_orders_orderer_created` | 복합 인덱스 | 등호(orderer_id) + 범위(created_at) 순서로 최좌선 접두사 규칙 충족. orderer_id 단독 쿼리에도 활용 가능 |
| `idx_orders_status_created` | 복합 인덱스 | status는 카디널리티가 낮으나, 등호 조건으로 사용되므로 선행 컬럼으로 적합 |
| `idx_orders_payment_waiting` | 부분 인덱스 | 전체 행 중 소수만 해당하는 조건을 필터링. 인덱스 크기 최소화, 유지 비용 절감 |
| `idx_line_items_order` | 단일 인덱스 | 애그리거트 로딩 패턴에 필수. Repository에서 Order + LineItems를 함께 조회 |
| `idx_line_items_product` | 단일 인덱스 | OLTP 필수는 아니지만, 상품별 주문 분석 쿼리가 예상되면 추가 |

### 리포지토리 매핑 시 주의사항

DDD에서 리포지토리는 애그리거트 단위로 동작한다. 주문 애그리거트 로딩 시
`orders` + `order_line_items` + `order_shipping_info`를 한 번에 조회하여
도메인 객체로 조립한다.

```python
class SqlOrderRepository(OrderRepository):
    """리포지토리는 애그리거트 전체를 로딩/저장한다.
    OrderLineItem이나 ShippingInfo를 위한 별도 리포지토리는 만들지 않는다.
    """

    def find_by_id(self, order_id: str) -> Order | None:
        # orders + order_line_items + order_shipping_info를
        # JOIN으로 한 번에 조회하여 N+1 방지
        ...

    def save(self, order: Order) -> None:
        # 하나의 트랜잭션에서 orders, order_line_items,
        # order_shipping_info를 함께 저장
        ...
```

**ORM 매핑 방향**: ORM은 도메인 모델을 임포트해야 하며, 도메인 모델이 ORM에
의존해서는 안 된다 (Data Mapper 패턴). 도메인 계층의 Order, OrderLineItem,
ShippingInfo 클래스는 순수 Python으로 유지하고, 인프라 계층에서 테이블 매핑을
정의한다.

---
> **관련 스킬 참조:**
> - [애그리거트 설계 규칙, 값 객체 정의, 도메인 이벤트] → **architecture-ddd** 스킬
> - [헥사고날 아키텍처, Data Mapper 패턴, Repository + UoW 구현] → **architecture-implementation-patterns** 스킬
> - [Django ORM 모델 코드, select_related/prefetch_related, 마이그레이션] → **implementation-django** 스킬
> - [트랜잭션 격리 수준, EXPLAIN ANALYZE 쿼리 최적화] → **architecture-db** 스킬
