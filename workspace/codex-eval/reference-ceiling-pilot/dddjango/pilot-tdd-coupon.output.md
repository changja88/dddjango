현재 `/private/tmp/dddjango-codex-eval` workspace는 비어 있고, 세션 권한이 read-only라 파일 생성/수정과 pytest 실행을 실제로 수행할 수 없었습니다. 그래서 실행했다고 주장하지 않고, 바로 옮겨 붙일 수 있는 **RED 테스트 → 예상 실패 → GREEN 구현 → Django Ninja API hook → REFACTOR 메모 → 실행 명령** 형태로 제공합니다.

**RED**

`tests/isolated/unit/test_coupon_application.py`

```python
from datetime import date, timedelta
from decimal import Decimal

import pytest

from apps.coupons.domain import CouponPolicy, DiscountType
from apps.coupons.services import CouponApplicationError, apply_coupon


def test_apply_coupon_percent_coupon_returns_discounted_total():
    # Arrange
    coupon = CouponPolicy(
        code="WELCOME10",
        discount_type=DiscountType.PERCENT,
        discount_value=Decimal("10"),
        min_order_amount=Decimal("30000"),
        starts_on=date.today() - timedelta(days=1),
        ends_on=date.today() + timedelta(days=1),
        is_active=True,
    )

    # Act
    result = apply_coupon(coupon=coupon, order_amount=Decimal("50000"), today=date.today())

    # Assert
    assert result.code == "WELCOME10"
    assert result.discount_amount == Decimal("5000")
    assert result.final_amount == Decimal("45000")


def test_apply_coupon_fixed_coupon_never_makes_final_amount_negative():
    # Arrange
    coupon = CouponPolicy(
        code="BIGSAVE",
        discount_type=DiscountType.FIXED,
        discount_value=Decimal("20000"),
        min_order_amount=Decimal("0"),
        starts_on=date.today() - timedelta(days=1),
        ends_on=date.today() + timedelta(days=1),
        is_active=True,
    )

    # Act
    result = apply_coupon(coupon=coupon, order_amount=Decimal("12000"), today=date.today())

    # Assert
    assert result.discount_amount == Decimal("12000")
    assert result.final_amount == Decimal("0")


def test_apply_coupon_below_min_order_amount_raises_error():
    # Arrange
    coupon = CouponPolicy(
        code="WELCOME10",
        discount_type=DiscountType.PERCENT,
        discount_value=Decimal("10"),
        min_order_amount=Decimal("30000"),
        starts_on=date.today() - timedelta(days=1),
        ends_on=date.today() + timedelta(days=1),
        is_active=True,
    )

    # Act / Assert
    with pytest.raises(CouponApplicationError, match="minimum order amount"):
        apply_coupon(coupon=coupon, order_amount=Decimal("20000"), today=date.today())


def test_apply_coupon_expired_coupon_raises_error():
    # Arrange
    coupon = CouponPolicy(
        code="OLD10",
        discount_type=DiscountType.PERCENT,
        discount_value=Decimal("10"),
        min_order_amount=Decimal("0"),
        starts_on=date.today() - timedelta(days=10),
        ends_on=date.today() - timedelta(days=1),
        is_active=True,
    )

    # Act / Assert
    with pytest.raises(CouponApplicationError, match="expired"):
        apply_coupon(coupon=coupon, order_amount=Decimal("50000"), today=date.today())
```

예상 RED 실패:

```text
ModuleNotFoundError: No module named 'apps'
```

또는 앱이 이미 있다면:

```text
ImportError: cannot import name 'CouponPolicy'
ImportError: cannot import name 'apply_coupon'
```

**GREEN**

`apps/coupons/domain.py`

```python
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum


class DiscountType(StrEnum):
    FIXED = "fixed"
    PERCENT = "percent"


@dataclass(frozen=True)
class CouponPolicy:
    """
    Coupon aggregate root.

    Invariants:
    - code must not be blank
    - discount_value must be positive
    - min_order_amount must not be negative
    - starts_on must not be after ends_on
    - percent discount cannot exceed 100
    """

    code: str
    discount_type: DiscountType
    discount_value: Decimal
    min_order_amount: Decimal
    starts_on: date
    ends_on: date
    is_active: bool

    def __post_init__(self) -> None:
        if not self.code.strip():
            raise ValueError("coupon code is required")
        if self.discount_value <= Decimal("0"):
            raise ValueError("discount value must be positive")
        if self.min_order_amount < Decimal("0"):
            raise ValueError("minimum order amount must not be negative")
        if self.starts_on > self.ends_on:
            raise ValueError("coupon period is invalid")
        if (
            self.discount_type == DiscountType.PERCENT
            and self.discount_value > Decimal("100")
        ):
            raise ValueError("percent discount cannot exceed 100")
```

`apps/coupons/services.py`

```python
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_DOWN

from apps.coupons.domain import CouponPolicy, DiscountType


class CouponApplicationError(Exception):
    pass


@dataclass(frozen=True)
class CouponApplicationResult:
    code: str
    order_amount: Decimal
    discount_amount: Decimal
    final_amount: Decimal


def apply_coupon(
    *,
    coupon: CouponPolicy,
    order_amount: Decimal,
    today: date,
) -> CouponApplicationResult:
    if order_amount < Decimal("0"):
        raise CouponApplicationError("order amount must not be negative")
    if not coupon.is_active:
        raise CouponApplicationError("coupon is inactive")
    if today < coupon.starts_on:
        raise CouponApplicationError("coupon is not started")
    if today > coupon.ends_on:
        raise CouponApplicationError("coupon is expired")
    if order_amount < coupon.min_order_amount:
        raise CouponApplicationError("minimum order amount is not met")

    discount_amount = _calculate_discount_amount(coupon, order_amount)
    final_amount = order_amount - discount_amount

    return CouponApplicationResult(
        code=coupon.code,
        order_amount=order_amount,
        discount_amount=discount_amount,
        final_amount=final_amount,
    )


def _calculate_discount_amount(
    coupon: CouponPolicy,
    order_amount: Decimal,
) -> Decimal:
    if coupon.discount_type == DiscountType.FIXED:
        return min(coupon.discount_value, order_amount)

    discount_amount = order_amount * coupon.discount_value / Decimal("100")
    return discount_amount.quantize(Decimal("1"), rounding=ROUND_DOWN)
```

**Django Model 예시**

`apps/coupons/models.py`

```python
from django.db import models


class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        FIXED = "fixed", "Fixed"
        PERCENT = "percent", "Percent"

    code = models.CharField(max_length=40, unique=True)
    discount_type = models.CharField(max_length=10, choices=DiscountType.choices)
    discount_value = models.DecimalField(max_digits=12, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    starts_on = models.DateField()
    ends_on = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active", "starts_on", "ends_on"]),
        ]

    def __str__(self) -> str:
        return self.code
```

`apps/coupons/selectors.py`

```python
from apps.coupons.models import Coupon


def coupon_get_by_code(*, code: str) -> Coupon:
    return Coupon.objects.get(code=code)
```

`apps/coupons/use_cases.py`

```python
from datetime import date
from decimal import Decimal

from apps.coupons.domain import CouponPolicy, DiscountType
from apps.coupons.models import Coupon
from apps.coupons.selectors import coupon_get_by_code
from apps.coupons.services import CouponApplicationResult, apply_coupon


def coupon_apply_by_code(
    *,
    code: str,
    order_amount: Decimal,
    today: date,
) -> CouponApplicationResult:
    coupon = coupon_get_by_code(code=code)

    policy = CouponPolicy(
        code=coupon.code,
        discount_type=DiscountType(coupon.discount_type),
        discount_value=coupon.discount_value,
        min_order_amount=coupon.min_order_amount,
        starts_on=coupon.starts_on,
        ends_on=coupon.ends_on,
        is_active=coupon.is_active,
    )

    return apply_coupon(coupon=policy, order_amount=order_amount, today=today)
```

**Django Ninja API hook**

`apps/coupons/api/schemas.py`

```python
from decimal import Decimal

from ninja import Schema


class CouponApplyIn(Schema):
    code: str
    order_amount: Decimal


class CouponApplyOut(Schema):
    code: str
    order_amount: Decimal
    discount_amount: Decimal
    final_amount: Decimal


class ProblemDetailOut(Schema):
    type: str
    title: str
    status: int
    detail: str
```

`apps/coupons/api/router.py`

```python
from datetime import date

from django.http import HttpRequest
from ninja import Router

from apps.coupons.api.schemas import CouponApplyIn, CouponApplyOut, ProblemDetailOut
from apps.coupons.services import CouponApplicationError
from apps.coupons.use_cases import coupon_apply_by_code

router = Router(tags=["coupons"])


@router.post(
    "/apply",
    response={200: CouponApplyOut, 400: ProblemDetailOut},
)
def apply_coupon_endpoint(
    request: HttpRequest,
    payload: CouponApplyIn,
) -> tuple[int, CouponApplyOut] | tuple[int, ProblemDetailOut]:
    try:
        result = coupon_apply_by_code(
            code=payload.code,
            order_amount=payload.order_amount,
            today=date.today(),
        )
    except CouponApplicationError as exc:
        return 400, ProblemDetailOut(
            type="https://example.com/problems/coupon-application-failed",
            title="Coupon application failed",
            status=400,
            detail=str(exc),
        )

    return 200, CouponApplyOut(
        code=result.code,
        order_amount=result.order_amount,
        discount_amount=result.discount_amount,
        final_amount=result.final_amount,
    )
```

`config/api.py`

```python
from ninja import NinjaAPI

from apps.coupons.api.router import router as coupons_router

api = NinjaAPI()

api.add_router("/coupons/", coupons_router)
```

`config/urls.py`

```python
from django.contrib import admin
from django.urls import path

from config.api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
```

**REFACTOR**

Green 이후 정리 방향은 이 정도가 적절합니다.

- `CouponPolicy`는 쿠폰 적용 불변식을 가진 Aggregate Root로 유지합니다.
- 금액 계산은 `Decimal`만 사용하고 float는 금지합니다.
- `CouponApplicationResult`처럼 명시적 결과 타입을 유지해 tuple/dict 반환을 피합니다.
- DB 조회는 `selectors.py`, 유스케이스 조율은 `use_cases.py`, 순수 도메인 계산은 `services.py`로 분리합니다.
- API는 DRF 미사용, Django Ninja `Schema`/`Router`만 사용합니다.
- sync endpoint는 `request: HttpRequest`와 명시적 반환 타입을 포함합니다.
- 목록 API가 필요해지면 `response=list[CouponApplyOut]`처럼 `list[Schema]`를 사용하고 `from typing import list`는 쓰지 않습니다.

**실행 명령**

실제 프로젝트에 파일을 추가한 뒤 아래 순서로 확인하세요.

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/unit/test_coupon_application.py -q
```

RED 단계에서는 위 테스트가 import 실패 또는 미구현 실패로 깨져야 합니다.

GREEN 구현 후:

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/unit/test_coupon_application.py -q
python manage.py makemigrations coupons
python manage.py check
pytest -q
```

API까지 확인하려면 Django Ninja endpoint 테스트를 추가합니다.

`tests/isolated/integration/test_coupon_api.py`

```python
from datetime import date, timedelta
from decimal import Decimal

import pytest
from ninja.testing import TestClient

from apps.coupons.api.router import router
from apps.coupons.models import Coupon


@pytest.mark.django_db
def test_apply_coupon_endpoint_returns_discounted_total():
    # Arrange
    Coupon.objects.create(
        code="WELCOME10",
        discount_type=Coupon.DiscountType.PERCENT,
        discount_value=Decimal("10"),
        min_order_amount=Decimal("30000"),
        starts_on=date.today() - timedelta(days=1),
        ends_on=date.today() + timedelta(days=1),
        is_active=True,
    )
    client = TestClient(router)

    # Act
    response = client.post(
        "/apply",
        json={"code": "WELCOME10", "order_amount": "50000"},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "code": "WELCOME10",
        "order_amount": "50000",
        "discount_amount": "5000",
        "final_amount": "45000",
    }
```

---
> **관련 스킬 참조:**
> - Django API 구현 → **implementation-django-ninja** 스킬
> - Django 테스트 구조 → **implementation-test** 스킬