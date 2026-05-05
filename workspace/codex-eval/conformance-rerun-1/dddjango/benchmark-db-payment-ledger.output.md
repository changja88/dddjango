**조회 패턴 / 워크로드**

대표 쿼리를 먼저 고정하고 인덱스를 그에 맞춥니다.

```python
# 주문 상세: 결제/환불 타임라인
PaymentLedgerEntry.objects.filter(order_id=order_id).order_by("occurred_at", "id")

# 사용자 결제 내역
PaymentLedgerEntry.objects.filter(user_id=user_id).order_by("-occurred_at")

# PG webhook 중복 처리 확인
PaymentLedgerEntry.objects.filter(
    provider=provider,
    provider_event_id=provider_event_id,
).exists()

# PG 재시도 idempotency 확인
PaymentLedgerEntry.objects.filter(
    merchant_id=merchant_id,
    idempotency_key=idempotency_key,
).first()

# 정산/감사 배치
PaymentLedgerEntry.objects.filter(
    provider=provider,
    occurred_at__gte=start,
    occurred_at__lt=end,
).order_by("occurred_at", "id")
```

**핵심 설계**

결제 원장은 `append-only`로 둡니다. 결제 성공, 환불 성공, 취소, 실패 기록을 수정하지 않고 새 행으로만 추가합니다. 상태 정정이 필요하면 기존 행을 수정하지 말고 `ADJUSTMENT` 또는 `REVERSAL` 성격의 보정 행을 추가합니다.

현재 결제 상태가 자주 필요하면 원장 테이블에서 매번 계산하지 말고 별도 `Payment` projection 테이블에 현재 상태와 누적 금액을 유지해도 됩니다. 다만 진실의 원천은 원장입니다.

**테이블**

```python
from django.db import models
from django.db.models import Q


class PaymentLedgerEntry(models.Model):
    class EntryType(models.TextChoices):
        PAYMENT_CAPTURED = "PAYMENT_CAPTURED"
        PAYMENT_FAILED = "PAYMENT_FAILED"
        REFUND_SUCCEEDED = "REFUND_SUCCEEDED"
        REFUND_FAILED = "REFUND_FAILED"
        REVERSAL = "REVERSAL"
        ADJUSTMENT = "ADJUSTMENT"

    class Provider(models.TextChoices):
        TOSS = "TOSS"
        NICE = "NICE"
        KCP = "KCP"
        IAMPORT = "IAMPORT"

    id = models.BigAutoField(primary_key=True)

    merchant_id = models.CharField(max_length=64)
    order_id = models.CharField(max_length=64, db_index=True)
    user_id = models.BigIntegerField(db_index=True)

    provider = models.CharField(max_length=32, choices=Provider)
    provider_payment_id = models.CharField(max_length=128)
    provider_refund_id = models.CharField(max_length=128, blank=True)

    idempotency_key = models.CharField(max_length=128)
    provider_event_id = models.CharField(max_length=128, blank=True)

    entry_type = models.CharField(max_length=32, choices=EntryType)
    amount_minor = models.BigIntegerField()
    currency = models.CharField(max_length=3)

    occurred_at = models.DateTimeField()
    received_at = models.DateTimeField(auto_now_add=True)

    raw_payload = models.JSONField()
    payload_hash = models.CharField(max_length=64)

    class Meta:
        db_table = "payment_ledger_entries"
        constraints = [
            models.CheckConstraint(
                condition=Q(amount_minor__gt=0),
                name="payment_ledger_amount_positive",
            ),
            models.CheckConstraint(
                condition=Q(currency__regex=r"^[A-Z]{3}$"),
                name="payment_ledger_currency_iso_4217",
            ),
            models.UniqueConstraint(
                fields=["merchant_id", "idempotency_key"],
                name="uniq_payment_ledger_idempotency_key",
            ),
            models.UniqueConstraint(
                fields=["provider", "provider_event_id"],
                condition=~Q(provider_event_id=""),
                name="uniq_payment_ledger_provider_event",
            ),
            models.UniqueConstraint(
                fields=["provider", "payload_hash"],
                condition=Q(provider_event_id=""),
                name="uniq_payment_ledger_provider_payload_hash_without_event_id",
            ),
        ]
        indexes = [
            models.Index(
                fields=["order_id", "occurred_at", "id"],
                name="idx_payment_ledger_order_time",
            ),
            models.Index(
                fields=["user_id", "-occurred_at"],
                name="idx_payment_ledger_user_recent",
            ),
            models.Index(
                fields=["provider", "occurred_at", "id"],
                name="idx_payment_ledger_provider_time",
            ),
            models.Index(
                fields=["provider_payment_id", "occurred_at"],
                name="idx_payment_ledger_pg_payment_time",
            ),
        ]
```

**컬럼 기준**

`amount_minor`는 원 단위/센트 단위 같은 최소 화폐 단위의 양수로 저장합니다. 결제와 환불의 부호는 금액 부호가 아니라 `entry_type`으로 표현합니다. 이렇게 해야 `amount_minor > 0` 제약을 유지할 수 있고, 환불 금액 검증도 명확해집니다.

`idempotency_key`는 클라이언트/API 재시도 단위의 멱등 키입니다. 같은 `merchant_id + idempotency_key`는 같은 결과를 반환해야 하므로 unique 제약을 둡니다.

`provider_event_id`는 PG webhook 중복 방지용입니다. PG가 이벤트 ID를 안정적으로 제공하면 `provider + provider_event_id`를 unique로 둡니다. 이벤트 ID가 없는 PG라면 canonical JSON payload의 SHA-256 같은 `payload_hash`를 보조 중복 키로 씁니다.

`raw_payload`는 감사와 장애 대응용 원본입니다. 검색 조건으로 자주 쓰지 않는 이상 JSON 내부 필드 인덱스는 처음부터 만들지 않습니다.

**불변성**

Django 모델만으로 불변성을 보장하면 우회 업데이트에 취약합니다. DB trigger 또는 권한 정책까지 같이 둡니다.

```sql
CREATE OR REPLACE FUNCTION prevent_payment_ledger_mutation()
RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'payment ledger entries are immutable';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_payment_ledger_no_update
BEFORE UPDATE ON payment_ledger_entries
FOR EACH ROW EXECUTE FUNCTION prevent_payment_ledger_mutation();

CREATE TRIGGER trg_payment_ledger_no_delete
BEFORE DELETE ON payment_ledger_entries
FOR EACH ROW EXECUTE FUNCTION prevent_payment_ledger_mutation();
```

Django에서는 서비스 레이어에서만 생성하게 하고, `save()`로 기존 행을 수정하는 코드를 만들지 않습니다. 운영 계정도 가능하면 `INSERT` 중심 권한으로 제한합니다.

**트랜잭션**

PG 재시도와 webhook 처리는 같은 패턴을 씁니다.

```python
from django.db import IntegrityError, transaction


def append_payment_ledger_entry(*, attrs):
    try:
        with transaction.atomic():
            return PaymentLedgerEntry.objects.create(**attrs), True
    except IntegrityError:
        return (
            PaymentLedgerEntry.objects.get(
                merchant_id=attrs["merchant_id"],
                idempotency_key=attrs["idempotency_key"],
            ),
            False,
        )
```

핵심은 `SELECT 후 INSERT`가 아니라 `INSERT 후 unique violation 처리`입니다. 동시 요청이 들어와도 DB unique constraint가 최종 방어선이 됩니다.

현재 상태 projection 테이블을 같이 갱신한다면 같은 `transaction.atomic()` 안에서 원장 insert와 projection update를 묶습니다. 주문/결제 row를 갱신할 때는 `select_for_update()`로 해당 payment row를 잠그고, 환불 누적액 검증은 잠금 안에서 수행합니다.

기본 격리 수준은 PostgreSQL의 `READ COMMITTED`로 충분합니다. 단, “잔여 환불 가능 금액”처럼 현재 누적값 기반 검증이 있으면 해당 payment row를 명시적으로 잠그는 것이 격리 수준을 올리는 것보다 보통 낫습니다.

**환불 제약**

단일 row 제약만으로 “총 환불액 <= 결제액”은 보장할 수 없습니다. 이 규칙은 transaction 안에서 검증해야 합니다.

```python
with transaction.atomic():
    payment = (
        Payment.objects
        .select_for_update()
        .get(id=payment_id)
    )

    if payment.refunded_amount_minor + refund_amount > payment.captured_amount_minor:
        raise ValueError("refund amount exceeds captured amount")

    PaymentLedgerEntry.objects.create(...)
    payment.refunded_amount_minor += refund_amount
    payment.save(update_fields=["refunded_amount_minor", "updated_at"])
```

**마이그레이션 검증**

마이그레이션은 다음을 확인합니다.

```bash
python manage.py makemigrations --check --dry-run
python manage.py sqlmigrate payments 0001
python manage.py migrate
python manage.py check
```

PostgreSQL 기준으로는 운영 전후에 실제 쿼리 계획을 확인합니다.

```sql
EXPLAIN ANALYZE
SELECT *
FROM payment_ledger_entries
WHERE order_id = 'ORDER-1'
ORDER BY occurred_at, id;

EXPLAIN ANALYZE
SELECT 1
FROM payment_ledger_entries
WHERE provider = 'TOSS'
  AND provider_event_id = 'evt_123'
LIMIT 1;
```

중복 방지 테스트는 필수입니다.

```python
def test_same_idempotency_key_creates_single_ledger_entry(db):
    attrs = make_ledger_attrs(idempotency_key="idem-1")

    first, created_first = append_payment_ledger_entry(attrs=attrs)
    second, created_second = append_payment_ledger_entry(attrs=attrs)

    assert created_first is True
    assert created_second is False
    assert first.id == second.id
    assert PaymentLedgerEntry.objects.count() == 1
```

---
> **관련 스킬 참조:**
> - Django Ninja webhook endpoint 설계 → **implementation-django-ninja** 스킬
> - 결제 도메인 aggregate/current projection 설계 → **architecture-ddd** 스킬