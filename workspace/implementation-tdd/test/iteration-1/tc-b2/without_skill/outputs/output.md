# Test Smells 분석 결과

## 1. Eager Test (과욕 테스트)

**위치:** `test_calculator()`, `test_all_operations_with_negative()`

하나의 테스트 함수가 여러 개의 독립적인 기능(add, subtract, multiply, divide, error)을 동시에 검증하고 있다. 앞쪽 assert가 실패하면 뒤쪽 assert는 실행조차 되지 않아 어떤 연산이 깨졌는지 파악하기 어렵다.

```python
# 문제: 하나의 테스트가 더하기, 빼기, 곱하기, 나누기, 에러를 모두 검증
def test_calculator():
    assert shared_calc.add(2, 3) == 5
    assert shared_calc.subtract(5, 3) == 2
    assert shared_calc.multiply(3, 4) == 12
    assert shared_calc.divide(10, 2) == 5.0
    with pytest.raises(ValueError):
        shared_calc.divide(10, 0)
```

연산별로 테스트를 분리해야 한다. `test_add`, `test_subtract`, `test_multiply`, `test_divide`, `test_divide_by_zero` 각각 별도 함수로 작성한다.

---

## 2. Obscure Test (불명확한 테스트)

**위치:** `test_complex_calculation()`

중첩된 연산의 기대값 `17.0`이 어떻게 도출되는지 테스트 코드만 보고는 알 수 없다. 계산 과정에 대한 설명이 없고 변수명도 `r`로 의미가 불분명하다.

```python
def test_complex_calculation():
    c = Calculator()
    r = c.add(c.multiply(3, 4), c.subtract(10, c.divide(20, 4)))
    assert r == 17.0
```

이 테스트가 무엇을 검증하려는 것인지 의도가 드러나지 않는다. 중간 계산 결과를 의미 있는 변수명으로 분리하거나, 테스트 자체를 단위 연산 조합이 아닌 명확한 비즈니스 시나리오로 표현해야 한다.

---

## 3. Global Shared Fixture (전역 공유 상태)

**위치:** 모듈 레벨의 `shared_calc = Calculator()`

```python
shared_calc = Calculator()

def test_calculator():
    assert shared_calc.add(2, 3) == 5
```

테스트 간에 전역 인스턴스를 공유하고 있다. 현재 `Calculator`가 상태를 갖지 않아 당장 문제가 없지만, 이후 Calculator에 상태(예: 히스토리, 설정)가 추가되면 테스트 간 간섭이 발생한다. pytest fixture를 사용하여 테스트마다 독립적인 인스턴스를 생성해야 한다.

```python
# 개선 방향
@pytest.fixture
def calculator():
    return Calculator()

def test_add(calculator):
    assert calculator.add(2, 3) == 5
```

---

## 4. Assertion Roulette (단언 룰렛)

**위치:** `test_calculator()`, `test_all_operations_with_negative()`, `test_edge_cases()`

여러 assert 문이 메시지 없이 나열되어 있어, 실패 시 어떤 조건에서 실패했는지 즉시 파악하기 어렵다.

```python
def test_all_operations_with_negative():
    c = Calculator()
    assert c.add(-5, -3) == -8
    assert c.subtract(-5, -3) == -2
    assert c.multiply(-3, 4) == -12
    assert c.divide(-10, 2) == -5.0
    assert c.multiply(-3, -4) == 12
    assert c.divide(-10, -2) == 5.0
```

각 assert에 실패 메시지를 추가하거나, `@pytest.mark.parametrize`를 사용하여 각 케이스를 독립 실행되도록 해야 한다.

---

## 5. Conditional Test Logic 부재 / 불완전한 예외 검증

**위치:** `test_calculator()` 내 예외 테스트

```python
with pytest.raises(ValueError):
    shared_calc.divide(10, 0)
```

예외가 발생하는 것만 확인하고, 예외 메시지의 내용을 검증하지 않는다. 다른 이유로 `ValueError`가 발생해도 테스트가 통과한다.

```python
# 개선 방향
with pytest.raises(ValueError, match="0으로 나눌 수 없습니다"):
    shared_calc.divide(10, 0)
```

---

## 6. 미사용 Import

**위치:** 파일 상단

```python
from unittest.mock import Mock
```

`Mock`이 어디에서도 사용되지 않는다. 불필요한 import는 코드를 읽는 사람에게 "어딘가에서 Mock을 쓸 것이다"라는 잘못된 기대를 준다. 제거해야 한다.

---

## 7. 테스트 이름의 모호성

**위치:** `test_calculator()`, `test_edge_cases()`

테스트 함수 이름이 테스트 대상과 기대 동작을 표현하지 않는다. `test_calculator`는 "Calculator의 무엇을 어떻게 검증하는가"를 전혀 전달하지 않는다. `test_edge_cases`도 마찬가지로, 어떤 경계 조건을 검증하는지 이름에 드러나지 않는다.

```
# 문제 이름
test_calculator
test_edge_cases

# 개선 방향 예시
test_add_returns_sum_of_two_positive_numbers
test_multiply_handles_float_precision
test_divide_returns_float_type
```

---

## 요약

| # | Test Smell | 위치 | 심각도 |
|---|-----------|------|--------|
| 1 | Eager Test | `test_calculator`, `test_all_operations_with_negative` | 높음 |
| 2 | Obscure Test | `test_complex_calculation` | 중간 |
| 3 | Global Shared Fixture | `shared_calc` | 중간 |
| 4 | Assertion Roulette | 다수 함수 | 중간 |
| 5 | 불완전한 예외 검증 | `test_calculator` | 낮음 |
| 6 | 미사용 Import | `Mock` | 낮음 |
| 7 | 모호한 테스트 이름 | `test_calculator`, `test_edge_cases` | 중간 |
