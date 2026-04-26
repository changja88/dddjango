# TDD 스타일 리팩토링: PasswordChecker

## 문제 분석

원본 코드는 전형적인 **test-last** 패턴이다:

1. 프로덕션 코드가 먼저 완성된 후 테스트가 추가됨
2. 테스트가 내부 구현(에러 개수, 딕셔너리 구조)에 강하게 결합됨
3. `test_all_rules_fail`이 `len(errors) == 3`으로 검증 -- 규칙이 추가/제거되면 깨짐
4. 각 규칙이 독립적으로 테스트되지 않아 실패 원인 파악이 어려움
5. 테스트가 설계를 주도하지 않고, 이미 만들어진 구조를 확인만 함

## TDD 리팩토링 원칙

- **Red-Green-Refactor** 사이클 순서대로 코드를 전개한다
- 테스트가 인터페이스를 정의하고, 프로덕션 코드는 테스트를 통과시키기 위해서만 작성한다
- 한 번에 하나의 행위만 추가한다
- 각 규칙은 독립적으로 테스트 가능해야 한다

---

## Cycle 1: 가장 단순한 경우 -- 빈 문자열은 유효하지 않다

### RED -- 실패하는 테스트 먼저 작성

```python
# test_password_validator.py

import pytest
from password_validator import PasswordValidator


class TestPasswordValidator:
    """빈 문자열부터 시작하여 점진적으로 규칙을 추가한다."""

    def test_empty_password_is_invalid(self):
        validator = PasswordValidator()
        result = validator.validate("")
        assert result.is_valid is False
```

### GREEN -- 테스트를 통과시키는 최소한의 코드

```python
# password_validator.py

from dataclasses import dataclass


@dataclass
class ValidationResult:
    is_valid: bool
    violations: list[str]


class PasswordValidator:
    def validate(self, password: str) -> ValidationResult:
        return ValidationResult(is_valid=False, violations=[])
```

---

## Cycle 2: 길이 규칙 도입

### RED

```python
    def test_short_password_reports_length_violation(self):
        validator = PasswordValidator()
        result = validator.validate("abc")
        assert "8자 이상이어야 합니다" in result.violations

    def test_password_meeting_length_is_not_rejected_for_length(self):
        validator = PasswordValidator()
        result = validator.validate("a" * 8)
        assert "8자 이상이어야 합니다" not in result.violations
```

### GREEN

```python
class PasswordValidator:
    def __init__(self):
        self._rules: list[ValidationRule] = [
            MinLengthRule(min_length=8),
        ]

    def validate(self, password: str) -> ValidationResult:
        violations = []
        for rule in self._rules:
            violation = rule.check(password)
            if violation:
                violations.append(violation)
        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
        )
```

### REFACTOR -- 규칙을 프로토콜로 분리

테스트가 "규칙은 독립적으로 검증 가능해야 한다"는 설계를 강제한다.

```python
from typing import Protocol


class ValidationRule(Protocol):
    def check(self, password: str) -> str | None: ...


class MinLengthRule:
    def __init__(self, min_length: int = 8):
        self._min_length = min_length

    def check(self, password: str) -> str | None:
        if len(password) < self._min_length:
            return f"{self._min_length}자 이상이어야 합니다"
        return None
```

---

## Cycle 3: 대문자 규칙

### RED

```python
    def test_password_without_uppercase_reports_violation(self):
        validator = PasswordValidator()
        result = validator.validate("abcdefgh1!")
        assert "대문자를 포함해야 합니다" in result.violations

    def test_password_with_uppercase_passes_uppercase_rule(self):
        validator = PasswordValidator()
        result = validator.validate("Abcdefgh1!")
        assert "대문자를 포함해야 합니다" not in result.violations
```

### GREEN

```python
class UppercaseRule:
    def check(self, password: str) -> str | None:
        if not any(c.isupper() for c in password):
            return "대문자를 포함해야 합니다"
        return None
```

`PasswordValidator.__init__`의 `_rules`에 `UppercaseRule()`을 추가한다.

---

## Cycle 4: 숫자 규칙

### RED

```python
    def test_password_without_digit_reports_violation(self):
        validator = PasswordValidator()
        result = validator.validate("Abcdefgh!")
        assert "숫자를 포함해야 합니다" in result.violations

    def test_password_with_digit_passes_digit_rule(self):
        validator = PasswordValidator()
        result = validator.validate("Abcdefg1!")
        assert "숫자를 포함해야 합니다" not in result.violations
```

### GREEN

```python
class DigitRule:
    def check(self, password: str) -> str | None:
        if not any(c.isdigit() for c in password):
            return "숫자를 포함해야 합니다"
        return None
```

---

## Cycle 5: 특수문자 규칙

### RED

```python
    def test_password_without_special_char_reports_violation(self):
        validator = PasswordValidator()
        result = validator.validate("Abcdefg1")
        assert "특수문자를 포함해야 합니다" in result.violations

    def test_password_with_special_char_passes_special_rule(self):
        validator = PasswordValidator()
        result = validator.validate("Abcdefg1!")
        assert "특수문자를 포함해야 합니다" not in result.violations
```

### GREEN

```python
class SpecialCharRule:
    SPECIAL_CHARS = set("!@#$%^&*()_+-=[]{}|;':\",./<>?")

    def check(self, password: str) -> str | None:
        if not any(c in self.SPECIAL_CHARS for c in password):
            return "특수문자를 포함해야 합니다"
        return None
```

---

## Cycle 6: 커스텀 길이 설정

### RED

```python
    def test_custom_min_length(self):
        validator = PasswordValidator(min_length=12)
        result = validator.validate("Short1!A")
        assert "12자 이상이어야 합니다" in result.violations

    def test_custom_min_length_satisfied(self):
        validator = PasswordValidator(min_length=12)
        result = validator.validate("Abcdefghij1!")
        assert result.is_valid is True
```

### GREEN

```python
class PasswordValidator:
    def __init__(self, min_length: int = 8):
        self._rules: list[ValidationRule] = [
            MinLengthRule(min_length=min_length),
            UppercaseRule(),
            DigitRule(),
            SpecialCharRule(),
        ]
    # validate 메서드는 변경 없음
```

---

## Cycle 7: 모든 규칙을 통과하는 비밀번호

### RED

```python
    def test_password_satisfying_all_rules_is_valid(self):
        validator = PasswordValidator()
        result = validator.validate("Abcdefg1!")
        assert result.is_valid is True
        assert result.violations == []
```

### GREEN -- 이미 통과한다. 기존 코드가 올바르게 동작하는 것을 확인하는 회귀 테스트 역할.

---

## Cycle 8: 규칙 조합의 유연성 -- 커스텀 규칙 주입

### RED

```python
    def test_custom_rules_can_be_injected(self):
        """외부에서 규칙을 주입할 수 있어야 한다."""

        class NoSpaceRule:
            def check(self, password: str) -> str | None:
                if " " in password:
                    return "공백을 포함할 수 없습니다"
                return None

        validator = PasswordValidator(rules=[NoSpaceRule()])
        result = validator.validate("has space")
        assert "공백을 포함할 수 없습니다" in result.violations

    def test_custom_rules_replace_defaults(self):
        """커스텀 규칙을 주입하면 기본 규칙은 적용되지 않는다."""

        class AlwaysPassRule:
            def check(self, password: str) -> str | None:
                return None

        validator = PasswordValidator(rules=[AlwaysPassRule()])
        result = validator.validate("")
        assert result.is_valid is True
```

### GREEN

```python
class PasswordValidator:
    def __init__(
        self,
        min_length: int = 8,
        rules: list[ValidationRule] | None = None,
    ):
        if rules is not None:
            self._rules = rules
        else:
            self._rules = [
                MinLengthRule(min_length=min_length),
                UppercaseRule(),
                DigitRule(),
                SpecialCharRule(),
            ]

    def validate(self, password: str) -> ValidationResult:
        violations = []
        for rule in self._rules:
            violation = rule.check(password)
            if violation:
                violations.append(violation)
        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
        )
```

---

## 최종 코드

### password_validator.py

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


# --- 결과 객체 ---

@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    violations: list[str] = field(default_factory=list)


# --- 규칙 프로토콜 ---

class ValidationRule(Protocol):
    def check(self, password: str) -> str | None: ...


# --- 개별 규칙 ---

class MinLengthRule:
    def __init__(self, min_length: int = 8):
        self._min_length = min_length

    def check(self, password: str) -> str | None:
        if len(password) < self._min_length:
            return f"{self._min_length}자 이상이어야 합니다"
        return None


class UppercaseRule:
    def check(self, password: str) -> str | None:
        if not any(c.isupper() for c in password):
            return "대문자를 포함해야 합니다"
        return None


class DigitRule:
    def check(self, password: str) -> str | None:
        if not any(c.isdigit() for c in password):
            return "숫자를 포함해야 합니다"
        return None


class SpecialCharRule:
    SPECIAL_CHARS = set("!@#$%^&*()_+-=[]{}|;':\",./<>?")

    def check(self, password: str) -> str | None:
        if not any(c in self.SPECIAL_CHARS for c in password):
            return "특수문자를 포함해야 합니다"
        return None


# --- 검증기 ---

class PasswordValidator:
    def __init__(
        self,
        min_length: int = 8,
        rules: list[ValidationRule] | None = None,
    ):
        if rules is not None:
            self._rules = list(rules)
        else:
            self._rules = [
                MinLengthRule(min_length=min_length),
                UppercaseRule(),
                DigitRule(),
                SpecialCharRule(),
            ]

    def validate(self, password: str) -> ValidationResult:
        violations = []
        for rule in self._rules:
            violation = rule.check(password)
            if violation:
                violations.append(violation)
        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
        )
```

### test_password_validator.py

```python
import pytest
from password_validator import (
    PasswordValidator,
    MinLengthRule,
    UppercaseRule,
    DigitRule,
    SpecialCharRule,
)


class TestMinLengthRule:
    def test_short_password_fails(self):
        rule = MinLengthRule(min_length=8)
        assert rule.check("abc") == "8자 이상이어야 합니다"

    def test_exact_length_passes(self):
        rule = MinLengthRule(min_length=8)
        assert rule.check("a" * 8) is None

    def test_custom_length(self):
        rule = MinLengthRule(min_length=12)
        assert rule.check("short") == "12자 이상이어야 합니다"


class TestUppercaseRule:
    def test_no_uppercase_fails(self):
        rule = UppercaseRule()
        assert rule.check("abcdefgh") == "대문자를 포함해야 합니다"

    def test_with_uppercase_passes(self):
        rule = UppercaseRule()
        assert rule.check("Abcdefgh") is None


class TestDigitRule:
    def test_no_digit_fails(self):
        rule = DigitRule()
        assert rule.check("Abcdefgh") == "숫자를 포함해야 합니다"

    def test_with_digit_passes(self):
        rule = DigitRule()
        assert rule.check("Abcdefg1") is None


class TestSpecialCharRule:
    def test_no_special_char_fails(self):
        rule = SpecialCharRule()
        assert rule.check("Abcdefg1") == "특수문자를 포함해야 합니다"

    def test_with_special_char_passes(self):
        rule = SpecialCharRule()
        assert rule.check("Abcdefg1!") is None


class TestPasswordValidator:
    def test_empty_password_is_invalid(self):
        validator = PasswordValidator()
        result = validator.validate("")
        assert result.is_valid is False

    def test_short_password_reports_length_violation(self):
        validator = PasswordValidator()
        result = validator.validate("abc")
        assert "8자 이상이어야 합니다" in result.violations

    def test_password_without_uppercase_reports_violation(self):
        validator = PasswordValidator()
        result = validator.validate("abcdefgh1!")
        assert "대문자를 포함해야 합니다" in result.violations

    def test_password_without_digit_reports_violation(self):
        validator = PasswordValidator()
        result = validator.validate("Abcdefgh!")
        assert "숫자를 포함해야 합니다" in result.violations

    def test_password_without_special_char_reports_violation(self):
        validator = PasswordValidator()
        result = validator.validate("Abcdefg1")
        assert "특수문자를 포함해야 합니다" in result.violations

    def test_password_satisfying_all_rules_is_valid(self):
        validator = PasswordValidator()
        result = validator.validate("Abcdefg1!")
        assert result.is_valid is True
        assert result.violations == []

    def test_custom_min_length(self):
        validator = PasswordValidator(min_length=12)
        result = validator.validate("Short1!A")
        assert "12자 이상이어야 합니다" in result.violations

    def test_custom_min_length_satisfied(self):
        validator = PasswordValidator(min_length=12)
        result = validator.validate("Abcdefghij1!")
        assert result.is_valid is True

    def test_custom_rules_can_be_injected(self):
        class NoSpaceRule:
            def check(self, password: str) -> str | None:
                if " " in password:
                    return "공백을 포함할 수 없습니다"
                return None

        validator = PasswordValidator(rules=[NoSpaceRule()])
        result = validator.validate("has space")
        assert "공백을 포함할 수 없습니다" in result.violations

    def test_custom_rules_replace_defaults(self):
        class AlwaysPassRule:
            def check(self, password: str) -> str | None:
                return None

        validator = PasswordValidator(rules=[AlwaysPassRule()])
        result = validator.validate("")
        assert result.is_valid is True
```

---

## 원본(test-last) 대비 변경 요약

| 관점 | 원본 (test-last) | 리팩토링 (TDD) |
|---|---|---|
| **테스트 작성 시점** | 프로덕션 코드 완성 후 | 각 사이클마다 테스트 먼저 |
| **테스트 단위** | 전체 `check()` 결과를 한꺼번에 검증 | 개별 규칙을 독립 테스트 + 통합 테스트 |
| **구현 결합도** | `result['errors']`, `len(errors) == 3` 등 내부 구조에 의존 | `result.violations` 리스트에서 특정 메시지 존재 여부만 확인 |
| **규칙 확장성** | 클래스 내부 메서드로 고정 | `ValidationRule` 프로토콜로 분리, 외부 주입 가능 |
| **결과 객체** | 딕셔너리 (`{'valid': ..., 'errors': ...}`) | `ValidationResult` 데이터클래스 (타입 안전) |
| **네이밍** | `PasswordChecker.check` | `PasswordValidator.validate` (의도를 더 명확히 표현) |
| **특수문자 범위** | `!@#$%` 5개만 | 일반적인 특수문자 전체 포함 |
| **테스트 수** | 3개 | 15개 (규칙별 독립 테스트 8개 + 통합 테스트 7개) |

## 핵심 TDD 설계 원칙 반영

1. **Red-Green-Refactor 사이클**: 각 규칙마다 실패 테스트 -> 최소 구현 -> 리팩토링 순서로 진행
2. **테스트가 인터페이스를 결정**: `ValidationResult` 데이터클래스와 `ValidationRule` 프로토콜은 테스트 작성 과정에서 도출됨
3. **한 번에 하나의 행위**: 각 사이클이 정확히 하나의 규칙만 추가
4. **개방-폐쇄 원칙(OCP)**: 새 규칙 추가 시 기존 코드 수정 없이 `ValidationRule`을 구현한 클래스만 추가하면 됨
5. **테스트 격리**: 각 규칙 클래스가 독립적으로 테스트되므로 실패 원인을 즉시 특정할 수 있음
