**[주요 내용]**

Fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 존재하지 않아 읽을 fixture 파일이 없었습니다.

Django에서 환불 처리의 핵심은 **DB 상태 변경은 짧은 `transaction.atomic()` 안에서 row lock으로 보호하고, 외부 PG 호출은 DB 트랜잭션 밖에서 수행**하는 것입니다. PG HTTP 호출을 트랜잭션 안에 넣으면 `Payment` row lock을 네트워크 지연 시간 동안 잡게 되어 중복 환불, 타임아웃, 데드락 가능성이 커집니다.

권장 흐름은 보통 2단계입니다.

1. 짧은 트랜잭션에서 `Payment`를 `select_for_update()`로 잠그고 환불 가능 여부를 검증한 뒤 `Refund`를 `REQUESTED` 또는 `PROCESSING`으로 생성한다.
2. 커밋 후 PG 환불 API를 호출한다.
3. PG 응답을 받은 뒤 새 트랜잭션에서 `Refund`와 `Payment`를 다시 잠그고 최종 상태를 반영한다.

핵심 모델 제약은 다음처럼 둡니다.

```python
class Refund(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "요청됨"
        PROCESSING = "processing", "처리중"
        SUCCEEDED = "succeeded", "성공"
        FAILED = "failed", "실패"

    payment = models.ForeignKey(Payment, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField()
    idempotency_key = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=Status)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["payment", "idempotency_key"],
                name="uniq_refund_idempotency_per_payment",
            ),
            models.UniqueConstraint(
                fields=["payment"],
                condition=models.Q(
                    status__in=["requested", "processing", "succeeded"]
                ),
                name="uniq_active_refund_per_payment",
            ),
        ]
```

`uniq_refund_idempotency_per_payment`는 같은 요청 재시도 방지용입니다. 클라이언트나 서버가 만든 `idempotency_key`를 PG에도 함께 전달해야 합니다. `uniq_active_refund_per_payment`는 “결제 1건당 전체 환불 1회만 허용”하는 정책일 때 유효합니다. 부분 환불을 허용한다면 이 제약은 빼고, `Payment` row lock 안에서 누적 환불액이 결제액을 넘지 않는지 검증해야 합니다.

서비스 코드는 이런 경계를 가져야 합니다.

```python
from django.db import IntegrityError, transaction

def request_refund(payment_id, amount, idempotency_key):
    try:
        with transaction.atomic():
            payment = (
                Payment.objects
                .select_for_update()
                .get(id=payment_id)
            )

            if not payment.can_refund(amount):
                raise ValueError("환불할 수 없는 결제입니다.")

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

            refund.status = Refund.Status.PROCESSING
            refund.save(update_fields=["status"])
    except IntegrityError:
        return Refund.objects.get(
            payment_id=payment_id,
            idempotency_key=idempotency_key,
        )

    pg_result = pg_client.refund(
        payment.pg_transaction_id,
        amount=amount,
        idempotency_key=idempotency_key,
    )

    with transaction.atomic():
        refund = Refund.objects.select_for_update().get(id=refund.id)
        payment = Payment.objects.select_for_update().get(id=payment_id)

        if pg_result.succeeded:
            refund.status = Refund.Status.SUCCEEDED
            payment.mark_refunded(amount)
        else:
            refund.status = Refund.Status.FAILED

        refund.save(update_fields=["status"])
        payment.save(update_fields=["status", "refunded_amount"])
```

`select_for_update()`가 필요한 이유는 동시에 두 요청이 같은 `Payment`를 읽고 “아직 환불 가능하다”고 판단하는 레이스를 막기 위해서입니다. `atomic()`만 있고 row lock이 없으면 Read Committed 기본 격리 수준에서 두 트랜잭션이 같은 이전 상태를 보고 각각 `Refund`를 만들 수 있습니다.

반대로 PG 호출은 `atomic()` 밖이어야 합니다. DB 트랜잭션은 내부 무결성 보호 수단이고, PG 호출은 외부 부수효과입니다. 외부 호출 성공 후 DB 업데이트가 실패할 수 있으므로 운영에서는 `transaction.on_commit()` 또는 outbox/job 패턴으로 “커밋된 환불 요청만 PG에 전송”하고, PG idempotency key로 재시도를 안전하게 만드는 방식이 더 견고합니다.

**검증 단계**

```bash
python manage.py makemigrations --check --dry-run
python manage.py test payments.tests.test_refunds
```

테스트에는 동시에 같은 `payment_id`와 같은/다른 `idempotency_key`로 환불을 요청했을 때 `Refund`가 중복 생성되지 않고, 환불액이 초과되지 않으며, 실패한 PG 응답이 `Payment`를 환불 완료로 바꾸지 않는 케이스를 포함해야 합니다.

---
> **관련 스킬 참조:**
> - 트랜잭션 격리와 제약 설계 → **architecture-db** 스킬
> - Django 서비스 레이어와 ORM 동시성 처리 → **implementation-django** 스킬