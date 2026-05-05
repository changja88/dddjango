실행 불가: 현재 workspace가 `read-only`라 파일 생성/수정 및 `pytest` 실행은 하지 못했습니다. 아래 코드는 그대로 프로젝트에 옮겨 `RED -> GREEN -> REFACTOR` 순서로 적용할 수 있는 순수 도메인 예시입니다.

**RED 실패 테스트**

`tests/isolated/unit/coupons/test_coupon_discount_policy.py`

```python
from datetime import date

import pytest

from coupons.domain.coupon import (
    CouponAlreadyApplied,
    CouponExpired,
    CouponId,
    CouponPolicy,
    MinimumOrderAmountNotMet,
    Money,
)


def test_coupon_discount_policy_when_order_meets_all_conditions_returns_discount_result():
    # Arrange
    policy = CouponPolicy(
        coupon_id=CouponId("WELCOME10"),
        discount_rate=10,
        minimum_order_amount=Money(10_000),
        maximum_discount_amount=Money(5_000),
        expires_on=date(2026, 5, 31),
    )

    # Act
    result = policy.apply(
        order_amount=Money(30_000),
        applied_coupon_ids=set(),
        today=date(2026, 5, 5),
    )

    # Assert
    assert result.discount_amount == Money(3_000)
    assert result.payable_amount == Money(27_000)
    assert result.coupon_id == CouponId("WELCOME10")


def test_coupon_discount_policy_when_discount_exceeds_max_caps_discount_amount():
    # Arrange
    policy = CouponPolicy(CouponId("MAX5000"), 50, Money(10_000), Money(5_000), date(2026, 5, 31))

    # Act
    result = policy.apply(Money(30_000), set(), date(2026, 5, 5))

    # Assert
    assert result.discount_amount == Money(5_000)
    assert result.payable_amount == Money(25_000)


def test_coupon_discount_policy_when_order_amount_below_minimum_raises_domain_exception():
    # Arrange
    policy = CouponPolicy(CouponId("MIN10000"), 10, Money(10_000), Money(5_000), date(2026, 5, 31))

    # Act / Assert
    with pytest.raises(MinimumOrderAmountNotMet):
        policy.apply(Money(9_999), set(), date(2026, 5, 5))


def test_coupon_discount_policy_when_coupon_expired_raises_domain_exception():
    # Arrange
    policy = CouponPolicy(CouponId("OLD"), 10, Money(10_000), Money(5_000), date(2026, 5, 4))

    # Act / Assert
    with pytest.raises(CouponExpired):
        policy.apply(Money(10_000), set(), date(2026, 5, 5))


def test_coupon_discount_policy_when_coupon_already_applied_raises_domain_exception():
    # Arrange
    policy = CouponPolicy(CouponId("WELCOME10"), 10, Money(10_000), Money(5_000), date(2026, 5, 31))

    # Act / Assert
    with pytest.raises(CouponAlreadyApplied):
        policy.apply(Money(10_000), {CouponId("WELCOME10")}, date(2026, 5, 5))
```

**예상 실패 이유**

아직 `coupons.domain.coupon` 모듈, `Money`, `CouponId`, `CouponPolicy`, `DiscountResult`, 도메인 예외들이 없으므로 import 단계에서 실패합니다. 구현 후에는 금액 경계, 만료일 비교, 중복 쿠폰 검증이 누락된 순서대로 실패해야 정상입니다.

**GREEN 최소 구현**

`coupons/domain/coupon.py`

```python
from dataclasses import dataclass
from datetime import date


class CouponPolicyViolation(Exception):
    pass


class MinimumOrderAmountNotMet(CouponPolicyViolation):
    pass


class CouponExpired(CouponPolicyViolation):
    pass


class CouponAlreadyApplied(CouponPolicyViolation):
    pass


@dataclass(frozen=True)
class Money:
    amount: int

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("money cannot be negative")

    def percentage(self, rate: int) -> "Money":
        return Money(self.amount * rate // 100)

    def min(self, other: "Money") -> "Money":
        return self if self.amount <= other.amount else other

    def __sub__(self, other: "Money") -> "Money":
        return Money(self.amount - other.amount)


@dataclass(frozen=True)
class CouponId:
    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("coupon id is required")


@dataclass(frozen=True)
class DiscountResult:
    coupon_id: CouponId
    discount_amount: Money
    payable_amount: Money


@dataclass(frozen=True)
class CouponPolicy:
    """Aggregate Root: 쿠폰 할인 가능 여부와 할인 금액 불변식을 보호한다."""

    coupon_id: CouponId
    discount_rate: int
    minimum_order_amount: Money
    maximum_discount_amount: Money
    expires_on: date

    def apply(
        self,
        order_amount: Money,
        applied_coupon_ids: set[CouponId],
        today: date,
    ) -> DiscountResult:
        if self.coupon_id in applied_coupon_ids:
            raise CouponAlreadyApplied(self.coupon_id.value)

        if today > self.expires_on:
            raise CouponExpired(self.coupon_id.value)

        if order_amount.amount < self.minimum_order_amount.amount:
            raise MinimumOrderAmountNotMet(self.coupon_id.value)

        discount_amount = order_amount.percentage(self.discount_rate).min(
            self.maximum_discount_amount
        )

        return DiscountResult(
            coupon_id=self.coupon_id,
            discount_amount=discount_amount,
            payable_amount=order_amount - discount_amount,
        )
```

**REFACTOR 방향**

- `Value Object`: `Money`, `CouponId`는 유지하고 `DiscountRate`를 추가해 `0 < rate <= 100` 검증을 옮깁니다.
- `Domain Exception`: 현재는 정책 실패를 예외로 표현했습니다. API 계층에서는 예외를 HTTP 응답으로 변환하고, 도메인은 Django/Ninja 타입을 몰라야 합니다.
- `Result Type`: `DiscountResult`는 성공 결과 전용으로 유지합니다. 실패까지 값으로 다루고 싶으면 `CouponDiscountDecision(success, reason)`을 별도 도입합니다.
- 중복 사용 여부는 DB 조회가 아니라 `applied_coupon_ids`라는 도메인 입력으로 받습니다. Repository/transaction은 응용 서비스에서 주문 애그리거트를 로드할 때만 둡니다.

**엣지 케이스 목록**

최소 주문금액 정확히 같음, 만료일 당일 사용 가능, 할인액 0원 금지 여부, 할인율 100%, 최대 할인금액 0원 허용 여부, 주문금액 0원, 음수 금액, 빈 쿠폰 ID, 이미 적용된 쿠폰 재시도.

**pytest 명령**

```bash
pytest tests/isolated/unit/coupons/test_coupon_discount_policy.py -q
```

---
> **관련 스킬 참조:**
> - Django 응용 서비스와 Repository 경계 연결 → **implementation-django** 스킬