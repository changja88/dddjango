현재 디렉터리가 비어 있고 `config.toml`도 없어 파일 수정은 못 했습니다. 아래는 Django 모델 기준 설계안입니다.

```python
import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class PaymentLedgerStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    AUTHORIZED = "authorized", "Authorized"
    CAPTURED = "captured", "Captured"
    SETTLED = "settled", "Settled"
    FAILED = "failed", "Failed"
    CANCELED = "canceled", "Canceled"
    REFUNDED = "refunded", "Refunded"
    PARTIALLY_REFUNDED = "partially_refunded", "Partially refunded"


class PaymentLedgerType(models.TextChoices):
    AUTHORIZATION = "authorization", "Authorization"
    CAPTURE = "capture", "Capture"
    REFUND = "refund", "Refund"
    VOID = "void", "Void"
    ADJUSTMENT = "adjustment", "Adjustment"


class PaymentLedger(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Business references
    order_id = models.CharField(max_length=64, db_index=True)
    customer_id = models.CharField(max_length=64, blank=True, db_index=True)

    # Idempotency
    idempotency_key = models.CharField(max_length=255)
    request_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="SHA-256 hash of normalized request payload.",
    )

    # Money
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    currency = models.CharField(
        max_length=3,
        help_text="ISO-4217 currency code, e.g. KRW, USD.",
    )

    ledger_type = models.CharField(
        max_length=32,
        choices=PaymentLedgerType.choices,
    )
    status = models.CharField(
        max_length=32,
        choices=PaymentLedgerStatus.choices,
        default=PaymentLedgerStatus.PENDING,
        db_index=True,
    )

    # External payment provider data
    provider = models.CharField(max_length=64, blank=True)
    provider_transaction_id = models.CharField(max_length=128, blank=True, db_index=True)
    provider_payload = models.JSONField(default=dict, blank=True)

    # Audit columns
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "payment_ledger"
        constraints = [
            models.UniqueConstraint(
                fields=["idempotency_key"],
                name="uq_payment_ledger_idempotency_key",
            ),
            models.CheckConstraint(
                check=Q(amount__gte=0),
                name="ck_payment_ledger_amount_non_negative",
            ),
            models.CheckConstraint(
                check=Q(currency__regex=r"^[A-Z]{3}$"),
                name="ck_payment_ledger_currency_iso_4217_shape",
            ),
        ]
        indexes = [
            models.Index(fields=["order_id", "status"]),
            models.Index(fields=["provider", "provider_transaction_id"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.order_id} {self.ledger_type} {self.amount} {self.currency} {self.status}"
```

Audit trail은 상태 변경 이력을 별도 append-only 테이블로 두는 편이 좋습니다.

```python
class PaymentLedgerAuditEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ledger = models.ForeignKey(
        PaymentLedger,
        on_delete=models.CASCADE,
        related_name="audit_events",
    )

    previous_status = models.CharField(
        max_length=32,
        choices=PaymentLedgerStatus.choices,
        null=True,
        blank=True,
    )
    new_status = models.CharField(
        max_length=32,
        choices=PaymentLedgerStatus.choices,
    )

    reason = models.CharField(max_length=255, blank=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )

    request_id = models.CharField(max_length=128, blank=True, db_index=True)
    idempotency_key = models.CharField(max_length=255, blank=True)
    snapshot = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payment_ledger_audit_event"
        indexes = [
            models.Index(fields=["ledger", "created_at"]),
            models.Index(fields=["new_status", "created_at"]),
        ]
        ordering = ["created_at"]
```

핵심 설계 포인트는 다음입니다.

- 금액은 `DecimalField` 사용. 정산/결제 금액에는 `FloatField` 금지.
- 통화는 ISO-4217 기준 `CharField(max_length=3)`로 저장.
- `idempotency_key`는 unique constraint로 중복 결제 방지.
- 상태 변경 이력은 `PaymentLedgerAuditEvent`에 append-only로 기록.
- 원본 PG 응답은 `provider_payload`, 업무용 확장은 `metadata`에 분리.
- 운영 환경에서는 `idempotency_key`를 전체 unique로 둘지, `merchant_id + idempotency_key` 복합 unique로 둘지 서비스 범위에 맞춰 정하면 됩니다.