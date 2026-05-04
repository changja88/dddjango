**[주요 내용]**

쿠폰은 `Promotion/Coupon` 바운디드 컨텍스트로 분리하고, 주문 컨텍스트의 `Order`는 `OrderId`, `Money`, `subtotal` 같은 published language만 제공받는 구조가 적절합니다. 할인 계산과 사용 가능성 판단은 Django `Coupon` model method에 몰아넣지 말고, 순수 도메인 `Policy Object`와 `Domain Service`로 둡니다. Django model은 저장/조회 어댑터 역할에 가깝게 유지합니다.

| 용어 | 의미 | 금지 동의어 |
|---|---|---|
| Coupon | 발급된 쿠폰 정의 | Discount, Voucher 혼용 |
| DiscountPolicy | 할인액 계산 규칙 | model method |
| RedemptionPolicy | 사용 가능성 규칙 | validation util |
| MinimumOrderAmount | 최소 주문 금액 | min_price |
| ExclusiveCoupon | 중복 사용 불가 쿠폰 | duplicate flag |

핵심 설계는 다음 정도면 충분합니다.

```python
# promotions/domain/model/coupon/policies.py
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


class CouponCannotBeApplied(Exception):
    pass


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "KRW"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money cannot be negative")

    def min(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise CouponCannotBeApplied("currency mismatch")
        return self if self.amount <= other.amount else other


class DiscountPolicy(Protocol):
    minimum_order_amount: Money

    def calculate(self, order_amount: Money) -> Money: ...


@dataclass(frozen=True)
class FixedAmountDiscountPolicy:
    fixed_amount: Money
    minimum_order_amount: Money

    def calculate(self, order_amount: Money) -> Money:
        if order_amount.amount < self.minimum_order_amount.amount:
            raise CouponCannotBeApplied("minimum order amount not met")
        return self.fixed_amount.min(order_amount)


@dataclass(frozen=True)
class PercentageDiscountPolicy:
    rate: Decimal
    minimum_order_amount: Money

    def __post_init__(self):
        if self.rate <= 0 or self.rate > 1:
            raise ValueError("rate must be between 0 and 1")

    def calculate(self, order_amount: Money) -> Money:
        if order_amount.amount < self.minimum_order_amount.amount:
            raise CouponCannotBeApplied("minimum order amount not met")
        return Money(order_amount.amount * self.rate, order_amount.currency)
```

```python
# promotions/domain/model/coupon/coupon.py
from dataclasses import dataclass
from uuid import UUID


@dataclass
class Coupon:
    """
    Aggregate Root invariant:
    - 할인액은 주문 금액을 초과할 수 없다.
    - minimum_order_amount 미만 주문에는 적용할 수 없다.
    - exclusive=True 쿠폰은 같은 주문의 다른 쿠폰과 함께 사용할 수 없다.
    """
    id: UUID
    policy: DiscountPolicy
    exclusive: bool = True
    version: int = 0

    def discount_for(self, order_amount: Money) -> Money:
        return self.policy.calculate(order_amount)
```

```python
# promotions/domain/services/redemption_policy.py
from typing import Protocol
from uuid import UUID


class CouponRedemptionHistory(Protocol):
    def has_redeemed(self, user_id: UUID, coupon_id: UUID) -> bool: ...


class CouponRedemptionPolicy:
    def __init__(self, history: CouponRedemptionHistory):
        self.history = history

    def assert_applicable(
        self,
        *,
        user_id: UUID,
        coupon: Coupon,
        existing_coupon_ids: list[UUID],
    ) -> None:
        if self.history.has_redeemed(user_id, coupon.id):
            raise CouponCannotBeApplied("coupon already redeemed by user")

        if coupon.exclusive and existing_coupon_ids:
            raise CouponCannotBeApplied("exclusive coupon cannot be combined")
```

```python
# promotions/application/apply_coupon.py
from typing import Protocol
from uuid import UUID


class CouponRepository(Protocol):
    def find_by_id(self, coupon_id: UUID) -> Coupon: ...


class ApplyCouponService:
    def __init__(
        self,
        coupons: CouponRepository,
        redemption_policy: CouponRedemptionPolicy,
    ):
        self.coupons = coupons
        self.redemption_policy = redemption_policy

    def apply(
        self,
        *,
        user_id: UUID,
        coupon_id: UUID,
        order_amount: Money,
        existing_coupon_ids: list[UUID],
    ) -> Money:
        coupon = self.coupons.find_by_id(coupon_id)
        self.redemption_policy.assert_applicable(
            user_id=user_id,
            coupon=coupon,
            existing_coupon_ids=existing_coupon_ids,
        )
        return coupon.discount_for(order_amount)
```

Django 쪽은 `CouponModel.discount_type`, `fixed_amount`, `rate`, `minimum_order_amount`, `exclusive`를 저장하고, repository adapter에서 도메인 `Coupon`과 `DiscountPolicy`로 변환합니다. 즉 `models.py`에 `calculate_discount()` 같은 정책 중심 메서드를 계속 추가하지 않습니다.

**검증**

pytest는 정책 edge case 중심으로 둡니다.

```python
def test_fixed_discount_cannot_exceed_order_amount():
    policy = FixedAmountDiscountPolicy(Money(Decimal("10000")), Money(Decimal("0")))
    assert policy.calculate(Money(Decimal("7000"))).amount == Decimal("7000")


def test_percentage_discount_requires_valid_rate():
    with pytest.raises(ValueError):
        PercentageDiscountPolicy(Decimal("1.5"), Money(Decimal("0")))


def test_minimum_order_amount_is_required():
    policy = FixedAmountDiscountPolicy(Money(Decimal("1000")), Money(Decimal("10000")))
    with pytest.raises(CouponCannotBeApplied):
        policy.calculate(Money(Decimal("9000")))


def test_exclusive_coupon_rejects_combination(history):
    coupon = Coupon(id=uuid4(), policy=FixedAmountDiscountPolicy(...), exclusive=True)
    service = CouponRedemptionPolicy(history)
    with pytest.raises(CouponCannotBeApplied):
        service.assert_applicable(
            user_id=uuid4(),
            coupon=coupon,
            existing_coupon_ids=[uuid4()],
        )
```

실행 기준은 `pytest tests/promotions/domain -q`로 도메인 정책 테스트가 DB 없이 통과하는 것입니다.

---
> **관련 스킬 참조:**
> - Django repository adapter/API 구현 → **implementation-django** 스킬