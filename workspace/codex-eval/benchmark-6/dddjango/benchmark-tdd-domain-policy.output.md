**[주요 내용]**

Fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, 현재 workspace도 비어 있어 pytest 실행과 파일 편집은 하지 못했습니다. 아래는 Django DB 없이 테스트 가능한 순수 도메인 객체를 TDD 순서로 적용하는 unified diff입니다.

**RED: 먼저 추가할 실패 테스트**

```diff
diff --git a/tests/isolated/unit/discounts/test_discount_policy.py b/tests/isolated/unit/discounts/test_discount_policy.py
new file mode 100644
--- /dev/null
+++ b/tests/isolated/unit/discounts/test_discount_policy.py
@@ -0,0 +1,72 @@
+from decimal import Decimal
+
+import pytest
+
+from apps.discounts.domain.discount_policy import (
+    DiscountPolicy,
+    InvalidDiscountPolicyError,
+    InvalidMoneyError,
+    Money,
+)
+
+
+@pytest.fixture
+def capped_vip_policy():
+    policy = DiscountPolicy.percentage(
+        rate=Decimal("0.10"),
+        min_order_amount=Money("10000"),
+        max_discount_amount=Money("3000"),
+    )
+    yield policy
+
+
+def test_discount_policy_subtotal_meets_minimum_applies_percentage_discount_capped(capped_vip_policy):
+    subtotal = Money("50000")
+
+    result = capped_vip_policy.apply_to(subtotal)
+
+    assert result.discount_amount == Money("3000")
+    assert result.payable_amount == Money("47000")
+
+
+def test_discount_policy_subtotal_below_minimum_returns_zero_discount(capped_vip_policy):
+    subtotal = Money("9999")
+
+    result = capped_vip_policy.apply_to(subtotal)
+
+    assert result.discount_amount == Money("0")
+    assert result.payable_amount == Money("9999")
+
+
+def test_discount_policy_subtotal_zero_returns_zero_discount(capped_vip_policy):
+    subtotal = Money("0")
+
+    result = capped_vip_policy.apply_to(subtotal)
+
+    assert result.discount_amount == Money("0")
+    assert result.payable_amount == Money("0")
+
+
+def test_discount_policy_fixed_discount_exceeds_subtotal_never_makes_payable_negative():
+    policy = DiscountPolicy.fixed(discount_amount=Money("5000"))
+
+    result = policy.apply_to(Money("3000"))
+
+    assert result.discount_amount == Money("3000")
+    assert result.payable_amount == Money("0")
+
+
+def test_discount_policy_negative_subtotal_raises_invalid_money_error():
+    with pytest.raises(InvalidMoneyError):
+        Money("-1")
+
+
+def test_discount_policy_percentage_rate_greater_than_one_raises_invalid_discount_policy_error():
+    with pytest.raises(InvalidDiscountPolicyError):
+        DiscountPolicy.percentage(rate=Decimal("1.01"))
+
+
+def test_discount_policy_currency_mismatch_raises_invalid_discount_policy_error():
+    policy = DiscountPolicy.fixed(discount_amount=Money("1000", currency="KRW"))
+
+    with pytest.raises(InvalidDiscountPolicyError):
+        policy.apply_to(Money("5000", currency="USD"))
```

예상 RED 실패: `apps.discounts.domain.discount_policy` 모듈과 정책 객체가 아직 없어서 import 단계에서 실패해야 합니다.

**GREEN: 최소 구현**

```diff
diff --git a/apps/discounts/domain/discount_policy.py b/apps/discounts/domain/discount_policy.py
new file mode 100644
--- /dev/null
+++ b/apps/discounts/domain/discount_policy.py
@@ -0,0 +1,100 @@
+from dataclasses import dataclass
+from decimal import Decimal, ROUND_DOWN
+from enum import StrEnum
+
+
+class InvalidMoneyError(ValueError):
+    pass
+
+
+class InvalidDiscountPolicyError(ValueError):
+    pass
+
+
+@dataclass(frozen=True, slots=True)
+class Money:
+    amount: Decimal | str | int
+    currency: str = "KRW"
+
+    def __post_init__(self) -> None:
+        amount = Decimal(str(self.amount))
+        if amount < 0:
+            raise InvalidMoneyError("amount must be greater than or equal to 0")
+        if not self.currency:
+            raise InvalidMoneyError("currency is required")
+        object.__setattr__(self, "amount", amount)
+
+    def subtract(self, other: "Money") -> "Money":
+        self._ensure_same_currency(other)
+        return Money(max(self.amount - other.amount, Decimal("0")), self.currency)
+
+    def min(self, other: "Money") -> "Money":
+        self._ensure_same_currency(other)
+        return self if self.amount <= other.amount else other
+
+    def multiply(self, rate: Decimal) -> "Money":
+        return Money((self.amount * rate).quantize(Decimal("1"), rounding=ROUND_DOWN), self.currency)
+
+    def _ensure_same_currency(self, other: "Money") -> None:
+        if self.currency != other.currency:
+            raise InvalidDiscountPolicyError("money currency must match")
+
+
+class DiscountKind(StrEnum):
+    FIXED = "fixed"
+    PERCENTAGE = "percentage"
+
+
+@dataclass(frozen=True, slots=True)
+class DiscountResult:
+    discount_amount: Money
+    payable_amount: Money
+
+
+@dataclass(frozen=True, slots=True)
+class DiscountPolicy:
+    """Aggregate Root: 할인 금액은 주문 금액보다 클 수 없고, 최소 주문 금액 미만이면 적용되지 않는다."""
+
+    kind: DiscountKind
+    discount_amount: Money | None = None
+    rate: Decimal | None = None
+    min_order_amount: Money = Money("0")
+    max_discount_amount: Money | None = None
+
+    def __post_init__(self) -> None:
+        if self.kind == DiscountKind.FIXED and self.discount_amount is None:
+            raise InvalidDiscountPolicyError("fixed policy requires discount_amount")
+        if self.kind == DiscountKind.PERCENTAGE:
+            if self.rate is None or self.rate < 0 or self.rate > 1:
+                raise InvalidDiscountPolicyError("percentage rate must be between 0 and 1")
+
+    @classmethod
+    def fixed(
+        cls,
+        discount_amount: Money,
+        min_order_amount: Money = Money("0"),
+    ) -> "DiscountPolicy":
+        return cls(
+            kind=DiscountKind.FIXED,
+            discount_amount=discount_amount,
+            min_order_amount=min_order_amount,
+        )
+
+    @classmethod
+    def percentage(
+        cls,
+        rate: Decimal,
+        min_order_amount: Money = Money("0"),
+        max_discount_amount: Money | None = None,
+    ) -> "DiscountPolicy":
+        return cls(
+            kind=DiscountKind.PERCENTAGE,
+            rate=rate,
+            min_order_amount=min_order_amount,
+            max_discount_amount=max_discount_amount,
+        )
+
+    def apply_to(self, subtotal: Money) -> DiscountResult:
+        subtotal._ensure_same_currency(self.min_order_amount)
+        if subtotal.amount < self.min_order_amount.amount:
+            return DiscountResult(Money("0", subtotal.currency), subtotal)
+
+        discount = self._calculate_discount(subtotal).min(subtotal)
+        return DiscountResult(discount, subtotal.subtract(discount))
+
+    def _calculate_discount(self, subtotal: Money) -> Money:
+        if self.kind == DiscountKind.FIXED:
+            self.discount_amount._ensure_same_currency(subtotal)
+            return self.discount_amount
+
+        calculated = subtotal.multiply(self.rate)
+        if self.max_discount_amount is None:
+            return calculated
+        self.max_discount_amount._ensure_same_currency(subtotal)
+        return calculated.min(self.max_discount_amount)
```

**REFACTOR notes**

이 구조는 할인 정책을 Django Model/ORM에서 분리한 순수 도메인 객체로 둡니다. Django 쪽에서는 ORM 모델 값을 `Money`, `DiscountPolicy`로 변환한 뒤 `apply_to()` 결과만 저장하면 됩니다. 다음 리팩터링은 `Money`를 공통 도메인 값 객체로 이동하고, 실제 정책 조회는 `DiscountPolicyRepository` 인터페이스와 Django 구현체로 분리하는 방향이 적절합니다.

실행 명령:

```bash
pytest tests/isolated/unit/discounts/test_discount_policy.py -q
pytest tests/isolated -q
```

---
> **관련 스킬 참조:**
> - Django ORM 연동과 repository 분리 → **implementation-django** 스킬