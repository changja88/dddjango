**[주요 내용]**

fixture path `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, 현재 작업 디렉터리에도 읽을 프로젝트 파일이 없어 새 앱 기준 diff로 제안합니다.

```diff
diff --git a/apps/payments/models.py b/apps/payments/models.py
new file mode 100644
--- /dev/null
+++ b/apps/payments/models.py
@@
+from django.conf import settings
+from django.core.validators import MinValueValidator
+from django.db import models
+from django.db.models import Q
+
+
+class PaymentLedger(models.Model):
+    class EntryType(models.TextChoices):
+        DEBIT = "debit", "Debit"
+        CREDIT = "credit", "Credit"
+
+    class Status(models.TextChoices):
+        PENDING = "pending", "Pending"
+        POSTED = "posted", "Posted"
+        FAILED = "failed", "Failed"
+        REVERSED = "reversed", "Reversed"
+
+    idempotency_key = models.CharField(max_length=128, unique=True)
+    external_reference = models.CharField(max_length=128, blank=True)
+
+    account_id = models.UUIDField(db_index=True)
+    entry_type = models.CharField(max_length=10, choices=EntryType.choices)
+    amount_minor_units = models.BigIntegerField(validators=[MinValueValidator(1)])
+    currency = models.CharField(max_length=3)
+
+    status = models.CharField(
+        max_length=16,
+        choices=Status.choices,
+        default=Status.PENDING,
+    )
+    posted_at = models.DateTimeField(null=True, blank=True)
+
+    metadata = models.JSONField(default=dict, blank=True)
+    created_by = models.ForeignKey(
+        settings.AUTH_USER_MODEL,
+        null=True,
+        blank=True,
+        on_delete=models.PROTECT,
+        related_name="created_payment_ledgers",
+    )
+    updated_by = models.ForeignKey(
+        settings.AUTH_USER_MODEL,
+        null=True,
+        blank=True,
+        on_delete=models.PROTECT,
+        related_name="updated_payment_ledgers",
+    )
+    created_at = models.DateTimeField(auto_now_add=True)
+    updated_at = models.DateTimeField(auto_now=True)
+
+    class Meta:
+        ordering = ["-created_at", "-id"]
+        indexes = [
+            models.Index(fields=["account_id", "-created_at"]),
+            models.Index(fields=["status", "-created_at"]),
+            models.Index(fields=["external_reference"]),
+        ]
+        constraints = [
+            models.CheckConstraint(
+                condition=Q(amount_minor_units__gt=0),
+                name="payment_ledger_amount_minor_units_positive",
+            ),
+        ]
+
+    def __str__(self):
+        return (
+            f"{self.entry_type} {self.amount_minor_units} "
+            f"{self.currency} {self.status}"
+        )
+
+
+class PaymentLedgerAudit(models.Model):
+    ledger = models.ForeignKey(
+        PaymentLedger,
+        on_delete=models.CASCADE,
+        related_name="audit_events",
+    )
+    from_status = models.CharField(
+        max_length=16,
+        choices=PaymentLedger.Status.choices,
+        blank=True,
+    )
+    to_status = models.CharField(max_length=16, choices=PaymentLedger.Status.choices)
+    reason = models.CharField(max_length=255, blank=True)
+    actor = models.ForeignKey(
+        settings.AUTH_USER_MODEL,
+        null=True,
+        blank=True,
+        on_delete=models.PROTECT,
+        related_name="payment_ledger_audit_events",
+    )
+    created_at = models.DateTimeField(auto_now_add=True)
+
+    class Meta:
+        ordering = ["-created_at", "-id"]
+        indexes = [
+            models.Index(fields=["ledger", "-created_at"]),
+        ]
+
+    def __str__(self):
+        return f"{self.ledger_id}: {self.from_status} -> {self.to_status}"
diff --git a/apps/payments/services.py b/apps/payments/services.py
new file mode 100644
--- /dev/null
+++ b/apps/payments/services.py
@@
+from django.db import IntegrityError, transaction
+from django.utils import timezone
+
+from .models import PaymentLedger, PaymentLedgerAudit
+
+
+ALLOWED_STATUS_TRANSITIONS = {
+    PaymentLedger.Status.PENDING: {
+        PaymentLedger.Status.POSTED,
+        PaymentLedger.Status.FAILED,
+    },
+    PaymentLedger.Status.POSTED: {PaymentLedger.Status.REVERSED},
+    PaymentLedger.Status.FAILED: set(),
+    PaymentLedger.Status.REVERSED: set(),
+}
+
+
+@transaction.atomic
+def payment_ledger_create_once(
+    *,
+    idempotency_key,
+    account_id,
+    entry_type,
+    amount_minor_units,
+    currency,
+    actor=None,
+    external_reference="",
+    metadata=None,
+):
+    try:
+        ledger = PaymentLedger.objects.create(
+            idempotency_key=idempotency_key,
+            account_id=account_id,
+            entry_type=entry_type,
+            amount_minor_units=amount_minor_units,
+            currency=currency.upper(),
+            external_reference=external_reference,
+            metadata=metadata or {},
+            created_by=actor,
+            updated_by=actor,
+        )
+    except IntegrityError:
+        ledger = PaymentLedger.objects.get(idempotency_key=idempotency_key)
+        return ledger, False
+
+    PaymentLedgerAudit.objects.create(
+        ledger=ledger,
+        from_status="",
+        to_status=ledger.status,
+        actor=actor,
+        reason="created",
+    )
+    return ledger, True
+
+
+@transaction.atomic
+def payment_ledger_transition(*, ledger_id, to_status, actor=None, reason=""):
+    ledger = PaymentLedger.objects.select_for_update().get(id=ledger_id)
+    allowed = ALLOWED_STATUS_TRANSITIONS[ledger.status]
+
+    if to_status not in allowed:
+        raise ValueError(f"invalid transition: {ledger.status} -> {to_status}")
+
+    from_status = ledger.status
+    ledger.status = to_status
+    ledger.updated_by = actor
+    if to_status == PaymentLedger.Status.POSTED:
+        ledger.posted_at = timezone.now()
+    ledger.save(update_fields=["status", "updated_by", "posted_at", "updated_at"])
+
+    PaymentLedgerAudit.objects.create(
+        ledger=ledger,
+        from_status=from_status,
+        to_status=to_status,
+        actor=actor,
+        reason=reason,
+    )
+    return ledger
```

금액은 `DecimalField` 대신 `amount_minor_units = BigIntegerField`로 저장합니다. 결제 원장은 정산/중복 처리/합계 계산이 중요하므로 부동소수점이나 표시용 decimal보다 최소 통화 단위 정수가 안전합니다. 통화는 `currency = CharField(max_length=3)`로 ISO-4217 코드 기준을 명시합니다.

상태 전이는 `pending -> posted|failed`, `posted -> reversed`만 허용합니다. `failed`, `reversed`는 terminal 상태입니다. 전이 함수는 `transaction.atomic()` 안에서 `select_for_update()`로 행 잠금을 잡고, ledger 상태 변경과 audit insert를 같은 트랜잭션 경계에 둡니다. 외부 PG/API 호출은 이 트랜잭션 밖에서 수행하고, DB 반영만 이 서비스에 넣는 구조가 맞습니다.

idempotency는 `idempotency_key unique=True`가 핵심입니다. 동시 요청이 들어와도 하나만 생성되고, 충돌 시 기존 ledger를 조회해 `(ledger, False)`를 반환합니다.

검증 절차:

```bash
python manage.py makemigrations payments
python manage.py sqlmigrate payments <migration_number>
python manage.py test apps.payments
```

테스트는 최소한 idempotency 중복 생성 방지, 잘못된 상태 전이 거부, `posted` 전이 시 audit row 생성과 `posted_at` 기록을 확인해야 합니다.

---
> **관련 스킬 참조:**
> - 결제 API 엔드포인트 설계 → **implementation-django-ninja** 스킬