사용한 스킬: `architecture-ddd`, `implementation-django`, `implementation-test`, `implementation-tdd`.

현재 `/private/tmp/dddjango-codex-eval`은 비어 있고 읽기 전용이라 파일 생성과 `pytest` 실행은 하지 못했습니다. 아래는 Django DB 없이 테스트 가능한 순수 도메인 정책 객체 기준의 RED → GREEN → REFACTOR 산출물입니다.

**RED 테스트**

`tests/isolated/unit/orders/test_discount_policy.py`

```python
from decimal import Decimal

import pytest

from apps.orders.domain.discounts import (
    DiscountKind,
    DiscountPolicy,
    InvalidDiscountPolicyError,
)


@pytest.fixture
def discount_policy_factory():
    def make(**overrides):
        values = {
            "kind": DiscountKind.PERCENTAGE,
            "value": Decimal("10"),
            "minimum_order_total": Decimal("10000"),
            "maximum_discount_amount": None,
            "is_active": True,
        }
        values.update(overrides)
        return DiscountPolicy(**values)

    yield make


def test_apply_discount_policy_amount_below_minimum_returns_original_total(
    discount_policy_factory,
):
    policy = discount_policy_factory()

    result = policy.apply_to(Decimal("9999"))

    assert result.discount_amount == Decimal("0.00")
    assert result.discounted_total == Decimal("9999.00")


def test_apply_discount_policy_amount_equal_minimum_applies_discount(
    discount_policy_factory,
):
    policy = discount_policy_factory()

    result = policy.apply_to(Decimal("10000"))

    assert result.discount_amount == Decimal("1000.00")
    assert result.discounted_total == Decimal("9000.00")


def test_apply_discount_policy_percentage_over_cap_limits_discount(
    discount_policy_factory,
):
    policy = discount_policy_factory(maximum_discount_amount=Decimal("1500"))

    result = policy.apply_to(Decimal("20000"))

    assert result.discount_amount == Decimal("1500.00")
    assert result.discounted_total == Decimal("18500.00")


def test_apply_discount_policy_fixed_discount_larger_than_total_never_negative(
    discount_policy_factory,
):
    policy = discount_policy_factory(
        kind=DiscountKind.FIXED_AMOUNT,
        value=Decimal("12000"),
        minimum_order_total=Decimal("0"),
    )

    result = policy.apply_to(Decimal("10000"))

    assert result.discount_amount == Decimal("10000.00")
    assert result.discounted_total == Decimal("0.00")


def test_apply_discount_policy_inactive_returns_original_total(discount_policy_factory):
    policy = discount_policy_factory(is_active=False)

    result = policy.apply_to(Decimal("10000"))

    assert result.discount_amount == Decimal("0.00")
    assert result.discounted_total == Decimal("10000.00")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("value", Decimal("0")),
        ("value", Decimal("-1")),
        ("minimum_order_total", Decimal("-1")),
        ("maximum_discount_amount", Decimal("-1")),
    ],
)
def test_create_discount_policy_invalid_money_value_raises_domain_error(
    discount_policy_factory,
    field,
    value,
):
    with pytest.raises(InvalidDiscountPolicyError):
        discount_policy_factory(**{field: value})


def test_create_discount_policy_percentage_above_100_raises_domain_error(
    discount_policy_factory,
):
    with pytest.raises(InvalidDiscountPolicyError):
        discount_policy_factory(value=Decimal("100.01"))
```

예상 실패: `apps.orders.domain.discounts` 모듈, `DiscountPolicy`, `DiscountKind`, `InvalidDiscountPolicyError`가 아직 없어서 import 단계에서 RED가 됩니다.

**GREEN 최소 구현**

`apps/orders/domain/discounts.py`

```python
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import StrEnum


class InvalidDiscountPolicyError(Exception):
    pass


class DiscountKind(StrEnum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"


@dataclass(frozen=True)
class DiscountApplication:
    original_total: Decimal
    discount_amount: Decimal
    discounted_total: Decimal


@dataclass(frozen=True)
class DiscountPolicy:
    """불변식: 할인값은 양수, 최소 주문금액은 0 이상, 최종 결제액은 음수가 될 수 없다."""

    kind: DiscountKind
    value: Decimal
    minimum_order_total: Decimal = Decimal("0")
    maximum_discount_amount: Decimal | None = None
    is_active: bool = True

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise InvalidDiscountPolicyError("discount value must be positive")
        if self.minimum_order_total < 0:
            raise InvalidDiscountPolicyError("minimum order total cannot be negative")
        if self.maximum_discount_amount is not None and self.maximum_discount_amount < 0:
            raise InvalidDiscountPolicyError("maximum discount cannot be negative")
        if self.kind == DiscountKind.PERCENTAGE and self.value > Decimal("100"):
            raise InvalidDiscountPolicyError("percentage discount cannot exceed 100")

    def apply_to(self, order_total: Decimal) -> DiscountApplication:
        original_total = _money(order_total)

        if order_total < 0:
            raise InvalidDiscountPolicyError("order total cannot be negative")

        if not self.is_active or original_total < self.minimum_order_total:
            return DiscountApplication(original_total, Decimal("0.00"), original_total)

        if self.kind == DiscountKind.PERCENTAGE:
            discount_amount = _money(original_total * self.value / Decimal("100"))
        else:
            discount_amount = _money(self.value)

        if self.maximum_discount_amount is not None:
            discount_amount = min(discount_amount, _money(self.maximum_discount_amount))

        discount_amount = min(discount_amount, original_total)
        discounted_total = _money(original_total - discount_amount)

        return DiscountApplication(original_total, discount_amount, discounted_total)


def _money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

**REFACTOR notes**

- Django `Model`이나 ORM 없이 `apps.orders.domain` 아래 순수 도메인 객체로 유지합니다.
- DB 저장 할인 쿠폰/프로모션이 필요해지면 Django 모델은 persistence DTO로 두고, 도메인 `DiscountPolicy`로 변환해서 테스트 경계를 유지합니다.
- 금액은 `Decimal`만 허용하고 float 입력은 애플리케이션 계층에서 차단하는 편이 좋습니다.
- 다음 edge case를 추가하면 좋습니다: `order_total < 0`, 소수점 반올림 `1000.005`, `maximum_discount_amount=0` 허용 여부, 정책 기간 만료 여부.

**pytest 명령**

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/unit/orders/test_discount_policy.py -q
pytest tests/isolated/unit/orders/test_discount_policy.py -q --randomly-seed=last
```

---
> **관련 스킬 참조:**
> - Django DB 저장 모델/서비스 연결 → **implementation-django** 스킬