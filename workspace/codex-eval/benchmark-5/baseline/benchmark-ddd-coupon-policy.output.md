지정된 fixture `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고 작업 디렉터리도 비어 있었습니다. 그래서 기존 코드 수정이 아니라, 새 Django 앱에 적용 가능한 DDD 기준 설계 diff로 제안합니다.

```diff
diff --git a/shop/coupons/domain.py b/shop/coupons/domain.py
new file mode 100644
--- /dev/null
+++ b/shop/coupons/domain.py
@@ -0,0 +1,117 @@
+from __future__ import annotations
+
+from dataclasses import dataclass
+from decimal import Decimal, ROUND_DOWN
+from enum import Enum
+
+
+Money = Decimal
+
+
+class CouponError(Exception):
+    pass
+
+
+class MinimumOrderAmountNotMet(CouponError):
+    pass
+
+
+class CouponCannotBeCombined(CouponError):
+    pass
+
+
+class DuplicateCouponSelected(CouponError):
+    pass
+
+
+class CouponAlreadyRedeemed(CouponError):
+    pass
+
+
+class DiscountType(str, Enum):
+    FIXED_AMOUNT = "fixed_amount"
+    PERCENT_RATE = "percent_rate"
+
+
+@dataclass(frozen=True)
+class OrderPrice:
+    subtotal: Money
+
+    def __post_init__(self) -> None:
+        if self.subtotal < 0:
+            raise ValueError("subtotal must be greater than or equal to 0")
+
+
+@dataclass(frozen=True)
+class DiscountResult:
+    discount_amount: Money
+    payable_amount: Money
+
+
+@dataclass(frozen=True)
+class CouponPolicy:
+    discount_type: DiscountType
+    discount_value: Money
+    minimum_order_amount: Money = Decimal("0")
+    combinable: bool = True
+
+    def validate(self, order_price: OrderPrice) -> None:
+        if order_price.subtotal < self.minimum_order_amount:
+            raise MinimumOrderAmountNotMet(
+                f"minimum order amount is {self.minimum_order_amount}"
+            )
+
+    def calculate_discount(self, order_price: OrderPrice) -> Money:
+        self.validate(order_price)
+
+        if self.discount_type == DiscountType.FIXED_AMOUNT:
+            discount = self.discount_value
+        elif self.discount_type == DiscountType.PERCENT_RATE:
+            discount = (order_price.subtotal * self.discount_value / Decimal("100")).quantize(
+                Decimal("1"),
+                rounding=ROUND_DOWN,
+            )
+        else:
+            raise ValueError(f"unsupported discount type: {self.discount_type}")
+
+        return min(discount, order_price.subtotal)
+
+
+@dataclass(frozen=True)
+class Coupon:
+    code: str
+    policy: CouponPolicy
+    active: bool = True
+
+    def discount_for(self, order_price: OrderPrice) -> Money:
+        if not self.active:
+            raise CouponError("inactive coupon")
+        return self.policy.calculate_discount(order_price)
+
+    @property
+    def combinable(self) -> bool:
+        return self.policy.combinable
+
+
+@dataclass(frozen=True)
+class CouponSelection:
+    coupons: tuple[Coupon, ...]
+
+    def __post_init__(self) -> None:
+        codes = [coupon.code for coupon in self.coupons]
+        if len(codes) != len(set(codes)):
+            raise DuplicateCouponSelected("same coupon cannot be selected twice")
+
+        if len(self.coupons) > 1 and any(not coupon.combinable for coupon in self.coupons):
+            raise CouponCannotBeCombined("non-combinable coupon must be used alone")
+
+    def apply_to(self, order_price: OrderPrice) -> DiscountResult:
+        remaining = order_price.subtotal
+        total_discount = Decimal("0")
+
+        for coupon in self.coupons:
+            discount = coupon.discount_for(OrderPrice(subtotal=remaining))
+            total_discount += discount
+            remaining -= discount
+
+        return DiscountResult(
+            discount_amount=total_discount,
+            payable_amount=order_price.subtotal - total_discount,
+        )
diff --git a/shop/coupons/application.py b/shop/coupons/application.py
new file mode 100644
--- /dev/null
+++ b/shop/coupons/application.py
@@ -0,0 +1,60 @@
+from dataclasses import dataclass
+from decimal import Decimal
+from typing import Protocol
+
+from shop.coupons.domain import (
+    Coupon,
+    CouponAlreadyRedeemed,
+    CouponSelection,
+    DiscountResult,
+    OrderPrice,
+)
+
+
+class CouponRepository(Protocol):
+    def get_by_code(self, code: str) -> Coupon:
+        raise NotImplementedError
+
+
+class CouponRedemptionRepository(Protocol):
+    def exists_for_customer(self, *, customer_id: int, coupon_code: str) -> bool:
+        raise NotImplementedError
+
+
+@dataclass(frozen=True)
+class ApplyCouponsCommand:
+    customer_id: int
+    order_subtotal: Decimal
+    coupon_codes: list[str]
+
+
+@dataclass(frozen=True)
+class ApplyCouponsResult:
+    discount_amount: Decimal
+    payable_amount: Decimal
+
+
+class ApplyCouponsUseCase:
+    def __init__(
+        self,
+        coupon_repository: CouponRepository,
+        redemption_repository: CouponRedemptionRepository,
+    ) -> None:
+        self.coupon_repository = coupon_repository
+        self.redemption_repository = redemption_repository
+
+    def execute(self, command: ApplyCouponsCommand) -> ApplyCouponsResult:
+        coupons = []
+
+        for code in command.coupon_codes:
+            coupon = self.coupon_repository.get_by_code(code)
+            if self.redemption_repository.exists_for_customer(
+                customer_id=command.customer_id,
+                coupon_code=coupon.code,
+            ):
+                raise CouponAlreadyRedeemed(f"coupon already redeemed: {coupon.code}")
+            coupons.append(coupon)
+
+        result: DiscountResult = CouponSelection(tuple(coupons)).apply_to(
+            OrderPrice(subtotal=command.order_subtotal)
+        )
+        return ApplyCouponsResult(
+            discount_amount=result.discount_amount,
+            payable_amount=result.payable_amount,
+        )
diff --git a/shop/coupons/models.py b/shop/coupons/models.py
new file mode 100644
--- /dev/null
+++ b/shop/coupons/models.py
@@ -0,0 +1,49 @@
+from decimal import Decimal
+
+from django.db import models
+
+from shop.coupons.domain import Coupon, CouponPolicy, DiscountType
+
+
+class CouponModel(models.Model):
+    code = models.CharField(max_length=40, unique=True)
+    discount_type = models.CharField(max_length=20, choices=[(item.value, item.value) for item in DiscountType])
+    discount_value = models.DecimalField(max_digits=12, decimal_places=2)
+    minimum_order_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
+    combinable = models.BooleanField(default=True)
+    active = models.BooleanField(default=True)
+
+    def to_domain(self) -> Coupon:
+        return Coupon(
+            code=self.code,
+            active=self.active,
+            policy=CouponPolicy(
+                discount_type=DiscountType(self.discount_type),
+                discount_value=self.discount_value,
+                minimum_order_amount=self.minimum_order_amount,
+                combinable=self.combinable,
+            ),
+        )
+
+
+class CouponRedemptionModel(models.Model):
+    customer_id = models.BigIntegerField()
+    coupon = models.ForeignKey(CouponModel, on_delete=models.PROTECT)
+    order_id = models.BigIntegerField()
+    redeemed_at = models.DateTimeField(auto_now_add=True)
+
+    class Meta:
+        constraints = [
+            models.UniqueConstraint(
+                fields=["customer_id", "coupon"],
+                name="uniq_coupon_redemption_per_customer",
+            )
+        ]
diff --git a/shop/coupons/repositories.py b/shop/coupons/repositories.py
new file mode 100644
--- /dev/null
+++ b/shop/coupons/repositories.py
@@ -0,0 +1,23 @@
+from django.shortcuts import get_object_or_404
+
+from shop.coupons.domain import Coupon
+from shop.coupons.models import CouponModel, CouponRedemptionModel
+
+
+class DjangoCouponRepository:
+    def get_by_code(self, code: str) -> Coupon:
+        return get_object_or_404(CouponModel, code=code).to_domain()
+
+
+class DjangoCouponRedemptionRepository:
+    def exists_for_customer(self, *, customer_id: int, coupon_code: str) -> bool:
+        return CouponRedemptionModel.objects.filter(
+            customer_id=customer_id,
+            coupon__code=coupon_code,
+        ).exists()
diff --git a/shop/coupons/api.py b/shop/coupons/api.py
new file mode 100644
--- /dev/null
+++ b/shop/coupons/api.py
@@ -0,0 +1,46 @@
+from decimal import Decimal
+
+from ninja import Router, Schema
+
+from shop.coupons.application import ApplyCouponsCommand, ApplyCouponsUseCase
+from shop.coupons.repositories import DjangoCouponRedemptionRepository, DjangoCouponRepository
+
+
+router = Router(tags=["coupons"])
+
+
+class ApplyCouponsRequest(Schema):
+    customer_id: int
+    order_subtotal: Decimal
+    coupon_codes: list[str]
+
+
+class ApplyCouponsResponse(Schema):
+    discount_amount: Decimal
+    payable_amount: Decimal
+
+
+@router.post("/apply", response=ApplyCouponsResponse)
+def apply_coupons(request, payload: ApplyCouponsRequest):
+    use_case = ApplyCouponsUseCase(
+        coupon_repository=DjangoCouponRepository(),
+        redemption_repository=DjangoCouponRedemptionRepository(),
+    )
+    result = use_case.execute(
+        ApplyCouponsCommand(
+            customer_id=payload.customer_id,
+            order_subtotal=payload.order_subtotal,
+            coupon_codes=payload.coupon_codes,
+        )
+    )
+    return ApplyCouponsResponse(
+        discount_amount=result.discount_amount,
+        payable_amount=result.payable_amount,
+    )
```

핵심 경계는 이렇게 잡았습니다.

- `domain.py`: 정액 할인, 정률 할인, 최소 주문 금액, 쿠폰 조합 가능 여부를 순수 도메인 규칙으로 둡니다.
- `application.py`: 고객이 이미 쓴 쿠폰인지 확인하고 도메인 정책을 실행합니다.
- `models.py`, `repositories.py`: Django ORM은 저장소 세부사항으로 격리합니다.
- `api.py`: Django Ninja endpoint는 요청/응답 변환과 유스케이스 호출만 담당합니다.

검증 포인트는 `CouponSelection` 도메인 테스트로 잡으면 됩니다. 특히 “최소 주문 금액 미달”, “정액 할인은 주문금액을 초과하지 않음”, “정률 할인은 절사 정책 적용”, “비조합 쿠폰은 단독 사용만 가능”, “동일 쿠폰 중복 선택 불가”, “고객별 재사용 불가”를 우선 테스트하세요.