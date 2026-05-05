지정된 fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, 현재 workspace에도 파일이 없습니다. read-only sandbox라 파일 생성/pytest 실행은 못 했습니다. 아래 diff는 RED 테스트를 먼저 추가하고, 그 뒤 GREEN 최소 구현을 추가하는 형태입니다.

**RED**
예상 실패: `apps.discounts.domain.discount_policy` 모듈이 없어 `ModuleNotFoundError`가 납니다.

```diff
diff --git a/tests/isolated/unit/test_discount_policy.py b/tests/isolated/unit/test_discount_policy.py
new file mode 100644
index 0000000..b7a2a41
--- /dev/null
+++ b/tests/isolated/unit/test_discount_policy.py
@@ -0,0 +1,86 @@
+from decimal import Decimal
+
+import pytest
+
+from apps.discounts.domain.discount_policy import (
+    DiscountPolicy,
+    InvalidDiscountPolicy,
+    InvalidSubtotal,
+)
+
+
+@pytest.fixture
+def fifteen_percent_over_10000_with_3000_cap():
+    policy = DiscountPolicy(
+        rate=Decimal("0.15"),
+        minimum_subtotal=Decimal("10000"),
+        maximum_discount=Decimal("3000"),
+    )
+    yield policy
+
+
+def test_discount_policy_when_subtotal_is_below_minimum_returns_zero(
+    fifteen_percent_over_10000_with_3000_cap,
+):
+    # Arrange
+    subtotal = Decimal("9999")
+
+    # Act
+    discount = fifteen_percent_over_10000_with_3000_cap.calculate_for(subtotal)
+
+    # Assert
+    assert discount == Decimal("0")
+
+
+def test_discount_policy_when_subtotal_equals_minimum_applies_discount(
+    fifteen_percent_over_10000_with_3000_cap,
+):
+    # Arrange
+    subtotal = Decimal("10000")
+
+    # Act
+    discount = fifteen_percent_over_10000_with_3000_cap.calculate_for(subtotal)
+
+    # Assert
+    assert discount == Decimal("1500")
+
+
+def test_discount_policy_when_raw_discount_exceeds_cap_returns_maximum_discount(
+    fifteen_percent_over_10000_with_3000_cap,
+):
+    # Arrange
+    subtotal = Decimal("50000")
+
+    # Act
+    discount = fifteen_percent_over_10000_with_3000_cap.calculate_for(subtotal)
+
+    # Assert
+    assert discount == Decimal("3000")
+
+
+def test_discount_policy_when_cap_is_larger_than_subtotal_never_exceeds_subtotal():
+    # Arrange
+    policy = DiscountPolicy(
+        rate=Decimal("1.00"),
+        minimum_subtotal=Decimal("0"),
+        maximum_discount=Decimal("10000"),
+    )
+
+    # Act
+    discount = policy.calculate_for(Decimal("7000"))
+
+    # Assert
+    assert discount == Decimal("7000")
+
+
+@pytest.mark.parametrize("rate", [Decimal("-0.01"), Decimal("1.01")])
+def test_discount_policy_when_rate_is_out_of_range_raises_invalid_policy(rate):
+    # Arrange / Act / Assert
+    with pytest.raises(InvalidDiscountPolicy):
+        DiscountPolicy(
+            rate=rate,
+            minimum_subtotal=Decimal("10000"),
+            maximum_discount=Decimal("3000"),
+        )
+
+
+def test_discount_policy_when_subtotal_is_negative_raises_invalid_subtotal(
+    fifteen_percent_over_10000_with_3000_cap,
+):
+    # Arrange / Act / Assert
+    with pytest.raises(InvalidSubtotal):
+        fifteen_percent_over_10000_with_3000_cap.calculate_for(Decimal("-1"))
diff --git a/apps/discounts/domain/discount_policy.py b/apps/discounts/domain/discount_policy.py
new file mode 100644
index 0000000..e1f9f61
--- /dev/null
+++ b/apps/discounts/domain/discount_policy.py
@@ -0,0 +1,52 @@
+from dataclasses import dataclass
+from decimal import Decimal, ROUND_DOWN
+
+
+class DiscountPolicyError(Exception):
+    pass
+
+
+class InvalidDiscountPolicy(DiscountPolicyError):
+    pass
+
+
+class InvalidSubtotal(DiscountPolicyError):
+    pass
+
+
+@dataclass(frozen=True)
+class DiscountPolicy:
+    """Django DB와 분리된 순수 도메인 할인 정책.
+
+    불변식:
+    - 할인율은 0 이상 1 이하이다.
+    - 최소 주문 금액과 최대 할인 금액은 음수일 수 없다.
+    - 계산된 할인 금액은 주문 금액을 초과할 수 없다.
+    """
+
+    rate: Decimal
+    minimum_subtotal: Decimal
+    maximum_discount: Decimal
+
+    def __post_init__(self) -> None:
+        if self.rate < Decimal("0") or self.rate > Decimal("1"):
+            raise InvalidDiscountPolicy("rate must be between 0 and 1")
+        if self.minimum_subtotal < Decimal("0"):
+            raise InvalidDiscountPolicy("minimum_subtotal must not be negative")
+        if self.maximum_discount < Decimal("0"):
+            raise InvalidDiscountPolicy("maximum_discount must not be negative")
+
+    def calculate_for(self, subtotal: Decimal) -> Decimal:
+        if subtotal < Decimal("0"):
+            raise InvalidSubtotal("subtotal must not be negative")
+        if subtotal < self.minimum_subtotal:
+            return Decimal("0")
+
+        raw_discount = self._money(subtotal * self.rate)
+        capped_discount = min(raw_discount, self.maximum_discount)
+        return min(capped_discount, subtotal)
+
+    def _money(self, amount: Decimal) -> Decimal:
+        return amount.quantize(Decimal("1"), rounding=ROUND_DOWN)
diff --git a/pyproject.toml b/pyproject.toml
new file mode 100644
index 0000000..d67bca2
--- /dev/null
+++ b/pyproject.toml
@@ -0,0 +1,6 @@
+[tool.pytest.ini_options]
+testpaths = ["tests/isolated", "tests/real"]
+python_files = ["test_*.py"]
```

**GREEN**
위 구현은 Django 모델/ORM/import 없이 `Decimal`과 frozen dataclass만 사용합니다. 그래서 할인 정책은 DB 없이 단위 테스트로 검증되고, Django 모델은 나중에 이 정책에 값만 전달하면 됩니다.

**REFACTOR**
다음 단계에서는 `DiscountPolicy`를 DB 모델에서 직접 상속하거나 호출하지 말고, Django 쪽에 `DiscountPolicyFactory` 또는 application service를 둬서 DB 레코드 값을 순수 도메인 객체로 변환하세요. 쿠폰/회원등급/상품별 정책이 늘어나면 같은 `calculate_for(subtotal)` 계약을 유지하는 정책 객체 조합으로 확장하면 됩니다.

**검증 명령**
실행은 못 했습니다. 적용 후 아래 순서로 확인하세요.

```bash
pytest tests/isolated/unit/test_discount_policy.py -q
pytest tests/isolated -q
```

---
> **관련 스킬 참조:**
> - Django DB 없는 도메인 정책 분리 → **architecture-ddd** 스킬
> - pytest fixture와 isolated 테스트 구조 → **implementation-test** 스킬
> - Red-Green-Refactor 진행 → **implementation-tdd** 스킬