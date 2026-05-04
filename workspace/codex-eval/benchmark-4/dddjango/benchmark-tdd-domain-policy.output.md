읽기 전용 workspace라 파일 생성/수정과 pytest 실행은 하지 못했습니다. 아래는 그대로 옮겨서 시작할 수 있는 RED → GREEN → REFACTOR 산출물입니다. Django ORM 없이 순수 도메인 객체만 테스트합니다.

**RED 테스트**

`tests/isolated/unit/pricing/test_discount_policy.py`

```python
from decimal import Decimal

import pytest

from apps.pricing.domain.discount import DiscountPolicy, InvalidDiscountPolicy


@pytest.fixture
def ten_percent_policy():
    return DiscountPolicy(
        rate=Decimal("0.10"),
        minimum_order_total=Decimal("10000"),
        max_discount=Decimal("5000"),
    )


@pytest.mark.parametrize(
    ("order_total", "expected_discount"),
    [
        (Decimal("10000"), Decimal("1000")),
        (Decimal("49999"), Decimal("4999")),
        (Decimal("50000"), Decimal("5000")),
        (Decimal("9999"), Decimal("0")),
        (Decimal("0"), Decimal("0")),
    ],
)
def test_discount_policy_order_total_boundary_returns_expected_discount(
    ten_percent_policy, order_total, expected_discount
):
    # Arrange
    policy = ten_percent_policy

    # Act
    discount = policy.calculate_discount(order_total)

    # Assert
    assert discount == expected_discount


@pytest.mark.parametrize(
    ("rate", "minimum_order_total", "max_discount"),
    [
        (Decimal("-0.01"), Decimal("10000"), Decimal("5000")),
        (Decimal("1.01"), Decimal("10000"), Decimal("5000")),
        (Decimal("0.10"), Decimal("-1"), Decimal("5000")),
        (Decimal("0.10"), Decimal("10000"), Decimal("-1")),
    ],
)
def test_discount_policy_invalid_invariant_raises_domain_error(
    rate, minimum_order_total, max_discount
):
    # Arrange / Act / Assert
    with pytest.raises(InvalidDiscountPolicy):
        DiscountPolicy(
            rate=rate,
            minimum_order_total=minimum_order_total,
            max_discount=max_discount,
        )


def test_discount_policy_negative_order_total_raises_domain_error(ten_percent_policy):
    # Arrange
    policy = ten_percent_policy

    # Act / Assert
    with pytest.raises(InvalidDiscountPolicy):
        policy.calculate_discount(Decimal("-1"))
```

**예상 실패**

아직 `apps.pricing.domain.discount.DiscountPolicy`와 `InvalidDiscountPolicy`가 없으므로 import error로 실패해야 합니다. 이미 클래스가 있다면, 경계값/불변식 실패가 RED 신호입니다.

**GREEN 최소 구현**

`apps/pricing/domain/discount.py`

```python
from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN


class InvalidDiscountPolicy(Exception):
    pass


@dataclass(frozen=True)
class DiscountPolicy:
    """
    Aggregate Root: DiscountPolicy

    Invariants:
    - rate는 0 이상 1 이하의 Decimal 비율이다.
    - minimum_order_total과 max_discount는 음수일 수 없다.
    - 주문 금액이 minimum_order_total 미만이면 할인은 0이다.
    - 계산된 할인은 max_discount를 초과할 수 없다.
    - Django DB/ORM에 의존하지 않는다.
    """

    rate: Decimal
    minimum_order_total: Decimal
    max_discount: Decimal

    def __post_init__(self):
        if self.rate < Decimal("0") or self.rate > Decimal("1"):
            raise InvalidDiscountPolicy("discount rate must be between 0 and 1")
        if self.minimum_order_total < Decimal("0"):
            raise InvalidDiscountPolicy("minimum order total cannot be negative")
        if self.max_discount < Decimal("0"):
            raise InvalidDiscountPolicy("max discount cannot be negative")

    def calculate_discount(self, order_total: Decimal) -> Decimal:
        if order_total < Decimal("0"):
            raise InvalidDiscountPolicy("order total cannot be negative")
        if order_total < self.minimum_order_total:
            return Decimal("0")

        discount = (order_total * self.rate).quantize(
            Decimal("1"),
            rounding=ROUND_DOWN,
        )
        return min(discount, self.max_discount)
```

**REFACTOR notes**

도메인이 커지면 `Money`와 `DiscountRate`를 `frozen=True` 값 객체로 분리하세요. Django 모델에는 정책 ID, rate, cap 같은 영속 데이터만 두고, 할인 계산은 이 도메인 객체에 위임합니다. API나 service layer는 `DiscountPolicy.calculate_discount()`를 호출만 해야 하며 DB fixture 없이 isolated unit test로 유지합니다.

**pytest 명령**

```bash
pytest tests/isolated/unit/pricing/test_discount_policy.py -q
```

---
> **관련 스킬 참조:**
> - Django DB 없는 도메인 정책 테스트 → **implementation-test** 스킬