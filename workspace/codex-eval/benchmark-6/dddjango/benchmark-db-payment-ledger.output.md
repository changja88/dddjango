Fixture 확인: `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, `/private/tmp/dddjango-codex-eval`에서도 fixture 파일이 발견되지 않았습니다. 따라서 기존 파일에 맞춘 패치가 아니라 새 `payments` 앱 기준의 unified diff 제안입니다.

**[주요 내용]**

```diff
diff --git a/apps/payments/models.py b/apps/payments/models.py
new file mode 100644
--- /dev/null
+++ b/apps/payments/models.py
@@
+from decimal import Decimal
+
+from django.conf import settings
+from django.core.validators import RegexValidator
+from django.db import models
+
+
+class PaymentLedgerEntry(models.Model):
+    class Status(models.TextChoices):
+        PENDING = "pending", "Pending"
+        AUTHORIZED = "authorized", "Authorized"
+        CAPTURED = "captured", "Captured"
+        FAILED = "failed", "Failed"
+        CANCELLED = "cancelled", "Cancelled"
+        REFUNDED = "refunded", "Refunded"
+
+    idempotency_key = models.CharField(max_length=128)
+    external_payment_id = models.CharField(max_length=128, blank=True)
+    amount = models.DecimalField(max_digits=19, decimal_places=4)
+    currency = models.CharField(
+        max_length=3,
+        validators=[RegexValidator(r"^[A-Z]{3}$")],
+    )
+    status = models.CharField(
+        max_length=20,
+        choices=Status,
+        default=Status.PENDING,
+    )
+    failure_code = models.CharField(max_length=64, blank=True)
+    failure_message = models.TextField(blank=True)
+    metadata = models.JSONField(default=dict, blank=True)
+    created_by = models.ForeignKey(
+        settings.AUTH_USER_MODEL,
+        null=True,
+        blank=True,
+        on_delete=models.SET_NULL,
+        related_name="created_payment_ledger_entries",
+    )
+    created_at = models.DateTimeField(auto_now_add=True)
+    updated_at = models.DateTimeField(auto_now=True)
+
+    class Meta:
+        ordering = ["-created_at", "-id"]
+        indexes = [
+            models.Index(fields=["status", "created_at"], name="pay_led_status_created_idx"),
+            models.Index(fields=["external_payment_id"], name="pay_led_external_id_idx"),
+        ]
+        constraints = [
+            models.UniqueConstraint(
+                fields=["idempotency_key"],
+                name="pay_led_idempotency_key_uniq",
+            ),
+            models.CheckConstraint(
+                check=models.Q(amount__gt=Decimal("0")),
+                name="pay_led_amount_positive",
+            ),
+        ]
+
+    def __str__(self):
+        return f"{self.currency} {self.amount} {self.status}"
+
+
+class PaymentLedgerAudit(models.Model):
+    ledger_entry = models.ForeignKey(
+        PaymentLedgerEntry,
+        on_delete=models.CASCADE,
+        related_name="audits",
+    )
+    from_status = models.CharField(max_length=20, blank=True)
+    to_status = models.CharField(max_length=20)
+    reason = models.CharField(max_length=255, blank=True)
+    actor = models.ForeignKey(
+        settings.AUTH_USER_MODEL,
+        null=True,
+        blank=True,
+        on_delete=models.SET_NULL,
+        related_name="payment_ledger_audits",
+    )
+    created_at = models.DateTimeField(auto_now_add=True)
+
+    class Meta:
+        ordering = ["created_at", "id"]
+        indexes = [
+            models.Index(fields=["ledger_entry", "created_at"], name="pay_audit_entry_created_idx"),
+        ]
diff --git a/apps/payments/services.py b/apps/payments/services.py
new file mode 100644
--- /dev/null
+++ b/apps/payments/services.py
@@
+from django.core.exceptions import ValidationError
+from django.db import IntegrityError, transaction
+
+from .models import PaymentLedgerAudit, PaymentLedgerEntry
+
+
+ALLOWED_TRANSITIONS = {
+    PaymentLedgerEntry.Status.PENDING: {
+        PaymentLedgerEntry.Status.AUTHORIZED,
+        PaymentLedgerEntry.Status.CAPTURED,
+        PaymentLedgerEntry.Status.FAILED,
+        PaymentLedgerEntry.Status.CANCELLED,
+    },
+    PaymentLedgerEntry.Status.AUTHORIZED: {
+        PaymentLedgerEntry.Status.CAPTURED,
+        PaymentLedgerEntry.Status.CANCELLED,
+        PaymentLedgerEntry.Status.FAILED,
+    },
+    PaymentLedgerEntry.Status.CAPTURED: {
+        PaymentLedgerEntry.Status.REFUNDED,
+    },
+}
+
+
+def payment_ledger_create(*, idempotency_key, amount, currency, actor=None, metadata=None):
+    try:
+        with transaction.atomic():
+            entry = PaymentLedgerEntry.objects.create(
+                idempotency_key=idempotency_key,
+                amount=amount,
+                currency=currency,
+                created_by=actor,
+                metadata=metadata or {},
+            )
+            PaymentLedgerAudit.objects.create(
+                ledger_entry=entry,
+                from_status="",
+                to_status=entry.status,
+                actor=actor,
+                reason="created",
+            )
+            return entry, True
+    except IntegrityError:
+        return PaymentLedgerEntry.objects.get(idempotency_key=idempotency_key), False
+
+
+def payment_ledger_transition(*, entry_id, to_status, actor=None, reason=""):
+    with transaction.atomic():
+        entry = PaymentLedgerEntry.objects.select_for_update().get(pk=entry_id)
+        allowed = ALLOWED_TRANSITIONS.get(entry.status, set())
+        if to_status not in allowed:
+            raise ValidationError("허용되지 않는 결제 ledger 상태 전이입니다.")
+
+        from_status = entry.status
+        entry.status = to_status
+        entry.save(update_fields=["status", "updated_at"])
+        PaymentLedgerAudit.objects.create(
+            ledger_entry=entry,
+            from_status=from_status,
+            to_status=to_status,
+            actor=actor,
+            reason=reason,
+        )
+        return entry
```

금액은 `DecimalField(max_digits=19, decimal_places=4)`로 명시하고 `FloatField`를 피합니다. 통화는 ISO 4217 기준 `CHAR(3)` 성격의 `currency` 컬럼으로 분리합니다. 상태는 Boolean 조합이 아니라 `TextChoices` 단일 컬럼으로 둡니다.

`idempotency_key`는 DB unique constraint로 최종 방어합니다. 생성 서비스는 `IntegrityError`를 잡아 같은 키의 기존 ledger를 반환하므로 재시도 요청이 중복 ledger를 만들지 않습니다.

상태 전이는 `payment_ledger_transition()`에서만 수행하고, `select_for_update()`로 같은 ledger row를 잠근 뒤 audit row를 같은 `transaction.atomic()` 안에서 기록합니다. 외부 결제 API 호출은 이 트랜잭션 밖에서 수행하고, DB 반영만 atomic 경계 안에 두는 것이 안전합니다.

검증 단계:

```bash
python manage.py makemigrations payments
python manage.py sqlmigrate payments 0001
python manage.py test apps.payments
```

테스트는 같은 `idempotency_key` 2회 생성 시 row가 1개인지, 허용되지 않은 상태 전이가 `ValidationError`인지, 상태 변경마다 `PaymentLedgerAudit`이 생성되는지를 확인하면 됩니다.

---
> **관련 스킬 참조:**
> - 결제 API 엔드포인트 설계 → **implementation-django-ninja** 스킬