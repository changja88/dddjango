# Test Code Review

## What the tests do right

- AAA 구조를 따르고 있다. 각 테스트는 하나의 Act과 하나의 Assert로 구성되어 명확하다.
- 테스트 간 공유 상태가 없다. 모든 테스트가 독립적이며 어떤 순서로 실행해도 결과가 동일하다.
- Mock을 전혀 사용하지 않는다. 순수 함수에 대해 실제 객체로 테스트하는 것이 올바른 접근이다.
- 예외 테스트에서 `pytest.raises`를 사용하여 자가 검증(Self-Validating) 원칙을 준수한다.

## Findings

### 1. Missing parametrize for repetitive test cases

[Missing parametrize] -- `validate_email`에 대해 구조가 동일한 테스트 5개가 개별 함수로 나열되어 있다. 데이터만 다르고 패턴이 동일한 테스트는 `@pytest.mark.parametrize`로 통합해야 유지보수가 쉽고, 새 케이스 추가 시 한 줄만 추가하면 된다.

```python
# 현재: 5개의 개별 함수
def test_valid_email():
    assert validate_email('user@example.com') is True

def test_invalid_email_no_at():
    assert validate_email('userexample.com') is False

# ... 반복 ...
```

```python
# 개선: parametrize로 통합
@pytest.mark.parametrize("email, expected", [
    ('user@example.com', True),
    ('userexample.com', False),
    ('user@', False),
    ('', False),
    (None, False),
])
def test_validate_email(email, expected):
    assert validate_email(email) == expected
```

### 2. Boundary conditions not tested -- mutation testing would expose surviving mutants

[Mutation Testing / Boundary] -- `calculate_shipping`의 경계값 테스트가 빠져 있다. 현재 테스트는 "내부" 값(weight=2.0, distance=150)만 사용한다. mutmut이 `distance // 100`을 `distance // 101`로 바꾸거나, `weight * 500`을 `weight * 499`로 바꿔도 현재 테스트로는 감지할 수 없다. 특히 다음 경계가 누락되었다:

- **distance 100 경계**: `distance=99`(distance_fee=0)와 `distance=100`(distance_fee=1000)의 차이를 검증하지 않음
- **최대 배송비 캡(50000) 경계**: `total > 50000` 조건의 경계인 49999, 50000, 50001 근처 값을 테스트하지 않음. mutmut이 `>` 를 `>=`로 바꾸면 감지 불가
- **express 1.5배 적용 후 캡에 걸리는 케이스**: express=True일 때 캡이 적용되는 조합을 테스트하지 않음

### 3. Missing edge cases for `validate_email`

[Dodger / 회피자] -- 커버리지는 높지만, `validate_email`의 핵심 분기를 실제로 검증하는 케이스가 빠져 있다. 다음이 누락되었다:

- `domain.startswith('.')` 분기: `'user@.example.com'` 같은 입력
- `domain.endswith('.')` 분기: `'user@example.'` 같은 입력
- 복수 `@` 기호: `'user@@example.com'`, `'user@ex@ample.com'`
- 도메인에 `.`이 없는 케이스: `'user@localhost'`

이 분기들은 프로덕션 코드에 조건문이 존재하지만 한 번도 실행되지 않는다. 라인 커버리지 도구에서는 해당 분기가 "covered"로 표시될 수 있으나, **branch coverage**를 켜면 미실행 분기가 드러난다.

### 4. Exception message not verified

[Weak assertion / The Liar 경향] -- `test_shipping_zero_weight`와 `test_shipping_negative_distance`에서 `pytest.raises(ValueError)`만 사용하고, 예외 메시지를 검증하지 않는다. 다른 이유로 `ValueError`가 발생해도 테스트가 통과하게 된다.

```python
# 현재
with pytest.raises(ValueError):
    calculate_shipping(0, 100)

# 개선: match로 메시지 검증
with pytest.raises(ValueError, match="무게는 0보다 커야 합니다"):
    calculate_shipping(0, 100)
```

### 5. Missing test for negative weight

[Dodger / 회피자] -- `weight <= 0` 조건에 대해 `weight=0`만 테스트하고 `weight=-1.0` 같은 음수 무게는 테스트하지 않는다. 마찬가지로 `distance=0`에 대한 테스트도 없다. `<=` 연산자를 `==`로 바꾸는 뮤턴트가 생존한다.

### 6. Return value precision not tested

[The Liar 경향] -- `calculate_shipping`이 `round(total, 2)`를 반환하지만, 소수점이 발생하는 입력을 테스트하지 않는다. 현재 테스트는 모두 정수 결과(5000, 7500)만 검증하므로, `round` 호출을 제거해도 테스트가 통과한다. 예: `weight=1.5`처럼 소수 결과가 나오는 케이스가 필요하다.

### 7. No property-based testing on pure validation function

[Missing Hypothesis] -- `validate_email`은 순수 함수이므로 property-based testing의 적합한 대상이다. Hypothesis의 `st.emails()` 전략으로 유효한 이메일을 자동 생성하여 True를 반환하는지, `st.text()`로 임의 문자열을 생성하여 크래시가 발생하지 않는지 검증할 수 있다. 이 방식은 수동으로 생각하지 못한 엣지 케이스를 자동으로 발견한다.

## Review checklist verification

| 항목 | 결과 |
|------|------|
| 여러 Act 섹션이 있는 테스트 | 해당 없음 -- 모든 테스트가 단일 Act |
| 테스트 간 공유 가변 상태 | 해당 없음 -- 공유 상태 없음 |
| Mock 과용 | 해당 없음 -- Mock 미사용 |
| Mock에 spec/autospec 누락 | 해당 없음 -- Mock 미사용 |
| 시간/순서/외부 서비스 의존 Flaky 테스트 | 해당 없음 |
| 반복 테스트에 parametrize 누락 | **해당** -- Finding #1 |
| 의도를 가리는 과도한 setup | 해당 없음 -- setup이 간결함 |
| 구현 세부사항 검증 (The Inspector) | 해당 없음 |
| 의미 없는 assertion (The Liar / Secret Catcher) | **부분 해당** -- Finding #4, #6 |
| 잘못된 테스트 레벨 | 해당 없음 |

## Summary

커버리지가 높은데 부족하게 느껴지는 이유는 명확하다: **라인 커버리지는 높지만 경계값 커버리지와 분기 커버리지가 낮다.** 현재 테스트는 "정상 경로"와 "명백한 에러"만 검증하고, 코드의 조건 분기가 실제로 갈라지는 경계 지점을 테스트하지 않는다. mutmut으로 mutation testing을 돌리면 다수의 mutant가 생존할 것이다. 핵심 개선 방향은 세 가지다:

1. **경계값 테스트 추가** -- 조건문의 `>`, `<=`, `//` 연산자가 변형되면 감지할 수 있도록 경계값(boundary)과 경계값+1 케이스를 포함
2. **parametrize로 데이터 케이스 확장** -- 반복 구조를 통합하고 누락된 분기(`.startswith('.')`, `.endswith('.')` 등)를 추가
3. **예외 메시지 검증 강화** -- `pytest.raises`에 `match` 파라미터를 사용하여 올바른 이유로 예외가 발생하는지 확인
