Django 모델 기준이면 결제 Ledger는 **append-only 성격의 원장 엔트리**로 두고, 금액은 `FloatField`가 아니라 `DecimalField`를 사용합니다. 중복 결제 방지를 위해 `idempotency_key`는 결제 요청 범위 안에서 유니크하게 잡고, 상태 변경 이력은 별도 audit 테이블로 분리하는 쪽이 운영상 안전합니다.

```python
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q


@dataclass(frozen=True, slots=True)
class Money:
    """Value Object: 금액은 음수가 아니며 통화와 함께만 의미가 있다."""
    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ValueError("금액은 0보다 커야 합니다.")
        if len(self.currency) != 3:
            raise ValueError("통화는 ISO-4217 3자리 코드여야 합니다.")


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PaymentLedger(TimeStampedModel):
    """
    Aggregate Root: 결제 원장 엔트리.

    불변식:
    - amount는 0보다 커야 한다.
    - currency는 ISO-4217 3자리 대문자 코드여야 한다.
    - 같은 merchant_id + idempotency_key 요청은 한 번만 기록된다.
    - terminal 상태(succeeded, failed, canceled, refunded)는 되돌리지 않는다.
    - 금액/통화/방향/외부 참조는 원장 성격상 생성 후 수정하지 않는다.
    """

    class Direction(models.TextChoices):
        DEBIT = "debit", "Debit"
        CREDIT = "credit", "Credit"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        AUTHORIZED = "authorized", "Authorized"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        CANCELED = "canceled", "Canceled"
        REFUNDED = "refunded", "Refunded"

    class EntryType(models.TextChoices):
        PAYMENT = "payment", "Payment"
        REFUND = "refund", "Refund"
        ADJUSTMENT = "adjustment", "Adjustment"
        CHARGEBACK = "chargeback", "Chargeback"

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    merchant_id = models.UUIDField(db_index=True)
    customer_id = models.UUIDField(null=True, blank=True, db_index=True)

    entry_type = models.CharField(max_length=20, choices=EntryType)
    direction = models.CharField(max_length=10, choices=Direction)
    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.PENDING,
        db_index=True,
    )

    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(
        max_length=3,
        validators=[RegexValidator(r"^[A-Z]{3}$")],
    )

    idempotency_key = models.CharField(max_length=255)
    payment_reference = models.CharField(max_length=255, blank=True)
    external_provider = models.CharField(max_length=50, blank=True)
    external_reference = models.CharField(max_length=255, blank=True)

    request_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="동일 idempotency_key에 다른 payload가 들어오는 것을 탐지하기 위한 SHA-256 해시",
    )

    metadata = models.JSONField(default=dict, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="created_payment_ledger_entries",
    )
    status_changed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Payment ledger entry"
        verbose_name_plural = "Payment ledger entries"
        constraints = [
            models.CheckConstraint(
                check=Q(amount__gt=0),
                name="payment_ledger_amount_gt_0",
            ),
            models.CheckConstraint(
                check=Q(currency__regex=r"^[A-Z]{3}$"),
                name="payment_ledger_currency_iso_4217",
            ),
            models.UniqueConstraint(
                fields=["merchant_id", "idempotency_key"],
                name="uq_payment_ledger_merchant_idempotency",
            ),
            models.UniqueConstraint(
                fields=["external_provider", "external_reference"],
                condition=~Q(external_provider="") & ~Q(external_reference=""),
                name="uq_payment_ledger_external_reference",
            ),
        ]
        indexes = [
            models.Index(
                fields=["merchant_id", "status", "created_at"],
                name="idx_pay_ledg_merchant_status_created",
            ),
            models.Index(
                fields=["merchant_id", "payment_reference"],
                name="idx_pay_ledg_merchant_payment_ref",
            ),
            models.Index(
                fields=["customer_id", "created_at"],
                name="idx_pay_ledg_customer_created",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.entry_type}:{self.amount} {self.currency} ({self.status})"

    def clean(self) -> None:
        if self.amount <= 0:
            raise ValidationError({"amount": "금액은 0보다 커야 합니다."})

        terminal_statuses = {
            self.Status.SUCCEEDED,
            self.Status.FAILED,
            self.Status.CANCELED,
            self.Status.REFUNDED,
        }

        if self.pk:
            previous = type(self).objects.only(
                "amount",
                "currency",
                "direction",
                "entry_type",
                "external_provider",
                "external_reference",
                "status",
            ).get(pk=self.pk)

            immutable_fields = [
                "amount",
                "currency",
                "direction",
                "entry_type",
                "external_provider",
                "external_reference",
            ]
            changed = [
                field
                for field in immutable_fields
                if getattr(previous, field) != getattr(self, field)
            ]
            if changed:
                raise ValidationError(
                    {field: "원장 엔트리의 핵심 필드는 수정할 수 없습니다." for field in changed}
                )

            if previous.status in terminal_statuses and previous.status != self.status:
                raise ValidationError({"status": "종료 상태는 변경할 수 없습니다."})
```

Audit trail은 원장 테이블 안에 JSON으로 뭉개기보다 별도 테이블로 두는 편이 낫습니다. 상태 변경, 운영자 보정, 외부 PG 콜백 반영 같은 행위를 모두 남길 수 있습니다.

```python
class PaymentLedgerAudit(models.Model):
    class Action(models.TextChoices):
        CREATED = "created", "Created"
        STATUS_CHANGED = "status_changed", "Status changed"
        PROVIDER_SYNCED = "provider_synced", "Provider synced"
        METADATA_UPDATED = "metadata_updated", "Metadata updated"

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    ledger = models.ForeignKey(
        PaymentLedger,
        on_delete=models.PROTECT,
        related_name="audit_events",
    )
    action = models.CharField(max_length=30, choices=Action)

    previous_status = models.CharField(
        max_length=20,
        choices=PaymentLedger.Status,
        blank=True,
    )
    new_status = models.CharField(
        max_length=20,
        choices=PaymentLedger.Status,
        blank=True,
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="payment_ledger_audit_events",
    )
    request_id = models.CharField(max_length=255, blank=True)
    reason = models.TextField(blank=True)
    snapshot = models.JSONField(default=dict, blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-occurred_at"]
        verbose_name = "Payment ledger audit event"
        verbose_name_plural = "Payment ledger audit events"
        indexes = [
            models.Index(fields=["ledger", "occurred_at"], name="idx_pay_audit_ledger_time"),
            models.Index(fields=["request_id"], name="idx_pay_audit_request_id"),
        ]

    def __str__(self) -> str:
        return f"{self.ledger_id}:{self.action}"
```

도메인 용어는 이렇게 고정하는 것을 권합니다.

| 용어 | 의미 |
|---|---|
| `PaymentLedger` | 결제 원장의 단일 엔트리, Aggregate Root |
| `Money` | `amount + currency` 값 객체 |
| `idempotency_key` | 동일 POST 재시도 중복 처리를 위한 클라이언트 키 |
| `payment_reference` | 내부 결제 흐름의 상관관계 키 |
| `external_reference` | PG사 거래 식별자 |
| `PaymentLedgerAudit` | 원장 변경 감사 이벤트 |

금지 동의어는 `price`, `cost`, `fee`를 원장 금액 의미로 쓰지 않는 것입니다. 원장에서는 `amount`로 통일하고, 부호 대신 `direction`으로 차변/대변 성격을 표현하는 편이 쿼리와 검증이 명확합니다.

Repository와 Application Service 경계는 최소한 이렇게 분리하면 됩니다.

```python
from abc import ABC, abstractmethod


class PaymentLedgerRepository(ABC):
    @abstractmethod
    def find_by_idempotency_key(
        self,
        *,
        merchant_id: str,
        idempotency_key: str,
    ) -> PaymentLedger | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, ledger: PaymentLedger) -> PaymentLedger:
        raise NotImplementedError


class PaymentApplicationService:
    def __init__(self, ledger_repository: PaymentLedgerRepository) -> None:
        self.ledger_repository = ledger_repository

    def record_payment(self, ledger: PaymentLedger) -> PaymentLedger:
        existing = self.ledger_repository.find_by_idempotency_key(
            merchant_id=str(ledger.merchant_id),
            idempotency_key=ledger.idempotency_key,
        )
        if existing is not None:
            return existing

        return self.ledger_repository.save(ledger)
```

마이그레이션 후에는 PostgreSQL 기준으로 `merchant_id + idempotency_key` 유니크 제약이 핵심입니다. 동일 키 동시 요청은 `transaction.atomic()` 안에서 생성하고, `IntegrityError` 발생 시 기존 행을 다시 읽어 같은 응답을 반환하는 방식으로 처리하는 것이 안전합니다.

---
> **관련 스킬 참조:**
> - Django 모델/마이그레이션 구현 → **implementation-django** 스킬
> - 인덱스/정규화/트랜잭션 검토 → **architecture-db** 스킬
> - 결제 도메인 경계와 애그리거트 설계 → **architecture-ddd** 스킬