# 트랜잭션과 격리 수준 레퍼런스

ACID 속성, 이상 현상, 4단계 격리 수준, 실전 선택 가이드.

---

## ACID

| 속성 | 의미 |
|------|------|
| **Atomicity** | 트랜잭션의 모든 연산이 성공하거나, 모두 실패 (전부 또는 전무) |
| **Consistency** | 트랜잭션 전후로 데이터베이스가 유효한 상태를 유지 |
| **Isolation** | 동시 트랜잭션이 서로 간섭하지 않음 |
| **Durability** | 커밋된 데이터는 시스템 장애 후에도 유지 |

---

## 이상 현상 (Phenomena)

| 현상 | 설명 |
|------|------|
| **Dirty Read** | 다른 트랜잭션이 아직 커밋하지 않은 데이터를 읽음 |
| **Non-Repeatable Read** | 같은 트랜잭션 내에서 같은 행을 두 번 읽었을 때 값이 다름 |
| **Phantom Read** | 같은 조건으로 두 번 조회했을 때 행의 집합이 다름 |
| **Serialization Anomaly** | 동시 트랜잭션의 결과가 어떤 직렬 실행 순서와도 일치하지 않음 |

---

## 4단계 격리 수준

| 격리 수준 | Dirty Read | Non-Repeatable Read | Phantom Read | 직렬화 이상 |
|-----------|:----------:|:-------------------:|:------------:|:-----------:|
| Read Uncommitted | 가능 | 가능 | 가능 | 가능 |
| **Read Committed** (일반 기본값) | 불가 | 가능 | 가능 | 가능 |
| Repeatable Read | 불가 | 불가 | 가능 | 가능 |
| Serializable | 불가 | 불가 | 불가 | 불가 |

---

## 실전 선택 가이드

| 격리 수준 | 적합한 경우 | 주의 |
|-----------|-----------|------|
| **Read Committed** | 대부분의 OLTP 애플리케이션 | 각 SQL 문이 새 스냅샷을 봄 |
| **Repeatable Read** | 일관된 읽기가 필요한 보고서/배치 | 직렬화 실패 시 재시도 필요 |
| **Serializable** | 정확성이 최우선인 금융/결제 | 직렬화 실패 시 반드시 재시도 로직 구현 |

---

## 핵심 원칙

격리 수준이 높을수록 안전하지만, 동시성이 낮아지고 직렬화 실패가 발생할 수 있다. 필요 이상으로 높은 격리 수준은 불필요한 성능 저하를 초래한다.

---

## Django 동시성 제어와 멱등성

주문 생성, 재고 예약, 결제 요청처럼 중복 실행과 동시 수정이 모두 문제가 되는
작업은 트랜잭션 경계, 잠금 전략, 멱등성 저장소를 함께 설계한다.

### 비관적 잠금: `select_for_update`

같은 재고 행을 동시에 차감할 수 없게 해야 한다면 `transaction.atomic()` 안에서
`select_for_update()`로 대상 행을 잠근다.

```python
from django.db import transaction


def reserve_stock(*, product_id: int, quantity: int) -> None:
    with transaction.atomic():
        stock = (
            Stock.objects
            .select_for_update()
            .get(product_id=product_id)
        )
        if stock.available < quantity:
            raise InsufficientStockError(product_id)
        stock.available -= quantity
        stock.save(update_fields=["available"])
```

### 낙관적 잠금: version 컬럼

긴 트랜잭션이나 충돌 빈도가 낮은 작업은 `version` 컬럼을 조건부 갱신에 포함한다.
갱신 행 수가 0이면 다른 트랜잭션이 먼저 수정한 것이므로 재조회 후 재시도한다.

```python
updated = (
    Stock.objects
    .filter(id=stock.id, version=stock.version)
    .update(
        available=F("available") - quantity,
        version=F("version") + 1,
    )
)
if updated != 1:
    raise ConcurrencyConflictError(stock.id)
```

### 유니크 제약과 재시도

중복 요청 방지는 애플리케이션 체크만으로 끝내지 않는다. 멱등성 키, 외부 요청 ID,
도메인 고유 키는 DB `UniqueConstraint`로 막고 `IntegrityError`를 명시적으로
처리한다.

```python
class Reservation(models.Model):
    idempotency_key = models.CharField(max_length=80)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["idempotency_key"],
                name="uniq_reservation_idempotency_key",
            )
        ]
```

### 멱등성 저장 경계

API의 `Idempotency-Key`는 단순 헤더가 아니라 도메인 명령 처리 결과와 함께 저장할
경계다. 같은 키가 다시 들어오면 새 주문/예약을 만들지 않고 이전 결과를 반환한다.
저장소는 요청 payload hash, 처리 상태, 응답 요약, 만료 시각을 함께 보관한다.
