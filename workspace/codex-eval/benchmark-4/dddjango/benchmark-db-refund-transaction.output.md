**주요 내용**

Django에서는 `Payment`와 `Refund`를 함께 바꾸는 환불 로직을 “DB 상태 전이”와 “외부 PG 호출”로 나누는 것이 핵심입니다. `transaction.atomic()`은 DB 정합성을 위한 것이고, 외부 PG 호출까지 감싸면 네트워크 지연 동안 row lock을 오래 잡아 동시성 문제가 커집니다.

권장 흐름은 다음입니다.

1. 짧은 DB 트랜잭션에서 `Payment`를 row lock
2. 중복 환불 여부와 환불 가능 금액 검증
3. `Refund(PENDING)` 생성 및 `Payment` 상태 갱신
4. 커밋 후 외부 PG 환불 호출
5. PG 결과를 다시 짧은 트랜잭션에서 반영

`select_for_update()`가 필요한 이유는 같은 결제에 대해 환불 요청이 거의 동시에 들어올 수 있기 때문입니다. 둘 다 “환불 가능”이라고 읽고 각각 `Refund`를 만들면 과환불이나 중복 환불이 발생합니다. 따라서 같은 `Payment` 기준의 환불 생성은 반드시 같은 row lock 아래에서 직렬화해야 합니다.

```python
# models.py
class Refund(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        SUCCEEDED = "succeeded"
        FAILED = "failed"

    payment = models.ForeignKey("Payment", on_delete=models.PROTECT)
    amount = models.PositiveIntegerField()
    idempotency_key = models.CharField(max_length=100)
    pg_refund_id = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status, default=Status.PENDING)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["payment", "idempotency_key"],
                name="uq_refund_payment_idempotency",
            ),
            models.UniqueConstraint(
                fields=["pg_refund_id"],
                condition=models.Q(pg_refund_id__isnull=False),
                name="uq_refund_pg_refund_id",
            ),
        ]
```

```python
# services.py
from django.db import IntegrityError, transaction

def refund_request(*, payment_id, amount, idempotency_key):
    with transaction.atomic():
        payment = (
            Payment.objects
            .select_for_update()
            .get(id=payment_id)
        )

        refund, created = Refund.objects.get_or_create(
            payment=payment,
            idempotency_key=idempotency_key,
            defaults={"amount": amount, "status": Refund.Status.PENDING},
        )

        if not created:
            return refund

        if payment.refundable_amount < amount:
            raise ValueError("환불 가능 금액을 초과했습니다.")

        payment.status = Payment.Status.REFUND_PENDING
        payment.save(update_fields=["status"])

        transaction.on_commit(lambda: pg_refund_issue.delay(refund.id))

    return refund
```

외부 PG 호출은 `atomic()` 내부에서 직접 호출하지 않는 편이 안전합니다. DB 트랜잭션이 롤백되었는데 PG 환불은 이미 성공한 상태가 될 수 있고, 반대로 PG 응답 지연 때문에 `Payment` row lock을 오래 잡을 수도 있습니다. 그래서 `transaction.on_commit()`으로 작업 큐를 예약하거나, 커밋 이후 별도 서비스에서 PG를 호출합니다.

PG 결과 반영도 lock이 필요합니다. 사용자의 재시도, 관리자 재처리, PG 웹훅이 동시에 들어올 수 있기 때문입니다.

```python
def refund_mark_succeeded(*, refund_id, pg_refund_id):
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
        refund.pg_refund_id = pg_refund_id
        refund.save(update_fields=["status", "pg_refund_id"])

        payment.apply_refund(refund.amount)
        payment.save(update_fields=["refunded_amount", "status"])

    return refund
```

중복 방지는 애플리케이션의 `if exists`만으로 부족합니다. 반드시 DB 제약이 있어야 합니다. 보통은 `(payment, idempotency_key)` unique constraint를 두고, 클라이언트 또는 서버가 생성한 idempotency key를 PG에도 같이 전달합니다. 전체 환불만 허용하는 정책이면 `payment` 단위로 `PENDING/SUCCEEDED` 환불이 하나만 존재하도록 partial unique constraint를 추가할 수 있습니다.

검증은 최소한 아래 케이스를 봐야 합니다.

```bash
python manage.py test payments.tests.test_refund_concurrency
python manage.py sqlmigrate payments <migration_number>
```

테스트에서는 `TransactionTestCase`로 두 개의 동시 환불 요청을 만들고, 최종 `Refund` 수와 `Payment.refunded_amount`가 한 번만 반영되는지 확인합니다. `sqlmigrate`로 unique constraint와 partial unique constraint가 실제 DB에 생성되는지도 확인해야 합니다.

---
> **관련 스킬 참조:**
> - 트랜잭션 격리와 제약 조건 설계 → **architecture-db** 스킬
> - Django 서비스 레이어와 `transaction.on_commit()` 구현 → **implementation-django** 스킬