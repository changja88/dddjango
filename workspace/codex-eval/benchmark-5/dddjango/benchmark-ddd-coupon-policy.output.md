지정된 fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, `/private/tmp/dddjango-codex-eval`에도 읽을 파일이 없었습니다. 그래서 기존 파일 패치가 아니라, Django/DDD 구조에 넣을 수 있는 제안용 unified diff입니다.

**[주요 내용]**

| 도메인 용어 | 정의 | 코드 표현 | 금지 동의어 |
|---|---|---|---|
| 쿠폰 정책 | 쿠폰이 주문에 적용 가능한지와 할인액을 결정하는 규칙 | `CouponPolicy` | `CouponModel.apply_discount()` |
| 정액 할인 | 주문 금액에서 고정 금액 차감 | `FixedAmountDiscount` | `amount_type="fixed"` 분기 남발 |
| 정률 할인 | 주문 금액의 비율 차감 | `PercentageDiscount` | float 할인율 |
| 최소 주문 금액 | 쿠폰 적용 하한 | `minimum_order_amount` | view/form 검증 전용 |
| 중복 사용 제한 | 같은 주문에 같이 쓸 수 있는지 제한 | `CouponUsagePolicy` | 모델 메서드 내부 중복 체크 |

```diff
diff --git a/applications/promotions/domain_layer/value_object/money.py b/applications/promotions/domain_layer/value_object/money.py
new file mode 100644
--- /dev/null
+++ b/applications/promotions/domain_layer/value_object/money.py
@@
+from dataclasses import dataclass
+
+
+class CurrencyMismatch(Exception): ...
+
+
+@dataclass(frozen=True)
+class Money:
+    amount: int
+    currency: str = "KRW"
+
+    def __post_init__(self) -> None:
+        if self.amount < 0:
+            raise ValueError("금액은 0 이상이어야 합니다")
+        if not self.currency:
+            raise ValueError("통화는 필수입니다")
+
+    def min(self, other: "Money") -> "Money":
+        self._ensure_same_currency(other)
+        return self if self.amount <= other.amount else other
+
+    def _ensure_same_currency(self, other: "Money") -> None:
+        if self.currency != other.currency:
+            raise CurrencyMismatch
diff --git a/applications/promotions/domain_layer/coupon/policy.py b/applications/promotions/domain_layer/coupon/policy.py
new file mode 100644
--- /dev/null
+++ b/applications/promotions/domain_layer/coupon/policy.py
@@
+from dataclasses import dataclass
+from typing import Protocol
+
+from applications.promotions.domain_layer.value_object.money import Money
+
+
+class CouponCannotBeApplied(Exception): ...
+class CouponCannotBeStacked(Exception): ...
+
+
+class DiscountPolicy(Protocol):
+    def discount_for(self, order_total: Money) -> Money: ...
+
+
+@dataclass(frozen=True)
+class FixedAmountDiscount:
+    amount: Money
+
+    def discount_for(self, order_total: Money) -> Money:
+        return self.amount.min(order_total)
+
+
+@dataclass(frozen=True)
+class PercentageDiscount:
+    basis_points: int
+
+    def __post_init__(self) -> None:
+        if not 0 <= self.basis_points <= 10_000:
+            raise ValueError("정률 할인은 0~10000bp 사이여야 합니다")
+
+    def discount_for(self, order_total: Money) -> Money:
+        return Money(order_total.amount * self.basis_points // 10_000, order_total.currency)
+
+
+@dataclass(frozen=True)
+class CouponPolicy:
+    code: str
+    discount_policy: DiscountPolicy
+    minimum_order_amount: Money
+    stackable: bool = False
+
+    def calculate_discount(self, order_total: Money) -> Money:
+        if order_total.amount < self.minimum_order_amount.amount:
+            raise CouponCannotBeApplied("최소 주문 금액을 충족하지 못했습니다")
+        return self.discount_policy.discount_for(order_total)
+
+
+class CouponUsagePolicy:
+    """쿠폰 중복 사용 제한 정책. Django 모델/DB 조회는 응용 서비스가 담당한다."""
+
+    def validate(self, coupons: list[CouponPolicy], already_used_codes: set[str]) -> None:
+        codes = [coupon.code for coupon in coupons]
+        if len(codes) != len(set(codes)) or set(codes) & already_used_codes:
+            raise CouponCannotBeApplied("이미 사용한 쿠폰입니다")
+        if len(coupons) > 1 and any(not coupon.stackable for coupon in coupons):
+            raise CouponCannotBeStacked("중복 사용이 제한된 쿠폰입니다")
diff --git a/applications/promotions/tests/domain/test_coupon_policy.py b/applications/promotions/tests/domain/test_coupon_policy.py
new file mode 100644
--- /dev/null
+++ b/applications/promotions/tests/domain/test_coupon_policy.py
@@
+import pytest
+
+from applications.promotions.domain_layer.coupon.policy import (
+    CouponCannotBeApplied,
+    CouponCannotBeStacked,
+    CouponPolicy,
+    CouponUsagePolicy,
+    FixedAmountDiscount,
+    PercentageDiscount,
+)
+from applications.promotions.domain_layer.value_object.money import Money
+
+
+def test_fixed_discount_is_capped_by_order_total():
+    coupon = CouponPolicy("FIXED", FixedAmountDiscount(Money(10_000)), Money(0))
+
+    assert coupon.calculate_discount(Money(7_000)) == Money(7_000)
+
+
+def test_percentage_discount_uses_integer_basis_points():
+    coupon = CouponPolicy("RATE", PercentageDiscount(1_500), Money(0))
+
+    assert coupon.calculate_discount(Money(10_000)) == Money(1_500)
+
+
+def test_minimum_order_amount_is_inclusive():
+    coupon = CouponPolicy("MIN", FixedAmountDiscount(Money(1_000)), Money(30_000))
+
+    assert coupon.calculate_discount(Money(30_000)) == Money(1_000)
+
+
+def test_below_minimum_order_amount_is_rejected():
+    coupon = CouponPolicy("MIN", FixedAmountDiscount(Money(1_000)), Money(30_000))
+
+    with pytest.raises(CouponCannotBeApplied):
+        coupon.calculate_discount(Money(29_999))
+
+
+def test_non_stackable_coupon_cannot_be_combined():
+    coupons = [
+        CouponPolicy("A", FixedAmountDiscount(Money(1_000)), Money(0), stackable=False),
+        CouponPolicy("B", PercentageDiscount(500), Money(0), stackable=True),
+    ]
+
+    with pytest.raises(CouponCannotBeStacked):
+        CouponUsagePolicy().validate(coupons, already_used_codes=set())
+
+
+def test_already_used_coupon_is_rejected():
+    coupon = CouponPolicy("WELCOME", FixedAmountDiscount(Money(1_000)), Money(0))
+
+    with pytest.raises(CouponCannotBeApplied):
+        CouponUsagePolicy().validate([coupon], already_used_codes={"WELCOME"})
```

설계 기준은 `promotions` 바운디드 컨텍스트 안에서 쿠폰 정책을 순수 도메인 정책 객체로 두는 것입니다. Django `CouponModel`은 저장 필드와 매핑만 담당하고, 주문 금액 스냅샷과 고객의 사용 이력은 응용 서비스가 repository로 조회해 `CouponUsagePolicy.validate(...)`에 값으로 전달합니다. 이렇게 해야 최소 주문 금액, 정액/정률 계산, 중복 사용 제한을 DB 없이 pytest로 빠르게 검증할 수 있습니다.

검증 명령:

```bash
pytest applications/promotions/tests/domain/test_coupon_policy.py
```

---
> **관련 스킬 참조:**
> - Django ORM 매핑과 repository 구현 → **implementation-django** 스킬
> - 쿠폰 사용 이력 저장, 동시성, 트랜잭션 경계 → **architecture-implementation-patterns** 스킬