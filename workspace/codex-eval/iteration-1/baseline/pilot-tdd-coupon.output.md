현재 `/private/tmp/dddjango-codex-eval`은 비어 있고 `manage.py`, Django 앱, `config.toml`이 없습니다. 또한 세션이 `read-only`라 파일 생성/수정과 `pytest` 실행을 할 수 없습니다. 그래서 실제 적용은 못 했고, 아래처럼 TDD 순서로 바로 넣을 수 있는 최소 구현안을 정리합니다.

**RED: 실패 테스트 먼저**

`tests/isolated/unit/coupons/test_apply_coupon.py`

```python
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.coupons.models import Coupon
from apps.coupons.services import CouponNotApplicable, apply_coupon


@pytest.mark.django_db
def test_apply_coupon_active_fixed_coupon_discounts_subtotal():
    # Arrange
    Coupon.objects.create(
        code="WELCOME10",
        discount_type=Coupon.DiscountType.FIXED,
        value=Decimal("10.00"),
        active=True,
    )

    # Act
    result = apply_coupon(code="welcome10", subtotal=Decimal("50.00"))

    # Assert
    assert result.discount_amount == Decimal("10.00")
    assert result.payable_amount == Decimal("40.00")


@pytest.mark.django_db
def test_apply_coupon_percent_coupon_discounts_by_rate():
    # Arrange
    Coupon.objects.create(
        code="SAVE20",
        discount_type=Coupon.DiscountType.PERCENT,
        value=Decimal("20.00"),
        active=True,
    )

    # Act
    result = apply_coupon(code="SAVE20", subtotal=Decimal("100.00"))

    # Assert
    assert result.discount_amount == Decimal("20.00")
    assert result.payable_amount == Decimal("80.00")


@pytest.mark.django_db
def test_apply_coupon_expired_coupon_raises_not_applicable():
    # Arrange
    Coupon.objects.create(
        code="OLD",
        discount_type=Coupon.DiscountType.FIXED,
        value=Decimal("5.00"),
        active=True,
        valid_until=timezone.now() - timezone.timedelta(days=1),
    )

    # Act / Assert
    with pytest.raises(CouponNotApplicable):
        apply_coupon(code="OLD", subtotal=Decimal("30.00"))
```

이 시점에서는 `apps.coupons`가 없으므로 테스트가 실패합니다.

**GREEN: 통과에 필요한 최소 구현**

`apps/coupons/models.py`

```python
from django.db import models
from django.utils import timezone


class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        FIXED = "fixed", "Fixed"
        PERCENT = "percent", "Percent"

    code = models.CharField(max_length=32, unique=True)
    discount_type = models.CharField(max_length=10, choices=DiscountType.choices)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["code", "active"])]

    def __str__(self):
        return self.code

    def is_applicable_at(self, now=None):
        now = now or timezone.now()
        if not self.active:
            return False
        if self.valid_from and self.valid_from > now:
            return False
        if self.valid_until and self.valid_until < now:
            return False
        return True
```

`apps/coupons/services.py`

```python
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from django.utils import timezone

from apps.coupons.models import Coupon


class CouponNotApplicable(Exception):
    pass


@dataclass(frozen=True)
class CouponApplicationResult:
    coupon: Coupon
    discount_amount: Decimal
    payable_amount: Decimal


def apply_coupon(*, code: str, subtotal: Decimal, now=None) -> CouponApplicationResult:
    now = now or timezone.now()

    try:
        coupon = Coupon.objects.get(code__iexact=code.strip())
    except Coupon.DoesNotExist as exc:
        raise CouponNotApplicable("Coupon does not exist.") from exc

    if not coupon.is_applicable_at(now):
        raise CouponNotApplicable("Coupon is not applicable.")

    discount_amount = _calculate_discount(coupon, subtotal)
    payable_amount = max(subtotal - discount_amount, Decimal("0.00"))

    return CouponApplicationResult(
        coupon=coupon,
        discount_amount=discount_amount,
        payable_amount=payable_amount,
    )


def _calculate_discount(coupon: Coupon, subtotal: Decimal) -> Decimal:
    if coupon.discount_type == Coupon.DiscountType.FIXED:
        amount = min(coupon.value, subtotal)
    else:
        amount = subtotal * coupon.value / Decimal("100")

    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

**REFACTOR: 그린 상태에서 정리**

리팩터링 포인트는 세 가지입니다.

1. 쿠폰 적용 결과를 `dict` 대신 `CouponApplicationResult`로 명시했습니다.
2. 만료/활성 검증은 모델의 `is_applicable_at()`로 이동해 도메인 규칙을 모델 가까이에 뒀습니다.
3. 할인 계산은 `_calculate_discount()`로 분리해 고정 금액/퍼센트 정책 추가가 쉬워졌습니다.

실제 프로젝트가 연결되면 다음 순서로 실행하면 됩니다.

```bash
python manage.py makemigrations coupons
python manage.py migrate
pytest tests/isolated/unit/coupons/test_apply_coupon.py
```

현재 환경에서는 프로젝트 파일이 없어 `pytest`를 실행하지 못했습니다.

---
> **관련 스킬 참조:**
> - pytest 테스트 작성 → **implementation-test** 스킬
> - Red-Green-Refactor 진행 → **implementation-tdd** 스킬
> - Django 모델/서비스 레이어 → **implementation-django** 스킬