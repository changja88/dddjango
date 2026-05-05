**주요 내용**

가정: `orders`와 `coupons`는 별도 바운디드 컨텍스트에 가깝지만, “쿠폰 적용” 유스케이스는 주문 결제 전 금액 산정 흐름에 속합니다. 애그리거트는 작게 유지하고, API는 Django Ninja만 사용합니다.

| 용어 | 의미 | 금지 동의어 |
|---|---|---|
| Coupon | 적용 가능 조건과 할인 규칙을 가진 애그리거트 루트 | Voucher, Promo |
| Redeem | 쿠폰을 주문에 사용 처리 | consume, use |
| Discount | 주문 금액에서 차감되는 금액 | sale, benefit |

```python
# coupons/domain.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass(frozen=True)
class Money:
    amount: Decimal

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money cannot be negative")

@dataclass(frozen=True)
class CouponAppliedEvent:
    order_id: int
    coupon_id: int
    discount: Money

class CouponCannotBeApplied(Exception): ...

@dataclass
class Coupon:
    """Aggregate Root.
    Invariants: 만료 전, 사용 한도 미만, 주문 금액이 최소 주문 금액 이상일 때만 redeem 가능.
    """
    id: int
    code: str
    discount: Money
    min_order_amount: Money
    expires_at: datetime
    usage_limit: int
    used_count: int

    def calculate_discount(self, order_total: Money, now: datetime) -> Money:
        if now >= self.expires_at:
            raise CouponCannotBeApplied("expired_coupon")
        if self.used_count >= self.usage_limit:
            raise CouponCannotBeApplied("coupon_usage_limit_exceeded")
        if order_total.amount < self.min_order_amount.amount:
            raise CouponCannotBeApplied("order_total_too_low")
        return Money(min(self.discount.amount, order_total.amount))

    def redeem(self) -> None:
        self.used_count += 1

class CouponRepository(ABC):
    @abstractmethod
    def find_by_code_for_update(self, code: str) -> Coupon | None: ...
    @abstractmethod
    def save(self, coupon: Coupon) -> None: ...
```

```python
# coupons/models.py
from django.db import models
from django.db.models import Q, F

class CouponModel(models.Model):
    code = models.CharField(max_length=32, unique=True)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expires_at = models.DateTimeField()
    usage_limit = models.PositiveIntegerField()
    used_count = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [models.Index(fields=["code"])]
        constraints = [
            models.CheckConstraint(
                condition=Q(discount_amount__gt=0) & Q(usage_limit__gt=0),
                name="coupon_positive_discount_and_limit",
            )
        ]

    def __str__(self):
        return self.code
```

```python
# coupons/repositories.py
from .domain import Coupon, Money, CouponRepository
from .models import CouponModel

class DjangoCouponRepository(CouponRepository):
    def find_by_code_for_update(self, code: str) -> Coupon | None:
        row = CouponModel.objects.select_for_update().filter(code=code).first()
        if row is None:
            return None
        return Coupon(
            id=row.id,
            code=row.code,
            discount=Money(row.discount_amount),
            min_order_amount=Money(row.min_order_amount),
            expires_at=row.expires_at,
            usage_limit=row.usage_limit,
            used_count=row.used_count,
        )

    def save(self, coupon: Coupon) -> None:
        CouponModel.objects.filter(id=coupon.id).update(used_count=coupon.used_count)
```

```python
# orders/services.py
from dataclasses import dataclass
from django.db import transaction
from django.utils import timezone
from coupons.domain import CouponAppliedEvent, CouponCannotBeApplied, Money

@dataclass(frozen=True)
class ApplyCouponCommand:
    order_id: int
    coupon_code: str

class ApplyCouponService:
    def __init__(self, order_repo, coupon_repo):
        self.order_repo = order_repo
        self.coupon_repo = coupon_repo

    @transaction.atomic
    def apply(self, cmd: ApplyCouponCommand) -> CouponAppliedEvent:
        order = self.order_repo.find_by_id_for_update(cmd.order_id)
        coupon = self.coupon_repo.find_by_code_for_update(cmd.coupon_code)
        if order is None or coupon is None:
            raise CouponCannotBeApplied("coupon_or_order_not_found")

        discount = coupon.calculate_discount(Money(order.total_amount), timezone.now())
        order.apply_coupon(coupon_id=coupon.id, discount=discount.amount)
        coupon.redeem()

        self.order_repo.save(order)
        self.coupon_repo.save(coupon)
        return CouponAppliedEvent(order.id, coupon.id, discount)
```

```python
# orders/api.py
from django.http import HttpRequest
from ninja import Router, Schema
from ninja.security import django_auth
from coupons.domain import CouponCannotBeApplied
from coupons.repositories import DjangoCouponRepository
from .repositories import DjangoOrderRepository
from .services import ApplyCouponCommand, ApplyCouponService

router = Router(tags=["orders"])

class ApplyCouponIn(Schema):
    coupon_code: str

class ApplyCouponOut(Schema):
    order_id: int
    coupon_id: int
    discount_amount: str

@router.post("/{order_id}/coupon", response={200: ApplyCouponOut, 409: dict}, auth=django_auth)
def apply_coupon(request: HttpRequest, order_id: int, payload: ApplyCouponIn):
    service = ApplyCouponService(DjangoOrderRepository(), DjangoCouponRepository())
    try:
        event = service.apply(ApplyCouponCommand(order_id, payload.coupon_code))
    except CouponCannotBeApplied as exc:
        return 409, {"type": "about:blank", "title": "Coupon cannot be applied", "detail": str(exc)}
    return ApplyCouponOut(
        order_id=event.order_id,
        coupon_id=event.coupon_id,
        discount_amount=str(event.discount.amount),
    )
```

```python
# config/api.py
from ninja import NinjaAPI
from orders.api import router as orders_router

api = NinjaAPI()
api.add_router("/orders/", orders_router)
```

```python
# tests/test_apply_coupon_red.py
import pytest
from coupons.domain import CouponCannotBeApplied

@pytest.mark.django_db
def test_expired_coupon_cannot_be_applied(apply_coupon_service, order, expired_coupon):
    with pytest.raises(CouponCannotBeApplied, match="expired_coupon"):
        apply_coupon_service.apply_code(order.id, expired_coupon.code)

@pytest.mark.django_db
def test_coupon_usage_count_increments_once(api_client, order, coupon):
    res = api_client.post(f"/api/orders/{order.id}/coupon", json={"coupon_code": coupon.code})
    assert res.status_code == 200
    coupon.refresh_from_db()
    assert coupon.used_count == 1
```

검증 명령:

```bash
python manage.py check
pytest tests/test_apply_coupon_red.py
```

---
> **관련 스킬 참조:**
> - API 오류 형식과 상태 코드 정교화 → **implementation-django-ninja** 스킬