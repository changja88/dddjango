**주요 내용**

아래 설계는 “주문 1건에 결제 시도는 여러 번 가능하지만, 성공 결제는 기본적으로 1건만 허용하고, 환불은 성공 결제에 대해 여러 번 부분 환불 가능”이라는 전제를 둡니다. 분할 결제나 복수 통화 정산이 필요하면 `Payment` 제약을 완화해야 합니다.

대표 워크로드를 먼저 정합니다.

| 워크로드 | 예시 쿼리 | 필요한 인덱스 |
|---|---|---|
| 사용자 주문 목록 | `WHERE user_id = ? ORDER BY created_at DESC` | `(user, -created_at)` |
| 주문 상세 | `WHERE order_number = ?` | `order_number UNIQUE` |
| 상태별 운영 목록 | `WHERE status = ? AND created_at >= ?` | `(status, -created_at)` |
| 결제 재시도/중복 방지 | `WHERE idempotency_key = ?` | unique |
| PG/webhook 매핑 | `WHERE provider, provider_payment_id` | partial unique |
| 주문의 결제 이력 | `WHERE order_id = ? ORDER BY created_at DESC` | `(order, -created_at)` |
| 결제의 환불 이력 | `WHERE payment_id = ? ORDER BY created_at DESC` | `(payment, -created_at)` |
| 환불 중복 방지 | `WHERE idempotency_key = ?` | unique |
| 운영자 환불 큐 | `WHERE status = ? AND requested_at >= ?` | `(status, -requested_at)` |

```python
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(db_index=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Order(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_PAYMENT = "pending_payment", "Pending payment"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"
        PARTIALLY_REFUNDED = "partially_refunded", "Partially refunded"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    order_number = models.CharField(max_length=32, unique=True)
    status = models.CharField(
        max_length=32,
        choices=Status,
        default=Status.DRAFT,
        db_default=Status.DRAFT,
    )
    currency = models.CharField(max_length=3)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["user", "-created_at"],
                name="order_user_created_idx",
            ),
            models.Index(
                fields=["status", "-created_at"],
                name="order_status_created_idx",
            ),
            models.Index(
                fields=["created_at"],
                name="order_created_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(total_amount__gt=Decimal("0.00")),
                name="order_total_amount_positive",
            ),
            models.CheckConstraint(
                condition=Q(currency__regex=r"^[A-Z]{3}$"),
                name="order_currency_iso_4217_like",
            ),
            models.CheckConstraint(
                condition=(
                    Q(status="paid", paid_at__isnull=False)
                    | ~Q(status="paid")
                ),
                name="order_paid_requires_paid_at",
            ),
        ]

    def __str__(self):
        return self.order_number

    def clean(self):
        if self.currency and self.currency != self.currency.upper():
            raise ValidationError({"currency": "Currency must be uppercase."})


class Payment(TimeStampedModel):
    class Status(models.TextChoices):
        READY = "ready", "Ready"
        AUTHORIZED = "authorized", "Authorized"
        CAPTURED = "captured", "Captured"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments",
    )
    status = models.CharField(
        max_length=32,
        choices=Status,
        default=Status.READY,
        db_default=Status.READY,
    )
    provider = models.CharField(max_length=32)
    provider_payment_id = models.CharField(max_length=128, null=True, blank=True)
    idempotency_key = models.CharField(max_length=128, unique=True)
    currency = models.CharField(max_length=3)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    authorized_at = models.DateTimeField(null=True, blank=True)
    captured_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    failure_code = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["order", "-created_at"],
                name="payment_order_created_idx",
            ),
            models.Index(
                fields=["status", "-created_at"],
                name="payment_status_created_idx",
            ),
            models.Index(
                fields=["provider", "provider_payment_id"],
                name="payment_provider_ref_idx",
                condition=Q(provider_payment_id__isnull=False),
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=Decimal("0.00")),
                name="payment_amount_positive",
            ),
            models.CheckConstraint(
                condition=Q(currency__regex=r"^[A-Z]{3}$"),
                name="payment_currency_iso_4217_like",
            ),
            models.UniqueConstraint(
                fields=["order"],
                condition=Q(status__in=["authorized", "captured"]),
                name="payment_one_active_success_per_order",
            ),
            models.UniqueConstraint(
                fields=["provider", "provider_payment_id"],
                condition=Q(provider_payment_id__isnull=False),
                name="payment_provider_payment_unique",
            ),
            models.CheckConstraint(
                condition=(
                    Q(status="captured", captured_at__isnull=False)
                    | ~Q(status="captured")
                ),
                name="payment_captured_requires_captured_at",
            ),
        ]

    def __str__(self):
        return f"{self.provider}:{self.provider_payment_id or self.pk}"

    def clean(self):
        if self.order_id and self.currency != self.order.currency:
            raise ValidationError({"currency": "Payment currency must match order."})
        if self.order_id and self.amount != self.order.total_amount:
            raise ValidationError({"amount": "Payment amount must match order total."})


class Refund(TimeStampedModel):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        PROCESSING = "processing", "Processing"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        related_name="refunds",
    )
    status = models.CharField(
        max_length=32,
        choices=Status,
        default=Status.REQUESTED,
        db_default=Status.REQUESTED,
    )
    provider_refund_id = models.CharField(max_length=128, null=True, blank=True)
    idempotency_key = models.CharField(max_length=128, unique=True)
    currency = models.CharField(max_length=3)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.CharField(max_length=255, blank=True)
    requested_at = models.DateTimeField(default=timezone.now)
    succeeded_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    failure_code = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-requested_at"]
        indexes = [
            models.Index(
                fields=["payment", "-created_at"],
                name="refund_payment_created_idx",
            ),
            models.Index(
                fields=["status", "-requested_at"],
                name="refund_status_requested_idx",
            ),
            models.Index(
                fields=["provider_refund_id"],
                name="refund_provider_ref_idx",
                condition=Q(provider_refund_id__isnull=False),
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=Decimal("0.00")),
                name="refund_amount_positive",
            ),
            models.CheckConstraint(
                condition=Q(currency__regex=r"^[A-Z]{3}$"),
                name="refund_currency_iso_4217_like",
            ),
            models.UniqueConstraint(
                fields=["provider_refund_id"],
                condition=Q(provider_refund_id__isnull=False),
                name="refund_provider_refund_unique",
            ),
            models.CheckConstraint(
                condition=(
                    Q(status="succeeded", succeeded_at__isnull=False)
                    | ~Q(status="succeeded")
                ),
                name="refund_succeeded_requires_succeeded_at",
            ),
        ]

    def __str__(self):
        return f"refund:{self.pk}"
```

핵심 제약은 DB와 애플리케이션 양쪽에 나눠 둡니다.

| 규칙 | 위치 | 이유 |
|---|---|---|
| 금액은 0보다 커야 함 | `CheckConstraint` | 단일 행 불변식이라 DB 제약 가능 |
| 통화 코드는 대문자 3자리 | `clean()` + `CheckConstraint` | 입력 검증과 DB 방어를 모두 둠 |
| 주문당 성공 결제 1건 | partial `UniqueConstraint` | 동시 결제 성공 race 방지 |
| PG 결제 ID 중복 금지 | partial `UniqueConstraint` | webhook 재전송/중복 승인 방지 |
| idempotency key 중복 금지 | `unique=True` | 같은 요청 재시도 시 같은 결과 반환 |
| 환불 총액 <= 결제 금액 | 서비스 트랜잭션 + row lock | 여러 `Refund` 행의 집계라 단순 CHECK로 불가 |
| 결제 통화/금액 = 주문 통화/금액 | `clean()` + 서비스 검증 | cross-table CHECK 불가 |

트랜잭션 전략은 `Read Committed + 명시적 row lock + unique constraint`를 기본으로 잡는 것이 실용적입니다. 결제와 환불은 외부 PG 호출이 끼기 때문에 “DB 트랜잭션 안에서 외부 API를 오래 붙잡는 방식”은 피하고, DB 상태 전이는 짧게 잠그며, 외부 호출 후 webhook/confirm 단계에서 idempotent하게 확정합니다.

```python
from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.utils import timezone


def payment_capture_confirm(
    *,
    order_id: int,
    provider: str,
    provider_payment_id: str,
    idempotency_key: str,
    amount,
    currency: str,
) -> Payment:
    with transaction.atomic():
        order = (
            Order.objects.select_for_update()
            .get(id=order_id)
        )

        existing = Payment.objects.filter(
            idempotency_key=idempotency_key,
        ).first()
        if existing:
            return existing

        if order.status not in {
            Order.Status.PENDING_PAYMENT,
            Order.Status.DRAFT,
        }:
            raise ValidationError("This order cannot be paid.")

        if order.total_amount != amount or order.currency != currency:
            raise ValidationError("Payment amount or currency mismatch.")

        payment = Payment.objects.create(
            order=order,
            status=Payment.Status.CAPTURED,
            provider=provider,
            provider_payment_id=provider_payment_id,
            idempotency_key=idempotency_key,
            amount=amount,
            currency=currency,
            captured_at=timezone.now(),
        )

        order.status = Order.Status.PAID
        order.paid_at = timezone.now()
        order.save(update_fields=["status", "paid_at", "updated_at"])

    transaction.on_commit(lambda: notify_payment_captured(payment.id))
    return payment
```

```python
def refund_request(
    *,
    payment_id: int,
    idempotency_key: str,
    amount,
    reason: str = "",
) -> Refund:
    with transaction.atomic():
        payment = (
            Payment.objects.select_for_update()
            .select_related("order")
            .get(id=payment_id)
        )

        existing = Refund.objects.filter(
            idempotency_key=idempotency_key,
        ).first()
        if existing:
            return existing

        if payment.status != Payment.Status.CAPTURED:
            raise ValidationError("Only captured payments can be refunded.")

        refunded_amount = (
            Refund.objects.filter(
                payment=payment,
                status__in=[
                    Refund.Status.PROCESSING,
                    Refund.Status.SUCCEEDED,
                ],
            ).aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        if refunded_amount + amount > payment.amount:
            raise ValidationError("Refund amount exceeds captured payment amount.")

        refund = Refund.objects.create(
            payment=payment,
            status=Refund.Status.REQUESTED,
            idempotency_key=idempotency_key,
            amount=amount,
            currency=payment.currency,
            reason=reason,
        )

    transaction.on_commit(lambda: request_pg_refund(refund.id))
    return refund
```

Locking 기준은 다음처럼 잡습니다.

| 작업 | Lock 대상 | 이유 |
|---|---|---|
| 결제 확정 | `Order.select_for_update()` | 같은 주문에 성공 결제가 2개 생기는 race 차단 |
| 환불 요청 | `Payment.select_for_update()` | 동시 부분 환불 합계 초과 차단 |
| webhook 처리 | `Payment` 또는 `Refund` row lock | 같은 provider event 재전송을 멱등 처리 |
| 상태 변경 | 상태 소유 row만 lock | 넓은 범위 lock으로 주문 목록 조회까지 막지 않음 |

`select_for_update()`만 믿지 말고 unique constraint를 반드시 같이 둬야 합니다. 애플리케이션 lock은 코드 경로가 새로 생기면 빠질 수 있지만, DB unique constraint는 마지막 방어선입니다.

마이그레이션 검증은 최소한 아래를 확인합니다.

```bash
python manage.py makemigrations --check --dry-run
python manage.py sqlmigrate orders 0001
python manage.py migrate
python manage.py check
```

pytest는 동시성/제약 중심으로 둡니다.

```python
import pytest
from django.db import IntegrityError, transaction


@pytest.mark.django_db
def test_order_allows_only_one_captured_payment(order):
    Payment.objects.create(
        order=order,
        status=Payment.Status.CAPTURED,
        provider="test",
        provider_payment_id="pay_1",
        idempotency_key="idem_1",
        amount=order.total_amount,
        currency=order.currency,
        captured_at=timezone.now(),
    )

    with pytest.raises(IntegrityError):
        Payment.objects.create(
            order=order,
            status=Payment.Status.CAPTURED,
            provider="test",
            provider_payment_id="pay_2",
            idempotency_key="idem_2",
            amount=order.total_amount,
            currency=order.currency,
            captured_at=timezone.now(),
        )


@pytest.mark.django_db
def test_refund_cannot_exceed_payment_amount(captured_payment):
    refund_request(
        payment_id=captured_payment.id,
        idempotency_key="refund_1",
        amount=Decimal("7000.00"),
    )

    with pytest.raises(ValidationError):
        refund_request(
            payment_id=captured_payment.id,
            idempotency_key="refund_2",
            amount=Decimal("4000.00"),
        )


@pytest.mark.django_db
def test_payment_idempotency_returns_existing_payment(order):
    first = payment_capture_confirm(
        order_id=order.id,
        provider="test",
        provider_payment_id="pay_1",
        idempotency_key="idem_1",
        amount=order.total_amount,
        currency=order.currency,
    )

    second = payment_capture_confirm(
        order_id=order.id,
        provider="test",
        provider_payment_id="pay_1",
        idempotency_key="idem_1",
        amount=order.total_amount,
        currency=order.currency,
    )

    assert second.id == first.id
```

API는 얇게 둡니다. Django Ninja 라우터는 요청 스키마 검증과 인증만 맡기고, 결제/환불 상태 전이는 위 서비스 함수로 위임합니다. 응답 스키마는 `fields="__all__"`을 피하고 `id`, `status`, `amount`, `currency`, `created_at`처럼 필요한 필드만 노출하는 편이 안전합니다.

---
> **관련 스킬 참조:**
> - Django Ninja API 구현 → **implementation-django-ninja** 스킬