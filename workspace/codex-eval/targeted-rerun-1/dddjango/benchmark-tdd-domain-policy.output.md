읽기 전용 빈 workspace라 파일 생성과 `pytest` 실행은 하지 못했습니다. 아래 코드는 Django DB 없이 순수 도메인 정책으로 테스트 가능한 TDD 산출물입니다. 사용 스킬: `architecture-ddd`, `implementation-django`, `implementation-django-ninja`, `implementation-tdd`, `implementation-test`.

**RED 테스트**

`tests/isolated/unit/test_discount_policy.py`

```python
import pytest

from apps.orders.domain.discounts import (
    DiscountAmountError,
    DiscountPolicy,
    DiscountRateError,
    Money,
)


@pytest.fixture
def subtotal_30000():
    return Money(cents=30_000)


@pytest.fixture
def ten_percent_max_5000_policy():
    return DiscountPolicy(name="WELCOME10", rate_percent=10, max_discount=Money(5_000))


def test_discount_policy_valid_subtotal_applies_percentage_discount(
    subtotal_30000, ten_percent_max_5000_policy
):
    result = ten_percent_max_5000_policy.apply(subtotal_30000)

    assert result.discount == Money(3_000)
    assert result.payable == Money(27_000)


def test_discount_policy_discount_over_max_discount_is_capped():
    policy = DiscountPolicy(name="WELCOME50", rate_percent=50, max_discount=Money(5_000))

    result = policy.apply(Money(30_000))

    assert result.discount == Money(5_000)
    assert result.payable == Money(25_000)


def test_discount_policy_zero_subtotal_returns_zero_discount(ten_percent_max_5000_policy):
    result = ten_percent_max_5000_policy.apply(Money(0))

    assert result.discount == Money(0)
    assert result.payable == Money(0)


@pytest.mark.parametrize("rate_percent", [-1, 101])
def test_discount_policy_rate_outside_0_to_100_raises_domain_error(rate_percent):
    with pytest.raises(DiscountRateError):
        DiscountPolicy(name="INVALID", rate_percent=rate_percent, max_discount=Money(5_000))


@pytest.mark.parametrize("cents", [-1, -100])
def test_money_negative_cents_raises_domain_error(cents):
    with pytest.raises(DiscountAmountError):
        Money(cents=cents)


def test_discount_policy_repeated_apply_is_idempotent(ten_percent_max_5000_policy):
    subtotal = Money(30_000)

    first = ten_percent_max_5000_policy.apply(subtotal)
    second = ten_percent_max_5000_policy.apply(subtotal)

    assert first == second
    assert subtotal == Money(30_000)
```

**예상 실패**

아직 `apps.orders.domain.discounts` 모듈, `Money`, `DiscountPolicy`, 도메인 예외, 결과 타입이 없으므로 import 단계에서 실패해야 합니다.

**GREEN 최소 구현**

`apps/orders/domain/discounts.py`

```python
from dataclasses import dataclass


class DiscountDomainError(Exception):
    pass


class DiscountAmountError(DiscountDomainError):
    pass


class DiscountRateError(DiscountDomainError):
    pass


@dataclass(frozen=True)
class Money:
    cents: int

    def __post_init__(self) -> None:
        if self.cents < 0:
            raise DiscountAmountError("money cannot be negative")


@dataclass(frozen=True)
class DiscountResult:
    original: Money
    discount: Money
    payable: Money


@dataclass(frozen=True)
class DiscountPolicy:
    """
    Domain Policy, not an Aggregate Root.
    Invariants:
    - rate_percent is 0..100 inclusive.
    - max_discount cannot be negative because it is Money.
    - apply() never mutates subtotal and never returns negative payable.
    """

    name: str
    rate_percent: int
    max_discount: Money

    def __post_init__(self) -> None:
        if not 0 <= self.rate_percent <= 100:
            raise DiscountRateError("rate_percent must be between 0 and 100")

    def apply(self, subtotal: Money) -> DiscountResult:
        calculated = subtotal.cents * self.rate_percent // 100
        discount_cents = min(calculated, self.max_discount.cents, subtotal.cents)
        discount = Money(discount_cents)

        return DiscountResult(
            original=subtotal,
            discount=discount,
            payable=Money(subtotal.cents - discount.cents),
        )
```

**REFACTOR 메모**

이 정책은 Django `Model`, ORM, Repository에 의존하지 않는 순수 도메인 객체입니다. 주문 생성/결제 use case에서는 응용 서비스가 `Order` Aggregate에 `DiscountPolicy.apply()` 결과를 전달하고, DB 저장은 Repository 또는 Django service layer에서 `transaction.atomic()` 경계 안에 둡니다. API가 필요하면 DRF가 아니라 Django Ninja `Schema`에서 cents를 입출력 값으로 변환하세요.

**검증 명령**

```bash
pytest tests/isolated/unit/test_discount_policy.py -q
```

Django settings가 필요한 프로젝트라면:

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/unit/test_discount_policy.py -q
```

---
> **관련 스킬 참조:**
> - Django DB 없는 도메인 정책 테스트 → **implementation-tdd** 스킬
> - 도메인 객체 경계와 불변식 설계 → **architecture-ddd** 스킬