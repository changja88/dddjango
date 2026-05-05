**[주요 내용]**

가정: `orders`는 별도 바운디드 컨텍스트이고, 쿠폰 컨텍스트는 `order_id`, `user_id`, `order_total`만 ID/값으로 받습니다. 주문 금액 변경은 쿠폰 컨텍스트가 직접 저장하지 않습니다.

**DDD layers**

| Layer | 책임 |
|---|---|
| Domain | 쿠폰 적용 가능 여부, 할인 계산, 중복 사용 불변식 |
| Application | use case 조율, transaction, repository 호출 |
| Infrastructure | Django ORM 모델/Repository 구현 |
| Interface | Django Ninja Schema/Router |

유비쿼터스 언어: `Coupon`, `Redemption`, `apply`, `discount_amount`
금지 동의어: `voucher`, `promotion_code`, `sale_code`

```python
# apps/coupons/domain.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class CouponStatus(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    DISABLED = "disabled"


class CouponCannotBeApplied(Exception): ...


@dataclass(frozen=True)
class Money:
    amount: Decimal

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise CouponCannotBeApplied("amount must be non-negative")


@dataclass(frozen=True)
class CouponAppliedEvent:
    coupon_id: int
    order_id: int
    user_id: int
    discount_amount: Decimal


@dataclass
class Coupon:
    """Aggregate Root.
    Invariants: active period, minimum order amount, redemption limit,
    one coupon redemption per user/order are protected before apply.
    """

    id: int
    code: str
    status: CouponStatus
    discount_amount: Money
    min_order_amount: Money
    valid_from: datetime
    valid_until: datetime
    max_redemptions: int
    redeemed_count: int

    def apply(self, *, order_id: int, user_id: int, order_total: Money, now: datetime) -> CouponAppliedEvent:
        if self.status != CouponStatus.ACTIVE:
            raise CouponCannotBeApplied("coupon is not active")
        if not self.valid_from <= now <= self.valid_until:
            raise CouponCannotBeApplied("coupon is outside valid period")
        if order_total.amount < self.min_order_amount.amount:
            raise CouponCannotBeApplied("order total is below minimum")
        if self.redeemed_count >= self.max_redemptions:
            raise CouponCannotBeApplied("coupon redemption limit reached")

        discount = min(self.discount_amount.amount, order_total.amount)
        return CouponAppliedEvent(self.id, order_id, user_id, discount)


class CouponRepository(ABC):
    @abstractmethod
    def get_by_code_for_update(self, code: str) -> Coupon: ...

    @abstractmethod
    def has_redemption(self, *, coupon_id: int, order_id: int, user_id: int) -> bool: ...

    @abstractmethod
    def save_redemption(self, event: CouponAppliedEvent) -> None: ...
```

```python
# apps/coupons/models.py
from django.db import models


class CouponModel(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        DISABLED = "disabled", "Disabled"

    code = models.CharField(max_length=40, unique=True)
    status = models.CharField(max_length=20, choices=Status)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=12, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    max_redemptions = models.PositiveIntegerField()
    redeemed_count = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [models.Index(fields=["code", "status"])]

    def __str__(self) -> str:
        return self.code


class CouponRedemption(models.Model):
    coupon = models.ForeignKey(CouponModel, on_delete=models.PROTECT)
    order_id = models.BigIntegerField()
    user_id = models.BigIntegerField()
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["coupon", "order_id", "user_id"],
                name="uniq_coupon_redemption_per_order_user",
            )
        ]
```

```python
# apps/coupons/repositories.py
from django.db.models import F

from .domain import Coupon, CouponAppliedEvent, CouponRepository, CouponStatus, Money
from .models import CouponModel, CouponRedemption


class DjangoCouponRepository(CouponRepository):
    def get_by_code_for_update(self, code: str) -> Coupon:
        row = CouponModel.objects.select_for_update().get(code=code)
        return Coupon(
            id=row.id,
            code=row.code,
            status=CouponStatus(row.status),
            discount_amount=Money(row.discount_amount),
            min_order_amount=Money(row.min_order_amount),
            valid_from=row.valid_from,
            valid_until=row.valid_until,
            max_redemptions=row.max_redemptions,
            redeemed_count=row.redeemed_count,
        )

    def has_redemption(self, *, coupon_id: int, order_id: int, user_id: int) -> bool:
        return CouponRedemption.objects.filter(
            coupon_id=coupon_id, order_id=order_id, user_id=user_id
        ).exists()

    def save_redemption(self, event: CouponAppliedEvent) -> None:
        CouponRedemption.objects.create(
            coupon_id=event.coupon_id,
            order_id=event.order_id,
            user_id=event.user_id,
            discount_amount=event.discount_amount,
        )
        CouponModel.objects.filter(id=event.coupon_id).update(
            redeemed_count=F("redeemed_count") + 1
        )
```

```python
# apps/coupons/services.py
from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from .domain import CouponCannotBeApplied, CouponRepository, Money


@dataclass(frozen=True)
class ApplyCouponCommand:
    code: str
    order_id: int
    user_id: int
    order_total: Decimal


class ApplyCouponService:
    def __init__(self, coupons: CouponRepository) -> None:
        self.coupons = coupons

    @transaction.atomic
    def apply(self, command: ApplyCouponCommand) -> Decimal:
        coupon = self.coupons.get_by_code_for_update(command.code)

        if self.coupons.has_redemption(
            coupon_id=coupon.id, order_id=command.order_id, user_id=command.user_id
        ):
            raise CouponCannotBeApplied("coupon already redeemed for this order")

        event = coupon.apply(
            order_id=command.order_id,
            user_id=command.user_id,
            order_total=Money(command.order_total),
            now=timezone.now(),
        )
        self.coupons.save_redemption(event)
        return event.discount_amount
```

```python
# apps/coupons/api.py
from decimal import Decimal

from django.http import HttpRequest
from ninja import Router, Schema
from ninja.security import django_auth

from .domain import CouponCannotBeApplied
from .repositories import DjangoCouponRepository
from .services import ApplyCouponCommand, ApplyCouponService

router = Router(tags=["coupons"])


class ApplyCouponIn(Schema):
    code: str
    order_id: int
    order_total: Decimal


class ApplyCouponOut(Schema):
    discount_amount: Decimal


@router.post("/apply", response={200: ApplyCouponOut, 400: dict}, auth=django_auth)
def apply_coupon(request: HttpRequest, payload: ApplyCouponIn) -> tuple[int, ApplyCouponOut | dict]:
    service = ApplyCouponService(DjangoCouponRepository())
    try:
        discount = service.apply(
            ApplyCouponCommand(
                code=payload.code,
                order_id=payload.order_id,
                user_id=request.user.id,
                order_total=payload.order_total,
            )
        )
    except CouponCannotBeApplied as exc:
        return 400, {"type": "coupon-not-applicable", "title": str(exc)}

    return 200, ApplyCouponOut(discount_amount=discount)
```

```python
# config/api.py
from ninja import NinjaAPI
from apps.coupons.api import router as coupons_router

api = NinjaAPI()
api.add_router("/coupons/", coupons_router)
```

**pytest RED checks**

```python
# tests/test_apply_coupon.py
import pytest
from apps.coupons.domain import CouponCannotBeApplied
from apps.coupons.services import ApplyCouponCommand, ApplyCouponService


@pytest.mark.django_db
def test_apply_coupon_rejects_duplicate_redemption(coupon_factory, redemption_factory):
    coupon = coupon_factory(code="SAVE10")
    redemption_factory(coupon=coupon, order_id=1, user_id=7)

    service = ApplyCouponService(DjangoCouponRepository())

    with pytest.raises(CouponCannotBeApplied):
        service.apply(ApplyCouponCommand("SAVE10", 1, 7, coupon.min_order_amount))


@pytest.mark.django_db
def test_apply_coupon_increments_redemption_count(coupon_factory):
    coupon = coupon_factory(code="SAVE10", redeemed_count=0)

    ApplyCouponService(DjangoCouponRepository()).apply(
        ApplyCouponCommand("SAVE10", 1, 7, coupon.min_order_amount)
    )

    coupon.refresh_from_db()
    assert coupon.redeemed_count == 1
```

검증 명령:

```bash
python manage.py check
pytest tests/test_apply_coupon.py
```

---
> **관련 스킬 참조:**
> - API 에러 형식/상태 코드 세부 설계 → **architecture-api** 스킬