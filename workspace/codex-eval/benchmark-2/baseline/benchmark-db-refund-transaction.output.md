Django에서 환불 처리로 `Payment`와 `Refund`를 함께 업데이트할 때 핵심은 다음입니다.

1. DB 상태 변경은 `transaction.atomic()` 안에서 처리
2. 동시 환불 요청은 `select_for_update()`로 같은 `Payment` 행을 잠금
3. 중복 요청은 idempotency key 또는 unique constraint로 막음
4. 외부 PG 호출은 DB 트랜잭션 안에 오래 넣지 않음
5. 트랜잭션 안에서는 상태 전이와 금액 검증만 짧게 처리

예시는 이런 형태가 안전합니다.

```python
from django.db import transaction
from django.db.models import Sum
from django.core.exceptions import ValidationError

def create_refund(*, payment_id, amount, request_key):
    with transaction.atomic():
        payment = (
            Payment.objects
            .select_for_update()
            .get(id=payment_id)
        )

        refund, created = Refund.objects.get_or_create(
            request_key=request_key,
            defaults={
                "payment": payment,
                "amount": amount,
                "status": Refund.Status.REQUESTED,
            },
        )

        if not created:
            return refund

        refunded_amount = (
            Refund.objects
            .filter(
                payment=payment,
                status__in=[
                    Refund.Status.REQUESTED,
                    Refund.Status.SUCCEEDED,
                ],
            )
            .aggregate(total=Sum("amount"))["total"]
            or 0
        )

        if refunded_amount > payment.amount:
            raise ValidationError("Refund amount exceeds payment amount")

        payment.refunded_amount = refunded_amount

        if refunded_amount == payment.amount:
            payment.status = Payment.Status.REFUNDED
        else:
            payment.status = Payment.Status.PARTIALLY_REFUNDED

        payment.save(update_fields=["refunded_amount", "status"])
        refund.save()

    return refund
```

중요한 점은 `Payment`를 먼저 `select_for_update()`로 잠근다는 것입니다. 같은 결제에 대해 두 개의 환불 요청이 동시에 들어와도 하나가 먼저 락을 잡고 계산 및 저장을 끝낸 뒤, 다음 요청이 최신 상태를 보고 다시 검증합니다. 그래서 초과 환불을 막을 수 있습니다.

`Refund`에는 보통 이런 제약을 둡니다.

```python
class Refund(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT)
    request_key = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=30)
```

외부 PG 환불 API 호출은 주의해야 합니다. DB 트랜잭션 안에서 PG API를 호출하면 락을 오래 잡게 되고, 장애 시 복구가 어려워집니다. 일반적으로는 다음 흐름이 더 낫습니다.

1. 트랜잭션에서 `Refund(status=REQUESTED)` 생성
2. `Payment` 잠금 후 환불 가능 금액 검증
3. 트랜잭션 커밋
4. 워커 또는 `transaction.on_commit()` 이후 PG 환불 요청
5. PG 결과에 따라 `Refund.status`, `Payment.status` 갱신

PG 호출 결과 반영 시에도 다시 짧은 트랜잭션을 잡습니다.

```python
def mark_refund_succeeded(refund_id):
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

        if refund.status == Refund.Status.SUCCEEDED:
            return refund

        refund.status = Refund.Status.SUCCEEDED
        refund.save(update_fields=["status"])

        succeeded_total = (
            Refund.objects
            .filter(payment=payment, status=Refund.Status.SUCCEEDED)
            .aggregate(total=Sum("amount"))["total"]
            or 0
        )

        payment.refunded_amount = succeeded_total
        payment.status = (
            Payment.Status.REFUNDED
            if succeeded_total == payment.amount
            else Payment.Status.PARTIALLY_REFUNDED
        )
        payment.save(update_fields=["refunded_amount", "status"])

    return refund
```

정리하면, Django 기준 권장 전략은 `transaction.atomic()` + `select_for_update()` + idempotency key입니다. 특히 `Payment`를 기준 행으로 잠그고, 항상 같은 순서로 `Payment -> Refund`를 다루면 동시성 문제와 데드락 가능성을 줄일 수 있습니다.