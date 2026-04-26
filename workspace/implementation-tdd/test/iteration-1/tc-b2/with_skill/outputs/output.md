# 테스트 냄새 리뷰

## 잘된 점

- 출력 기반 테스트(Output-based)를 사용하여 순수 함수의 반환값을 검증하고 있다. 이는 Khorikov의 테스트 스타일 우선순위에서 가장 권장되는 방식이다.
- `pytest.raises`를 사용한 예외 검증이 포함되어 있다.
- `pytest.approx`를 사용하여 부동소수점 비교를 올바르게 처리하고 있다.
- Mock을 남용하지 않았다. `unittest.mock.Mock`이 import되어 있지만 실제로 사용되지 않으므로, 불필요한 import라는 점을 제외하면 Mock 과용 문제는 없다.

---

## 발견된 테스트 냄새

### 1. Erratic Test (불안정 테스트) -- 공유 가변 상태

```python
shared_calc = Calculator()

def test_calculator():
    assert shared_calc.add(2, 3) == 5
    ...
```

[테스트 격리] -- `shared_calc`는 모듈 수준의 전역 공유 상태다. 현재 `Calculator`는 내부 상태가 없는 순수 객체이므로 실질적 문제가 발생하지 않지만, 이는 **구현에 의존한 안전성**이다. `Calculator`에 상태가 추가되는 순간(예: 계산 이력, 설정값) 테스트 간 간섭이 발생한다. 각 테스트에서 독립적으로 인스턴스를 생성하거나, pytest fixture를 사용해야 한다.

---

### 2. Eager Test -- 하나의 테스트가 너무 많은 것을 검증

```python
def test_calculator():
    # 더하기
    assert shared_calc.add(2, 3) == 5
    assert shared_calc.add(-1, 1) == 0
    assert shared_calc.add(0, 0) == 0
    # 빼기
    assert shared_calc.subtract(5, 3) == 2
    assert shared_calc.subtract(0, 5) == -5
    # 곱하기
    assert shared_calc.multiply(3, 4) == 12
    assert shared_calc.multiply(0, 100) == 0
    # 나누기
    assert shared_calc.divide(10, 2) == 5.0
    assert shared_calc.divide(7, 2) == 3.5
    # 에러
    with pytest.raises(ValueError):
        shared_calc.divide(10, 0)
```

[Eager Test] -- 하나의 테스트 함수에서 `add`, `subtract`, `multiply`, `divide`, 예외 발생까지 **네 가지 서로 다른 연산과 하나의 에러 경로**를 모두 검증한다. 하나의 테스트는 하나의 행위(또는 밀접하게 관련된 행위)만 검증해야 한다.

---

### 3. Assertion Roulette -- 어떤 단언이 실패했는지 알기 어려움

```python
def test_calculator():
    assert shared_calc.add(2, 3) == 5
    assert shared_calc.add(-1, 1) == 0
    assert shared_calc.add(0, 0) == 0
    assert shared_calc.subtract(5, 3) == 2
    assert shared_calc.subtract(0, 5) == -5
    assert shared_calc.multiply(3, 4) == 12
    assert shared_calc.multiply(0, 100) == 0
    assert shared_calc.divide(10, 2) == 5.0
    assert shared_calc.divide(7, 2) == 3.5
```

[Assertion Roulette] -- `test_calculator`에 11개의 단언이 나열되어 있다. 중간의 한 단언이 실패하면 이후 단언은 실행되지 않으며, 실패 메시지만으로는 어떤 연산의 어떤 케이스가 실패했는지 즉시 파악하기 어렵다. `test_all_operations_with_negative`도 동일한 문제를 갖고 있다(6개 단언, 4가지 연산 혼합).

---

### 4. Eager Test -- 음수 테스트의 다중 관심사

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

[Eager Test] -- "음수"라는 데이터 특성을 기준으로 네 가지 서로 다른 연산을 하나의 테스트에 묶었다. 테스트는 데이터 특성이 아닌 **행위 단위**로 분리해야 한다. `test_add_negative_numbers`, `test_subtract_negative_numbers` 등으로 분리하면 실패 시 원인 파악이 즉시 가능하다.

---

### 5. Obscure Test -- 의도가 불명확한 테스트 이름과 구조

```python
def test_complex_calculation():
    c = Calculator()
    r = c.add(c.multiply(3, 4), c.subtract(10, c.divide(20, 4)))
    assert r == 17.0
```

[Obscure Test] -- 테스트 이름 `test_complex_calculation`은 무엇을 검증하는지 드러내지 않는다. 변수명 `r`은 의미가 없고, 중첩된 메서드 호출 `c.add(c.multiply(3, 4), c.subtract(10, c.divide(20, 4)))`은 한눈에 계산 의도를 파악하기 어렵다. 또한 이 테스트가 검증하는 행위가 불분명하다 -- Calculator의 개별 연산은 이미 다른 테스트에서 검증하고 있으므로, 연산의 조합이 올바르게 동작하는지를 검증하는 것이라면 그 의도를 이름과 구조로 드러내야 한다.

---

### 6. Eager Test -- 엣지 케이스 묶음

```python
def test_edge_cases():
    c = Calculator()
    assert c.add(10**18, 10**18) == 2 * 10**18       # 큰 수
    assert c.multiply(0.1, 0.2) == pytest.approx(0.02)  # 소수점
    assert isinstance(c.divide(10, 3), float)           # 타입
```

[Eager Test] -- "엣지 케이스"라는 모호한 범주로 세 가지 서로 다른 관심사(큰 수 덧셈, 부동소수점 곱셈, 반환 타입 검증)를 묶었다. 각각은 독립적인 테스트로 분리해야 한다. `test_add_large_numbers`, `test_multiply_floating_point_precision`, `test_divide_returns_float` 등으로 나누면 실패 원인이 명확해진다.

---

### 7. Hard-Coded Test Data -- 매직 넘버

```python
def test_complex_calculation():
    c = Calculator()
    r = c.add(c.multiply(3, 4), c.subtract(10, c.divide(20, 4)))
    assert r == 17.0
```

[Hard-Coded Test Data] -- `3, 4, 10, 20, 4, 17.0`이 모두 매직 넘버로 하드코딩되어 있다. 17.0이라는 기대값이 왜 정답인지 테스트 코드만 보고 알 수 없다. 명백한 데이터 패턴을 적용하여 계산 과정을 드러내야 한다. 예: `assert r == (3 * 4) + (10 - 20 / 4)`.

---

### 8. Test Code Duplication -- 반복되는 설정 코드

```python
def test_complex_calculation():
    c = Calculator()
    ...

def test_all_operations_with_negative():
    c = Calculator()
    ...

def test_edge_cases():
    c = Calculator()
    ...
```

[Test Code Duplication] -- `Calculator()` 인스턴스 생성이 세 개의 테스트에서 반복된다. pytest fixture를 사용하여 중복을 제거해야 한다.

```python
@pytest.fixture
def calc():
    return Calculator()
```

---

### 9. 불필요한 import

```python
from unittest.mock import Mock
```

`Mock`은 코드 어디에서도 사용되지 않는다. 불필요한 import는 테스트의 가독성을 저해하고, 이 테스트가 Mock 기반 검증을 할 것이라는 잘못된 기대를 만든다.

---

## 리뷰 체크리스트 검증

| 항목 | 결과 |
|------|------|
| Tests written after production code | 해당 -- 프로덕션 코드와 테스트 코드가 같은 파일에 있어 test-last로 추정 |
| No Red-Green-Refactor cycle evidence | 해당 -- `test_calculator`의 대규모 검증은 점진적 개발의 흔적이 없음 |
| Tests coupled to implementation details | 해당 없음 -- 출력 기반 테스트를 사용하여 반환값만 검증 |
| Mock overuse | 해당 없음 -- Mock 미사용 |
| Missing test isolation | **해당** -- `shared_calc` 전역 공유 상태 |
| Test smells | **해당** -- Assertion Roulette, Eager Test, Obscure Test, Hard-Coded Test Data, Test Code Duplication |
| No incremental development | 해당 -- 한 번에 모든 연산을 테스트하는 구조 |
| Communication-based testing where output-based would suffice | 해당 없음 -- 출력 기반 테스트 사용 |
| Missing boundary/edge case tests | 부분 해당 -- 일부 엣지 케이스가 있으나 음수 나눗셈의 0 제수 등은 누락 |
| Tests that don't drive design | 해당 -- 프로덕션 코드가 이미 완성된 상태에서 사후 검증하는 구조 |

---

## 요약 (심각도 순)

| 순위 | 냄새 | 심각도 | 위치 |
|------|------|--------|------|
| 1 | Eager Test | 높음 | `test_calculator`, `test_all_operations_with_negative`, `test_edge_cases` |
| 2 | Assertion Roulette | 높음 | `test_calculator`, `test_all_operations_with_negative` |
| 3 | Obscure Test | 중간 | `test_complex_calculation` |
| 4 | Erratic Test (공유 상태) | 중간 | `shared_calc` 전역 변수 |
| 5 | Hard-Coded Test Data | 중간 | `test_complex_calculation` |
| 6 | Test Code Duplication | 낮음 | `Calculator()` 생성 반복 |
| 7 | 불필요한 import | 낮음 | `from unittest.mock import Mock` |
