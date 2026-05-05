**조회 패턴 / 워크로드**

대표 조회는 아래를 기준으로 인덱스와 잠금 범위를 잡습니다.

```python
Refund.objects.filter(order_id=order_id, idempotency_key=key).first()
Refund.objects.filter(order_id=order_id).order_by("-created_at")
Refund.objects.filter(status=Refund.Status.PENDING).order_by("created_at")
Order.objects.select_for_update().get(id=order_id)
Order.objects.filter(customer_id=customer_id).order_by("-created_at")
```

핵심은 `Order.refunded_amount`를 주문의 환불 누적 잔액으로 두고, 환불 생성 시 `Order` 행 하나를 `select_for_update()`로 잠그는 구조입니다. “부분 환불 허용”, “중복 요청 방지”, “잔액 초과 방지”를 모두 이 주문 행 잠금 기준으로 직렬화합니다.

**모델 설계**

```python
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import CheckConstraint, F, Q, UniqueConstraint


class Order(models.Model):
    class Status(models.TextChoices):
        PAID = "paid", "Paid"
        PARTIALLY_REFUNDED = "partially_refunded", "Partially refunded"
        REFUNDED = "refunded", "Refunded"

    customer = models.ForeignKey("users.User", on_delete=models.PROTECT)
    status = models.CharField(max_length=32, choices=Status.choices)
    paid_amount = models.PositiveBigIntegerField()
    refunded_amount = models.PositiveBigIntegerField(default=0)

    class Meta:
        constraints = [
            CheckConstraint(
                condition=Q(paid_amount__gt=0),
                name="orders_order_paid_amount_positive",
            ),
            CheckConstraint(
                condition=Q(refunded_amount__gte=0),
                name="orders_order_refunded_amount_non_negative",
            ),
            CheckConstraint(
                condition=Q(refunded_amount__lte=F("paid_amount")),
                name="orders_order_refunded_not_over_paid",
            ),
        ]

    @property
    def refundable_amount(self) -> int:
        return self.paid_amount - self.refunded_amount


class Refund(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="refunds",
    )
    idempotency_key = models.CharField(max_length=128)
    amount = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING,
    )
    reason = models.CharField(max_length=255, blank=True)
    gateway_refund_id = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["order", "idempotency_key"],
                name="orders_refund_order_idempotency_key_unique",
            ),
            CheckConstraint(
                condition=Q(amount__gt=0),
                name="orders_refund_amount_positive",
            ),
        ]
        indexes = [
            models.Index(
                fields=["order", "-created_at"],
                name="orders_refund_order_created_idx",
            ),
            models.Index(
                fields=["status", "created_at"],
                name="orders_refund_status_created_idx",
            ),
        ]
```

`Refund.amount`들의 합계를 매번 계산해서 잔액을 판단하지 않는 이유는 동시성 때문입니다. 동시 요청 두 개가 같은 잔액을 보고 각각 통과할 수 있습니다. `Order.refunded_amount`를 잠금 대상 누적값으로 두면 주문 단위로 환불 가능 금액 판단이 직렬화됩니다.

**환불 생성 서비스**

```python
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from .models import Order, Refund


class RefundAlreadyExists(Exception):
    def __init__(self, refund: Refund):
        self.refund = refund


def order_refund_request(
    *,
    order_id: int,
    amount: int,
    idempotency_key: str,
    reason: str = "",
) -> Refund:
    if amount <= 0:
        raise ValidationError("Refund amount must be positive.")

    with transaction.atomic():
        order = (
            Order.objects.select_for_update()
            .only("id", "status", "paid_amount", "refunded_amount")
            .get(id=order_id)
        )

        existing = Refund.objects.filter(
            order=order,
            idempotency_key=idempotency_key,
        ).first()
        if existing:
            if existing.amount != amount:
                raise ValidationError(
                    "Idempotency key was already used with a different amount."
                )
            return existing

        if order.status not in {
            Order.Status.PAID,
            Order.Status.PARTIALLY_REFUNDED,
        }:
            raise ValidationError("Order is not refundable.")

        if amount > order.refundable_amount:
            raise ValidationError("Refund amount exceeds refundable balance.")

        try:
            refund = Refund.objects.create(
                order=order,
                idempotency_key=idempotency_key,
                amount=amount,
                reason=reason,
            )
        except IntegrityError:
            refund = Refund.objects.get(
                order=order,
                idempotency_key=idempotency_key,
            )
            if refund.amount != amount:
                raise ValidationError(
                    "Idempotency key was already used with a different amount."
                )
            return refund

        order.refunded_amount += amount
        order.status = (
            Order.Status.REFUNDED
            if order.refunded_amount == order.paid_amount
            else Order.Status.PARTIALLY_REFUNDED
        )
        order.save(update_fields=["refunded_amount", "status"])

        transaction.on_commit(lambda: enqueue_refund_to_gateway(refund.id))

        return refund
```

외부 결제사 호출은 DB 트랜잭션 안에서 직접 하지 않는 편이 안전합니다. DB 잠금을 오래 잡고 외부 네트워크 장애까지 트랜잭션에 묶으면 주문 행 경합과 장애 전파가 커집니다. 위 구조는 내부 환불 예약을 먼저 확정하고, 커밋 후 `on_commit()`에서 작업 큐나 outbox로 결제사 환불을 보냅니다. 결제사에도 같은 `idempotency_key` 또는 `refund.id`를 전달해야 외부 중복 환불까지 막을 수 있습니다.

**결제사 성공/실패 반영**

```python
from django.db import transaction
from django.utils import timezone

from .models import Refund


def refund_mark_succeeded(*, refund_id: int, gateway_refund_id: str) -> None:
    with transaction.atomic():
        refund = Refund.objects.select_for_update().get(id=refund_id)

        if refund.status == Refund.Status.SUCCEEDED:
            return

        if refund.status == Refund.Status.FAILED:
            raise ValidationError("Failed refund cannot be marked succeeded.")

        refund.status = Refund.Status.SUCCEEDED
        refund.gateway_refund_id = gateway_refund_id
        refund.completed_at = timezone.now()
        refund.save(update_fields=["status", "gateway_refund_id", "completed_at"])
```

실패 처리 정책은 두 가지 중 하나를 명확히 선택해야 합니다.

1. 결제사 실패 시 환불 잔액을 되돌린다.
2. 실패는 별도 보정 작업으로 처리하고, `refunded_amount`는 “환불 예약 금액”으로 본다.

일반적으로는 `PENDING` 상태가 오래 남는 장애까지 고려해 outbox/재시도 정책을 둡니다. 결제사에서 최종 실패가 확정된 경우에만 같은 주문 행을 `select_for_update()`로 잠그고 `refunded_amount -= refund.amount`를 수행합니다.

**조회 패턴**

읽기 전용 조회는 selector로 분리합니다.

```python
from django.db.models import QuerySet

from .models import Refund


def refunds_for_order(*, order_id: int) -> QuerySet[Refund]:
    return (
        Refund.objects.filter(order_id=order_id)
        .only(
            "id",
            "order_id",
            "amount",
            "status",
            "idempotency_key",
            "created_at",
            "completed_at",
        )
        .order_by("-created_at")
    )


def pending_refunds_for_worker(*, limit: int = 100) -> QuerySet[Refund]:
    return (
        Refund.objects.filter(status=Refund.Status.PENDING)
        .select_related("order")
        .order_by("created_at")[:limit]
    )
```

작업자가 여러 개라면 `select_for_update(skip_locked=True)`로 pending refund를 가져와 같은 환불 작업을 여러 워커가 잡지 않게 합니다.

```python
with transaction.atomic():
    refunds = list(
        Refund.objects.select_for_update(skip_locked=True)
        .filter(status=Refund.Status.PENDING)
        .order_by("created_at")[:100]
    )
```

**마이그레이션 순서**

운영 테이블이면 expand → backfill → contract로 나눕니다.

1. `Order.refunded_amount`를 nullable 또는 default `0`으로 추가합니다.
2. `Refund` 테이블, unique constraint, check constraint, 인덱스를 추가합니다.
3. 기존 환불 이력이 있다면 `order_id`별 성공 환불 합계로 `refunded_amount`를 백필합니다.
4. 백필 검증 쿼리로 `refunded_amount > paid_amount` 주문이 없는지 확인합니다.
5. `refunded_amount`를 `NOT NULL`로 고정하고 `refunded_amount <= paid_amount` check constraint를 추가합니다.
6. `sqlmigrate`와 DB의 `EXPLAIN`으로 실제 SQL과 인덱스 사용을 확인합니다.

검증용 쿼리는 최소한 아래를 둡니다.

```sql
SELECT id, paid_amount, refunded_amount
FROM orders_order
WHERE refunded_amount > paid_amount;

SELECT order_id, idempotency_key, COUNT(*)
FROM orders_refund
GROUP BY order_id, idempotency_key
HAVING COUNT(*) > 1;

SELECT order_id, SUM(amount)
FROM orders_refund
WHERE status IN ('pending', 'succeeded')
GROUP BY order_id
HAVING SUM(amount) > (
    SELECT paid_amount FROM orders_order WHERE id = order_id
);
```

**테스트 포인트**

```python
def test_partial_refund_updates_balance(order):
    refund = order_refund_request(
        order_id=order.id,
        amount=3_000,
        idempotency_key="refund-1",
    )

    order.refresh_from_db()
    assert refund.amount == 3_000
    assert order.refunded_amount == 3_000
    assert order.status == Order.Status.PARTIALLY_REFUNDED


def test_same_idempotency_key_returns_existing_refund(order):
    first = order_refund_request(
        order_id=order.id,
        amount=3_000,
        idempotency_key="refund-1",
    )
    second = order_refund_request(
        order_id=order.id,
        amount=3_000,
        idempotency_key="refund-1",
    )

    assert second.id == first.id
    assert Refund.objects.count() == 1


def test_refund_cannot_exceed_remaining_balance(order):
    order_refund_request(
        order_id=order.id,
        amount=7_000,
        idempotency_key="refund-1",
    )

    with pytest.raises(ValidationError):
        order_refund_request(
            order_id=order.id,
            amount=4_000,
            idempotency_key="refund-2",
        )
```

동시성 테스트는 PostgreSQL 기반 `TransactionTestCase` 또는 `pytest.mark.django_db(transaction=True)`로 두 트랜잭션을 실제로 겹치게 검증해야 합니다. SQLite에서는 행 잠금 동작이 달라 `select_for_update()` 검증 신뢰도가 낮습니다.

---
> **관련 스킬 참조:**
> - 환불 API 엔드포인트와 HTTP 상태 코드 설계 → **architecture-api** 스킬
> - Django Ninja로 환불 요청 API 구현 → **implementation-django-ninja** 스킬