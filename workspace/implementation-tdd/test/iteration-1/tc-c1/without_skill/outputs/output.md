# TDD로 CSV 파서 구현 - Fake It 전략

## 전략 개요

**Fake It** 전략은 테스트를 통과시키기 위해 가장 단순한 하드코딩 값을 먼저 반환한 뒤,
테스트를 추가(Triangulation)하면서 점진적으로 일반화하는 TDD 기법이다.

```
Red -> Green(Fake It) -> Triangulation -> Refactor(일반화)
```

---

## 요구사항 1: 쉼표로 구분된 문자열 파싱

### Step 1: Red - 첫 번째 테스트 작성

```python
import pytest
from csv_parser import parse_csv


def test_parse_single_row_with_two_fields():
    result = parse_csv("a,b")
    assert result == [["a", "b"]]
```

실행 결과: **RED** - `csv_parser` 모듈이 존재하지 않아 ImportError 발생.

### Step 2: Green (Fake It) - 하드코딩으로 통과

```python
# csv_parser.py
def parse_csv(text):
    return [["a", "b"]]
```

실행 결과: **GREEN** - 테스트 통과. 하지만 하드코딩이므로 어떤 입력이든 `[["a", "b"]]`를 반환한다.

### Step 3: Triangulation - 두 번째 테스트로 하드코딩을 깨뜨린다

```python
def test_parse_single_row_with_three_fields():
    result = parse_csv("x,y,z")
    assert result == [["x", "y", "z"]]
```

실행 결과: **RED** - `[["a", "b"]] != [["x", "y", "z"]]`. 하드코딩이 깨졌다.

### Step 4: Refactor (일반화) - 실제 분리 로직 구현

```python
# csv_parser.py
def parse_csv(text):
    return [text.split(",")]
```

실행 결과: **GREEN** - 두 테스트 모두 통과.

### Step 5: Triangulation - 여러 행 처리 테스트

```python
def test_parse_multiple_rows():
    result = parse_csv("a,b\nc,d")
    assert result == [["a", "b"], ["c", "d"]]
```

실행 결과: **RED** - `[["a,b\nc,d"]]` 반환. 행 분리가 없다.

### Step 6: Refactor (일반화) - 행 분리 추가

```python
# csv_parser.py
def parse_csv(text):
    lines = text.split("\n")
    return [line.split(",") for line in lines]
```

실행 결과: **GREEN** - 세 테스트 모두 통과.

> **현재 구현 상태:**
> ```python
> def parse_csv(text):
>     lines = text.split("\n")
>     return [line.split(",") for line in lines]
> ```

---

## 요구사항 2: 헤더 행 지원

### Step 7: Red - 헤더가 있는 경우 딕셔너리 리스트 반환

```python
def test_parse_with_header():
    result = parse_csv("name,age\nAlice,30", header=True)
    assert result == [{"name": "Alice", "age": "30"}]
```

실행 결과: **RED** - `parse_csv()`가 `header` 키워드 인자를 받지 않아 TypeError 발생.

### Step 8: Green (Fake It) - 하드코딩으로 통과

```python
# csv_parser.py
def parse_csv(text, header=False):
    lines = text.split("\n")
    if header:
        return [{"name": "Alice", "age": "30"}]
    return [line.split(",") for line in lines]
```

실행 결과: **GREEN** - 통과. 하지만 header=True일 때 하드코딩이다.

### Step 9: Triangulation - 다른 헤더 데이터로 테스트

```python
def test_parse_with_header_different_data():
    result = parse_csv("city,country\nSeoul,Korea\nTokyo,Japan", header=True)
    assert result == [
        {"city": "Seoul", "country": "Korea"},
        {"city": "Tokyo", "country": "Japan"},
    ]
```

실행 결과: **RED** - 하드코딩된 Alice/30 데이터가 반환되어 실패.

### Step 10: Refactor (일반화) - 헤더 로직 구현

```python
# csv_parser.py
def parse_csv(text, header=False):
    lines = text.split("\n")
    rows = [line.split(",") for line in lines]
    if header:
        keys = rows[0]
        return [dict(zip(keys, row)) for row in rows[1:]]
    return rows
```

실행 결과: **GREEN** - 모든 테스트 통과.

> **현재 구현 상태:**
> ```python
> def parse_csv(text, header=False):
>     lines = text.split("\n")
>     rows = [line.split(",") for line in lines]
>     if header:
>         keys = rows[0]
>         return [dict(zip(keys, row)) for row in rows[1:]]
>     return rows
> ```

---

## 요구사항 3: 빈 값 처리

### Step 11: Red - 빈 필드가 있는 경우

```python
def test_parse_empty_fields():
    result = parse_csv("a,,c")
    assert result == [["a", "", "c"]]
```

실행 결과: **GREEN** - `str.split(",")` 은 빈 문자열을 보존하므로 이미 통과한다.

> 이미 통과하는 테스트는 **회귀 방지** 역할을 한다. 다음 테스트로 넘어간다.

### Step 12: Red - 빈 값이 포함된 헤더 모드

```python
def test_parse_empty_fields_with_header():
    result = parse_csv("name,age,city\nAlice,,Seoul", header=True)
    assert result == [{"name": "Alice", "age": "", "city": "Seoul"}]
```

실행 결과: **GREEN** - 현재 구현이 이미 빈 문자열을 올바르게 처리한다.

### Step 13: Red - 모든 필드가 빈 경우

```python
def test_parse_all_empty_fields():
    result = parse_csv(",,")
    assert result == [["", "", ""]]
```

실행 결과: **GREEN** - 역시 이미 통과.

### Step 14: Red - 빈 행 처리 (트레일링 개행)

```python
def test_trailing_newline_ignored():
    result = parse_csv("a,b\nc,d\n")
    assert result == [["a", "b"], ["c", "d"]]
```

실행 결과: **RED** - 마지막 빈 줄이 `[""]`로 파싱되어 `[["a", "b"], ["c", "d"], [""]]` 반환.

### Step 15: Green (Fake It) - 빈 행 제거

```python
# csv_parser.py
def parse_csv(text, header=False):
    lines = text.split("\n")
    lines = [line for line in lines if line]
    rows = [line.split(",") for line in lines]
    if header:
        keys = rows[0]
        return [dict(zip(keys, row)) for row in rows[1:]]
    return rows
```

실행 결과: **GREEN** - 모든 테스트 통과.

> 여기서 Fake It이 아닌 즉시 일반화를 적용했다. 빈 행 필터링은
> 충분히 단순하여 하드코딩 단계가 불필요하다고 판단했다.
> TDD에서는 자신감이 있을 때 보폭을 넓힐 수 있다.

> **현재 구현 상태:**
> ```python
> def parse_csv(text, header=False):
>     lines = text.split("\n")
>     lines = [line for line in lines if line]
>     rows = [line.split(",") for line in lines]
>     if header:
>         keys = rows[0]
>         return [dict(zip(keys, row)) for row in rows[1:]]
>     return rows
> ```

---

## 요구사항 4: 따옴표로 감싼 필드 (쉼표 포함 가능)

이 요구사항이 가장 복잡하므로 Fake It 전략이 빛을 발하는 구간이다.

### Step 16: Red - 따옴표 필드 기본

```python
def test_parse_quoted_field():
    result = parse_csv('"hello",world')
    assert result == [["hello", "world"]]
```

실행 결과: **RED** - `[["\"hello\"", "world"]]` 반환. 따옴표가 제거되지 않는다.

### Step 17: Green (Fake It) - 하드코딩

```python
def parse_csv(text, header=False):
    lines = text.split("\n")
    lines = [line for line in lines if line]
    rows = [_parse_line(line) for line in lines]
    if header:
        keys = rows[0]
        return [dict(zip(keys, row)) for row in rows[1:]]
    return rows


def _parse_line(line):
    if '"' in line:
        return ["hello", "world"]
    return line.split(",")
```

실행 결과: **GREEN** - 통과. 하지만 완전한 하드코딩이다.

### Step 18: Triangulation - 다른 따옴표 필드

```python
def test_parse_different_quoted_field():
    result = parse_csv('"foo",bar')
    assert result == [["foo", "bar"]]
```

실행 결과: **RED** - `[["hello", "world"]] != [["foo", "bar"]]`. 하드코딩이 깨졌다.

### Step 19: Refactor (일반화) - 따옴표 제거 로직

```python
def _parse_line(line):
    if '"' not in line:
        return line.split(",")
    fields = []
    for field in line.split(","):
        field = field.strip('"')
        fields.append(field)
    return fields
```

실행 결과: **GREEN** - 두 따옴표 테스트 모두 통과.

### Step 20: Triangulation - 쉼표가 포함된 따옴표 필드 (핵심 케이스)

```python
def test_parse_quoted_field_with_comma():
    result = parse_csv('"hello, world",foo')
    assert result == [["hello, world", "foo"]]
```

실행 결과: **RED** - `split(",")` 가 따옴표 안의 쉼표도 분리해버린다.
`[["hello", " world", "foo"]]` 반환.

### Step 21: Green (Fake It) - 특정 케이스 하드코딩

```python
def _parse_line(line):
    if '"' not in line:
        return line.split(",")
    # Fake: 특정 입력에 대해 하드코딩
    if line == '"hello, world",foo':
        return ["hello, world", "foo"]
    fields = []
    for field in line.split(","):
        field = field.strip('"')
        fields.append(field)
    return fields
```

실행 결과: **GREEN** - 통과. 하지만 하나의 입력에만 동작한다.

### Step 22: Triangulation - 또 다른 쉼표 포함 필드

```python
def test_parse_another_quoted_field_with_comma():
    result = parse_csv('first,"Seoul, Korea",last')
    assert result == [["first", "Seoul, Korea", "last"]]
```

실행 결과: **RED** - 하드코딩이 이 입력을 처리하지 못한다.

### Step 23: Refactor (일반화) - 상태 기반 파서 구현

이제 두 개의 삼각측량 테스트가 하드코딩을 깨뜨렸으므로, 일반적인 파싱 로직을 구현한다.

```python
def _parse_line(line):
    fields = []
    current = []
    in_quotes = False

    for char in line:
        if char == '"':
            in_quotes = not in_quotes
        elif char == ',' and not in_quotes:
            fields.append(''.join(current))
            current = []
        else:
            current.append(char)

    fields.append(''.join(current))
    return fields
```

실행 결과: **GREEN** - 모든 테스트 통과.

### Step 24: Triangulation - 복합 케이스 검증

```python
def test_parse_mixed_quoted_and_unquoted():
    result = parse_csv('name,address,note\nAlice,"Seoul, Korea","good, very good"', header=True)
    assert result == [
        {"name": "Alice", "address": "Seoul, Korea", "note": "good, very good"}
    ]
```

실행 결과: **GREEN** - 일반화된 파서가 복합 케이스도 처리한다.

### Step 25: 엣지 케이스 - 따옴표 안의 따옴표 (이스케이프)

```python
def test_parse_escaped_quotes():
    result = parse_csv('"She said ""hi""",b')
    assert result == [['She said "hi"', "b"]]
```

실행 결과: **RED** - `""` 이스케이프를 처리하지 못한다.

### Step 26: Green (Fake It) - 이스케이프 하드코딩

```python
def _parse_line(line):
    if '""' in line:
        return ['She said "hi"', "b"]
    # ... 기존 로직
```

실행 결과: **GREEN** - 하드코딩 통과.

### Step 27: Triangulation

```python
def test_parse_escaped_quotes_different():
    result = parse_csv('a,"value with ""quotes""",c')
    assert result == [["a", 'value with "quotes"', "c"]]
```

실행 결과: **RED** - 하드코딩이 깨졌다.

### Step 28: Refactor (일반화) - 이스케이프 처리 추가

```python
def _parse_line(line):
    fields = []
    current = []
    in_quotes = False
    i = 0

    while i < len(line):
        char = line[i]
        if char == '"':
            if in_quotes and i + 1 < len(line) and line[i + 1] == '"':
                current.append('"')
                i += 2
                continue
            in_quotes = not in_quotes
        elif char == ',' and not in_quotes:
            fields.append(''.join(current))
            current = []
        else:
            current.append(char)
        i += 1

    fields.append(''.join(current))
    return fields
```

실행 결과: **GREEN** - 모든 테스트 통과.

---

## 최종 코드

### csv_parser.py

```python
def parse_csv(text, header=False):
    """CSV 문자열을 파싱하여 2차원 리스트 또는 딕셔너리 리스트를 반환한다.

    Args:
        text: CSV 형식의 문자열
        header: True이면 첫 행을 헤더로 사용하여 딕셔너리 리스트 반환

    Returns:
        header=False: list[list[str]]
        header=True: list[dict[str, str]]
    """
    lines = text.split("\n")
    lines = [line for line in lines if line]
    rows = [_parse_line(line) for line in lines]
    if header:
        keys = rows[0]
        return [dict(zip(keys, row)) for row in rows[1:]]
    return rows


def _parse_line(line):
    """한 줄의 CSV를 필드 리스트로 파싱한다.

    따옴표로 감싼 필드 내의 쉼표와 이스케이프된 따옴표("")를 처리한다.
    """
    fields = []
    current = []
    in_quotes = False
    i = 0

    while i < len(line):
        char = line[i]
        if char == '"':
            if in_quotes and i + 1 < len(line) and line[i + 1] == '"':
                current.append('"')
                i += 2
                continue
            in_quotes = not in_quotes
        elif char == ',' and not in_quotes:
            fields.append(''.join(current))
            current = []
        else:
            current.append(char)
        i += 1

    fields.append(''.join(current))
    return fields
```

### test_csv_parser.py

```python
import pytest
from csv_parser import parse_csv


# --- 요구사항 1: 쉼표로 구분된 문자열 파싱 ---

def test_parse_single_row_with_two_fields():
    result = parse_csv("a,b")
    assert result == [["a", "b"]]


def test_parse_single_row_with_three_fields():
    result = parse_csv("x,y,z")
    assert result == [["x", "y", "z"]]


def test_parse_multiple_rows():
    result = parse_csv("a,b\nc,d")
    assert result == [["a", "b"], ["c", "d"]]


# --- 요구사항 2: 헤더 행 지원 ---

def test_parse_with_header():
    result = parse_csv("name,age\nAlice,30", header=True)
    assert result == [{"name": "Alice", "age": "30"}]


def test_parse_with_header_different_data():
    result = parse_csv("city,country\nSeoul,Korea\nTokyo,Japan", header=True)
    assert result == [
        {"city": "Seoul", "country": "Korea"},
        {"city": "Tokyo", "country": "Japan"},
    ]


# --- 요구사항 3: 빈 값 처리 ---

def test_parse_empty_fields():
    result = parse_csv("a,,c")
    assert result == [["a", "", "c"]]


def test_parse_empty_fields_with_header():
    result = parse_csv("name,age,city\nAlice,,Seoul", header=True)
    assert result == [{"name": "Alice", "age": "", "city": "Seoul"}]


def test_parse_all_empty_fields():
    result = parse_csv(",,")
    assert result == [["", "", ""]]


def test_trailing_newline_ignored():
    result = parse_csv("a,b\nc,d\n")
    assert result == [["a", "b"], ["c", "d"]]


# --- 요구사항 4: 따옴표로 감싼 필드 ---

def test_parse_quoted_field():
    result = parse_csv('"hello",world')
    assert result == [["hello", "world"]]


def test_parse_different_quoted_field():
    result = parse_csv('"foo",bar')
    assert result == [["foo", "bar"]]


def test_parse_quoted_field_with_comma():
    result = parse_csv('"hello, world",foo')
    assert result == [["hello, world", "foo"]]


def test_parse_another_quoted_field_with_comma():
    result = parse_csv('first,"Seoul, Korea",last')
    assert result == [["first", "Seoul, Korea", "last"]]


def test_parse_mixed_quoted_and_unquoted():
    result = parse_csv(
        'name,address,note\nAlice,"Seoul, Korea","good, very good"',
        header=True,
    )
    assert result == [
        {"name": "Alice", "address": "Seoul, Korea", "note": "good, very good"}
    ]


def test_parse_escaped_quotes():
    result = parse_csv('"She said ""hi""",b')
    assert result == [['She said "hi"', "b"]]


def test_parse_escaped_quotes_different():
    result = parse_csv('a,"value with ""quotes""",c')
    assert result == [["a", 'value with "quotes"', "c"]]
```

---

## Fake It 전략 요약

| 단계 | 요구사항 | Fake It | Triangulation | 일반화 |
|------|----------|---------|---------------|--------|
| 1-4 | 쉼표 분리 | `return [["a", "b"]]` | `"x,y,z"` 입력 추가 | `line.split(",")` |
| 5-6 | 다중 행 | (단일 행만 처리) | `"a,b\nc,d"` 입력 | `text.split("\n")` + 리스트 컴프리헨션 |
| 7-10 | 헤더 | `return [{"name": "Alice"...}]` | 다른 헤더/데이터 입력 | `dict(zip(keys, row))` |
| 14-15 | 빈 행 | - | 트레일링 개행 | `if line` 필터 |
| 16-19 | 따옴표 제거 | `return ["hello", "world"]` | `"foo",bar` 입력 | `strip('"')` |
| 20-23 | 따옴표+쉼표 | 특정 문자열 하드코딩 | 다른 쉼표 포함 필드 | 상태 기반 파서 (`in_quotes` 플래그) |
| 25-28 | 이스케이프 따옴표 | `return ['She said "hi"', "b"]` | 다른 이스케이프 패턴 | `""` -> `"` 변환 로직 |

### 핵심 교훈

1. **Fake It은 두려움을 줄인다**: 복잡한 따옴표 파싱도 하드코딩부터 시작하면 부담이 없다.
2. **Triangulation이 설계를 이끈다**: 두 번째 테스트가 하드코딩을 깨뜨릴 때, 그때 비로소 일반화의 방향이 명확해진다.
3. **보폭 조절**: 빈 값 처리처럼 단순한 경우는 Fake It 없이 바로 일반화해도 된다. TDD의 보폭은 자신감에 비례한다.
4. **점진적 복잡도 증가**: 단순 split -> 행 분리 -> 헤더 -> 따옴표 -> 이스케이프 순서로, 각 단계가 이전 단계 위에 쌓인다.
