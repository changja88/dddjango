# PricingService 테스트 코드

## 프로덕션 코드 (pricing.py)

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class MemberTier(Enum):
    BASIC = 'basic'
    SILVER = 'silver'
    GOLD = 'gold'
    PLATINUM = 'platinum'


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
        self, member: Member, product: Product, promotions: list[Promotion],
    ) -> float:
        if product.price <= 0:
            raise ValueError('상품 가격은 0보다 커야 합니다')

        tier_discount = self.TIER_DISCOUNTS[member.tier]

        applicable_promos = [
            p for p in promotions
            if self._is_applicable(p, product, member)
        ]
        promo_discount = max(
            (p.discount_rate for p in applicable_promos), default=0.0
        )

        total_discount = min(tier_discount + promo_discount, self.MAX_DISCOUNT)
        return round(product.price * (1 - total_discount), 2)

    def _is_applicable(
        self, promo: Promotion, product: Product, member: Member,
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
```

## 테스트 코드

### conftest.py -- 팩토리 및 픽스처

```python
import factory
from factory import fuzzy
import pytest
from datetime import datetime, timedelta

from pricing import Member, MemberTier, Product, Promotion, PricingService


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------

class MemberFactory(factory.Factory):
    class Meta:
        model = Member

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("name")
    email = factory.LazyAttribute(lambda obj: f"user_{obj.id}@example.com")
    tier = MemberTier.BASIC
    joined_at = factory.LazyFunction(datetime.now)
    total_purchases = 0.0

    class Params:
        silver = factory.Trait(tier=MemberTier.SILVER)
        gold = factory.Trait(tier=MemberTier.GOLD)
        platinum = factory.Trait(tier=MemberTier.PLATINUM)
        vip_buyer = factory.Trait(
            tier=MemberTier.PLATINUM,
            total_purchases=500_000.0,
        )


class ProductFactory(factory.Factory):
    class Meta:
        model = Product

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("word")
    price = fuzzy.FuzzyFloat(1000.0, 500_000.0)
    category = fuzzy.FuzzyChoice(["electronics", "fashion", "food", "books"])


class PromotionFactory(factory.Factory):
    class Meta:
        model = Promotion

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("catch_phrase")
    discount_rate = fuzzy.FuzzyFloat(0.01, 0.25)
    category = None
    min_purchase = 0.0
    started_at = factory.LazyFunction(lambda: datetime.now() - timedelta(days=1))
    ended_at = factory.LazyFunction(lambda: datetime.now() + timedelta(days=30))

    class Params:
        expired = factory.Trait(
            started_at=factory.LazyFunction(lambda: datetime.now() - timedelta(days=60)),
            ended_at=factory.LazyFunction(lambda: datetime.now() - timedelta(days=1)),
        )
        future = factory.Trait(
            started_at=factory.LazyFunction(lambda: datetime.now() + timedelta(days=1)),
            ended_at=factory.LazyFunction(lambda: datetime.now() + timedelta(days=60)),
        )
        category_specific = factory.Trait(
            category="electronics",
        )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def pricing_service():
    return PricingService()
```

### test_pricing_service.py -- 단위 테스트

```python
import pytest
import time_machine
from datetime import datetime, timedelta

from pricing import MemberTier, PricingService
from conftest import MemberFactory, ProductFactory, PromotionFactory


class TestTierDiscount:
    """회원 등급별 할인율이 올바르게 적용되는지 검증한다."""

    @pytest.mark.parametrize("tier, expected_rate", [
        (MemberTier.BASIC, 0.0),
        (MemberTier.SILVER, 0.03),
        (MemberTier.GOLD, 0.05),
        (MemberTier.PLATINUM, 0.10),
    ])
    def test_tier_discount_without_promotions(self, pricing_service, tier, expected_rate):
        member = MemberFactory(tier=tier)
        product = ProductFactory(price=10_000.0)

        result = pricing_service.calculate_price(member, product, promotions=[])

        assert result == round(10_000.0 * (1 - expected_rate), 2)

    def test_basic_member_pays_full_price(self, pricing_service):
        member = MemberFactory(tier=MemberTier.BASIC)
        product = ProductFactory(price=50_000.0)

        result = pricing_service.calculate_price(member, product, promotions=[])

        assert result == 50_000.0


class TestPromotionApplicability:
    """프로모션 적용 조건(카테고리, 최소 구매, 기간)을 검증한다."""

    def test_category_matching_promotion_applies(self, pricing_service):
        member = MemberFactory(tier=MemberTier.BASIC)
        product = ProductFactory(price=100_000.0, category="electronics")
        promo = PromotionFactory(discount_rate=0.10, category="electronics")

        result = pricing_service.calculate_price(member, product, promotions=[promo])

        assert result == 90_000.0

    def test_category_mismatched_promotion_ignored(self, pricing_service):
        member = MemberFactory(tier=MemberTier.BASIC)
        product = ProductFactory(price=100_000.0, category="fashion")
        promo = PromotionFactory(discount_rate=0.10, category="electronics")

        result = pricing_service.calculate_price(member, product, promotions=[promo])

        assert result == 100_000.0

    def test_global_promotion_applies_to_any_category(self, pricing_service):
        member = MemberFactory(tier=MemberTier.BASIC)
        product = ProductFactory(price=100_000.0, category="fashion")
        promo = PromotionFactory(discount_rate=0.15, category=None)

        result = pricing_service.calculate_price(member, product, promotions=[promo])

        assert result == 85_000.0

    def test_min_purchase_not_met_excludes_promotion(self, pricing_service):
        member = MemberFactory(tier=MemberTier.BASIC, total_purchases=5_000.0)
        product = ProductFactory(price=100_000.0)
        promo = PromotionFactory(discount_rate=0.20, min_purchase=10_000.0)

        result = pricing_service.calculate_price(member, product, promotions=[promo])

        assert result == 100_000.0

    def test_min_purchase_met_includes_promotion(self, pricing_service):
        member = MemberFactory(tier=MemberTier.BASIC, total_purchases=50_000.0)
        product = ProductFactory(price=100_000.0)
        promo = PromotionFactory(discount_rate=0.20, min_purchase=10_000.0)

        result = pricing_service.calculate_price(member, product, promotions=[promo])

        assert result == 80_000.0

    @time_machine.travel("2025-06-15 12:00:00")
    def test_expired_promotion_ignored(self, pricing_service):
        member = MemberFactory(tier=MemberTier.BASIC)
        product = ProductFactory(price=100_000.0)
        promo = PromotionFactory(
            discount_rate=0.10,
            started_at=datetime(2025, 1, 1),
            ended_at=datetime(2025, 5, 31),
        )

        result = pricing_service.calculate_price(member, product, promotions=[promo])

        assert result == 100_000.0

    @time_machine.travel("2025-06-15 12:00:00")
    def test_future_promotion_ignored(self, pricing_service):
        member = MemberFactory(tier=MemberTier.BASIC)
        product = ProductFactory(price=100_000.0)
        promo = PromotionFactory(
            discount_rate=0.10,
            started_at=datetime(2025, 7, 1),
            ended_at=datetime(2025, 12, 31),
        )

        result = pricing_service.calculate_price(member, product, promotions=[promo])

        assert result == 100_000.0

    @time_machine.travel("2025-06-15 12:00:00")
    def test_active_promotion_applies(self, pricing_service):
        member = MemberFactory(tier=MemberTier.BASIC)
        product = ProductFactory(price=100_000.0)
        promo = PromotionFactory(
            discount_rate=0.10,
            started_at=datetime(2025, 6, 1),
            ended_at=datetime(2025, 6, 30),
        )

        result = pricing_service.calculate_price(member, product, promotions=[promo])

        assert result == 90_000.0


class TestCombinedDiscounts:
    """등급 할인과 프로모션 할인이 합산되는 시나리오를 검증한다."""

    def test_tier_and_promotion_discounts_sum(self, pricing_service):
        member = MemberFactory(gold=True)
        product = ProductFactory(price=100_000.0)
        promo = PromotionFactory(discount_rate=0.10)

        result = pricing_service.calculate_price(member, product, promotions=[promo])

        assert result == 85_000.0  # 5% + 10% = 15%

    def test_highest_promotion_selected_among_multiple(self, pricing_service):
        """여러 프로모션 중 가장 높은 할인율만 적용된다."""
        member = MemberFactory(tier=MemberTier.BASIC)
        product = ProductFactory(price=100_000.0, category="electronics")
        promos = [
            PromotionFactory(discount_rate=0.05),
            PromotionFactory(discount_rate=0.15),
            PromotionFactory(discount_rate=0.10),
        ]

        result = pricing_service.calculate_price(member, product, promotions=promos)

        assert result == 85_000.0  # max(5%, 15%, 10%) = 15%

    def test_only_applicable_promotions_considered(self, pricing_service):
        """적용 불가 프로모션은 최대값 계산에서 제외된다."""
        member = MemberFactory(tier=MemberTier.BASIC, total_purchases=0.0)
        product = ProductFactory(price=100_000.0, category="electronics")
        promos = [
            PromotionFactory(discount_rate=0.20, min_purchase=100_000.0),
            PromotionFactory(discount_rate=0.05, category="electronics"),
        ]

        result = pricing_service.calculate_price(member, product, promotions=promos)

        assert result == 95_000.0  # 20% 프로모션은 min_purchase 미충족

    def test_platinum_with_large_promotion_capped_at_max(self, pricing_service):
        """총 할인율이 MAX_DISCOUNT(30%)를 초과하면 30%로 제한된다."""
        member = MemberFactory(platinum=True)  # 10%
        product = ProductFactory(price=100_000.0)
        promo = PromotionFactory(discount_rate=0.25)  # 10% + 25% = 35% -> 30%

        result = pricing_service.calculate_price(member, product, promotions=[promo])

        assert result == 70_000.0  # 30% cap

    def test_discount_at_exact_max_boundary(self, pricing_service):
        """총 할인율이 정확히 MAX_DISCOUNT와 같을 때 정상 적용된다."""
        member = MemberFactory(platinum=True)  # 10%
        product = ProductFactory(price=100_000.0)
        promo = PromotionFactory(discount_rate=0.20)  # 10% + 20% = 30%

        result = pricing_service.calculate_price(member, product, promotions=[promo])

        assert result == 70_000.0


class TestEdgeCases:
    """경계값과 예외 상황을 검증한다."""

    def test_zero_price_raises_value_error(self, pricing_service):
        member = MemberFactory()
        product = ProductFactory(price=0.0)

        with pytest.raises(ValueError, match="상품 가격은 0보다 커야 합니다"):
            pricing_service.calculate_price(member, product, promotions=[])

    def test_negative_price_raises_value_error(self, pricing_service):
        member = MemberFactory()
        product = ProductFactory(price=-1_000.0)

        with pytest.raises(ValueError, match="상품 가격은 0보다 커야 합니다"):
            pricing_service.calculate_price(member, product, promotions=[])

    def test_empty_promotions_list(self, pricing_service):
        member = MemberFactory(gold=True)
        product = ProductFactory(price=10_000.0)

        result = pricing_service.calculate_price(member, product, promotions=[])

        assert result == 9_500.0  # 골드 5%만 적용

    def test_result_rounded_to_two_decimal_places(self, pricing_service):
        member = MemberFactory(tier=MemberTier.SILVER)  # 3%
        product = ProductFactory(price=9_999.0)

        result = pricing_service.calculate_price(member, product, promotions=[])

        assert result == round(9_999.0 * 0.97, 2)
        assert result == 9699.03
```

### test_pricing_property.py -- Hypothesis 속성 기반 테스트

```python
import pytest
import time_machine
from datetime import datetime, timedelta
from hypothesis import given, example, settings, assume
from hypothesis import strategies as st

from pricing import (
    Member, MemberTier, Product, Promotion, PricingService,
)


# ---------------------------------------------------------------------------
# Hypothesis Strategies
# ---------------------------------------------------------------------------

tier_strategy = st.sampled_from(list(MemberTier))

member_strategy = st.builds(
    Member,
    id=st.integers(min_value=1, max_value=10_000),
    name=st.text(min_size=1, max_size=30),
    email=st.emails(),
    tier=tier_strategy,
    joined_at=st.datetimes(
        min_value=datetime(2000, 1, 1),
        max_value=datetime(2025, 12, 31),
    ),
    total_purchases=st.floats(min_value=0.0, max_value=10_000_000.0),
)

product_strategy = st.builds(
    Product,
    id=st.integers(min_value=1, max_value=10_000),
    name=st.text(min_size=1, max_size=50),
    price=st.floats(min_value=0.01, max_value=10_000_000.0, allow_nan=False, allow_infinity=False),
    category=st.sampled_from(["electronics", "fashion", "food", "books"]),
)

active_promotion_strategy = st.builds(
    Promotion,
    id=st.integers(min_value=1, max_value=10_000),
    name=st.text(min_size=1, max_size=30),
    discount_rate=st.floats(min_value=0.0, max_value=0.30, allow_nan=False, allow_infinity=False),
    category=st.none(),
    min_purchase=st.just(0.0),
    started_at=st.just(datetime(2020, 1, 1)),
    ended_at=st.just(datetime(2030, 12, 31)),
)


# ---------------------------------------------------------------------------
# Property-Based Tests
# ---------------------------------------------------------------------------

class TestPricingProperties:
    """PricingService가 모든 입력 조합에서 만족해야 할 불변 조건을 검증한다."""

    @given(member=member_strategy, product=product_strategy)
    @time_machine.travel("2025-06-15 12:00:00")
    def test_price_never_negative(self, member, product):
        """할인 후 가격은 항상 0 이상이어야 한다."""
        service = PricingService()

        result = service.calculate_price(member, product, promotions=[])

        assert result >= 0

    @given(
        member=member_strategy,
        product=product_strategy,
        promos=st.lists(active_promotion_strategy, max_size=5),
    )
    @time_machine.travel("2025-06-15 12:00:00")
    def test_price_never_exceeds_original(self, member, product, promos):
        """할인 후 가격은 원래 가격을 초과할 수 없다."""
        service = PricingService()

        result = service.calculate_price(member, product, promotions=promos)

        assert result <= product.price + 0.01  # 부동소수점 반올림 허용

    @given(
        member=member_strategy,
        product=product_strategy,
        promos=st.lists(active_promotion_strategy, max_size=5),
    )
    @time_machine.travel("2025-06-15 12:00:00")
    def test_discount_never_exceeds_max(self, member, product, promos):
        """적용된 총 할인율이 MAX_DISCOUNT(30%)를 초과하지 않는다."""
        service = PricingService()

        result = service.calculate_price(member, product, promotions=promos)
        min_allowed = round(product.price * (1 - PricingService.MAX_DISCOUNT), 2)

        assert result >= min_allowed - 0.01  # 부동소수점 반올림 허용

    @given(tier=tier_strategy)
    @time_machine.travel("2025-06-15 12:00:00")
    def test_higher_tier_gets_equal_or_lower_price(self, tier):
        """상위 등급 회원은 같은 상품에 대해 동일하거나 더 낮은 가격을 받는다."""
        service = PricingService()
        product = Product(id=1, name="test", price=100_000.0, category="electronics")
        basic_member = Member(
            id=1, name="A", email="a@test.com",
            tier=MemberTier.BASIC, joined_at=datetime(2020, 1, 1),
        )
        tiered_member = Member(
            id=2, name="B", email="b@test.com",
            tier=tier, joined_at=datetime(2020, 1, 1),
        )

        basic_price = service.calculate_price(basic_member, product, promotions=[])
        tiered_price = service.calculate_price(tiered_member, product, promotions=[])

        assert tiered_price <= basic_price

    @given(
        product=product_strategy,
        promos=st.lists(active_promotion_strategy, min_size=1, max_size=5),
    )
    @time_machine.travel("2025-06-15 12:00:00")
    def test_adding_promotions_does_not_increase_price(self, product, promos):
        """프로모션이 추가되면 가격이 올라가지 않는다."""
        service = PricingService()
        member = Member(
            id=1, name="test", email="t@test.com",
            tier=MemberTier.BASIC, joined_at=datetime(2020, 1, 1),
        )

        price_without = service.calculate_price(member, product, promotions=[])
        price_with = service.calculate_price(member, product, promotions=promos)

        assert price_with <= price_without + 0.01  # 부동소수점 반올림 허용

    @given(
        price=st.floats(min_value=0.01, max_value=10_000_000.0, allow_nan=False, allow_infinity=False),
    )
    def test_invalid_price_always_raises(self, price):
        """가격이 0 이하이면 항상 ValueError가 발생한다."""
        service = PricingService()
        member = Member(
            id=1, name="test", email="t@test.com",
            tier=MemberTier.BASIC, joined_at=datetime(2020, 1, 1),
        )
        product = Product(id=1, name="test", price=-price, category="electronics")

        with pytest.raises(ValueError):
            service.calculate_price(member, product, promotions=[])


class TestPromotionFilteringProperties:
    """프로모션 필터링 로직의 속성을 검증한다."""

    @given(
        discount_a=st.floats(min_value=0.01, max_value=0.15, allow_nan=False, allow_infinity=False),
        discount_b=st.floats(min_value=0.01, max_value=0.15, allow_nan=False, allow_infinity=False),
    )
    @time_machine.travel("2025-06-15 12:00:00")
    def test_max_promotion_wins(self, discount_a, discount_b):
        """두 프로모션 중 더 높은 할인율이 적용된다."""
        service = PricingService()
        member = Member(
            id=1, name="test", email="t@test.com",
            tier=MemberTier.BASIC, joined_at=datetime(2020, 1, 1),
        )
        product = Product(id=1, name="test", price=100_000.0, category="electronics")
        promo_a = Promotion(
            id=1, name="A", discount_rate=discount_a,
            started_at=datetime(2020, 1, 1), ended_at=datetime(2030, 12, 31),
        )
        promo_b = Promotion(
            id=2, name="B", discount_rate=discount_b,
            started_at=datetime(2020, 1, 1), ended_at=datetime(2030, 12, 31),
        )

        result = service.calculate_price(member, product, promotions=[promo_a, promo_b])
        expected = round(100_000.0 * (1 - max(discount_a, discount_b)), 2)

        assert result == expected

    @given(
        category=st.sampled_from(["electronics", "fashion", "food", "books"]),
        promo_category=st.sampled_from(["electronics", "fashion", "food", "books"]),
    )
    @time_machine.travel("2025-06-15 12:00:00")
    def test_category_filter_is_exact_match(self, category, promo_category):
        """카테고리 필터는 정확히 일치할 때만 프로모션이 적용된다."""
        service = PricingService()
        member = Member(
            id=1, name="test", email="t@test.com",
            tier=MemberTier.BASIC, joined_at=datetime(2020, 1, 1),
        )
        product = Product(id=1, name="test", price=100_000.0, category=category)
        promo = Promotion(
            id=1, name="promo", discount_rate=0.10, category=promo_category,
            started_at=datetime(2020, 1, 1), ended_at=datetime(2030, 12, 31),
        )

        result = service.calculate_price(member, product, promotions=[promo])

        if category == promo_category:
            assert result == 90_000.0
        else:
            assert result == 100_000.0
```

## 설계 근거

### factory_boy 활용

- **`MemberFactory`**: `Trait`으로 `silver`, `gold`, `platinum`, `vip_buyer` 변형을 선언했다. 테스트에서 `MemberFactory(gold=True)`처럼 한 줄로 특정 등급 회원을 생성할 수 있어 Arrange 섹션이 간결해진다.
- **`ProductFactory`**: `FuzzyFloat`와 `FuzzyChoice`로 기본값에 자연스러운 변동을 부여하되, 개별 테스트에서 `price=100_000.0`처럼 명시적으로 오버라이드하여 검증 대상 값을 통제한다.
- **`PromotionFactory`**: `Trait`으로 `expired`, `future`, `category_specific` 변형을 정의했다. 기본 생성 시 현재 시점 기준 활성 프로모션이 되도록 `started_at`/`ended_at`을 설정했다.

### Hypothesis 활용

- **불변 조건(invariant) 중심 설계**: 특정 예상값을 하드코딩하는 대신, "가격은 음수가 되지 않는다", "가격은 원가를 초과하지 않는다", "총 할인율은 30%를 넘지 않는다" 같은 속성을 검증한다.
- **`st.builds`로 도메인 객체 직접 생성**: 데이터클래스 구조를 활용하여 유효한 범위 내에서 다양한 입력을 자동 생성한다.
- **단조성(monotonicity) 검증**: 상위 등급이면 가격이 같거나 낮다, 프로모션을 추가하면 가격이 올라가지 않는다 등 비즈니스 로직의 단조 성질을 속성으로 표현했다.

### time-machine 사용

- 프로모션 기간 판정에 `datetime.now()`가 사용되므로, `time_machine.travel`로 시간을 고정하여 테스트를 반복 가능하게 만들었다. freezegun 대비 100-200배 빠른 time-machine을 선택했다.

### 테스트 구조

- **클래스별 행위 그룹화**: `TestTierDiscount`, `TestPromotionApplicability`, `TestCombinedDiscounts`, `TestEdgeCases`로 검증 대상 행위를 분리했다.
- **AAA 패턴 준수**: 모든 테스트가 Arrange-Act-Assert 구조이며, Act은 단일 호출이다.
- **출력 기반 검증 우선**: `calculate_price`의 반환값을 직접 assert하며, 내부 구현 세부사항(`_is_applicable` 호출 여부 등)을 검증하지 않는다.
- **parametrize 활용**: 등급별 할인율처럼 동일한 구조에서 데이터만 달라지는 케이스는 `@pytest.mark.parametrize`로 중복을 제거했다.
