# TDD Review: PriceCalculator 테스트 코드

## 잘한 점

- AAA 패턴(Arrange-Act-Assert)의 구조가 명확하다.
- 경계값 테스트(`test_zero_quantity`)와 반올림 테스트(`test_rounding`)를 포함하고 있다.
- `create_autospec`을 사용하여 Mock의 인터페이스 정합성을 보장하고 있다.

---

## 핵심 문제: 순수 도메인 로직에 런던 학파(Mock)를 적용했다

이 코드의 가장 근본적인 문제는 **학파 선택 오류**다. `PriceCalculator.calculate()`는 산술 연산으로만 구성된 순수 도메인 로직이다. 이런 코드에는 고전 학파(실제 객체, 상태/출력 검증)가 적합하다.

| 상황 | 권장 접근법 |
|------|-----------|
| **순수 도메인 로직** | **고전 학파 (실제 객체, 상태 검증)** |
| 외부 시스템 연동 (DB, API) | 런던 학파 (Mock, 행위 검증) |

`TaxProvider`와 `DiscountProvider`는 외부 시스템(API, DB)이 아니라 도메인 내부 협력 객체다. 이들을 Mock으로 대체하면 런던 학파를 잘못 적용한 것이 된다.

---

## 리뷰 체크리스트

### [학파 선택 오류] -- 순수 도메인 로직에 런던 학파를 적용했다

`PriceCalculator`의 계산 로직은 `base_price * quantity`, 할인율 적용, 세율 적용이라는 순수 산술이다. `TaxProvider`와 `DiscountProvider`는 값을 반환하는 도메인 내부 협력 객체이므로, 실제 구현체(또는 간단한 Fake)를 사용하여 테스트해야 한다.

Mock을 사용하면 테스트가 "어떤 메서드를 어떤 인자로 호출하는가"라는 구현 세부사항에 결합되어, 내부 리팩토링 시 테스트가 깨진다.

### [통신 기반 검증 남용] -- 출력 기반 테스트가 가능한데 통신 기반 테스트를 사용했다

Khorikov의 테스트 스타일 우선순위: **출력 기반 > 상태 기반 > 통신 기반**

`calculate()`는 입력을 받아 결과를 반환하는 함수다. 반환값만 검증하면 되는 전형적인 **출력 기반 테스트** 대상이다. 그런데 매 테스트마다 `assert_called_once_with`로 통신 기반 검증을 추가하고 있다.

```python
# 불필요한 통신 기반 검증
self.tax.get_tax_rate.assert_called_once_with('KR')
self.discount.get_discount.assert_called_once_with('basic', 2000)
```

이 검증들은 `calculate()`의 내부 구현(어떤 메서드를 어떤 순서로 호출하는지)에 테스트를 결합시킨다. 반환값 `2200.0`이 정확하다면, 내부적으로 어떤 호출이 일어났는지는 테스트가 관심 가질 대상이 아니다.

### [리팩토링 내성 부재] -- 구현 변경 시 테스트가 대량으로 깨진다

현재 테스트가 검증하는 것:
1. 반환값 (출력 기반) -- 정당한 검증
2. Mock 호출 인자와 횟수 (통신 기반) -- 구현에 결합된 검증

만약 `calculate()` 내부에서 할인과 세금 계산 순서를 바꾸거나, 캐싱을 도입하거나, 메서드 시그니처를 리팩토링하면 모든 테스트가 깨진다. 이것은 거짓 양성(false positive)이다 -- 동작은 올바르지만 테스트가 실패하는 상황.

Khorikov는 리팩토링 내성을 "거짓 양성 빈도"로 측정하며, Mock 과용이 이 기둥을 훼손하는 대표 원인이라 지적한다.

### [구현 순서 검증] -- `test_calls_providers_in_order`는 화이트박스 테스트다

```python
def test_calls_providers_in_order(self):
    call_order = []
    self.discount.get_discount.side_effect = lambda *a: (call_order.append('discount'), 0.0)[1]
    self.tax.get_tax_rate.side_effect = lambda *a: (call_order.append('tax'), 0.1)[1]

    self.calc.calculate(100, 1, 'basic')

    assert call_order == ['discount', 'tax']
```

이 테스트는 가장 심각한 위반이다. 할인을 먼저 계산하든 세금을 먼저 계산하든, 최종 결과가 동일하다면 호출 순서는 구현 세부사항이다. 이 테스트는 어떤 회귀도 방지하지 못하면서 리팩토링만 방해한다.

이것은 Khorikov의 CAP 유사성에서 "회귀 방지 낮음 + 빠른 피드백 높음 + 리팩토링 내성 낮음" 영역에 해당하는, 가치 없는 테스트다.

### [통신 기반 테스트 과잉] -- assert_called_once_with를 모든 테스트에 반복하고 있다

5개 테스트 중 3개에서 `assert_called_once_with`를 사용하고 있다. 도메인 순수 함수의 테스트에서 이런 검증은 한 건도 필요하지 않다.

### [테스트 스멜: Fragile Test] -- 사소한 리팩토링에도 테스트가 깨진다

예를 들어 `get_tax_rate` 메서드에 두 번째 파라미터가 추가되거나, 내부에서 호출 방식이 바뀌면, 동작이 동일해도 `assert_called_once_with('KR')` 같은 검증이 일제히 실패한다. 이것은 전형적인 Fragile Test 스멜이다.

---

## 올바른 접근: 고전 학파로 재설계

`TaxProvider`와 `DiscountProvider`를 실제 구현체(또는 테스트용 간단한 구현체)로 교체하고, 반환값만 검증한다.

```python
import pytest


class PriceCalculator:
    def __init__(self, tax_provider, discount_provider):
        self.tax_provider = tax_provider
        self.discount_provider = discount_provider

    def calculate(self, base_price: float, quantity: int, customer_tier: str) -> float:
        subtotal = base_price * quantity
        discount = self.discount_provider.get_discount(customer_tier, subtotal)
        discounted = subtotal * (1 - discount)
        tax_rate = self.tax_provider.get_tax_rate('KR')
        return round(discounted * (1 + tax_rate), 2)


class SimpleTaxProvider:
    def __init__(self, rate: float):
        self._rate = rate

    def get_tax_rate(self, country: str) -> float:
        return self._rate


class SimpleDiscountProvider:
    def __init__(self, discount: float):
        self._discount = discount

    def get_discount(self, tier: str, amount: float) -> float:
        return self._discount


class TestPriceCalculation:
    def test_basic_price_no_discount(self):
        calc = PriceCalculator(
            tax_provider=SimpleTaxProvider(rate=0.1),
            discount_provider=SimpleDiscountProvider(discount=0.0),
        )

        result = calc.calculate(1000, 2, 'basic')

        assert result == 2200.0

    def test_price_with_discount(self):
        calc = PriceCalculator(
            tax_provider=SimpleTaxProvider(rate=0.1),
            discount_provider=SimpleDiscountProvider(discount=0.1),
        )

        result = calc.calculate(1000, 3, 'gold')

        assert result == 2970.0

    def test_zero_quantity(self):
        calc = PriceCalculator(
            tax_provider=SimpleTaxProvider(rate=0.1),
            discount_provider=SimpleDiscountProvider(discount=0.0),
        )

        result = calc.calculate(1000, 0, 'basic')

        assert result == 0.0

    def test_rounding(self):
        calc = PriceCalculator(
            tax_provider=SimpleTaxProvider(rate=0.1),
            discount_provider=SimpleDiscountProvider(discount=0.15),
        )

        result = calc.calculate(999, 1, 'platinum')

        assert result == round(999 * 0.85 * 1.1, 2)
```

### 무엇이 달라졌는가

| 항목 | 변경 전 (Mock) | 변경 후 (실제 객체) |
|------|---------------|-------------------|
| 테스트 스타일 | 통신 기반 (assert_called) | 출력 기반 (반환값 검증) |
| 리팩토링 내성 | 낮음 (내부 변경 시 깨짐) | 높음 (결과만 검증) |
| 유지보수성 | 낮음 (Mock 설정 + 호출 검증) | 높음 (Arrange가 명확) |
| 호출 순서 테스트 | 존재 (가치 없는 테스트) | 삭제 |
| 학파 | 런던 학파 (잘못 적용) | 고전 학파 (적합) |

### `test_calls_providers_in_order`를 삭제한 이유

이 테스트는 어떤 비즈니스 요구사항도 보호하지 않는다. 할인 적용 후 세금을 계산하든, 세금 적용 후 할인을 계산하든, 최종 금액이 동일하면 고객에게는 차이가 없다. 구현 순서가 결과에 영향을 미치는 경우(예: 할인 기준금액이 세전/세후에 따라 다른 경우)에는 순서가 아니라 그 결과값 차이를 테스트해야 한다.
