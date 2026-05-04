현재 `/private/tmp/dddjango-codex-eval`은 빈 디렉터리이고 읽기 전용 샌드박스라 파일을 직접 생성할 수 없었습니다. 아래 패치를 적용하면 pytest 기반 TDD 테스트와 할인 정책 객체 구현이 들어갑니다.

```diff
*** Begin Patch
*** Add File: discount_policy.py
+from dataclasses import dataclass
+from decimal import Decimal, ROUND_HALF_UP
+
+
+CENT = Decimal("0.01")
+
+
+def money(value: Decimal | int | str) -> Decimal:
+    amount = Decimal(str(value))
+    if amount < 0:
+        raise ValueError("amount must be greater than or equal to 0")
+    return amount.quantize(CENT, rounding=ROUND_HALF_UP)
+
+
+class DiscountPolicy:
+    def discount_for(self, subtotal: Decimal, *, quantity: int = 1) -> Decimal:
+        raise NotImplementedError
+
+    def apply(self, subtotal: Decimal, *, quantity: int = 1) -> Decimal:
+        subtotal = money(subtotal)
+        discount = self.discount_for(subtotal, quantity=quantity)
+        return money(max(Decimal("0"), subtotal - discount))
+
+
+@dataclass(frozen=True)
+class PercentageDiscountPolicy(DiscountPolicy):
+    rate: Decimal
+
+    def __post_init__(self) -> None:
+        rate = Decimal(str(self.rate))
+        if rate < 0 or rate > 1:
+            raise ValueError("rate must be between 0 and 1")
+        object.__setattr__(self, "rate", rate)
+
+    def discount_for(self, subtotal: Decimal, *, quantity: int = 1) -> Decimal:
+        return money(subtotal * self.rate)
+
+
+@dataclass(frozen=True)
+class FixedAmountDiscountPolicy(DiscountPolicy):
+    amount: Decimal
+
+    def __post_init__(self) -> None:
+        object.__setattr__(self, "amount", money(self.amount))
+
+    def discount_for(self, subtotal: Decimal, *, quantity: int = 1) -> Decimal:
+        return min(self.amount, money(subtotal))
+
+
+@dataclass(frozen=True)
+class QuantityTierDiscountPolicy(DiscountPolicy):
+    minimum_quantity: int
+    delegate: DiscountPolicy
+
+    def __post_init__(self) -> None:
+        if self.minimum_quantity < 1:
+            raise ValueError("minimum_quantity must be greater than 0")
+
+    def discount_for(self, subtotal: Decimal, *, quantity: int = 1) -> Decimal:
+        if quantity < 1:
+            raise ValueError("quantity must be greater than 0")
+        if quantity < self.minimum_quantity:
+            return Decimal("0.00")
+        return self.delegate.discount_for(subtotal, quantity=quantity)
+
+
+@dataclass(frozen=True)
+class BestDiscountPolicy(DiscountPolicy):
+    policies: tuple[DiscountPolicy, ...]
+
+    def __post_init__(self) -> None:
+        if not self.policies:
+            raise ValueError("policies must not be empty")
+
+    def discount_for(self, subtotal: Decimal, *, quantity: int = 1) -> Decimal:
+        return max(policy.discount_for(subtotal, quantity=quantity) for policy in self.policies)
*** Add File: tests/test_discount_policy.py
+from decimal import Decimal
+
+import pytest
+
+from discount_policy import (
+    BestDiscountPolicy,
+    FixedAmountDiscountPolicy,
+    PercentageDiscountPolicy,
+    QuantityTierDiscountPolicy,
+    money,
+)
+
+
+@pytest.fixture
+def subtotal():
+    return Decimal("100.00")
+
+
+@pytest.fixture
+def ten_percent_policy():
+    return PercentageDiscountPolicy(Decimal("0.10"))
+
+
+def test_percentage_discount_policy_applies_rate_to_subtotal(subtotal, ten_percent_policy):
+    assert ten_percent_policy.apply(subtotal) == Decimal("90.00")
+
+
+def test_percentage_discount_policy_rounds_to_nearest_cent():
+    policy = PercentageDiscountPolicy(Decimal("0.155"))
+
+    assert policy.apply(Decimal("10.00")) == Decimal("8.45")
+
+
+@pytest.mark.parametrize("rate", [Decimal("-0.01"), Decimal("1.01")])
+def test_percentage_discount_policy_rejects_rate_outside_zero_to_one(rate):
+    with pytest.raises(ValueError, match="rate"):
+        PercentageDiscountPolicy(rate)
+
+
+def test_fixed_amount_discount_policy_subtracts_fixed_amount(subtotal):
+    policy = FixedAmountDiscountPolicy(Decimal("15.00"))
+
+    assert policy.apply(subtotal) == Decimal("85.00")
+
+
+def test_fixed_amount_discount_policy_never_makes_total_negative():
+    policy = FixedAmountDiscountPolicy(Decimal("150.00"))
+
+    assert policy.apply(Decimal("100.00")) == Decimal("0.00")
+
+
+def test_fixed_amount_discount_policy_rejects_negative_amount():
+    with pytest.raises(ValueError, match="amount"):
+        FixedAmountDiscountPolicy(Decimal("-1.00"))
+
+
+def test_quantity_tier_discount_policy_applies_delegate_when_quantity_matches_threshold(
+    subtotal, ten_percent_policy
+):
+    policy = QuantityTierDiscountPolicy(minimum_quantity=3, delegate=ten_percent_policy)
+
+    assert policy.apply(subtotal, quantity=3) == Decimal("90.00")
+
+
+def test_quantity_tier_discount_policy_skips_delegate_below_threshold(
+    subtotal, ten_percent_policy
+):
+    policy = QuantityTierDiscountPolicy(minimum_quantity=3, delegate=ten_percent_policy)
+
+    assert policy.apply(subtotal, quantity=2) == Decimal("100.00")
+
+
+@pytest.mark.parametrize("quantity", [0, -1])
+def test_quantity_tier_discount_policy_rejects_non_positive_quantity(
+    subtotal, ten_percent_policy, quantity
+):
+    policy = QuantityTierDiscountPolicy(minimum_quantity=3, delegate=ten_percent_policy)
+
+    with pytest.raises(ValueError, match="quantity"):
+        policy.apply(subtotal, quantity=quantity)
+
+
+def test_best_discount_policy_applies_largest_available_discount(subtotal):
+    policy = BestDiscountPolicy(
+        (
+            PercentageDiscountPolicy(Decimal("0.10")),
+            FixedAmountDiscountPolicy(Decimal("20.00")),
+        )
+    )
+
+    assert policy.apply(subtotal) == Decimal("80.00")
+
+
+def test_best_discount_policy_rejects_empty_policy_list():
+    with pytest.raises(ValueError, match="policies"):
+        BestDiscountPolicy(())
+
+
+def test_money_rejects_negative_subtotal():
+    with pytest.raises(ValueError, match="amount"):
+        money(Decimal("-0.01"))
*** End Patch
```

실행 명령:

```bash
pytest
```

검증은 수행하지 못했습니다. 현재 디렉터리가 빈 상태이고, 세션 권한이 읽기 전용이라 파일 생성 및 테스트 실행 환경 구성이 불가능했습니다.