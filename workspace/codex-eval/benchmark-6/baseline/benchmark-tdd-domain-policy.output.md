지정된 `/Users/hyun/Desktop/dddjango/none` fixture는 없어서, 읽을 수 있는 실제 fixture인 `/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop` 기준으로 작성했습니다. 읽기 전용이라 파일은 수정하지 않았고, 아래 diff를 적용하면 됩니다.

```diff
diff --git a/shop/orders/test_discounts.py b/shop/orders/test_discounts.py
new file mode 100644
index 0000000..c2d2c7a
--- /dev/null
+++ b/shop/orders/test_discounts.py
@@ -0,0 +1,68 @@
+from decimal import Decimal
+
+import pytest
+
+from shop.orders.discounts import DiscountPolicy
+
+
+@pytest.fixture
+def money():
+    def as_decimal(value: str) -> Decimal:
+        return Decimal(value)
+
+    return as_decimal
+
+
+@pytest.fixture
+def ten_percent_policy(money):
+    return DiscountPolicy(
+        percentage=money("10"),
+        minimum_order_amount=money("100.00"),
+    )
+
+
+def test_discount_policy_returns_zero_when_subtotal_is_below_minimum(
+    ten_percent_policy,
+    money,
+):
+    assert ten_percent_policy.calculate_discount(money("99.99")) == money("0.00")
+
+
+def test_discount_policy_applies_percentage_when_subtotal_meets_minimum(
+    ten_percent_policy,
+    money,
+):
+    assert ten_percent_policy.calculate_discount(money("100.00")) == money("10.00")
+
+
+def test_discount_policy_keeps_payable_amount_from_going_below_zero(money):
+    policy = DiscountPolicy(percentage=money("100"))
+
+    assert policy.apply_to(money("15.00")) == money("0.00")
+
+
+def test_discount_policy_caps_discount_with_max_discount_amount(money):
+    policy = DiscountPolicy(
+        percentage=money("50"),
+        minimum_order_amount=money("100.00"),
+        max_discount_amount=money("30.00"),
+    )
+
+    assert policy.calculate_discount(money("100.00")) == money("30.00")
+
+
+@pytest.mark.parametrize(
+    "subtotal, expected_discount",
+    [
+        ("0.00", "0.00"),
+        ("100.00", "10.00"),
+        ("100.05", "10.01"),
+    ],
+)
+def test_discount_policy_handles_boundary_and_rounding_cases(
+    ten_percent_policy,
+    money,
+    subtotal,
+    expected_discount,
+):
+    assert ten_percent_policy.calculate_discount(money(subtotal)) == money(expected_discount)
+
+
+def test_discount_policy_rejects_negative_subtotal(money):
+    policy = DiscountPolicy(percentage=money("10"))
+
+    with pytest.raises(ValueError, match="subtotal cannot be negative"):
+        policy.calculate_discount(money("-1.00"))
+
+
+@pytest.mark.parametrize("percentage", ["-0.01", "100.01"])
+def test_discount_policy_rejects_invalid_percentage(money, percentage):
+    with pytest.raises(ValueError, match="percentage must be between 0 and 100"):
+        DiscountPolicy(percentage=money(percentage))
diff --git a/shop/orders/discounts.py b/shop/orders/discounts.py
new file mode 100644
index 0000000..66ccfd1
--- /dev/null
+++ b/shop/orders/discounts.py
@@ -0,0 +1,57 @@
+from dataclasses import dataclass
+from decimal import Decimal, ROUND_HALF_UP
+
+
+CENT = Decimal("0.01")
+
+
+@dataclass(frozen=True)
+class DiscountPolicy:
+    percentage: Decimal
+    minimum_order_amount: Decimal = Decimal("0.00")
+    max_discount_amount: Decimal | None = None
+
+    def __post_init__(self) -> None:
+        percentage = self._to_money(self.percentage)
+        minimum_order_amount = self._to_money(self.minimum_order_amount)
+        max_discount_amount = (
+            None
+            if self.max_discount_amount is None
+            else self._to_money(self.max_discount_amount)
+        )
+
+        if percentage < Decimal("0") or percentage > Decimal("100"):
+            raise ValueError("percentage must be between 0 and 100")
+        if minimum_order_amount < Decimal("0.00"):
+            raise ValueError("minimum order amount cannot be negative")
+        if max_discount_amount is not None and max_discount_amount < Decimal("0.00"):
+            raise ValueError("max discount amount cannot be negative")
+
+        object.__setattr__(self, "percentage", percentage)
+        object.__setattr__(self, "minimum_order_amount", minimum_order_amount)
+        object.__setattr__(self, "max_discount_amount", max_discount_amount)
+
+    def calculate_discount(self, subtotal: Decimal) -> Decimal:
+        subtotal = self._to_money(subtotal)
+        if subtotal < Decimal("0.00"):
+            raise ValueError("subtotal cannot be negative")
+        if subtotal < self.minimum_order_amount:
+            return Decimal("0.00")
+
+        discount = (subtotal * self.percentage / Decimal("100")).quantize(
+            CENT,
+            rounding=ROUND_HALF_UP,
+        )
+
+        if self.max_discount_amount is not None:
+            discount = min(discount, self.max_discount_amount)
+
+        return min(discount, subtotal)
+
+    def apply_to(self, subtotal: Decimal) -> Decimal:
+        subtotal = self._to_money(subtotal)
+        discount = self.calculate_discount(subtotal)
+        return (subtotal - discount).quantize(CENT, rounding=ROUND_HALF_UP)
+
+    @staticmethod
+    def _to_money(value: Decimal) -> Decimal:
+        return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)
```

테스트는 `pytest shop/orders/test_discounts.py`로 실행하는 전제입니다. 포함한 edge case는 최소 주문금액 미만, 최소 주문금액 경계값, 반올림, 최대 할인 한도, 100% 할인 시 0원 보장, 음수 subtotal, 잘못된 할인율입니다.