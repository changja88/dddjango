현재 `/private/tmp/dddjango-codex-eval`은 파일이 없고, 세션이 읽기 전용이라 실제 파일 생성은 못 했습니다. 아래가 그대로 적용할 수 있는 RED/GREEN/REFACTOR 최소 구현입니다.

**RED: 테스트 먼저**

`tests/test_coupon_policy.py`

```python
from datetime import date
from decimal import Decimal

import pytest

from coupons.domain import CouponPolicy, CouponCannotBeApplied


def test_coupon_requires_minimum_order_amount():
    coupon = CouponPolicy(
        discount_rate=Decimal("0.10"),
        minimum_order_amount=Decimal("10000"),
        maximum_discount_amount=Decimal("3000"),
        expires_on=date(2026, 5, 31),
    )

    with pytest.raises(CouponCannotBeApplied, match="minimum order amount"):
        coupon.calculate_discount(
            order_amount=Decimal("9000"),
            today=date(2026, 5, 5),
        )


def test_coupon_discount_is_capped_by_maximum_discount_amount():
    coupon = CouponPolicy(
        discount_rate=Decimal("0.10"),
        minimum_order_amount=Decimal("10000"),
        maximum_discount_amount=Decimal("3000"),
        expires_on=date(2026, 5, 31),
    )

    discount = coupon.calculate_discount(
        order_amount=Decimal("50000"),
        today=date(2026, 5, 5),
    )

    assert discount == Decimal("3000")


def test_coupon_cannot_be_used_after_expiration_date():
    coupon = CouponPolicy(
        discount_rate=Decimal("0.10"),
        minimum_order_amount=Decimal("10000"),
        maximum_discount_amount=Decimal("3000"),
        expires_on=date(2026, 5, 4),
    )

    with pytest.raises(CouponCannotBeApplied, match="expired"):
        coupon.calculate_discount(
            order_amount=Decimal("10000"),
            today=date(2026, 5, 5),
        )


def test_coupon_can_be_used_on_expiration_date():
    coupon = CouponPolicy(
        discount_rate=Decimal("0.10"),
        minimum_order_amount=Decimal("10000"),
        maximum_discount_amount=Decimal("3000"),
        expires_on=date(2026, 5, 5),
    )

    discount = coupon.calculate_discount(
        order_amount=Decimal("10000"),
        today=date(2026, 5, 5),
    )

    assert discount == Decimal("1000")


def test_coupon_cannot_be_combined_with_another_coupon():
    coupon = CouponPolicy(
        discount_rate=Decimal("0.10"),
        minimum_order_amount=Decimal("10000"),
        maximum_discount_amount=Decimal("3000"),
        expires_on=date(2026, 5, 31),
        combinable=False,
    )

    with pytest.raises(CouponCannotBeApplied, match="combined"):
        coupon.calculate_discount(
            order_amount=Decimal("10000"),
            today=date(2026, 5, 5),
            already_applied_coupon=True,
        )
```

**GREEN: 최소 구현**

`coupons/domain.py`

```python
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_DOWN


class CouponCannotBeApplied(Exception):
    pass


@dataclass(frozen=True)
class CouponPolicy:
    discount_rate: Decimal
    minimum_order_amount: Decimal
    maximum_discount_amount: Decimal
    expires_on: date
    combinable: bool = False

    def calculate_discount(
        self,
        *,
        order_amount: Decimal,
        today: date,
        already_applied_coupon: bool = False,
    ) -> Decimal:
        if order_amount < self.minimum_order_amount:
            raise CouponCannotBeApplied("minimum order amount is not satisfied")

        if today > self.expires_on:
            raise CouponCannotBeApplied("coupon is expired")

        if already_applied_coupon and not self.combinable:
            raise CouponCannotBeApplied("coupon cannot be combined")

        discount = (order_amount * self.discount_rate).quantize(
            Decimal("1"),
            rounding=ROUND_DOWN,
        )

        return min(discount, self.maximum_discount_amount)
```

`coupons/__init__.py`

```python
```

실행:

```bash
pytest
```

**REFACTOR**

현재는 순수 도메인 정책으로 충분히 작아서 과한 분리는 하지 않는 게 맞습니다. 다만 호출부 인자가 늘어나면 아래처럼 요청 값을 명시적인 값 객체로 묶을 수 있습니다.

```python
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class CouponApplication:
    order_amount: Decimal
    today: date
    already_applied_coupon: bool = False
```

그다음 `calculate_discount(application: CouponApplication)` 형태로 바꾸면 호출부 의도가 더 분명해집니다. 지금 단계에서는 테스트가 정책을 잘 고정하고 있으므로 GREEN 구현만으로도 충분합니다.