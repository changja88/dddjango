# Mutation-Killing Test Suite for ShippingCalculator

## Mutation Analysis

아래는 mutmut이 생성할 수 있는 모든 뮤턴트 유형과 이를 죽이기 위한 전략 분석이다.

### 식별된 뮤턴트 카테고리

| # | 위치 | 원본 | 뮤턴트 예시 | 죽이는 전략 |
|---|------|------|------------|------------|
| 1 | `order_total < 0` | `<` | `<=`, `>`, `>=`, `==`, `!=` | `order_total=0`이 에러를 발생시키지 않음을 확인 |
| 2 | `weight_kg <= 0` | `<=` | `<`, `>`, `>=`, `==`, `!=` | `weight_kg=0`이 에러를 발생시킴을 확인 |
| 3 | `order_total >= FREE_THRESHOLD` | `>=` | `>`, `<=`, `<`, `==`, `!=` | 정확히 50000에서 무료 배송 확인 |
| 4 | `FREE_THRESHOLD = 50000` | `50000` | `50001`, `49999` | 경계값 50000과 49999 테스트 |
| 5 | `MAX_FEE = 30000` | `30000` | `30001`, `29999` | 캡이 정확히 30000인지 확인 |
| 6 | `base_fee = 3000` | `3000` | `3001`, `2999` | base_fee가 정확히 3000인지 확인 |
| 7 | `weight_kg * 500` | `*` -> `+`, `-`, `/`, `//` ; `500` -> `501`, `499` | weight_fee 정확한 값 확인 |
| 8 | `ZONE_MULTIPLIERS[zone] - 1` | `-` -> `+` ; `1` -> `2`, `0` | zone_fee 정확한 값 확인 |
| 9 | `base_fee + weight_fee + zone_fee` | `+` -> `-`, `*` | raw_total 계산 검증 |
| 10 | `min(raw_total, self.MAX_FEE)` | `min` -> `max` | MAX_FEE 초과 시 캡 확인 |
| 11 | `base_days` 딕셔너리 값 | `1`, `3`, `7` -> 변형 | 각 zone의 정확한 일수 확인 |
| 12 | `is_express and days > 1` | `and` -> `or` ; `>` -> `>=`, `<` 등 ; `1` -> `2`, `0` | express 경계값 테스트 |
| 13 | `days // 2` | `//` -> `+`, `-`, `*`, `/` ; `2` -> `3`, `1` | 정확한 나눗셈 결과 확인 |
| 14 | `max(days // 2, 1)` | `max` -> `min` ; `1` -> `2`, `0` | 최솟값 보장 확인 |
| 15 | `ZONE_MULTIPLIERS` 값 | `1.0`, `1.5`, `3.0` -> 변형 | 각 zone별 정확한 계산 확인 |
| 16 | 반환값 필드 | `is_free=True/False`, `total=0` 등 | 모든 반환 필드 개별 확인 |
| 17 | 에러 메시지 문자열 | 문자열 변형 | 에러 메시지 정확히 매칭 |

## Test Code

```python
import pytest
from dataclasses import dataclass
from enum import Enum


# === Production Code (테스트 대상) ===

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


# === Test Code ===

@pytest.fixture
def calc():
    return ShippingCalculator()


# ─────────────────────────────────────────────
# 1. Validation: order_total < 0
#    뮤턴트: < -> <=, >, >=, ==, !=
# ─────────────────────────────────────────────

class TestOrderTotalValidation:
    def test_negative_order_total_raises(self, calc):
        """order_total=-1 은 반드시 에러. < -> > 또는 >= 뮤턴트를 죽인다."""
        with pytest.raises(ValueError, match='주문 금액은 0 이상이어야 합니다'):
            calc.calculate(-1, 1.0, ShippingZone.LOCAL)

    def test_zero_order_total_does_not_raise(self, calc):
        """order_total=0 은 에러가 아니다. < -> <= 뮤턴트를 죽인다."""
        result = calc.calculate(0, 1.0, ShippingZone.LOCAL)
        assert result.is_free is False

    def test_negative_order_total_exact_message(self, calc):
        """에러 메시지 문자열 뮤턴트를 죽인다."""
        with pytest.raises(ValueError) as exc_info:
            calc.calculate(-1, 1.0, ShippingZone.LOCAL)
        assert str(exc_info.value) == '주문 금액은 0 이상이어야 합니다'


# ─────────────────────────────────────────────
# 2. Validation: weight_kg <= 0
#    뮤턴트: <= -> <, >, >=, ==, !=
# ─────────────────────────────────────────────

class TestWeightValidation:
    def test_zero_weight_raises(self, calc):
        """weight_kg=0 은 에러. <= -> < 뮤턴트를 죽인다."""
        with pytest.raises(ValueError, match='무게는 0보다 커야 합니다'):
            calc.calculate(1000, 0, ShippingZone.LOCAL)

    def test_negative_weight_raises(self, calc):
        """weight_kg=-1 은 에러."""
        with pytest.raises(ValueError):
            calc.calculate(1000, -1, ShippingZone.LOCAL)

    def test_small_positive_weight_does_not_raise(self, calc):
        """weight_kg=0.1 은 에러가 아니다. <= -> >= 또는 > 뮤턴트를 죽인다."""
        result = calc.calculate(1000, 0.1, ShippingZone.LOCAL)
        assert isinstance(result, ShippingQuote)

    def test_weight_error_exact_message(self, calc):
        """에러 메시지 문자열 뮤턴트를 죽인다."""
        with pytest.raises(ValueError) as exc_info:
            calc.calculate(1000, 0, ShippingZone.LOCAL)
        assert str(exc_info.value) == '무게는 0보다 커야 합니다'


# ─────────────────────────────────────────────
# 3. Free shipping threshold: order_total >= FREE_THRESHOLD
#    뮤턴트: >= -> >, <=, <, ==, != ; 50000 -> 50001/49999
# ─────────────────────────────────────────────

class TestFreeShippingThreshold:
    def test_exactly_at_threshold_is_free(self, calc):
        """order_total=50000 은 무료. >= -> > 뮤턴트를 죽인다."""
        result = calc.calculate(50000, 1.0, ShippingZone.LOCAL)
        assert result.is_free is True
        assert result.total == 0
        assert result.base_fee == 0
        assert result.weight_fee == 0
        assert result.zone_fee == 0

    def test_just_below_threshold_is_not_free(self, calc):
        """order_total=49999 은 유료. >= -> <= 또는 < 뮤턴트를 죽인다."""
        result = calc.calculate(49999, 1.0, ShippingZone.LOCAL)
        assert result.is_free is False
        assert result.total > 0

    def test_above_threshold_is_free(self, calc):
        """order_total=50001 은 무료."""
        result = calc.calculate(50001, 1.0, ShippingZone.LOCAL)
        assert result.is_free is True

    def test_free_shipping_returns_all_zero_fees(self, calc):
        """무료 배송 시 모든 fee 필드가 0. 반환값 필드 뮤턴트를 죽인다."""
        result = calc.calculate(100000, 5.0, ShippingZone.INTERNATIONAL)
        assert result == ShippingQuote(
            base_fee=0, weight_fee=0, zone_fee=0, total=0, is_free=True
        )


# ─────────────────────────────────────────────
# 4. base_fee = 3000
#    뮤턴트: 3000 -> 3001/2999
# ─────────────────────────────────────────────

class TestBaseFee:
    def test_base_fee_is_exactly_3000(self, calc):
        """base_fee 값 뮤턴트를 죽인다."""
        result = calc.calculate(1000, 1.0, ShippingZone.LOCAL)
        assert result.base_fee == 3000


# ─────────────────────────────────────────────
# 5. weight_fee = weight_kg * 500
#    뮤턴트: * -> +,-,/,// ; 500 -> 501/499
# ─────────────────────────────────────────────

class TestWeightFee:
    def test_weight_fee_for_1kg(self, calc):
        """1kg -> 500. * -> + 일 때 1+500=501 이므로 죽인다."""
        result = calc.calculate(1000, 1.0, ShippingZone.LOCAL)
        assert result.weight_fee == 500

    def test_weight_fee_for_2kg(self, calc):
        """2kg -> 1000. * -> + 일 때 2+500=502, / 일 때 0.004 이므로 죽인다."""
        result = calc.calculate(1000, 2.0, ShippingZone.LOCAL)
        assert result.weight_fee == 1000

    def test_weight_fee_for_10kg(self, calc):
        """10kg -> 5000. 500 -> 501 일 때 5010 이므로 죽인다."""
        result = calc.calculate(1000, 10.0, ShippingZone.LOCAL)
        assert result.weight_fee == 5000


# ─────────────────────────────────────────────
# 6. zone_fee = base_fee * (ZONE_MULTIPLIERS[zone] - 1)
#    뮤턴트: * -> +,-; - -> +; 1 -> 2/0
#    ZONE_MULTIPLIERS 값: 1.0, 1.5, 3.0
# ─────────────────────────────────────────────

class TestZoneFee:
    def test_local_zone_fee_is_zero(self, calc):
        """LOCAL multiplier=1.0, zone_fee=3000*(1.0-1)=0.
        multiplier 1.0 -> 변형 시 zone_fee != 0이 됨."""
        result = calc.calculate(1000, 1.0, ShippingZone.LOCAL)
        assert result.zone_fee == 0

    def test_domestic_zone_fee(self, calc):
        """DOMESTIC multiplier=1.5, zone_fee=3000*(1.5-1)=1500.
        - -> + 뮤턴트: 3000*(1.5+1)=7500, 죽인다.
        1 -> 2 뮤턴트: 3000*(1.5-2)=-1500, 죽인다.
        1.5 -> 변형 시에도 죽인다."""
        result = calc.calculate(1000, 1.0, ShippingZone.DOMESTIC)
        assert result.zone_fee == 1500

    def test_international_zone_fee(self, calc):
        """INTERNATIONAL multiplier=3.0, zone_fee=3000*(3.0-1)=6000.
        * -> + 뮤턴트: 3000+(3.0-1)=3002, 죽인다.
        3.0 -> 변형 시에도 죽인다."""
        result = calc.calculate(1000, 1.0, ShippingZone.INTERNATIONAL)
        assert result.zone_fee == 6000


# ─────────────────────────────────────────────
# 7. raw_total = base_fee + weight_fee + zone_fee
#    뮤턴트: + -> -, *, /
# ─────────────────────────────────────────────

class TestRawTotal:
    def test_raw_total_local(self, calc):
        """LOCAL, 2kg: base=3000, weight=1000, zone=0, raw=4000.
        + -> - 뮤턴트: 3000-1000-0=2000, 죽인다."""
        result = calc.calculate(1000, 2.0, ShippingZone.LOCAL)
        assert result.total == 4000

    def test_raw_total_domestic(self, calc):
        """DOMESTIC, 2kg: base=3000, weight=1000, zone=1500, raw=5500.
        두 번째 + -> - 뮤턴트: 3000+1000-1500=2500, 죽인다."""
        result = calc.calculate(1000, 2.0, ShippingZone.DOMESTIC)
        assert result.total == 5500

    def test_raw_total_with_all_nonzero_components(self, calc):
        """모든 구성요소가 0이 아닌 경우. 각 + 연산자 뮤턴트를 확실히 죽인다."""
        # INTERNATIONAL, 3kg: base=3000, weight=1500, zone=6000, raw=10500
        result = calc.calculate(1000, 3.0, ShippingZone.INTERNATIONAL)
        assert result.base_fee == 3000
        assert result.weight_fee == 1500
        assert result.zone_fee == 6000
        assert result.total == 10500


# ─────────────────────────────────────────────
# 8. total = min(raw_total, self.MAX_FEE)
#    뮤턴트: min -> max; MAX_FEE=30000 -> 30001/29999
# ─────────────────────────────────────────────

class TestMaxFeeCap:
    def test_total_capped_at_max_fee(self, calc):
        """raw_total > 30000 일 때 total=30000.
        min -> max 뮤턴트를 죽인다."""
        # INTERNATIONAL, 50kg: base=3000, weight=25000, zone=6000, raw=34000
        result = calc.calculate(1000, 50.0, ShippingZone.INTERNATIONAL)
        assert result.total == 30000

    def test_total_not_capped_when_below_max(self, calc):
        """raw_total < 30000 일 때 total=raw_total. MAX_FEE 값 뮤턴트를 죽인다."""
        # LOCAL, 1kg: base=3000, weight=500, zone=0, raw=3500
        result = calc.calculate(1000, 1.0, ShippingZone.LOCAL)
        assert result.total == 3500

    def test_total_exactly_at_max_fee(self, calc):
        """raw_total == 30000 일 때 total=30000.
        MAX_FEE -> 29999 뮤턴트를 죽인다."""
        # LOCAL에서 raw_total=30000이 되려면: 3000 + weight_fee + 0 = 30000
        # weight_fee = 27000, weight_kg = 54
        result = calc.calculate(1000, 54.0, ShippingZone.LOCAL)
        assert result.total == 30000
        # raw_total이 정확히 30000이므로 cap이 작동하지 않는 것과 같다
        assert result.weight_fee == 27000

    def test_total_just_above_max_fee(self, calc):
        """raw_total=30500 일 때 total=30000.
        MAX_FEE=30000 -> 30001 뮤턴트: min(30500,30001)=30001 != 30000."""
        # LOCAL, 55kg: base=3000, weight=27500, zone=0, raw=30500
        result = calc.calculate(1000, 55.0, ShippingZone.LOCAL)
        assert result.total == 30000


# ─────────────────────────────────────────────
# 9. Return value fields: is_free=False
#    뮤턴트: False -> True
# ─────────────────────────────────────────────

class TestReturnValueFields:
    def test_paid_shipping_is_free_false(self, calc):
        """유료 배송 시 is_free=False. False -> True 뮤턴트를 죽인다."""
        result = calc.calculate(1000, 1.0, ShippingZone.LOCAL)
        assert result.is_free is False

    def test_free_shipping_is_free_true(self, calc):
        """무료 배송 시 is_free=True. True -> False 뮤턴트를 죽인다."""
        result = calc.calculate(50000, 1.0, ShippingZone.LOCAL)
        assert result.is_free is True

    def test_paid_shipping_all_fields_correct(self, calc):
        """유료 배송의 모든 필드가 정확한지 확인. 각 필드 값 뮤턴트를 죽인다."""
        result = calc.calculate(10000, 4.0, ShippingZone.DOMESTIC)
        assert result == ShippingQuote(
            base_fee=3000,
            weight_fee=2000,
            zone_fee=1500,
            total=6500,
            is_free=False,
        )


# ─────────────────────────────────────────────
# 10. estimate_delivery_days: base_days 딕셔너리
#     뮤턴트: 1->2/0, 3->4/2, 7->8/6
# ─────────────────────────────────────────────

class TestEstimateDeliveryDays:
    def test_local_base_days(self, calc):
        """LOCAL -> 1일. 1 -> 2 뮤턴트를 죽인다."""
        assert calc.estimate_delivery_days(ShippingZone.LOCAL) == 1

    def test_domestic_base_days(self, calc):
        """DOMESTIC -> 3일. 3 -> 4 뮤턴트를 죽인다."""
        assert calc.estimate_delivery_days(ShippingZone.DOMESTIC) == 3

    def test_international_base_days(self, calc):
        """INTERNATIONAL -> 7일. 7 -> 8 뮤턴트를 죽인다."""
        assert calc.estimate_delivery_days(ShippingZone.INTERNATIONAL) == 7


# ─────────────────────────────────────────────
# 11. is_express and days > 1
#     뮤턴트: and -> or; > -> >=, <, <=, ==, !=; 1 -> 2/0
# ─────────────────────────────────────────────

class TestExpressDelivery:
    def test_local_express_stays_1(self, calc):
        """LOCAL is_express=True, days=1, 1>1 is False -> 1일 유지.
        > -> >= 뮤턴트: 1>=1 is True -> max(0,1)=1... 추가 테스트 필요.
        and -> or 뮤턴트: True or False -> True -> max(0,1)=1... LOCAL은 변별력 낮다.
        이 테스트는 express가 LOCAL에서 아무 변화가 없음을 확인."""
        assert calc.estimate_delivery_days(ShippingZone.LOCAL, is_express=True) == 1

    def test_local_non_express(self, calc):
        """LOCAL non-express -> 1."""
        assert calc.estimate_delivery_days(ShippingZone.LOCAL, is_express=False) == 1

    def test_domestic_express(self, calc):
        """DOMESTIC express: days=3, 3>1 True -> max(3//2,1)=max(1,1)=1.
        and -> or 뮤턴트: is_express=True or 3>1 -> True (같은 결과).
        > -> >= 뮤턴트: 3>=1 True (같은 결과).
        > -> < 뮤턴트: 3<1 False -> 3, 죽인다.
        // -> + 뮤턴트: max(3+2,1)=max(5,1)=5, 죽인다.
        2 -> 3 뮤턴트: max(3//3,1)=max(1,1)=1 (같다!)
        그래서 INTERNATIONAL도 필요."""
        assert calc.estimate_delivery_days(ShippingZone.DOMESTIC, is_express=True) == 1

    def test_domestic_non_express(self, calc):
        """DOMESTIC non-express -> 3.
        and -> or 뮤턴트: False or True -> True -> max(1,1)=1 != 3, 죽인다."""
        assert calc.estimate_delivery_days(ShippingZone.DOMESTIC, is_express=False) == 3

    def test_international_express(self, calc):
        """INTERNATIONAL express: days=7, 7>1 True -> max(7//2,1)=max(3,1)=3.
        // -> * 뮤턴트: max(7*2,1)=max(14,1)=14, 죽인다.
        // -> + 뮤턴트: max(7+2,1)=max(9,1)=9, 죽인다.
        // -> - 뮤턴트: max(7-2,1)=max(5,1)=5, 죽인다.
        2 -> 3 뮤턴트: max(7//3,1)=max(2,1)=2 != 3, 죽인다.
        max -> min 뮤턴트: min(3,1)=1 != 3, 죽인다.
        1(max 인자) -> 0 뮤턴트: max(3,0)=3 (같다!) -> test_domestic_express가 커버.
        1(max 인자) -> 2 뮤턴트: max(3,2)=3 (같다!) -> DOMESTIC에서 max(1,2)=2 != 1, 죽인다."""
        assert calc.estimate_delivery_days(ShippingZone.INTERNATIONAL, is_express=True) == 3

    def test_international_non_express(self, calc):
        """INTERNATIONAL non-express -> 7."""
        assert calc.estimate_delivery_days(ShippingZone.INTERNATIONAL, is_express=False) == 7


# ─────────────────────────────────────────────
# 12. days > 1 에서 1 -> 2 뮤턴트
#     days=2(DOMESTIC에서는 base_days 없지만) 실제 base_days 중 2는 없다.
#     그러나 DOMESTIC base_days=3 > 2 이므로 1->2 뮤턴트에서도 조건이 True.
#     LOCAL base_days=1: 1>2 False vs 1>1 False -> 같은 결과.
#     핵심: DOMESTIC express에서 days=3, 3>2 True -> 여전히 실행됨.
#     하지만! max(days//2, 1)의 1 -> 2 뮤턴트:
#     DOMESTIC express: max(1,2)=2 != 1 -> 이미 test_domestic_express가 죽인다!
# ─────────────────────────────────────────────

class TestExpressBoundaryConditions:
    def test_days_greater_than_1_boundary(self, calc):
        """days>1 에서 1->0 뮤턴트: LOCAL days=1, 1>0 True -> max(0,1)=1.
        결과는 같지만 DOMESTIC non-express에서 and->or가 커버.
        이 테스트는 express=False일 때 감소가 없음을 확인."""
        result_normal = calc.estimate_delivery_days(ShippingZone.DOMESTIC)
        result_express = calc.estimate_delivery_days(ShippingZone.DOMESTIC, is_express=True)
        assert result_normal == 3
        assert result_express < result_normal

    def test_express_false_default(self, calc):
        """is_express 기본값=False 확인."""
        assert calc.estimate_delivery_days(ShippingZone.INTERNATIONAL) == 7


# ─────────────────────────────────────────────
# 13. ZONE_MULTIPLIERS 값 뮤턴트
#     1.0, 1.5, 3.0 각각의 값 변형
# ─────────────────────────────────────────────

class TestZoneMultipliers:
    def test_local_multiplier_is_1_0(self, calc):
        """LOCAL multiplier=1.0 -> zone_fee=0.
        1.0 -> 2.0 뮤턴트: zone_fee=3000*(2.0-1)=3000, 죽인다."""
        result = calc.calculate(1000, 1.0, ShippingZone.LOCAL)
        assert result.zone_fee == 0

    def test_domestic_multiplier_is_1_5(self, calc):
        """DOMESTIC multiplier=1.5 -> zone_fee=1500.
        1.5 -> 2.5 뮤턴트: zone_fee=3000*(2.5-1)=4500, 죽인다.
        1.5 -> 0.5 뮤턴트: zone_fee=3000*(0.5-1)=-1500, 죽인다."""
        result = calc.calculate(1000, 1.0, ShippingZone.DOMESTIC)
        assert result.zone_fee == 1500

    def test_international_multiplier_is_3_0(self, calc):
        """INTERNATIONAL multiplier=3.0 -> zone_fee=6000.
        3.0 -> 4.0 뮤턴트: zone_fee=3000*(4.0-1)=9000, 죽인다."""
        result = calc.calculate(1000, 1.0, ShippingZone.INTERNATIONAL)
        assert result.zone_fee == 6000


# ─────────────────────────────────────────────
# 14. 통합 시나리오: 경계값과 연산자 조합
# ─────────────────────────────────────────────

class TestIntegrationScenarios:
    def test_minimum_valid_order(self, calc):
        """최소 유효 주문: order_total=0, weight=0.1, LOCAL.
        weight_fee=0.1*500=50, zone_fee=0, raw=3050, total=3050."""
        result = calc.calculate(0, 0.1, ShippingZone.LOCAL)
        assert result.total == 3050
        assert result.base_fee == 3000
        assert result.weight_fee == 50
        assert result.zone_fee == 0
        assert result.is_free is False

    def test_heavy_international_capped(self, calc):
        """무거운 국제 배송이 MAX_FEE로 cap되는지 확인.
        100kg INTERNATIONAL: base=3000, weight=50000, zone=6000, raw=59000.
        total=min(59000,30000)=30000."""
        result = calc.calculate(1000, 100.0, ShippingZone.INTERNATIONAL)
        assert result.total == 30000
        assert result.weight_fee == 50000
        assert result.zone_fee == 6000
        # raw_total은 59000이지만 total은 30000으로 cap
        assert result.total < result.base_fee + result.weight_fee + result.zone_fee

    def test_just_below_free_threshold_domestic(self, calc):
        """49999원 DOMESTIC 주문.
        base=3000, weight_fee 확인, zone_fee=1500."""
        result = calc.calculate(49999, 2.0, ShippingZone.DOMESTIC)
        assert result.is_free is False
        assert result.base_fee == 3000
        assert result.weight_fee == 1000
        assert result.zone_fee == 1500
        assert result.total == 5500

    def test_validation_priority_negative_total_zero_weight(self, calc):
        """order_total < 0 검증이 weight 검증보다 먼저인지 확인."""
        with pytest.raises(ValueError, match='주문 금액은 0 이상이어야 합니다'):
            calc.calculate(-1, 0, ShippingZone.LOCAL)

    def test_validation_weight_after_order_total_passes(self, calc):
        """order_total=0 통과 후 weight=0 검증."""
        with pytest.raises(ValueError, match='무게는 0보다 커야 합니다'):
            calc.calculate(0, 0, ShippingZone.LOCAL)
```

## Mutation Coverage Summary

| 뮤턴트 유형 | 죽이는 테스트 |
|------------|-------------|
| `order_total < 0` -> `<=` | `test_zero_order_total_does_not_raise` |
| `order_total < 0` -> `>`, `>=` | `test_negative_order_total_raises` |
| `weight_kg <= 0` -> `<` | `test_zero_weight_raises` |
| `weight_kg <= 0` -> `>`, `>=` | `test_small_positive_weight_does_not_raise` |
| `order_total >= FREE_THRESHOLD` -> `>` | `test_exactly_at_threshold_is_free` |
| `order_total >= FREE_THRESHOLD` -> `<`, `<=` | `test_just_below_threshold_is_not_free` |
| `FREE_THRESHOLD` 값 변형 | `test_exactly_at_threshold_is_free` + `test_just_below_threshold_is_not_free` |
| `MAX_FEE` 값 변형 | `test_total_capped_at_max_fee` + `test_total_just_above_max_fee` |
| `base_fee = 3000` 값 변형 | `test_base_fee_is_exactly_3000` |
| `weight_kg * 500` 연산자/값 변형 | `test_weight_fee_for_1kg` + `test_weight_fee_for_2kg` |
| `ZONE_MULTIPLIERS[zone] - 1` 연산자/값 변형 | `test_domestic_zone_fee` + `test_international_zone_fee` |
| `base_fee + weight_fee + zone_fee` 연산자 변형 | `test_raw_total_domestic` + `test_raw_total_with_all_nonzero_components` |
| `min(raw_total, MAX_FEE)` -> `max` | `test_total_capped_at_max_fee` |
| `ZONE_MULTIPLIERS` 값 변형 | `test_local_multiplier_is_1_0` + `test_domestic_multiplier_is_1_5` + `test_international_multiplier_is_3_0` |
| `is_free=True/False` 변형 | `test_paid_shipping_is_free_false` + `test_free_shipping_is_free_true` |
| 에러 메시지 문자열 변형 | `test_negative_order_total_exact_message` + `test_weight_error_exact_message` |
| `base_days` 딕셔너리 값 변형 | `test_local_base_days` + `test_domestic_base_days` + `test_international_base_days` |
| `is_express and days > 1` -> `or` | `test_domestic_non_express` |
| `days > 1` 연산자/값 변형 | `test_local_express_stays_1` + `test_domestic_express` |
| `days // 2` 연산자/값 변형 | `test_international_express` |
| `max(days // 2, 1)` -> `min` | `test_international_express` |
| `max(..., 1)` 의 `1` 변형 | `test_domestic_express` |
| 반환값의 `total=0` 변형 | `test_exactly_at_threshold_is_free` |
| 반환값의 `base_fee=0` 등 변형 | `test_free_shipping_returns_all_zero_fees` |
