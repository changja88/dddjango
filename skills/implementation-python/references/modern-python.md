# Modern Python: 3.12-3.14 최신 기능

Python 3.12~3.14에서 도입된 주요 기능과 변경사항을 정리한다.

---

## f-문자열 제한 해제 (PEP 701, Python 3.12+)

PEG 파서 덕분에 f-문자열의 모든 제한이 사라졌다.

```python
# 1. 동일 따옴표 재사용
songs = ["Yesterday", "Hey Jude"]
result = f"{''.join(songs)}"

# 2. 여러 줄 + 인라인 주석
query = f"""
    SELECT *
    FROM users
    WHERE active = {
        True  # 활성 사용자만
    }
"""

# 3. 백슬래시와 표현식 내부 사용
words = ["hello", "world"]
result = f"{'\n'.join(words)}"

# 4. 중첩 f-문자열
data = {"key": "value"}
result = f"{f"{list(data.keys())[0]}"}"
```

---

## PEP 695: 새 타입 매개변수 문법 (3.12+)

TypeVar를 전역 스코프에 선언해야 하는 번거로움을 제거한다.

```python
# 3.11 이전 (레거시)
from typing import TypeVar, Generic
T = TypeVar('T')
class Container(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value

# 3.12+ -- 권장
class Container[T]:
    def __init__(self, value: T) -> None:
        self.value = value

# type 문으로 타입 앨리어스 선언 (지연 평가)
type Vector[T] = list[T]
type Matrix[T] = list[Vector[T]]
type RecursiveList[T] = T | list['RecursiveList[T]']
```

---

## 컴프리헨션 인라이닝 (PEP 709, Python 3.12+)

컴프리헨션이 인라인으로 실행되어 별도 함수 객체/프레임 생성 없이 최대 2배 빠르다.

---

## @deprecated (PEP 702, Python 3.13+)

런타임 `DeprecationWarning` + 타입 체커 경고를 동시에 발생시킨다.

```python
from warnings import deprecated

@deprecated("Use UserV2 instead")
class UserV1:
    pass

@deprecated("Use fetch_data_v2() instead")
def fetch_data(url: str) -> bytes:
    return b""
```

---

## TypeIs (PEP 742, Python 3.13+)

if/else 양쪽 분기 모두에서 타입 좁히기가 가능하다. `TypeGuard`의 개선판.

---

## TypeVar 기본값 (PEP 696, Python 3.13+)

```python
class Container[T = str]:
    def __init__(self, value: T) -> None:
        self.value = value

c = Container("hello")    # Container[str]
c2 = Container[int](42)   # Container[int]
```

---

## Free-Threaded Python (PEP 703, Python 3.13+)

GIL을 비활성화하여 스레드 기반 진정한 병렬 실행. 실험적 기능.
`python3.13t` 또는 `PYTHON_GIL=0` / `-X gil=0`으로 활성화.

---

## 어노테이션 지연 평가 (PEP 649, Python 3.14)

`from __future__ import annotations` 없이도 전방 참조가 가능하다.

```python
# 3.14+: 따옴표 없이 전방 참조 가능
class Tree:
    def __init__(self, left: Tree | None, right: Tree | None):
        ...  # 어노테이션이 지연 평가되므로 OK

# 어노테이션 접근 방법
import annotationlib
# VALUE: 런타임 값으로 평가 (기존 동작)
# FORWARDREF: 미정의 이름을 ForwardRef로 대체
# STRING: 문자열로 반환
```

---

## Template Strings (t-strings) -- PEP 750, Python 3.14

f-string과 달리 Template 객체를 반환하여 보간 전에 검증/이스케이프가 가능하다.

```python
from string.templatelib import Template

name = "World"
t_result = t"Hello, {name}!"  # Template 객체 (즉시 문자열 아님)

# SQL 인젝션 방지 예시
def safe_sql(template: Template) -> str:
    parts = []
    params = []
    for item in template:
        if isinstance(item, str):
            parts.append(item)
        else:
            parts.append("?")
            params.append(item.value)
    return "".join(parts), params

user_input = "'; DROP TABLE users; --"
query, params = safe_sql(t"SELECT * FROM users WHERE name = {user_input}")
# query: "SELECT * FROM users WHERE name = ?"
# params: ["'; DROP TABLE users; --"]  -- 안전하게 파라미터화
```

---

## Subinterpreters (PEP 734, Python 3.14)

GIL 없이 진정한 멀티코어 병렬성을 제공하는 공식 API.

```python
import concurrent.interpreters as interpreters

interp = interpreters.create()
interp.exec("print('별도 인터프리터에서 실행')")
```

---

## 버전별 핵심 기능 요약

| 버전 | 핵심 기능 | PEP |
|------|----------|-----|
| 3.10 | match/case, `X \| Y` 유니온, ParamSpec | 634, 604, 612 |
| 3.11 | ExceptionGroup, TaskGroup, 25% 성능 향상 | 654, 680, 659 |
| 3.12 | type 문, `def f[T]()`, f-string 제한 해제, 컴프리헨션 인라이닝 | 695, 701, 709 |
| 3.13 | Free-threading, JIT, TypeIs, @deprecated | 703, 744, 742, 702 |
| 3.14 | 어노테이션 지연 평가, t-strings, subinterpreters | 649, 750, 734 |

---

## 타입 시스템 진화 요약

| 기능 | 도입 버전 | 용도 |
|------|----------|------|
| `TypeGuard` | 3.10 | 사용자 정의 타입 가드 (if만 좁히기) |
| `ParamSpec` | 3.10 | 데코레이터 매개변수 타입 보존 |
| `TypeVarTuple` | 3.11 | 가변 길이 제네릭 |
| `type` 문 | 3.12 | 지연 평가 타입 앨리어스 |
| `def f[T]()` | 3.12 | 간결한 제네릭 문법 |
| `@override` | 3.12 | 오버라이드 안전성 검증 |
| `TypeIs` | 3.13 | 양방향 타입 좁히기 |
| `@deprecated` | 3.13 | 지원 중단 표시 |
| TypeVar 기본값 | 3.13 | 제네릭 타입 기본값 |
| 어노테이션 지연 평가 | 3.14 | 전방 참조 자연스러운 지원 |
