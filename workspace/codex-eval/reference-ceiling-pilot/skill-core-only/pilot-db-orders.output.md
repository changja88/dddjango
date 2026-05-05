**주요 내용**

아래 설계는 “주문 1건에 결제 시도 여러 건, 결제 1건에 환불 여러 건”을 기준으로 합니다. 금액은 정수 cents가 더 안전하지만, Django 모델 예시는 `DecimalField`로 작성합니다. PostgreSQL 기준이면 부분 인덱스와 조건부 unique constraint를 적극적으로 쓸 수 있습니다.

```python
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
        PENDING_PAYMENT = "pending_payment", "Pending payment"
        PAID = "paid", "Paid"
        PARTIALLY_REFUNDED = "partially_refunded", "Partially refunded"
        REFUNDED = "refunded", "Refunded"
        CANCELLED = "cancelled", "Cancelled"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    order_number = models.CharField(max_length=32, unique=True)
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING_PAYMENT,
    )
    currency = models.CharField(max_length=3)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    captured_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    refunded_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(total_amount__gt=0),
                name="order_total_amount_positive",
            ),
            models.CheckConstraint(
                condition=Q(captured_amount__gte=0),
                name="order_captured_amount_non_negative",
            ),
            models.CheckConstraint(
                condition=Q(refunded_amount__gte=0),
                name="order_refunded_amount_non_negative",
            ),
            models.CheckConstraint(
                condition=Q(captured_amount__lte=models.F("total_amount")),
                name="order_captured_lte_total",
            ),
            models.CheckConstraint(
                condition=Q(refunded_amount__lte=models.F("captured_amount")),
                name="order_refunded_lte_captured",
            ),
        ]
        indexes = [
            models.Index(
                fields=["customer", "-created_at"],
                name="order_customer_created_idx",
            ),
            models.Index(
                fields=["status", "-created_at"],
                name="order_status_created_idx",
            ),
            models.Index(
                fields=["-created_at"],
                condition=Q(status="pending_payment"),
                name="order_pending_created_idx",
            ),
        ]

    def __str__(self):
        return self.order_number


class Payment(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
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
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField(max_length=3)

    provider = models.CharField(max_length=32)
    provider_payment_id = models.CharField(max_length=128, null=True, blank=True)
    idempotency_key = models.CharField(max_length=128)

    authorized_at = models.DateTimeField(null=True, blank=True)
    captured_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="payment_amount_positive",
            ),
            models.UniqueConstraint(
                fields=["order", "idempotency_key"],
                name="payment_order_idempotency_key_uniq",
            ),
            models.UniqueConstraint(
                fields=["provider", "provider_payment_id"],
                condition=Q(provider_payment_id__isnull=False),
                name="payment_provider_payment_id_uniq",
            ),
        ]
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
                name="payment_provider_pid_idx",
            ),
            models.Index(
                fields=["-created_at"],
                condition=Q(status="pending"),
                name="payment_pending_created_idx",
            ),
        ]

    def __str__(self):
        return f"{self.provider}:{self.provider_payment_id or self.id}"


class Refund(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

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
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField(max_length=3)

    provider_refund_id = models.CharField(max_length=128, null=True, blank=True)
    idempotency_key = models.CharField(max_length=128)

    succeeded_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="refund_amount_positive",
            ),
            models.UniqueConstraint(
                fields=["payment", "idempotency_key"],
                name="refund_payment_idempotency_key_uniq",
            ),
            models.UniqueConstraint(
                fields=["provider_refund_id"],
                condition=Q(provider_refund_id__isnull=False),
                name="refund_provider_refund_id_uniq",
            ),
        ]
        indexes = [
            models.Index(
                fields=["order", "-created_at"],
                name="refund_order_created_idx",
            ),
            models.Index(
                fields=["payment", "-created_at"],
                name="refund_payment_created_idx",
            ),
            models.Index(
                fields=["status", "-created_at"],
                name="refund_status_created_idx",
            ),
            models.Index(
                fields=["-created_at"],
                condition=Q(status="pending"),
                name="refund_pending_created_idx",
            ),
        ]

    def __str__(self):
        return f"refund:{self.provider_refund_id or self.id}"
```

핵심 제약은 Django 모델 검증보다 DB 제약에 둡니다. 특히 `captured_amount <= total_amount`, `refunded_amount <= captured_amount`, 결제/환불 멱등성 unique constraint, PG사 거래 ID unique constraint는 애플리케이션 버그가 있어도 데이터 무결성을 지켜야 합니다.

`Refund.order`는 `payment.order`에서 유도 가능하므로 정규화만 보면 중복입니다. 다만 주문별 환불 목록 조회가 매우 흔한 결제 도메인에서는 합리적인 관계 단축입니다. 대신 서비스 레이어에서 `refund.order_id == refund.payment.order_id`를 보장해야 합니다. PostgreSQL만으로 FK 간 동등성을 직접 제약하기는 어렵기 때문에, 더 엄격히 가려면 `Refund.order`를 제거하고 항상 `payment__order`로 조회합니다.

인덱스는 예상 워크로드 기준입니다.

| 조회 | 인덱스 |
|---|---|
| 고객 주문 목록 | `Order(customer, -created_at)` |
| 관리자 상태별 주문 목록 | `Order(status, -created_at)` |
| 결제 대기 주문 배치 | partial `Order(-created_at) WHERE status='pending_payment'` |
| 주문별 결제 내역 | `Payment(order, -created_at)` |
| PG 콜백 처리 | unique/index `Payment(provider, provider_payment_id)` |
| 결제 pending 재처리 | partial `Payment(-created_at) WHERE status='pending'` |
| 주문별 환불 내역 | `Refund(order, -created_at)` |
| 결제별 환불 내역 | `Refund(payment, -created_at)` |
| 환불 pending 재처리 | partial `Refund(-created_at) WHERE status='pending'` |

복합 인덱스는 동등 조건 컬럼을 앞에 두고 정렬/범위 컬럼을 뒤에 둡니다. 예를 들어 `WHERE customer_id = ? ORDER BY created_at DESC`에는 `customer, -created_at` 순서가 맞습니다. 단순히 모든 FK에 인덱스를 추가하는 것보다 실제 목록, 콜백, 재처리 쿼리를 기준으로 잡는 편이 낫습니다.

트랜잭션 전략은 상태 전이마다 짧고 명시적으로 잡는 것이 안전합니다.

```python
from django.db import IntegrityError, transaction
from django.db.models import F


def mark_payment_captured(*, payment_id, provider_payment_id):
    with transaction.atomic():
        payment = (
            Payment.objects
            .select_related("order")
            .select_for_update()
            .get(id=payment_id)
        )
        order = (
            Order.objects
            .select_for_update()
            .get(id=payment.order_id)
        )

        if payment.status == Payment.Status.CAPTURED:
            return payment

        if payment.status not in {
            Payment.Status.PENDING,
            Payment.Status.AUTHORIZED,
        }:
            raise ValueError("payment is not capturable")

        if payment.currency != order.currency:
            raise ValueError("currency mismatch")

        if order.captured_amount + payment.amount > order.total_amount:
            raise ValueError("captured amount exceeds order total")

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

        Order.objects.filter(id=order.id).update(
            captured_amount=F("captured_amount") + payment.amount,
            status=Order.Status.PAID,
        )

        transaction.on_commit(
            lambda: send_payment_captured_notification(payment.id)
        )

        return payment
```

환불도 같은 패턴입니다. 먼저 `Order`와 관련 `Payment`를 `select_for_update()`로 잠그고, 이미 성공한 환불 합계와 새 환불 금액이 `payment.amount` 또는 `order.captured_amount - order.refunded_amount`를 넘지 않는지 확인한 뒤 상태와 누적 금액을 같은 트랜잭션에서 갱신합니다.

멱등성은 애플리케이션 로직과 DB unique constraint를 같이 써야 합니다.

```python
def create_payment_once(*, order_id, idempotency_key, amount, currency, provider):
    try:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=order_id)

            payment, created = Payment.objects.get_or_create(
                order=order,
                idempotency_key=idempotency_key,
                defaults={
                    "amount": amount,
                    "currency": currency,
                    "provider": provider,
                },
            )

            if not created:
                if payment.amount != amount or payment.currency != currency:
                    raise ValueError("idempotency key reused with different payload")
                return payment

            return payment
    except IntegrityError:
        payment = Payment.objects.get(
            order_id=order_id,
            idempotency_key=idempotency_key,
        )
        if payment.amount != amount or payment.currency != currency:
            raise ValueError("idempotency key reused with different payload")
        return payment
```

외부 PG API 호출은 DB 트랜잭션 안에서 오래 붙잡지 않는 편이 좋습니다. 일반적으로는 `Payment(PENDING)`을 멱등하게 만든 뒤 커밋하고, PG 호출을 수행한 다음, 콜백 또는 결과 반영 단계에서 짧은 `atomic()` + row lock으로 상태를 확정합니다. 이메일, 알림, 웹훅 발행 같은 부수효과는 `transaction.on_commit()` 뒤로 미룹니다.

기본 격리 수준은 PostgreSQL `READ COMMITTED`로 충분합니다. 동시 결제 확정, 동시 환불, PG 콜백 중복 수신처럼 같은 주문/결제 행을 갱신하는 경로에서는 `select_for_update()`가 핵심입니다. `SERIALIZABLE`을 전역으로 올리기보다 충돌 지점에 row lock과 unique constraint를 두는 쪽이 운영상 단순합니다.

테스트와 마이그레이션 체크는 최소한 아래를 잡아야 합니다.

```python
import pytest
from django.db import IntegrityError, transaction


@pytest.mark.django_db
def test_payment_idempotency_key_is_unique_per_order(order):
    Payment.objects.create(
        order=order,
        idempotency_key="pay-1",
        amount=order.total_amount,
        currency=order.currency,
        provider="toss",
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Payment.objects.create(
                order=order,
                idempotency_key="pay-1",
                amount=order.total_amount,
                currency=order.currency,
                provider="toss",
            )


@pytest.mark.django_db
def test_order_refunded_amount_cannot_exceed_captured_amount(order):
    order.captured_amount = 100
    order.refunded_amount = 101

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            order.save()
```

마이그레이션은 `python manage.py makemigrations --check --dry-run`으로 누락 여부를 보고, 중요한 제약/부분 인덱스는 `python manage.py sqlmigrate orders <migration_name>`로 실제 SQL을 확인하는 것을 권장합니다. 동시성 로직은 단순 단위 테스트만으로 부족하므로 동일 주문에 대해 결제 확정/환불 생성을 병렬 실행하는 pytest도 별도로 두는 편이 좋습니다.

API는 짧게 말하면, 클라이언트 요청마다 `Idempotency-Key`를 받고 서버에서 `Payment.idempotency_key` 또는 `Refund.idempotency_key`로 저장하면 됩니다. API 레이어는 얇게 두고, 상태 전이와 트랜잭션은 서비스 함수에 모으는 구조가 Django에서 유지보수하기 좋습니다.

---
> **관련 스킬 참조:**
> - Django 모델/마이그레이션 구현 → **implementation-django** 스킬