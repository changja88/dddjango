지정 경로는 없어서 실제 fixture는 `/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop` 기준으로 읽었습니다. read-only라 직접 수정하지 않고, 적용 가능한 unified diff로 제공합니다.

```diff
diff --git a/shop/orders/discounts.py b/shop/orders/discounts.py
new file mode 100644
index 0000000..8f4f92a
--- /dev/null
+++ b/shop/orders/discounts.py
@@ -0,0 +1,63 @@
+from dataclasses import dataclass
+from decimal import Decimal, ROUND_HALF_UP
+
+
+CENT = Decimal("0.01")
+ZERO_MONEY = Decimal("0.00")
+
+
+def _to_money(value) -> Decimal:
+    return Decimal(str(value)).quantize(CENT)
+
+
+def _to_decimal(value) -> Decimal:
+    return Decimal(str(value))
+
+
+@dataclass(frozen=True)
+class DiscountPolicy:
+    percentage_rate: Decimal = Decimal("0")
+    fixed_amount: Decimal = ZERO_MONEY
+    minimum_order_amount: Decimal = ZERO_MONEY
+
+    def __post_init__(self) -> None:
+        percentage_rate = _to_decimal(self.percentage_rate)
+        fixed_amount = _to_money(self.fixed_amount)
+        minimum_order_amount = _to_money(self.minimum_order_amount)
+
+        if percentage_rate < 0 or percentage_rate > 100:
+            raise ValueError("percentage_rate must be between 0 and 100")
+        if fixed_amount < 0:
+            raise ValueError("fixed_amount must be greater than or equal to 0")
+        if minimum_order_amount < 0:
+            raise ValueError("minimum_order_amount must be greater than or equal to 0")
+
+        object.__setattr__(self, "percentage_rate", percentage_rate)
+        object.__setattr__(self, "fixed_amount", fixed_amount)
+        object.__setattr__(self, "minimum_order_amount", minimum_order_amount)
+
+    @classmethod
+    def none(cls) -> "DiscountPolicy":
+        return cls()
+
+    @classmethod
+    def percentage(cls, rate, *, minimum_order_amount=ZERO_MONEY) -> "DiscountPolicy":
+        return cls(
+            percentage_rate=rate,
+            minimum_order_amount=minimum_order_amount,
+        )
+
+    @classmethod
+    def fixed(cls, amount, *, minimum_order_amount=ZERO_MONEY) -> "DiscountPolicy":
+        return cls(
+            fixed_amount=amount,
+            minimum_order_amount=minimum_order_amount,
+        )
+
+    def discount_amount(self, subtotal) -> Decimal:
+        subtotal = _to_money(subtotal)
+        if subtotal < 0:
+            raise ValueError("subtotal must be greater than or equal to 0")
+        if subtotal < self.minimum_order_amount:
+            return ZERO_MONEY
+
+        percentage_discount = (subtotal * self.percentage_rate / Decimal("100")).quantize(
+            CENT,
+            rounding=ROUND_HALF_UP,
+        )
+        return min(subtotal, percentage_discount + self.fixed_amount).quantize(CENT)
+
+    def discounted_total(self, subtotal) -> Decimal:
+        subtotal = _to_money(subtotal)
+        return (subtotal - self.discount_amount(subtotal)).quantize(CENT)
diff --git a/shop/orders/test_discount_policy.py b/shop/orders/test_discount_policy.py
new file mode 100644
index 0000000..9de1c53
--- /dev/null
+++ b/shop/orders/test_discount_policy.py
@@ -0,0 +1,79 @@
+from decimal import Decimal
+
+import pytest
+
+from shop.orders.discounts import DiscountPolicy
+
+
+@pytest.fixture
+def subtotal():
+    return Decimal("100.00")
+
+
+@pytest.fixture
+def percentage_10_policy():
+    return DiscountPolicy.percentage("10")
+
+
+@pytest.fixture
+def fixed_15_policy():
+    return DiscountPolicy.fixed("15.00")
+
+
+def test_percentage_discount_returns_discounted_total(percentage_10_policy, subtotal):
+    assert percentage_10_policy.discount_amount(subtotal) == Decimal("10.00")
+    assert percentage_10_policy.discounted_total(subtotal) == Decimal("90.00")
+
+
+def test_fixed_discount_returns_discounted_total(fixed_15_policy, subtotal):
+    assert fixed_15_policy.discount_amount(subtotal) == Decimal("15.00")
+    assert fixed_15_policy.discounted_total(subtotal) == Decimal("85.00")
+
+
+def test_zero_discount_policy_returns_original_total(subtotal):
+    policy = DiscountPolicy.none()
+
+    assert policy.discount_amount(subtotal) == Decimal("0.00")
+    assert policy.discounted_total(subtotal) == Decimal("100.00")
+
+
+def test_fixed_discount_never_reduces_total_below_zero():
+    policy = DiscountPolicy.fixed("150.00")
+
+    assert policy.discount_amount("100.00") == Decimal("100.00")
+    assert policy.discounted_total("100.00") == Decimal("0.00")
+
+
+def test_policy_is_not_applied_below_minimum_order_amount():
+    policy = DiscountPolicy.percentage("10", minimum_order_amount="100.00")
+
+    assert policy.discount_amount("99.99") == Decimal("0.00")
+    assert policy.discounted_total("99.99") == Decimal("99.99")
+
+
+def test_policy_is_applied_at_minimum_order_amount_boundary():
+    policy = DiscountPolicy.percentage("10", minimum_order_amount="100.00")
+
+    assert policy.discount_amount("100.00") == Decimal("10.00")
+    assert policy.discounted_total("100.00") == Decimal("90.00")
+
+
+def test_percentage_discount_rounds_to_cents_half_up():
+    policy = DiscountPolicy.percentage("12.5")
+
+    assert policy.discount_amount("10.01") == Decimal("1.25")
+    assert policy.discounted_total("10.01") == Decimal("8.76")
+
+
+@pytest.mark.parametrize("rate", ["-0.01", "100.01"])
+def test_percentage_rate_must_be_between_zero_and_one_hundred(rate):
+    with pytest.raises(ValueError, match="percentage_rate"):
+        DiscountPolicy.percentage(rate)
+
+
+@pytest.mark.parametrize(
+    "factory",
+    [
+        lambda: DiscountPolicy.fixed("-0.01"),
+        lambda: DiscountPolicy.percentage("10", minimum_order_amount="-0.01"),
+    ],
+)
+def test_money_inputs_cannot_be_negative(factory):
+    with pytest.raises(ValueError):
+        factory()
+
+
+def test_negative_subtotal_is_rejected(percentage_10_policy):
+    with pytest.raises(ValueError, match="subtotal"):
+        percentage_10_policy.discounted_total("-0.01")
```

핵심은 `Order` 모델에 계산 로직을 넣지 않고 `shop.orders.discounts.DiscountPolicy`를 순수 객체로 둔 점입니다. pytest fixture는 `subtotal`, `percentage_10_policy`, `fixed_15_policy`를 포함했고, edge case는 최소 주문 금액 경계, 초과 할인 방지, 반올림, 잘못된 비율/금액, 음수 subtotal까지 커버했습니다.