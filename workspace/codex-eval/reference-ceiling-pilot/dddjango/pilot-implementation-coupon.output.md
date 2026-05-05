아래는 `coupons` 바운디드 컨텍스트를 `orders` 결제 흐름과 분리한 구조입니다. 쿠폰 적용의 일관성 경계는 `Coupon` 애그리거트가 갖고, 주문 합계/장바구니 상태는 ID와 금액만 받아 검증합니다.

**유비쿼터스 언어**

| 용어 | 의미 | 금지 동의어 |
|---|---|---|
| Coupon | 발급된 할인 권리 | Voucher, Promo |
| Apply | 주문 금액에 쿠폰을 검증 후 반영 | Use, Redeem |
| Discount | 적용 결과 할인액 | Benefit |

```python
# apps/coupons/domain.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


class CouponNotApplicableError(Exception): ...


@dataclass(frozen=True)
class Money:
    amount: Decimal

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise CouponNotApplicableError("amount must be positive")


@dataclass(frozen=True)
class CouponAppliedEvent:
    coupon_id: UUID
    order_id: UUID
    discount: Money


class Coupon:
    """Aggregate Root.
    Invariant: active coupon만 적용 가능하며, 최소 주문 금액 이상에서만 할인된다.
    """

    def __init__(self, id: UUID, code: str, active: bool, min_order_amount: Money, discount: Money):
        self.id = id
        self.code = code
        self.active = active
        self.min_order_amount = min_order_amount
        self.discount = discount

    def apply_to(self, order_id: UUID, order_total: Money) -> CouponAppliedEvent:
        if not self.active or order_total.amount < self.min_order_amount.amount:
            raise CouponNotApplicableError("coupon is not applicable")
        return CouponAppliedEvent(self.id, order_id, self.discount)


class CouponRepository(ABC):
    @abstractmethod
    def find_by_code_for_update(self, code: str) -> Coupon | None: ...

    @abstractmethod
    def mark_applied(self, coupon_id: UUID, order_id: UUID) -> None: ...
```

```python
# apps/coupons/models.py
from django.db import models


class CouponModel(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        EXPIRED = "EXPIRED", "Expired"

    code = models.CharField(max_length=40, unique=True)
    status = models.CharField(max_length=20, choices=Status)
    min_order_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        indexes = [models.Index(fields=["code", "status"])]

    def __str__(self) -> str:
        return self.code


class CouponApplicationModel(models.Model):
    coupon = models.ForeignKey(CouponModel, on_delete=models.PROTECT)
    order_id = models.UUIDField()
    applied_at = models.DateTimeField(auto_now_add=True)
```

```python
# apps/coupons/repositories.py
from uuid import UUID

from .domain import Coupon, CouponRepository, Money
from .models import CouponApplicationModel, CouponModel


class DjangoCouponRepository(CouponRepository):
    def find_by_code_for_update(self, code: str) -> Coupon | None:
        row = CouponModel.objects.select_for_update().filter(code=code).first()
        if row is None:
            return None
        return Coupon(
            id=row.id,
            code=row.code,
            active=row.status == CouponModel.Status.ACTIVE,
            min_order_amount=Money(row.min_order_amount),
            discount=Money(row.discount_amount),
        )

    def mark_applied(self, coupon_id: UUID, order_id: UUID) -> None:
        CouponApplicationModel.objects.create(coupon_id=coupon_id, order_id=order_id)
```

```python
# apps/coupons/services.py
from decimal import Decimal
from uuid import UUID

from django.db import transaction

from .domain import CouponNotApplicableError, CouponRepository, Money


class ApplyCouponService:
    def __init__(self, coupons: CouponRepository):
        self.coupons = coupons

    @transaction.atomic
    def apply(self, *, code: str, order_id: UUID, order_total: Decimal) -> Decimal:
        coupon = self.coupons.find_by_code_for_update(code)
        if coupon is None:
            raise CouponNotApplicableError("coupon not found")
        event = coupon.apply_to(order_id, Money(order_total))
        self.coupons.mark_applied(event.coupon_id, event.order_id)
        return event.discount.amount
```

```python
# apps/coupons/api/schemas.py
from decimal import Decimal
from uuid import UUID

from ninja import Schema


class ApplyCouponIn(Schema):
    code: str
    order_id: UUID
    order_total: Decimal


class ApplyCouponOut(Schema):
    discount_amount: Decimal


class CouponSchema(Schema):
    code: str
    status: str
```

```python
# apps/coupons/api/router.py
from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError
from ninja.security import django_auth

from apps.coupons.domain import CouponNotApplicableError
from apps.coupons.models import CouponModel
from apps.coupons.repositories import DjangoCouponRepository
from apps.coupons.services import ApplyCouponService

from .schemas import ApplyCouponIn, ApplyCouponOut, CouponSchema

router = Router(auth=django_auth)


@router.post("/apply", response=ApplyCouponOut)
def apply_coupon(request: HttpRequest, payload: ApplyCouponIn) -> ApplyCouponOut:
    try:
        discount = ApplyCouponService(DjangoCouponRepository()).apply(**payload.dict())
    except CouponNotApplicableError as exc:
        raise HttpError(400, str(exc)) from exc
    return ApplyCouponOut(discount_amount=discount)


@router.get("", response=list[CouponSchema])
def list_coupons(request: HttpRequest) -> list[CouponSchema]:
    return [CouponSchema(code=c.code, status=c.status) for c in CouponModel.objects.all()]
```

```python
# config/api.py
from ninja import NinjaAPI
from apps.coupons.api.router import router as coupons_router

api = NinjaAPI()
api.add_router("/coupons/", coupons_router)
```

**RED checks**

```python
# tests/test_apply_coupon.py
import pytest
from decimal import Decimal

from apps.coupons.domain import CouponNotApplicableError
from apps.coupons.services import ApplyCouponService


def test_expired_coupon_is_rejected(coupon_repo_with_expired_coupon, order_id):
    service = ApplyCouponService(coupon_repo_with_expired_coupon)

    with pytest.raises(CouponNotApplicableError):
        service.apply(code="OLD10", order_id=order_id, order_total=Decimal("50000"))


def test_coupon_below_minimum_order_amount_is_rejected(coupon_repo_with_active_coupon, order_id):
    service = ApplyCouponService(coupon_repo_with_active_coupon)

    with pytest.raises(CouponNotApplicableError):
        service.apply(code="WELCOME", order_id=order_id, order_total=Decimal("1000"))
```

검증 명령은 `python manage.py check`와 `pytest tests/test_apply_coupon.py`입니다. 현재 환경은 읽기 전용이라 실제 파일 생성과 테스트 실행은 하지 않았습니다.

---
> **관련 스킬 참조:**
> - API 구현/오류 응답 정교화 → **implementation-django-ninja** 스킬