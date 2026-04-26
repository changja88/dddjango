# 결제 시스템 트랜잭션 격리 수준 설계

## 배경: 격리 수준과 이상 현상 요약

| 격리 수준 | Dirty Read | Non-Repeatable Read | Phantom Read | Lost Update |
|---|---|---|---|---|
| READ UNCOMMITTED | O | O | O | O |
| READ COMMITTED | X | O | O | O |
| REPEATABLE READ | X | X | O | 부분적 방지 |
| SERIALIZABLE | X | X | X | X |

---

## 시나리오 1: 재고 차감 + 주문 생성

**상황**: 재고 10개인 상품에 100명이 동시에 구매를 시도한다.

### 권장 격리 수준: REPEATABLE READ + 비관적 락(SELECT ... FOR UPDATE)

### 설계 근거

격리 수준만으로는 이 문제를 해결할 수 없다. 핵심은 **재고 읽기와 차감 사이의 간극**이다.

```sql
BEGIN;  -- REPEATABLE READ

-- 1) 비관적 락으로 재고 행을 잠금
SELECT stock FROM products WHERE product_id = 123 FOR UPDATE;

-- 2) 애플리케이션에서 재고 확인
-- if (stock <= 0) ROLLBACK;

-- 3) 재고 차감
UPDATE products SET stock = stock - 1 WHERE product_id = 123;

-- 4) 주문 생성
INSERT INTO orders (product_id, user_id, amount) VALUES (123, @user_id, 1);

COMMIT;
```

### 왜 이 수준인가

| 대안 | 문제점 |
|---|---|
| READ COMMITTED | 두 트랜잭션이 동시에 `stock=10`을 읽고 둘 다 차감 가능 (Lost Update) |
| REPEATABLE READ (락 없이) | MySQL InnoDB는 MVCC로 스냅샷을 읽으므로, 두 트랜잭션이 같은 스냅샷의 `stock=10`을 본다. UPDATE 시점에 행 락이 걸리지만, 이미 읽은 값 기준으로 판단하면 초과 차감 가능 |
| SERIALIZABLE | 안전하지만 동시성이 극도로 떨어진다. 100명이 직렬 실행되면 응답 시간이 수 초로 늘어남 |

`FOR UPDATE`는 해당 행에 배타적 락을 걸어, 다른 트랜잭션이 같은 행을 읽으려 할 때 대기하게 만든다. 이로써 재고 확인과 차감이 원자적으로 동작한다.

### 발생 가능한 이상 현상 및 대응

| 이상 현상 | 발생 여부 | 대응 |
|---|---|---|
| Lost Update | FOR UPDATE로 방지 | - |
| 데드락 | 여러 상품을 동시에 주문할 때 발생 가능 | 상품 ID 오름차순으로 락 획득 순서를 고정 |
| 락 대기 타임아웃 | 동시 요청이 많으면 발생 | `innodb_lock_wait_timeout` 조정 + 재시도 로직 |

### 대안: 낙관적 락

트래픽이 극단적으로 높으면 비관적 락의 대기 비용이 크다. 이 경우 버전 컬럼을 사용할 수 있다.

```sql
-- 1) 읽기 (락 없음)
SELECT stock, version FROM products WHERE product_id = 123;

-- 2) 조건부 갱신
UPDATE products
SET stock = stock - 1, version = version + 1
WHERE product_id = 123 AND version = @read_version AND stock > 0;

-- affected_rows == 0 이면 재시도 또는 실패 처리
```

---

## 시나리오 2: 포인트 적립

**상황**: 주문 완료 후 포인트를 추가한다. 여러 주문이 동시에 완료되어 같은 사용자에게 동시 적립이 발생한다.

### 권장 격리 수준: READ COMMITTED + 원자적 UPDATE

### 설계 근거

포인트 적립은 **현재 잔액을 읽어서 더하는 것**이 아니라, **원자적으로 증가시키는 것**이다.

```sql
BEGIN;  -- READ COMMITTED

-- 원자적 증가: 읽기+쓰기가 하나의 연산
UPDATE user_points
SET balance = balance + @earned_points,
    updated_at = NOW()
WHERE user_id = @user_id;

-- 적립 이력 기록
INSERT INTO point_history (user_id, amount, type, order_id)
VALUES (@user_id, @earned_points, 'EARN', @order_id);

COMMIT;
```

### 왜 이 수준인가

| 대안 | 문제점 |
|---|---|
| READ UNCOMMITTED | 커밋되지 않은 포인트 잔액을 읽을 위험 (Dirty Read) |
| REPEATABLE READ | 불필요하게 높은 격리 수준. 스냅샷 읽기로 인해 동시 적립 시 충돌 가능성 증가 |
| SERIALIZABLE | 포인트 적립은 상호 의존성이 낮아 직렬화가 불필요 |

`balance = balance + N` 구문은 DB 엔진이 내부적으로 행 락을 획득한 뒤 현재 값에 더하므로, 애플리케이션에서 별도의 락을 관리할 필요가 없다. READ COMMITTED면 충분하다.

### 발생 가능한 이상 현상 및 대응

| 이상 현상 | 발생 여부 | 대응 |
|---|---|---|
| Lost Update | `balance = balance + N` 패턴으로 방지 | - |
| Non-Repeatable Read | 발생 가능하나 무해 (같은 트랜잭션 내에서 잔액을 두 번 읽을 필요 없음) | - |
| 중복 적립 | 격리 수준과 무관. 주문-적립 관계의 유니크 제약 필요 | `UNIQUE(order_id)` on point_history |
| 적립 누락 | 주문 서비스와 포인트 서비스 간 통신 실패 | Outbox 패턴 또는 이벤트 소싱으로 보장 |

### 주의: 포인트 차감은 다르다

적립과 달리 **차감**은 잔액 부족 검증이 필요하므로 시나리오 1과 동일하게 `FOR UPDATE`를 사용해야 한다.

```sql
SELECT balance FROM user_points WHERE user_id = @user_id FOR UPDATE;
-- if (balance < deduction_amount) ROLLBACK;
UPDATE user_points SET balance = balance - @amount WHERE user_id = @user_id;
```

---

## 시나리오 3: 일일 정산 보고서

**상황**: 하루 매출을 집계하는 쿼리를 실행한다. 집계 중에도 새로운 주문이 계속 들어온다.

### 권장 격리 수준: REPEATABLE READ (또는 스냅샷 격리)

### 설계 근거

정산 보고서에 필요한 것은 **특정 시점의 일관된 스냅샷**이다. 집계 도중 새로운 주문이 추가되면 앞부분과 뒷부분의 합산이 불일치하는 문제가 발생한다.

```sql
-- 방법 A: REPEATABLE READ 트랜잭션
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN;

-- 이 시점의 스냅샷 기준으로 모든 쿼리가 실행됨
SELECT SUM(amount) AS total_sales
FROM orders
WHERE order_date = '2026-04-03' AND status = 'COMPLETED';

SELECT COUNT(*) AS total_orders
FROM orders
WHERE order_date = '2026-04-03' AND status = 'COMPLETED';

-- 두 쿼리의 결과가 일관됨 (같은 스냅샷)
COMMIT;
```

```sql
-- 방법 B: PostgreSQL의 경우 명시적 스냅샷
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY;
-- 읽기 전용이므로 쓰기 트랜잭션과 충돌하지 않음
SELECT ...;
COMMIT;
```

### 왜 이 수준인가

| 대안 | 문제점 |
|---|---|
| READ UNCOMMITTED | 커밋되지 않은(나중에 롤백될 수도 있는) 주문까지 집계에 포함 |
| READ COMMITTED | 집계 쿼리 실행 중 새 주문이 커밋되면, SUM과 COUNT의 결과가 불일치 (Non-Repeatable Read, Phantom Read) |
| SERIALIZABLE | 읽기 전용 보고서에 과도한 격리. 쓰기 트랜잭션을 불필요하게 블로킹 |

REPEATABLE READ는 트랜잭션 시작 시점의 스냅샷을 기준으로 모든 읽기를 수행한다. 집계 도중 새 주문이 들어와도 스냅샷에는 반영되지 않으므로, 일관된 보고서가 생성된다.

### 발생 가능한 이상 현상 및 대응

| 이상 현상 | 발생 여부 | 대응 |
|---|---|---|
| Phantom Read | MySQL InnoDB의 REPEATABLE READ는 MVCC로 Phantom Read도 방지 (다만 표준 SQL에서는 SERIALIZABLE에서만 보장) | DB 엔진별 동작 확인 필요 |
| 정산 시점 이후 주문 누락 | 정산 시작 시점 이후 완료된 주문은 다음 정산에 포함 | 정산 기준 시각을 명확히 정의 (예: 자정 기준 UTC) |
| 장기 트랜잭션으로 인한 성능 저하 | MVCC 스냅샷 유지 비용 | 별도 리플리카(읽기 전용 DB)에서 정산 실행 |

### 실무 권장: 읽기 전용 리플리카 활용

```
[Primary DB] --replication--> [Read Replica]
                                  |
                          정산 보고서 실행
```

운영 DB에 부하를 주지 않으면서 일관된 스냅샷을 확보할 수 있다.

---

## 시나리오 4: 쿠폰 사용

**상황**: 1회용 쿠폰을 두 사람이 동시에 사용하려 한다.

### 권장 격리 수준: READ COMMITTED + 비관적 락(SELECT ... FOR UPDATE) + 상태 검증

### 설계 근거

쿠폰은 **한 번만 사용 가능**이라는 비즈니스 규칙을 DB 수준에서 보장해야 한다.

```sql
BEGIN;  -- READ COMMITTED

-- 1) 쿠폰 행을 락으로 잠금
SELECT coupon_id, status, user_id
FROM coupons
WHERE coupon_id = @coupon_id
FOR UPDATE;

-- 2) 애플리케이션에서 상태 확인
-- if (status != 'AVAILABLE') ROLLBACK; -- 이미 사용된 쿠폰

-- 3) 쿠폰 상태 변경
UPDATE coupons
SET status = 'USED',
    used_by = @user_id,
    used_at = NOW()
WHERE coupon_id = @coupon_id;

-- 4) 주문에 쿠폰 할인 적용
UPDATE orders SET discount = @coupon_value WHERE order_id = @order_id;

COMMIT;
```

### 왜 이 수준인가

| 대안 | 문제점 |
|---|---|
| READ COMMITTED (락 없이) | 두 트랜잭션이 동시에 `status='AVAILABLE'`을 읽고 둘 다 사용 처리 (Double Spending) |
| REPEATABLE READ | 스냅샷 격리로 인해, 먼저 커밋한 쪽의 변경을 뒤늦게 읽는 트랜잭션이 인지 못함. FOR UPDATE 없이는 여전히 이중 사용 가능 |
| SERIALIZABLE | 안전하지만, 쿠폰 테이블 전체에 락 범위가 확대될 수 있어 성능 저하 |

READ COMMITTED + FOR UPDATE 조합이면 충분하다. FOR UPDATE가 행 단위 배타적 락을 보장하므로, 두 번째 트랜잭션은 첫 번째가 커밋될 때까지 대기한 후 변경된 상태(`USED`)를 읽게 된다.

### 발생 가능한 이상 현상 및 대응

| 이상 현상 | 발생 여부 | 대응 |
|---|---|---|
| Double Spending | FOR UPDATE로 방지 | - |
| 데드락 | 쿠폰 사용과 주문 업데이트 순서가 꼬일 때 | 항상 쿠폰 락 -> 주문 업데이트 순서 고정 |
| 만료 쿠폰 사용 | 격리 수준과 무관 | `WHERE ... AND expires_at > NOW()` 조건 추가 |

### 대안: 유니크 제약으로 방어층 추가

```sql
-- 쿠폰 사용 이력 테이블에 유니크 제약
CREATE TABLE coupon_usage (
    coupon_id BIGINT NOT NULL,
    order_id  BIGINT NOT NULL,
    used_at   TIMESTAMP NOT NULL,
    UNIQUE KEY uk_coupon (coupon_id)  -- 쿠폰당 1회만 사용 가능
);
```

락이 실패하더라도 유니크 제약이 최종 방어선으로 이중 사용을 차단한다.

---

## 종합 정리

| 시나리오 | 격리 수준 | 추가 메커니즘 | 핵심 방어 대상 |
|---|---|---|---|
| 재고 차감 + 주문 | REPEATABLE READ | SELECT ... FOR UPDATE | Lost Update (초과 판매) |
| 포인트 적립 | READ COMMITTED | 원자적 UPDATE (`balance = balance + N`) | Lost Update (적립 누락) |
| 일일 정산 보고서 | REPEATABLE READ | READ ONLY 트랜잭션 | Non-Repeatable Read, Phantom Read (불일치 집계) |
| 쿠폰 사용 | READ COMMITTED | SELECT ... FOR UPDATE + UNIQUE 제약 | Double Spending (이중 사용) |

## 설계 원칙

1. **격리 수준은 최소한으로**: 높은 격리 수준은 동시성을 떨어뜨린다. 필요한 만큼만 올린다.
2. **격리 수준만으로 해결하지 않는다**: 락, 유니크 제약, 원자적 연산 등 추가 메커니즘을 조합한다.
3. **락 순서를 통일한다**: 데드락 방지의 가장 효과적인 방법은 모든 트랜잭션이 같은 순서로 락을 획득하는 것이다.
4. **재시도 로직을 반드시 구현한다**: 락 대기 타임아웃, 데드락 감지에 의한 롤백은 정상적인 상황이다. 애플리케이션에서 재시도해야 한다.
5. **읽기 부하는 분리한다**: 정산, 통계 등 읽기 전용 작업은 리플리카에서 실행하여 운영 DB를 보호한다.
