Django에서 환불 처리로 `Payment`와 `Refund`를 함께 업데이트한다면 핵심은 **하나의 DB 트랜잭션 안에서 상태 전이를 원자적으로 처리하고, 동일 결제에 대한 동시 환불 요청을 직렬화하는 것**입니다.

가장 일반적인 전략은 `transaction.atomic()` + `select_for_update()`입니다.

```python
from django.db import transaction
from django.db.models import F

def process_refund(payment_id, amount, idempotency_key):
    with transaction.atomic():
        payment = (
            Payment.objects
            .select_for_update()
            .get(id=payment_id)
        )

        # 멱등성 체크
        refund, created = Refund.objects.get_or_create(
            idempotency_key=idempotency_key,
            defaults={
                "payment": payment,
                "amount": amount,
                "status": Refund.Status.PENDING,
            },
        )

        if not created:
            return refund

        if payment.refunded_amount + amount > payment.amount:
            raise ValueError("Refund amount exceeds payment amount")

        payment.refunded_amount = F("refunded_amount") + amount

        if payment.refunded_amount + amount == payment.amount:
            payment.status = Payment.Status.REFUNDED
        else:
            payment.status = Payment.Status.PARTIALLY_REFUNDED

        payment.save(update_fields=["refunded_amount", "status"])

        refund.status = Refund.Status.SUCCEEDED
        refund.save(update_fields=["status"])

        return refund
```

주의할 점은 `select_for_update()`가 `Payment` row에 락을 걸기 때문에 같은 `Payment`에 대한 동시 환불 요청은 동시에 계산되지 않고 순서대로 처리된다는 것입니다. 그래서 “현재 환불된 금액 확인 → 환불 가능 여부 판단 → Payment/Refund 업데이트”가 깨지지 않습니다.

실무에서는 다음도 같이 둡니다.

- `Refund.idempotency_key`에 unique constraint를 둬서 중복 요청 방지
- `Refund(payment, external_refund_id)` 같은 외부 PG 환불 ID에도 unique constraint
- `Payment.refunded_amount <= Payment.amount`를 애플리케이션 레벨뿐 아니라 가능하면 DB constraint로도 방어
- PG API 호출은 조심해서 배치

PG API 호출 위치는 특히 중요합니다. DB 트랜잭션을 오래 잡은 채 외부 API를 호출하면 락 시간이 길어집니다. 보통은 다음 둘 중 하나를 선택합니다.

1. **락 안에서 Refund를 PENDING으로 만들고 커밋 후 PG 호출**
   - 이후 콜백/잡에서 `Refund`를 `SUCCEEDED`로 바꾸고 `Payment`를 갱신
   - 확장성과 장애 복구에 유리

2. **PG 호출 후 짧은 트랜잭션으로 상태 반영**
   - 단순하지만 PG 성공 후 DB 실패 같은 보상 처리가 필요

권장 구조는 `Refund`를 먼저 `PENDING`으로 생성하고, 실제 환불 성공 이벤트를 기준으로 `transaction.atomic()` 안에서 `Payment`와 `Refund`를 함께 확정하는 방식입니다. 동시성은 `Payment.objects.select_for_update()`로 잡고, 중복 처리는 unique key 기반 멱등성으로 막는 것이 Django에서 가장 방어적인 패턴입니다.