**주요 내용**

현재 `/private/tmp/dddjango-codex-eval`은 빈 디렉터리이고 sandbox가 읽기 전용이라 파일 생성, 수정, `pytest` 실행은 불가능했습니다. 따라서 실행했다고 주장하지 않고, Django 프로젝트에 바로 추가할 수 있는 RED 테스트와 GREEN 최소 구현을 제시합니다.

**RED: 실패 테스트**

`tests/isolated/unit/test_coupon_application.py`

```python
from decimal import Decimal

import pytest
from django.utils import timezone

from coupons.models import Coupon, CouponRedemption
from coupons.services import CouponNotApplicable, apply_coupon


@pytest.mark.django_db
def test_apply_coupon_valid_percentage_creates_discounted_total_and_redemption(django_user_model):
    # Arrange
    user = django_user_model.objects.create_user(username="buyer")
    coupon = Coupon.objects.create(
        code="SAVE10",
        discount_percent=Decimal("10.00"),
        starts_at=timezone.now() - timezone.timedelta(days=1),
        ends_at=timezone.now() + timezone.timedelta(days=1),
        is_active=True,
    )

    # Act
    result = apply_coupon(user=user, code="SAVE10", subtotal=Decimal("100.00"))

    # Assert
    assert result.discount == Decimal("10.00")
    assert result.total == Decimal("90.00")
    assert CouponRedemption.objects.filter(user=user, coupon=coupon).exists()


@pytest.mark.django_db
def test_apply_coupon_expired_coupon_raises_coupon_not_applicable(django_user_model):
    # Arrange
    user = django_user_model.objects.create_user(username="buyer")
    Coupon.objects.create(
        code="OLD10",
        discount_percent=Decimal("10.00"),
        starts_at=timezone.now() - timezone.timedelta(days=10),
        ends_at=timezone.now() - timezone.timedelta(days=1),
        is_active=True,
    )

    # Act / Assert
    with pytest.raises(CouponNotApplicable):
        apply_coupon(user=user, code="OLD10", subtotal=Decimal("100.00"))
```

예상 실패 이유: `coupons` 앱, `Coupon`, `CouponRedemption`, `apply_coupon`, `CouponNotApplicable`가 아직 없으므로 import 단계에서 실패해야 합니다.

**GREEN: 최소 구현**

`coupons/models.py`

```python
from django.conf import settings
from django.db import models


class Coupon(models.Model):
    code = models.CharField(max_length=40, unique=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    max_redemptions = models.PositiveIntegerField(null=True, blank=True)

    def is_usable_at(self, now):
        return self.is_active and self.starts_at <= now <= self.ends_at


class CouponRedemption(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    redeemed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "coupon"],
                name="unique_coupon_redemption_per_user",
            )
        ]
```

`coupons/services.py`

```python
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.utils import timezone

from .models import Coupon, CouponRedemption


class CouponNotApplicable(Exception):
    pass


@dataclass(frozen=True)
class CouponApplicationResult:
    discount: Decimal
    total: Decimal


@transaction.atomic
def apply_coupon(*, user, code: str, subtotal: Decimal) -> CouponApplicationResult:
    now = timezone.now()

    try:
        coupon = Coupon.objects.select_for_update().get(code=code)
    except Coupon.DoesNotExist as exc:
        raise CouponNotApplicable("coupon does not exist") from exc

    if not coupon.is_usable_at(now):
        raise CouponNotApplicable("coupon is not active")

    if CouponRedemption.objects.filter(user=user, coupon=coupon).exists():
        raise CouponNotApplicable("coupon already redeemed")

    if coupon.max_redemptions is not None:
        used = CouponRedemption.objects.filter(coupon=coupon).count()
        if used >= coupon.max_redemptions:
            raise CouponNotApplicable("coupon redemption limit reached")

    discount = (subtotal * coupon.discount_percent / Decimal("100")).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )
    total = max(Decimal("0.00"), subtotal - discount)

    CouponRedemption.objects.create(user=user, coupon=coupon)

    return CouponApplicationResult(discount=discount, total=total)
```

필요한 Django 작업: `INSTALLED_APPS`에 `coupons` 추가 후 migration 생성.

```bash
python manage.py makemigrations coupons
python manage.py migrate
```

**REFACTOR 방향**

다음 단계에서는 `max_redemptions`, 중복 사용, 비활성 쿠폰, 존재하지 않는 코드, 할인액이 주문 금액을 초과하는 케이스를 `pytest.mark.parametrize`로 늘리면 됩니다. 주문 모델이 있다면 `apply_coupon`의 입력을 `subtotal` 대신 `order`로 바꾸기 전에 현재 테스트를 먼저 GREEN으로 유지하는 것이 좋습니다.

**검증 명령**

읽기 전용이라 실행하지 못했습니다. 실제 프로젝트에서는 다음 순서로 확인하세요.

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/unit/test_coupon_application.py -q
pytest tests/isolated -q
```

---
> **관련 스킬 참조:**
> - Django pytest/TDD 구현 → **implementation-tdd** 스킬
> - pytest fixture와 isolated 테스트 구조 → **implementation-test** 스킬