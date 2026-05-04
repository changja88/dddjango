**주요 내용**

현재 워크스페이스가 read-only라 파일을 만들지는 않고, 붙여 넣을 핵심 구조만 제안합니다. 쿠폰은 `promotions` 바운디드 컨텍스트의 지원 서브도메인으로 두고, 주문/결제는 ID로만 참조합니다.

| 용어 | 의미 | 금지 동의어 |
|---|---|---|
| Coupon | 적용 가능한 할인 정책 | voucher, discount_code |
| Redeem | 주문에 쿠폰을 적용 | use, consume |
| Redemption | 적용 이력 | usage |

```text
apps/promotions/
  domain/coupons.py          # Aggregate, VO, Repository ABC
  models.py                  # Django persistence model
  repositories.py            # ORM repository
  services.py                # application service
  api/schemas.py
  api/router.py
```

```python
# domain/coupons.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

class CouponNotApplicable(Exception): ...
class CouponAlreadyRedeemed(Exception): ...

@dataclass(frozen=True)
class Money:
    amount: Decimal

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise CouponNotApplicable("amount must be positive")

@dataclass(frozen=True)
class CouponRedeemedEvent:
    coupon_id: UUID
    order_id: UUID
    discounted_amount: Decimal

class CouponRepository(ABC):
    @abstractmethod
    def get_active_for_update(self, code: str): ...
    @abstractmethod
    def exists_redemption(self, *, coupon_id: UUID, order_id: UUID) -> bool: ...
    @abstractmethod
    def save_redemption(self, *, coupon_id: UUID, order_id: UUID, amount: Decimal) -> None: ...
```

```python
# models.py
class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        FIXED = "fixed", "Fixed"
        PERCENT = "percent", "Percent"

    code = models.CharField(max_length=40, unique=True)
    status = models.CharField(max_length=20, choices=[("active", "Active"), ("expired", "Expired")])
    discount_type = models.CharField(max_length=20, choices=DiscountType)
    discount_value = models.DecimalField(max_digits=12, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()

    class Meta:
        indexes = [models.Index(fields=["code", "status"])]
        ordering = ["code"]

    def calculate_discount(self, order_amount: Decimal) -> Decimal:
        if self.status != "active" or order_amount < self.min_order_amount:
            raise CouponNotApplicable()
        if self.discount_type == self.DiscountType.FIXED:
            discount = self.discount_value
        else:
            discount = order_amount * self.discount_value / Decimal("100")
        return min(discount, self.max_discount_amount or discount, order_amount)

class CouponRedemption(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT)
    order_id = models.UUIDField()
    discounted_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["coupon", "order_id"], name="uniq_coupon_order")
        ]
```

```python
# repositories.py
class DjangoCouponRepository(CouponRepository):
    def get_active_for_update(self, code: str) -> Coupon:
        return Coupon.objects.select_for_update().get(code=code, status="active")

    def exists_redemption(self, *, coupon_id, order_id) -> bool:
        return CouponRedemption.objects.filter(coupon_id=coupon_id, order_id=order_id).exists()

    def save_redemption(self, *, coupon_id, order_id, amount) -> None:
        CouponRedemption.objects.create(
            coupon_id=coupon_id, order_id=order_id, discounted_amount=amount
        )
```

```python
# services.py
@dataclass
class ApplyCouponCommand:
    code: str
    order_id: UUID
    order_amount: Decimal

class CouponApplicationService:
    def __init__(self, repo: CouponRepository):
        self.repo = repo

    @transaction.atomic
    def apply_coupon(self, command: ApplyCouponCommand) -> Decimal:
        coupon = self.repo.get_active_for_update(command.code)
        if self.repo.exists_redemption(coupon_id=coupon.id, order_id=command.order_id):
            raise CouponAlreadyRedeemed()
        discount = coupon.calculate_discount(command.order_amount)
        self.repo.save_redemption(
            coupon_id=coupon.id,
            order_id=command.order_id,
            amount=discount,
        )
        return discount
```

```python
# api/schemas.py
class ApplyCouponIn(Schema):
    code: str
    order_id: UUID
    order_amount: Decimal

class ApplyCouponOut(Schema):
    discounted_amount: Decimal

# api/router.py
router = Router(tags=["coupons"])

@router.post("/coupons/apply", response={200: ApplyCouponOut}, auth=django_auth)
def apply_coupon(request, payload: ApplyCouponIn) -> ApplyCouponOut:
    service = CouponApplicationService(DjangoCouponRepository())
    amount = service.apply_coupon(ApplyCouponCommand(**payload.dict()))
    return ApplyCouponOut(discounted_amount=amount)
```

```python
# tests/test_apply_coupon.py
@pytest.mark.django_db
def test_red_coupon_rejects_below_minimum(coupon_factory):
    coupon_factory(code="SAVE10", min_order_amount=Decimal("50000"))

    with pytest.raises(CouponNotApplicable):
        CouponApplicationService(DjangoCouponRepository()).apply_coupon(
            ApplyCouponCommand("SAVE10", uuid4(), Decimal("30000"))
        )

@pytest.mark.django_db
def test_red_coupon_cannot_be_redeemed_twice_for_same_order(coupon_factory):
    order_id = uuid4()
    coupon_factory(code="SAVE10", discount_value=Decimal("1000"))

    service = CouponApplicationService(DjangoCouponRepository())
    service.apply_coupon(ApplyCouponCommand("SAVE10", order_id, Decimal("10000")))

    with pytest.raises(CouponAlreadyRedeemed):
        service.apply_coupon(ApplyCouponCommand("SAVE10", order_id, Decimal("10000")))
```

---
> **관련 스킬 참조:**
> - 도메인 경계와 애그리거트 정교화 → **architecture-ddd** 스킬
> - Django 모델/서비스/테스트 구체화 → **implementation-django** 스킬
> - API Schema/Router/Error 응답 구체화 → **implementation-django-ninja** 스킬