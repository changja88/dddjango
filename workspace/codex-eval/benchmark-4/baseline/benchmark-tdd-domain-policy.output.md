**[주요 내용]**

작업 디렉터리가 비어 있고 현재 샌드박스가 읽기 전용이라 파일 생성과 `pytest` 실행은 하지 못했습니다. 아래는 그대로 배치하면 되는 TDD 산출물입니다.

**RED: `tests/isolated/unit/test_discount_policy.py`**

```python
from decimal import Decimal

import pytest

from discounts.policy import (
    DiscountPolicy,
    DiscountRate,
    InvalidDiscountRateError,
    InvalidMoneyError,
)


@pytest.fixture
def ten_percent_policy() -> DiscountPolicy:
    return DiscountPolicy(rate=DiscountRate.percent(10))


@pytest.fixture
def minimum_order_policy() -> DiscountPolicy:
    return DiscountPolicy(rate=DiscountRate.percent(10), minimum_order_amount=Decimal("100.00"))


@pytest.fixture
def capped_policy() -> DiscountPolicy:
    return DiscountPolicy(rate=DiscountRate.percent(20), maximum_discount_amount=Decimal("30.00"))


def test_apply_to_regular_order_returns_discounted_total(ten_percent_policy):
    order_amount = Decimal("100.00")

    discounted_total = ten_percent_policy.apply_to(order_amount)

    assert discounted_total == Decimal("90.00")


def test_apply_to_zero_amount_returns_zero(ten_percent_policy):
    order_amount = Decimal("0.00")

    discounted_total = ten_percent_policy.apply_to(order_amount)

    assert discounted_total == Decimal("0.00")


def test_apply_to_amount_below_minimum_order_returns_original_total(minimum_order_policy):
    order_amount = Decimal("99.99")

    discounted_total = minimum_order_policy.apply_to(order_amount)

    assert discounted_total == Decimal("99.99")


def test_apply_to_amount_equal_to_minimum_order_returns_discounted_total(minimum_order_policy):
    order_amount = Decimal("100.00")

    discounted_total = minimum_order_policy.apply_to(order_amount)

    assert discounted_total == Decimal("90.00")


def test_apply_to_discount_over_cap_returns_total_with_capped_discount(capped_policy):
    order_amount = Decimal("200.00")

    discounted_total = capped_policy.apply_to(order_amount)

    assert discounted_total == Decimal("170.00")


@pytest.mark.parametrize(
    ("order_amount", "expected_total"),
    [(Decimal("10.005"), Decimal("9.00")), (Decimal("10.015"), Decimal("9.01"))],
)
def test_apply_to_fractional_cent_amount_returns_half_up_rounded_total(order_amount, expected_total):
    policy = DiscountPolicy(rate=DiscountRate.percent(10))

    discounted_total = policy.apply_to(order_amount)

    assert discounted_total == expected_total


def test_apply_to_negative_amount_raises_invalid_money_error(ten_percent_policy):
    with pytest.raises(InvalidMoneyError):
        ten_percent_policy.apply_to(Decimal("-0.01"))


@pytest.mark.parametrize("invalid_rate", [Decimal("-0.01"), Decimal("1.01")])
def test_create_discount_rate_outside_supported_range_raises_invalid_discount_rate_error(invalid_rate):
    with pytest.raises(InvalidDiscountRateError):
        DiscountRate(invalid_rate)
```

**GREEN: `discounts/policy.py`**

```python
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


class DiscountPolicyError(Exception):
    pass


class InvalidMoneyError(DiscountPolicyError):
    pass


class InvalidDiscountRateError(DiscountPolicyError):
    pass


@dataclass(frozen=True)
class DiscountRate:
    """Value Object invariant: rate must be between 0 and 1 inclusive."""

    value: Decimal

    def __post_init__(self) -> None:
        if not self.value.is_finite() or self.value < Decimal("0") or self.value > Decimal("1"):
            raise InvalidDiscountRateError("discount rate must be between 0 and 1")

    @classmethod
    def percent(cls, percent: int | str | Decimal) -> "DiscountRate":
        return cls(Decimal(percent) / Decimal("100"))


@dataclass(frozen=True)
class DiscountPolicy:
    """Aggregate Root invariant: discounted total never becomes negative."""

    rate: DiscountRate
    minimum_order_amount: Decimal = Decimal("0")
    maximum_discount_amount: Decimal | None = None

    def __post_init__(self) -> None:
        _ensure_valid_money(self.minimum_order_amount)
        if self.maximum_discount_amount is not None:
            _ensure_valid_money(self.maximum_discount_amount)

    def apply_to(self, order_amount: Decimal) -> Decimal:
        _ensure_valid_money(order_amount)

        if order_amount < self.minimum_order_amount:
            return _money(order_amount)

        discount_amount = order_amount * self.rate.value
        if self.maximum_discount_amount is not None:
            discount_amount = min(discount_amount, self.maximum_discount_amount)

        return _money(order_amount - discount_amount)


def _ensure_valid_money(amount: Decimal) -> None:
    if not amount.is_finite() or amount < Decimal("0"):
        raise InvalidMoneyError("money must be finite and non-negative")


def _money(amount: Decimal) -> Decimal:
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

**REFACTOR 방향**

- `DiscountRate`는 값 객체로 유지하고, 퍼센트/비율 입력 정책을 명확히 분리합니다.
- 정책이 많아지면 `PercentageDiscountPolicy`, `FixedAmountDiscountPolicy`, `NoDiscountPolicy`로 전략 객체를 나눕니다.
- Django 앱에 붙일 경우 ORM 모델에는 저장만 맡기고, 계산 규칙은 이 도메인 객체에 둡니다.

실행 명령:

```bash
pytest tests/isolated/unit/test_discount_policy.py -q
```

---
> **관련 스킬 참조:**
> - pytest fixture/edge case 설계 → **implementation-test** 스킬
> - Red-Green-Refactor 개발 흐름 → **implementation-tdd** 스킬