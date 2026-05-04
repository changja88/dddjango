**[주요 내용]**

쿠폰은 `Coupons` 바운디드 컨텍스트로 두고, 주문 금액은 `Orders` 컨텍스트에서 넘어온 스냅샷만 사용합니다. 핵심 원칙은 `Coupon.can_apply()` 같은 Django model method에 정책을 몰아넣지 않고, 할인 계산과 사용 가능성 판단을 도메인 `Policy Object`/`Domain Service`로 분리하는 것입니다.

| 유비쿼터스 언어 | 의미 | 금지 동의어 |
|---|---|---|
| Coupon | 발급된 할인 수단 | DiscountModel, PromoData |
| DiscountPolicy | 할인 계산 규칙 | model method, helper |
| MinimumOrderAmount | 적용 가능한 최소 주문 금액 | min_price |
| CouponRedemption | 쿠폰 사용 기록 | coupon_log, usage_row |
| DuplicateUseRestriction | 중복 사용 제한 | is_used flag only |

```python
# apps/coupons/domain/model/coupon.py
from dataclasses import dataclass
from decimal import Decimal
from abc import ABC, abstractmethod


class CouponPolicyError(Exception): ...


class MinimumOrderAmountNotMet(CouponPolicyError): ...


class DuplicateCouponUseNotAllowed(CouponPolicyError): ...


class InvalidDiscountPolicy(CouponPolicyError): ...


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "KRW"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money cannot be negative")

    def min(self, other: "Money") -> "Money":
        self._ensure_same_currency(other)
        return self if self.amount <= other.amount else other

    def _ensure_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")


@dataclass(frozen=True)
class CouponId:
    value: str


@dataclass(frozen=True)
class CustomerId:
    value: str


@dataclass(frozen=True)
class OrderSnapshot:
    order_id: str
    customer_id: CustomerId
    total: Money


@dataclass(frozen=True)
class Coupon:
    """
    Aggregate Root.
    Invariants:
    - 할인 정책은 유효한 금액/비율만 가진다.
    - 최소 주문 금액 미만 주문에는 적용될 수 없다.
    - 중복 사용 제한은 CouponUsagePolicy를 통해 일관되게 판단한다.
    """
    id: CouponId
    discount_policy: "DiscountPolicy"
    minimum_order_amount: Money
    duplicate_restriction: "DuplicateUseRestriction"


@dataclass(frozen=True)
class CouponRedeemedEvent:
    coupon_id: CouponId
    customer_id: CustomerId
    order_id: str
    discount_amount: Money
```

할인 계산은 정책 객체로 분리합니다.

```python
# apps/coupons/domain/policies.py
class DiscountPolicy(ABC):
    @abstractmethod
    def calculate(self, order_total: Money) -> Money: ...


@dataclass(frozen=True)
class FixedAmountDiscountPolicy(DiscountPolicy):
    amount: Money

    def calculate(self, order_total: Money) -> Money:
        self.amount._ensure_same_currency(order_total)
        return self.amount.min(order_total)


@dataclass(frozen=True)
class PercentageDiscountPolicy(DiscountPolicy):
    rate: Decimal
    max_discount: Money | None = None

    def __post_init__(self):
        if self.rate <= 0 or self.rate > 100:
            raise InvalidDiscountPolicy("rate must be 0 < rate <= 100")

    def calculate(self, order_total: Money) -> Money:
        discount = Money(order_total.amount * self.rate / Decimal("100"), order_total.currency)
        return discount.min(self.max_discount) if self.max_discount else discount


@dataclass(frozen=True)
class DuplicateUseRestriction:
    once_per_customer: bool = True
    once_per_order: bool = True
```

중복 사용은 과거 사용 이력이 필요하므로 엔티티 단독 메서드보다 도메인 서비스가 맞습니다.

```python
# apps/coupons/domain/services.py
class CouponRedemptionRepository(ABC):
    @abstractmethod
    def exists_for_customer(self, coupon_id: CouponId, customer_id: CustomerId) -> bool: ...

    @abstractmethod
    def exists_for_order(self, coupon_id: CouponId, order_id: str) -> bool: ...

    @abstractmethod
    def save_redemption(self, event: CouponRedeemedEvent) -> None: ...


class CouponApplicationPolicy:
    def __init__(self, redemptions: CouponRedemptionRepository):
        self.redemptions = redemptions

    def apply(self, coupon: Coupon, order: OrderSnapshot) -> CouponRedeemedEvent:
        if order.total.amount < coupon.minimum_order_amount.amount:
            raise MinimumOrderAmountNotMet()

        restriction = coupon.duplicate_restriction
        if restriction.once_per_customer and self.redemptions.exists_for_customer(
            coupon.id, order.customer_id
        ):
            raise DuplicateCouponUseNotAllowed()

        if restriction.once_per_order and self.redemptions.exists_for_order(
            coupon.id, order.order_id
        ):
            raise DuplicateCouponUseNotAllowed()

        discount = coupon.discount_policy.calculate(order.total)
        return CouponRedeemedEvent(coupon.id, order.customer_id, order.order_id, discount)
```

Django 쪽은 얇게 둡니다. `CouponModel`은 저장 구조와 ORM 제약을 담당하고, 정책 판단은 `CouponApplicationPolicy`가 담당합니다. Application Service는 트랜잭션과 Repository 조율만 합니다.

```python
# apps/coupons/application/services.py
from django.db import transaction

class ApplyCouponService:
    def __init__(self, coupons, redemptions):
        self.coupons = coupons
        self.redemptions = redemptions

    @transaction.atomic
    def apply_coupon(self, coupon_id: str, order: OrderSnapshot) -> CouponRedeemedEvent:
        coupon = self.coupons.find_by_id(CouponId(coupon_id))
        event = CouponApplicationPolicy(self.redemptions).apply(coupon, order)
        self.redemptions.save_redemption(event)
        return event
```

검증은 pytest로 정책 edge case를 직접 때리는 방식이 좋습니다.

```python
def test_fixed_discount_cannot_exceed_order_total():
    policy = FixedAmountDiscountPolicy(Money(Decimal("10000")))
    assert policy.calculate(Money(Decimal("7000"))).amount == Decimal("7000")


def test_percentage_discount_with_max_discount():
    policy = PercentageDiscountPolicy(Decimal("20"), Money(Decimal("3000")))
    assert policy.calculate(Money(Decimal("50000"))).amount == Decimal("3000")


def test_minimum_order_amount_blocks_coupon(redemptions):
    coupon = coupon_fixture(minimum_order_amount=Money(Decimal("30000")))
    order = OrderSnapshot("o1", CustomerId("c1"), Money(Decimal("10000")))

    with pytest.raises(MinimumOrderAmountNotMet):
        CouponApplicationPolicy(redemptions).apply(coupon, order)


def test_duplicate_customer_use_is_blocked(redemptions):
    redemptions.exists_for_customer.return_value = True

    with pytest.raises(DuplicateCouponUseNotAllowed):
        CouponApplicationPolicy(redemptions).apply(coupon_fixture(), order_fixture())
```

검증 명령은 `pytest apps/coupons/tests/domain/test_coupon_policies.py`로 두고, Django ORM 어댑터 테스트는 별도로 `pytest.mark.django_db`를 붙여 Repository 저장/조회만 확인하면 됩니다.

---
> **관련 스킬 참조:**
> - Django 모델/서비스/pytest 구현 → **implementation-django** 스킬
> - Repository, Application Service, 의존성 방향 구체화 → **architecture-implementation-patterns** 스킬