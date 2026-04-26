# Mutation-Resilient Tests for ShippingCalculator

## Mutation Analysis

Before writing tests, I identified every mutation point mutmut would target:

### `calculate` method mutations
| # | Original | Possible Mutation | Kill Strategy |
|---|----------|-------------------|---------------|
| 1 | `order_total < 0` | `order_total <= 0` | Test with `order_total=0` -- must not raise |
| 2 | `weight_kg <= 0` | `weight_kg < 0` | Test with `weight_kg=0` -- must raise |
| 3 | `order_total >= self.FREE_THRESHOLD` | `order_total > self.FREE_THRESHOLD` | Test with `order_total=50000` exactly -- must be free |
| 4 | `base_fee = 3000` | `base_fee = 3001` etc. | Assert exact `base_fee` value |
| 5 | `weight_kg * 500` | `weight_kg * 501`, `weight_kg + 500` etc. | Assert exact `weight_fee` with known weight |
| 6 | `self.ZONE_MULTIPLIERS[zone] - 1` | `... + 1` | Assert exact `zone_fee` for LOCAL (must be 0) and DOMESTIC |
| 7 | `base_fee + weight_fee + zone_fee` | Any `+` to `-` | Assert exact `total` vs computed components |
| 8 | `min(raw_total, self.MAX_FEE)` | Removing `min`, swapping args | Test case where `raw_total > MAX_FEE` and one where `raw_total < MAX_FEE` |
| 9 | `is_free=True` / `is_free=False` | Swap True/False | Assert `is_free` in both free and non-free cases |
| 10 | Return structure fields | Swap or zero out fields | Assert every field of `ShippingQuote` in each scenario |

### `estimate_delivery_days` mutations
| # | Original | Possible Mutation | Kill Strategy |
|---|----------|-------------------|---------------|
| 11 | `LOCAL: 1` | `LOCAL: 2` etc. | Assert exact day count per zone |
| 12 | `DOMESTIC: 3` | `DOMESTIC: 2` or `4` | Assert exact day count |
| 13 | `INTERNATIONAL: 7` | `INTERNATIONAL: 6` or `8` | Assert exact day count |
| 14 | `days > 1` | `days >= 1`, `days > 2` etc. | Test LOCAL express (days=1, should NOT halve) and DOMESTIC express (days=3, should halve) |
| 15 | `days // 2` | `days // 3`, `days * 2` etc. | Assert exact express day counts |
| 16 | `max(days // 2, 1)` | Remove `max`, change `1` | Test DOMESTIC express: `3 // 2 = 1`, so `max(1, 1) = 1` -- need INTERNATIONAL express: `7 // 2 = 3` to differentiate `//` mutations |
| 17 | `is_express and days > 1` | `is_express or days > 1` | Test non-express with days > 1 -- must return full days |

## Test Code

```python
import pytest
from dataclasses import dataclass
from enum import Enum


class ShippingZone(Enum):
    LOCAL = 'local'
    DOMESTIC = 'domestic'
    INTERNATIONAL = 'international'


@dataclass(frozen=True)
class ShippingQuote:
    base_fee: float
    weight_fee: float
    zone_fee: float
    total: float
    is_free: bool


class ShippingCalculator:
    FREE_THRESHOLD = 50000
    MAX_FEE = 30000
    ZONE_MULTIPLIERS = {
        ShippingZone.LOCAL: 1.0,
        ShippingZone.DOMESTIC: 1.5,
        ShippingZone.INTERNATIONAL: 3.0,
    }

    def calculate(self, order_total: float, weight_kg: float, zone: ShippingZone) -> ShippingQuote:
        if order_total < 0:
            raise ValueError('주문 금액은 0 이상이어야 합니다')
        if weight_kg <= 0:
            raise ValueError('무게는 0보다 커야 합니다')

        if order_total >= self.FREE_THRESHOLD:
            return ShippingQuote(base_fee=0, weight_fee=0, zone_fee=0, total=0, is_free=True)

        base_fee = 3000
        weight_fee = weight_kg * 500
        zone_fee = base_fee * (self.ZONE_MULTIPLIERS[zone] - 1)
        raw_total = base_fee + weight_fee + zone_fee

        total = min(raw_total, self.MAX_FEE)
        return ShippingQuote(
            base_fee=base_fee,
            weight_fee=weight_fee,
            zone_fee=zone_fee,
            total=total,
            is_free=False,
        )

    def estimate_delivery_days(self, zone: ShippingZone, is_express: bool = False) -> int:
        base_days = {
            ShippingZone.LOCAL: 1,
            ShippingZone.DOMESTIC: 3,
            ShippingZone.INTERNATIONAL: 7,
        }
        days = base_days[zone]
        if is_express and days > 1:
            days = max(days // 2, 1)
        return days


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.fixture
def calculator():
    return ShippingCalculator()


# ===== calculate: input validation =====


class TestCalculateValidation:
    def test_negative_order_total_raises(self, calculator):
        """order_total < 0 raises ValueError. Kills: < mutated to <=."""
        with pytest.raises(ValueError, match='주문 금액'):
            calculator.calculate(order_total=-1, weight_kg=1, zone=ShippingZone.LOCAL)

    def test_zero_order_total_does_not_raise(self, calculator):
        """order_total=0 is valid. Kills: < 0 mutated to <= 0."""
        quote = calculator.calculate(order_total=0, weight_kg=1, zone=ShippingZone.LOCAL)
        assert quote.is_free is False

    def test_zero_weight_raises(self, calculator):
        """weight_kg=0 must raise. Kills: <= 0 mutated to < 0."""
        with pytest.raises(ValueError, match='무게'):
            calculator.calculate(order_total=1000, weight_kg=0, zone=ShippingZone.LOCAL)

    def test_negative_weight_raises(self, calculator):
        with pytest.raises(ValueError, match='무게'):
            calculator.calculate(order_total=1000, weight_kg=-1, zone=ShippingZone.LOCAL)

    def test_positive_weight_does_not_raise(self, calculator):
        """weight_kg=0.1 is valid. Ensures <= boundary is correct."""
        quote = calculator.calculate(order_total=1000, weight_kg=0.1, zone=ShippingZone.LOCAL)
        assert quote.weight_fee == pytest.approx(0.1 * 500)


# ===== calculate: free shipping threshold =====


class TestFreeShipping:
    def test_exactly_at_threshold_is_free(self, calculator):
        """order_total == FREE_THRESHOLD triggers free shipping.
        Kills: >= mutated to >.
        """
        quote = calculator.calculate(
            order_total=50000, weight_kg=1, zone=ShippingZone.LOCAL
        )
        assert quote.is_free is True
        assert quote.total == 0
        assert quote.base_fee == 0
        assert quote.weight_fee == 0
        assert quote.zone_fee == 0

    def test_just_below_threshold_is_not_free(self, calculator):
        """order_total == FREE_THRESHOLD - 1 is not free.
        Kills: >= mutated to > (complementary boundary).
        """
        quote = calculator.calculate(
            order_total=49999, weight_kg=1, zone=ShippingZone.LOCAL
        )
        assert quote.is_free is False
        assert quote.total > 0

    def test_above_threshold_is_free(self, calculator):
        quote = calculator.calculate(
            order_total=100000, weight_kg=10, zone=ShippingZone.INTERNATIONAL
        )
        assert quote.is_free is True
        assert quote.total == 0


# ===== calculate: fee computation per zone =====


class TestFeeComputation:
    def test_local_zone_fees(self, calculator):
        """LOCAL multiplier is 1.0, so zone_fee = 3000 * (1.0 - 1) = 0.
        Kills: multiplier constant mutations, - mutated to +, base_fee constant mutation.
        """
        quote = calculator.calculate(
            order_total=10000, weight_kg=2, zone=ShippingZone.LOCAL
        )
        assert quote.base_fee == 3000
        assert quote.weight_fee == pytest.approx(2 * 500)
        assert quote.zone_fee == pytest.approx(0)
        assert quote.total == pytest.approx(3000 + 1000 + 0)
        assert quote.is_free is False

    def test_domestic_zone_fees(self, calculator):
        """DOMESTIC multiplier is 1.5, so zone_fee = 3000 * (1.5 - 1) = 1500.
        Kills: 1.5 constant mutation, arithmetic operator mutations in zone_fee.
        """
        quote = calculator.calculate(
            order_total=10000, weight_kg=2, zone=ShippingZone.DOMESTIC
        )
        assert quote.base_fee == 3000
        assert quote.weight_fee == pytest.approx(1000)
        assert quote.zone_fee == pytest.approx(1500)
        assert quote.total == pytest.approx(3000 + 1000 + 1500)
        assert quote.is_free is False

    def test_international_zone_fees(self, calculator):
        """INTERNATIONAL multiplier is 3.0, so zone_fee = 3000 * (3.0 - 1) = 6000.
        Kills: 3.0 constant mutation.
        """
        quote = calculator.calculate(
            order_total=10000, weight_kg=2, zone=ShippingZone.INTERNATIONAL
        )
        assert quote.base_fee == 3000
        assert quote.weight_fee == pytest.approx(1000)
        assert quote.zone_fee == pytest.approx(6000)
        assert quote.total == pytest.approx(3000 + 1000 + 6000)
        assert quote.is_free is False

    def test_weight_fee_scales_with_weight(self, calculator):
        """weight_fee = weight_kg * 500. Using weight_kg=1 isolates the 500 constant.
        Kills: * mutated to +, 500 constant mutation.
        """
        quote = calculator.calculate(
            order_total=10000, weight_kg=1, zone=ShippingZone.LOCAL
        )
        assert quote.weight_fee == pytest.approx(500)

    def test_weight_fee_with_different_weight(self, calculator):
        """Using weight_kg=3 to distinguish * from +. (3*500=1500 vs 3+500=503).
        Kills: * mutated to +.
        """
        quote = calculator.calculate(
            order_total=10000, weight_kg=3, zone=ShippingZone.LOCAL
        )
        assert quote.weight_fee == pytest.approx(1500)


# ===== calculate: MAX_FEE cap =====


class TestMaxFeeCap:
    def test_total_below_max_fee_is_not_capped(self, calculator):
        """raw_total < MAX_FEE: total equals raw_total.
        Kills: min() removal or argument swap when combined with capped test.
        """
        quote = calculator.calculate(
            order_total=10000, weight_kg=1, zone=ShippingZone.LOCAL
        )
        raw = 3000 + 500 + 0
        assert raw < ShippingCalculator.MAX_FEE
        assert quote.total == pytest.approx(raw)

    def test_total_above_max_fee_is_capped(self, calculator):
        """raw_total > MAX_FEE: total is capped at MAX_FEE.
        Kills: min() removal, MAX_FEE constant mutation.
        Using INTERNATIONAL with heavy weight to exceed 30000.
        raw = 3000 + (50*500) + 6000 = 3000 + 25000 + 6000 = 34000 > 30000.
        """
        quote = calculator.calculate(
            order_total=10000, weight_kg=50, zone=ShippingZone.INTERNATIONAL
        )
        assert quote.total == 30000
        raw = quote.base_fee + quote.weight_fee + quote.zone_fee
        assert raw > 30000

    def test_total_exactly_at_max_fee(self, calculator):
        """raw_total == MAX_FEE: total equals MAX_FEE.
        min(30000, 30000) = 30000. Kills boundary mutations of min().
        raw = 3000 + weight_fee + zone_fee = 30000.
        LOCAL zone_fee = 0, so weight_fee = 27000 -> weight = 54.
        """
        quote = calculator.calculate(
            order_total=10000, weight_kg=54, zone=ShippingZone.LOCAL
        )
        raw = 3000 + 54 * 500 + 0
        assert raw == 30000
        assert quote.total == pytest.approx(30000)


# ===== calculate: return value structure =====


class TestReturnStructure:
    def test_free_quote_all_fields(self, calculator):
        """Verify every field of the free shipping quote.
        Kills: any field swap or default value mutation in the free return.
        """
        quote = calculator.calculate(
            order_total=50000, weight_kg=1, zone=ShippingZone.LOCAL
        )
        assert quote.base_fee == 0
        assert quote.weight_fee == 0
        assert quote.zone_fee == 0
        assert quote.total == 0
        assert quote.is_free is True

    def test_paid_quote_all_fields(self, calculator):
        """Verify every field of the paid shipping quote.
        Kills: any field swap or default value mutation in the paid return.
        """
        quote = calculator.calculate(
            order_total=10000, weight_kg=2, zone=ShippingZone.DOMESTIC
        )
        assert quote.base_fee == 3000
        assert quote.weight_fee == pytest.approx(1000)
        assert quote.zone_fee == pytest.approx(1500)
        assert quote.total == pytest.approx(5500)
        assert quote.is_free is False


# ===== estimate_delivery_days: base days =====


class TestEstimateDeliveryDays:
    @pytest.mark.parametrize(
        'zone, expected_days',
        [
            (ShippingZone.LOCAL, 1),
            (ShippingZone.DOMESTIC, 3),
            (ShippingZone.INTERNATIONAL, 7),
        ],
    )
    def test_standard_delivery_days(self, calculator, zone, expected_days):
        """Each zone returns its specific base days.
        Kills: constant mutations in base_days dict (1, 3, 7).
        """
        assert calculator.estimate_delivery_days(zone) == expected_days

    def test_local_express_no_reduction(self, calculator):
        """LOCAL has 1 day. Express does not reduce because days > 1 is False.
        Kills: > 1 mutated to >= 1 (would incorrectly halve 1-day delivery).
        """
        assert calculator.estimate_delivery_days(ShippingZone.LOCAL, is_express=True) == 1

    def test_domestic_express_halved(self, calculator):
        """DOMESTIC: 3 // 2 = 1, max(1, 1) = 1.
        Kills: // 2 mutations, and condition mutations for days > 1.
        """
        assert calculator.estimate_delivery_days(ShippingZone.DOMESTIC, is_express=True) == 1

    def test_international_express_halved(self, calculator):
        """INTERNATIONAL: 7 // 2 = 3, max(3, 1) = 3.
        Kills: // mutated to /, // 2 mutated to // 3, max() removal.
        """
        assert calculator.estimate_delivery_days(ShippingZone.INTERNATIONAL, is_express=True) == 3

    def test_non_express_domestic_full_days(self, calculator):
        """DOMESTIC without express returns full 3 days.
        Kills: 'and' mutated to 'or' (would incorrectly halve non-express).
        """
        assert calculator.estimate_delivery_days(ShippingZone.DOMESTIC, is_express=False) == 3

    def test_non_express_international_full_days(self, calculator):
        """INTERNATIONAL without express returns full 7 days.
        Kills: 'and' mutated to 'or'.
        """
        assert calculator.estimate_delivery_days(ShippingZone.INTERNATIONAL, is_express=False) == 7
```

## Mutation Kill Matrix

Each test targets specific mutant types. Here is the comprehensive mapping:

### Comparison Operator Mutations
| Mutation | Killed By |
|----------|-----------|
| `order_total < 0` -> `<= 0` | `test_zero_order_total_does_not_raise` |
| `weight_kg <= 0` -> `< 0` | `test_zero_weight_raises` |
| `order_total >= FREE_THRESHOLD` -> `>` | `test_exactly_at_threshold_is_free` |
| `days > 1` -> `>= 1` | `test_local_express_no_reduction` |
| `days > 1` -> `> 2` | `test_domestic_express_halved` |

### Arithmetic Operator Mutations
| Mutation | Killed By |
|----------|-----------|
| `weight_kg * 500` -> `weight_kg + 500` | `test_weight_fee_with_different_weight` (1500 vs 503) |
| `ZONE_MULTIPLIERS[zone] - 1` -> `+ 1` | `test_domestic_zone_fees` (1500 vs 7500) |
| `base_fee + weight_fee + zone_fee` -> any `-` | `test_local_zone_fees`, `test_domestic_zone_fees` |
| `days // 2` -> `days // 3` | `test_international_express_halved` (3 vs 2) |
| `days // 2` -> `days * 2` | `test_domestic_express_halved` (1 vs 6) |

### Constant Mutations
| Mutation | Killed By |
|----------|-----------|
| `3000` -> other | `test_local_zone_fees` (assert base_fee == 3000) |
| `500` -> other | `test_weight_fee_scales_with_weight` (assert 500) |
| `FREE_THRESHOLD = 50000` -> other | `test_exactly_at_threshold_is_free` + `test_just_below_threshold_is_not_free` |
| `MAX_FEE = 30000` -> other | `test_total_above_max_fee_is_capped` (assert 30000) |
| `1.0` multiplier | `test_local_zone_fees` (zone_fee must be 0) |
| `1.5` multiplier | `test_domestic_zone_fees` (zone_fee must be 1500) |
| `3.0` multiplier | `test_international_zone_fees` (zone_fee must be 6000) |
| `base_days LOCAL: 1` | `test_standard_delivery_days` parametrized |
| `base_days DOMESTIC: 3` | `test_standard_delivery_days` parametrized |
| `base_days INTERNATIONAL: 7` | `test_standard_delivery_days` parametrized |
| `is_free=True` -> False | `test_free_quote_all_fields` |
| `is_free=False` -> True | `test_paid_quote_all_fields` |

### Logical Operator Mutations
| Mutation | Killed By |
|----------|-----------|
| `is_express and days > 1` -> `or` | `test_non_express_domestic_full_days` (3 vs 1) |

### Function Call Mutations
| Mutation | Killed By |
|----------|-----------|
| `min(raw_total, MAX_FEE)` removed | `test_total_above_max_fee_is_capped` |
| `max(days // 2, 1)` removed | `test_international_express_halved` |

### Statement Deletion Mutations
| Mutation | Killed By |
|----------|-----------|
| Delete `raise ValueError` (order) | `test_negative_order_total_raises` |
| Delete `raise ValueError` (weight) | `test_zero_weight_raises` |
| Delete `days = max(...)` line | `test_domestic_express_halved`, `test_international_express_halved` |
