# PasswordChecker: Test-Last to TDD Refactoring

## Review Findings

원본 코드를 Refactoring Mode 체크리스트 기준으로 진단한다.

- [x] **Test-last code** -- 프로덕션 코드가 먼저 완성된 후 테스트가 추가됨. 테스트가 설계를 주도하지 않음.
- [x] **No Red-Green-Refactor cycle evidence** -- 모든 규칙(length, uppercase, digit, special)이 한 번에 구현됨. 점진적 발전 없음.
- [x] **Tests coupled to implementation details** -- `len(result['errors']) == 3`처럼 에러 개수를 매직 넘버로 검증하며, 규칙 변경 시 테스트가 함께 깨짐.
- [x] **Test smells: Assertion Roulette, Obscure Test** -- `test_all_rules_fail`에서 어떤 규칙이 실패했는지 불명확. `test_valid_password`/`test_custom_length` 이름이 검증 행위를 설명하지 않음.
- [x] **No incremental development** -- Big-bang 구현. 4개 규칙이 동시에 존재.
- [x] **Missing boundary/edge case tests** -- 각 규칙의 개별 실패/성공 경계, 빈 문자열, 특수문자 경계 등 미검증.
- [x] **Weak assertions** -- `len(result['errors']) == 3`은 어떤 에러인지 불명. 주석에 "4개 중 3개"라 적었으나 실제로는 4개 모두 실패해야 할 상황.

---

## Refactoring Changes

### Change 1: Test-Last to Red-Green-Refactor Steps

[Before]
```python
# 프로덕션 코드 (먼저 작성됨) -- 4개 규칙이 한 번에 구현
class PasswordChecker:
    def __init__(self, min_length=8):
        self.min_length = min_length
        self.rules = [
            self._check_length,
            self._check_uppercase,
            self._check_digit,
            self._check_special,
        ]

    def check(self, password):
        errors = []
        for rule in self.rules:
            error = rule(password)
            if error:
                errors.append(error)
        return {'valid': len(errors) == 0, 'errors': errors}
    # ... 4개 _check 메서드 전부 존재


# 테스트 코드 (나중에 작성됨)
def test_valid_password():
    checker = PasswordChecker()
    result = checker.check('Abcdef1!')
    assert result['valid'] is True
```

[After]
```python
# Step 1 Red: 가장 단순한 경우 -- 빈 비밀번호
def test_check__empty_password__returns_invalid():
    checker = PasswordChecker()
    result = checker.check('')
    assert result.is_valid is False

# Step 1 Green: 최소 구현
class PasswordChecker:
    def check(self, password):
        return ValidationResult(is_valid=False, errors=[])

# Step 2 Red: 길이 규칙만 검증
def test_check__shorter_than_min_length__reports_length_error():
    checker = PasswordChecker(min_length=8)
    result = checker.check('Ab1!')
    assert result.is_valid is False
    assert '최소 8자 이상' in result.errors

# Step 2 Green: 길이 규칙만 추가
# Step 3 Red: 대문자 규칙 ...
# (이하 규칙별로 Red-Green 반복)
```

[Reason] Red-Green-Refactor Cycle -- 테스트가 설계를 주도하려면 가장 단순한 경우(빈 문자열)부터 시작하여 규칙을 하나씩 추가해야 한다. Big-bang 구현은 테스트가 설계에 영향을 줄 기회를 제거한다.

---

### Change 2: dict Return to Value Object

[Before]
```python
return {'valid': len(errors) == 0, 'errors': errors}
```

[After]
```python
@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    errors: tuple[str, ...]
```

[Reason] Value Object (Design Patterns in TDD) -- dict 반환은 테스트에서 `result['valid']`, `result['errors']` 같은 문자열 키 접근을 강제한다. Value Object를 사용하면 타입 안전성이 높아지고, frozen=True로 불변성을 보장하며, 테스트에서 `result.is_valid`로 명확하게 접근할 수 있다.

---

### Change 3: Obscure Tests to Behavior-Describing Tests

[Before]
```python
def test_valid_password():
    checker = PasswordChecker()
    result = checker.check('Abcdef1!')
    assert result['valid'] is True

def test_all_rules_fail():
    checker = PasswordChecker()
    result = checker.check('abc')
    assert result['valid'] is False
    assert len(result['errors']) == 3  # 어떤 에러인지 불명확
```

[After]
```python
def test_check__satisfies_all_rules__returns_valid():
    checker = PasswordChecker(min_length=8)
    result = checker.check('Abcdef1!')
    assert result.is_valid is True
    assert result.errors == ()

def test_check__violates_all_rules__reports_every_error():
    checker = PasswordChecker(min_length=8)
    result = checker.check('abc')
    assert result.is_valid is False
    assert '최소 8자 이상' in result.errors
    assert '대문자 포함 필요' in result.errors
    assert '숫자 포함 필요' in result.errors
    assert '특수문자 포함 필요' in result.errors
```

[Reason] Obscure Test / Assertion Roulette Remedy (Test Smells) -- 테스트 이름이 `[대상]__[조건]__[기대행위]` 패턴을 따르고, 매직 넘버 `3` 대신 구체적 에러 메시지를 검증하여 어떤 단언이 실패했는지 즉시 파악할 수 있다.

---

### Change 4: Missing Edge Cases to Boundary Tests

[Before]
```python
# 각 규칙의 개별 경계 테스트 없음
def test_custom_length():
    checker = PasswordChecker(min_length=12)
    result = checker.check('Short1!')
    assert '최소 12자' in result['errors'][0]
```

[After]
```python
# 규칙별 독립 경계 테스트
def test_check__missing_only_uppercase__reports_only_uppercase_error():
    checker = PasswordChecker(min_length=8)
    result = checker.check('abcdefg1!')
    assert result.is_valid is False
    assert result.errors == ('대문자 포함 필요',)

def test_check__missing_only_digit__reports_only_digit_error():
    checker = PasswordChecker(min_length=8)
    result = checker.check('Abcdefgh!')
    assert result.is_valid is False
    assert result.errors == ('숫자 포함 필요',)

def test_check__missing_only_special__reports_only_special_error():
    checker = PasswordChecker(min_length=8)
    result = checker.check('Abcdefg1')
    assert result.is_valid is False
    assert result.errors == ('특수문자 포함 필요',)

def test_check__exact_min_length__passes_length_rule():
    checker = PasswordChecker(min_length=8)
    result = checker.check('Abcdef1!')
    assert '최소 8자 이상' not in result.errors

def test_check__custom_min_length__reports_custom_message():
    checker = PasswordChecker(min_length=12)
    result = checker.check('Short1!A')
    assert result.is_valid is False
    assert '최소 12자 이상' in result.errors
```

[Reason] Missing Boundary Tests (Red Bar Patterns: Test List) -- 원본은 각 규칙을 개별적으로 검증하는 테스트가 없다. 규칙별 단일 실패 테스트와 정확히 경계값에서의 통과 테스트를 추가하여 회귀 방지 능력을 높인다.

---

### Change 5: Weak Assertions to Strong Assertions

[Before]
```python
assert len(result['errors']) == 3  # 주석: "4개 중 3개" -- 실제로 4개 모두 실패
assert '최소 12자' in result['errors'][0]  # 인덱스 의존
```

[After]
```python
assert result.errors == ('최소 8자 이상', '대문자 포함 필요', '숫자 포함 필요', '특수문자 포함 필요')
# 또는 순서 무관하게:
assert '최소 12자 이상' in result.errors  # 인덱스 아닌 멤버십 검사
```

[Reason] Weak Assertions / Fragile Test Remedy -- 인덱스 기반 접근(`errors[0]`)은 규칙 순서 변경 시 깨진다. 전체 목록 비교 또는 멤버십 검사를 사용하여 리팩토링 내성을 높인다.

---

### Change 6: Implementation-Coupled Rules to Strategy Pattern

[Before]
```python
self.rules = [
    self._check_length,
    self._check_uppercase,
    self._check_digit,
    self._check_special,
]
```

[After]
```python
from typing import Protocol

class PasswordRule(Protocol):
    def validate(self, password: str) -> str | None: ...

class MinLengthRule:
    def __init__(self, min_length: int = 8):
        self._min_length = min_length

    def validate(self, password: str) -> str | None:
        if len(password) < self._min_length:
            return f'최소 {self._min_length}자 이상'
        return None
```

[Reason] Extract Interface (Refactoring Patterns) + Open-Closed Principle -- 규칙을 Protocol 기반 독립 객체로 분리하면, 새 규칙 추가 시 PasswordChecker를 수정하지 않고 규칙만 추가하면 된다. 각 규칙을 독립적으로 TDD할 수 있다.

---

## Complete Refactored Code

### TDD Red-Green-Refactor Progression

아래는 TDD로 이 코드를 처음부터 개발했을 때의 단계별 진행을 보여준다.

**Test List (시작 전 작성):**
```
[ ] 빈 비밀번호는 invalid
[ ] 최소 길이 미만이면 길이 에러
[ ] 정확히 최소 길이이면 길이 규칙 통과
[ ] 커스텀 최소 길이 지원
[ ] 대문자 없으면 대문자 에러
[ ] 숫자 없으면 숫자 에러
[ ] 특수문자 없으면 특수문자 에러
[ ] 모든 규칙 충족 시 valid
[ ] 여러 규칙 동시 위반 시 모든 에러 수집
```

---

#### Step 1: 빈 비밀번호 (Simplest Case)

```python
# RED: 가장 단순한 경우부터 시작
def test_check__empty_password__returns_invalid():
    checker = PasswordChecker()
    result = checker.check('')
    assert result.is_valid is False
```

```python
# GREEN: Fake It -- 항상 invalid 반환
from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    errors: tuple[str, ...]


class PasswordChecker:
    def check(self, password: str) -> ValidationResult:
        return ValidationResult(is_valid=False, errors=())
```

---

#### Step 2: 길이 규칙 도입

```python
# RED: 길이 규칙 실패 검증
def test_check__shorter_than_min_length__reports_length_error():
    checker = PasswordChecker(min_length=8)
    result = checker.check('Ab1!')
    assert result.is_valid is False
    assert '최소 8자 이상' in result.errors
```

```python
# GREEN: 길이 규칙 구현
class MinLengthRule:
    def __init__(self, min_length: int = 8):
        self._min_length = min_length

    def validate(self, password: str) -> str | None:
        if len(password) < self._min_length:
            return f'최소 {self._min_length}자 이상'
        return None


class PasswordChecker:
    def __init__(self, min_length: int = 8):
        self._rules = [MinLengthRule(min_length)]

    def check(self, password: str) -> ValidationResult:
        errors = tuple(
            error for rule in self._rules
            if (error := rule.validate(password)) is not None
        )
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
```

```python
# RED: 길이 경계값
def test_check__exact_min_length__passes_length_rule():
    checker = PasswordChecker(min_length=4)
    result = checker.check('Ab1!')
    assert '최소 4자 이상' not in result.errors
```

```python
# GREEN: 이미 통과 (len('Ab1!') == 4, min_length == 4 이므로 < 조건 미충족)
```

```python
# RED: 커스텀 길이
def test_check__custom_min_length__reports_custom_message():
    checker = PasswordChecker(min_length=12)
    result = checker.check('Short1!A')
    assert result.is_valid is False
    assert '최소 12자 이상' in result.errors
```

```python
# GREEN: 이미 통과 (MinLengthRule이 min_length를 매개변수로 받으므로)
```

---

#### Step 3: 대문자 규칙 추가

```python
# RED: 대문자 없으면 에러
def test_check__missing_only_uppercase__reports_only_uppercase_error():
    checker = PasswordChecker(min_length=8)
    result = checker.check('abcdefg1!')
    assert result.is_valid is False
    assert result.errors == ('대문자 포함 필요',)
```

```python
# GREEN: 대문자 규칙 구현
class UppercaseRule:
    def validate(self, password: str) -> str | None:
        if not any(c.isupper() for c in password):
            return '대문자 포함 필요'
        return None


class PasswordChecker:
    def __init__(self, min_length: int = 8):
        self._rules = [MinLengthRule(min_length), UppercaseRule()]
    # check 메서드는 변경 없음
```

---

#### Step 4: 숫자 규칙 추가

```python
# RED
def test_check__missing_only_digit__reports_only_digit_error():
    checker = PasswordChecker(min_length=8)
    result = checker.check('Abcdefgh!')
    assert result.is_valid is False
    assert result.errors == ('숫자 포함 필요',)
```

```python
# GREEN
class DigitRule:
    def validate(self, password: str) -> str | None:
        if not any(c.isdigit() for c in password):
            return '숫자 포함 필요'
        return None
```

---

#### Step 5: 특수문자 규칙 추가

```python
# RED
def test_check__missing_only_special__reports_only_special_error():
    checker = PasswordChecker(min_length=8)
    result = checker.check('Abcdefg1')
    assert result.is_valid is False
    assert result.errors == ('특수문자 포함 필요',)
```

```python
# GREEN
class SpecialCharRule:
    def __init__(self, chars: str = '!@#$%'):
        self._chars = chars

    def validate(self, password: str) -> str | None:
        if not any(c in self._chars for c in password):
            return '특수문자 포함 필요'
        return None
```

---

#### Step 6: 모든 규칙 충족 + 전체 실패

```python
# RED: 모든 규칙 충족
def test_check__satisfies_all_rules__returns_valid():
    checker = PasswordChecker(min_length=8)
    result = checker.check('Abcdef1!')
    assert result.is_valid is True
    assert result.errors == ()
```

```python
# GREEN: 이미 통과
```

```python
# RED: 모든 규칙 위반
def test_check__violates_all_rules__reports_every_error():
    checker = PasswordChecker(min_length=8)
    result = checker.check('abc')
    assert result.is_valid is False
    assert '최소 8자 이상' in result.errors
    assert '대문자 포함 필요' in result.errors
    assert '숫자 포함 필요' in result.errors
    assert '특수문자 포함 필요' in result.errors
```

```python
# GREEN: 이미 통과
```

---

### Final Code: Production

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    errors: tuple[str, ...]


class PasswordRule(Protocol):
    def validate(self, password: str) -> str | None: ...


class MinLengthRule:
    def __init__(self, min_length: int = 8):
        self._min_length = min_length

    def validate(self, password: str) -> str | None:
        if len(password) < self._min_length:
            return f'최소 {self._min_length}자 이상'
        return None


class UppercaseRule:
    def validate(self, password: str) -> str | None:
        if not any(c.isupper() for c in password):
            return '대문자 포함 필요'
        return None


class DigitRule:
    def validate(self, password: str) -> str | None:
        if not any(c.isdigit() for c in password):
            return '숫자 포함 필요'
        return None


class SpecialCharRule:
    def __init__(self, chars: str = '!@#$%'):
        self._chars = chars

    def validate(self, password: str) -> str | None:
        if not any(c in self._chars for c in password):
            return '특수문자 포함 필요'
        return None


class PasswordChecker:
    def __init__(self, min_length: int = 8):
        self._rules: list[PasswordRule] = [
            MinLengthRule(min_length),
            UppercaseRule(),
            DigitRule(),
            SpecialCharRule(),
        ]

    def check(self, password: str) -> ValidationResult:
        errors = tuple(
            error for rule in self._rules
            if (error := rule.validate(password)) is not None
        )
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
```

### Final Code: Tests

```python
import pytest

from password_checker import PasswordChecker


class TestPasswordChecker:

    # --- Step 1: Simplest case ---

    def test_check__empty_password__returns_invalid(self):
        checker = PasswordChecker()
        result = checker.check('')
        assert result.is_valid is False

    # --- Step 2: Length rule ---

    def test_check__shorter_than_min_length__reports_length_error(self):
        checker = PasswordChecker(min_length=8)
        result = checker.check('Ab1!')
        assert result.is_valid is False
        assert '최소 8자 이상' in result.errors

    def test_check__exact_min_length__passes_length_rule(self):
        checker = PasswordChecker(min_length=4)
        result = checker.check('Ab1!')
        assert '최소 4자 이상' not in result.errors

    def test_check__custom_min_length__reports_custom_message(self):
        checker = PasswordChecker(min_length=12)
        result = checker.check('Short1!A')
        assert result.is_valid is False
        assert '최소 12자 이상' in result.errors

    # --- Step 3: Uppercase rule ---

    def test_check__missing_only_uppercase__reports_only_uppercase_error(self):
        checker = PasswordChecker(min_length=8)
        result = checker.check('abcdefg1!')
        assert result.is_valid is False
        assert result.errors == ('대문자 포함 필요',)

    # --- Step 4: Digit rule ---

    def test_check__missing_only_digit__reports_only_digit_error(self):
        checker = PasswordChecker(min_length=8)
        result = checker.check('Abcdefgh!')
        assert result.is_valid is False
        assert result.errors == ('숫자 포함 필요',)

    # --- Step 5: Special char rule ---

    def test_check__missing_only_special__reports_only_special_error(self):
        checker = PasswordChecker(min_length=8)
        result = checker.check('Abcdefg1')
        assert result.is_valid is False
        assert result.errors == ('특수문자 포함 필요',)

    # --- Step 6: All rules ---

    def test_check__satisfies_all_rules__returns_valid(self):
        checker = PasswordChecker(min_length=8)
        result = checker.check('Abcdef1!')
        assert result.is_valid is True
        assert result.errors == ()

    def test_check__violates_all_rules__reports_every_error(self):
        checker = PasswordChecker(min_length=8)
        result = checker.check('abc')
        assert result.is_valid is False
        assert '최소 8자 이상' in result.errors
        assert '대문자 포함 필요' in result.errors
        assert '숫자 포함 필요' in result.errors
        assert '특수문자 포함 필요' in result.errors
```

## Summary of TDD Principles Applied

| Principle | Application |
|-----------|-------------|
| Red-Green-Refactor | 6단계에 걸쳐 규칙을 하나씩 추가. 매 단계마다 실패 테스트 작성 후 통과. |
| Start Test (Red Bar) | 빈 비밀번호(가장 단순한 경우)부터 시작. |
| One Step Test (Red Bar) | 규칙 하나씩 추가하여 점진적 발전. |
| Fake It (Green Bar) | Step 1에서 항상 invalid를 반환하는 것으로 시작. |
| Obvious Implementation (Green Bar) | Step 2 이후 규칙 구현이 명백하므로 바로 구현. |
| Value Object (Design Patterns) | dict 반환을 frozen dataclass로 교체. |
| Extract Interface (Refactoring) | PasswordRule Protocol로 규칙을 독립 객체화. |
| AAA Pattern (Testing Patterns) | 모든 테스트가 Arrange-Act-Assert 구조. |
| Test Naming (Testing Patterns) | `[대상]__[조건]__[기대행위]` 패턴 적용. |
| Output-Based Testing (Four Pillars) | 반환된 ValidationResult의 값만 검증. Mock 없음. |
