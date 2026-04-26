# TDD 관점 테스트 코드 리뷰

## 총평

Kent Beck의 Money 예제를 기반으로 한 테스트로, TDD의 기본 원칙을 잘 따르고 있다. 테스트 클래스 분류가 명확하고, 각 테스트가 하나의 행위에 집중하며, 테스트 이름이 의도를 잘 드러낸다. 다만 TDD 사이클(Red-Green-Refactor)의 완성도를 높이려면 몇 가지 보완이 필요하다.

---

## 잘된 점

### 1. 테스트 구조화가 명확하다
- `TestMoneyCreation`, `TestMoneyAddition`, `TestMoneyMultiplication`으로 행위 단위 분류가 적절하다.
- 각 테스트가 단일 책임을 가진다.

### 2. 테스트 이름이 행위를 설명한다
- `test_adds_same_currency`, `test_rejects_different_currency` 등 "무엇을 하는가"가 이름에 드러난다.

### 3. 불변성 검증이 포함되어 있다
- `test_is_immutable`, `test_addition_returns_new_instance`, `test_multiplication_returns_new_instance`로 Value Object의 핵심 속성인 불변성을 검증한다.

### 4. 경계 조건 테스트가 존재한다
- `test_multiplies_by_zero`로 0 곱셈 경계 케이스를 다루고 있다.

---

## 개선이 필요한 점

### 1. 프로덕션 코드와 테스트 코드가 같은 파일에 있다

TDD에서 테스트는 프로덕션 코드와 분리되어야 한다. 같은 파일에 있으면 Red 단계에서 "테스트 먼저 작성하고, 컴파일/임포트 실패를 확인"하는 흐름이 성립하지 않는다.

```python
# money.py (프로덕션 코드)
@dataclass(frozen=True)
class Money:
    ...

# test_money.py (테스트 코드)
from money import Money
```

### 2. Value Object의 동등성(equality) 테스트가 빠져 있다

`dataclass`가 `__eq__`를 자동 생성하므로 모든 `assert result == Money(...)` 비교가 동작하지만, **동등성 자체를 검증하는 테스트가 없다**. TDD에서는 암묵적 의존을 명시적으로 테스트해야 한다. Kent Beck의 원서에서도 동등성 테스트를 별도로 작성한다.

```python
class TestMoneyEquality:
    def test_equal_money_objects_are_equal(self):
        assert Money(1000, 'KRW') == Money(1000, 'KRW')

    def test_different_amount_is_not_equal(self):
        assert Money(1000, 'KRW') != Money(2000, 'KRW')

    def test_different_currency_is_not_equal(self):
        assert Money(1000, 'KRW') != Money(1000, 'USD')
```

이 테스트가 없으면, `dataclass`의 `eq=True` 기본값에 전적으로 의존하는 셈이다. 추후 `__eq__`를 커스터마이징하거나 `dataclass` 대신 일반 클래스로 변경할 때 회귀 테스트가 부재한다.

### 3. 음수 금액에 대한 테스트가 없다

현재 `amount`가 `int` 타입이므로 음수가 허용된다. 도메인 관점에서 음수 금액이 유효한지 결정하고, 그에 맞는 테스트가 필요하다.

```python
# 음수를 허용하는 경우
def test_allows_negative_amount(self):
    assert Money(-500, 'KRW').amount == -500

# 음수를 거부하는 경우
def test_rejects_negative_amount(self):
    with pytest.raises(ValueError):
        Money(-500, 'KRW')
```

어느 쪽이든 명시적 테스트로 도메인 규칙을 문서화해야 한다.

### 4. `times`에 음수 승수 테스트가 없다

`times(0)` 경계 케이스는 있지만, `times(-1)` 같은 음수 승수에 대한 결정이 빠져 있다. 0은 테스트했으면서 음수를 빠뜨린 것은 경계값 분석이 불완전하다는 뜻이다.

### 5. `plus`의 항등원 테스트가 없다

덧셈의 기본 속성(0을 더해도 변하지 않음)을 검증하는 테스트가 빠져 있다.

```python
def test_adding_zero_returns_same_value(self):
    result = Money(1000, 'KRW').plus(Money(0, 'KRW'))
    assert result == Money(1000, 'KRW')
```

### 6. 에러 메시지 검증이 구현 결합도를 높인다

```python
with pytest.raises(ValueError, match='통화 불일치'):
```

`match='통화 불일치'`는 에러 메시지 문구에 테스트가 결합된다. 메시지를 수정하면 테스트가 깨진다. TDD에서 테스트는 **행위**에 결합해야지, 메시지 문구에 결합하면 안 된다. `ValueError`가 발생한다는 사실만 검증하는 것이 더 적절하다.

```python
def test_rejects_different_currency(self):
    with pytest.raises(ValueError):
        Money(1000, 'KRW').plus(Money(10, 'USD'))
```

### 7. Triangulation이 부족하다

TDD에서 삼각측량(triangulation)은 하나의 행위를 여러 데이터로 검증하여 구현의 일반성을 보장하는 기법이다. 현재 대부분의 테스트가 `KRW` 단일 통화, 특정 금액에만 의존한다.

```python
# 다른 통화로도 검증
def test_adds_same_currency_usd(self):
    result = Money(10, 'USD').plus(Money(20, 'USD'))
    assert result == Money(30, 'USD')
```

또는 `@pytest.mark.parametrize`를 활용할 수 있다.

```python
@pytest.mark.parametrize("a, b, expected", [
    (Money(1000, 'KRW'), Money(2000, 'KRW'), Money(3000, 'KRW')),
    (Money(10, 'USD'), Money(20, 'USD'), Money(30, 'USD')),
])
def test_adds_same_currency(self, a, b, expected):
    assert a.plus(b) == expected
```

---

## 요약

| 항목 | 상태 |
|------|------|
| 테스트 클래스 구조 | 양호 |
| 테스트 이름 | 양호 |
| 불변성 검증 | 양호 |
| 경계값 (0 곱셈) | 양호 |
| 프로덕션/테스트 분리 | 미흡 |
| 동등성 명시적 테스트 | 누락 |
| 음수 금액/승수 경계값 | 누락 |
| 항등원 테스트 | 누락 |
| 에러 메시지 결합도 | 개선 필요 |
| 삼각측량 | 부족 |

핵심 메시지: 기본 구조는 탄탄하지만, **Value Object의 동등성 테스트 누락**과 **경계값 분석 불완전**이 가장 큰 보완 포인트다. TDD는 "실패하는 테스트를 먼저 작성"하는 것 외에도, 테스트가 도메인 규칙을 빠짐없이 문서화하는 역할을 해야 한다.
