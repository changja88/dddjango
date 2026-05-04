**[주요 내용]**

결제 상태 컬럼은 한 번에 `NOT NULL + default + backfill`로 넣지 말고, 운영에서는 **expand → backfill → contract** 순서로 나누는 게 안전합니다. 핵심은 첫 migration이 오래 락을 잡지 않게 하고, 새 코드와 구 코드가 동시에 떠도 깨지지 않게 하는 것입니다.

1. **1차 배포: nullable 컬럼만 추가**

```python
# orders/models.py
class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    FAILED = "failed", "Failed"
    CANCELED = "canceled", "Canceled"


class Order(models.Model):
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        null=True,
        blank=True,
        db_index=True,
    )
```

Migration은 `null=True` 상태로 추가합니다. 대형 테이블에서 `NOT NULL`이나 Python/Django default를 동시에 추가하면 테이블 스캔, 락 대기, 긴 transaction이 생길 수 있습니다. 새 코드에서는 신규 주문 생성 시 반드시 `payment_status`를 명시적으로 저장하게 합니다.

```python
Order.objects.create(
    # ...
    payment_status=Order.PaymentStatus.PENDING,
)
```

2. **백필: migration 안에 무거운 데이터 변경을 넣지 않는 것을 우선**

작은 테이블이면 `RunPython`도 가능하지만, 운영 주문 테이블처럼 크거나 쓰기가 많은 테이블이면 별도 management command나 배치 작업으로 처리하는 편이 안전합니다. 데이터 migration은 rollback 시 원래 값 복원이 어렵고, 긴 transaction으로 replication lag나 lock 경합을 만들 수 있습니다.

```python
# 예: 관리 명령/운영 스크립트의 핵심 로직
BATCH_SIZE = 1000

while True:
    ids = list(
        Order.objects.filter(payment_status__isnull=True)
        .order_by("id")
        .values_list("id", flat=True)[:BATCH_SIZE]
    )
    if not ids:
        break

    Order.objects.filter(id__in=ids).update(
        payment_status=Order.PaymentStatus.PENDING
    )
```

기존 결제 테이블이나 PG/VAN 응답 상태에서 유도할 수 있다면 `PENDING` 고정값보다 실제 데이터 기준으로 매핑해야 합니다. 단, 이 경우 rollback은 더 위험합니다. 예를 들어 `paid_at IS NOT NULL → paid`로 백필한 뒤 rollback에서 다시 `NULL`로 돌리면, 백필 전부터 사람이 수정한 상태까지 날릴 수 있습니다. 그래서 데이터 migration의 reverse는 “완전 복원”이 아니라 “제약 추가 전 상태로 되돌릴 수 있는 정도”로 봐야 합니다.

3. **검증 후 2차 migration: 제약 추가**

백필 완료 후 NULL이 없음을 확인하고 `null=False`로 변경합니다.

```python
class Order(models.Model):
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        null=False,
        blank=False,
        db_index=True,
    )
```

가능하면 DB 수준 제약도 둡니다.

```python
class Meta:
    constraints = [
        models.CheckConstraint(
            condition=models.Q(
                payment_status__in=["pending", "paid", "failed", "canceled"]
            ),
            name="order_payment_status_valid",
        )
    ]
```

**검증 명령**

배포 전:

```bash
python manage.py makemigrations --dry-run --check
python manage.py sqlmigrate orders 000X
python manage.py migrate --plan
python manage.py test
python manage.py check --deploy
```

1차 migration 적용 후:

```bash
python manage.py migrate orders 000X
python manage.py showmigrations orders
```

백필 중/후 DB 검증:

```sql
SELECT COUNT(*) FROM orders_order WHERE payment_status IS NULL;
SELECT payment_status, COUNT(*) FROM orders_order GROUP BY payment_status;
```

2차 migration 전에는 반드시 `NULL count = 0`이어야 합니다.

2차 migration 적용 전 SQL 확인:

```bash
python manage.py sqlmigrate orders 000Y
python manage.py migrate --plan
```

Rollback은 schema만 되돌릴 수 있다고 가정하는 게 안전합니다.

```bash
python manage.py migrate orders 000X
```

단, 이미 백필된 데이터는 “원래 어떤 row가 NULL이었는지”를 별도 기록하지 않았다면 정확히 복구할 수 없습니다. 결제 상태처럼 감사성과 정산 영향이 있는 데이터는 rollback으로 삭제하지 말고, 필요하면 보정 migration이나 운영 SQL을 별도 승인 절차로 실행하는 게 낫습니다.

---
> **관련 스킬 참조:**
> - 운영 Django migration / 데이터 백필 → **implementation-django** 스킬
> - 컬럼 추가, 제약, 인덱스와 락 위험 → **architecture-db** 스킬