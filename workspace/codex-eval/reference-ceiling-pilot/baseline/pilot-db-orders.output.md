아래는 Django 모델 기준의 기본 설계안입니다. 결제/환불은 돈과 상태 전이가 핵심이라, `Order`를 중심 엔티티로 두고 `Payment`, `Refund`는 각각 별도 상태 머신을 갖는 구조가 안전합니다.

**모델 구조**

```python
from django.db import models
from django.conf import settings


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        PARTIALLY_REFUNDED = "partially_refunded", "Partially Refunded"
        REFUNDED = "refunded", "Refunded"
        CANCELED = "canceled", "Canceled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )

    order_number = models.CharField(max_length=40, unique=True)

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
    )

    currency = models.CharField(max_length=3, default="KRW")
    total_amount = models.PositiveBigIntegerField()
    paid_amount = models.PositiveBigIntegerField(default=0)
    refunded_amount = models.PositiveBigIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["created_at"]),
        ]
```

```python
class Payment(models.Model):
    class Status(models.TextChoices):
        READY = "ready", "Ready"
        AUTHORIZED = "authorized", "Authorized"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        CANCELED = "canceled", "Canceled"

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments",
    )

    provider = models.CharField(max_length=30)
    provider_payment_id = models.CharField(max_length=100)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.READY,
    )

    currency = models.CharField(max_length=3, default="KRW")
    amount = models.PositiveBigIntegerField()

    approved_at = models.DateTimeField(null=True, blank=True)
    failed_reason = models.TextField(blank=True)

    idempotency_key = models.CharField(max_length=100, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "provider_payment_id"],
                name="uniq_provider_payment",
            ),
        ]
        indexes = [
            models.Index(fields=["order", "status"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["provider", "provider_payment_id"]),
        ]
```

```python
class Refund(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
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

    provider_refund_id = models.CharField(max_length=100, blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REQUESTED,
    )

    currency = models.CharField(max_length=3, default="KRW")
    amount = models.PositiveBigIntegerField()
    reason = models.TextField(blank=True)

    idempotency_key = models.CharField(max_length=100, unique=True)

    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["order", "status"]),
            models.Index(fields=["payment", "status"]),
            models.Index(fields=["status", "-requested_at"]),
        ]
```

**설계 기준**

`Order`는 주문의 최종 상태와 금액 집계를 가진 루트에 가깝게 둡니다. `Payment`는 PG 승인/실패/취소 상태를 독립적으로 기록하고, `Refund`는 환불 요청과 결과를 별도 이력으로 남깁니다.

금액은 `DecimalField`보다 `PositiveBigIntegerField`를 추천합니다. KRW 기준이면 원 단위 정수로 저장하고, USD 같은 소수 통화가 필요하면 최소 화폐 단위, 예를 들어 cents 단위로 저장하는 방식이 예측 가능합니다.

`on_delete=PROTECT`를 쓰는 이유는 결제/환불 이력이 있는 주문을 실수로 삭제하지 않기 위해서입니다. 결제 데이터는 회계, CS, 정산과 연결되기 때문에 물리 삭제보다 상태 변경이나 별도 soft delete 정책이 낫습니다.

**추천 인덱스**

자주 필요한 조회를 기준으로 잡습니다.

```python
Order(user, -created_at)
```

사용자별 주문 목록 조회용입니다.

```python
Order(status, -created_at)
```

관리자 화면에서 결제 대기, 취소, 환불 상태별 목록을 볼 때 필요합니다.

```python
Payment(provider, provider_payment_id)
```

PG 웹훅을 받을 때 외부 결제 ID로 내부 결제를 찾기 위한 핵심 인덱스입니다. 유니크 제약도 같이 둡니다.

```python
Payment(idempotency_key)
Refund(idempotency_key)
```

중복 요청 방지용입니다. 결제 승인, 환불 요청 API는 재시도될 수 있으므로 필수에 가깝습니다.

```python
Refund(order, status)
Refund(payment, status)
```

주문 기준 환불 내역, 결제 건 기준 환불 누적액 검증에 씁니다.

**트랜잭션 전략**

결제 성공 처리처럼 주문과 결제를 함께 바꾸는 코드는 `transaction.atomic()` 안에서 처리합니다.

```python
from django.db import transaction
from django.db.models import F


@transaction.atomic
def mark_payment_paid(payment_id):
    payment = (
        Payment.objects
        .select_for_update()
        .select_related("order")
        .get(id=payment_id)
    )

    order = (
        Order.objects
        .select_for_update()
        .get(id=payment.order_id)
    )

    if payment.status == Payment.Status.PAID:
        return payment

    payment.status = Payment.Status.PAID
    payment.save(update_fields=["status", "updated_at"])

    order.paid_amount = F("paid_amount") + payment.amount
    order.status = Order.Status.PAID
    order.save(update_fields=["paid_amount", "status", "updated_at"])

    return payment
```

환불도 같은 방식으로 `Order`와 `Payment`를 잠근 뒤 처리합니다. 핵심은 환불 가능 금액을 트랜잭션 안에서 검증하는 것입니다.

```python
available = order.paid_amount - order.refunded_amount

if refund_amount > available:
    raise ValueError("Refund amount exceeds refundable amount")
```

환불 성공 후에는 `refunded_amount`를 증가시키고, 금액에 따라 주문 상태를 바꿉니다.

```python
if order.refunded_amount + refund_amount == order.paid_amount:
    order.status = Order.Status.REFUNDED
else:
    order.status = Order.Status.PARTIALLY_REFUNDED
```

**중요한 운영 원칙**

PG API 호출 자체는 가능하면 DB 트랜잭션 밖에서 수행하고, DB 상태 반영만 짧은 트랜잭션으로 묶는 것이 좋습니다. 외부 API 응답을 기다리는 동안 row lock을 잡고 있으면 주문/환불 처리량이 쉽게 떨어집니다.

웹훅 처리는 반드시 멱등적으로 만들어야 합니다. 같은 결제 성공 웹훅이 여러 번 와도 `Payment.status == PAID`이면 추가 반영하지 않아야 합니다.

정산이나 감사가 중요하면 `PaymentEvent`, `RefundEvent` 같은 이벤트 로그 테이블을 추가해 PG 원본 payload와 상태 변경 이력을 별도로 남기는 것을 추천합니다. 다만 처음부터 복잡하게 시작할 필요는 없고, 결제/환불의 중복 처리와 금액 불변식부터 확실히 잡는 것이 우선입니다.