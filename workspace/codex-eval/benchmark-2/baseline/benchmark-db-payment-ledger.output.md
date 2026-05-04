작업 디렉터리가 비어 있고 `config.toml`도 없어서 기존 프로젝트 스타일은 확인할 수 없었습니다. 아래는 Django 모델 기준으로 바로 적용 가능한 결제 ledger 설계입니다.

```python
# payments/models.py

from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class LedgerStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    POSTED = "posted", "Posted"
    FAILED = "failed", "Failed"
    REVERSED = "reversed", "Reversed"
    CANCELED = "canceled", "Canceled"


class LedgerDirection(models.TextChoices):
    DEBIT = "debit", "Debit"
    CREDIT = "credit", "Credit"


class PaymentLedgerEntry(models.Model):
    """
    결제 원장 엔트리.

    권장 정책:
    - posted/reversed 상태의 금액, 통화, direction은 수정하지 않는다.
    - 정정은 기존 row 수정이 아니라 reversal/refund row를 추가한다.
    """

    id = models.BigAutoField(primary_key=True)

    # 외부/내부 참조
    payment_id = models.CharField(max_length=64, db_index=True)
    order_id = models.CharField(max_length=64, db_index=True, blank=True)
    customer_id = models.CharField(max_length=64, db_index=True, blank=True)

    # idempotency
    idempotency_key = models.CharField(max_length=128)
    idempotency_scope = models.CharField(
        max_length=64,
        default="payment",
        help_text="예: payment, refund, capture, cancel",
    )

    # 금액
    amount = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        validators=[MinValueValidator(Decimal("0.0001"))],
        help_text="통화 minor unit 차이를 흡수하기 위해 4 decimal places 사용",
    )
    currency = models.CharField(
        max_length=3,
        help_text="ISO-4217 currency code, e.g. KRW, USD",
    )
    direction = models.CharField(
        max_length=10,
        choices=LedgerDirection.choices,
    )

    # 상태
    status = models.CharField(
        max_length=20,
        choices=LedgerStatus.choices,
        default=LedgerStatus.PENDING,
        db_index=True,
    )

    # 공급자 정보
    provider = models.CharField(max_length=40, blank=True)
    provider_transaction_id = models.CharField(max_length=128, blank=True, db_index=True)
    provider_payload = models.JSONField(default=dict, blank=True)

    # 정정/취소 추적
    original_entry = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="adjustment_entries",
        help_text="refund/reversal/cancel entry가 원본 ledger entry를 참조",
    )

    # audit 기본 필드
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "payment_ledger_entry"
        indexes = [
            models.Index(fields=["payment_id", "status"]),
            models.Index(fields=["order_id", "created_at"]),
            models.Index(fields=["currency", "status"]),
            models.Index(fields=["provider", "provider_transaction_id"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["idempotency_scope", "idempotency_key"],
                name="uq_payment_ledger_idempotency",
            ),
            models.CheckConstraint(
                check=Q(amount__gt=0),
                name="ck_payment_ledger_amount_positive",
            ),
            models.CheckConstraint(
                check=Q(currency__regex=r"^[A-Z]{3}$"),
                name="ck_payment_ledger_currency_iso_4217_shape",
            ),
        ]

    def __str__(self):
        return f"{self.payment_id} {self.direction} {self.amount} {self.currency} {self.status}"
```

Audit trail은 별도 append-only 테이블로 두는 게 좋습니다. 원장 row의 최종 상태만 보면 안 되고, 상태 전이와 운영자/시스템 변경 이력을 따로 남겨야 합니다.

```python
class PaymentLedgerAuditLog(models.Model):
    id = models.BigAutoField(primary_key=True)

    ledger_entry = models.ForeignKey(
        PaymentLedgerEntry,
        on_delete=models.PROTECT,
        related_name="audit_logs",
    )

    action = models.CharField(
        max_length=40,
        help_text="created, status_changed, provider_synced, reversed 등",
    )

    previous_status = models.CharField(
        max_length=20,
        choices=LedgerStatus.choices,
        blank=True,
    )
    new_status = models.CharField(
        max_length=20,
        choices=LedgerStatus.choices,
        blank=True,
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )
    actor_type = models.CharField(
        max_length=20,
        default="system",
        help_text="system, user, provider, admin",
    )

    request_id = models.CharField(max_length=64, blank=True, db_index=True)
    idempotency_key = models.CharField(max_length=128, blank=True, db_index=True)

    changes = models.JSONField(default=dict, blank=True)
    note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "payment_ledger_audit_log"
        indexes = [
            models.Index(fields=["ledger_entry", "created_at"]),
            models.Index(fields=["action", "created_at"]),
        ]
```

핵심 설계 기준은 이렇습니다.

- 금액은 `DecimalField`를 사용하고 `FloatField`는 피합니다.
- 통화는 ISO-4217 기준 `CharField(max_length=3)`로 저장합니다.
- idempotency는 `idempotency_scope + idempotency_key` 유니크 제약으로 잡습니다.
- 결제 취소, 환불, 정정은 기존 row 수정이 아니라 새 ledger entry로 추가하고 `original_entry`로 연결합니다.
- audit trail은 ledger row 내부 JSON에만 넣지 말고 별도 append-only 로그 테이블로 둡니다.
- `posted` 이후 원장 핵심 필드 변경은 서비스 레이어에서 막는 편이 안전합니다.