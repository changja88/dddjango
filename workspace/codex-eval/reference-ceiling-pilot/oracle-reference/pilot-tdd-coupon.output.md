작업 디렉터리 `/private/tmp/dddjango-codex-eval`은 비어 있고 현재 세션은 read-only라 파일 생성과 pytest 실행은 못 했습니다. 아래는 그대로 붙여 넣어 적용할 수 있는 **RED → 예상 실패 → GREEN → REFACTOR** 순서의 최소 구현입니다. 정책상 API는 DRF가 아니라 **Django Ninja**로 작성합니다.

**도메인 경계**
| 용어 | 의미 | 금지 동의어 |
|---|---|---|
| `Coupon` | 할인 정책을 가진 Aggregate Root | discount row |
| `Money` | 금액 Value Object | raw decimal |
| `apply` | 주문 금액에 쿠폰을 적용한다 | calculate만 호출 |
| `CouponAppliedEvent` | 쿠폰 적용 완료 도메인 이벤트 | CouponApplyEvent |

Aggregate Root는 `Coupon`입니다. 보호할 불변식은 “비활성/기간 외/최소 주문금액 미달 쿠폰은 적용할 수 없고, 할인 후 금액은 0원 미만이 될 수 없다”입니다.

**RED: 실패 pytest 먼저**
`tests/isolated/unit/coupons/test_coupon_apply.py`

```python
from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.coupons.domain import (
    Coupon,
    CouponExpiredError,
    CouponNotApplicableError,
    DiscountType,
    Money,
)


def test_coupon_apply_fixed_discount_returns_discounted_total():
    # Arrange
    now = timezone.now()
    coupon = Coupon(
        code="WELCOME10",
        discount_type=DiscountType.FIXED,
        discount_value=Money("1000"),
        minimum_order_amount=Money("5000"),
        starts_at=now - timedelta(days=1),
        ends_at=now + timedelta(days=1),
    )

    # Act
    result = coupon.apply(Money("10000"), applied_at=now)

    # Assert
    assert result.original_amount == Money("10000")
    assert result.discount_amount == Money("1000")
    assert result.final_amount == Money("9000")
    assert result.event.coupon_code == "WELCOME10"


def test_coupon_apply_percent_discount_respects_max_discount_amount():
    # Arrange
    now = timezone.now()
    coupon = Coupon(
        code="SPRING20",
        discount_type=DiscountType.PERCENT,
        discount_value=Decimal("20"),
        minimum_order_amount=Money("10000"),
        max_discount_amount=Money("3000"),
        starts_at=now - timedelta(days=1),
        ends_at=now + timedelta(days=1),
    )

    # Act
    result = coupon.apply(Money("50000"), applied_at=now)

    # Assert
    assert result.discount_amount == Money("3000")
    assert result.final_amount == Money("47000")


def test_coupon_apply_when_expired_raises_domain_error():
    # Arrange
    now = timezone.now()
    coupon = Coupon(
        code="OLD10",
        discount_type=DiscountType.FIXED,
        discount_value=Money("1000"),
        minimum_order_amount=Money("5000"),
        starts_at=now - timedelta(days=10),
        ends_at=now - timedelta(days=1),
    )

    # Act / Assert
    with pytest.raises(CouponExpiredError):
        coupon.apply(Money("10000"), applied_at=now)


def test_coupon_apply_when_order_amount_is_too_low_raises_domain_error():
    # Arrange
    now = timezone.now()
    coupon = Coupon(
        code="MIN10",
        discount_type=DiscountType.FIXED,
        discount_value=Money("1000"),
        minimum_order_amount=Money("5000"),
        starts_at=now - timedelta(days=1),
        ends_at=now + timedelta(days=1),
    )

    # Act / Assert
    with pytest.raises(CouponNotApplicableError):
        coupon.apply(Money("4000"), applied_at=now)
```

**예상 실패 이유**

첫 실행에서는 `apps.coupons.domain` 모듈, `Coupon`, `Money`, `DiscountType`, 도메인 예외가 없어서 `ModuleNotFoundError` 또는 `ImportError`가 나야 합니다. 이 실패가 RED입니다.

**GREEN: 최소 구현**
`apps/coupons/domain.py`

```python
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class CouponError(Exception):
    pass


class CouponExpiredError(CouponError):
    pass


class CouponNotApplicableError(CouponError):
    pass


class DiscountType(StrEnum):
    FIXED = "fixed"
    PERCENT = "percent"


@dataclass(frozen=True)
class Money:
    amount: Decimal

    def __init__(self, amount: str | int | Decimal) -> None:
        value = Decimal(amount)
        if value < 0:
            raise ValueError("amount must be zero or greater")
        object.__setattr__(self, "amount", value)

    def __sub__(self, other: "Money") -> "Money":
        return Money(max(self.amount - other.amount, Decimal("0")))

    def min(self, other: "Money") -> "Money":
        return self if self.amount <= other.amount else other


@dataclass(frozen=True)
class CouponAppliedEvent:
    coupon_code: str
    original_amount: Money
    discount_amount: Money
    final_amount: Money


@dataclass(frozen=True)
class AppliedCoupon:
    original_amount: Money
    discount_amount: Money
    final_amount: Money
    event: CouponAppliedEvent


@dataclass
class Coupon:
    """Aggregate Root.

    Invariants:
    - 기간 밖의 쿠폰은 적용할 수 없다.
    - 최소 주문 금액 미만에는 적용할 수 없다.
    - 할인 후 금액은 0원 미만이 될 수 없다.
    """

    code: str
    discount_type: DiscountType
    discount_value: Money | Decimal
    minimum_order_amount: Money
    starts_at: datetime
    ends_at: datetime
    max_discount_amount: Money | None = None
    is_active: bool = True

    def apply(self, order_amount: Money, *, applied_at: datetime) -> AppliedCoupon:
        if not self.is_active or not (self.starts_at <= applied_at <= self.ends_at):
            raise CouponExpiredError("coupon is not active at applied_at")

        if order_amount.amount < self.minimum_order_amount.amount:
            raise CouponNotApplicableError("order amount is below coupon minimum")

        discount_amount = self._discount_amount(order_amount)
        final_amount = order_amount - discount_amount

        event = CouponAppliedEvent(
            coupon_code=self.code,
            original_amount=order_amount,
            discount_amount=discount_amount,
            final_amount=final_amount,
        )
        return AppliedCoupon(
            original_amount=order_amount,
            discount_amount=discount_amount,
            final_amount=final_amount,
            event=event,
        )

    def _discount_amount(self, order_amount: Money) -> Money:
        if self.discount_type == DiscountType.FIXED:
            discount = self.discount_value
            if not isinstance(discount, Money):
                discount = Money(discount)
        else:
            rate = Decimal(self.discount_value) / Decimal("100")
            discount = Money(order_amount.amount * rate)

        discount = discount.min(order_amount)
        if self.max_discount_amount is not None:
            discount = discount.min(self.max_discount_amount)
        return discount
```

**Django 모델 + Repository**
`apps/coupons/models.py`

```python
from django.conf import settings
from django.db import models


class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        FIXED = "fixed", "Fixed"
        PERCENT = "percent", "Percent"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"

    code = models.CharField(max_length=40, unique=True)
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    discount_value = models.DecimalField(max_digits=12, decimal_places=2)
    minimum_order_amount = models.DecimalField(max_digits=12, decimal_places=2)
    max_discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    class Meta:
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code", "status"]),
            models.Index(fields=["starts_at", "ends_at"]),
        ]

    def __str__(self) -> str:
        return self.code


class CouponRedemption(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    original_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2)
    final_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "created_at"])]
```

`apps/coupons/repositories.py`

```python
from abc import ABC, abstractmethod

from django.shortcuts import get_object_or_404

from apps.coupons import domain
from apps.coupons.models import Coupon as CouponModel


class CouponRepository(ABC):
    @abstractmethod
    def find_by_code(self, code: str) -> domain.Coupon:
        raise NotImplementedError


class DjangoCouponRepository(CouponRepository):
    def find_by_code(self, code: str) -> domain.Coupon:
        coupon = get_object_or_404(CouponModel, code=code)

        return domain.Coupon(
            code=coupon.code,
            discount_type=domain.DiscountType(coupon.discount_type),
            discount_value=(
                domain.Money(coupon.discount_value)
                if coupon.discount_type == CouponModel.DiscountType.FIXED
                else coupon.discount_value
            ),
            minimum_order_amount=domain.Money(coupon.minimum_order_amount),
            max_discount_amount=(
                domain.Money(coupon.max_discount_amount)
                if coupon.max_discount_amount is not None
                else None
            ),
            starts_at=coupon.starts_at,
            ends_at=coupon.ends_at,
            is_active=coupon.status == CouponModel.Status.ACTIVE,
        )
```

`apps/coupons/services.py`

```python
from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.coupons.domain import AppliedCoupon, Money
from apps.coupons.models import Coupon as CouponModel
from apps.coupons.models import CouponRedemption
from apps.coupons.repositories import CouponRepository, DjangoCouponRepository


@dataclass(frozen=True)
class ApplyCouponCommand:
    user_id: int
    coupon_code: str
    order_amount: Decimal


def apply_coupon(
    command: ApplyCouponCommand,
    *,
    repository: CouponRepository | None = None,
) -> AppliedCoupon:
    repository = repository or DjangoCouponRepository()

    with transaction.atomic():
        coupon = repository.find_by_code(command.coupon_code)
        result = coupon.apply(Money(command.order_amount), applied_at=timezone.now())

        coupon_model = CouponModel.objects.select_for_update().get(code=coupon.code)
        CouponRedemption.objects.create(
            coupon=coupon_model,
            user_id=command.user_id,
            original_amount=result.original_amount.amount,
            discount_amount=result.discount_amount.amount,
            final_amount=result.final_amount.amount,
        )

    return result
```

**Django Ninja API Hook**
`apps/coupons/api.py`

```python
from decimal import Decimal

from django.http import HttpRequest
from ninja import Router, Schema
from ninja.security import django_auth

from apps.coupons.services import ApplyCouponCommand, apply_coupon

router = Router(tags=["coupons"])


class ApplyCouponIn(Schema):
    code: str
    order_amount: Decimal


class ApplyCouponOut(Schema):
    code: str
    original_amount: Decimal
    discount_amount: Decimal
    final_amount: Decimal


@router.post("/apply", response=ApplyCouponOut, auth=django_auth)
def apply_coupon_api(request: HttpRequest, payload: ApplyCouponIn) -> ApplyCouponOut:
    result = apply_coupon(
        ApplyCouponCommand(
            user_id=request.user.id,
            coupon_code=payload.code,
            order_amount=payload.order_amount,
        )
    )

    return ApplyCouponOut(
        code=result.event.coupon_code,
        original_amount=result.original_amount.amount,
        discount_amount=result.discount_amount.amount,
        final_amount=result.final_amount.amount,
    )
```

`config/api.py`

```python
from ninja import NinjaAPI

from apps.coupons.api import router as coupons_router

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

**API RED 테스트 추가**
`tests/isolated/integration/coupons/test_apply_coupon_api.py`

```python
from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from ninja.testing import TestClient

from apps.coupons.api import router
from apps.coupons.models import Coupon


@pytest.mark.django_db
def test_apply_coupon_api_with_authenticated_user_returns_discount(
    django_user_model,
):
    # Arrange
    user = django_user_model.objects.create_user(
        username="buyer",
        password="password",
    )
    now = timezone.now()
    Coupon.objects.create(
        code="WELCOME10",
        discount_type=Coupon.DiscountType.FIXED,
        discount_value=Decimal("1000"),
        minimum_order_amount=Decimal("5000"),
        starts_at=now - timedelta(days=1),
        ends_at=now + timedelta(days=1),
        status=Coupon.Status.ACTIVE,
    )
    client = TestClient(router)

    # Act
    response = client.post(
        "/apply",
        json={"code": "WELCOME10", "order_amount": "10000"},
        user=user,
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "code": "WELCOME10",
        "original_amount": "10000",
        "discount_amount": "1000",
        "final_amount": "9000",
    }
```

**예상 실패 이유**

API RED는 모델, 마이그레이션, 라우터, 서비스가 없을 때 실패합니다. GREEN 구현 후에도 `Coupon` 테이블이 없으면 DB 에러가 나므로 마이그레이션 생성이 필요합니다.

**실행 명령**

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/unit/coupons/test_coupon_apply.py -q
python manage.py makemigrations coupons
python manage.py migrate
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/integration/coupons/test_apply_coupon_api.py -q
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/ -q
python manage.py check
```

**REFACTOR 기준**

GREEN 이후에만 리팩터링합니다. 우선순위는 `Coupon.apply()`의 도메인 규칙 유지, `Money` 비교 연산 보강, `CouponRedemption` 중복 적용 방지 정책 추가, API 에러를 RFC 9457 Problem Details로 매핑, 테스트 fixture를 `tests/isolated/conftest.py`로 추출하는 순서가 적절합니다. 테스트가 계속 통과하는 동안만 구조를 바꾸고, 할인 정책 종류가 실제로 늘어나기 전에는 전략 객체나 플러그인 구조를 만들지 않는 편이 낫습니다.

---
> **관련 스킬 참조:**
> - Django Ninja API 에러 처리와 인증 확장 → **implementation-django-ninja** 스킬