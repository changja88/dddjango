# 주문-상품-카테고리 DB 스키마 설계

## 1. ERD 개요

```
Category (1) --< ProductCategory (>-- (1) Product (1) --< OrderItem (>-- (1) Order (>-- (1) Customer
    |                                      |
    +-- (self-referential: parent_id)      +-- ProductOption (1) --< OrderItem
```

- Category : Product = M:N (다대다, 중간 테이블 사용)
- Product : Order = M:N (OrderItem을 통한 다대다)
- Category는 자기참조로 계층 구조 지원

---

## 2. 정규화 수준: 제3정규형(3NF) + 전략적 반정규화

### 2.1 정규화 원칙

| 정규형 | 적용 여부 | 설명 |
|--------|-----------|------|
| 1NF | O | 모든 컬럼이 원자값, 반복 그룹 없음 |
| 2NF | O | 복합키에 대한 부분 함수 종속 제거 (OrderItem 분리) |
| 3NF | O | 이행적 함수 종속 제거 (Category를 Product에서 분리) |
| BCNF | 부분 적용 | 결정자가 후보키인 경우만 해당 |

### 2.2 전략적 반정규화

성능을 위해 다음 항목은 의도적으로 반정규화한다:

- `Order.total_amount`: OrderItem의 합계를 캐싱 (매 조회마다 SUM 방지)
- `Order.item_count`: 주문 내 상품 수 캐싱
- `Product.review_avg`, `Product.review_count`: 리뷰 집계 캐싱
- `Category.product_count`: 카테고리별 상품 수 캐싱

이 값들은 트리거 또는 애플리케이션 레벨에서 동기화한다.

---

## 3. 테이블 정의

### 3.1 Category (카테고리)

```sql
CREATE TABLE category (
    id              BIGINT          PRIMARY KEY AUTO_INCREMENT,
    parent_id       BIGINT          NULL,
    name            VARCHAR(100)    NOT NULL,
    slug            VARCHAR(120)    NOT NULL,
    depth           TINYINT         NOT NULL DEFAULT 0,
    sort_order      INT             NOT NULL DEFAULT 0,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    product_count   INT             NOT NULL DEFAULT 0,       -- 반정규화
    created_at      DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at      DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),

    CONSTRAINT fk_category_parent
        FOREIGN KEY (parent_id) REFERENCES category(id)
        ON DELETE SET NULL,

    CONSTRAINT uq_category_slug UNIQUE (slug)
);
```

**설계 근거:**
- `parent_id`로 자기참조하여 무한 계층 지원 (Adjacency List 패턴)
- `depth`는 반정규화이지만, 계층 쿼리 성능을 위해 유지
- `slug`는 URL-safe 식별자로 UNIQUE 제약

### 3.2 Product (상품)

```sql
CREATE TABLE product (
    id              BIGINT          PRIMARY KEY AUTO_INCREMENT,
    sku             VARCHAR(50)     NOT NULL,
    name            VARCHAR(255)    NOT NULL,
    slug            VARCHAR(280)    NOT NULL,
    description     TEXT            NULL,
    base_price      DECIMAL(12,2)   NOT NULL,
    cost_price      DECIMAL(12,2)   NULL,
    stock_quantity  INT             NOT NULL DEFAULT 0,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    weight_gram     INT             NULL,
    review_avg      DECIMAL(2,1)    NOT NULL DEFAULT 0.0,     -- 반정규화
    review_count    INT             NOT NULL DEFAULT 0,        -- 반정규화
    created_at      DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at      DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),

    CONSTRAINT uq_product_sku UNIQUE (sku),
    CONSTRAINT uq_product_slug UNIQUE (slug),
    CONSTRAINT chk_base_price CHECK (base_price >= 0),
    CONSTRAINT chk_stock CHECK (stock_quantity >= 0)
);
```

### 3.3 ProductCategory (상품-카테고리 매핑)

```sql
CREATE TABLE product_category (
    product_id      BIGINT      NOT NULL,
    category_id     BIGINT      NOT NULL,
    is_primary      BOOLEAN     NOT NULL DEFAULT FALSE,
    sort_order      INT         NOT NULL DEFAULT 0,

    PRIMARY KEY (product_id, category_id),

    CONSTRAINT fk_pc_product
        FOREIGN KEY (product_id) REFERENCES product(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_pc_category
        FOREIGN KEY (category_id) REFERENCES category(id)
        ON DELETE CASCADE
);
```

**설계 근거:**
- 복합 PK로 중복 매핑 방지
- `is_primary`로 대표 카테고리 지정 (상품 상세 페이지 breadcrumb 등)

### 3.4 ProductOption (상품 옵션)

```sql
CREATE TABLE product_option (
    id              BIGINT          PRIMARY KEY AUTO_INCREMENT,
    product_id      BIGINT          NOT NULL,
    name            VARCHAR(100)    NOT NULL,           -- 예: "빨강 / XL"
    price_delta     DECIMAL(12,2)   NOT NULL DEFAULT 0, -- 기본가 대비 가격 차이
    stock_quantity  INT             NOT NULL DEFAULT 0,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),

    CONSTRAINT fk_option_product
        FOREIGN KEY (product_id) REFERENCES product(id)
        ON DELETE CASCADE,
    CONSTRAINT chk_option_stock CHECK (stock_quantity >= 0)
);
```

### 3.5 Customer (고객)

```sql
CREATE TABLE customer (
    id              BIGINT          PRIMARY KEY AUTO_INCREMENT,
    email           VARCHAR(255)    NOT NULL,
    name            VARCHAR(100)    NOT NULL,
    phone           VARCHAR(20)     NULL,
    created_at      DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at      DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),

    CONSTRAINT uq_customer_email UNIQUE (email)
);
```

### 3.6 Order (주문)

```sql
CREATE TABLE `order` (
    id              BIGINT          PRIMARY KEY AUTO_INCREMENT,
    order_number    VARCHAR(30)     NOT NULL,
    customer_id     BIGINT          NOT NULL,
    status          VARCHAR(20)     NOT NULL DEFAULT 'PENDING',
    total_amount    DECIMAL(14,2)   NOT NULL DEFAULT 0,        -- 반정규화
    item_count      INT             NOT NULL DEFAULT 0,         -- 반정규화
    shipping_address TEXT           NULL,
    ordered_at      DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    paid_at         DATETIME(6)     NULL,
    shipped_at      DATETIME(6)     NULL,
    completed_at    DATETIME(6)     NULL,
    cancelled_at    DATETIME(6)     NULL,
    created_at      DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at      DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),

    CONSTRAINT fk_order_customer
        FOREIGN KEY (customer_id) REFERENCES customer(id)
        ON DELETE RESTRICT,

    CONSTRAINT uq_order_number UNIQUE (order_number),
    CONSTRAINT chk_order_status CHECK (
        status IN ('PENDING', 'PAID', 'PREPARING', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'REFUNDED')
    ),
    CONSTRAINT chk_total_amount CHECK (total_amount >= 0)
);
```

**설계 근거:**
- `order_number`는 비즈니스 식별자 (예: `ORD-20260406-00001`), PK와 분리
- 상태 전이는 CHECK 제약으로 유효 값만 허용
- `customer_id` ON DELETE RESTRICT: 주문이 있는 고객은 삭제 불가

### 3.7 OrderItem (주문 항목)

```sql
CREATE TABLE order_item (
    id                  BIGINT          PRIMARY KEY AUTO_INCREMENT,
    order_id            BIGINT          NOT NULL,
    product_id          BIGINT          NOT NULL,
    product_option_id   BIGINT          NULL,
    quantity            INT             NOT NULL DEFAULT 1,
    unit_price          DECIMAL(12,2)   NOT NULL,   -- 주문 시점의 확정 가격
    subtotal            DECIMAL(14,2)   NOT NULL,   -- unit_price * quantity
    product_name        VARCHAR(255)    NOT NULL,   -- 스냅샷 (반정규화)
    option_name         VARCHAR(100)    NULL,       -- 스냅샷 (반정규화)
    created_at          DATETIME(6)     NOT NULL DEFAULT CURRENT_TIMESTAMP(6),

    CONSTRAINT fk_oi_order
        FOREIGN KEY (order_id) REFERENCES `order`(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_oi_product
        FOREIGN KEY (product_id) REFERENCES product(id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_oi_option
        FOREIGN KEY (product_option_id) REFERENCES product_option(id)
        ON DELETE SET NULL,

    CONSTRAINT chk_quantity CHECK (quantity > 0),
    CONSTRAINT chk_unit_price CHECK (unit_price >= 0)
);
```

**설계 근거:**
- `unit_price`: 주문 시점의 가격을 스냅샷으로 저장 (상품 가격 변경에 영향 받지 않음)
- `product_name`, `option_name`: 상품이 수정/삭제되어도 주문 이력 보존
- 이 스냅샷 필드들은 의도적인 반정규화이며, 주문 데이터의 불변성을 보장

---

## 4. 인덱싱 전략

### 4.1 인덱스 정의

```sql
-- ============================================================
-- Category 인덱스
-- ============================================================
CREATE INDEX idx_category_parent_sort
    ON category (parent_id, sort_order);
    -- 용도: 특정 부모 아래 자식 카테고리 정렬 조회
    -- 쿼리: WHERE parent_id = ? ORDER BY sort_order

CREATE INDEX idx_category_active_depth
    ON category (is_active, depth);
    -- 용도: 활성 카테고리를 depth별로 필터링
    -- 쿼리: WHERE is_active = TRUE AND depth <= ?

-- ============================================================
-- Product 인덱스
-- ============================================================
CREATE INDEX idx_product_active_created
    ON product (is_active, created_at DESC);
    -- 용도: 활성 상품 최신순 목록 (상품 리스트 페이지)
    -- 쿼리: WHERE is_active = TRUE ORDER BY created_at DESC LIMIT ?

CREATE INDEX idx_product_active_price
    ON product (is_active, base_price);
    -- 용도: 가격 범위 필터링
    -- 쿼리: WHERE is_active = TRUE AND base_price BETWEEN ? AND ?

CREATE INDEX idx_product_name_search
    ON product (name);
    -- 용도: 상품명 검색 (LIKE 'keyword%' 전방일치)
    -- 참고: 전문 검색이 필요하면 FULLTEXT INDEX 또는 Elasticsearch 도입 권장

-- ============================================================
-- ProductCategory 인덱스
-- ============================================================
-- PK (product_id, category_id)가 이미 존재하므로 product_id 기준 조회 커버
CREATE INDEX idx_pc_category_primary
    ON product_category (category_id, is_primary, sort_order);
    -- 용도: 특정 카테고리의 상품 목록 조회
    -- 쿼리: WHERE category_id = ? ORDER BY sort_order

-- ============================================================
-- ProductOption 인덱스
-- ============================================================
CREATE INDEX idx_option_product_active
    ON product_option (product_id, is_active);
    -- 용도: 특정 상품의 활성 옵션 조회
    -- 쿼리: WHERE product_id = ? AND is_active = TRUE

-- ============================================================
-- Order 인덱스
-- ============================================================
CREATE INDEX idx_order_customer_ordered
    ON `order` (customer_id, ordered_at DESC);
    -- 용도: 고객별 주문 내역 최신순 조회 (마이페이지)
    -- 쿼리: WHERE customer_id = ? ORDER BY ordered_at DESC

CREATE INDEX idx_order_status_ordered
    ON `order` (status, ordered_at DESC);
    -- 용도: 상태별 주문 관리 (관리자 페이지)
    -- 쿼리: WHERE status = ? ORDER BY ordered_at DESC

CREATE INDEX idx_order_ordered_at
    ON `order` (ordered_at DESC);
    -- 용도: 전체 주문 최신순 (대시보드, 리포트)

-- ============================================================
-- OrderItem 인덱스
-- ============================================================
CREATE INDEX idx_oi_order
    ON order_item (order_id);
    -- 용도: 특정 주문의 상품 목록 조회 (FK 인덱스)

CREATE INDEX idx_oi_product_created
    ON order_item (product_id, created_at DESC);
    -- 용도: 특정 상품의 판매 이력 조회
    -- 쿼리: WHERE product_id = ? ORDER BY created_at DESC
```

### 4.2 인덱스 설계 원칙 요약

| 원칙 | 적용 |
|------|------|
| FK에는 반드시 인덱스 | 모든 외래키 컬럼에 인덱스 생성 |
| 복합 인덱스 컬럼 순서 | 선택도(cardinality) 높은 컬럼을 앞에 배치 |
| 커버링 인덱스 활용 | `idx_pc_category_primary`는 JOIN 없이 정렬까지 커버 |
| 과도한 인덱싱 방지 | 쓰기 비중 높은 OrderItem은 필수 인덱스만 유지 |
| 정렬 방향 명시 | `DESC`가 필요한 경우 인덱스에 방향 지정 |

---

## 5. 트랜잭션 격리 수준

### 5.1 기본 설정

```
기본 격리 수준: READ COMMITTED
```

MySQL/PostgreSQL 모두에서 `READ COMMITTED`를 기본으로 사용한다.

| 격리 수준 | Dirty Read | Non-Repeatable Read | Phantom Read | 채택 여부 |
|-----------|:----------:|:-------------------:|:------------:|:---------:|
| READ UNCOMMITTED | O | O | O | X |
| READ COMMITTED | X | O | O | 기본값 |
| REPEATABLE READ | X | X | O | 특정 작업 |
| SERIALIZABLE | X | X | X | 극히 제한적 |

### 5.2 작업별 격리 수준

#### 주문 생성 (재고 차감 포함) -- REPEATABLE READ

```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN;

-- 1) 재고 확인 및 차감 (비관적 잠금)
SELECT stock_quantity
  FROM product
 WHERE id = ?
   FOR UPDATE;

UPDATE product
   SET stock_quantity = stock_quantity - ?
 WHERE id = ?
   AND stock_quantity >= ?;

-- 옵션이 있는 경우
SELECT stock_quantity
  FROM product_option
 WHERE id = ?
   FOR UPDATE;

UPDATE product_option
   SET stock_quantity = stock_quantity - ?
 WHERE id = ?
   AND stock_quantity >= ?;

-- 2) 주문 생성
INSERT INTO `order` (order_number, customer_id, status, total_amount, item_count)
VALUES (?, ?, 'PENDING', ?, ?);

-- 3) 주문 항목 생성
INSERT INTO order_item (order_id, product_id, product_option_id, quantity, unit_price, subtotal, product_name, option_name)
VALUES (?, ?, ?, ?, ?, ?, ?, ?);

COMMIT;
```

**근거:** 재고 차감은 동시성 이슈가 가장 치명적인 영역이다. `SELECT ... FOR UPDATE`로 비관적 잠금을 걸어 초과 판매(oversell)를 방지하고, REPEATABLE READ로 트랜잭션 내 일관된 읽기를 보장한다.

#### 주문 상태 변경 -- READ COMMITTED

```sql
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
BEGIN;

SELECT id, status
  FROM `order`
 WHERE id = ?
   FOR UPDATE;

-- 애플리케이션 레벨에서 상태 전이 유효성 검증
-- 예: PAID -> PREPARING (O), CANCELLED -> PAID (X)

UPDATE `order`
   SET status = ?, updated_at = CURRENT_TIMESTAMP(6)
 WHERE id = ?;

COMMIT;
```

**근거:** 단일 레코드 업데이트이므로 READ COMMITTED로 충분하다. `FOR UPDATE`로 동시 상태 변경만 방지한다.

#### 상품 목록 조회 -- READ COMMITTED (기본값)

```sql
-- 별도 격리 수준 설정 불필요 (기본값 사용)
SELECT p.id, p.name, p.base_price, p.review_avg, p.review_count
  FROM product p
  JOIN product_category pc ON p.id = pc.product_id
 WHERE pc.category_id = ?
   AND p.is_active = TRUE
 ORDER BY pc.sort_order
 LIMIT ? OFFSET ?;
```

**근거:** 읽기 전용 조회이므로 최소 격리 수준으로 동시성을 극대화한다.

#### 매출 리포트 집계 -- REPEATABLE READ

```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN;

SELECT DATE(o.ordered_at) AS order_date,
       COUNT(DISTINCT o.id) AS order_count,
       SUM(o.total_amount)  AS daily_revenue
  FROM `order` o
 WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
   AND o.ordered_at BETWEEN ? AND ?
 GROUP BY DATE(o.ordered_at)
 ORDER BY order_date;

COMMIT;
```

**근거:** 리포트 쿼리는 여러 행을 집계하므로, 트랜잭션 도중 다른 주문이 끼어들어 수치가 달라지는 것을 방지해야 한다.

### 5.3 잠금 전략 요약

| 시나리오 | 격리 수준 | 잠금 방식 | 이유 |
|----------|-----------|-----------|------|
| 주문 생성 + 재고 차감 | REPEATABLE READ | 비관적 (FOR UPDATE) | 초과 판매 방지 |
| 주문 상태 변경 | READ COMMITTED | 비관적 (FOR UPDATE) | 동시 상태 충돌 방지 |
| 상품 조회 | READ COMMITTED | 잠금 없음 | 최대 동시성 |
| 매출 리포트 | REPEATABLE READ | 잠금 없음 | 스냅샷 일관성 |
| 카테고리 관리 | READ COMMITTED | 낙관적 (updated_at 비교) | 충돌 빈도 낮음 |

---

## 6. Django 모델 구현

```python
from django.db import models
from django.core.validators import MinValueValidator


class Category(models.Model):
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='children',
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    depth = models.PositiveSmallIntegerField(default=0)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    product_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'category'
        indexes = [
            models.Index(fields=['parent', 'sort_order'], name='idx_category_parent_sort'),
            models.Index(fields=['is_active', 'depth'], name='idx_category_active_depth'),
        ]
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    cost_price = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
    )
    stock_quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
    )
    is_active = models.BooleanField(default=True)
    weight_gram = models.IntegerField(null=True, blank=True)
    review_avg = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    review_count = models.IntegerField(default=0)
    categories = models.ManyToManyField(
        Category,
        through='ProductCategory',
        related_name='products',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product'
        indexes = [
            models.Index(fields=['is_active', '-created_at'], name='idx_product_active_created'),
            models.Index(fields=['is_active', 'base_price'], name='idx_product_active_price'),
            models.Index(fields=['name'], name='idx_product_name_search'),
        ]

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'product_category'
        unique_together = [('product', 'category')]
        indexes = [
            models.Index(
                fields=['category', 'is_primary', 'sort_order'],
                name='idx_pc_category_primary',
            ),
        ]


class ProductOption(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name='options',
    )
    name = models.CharField(max_length=100)
    price_delta = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
    )
    stock_quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_option'
        indexes = [
            models.Index(fields=['product', 'is_active'], name='idx_option_product_active'),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.name}"


class Customer(models.Model):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer'

    def __str__(self):
        return self.name


class Order(models.Model):

    class Status(models.TextChoices):
        PENDING = 'PENDING', '결제 대기'
        PAID = 'PAID', '결제 완료'
        PREPARING = 'PREPARING', '상품 준비중'
        SHIPPED = 'SHIPPED', '배송중'
        DELIVERED = 'DELIVERED', '배송 완료'
        CANCELLED = 'CANCELLED', '주문 취소'
        REFUNDED = 'REFUNDED', '환불 완료'

    order_number = models.CharField(max_length=30, unique=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.RESTRICT,
        related_name='orders',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    total_amount = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
    )
    item_count = models.IntegerField(default=0)
    shipping_address = models.TextField(blank=True)
    ordered_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order'
        indexes = [
            models.Index(
                fields=['customer', '-ordered_at'],
                name='idx_order_customer_ordered',
            ),
            models.Index(
                fields=['status', '-ordered_at'],
                name='idx_order_status_ordered',
            ),
            models.Index(
                fields=['-ordered_at'],
                name='idx_order_ordered_at',
            ),
        ]

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        Product, on_delete=models.RESTRICT,
        related_name='order_items',
    )
    product_option = models.ForeignKey(
        ProductOption, on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2)
    product_name = models.CharField(max_length=255)
    option_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_item'
        indexes = [
            models.Index(fields=['order'], name='idx_oi_order'),
            models.Index(fields=['product', '-created_at'], name='idx_oi_product_created'),
        ]

    def __str__(self):
        return f"OrderItem({self.order.order_number}: {self.product_name})"
```

---

## 7. 주문 생성 서비스 (트랜잭션 적용 예시)

```python
from django.db import transaction
from decimal import Decimal


class OrderService:
    """주문 생성 서비스 -- 재고 차감을 포함한 트랜잭션 처리"""

    @staticmethod
    @transaction.atomic
    def create_order(customer: Customer, cart_items: list[dict]) -> Order:
        """
        cart_items 형식:
        [
            {"product_id": 1, "option_id": None, "quantity": 2},
            {"product_id": 3, "option_id": 7, "quantity": 1},
        ]
        """
        order = Order.objects.create(
            order_number=OrderService._generate_order_number(),
            customer=customer,
        )

        total_amount = Decimal('0')
        item_count = 0

        for item in cart_items:
            # 비관적 잠금으로 재고 조회
            product = (
                Product.objects
                .select_for_update()
                .get(id=item['product_id'])
            )

            option = None
            if item.get('option_id'):
                option = (
                    ProductOption.objects
                    .select_for_update()
                    .get(id=item['option_id'])
                )

            quantity = item['quantity']

            # 재고 검증
            stock_target = option if option else product
            if stock_target.stock_quantity < quantity:
                raise ValueError(
                    f"재고 부족: {product.name} "
                    f"(요청: {quantity}, 재고: {stock_target.stock_quantity})"
                )

            # 재고 차감
            stock_target.stock_quantity -= quantity
            stock_target.save(update_fields=['stock_quantity'])

            # 가격 계산
            unit_price = product.base_price
            if option:
                unit_price += option.price_delta
            subtotal = unit_price * quantity

            # 주문 항목 생성 (가격/이름 스냅샷)
            OrderItem.objects.create(
                order=order,
                product=product,
                product_option=option,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=subtotal,
                product_name=product.name,
                option_name=option.name if option else '',
            )

            total_amount += subtotal
            item_count += quantity

        # 주문 합계 업데이트 (반정규화 필드)
        order.total_amount = total_amount
        order.item_count = item_count
        order.save(update_fields=['total_amount', 'item_count'])

        return order

    @staticmethod
    def _generate_order_number() -> str:
        from django.utils import timezone
        import uuid
        now = timezone.now()
        short_uuid = uuid.uuid4().hex[:8].upper()
        return f"ORD-{now.strftime('%Y%m%d')}-{short_uuid}"
```

---

## 8. 핵심 설계 결정 요약

| 항목 | 결정 | 근거 |
|------|------|------|
| 정규화 수준 | 3NF + 전략적 반정규화 | 조회 성능과 데이터 무결성 균형 |
| 카테고리 계층 | Adjacency List + depth | 구현 단순성, depth로 쿼리 보조 |
| 상품-카테고리 | M:N 중간 테이블 | 하나의 상품이 여러 카테고리에 속할 수 있음 |
| 주문 가격 저장 | 스냅샷 방식 | 상품 가격 변경과 주문 이력 분리 |
| 기본 격리 수준 | READ COMMITTED | 대부분의 읽기 작업에 적합한 동시성 |
| 재고 차감 | REPEATABLE READ + FOR UPDATE | 초과 판매 방지 |
| 인덱스 전략 | 쿼리 패턴 기반 복합 인덱스 | 실제 사용되는 쿼리에 맞춤 설계 |
| PK 전략 | BIGINT AUTO_INCREMENT | 단순성, 성능, 충분한 범위 |
