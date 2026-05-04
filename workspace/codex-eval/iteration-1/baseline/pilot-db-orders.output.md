`/private/tmp/dddjango-codex-eval`에는 `config.toml`이 없어서 별도 프로젝트 지침은 확인하지 못했습니다. 아래는 Django + PostgreSQL 기준의 실무형 설계안입니다.

**핵심 방향**

- `Order`는 주문의 비즈니스 원장
- `Payment`는 결제 시도 및 승인 결과
- `Refund`는 결제에 대한 환불 원장
- 금액은 `DecimalField`, 통화는 명시
- 외부 PG 연동값은 `provider`, `provider_payment_id`, `provider_refund_id`로 보관
- 중복 결제/환불 방지를 위해 `idempotency_key` 유니크 제약 사용
- 상태 전이는 트랜잭션 + row lock으로 보호

```python
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


class OrderStatus(models.TextChoices):
    PENDING = "pending", "결제 대기"
    PAID = "paid", "결제 완료"
    PARTIALLY_REFUNDED = "partially_refunded", "부분 환불"
    REFUNDED = "refunded", "전체 환불"
    CANCELED = "canceled", "취소"


class PaymentStatus(models.TextChoices):
    READY = "ready", "결제 준비"
    AUTHORIZED = "authorized", "승인"
    CAPTURED = "captured", "매입 완료"
    FAILED = "failed", "실패"
    CANCELED = "canceled", "취소"
    PARTIALLY_REFUNDED = "partially_refunded", "부분 환불"
    REFUNDED = "refunded", "전체 환불"


class RefundStatus(models.TextChoices):
    REQUESTED = "requested", "요청"
    SUCCEEDED = "succeeded", "성공"
    FAILED = "failed", "실패"
    CANCELED = "canceled", "취소"


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    order_number = models.CharField(max_length=32, unique=True)

    status = models.CharField(
        max_length=32,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
    )

    currency = models.CharField(max_length=3, default="KRW")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    refunded_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    placed_at = models.DateTimeField(default=timezone.now)
    paid_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["-created_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(total_amount__gte=0),
                name="order_total_amount_gte_0",
            ),
            models.CheckConstraint(
                check=Q(paid_amount__gte=0),
                name="order_paid_amount_gte_0",
            ),
            models.CheckConstraint(
                check=Q(refunded_amount__gte=0),
                name="order_refunded_amount_gte_0",
            ),
        ]


class Payment(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments",
    )

    status = models.CharField(
        max_length=32,
        choices=PaymentStatus.choices,
        default=PaymentStatus.READY,
    )

    provider = models.CharField(max_length=32)
    provider_payment_id = models.CharField(max_length=128, null=True, blank=True)
    idempotency_key = models.CharField(max_length=128, unique=True)

    currency = models.CharField(max_length=3, default="KRW")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    captured_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    refunded_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    failure_code = models.CharField(max_length=64, null=True, blank=True)
    failure_message = models.TextField(null=True, blank=True)

    requested_at = models.DateTimeField(default=timezone.now)
    authorized_at = models.DateTimeField(null=True, blank=True)
    captured_at = models.DateTimeField(null=True, blank=True)

    raw_response = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["order", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["provider", "provider_payment_id"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "provider_payment_id"],
                condition=Q(provider_payment_id__isnull=False),
                name="uniq_payment_provider_payment_id",
            ),
            models.CheckConstraint(
                check=Q(amount__gt=0),
                name="payment_amount_gt_0",
            ),
        ]


class Refund(models.Model):
    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        related_name="refunds",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="refunds",
    )

    status = models.CharField(
        max_length=32,
        choices=RefundStatus.choices,
        default=RefundStatus.REQUESTED,
    )

    provider_refund_id = models.CharField(max_length=128, null=True, blank=True)
    idempotency_key = models.CharField(max_length=128, unique=True)

    currency = models.CharField(max_length=3, default="KRW")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.CharField(max_length=255, blank=True)

    requested_at = models.DateTimeField(default=timezone.now)
    succeeded_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)

    raw_response = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["order", "-created_at"]),
            models.Index(fields=["payment", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["payment", "provider_refund_id"],
                condition=Q(provider_refund_id__isnull=False),
                name="uniq_refund_payment_provider_refund_id",
            ),
            models.CheckConstraint(
                check=Q(amount__gt=0),
                name="refund_amount_gt_0",
            ),
        ]
```

**인덱스 전략**

- `Order.user + created_at`: 마이페이지 주문 목록 조회용
- `Order.status + created_at`: 관리자 주문 상태별 조회용
- `Payment.order + created_at`: 주문 상세에서 결제 이력 조회
- `Payment.provider + provider_payment_id`: PG 웹훅 수신 시 결제 식별
- `Refund.payment + created_at`: 결제별 환불 이력 조회
- `Refund.order + created_at`: 주문 상세에서 환불 이력 조회
- `idempotency_key unique`: 재시도, 중복 요청, 웹훅 중복 수신 방지

**트랜잭션 전략**

결제 승인/매입 반영 시에는 `Order`를 먼저 잠급니다.

```python
from django.db import transaction
from django.utils import timezone

@transaction.atomic
def mark_payment_captured(payment_id):
    payment = (
        Payment.objects
        .select_for_update()
        .select_related("order")
        .get(id=payment_id)
    )
    order = Order.objects.select_for_update().get(id=payment.order_id)

    if payment.status == PaymentStatus.CAPTURED:
        return payment

    payment.status = PaymentStatus.CAPTURED
    payment.captured_amount = payment.amount
    payment.captured_at = timezone.now()
    payment.save(update_fields=[
        "status",
        "captured_amount",
        "captured_at",
        "updated_at",
    ])

    order.paid_amount += payment.amount
    order.status = OrderStatus.PAID
    order.paid_at = order.paid_at or timezone.now()
    order.save(update_fields=[
        "paid_amount",
        "status",
        "paid_at",
        "updated_at",
    ])

    return payment
```

환불도 마찬가지로 `Order`, `Payment`를 잠그고 처리합니다.

```python
@transaction.atomic
def mark_refund_succeeded(refund_id):
    refund = (
        Refund.objects
        .select_for_update()
        .select_related("order", "payment")
        .get(id=refund_id)
    )
    order = Order.objects.select_for_update().get(id=refund.order_id)
    payment = Payment.objects.select_for_update().get(id=refund.payment_id)

    if refund.status == RefundStatus.SUCCEEDED:
        return refund

    if payment.refunded_amount + refund.amount > payment.captured_amount:
        raise ValueError("Refund amount exceeds captured amount")

    refund.status = RefundStatus.SUCCEEDED
    refund.succeeded_at = timezone.now()
    refund.save(update_fields=["status", "succeeded_at", "updated_at"])

    payment.refunded_amount += refund.amount
    payment.status = (
        PaymentStatus.REFUNDED
        if payment.refunded_amount == payment.captured_amount
        else PaymentStatus.PARTIALLY_REFUNDED
    )
    payment.save(update_fields=["refunded_amount", "status", "updated_at"])

    order.refunded_amount += refund.amount
    order.status = (
        OrderStatus.REFUNDED
        if order.refunded_amount == order.paid_amount
        else OrderStatus.PARTIALLY_REFUNDED
    )
    order.save(update_fields=["refunded_amount", "status", "updated_at"])

    return refund
```

실무에서는 PG API 호출 자체는 DB 트랜잭션 밖에서 수행하고, PG 결과를 DB에 반영하는 짧은 구간만 `transaction.atomic()`으로 묶는 편이 좋습니다. 외부 네트워크 호출을 트랜잭션 안에 넣으면 lock 시간이 길어져 주문/환불 동시 처리에서 병목이 생깁니다.