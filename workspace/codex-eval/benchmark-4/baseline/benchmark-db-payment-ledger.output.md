저장소가 비어 있고 `config.toml`도 존재하지 않아 파일에는 반영하지 못했습니다. 아래는 Django 모델 기준의 결제 ledger 설계안입니다.

```python
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
import uuid


class LedgerStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    POSTED = "posted", "Posted"
    FAILED = "failed", "Failed"
    REVERSED = "reversed", "Reversed"


class LedgerDirection(models.TextChoices):
    DEBIT = "debit", "Debit"
    CREDIT = "credit", "Credit"


class PaymentLedger(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Domain references
    payment_id = models.UUIDField(db_index=True)
    customer_id = models.UUIDField(null=True, blank=True, db_index=True)
    merchant_id = models.UUIDField(null=True, blank=True, db_index=True)

    # Money
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=3)  # ISO-4217, e.g. USD, KRW
    direction = models.CharField(max_length=10, choices=LedgerDirection.choices)

    # Ledger lifecycle
    status = models.CharField(
        max_length=20,
        choices=LedgerStatus.choices,
        default=LedgerStatus.PENDING,
        db_index=True,
    )
    posted_at = models.DateTimeField(null=True, blank=True)
    reversed_at = models.DateTimeField(null=True, blank=True)

    # Idempotency
    idempotency_key = models.CharField(max_length=255)
    idempotency_scope = models.CharField(
        max_length=100,
        help_text="Logical scope such as payment:create, refund:create",
    )

    # External/payment provider references
    provider = models.CharField(max_length=50, blank=True)
    provider_transaction_id = models.CharField(max_length=255, blank=True)

    # Audit trail
    metadata = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payment_ledger"
        constraints = [
            models.CheckConstraint(
                check=Q(amount__gt=0),
                name="payment_ledger_amount_positive",
            ),
            models.CheckConstraint(
                check=Q(currency__regex=r"^[A-Z]{3}$"),
                name="payment_ledger_currency_iso_4217_shape",
            ),
            models.UniqueConstraint(
                fields=["idempotency_scope", "idempotency_key"],
                name="payment_ledger_unique_idempotency",
            ),
        ]
        indexes = [
            models.Index(fields=["payment_id", "status"]),
            models.Index(fields=["merchant_id", "created_at"]),
            models.Index(fields=["provider", "provider_transaction_id"]),
        ]

    def mark_posted(self):
        self.status = LedgerStatus.POSTED
        self.posted_at = timezone.now()

    def mark_reversed(self):
        self.status = LedgerStatus.REVERSED
        self.reversed_at = timezone.now()


class PaymentLedgerAudit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ledger = models.ForeignKey(
        PaymentLedger,
        related_name="audit_events",
        on_delete=models.CASCADE,
    )

    event_type = models.CharField(max_length=50)
    previous_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, blank=True)

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
    )
    reason = models.TextField(blank=True)
    payload = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        db_table = "payment_ledger_audit"
        indexes = [
            models.Index(fields=["ledger", "created_at"]),
            models.Index(fields=["event_type", "created_at"]),
        ]
```

핵심 설계는 다음 기준입니다.

- `amount`: `DecimalField` 사용. 결제 금액에는 `FloatField`를 쓰면 안 됩니다.
- `currency`: ISO-4217 기준 3자리 문자열. 예: `USD`, `KRW`.
- `status`: `pending -> posted / failed / reversed` 흐름을 명시.
- `idempotency`: `idempotency_scope + idempotency_key` 유니크 제약으로 중복 결제 요청 방지.
- `audit trail`: ledger 본문에는 현재 상태만 두고, 상태 변경/외부 응답/운영자 조치 이력은 `PaymentLedgerAudit`에 append-only로 남기는 구조.

운영 결제 시스템이라면 ledger row 자체는 가급적 수정하지 않고, 정정은 `reversed` 처리 후 별도 반대 방향 entry를 추가하는 방식이 더 안전합니다.