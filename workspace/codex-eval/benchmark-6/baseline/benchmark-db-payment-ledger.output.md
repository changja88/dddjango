지정된 fixture path `/Users/hyun/Desktop/dddjango/none`은 존재하지 않고, `/private/tmp/dddjango-codex-eval`도 비어 있어서 기존 프로젝트 스타일에 맞춘 위치 지정은 할 수 없었습니다. 아래는 `payments` 앱이 있다는 가정의 적용용 unified diff입니다.

```diff
diff --git a/payments/models.py b/payments/models.py
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/payments/models.py
@@ -0,0 +1,119 @@
+import uuid
+from decimal import Decimal
+
+from django.conf import settings
+from django.core.validators import MinValueValidator, RegexValidator
+from django.db import models
+
+
+currency_validator = RegexValidator(
+    regex=r"^[A-Z]{3}$",
+    message="Currency must be an ISO-4217 alpha-3 code.",
+)
+
+
+class PaymentLedgerEntry(models.Model):
+    class EntryType(models.TextChoices):
+        AUTHORIZATION = "authorization", "Authorization"
+        CAPTURE = "capture", "Capture"
+        REFUND = "refund", "Refund"
+        CHARGEBACK = "chargeback", "Chargeback"
+        ADJUSTMENT = "adjustment", "Adjustment"
+
+    class Direction(models.TextChoices):
+        DEBIT = "debit", "Debit"
+        CREDIT = "credit", "Credit"
+
+    class Status(models.TextChoices):
+        PENDING = "pending", "Pending"
+        POSTED = "posted", "Posted"
+        FAILED = "failed", "Failed"
+        VOIDED = "voided", "Voided"
+        REVERSED = "reversed", "Reversed"
+
+    ledger_id = models.UUIDField(
+        default=uuid.uuid4,
+        editable=False,
+        unique=True,
+        db_index=True,
+    )
+    entry_type = models.CharField(max_length=32, choices=EntryType.choices)
+    direction = models.CharField(max_length=16, choices=Direction.choices)
+
+    amount = models.DecimalField(
+        max_digits=19,
+        decimal_places=4,
+        validators=[MinValueValidator(Decimal("0.0001"))],
+        help_text="Minor-unit compatible decimal amount. Always positive; use direction for debit/credit.",
+    )
+    currency = models.CharField(
+        max_length=3,
+        validators=[currency_validator],
+        help_text="ISO-4217 alpha-3 currency code.",
+    )
+
+    status = models.CharField(
+        max_length=16,
+        choices=Status.choices,
+        default=Status.PENDING,
+        db_index=True,
+    )
+    posted_at = models.DateTimeField(null=True, blank=True)
+
+    idempotency_key = models.CharField(
+        max_length=128,
+        unique=True,
+        db_index=True,
+        help_text="Client or upstream supplied key preventing duplicate ledger entries.",
+    )
+    idempotency_hash = models.CharField(
+        max_length=64,
+        blank=True,
+        help_text="Optional SHA-256 hash of the normalized request payload.",
+    )
+
+    provider = models.CharField(max_length=64, blank=True)
+    provider_reference = models.CharField(max_length=128, blank=True)
+    description = models.CharField(max_length=255, blank=True)
+    metadata = models.JSONField(default=dict, blank=True)
+
+    created_at = models.DateTimeField(auto_now_add=True)
+    updated_at = models.DateTimeField(auto_now=True)
+    created_by = models.ForeignKey(
+        settings.AUTH_USER_MODEL,
+        null=True,
+        blank=True,
+        on_delete=models.PROTECT,
+        related_name="created_payment_ledger_entries",
+    )
+    updated_by = models.ForeignKey(
+        settings.AUTH_USER_MODEL,
+        null=True,
+        blank=True,
+        on_delete=models.PROTECT,
+        related_name="updated_payment_ledger_entries",
+    )
+
+    class Meta:
+        db_table = "payment_ledger_entry"
+        indexes = [
+            models.Index(fields=["currency", "status"]),
+            models.Index(fields=["provider", "provider_reference"]),
+            models.Index(fields=["created_at"]),
+        ]
+        constraints = [
+            models.CheckConstraint(
+                check=models.Q(amount__gt=Decimal("0")),
+                name="payment_ledger_amount_positive",
+            ),
+            models.UniqueConstraint(
+                fields=["provider", "provider_reference"],
+                condition=~models.Q(provider="") & ~models.Q(provider_reference=""),
+                name="payment_ledger_unique_provider_reference",
+            ),
+        ]
+
+    def __str__(self):
+        return f"{self.ledger_id} {self.direction} {self.amount} {self.currency}"
+
+
+class PaymentLedgerAudit(models.Model):
+    ledger_entry = models.ForeignKey(
+        PaymentLedgerEntry,
+        on_delete=models.PROTECT,
+        related_name="audits",
+    )
+    previous_status = models.CharField(
+        max_length=16,
+        choices=PaymentLedgerEntry.Status.choices,
+        blank=True,
+    )
+    new_status = models.CharField(
+        max_length=16,
+        choices=PaymentLedgerEntry.Status.choices,
+    )
+    reason = models.CharField(max_length=255, blank=True)
+    snapshot = models.JSONField(default=dict, blank=True)
+    created_at = models.DateTimeField(auto_now_add=True)
+    created_by = models.ForeignKey(
+        settings.AUTH_USER_MODEL,
+        null=True,
+        blank=True,
+        on_delete=models.PROTECT,
+        related_name="payment_ledger_audits",
+    )
+
+    class Meta:
+        db_table = "payment_ledger_audit"
+        indexes = [
+            models.Index(fields=["ledger_entry", "created_at"]),
+        ]
```

핵심 의도는 `amount`를 항상 양수로 두고 `direction`으로 차변/대변을 표현하는 것입니다. 통화는 ISO-4217 3자리 코드로 제한했고, `idempotency_key`는 전역 unique로 중복 요청을 막습니다. 상태 변경 이력은 별도 `PaymentLedgerAudit`에 쌓아서 원장 row 자체의 현재 상태와 감사 추적을 분리했습니다.