**[주요 내용]**

대표 조회 패턴을 먼저 고정합니다.

1. 주문/결제 상세: `payment_id`로 현재 결제 상태 1건 + 최신 원장 N건 조회
2. PG webhook 중복 처리: `(pg, merchant_id, webhook_event_id)`로 이미 처리한 이벤트 확인
3. PG 재시도 idempotency: `(pg, merchant_id, idempotency_key)`로 같은 요청의 기존 원장 반환
4. 고객/관리자 이력: `merchant_id + order_id + created_at desc`, `merchant_id + created_at desc`
5. 정산/감사: `pg + pg_transaction_id`, 기간별 `created_at` 범위 조회

권장 구조는 “현재 상태 테이블 1개 + 불변 원장 테이블 1개”입니다. 환불 가능 금액 같은 교차 행 검증은 DB `CHECK`만으로 안전하게 막기 어렵기 때문에, 현재 상태 행을 `select_for_update()`로 잠그고 원장을 append-only로 씁니다.

```python
class Payment(models.Model):
    class Status(models.TextChoices):
        READY = "ready"
        AUTHORIZED = "authorized"
        CAPTURED = "captured"
        PARTIALLY_REFUNDED = "partially_refunded"
        REFUNDED = "refunded"
        FAILED = "failed"

    merchant_id = models.CharField(max_length=64)
    order_id = models.CharField(max_length=64)
    status = models.CharField(max_length=32, choices=Status)
    currency = models.CharField(max_length=3)
    captured_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    refunded_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["merchant_id", "order_id"],
                name="uq_payment_merchant_order",
            ),
            models.CheckConstraint(
                condition=models.Q(captured_amount__gte=0, refunded_amount__gte=0),
                name="ck_payment_amount_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(refunded_amount__lte=models.F("captured_amount")),
                name="ck_payment_refund_lte_capture",
            ),
        ]
        indexes = [
            models.Index(fields=["merchant_id", "order_id"], name="ix_payment_order"),
            models.Index(fields=["merchant_id", "-created_at"], name="ix_payment_recent"),
        ]


class PaymentLedgerEntry(models.Model):
    class Kind(models.TextChoices):
        AUTHORIZE = "authorize"
        CAPTURE = "capture"
        REFUND = "refund"
        FAIL = "fail"

    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        related_name="ledger_entries",
    )
    merchant_id = models.CharField(max_length=64)
    order_id = models.CharField(max_length=64)
    pg = models.CharField(max_length=32)
    kind = models.CharField(max_length=32, choices=Kind)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=3)
    idempotency_key = models.CharField(max_length=128)
    webhook_event_id = models.CharField(max_length=128, null=True, blank=True)
    pg_transaction_id = models.CharField(max_length=128, null=True, blank=True)
    raw_payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gt=0), name="ck_ledger_amount_positive"),
            models.UniqueConstraint(
                fields=["pg", "merchant_id", "idempotency_key"],
                name="uq_ledger_idempotency",
            ),
            models.UniqueConstraint(
                fields=["pg", "merchant_id", "webhook_event_id"],
                condition=models.Q(webhook_event_id__isnull=False),
                name="uq_ledger_webhook_event",
            ),
            models.UniqueConstraint(
                fields=["pg", "merchant_id", "pg_transaction_id", "kind"],
                condition=models.Q(pg_transaction_id__isnull=False),
                name="uq_ledger_pg_tx_kind",
            ),
        ]
        indexes = [
            models.Index(fields=["payment", "-created_at"], name="ix_ledger_payment_recent"),
            models.Index(fields=["merchant_id", "order_id", "-created_at"], name="ix_ledger_order_recent"),
            models.Index(fields=["merchant_id", "-created_at"], name="ix_ledger_merchant_recent"),
            models.Index(fields=["pg", "pg_transaction_id"], name="ix_ledger_pg_tx"),
        ]
```

불변성은 앱 레벨과 DB 레벨을 같이 둡니다. Django에서는 원장 모델에 `save()` 업데이트 금지, `delete()` 금지를 넣고, PostgreSQL에는 `BEFORE UPDATE OR DELETE` trigger를 마이그레이션으로 추가하는 방식이 안전합니다. 운영자가 ORM을 우회해도 원장이 바뀌면 안 됩니다.

```python
@transaction.atomic
def record_refund(payment_id, *, pg, merchant_id, idempotency_key, amount, payload):
    payment = Payment.objects.select_for_update().get(
        id=payment_id,
        merchant_id=merchant_id,
    )

    entry, created = PaymentLedgerEntry.objects.get_or_create(
        pg=pg,
        merchant_id=merchant_id,
        idempotency_key=idempotency_key,
        defaults={
            "payment": payment,
            "order_id": payment.order_id,
            "kind": PaymentLedgerEntry.Kind.REFUND,
            "amount": amount,
            "currency": payment.currency,
            "raw_payload": payload,
        },
    )
    if not created:
        return entry

    if payment.refunded_amount + amount > payment.captured_amount:
        raise ValueError("refund exceeds captured amount")

    payment.refunded_amount = models.F("refunded_amount") + amount
    payment.status = Payment.Status.REFUNDED
    payment.save(update_fields=["refunded_amount", "status"])
    return entry
```

마이그레이션 검증은 필수로 봅니다.

```bash
python manage.py makemigrations --check --dry-run
python manage.py sqlmigrate payments 0001
python manage.py migrate
python manage.py check
python manage.py test payments
```

테스트는 최소한 다음을 포함합니다.

```python
def test_same_idempotency_key_creates_one_ledger_entry(db):
    # 같은 pg, merchant_id, idempotency_key 재호출 시 count == 1

def test_same_webhook_event_is_ignored(db):
    # 같은 webhook_event_id 중복 수신 시 IntegrityError 또는 기존 entry 반환

def test_refund_cannot_exceed_capture_with_concurrent_requests(transactional_db):
    # select_for_update 경로로 초과 환불 방지

def test_ledger_entry_cannot_be_updated_or_deleted(db):
    # ORM update/delete 및 DB trigger 검증
```

대량 데이터 전에는 `EXPLAIN ANALYZE`로 대표 조회 5개가 위 인덱스를 타는지 확인합니다. 특히 `payment_id + created_at desc`, `merchant_id + order_id + created_at desc`, idempotency unique 조회는 Seq Scan이 나오면 인덱스 설계를 다시 봐야 합니다.

---
> **관련 스킬 참조:**
> - Django 모델/마이그레이션 구현 → **implementation-django** 스킬
> - 인덱스/트랜잭션 검증 → **architecture-db** 스킬