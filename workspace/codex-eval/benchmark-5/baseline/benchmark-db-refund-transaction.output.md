지정한 fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 없었습니다. 대신 사용 가능한 fixture인 `evals/fixtures/django-shop`를 읽어보니 현재는 `Order`, `Product`, `Reservation`만 있고 `Payment`, `Refund` 모델은 없습니다. 동시성 예시는 `reserve_inventory()`에서 `transaction.atomic()` + `select_for_update()`로 재고 차감을 보호하는 구조입니다.

환불 처리도 Django에서는 같은 방향으로 잡는 게 맞습니다.

**핵심 전략**

환불은 보통 `Payment`의 환불 가능 금액/상태와 `Refund` 생성 또는 상태 변경을 함께 다룹니다. 이 둘은 같은 비즈니스 불변식에 묶여 있으므로 하나의 DB 트랜잭션 안에서 처리해야 합니다.

예를 들어 불변식은 이런 것들입니다.

```text
sum(successful_refunds.amount) <= payment.amount
payment.status는 refunded / partially_refunded와 일관되어야 함
같은 idempotency_key로 Refund가 중복 생성되면 안 됨
이미 성공/실패로 끝난 Refund를 다시 성공 처리하면 안 됨
```

Django 기준 기본 형태는 다음과 같습니다.

```python
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

def request_refund(payment_id, amount, idempotency_key):
    with transaction.atomic():
        payment = (
            Payment.objects
            .select_for_update()
            .get(id=payment_id)
        )

        refund, created = Refund.objects.get_or_create(
            payment=payment,
            idempotency_key=idempotency_key,
            defaults={
                "amount": amount,
                "status": Refund.STATUS_PENDING,
            },
        )

        if not created:
            return refund

        refunded_amount = (
            Refund.objects
            .filter(
                payment=payment,
                status__in=[Refund.STATUS_PENDING, Refund.STATUS_SUCCEEDED],
            )
            .aggregate(total=Sum("amount"))["total"]
            or 0
        )

        if refunded_amount > payment.amount:
            raise ValueError("refund amount exceeds refundable amount")

        payment.refunded_amount = refunded_amount
        payment.status = (
            Payment.STATUS_REFUNDED
            if refunded_amount == payment.amount
            else Payment.STATUS_PARTIALLY_REFUNDED
        )
        payment.save(update_fields=["refunded_amount", "status"])

    return refund
```

중요한 점은 `Payment.objects.select_for_update()`입니다. 같은 `Payment`에 대해 두 환불 요청이 동시에 들어와도 먼저 잡은 트랜잭션이 끝날 때까지 다른 트랜잭션이 기다립니다. 그래서 둘 다 “아직 환불 가능하다”고 보고 초과 환불을 만드는 lost update를 막을 수 있습니다.

**외부 PG 호출은 트랜잭션 밖에서**

PG사 환불 API 호출을 DB 트랜잭션 안에서 오래 붙잡고 있으면 안 됩니다. 네트워크 지연 동안 row lock을 잡게 되고, 장애 시 DB 락 대기가 길어집니다.

권장 흐름은 보통 이렇습니다.

1. DB 트랜잭션에서 `Refund(PENDING)`를 만들고 `Payment`를 잠근 뒤 환불 가능 여부를 확정한다.
2. 커밋 후 PG 환불 API를 호출한다. 이때 `Refund.id`나 `idempotency_key`를 PG idempotency key로 쓴다.
3. PG 응답을 받은 뒤 별도 트랜잭션에서 `Refund`와 `Payment` 상태를 확정한다.

```python
def mark_refund_succeeded(refund_id, gateway_refund_id):
    with transaction.atomic():
        refund = (
            Refund.objects
            .select_for_update()
            .select_related("payment")
            .get(id=refund_id)
        )
        payment = (
            Payment.objects
            .select_for_update()
            .get(id=refund.payment_id)
        )

        if refund.status == Refund.STATUS_SUCCEEDED:
            return refund

        refund.status = Refund.STATUS_SUCCEEDED
        refund.gateway_refund_id = gateway_refund_id
        refund.refunded_at = timezone.now()
        refund.save(update_fields=["status", "gateway_refund_id", "refunded_at"])

        succeeded_total = (
            Refund.objects
            .filter(payment=payment, status=Refund.STATUS_SUCCEEDED)
            .aggregate(total=Sum("amount"))["total"]
            or 0
        )

        payment.refunded_amount = succeeded_total
        payment.status = (
            Payment.STATUS_REFUNDED
            if succeeded_total == payment.amount
            else Payment.STATUS_PARTIALLY_REFUNDED
        )
        payment.save(update_fields=["refunded_amount", "status"])

    return refund
```

**DB 제약도 같이 둬야 함**

애플리케이션 락만 믿기보다 DB 제약을 같이 두는 게 좋습니다.

```python
class Refund(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT)
    idempotency_key = models.CharField(max_length=128)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=24)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["payment", "idempotency_key"],
                name="uniq_refund_payment_idempotency_key",
            ),
            models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name="refund_amount_positive",
            ),
        ]
```

정리하면, Django에서는 `transaction.atomic()`으로 `Payment`와 `Refund` 변경을 하나의 단위로 묶고, 같은 결제에 대한 동시 환불은 `select_for_update()`로 `Payment` row를 잠그는 방식이 가장 명확합니다. 외부 PG 호출은 트랜잭션 밖으로 빼고, idempotency key와 DB unique constraint로 재시도와 중복 요청을 견디게 만드는 구조가 안전합니다.