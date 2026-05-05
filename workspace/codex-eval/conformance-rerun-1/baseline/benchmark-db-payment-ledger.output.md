아래 설계는 “결제/환불 이력은 절대 수정하지 않고 append-only로 쌓는다”는 전제를 둡니다. 핵심은 `Payment` 같은 현재 상태 테이블과, 불변 원장인 `PaymentLedgerEntry`를 분리하는 방식입니다.

**핵심 테이블**

```python
# payments/models.py
from django.db import models
from django.db.models import Q


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        AUTHORIZED = "authorized"
        PAID = "paid"
        PARTIALLY_REFUNDED = "partially_refunded"
        REFUNDED = "refunded"
        FAILED = "failed"
        CANCELED = "canceled"

    order_id = models.BigIntegerField(db_index=True)
    merchant_uid = models.CharField(max_length=100, unique=True)

    currency = models.CharField(max_length=3)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    refunded_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    status = models.CharField(max_length=32, choices=Status.choices, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PaymentLedgerEntry(models.Model):
    class EntryType(models.TextChoices):
        PAYMENT_REQUESTED = "payment_requested"
        PAYMENT_AUTHORIZED = "payment_authorized"
        PAYMENT_CAPTURED = "payment_captured"
        PAYMENT_FAILED = "payment_failed"
        REFUND_REQUESTED = "refund_requested"
        REFUND_SUCCEEDED = "refund_succeeded"
        REFUND_FAILED = "refund_failed"
        WEBHOOK_RECEIVED = "webhook_received"

    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        related_name="ledger_entries",
    )

    entry_type = models.CharField(max_length=40, choices=EntryType.choices)
    idempotency_key = models.CharField(max_length=200)

    pg_provider = models.CharField(max_length=40)
    pg_transaction_id = models.CharField(max_length=120, blank=True)
    pg_event_id = models.CharField(max_length=120, blank=True)

    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=3)

    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    # 원본 webhook / PG 응답 보관. 감사 목적.
    payload = models.JSONField(default=dict)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["pg_provider", "idempotency_key"],
                name="uq_ledger_provider_idempotency_key",
            ),
            models.UniqueConstraint(
                fields=["pg_provider", "pg_event_id"],
                condition=~Q(pg_event_id=""),
                name="uq_ledger_provider_pg_event_id",
            ),
            models.CheckConstraint(
                check=Q(amount__gte=0),
                name="ck_ledger_amount_non_negative",
            ),
        ]
        indexes = [
            models.Index(
                fields=["payment", "created_at"],
                name="idx_ledger_payment_created",
            ),
            models.Index(
                fields=["pg_provider", "pg_transaction_id"],
                name="idx_ledger_pg_tx",
            ),
            models.Index(
                fields=["entry_type", "created_at"],
                name="idx_ledger_type_created",
            ),
            models.Index(
                fields=["created_at"],
                name="idx_ledger_created",
            ),
        ]
```

**조회 패턴 기준 인덱스**

주요 조회가 아래라면 위 인덱스가 기준입니다.

```sql
-- 결제 상세 화면: 결제별 이력 시간순
WHERE payment_id = ? ORDER BY created_at ASC

-- webhook 중복 확인
WHERE pg_provider = ? AND pg_event_id = ?

-- PG 거래번호로 추적
WHERE pg_provider = ? AND pg_transaction_id = ?

-- 운영/정산 배치
WHERE entry_type = ? AND created_at BETWEEN ? AND ?
```

`idempotency_key`는 PG 요청 재시도, webhook 재전송, 내부 잡 재시도 모두를 막는 키입니다. 보통 다음처럼 만듭니다.

```text
payment:{merchant_uid}:capture:{pg_attempt_id}
refund:{payment_id}:{refund_request_id}
webhook:{provider}:{pg_event_id}
```

동일 작업을 재시도하면 반드시 같은 key를 사용해야 합니다.

**불변성**

원장 테이블은 update/delete를 애플리케이션 레벨에서 금지합니다.

```python
class ImmutableLedgerQuerySet(models.QuerySet):
    def update(self, *args, **kwargs):
        raise RuntimeError("Ledger entries are immutable")

    def delete(self):
        raise RuntimeError("Ledger entries are immutable")
```

운영 DB에서는 가능하면 DB 트리거까지 둡니다.

```sql
CREATE OR REPLACE FUNCTION prevent_ledger_update_delete()
RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'payment ledger is immutable';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevent_ledger_update
BEFORE UPDATE OR DELETE ON payments_paymentledgerentry
FOR EACH ROW EXECUTE FUNCTION prevent_ledger_update_delete();
```

Django만으로는 `QuerySet.update()`나 직접 SQL을 완전히 막을 수 없기 때문에, 회계/정산 성격이면 DB 제약이 더 안전합니다.

**트랜잭션 처리**

결제 상태 갱신과 원장 insert는 같은 transaction 안에서 처리합니다.

```python
from django.db import IntegrityError, transaction

def record_payment_event(*, payment_id, idempotency_key, entry_type, amount, payload):
    try:
        with transaction.atomic():
            payment = (
                Payment.objects
                .select_for_update()
                .get(id=payment_id)
            )

            entry = PaymentLedgerEntry.objects.create(
                payment=payment,
                idempotency_key=idempotency_key,
                entry_type=entry_type,
                pg_provider=payload["provider"],
                pg_transaction_id=payload.get("transaction_id", ""),
                pg_event_id=payload.get("event_id", ""),
                amount=amount,
                currency=payment.currency,
                occurred_at=payload["occurred_at"],
                payload=payload,
            )

            # 현재 상태 테이블은 파생 상태로만 갱신
            apply_payment_state(payment, entry)
            payment.save(update_fields=["status", "refunded_amount", "updated_at"])

            return entry, True

    except IntegrityError:
        # unique idempotency key 또는 pg_event_id 충돌이면 이미 처리된 이벤트
        existing = PaymentLedgerEntry.objects.get(
            pg_provider=payload["provider"],
            idempotency_key=idempotency_key,
        )
        return existing, False
```

중요한 점은 `select_for_update()`로 `Payment` row를 잠그는 것입니다. refund webhook이 동시에 여러 개 들어와도 `refunded_amount` 계산과 상태 전이가 꼬이지 않습니다.

**제약조건**

권장 제약은 다음입니다.

```text
Payment.merchant_uid unique
Ledger(pg_provider, idempotency_key) unique
Ledger(pg_provider, pg_event_id) unique where pg_event_id != ''
Ledger.amount >= 0
Ledger.payment_id on_delete=PROTECT
```

추가로 환불 총액이 결제 금액을 넘지 않아야 합니다. 이건 단일 row check constraint로는 어렵기 때문에 transaction 안에서 `select_for_update()` 후 검증하거나, PostgreSQL trigger/materialized aggregate로 강제합니다.

```python
if payment.refunded_amount + entry.amount > payment.amount:
    raise ValueError("Refund amount exceeds paid amount")
```

**Migration 검증**

마이그레이션에는 최소한 다음 검증을 포함합니다.

```python
from django.core.exceptions import ValidationError
from django.db import migrations


def validate_existing_ledger(apps, schema_editor):
    Ledger = apps.get_model("payments", "PaymentLedgerEntry")

    duplicated = (
        Ledger.objects
        .values("pg_provider", "idempotency_key")
        .annotate(count=models.Count("id"))
        .filter(count__gt=1)
    )

    if duplicated.exists():
        raise RuntimeError("Duplicate ledger idempotency keys exist")

    invalid_amount = Ledger.objects.filter(amount__lt=0)
    if invalid_amount.exists():
        raise RuntimeError("Negative ledger amount exists")
```

실제 운영 DB라면 unique constraint 추가 전에 별도 dry-run SQL로 먼저 확인하는 편이 안전합니다.

```sql
SELECT pg_provider, idempotency_key, COUNT(*)
FROM payments_paymentledgerentry
GROUP BY pg_provider, idempotency_key
HAVING COUNT(*) > 1;

SELECT id
FROM payments_paymentledgerentry
WHERE amount < 0;
```

정리하면, 원장은 append-only 이벤트 저장소로 두고, `Payment`는 빠른 조회를 위한 현재 상태 projection으로 봐야 합니다. 중복 webhook과 PG 재시도는 `idempotency_key` unique constraint로 막고, 상태 전이는 `transaction.atomic()` + `select_for_update()` 안에서만 수행하는 구조가 가장 안정적입니다.