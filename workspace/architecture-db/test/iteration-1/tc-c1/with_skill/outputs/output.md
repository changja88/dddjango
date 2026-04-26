# 결제 시스템 트랜잭션 격리 수준 설계

---

## 시나리오 요약 및 격리 수준 결정

| # | 시나리오 | 격리 수준 | 핵심 이유 |
|---|----------|-----------|-----------|
| 1 | 재고 차감 + 주문 생성 | **Serializable** | 재고 음수 방지 (동시 100명 경합) |
| 2 | 포인트 적립 | **Read Committed** | 단순 가산 연산, 높은 동시성 필요 |
| 3 | 일일 정산 보고서 | **Repeatable Read** | 집계 도중 일관된 스냅샷 필요 |
| 4 | 쿠폰 사용 | **Serializable** | 1회용 쿠폰 이중 사용 방지 |

---

## 시나리오 1: 재고 차감 + 주문 생성

### 격리 수준: Serializable

### 상황

100명의 사용자가 동시에 같은 상품(재고 1개)을 구매 시도한다. 트랜잭션은 (1) 재고 확인, (2) 재고 차감, (3) 주문 생성의 세 단계를 수행한다.

### 왜 Serializable인가

이 시나리오의 핵심은 **read-then-write 패턴**이다. 재고를 읽고, 그 값을 기반으로 차감 여부를 결정한 뒤 쓴다. 낮은 격리 수준에서 어떤 문제가 발생하는지 살펴보면:

- **Read Committed**: 트랜잭션 A가 재고=1을 읽고 차감을 시작하기 전에, 트랜잭션 B도 재고=1을 읽는다. 둘 다 차감을 진행하면 재고가 -1이 된다. Non-Repeatable Read가 허용되므로 읽은 값이 커밋 시점에 이미 변경되어 있을 수 있다.
- **Repeatable Read**: 트랜잭션 시작 시점의 스냅샷을 유지하므로 같은 값을 다시 읽어도 동일하다. 그러나 두 트랜잭션이 동일한 스냅샷(재고=1)을 보고 동시에 차감하면 직렬화 이상(Serialization Anomaly)이 발생할 수 있다. 데이터베이스에 따라 write-write 충돌을 감지해 하나를 롤백하기도 하지만, 모든 구현에서 보장되지는 않는다.
- **Serializable**: 모든 트랜잭션이 마치 순차적으로 실행된 것처럼 동작한다. 한 트랜잭션이 재고를 읽고 차감하는 동안 다른 트랜잭션은 대기하거나 충돌 감지 시 롤백된다.

### 발생 가능한 이상 현상 (낮은 격리 수준 사용 시)

| 이상 현상 | 구체적 상황 |
|-----------|------------|
| Non-Repeatable Read | 재고=1을 읽었는데 차감 직전에 다른 트랜잭션이 재고=0으로 변경 |
| Serialization Anomaly | 두 트랜잭션이 모두 재고=1을 보고 동시에 차감 -> 재고=-1 |

### 설계 시 고려사항

```
트랜잭션 흐름:
BEGIN (Serializable)
  SELECT stock FROM products WHERE id = ? FOR UPDATE
  IF stock < quantity THEN ROLLBACK
  UPDATE products SET stock = stock - quantity WHERE id = ?
  INSERT INTO orders (product_id, quantity, ...) VALUES (?, ?, ...)
COMMIT
```

- 직렬화 실패 시 반드시 재시도 로직을 구현해야 한다.
- 대안으로 `SELECT ... FOR UPDATE`(비관적 잠금)를 Read Committed에서 사용하는 방법도 있다. 이 경우 행 단위 잠금으로 동시성을 확보하면서도 재고 음수를 방지할 수 있다. 다만 이는 격리 수준이 아닌 잠금 전략에 의존하는 방식이다.
- 동시성이 매우 높은 환경에서는 큐 기반 순차 처리도 고려한다.

---

## 시나리오 2: 포인트 적립

### 격리 수준: Read Committed

### 상황

주문 완료 후 사용자에게 포인트를 추가한다. 여러 주문이 동시에 완료되면 같은 사용자의 포인트가 동시에 적립될 수 있다.

### 왜 Read Committed인가

포인트 적립은 **단순 가산 연산**이다. `UPDATE points SET balance = balance + amount`처럼 현재 값에 더하는 방식이므로 read-then-write 패턴이 아니다. 데이터베이스는 이 UPDATE를 원자적으로 처리한다.

- 읽기 시점의 스냅샷 일관성이 필요하지 않다 (이전 포인트 잔액을 읽고 비교할 필요 없음).
- 동시 적립은 각각 독립적인 가산이므로 서로 간섭하지 않는다.
- 높은 동시성이 필요한 영역이므로 불필요하게 격리 수준을 올리면 처리량이 떨어진다.

### 발생 가능한 이상 현상

| 이상 현상 | 영향 |
|-----------|------|
| Non-Repeatable Read | 트랜잭션 내에서 포인트 잔액을 두 번 읽으면 다른 값이 나올 수 있음. 그러나 단순 가산에는 영향 없음 |
| Phantom Read | 포인트 이력을 조회할 때 새 행이 추가될 수 있음. 적립 연산 자체에는 무관 |

### 설계 시 고려사항

```
트랜잭션 흐름:
BEGIN (Read Committed)
  UPDATE user_points SET balance = balance + ? WHERE user_id = ?
  INSERT INTO point_history (user_id, amount, reason, ...) VALUES (?, ?, ?, ...)
COMMIT
```

- `balance + amount` 형태의 원자적 UPDATE를 사용한다. 절대로 SELECT로 잔액을 읽고 계산 후 UPDATE하지 않는다 (read-then-write 안티패턴).
- 포인트 이력 테이블에 INSERT하여 감사 추적이 가능하도록 한다.
- 멱등성 키(idempotency key)를 두어 네트워크 재시도로 인한 이중 적립을 방지한다.

---

## 시나리오 3: 일일 정산 보고서

### 격리 수준: Repeatable Read

### 상황

하루치 매출을 집계하는 보고서 쿼리가 수 초~수 분간 실행된다. 이 동안에도 새로운 주문이 계속 들어오고 결제가 완료된다.

### 왜 Repeatable Read인가

정산 보고서는 **시점 일관성(point-in-time consistency)**이 핵심이다. 보고서가 시작된 시점의 데이터 스냅샷을 기준으로 집계해야 한다.

- **Read Committed**: 각 SQL 문이 실행될 때마다 새로운 스냅샷을 본다. 보고서 쿼리가 여러 테이블을 순차적으로 조회하면, 앞서 집계한 주문 테이블과 나중에 조회한 결제 테이블의 시점이 달라 수치가 맞지 않을 수 있다 (Non-Repeatable Read).
- **Repeatable Read**: 트랜잭션 시작 시점의 스냅샷을 전체 트랜잭션 동안 유지한다. 보고서 실행 중 새로 들어온 주문은 보이지 않으므로 일관된 집계가 가능하다.
- **Serializable**: 불필요하게 높다. 보고서는 읽기 전용이므로 직렬화 이상이 발생할 여지가 없다. Serializable은 동시 쓰기 트랜잭션과의 충돌을 유발하여 정산 쿼리가 롤백될 수 있다.

### 발생 가능한 이상 현상 (Read Committed 사용 시)

| 이상 현상 | 구체적 상황 |
|-----------|------------|
| Non-Repeatable Read | 주문 합계를 구한 후 결제 합계를 구하는 사이에 새 결제가 완료되어 두 수치가 불일치 |
| Phantom Read | COUNT 쿼리 실행 중 새 주문 행이 추가되어 앞뒤 집계 건수가 다름 |

### 설계 시 고려사항

```
트랜잭션 흐름:
BEGIN (Repeatable Read, READ ONLY)
  SELECT SUM(amount) FROM orders WHERE order_date = ?
  SELECT SUM(amount) FROM payments WHERE payment_date = ?
  SELECT COUNT(*) FROM orders WHERE order_date = ? AND status = 'completed'
  ...
COMMIT
```

- `READ ONLY` 힌트를 추가하면 데이터베이스가 읽기 전용 최적화를 적용할 수 있다.
- 보고서가 OLTP 성능에 영향을 주지 않도록 읽기 전용 복제본(replica)에서 실행하는 것을 권장한다.
- Phantom Read가 Repeatable Read에서 이론적으로 가능하나, 보고서가 읽기 전용이므로 실질적 피해는 없다. 정확한 시점 일관성이 중요하다면 보고서 시작 전 기준 시각을 WHERE 조건으로 명시하여 범위를 확정한다.

---

## 시나리오 4: 쿠폰 사용

### 격리 수준: Serializable

### 상황

1회용 쿠폰(또는 사용 횟수 제한 쿠폰)을 두 사용자가 동시에 적용하려 한다. 쿠폰 상태를 확인하고 사용 처리하는 과정에서 이중 사용이 발생할 수 있다.

### 왜 Serializable인가

시나리오 1과 동일한 **read-then-write 패턴**이다. 쿠폰의 사용 여부를 확인(read)한 뒤, 미사용이면 사용 처리(write)한다. 재고 차감과 본질적으로 같은 경합 구조다.

- **Read Committed**: 트랜잭션 A가 쿠폰 상태=미사용을 읽는 동시에, 트랜잭션 B도 미사용을 읽는다. 둘 다 사용 처리를 진행하면 같은 쿠폰이 두 번 적용된다.
- **Repeatable Read**: 스냅샷은 일관되지만, 두 트랜잭션이 동일한 스냅샷을 기반으로 동시에 UPDATE하면 직렬화 이상이 발생할 수 있다.
- **Serializable**: 트랜잭션이 순차 실행되는 것처럼 보장하므로 이중 사용이 원천 차단된다.

### 발생 가능한 이상 현상 (낮은 격리 수준 사용 시)

| 이상 현상 | 구체적 상황 |
|-----------|------------|
| Non-Repeatable Read | 쿠폰 상태=미사용을 읽었는데 사용 처리 직전에 다른 트랜잭션이 이미 사용 처리 |
| Serialization Anomaly | 두 트랜잭션이 모두 미사용 상태를 보고 동시에 사용 처리 -> 이중 사용 |

### 설계 시 고려사항

```
트랜잭션 흐름:
BEGIN (Serializable)
  SELECT status, usage_count, max_usage FROM coupons WHERE code = ? FOR UPDATE
  IF status = 'used' OR usage_count >= max_usage THEN ROLLBACK
  UPDATE coupons SET usage_count = usage_count + 1,
    status = CASE WHEN usage_count + 1 >= max_usage THEN 'used' ELSE status END
    WHERE code = ?
  INSERT INTO coupon_usage (coupon_code, user_id, order_id, ...) VALUES (?, ?, ?, ...)
COMMIT
```

- 직렬화 실패 시 재시도 로직이 필수다.
- 대안: 유니크 제약조건(`UNIQUE(coupon_code, user_id)` 또는 `UNIQUE(coupon_code)`)을 활용하면 Read Committed에서도 이중 사용을 방지할 수 있다. 중복 INSERT 시 제약 위반 에러를 처리하는 방식이다. 다만 이는 격리 수준이 아닌 제약조건에 의존하는 방식이다.
- 쿠폰 사용 이력 테이블을 별도로 두어 감사 추적과 분석에 활용한다.

---

## 전체 설계 요약

```
높은 격리                                              낮은 격리
(안전, 낮은 동시성)                                    (위험, 높은 동시성)

Serializable          Repeatable Read       Read Committed
    |                       |                      |
    |-- 재고 차감 + 주문    |-- 일일 정산 보고서   |-- 포인트 적립
    |-- 쿠폰 사용           |                      |
```

### 핵심 판단 기준

| 판단 기준 | 설명 |
|-----------|------|
| **read-then-write 패턴 여부** | 값을 읽고 그 값에 기반해 쓰기를 결정하면 높은 격리 수준이 필요 (시나리오 1, 4) |
| **원자적 UPDATE 가능 여부** | `SET x = x + n` 같은 원자적 연산이면 낮은 격리 수준으로 충분 (시나리오 2) |
| **스냅샷 일관성 필요 여부** | 여러 테이블에 걸친 읽기가 동일 시점을 봐야 하면 Repeatable Read (시나리오 3) |
| **비즈니스 임계도** | 금전적 손실이 발생하는 경합이면 Serializable, 재시도 비용을 감수 |

### 공통 설계 원칙

1. **Serializable 사용 시 반드시 재시도 로직을 구현한다.** 직렬화 실패는 정상 동작이며, 에러가 아니라 재시도 신호다.
2. **필요 이상으로 높은 격리 수준은 불필요한 성능 저하를 초래한다.** 격리 수준은 시나리오별로 개별 설정한다.
3. **격리 수준 외의 보호 수단도 함께 고려한다.** `FOR UPDATE`(비관적 잠금), 유니크 제약조건, 낙관적 잠금(version 컬럼) 등은 격리 수준을 보완하거나 대체할 수 있다.
4. **OLAP(보고서) 쿼리는 OLTP 트래픽과 분리한다.** 읽기 전용 복제본 사용을 권장한다.
