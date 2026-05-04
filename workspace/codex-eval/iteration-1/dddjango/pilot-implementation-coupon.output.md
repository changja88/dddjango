## 주요 내용

현재 `/private/tmp/dddjango-codex-eval` 디렉터리는 비어 있고 `config.toml`도 없어 실제 파일 패치는 할 수 없습니다. 대신 Django + DDD + 클린 아키텍처 + Django Ninja 기준으로 바로 적용할 수 있는 구조를 제안합니다.

핵심 방향은 **쿠폰 적용을 “주문에 쿠폰 적용 리소스를 생성하는 행위”**로 보고, API는 동사형 `/apply-coupon` 대신 명사형 리소스인 `coupon-applications`를 사용합니다.

```text
project/
  config/
    api.py
    urls.py

  coupons/
    domain/
      entities.py
      value_objects.py
      policies.py
      exceptions.py

    application/
      commands.py
      results.py
      ports.py
      services.py

    infrastructure/
      models.py
      repositories.py
      unit_of_work.py

    api/
      schemas.py
      router.py
```

**도메인 모델**

Django ORM 모델을 도메인 모델로 직접 쓰지 않고, 쿠폰 규칙은 순수 Python 객체에 둡니다. Django 모델은 저장소 구현체에 가깝게 둡니다.

```python
# coupons/domain/value_objects.py
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class DiscountType(StrEnum):
    FIXED_AMOUNT = "fixed_amount"
    PERCENTAGE = "percentage"


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str = "KRW"

    def subtract(self, discount: "Money") -> "Money":
        return Money(max(self.amount - discount.amount, Decimal("0")), self.currency)


@dataclass(frozen=True, slots=True)
class Discount:
    type: DiscountType
    value: Decimal

    def calculate(self, subtotal: Money) -> Money:
        if self.type == DiscountType.FIXED_AMOUNT:
            return Money(min(self.value, subtotal.amount), subtotal.currency)

        discount_amount = subtotal.amount * self.value / Decimal("100")
        return Money(min(discount_amount, subtotal.amount), subtotal.currency)
```

```python
# coupons/domain/entities.py
from dataclasses import dataclass
from datetime import datetime

from .exceptions import CouponAlreadyUsedError, CouponExpiredError, CouponNotActiveError
from .value_objects import Discount, Money


@dataclass(slots=True)
class Coupon:
    id: int
    code: str
    discount: Discount
    starts_at: datetime
    ends_at: datetime
    is_active: bool
    usage_limit: int
    used_count: int
    minimum_order_amount: Money

    def apply_to(self, subtotal: Money, now: datetime) -> Money:
        self._ensure_applicable(subtotal, now)
        return self.discount.calculate(subtotal)

    def mark_used(self) -> None:
        if self.used_count >= self.usage_limit:
            raise CouponAlreadyUsedError(self.code)
        self.used_count += 1

    def _ensure_applicable(self, subtotal: Money, now: datetime) -> None:
        if not self.is_active:
            raise CouponNotActiveError(self.code)
        if not self.starts_at <= now <= self.ends_at:
            raise CouponExpiredError(self.code)
        if self.used_count >= self.usage_limit:
            raise CouponAlreadyUsedError(self.code)
        if subtotal.amount < self.minimum_order_amount.amount:
            raise CouponNotActiveError(self.code)
```

```python
# coupons/domain/exceptions.py
class CouponError(Exception):
    pass


class CouponNotFoundError(CouponError):
    def __init__(self, code: str) -> None:
        self.code = code


class CouponNotActiveError(CouponError):
    def __init__(self, code: str) -> None:
        self.code = code


class CouponExpiredError(CouponError):
    def __init__(self, code: str) -> None:
        self.code = code


class CouponAlreadyUsedError(CouponError):
    def __init__(self, code: str) -> None:
        self.code = code
```

**Django ORM 모델**

DB에는 조회, 중복 방지, 사용 이력 추적에 필요한 제약을 둡니다.

```python
# coupons/infrastructure/models.py
from django.conf import settings
from django.db import models


class CouponModel(models.Model):
    code = models.CharField(max_length=50, unique=True, db_index=True)
    discount_type = models.CharField(max_length=30)
    discount_value = models.DecimalField(max_digits=12, decimal_places=2)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField()
    used_count = models.PositiveIntegerField(default=0)
    minimum_order_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "coupons"


class CouponRedemptionModel(models.Model):
    coupon = models.ForeignKey(CouponModel, on_delete=models.PROTECT)
    order_id = models.BigIntegerField(db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "coupon_redemptions"
        constraints = [
            models.UniqueConstraint(
                fields=["coupon", "order_id"],
                name="unique_coupon_redemption_per_order",
            )
        ]
```

**Application Service**

서비스는 트랜잭션 경계, 저장소 호출, 도메인 객체 실행을 조율합니다. 쿠폰 할인 계산 자체는 서비스가 아니라 도메인 객체가 담당합니다.

```python
# coupons/application/commands.py
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ApplyCouponCommand:
    order_id: int
    user_id: int
    code: str
```

```python
# coupons/application/results.py
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ApplyCouponResult:
    order_id: int
    coupon_code: str
    discount_amount: Decimal
    payable_amount: Decimal
```

```python
# coupons/application/ports.py
from typing import Protocol

from coupons.domain.entities import Coupon
from coupons.domain.value_objects import Money


class CouponRepository(Protocol):
    def get_by_code_for_update(self, code: str) -> Coupon: ...
    def save(self, coupon: Coupon) -> None: ...
    def create_redemption(
        self,
        *,
        coupon: Coupon,
        order_id: int,
        user_id: int,
        discount_amount: Money,
    ) -> None: ...


class OrderPricingPort(Protocol):
    def get_order_subtotal(self, order_id: int, user_id: int) -> Money: ...
    def apply_discount(self, order_id: int, discount_amount: Money) -> Money: ...


class UnitOfWork(Protocol):
    def __enter__(self) -> "UnitOfWork": ...
    def __exit__(self, exc_type, exc, traceback) -> None: ...
```

```python
# coupons/application/services.py
from django.utils import timezone

from .commands import ApplyCouponCommand
from .ports import CouponRepository, OrderPricingPort, UnitOfWork
from .results import ApplyCouponResult


class ApplyCouponService:
    def __init__(
        self,
        *,
        coupons: CouponRepository,
        order_pricing: OrderPricingPort,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._coupons = coupons
        self._order_pricing = order_pricing
        self._unit_of_work = unit_of_work

    def apply(self, command: ApplyCouponCommand) -> ApplyCouponResult:
        with self._unit_of_work:
            coupon = self._coupons.get_by_code_for_update(command.code)
            subtotal = self._order_pricing.get_order_subtotal(
                command.order_id,
                command.user_id,
            )

            discount_amount = coupon.apply_to(subtotal, timezone.now())
            payable_amount = self._order_pricing.apply_discount(
                command.order_id,
                discount_amount,
            )

            coupon.mark_used()
            self._coupons.save(coupon)
            self._coupons.create_redemption(
                coupon=coupon,
                order_id=command.order_id,
                user_id=command.user_id,
                discount_amount=discount_amount,
            )

        return ApplyCouponResult(
            order_id=command.order_id,
            coupon_code=coupon.code,
            discount_amount=discount_amount.amount,
            payable_amount=payable_amount.amount,
        )
```

**Django Ninja Endpoint**

쿠폰 적용은 `POST /v1/orders/{order_id}/coupon-applications`로 둡니다. POST는 멱등하지 않으므로 실제 주문/결제 흐름에서는 `Idempotency-Key` 헤더 저장도 같이 권장합니다.

```python
# coupons/api/schemas.py
from decimal import Decimal

from ninja import Schema


class ApplyCouponIn(Schema):
    code: str


class ApplyCouponOut(Schema):
    order_id: int
    coupon_code: str
    discount_amount: Decimal
    payable_amount: Decimal


class ProblemDetail(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str
```

```python
# coupons/api/router.py
from ninja import Path, Router
from ninja.security import django_auth

from coupons.application.commands import ApplyCouponCommand
from coupons.application.services import ApplyCouponService
from coupons.domain.exceptions import (
    CouponAlreadyUsedError,
    CouponExpiredError,
    CouponNotActiveError,
)

from .schemas import ApplyCouponIn, ApplyCouponOut, ProblemDetail

router = Router(tags=["coupon-applications"], auth=django_auth)


@router.post(
    "/orders/{order_id}/coupon-applications",
    response={201: ApplyCouponOut, 409: ProblemDetail, 422: ProblemDetail},
)
def apply_coupon(
    request,
    order_id: Path[int],
    payload: ApplyCouponIn,
) -> tuple[int, ApplyCouponOut]:
    service: ApplyCouponService = request.app.state.apply_coupon_service

    result = service.apply(
        ApplyCouponCommand(
            order_id=order_id,
            user_id=request.user.id,
            code=payload.code,
        )
    )

    return 201, ApplyCouponOut(
        order_id=result.order_id,
        coupon_code=result.coupon_code,
        discount_amount=result.discount_amount,
        payable_amount=result.payable_amount,
    )
```

예외는 `api.exception_handler()`에서 RFC 9457 Problem Details로 통일합니다.

```python
# config/api.py
from django.http import JsonResponse
from ninja import NinjaAPI

from coupons.api.router import router as coupon_router
from coupons.domain.exceptions import (
    CouponAlreadyUsedError,
    CouponExpiredError,
    CouponNotActiveError,
)

api = NinjaAPI(version="1.0.0")
api.add_router("/v1", coupon_router)


@api.exception_handler(CouponExpiredError)
@api.exception_handler(CouponNotActiveError)
def handle_unprocessable_coupon(request, exc):
    return JsonResponse(
        {
            "type": "https://api.example.com/problems/coupon-not-applicable",
            "title": "Coupon cannot be applied",
            "status": 422,
            "detail": "The coupon cannot be applied to this order.",
            "instance": request.path,
        },
        status=422,
        content_type="application/problem+json",
    )


@api.exception_handler(CouponAlreadyUsedError)
def handle_coupon_conflict(request, exc):
    return JsonResponse(
        {
            "type": "https://api.example.com/problems/coupon-conflict",
            "title": "Coupon usage conflict",
            "status": 409,
            "detail": "The coupon usage limit has already been reached.",
            "instance": request.path,
        },
        status=409,
        content_type="application/problem+json",
    )
```

정리하면, 책임 분리는 이렇게 잡는 게 좋습니다.

```text
API Router
  - HTTP 요청/응답 변환
  - 인증 사용자 추출
  - Schema 검증

Application Service
  - 트랜잭션 경계
  - Repository / 외부 포트 조율
  - Use case 실행

Domain
  - 쿠폰 적용 가능 여부
  - 할인 계산
  - 사용량 증가 규칙
  - 도메인 예외

Infrastructure
  - Django ORM 모델
  - select_for_update 기반 Repository
  - transaction.atomic 기반 UnitOfWork
```

이 구조에서 가장 중요한 점은 **“쿠폰 할인 규칙을 Django view나 ORM 모델 메서드에 넣지 않는 것”**입니다. 할인 정책이 늘어나면 `DiscountPolicy` 전략 객체로 분리하고, API와 DB 계층은 그대로 유지하는 식으로 확장할 수 있습니다.

---
> **관련 스킬 참조:**
> - Django Ninja API 구현 → **implementation-django-ninja** 스킬
> - REST 엔드포인트 설계 → **architecture-api** 스킬
> - Python 도메인 모델링 → **implementation-python** 스킬
> - 테스트 설계와 pytest → **implementation-test** 스킬