**[주요 내용]**

fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, 현재 작업 디렉터리에도 읽을 fixture 파일이 없었습니다. 따라서 구체 코드에 대한 diff 대신 Django 기준 전략으로 정리합니다.

환불은 `Payment`와 `Refund`가 함께 바뀌므로 `transaction.atomic()`이 필요합니다. 예를 들어 `Refund`는 생성됐는데 `Payment.refunded_amount`나 `Payment.status` 업데이트가 실패하면 결제 상태와 환불 내역이 불일치합니다. 두 모델의 DB 변경은 하나의 원자적 단위로 묶어야 합니다.

동시성에서는 `select_for_update()`로 기준 행을 잠가야 합니다. 같은 결제에 대해 환불 요청 2개가 동시에 들어오면 둘 다 “아직 환불 가능”이라고 판단한 뒤 중복 환불을 만들 수 있습니다. 보통 `Payment` 행을 잠그고, 그 잠금 안에서 환불 가능 금액과 상태 전이를 검사합니다.

```python
# models.py
class Refund(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        SUCCEEDED = "succeeded"
        FAILED = "failed"

    payment = models.ForeignKey(Payment, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField()
    idempotency_key = models.CharField(max_length=128)
    provider_refund_id = models.CharField(max_length=128, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status, default=Status.PENDING)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["payment", "idempotency_key"],
                name="uq_refund_payment_idempotency_key",
            ),
            models.UniqueConstraint(
                fields=["provider_refund_id"],
                condition=models.Q(provider_refund_id__isnull=False),
                name="uq_refund_provider_refund_id",
            ),
        ]
```

서비스 흐름은 외부 PG 호출과 DB 트랜잭션 경계를 분리하는 쪽이 안전합니다. 네트워크 호출을 `atomic()` 안에서 하면 DB row lock을 오래 잡고, PG 응답 지연이 결제 테이블 동시성을 막습니다. 반대로 PG 환불을 먼저 호출하고 DB 저장이 실패하면 “실제 환불은 됐는데 DB에는 없음” 상태가 됩니다.

권장 흐름은 `Refund(PENDING)`을 DB에 먼저 만들고 커밋 후 PG 호출을 실행한 뒤, 별도 트랜잭션에서 결과를 반영하는 방식입니다.

```python
# services.py
from django.db import IntegrityError, transaction

def refund_request(*, payment_id: int, amount: int, idempotency_key: str) -> Refund:
    with transaction.atomic():
        payment = (
            Payment.objects
            .select_for_update()
            .get(id=payment_id)
        )

        refund, created = Refund.objects.get_or_create(
            payment=payment,
            idempotency_key=idempotency_key,
            defaults={"amount": amount},
        )
        if not created:
            return refund

        if payment.refundable_amount < amount:
            raise ValidationError("환불 가능 금액을 초과했습니다.")

        transaction.on_commit(
            lambda: refund_call_provider(refund_id=refund.id)
        )

    return refund


def refund_mark_succeeded(*, refund_id: int, provider_refund_id: str) -> Refund:
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
        refund.provider_refund_id = provider_refund_id
        refund.save(update_fields=["status", "provider_refund_id"])

        payment.refunded_amount = models.F("refunded_amount") + refund.amount
        payment.save(update_fields=["refunded_amount"])

    return refund
```

핵심은 세 겹 방어입니다.

1. `transaction.atomic()`  
   `Refund` 생성/상태 변경과 `Payment` 금액/상태 변경을 함께 커밋하거나 함께 롤백합니다.

2. `select_for_update()`  
   같은 `Payment`에 대한 환불 가능 금액 계산과 상태 전이를 직렬화합니다. Django 테스트에서는 실제 lock 검증에 `TransactionTestCase`가 필요합니다.

3. DB constraint와 idempotency  
   `payment + idempotency_key` unique 제약으로 같은 요청의 중복 생성을 막고, PG에도 같은 idempotency key를 전달합니다. PG가 반환하는 `provider_refund_id`도 unique로 잡아 webhook 중복 수신을 방어합니다.

검증은 최소한 다음을 포함해야 합니다.

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/payments/
```

테스트 케이스는 `idempotency_key` 재호출 시 같은 `Refund` 반환, 동시 요청 시 `Refund` 1건만 생성, PG 성공 webhook 중복 수신 시 `Payment.refunded_amount`가 한 번만 증가하는지를 확인해야 합니다.

---
> **관련 스킬 참조:**
> - 트랜잭션/격리 수준/row locking → **architecture-db** 스킬
> - Django 서비스 레이어/transaction.on_commit/테스트 → **implementation-django** 스킬