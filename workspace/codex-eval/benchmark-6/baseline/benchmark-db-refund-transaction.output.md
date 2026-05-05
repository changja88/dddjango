지정된 fixture path `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았습니다. 대신 평가 repo의 Django fixture인 `/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop`를 확인했습니다. 현재 fixture에는 `Payment`/`Refund` 모델은 없고, `reserve_inventory()`에서 `transaction.atomic()` + `select_for_update()`로 `Product`와 `Order`를 잠그는 패턴만 있습니다. 환불 처리도 같은 기준으로 설계하는 게 맞습니다.

환불에서 핵심은 `Payment`와 `Refund`를 같은 DB 트랜잭션 안에서 일관되게 갱신하고, 같은 결제에 대한 동시 환불 요청이 환불 가능 금액을 초과하지 못하게 막는 것입니다.

```python
from django.db import transaction
from django.utils import timezone

def create_refund(*, payment_id, amount, idempotency_key):
    with transaction.atomic():
        payment = (
            Payment.objects
            .select_for_update()
            .get(id=payment_id)
        )

        existing = Refund.objects.filter(
            payment=payment,
            idempotency_key=idempotency_key,
        ).first()
        if existing:
            return existing

        if payment.status not in [Payment.STATUS_PAID, Payment.STATUS_PARTIALLY_REFUNDED]:
            raise ValueError("payment is not refundable")

        if payment.refunded_amount + amount > payment.amount:
            raise ValueError("refund amount exceeds paid amount")

        refund = Refund.objects.create(
            payment=payment,
            amount=amount,
            status=Refund.STATUS_PENDING,
            idempotency_key=idempotency_key,
        )

        payment.refunded_amount += amount
        payment.status = (
            Payment.STATUS_REFUNDED
            if payment.refunded_amount == payment.amount
            else Payment.STATUS_PARTIALLY_REFUNDED
        )
        payment.save(update_fields=["refunded_amount", "status"])

    return refund
```

중요한 기준은 이렇습니다.

`transaction.atomic()`은 `Payment.refunded_amount` 갱신과 `Refund` 생성이 같이 성공하거나 같이 롤백되게 합니다. 둘 중 하나만 반영되면 결제 상태와 환불 이력이 어긋납니다.

`select_for_update()`는 같은 `Payment` row에 대해 동시에 들어온 환불 요청을 직렬화합니다. 예를 들어 결제 금액이 10,000원이고 두 요청이 동시에 7,000원씩 환불하려고 할 때, 잠금이 없으면 둘 다 “가능”하다고 판단할 수 있습니다. `Payment`를 row lock으로 잡으면 두 번째 요청은 첫 번째 트랜잭션이 끝난 뒤 갱신된 `refunded_amount`를 보고 초과 여부를 다시 판단합니다.

`Refund`에는 `idempotency_key`를 두고, 보통 DB 제약도 같이 둡니다.

```python
class Refund(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=24)
    idempotency_key = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["payment", "idempotency_key"],
                name="uniq_refund_payment_idempotency_key",
            ),
        ]
```

외부 PG사 환불 API 호출은 주의가 필요합니다. DB 트랜잭션을 열고 row lock을 잡은 채로 외부 HTTP 요청을 오래 기다리면 잠금 시간이 길어집니다. 실무에서는 보통 두 단계로 나눕니다.

1. 짧은 트랜잭션 안에서 `Refund(status="pending")`를 만들고 `Payment`를 잠근 상태로 환불 가능 금액을 예약한다.
2. 트랜잭션 밖에서 PG 환불 API를 호출한다.
3. 결과 콜백 또는 후속 처리에서 다시 `transaction.atomic()` + `select_for_update()`로 `Refund`/`Payment`를 확정 상태로 바꾼다.

즉, Django 기준의 기본 전략은 `Payment`를 동시성 기준 row로 삼고, `transaction.atomic()` 안에서 `select_for_update()`로 잠근 뒤, 환불 가능 금액 검증, `Refund` 생성, `Payment` 상태 갱신을 한 단위로 처리하는 것입니다. idempotency key와 unique constraint는 재시도/중복 요청 방어용으로 반드시 같이 두는 편이 안전합니다.