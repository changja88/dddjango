**주요 내용**

안전한 순서는 한 번에 `NOT NULL + default + backfill + index`를 몰아서 하지 않고, 배포 가능한 작은 단계로 나누는 것입니다.

1. 먼저 `payment_status`를 nullable로 추가합니다.
2. 애플리케이션 코드를 배포해서 새 주문/결제에는 값을 쓰게 합니다.
3. 기존 데이터를 배치로 백필합니다.
4. 백필 검증 후 `NOT NULL`, 기본값, 제약조건, 필요한 인덱스를 추가합니다.

예시는 `Order`에 결제 상태를 추가하는 경우입니다.

```python
# orders/models.py
from django.db import models


class Order(models.Model):
    class PaymentStatus(models.TextChoices):
        UNPAID = "unpaid", "미결제"
        PENDING = "pending", "결제대기"
        PAID = "paid", "결제완료"
        FAILED = "failed", "결제실패"
        REFUNDED = "refunded", "환불완료"

    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus,
        null=True,
        blank=True,
    )
```

1차 마이그레이션은 컬럼만 추가합니다. 대형 테이블에서는 여기서 `default`와 `null=False`를 같이 넣지 않는 것이 안전합니다.

```python
# orders/migrations/0002_add_payment_status.py
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="payment_status",
            field=models.CharField(
                max_length=20,
                choices=[
                    ("unpaid", "미결제"),
                    ("pending", "결제대기"),
                    ("paid", "결제완료"),
                    ("failed", "결제실패"),
                    ("refunded", "환불완료"),
                ],
                null=True,
                blank=True,
            ),
        ),
    ]
```

그 다음 애플리케이션 코드에서 새 레코드 생성 시 값을 반드시 쓰게 배포합니다.

```python
Order.objects.create(
    user=user,
    total_amount=amount,
    payment_status=Order.PaymentStatus.UNPAID,
)
```

기존 데이터 백필은 별도 데이터 마이그레이션으로 분리합니다. 직접 `Order`를 import하지 말고 `apps.get_model()`을 사용합니다.

```python
# orders/migrations/0003_backfill_payment_status.py
from django.db import migrations


def backfill_payment_status(apps, schema_editor):
    Order = apps.get_model("orders", "Order")

    Order.objects.filter(payment_status__isnull=True).update(
        payment_status="unpaid"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0002_add_payment_status"),
    ]

    operations = [
        migrations.RunPython(
            backfill_payment_status,
            migrations.RunPython.noop,
        ),
    ]
```

대형 테이블이면 한 번의 `UPDATE`가 오래 락을 잡을 수 있으므로 관리 커맨드나 별도 배치 작업으로 `id` 범위를 나누어 백필하는 편이 더 안전합니다.

백필 검증 후 마지막으로 `null=False`, 기본값, DB 제약을 추가합니다.

```python
# orders/models.py
from django.db import models


class Order(models.Model):
    class PaymentStatus(models.TextChoices):
        UNPAID = "unpaid", "미결제"
        PENDING = "pending", "결제대기"
        PAID = "paid", "결제완료"
        FAILED = "failed", "결제실패"
        REFUNDED = "refunded", "환불완료"

    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus,
        default=PaymentStatus.UNPAID,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    payment_status__in=[
                        "unpaid",
                        "pending",
                        "paid",
                        "failed",
                        "refunded",
                    ]
                ),
                name="order_payment_status_valid",
            ),
        ]
```

```python
# orders/migrations/0004_enforce_payment_status.py
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0003_backfill_payment_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="payment_status",
            field=models.CharField(
                max_length=20,
                choices=[
                    ("unpaid", "미결제"),
                    ("pending", "결제대기"),
                    ("paid", "결제완료"),
                    ("failed", "결제실패"),
                    ("refunded", "환불완료"),
                ],
                default="unpaid",
            ),
        ),
        migrations.AddConstraint(
            model_name="order",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    payment_status__in=[
                        "unpaid",
                        "pending",
                        "paid",
                        "failed",
                        "refunded",
                    ]
                ),
                name="order_payment_status_valid",
            ),
        ),
    ]
```

인덱스는 조회 패턴이 있을 때만 추가하세요. `payment_status` 단독 인덱스는 값 종류가 적어서 효과가 제한적일 수 있습니다. 예를 들어 “최근 미결제 주문 목록”을 자주 조회한다면 단독 인덱스보다 `(payment_status, created_at)` 복합 인덱스가 더 적합할 수 있습니다.

배포 전에는 반드시 실제 SQL과 계획을 확인합니다.

```bash
python manage.py makemigrations
python manage.py sqlmigrate orders 0002
python manage.py sqlmigrate orders 0003
python manage.py sqlmigrate orders 0004
python manage.py migrate --plan
python manage.py migrate
```

운영 배포 순서는 보통 이렇게 잡습니다.

```text
배포 1: nullable 컬럼 추가
배포 2: 애플리케이션에서 payment_status 쓰기 시작
배포 3: 기존 데이터 백필
배포 4: null 값 0건 확인
배포 5: NOT NULL, default, CheckConstraint, 필요한 인덱스 추가
```

핵심 체크리스트는 이렇습니다.

- `BooleanField` 여러 개 대신 `TextChoices` 기반 단일 상태 컬럼 사용
- 기존 코드와 신코드가 동시에 떠 있어도 실패하지 않도록 처음엔 `null=True`
- 백필은 별도 migration 또는 배치로 분리
- `sqlmigrate`로 DDL 확인
- 대형 테이블은 락 시간과 인덱스 생성 방식을 별도 검토
- 결제 상태별 조회가 실제로 많을 때만 워크로드 기반 인덱스 추가
- 최종 단계에서 `NOT NULL`과 `CheckConstraint`로 데이터 무결성 고정

---
> **관련 스킬 참조:**
> - Django 마이그레이션 구현 → **implementation-django** 스킬
> - 컬럼/인덱스/제약조건 설계 → **architecture-db** 스킬