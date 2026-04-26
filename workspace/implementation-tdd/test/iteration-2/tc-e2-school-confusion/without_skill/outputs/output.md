# TDD 관점 테스트 코드 리뷰: PriceCalculator

## 핵심 판단

**Mock 사용이 과도하다. 순수 도메인 로직 테스트에서 Mock은 불필요하며, 오히려 테스트의 가치를 떨어뜨리고 있다.**

---

## 1. 근본적인 설계 문제: 순수 도메인 로직에 Mock을 쓰면 안 되는 이유

`PriceCalculator.calculate`의 핵심 로직은 다음과 같다:

```
subtotal = base_price * quantity
discounted = subtotal * (1 - discount)
final = discounted * (1 + tax_rate)
```

이것은 **순수한 산술 연산**이다. 외부 I/O가 없고, DB 호출도 없고, 네트워크 요청도 없다. 그런데 `TaxProvider`와 `DiscountProvider`를 주입받아 Mock으로 대체하고 있다.

TDD에서 Mock의 올바른 사용처는 **제어할 수 없는 외부 의존성**(DB, API, 파일시스템 등)을 격리할 때다. 순수 도메인 로직에서 Mock을 사용하면 다음 문제가 발생한다:

- **테스트가 구현에 결합된다**: 내부적으로 어떤 메서드를 어떤 인자로 호출하는지를 검증하는 순간, 리팩터링할 때마다 테스트가 깨진다.
- **테스트가 실제 동작을 검증하지 못한다**: Mock이 반환하는 값을 테스터가 직접 세팅하므로, 실제 할인/세금 정책의 정합성은 전혀 검증되지 않는다.
- **가독성이 떨어진다**: `setup_method`에서 Mock을 만들고, 각 테스트에서 `return_value`를 세팅하는 보일러플레이트가 테스트의 의도를 가린다.

---

## 2. 개별 테스트 문제점

### `test_basic_price`, `test_with_discount`

```python
self.tax.get_tax_rate.assert_called_once_with('KR')
self.discount.get_discount.assert_called_once_with('basic', 2000)
```

`assert_called_once_with` 호출은 **행위 검증(behavior verification)**이다. "결과가 2200.0이다"라는 **상태 검증(state verification)**만으로 충분한 상황에서, 내부 호출 순서와 인자까지 검증하는 것은 과잉이다. 이렇게 하면 `calculate` 내부 구현을 조금만 바꿔도 (예: 세금을 먼저 조회하도록 순서 변경) 로직이 정확해도 테스트가 깨진다.

### `test_calls_providers_in_order`

```python
assert call_order == ['discount', 'tax']
```

**호출 순서를 검증하는 테스트는 순수 도메인 로직에서 거의 항상 잘못된 테스트다.** discount를 먼저 조회하든 tax를 먼저 조회하든 최종 계산 결과는 동일하다. 이 테스트는 "구현 세부사항"을 검증하는 것이지, "비즈니스 요구사항"을 검증하는 것이 아니다. 리팩터링 내성이 제로에 가깝다.

### `test_zero_quantity`

로직 자체는 유효한 경계값 테스트이나, Mock 세팅이 테스트의 의도를 흐린다. quantity가 0이면 결과가 0이라는 단순한 사실을 검증하기 위해 tax와 discount Mock을 세팅해야 하는 것 자체가 설계 문제를 드러낸다.

### `test_rounding`

```python
expected = round(999 * 0.85 * 1.1, 2)
assert result == expected
```

검증 로직이 프로덕션 코드의 구현을 그대로 복제하고 있다. 이런 테스트는 "구현을 두 번 작성한 것"에 불과하며, 만약 계산 공식 자체에 버그가 있으면 테스트도 동일한 버그를 가진다. 기대값은 **하드코딩된 상수**로 적는 것이 올바르다.

---

## 3. 개선 방안

### 방법 A: 순수 함수로 추출 (권장)

도메인 로직을 순수 함수로 만들면 Mock이 필요 없어진다.

```python
# 프로덕션 코드
def calculate_price(base_price: float, quantity: int, discount: float, tax_rate: float) -> float:
    subtotal = base_price * quantity
    discounted = subtotal * (1 - discount)
    return round(discounted * (1 + tax_rate), 2)


class PriceCalculator:
    """Provider 조회와 계산을 조합하는 얇은 레이어"""
    def __init__(self, tax_provider, discount_provider):
        self.tax_provider = tax_provider
        self.discount_provider = discount_provider

    def calculate(self, base_price, quantity, customer_tier):
        discount = self.discount_provider.get_discount(customer_tier, base_price * quantity)
        tax_rate = self.tax_provider.get_tax_rate('KR')
        return calculate_price(base_price, quantity, discount, tax_rate)
```

```python
# 테스트 코드 - Mock 없음
class TestCalculatePrice:
    def test_no_discount_with_tax(self):
        assert calculate_price(1000, 2, discount=0.0, tax_rate=0.1) == 2200.0

    def test_with_discount_and_tax(self):
        assert calculate_price(1000, 3, discount=0.1, tax_rate=0.1) == 2970.0

    def test_zero_quantity(self):
        assert calculate_price(1000, 0, discount=0.0, tax_rate=0.1) == 0.0

    def test_rounding(self):
        assert calculate_price(999, 1, discount=0.15, tax_rate=0.1) == 934.07
```

Mock이 사라지면서 테스트가 명확해지고, 리팩터링 내성도 높아진다.

### 방법 B: Stub 객체 사용 (Mock보다 나은 대안)

Provider 인터페이스를 유지해야 한다면, Mock 대신 간단한 Stub을 만든다.

```python
class StubTaxProvider(TaxProvider):
    def __init__(self, rate):
        self.rate = rate
    def get_tax_rate(self, country):
        return self.rate

class StubDiscountProvider(DiscountProvider):
    def __init__(self, discount):
        self.discount = discount
    def get_discount(self, tier, amount):
        return self.discount


class TestPriceCalculation:
    def test_no_discount(self):
        calc = PriceCalculator(StubTaxProvider(0.1), StubDiscountProvider(0.0))
        assert calc.calculate(1000, 2, 'basic') == 2200.0

    def test_with_discount(self):
        calc = PriceCalculator(StubTaxProvider(0.1), StubDiscountProvider(0.1))
        assert calc.calculate(1000, 3, 'gold') == 2970.0
```

Stub은 Mock과 달리 `assert_called_once_with` 같은 행위 검증을 유도하지 않으므로, 자연스럽게 상태 검증 중심의 테스트를 작성하게 된다.

---

## 4. 요약

| 항목 | 현재 코드 | 문제 |
|------|-----------|------|
| Mock 사용 | `create_autospec`으로 두 Provider Mock | 순수 계산 로직에 불필요 |
| 행위 검증 | `assert_called_once_with` 다수 | 구현 결합, 리팩터링 내성 없음 |
| 호출 순서 검증 | `test_calls_providers_in_order` | 비즈니스 요구사항이 아닌 구현 세부사항 검증 |
| 기대값 계산 | `test_rounding`에서 공식 복제 | 테스트가 프로덕션 로직을 반복, 버그 동시 재현 가능 |
| 전체 방향 | Mock 중심 테스트 | 순수 함수 추출 또는 Stub 사용으로 전환 필요 |

**결론: 이 코드는 "순수 도메인 로직인데 Mock을 많이 사용하고 있다"는 직감이 정확하다.** 핵심 계산 로직을 순수 함수로 분리하고, Mock/행위검증을 제거하면 테스트의 품질이 크게 향상된다. Mock은 외부 시스템(DB, HTTP API 등)과의 통합 지점을 테스트할 때 사용해야 한다.
