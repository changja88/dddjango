**[주요 내용]**

아래처럼 `ledger`는 결제 요청의 현재 상태를 가진 원장 행, `ledger_audit`는 상태 변경 이력으로 분리하는 설계를 권장합니다. 금액은 부동소수점이 아닌 `DecimalField`, 통화는 ISO-4217 `CHAR(3)` 컬럼으로 명시합니다.

```python
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import Q


class PaymentLedger(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        POSTED = "posted", "Posted"
        FAILED = "failed", "Failed"
        VOIDED = "voided", "Voided"

    id = models.BigAutoField(primary_key=True)
    payment_id = models.UUIDField(db_index=True)
    idempotency_key = models.CharField(max_length=128, unique=True)
    amount = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        validators=[MinValueValidator(Decimal("0.0001"))],
    )
    currency = models.CharField(
        max_length=3,
        validators=[RegexValidator(r"^[A-Z]{3}$")],
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    provider_reference = models.CharField(max_length=128, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payment_ledger"
        ordering = ["-id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="payment_ledger_amount_gt_0",
            ),
        ]
        indexes = [
            models.Index(fields=["payment_id", "status"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"{self.payment_id} {self.amount} {self.currency} {self.status}"


class PaymentLedgerAudit(models.Model):
    ledger = models.ForeignKey(
        PaymentLedger,
        on_delete=models.PROTECT,
        related_name="audits",
    )
    from_status = models.CharField(max_length=16, blank=True)
    to_status = models.CharField(max_length=16)
    reason = models.CharField(max_length=255, blank=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )
    snapshot = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payment_ledger_audit"
        ordering = ["-id"]
        indexes = [
            models.Index(fields=["ledger", "created_at"]),
        ]
```

상태 전이는 서비스 함수에서만 허용하는 편이 안전합니다.

```python
ALLOWED_TRANSITIONS = {
    "pending": {"posted", "failed"},
    "posted": {"voided"},
    "failed": set(),
    "voided": set(),
}
```

트랜잭션 경계는 “원장 행 생성 또는 상태 변경 + 감사 이력 기록”을 하나의 `transaction.atomic()` 안에 둡니다. 기존 행을 변경할 때는 `select_for_update()`로 잠그고, 외부 결제사 호출이나 알림은 커밋 이후 `transaction.on_commit()`으로 분리합니다. 동일 `idempotency_key` 재요청은 unique constraint로 중복 삽입을 막고, `IntegrityError` 또는 `get(idempotency_key=...)` 경로에서 기존 결과를 반환하게 설계합니다.

검증 단계:

```bash
python manage.py makemigrations
python manage.py sqlmigrate payments 0001
python manage.py test apps.payments
```

확인할 항목은 `amount`가 `numeric(20, 4)`로 생성되는지, `currency`가 길이 3 컬럼인지, `idempotency_key` unique index가 있는지, 중복 idempotency 요청 테스트와 `pending -> posted`, `posted -> voided`, `failed -> posted` 금지 테스트가 통과하는지입니다.

---
> **관련 스킬 참조:**
> - 결제 API/서비스 구현 → **implementation-django** 스킬