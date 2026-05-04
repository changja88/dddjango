**[주요 내용]**

결제 상태 컬럼은 한 번에 `NOT NULL + default + backfill`로 넣지 말고, 운영에서는 3단계로 나누는 것이 안전합니다. 핵심은 “스키마 변경”, “데이터 채우기”, “제약 강화”를 분리하는 것입니다.

1. **1차 배포: nullable 컬럼 추가**

```python
# models.py
class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    FAILED = "failed", "Failed"
    CANCELED = "canceled", "Canceled"


payment_status = models.CharField(
    max_length=20,
    choices=PaymentStatus.choices,
    null=True,
    blank=True,
    db_index=True,  # 결제 상태로 조회/집계한다면만 추가
)
```

```python
# migration
migrations.AddField(
    model_name="order",
    name="payment_status",
    field=models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("paid", "Paid"),
            ("failed", "Failed"),
            ("canceled", "Canceled"),
        ],
        null=True,
        blank=True,
        db_index=True,
    ),
)
```

이 단계에서는 기존 row를 건드리지 않습니다. 대형 테이블에서 가장 안전한 형태입니다. 애플리케이션 코드는 `payment_status is None`을 임시 상태로 처리하거나, 새 주문 생성 시 명시적으로 `"pending"`을 써야 합니다.

2. **2차 배포: 데이터 백필**

대형 테이블이면 migration 안의 단일 `UPDATE`보다 배치 백필이 안전합니다. migration으로 처리한다면 `atomic = False`로 두고 작은 트랜잭션으로 나눕니다.

```python
# migration
from django.db import migrations, transaction

BATCH_SIZE = 5000


def backfill_payment_status(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    qs = Order.objects.filter(payment_status__isnull=True).order_by("pk")

    last_pk = 0
    while True:
        ids = list(
            qs.filter(pk__gt=last_pk)
            .values_list("pk", flat=True)[:BATCH_SIZE]
        )
        if not ids:
            break

        with transaction.atomic():
            Order.objects.filter(pk__in=ids).update(payment_status="pending")

        last_pk = ids[-1]


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("orders", "0001_add_payment_status"),
    ]

    operations = [
        migrations.RunPython(backfill_payment_status, migrations.RunPython.noop),
    ]
```

실제 결제 이력, PG 승인 테이블, 기존 boolean 필드(`is_paid`)가 있다면 `"pending"` 고정값 대신 그 데이터를 기준으로 매핑해야 합니다. 이때는 반드시 샘플 검증 쿼리로 매핑 결과를 확인한 뒤 실행하세요.

3. **3차 배포: 제약 조건 강화**

백필이 끝나고 새 코드가 항상 값을 쓰는 것이 확인되면 `null=False`로 변경합니다. `choices`는 Django 애플리케이션 검증일 뿐 DB 제약이 아니므로, 중요한 상태값이면 `CheckConstraint`도 추가합니다.

```python
migrations.AlterField(
    model_name="order",
    name="payment_status",
    field=models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("paid", "Paid"),
            ("failed", "Failed"),
            ("canceled", "Canceled"),
        ],
        null=False,
        db_index=True,
    ),
)
```

PostgreSQL 대형 테이블에서 체크 제약을 추가한다면 일반 Django `AddConstraint`가 검증 락을 유발할 수 있습니다. 트래픽이 큰 테이블은 `NOT VALID`로 추가한 뒤 별도 시간대에 `VALIDATE CONSTRAINT` 하는 방식을 검토하세요.

**데이터 migration과 rollback 위험**

데이터 migration은 rollback이 스키마 migration보다 위험합니다. 예를 들어 기존 `is_paid=True`를 `"paid"`로 바꾼 뒤 rollback한다고 해서 원래 의미를 완전히 복원할 수 있는 것은 아닙니다. 특히 rollback 이후에도 새 코드가 `"failed"`, `"canceled"` 같은 값을 썼다면 단순 reverse migration은 데이터를 잃거나 잘못된 상태로 되돌릴 수 있습니다.

그래서 운영에서는 다음 원칙이 안전합니다.

- 데이터 migration의 reverse는 대부분 `noop`으로 두고, 장애 시 “되돌리기”보다 “forward fix”를 준비합니다.
- 백필 전 row 수와 상태별 예상 분포를 저장합니다.
- 대량 백필 전 DB snapshot 또는 point-in-time recovery 가능 여부를 확인합니다.
- 결제 상태처럼 금전 도메인에 가까운 값은 기존 결제 이벤트/거래 로그를 source of truth로 삼습니다.

**검증 명령**

```bash
python manage.py makemigrations --check --dry-run
python manage.py sqlmigrate orders 0001_add_payment_status
python manage.py migrate --plan
python manage.py migrate
python manage.py shell -c "from apps.orders.models import Order; print(Order.objects.filter(payment_status__isnull=True).count())"
python manage.py check --deploy
```

백필 후에는 최소한 다음도 확인합니다.

```bash
python manage.py shell -c "from apps.orders.models import Order; print(Order.objects.values('payment_status').order_by('payment_status').annotate(c=__import__('django.db.models').db.models.Count('id')))"
```

결론적으로, 안전한 순서는 **nullable 컬럼 추가 → 코드가 새 컬럼을 쓰게 배포 → 배치 백필 → null 잔여 검증 → NOT NULL/제약 추가**입니다.

---
> **관련 스킬 참조:**
> - 운영 DB migration / 제약 조건 / 인덱스 검토 → **architecture-db** 스킬
> - Django model field / migration / data migration 작성 → **implementation-django** 스킬