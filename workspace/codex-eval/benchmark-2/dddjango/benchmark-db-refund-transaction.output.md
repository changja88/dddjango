**주요 내용**

Django에서 환불 처리는 `transaction.atomic()`만으로는 부족합니다. 기본 격리 수준인 Read Committed에서는 두 요청이 동시에 같은 `Payment`를 읽고 “아직 환불 가능”하다고 판단할 수 있습니다. 그래서 `Payment` 기준으로 `select_for_update()` row lock을 잡고, DB 제약 조건으로 중복 환불을 막아야 합니다.

핵심 원칙은 세 가지입니다.

1. DB 상태 변경은 짧은 `transaction.atomic()` 안에서 처리한다.
2. 같은 결제 건의 환불 가능 금액 계산은 `Payment.objects.select_for_update()`로 직렬화한다.
3. 외부 PG 호출은 DB transaction 밖에서 실행한다. PG 응답 반영만 다시 짧은 transaction으로 처리한다.

예시 모델 제약:

```python
class Refund(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested"
        SUCCEEDED = "succeeded"
        FAILED = "failed"

    payment = models.ForeignKey(Payment, on_delete=models.PROTECT)
    idempotency_key = models.CharField(max_length=80)
    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["payment", "idempotency_key"],
                name="uniq_refund_payment_idempotency_key",
            ),
        ]
```

서비스 흐름:

```python
from django.db import IntegrityError, transaction

def request_refund(*, payment_id, amount, idempotency_key):
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
                "status": Refund.Status.REQUESTED,
            },
        )

        if not created:
            return refund

        refunded_amount = Refund.objects.filter(
            payment=payment,
            status=Refund.Status.SUCCEEDED,
        ).aggregate(total=Sum("amount"))["total"] or 0

        if refunded_amount + amount > payment.amount:
            raise ValueError("환불 가능 금액 초과")

    # 외부 PG 호출은 transaction 밖에서 수행
    pg_result = pg_client.refund(
        payment.pg_transaction_id,
        amount=amount,
        idempotency_key=idempotency_key,
    )

    with transaction.atomic():
        refund = (
            Refund.objects
            .select_for_update()
            .select_related("payment")
            .get(payment_id=payment_id, idempotency_key=idempotency_key)
        )

        if refund.status != Refund.Status.REQUESTED:
            return refund

        payment = Payment.objects.select_for_update().get(id=payment_id)

        if pg_result.succeeded:
            refund.status = Refund.Status.SUCCEEDED
            payment.refunded_amount = F("refunded_amount") + refund.amount
            payment.save(update_fields=["refunded_amount"])
        else:
            refund.status = Refund.Status.FAILED

        refund.save(update_fields=["status"])

    return refund
```

주의할 점은 첫 transaction 안에서 PG API를 호출하지 않는 것입니다. DB lock을 잡은 채 외부 네트워크를 기다리면 lock 대기 시간이 길어지고, 타임아웃이나 장애 시 결제 테이블 전체의 처리량이 급격히 떨어집니다. 대신 DB에는 “환불 요청 생성”까지만 확정하고, PG 호출 후 결과 반영을 별도 transaction으로 나눕니다.

`Payment` row lock은 환불 가능 금액 계산과 상태 전이를 보호합니다. `Refund`의 unique constraint는 같은 idempotency key로 들어온 재시도, 브라우저 중복 클릭, worker 재실행을 DB 수준에서 차단합니다. 애플리케이션 체크만으로는 동시성 경쟁을 완전히 막을 수 없습니다.

검증은 최소한 다음을 포함해야 합니다.

```python
def test_same_idempotency_key_creates_single_refund():
    ...

def test_concurrent_refunds_do_not_exceed_payment_amount():
    ...

def test_pg_call_is_not_inside_payment_row_lock():
    ...
```

동시성 테스트는 일반 `TestCase`보다 실제 transaction 경계를 확인할 수 있는 `TransactionTestCase` 또는 `pytest.mark.django_db(transaction=True)`가 적합합니다.

---
> **관련 스킬 참조:**
> - 트랜잭션/격리 수준/row lock 설계 → **architecture-db** 스킬
> - Django 서비스 레이어와 ORM 구현 → **implementation-django** 스킬