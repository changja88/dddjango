**주요 내용**

핵심은 `Order.refunded_amount`를 “누적 환불 확정 또는 예약 금액”으로 두고, 환불 생성 시 `Order` 행을 잠근 뒤 같은 트랜잭션 안에서 중복 키와 잔액을 검사하는 구조입니다. `Refund`들의 합계를 매번 계산해서 막는 방식은 동시 요청에서 깨지기 쉽고, DB `CHECK`로도 “자식 row 합계 <= 부모 금액”은 직접 표현하기 어렵습니다.

```python
# orders/models.py
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, F


class Order(models.Model):
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2)
    refunded_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(paid_amount__gte=0),
                name="order_paid_amount_gte_0",
            ),
            models.CheckConstraint(
                condition=Q(refunded_amount__gte=0),
                name="order_refunded_amount_gte_0",
            ),
            models.CheckConstraint(
                condition=Q(refunded_amount__lte=F("paid_amount")),
                name="order_refunded_amount_lte_paid_amount",
            ),
        ]


class Refund(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"

    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="refunds")
    idempotency_key = models.CharField(max_length=80)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator("0.01")],
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="refund_amount_gt_0",
            ),
            models.UniqueConstraint(
                fields=["order", "idempotency_key"],
                name="uniq_refund_order_idempotency_key",
            ),
        ]
        indexes = [
            models.Index(fields=["order", "-created_at"], name="refund_order_created_idx"),
            models.Index(fields=["order", "status"], name="refund_order_status_idx"),
        ]
```

환불 생성은 서비스 함수로 고정합니다. 잔액 초과와 중복 요청은 애플리케이션 체크만 믿지 말고, `select_for_update()`와 DB unique/check constraint를 같이 사용합니다.

```python
# orders/services.py
from django.db import IntegrityError, transaction
from django.db.models import F

from .models import Order, Refund


class DuplicateRefundRequest(Exception):
    pass


class RefundAmountExceeded(Exception):
    pass


def refund_create(*, order_id: int, amount, idempotency_key: str, reason: str = ""):
    try:
        with transaction.atomic():
            order = (
                Order.objects
                .select_for_update()
                .get(id=order_id)
            )

            existing = Refund.objects.filter(
                order=order,
                idempotency_key=idempotency_key,
            ).first()
            if existing:
                raise DuplicateRefundRequest(existing.id)

            available = order.paid_amount - order.refunded_amount
            if amount > available:
                raise RefundAmountExceeded(
                    f"available={available}, requested={amount}"
                )

            refund = Refund.objects.create(
                order=order,
                amount=amount,
                idempotency_key=idempotency_key,
                reason=reason,
            )

            Order.objects.filter(id=order.id).update(
                refunded_amount=F("refunded_amount") + amount
            )

            return refund

    except IntegrityError as exc:
        raise DuplicateRefundRequest from exc
```

부분 환불은 자연스럽게 허용됩니다. 예를 들어 `paid_amount=10000`, `refunded_amount=3000`이면 다음 요청은 `7000`까지만 통과합니다. 동시에 두 요청이 들어와도 같은 `Order` row lock 때문에 두 번째 트랜잭션은 첫 번째 커밋 이후의 `refunded_amount`를 보고 다시 검증합니다.

외부 PG 환불 API가 있다면 DB 트랜잭션 안에서 호출하지 말고, 위 트랜잭션에서는 환불 금액을 “예약”한 뒤 `transaction.on_commit()`으로 워커 작업을 enqueue하세요. 실패 시 별도 보상 트랜잭션에서 `Refund.status=FAILED`로 바꾸고 `Order.refunded_amount`를 차감합니다.

조회 패턴과 인덱스 근거는 다음처럼 잡습니다.

```python
# orders/api/selectors.py
from .models import Refund


def refund_history_for_order(order_id: int):
    return (
        Refund.objects
        .filter(order_id=order_id)
        .order_by("-created_at")
    )


def active_refunds_for_order(order_id: int):
    return Refund.objects.filter(
        order_id=order_id,
        status__in=[Refund.Status.PENDING, Refund.Status.SUCCEEDED],
    )
```

`refund_order_created_idx(order, -created_at)`는 주문 상세의 환불 내역 조회를 인덱스 순서대로 처리하기 위한 것입니다. `refund_order_status_idx(order, status)`는 특정 주문의 진행 중/성공 환불만 확인하는 운영성 조회에 맞춘 인덱스입니다. `uniq_refund_order_idempotency_key`는 중복 요청 방지의 최종 방어선입니다.

검증 명령은 마이그레이션 생성 SQL과 실제 적용 가능성을 둘 다 확인합니다.

```bash
python manage.py makemigrations orders --check --dry-run
python manage.py makemigrations orders
python manage.py sqlmigrate orders 000X
python manage.py migrate --plan
python manage.py migrate
python manage.py test orders
```

PostgreSQL 기준으로는 `sqlmigrate`에서 `CHECK`, `UNIQUE`, `CREATE INDEX`가 의도대로 생성되는지 확인하고, 동시성 테스트는 `TransactionTestCase`에서 별도 DB connection/thread로 같은 주문에 환불 2건을 동시에 요청해 하나만 성공하는지 검증합니다.

---
> **관련 스킬 참조:**
> - API 엔드포인트 설계와 인증 적용 → **implementation-django-ninja** 스킬