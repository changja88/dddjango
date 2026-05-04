**주요 내용**

환불 처리는 Django 기준으로 **서비스 함수 하나가 유스케이스를 조율하고, DB 변경은 `transaction.atomic()` 안에서, 외부 결제사 호출은 `transaction.on_commit()` 이후에 처리**하는 방식이 가장 안전합니다.

핵심은 `Payment`와 `Refund`를 단순히 “둘 다 저장한다”가 아니라, 다음 불변식을 트랜잭션 경계 안에서 보호하는 것입니다.

- 같은 결제에 대해 환불 가능 금액을 초과할 수 없다.
- 같은 환불 요청은 중복 처리되지 않는다.
- `Payment.refunded_amount`, `Payment.status`, `Refund.status`가 서로 모순되면 안 된다.
- 결제사 API 호출은 DB 롤백으로 되돌릴 수 없으므로 트랜잭션 안에서 직접 호출하지 않는다.

DDD 관점에서는 선택지가 두 가지입니다.

1. `Payment`를 Aggregate Root로 보고 `Refund`를 그 하위 개념처럼 다룬다.
   이 경우 “환불 가능 금액” 같은 강한 불변식은 `Payment` 락 하나로 보호합니다. 일반적인 Django 결제 도메인에서는 이 방식이 실용적입니다.

2. `Payment`와 `Refund`를 별도 Aggregate로 본다.
   이 경우 같은 트랜잭션에서 둘 다 강하게 맞추기보다 도메인 이벤트나 outbox/job으로 결과적 일관성을 사용합니다. 다만 같은 DB 안의 단순 환불 처리라면, 실무적으로 하나의 `atomic()`에서 함께 갱신하는 예외는 허용할 수 있습니다.

Django 구현 전략은 보통 이렇게 잡습니다.

```python
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from payments.models import Payment, Refund
from payments.tasks import request_refund_to_gateway


def refund_request(
    *,
    payment_id: int,
    amount,
    idempotency_key: str,
    reason: str = "",
) -> Refund:
    with transaction.atomic():
        payment = (
            Payment.objects
            .select_for_update()
            .get(pk=payment_id)
        )

        refund, created = Refund.objects.get_or_create(
            payment=payment,
            idempotency_key=idempotency_key,
            defaults={
                "amount": amount,
                "reason": reason,
                "status": Refund.Status.REQUESTED,
                "requested_at": timezone.now(),
            },
        )

        if not created:
            return refund

        if payment.refundable_amount < amount:
            raise ValidationError("환불 가능 금액을 초과했습니다.")

        payment.refunding_amount = F("refunding_amount") + amount
        payment.status = Payment.Status.REFUNDING
        payment.save(update_fields=["refunding_amount", "status", "updated_at"])

    transaction.on_commit(
        lambda: request_refund_to_gateway.delay(refund_id=refund.id)
    )

    return refund
```

여기서 중요한 점은 `select_for_update()`입니다. 동시에 두 요청이 같은 `Payment`를 환불하려고 하면 한 요청이 먼저 `Payment` 행 락을 잡고, 다른 요청은 대기합니다. 그래서 둘 다 같은 `refundable_amount`를 보고 초과 환불하는 race condition을 막을 수 있습니다.

`idempotency_key`에는 DB 유니크 제약을 둬야 합니다.

```python
class Refund(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        PROCESSING = "processing", "Processing"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"

    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        related_name="refunds",
    )
    idempotency_key = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status)
    reason = models.CharField(max_length=255, blank=True)
    requested_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["payment", "idempotency_key"],
                name="unique_refund_idempotency_per_payment",
            ),
        ]
```

결제사 호출 결과를 반영할 때도 같은 원칙입니다. 웹훅이나 worker에서 `Refund`와 `Payment`를 함께 갱신할 때 다시 락을 잡습니다.

```python
def refund_mark_succeeded(*, refund_id: int, gateway_refund_id: str) -> Refund:
    with transaction.atomic():
        refund = (
            Refund.objects
            .select_for_update()
            .select_related("payment")
            .get(pk=refund_id)
        )

        payment = (
            Payment.objects
            .select_for_update()
            .get(pk=refund.payment_id)
        )

        if refund.status == Refund.Status.SUCCEEDED:
            return refund

        if refund.status not in {
            Refund.Status.REQUESTED,
            Refund.Status.PROCESSING,
        }:
            raise ValidationError("성공 처리할 수 없는 환불 상태입니다.")

        refund.status = Refund.Status.SUCCEEDED
        refund.gateway_refund_id = gateway_refund_id
        refund.completed_at = timezone.now()
        refund.save(
            update_fields=[
                "status",
                "gateway_refund_id",
                "completed_at",
                "updated_at",
            ]
        )

        payment.refunding_amount = F("refunding_amount") - refund.amount
        payment.refunded_amount = F("refunded_amount") + refund.amount

        if payment.amount == payment.refunded_amount + refund.amount:
            payment.status = Payment.Status.REFUNDED
        else:
            payment.status = Payment.Status.PARTIALLY_REFUNDED

        payment.save(
            update_fields=[
                "refunding_amount",
                "refunded_amount",
                "status",
                "updated_at",
            ]
        )

    return refund
```

실무에서는 위 코드의 `payment.amount == payment.refunded_amount + refund.amount`처럼 Python 객체의 오래된 값을 섞는 부분을 더 엄격히 다루는 게 좋습니다. `select_for_update()`로 잠근 상태라면 허용 가능하지만, 명확하게 하려면 저장 후 `refresh_from_db()` 하거나 상태 계산을 별도 메서드로 캡슐화합니다.

동시성 전략을 정리하면 다음과 같습니다.

- `transaction.atomic()`으로 `Payment`와 `Refund`의 DB 변경을 하나의 원자적 단위로 묶는다.
- 같은 `Payment`의 환불 가능 금액을 검사하고 변경할 때는 `Payment.objects.select_for_update()`로 행 락을 잡는다.
- 중복 요청 방지는 애플리케이션 코드만 믿지 말고 `UniqueConstraint(payment, idempotency_key)`로 DB에서 강제한다.
- 금액 누적 필드는 `F()` 표현식으로 갱신해 lost update를 피한다.
- `save(update_fields=[...])`를 사용해 불필요한 컬럼 덮어쓰기를 줄인다.
- 결제사 API, 이메일, 알림, 메시지 발행은 `atomic()` 안에서 직접 실행하지 않고 `transaction.on_commit()`이나 outbox 패턴으로 트랜잭션 커밋 후 실행한다.
- `READ COMMITTED`는 대부분의 Django OLTP에서 충분하지만, 환불처럼 경합이 큰 행은 격리 수준을 올리기보다 명시적 row lock과 idempotency를 먼저 적용한다.
- `SERIALIZABLE`은 금융적으로 매우 엄격한 경로에서 고려할 수 있지만, 직렬화 실패 재시도 로직이 반드시 필요하다.

가장 피해야 할 코드는 이런 형태입니다.

```python
payment = Payment.objects.get(pk=payment_id)

if payment.refundable_amount >= amount:
    Refund.objects.create(payment=payment, amount=amount)
    payment.refunded_amount += amount
    payment.save()
    gateway.refund(...)
```

이 코드는 동시에 두 요청이 들어오면 둘 다 같은 환불 가능 금액을 보고 통과할 수 있고, 결제사 호출이 DB 트랜잭션과 분리되지 않아 “DB는 롤백됐는데 실제 환불은 나간 상태”가 될 수 있습니다.

결론적으로, Django에서 환불 처리는 **서비스 레이어 + `atomic()` + `select_for_update()` + idempotency unique constraint + `F()` update + `on_commit()`** 조합으로 설계하는 것이 기준선입니다.

---
> **관련 스킬 참조:**
> - Django 서비스 레이어와 트랜잭션 구현 → **implementation-django** 스킬
> - 격리 수준과 row lock 판단 → **architecture-db** 스킬
> - Payment/Refund 애그리거트 경계 설계 → **architecture-ddd** 스킬