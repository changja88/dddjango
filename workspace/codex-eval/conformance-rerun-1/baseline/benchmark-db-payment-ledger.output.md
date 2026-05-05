아래는 Django 기준의 “불변 결제 원장(payment ledger)” 설계안입니다. 핵심은 **상태 테이블과 이력 테이블을 분리**하고, PG 재시도와 중복 webhook은 **idempotency key + DB 제약조건**으로 막는 구조입니다.

**핵심 모델**
```python
# payments/models.py
from django.db import models
from django.utils import timezone


class PaymentIntent(models.Model):
    """
    현재 결제 상태를 빠르게 조회하기 위한 mutable aggregate.
    원장 자체는 PaymentLedgerEntry에 불변으로 남긴다.
    """
    class Status(models.TextChoices):
        PENDING = "pending"
        AUTHORIZED = "authorized"
        CAPTURED = "captured"
        PARTIALLY_REFUNDED = "partially_refunded"
        REFUNDED = "refunded"
        FAILED = "failed"
        CANCELED = "canceled"

    merchant_order_id = models.CharField(max_length=100)
    user_id = models.BigIntegerField(db_index=True)

    currency = models.CharField(max_length=3)
    amount = models.PositiveBigIntegerField()  # minor unit: KRW 1000, USD cents

    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING,
    )

    pg_provider = models.CharField(max_length=32)
    pg_payment_id = models.CharField(max_length=128, null=True, blank=True)

    authorized_amount = models.PositiveBigIntegerField(default=0)
    captured_amount = models.PositiveBigIntegerField(default=0)
    refunded_amount = models.PositiveBigIntegerField(default=0)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["merchant_order_id"],
                name="uq_payment_intent_merchant_order_id",
            ),
            models.UniqueConstraint(
                fields=["pg_provider", "pg_payment_id"],
                condition=models.Q(pg_payment_id__isnull=False),
                name="uq_payment_intent_pg_payment",
            ),
            models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name="ck_payment_intent_amount_gt_0",
            ),
            models.CheckConstraint(
                check=models.Q(authorized_amount__gte=0)
                & models.Q(captured_amount__gte=0)
                & models.Q(refunded_amount__gte=0),
                name="ck_payment_intent_amounts_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(refunded_amount__lte=models.F("captured_amount")),
                name="ck_payment_intent_refund_lte_capture",
            ),
        ]
        indexes = [
            models.Index(fields=["user_id", "-created_at"], name="idx_payment_user_created"),
            models.Index(fields=["status", "-created_at"], name="idx_payment_status_created"),
            models.Index(fields=["merchant_order_id"], name="idx_payment_order"),
        ]


class PaymentLedgerEntry(models.Model):
    """
    append-only 불변 원장.
    결제 승인, 매입, 실패, 취소, 환불, webhook 수신 결과를 모두 event로 남긴다.
    """
    class EntryType(models.TextChoices):
        AUTHORIZE_REQUESTED = "authorize_requested"
        AUTHORIZE_SUCCEEDED = "authorize_succeeded"
        AUTHORIZE_FAILED = "authorize_failed"

        CAPTURE_REQUESTED = "capture_requested"
        CAPTURE_SUCCEEDED = "capture_succeeded"
        CAPTURE_FAILED = "capture_failed"

        REFUND_REQUESTED = "refund_requested"
        REFUND_SUCCEEDED = "refund_succeeded"
        REFUND_FAILED = "refund_failed"

        CANCELED = "canceled"
        WEBHOOK_RECEIVED = "webhook_received"

    payment = models.ForeignKey(
        PaymentIntent,
        on_delete=models.PROTECT,
        related_name="ledger_entries",
    )

    entry_type = models.CharField(max_length=64, choices=EntryType.choices)

    # + 금액: 결제/매입 증가, - 금액 대신 entry_type으로 의미 구분해도 됨.
    # 단순성을 위해 amount는 항상 양수, 의미는 entry_type에서 판단.
    amount = models.PositiveBigIntegerField(default=0)
    currency = models.CharField(max_length=3)

    pg_provider = models.CharField(max_length=32)
    pg_payment_id = models.CharField(max_length=128, null=True, blank=True)
    pg_refund_id = models.CharField(max_length=128, null=True, blank=True)
    pg_event_id = models.CharField(max_length=128, null=True, blank=True)

    # 내부 요청 재시도/외부 webhook 중복 방지의 핵심
    idempotency_key = models.CharField(max_length=160)

    # PG 원본 응답/웹훅 payload. 감사 목적.
    payload = models.JSONField(default=dict)

    occurred_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["pg_provider", "idempotency_key"],
                name="uq_ledger_provider_idempotency_key",
            ),
            models.UniqueConstraint(
                fields=["pg_provider", "pg_event_id"],
                condition=models.Q(pg_event_id__isnull=False),
                name="uq_ledger_provider_pg_event_id",
            ),
            models.UniqueConstraint(
                fields=["pg_provider", "pg_refund_id"],
                condition=models.Q(pg_refund_id__isnull=False),
                name="uq_ledger_provider_pg_refund_id",
            ),
            models.CheckConstraint(
                check=models.Q(amount__gte=0),
                name="ck_ledger_amount_gte_0",
            ),
        ]
        indexes = [
            models.Index(fields=["payment", "created_at"], name="idx_ledger_payment_created"),
            models.Index(fields=["pg_provider", "pg_payment_id"], name="idx_ledger_pg_payment"),
            models.Index(fields=["pg_provider", "idempotency_key"], name="idx_ledger_idempotency"),
            models.Index(fields=["entry_type", "-created_at"], name="idx_ledger_type_created"),
        ]
```

**불변성 보장**
Django 레벨만 믿으면 부족합니다. 최소한 아래 정책을 둡니다.

```python
class PaymentLedgerEntry(models.Model):
    # fields...

    def save(self, *args, **kwargs):
        if self.pk:
            raise RuntimeError("PaymentLedgerEntry is immutable")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise RuntimeError("PaymentLedgerEntry cannot be deleted")
```

운영 DB에서는 더 강하게 하려면 PostgreSQL trigger로 `UPDATE`, `DELETE`를 막는 것을 권장합니다. Django 코드 우회, admin 수정, SQL 콘솔 실수를 막을 수 있습니다.

**조회 패턴**
주요 조회는 보통 네 가지입니다.

```sql
-- 주문 기준 결제 상태 조회
WHERE merchant_order_id = ?

-- 사용자 결제 목록
WHERE user_id = ?
ORDER BY created_at DESC

-- PG payment id로 reconciliation
WHERE pg_provider = ? AND pg_payment_id = ?

-- 특정 결제의 원장 이력
WHERE payment_id = ?
ORDER BY created_at ASC
```

그래서 `PaymentIntent`에는 `merchant_order_id`, `(user_id, -created_at)`, `(status, -created_at)`, `(pg_provider, pg_payment_id)`가 필요합니다.
`PaymentLedgerEntry`에는 `(payment_id, created_at)`, `(pg_provider, pg_payment_id)`, `(pg_provider, idempotency_key)`, `(pg_provider, pg_event_id)`가 필요합니다.

**Idempotency 전략**
내부 결제 요청:

```text
idempotency_key = "{operation}:{payment_id}:{client_request_id}"
예: "capture:12345:9db2..."
```

webhook:

```text
idempotency_key = "webhook:{pg_provider}:{pg_event_id}"
```

PG가 event id를 안정적으로 주지 않는다면:

```text
idempotency_key = "webhook:{pg_provider}:{pg_payment_id}:{event_type}:{pg_created_at}:{amount}"
```

다만 이 fallback은 충돌 가능성이 있으므로 PG가 제공하는 고유 이벤트 ID를 우선해야 합니다.

**트랜잭션 처리**
결제/환불 반영은 반드시 한 transaction 안에서 `PaymentIntent`를 잠그고 원장 insert와 상태 갱신을 같이 처리합니다.

```python
from django.db import IntegrityError, transaction


def record_capture_success(*, payment_id, amount, currency, provider, pg_payment_id, idempotency_key, payload):
    with transaction.atomic():
        payment = (
            PaymentIntent.objects
            .select_for_update()
            .get(id=payment_id)
        )

        try:
            PaymentLedgerEntry.objects.create(
                payment=payment,
                entry_type=PaymentLedgerEntry.EntryType.CAPTURE_SUCCEEDED,
                amount=amount,
                currency=currency,
                pg_provider=provider,
                pg_payment_id=pg_payment_id,
                idempotency_key=idempotency_key,
                payload=payload,
            )
        except IntegrityError:
            # 이미 같은 idempotency key로 처리됨.
            return payment

        if payment.captured_amount + amount > payment.amount:
            raise ValueError("captured amount exceeds payment amount")

        payment.captured_amount += amount
        payment.status = PaymentIntent.Status.CAPTURED
        payment.pg_payment_id = pg_payment_id
        payment.save(
            update_fields=[
                "captured_amount",
                "status",
                "pg_payment_id",
                "updated_at",
            ]
        )

        return payment
```

환불도 동일하게 `select_for_update()`로 결제 row를 잠근 뒤:

```python
if payment.refunded_amount + refund_amount > payment.captured_amount:
    raise ValueError("refund amount exceeds captured amount")
```

검증 후 원장 insert, aggregate 갱신을 같이 수행합니다.

**Webhook 처리 흐름**
```python
def handle_webhook(event):
    idempotency_key = f"webhook:{event.provider}:{event.event_id}"

    with transaction.atomic():
        payment = (
            PaymentIntent.objects
            .select_for_update()
            .get(pg_provider=event.provider, pg_payment_id=event.payment_id)
        )

        try:
            PaymentLedgerEntry.objects.create(
                payment=payment,
                entry_type=map_event_type(event),
                amount=event.amount or 0,
                currency=event.currency,
                pg_provider=event.provider,
                pg_payment_id=event.payment_id,
                pg_event_id=event.event_id,
                idempotency_key=idempotency_key,
                payload=event.raw_payload,
                occurred_at=event.occurred_at,
            )
        except IntegrityError:
            return "duplicate"

        apply_event_to_payment(payment, event)
        payment.save()
        return "processed"
```

중복 webhook은 `uq_ledger_provider_idempotency_key` 또는 `uq_ledger_provider_pg_event_id`에서 막힙니다.

**마이그레이션 검증**
마이그레이션에는 단순 생성만 넣지 말고 DB 제약이 실제로 생성됐는지 테스트해야 합니다.

테스트 예시:

```python
import pytest
from django.db import IntegrityError, transaction


@pytest.mark.django_db
def test_ledger_idempotency_key_is_unique(payment):
    PaymentLedgerEntry.objects.create(
        payment=payment,
        entry_type="capture_succeeded",
        amount=1000,
        currency="KRW",
        pg_provider="toss",
        idempotency_key="capture:1:req-1",
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            PaymentLedgerEntry.objects.create(
                payment=payment,
                entry_type="capture_succeeded",
                amount=1000,
                currency="KRW",
                pg_provider="toss",
                idempotency_key="capture:1:req-1",
            )


@pytest.mark.django_db
def test_refund_cannot_exceed_capture(payment):
    payment.captured_amount = 1000
    payment.refunded_amount = 1500

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            payment.save()
```

PostgreSQL 기준으로 migration 이후 확인할 항목:

```sql
\d payments_paymentintent
\d payments_paymentledgerentry

SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename IN ('payments_paymentintent', 'payments_paymentledgerentry');

SELECT conname, contype
FROM pg_constraint
WHERE conrelid IN (
  'payments_paymentintent'::regclass,
  'payments_paymentledgerentry'::regclass
);
```

**운영 권장사항**
결제 원장은 `PaymentLedgerEntry`를 정정하지 말고, 잘못된 이벤트가 있으면 “보정 이벤트”를 append 합니다. 상태 조회는 `PaymentIntent`에서 빠르게 하고, 감사/정산/reconciliation은 원장을 기준으로 재계산 가능해야 합니다.

정산 정확성이 중요하면 `PaymentIntent`의 금액 필드는 캐시로 보고, 배치 작업에서 원장 합계와 aggregate 값이 일치하는지 주기적으로 검증하는 reconciliation job을 두는 게 좋습니다.