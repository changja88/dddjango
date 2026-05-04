읽기 전용/빈 워크스페이스라 파일 생성, 수정, pytest 실행은 하지 못했습니다. 아래는 Django 프로젝트에 그대로 옮길 수 있는 TDD 산출물입니다. RED 테스트가 먼저이며, 현재 상태에서는 `coupons` 앱/모델/서비스가 없어서 실패해야 정상입니다.

**RED 테스트**

`tests/isolated/unit/coupons/test_apply_coupon.py`

```python
from decimal import Decimal

import pytest
from django.utils import timezone

from coupons.models import Coupon
from coupons.services import CouponNotApplicable, apply_coupon


@pytest.mark.django_db
def test_apply_coupon_valid_percent_coupon_returns_discounted_total():
    # Arrange
    coupon = Coupon.objects.create(
        code="SAVE10",
        discount_type=Coupon.DiscountType.PERCENT,
        amount=Decimal("10.00"),
        active=True,
        starts_at=timezone.now() - timezone.timedelta(days=1),
        ends_at=timezone.now() + timezone.timedelta(days=1),
        minimum_order_amount=Decimal("0.00"),
    )

    # Act
    result = apply_coupon(subtotal=Decimal("100.00"), code="SAVE10")

    # Assert
    assert result.coupon == coupon
    assert result.discount_amount == Decimal("10.00")
    assert result.total == Decimal("90.00")


@pytest.mark.django_db
def test_apply_coupon_below_minimum_order_amount_raises_not_applicable():
    # Arrange
    Coupon.objects.create(
        code="SAVE20",
        discount_type=Coupon.DiscountType.FIXED,
        amount=Decimal("20.00"),
        active=True,
        starts_at=timezone.now() - timezone.timedelta(days=1),
        ends_at=timezone.now() + timezone.timedelta(days=1),
        minimum_order_amount=Decimal("100.00"),
    )

    # Act / Assert
    with pytest.raises(CouponNotApplicable):
        apply_coupon(subtotal=Decimal("50.00"), code="SAVE20")
```

**예상 실패**

처음 실행하면 `ModuleNotFoundError: No module named 'coupons'`, `ImportError`, 또는 `Coupon`/`apply_coupon` 미구현 오류로 실패해야 합니다. 이것이 RED 단계입니다.

**GREEN 최소 구현**

`coupons/models.py`

```python
from django.db import models


class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        PERCENT = "percent", "Percent"
        FIXED = "fixed", "Fixed"

    code = models.CharField(max_length=64, unique=True)
    discount_type = models.CharField(max_length=16, choices=DiscountType.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    minimum_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
```

`coupons/services.py`

```python
from dataclasses import dataclass
from decimal import Decimal

from django.utils import timezone

from coupons.models import Coupon


class CouponNotApplicable(Exception):
    pass


@dataclass(frozen=True)
class CouponApplicationResult:
    coupon: Coupon
    discount_amount: Decimal
    total: Decimal


def apply_coupon(*, subtotal: Decimal, code: str) -> CouponApplicationResult:
    now = timezone.now()

    try:
        coupon = Coupon.objects.get(code=code)
    except Coupon.DoesNotExist as exc:
        raise CouponNotApplicable from exc

    if not coupon.active:
        raise CouponNotApplicable

    if coupon.starts_at > now or coupon.ends_at < now:
        raise CouponNotApplicable

    if subtotal < coupon.minimum_order_amount:
        raise CouponNotApplicable

    if coupon.discount_type == Coupon.DiscountType.PERCENT:
        discount_amount = subtotal * coupon.amount / Decimal("100")
    else:
        discount_amount = coupon.amount

    discount_amount = min(discount_amount, subtotal).quantize(Decimal("0.01"))
    total = (subtotal - discount_amount).quantize(Decimal("0.01"))

    return CouponApplicationResult(
        coupon=coupon,
        discount_amount=discount_amount,
        total=total,
    )
```

**REFACTOR 방향**

그린 이후에만 `Coupon.is_applicable_to(subtotal, now)` 같은 도메인 메서드로 조건을 이동하고, 만료/비활성/없는 쿠폰 케이스를 별도 테스트로 추가하세요. 주문 모델이 있다면 `apply_coupon(order, code)`로 확장하되, 할인 계산과 주문 상태 변경은 테스트를 분리하는 편이 좋습니다.

**pytest 명령**

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/unit/coupons/test_apply_coupon.py -q
```

앱 생성 후에는 `INSTALLED_APPS`에 `coupons`를 추가하고 마이그레이션을 만든 뒤 실행하세요.

---
> **관련 스킬 참조:**
> - Django/pytest 테스트 확장 → **implementation-test** 스킬