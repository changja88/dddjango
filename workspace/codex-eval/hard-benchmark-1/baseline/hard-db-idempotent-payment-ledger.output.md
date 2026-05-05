아래는 Django에서 “주문 결제 원장”을 설계할 때의 권장 구조입니다. 핵심은 **PG 이벤트 수신은 여러 번 올 수 있다**, **idempotency key 기준으로 처리 결과가 한 번만 반영되어야 한다**, **원장은 append-only에 가깝게 유지한다**, **잔액/상태 갱신은 transaction 안에서 잠금으로 보호한다**입니다.

**모델 구조**

```python
class PaymentLedger(models.Model):
    class Direction(models.TextChoices):
        DEBIT = "debit"      # 청구, 결제 요청, 매출 증가
        CREDIT = "credit"    # 환불, 취소, 차감

    class EventType(models.TextChoices):
        AUTHORIZE = "authorize"
        CAPTURE = "capture"
        CANCEL = "cancel"
        REFUND = "refund"
        ADJUSTMENT = "adjustment"

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="payment_ledgers",
    )

    payment = models.ForeignKey(
        "payments.Payment",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="ledgers",
    )

    pg_provider = models.CharField(max_length=32)
    pg_transaction_id = models.CharField(max_length=128, null=True, blank=True)

    event_type = models.CharField(max_length=32, choices=EventType.choices)
    direction = models.CharField(max_length=16, choices=Direction.choices)

    amount = models.PositiveBigIntegerField()
    currency = models.CharField(max_length=3, default="KRW")

    # PG 재시도 / webhook 중복 방지의 핵심
    idempotency_key = models.CharField(max_length=255)

    # 원본 이벤트 추적용
    pg_event_id = models.CharField(max_length=128, null=True, blank=True)
    raw_payload = models.JSONField(default=dict)

    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["pg_provider", "idempotency_key"],
                name="uq_payment_ledger_provider_idempotency_key",
            ),
            models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name="ck_payment_ledger_amount_positive",
            ),
        ]
        indexes = [
            models.Index(
                fields=["order", "-created_at"],
                name="idx_ledger_order_created",
            ),
            models.Index(
                fields=["payment", "-created_at"],
                name="idx_ledger_payment_created",
            ),
            models.Index(
                fields=["pg_provider", "pg_transaction_id"],
                name="idx_ledger_pg_tx",
            ),
            models.Index(
                fields=["occurred_at"],
                name="idx_ledger_occurred_at",
            ),
        ]
```

`idempotency_key`는 가능하면 PG가 준 이벤트 ID, 결제 승인 ID, 환불 ID처럼 **PG 기준으로 안정적인 값**을 쓰는 게 좋습니다. 없다면 직접 조합합니다.

```text
{provider}:{event_type}:{pg_transaction_id}:{amount}:{occurred_at_or_sequence}
```

단, 조합 키는 재시도마다 달라지면 안 됩니다. payload 전체 hash는 필드 순서나 사소한 값 차이로 흔들릴 수 있어 신중해야 합니다.

**주문 결제 상태 테이블**

원장은 사실 기록이고, 빠른 조회를 위해 현재 상태는 별도 테이블이나 `Payment` 모델에 둡니다.

```python
class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        AUTHORIZED = "authorized"
        PAID = "paid"
        CANCELED = "canceled"
        PARTIAL_REFUNDED = "partial_refunded"
        REFUNDED = "refunded"
        FAILED = "failed"

    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="payment",
    )

    status = models.CharField(max_length=32, choices=Status.choices)
    authorized_amount = models.PositiveBigIntegerField(default=0)
    captured_amount = models.PositiveBigIntegerField(default=0)
    refunded_amount = models.PositiveBigIntegerField(default=0)

    currency = models.CharField(max_length=3, default="KRW")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["order"], name="idx_payment_order"),
            models.Index(fields=["status", "-updated_at"], name="idx_payment_status_updated"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(authorized_amount__gte=0),
                name="ck_payment_authorized_amount_gte_0",
            ),
            models.CheckConstraint(
                check=models.Q(captured_amount__gte=0),
                name="ck_payment_captured_amount_gte_0",
            ),
            models.CheckConstraint(
                check=models.Q(refunded_amount__gte=0),
                name="ck_payment_refunded_amount_gte_0",
            ),
            models.CheckConstraint(
                check=models.Q(refunded_amount__lte=models.F("captured_amount")),
                name="ck_payment_refunded_lte_captured",
            ),
        ]
```

**조회 패턴과 인덱스**

주요 조회 패턴은 보통 아래입니다.

1. 주문 상세에서 결제 원장 조회
   `WHERE order_id = ? ORDER BY created_at DESC`
   인덱스: `["order", "-created_at"]`

2. 결제 단위 원장 조회
   `WHERE payment_id = ? ORDER BY created_at DESC`
   인덱스: `["payment", "-created_at"]`

3. PG 트랜잭션 추적
   `WHERE pg_provider = ? AND pg_transaction_id = ?`
   인덱스: `["pg_provider", "pg_transaction_id"]`

4. idempotency 중복 방지
   `UNIQUE(pg_provider, idempotency_key)`

5. 정산/감사용 기간 조회
   `WHERE occurred_at BETWEEN ? AND ?`
   인덱스: `["occurred_at"]`

원장이 커질 가능성이 크면 `created_at` 또는 `occurred_at` 기준 파티셔닝도 검토할 수 있습니다. 다만 초기부터 파티셔닝을 넣기보다는 데이터량과 보관 정책이 확인된 뒤 도입하는 편이 안전합니다.

**이벤트 처리 흐름**

핵심은 `transaction.atomic()` 안에서 다음 순서를 지키는 것입니다.

```python
from django.db import IntegrityError, transaction

def apply_payment_event(event):
    with transaction.atomic():
        payment = (
            Payment.objects
            .select_for_update()
            .get(order_id=event.order_id)
        )

        try:
            ledger = PaymentLedger.objects.create(
                order_id=event.order_id,
                payment=payment,
                pg_provider=event.provider,
                pg_transaction_id=event.pg_transaction_id,
                pg_event_id=event.pg_event_id,
                idempotency_key=event.idempotency_key,
                event_type=event.event_type,
                direction=event.direction,
                amount=event.amount,
                currency=event.currency,
                raw_payload=event.raw_payload,
                occurred_at=event.occurred_at,
            )
        except IntegrityError:
            # 같은 이벤트가 이미 반영됨.
            # 여기서 성공 응답을 반환해야 PG가 재시도하지 않는다.
            return "duplicate_ignored"

        if ledger.event_type == PaymentLedger.EventType.CAPTURE:
            payment.captured_amount += ledger.amount
            payment.status = Payment.Status.PAID

        elif ledger.event_type == PaymentLedger.EventType.REFUND:
            if payment.refunded_amount + ledger.amount > payment.captured_amount:
                raise ValueError("refund amount exceeds captured amount")

            payment.refunded_amount += ledger.amount

            if payment.refunded_amount == payment.captured_amount:
                payment.status = Payment.Status.REFUNDED
            else:
                payment.status = Payment.Status.PARTIAL_REFUNDED

        payment.save(
            update_fields=[
                "captured_amount",
                "refunded_amount",
                "status",
                "updated_at",
            ]
        )

        return "applied"
```

여기서 중요한 점은 두 가지입니다.

첫째, `Payment.objects.select_for_update()`로 같은 주문/결제에 대한 동시 처리를 직렬화합니다. 환불 이벤트 두 개가 동시에 들어왔을 때 `refunded_amount <= captured_amount` 같은 불변식이 깨지는 것을 막습니다.

둘째, 원장 insert의 unique constraint가 idempotency의 최종 방어선입니다. 애플리케이션에서 먼저 조회해서 “없으면 생성”하는 방식만 쓰면 race condition이 생깁니다. 반드시 DB unique constraint가 있어야 합니다.

**락 범위**

락은 `Payment` 또는 `OrderPaymentSummary`처럼 “현재 누적 상태를 가진 row”에 거는 것이 좋습니다. `Order` 전체를 잠그면 주문 수정, 배송 상태 변경 등 다른 흐름과 불필요하게 충돌할 수 있습니다.

권장:

```python
Payment.objects.select_for_update().get(order_id=order_id)
```

피해야 할 패턴:

```python
if not PaymentLedger.objects.filter(idempotency_key=key).exists():
    PaymentLedger.objects.create(...)
```

이 패턴은 동시 요청에서 중복 insert를 막지 못합니다.

**원장 중복 방지 제약조건**

최소 제약:

```python
UniqueConstraint(
    fields=["pg_provider", "idempotency_key"],
    name="uq_payment_ledger_provider_idempotency_key",
)
```

PG 이벤트 ID가 항상 존재하고 안정적이라면 추가로 둘 수 있습니다.

```python
UniqueConstraint(
    fields=["pg_provider", "pg_event_id"],
    condition=models.Q(pg_event_id__isnull=False),
    name="uq_payment_ledger_provider_pg_event_id",
)
```

PostgreSQL 기준 partial unique index로 생성됩니다. 같은 PG 이벤트 ID가 두 번 들어오는 경우도 막을 수 있습니다.

**마이그레이션 검증**

마이그레이션 전 검증 쿼리를 먼저 돌려야 합니다.

중복 idempotency key 확인:

```sql
SELECT pg_provider, idempotency_key, COUNT(*)
FROM payment_ledger
GROUP BY pg_provider, idempotency_key
HAVING COUNT(*) > 1;
```

금액 이상치 확인:

```sql
SELECT id, amount
FROM payment_ledger
WHERE amount <= 0;
```

환불 누계 이상 확인:

```sql
SELECT payment_id,
       SUM(CASE WHEN event_type = 'capture' THEN amount ELSE 0 END) AS captured,
       SUM(CASE WHEN event_type = 'refund' THEN amount ELSE 0 END) AS refunded
FROM payment_ledger
GROUP BY payment_id
HAVING SUM(CASE WHEN event_type = 'refund' THEN amount ELSE 0 END)
     > SUM(CASE WHEN event_type = 'capture' THEN amount ELSE 0 END);
```

Django migration에서는 `RunSQL` 또는 별도 management command로 사전 검증을 두는 편이 좋습니다. 운영 DB에 이미 데이터가 있으면 unique constraint 추가가 실패할 수 있으므로, 먼저 중복을 정리한 뒤 constraint를 추가해야 합니다.

**테스트해야 할 케이스**

- 같은 `pg_provider`, `idempotency_key` 이벤트가 두 번 들어오면 원장은 하나만 생긴다.
- 중복 이벤트 두 번째 요청도 PG에는 성공 응답을 반환한다.
- 같은 결제에 대해 환불 이벤트 두 개가 동시에 들어와도 `refunded_amount > captured_amount`가 되지 않는다.
- `IntegrityError` 발생 시 transaction 전체가 불필요하게 실패하지 않도록 중복 이벤트 경로를 명확히 처리한다.
- 원장 생성 후 상태 갱신 중 예외가 나면 원장도 rollback된다.
- unique constraint가 실제 DB migration에 반영되어 있다.

핵심 설계 결론은 이렇습니다. **중복 방지는 애플리케이션 로직이 아니라 DB unique constraint로 보장하고**, **금액 누계와 결제 상태는 `select_for_update()`로 잠근 현재 상태 row 안에서 갱신하며**, **원장은 감사 가능한 append-only 기록으로 남기는 구조**가 가장 안전합니다.