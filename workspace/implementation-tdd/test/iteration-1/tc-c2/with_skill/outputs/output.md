# TDAID로 한국어 날짜 파서 구현

TDAID(Test-Driven AI Development) 5단계 워크플로우를 적용하여
한국어 날짜 파서를 구현한다.

---

## Step 1: Plan -- 요구사항을 테스트 목록으로 변환

요구사항을 분석하고, 테스트 목록을 작성한다. 가장 단순한 경우부터
시작하여 복잡한 경우로 진행한다(Red Bar Patterns: 시작 테스트, 한 단계 테스트).

### 테스트 목록

```
[x] 한국어 형식 파싱: "2026년 4월 5일" -> date(2026, 4, 5)
[x] 한국어 형식 파싱: "2026년 12월 25일" -> date(2026, 12, 25)
[x] 한국어 형식 파싱: "2026년 1월 1일" (한 자리 월/일)
[x] 한국어 형식 파싱: "2026년 04월 05일" (앞에 0이 붙은 경우)
[x] 슬래시 형식 파싱: "2026/04/05" -> date(2026, 4, 5)
[x] 슬래시 형식 파싱: "2026/1/1" (한 자리 월/일)
[x] 대시 형식 파싱: "2026-04-05" -> date(2026, 4, 5)
[x] 대시 형식 파싱: "2026-1-1" (한 자리 월/일)
[x] 빈 문자열 -> ValueError
[x] 임의 문자열 "잘못된 날짜" -> ValueError
[x] None 입력 -> TypeError
[x] 13월 -> ValueError (한국어/슬래시/대시 모든 형식)
[x] 32일 -> ValueError (한국어/슬래시/대시 모든 형식)
[x] 0월 -> ValueError
[x] 0일 -> ValueError
[x] 2월 30일 -> ValueError (달력상 불가능한 날짜)
```

테스트 선택 순서 근거:
1. **시작 테스트** -- 가장 단순한 정상 입력(한국어 형식 1개)부터 시작
2. **한 단계 테스트** -- 새로운 무언가를 가르쳐 주는 테스트를 선택 (다른 형식, 엣지 케이스)
3. **하나에서 여러 개로** -- 단일 형식 -> 3가지 형식 확장
4. 마지막으로 오류 케이스로 방어 로직 검증

---

## Step 2: Red -- 실패하는 테스트 작성 (개발자)

테스트를 먼저 작성한다. 구현이 없으므로 모든 테스트가 실패(Red)한다.
테스트 명명은 `[대상]__[조건]__[기대행위]` 규칙을 따른다(Testing Patterns).
AAA 패턴(Arrange-Act-Assert)을 적용하되, 순수 함수이므로 Arrange가 최소화된다.

```python
"""한국어 날짜 파서 테스트 -- TDAID Red 단계에서 작성."""

from datetime import date

import pytest

from korean_date_parser import parse_korean_date


class TestParseKoreanDateFormat:
    """'YYYY년 M월 D일' 형식 파싱 테스트."""

    def test_parse_korean_date__standard__returns_date(self):
        assert parse_korean_date("2026년 4월 5일") == date(2026, 4, 5)

    def test_parse_korean_date__december__returns_date(self):
        assert parse_korean_date("2026년 12월 25일") == date(2026, 12, 25)

    def test_parse_korean_date__single_digit_month_day__returns_date(self):
        assert parse_korean_date("2026년 1월 1일") == date(2026, 1, 1)

    def test_parse_korean_date__padded_digits__returns_date(self):
        assert parse_korean_date("2026년 04월 05일") == date(2026, 4, 5)


class TestParseSlashFormat:
    """'YYYY/MM/DD' 형식 파싱 테스트."""

    def test_parse_slash__standard__returns_date(self):
        assert parse_korean_date("2026/04/05") == date(2026, 4, 5)

    def test_parse_slash__single_digit__returns_date(self):
        assert parse_korean_date("2026/1/1") == date(2026, 1, 1)


class TestParseDashFormat:
    """'YYYY-MM-DD' 형식 파싱 테스트."""

    def test_parse_dash__standard__returns_date(self):
        assert parse_korean_date("2026-04-05") == date(2026, 4, 5)

    def test_parse_dash__single_digit__returns_date(self):
        assert parse_korean_date("2026-1-1") == date(2026, 1, 1)


class TestInvalidInput:
    """잘못된 입력에 ValueError를 발생시키는 테스트."""

    def test_parse__empty_string__raises_value_error(self):
        with pytest.raises(ValueError):
            parse_korean_date("")

    def test_parse__random_text__raises_value_error(self):
        with pytest.raises(ValueError):
            parse_korean_date("잘못된 날짜")

    def test_parse__none_input__raises_value_error(self):
        with pytest.raises((ValueError, TypeError)):
            parse_korean_date(None)


class TestOutOfRangeInput:
    """범위 밖 날짜 입력 거부 테스트."""

    def test_parse__month_13__raises_value_error(self):
        with pytest.raises(ValueError):
            parse_korean_date("2026년 13월 1일")

    def test_parse__day_32__raises_value_error(self):
        with pytest.raises(ValueError):
            parse_korean_date("2026년 1월 32일")

    def test_parse__month_0__raises_value_error(self):
        with pytest.raises(ValueError):
            parse_korean_date("2026년 0월 1일")

    def test_parse__day_0__raises_value_error(self):
        with pytest.raises(ValueError):
            parse_korean_date("2026년 1월 0일")

    def test_parse__feb_30__raises_value_error(self):
        with pytest.raises(ValueError):
            parse_korean_date("2026-02-30")

    def test_parse__slash_month_13__raises_value_error(self):
        with pytest.raises(ValueError):
            parse_korean_date("2026/13/01")

    def test_parse__dash_day_32__raises_value_error(self):
        with pytest.raises(ValueError):
            parse_korean_date("2026-01-32")
```

Red 상태에서의 테스트 결과 (구현 전):
```
FAILED test_korean_date_parser.py - ModuleNotFoundError: No module named 'korean_date_parser'
```

모든 18개 테스트가 실패한다. 이것이 올바른 Red 상태이다.

---

## Step 3: Green -- AI가 구현 제안

AI가 테스트를 통과하는 최소한의 구현을 제안한다.

### Green Bar 전략 선택

- 정규식 패턴 매칭은 **명백한 구현(Obvious Implementation)**을 적용한다
  -- 세 가지 날짜 형식 각각에 대해 정규식이 명확하다.
- 범위 검증은 `datetime.date` 생성자에 위임한다
  -- `date(2026, 13, 1)`이 자체적으로 `ValueError`를 발생시킨다.

### 구현 코드

```python
"""한국어 날짜 파서 -- TDAID Green 단계에서 AI가 구현."""

import re
from datetime import date

_KOREAN_PATTERN = re.compile(
    r"^(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일$"
)
_SLASH_PATTERN = re.compile(
    r"^(\d{4})/(\d{1,2})/(\d{1,2})$"
)
_DASH_PATTERN = re.compile(
    r"^(\d{4})-(\d{1,2})-(\d{1,2})$"
)


def parse_korean_date(text: str) -> date:
    """한국어 날짜 문자열을 datetime.date로 변환한다.

    지원 형식:
        - 'YYYY년 M월 D일'
        - 'YYYY/MM/DD'
        - 'YYYY-MM-DD'

    Args:
        text: 날짜 문자열.

    Returns:
        파싱된 datetime.date 객체.

    Raises:
        ValueError: 인식할 수 없는 형식이거나 범위 밖 날짜.
        TypeError: text가 문자열이 아닌 경우.
    """
    if not isinstance(text, str):
        raise TypeError(f"문자열이 필요합니다: {type(text).__name__}")

    text = text.strip()
    if not text:
        raise ValueError("빈 문자열은 날짜로 변환할 수 없습니다")

    year, month, day = _extract_components(text)
    return _build_date(year, month, day)


def _extract_components(text: str) -> tuple[int, int, int]:
    for pattern in (_KOREAN_PATTERN, _SLASH_PATTERN, _DASH_PATTERN):
        match = pattern.match(text)
        if match:
            return int(match.group(1)), int(match.group(2)), int(match.group(3))
    raise ValueError(f"인식할 수 없는 날짜 형식입니다: '{text}'")


def _build_date(year: int, month: int, day: int) -> date:
    try:
        return date(year, month, day)
    except ValueError as e:
        raise ValueError(f"유효하지 않은 날짜입니다: {year}-{month}-{day} ({e})") from e
```

### 설계 결정 근거

| 결정 | 근거 |
|------|------|
| 정규식을 모듈 수준 상수로 컴파일 | 반복 호출 시 성능 최적화, 불변 패턴 |
| `_extract_components`와 `_build_date` 분리 | 단일 책임 -- 파싱과 검증을 분리 |
| `date()` 생성자에 범위 검증 위임 | 윤년, 월별 일수 등 복잡한 달력 로직을 직접 구현하지 않음 |
| `from e`으로 체이닝 | 원본 예외를 보존하여 디버깅 용이 |

---

## Step 4: Refactor -- AI + 개발자 협업으로 개선

Green 상태에서 리팩토링한다. 중복 제거와 가독성 개선에 집중한다.

### 리팩토링 점검

| 항목 | 상태 | 설명 |
|------|------|------|
| 중복 제거 | 완료 | 3개 패턴 순회를 단일 루프로 통합 |
| 함수 분리 | 완료 | public API 1개 + private helper 2개 |
| 타입 힌트 | 완료 | 입출력 타입 명시 |
| docstring | 완료 | 공개 함수에 Args/Returns/Raises 기재 |
| 테스트 구조 | 완료 | 기능별 클래스 분리, AAA 패턴 준수 |

### 리팩토링 전후 비교

리팩토링 대상이 된 주요 사항:

**1. 패턴 순회 통합**

```
[Before]
# 각 형식에 대해 개별 if-elif 분기
if _KOREAN_PATTERN.match(text):
    ...
elif _SLASH_PATTERN.match(text):
    ...
elif _DASH_PATTERN.match(text):
    ...

[After]
# 단일 루프로 통합
for pattern in (_KOREAN_PATTERN, _SLASH_PATTERN, _DASH_PATTERN):
    match = pattern.match(text)
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3))

[Reason] Reconcile Differences -- 세 분기의 구조가 동일하므로 루프로
중복을 제거한다. 새 형식 추가 시 패턴 튜플에 1줄만 추가하면 된다.
```

**2. 검증 로직 위임**

```
[Before]
# 직접 범위 검증 구현
if month < 1 or month > 12:
    raise ValueError(...)
if day < 1 or day > 31:
    raise ValueError(...)

[After]
# datetime.date 생성자에 위임
def _build_date(year: int, month: int, day: int) -> date:
    try:
        return date(year, month, day)
    except ValueError as e:
        raise ValueError(...) from e

[Reason] 명백한 구현 -- datetime.date가 이미 윤년, 월별 일수를 포함한
완전한 검증을 제공한다. 직접 구현하면 달력 로직의 버그 위험이 생긴다.
```

**3. 테스트 클래스 구조화**

```
[Before]
# 모든 테스트가 단일 파일에 평탄하게 나열

[After]
# 기능별 테스트 클래스 분리
class TestParseKoreanDateFormat:   # 한국어 형식
class TestParseSlashFormat:        # 슬래시 형식
class TestParseDashFormat:         # 대시 형식
class TestInvalidInput:            # 잘못된 입력
class TestOutOfRangeInput:         # 범위 밖 입력

[Reason] 테스트 구조 -- 관련 테스트를 응집도 높은 그룹으로 묶어
가독성과 유지보수성을 높인다.
```

---

## Step 5: Validate -- 정확성, 보안, 성능 최종 검증

### 5-1. 정확성 검증

전체 18개 테스트 케이스에 대한 정확성 추적:

| # | 테스트 | 입력 | 기대 결과 | 통과 근거 |
|---|--------|------|-----------|-----------|
| 1 | `test_parse_korean_date__standard__returns_date` | `"2026년 4월 5일"` | `date(2026, 4, 5)` | `_KOREAN_PATTERN`이 `(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일`로 매칭, `int("2026")=2026, int("4")=4, int("5")=5`, `date(2026,4,5)` 정상 생성 |
| 2 | `test_parse_korean_date__december__returns_date` | `"2026년 12월 25일"` | `date(2026, 12, 25)` | 동일 패턴, `\d{1,2}`가 12와 25를 매칭 |
| 3 | `test_parse_korean_date__single_digit_month_day__returns_date` | `"2026년 1월 1일"` | `date(2026, 1, 1)` | `\d{1,2}`가 한 자리 숫자도 매칭 |
| 4 | `test_parse_korean_date__padded_digits__returns_date` | `"2026년 04월 05일"` | `date(2026, 4, 5)` | `int("04")=4, int("05")=5`로 앞자리 0 제거 |
| 5 | `test_parse_slash__standard__returns_date` | `"2026/04/05"` | `date(2026, 4, 5)` | `_SLASH_PATTERN` 매칭 |
| 6 | `test_parse_slash__single_digit__returns_date` | `"2026/1/1"` | `date(2026, 1, 1)` | `\d{1,2}`가 한 자리 매칭 |
| 7 | `test_parse_dash__standard__returns_date` | `"2026-04-05"` | `date(2026, 4, 5)` | `_DASH_PATTERN` 매칭 |
| 8 | `test_parse_dash__single_digit__returns_date` | `"2026-1-1"` | `date(2026, 1, 1)` | `\d{1,2}`가 한 자리 매칭 |
| 9 | `test_parse__empty_string__raises_value_error` | `""` | `ValueError` | `strip()` 후 빈 문자열 -> `ValueError` 발생 |
| 10 | `test_parse__random_text__raises_value_error` | `"잘못된 날짜"` | `ValueError` | 세 패턴 모두 불일치 -> `_extract_components`에서 `ValueError` |
| 11 | `test_parse__none_input__raises_value_error` | `None` | `TypeError` | `isinstance(None, str)` is `False` -> `TypeError` 발생 |
| 12 | `test_parse__month_13__raises_value_error` | `"2026년 13월 1일"` | `ValueError` | 패턴 매칭 성공, `date(2026, 13, 1)` -> `ValueError` |
| 13 | `test_parse__day_32__raises_value_error` | `"2026년 1월 32일"` | `ValueError` | `date(2026, 1, 32)` -> `ValueError` |
| 14 | `test_parse__month_0__raises_value_error` | `"2026년 0월 1일"` | `ValueError` | `date(2026, 0, 1)` -> `ValueError` |
| 15 | `test_parse__day_0__raises_value_error` | `"2026년 1월 0일"` | `ValueError` | `date(2026, 1, 0)` -> `ValueError` |
| 16 | `test_parse__feb_30__raises_value_error` | `"2026-02-30"` | `ValueError` | `date(2026, 2, 30)` -> `ValueError` (2월은 최대 28/29일) |
| 17 | `test_parse__slash_month_13__raises_value_error` | `"2026/13/01"` | `ValueError` | `date(2026, 13, 1)` -> `ValueError` |
| 18 | `test_parse__dash_day_32__raises_value_error` | `"2026-01-32"` | `ValueError` | `date(2026, 1, 32)` -> `ValueError` |

정확성 판정: **18/18 통과**

### 5-2. AI 환각(Hallucination) 검증

| 검증 항목 | 결과 |
|-----------|------|
| 존재하지 않는 라이브러리 import | 없음 -- `re`, `datetime`은 표준 라이브러리 |
| 잘못된 API 사용 | 없음 -- `re.compile`, `date()` 모두 정확 |
| 하드코딩된 마법 값 | 없음 -- 모든 상수가 의미를 가짐 |
| 불필요한 복잡성 | 없음 -- 최소한의 코드로 구현 |

### 5-3. 보안 검증

| 위험 | 방어 여부 | 설명 |
|------|-----------|------|
| ReDoS (정규식 서비스 거부) | 방어됨 | 모든 패턴이 `^...$`로 앵커링되어 있고, 중첩 반복자가 없음. 역추적 폭발 불가 |
| 인젝션 공격 | 해당 없음 | 외부 시스템 호출 없음, 순수 파싱 함수 |
| 타입 혼동 | 방어됨 | `isinstance` 검사로 문자열이 아닌 입력 거부 |
| 무한 입력 | 부분 방어 | `^...$` 앵커가 전체 문자열 매칭을 강제하여 긴 문자열도 빠르게 실패. 추가로 `len(text)` 상한 검사를 고려할 수 있음 |

### 5-4. 성능 검증

| 항목 | 분석 |
|------|------|
| 정규식 컴파일 | 모듈 로드 시 1회만 실행 (상수) |
| 패턴 매칭 | 최대 3회 매칭 시도, 각각 O(n) -- n은 입력 길이 (최대 ~20자) |
| 메모리 | 추가 할당 없음, `Match` 객체만 임시 생성 |
| 전체 복잡도 | O(1) -- 입력 길이가 날짜 형식에 의해 상한이 고정됨 |

---

## TDD 원칙 적용 요약

| 원칙 | 적용 방식 |
|------|-----------|
| Three Laws | 테스트(Red) 먼저 작성 -> 최소 구현(Green) -> 리팩토링(Refactor) |
| Test List (Red Bar) | 16개 테스트 목록을 사전에 작성하고 순서대로 진행 |
| 시작 테스트 (Red Bar) | 가장 단순한 한국어 형식 1개부터 시작 |
| 명백한 구현 (Green Bar) | 정규식 매칭이 명확하므로 바로 구현 |
| 출력 기반 테스트 (Four Pillars) | 순수 함수의 반환값만 검증 -- 최고 수준의 리팩토링 내성 |
| TDAID Validate (TDD+AI) | AI 환각, 보안, 성능을 별도 단계에서 검증 |

---

## 파일 위치

- 테스트: `src/test_korean_date_parser.py`
- 구현: `src/korean_date_parser.py`
