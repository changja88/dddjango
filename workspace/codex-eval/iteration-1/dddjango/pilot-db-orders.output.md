현재 작업 디렉터리에 `config.toml`이 없어서 프로젝트별 규칙은 확인하지 못했습니다. 아래는 **Django + PostgreSQL 기준**의 실무형 설계안입니다. MySQL을 쓴다면 partial index/conditional unique 제약은 별도 방식으로 조정해야 합니다.

**핵심 모델**

```python
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Order(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_PAYMENT = "pending_payment", "Pending payment"
        PAID = "paid", "Paid"
        PARTIALLY_REFUNDED = "partially_refunded", "Partially refunded"
        REFUNDED = "refunded", "Refunded"
        CANCELED = "canceled", "Canceled"
        FAILED = "failed", "Failed"

    order_number = models.CharField(max_length=32, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )

    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    currency = models.CharField(max_length=3, default="KRW")
    subtotal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    shipping_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    refunded_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    placed_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="order_amounts_non_negative",
                condition=(
                    Q(subtotal_amount__gte=0)
                    & Q(discount_amount__gte=0)
                    & Q(shipping_amount__gte=0)
                    & Q(tax_amount__gte=0)
                    & Q(total_amount__gte=0)
                    & Q(paid_amount__gte=0)
                    & Q(refunded_amount__gte=0)
                ),
            ),
            models.CheckConstraint(
                name="order_paid_not_over_total",
                condition=Q(paid_amount__lte=models.F("total_amount")),
            ),
            models.CheckConstraint(
                name="order_refunded_not_over_paid",
                condition=Q(refunded_amount__lte=models.F("paid_amount")),
            ),
        ]
        indexes = [
            models.Index(fields=["user", "-created_at"], name="order_user_created_idx"),
            models.Index(fields=["status", "-created_at"], name="order_status_created_idx"),
            models.Index(fields=["placed_at"], name="order_placed_at_idx"),
        ]


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        AUTHORIZED = "authorized", "Authorized"
        CAPTURED = "captured", "Captured"
        FAILED = "failed", "Failed"
        CANCELED = "canceled", "Canceled"

    class Method(models.TextChoices):
        CARD = "card", "Card"
        BANK_TRANSFER = "bank_transfer", "Bank transfer"
        VIRTUAL_ACCOUNT = "virtual_account", "Virtual account"
        WALLET = "wallet", "Wallet"

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments",
    )

    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING)
    method = models.CharField(max_length=32, choices=Method.choices)
    provider = models.CharField(max_length=32)  # toss, iamport, stripe, etc.

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="KRW")

    idempotency_key = models.CharField(max_length=128)
    provider_payment_id = models.CharField(max_length=128, null=True, blank=True)
    provider_transaction_id = models.CharField(max_length=128, null=True, blank=True)

    failure_code = models.CharField(max_length=64, null=True, blank=True)
    failure_message = models.TextField(null=True, blank=True)

    requested_at = models.DateTimeField(default=timezone.now)
    authorized_at = models.DateTimeField(null=True, blank=True)
    captured_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)

    raw_response = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="payment_amount_non_negative",
                condition=Q(amount__gt=0),
            ),
            models.UniqueConstraint(
                fields=["provider", "idempotency_key"],
                name="uniq_payment_provider_idempotency",
            ),
            models.UniqueConstraint(
                fields=["provider", "provider_payment_id"],
                condition=Q(provider_payment_id__isnull=False),
                name="uniq_payment_provider_payment_id",
            ),
        ]
        indexes = [
            models.Index(fields=["order", "status"], name="payment_order_status_idx"),
            models.Index(fields=["status", "-created_at"], name="payment_status_created_idx"),
            models.Index(fields=["provider", "provider_transaction_id"], name="payment_provider_tx_idx"),
            models.Index(
                fields=["provider", "provider_payment_id"],
                name="payment_provider_pid_idx",
                condition=Q(provider_payment_id__isnull=False),
            ),
        ]


class Refund(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        CANCELED = "canceled", "Canceled"

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="refunds",
    )
    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        related_name="refunds",
    )

    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="KRW")
    reason = models.CharField(max_length=255, blank=True)

    provider = models.CharField(max_length=32)
    idempotency_key = models.CharField(max_length=128)
    provider_refund_id = models.CharField(max_length=128, null=True, blank=True)

    failure_code = models.CharField(max_length=64, null=True, blank=True)
    failure_message = models.TextField(null=True, blank=True)

    requested_at = models.DateTimeField(default=timezone.now)
    succeeded_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)

    raw_response = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="refund_amount_positive",
                condition=Q(amount__gt=0),
            ),
            models.UniqueConstraint(
                fields=["provider", "idempotency_key"],
                name="uniq_refund_provider_idempotency",
            ),
            models.UniqueConstraint(
                fields=["provider", "provider_refund_id"],
                condition=Q(provider_refund_id__isnull=False),
                name="uniq_refund_provider_refund_id",
            ),
        ]
        indexes = [
            models.Index(fields=["order", "status"], name="refund_order_status_idx"),
            models.Index(fields=["payment", "status"], name="refund_payment_status_idx"),
            models.Index(fields=["status", "-created_at"], name="refund_status_created_idx"),
            models.Index(
                fields=["provider", "provider_refund_id"],
                name="refund_provider_rid_idx",
                condition=Q(provider_refund_id__isnull=False),
            ),
        ]
```

**설계 포인트**

`Order`는 주문의 비즈니스 상태와 금액 합계를 담당합니다. 결제 성공 여부를 매번 `Payment` aggregate로 계산하면 정확하지만 조회 비용이 커지므로, `paid_amount`, `refunded_amount`를 `Order`에 denormalized column으로 두고 트랜잭션 안에서만 갱신하는 방식이 실무적으로 좋습니다.

`Payment`는 결제 시도 단위입니다. 한 주문에 여러 결제 시도가 생길 수 있으므로 `Order : Payment = 1:N`이 맞습니다. 예를 들어 카드 결제 실패 후 계좌이체로 재시도할 수 있습니다.

`Refund`는 환불 요청 단위입니다. 부분 환불이 가능하므로 `Payment : Refund = 1:N`이 맞습니다. `order`도 함께 들고 있으면 주문 환불 목록 조회가 빠르고 단순해집니다. 단, `payment.order_id == refund.order_id`는 애플리케이션 레벨 또는 DB trigger로 보장해야 합니다. Django 기본 `CheckConstraint`만으로 cross-table FK 비교는 어렵습니다.

**추천 인덱스**

주문 목록은 보통 `user + created_at`, 운영자 조회는 `status + created_at` 패턴이 많습니다.

```python
models.Index(fields=["user", "-created_at"])
models.Index(fields=["status", "-created_at"])
```

결제/환불은 외부 PG webhook 처리가 중요하므로 provider 식별자 인덱스가 필요합니다.

```python
models.Index(fields=["provider", "provider_payment_id"])
models.Index(fields=["provider", "provider_refund_id"])
```

idempotency 처리는 반드시 unique constraint로 막아야 합니다.

```python
UniqueConstraint(fields=["provider", "idempotency_key"])
```

PostgreSQL이면 `provider_payment_id IS NOT NULL` 같은 conditional unique/index를 쓰는 게 좋습니다. 결제 생성 직후에는 provider id가 아직 없을 수 있기 때문입니다.

**트랜잭션 전략**

주문 생성은 짧은 DB 트랜잭션으로 처리합니다.

```python
from django.db import transaction

with transaction.atomic():
    order = Order.objects.create(
        user=user,
        status=Order.Status.PENDING_PAYMENT,
        subtotal_amount=subtotal,
        discount_amount=discount,
        shipping_amount=shipping,
        tax_amount=tax,
        total_amount=total,
        placed_at=timezone.now(),
    )

    payment = Payment.objects.create(
        order=order,
        provider="toss",
        method=Payment.Method.CARD,
        amount=order.total_amount,
        currency=order.currency,
        idempotency_key=idempotency_key,
    )
```

외부 PG API 호출은 DB 트랜잭션 밖에서 하는 것을 권장합니다. DB lock을 잡은 채 네트워크 호출을 하면 지연, timeout, deadlock 위험이 커집니다.

결제 승인/성공 webhook 처리에서는 `select_for_update()`로 `Payment`와 `Order`를 잠급니다.

```python
with transaction.atomic():
    payment = (
        Payment.objects
        .select_for_update()
        .select_related("order")
        .get(provider="toss", provider_payment_id=provider_payment_id)
    )
    order = Order.objects.select_for_update().get(id=payment.order_id)

    if payment.status == Payment.Status.CAPTURED:
        return  # webhook 재전송에 대한 idempotent 처리

    if payment.amount != order.total_amount or payment.currency != order.currency:
        raise ValueError("Payment amount mismatch")

    payment.status = Payment.Status.CAPTURED
    payment.captured_at = timezone.now()
    payment.raw_response = payload
    payment.save(update_fields=["status", "captured_at", "raw_response", "updated_at"])

    order.status = Order.Status.PAID
    order.paid_amount = payment.amount
    order.paid_at = timezone.now()
    order.save(update_fields=["status", "paid_amount", "paid_at", "updated_at"])
```

환불 요청도 먼저 DB에서 가능 금액을 잠금 상태로 검증하고 `Refund(PENDING)`을 만듭니다. 그다음 PG 환불 API를 트랜잭션 밖에서 호출합니다.

```python
with transaction.atomic():
    order = Order.objects.select_for_update().get(id=order_id)
    payment = Payment.objects.select_for_update().get(id=payment_id, order=order)

    refundable_amount = payment.amount - order.refunded_amount
    if refund_amount > refundable_amount:
        raise ValueError("Refund amount exceeds refundable amount")

    refund = Refund.objects.create(
        order=order,
        payment=payment,
        provider=payment.provider,
        amount=refund_amount,
        currency=payment.currency,
        idempotency_key=idempotency_key,
        reason=reason,
    )
```

환불 성공 webhook에서는 다시 lock을 잡고 `Refund`와 `Order`를 함께 갱신합니다.

```python
with transaction.atomic():
    refund = (
        Refund.objects
        .select_for_update()
        .select_related("order", "payment")
        .get(provider="toss", provider_refund_id=provider_refund_id)
    )
    order = Order.objects.select_for_update().get(id=refund.order_id)

    if refund.status == Refund.Status.SUCCEEDED:
        return

    refund.status = Refund.Status.SUCCEEDED
    refund.succeeded_at = timezone.now()
    refund.raw_response = payload
    refund.save(update_fields=["status", "succeeded_at", "raw_response", "updated_at"])

    order.refunded_amount = order.refunded_amount + refund.amount
    if order.refunded_amount == order.paid_amount:
        order.status = Order.Status.REFUNDED
    else:
        order.status = Order.Status.PARTIALLY_REFUNDED

    order.save(update_fields=["refunded_amount", "status", "updated_at"])
```

**운영 기준**

결제/환불 상태 변경은 state machine처럼 제한해야 합니다. 예를 들어 `CAPTURED -> FAILED` 같은 역방향 전이는 막아야 합니다.

Webhook은 중복 수신을 기본값으로 가정해야 합니다. 가능하면 `PaymentWebhookEvent` 같은 별도 테이블을 두고 `provider + event_id` unique constraint를 잡는 것이 가장 안전합니다. 이번 범위가 `Order`, `Payment`, `Refund` 세 테이블이라면 각 테이블의 provider idempotency key와 provider payment/refund id unique constraint로 최소 방어선을 둡니다.

격리 수준은 일반적으로 PostgreSQL `READ COMMITTED` + `select_for_update()`면 충분합니다. 중요한 것은 주문/결제/환불 금액을 갱신하는 모든 코드 경로에서 같은 row lock 순서를 지키는 것입니다. 추천 순서는 항상 `Order -> Payment -> Refund`입니다.