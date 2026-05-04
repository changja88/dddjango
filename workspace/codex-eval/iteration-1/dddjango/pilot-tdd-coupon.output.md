읽기 전용/빈 워크스페이스라 파일 생성, 수정, `pytest` 실행은 하지 못했습니다. 루트에 `config.toml`도 없어서 기존 Django 프로젝트 구조를 확인할 수 없었습니다. 아래는 `coupons` 앱을 추가한다는 가정의 TDD 산출물입니다. API는 프로젝트 정책대로 DRF 없이 Django Ninja `Schema`/`Router`로 작성합니다.

**RED**

`tests/isolated/coupons/test_apply_coupon.py`

```python
import pytest

from coupons.domain import CouponNotApplicableError
from coupons.services import apply_coupon


@pytest.mark.django_db
def test_apply_coupon_valid_percent_coupon_returns_discounted_total(coupon):
    # Arrange
    order_total = 10000

    # Act
    result = apply_coupon(code=coupon.code, order_total=order_total)

    # Assert
    assert result.original_total == 10000
    assert result.discount_amount == 1000
    assert result.payable_total == 9000
    assert result.coupon_code == coupon.code


@pytest.mark.django_db
def test_apply_coupon_expired_coupon_raises_not_applicable_error(expired_coupon):
    # Arrange
    order_total = 10000

    # Act / Assert
    with pytest.raises(CouponNotApplicableError, match="expired"):
        apply_coupon(code=expired_coupon.code, order_total=order_total)


@pytest.mark.django_db
def test_apply_coupon_below_minimum_order_total_raises_not_applicable_error(coupon):
    # Arrange
    order_total = 4999

    # Act / Assert
    with pytest.raises(CouponNotApplicableError, match="minimum"):
        apply_coupon(code=coupon.code, order_total=order_total)
```

예상 실패: `coupons` 앱, `Coupon` 모델, `apply_coupon`, 도메인 예외, fixture가 아직 없으므로 `ModuleNotFoundError` 또는 import 실패가 먼저 납니다.

**GREEN**

`coupons/domain.py`

```python
from dataclasses import dataclass


class CouponNotApplicableError(Exception):
    pass


@dataclass(frozen=True)
class ApplyCouponResult:
    original_total: int
    discount_amount: int
    payable_total: int
    coupon_code: str
```

`coupons/models.py`

```python
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Coupon(models.Model):
    """Aggregate Root: 쿠폰 적용 가능 여부와 할인 금액 불변식을 보호한다."""

    class DiscountType(models.TextChoices):
        PERCENT = "percent", "Percent"
        FIXED = "fixed", "Fixed"

    code = models.CharField(max_length=40, unique=True)
    discount_type = models.CharField(max_length=16, choices=DiscountType.choices)
    discount_value = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    minimum_order_total = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [models.Index(fields=["code"])]
        ordering = ["code"]

    def __str__(self) -> str:
        return self.code

    def can_apply_to(self, order_total: int) -> bool:
        return (
            self.is_active
            and self.expires_at > timezone.now()
            and order_total >= self.minimum_order_total
        )

    def calculate_discount(self, order_total: int) -> int:
        if self.discount_type == self.DiscountType.PERCENT:
            return min(order_total, order_total * self.discount_value // 100)
        return min(order_total, self.discount_value)
```

`coupons/repositories.py`

```python
from abc import ABC, abstractmethod

from .models import Coupon


class CouponRepository(ABC):
    @abstractmethod
    def find_active_by_code(self, code: str) -> Coupon | None:
        raise NotImplementedError


class DjangoCouponRepository(CouponRepository):
    def find_active_by_code(self, code: str) -> Coupon | None:
        return Coupon.objects.filter(code=code, is_active=True).first()
```

`coupons/services.py`

```python
from .domain import ApplyCouponResult, CouponNotApplicableError
from .repositories import CouponRepository, DjangoCouponRepository


def apply_coupon(
    *,
    code: str,
    order_total: int,
    repository: CouponRepository | None = None,
) -> ApplyCouponResult:
    repository = repository or DjangoCouponRepository()
    coupon = repository.find_active_by_code(code)

    if coupon is None:
        raise CouponNotApplicableError("coupon not found")

    if coupon.expires_at <= coupon._meta.get_field("expires_at").model.objects.get(pk=coupon.pk).expires_at.__class__.now():
        raise CouponNotApplicableError("coupon expired")

    if order_total < coupon.minimum_order_total:
        raise CouponNotApplicableError("minimum order total not satisfied")

    discount_amount = coupon.calculate_discount(order_total)

    return ApplyCouponResult(
        original_total=order_total,
        discount_amount=discount_amount,
        payable_total=order_total - discount_amount,
        coupon_code=coupon.code,
    )
```

위 `expires_at` 검사는 더럽습니다. Green 단계의 “일단 통과” 코드로 두고, 바로 Refactor에서 모델 메서드로 정리합니다.

**REFACTOR**

`coupons/services.py`를 아래처럼 정리합니다.

```python
from .domain import ApplyCouponResult, CouponNotApplicableError
from .repositories import CouponRepository, DjangoCouponRepository


def apply_coupon(
    *,
    code: str,
    order_total: int,
    repository: CouponRepository | None = None,
) -> ApplyCouponResult:
    repository = repository or DjangoCouponRepository()
    coupon = repository.find_active_by_code(code)

    if coupon is None:
        raise CouponNotApplicableError("coupon not found")

    if not coupon.can_apply_to(order_total):
        if order_total < coupon.minimum_order_total:
            raise CouponNotApplicableError("minimum order total not satisfied")
        raise CouponNotApplicableError("coupon expired")

    discount_amount = coupon.calculate_discount(order_total)

    return ApplyCouponResult(
        original_total=order_total,
        discount_amount=discount_amount,
        payable_total=order_total - discount_amount,
        coupon_code=coupon.code,
    )
```

`coupons/api.py`

```python
from ninja import Router, Schema
from ninja.security import django_auth

from .domain import CouponNotApplicableError
from .services import apply_coupon

router = Router(tags=["coupons"])


class ApplyCouponIn(Schema):
    code: str
    order_total: int


class ApplyCouponOut(Schema):
    original_total: int
    discount_amount: int
    payable_total: int
    coupon_code: str


class ProblemDetail(Schema):
    type: str
    title: str
    status: int
    detail: str


@router.post("/apply", response={200: ApplyCouponOut, 400: ProblemDetail}, auth=django_auth)
def apply_coupon_api(request, payload: ApplyCouponIn) -> tuple[int, ApplyCouponOut | ProblemDetail]:
    try:
        return 200, apply_coupon(code=payload.code, order_total=payload.order_total)
    except CouponNotApplicableError as exc:
        return 400, ProblemDetail(
            type="https://example.com/problems/coupon-not-applicable",
            title="Coupon not applicable",
            status=400,
            detail=str(exc),
        )
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

from .api import api

urlpatterns = [
    path("api/", api.urls),
]
```

실행 명령:

```bash
python manage.py makemigrations coupons
python manage.py migrate
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/coupons/test_apply_coupon.py -q
```

리팩터링 후 추가할 테스트는 고정 금액 쿠폰, 할인액이 주문 금액을 초과하는 경우, 비활성 쿠폰, 존재하지 않는 코드, 0원/음수 주문 금액 경계값입니다. `conftest.py`에는 `coupon`, `expired_coupon` fixture를 function scope로 두고, isolated settings에서 locmem cache/email과 테스트 DB를 사용하세요.

---
> **관련 스킬 참조:**
> - Django API 구현 → **implementation-django-ninja** 스킬