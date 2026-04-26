# 할인 정책 시스템 테스트

## 분석

주어진 `PricingService`는 다음 요소들의 조합으로 최종 가격을 결정한다:

1. **회원 등급 할인** -- BASIC(0%), SILVER(3%), GOLD(5%), PLATINUM(10%)
2. **프로모션 할인** -- 카테고리 필터, 최소 구매금액, 유효기간 조건 충족 시 적용
3. **최대 할인 상한** -- 등급 할인 + 프로모션 할인 합계가 30%를 초과할 수 없음
4. **가격 검증** -- 상품 가격이 0 이하이면 `ValueError` 발생

테스트 전략:
- `factory_boy`로 `Member`, `Product`, `Promotion` 객체를 선언적으로 생성
- `Hypothesis`로 다양한 입력 조합에 대한 속성 기반 테스트(property-based test) 수행
- 경계값, 예외 케이스, 비즈니스 규칙을 명시적 단위 테스트로 검증

---

## 테스트 코드

```python
"""할인 정책 시스템 테스트 — factory_boy + Hypothesis 활용."""

from __future__ import annotations

import math
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

import factory
import pytest
from hypothesis import given, assume, settings, HealthCheck
from hypothesis import strategies as st

# ──────────────────────────────────────────────
# 프로덕션 코드 (테스트 대상)
# ──────────────────────────────────────────────


class MemberTier(Enum):
    BASIC = "basic"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


@dataclass
class Member:
    id: int
    name: str
    email: str
    tier: MemberTier
    joined_at: datetime
    total_purchases: float = 0.0


@dataclass
class Product:
    id: int
    name: str
    price: float
    category: str


@dataclass
class Promotion:
    id: int
    name: str
    discount_rate: float
    category: str | None = None
    min_purchase: float = 0.0
    started_at: datetime | None = None
    ended_at: datetime | None = None


class PricingService:
    TIER_DISCOUNTS = {
        MemberTier.BASIC: 0.0,
        MemberTier.SILVER: 0.03,
        MemberTier.GOLD: 0.05,
        MemberTier.PLATINUM: 0.10,
    }
    MAX_DISCOUNT = 0.30

    def calculate_price(
        self,
        member: Member,
        product: Product,
        promotions: list[Promotion],
    ) -> float:
        if product.price <= 0:
            raise ValueError("상품 가격은 0보다 커야 합니다")

        tier_discount = self.TIER_DISCOUNTS[member.tier]

        applicable_promos = [
            p for p in promotions if self._is_applicable(p, product, member)
        ]
        promo_discount = max(
            (p.discount_rate for p in applicable_promos), default=0.0
        )

        total_discount = min(tier_discount + promo_discount, self.MAX_DISCOUNT)
        return round(product.price * (1 - total_discount), 2)

    def _is_applicable(
        self,
        promo: Promotion,
        product: Product,
        member: Member,
    ) -> bool:
        if promo.category and promo.category != product.category:
            return False
        if member.total_purchases < promo.min_purchase:
            return False
        now = datetime.now()
        if promo.started_at and now < promo.started_at:
            return False
        if promo.ended_at and now > promo.ended_at:
            return False
        return True


# ──────────────────────────────────────────────
# factory_boy 팩토리 정의
# ──────────────────────────────────────────────


class MemberFactory(factory.Factory):
    class Meta:
        model = Member

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("name")
    email = factory.Faker("email")
    tier = MemberTier.BASIC
    joined_at = factory.LazyFunction(datetime.now)
    total_purchases = 0.0


class ProductFactory(factory.Factory):
    class Meta:
        model = Product

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("word")
    price = 10000.0
    category = "electronics"


class PromotionFactory(factory.Factory):
    class Meta:
        model = Promotion

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("sentence", nb_words=3)
    discount_rate = 0.10
    category = None
    min_purchase = 0.0
    started_at = factory.LazyFunction(lambda: datetime.now() - timedelta(days=1))
    ended_at = factory.LazyFunction(lambda: datetime.now() + timedelta(days=30))


# ──────────────────────────────────────────────
# Hypothesis 전략 정의
# ──────────────────────────────────────────────

tier_strategy = st.sampled_from(list(MemberTier))

positive_price_strategy = st.floats(
    min_value=0.01, max_value=1_000_000.0, allow_nan=False, allow_infinity=False
)

discount_rate_strategy = st.floats(
    min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False
)

category_strategy = st.sampled_from(
    ["electronics", "clothing", "food", "books", "sports"]
)


# ──────────────────────────────────────────────
# 1. 회원 등급별 할인 단위 테스트
# ──────────────────────────────────────────────


class TestTierDiscount:
    """회원 등급에 따른 기본 할인율 검증."""

    def setup_method(self):
        self.service = PricingService()
        self.product = ProductFactory(price=10000.0)

    @pytest.mark.parametrize(
        "tier, expected_discount",
        [
            (MemberTier.BASIC, 0.0),
            (MemberTier.SILVER, 0.03),
            (MemberTier.GOLD, 0.05),
            (MemberTier.PLATINUM, 0.10),
        ],
    )
    def test_tier_discount_applied_correctly(self, tier, expected_discount):
        member = MemberFactory(tier=tier)
        result = self.service.calculate_price(member, self.product, [])
        expected = round(10000.0 * (1 - expected_discount), 2)
        assert result == expected

    def test_basic_member_pays_full_price(self):
        member = MemberFactory(tier=MemberTier.BASIC)
        result = self.service.calculate_price(member, self.product, [])
        assert result == 10000.0

    def test_platinum_member_gets_10_percent_off(self):
        member = MemberFactory(tier=MemberTier.PLATINUM)
        result = self.service.calculate_price(member, self.product, [])
        assert result == 9000.0


# ──────────────────────────────────────────────
# 2. 프로모션 적용 조건 테스트
# ──────────────────────────────────────────────


class TestPromotionApplicability:
    """프로모션의 카테고리, 최소 구매, 기간 조건 검증."""

    def setup_method(self):
        self.service = PricingService()

    def test_category_matching_promo_applies(self):
        member = MemberFactory(tier=MemberTier.BASIC)
        product = ProductFactory(category="electronics")
        promo = PromotionFactory(discount_rate=0.15, category="electronics")

        result = self.service.calculate_price(member, product, [promo])
        assert result == round(10000.0 * (1 - 0.15), 2)

    def test_category_mismatch_promo_does_not_apply(self):
        member = MemberFactory(tier=MemberTier.BASIC)
        product = ProductFactory(category="electronics")
        promo = PromotionFactory(discount_rate=0.15, category="clothing")

        result = self.service.calculate_price(member, product, [promo])
        assert result == 10000.0  # 할인 없음

    def test_null_category_promo_applies_to_all(self):
        member = MemberFactory(tier=MemberTier.BASIC)
        product = ProductFactory(category="food")
        promo = PromotionFactory(discount_rate=0.10, category=None)

        result = self.service.calculate_price(member, product, [promo])
        assert result == round(10000.0 * 0.90, 2)

    def test_min_purchase_met(self):
        member = MemberFactory(tier=MemberTier.BASIC, total_purchases=50000.0)
        product = ProductFactory(price=10000.0)
        promo = PromotionFactory(discount_rate=0.10, min_purchase=30000.0)

        result = self.service.calculate_price(member, product, [promo])
        assert result == 9000.0

    def test_min_purchase_not_met(self):
        member = MemberFactory(tier=MemberTier.BASIC, total_purchases=10000.0)
        product = ProductFactory(price=10000.0)
        promo = PromotionFactory(discount_rate=0.10, min_purchase=50000.0)

        result = self.service.calculate_price(member, product, [promo])
        assert result == 10000.0  # 할인 없음

    def test_promo_not_yet_started(self):
        member = MemberFactory(tier=MemberTier.BASIC)
        product = ProductFactory(price=10000.0)
        promo = PromotionFactory(
            discount_rate=0.20,
            started_at=datetime.now() + timedelta(days=7),
            ended_at=datetime.now() + timedelta(days=30),
        )

        result = self.service.calculate_price(member, product, [promo])
        assert result == 10000.0

    def test_promo_already_expired(self):
        member = MemberFactory(tier=MemberTier.BASIC)
        product = ProductFactory(price=10000.0)
        promo = PromotionFactory(
            discount_rate=0.20,
            started_at=datetime.now() - timedelta(days=30),
            ended_at=datetime.now() - timedelta(days=1),
        )

        result = self.service.calculate_price(member, product, [promo])
        assert result == 10000.0

    def test_promo_within_valid_period(self):
        member = MemberFactory(tier=MemberTier.BASIC)
        product = ProductFactory(price=10000.0)
        promo = PromotionFactory(
            discount_rate=0.20,
            started_at=datetime.now() - timedelta(days=1),
            ended_at=datetime.now() + timedelta(days=1),
        )

        result = self.service.calculate_price(member, product, [promo])
        assert result == 8000.0

    def test_promo_with_no_date_constraints(self):
        """started_at, ended_at 모두 None인 프로모션은 항상 적용."""
        member = MemberFactory(tier=MemberTier.BASIC)
        product = ProductFactory(price=10000.0)
        promo = PromotionFactory(
            discount_rate=0.10, started_at=None, ended_at=None
        )

        result = self.service.calculate_price(member, product, [promo])
        assert result == 9000.0


# ──────────────────────────────────────────────
# 3. 등급 + 프로모션 조합 테스트
# ──────────────────────────────────────────────


class TestCombinedDiscount:
    """등급 할인과 프로모션 할인이 합산되는지 검증."""

    def setup_method(self):
        self.service = PricingService()

    def test_gold_with_promo_combined(self):
        """GOLD(5%) + 프로모션(10%) = 15% 할인."""
        member = MemberFactory(tier=MemberTier.GOLD)
        product = ProductFactory(price=20000.0)
        promo = PromotionFactory(discount_rate=0.10)

        result = self.service.calculate_price(member, product, [promo])
        expected = round(20000.0 * (1 - 0.15), 2)
        assert result == expected

    def test_silver_with_promo_combined(self):
        """SILVER(3%) + 프로모션(7%) = 10% 할인."""
        member = MemberFactory(tier=MemberTier.SILVER)
        product = ProductFactory(price=50000.0)
        promo = PromotionFactory(discount_rate=0.07)

        result = self.service.calculate_price(member, product, [promo])
        expected = round(50000.0 * 0.90, 2)
        assert result == expected

    def test_multiple_promos_best_one_selected(self):
        """여러 프로모션 중 할인율이 가장 높은 것만 적용."""
        member = MemberFactory(tier=MemberTier.BASIC)
        product = ProductFactory(price=10000.0, category="electronics")
        promos = [
            PromotionFactory(discount_rate=0.05, category="electronics"),
            PromotionFactory(discount_rate=0.15, category="electronics"),
            PromotionFactory(discount_rate=0.10, category=None),
        ]

        result = self.service.calculate_price(member, product, promos)
        # 가장 높은 15%가 선택됨
        assert result == round(10000.0 * 0.85, 2)

    def test_only_applicable_promos_considered(self):
        """적용 불가능한 프로모션은 무시하고, 적용 가능한 것 중 최대값 사용."""
        member = MemberFactory(tier=MemberTier.BASIC, total_purchases=0.0)
        product = ProductFactory(price=10000.0, category="electronics")
        promos = [
            PromotionFactory(
                discount_rate=0.25, category="electronics", min_purchase=100000.0
            ),  # 최소 구매 미충족
            PromotionFactory(
                discount_rate=0.05, category="electronics", min_purchase=0.0
            ),  # 적용 가능
        ]

        result = self.service.calculate_price(member, product, promos)
        assert result == round(10000.0 * 0.95, 2)


# ──────────────────────────────────────────────
# 4. 최대 할인 상한(30%) 테스트
# ──────────────────────────────────────────────


class TestMaxDiscountCap:
    """등급 할인 + 프로모션 할인 합계가 30%를 초과하지 않는지 검증."""

    def setup_method(self):
        self.service = PricingService()

    def test_discount_capped_at_30_percent(self):
        """PLATINUM(10%) + 프로모션(25%) = 35% -> 30%로 제한."""
        member = MemberFactory(tier=MemberTier.PLATINUM)
        product = ProductFactory(price=100000.0)
        promo = PromotionFactory(discount_rate=0.25)

        result = self.service.calculate_price(member, product, [promo])
        expected = round(100000.0 * 0.70, 2)
        assert result == expected

    def test_exactly_30_percent(self):
        """PLATINUM(10%) + 프로모션(20%) = 정확히 30%."""
        member = MemberFactory(tier=MemberTier.PLATINUM)
        product = ProductFactory(price=100000.0)
        promo = PromotionFactory(discount_rate=0.20)

        result = self.service.calculate_price(member, product, [promo])
        expected = round(100000.0 * 0.70, 2)
        assert result == expected

    def test_below_30_percent_not_capped(self):
        """GOLD(5%) + 프로모션(10%) = 15% -> 상한 미적용."""
        member = MemberFactory(tier=MemberTier.GOLD)
        product = ProductFactory(price=100000.0)
        promo = PromotionFactory(discount_rate=0.10)

        result = self.service.calculate_price(member, product, [promo])
        expected = round(100000.0 * 0.85, 2)
        assert result == expected


# ──────────────────────────────────────────────
# 5. 에지 케이스 / 예외 테스트
# ──────────────────────────────────────────────


class TestEdgeCases:
    """경계값과 예외 상황 검증."""

    def setup_method(self):
        self.service = PricingService()

    def test_zero_price_raises_error(self):
        member = MemberFactory()
        product = ProductFactory(price=0.0)
        with pytest.raises(ValueError, match="상품 가격은 0보다 커야 합니다"):
            self.service.calculate_price(member, product, [])

    def test_negative_price_raises_error(self):
        member = MemberFactory()
        product = ProductFactory(price=-500.0)
        with pytest.raises(ValueError, match="상품 가격은 0보다 커야 합니다"):
            self.service.calculate_price(member, product, [])

    def test_empty_promotions_list(self):
        member = MemberFactory(tier=MemberTier.GOLD)
        product = ProductFactory(price=10000.0)
        result = self.service.calculate_price(member, product, [])
        assert result == round(10000.0 * 0.95, 2)

    def test_all_promos_inapplicable(self):
        member = MemberFactory(tier=MemberTier.BASIC, total_purchases=0.0)
        product = ProductFactory(price=10000.0, category="electronics")
        promos = [
            PromotionFactory(discount_rate=0.20, category="clothing"),
            PromotionFactory(discount_rate=0.15, min_purchase=999999.0),
        ]
        result = self.service.calculate_price(member, product, promos)
        assert result == 10000.0

    def test_very_small_price(self):
        member = MemberFactory(tier=MemberTier.PLATINUM)
        product = ProductFactory(price=0.01)
        result = self.service.calculate_price(member, product, [])
        expected = round(0.01 * 0.90, 2)
        assert result == expected

    def test_very_large_price(self):
        member = MemberFactory(tier=MemberTier.PLATINUM)
        product = ProductFactory(price=999_999_999.99)
        promo = PromotionFactory(discount_rate=0.20)
        result = self.service.calculate_price(member, product, [promo])
        expected = round(999_999_999.99 * 0.70, 2)
        assert result == expected

    def test_result_is_rounded_to_two_decimals(self):
        """가격이 소수점 둘째 자리까지 반올림되는지 확인."""
        member = MemberFactory(tier=MemberTier.SILVER)
        product = ProductFactory(price=9999.99)
        result = self.service.calculate_price(member, product, [])
        # 9999.99 * 0.97 = 9699.9903
        assert result == round(9999.99 * 0.97, 2)

    def test_min_purchase_boundary_exact_match(self):
        """total_purchases가 min_purchase와 정확히 같을 때 (미충족)."""
        member = MemberFactory(tier=MemberTier.BASIC, total_purchases=10000.0)
        product = ProductFactory(price=5000.0)
        # member.total_purchases < promo.min_purchase 이므로 10000 < 10000 은 False -> 적용됨
        promo = PromotionFactory(discount_rate=0.10, min_purchase=10000.0)

        result = self.service.calculate_price(member, product, [promo])
        # total_purchases(10000) < min_purchase(10000) 은 False이므로 프로모션 적용
        assert result == round(5000.0 * 0.90, 2)


# ──────────────────────────────────────────────
# 6. Hypothesis 속성 기반 테스트
# ──────────────────────────────────────────────


class TestHypothesisProperties:
    """Hypothesis를 활용한 속성 기반 테스트."""

    def setup_method(self):
        self.service = PricingService()

    @given(
        tier=tier_strategy,
        price=positive_price_strategy,
    )
    def test_result_never_exceeds_original_price(self, tier, price):
        """할인 적용 후 가격은 항상 원래 가격 이하."""
        member = MemberFactory(tier=tier)
        product = ProductFactory(price=price)
        result = self.service.calculate_price(member, product, [])
        assert result <= price + 0.01  # 반올림 허용 오차

    @given(
        tier=tier_strategy,
        price=positive_price_strategy,
        promo_rate=discount_rate_strategy,
    )
    def test_result_always_non_negative(self, tier, price, promo_rate):
        """결과 가격은 항상 0 이상."""
        member = MemberFactory(tier=tier)
        product = ProductFactory(price=price)
        promo = PromotionFactory(
            discount_rate=promo_rate,
            started_at=datetime.now() - timedelta(days=1),
            ended_at=datetime.now() + timedelta(days=1),
        )
        result = self.service.calculate_price(member, product, [promo])
        assert result >= 0.0

    @given(
        tier=tier_strategy,
        price=positive_price_strategy,
        promo_rate=discount_rate_strategy,
    )
    def test_discount_never_exceeds_30_percent(self, tier, price, promo_rate):
        """적용된 할인율은 절대 30%를 초과하지 않음."""
        member = MemberFactory(tier=tier)
        product = ProductFactory(price=price)
        promo = PromotionFactory(
            discount_rate=promo_rate,
            started_at=datetime.now() - timedelta(days=1),
            ended_at=datetime.now() + timedelta(days=1),
        )
        result = self.service.calculate_price(member, product, [promo])
        min_allowed = round(price * (1 - PricingService.MAX_DISCOUNT), 2)
        # 반올림 허용 오차
        assert result >= min_allowed - 0.01

    @given(
        price=positive_price_strategy,
    )
    def test_higher_tier_always_cheaper_or_equal(self, price):
        """등급이 높을수록 가격이 같거나 낮아야 함."""
        product = ProductFactory(price=price)
        tiers_in_order = [
            MemberTier.BASIC,
            MemberTier.SILVER,
            MemberTier.GOLD,
            MemberTier.PLATINUM,
        ]
        prices = []
        for tier in tiers_in_order:
            member = MemberFactory(tier=tier)
            result = self.service.calculate_price(member, product, [])
            prices.append(result)

        for i in range(len(prices) - 1):
            assert prices[i] >= prices[i + 1]

    @given(
        tier=tier_strategy,
        price=positive_price_strategy,
        rate_a=discount_rate_strategy,
        rate_b=discount_rate_strategy,
    )
    def test_higher_promo_rate_gives_lower_or_equal_price(
        self, tier, price, rate_a, rate_b
    ):
        """프로모션 할인율이 높을수록 가격이 같거나 낮아야 함."""
        assume(rate_a <= rate_b)
        member = MemberFactory(tier=tier)
        product = ProductFactory(price=price)

        promo_a = PromotionFactory(
            discount_rate=rate_a,
            started_at=datetime.now() - timedelta(days=1),
            ended_at=datetime.now() + timedelta(days=1),
        )
        promo_b = PromotionFactory(
            discount_rate=rate_b,
            started_at=datetime.now() - timedelta(days=1),
            ended_at=datetime.now() + timedelta(days=1),
        )

        result_a = self.service.calculate_price(member, product, [promo_a])
        result_b = self.service.calculate_price(member, product, [promo_b])
        assert result_a >= result_b - 0.01  # 반올림 허용 오차

    @given(
        tier=tier_strategy,
        price=positive_price_strategy,
    )
    def test_no_promo_equals_tier_discount_only(self, tier, price):
        """프로모션 없이 계산하면 등급 할인만 적용."""
        member = MemberFactory(tier=tier)
        product = ProductFactory(price=price)
        result = self.service.calculate_price(member, product, [])
        tier_discount = PricingService.TIER_DISCOUNTS[tier]
        expected = round(price * (1 - tier_discount), 2)
        assert result == expected

    @given(
        price=st.floats(
            min_value=-1_000_000, max_value=0.0, allow_nan=False, allow_infinity=False
        ),
    )
    def test_non_positive_price_always_raises(self, price):
        """0 이하의 가격은 항상 ValueError를 발생시킴."""
        member = MemberFactory()
        product = ProductFactory(price=price)
        with pytest.raises(ValueError):
            self.service.calculate_price(member, product, [])

    @given(
        tier=tier_strategy,
        price=positive_price_strategy,
        num_promos=st.integers(min_value=1, max_value=10),
        data=st.data(),
    )
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_result_is_deterministic(self, tier, price, num_promos, data):
        """같은 입력에 대해 항상 같은 결과를 반환."""
        member = MemberFactory(tier=tier, total_purchases=100000.0)
        product = ProductFactory(price=price)
        promos = []
        for _ in range(num_promos):
            rate = data.draw(discount_rate_strategy)
            promos.append(
                PromotionFactory(
                    discount_rate=rate,
                    category=None,
                    min_purchase=0.0,
                    started_at=datetime.now() - timedelta(days=1),
                    ended_at=datetime.now() + timedelta(days=1),
                )
            )

        result_1 = self.service.calculate_price(member, product, promos)
        result_2 = self.service.calculate_price(member, product, promos)
        assert result_1 == result_2

    @given(
        tier=tier_strategy,
        price=positive_price_strategy,
        category=category_strategy,
    )
    def test_mismatched_category_promo_has_no_effect(self, tier, price, category):
        """카테고리가 불일치하는 프로모션은 가격에 영향을 주지 않음."""
        member = MemberFactory(tier=tier)
        product = ProductFactory(price=price, category=category)

        other_categories = [c for c in ["electronics", "clothing", "food", "books", "sports"] if c != category]
        promo = PromotionFactory(
            discount_rate=0.20,
            category=other_categories[0],
            started_at=datetime.now() - timedelta(days=1),
            ended_at=datetime.now() + timedelta(days=1),
        )

        result_with_promo = self.service.calculate_price(member, product, [promo])
        result_without_promo = self.service.calculate_price(member, product, [])
        assert result_with_promo == result_without_promo
```

---

## 테스트 구조 요약

| 테스트 클래스 | 테스트 수 | 설명 |
|---|---|---|
| `TestTierDiscount` | 3 | 회원 등급별 기본 할인율 검증 (parametrize 포함 4 케이스) |
| `TestPromotionApplicability` | 8 | 카테고리 매칭, 최소 구매금액, 유효기간 조건 검증 |
| `TestCombinedDiscount` | 4 | 등급 할인 + 프로모션 할인 합산 로직 검증 |
| `TestMaxDiscountCap` | 3 | 30% 상한 초과, 정확히 30%, 미만 케이스 |
| `TestEdgeCases` | 8 | 0/음수 가격 예외, 빈 프로모션, 극단값, 반올림, 경계값 |
| `TestHypothesisProperties` | 9 | 속성 기반 테스트 -- 무작위 입력으로 불변 조건 검증 |

**총 35+ 테스트 케이스** (parametrize 및 Hypothesis 반복 포함)

---

## factory_boy 활용 포인트

- `MemberFactory`, `ProductFactory`, `PromotionFactory`로 객체 생성 보일러플레이트 제거
- `factory.Sequence`로 고유 ID 자동 생성
- `factory.LazyFunction`으로 프로모션 유효기간 동적 설정
- 팩토리 기본값을 정의하고, 개별 테스트에서 필요한 필드만 오버라이드

## Hypothesis 활용 포인트

- `st.sampled_from` -- 열거형(MemberTier)에서 무작위 선택
- `st.floats` -- 가격, 할인율에 대한 경계값 자동 탐색
- `st.data()` -- 동적으로 전략을 조합하여 가변 길이 프로모션 리스트 생성
- `assume()` -- 테스트 전제조건 명시 (rate_a <= rate_b)
- 속성 기반 검증: "결과가 원래 가격 이하", "결과가 0 이상", "30% 상한 준수", "등급 순서 단조성", "결정론성"
