아래 구조가 Django에서 DDD + 클린 아키텍처를 과하지 않게 적용한 쿠폰 적용 기능 설계안입니다. 핵심은 “쿠폰을 적용할 수 있는가?”라는 도메인 규칙을 Django ORM, HTTP, Ninja schema에서 분리하는 것입니다.

**추천 구조**

```text
apps/
  coupons/
    domain/
      models.py
      services.py
      policies.py
      exceptions.py
      repositories.py
    application/
      use_cases.py
      dto.py
    infrastructure/
      django_models.py
      repositories.py
    interfaces/
      ninja/
        schemas.py
        endpoints.py
```

**Domain Model**

```python
# apps/coupons/domain/models.py

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum


class CouponType(str, Enum):
    FIXED = "fixed"
    PERCENT = "percent"


@dataclass(frozen=True)
class Money:
    amount: Decimal

    def subtract(self, value: Decimal) -> "Money":
        return Money(max(self.amount - value, Decimal("0")))


@dataclass
class Coupon:
    id: int
    code: str
    coupon_type: CouponType
    discount_value: Decimal
    min_order_amount: Decimal
    max_discount_amount: Decimal | None
    starts_at: datetime
    ends_at: datetime
    usage_limit: int | None
    used_count: int
    is_active: bool

    def validate_applicable(self, order_amount: Money, now: datetime) -> None:
        if not self.is_active:
            raise CouponNotActiveError()

        if now < self.starts_at or now > self.ends_at:
            raise CouponExpiredError()

        if order_amount.amount < self.min_order_amount:
            raise CouponMinOrderAmountError()

        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            raise CouponUsageLimitExceededError()

    def calculate_discount(self, order_amount: Money) -> Money:
        if self.coupon_type == CouponType.FIXED:
            discount = self.discount_value
        else:
            discount = order_amount.amount * self.discount_value / Decimal("100")

        if self.max_discount_amount is not None:
            discount = min(discount, self.max_discount_amount)

        return Money(discount)

    def apply_to(self, order_amount: Money, now: datetime) -> "CouponApplicationResult":
        self.validate_applicable(order_amount, now)

        discount = self.calculate_discount(order_amount)
        final_amount = order_amount.subtract(discount.amount)

        return CouponApplicationResult(
            coupon_id=self.id,
            code=self.code,
            original_amount=order_amount,
            discount_amount=discount,
            final_amount=final_amount,
        )


@dataclass(frozen=True)
class CouponApplicationResult:
    coupon_id: int
    code: str
    original_amount: Money
    discount_amount: Money
    final_amount: Money
```

**Domain Exceptions**

```python
# apps/coupons/domain/exceptions.py

class CouponError(Exception):
    message = "쿠폰을 적용할 수 없습니다."


class CouponNotFoundError(CouponError):
    message = "존재하지 않는 쿠폰입니다."


class CouponNotActiveError(CouponError):
    message = "비활성화된 쿠폰입니다."


class CouponExpiredError(CouponError):
    message = "사용 기간이 지난 쿠폰입니다."


class CouponMinOrderAmountError(CouponError):
    message = "최소 주문 금액을 충족하지 않습니다."


class CouponUsageLimitExceededError(CouponError):
    message = "쿠폰 사용 가능 횟수를 초과했습니다."


class CouponAlreadyUsedError(CouponError):
    message = "이미 사용한 쿠폰입니다."
```

**Repository Contract**

```python
# apps/coupons/domain/repositories.py

from abc import ABC, abstractmethod

from apps.coupons.domain.models import Coupon


class CouponRepository(ABC):
    @abstractmethod
    def get_by_code(self, code: str) -> Coupon | None:
        raise NotImplementedError

    @abstractmethod
    def exists_user_usage(self, user_id: int, coupon_id: int) -> bool:
        raise NotImplementedError
```

**Application Use Case**

```python
# apps/coupons/application/use_cases.py

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from apps.coupons.domain.exceptions import CouponAlreadyUsedError, CouponNotFoundError
from apps.coupons.domain.models import Money
from apps.coupons.domain.repositories import CouponRepository


@dataclass(frozen=True)
class ApplyCouponCommand:
    user_id: int
    code: str
    order_amount: Decimal
    requested_at: datetime


@dataclass(frozen=True)
class ApplyCouponResult:
    coupon_id: int
    code: str
    original_amount: Decimal
    discount_amount: Decimal
    final_amount: Decimal


class ApplyCouponUseCase:
    def __init__(self, coupon_repository: CouponRepository):
        self.coupon_repository = coupon_repository

    def execute(self, command: ApplyCouponCommand) -> ApplyCouponResult:
        coupon = self.coupon_repository.get_by_code(command.code)

        if coupon is None:
            raise CouponNotFoundError()

        if self.coupon_repository.exists_user_usage(command.user_id, coupon.id):
            raise CouponAlreadyUsedError()

        result = coupon.apply_to(
            order_amount=Money(command.order_amount),
            now=command.requested_at,
        )

        return ApplyCouponResult(
            coupon_id=result.coupon_id,
            code=result.code,
            original_amount=result.original_amount.amount,
            discount_amount=result.discount_amount.amount,
            final_amount=result.final_amount.amount,
        )
```

**Django ORM Models**

```python
# apps/coupons/infrastructure/django_models.py

from django.conf import settings
from django.db import models


class CouponModel(models.Model):
    class CouponType(models.TextChoices):
        FIXED = "fixed", "Fixed"
        PERCENT = "percent", "Percent"

    code = models.CharField(max_length=50, unique=True)
    coupon_type = models.CharField(max_length=20, choices=CouponType.choices)
    discount_value = models.DecimalField(max_digits=12, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CouponUsageModel(models.Model):
    coupon = models.ForeignKey(CouponModel, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_id = models.PositiveIntegerField(null=True, blank=True)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["coupon", "user"],
                name="unique_coupon_usage_per_user",
            )
        ]
```

**Django Repository 구현**

```python
# apps/coupons/infrastructure/repositories.py

from apps.coupons.domain.models import Coupon, CouponType
from apps.coupons.domain.repositories import CouponRepository
from apps.coupons.infrastructure.django_models import CouponModel, CouponUsageModel


class DjangoCouponRepository(CouponRepository):
    def get_by_code(self, code: str) -> Coupon | None:
        coupon = CouponModel.objects.filter(code=code).first()

        if coupon is None:
            return None

        return Coupon(
            id=coupon.id,
            code=coupon.code,
            coupon_type=CouponType(coupon.coupon_type),
            discount_value=coupon.discount_value,
            min_order_amount=coupon.min_order_amount,
            max_discount_amount=coupon.max_discount_amount,
            starts_at=coupon.starts_at,
            ends_at=coupon.ends_at,
            usage_limit=coupon.usage_limit,
            used_count=coupon.used_count,
            is_active=coupon.is_active,
        )

    def exists_user_usage(self, user_id: int, coupon_id: int) -> bool:
        return CouponUsageModel.objects.filter(
            user_id=user_id,
            coupon_id=coupon_id,
        ).exists()
```

**Django Ninja Schema**

```python
# apps/coupons/interfaces/ninja/schemas.py

from decimal import Decimal

from ninja import Schema


class ApplyCouponRequest(Schema):
    code: str
    order_amount: Decimal


class ApplyCouponResponse(Schema):
    coupon_id: int
    code: str
    original_amount: Decimal
    discount_amount: Decimal
    final_amount: Decimal


class ErrorResponse(Schema):
    message: str
```

**Django Ninja Endpoint**

```python
# apps/coupons/interfaces/ninja/endpoints.py

from django.utils import timezone
from ninja import Router

from apps.coupons.application.use_cases import ApplyCouponCommand, ApplyCouponUseCase
from apps.coupons.domain.exceptions import CouponError
from apps.coupons.infrastructure.repositories import DjangoCouponRepository
from apps.coupons.interfaces.ninja.schemas import (
    ApplyCouponRequest,
    ApplyCouponResponse,
    ErrorResponse,
)

router = Router(tags=["coupons"])


@router.post(
    "/apply",
    response={
        200: ApplyCouponResponse,
        400: ErrorResponse,
    },
)
def apply_coupon(request, payload: ApplyCouponRequest):
    use_case = ApplyCouponUseCase(
        coupon_repository=DjangoCouponRepository(),
    )

    try:
        result = use_case.execute(
            ApplyCouponCommand(
                user_id=request.user.id,
                code=payload.code,
                order_amount=payload.order_amount,
                requested_at=timezone.now(),
            )
        )
    except CouponError as exc:
        return 400, {"message": exc.message}

    return 200, result
```

**핵심 판단 기준**

- `Coupon`은 할인 계산, 기간 검증, 최소 주문 금액 검증 같은 도메인 규칙을 가진다.
- `ApplyCouponUseCase`는 “사용자가 주문 금액에 쿠폰을 적용한다”는 애플리케이션 흐름을 담당한다.
- Django ORM 모델은 저장 구조일 뿐이고, 도메인 규칙을 직접 담지 않는다.
- Ninja endpoint는 HTTP 요청/응답 변환만 담당한다.
- 쿠폰 사용 기록 생성, 주문 확정 시 사용량 증가 같은 변경은 별도 use case로 분리하는 것이 좋다.

실제 결제/주문 플로우에서는 `/coupons/apply`가 쿠폰을 “예약”하거나 “미리 계산”만 할지, 주문 생성 시점에 최종 검증 후 `CouponUsageModel`을 생성할지 명확히 나누는 게 중요합니다. 보통은 적용 미리보기와 최종 사용 처리를 분리합니다.