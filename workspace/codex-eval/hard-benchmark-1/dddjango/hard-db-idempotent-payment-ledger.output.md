**[주요 내용]**

대표 조회 패턴을 먼저 고정하고 스키마를 맞춥니다.

1. PG 웹훅 처리: `provider + idempotency_key` 또는 `provider + provider_event_id`로 중복 이벤트 확인
2. 주문 결제 상태 확인: `order_id`로 최신 결제 상태 조회
3. 원장 조회: `order_id`, `payment_id`, `occurred_at DESC` 기준으로 감사 추적
4. 정산/대사: `provider + provider_transaction_id`, 기간 범위, 이벤트 타입 기준 조회

핵심은 “중복 수신 방지 테이블”과 “불변 원장 테이블”을 분리하는 것입니다. 멱등성은 `PaymentEventInbox`가 맡고, 회계적 사실은 `PaymentLedgerEntry`에 append-only로 남깁니다.

```python
class PaymentEventInbox(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "received"
        APPLIED = "applied"
        FAILED = "failed"

    provider = models.CharField(max_length=32)
    idempotency_key = models.CharField(max_length=128)
    provider_event_id = models.CharField(max_length=128, null=True, blank=True)
    payload_hash = models.CharField(max_length=64)
    status = models.CharField(max_length=16, choices=Status, default=Status.RECEIVED)
    ledger_entry = models.OneToOneField(
        "PaymentLedgerEntry",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="source_event",
    )
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "idempotency_key"],
                name="uq_payment_event_provider_idempotency_key",
            ),
            models.UniqueConstraint(
                fields=["provider", "provider_event_id"],
                condition=models.Q(provider_event_id__isnull=False),
                name="uq_payment_event_provider_event_id",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "received_at"], name="idx_payment_event_status_received"),
        ]


class PaymentLedgerEntry(models.Model):
    class EntryType(models.TextChoices):
        AUTHORIZED = "authorized"
        CAPTURED = "captured"
        REFUNDED = "refunded"
        CANCELED = "canceled"

    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT)
    payment = models.ForeignKey("payments.Payment", on_delete=models.PROTECT)
    provider = models.CharField(max_length=32)
    provider_transaction_id = models.CharField(max_length=128)
    entry_type = models.CharField(max_length=16, choices=EntryType)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3)
    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="ck_payment_ledger_amount_positive",
            ),
            models.UniqueConstraint(
                fields=["provider", "provider_transaction_id", "entry_type"],
                name="uq_payment_ledger_provider_tx_type",
            ),
        ]
        indexes = [
            models.Index(fields=["order", "-occurred_at"], name="idx_payment_ledger_order_time"),
            models.Index(fields=["payment", "-occurred_at"], name="idx_payment_ledger_payment_time"),
            models.Index(fields=["provider", "provider_transaction_id"], name="idx_payment_ledger_provider_tx"),
            models.Index(fields=["entry_type", "occurred_at"], name="idx_payment_ledger_type_time"),
        ]
```

처리 흐름은 `transaction.atomic()` 안에서 한 번에 끝냅니다. 같은 주문 결제 상태 전이를 동시에 처리하지 못하게 `Payment` 또는 `Order` 행을 `select_for_update()`로 잠급니다. 중복 이벤트는 DB unique constraint가 최종 방어선입니다.

```python
from django.db import IntegrityError, transaction

def apply_pg_event(event):
    with transaction.atomic():
        payment = (
            Payment.objects
            .select_for_update()
            .get(order_id=event.order_id)
        )

        try:
            inbox = PaymentEventInbox.objects.create(
                provider=event.provider,
                idempotency_key=event.idempotency_key,
                provider_event_id=event.provider_event_id,
                payload_hash=event.payload_hash,
            )
        except IntegrityError:
            return (
                PaymentEventInbox.objects
                .select_for_update()
                .select_related("ledger_entry")
                .get(provider=event.provider, idempotency_key=event.idempotency_key)
                .ledger_entry
            )

        ledger_entry = PaymentLedgerEntry.objects.create(
            order_id=event.order_id,
            payment=payment,
            provider=event.provider,
            provider_transaction_id=event.provider_transaction_id,
            entry_type=event.entry_type,
            amount=event.amount,
            currency=event.currency,
            occurred_at=event.occurred_at,
        )

        payment.apply_ledger_entry(ledger_entry)
        payment.save(update_fields=["status", "paid_amount", "updated_at"])

        inbox.status = PaymentEventInbox.Status.APPLIED
        inbox.ledger_entry = ledger_entry
        inbox.save(update_fields=["status", "ledger_entry"])

        return ledger_entry
```

원장은 update/delete 하지 않는 것을 애플리케이션 규칙으로 두고, 환불/취소/정정은 새 `PaymentLedgerEntry`를 추가합니다. 운영 강도가 높으면 DB trigger로 `payment_ledger_entry`의 `UPDATE/DELETE`를 막는 migration을 추가하는 것이 더 확실합니다.

마이그레이션 검증은 최소한 아래를 봅니다.

```bash
python manage.py makemigrations payments --check --dry-run
python manage.py sqlmigrate payments 0001
python manage.py migrate --plan
python manage.py migrate
python manage.py check
```

PostgreSQL이면 배포 전후에 대표 쿼리로 `EXPLAIN ANALYZE`를 확인합니다.

```sql
EXPLAIN ANALYZE
SELECT *
FROM payments_paymentledgerentry
WHERE order_id = 123
ORDER BY occurred_at DESC;
```

---
> **관련 스킬 참조:**
> - Django 모델/마이그레이션 구현 → **implementation-django** 스킬
> - 인덱스/제약조건/트랜잭션 설계 → **architecture-db** 스킬