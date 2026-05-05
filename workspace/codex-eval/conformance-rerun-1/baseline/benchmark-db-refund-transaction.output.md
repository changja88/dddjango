아래처럼 “환불 요청을 멱등 키 단위로 기록하고, 주문 잔액은 주문 row lock 안에서만 차감”하는 구조가 가장 안전합니다.

**모델 설계**

```python
class Order(models.Model):
    class Status(models.TextChoices):
        PAID = "paid"
        PARTIALLY_REFUNDED = "partially_refunded"
        REFUNDED = "refunded"

    total_paid_amount = models.PositiveBigIntegerField()
    refunded_amount = models.PositiveBigIntegerField(default=0)
    status = models.CharField(max_length=32, choices=Status.choices)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(refunded_amount__gte=0),
                name="order_refunded_amount_gte_0",
            ),
            models.CheckConstraint(
                check=Q(refunded_amount__lte=F("total_paid_amount")),
                name="order_refunded_amount_lte_total_paid",
            ),
        ]


class Refund(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        SUCCEEDED = "succeeded"
        FAILED = "failed"

    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="refunds")
    idempotency_key = models.CharField(max_length=128)
    amount = models.PositiveBigIntegerField()
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING)
    payment_refund_id = models.CharField(max_length=128, blank=True, null=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["order", "idempotency_key"],
                name="uniq_refund_order_idempotency_key",
            ),
            models.CheckConstraint(
                check=Q(amount__gt=0),
                name="refund_amount_gt_0",
            ),
        ]
```

핵심 제약은 두 개입니다.

- `Refund(order, idempotency_key)` unique: 같은 환불 요청 재시도는 같은 결과를 돌려줌
- `Order.refunded_amount <= Order.total_paid_amount`: 애플리케이션 버그가 있어도 잔액 초과 환불을 DB가 막음

**환불 처리 흐름**

```python
from django.db import IntegrityError, transaction
from django.utils import timezone

def refund_order(*, order_id: int, amount: int, idempotency_key: str):
    if amount <= 0:
        raise ValueError("refund amount must be positive")

    with transaction.atomic():
        order = (
            Order.objects
            .select_for_update()
            .get(id=order_id)
        )

        existing = Refund.objects.filter(
            order=order,
            idempotency_key=idempotency_key,
        ).first()

        if existing:
            return existing

        remaining = order.total_paid_amount - order.refunded_amount
        if amount > remaining:
            raise ValueError("refund amount exceeds remaining balance")

        refund = Refund.objects.create(
            order=order,
            amount=amount,
            idempotency_key=idempotency_key,
            status=Refund.Status.PENDING,
        )

        order.refunded_amount += amount
        order.status = (
            Order.Status.REFUNDED
            if order.refunded_amount == order.total_paid_amount
            else Order.Status.PARTIALLY_REFUNDED
        )
        order.save(update_fields=["refunded_amount", "status"])

    # 외부 PG/API 호출은 DB lock 밖에서 실행하는 편이 보통 안전합니다.
    # 단, 실제 돈 환불과 DB 상태 전이를 더 엄격히 묶어야 한다면 outbox/job 패턴을 권장합니다.
    result = payment_client.refund(order_id=order_id, amount=amount, key=idempotency_key)

    with transaction.atomic():
        refund = Refund.objects.select_for_update().get(id=refund.id)
        refund.status = Refund.Status.SUCCEEDED
        refund.payment_refund_id = result.refund_id
        refund.completed_at = timezone.now()
        refund.save(update_fields=["status", "payment_refund_id", "completed_at"])

    return refund
```

더 강한 운영 설계라면 `Refund`를 먼저 `PENDING`으로 만들고, 별도 worker가 `select_for_update(skip_locked=True)`로 가져가 PG 환불을 실행하는 outbox 패턴이 좋습니다. API 요청 transaction 안에서 외부 결제사를 호출하면 DB lock 시간이 길어지고 장애 시 복구가 어려워집니다.

**중복 요청 처리**

동일한 `order_id + idempotency_key`가 다시 들어오면 새 환불을 만들지 말고 기존 `Refund`를 반환합니다.

주의할 점은 같은 idempotency key에 다른 금액이 들어오는 경우입니다. 이건 재시도가 아니라 충돌입니다.

```python
if existing:
    if existing.amount != amount:
        raise ValueError("idempotency key reused with different amount")
    return existing
```

**잔액 초과 방지**

애플리케이션 레벨에서는 반드시 `Order`를 `select_for_update()`로 잠근 뒤 계산합니다.

```python
remaining = order.total_paid_amount - order.refunded_amount

if amount > remaining:
    raise ValueError("refund amount exceeds remaining balance")
```

동시에 두 요청이 들어와도 같은 주문 row lock 때문에 한 요청씩 순차 처리됩니다. 두 번째 요청은 첫 번째 요청이 반영한 `refunded_amount`를 보고 다시 잔액 검사를 하게 됩니다.

DB 레벨에서는 `CheckConstraint(refunded_amount <= total_paid_amount)`가 최후 방어선입니다.

**조회 패턴**

관리자/상세 화면:

```python
order = (
    Order.objects
    .prefetch_related("refunds")
    .get(id=order_id)
)
```

환불 가능 금액이 필요한 목록 화면은 annotation을 쓰거나 저장된 `refunded_amount`를 그대로 씁니다.

```python
Order.objects.annotate(
    refundable_amount=F("total_paid_amount") - F("refunded_amount")
)
```

처리 대기 환불 worker:

```python
with transaction.atomic():
    refunds = (
        Refund.objects
        .select_for_update(skip_locked=True)
        .filter(status=Refund.Status.PENDING)
        .order_by("id")[:100]
    )
```

`skip_locked=True`를 쓰면 여러 worker가 같은 pending refund를 잡지 않습니다.

**마이그레이션 검증**

기존 데이터가 있다면 제약 추가 전에 검증용 data migration 또는 배포 전 SQL 점검이 필요합니다.

```python
invalid_orders = Order.objects.filter(
    refunded_amount__gt=F("total_paid_amount")
).exists()

if invalid_orders:
    raise RuntimeError("invalid refunded_amount exists")
```

`Refund.amount > 0`, `Order.refunded_amount <= total_paid_amount`, 중복 idempotency key도 확인합니다.

```python
from django.db.models import Count

duplicates = (
    Refund.objects
    .values("order_id", "idempotency_key")
    .annotate(count=Count("id"))
    .filter(count__gt=1)
)

if duplicates.exists():
    raise RuntimeError("duplicate refund idempotency keys exist")
```

PostgreSQL을 쓴다면 큰 테이블에서는 바로 강한 제약을 추가하기보다 `NOT VALID` constraint를 추가한 뒤 `VALIDATE CONSTRAINT`로 나누는 방식도 고려합니다. Django 기본 migration API만으로 부족하면 `RunSQL`을 사용합니다.

**테스트 케이스**

반드시 아래는 있어야 합니다.

- 부분 환불 후 `refunded_amount`와 상태가 맞게 바뀐다
- 같은 idempotency key 재요청은 새 `Refund`를 만들지 않는다
- 같은 idempotency key에 다른 금액은 실패한다
- 잔액보다 큰 환불은 실패한다
- 동시 환불 요청 두 개가 합산 잔액을 넘기려 할 때 하나만 성공한다
- DB constraint가 직접적인 잘못된 update도 막는다

요약하면, 금액 불변식은 `Order`에 저장하고 DB constraint로 보호하며, 환불 생성은 `transaction.atomic()` 안에서 `Order.select_for_update()`로 직렬화합니다. 중복 요청은 `Refund(order, idempotency_key)` unique constraint로 막고, 외부 결제 연동은 pending refund/outbox 방식으로 분리하는 편이 운영상 가장 견고합니다.