현재 `/private/tmp/dddjango-codex-eval` 워크스페이스가 비어 있고, 세션이 `read-only`라 파일 생성/수정과 pytest 실행은 못 했습니다. 실행했다고 주장하지 않고, `coupons` 앱 기준으로 바로 적용 가능한 RED-GREEN-REFACTOR 산출물을 정리합니다.

**RED**

`tests/isolated/coupons/test_apply_coupon.py`

```python
from decimal import Decimal

import pytest
from django.utils import timezone

from coupons.models import Coupon
from coupons.services import CouponCannotBeApplied, apply_coupon


@pytest.mark.django_db
def test_apply_coupon_active_percent_coupon_returns_discounted_total():
    # Arrange
    coupon = Coupon.objects.create(
        code="SPRING10",
        discount_percent=10,
        is_active=True,
        starts_at=timezone.now() - timezone.timedelta(days=1),
        ends_at=timezone.now() + timezone.timedelta(days=1),
    )

    # Act
    result = apply_coupon(code=coupon.code, order_total=Decimal("50000"))

    # Assert
    assert result.coupon_code == "SPRING10"
    assert result.discount_amount == Decimal("5000")
    assert result.discounted_total == Decimal("45000")


@pytest.mark.django_db
def test_apply_coupon_inactive_coupon_raises_domain_error():
    # Arrange
    Coupon.objects.create(code="STOP10", discount_percent=10, is_active=False)

    # Act / Assert
    with pytest.raises(CouponCannotBeApplied, match="활성화되지 않은 쿠폰"):
        apply_coupon(code="STOP10", order_total=Decimal("50000"))
```

예상 실패:

```bash
pytest tests/isolated/coupons/test_apply_coupon.py -q
```

처음에는 `ModuleNotFoundError: No module named 'coupons'` 또는 `ImportError: cannot import name 'apply_coupon'`로 실패해야 정상입니다. 테스트가 아직 없는 서비스, 도메인 예외, 모델 동작을 요구하고 있기 때문입니다.

**GREEN**

`coupons/apps.py`

```python
from django.apps import AppConfig


class CouponsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "coupons"
```

`coupons/models.py`

```python
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Coupon(models.Model):
    """
    Aggregate Root.

    Invariants:
    - discount_percent is between 1 and 100.
    - an inactive coupon cannot be applied.
    - a coupon outside its validity window cannot be applied.
    - discount never makes the order total negative.
    """

    code = models.CharField(max_length=40, unique=True)
    discount_percent = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    is_active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["code"]
        indexes = [models.Index(fields=["code"])]

    def __str__(self) -> str:
        return self.code

    def clean(self) -> None:
        if self.starts_at and self.ends_at and self.starts_at >= self.ends_at:
            raise ValidationError("쿠폰 시작일은 종료일보다 빨라야 합니다.")

    def can_be_applied(self, now=None) -> bool:
        now = now or timezone.now()
        if not self.is_active:
            return False
        if self.starts_at and self.starts_at > now:
            return False
        if self.ends_at and self.ends_at < now:
            return False
        return True

    def calculate_discount_amount(self, order_total: Decimal) -> Decimal:
        discount = order_total * Decimal(self.discount_percent) / Decimal("100")
        return min(discount, order_total).quantize(Decimal("1"))
```

`coupons/services.py`

```python
from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from coupons.models import Coupon


class CouponCannotBeApplied(Exception):
    pass


@dataclass(frozen=True)
class CouponApplicationResult:
    coupon_code: str
    order_total: Decimal
    discount_amount: Decimal
    discounted_total: Decimal


def apply_coupon(*, code: str, order_total: Decimal) -> CouponApplicationResult:
    if order_total <= Decimal("0"):
        raise CouponCannotBeApplied("주문 금액은 0보다 커야 합니다.")

    with transaction.atomic():
        coupon = Coupon.objects.select_for_update().get(code=code)

        if not coupon.can_be_applied(now=timezone.now()):
            raise CouponCannotBeApplied("활성화되지 않은 쿠폰입니다.")

        discount_amount = coupon.calculate_discount_amount(order_total)
        discounted_total = order_total - discount_amount

    return CouponApplicationResult(
        coupon_code=coupon.code,
        order_total=order_total,
        discount_amount=discount_amount,
        discounted_total=discounted_total,
    )
```

`coupons/api.py`

```python
from decimal import Decimal

from django.http import HttpRequest
from ninja import Router, Schema
from ninja.errors import HttpError

from coupons.services import CouponCannotBeApplied, apply_coupon

router = Router(tags=["coupons"])


class ApplyCouponIn(Schema):
    code: str
    order_total: Decimal


class ApplyCouponOut(Schema):
    coupon_code: str
    order_total: Decimal
    discount_amount: Decimal
    discounted_total: Decimal


@router.post("/apply", response=ApplyCouponOut)
def apply_coupon_api(request: HttpRequest, payload: ApplyCouponIn) -> ApplyCouponOut:
    try:
        result = apply_coupon(code=payload.code, order_total=payload.order_total)
    except CouponCannotBeApplied as exc:
        raise HttpError(400, str(exc)) from exc
    except Coupon.DoesNotExist as exc:
        raise HttpError(404, "쿠폰을 찾을 수 없습니다.") from exc

    return ApplyCouponOut(
        coupon_code=result.coupon_code,
        order_total=result.order_total,
        discount_amount=result.discount_amount,
        discounted_total=result.discounted_total,
    )
```

위 `api.py`는 `Coupon.DoesNotExist`를 참조하므로 import가 하나 더 필요합니다:

```python
from coupons.models import Coupon
```

`config/api.py`

```python
from ninja import NinjaAPI

from coupons.api import router as coupons_router

api = NinjaAPI()
api.add_router("/coupons/", coupons_router)
```

`config/urls.py`

```python
from django.urls import path

from config.api import api

urlpatterns = [
    path("api/", api.urls),
]
```

**REFACTOR**

그린 이후에는 먼저 서비스의 책임을 안정화합니다. `apply_coupon()`은 유스케이스 조율만 맡고, 할인 계산과 적용 가능 여부는 `Coupon` aggregate root에 남겨 도메인 규칙이 API나 테스트로 새지 않게 둡니다.

다음 단계 리팩터링 후보는 이 정도가 적절합니다.

```python
@dataclass(frozen=True)
class Money:
    amount: Decimal

    def __post_init__(self) -> None:
        if self.amount < Decimal("0"):
            raise ValueError("금액은 음수일 수 없습니다.")
```

다만 현재 요구에서는 `Decimal`만으로 충분하므로, `Money` 값 객체는 금액 규칙이 여러 곳에서 반복되기 시작할 때 도입하는 편이 낫습니다. 지금은 성급한 추상화보다 `Coupon`과 `apply_coupon()`의 경계를 명확히 유지하는 것이 더 단순합니다.

**명령**

```bash
python manage.py makemigrations coupons
python manage.py migrate
pytest tests/isolated/coupons/test_apply_coupon.py -q
pytest -q
python manage.py check
```

Django Ninja API까지 확인하려면:

```bash
curl -X POST http://localhost:8000/api/coupons/apply \
  -H "Content-Type: application/json" \
  -d '{"code":"SPRING10","order_total":"50000"}'
```

---
> **관련 스킬 참조:**
> - Django 모델/API 구현 → **implementation-django**, **implementation-django-ninja** 스킬
> - pytest와 Red-Green-Refactor → **implementation-tdd**, **implementation-test** 스킬