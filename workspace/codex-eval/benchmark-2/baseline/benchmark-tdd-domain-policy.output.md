작업 디렉터리 `/private/tmp/dddjango-codex-eval`이 비어 있고 현재 세션이 읽기 전용이라 파일 생성과 `pytest` 실행은 하지 못했습니다. 대신 바로 옮길 수 있는 TDD 산출물로 정리합니다.

**RED 테스트**

`tests/isolated/unit/test_discount_policy.py`

```python
from decimal import Decimal

import pytest

from apps.orders.discounts import DiscountPolicy, InvalidDiscountPolicy


@pytest.fixture
def fixed_amount_policy():
    return DiscountPolicy.fixed_amount(Decimal("3000"))


@pytest.fixture
def percent_policy():
    return DiscountPolicy.percent(Decimal("10"))


def test_apply_fixed_amount_discount_when_order_total_is_greater_than_discount_returns_reduced_total(fixed_amount_policy):
    # Arrange
    order_total = Decimal("10000")

    # Act
    discounted_total = fixed_amount_policy.apply(order_total)

    # Assert
    assert discounted_total == Decimal("7000")


def test_apply_fixed_amount_discount_when_discount_exceeds_order_total_returns_zero(fixed_amount_policy):
    # Arrange
    order_total = Decimal("2000")

    # Act
    discounted_total = fixed_amount_policy.apply(order_total)

    # Assert
    assert discounted_total == Decimal("0")


def test_apply_percent_discount_when_order_total_is_positive_returns_percent_reduced_total(percent_policy):
    # Arrange
    order_total = Decimal("10000")

    # Act
    discounted_total = percent_policy.apply(order_total)

    # Assert
    assert discounted_total == Decimal("9000")


@pytest.mark.parametrize("rate", [Decimal("-1"), Decimal("101")])
def test_create_percent_policy_when_rate_is_out_of_range_raises_invalid_policy(rate):
    # Arrange / Act / Assert
    with pytest.raises(InvalidDiscountPolicy):
        DiscountPolicy.percent(rate)


@pytest.mark.parametrize("amount", [Decimal("-1"), Decimal("0")])
def test_create_fixed_amount_policy_when_amount_is_not_positive_raises_invalid_policy(amount):
    # Arrange / Act / Assert
    with pytest.raises(InvalidDiscountPolicy):
        DiscountPolicy.fixed_amount(amount)


def test_apply_discount_when_order_total_is_negative_raises_invalid_policy(percent_policy):
    # Arrange
    order_total = Decimal("-1000")

    # Act / Assert
    with pytest.raises(InvalidDiscountPolicy):
        percent_policy.apply(order_total)
```

예상 RED 실패: `apps.orders.discounts.DiscountPolicy`와 `InvalidDiscountPolicy`가 아직 없으므로 import 단계에서 실패해야 합니다.

**GREEN 최소 구현**

`apps/orders/discounts.py`

```python
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class InvalidDiscountPolicy(ValueError):
    pass


class DiscountType(StrEnum):
    FIXED_AMOUNT = "fixed_amount"
    PERCENT = "percent"


@dataclass(frozen=True)
class DiscountPolicy:
    discount_type: DiscountType
    value: Decimal

    @classmethod
    def fixed_amount(cls, amount: Decimal) -> "DiscountPolicy":
        if amount <= Decimal("0"):
            raise InvalidDiscountPolicy("Fixed discount amount must be positive.")
        return cls(discount_type=DiscountType.FIXED_AMOUNT, value=amount)

    @classmethod
    def percent(cls, rate: Decimal) -> "DiscountPolicy":
        if rate < Decimal("0") or rate > Decimal("100"):
            raise InvalidDiscountPolicy("Percent discount rate must be between 0 and 100.")
        return cls(discount_type=DiscountType.PERCENT, value=rate)

    def apply(self, order_total: Decimal) -> Decimal:
        if order_total < Decimal("0"):
            raise InvalidDiscountPolicy("Order total must not be negative.")

        if self.discount_type == DiscountType.FIXED_AMOUNT:
            return max(Decimal("0"), order_total - self.value)

        discount_amount = order_total * self.value / Decimal("100")
        return max(Decimal("0"), order_total - discount_amount)
```

실행 명령:

```bash
pytest tests/isolated/unit/test_discount_policy.py -q
```

**REFACTOR 방향**

그린 이후에는 `DiscountPolicy`를 쿠폰 모델이나 주문 모델에 직접 묶기보다 순수 도메인 객체로 유지하는 게 좋습니다. DB가 필요한 쿠폰 조회는 selector/service에서 처리하고, 할인 계산은 이 객체가 담당하게 분리하면 테스트가 빠르고 안정적입니다.

---
> **관련 스킬 참조:**
> - Django 도메인 서비스/selector 분리 → **implementation-django** 스킬
> - pytest fixture와 edge case 확장 → **implementation-test** 스킬
> - Red-Green-Refactor 반복 개발 → **implementation-tdd** 스킬