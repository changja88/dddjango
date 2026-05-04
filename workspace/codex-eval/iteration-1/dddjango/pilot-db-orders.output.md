**주요 내용**

아래 설계는 “주문 1건에 결제 시도 N건, 결제 1건에 환불 N건”을 기준으로 둡니다. 실제 커머스라면 `OrderItem`은 별도 테이블로 두는 것이 맞지만, 요청 범위가 `Order`, `Payment`, `Refund`라서 금액 확정 후 주문 요약값만 `Order`에 둡니다.

```python
# apps/orders/models.py

import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Order(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING_PAYMENT = "pending_payment", "결제대기"
        PAID = "paid", "결제완료"
        CANCELED = "canceled", "취소"
        PARTIALLY_REFUNDED = "partially_refunded", "부분환불"
        REFUNDED = "refunded", "환불완료"

    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING_PAYMENT,
    )
    currency = models.CharField(max_length=3)
    subtotal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(subtotal_amount__gte=0)
                & Q(discount_amount__gte=0)
                & Q(shipping_amount__gte=0)
                & Q(tax_amount__gte=0)
                & Q(total_amount__gte=0),
                name="order_amounts_non_negative",
            ),
            models.CheckConstraint(
                condition=Q(currency__regex=r"^[A-Z]{3}$"),
                name="order_currency_iso_4217_format",
            ),
        ]
        indexes = [
            models.Index(fields=["customer", "-created_at"], name="order_customer_created_idx"),
            models.Index(fields=["status", "-created_at"], name="order_status_created_idx"),
            models.Index(
                fields=["customer", "status", "-created_at"],
                name="order_customer_status_idx",
            ),
            models.Index(
                fields=["-created_at"],
                name="order_open_created_idx",
                condition=Q(status="pending_payment"),
            ),
        ]

    def __str__(self):
        return f"Order({self.public_id})"


class Payment(TimeStampedModel):
    class Status(models.TextChoices):
        REQUIRES_ACTION = "requires_action", "추가인증필요"
        AUTHORIZED = "authorized", "승인"
        CAPTURED = "captured", "매입완료"
        FAILED = "failed", "실패"
        CANCELED = "canceled", "취소"

    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments",
    )
    idempotency_key = models.CharField(max_length=128)
    provider = models.CharField(max_length=32)
    provider_payment_id = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=32, choices=Status.choices)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField(max_length=3)
    authorized_at = models.DateTimeField(null=True, blank=True)
    captured_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["order", "idempotency_key"],
                name="unique_payment_idempotency_per_order",
            ),
            models.UniqueConstraint(
                fields=["provider", "provider_payment_id"],
                condition=~Q(provider_payment_id=""),
                name="unique_provider_payment_id",
            ),
            models.CheckConstraint(
                condition=Q(amount__gte=0),
                name="payment_amount_non_negative",
            ),
            models.CheckConstraint(
                condition=Q(currency__regex=r"^[A-Z]{3}$"),
                name="payment_currency_iso_4217_format",
            ),
        ]
        indexes = [
            models.Index(fields=["order", "-created_at"], name="payment_order_created_idx"),
            models.Index(fields=["status", "-created_at"], name="payment_status_created_idx"),
            models.Index(
                fields=["provider", "provider_payment_id"],
                name="payment_provider_lookup_idx",
            ),
            models.Index(
                fields=["order", "status"],
                name="payment_order_status_idx",
                condition=Q(status__in=["authorized", "captured"]),
            ),
        ]

    def __str__(self):
        return f"Payment({self.public_id})"


class Refund(TimeStampedModel):
    class Status(models.TextChoices):
        REQUESTED = "requested", "요청"
        SUCCEEDED = "succeeded", "성공"
        FAILED = "failed", "실패"
        CANCELED = "canceled", "취소"

    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        related_name="refunds",
    )
    idempotency_key = models.CharField(max_length=128)
    provider_refund_id = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=32, choices=Status.choices)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField(max_length=3)
    reason = models.CharField(max_length=255, blank=True)
    succeeded_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["payment", "idempotency_key"],
                name="unique_refund_idempotency_per_payment",
            ),
            models.UniqueConstraint(
                fields=["provider_refund_id"],
                condition=~Q(provider_refund_id=""),
                name="unique_provider_refund_id",
            ),
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="refund_amount_positive",
            ),
            models.CheckConstraint(
                condition=Q(currency__regex=r"^[A-Z]{3}$"),
                name="refund_currency_iso_4217_format",
            ),
        ]
        indexes = [
            models.Index(fields=["payment", "-created_at"], name="refund_payment_created_idx"),
            models.Index(fields=["status", "-created_at"], name="refund_status_created_idx"),
            models.Index(
                fields=["payment", "status"],
                name="refund_payment_status_idx",
                condition=Q(status="succeeded"),
            ),
        ]

    def __str__(self):
        return f"Refund({self.public_id})"
```

핵심 제약은 `idempotency_key`입니다. 결제는 `order + idempotency_key`, 환불은 `payment + idempotency_key`로 유니크하게 잡아야 같은 요청 재시도에서 중복 결제/중복 환불이 생성되지 않습니다. PG사 식별자인 `provider_payment_id`, `provider_refund_id`도 별도 유니크로 두어 웹훅 중복 수신을 막습니다.

환불 금액 합계가 결제 금액을 넘지 않아야 하는 제약은 단일 행 `CheckConstraint`로 표현할 수 없습니다. 이건 서비스 레이어에서 `select_for_update()`로 `Payment`와 관련 `Refund` 집계를 잠근 뒤 검증해야 합니다.

```python
# apps/orders/services.py

from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.utils import timezone

from .models import Order, Payment, Refund


@transaction.atomic
def payment_capture(*, order_id, amount, currency, idempotency_key, provider):
    order = Order.objects.select_for_update().get(id=order_id)

    payment, created = Payment.objects.get_or_create(
        order=order,
        idempotency_key=idempotency_key,
        defaults={
            "provider": provider,
            "status": Payment.Status.CAPTURED,
            "amount": amount,
            "currency": currency,
            "captured_at": timezone.now(),
        },
    )

    if not created:
        return payment

    if order.status not in {
        Order.Status.PENDING_PAYMENT,
        Order.Status.PARTIALLY_REFUNDED,
    }:
        raise ValueError("order is not payable")

    if payment.currency != order.currency:
        raise ValueError("currency mismatch")

    captured_total = (
        order.payments.filter(status=Payment.Status.CAPTURED)
        .aggregate(total=Sum("amount"))
        .get("total")
        or 0
    )

    if captured_total >= order.total_amount:
        order.status = Order.Status.PAID
        order.save(update_fields=["status", "updated_at"])

    transaction.on_commit(lambda: notify_payment_captured(payment.id))
    return payment


@transaction.atomic
def refund_create(*, payment_id, amount, currency, idempotency_key, reason=""):
    payment = (
        Payment.objects.select_for_update()
        .select_related("order")
        .get(id=payment_id)
    )
    order = Order.objects.select_for_update().get(id=payment.order_id)

    refund, created = Refund.objects.get_or_create(
        payment=payment,
        idempotency_key=idempotency_key,
        defaults={
            "status": Refund.Status.REQUESTED,
            "amount": amount,
            "currency": currency,
            "reason": reason,
        },
    )

    if not created:
        return refund

    if payment.status != Payment.Status.CAPTURED:
        raise ValueError("only captured payment can be refunded")

    if currency != payment.currency or currency != order.currency:
        raise ValueError("currency mismatch")

    refunded_total = (
        payment.refunds.filter(status=Refund.Status.SUCCEEDED)
        .aggregate(total=Sum("amount"))
        .get("total")
        or 0
    )

    if refunded_total + amount > payment.amount:
        raise ValueError("refund amount exceeds captured payment amount")

    transaction.on_commit(lambda: request_provider_refund(refund.id))
    return refund
```

트랜잭션 전략은 `READ COMMITTED + row lock`을 기본으로 잡는 것이 실용적입니다. 결제 승인, 매입, 환불처럼 금액 상태가 바뀌는 경로에서는 `transaction.atomic()` 안에서 `Order` 또는 `Payment`를 `select_for_update()`로 잠급니다. 외부 PG 호출, 이메일, 알림, 웹훅 발행은 트랜잭션 안에서 실행하지 말고 `transaction.on_commit()` 이후로 넘깁니다.

인덱스는 조회 패턴 기준입니다. 주문 목록은 보통 `customer + created_at`, 운영 콘솔은 `status + created_at`, 결제/환불 웹훅은 `provider_payment_id`, `provider_refund_id`로 찾습니다. 부분 인덱스는 `pending_payment`, `captured`, `succeeded`처럼 자주 조회하지만 전체 행 중 일부인 상태에만 둡니다. 단순히 모든 FK와 모든 status에 인덱스를 추가하면 쓰기 비용만 늘어납니다.

테스트는 최소한 다음을 잡아야 합니다.

```python
import pytest
from django.db import IntegrityError, transaction

from apps.orders.models import Payment, Refund


@pytest.mark.django_db
def test_payment_idempotency_key_is_unique_per_order(order):
    Payment.objects.create(
        order=order,
        idempotency_key="pay-1",
        provider="stripe",
        status=Payment.Status.CAPTURED,
        amount=order.total_amount,
        currency=order.currency,
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Payment.objects.create(
                order=order,
                idempotency_key="pay-1",
                provider="stripe",
                status=Payment.Status.CAPTURED,
                amount=order.total_amount,
                currency=order.currency,
            )


@pytest.mark.django_db
def test_refund_idempotency_key_is_unique_per_payment(payment):
    Refund.objects.create(
        payment=payment,
        idempotency_key="refund-1",
        status=Refund.Status.REQUESTED,
        amount=1000,
        currency=payment.currency,
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Refund.objects.create(
                payment=payment,
                idempotency_key="refund-1",
                status=Refund.Status.REQUESTED,
                amount=1000,
                currency=payment.currency,
            )
```

마이그레이션 검증은 `python manage.py makemigrations --check --dry-run`, `python manage.py migrate`, `python manage.py sqlmigrate orders <migration_number>`로 제약과 인덱스 SQL을 확인하면 됩니다. PostgreSQL 운영 환경이면 주요 목록/웹훅 조회 쿼리는 실제 데이터 규모에서 `EXPLAIN ANALYZE`로 인덱스 사용 여부까지 확인해야 합니다.

---
> **관련 스킬 참조:**
> - 결제/환불 상태 전이와 서비스 함수 구현 → **implementation-django** 스킬
> - 실제 쿼리 플랜, 부분 인덱스, 락 경합 검증 → **architecture-db** 스킬