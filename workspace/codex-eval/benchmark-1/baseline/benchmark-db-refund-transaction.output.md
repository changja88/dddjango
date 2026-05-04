Django에서 환불 처리 중 `Payment`와 `Refund`를 함께 업데이트한다면 핵심은 **하나의 DB 트랜잭션 안에서 상태 전이를 원자적으로 처리**하고, **같은 결제에 대한 중복 환불 요청을 직렬화**하는 것입니다.

기본 구조는 보통 이렇게 잡습니다.

```python
from django.db import transaction

@transaction.atomic
def process_refund(payment_id, amount, idempotency_key):
    payment = (
        Payment.objects
        .select_for_update()
        .get(id=payment_id)
    )

    if payment.status not in ["paid", "partially_refunded"]:
        raise ValueError("Refund not allowed")

    refund, created = Refund.objects.get_or_create(
        idempotency_key=idempotency_key,
        defaults={
            "payment": payment,
            "amount": amount,
            "status": "pending",
        },
    )

    if not created:
        return refund

    if payment.refunded_amount + amount > payment.amount:
        raise ValueError("Refund exceeds payment amount")

    payment.refunded_amount += amount
    payment.status = (
        "refunded"
        if payment.refunded_amount == payment.amount
        else "partially_refunded"
    )
    payment.save(update_fields=["refunded_amount", "status"])

    refund.status = "succeeded"
    refund.save(update_fields=["status"])

    return refund
```

중요한 포인트는 다음입니다.

1. `transaction.atomic()`  
   `Payment` 업데이트와 `Refund` 생성/상태 변경을 하나의 트랜잭션으로 묶습니다. 중간에 예외가 나면 둘 다 롤백되어 `Payment`만 환불된 상태거나 `Refund`만 생성된 상태가 되는 일을 막습니다.

2. `select_for_update()`  
   같은 `Payment`에 대해 동시에 두 개의 환불 요청이 들어오면 둘 다 기존 `refunded_amount`를 보고 초과 환불을 만들 수 있습니다. `select_for_update()`는 해당 결제 row에 DB lock을 걸어서 한 트랜잭션이 끝날 때까지 다른 트랜잭션이 같은 row를 수정하지 못하게 합니다.

3. 멱등성 키  
   PG사 webhook 재시도, 클라이언트 재요청, 네트워크 timeout 때문에 같은 환불 요청이 여러 번 들어올 수 있습니다. `Refund.idempotency_key`에 unique constraint를 두고 `get_or_create()` 또는 명시적인 중복 처리를 해야 합니다.

```python
class Refund(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT)
    idempotency_key = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(...)
    status = models.CharField(...)
```

4. 외부 PG 호출 위치  
   DB 트랜잭션 안에서 PG API를 오래 호출하는 것은 조심해야 합니다. row lock을 오래 잡기 때문입니다. 실무에서는 보통 둘 중 하나를 선택합니다.

   - 먼저 DB에서 `Refund(pending)`를 만들고 커밋한 뒤 PG 호출, 이후 결과를 별도 트랜잭션에서 반영
   - 또는 짧은 트랜잭션 안에서 상태 검증/예약만 하고, 실제 PG 호출은 비동기 작업으로 처리

가장 안전한 패턴은 상태를 나누는 것입니다.

```text
Refund: pending -> processing -> succeeded / failed
Payment: paid -> partially_refunded -> refunded
```

그리고 최종 반영 시점에 다시 `Payment.objects.select_for_update()`로 잠근 뒤 `refunded_amount`와 `status`를 갱신합니다.

요약하면, Django 기준 권장 전략은:

- `transaction.atomic()`으로 `Payment`와 `Refund` 변경을 묶기
- `select_for_update()`로 같은 `Payment` 환불을 직렬화하기
- `Refund.idempotency_key`에 unique constraint 두기
- 환불 금액 검증은 lock을 잡은 뒤 수행하기
- PG API 호출은 긴 DB 트랜잭션 안에 넣지 않는 방향을 우선 고려하기