**주요 내용**

전제는 “하나의 주문에 여러 결제 시도 가능, 하나의 성공 결제에 여러 환불 가능”입니다. 결제/환불은 외부 PG/PSP와 통신하므로 `provider_*_id`와 `idempotency_key`를 별도 보관하고, 돈은 반올림 문제를 피하려고 `DecimalField`보다 **minor unit 정수**를 권합니다. 예: KRW 1000원은 `1000`, USD 10.25는 `1025`.

```python
import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Order(TimestampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_PAYMENT = "pending_payment", "Pending payment"
        PAID = "paid", "Paid"
        CANCELED = "canceled", "Canceled"
        REFUNDED = "refunded", "Refunded"
        PARTIALLY_REFUNDED = "partially_refunded", "Partially refunded"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
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
    currency = models.CharField(max_length=3)

    subtotal_amount = models.PositiveBigIntegerField()
    discount_amount = models.PositiveBigIntegerField(default=0)
    shipping_amount = models.PositiveBigIntegerField(default=0)
    tax_amount = models.PositiveBigIntegerField(default=0)
    total_amount = models.PositiveBigIntegerField()

    paid_amount = models.PositiveBigIntegerField(default=0)
    refunded_amount = models.PositiveBigIntegerField(default=0)

    placed_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                name="orders_total_amount_matches_components",
                condition=Q(
                    total_amount=models.F("subtotal_amount")
                    - models.F("discount_amount")
                    + models.F("shipping_amount")
                    + models.F("tax_amount")
                ),
            ),
            models.CheckConstraint(
                name="orders_paid_amount_not_over_total",
                condition=Q(paid_amount__lte=models.F("total_amount")),
            ),
            models.CheckConstraint(
                name="orders_refunded_amount_not_over_paid",
                condition=Q(refunded_amount__lte=models.F("paid_amount")),
            ),
        ]
        indexes = [
            models.Index(fields=["user", "-created_at"], name="orders_user_created_idx"),
            models.Index(fields=["status", "-created_at"], name="orders_status_created_idx"),
            models.Index(fields=["placed_at"], name="orders_placed_at_idx"),
        ]

    def __str__(self) -> str:
        return f"Order({self.public_id})"


class Payment(TimestampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        REQUIRES_ACTION = "requires_action", "Requires action"
        AUTHORIZED = "authorized", "Authorized"
        CAPTURED = "captured", "Captured"
        FAILED = "failed", "Failed"
        CANCELED = "canceled", "Canceled"

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments",
    )
    idempotency_key = models.CharField(max_length=128)
    provider = models.CharField(max_length=32)
    provider_payment_id = models.CharField(max_length=128, null=True, blank=True)

    status = models.CharField(max_length=32, choices=Status.choices)
    amount = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    currency = models.CharField(max_length=3)

    authorized_at = models.DateTimeField(null=True, blank=True)
    captured_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    failure_code = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["order", "idempotency_key"],
                name="payments_order_idempotency_key_uniq",
            ),
            models.UniqueConstraint(
                fields=["provider", "provider_payment_id"],
                condition=Q(provider_payment_id__isnull=False),
                name="payments_provider_payment_id_uniq",
            ),
            models.CheckConstraint(
                name="payments_amount_positive",
                condition=Q(amount__gt=0),
            ),
        ]
        indexes = [
            models.Index(fields=["order", "-created_at"], name="payments_order_created_idx"),
            models.Index(fields=["status", "-created_at"], name="payments_status_created_idx"),
            models.Index(fields=["provider", "status"], name="payments_provider_status_idx"),
        ]

    def __str__(self) -> str:
        return f"Payment({self.provider}, {self.status})"


class Refund(TimestampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        CANCELED = "canceled", "Canceled"

    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        related_name="refunds",
    )
    idempotency_key = models.CharField(max_length=128)
    provider_refund_id = models.CharField(max_length=128, null=True, blank=True)

    status = models.CharField(max_length=32, choices=Status.choices)
    amount = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    currency = models.CharField(max_length=3)
    reason = models.CharField(max_length=255, blank=True)

    succeeded_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    failure_code = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["payment", "idempotency_key"],
                name="refunds_payment_idempotency_key_uniq",
            ),
            models.UniqueConstraint(
                fields=["payment", "provider_refund_id"],
                condition=Q(provider_refund_id__isnull=False),
                name="refunds_payment_provider_refund_id_uniq",
            ),
            models.CheckConstraint(
                name="refunds_amount_positive",
                condition=Q(amount__gt=0),
            ),
        ]
        indexes = [
            models.Index(fields=["payment", "-created_at"], name="refunds_payment_created_idx"),
            models.Index(fields=["status", "-created_at"], name="refunds_status_created_idx"),
        ]

    def __str__(self) -> str:
        return f"Refund({self.payment_id}, {self.status})"
```

`Refund`에는 `order_id`를 두지 않는 편이 낫습니다. `payment.order`로 도달할 수 있는데 `refund.order_id`를 중복 저장하면 `refund.order != refund.payment.order` 같은 불일치가 생깁니다. 주문별 환불 조회가 병목으로 확인되기 전까지는 정규화된 구조를 유지하는 쪽이 안전합니다.

인덱스는 예상 워크로드 기준입니다.

- 주문 목록: `Order(user, -created_at)`
- 운영자 상태별 주문 조회: `Order(status, -created_at)`
- 결제 시도 조회: `Payment(order, -created_at)`
- 결제 웹훅 처리: `Payment(provider, provider_payment_id)` unique
- 결제 재시도 방지: `Payment(order, idempotency_key)` unique
- 환불 목록: `Refund(payment, -created_at)`
- 환불 웹훅 처리: `Refund(payment, provider_refund_id)` unique

트랜잭션 전략은 서비스 함수에서 명시적으로 가져가는 것이 좋습니다. 핵심은 **주문 또는 결제 row를 잠근 뒤 상태 전이를 검증하고, 외부 API 호출은 트랜잭션 안에서 길게 잡지 않는 것**입니다.

```python
from django.db import IntegrityError, transaction
from django.utils import timezone


def payment_create(
    *,
    order_id: int,
    idempotency_key: str,
    provider: str,
    amount: int,
    currency: str,
) -> Payment:
    with transaction.atomic():
        order = (
            Order.objects.select_for_update()
            .get(id=order_id)
        )

        if order.status not in {
            Order.Status.DRAFT,
            Order.Status.PENDING_PAYMENT,
        }:
            raise ValueError("Order is not payable.")

        if order.currency != currency:
            raise ValueError("Currency mismatch.")

        if amount != order.total_amount - order.paid_amount:
            raise ValueError("Payment amount mismatch.")

        payment, created = Payment.objects.get_or_create(
            order=order,
            idempotency_key=idempotency_key,
            defaults={
                "provider": provider,
                "status": Payment.Status.PENDING,
                "amount": amount,
                "currency": currency,
            },
        )

        if not created:
            return payment

        order.status = Order.Status.PENDING_PAYMENT
        order.save(update_fields=["status", "updated_at"])

    return payment
```

외부 PG 승인/캡처 요청은 보통 위 트랜잭션 밖에서 호출하고, 결과 반영은 다시 짧은 트랜잭션으로 처리합니다. 외부 호출을 DB lock 안에 넣으면 PG 지연이 그대로 주문 row lock 시간으로 이어집니다.

```python
def payment_mark_captured(*, payment_id: int, provider_payment_id: str) -> Payment:
    with transaction.atomic():
        payment = (
            Payment.objects.select_for_update()
            .select_related("order")
            .get(id=payment_id)
        )
        order = (
            Order.objects.select_for_update()
            .get(id=payment.order_id)
        )

        if payment.status == Payment.Status.CAPTURED:
            return payment

        if payment.status not in {
            Payment.Status.PENDING,
            Payment.Status.AUTHORIZED,
            Payment.Status.REQUIRES_ACTION,
        }:
            raise ValueError("Payment cannot be captured.")

        payment.status = Payment.Status.CAPTURED
        payment.provider_payment_id = provider_payment_id
        payment.captured_at = timezone.now()
        payment.save(
            update_fields=[
                "status",
                "provider_payment_id",
                "captured_at",
                "updated_at",
            ]
        )

        order.paid_amount += payment.amount
        order.status = Order.Status.PAID
        order.paid_at = payment.captured_at
        order.save(
            update_fields=[
                "paid_amount",
                "status",
                "paid_at",
                "updated_at",
            ]
        )

    return payment
```

환불은 `Payment`와 `Order`를 함께 잠그고, 이미 성공한 환불 합계가 결제 금액 또는 주문 결제 금액을 넘지 않게 검증합니다. 동시 환불 요청이 들어올 수 있으므로 이 부분은 반드시 row lock이 필요합니다.

```python
def refund_create(
    *,
    payment_id: int,
    idempotency_key: str,
    amount: int,
    reason: str = "",
) -> Refund:
    with transaction.atomic():
        payment = (
            Payment.objects.select_for_update()
            .select_related("order")
            .get(id=payment_id)
        )
        order = (
            Order.objects.select_for_update()
            .get(id=payment.order_id)
        )

        if payment.status != Payment.Status.CAPTURED:
            raise ValueError("Payment is not refundable.")

        refund, created = Refund.objects.get_or_create(
            payment=payment,
            idempotency_key=idempotency_key,
            defaults={
                "status": Refund.Status.PENDING,
                "amount": amount,
                "currency": payment.currency,
                "reason": reason,
            },
        )

        if not created:
            return refund

        succeeded_refunded_amount = (
            payment.refunds.filter(status=Refund.Status.SUCCEEDED)
            .aggregate(total=models.Sum("amount"))["total"]
            or 0
        )

        if succeeded_refunded_amount + amount > payment.amount:
            raise ValueError("Refund amount exceeds captured payment amount.")

    return refund
```

웹훅은 `provider_payment_id`, `provider_refund_id` unique constraint로 중복 처리를 막고, 같은 이벤트가 여러 번 와도 현재 상태를 보고 같은 결과를 반환하게 만들어야 합니다. 별도 `WebhookEvent` 테이블을 둘 수 있다면 `provider + event_id` unique를 추가하는 편이 더 좋습니다.

Django Ninja API는 얇게 두고, 위 서비스 함수를 호출하는 구조가 적절합니다. 동기 엔드포인트라면 `request: HttpRequest`와 명시적 반환 타입을 둡니다.

```python
from django.http import HttpRequest
from ninja import Router, Schema

router = Router()


class PaymentOut(Schema):
    id: int
    status: str
    amount: int
    currency: str


@router.get("/orders/{order_id}/payments", response=list[PaymentOut])
def payment_list(request: HttpRequest, order_id: int) -> list[PaymentOut]:
    payments = Payment.objects.filter(order_id=order_id).order_by("-created_at")
    return list(payments)
```

검증은 최소한 아래를 권합니다.

- `python manage.py makemigrations --check --dry-run`
- `python manage.py sqlmigrate orders <migration_number>`로 unique/check/index SQL 확인
- `pytest.mark.django_db(transaction=True)`로 동시 결제/환불 케이스 테스트
- 같은 `idempotency_key` 두 번 호출 시 row가 하나만 생기는지 테스트
- 환불 2개가 동시에 들어와도 `payment.amount`를 초과하지 않는지 테스트
- 목록 API에는 `assertNumQueries`로 `select_related`/인덱스 전제 깨짐을 회귀 방지

---
> **관련 스킬 참조:**
> - API 엔드포인트 구현 → **implementation-django-ninja** 스킬
> - 동시성 테스트와 마이그레이션 검증 → **implementation-django** 스킬