현재 `/private/tmp/dddjango-codex-eval` 디렉터리가 비어 있고 세션이 읽기 전용이라 실제 파일 생성은 못 했습니다. 대신 Django + Django Ninja에 바로 적용 가능한 DDD/클린 아키텍처 구조를 아래처럼 제안합니다.

**구조**

```text
coupons/
  domain/
    entities.py
    value_objects.py
    repositories.py
    exceptions.py
  application/
    services.py
    commands.py
    dto.py
  infrastructure/
    models.py
    repositories.py
  interfaces/
    ninja_api.py
    schemas.py
```

**핵심 방향**

- `domain`: Django 의존성 없음. 쿠폰 정책과 할인 계산 규칙만 둠.
- `application`: 유스케이스 서비스. “쿠폰 적용” 같은 앱 동작을 조율.
- `infrastructure`: Django ORM 모델과 repository 구현.
- `interfaces`: Django Ninja endpoint, request/response schema.

**Domain 예시**

```python
# coupons/domain/entities.py
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

from .exceptions import CouponExpired, CouponNotActive, MinimumOrderAmountNotMet


@dataclass(frozen=True)
class Coupon:
    id: int
    code: str
    discount_type: str  # "fixed" | "percent"
    discount_value: Decimal
    minimum_order_amount: Decimal
    max_discount_amount: Decimal | None
    starts_at: datetime
    ends_at: datetime
    is_active: bool

    def calculate_discount(self, order_amount: Decimal, now: datetime) -> Decimal:
        if not self.is_active:
            raise CouponNotActive()

        if not (self.starts_at <= now <= self.ends_at):
            raise CouponExpired()

        if order_amount < self.minimum_order_amount:
            raise MinimumOrderAmountNotMet()

        if self.discount_type == "fixed":
            discount = self.discount_value
        elif self.discount_type == "percent":
            discount = order_amount * self.discount_value / Decimal("100")
        else:
            raise ValueError("Invalid discount type")

        if self.max_discount_amount is not None:
            discount = min(discount, self.max_discount_amount)

        return min(discount, order_amount)
```

```python
# coupons/domain/repositories.py
from typing import Protocol
from .entities import Coupon


class CouponRepository(Protocol):
    def get_by_code(self, code: str) -> Coupon | None:
        ...
```

```python
# coupons/domain/exceptions.py
class CouponError(Exception):
    pass


class CouponNotFound(CouponError):
    pass


class CouponNotActive(CouponError):
    pass


class CouponExpired(CouponError):
    pass


class MinimumOrderAmountNotMet(CouponError):
    pass
```

**Application Service**

```python
# coupons/application/services.py
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from coupons.domain.repositories import CouponRepository
from coupons.domain.exceptions import CouponNotFound


@dataclass(frozen=True)
class ApplyCouponResult:
    coupon_code: str
    order_amount: Decimal
    discount_amount: Decimal
    final_amount: Decimal


class ApplyCouponService:
    def __init__(self, coupon_repository: CouponRepository):
        self.coupon_repository = coupon_repository

    def execute(
        self,
        *,
        code: str,
        order_amount: Decimal,
        now: datetime,
    ) -> ApplyCouponResult:
        coupon = self.coupon_repository.get_by_code(code)

        if coupon is None:
            raise CouponNotFound()

        discount_amount = coupon.calculate_discount(order_amount, now)

        return ApplyCouponResult(
            coupon_code=coupon.code,
            order_amount=order_amount,
            discount_amount=discount_amount,
            final_amount=order_amount - discount_amount,
        )
```

**Django ORM Model**

```python
# coupons/infrastructure/models.py
from django.db import models


class CouponModel(models.Model):
    class DiscountType(models.TextChoices):
        FIXED = "fixed"
        PERCENT = "percent"

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    discount_value = models.DecimalField(max_digits=12, decimal_places=2)
    minimum_order_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Repository 구현**

```python
# coupons/infrastructure/repositories.py
from coupons.domain.entities import Coupon
from .models import CouponModel


class DjangoCouponRepository:
    def get_by_code(self, code: str) -> Coupon | None:
        coupon = CouponModel.objects.filter(code=code).first()

        if coupon is None:
            return None

        return Coupon(
            id=coupon.id,
            code=coupon.code,
            discount_type=coupon.discount_type,
            discount_value=coupon.discount_value,
            minimum_order_amount=coupon.minimum_order_amount,
            max_discount_amount=coupon.max_discount_amount,
            starts_at=coupon.starts_at,
            ends_at=coupon.ends_at,
            is_active=coupon.is_active,
        )
```

**Django Ninja Endpoint**

```python
# coupons/interfaces/schemas.py
from decimal import Decimal
from ninja import Schema


class ApplyCouponRequest(Schema):
    code: str
    order_amount: Decimal


class ApplyCouponResponse(Schema):
    coupon_code: str
    order_amount: Decimal
    discount_amount: Decimal
    final_amount: Decimal


class ErrorResponse(Schema):
    message: str
```

```python
# coupons/interfaces/ninja_api.py
from django.utils import timezone
from ninja import Router

from coupons.application.services import ApplyCouponService
from coupons.domain.exceptions import (
    CouponNotFound,
    CouponNotActive,
    CouponExpired,
    MinimumOrderAmountNotMet,
)
from coupons.infrastructure.repositories import DjangoCouponRepository
from .schemas import ApplyCouponRequest, ApplyCouponResponse, ErrorResponse

router = Router(tags=["coupons"])


@router.post(
    "/apply",
    response={
        200: ApplyCouponResponse,
        400: ErrorResponse,
        404: ErrorResponse,
    },
)
def apply_coupon(request, payload: ApplyCouponRequest):
    service = ApplyCouponService(
        coupon_repository=DjangoCouponRepository(),
    )

    try:
        result = service.execute(
            code=payload.code,
            order_amount=payload.order_amount,
            now=timezone.now(),
        )
    except CouponNotFound:
        return 404, {"message": "쿠폰을 찾을 수 없습니다."}
    except CouponNotActive:
        return 400, {"message": "비활성화된 쿠폰입니다."}
    except CouponExpired:
        return 400, {"message": "사용 기간이 지난 쿠폰입니다."}
    except MinimumOrderAmountNotMet:
        return 400, {"message": "최소 주문 금액을 충족하지 않습니다."}

    return 200, result
```

**루트 API 연결**

```python
# project/api.py
from ninja import NinjaAPI
from coupons.interfaces.ninja_api import router as coupons_router

api = NinjaAPI()
api.add_router("/coupons", coupons_router)
```

이 구조에서는 쿠폰 정책이 Django ORM이나 Ninja에 묶이지 않습니다. 나중에 “회원당 1회 사용”, “특정 상품/카테고리 제한”, “쿠폰 사용 이력 저장”, “동시성 제어”가 필요해져도 domain/application 계층에 규칙을 추가하고 infrastructure에서 저장소만 확장하면 됩니다.