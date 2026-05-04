## [주요 내용]

현재 `/private/tmp/dddjango-codex-eval`은 빈 디렉터리이고 `config.toml`도 존재하지 않습니다. 또한 세션이 read-only라 파일 생성/수정 및 pytest 실행은 못 했습니다. 따라서 실행했다고 주장하지 않고, 실제 프로젝트에 옮길 수 있는 RED 테스트, 예상 실패, GREEN 최소 구현, REFACTOR 방향을 제공합니다.

전제: `Pricing` 바운디드 컨텍스트에서 `DiscountPolicy`는 Aggregate Root가 아니라 불변 Value Object입니다. 주문/쿠폰/프로모션 Aggregate Root가 이 정책을 소유하게 두는 구조가 맞습니다.

**RED: `tests/isolated/unit/test_discount_policy.py`**

```python
import pytest
from hypothesis import example, given
from hypothesis import strategies as st

from pricing.discount_policy import (
    DiscountPolicy,
    InvalidDiscountPolicyError,
    InvalidOrderAmountError,
)


@pytest.fixture
def ten_percent_policy():
    policy = DiscountPolicy(
        percent=10,
        minimum_order_amount=10_000,
        maximum_discount_amount=None,
    )
    yield policy


@pytest.fixture
def capped_discount_policy():
    policy = DiscountPolicy(
        percent=30,
        minimum_order_amount=10_000,
        maximum_discount_amount=5_000,
    )
    yield policy


def test_discount_policy_apply_when_order_amount_meets_minimum_returns_discounted_amount(ten_percent_policy):
    # Arrange
    order_amount = 20_000

    # Act
    discounted_amount = ten_percent_policy.apply(order_amount)

    # Assert
    assert discounted_amount == 18_000


def test_discount_policy_apply_when_order_amount_is_below_minimum_returns_original_amount(ten_percent_policy):
    # Arrange
    order_amount = 9_999

    # Act
    discounted_amount = ten_percent_policy.apply(order_amount)

    # Assert
    assert discounted_amount == 9_999


def test_discount_policy_apply_when_order_amount_equals_minimum_returns_discounted_amount(ten_percent_policy):
    # Arrange
    order_amount = 10_000

    # Act
    discounted_amount = ten_percent_policy.apply(order_amount)

    # Assert
    assert discounted_amount == 9_000


def test_discount_policy_apply_when_discount_exceeds_cap_returns_capped_discount(capped_discount_policy):
    # Arrange
    order_amount = 100_000

    # Act
    discounted_amount = capped_discount_policy.apply(order_amount)

    # Assert
    assert discounted_amount == 95_000


@pytest.mark.parametrize("percent", [-1, 101])
def test_discount_policy_create_when_percent_is_out_of_range_raises_invalid_discount_policy_error(percent):
    # Arrange / Act / Assert
    with pytest.raises(InvalidDiscountPolicyError, match="percent"):
        DiscountPolicy(percent=percent, minimum_order_amount=0, maximum_discount_amount=None)


@pytest.mark.parametrize("minimum_order_amount", [-1])
def test_discount_policy_create_when_minimum_order_amount_is_negative_raises_invalid_discount_policy_error(
    minimum_order_amount,
):
    # Arrange / Act / Assert
    with pytest.raises(InvalidDiscountPolicyError, match="minimum_order_amount"):
        DiscountPolicy(percent=10, minimum_order_amount=minimum_order_amount, maximum_discount_amount=None)


def test_discount_policy_apply_when_order_amount_is_negative_raises_invalid_order_amount_error(ten_percent_policy):
    # Arrange / Act / Assert
    with pytest.raises(InvalidOrderAmountError, match="order_amount"):
        ten_percent_policy.apply(-1)


@given(
    order_amount=st.integers(min_value=0, max_value=10_000_000),
    percent=st.integers(min_value=0, max_value=100),
)
@example(order_amount=0, percent=0)
@example(order_amount=1, percent=100)
@example(order_amount=10_000, percent=100)
def test_discount_policy_apply_when_valid_input_never_returns_negative_amount(order_amount, percent):
    # Arrange
    policy = DiscountPolicy(
        percent=percent,
        minimum_order_amount=0,
        maximum_discount_amount=None,
    )

    # Act
    discounted_amount = policy.apply(order_amount)

    # Assert
    assert 0 <= discounted_amount <= order_amount
```

**예상 실패 이유**

처음 RED 단계에서는 `pricing.discount_policy` 모듈, `DiscountPolicy`, `InvalidDiscountPolicyError`, `InvalidOrderAmountError`가 없어서 import 단계에서 실패해야 정상입니다. 테스트가 통과하면 이미 구현이 있거나 테스트가 잘못된 대상을 보고 있는 것입니다.

**GREEN: `pricing/discount_policy.py`**

```python
from dataclasses import dataclass


class DiscountPolicyError(Exception):
    """할인 정책 도메인 예외의 최상위 타입."""


class InvalidDiscountPolicyError(DiscountPolicyError):
    """할인 정책 불변식이 깨졌을 때 발생한다."""


class InvalidOrderAmountError(DiscountPolicyError):
    """할인 적용 대상 주문 금액이 유효하지 않을 때 발생한다."""


@dataclass(frozen=True, slots=True, kw_only=True)
class DiscountPolicy:
    """주문 금액에 정률 할인을 적용하는 불변 할인 정책.

    Invariants:
        percent는 0 이상 100 이하이다.
        minimum_order_amount는 0 이상이다.
        maximum_discount_amount는 None이거나 0 이상이다.
    """

    percent: int
    minimum_order_amount: int
    maximum_discount_amount: int | None = None

    def __post_init__(self) -> None:
        if not 0 <= self.percent <= 100:
            raise InvalidDiscountPolicyError("percent must be between 0 and 100")
        if self.minimum_order_amount < 0:
            raise InvalidDiscountPolicyError("minimum_order_amount must be greater than or equal to 0")
        if self.maximum_discount_amount is not None and self.maximum_discount_amount < 0:
            raise InvalidDiscountPolicyError("maximum_discount_amount must be greater than or equal to 0")

    def apply(self, order_amount: int) -> int:
        """주문 금액에 할인 정책을 적용한 최종 결제 금액을 반환한다."""
        if order_amount < 0:
            raise InvalidOrderAmountError("order_amount must be greater than or equal to 0")
        if order_amount < self.minimum_order_amount:
            return order_amount

        discount_amount = order_amount * self.percent // 100
        if self.maximum_discount_amount is not None:
            discount_amount = min(discount_amount, self.maximum_discount_amount)

        return order_amount - discount_amount
```

**REFACTOR 방향**

`DiscountPolicy`가 더 커지면 `Money` 값 객체를 추가해 원시 `int` 금액을 감싸고, 할인 방식이 정률/정액/무료배송으로 늘어나면 `RateDiscountPolicy`, `FixedAmountDiscountPolicy`처럼 정책 타입을 분리하세요. 쿠폰 발급 수량, 사용자별 사용 여부, 기간 조건은 이 값 객체에 넣지 말고 `Coupon` 또는 `Promotion` Aggregate Root의 불변식으로 이동하는 편이 좋습니다.

테스트 디렉터리는 `tests/isolated/unit/`처럼 환경 축을 먼저 두세요. `tests/isolated/`는 Fake, in-memory, 네트워크 차단, 고정 시계 기반의 결정적 테스트이고, `tests/real/`은 실제 DB/외부 서비스 검증용입니다.

실행 명령:

```bash
pytest tests/isolated/unit/test_discount_policy.py -q
pytest tests/isolated -q
pip install hypothesis pytest-randomly
pytest tests/isolated --randomly-seed=last -q
pip install mutmut
mutmut run --paths-to-mutate "pricing/" --tests-dir "tests/isolated/"
```

---
> **관련 스킬 참조:**
> - TDD Red-Green-Refactor → **implementation-tdd** 스킬
> - pytest fixture/edge case/property testing → **implementation-test** 스킬
> - DDD Value Object/Aggregate 경계 → **architecture-ddd** 스킬
> - Python dataclass/도메인 예외/타입 힌트 → **implementation-python** 스킬