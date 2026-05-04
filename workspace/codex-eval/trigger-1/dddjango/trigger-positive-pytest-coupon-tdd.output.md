**주요 내용**

실제 구현 파일 수정과 pytest 실행은 못 했습니다. 현재 `/private/tmp/dddjango-codex-eval`은 비어 있고 `config.toml`도 없으며, 세션이 read-only입니다. 그래서 실행했다고 주장하지 않고, 이 프로젝트의 `dddjango` 규칙에 맞춰 붙여 넣을 수 있는 TDD 산출물로 제공합니다. API는 DRF가 아니라 Django Ninja 기준입니다.

권장 설계는 `Coupon`을 쿠폰 규칙의 Aggregate Root로 두고, `coupon_apply()` 서비스가 `Order`와 `Coupon`을 `transaction.atomic()` + `select_for_update()`로 조율하는 방식입니다.

**RED**

`tests/isolated/integration/test_coupon_apply.py`

```python
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.coupons.exceptions import CouponMinimumOrderAmountNotMet
from apps.coupons.models import Coupon
from apps.coupons.services import coupon_apply
from apps.orders.models import Order

pytestmark = pytest.mark.django_db


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user("buyer@example.com")


def test_coupon_apply_valid_fixed_coupon_discounts_order_and_consumes_usage(user):
    now = timezone.now()
    order = Order.objects.create(
        user=user,
        subtotal=Decimal("30000.00"),
        discount_total=Decimal("0.00"),
        total=Decimal("30000.00"),
        status=Order.Status.DRAFT,
    )
    coupon = Coupon.objects.create(
        code="WELCOME5000",
        discount_type=Coupon.DiscountType.FIXED,
        amount=Decimal("5000.00"),
        minimum_order_amount=Decimal("10000.00"),
        valid_from=now,
        valid_until=now + timezone.timedelta(days=7),
        usage_limit=10,
    )

    result = coupon_apply(order_id=order.id, code=" welcome5000 ", user=user)

    order.refresh_from_db()
    coupon.refresh_from_db()
    assert result.discount_total == Decimal("5000.00")
    assert order.discount_total == Decimal("5000.00")
    assert order.total == Decimal("25000.00")
    assert order.applied_coupon == coupon
    assert coupon.used_count == 1


def test_coupon_apply_requires_minimum_order_amount(user):
    now = timezone.now()
    order = Order.objects.create(
        user=user,
        subtotal=Decimal("9000.00"),
        discount_total=Decimal("0.00"),
        total=Decimal("9000.00"),
        status=Order.Status.DRAFT,
    )
    Coupon.objects.create(
        code="MIN10000",
        discount_type=Coupon.DiscountType.FIXED,
        amount=Decimal("1000.00"),
        minimum_order_amount=Decimal("10000.00"),
        valid_from=now,
        valid_until=now + timezone.timedelta(days=7),
    )

    with pytest.raises(CouponMinimumOrderAmountNotMet):
        coupon_apply(order_id=order.id, code="MIN10000", user=user)
```

예상 RED 실패 이유: `apps.coupons` 앱, `Coupon` 모델, 쿠폰 예외, `coupon_apply()` 서비스, `Order.applied_coupon`/`discount_total` 필드가 아직 없어서 import 또는 ORM 필드 오류로 실패해야 합니다.

**GREEN**

`apps/coupons/exceptions.py`

```python
class CouponApplyError(Exception): ...


class CouponNotRedeemable(CouponApplyError): ...


class CouponMinimumOrderAmountNotMet(CouponNotRedeemable): ...


class CouponUsageLimitExceeded(CouponNotRedeemable): ...


class CouponApplyNotAllowed(CouponApplyError): ...
```

`apps/coupons/models.py`

```python
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        FIXED = "fixed", "Fixed"
        PERCENT = "percent", "Percent"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    code = models.CharField(max_length=40, unique=True)
    discount_type = models.CharField(max_length=10, choices=DiscountType)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=Status, default=Status.ACTIVE)

    class Meta:
        ordering = ["code"]
        indexes = [models.Index(fields=["code", "status"])]
        constraints = [
            models.CheckConstraint(check=Q(amount__gt=0), name="coupon_amount_positive"),
            models.CheckConstraint(check=Q(valid_until__gte=F("valid_from")), name="coupon_valid_range"),
            models.CheckConstraint(
                check=~Q(discount_type="percent") | Q(amount__lte=100),
                name="coupon_percent_lte_100",
            ),
            models.CheckConstraint(
                check=Q(usage_limit__isnull=True) | Q(used_count__lte=F("usage_limit")),
                name="coupon_usage_not_over_limit",
            ),
        ]

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        self.code = self.code.strip().upper()
        super().save(*args, **kwargs)

    def calculate_discount(self, subtotal):
        if self.discount_type == self.DiscountType.FIXED:
            return min(self.amount, subtotal).quantize(Decimal("0.01"))
        return min(subtotal * self.amount / Decimal("100"), subtotal).quantize(Decimal("0.01"))

    def validate_redeemable(self, subtotal, at=None):
        from apps.coupons.exceptions import (
            CouponMinimumOrderAmountNotMet,
            CouponNotRedeemable,
            CouponUsageLimitExceeded,
        )

        at = at or timezone.now()
        if self.status != self.Status.ACTIVE or not (self.valid_from <= at <= self.valid_until):
            raise CouponNotRedeemable("Coupon is not active.")
        if subtotal < self.minimum_order_amount:
            raise CouponMinimumOrderAmountNotMet("Order amount is below coupon minimum.")
        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            raise CouponUsageLimitExceeded("Coupon usage limit exceeded.")
```

`apps/orders/models.py`에 필요한 최소 필드/메서드:

```python
from decimal import Decimal

from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    applied_coupon = models.ForeignKey(
        "coupons.Coupon",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    status = models.CharField(max_length=12, choices=Status, default=Status.DRAFT)

    def apply_coupon(self, coupon, discount_total):
        self.applied_coupon = coupon
        self.discount_total = discount_total
        self.total = max(self.subtotal - discount_total, Decimal("0.00"))
```

`apps/coupons/services.py`

```python
from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.coupons.exceptions import CouponApplyNotAllowed
from apps.coupons.models import Coupon
from apps.orders.models import Order


@dataclass(frozen=True)
class CouponApplyResult:
    order_id: int
    code: str
    discount_total: Decimal
    total: Decimal


@transaction.atomic
def coupon_apply(*, order_id: int, code: str, user) -> CouponApplyResult:
    try:
        order = Order.objects.select_for_update().get(
            id=order_id,
            user=user,
            status=Order.Status.DRAFT,
        )
    except Order.DoesNotExist as exc:
        raise CouponApplyNotAllowed("Order cannot accept a coupon.") from exc

    if order.applied_coupon_id:
        raise CouponApplyNotAllowed("Order already has a coupon.")

    coupon = Coupon.objects.select_for_update().get(code=code.strip().upper())
    coupon.validate_redeemable(order.subtotal, timezone.now())

    discount_total = coupon.calculate_discount(order.subtotal)
    order.apply_coupon(coupon, discount_total)
    coupon.used_count += 1

    order.save(update_fields=["applied_coupon", "discount_total", "total"])
    coupon.save(update_fields=["used_count"])
    return CouponApplyResult(order.id, coupon.code, order.discount_total, order.total)
```

Django Ninja API가 필요하면 `apps/coupons/api.py`:

```python
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.security import SessionAuth

from apps.coupons.exceptions import CouponApplyError
from apps.coupons.services import coupon_apply

router = Router(auth=SessionAuth(), tags=["coupons"])


class CouponApplyIn(Schema):
    code: str


class CouponApplyOut(Schema):
    order_id: int
    code: str
    discount_total: str
    total: str


@router.post("/orders/{order_id}/coupon/", response=CouponApplyOut)
def apply_coupon(request, order_id: int, payload: CouponApplyIn) -> CouponApplyOut:
    try:
        result = coupon_apply(order_id=order_id, code=payload.code, user=request.auth)
    except CouponApplyError as exc:
        raise HttpError(400, str(exc)) from exc
    return CouponApplyOut(
        order_id=result.order_id,
        code=result.code,
        discount_total=str(result.discount_total),
        total=str(result.total),
    )
```

`config/api.py`에는 문자열 경로가 아니라 직접 import로 합성합니다.

```python
from ninja import NinjaAPI

from apps.coupons.api import router as coupons_router

api = NinjaAPI()
api.add_router("/coupons/", coupons_router)
```

**REFACTOR 방향**

다음 그린 바 이후에는 `CouponFactory`, `OrderFactory`를 `tests/isolated/conftest.py`로 빼고, 만료/비활성/사용량 초과/퍼센트 할인 경계값을 `parametrize`로 추가하세요. 시간 고정은 `time-machine`을 사용합니다. freezegun은 순수 Python 구현인 반면 time-machine은 C 확장으로 구현되어 있어 동일 작업에서 100~200배 빠르고, 시간 모킹이 많은 테스트 스위트에서 실질적인 실행 시간 차이가 납니다.

테스트 배치는 `tests/isolated/unit`, `tests/isolated/integration`, `tests/real/integration`처럼 1차 축을 실행 환경으로 유지하세요. `pyproject.toml`에는 `DJANGO_SETTINGS_MODULE = "config.settings.test"`와 `testpaths = ["tests/isolated", "tests/real"]`를 둡니다.

실행 명령:

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/integration/test_coupon_apply.py -q
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated -q
pip install pytest-randomly
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated --randomly-seed=last -q
```

---
> **관련 스킬 참조:**
> - Django 모델/서비스 구현 → **implementation-django** 스킬
> - pytest 테스트 구조 → **implementation-test** 스킬
> - Red-Green-Refactor → **implementation-tdd** 스킬
> - 쿠폰 도메인 경계와 Aggregate 설계 → **architecture-ddd** 스킬