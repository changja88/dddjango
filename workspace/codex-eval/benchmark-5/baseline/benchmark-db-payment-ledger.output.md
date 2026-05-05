fixture를 읽으려고 했지만 `/Users/hyun/Desktop/dddjango/none` 경로가 존재하지 않고, 현재 작업 디렉터리도 비어 있습니다. 그래서 실제 프로젝트 파일에 맞춘 패치는 만들 수 없고, Django 앱에 적용할 수 있는 기준 모델 diff로 제안합니다.

```diff
diff --git a/payments/models.py b/payments/models.py
new file mode 100644
--- /dev/null
+++ b/payments/models.py
@@ -0,0 +1,104 @@
+import uuid
+
+from django.conf import settings
+from django.core.validators import MinValueValidator, RegexValidator
+from django.db import models
+
+
+currency_validator = RegexValidator(
+    regex=r"^[A-Z]{3}$",
+    message="Currency must be an ISO 4217 alpha-3 code.",
+)
+
+
+class PaymentLedgerEntry(models.Model):
+    class Direction(models.TextChoices):
+        DEBIT = "DEBIT", "Debit"
+        CREDIT = "CREDIT", "Credit"
+
+    class Status(models.TextChoices):
+        PENDING = "PENDING", "Pending"
+        POSTED = "POSTED", "Posted"
+        FAILED = "FAILED", "Failed"
+        VOIDED = "VOIDED", "Voided"
+        REVERSED = "REVERSED", "Reversed"
+
+    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
+
+    # Domain references
+    account_id = models.UUIDField(db_index=True)
+    payment_id = models.UUIDField(null=True, blank=True, db_index=True)
+    external_reference = models.CharField(max_length=128, blank=True)
+
+    # Money is stored as minor units, e.g. USD cents or KRW won.
+    amount_minor = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
+    currency = models.CharField(
+        max_length=3,
+        validators=[currency_validator],
+        help_text="ISO 4217 currency code.",
+    )
+    direction = models.CharField(max_length=6, choices=Direction.choices)
+
+    status = models.CharField(
+        max_length=16,
+        choices=Status.choices,
+        default=Status.PENDING,
+        db_index=True,
+    )
+
+    # Idempotency is scoped so different operations may safely reuse keys.
+    idempotency_scope = models.CharField(max_length=64)
+    idempotency_key = models.CharField(max_length=255)
+
+    metadata = models.JSONField(default=dict, blank=True)
+
+    created_at = models.DateTimeField(auto_now_add=True)
+    updated_at = models.DateTimeField(auto_now=True)
+    created_by = models.ForeignKey(
+        settings.AUTH_USER_MODEL,
+        null=True,
+        blank=True,
+        on_delete=models.SET_NULL,
+        related_name="+",
+    )
+
+    class Meta:
+        db_table = "payment_ledger_entries"
+        indexes = [
+            models.Index(fields=["account_id", "created_at"]),
+            models.Index(fields=["payment_id", "status"]),
+            models.Index(fields=["currency", "status"]),
+        ]
+        constraints = [
+            models.UniqueConstraint(
+                fields=["idempotency_scope", "idempotency_key"],
+                name="uniq_payment_ledger_idempotency",
+            ),
+            models.CheckConstraint(
+                check=models.Q(amount_minor__gt=0),
+                name="payment_ledger_amount_minor_positive",
+            ),
+        ]
+
+    def __str__(self):
+        return f"{self.direction} {self.amount_minor} {self.currency} ({self.status})"
+
+
+class PaymentLedgerAuditEvent(models.Model):
+    class EventType(models.TextChoices):
+        CREATED = "CREATED", "Created"
+        STATUS_CHANGED = "STATUS_CHANGED", "Status changed"
+        METADATA_UPDATED = "METADATA_UPDATED", "Metadata updated"
+
+    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
+    ledger_entry = models.ForeignKey(
+        PaymentLedgerEntry,
+        on_delete=models.CASCADE,
+        related_name="audit_events",
+    )
+    event_type = models.CharField(max_length=32, choices=EventType.choices)
+    previous_status = models.CharField(
+        max_length=16,
+        choices=PaymentLedgerEntry.Status.choices,
+        blank=True,
+    )
+    new_status = models.CharField(
+        max_length=16,
+        choices=PaymentLedgerEntry.Status.choices,
+        blank=True,
+    )
+    payload = models.JSONField(default=dict, blank=True)
+    actor = models.ForeignKey(
+        settings.AUTH_USER_MODEL,
+        null=True,
+        blank=True,
+        on_delete=models.SET_NULL,
+        related_name="+",
+    )
+    created_at = models.DateTimeField(auto_now_add=True)
+
+    class Meta:
+        db_table = "payment_ledger_audit_events"
+        indexes = [
+            models.Index(fields=["ledger_entry", "created_at"]),
+            models.Index(fields=["event_type", "created_at"]),
+        ]
```

핵심 설계는 금액을 `DecimalField`가 아니라 `amount_minor` 정수로 저장하는 방식입니다. 결제 ledger에서는 반올림, 통화별 소수점 차이, DB decimal 설정 차이로 인한 오류를 줄이기 위해 minor unit 정수가 더 안전합니다. 음수 금액은 허용하지 않고 `direction`으로 입출금을 표현합니다.

상태 변경 이력은 ledger row 자체에 덮어쓰지 않고 `PaymentLedgerAuditEvent`에 append-only로 남기는 구조가 적합합니다. `idempotency_scope + idempotency_key` unique 제약으로 중복 결제/중복 ledger 기록도 DB 레벨에서 막습니다.