지정된 fixture path `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, 현재 작업 디렉터리 `/private/tmp/dddjango-codex-eval`에도 읽을 파일이 없었습니다. 그래서 기존 코드에 덮어쓰는 diff가 아니라, Django 모델 밖의 domain policy/service로 쿠폰 정책을 분리하는 추가 diff로 제안합니다.

```diff
diff --git a/apps/coupons/domain/policies.py b/apps/coupons/domain/policies.py
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/apps/coupons/domain/policies.py
@@ -0,0 +1,115 @@
+from __future__ import annotations
+
+from dataclasses import dataclass
+from decimal import Decimal
+from typing import Literal
+
+
+class CouponPolicyError(Exception):
+    pass
+
+
+class MinimumOrderAmountNotMet(CouponPolicyError):
+    pass
+
+
+class DuplicateCouponUseNotAllowed(CouponPolicyError):
+    pass
+
+
+class InvalidDiscountPolicy(CouponPolicyError):
+    pass
+
+
+@dataclass(frozen=True)
+class Money:
+    amount: Decimal
+    currency: str = "KRW"
+
+    def __post_init__(self) -> None:
+        if self.amount < 0:
+            raise InvalidDiscountPolicy("money amount must be zero or positive")
+
+    def same_currency(self, other: "Money") -> None:
+        if self.currency != other.currency:
+            raise InvalidDiscountPolicy("currency mismatch")
+
+    def min(self, other: "Money") -> "Money":
+        self.same_currency(other)
+        return self if self.amount <= other.amount else other
+
+
+@dataclass(frozen=True)
+class CouponPolicy:
+    """
+    Coupon aggregate invariant:
+    - discount must never exceed order amount
+    - fixed discount needs discount_amount
+    - rate discount needs discount_rate between 0 and 1
+    - minimum_order_amount is inclusive
+    - non-stackable coupon cannot be used with already applied coupons
+    """
+
+    code: str
+    discount_type: Literal["fixed", "rate"]
+    minimum_order_amount: Money
+    can_stack: bool
+    discount_amount: Money | None = None
+    discount_rate: Decimal | None = None
+
+    def calculate_discount(
+        self,
+        order_amount: Money,
+        applied_coupon_codes: set[str],
+    ) -> Money:
+        self._validate(order_amount, applied_coupon_codes)
+
+        if self.discount_type == "fixed":
+            assert self.discount_amount is not None
+            return self.discount_amount.min(order_amount)
+
+        if self.discount_type == "rate":
+            assert self.discount_rate is not None
+            return Money(order_amount.amount * self.discount_rate, order_amount.currency)
+
+        raise InvalidDiscountPolicy("unsupported discount type")
+
+    def _validate(self, order_amount: Money, applied_coupon_codes: set[str]) -> None:
+        order_amount.same_currency(self.minimum_order_amount)
+
+        if order_amount.amount < self.minimum_order_amount.amount:
+            raise MinimumOrderAmountNotMet(self.code)
+
+        if self.code in applied_coupon_codes:
+            raise DuplicateCouponUseNotAllowed(self.code)
+
+        if applied_coupon_codes and not self.can_stack:
+            raise DuplicateCouponUseNotAllowed(self.code)
+
+        if self.discount_type == "fixed":
+            if self.discount_amount is None:
+                raise InvalidDiscountPolicy("fixed coupon needs discount_amount")
+            order_amount.same_currency(self.discount_amount)
+            return
+
+        if self.discount_type == "rate":
+            if self.discount_rate is None:
+                raise InvalidDiscountPolicy("rate coupon needs discount_rate")
+            if self.discount_rate <= 0 or self.discount_rate > Decimal("1"):
+                raise InvalidDiscountPolicy("discount_rate must be > 0 and <= 1")
+            return
+
+        raise InvalidDiscountPolicy("unsupported discount type")
+
+
+class CouponDiscountService:
+    def apply(
+        self,
+        policy: CouponPolicy,
+        order_amount: Money,
+        applied_coupon_codes: set[str],
+    ) -> Money:
+        return policy.calculate_discount(order_amount, applied_coupon_codes)
diff --git a/tests/coupons/test_coupon_policy.py b/tests/coupons/test_coupon_policy.py
new file mode 100644
index 0000000..2222222
--- /dev/null
+++ b/tests/coupons/test_coupon_policy.py
@@ -0,0 +1,72 @@
+from decimal import Decimal
+
+import pytest
+
+from apps.coupons.domain.policies import (
+    CouponDiscountService,
+    CouponPolicy,
+    DuplicateCouponUseNotAllowed,
+    MinimumOrderAmountNotMet,
+    Money,
+)
+
+
+def test_fixed_discount_is_capped_by_order_amount():
+    policy = CouponPolicy(
+        code="FIXED_5000",
+        discount_type="fixed",
+        minimum_order_amount=Money(Decimal("1000")),
+        can_stack=True,
+        discount_amount=Money(Decimal("5000")),
+    )
+
+    discount = CouponDiscountService().apply(
+        policy,
+        order_amount=Money(Decimal("3000")),
+        applied_coupon_codes=set(),
+    )
+
+    assert discount == Money(Decimal("3000"))
+
+
+def test_rate_discount_calculates_from_order_amount():
+    policy = CouponPolicy(
+        code="RATE_10",
+        discount_type="rate",
+        minimum_order_amount=Money(Decimal("10000")),
+        can_stack=True,
+        discount_rate=Decimal("0.10"),
+    )
+
+    discount = CouponDiscountService().apply(
+        policy,
+        order_amount=Money(Decimal("20000")),
+        applied_coupon_codes=set(),
+    )
+
+    assert discount == Money(Decimal("2000.00"))
+
+
+def test_minimum_order_amount_is_required():
+    policy = CouponPolicy(
+        code="MIN_10000",
+        discount_type="fixed",
+        minimum_order_amount=Money(Decimal("10000")),
+        can_stack=True,
+        discount_amount=Money(Decimal("1000")),
+    )
+
+    with pytest.raises(MinimumOrderAmountNotMet):
+        CouponDiscountService().apply(policy, Money(Decimal("9999")), set())
+
+
+def test_same_coupon_cannot_be_applied_twice():
+    policy = CouponPolicy(
+        code="ONCE",
+        discount_type="fixed",
+        minimum_order_amount=Money(Decimal("0")),
+        can_stack=True,
+        discount_amount=Money(Decimal("1000")),
+    )
+
+    with pytest.raises(DuplicateCouponUseNotAllowed):
+        CouponDiscountService().apply(policy, Money(Decimal("10000")), {"ONCE"})
+
+
+def test_non_stackable_coupon_rejects_existing_coupon():
+    policy = CouponPolicy(
+        code="ONLY_ONE",
+        discount_type="rate",
+        minimum_order_amount=Money(Decimal("0")),
+        can_stack=False,
+        discount_rate=Decimal("0.10"),
+    )
+
+    with pytest.raises(DuplicateCouponUseNotAllowed):
+        CouponDiscountService().apply(policy, Money(Decimal("10000")), {"WELCOME"})
```

Django `Coupon` 모델에는 `calculate_discount()` 같은 정책 메서드를 몰아넣지 말고, 필요하면 `to_policy()`처럼 DB 필드를 `CouponPolicy`로 변환하는 얇은 메서드만 두는 쪽이 맞습니다. 주문 금액, 이미 적용된 쿠폰 코드 집합, 중복 허용 여부 판단은 위 domain service/policy object에서 검증합니다.

검증 명령:

```bash
pytest tests/coupons/test_coupon_policy.py
```

---
> **관련 스킬 참조:**
> - 쿠폰 정책을 실제 Django 모델/서비스/테스트 구조에 맞춰 반영 → **implementation-django** 스킬