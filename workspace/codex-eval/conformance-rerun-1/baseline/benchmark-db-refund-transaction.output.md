아래처럼 “환불 요청은 여러 번 올 수 있지만, 실제 환불 가능 금액은 DB와 트랜잭션이 최종적으로 막는다”는 구조로 잡는 게 좋습니다.

**핵심 모델**

```python
class Order(models.Model):
    paid_amount = models.PositiveBigIntegerField()
    refunded_amount = models.PositiveBigIntegerField(default=0)

    class Status(models.TextChoices):
        PAID = "paid"
        PARTIALLY_REFUNDED = "partially_refunded"
        REFUNDED = "refunded"

    status = models.CharField(max_length=32, choices=Status.choices)


class Refund(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        SUCCEEDED = "succeeded"
        FAILED = "failed"

    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="refunds")
    amount = models.PositiveBigIntegerField()
    idempotency_key = models.CharField(max_length=128)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    succeeded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["order", "idempotency_key"],
                name="uniq_refund_order_idempotency_key",
            ),
            models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name="refund_amount_gt_zero",
            ),
        ]
```

`Order.refunded_amount`를 별도로 두는 이유는 조회와 잠금이 단순해지기 때문입니다. 매번 `Refund.objects.aggregate(Sum(...))`로 계산하면 동시성 제어가 까다로워지고, 인덱스와 잠금 범위도 애매해집니다.

**환불 처리 흐름**

```python
from django.db import IntegrityError, transaction
from django.utils import timezone

def refund_order(*, order_id: int, amount: int, idempotency_key: str) -> Refund:
    if amount <= 0:
        raise ValueError("Refund amount must be positive")

    try:
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

            remaining_amount = order.paid_amount - order.refunded_amount

            if amount > remaining_amount:
                raise ValueError("Refund amount exceeds remaining refundable amount")

            refund = Refund.objects.create(
                order=order,
                amount=amount,
                idempotency_key=idempotency_key,
                status=Refund.Status.SUCCEEDED,
                succeeded_at=timezone.now(),
            )

            order.refunded_amount += amount
            order.status = (
                Order.Status.REFUNDED
                if order.refunded_amount == order.paid_amount
                else Order.Status.PARTIALLY_REFUNDED
            )
            order.save(update_fields=["refunded_amount", "status"])

            return refund

    except IntegrityError:
        return Refund.objects.get(
            order_id=order_id,
            idempotency_key=idempotency_key,
        )
```

여기서 중요한 점은 `Order` 한 row를 `select_for_update()`로 잠근다는 것입니다. 같은 주문에 대한 환불은 동시에 들어와도 한 트랜잭션씩만 잔액을 검사하고 차감합니다.

**막는 조건**

부분 환불:
`refunded_amount`가 `paid_amount`보다 작으면 계속 허용합니다.

중복 요청:
`UniqueConstraint(order, idempotency_key)`로 막습니다. 애플리케이션에서 먼저 조회하더라도 race condition이 있으므로 DB unique constraint가 최종 방어선입니다.

잔액 초과 환불:
`select_for_update()`로 주문을 잠근 뒤 `paid_amount - refunded_amount`를 검사합니다. 이 검사는 반드시 같은 `transaction.atomic()` 안에서 해야 합니다.

**DB 제약**

`Refund.amount > 0`은 `CheckConstraint`로 강제할 수 있습니다.

`Order.refunded_amount <= Order.paid_amount`도 가능하면 DB check로 둡니다.

```python
models.CheckConstraint(
    check=models.Q(refunded_amount__lte=models.F("paid_amount")),
    name="order_refunded_amount_lte_paid_amount",
)
```

다만 이 제약은 `Order` row 내부 값만 검증합니다. `Refund` 합계와 `Order.refunded_amount`의 일치는 DB check만으로는 보장하기 어렵기 때문에, 서비스 레이어에서 `Order.refunded_amount`를 단일 출처로 관리하고 테스트로 보호하는 편이 현실적입니다.

**조회 패턴**

목록 화면에서는 `Refund`를 합산하지 말고 `Order.refunded_amount`를 바로 읽습니다.

```python
Order.objects.only("id", "paid_amount", "refunded_amount", "status")
```

상세 화면에서는 환불 이력이 필요하므로 prefetch합니다.

```python
Order.objects.prefetch_related(
    Prefetch(
        "refunds",
        queryset=Refund.objects.order_by("-created_at"),
    )
).get(id=order_id)
```

환불 처리 경로에서는 aggregate 조회를 피하고, 반드시 주문 row를 잠근 뒤 현재 잔액을 봅니다.

```python
Order.objects.select_for_update().get(id=order_id)
```

**마이그레이션 검증**

기존 데이터가 있다면 제약 추가 전에 데이터 검증 migration을 먼저 넣는 게 좋습니다.

검증할 것:

```python
# 1. refunded_amount > paid_amount 인 주문이 없는지
Order.objects.filter(refunded_amount__gt=F("paid_amount")).exists()

# 2. Refund.amount <= 0 인 데이터가 없는지
Refund.objects.filter(amount__lte=0).exists()

# 3. 같은 order + idempotency_key 중복이 없는지
Refund.objects.values("order_id", "idempotency_key") \
    .annotate(count=Count("id")) \
    .filter(count__gt=1)
```

기존 `Refund` 합계로 `Order.refunded_amount`를 채워야 한다면 별도 data migration에서 성공한 환불만 집계합니다.

```python
total = Refund.objects.filter(
    order=order,
    status=Refund.Status.SUCCEEDED,
).aggregate(total=Sum("amount"))["total"] or 0
```

그 다음:

1. 데이터 보정 migration
2. 검증 migration
3. unique/check constraint 추가 migration

순서로 나누는 게 안전합니다.

**테스트 포인트**

반드시 넣을 테스트는 이 정도입니다.

- 같은 `idempotency_key`로 두 번 요청하면 같은 `Refund`가 반환된다.
- 10,000원 결제 주문에 3,000원, 4,000원 부분 환불이 가능하다.
- 남은 금액 3,000원에서 4,000원 환불은 실패한다.
- 동시에 같은 주문에 환불 요청이 들어와도 `refunded_amount <= paid_amount`가 유지된다.
- unique constraint가 `IntegrityError`를 내도 기존 refund를 조회해 idempotent하게 응답한다.

정리하면, 환불 잔액은 `Order` row에 보관하고, 환불 처리 시 `transaction.atomic()` + `select_for_update()`로 해당 주문을 잠근 뒤 갱신하는 구조가 가장 단순하고 견고합니다. 중복 방지는 idempotency key unique constraint, 금액 불변식은 check constraint와 트랜잭션 내부 검증을 같이 둡니다.