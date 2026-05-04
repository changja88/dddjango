**[주요 내용]**

결제 ledger는 돈의 정합성이 핵심이라 `FloatField`는 쓰지 않습니다. 권장 설계는 `amount_minor`를 정수 minor unit으로 저장하고, `currency`를 ISO-4217 3자리 컬럼으로 분리하는 방식입니다. 예: USD 10.25 → `amount_minor=1025`, `currency="USD"`.

```python
from django.conf import settings
from django.db import models
from django.db.models import Q


class PaymentLedger(models.Model):
    class Direction(models.TextChoices):
        CREDIT = "credit", "Credit"
        DEBIT = "debit", "Debit"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        POSTED = "posted", "Posted"
        FAILED = "failed", "Failed"
        REVERSED = "reversed", "Reversed"

    merchant_id = models.UUIDField()
    payment_id = models.UUIDField(db_index=True)

    idempotency_key = models.CharField(max_length=128)

    amount_minor = models.BigIntegerField()
    currency = models.CharField(max_length=3)
    direction = models.CharField(max_length=10, choices=Direction.choices)

    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
    )

    provider = models.CharField(max_length=40)
    provider_reference = models.CharField(max_length=128, blank=True)

    posted_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    reversed_at = models.DateTimeField(null=True, blank=True)

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
        constraints = [
            models.UniqueConstraint(
                fields=["merchant_id", "idempotency_key"],
                name="uq_payment_ledger_merchant_idempotency_key",
            ),
            models.CheckConstraint(
                condition=Q(amount_minor__gt=0),
                name="ck_payment_ledger_amount_minor_positive",
            ),
            models.CheckConstraint(
                condition=Q(currency__regex=r"^[A-Z]{3}$"),
                name="ck_payment_ledger_currency_iso4217",
            ),
            models.CheckConstraint(
                condition=(
                    Q(status="pending", posted_at__isnull=True, failed_at__isnull=True)
                    | Q(status="posted", posted_at__isnull=False)
                    | Q(status="failed", failed_at__isnull=False)
                    | Q(status="reversed", reversed_at__isnull=False)
                ),
                name="ck_payment_ledger_status_timestamp",
            ),
        ]
        indexes = [
            models.Index(fields=["merchant_id", "payment_id"]),
            models.Index(fields=["merchant_id", "status", "created_at"]),
            models.Index(fields=["provider", "provider_reference"]),
        ]

    def __str__(self):
        return f"{self.payment_id} {self.direction} {self.amount_minor} {self.currency}"
```

Audit trail은 ledger row를 덮어쓰는 대신 상태 변경 이력을 별도 테이블에 남깁니다.

```python
class PaymentLedgerAudit(models.Model):
    ledger = models.ForeignKey(
        PaymentLedger,
        on_delete=models.PROTECT,
        related_name="audits",
    )
    from_status = models.CharField(max_length=16, blank=True)
    to_status = models.CharField(max_length=16)
    reason = models.CharField(max_length=120, blank=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )
    snapshot = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["ledger", "created_at"]),
        ]
```

상태 전이는 서비스 레이어에서만 허용합니다.

```python
ALLOWED_TRANSITIONS = {
    "pending": {"posted", "failed"},
    "posted": {"reversed"},
    "failed": set(),
    "reversed": set(),
}
```

트랜잭션 경계는 `idempotency_key` 확인, ledger 생성/조회, 상태 변경, audit 기록까지 하나의 `transaction.atomic()` 안에 둡니다. 외부 PG 호출, 알림, 웹훅 발행은 DB 커밋 이후 `transaction.on_commit()`으로 분리합니다. 동시 요청은 unique constraint가 최종 방어선이고, 같은 `merchant_id + idempotency_key` 재요청은 기존 ledger를 반환해야 합니다.

검증 단계:

```bash
python manage.py makemigrations payments
python manage.py sqlmigrate payments <migration_number>
python manage.py test apps.payments
```

테스트는 최소한 `merchant_id + idempotency_key` 중복 생성 방지, `amount_minor <= 0` 거부, 잘못된 상태 전이 거부, 상태 변경 시 `PaymentLedgerAudit` 생성, 같은 idempotency 재요청 시 기존 ledger 반환을 확인해야 합니다.

---
> **관련 스킬 참조:**
> - 결제 상태 전이/API 설계 → **implementation-django-ninja** 스킬