# 도구: Ruff, mypy, pyright, 프로파일링

Python 개발 도구 체인의 설정과 활용법을 정리한다.

---

## Ruff: 통합 린터/포매터

Rust로 작성된 초고속 린터/포매터. Flake8, Black, isort 등을 대체한다.
기존 도구 대비 10-100배 빠르다.

### 권장 pyproject.toml 설정

```toml
[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = [
    "F",     # Pyflakes: 미사용 import, 정의되지 않은 이름
    "E",     # pycodestyle 에러
    "W",     # pycodestyle 경고
    "I",     # isort: import 정렬
    "UP",    # pyupgrade: 최신 Python 문법으로 업그레이드
    "B",     # flake8-bugbear: 흔한 버그 패턴
    "SIM",   # flake8-simplify: 코드 단순화
    "C4",    # flake8-comprehensions: 컴프리헨션 개선
    "RET",   # flake8-return: 반환문 개선
    "PTH",   # flake8-use-pathlib: os.path -> pathlib
    "RUF",   # Ruff 자체 규칙
]

ignore = [
    "E501",   # line-too-long (포매터가 처리)
    "ISC001", # implicit-string-concatenation (포매터와 충돌)
]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]       # 테스트에서 assert 허용
"__init__.py" = ["F401"]   # __init__에서 미사용 import 허용

[tool.ruff.lint.isort]
known-first-party = ["my_project"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### 핵심 규칙 카테고리

```python
# UP (pyupgrade): 구버전 패턴을 최신 문법으로 자동 변환
# 나쁜 예 (UP006): typing.List 사용
from typing import List, Dict
def f(x: List[int]) -> Dict[str, int]: ...

# 좋은 예: 내장 타입 사용 (3.9+)
def f(x: list[int]) -> dict[str, int]: ...

# 나쁜 예 (UP007): Union 대신 | 사용 가능
from typing import Union
x: Union[int, str]

# 좋은 예: X | Y 문법 (3.10+)
x: int | str

# B (bugbear): 미묘한 버그 감지
def bad(items: list[int] = []):  # B006: 가변 디폴트 인자!
    ...

for x in range(10):  # B007: x 미사용 -> for _ in range(10)
    do_something()

# SIM (simplify): 불필요한 복잡성 제거
# SIM102: 중첩 if -> if a and b:
# SIM108: if-else -> 삼항 표현식
```

---

## mypy strict 모드

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.12"
strict = true

# strict는 아래를 모두 활성화:
# warn_return_any, disallow_any_generics,
# disallow_untyped_calls, disallow_untyped_defs,
# disallow_incomplete_defs, check_untyped_defs,
# no_implicit_optional, warn_redundant_casts,
# warn_unused_ignores, no_implicit_reexport

# 점진적 도입: 모듈별 설정
[[tool.mypy.overrides]]
module = "legacy_code.*"
ignore_errors = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

---

## pyright strict 모드

```json
{
    "pythonVersion": "3.12",
    "typeCheckingMode": "strict",
    "reportMissingTypeStubs": "warning",
    "reportUnusedImport": "error",
    "reportUnusedVariable": "warning"
}
```

---

## 프로파일링 도구 계층

### 1단계: cProfile로 함수 수준 병목 식별

```python
import cProfile
cProfile.run('main()', 'output.prof')
# python -m cProfile -o output.prof my_script.py
```

### 2단계: line_profiler로 라인 수준 분석

```python
# pip install line_profiler
@profile
def expensive_function(data):
    result = []                          # 0.1ms
    for item in data:                    # 0.2ms
        processed = complex_calc(item)   # 850ms  <-- 병목!
        result.append(processed)         # 0.3ms
    return result
# kernprof -l -v my_script.py
```

### 3단계: memory_profiler로 메모리 사용량 분석

```python
from memory_profiler import profile as mem_profile

@mem_profile
def memory_heavy():
    a = [1] * (10 ** 6)        # +7.6 MiB
    b = [2] * (2 * 10 ** 7)    # +152.6 MiB
    del b                       # -152.6 MiB
    return a
```

---

## 성능 최적화 전략

```python
# 전략 1: 올바른 자료구조 선택
large_list = list(range(1_000_000))
999_999 in large_list  # ~14ms (O(n))

large_set = set(range(1_000_000))
999_999 in large_set   # ~0.05ms (O(1))

# 전략 2: 불필요한 객체 생성 회피
# 나쁜 예: 문자열 반복 연결 O(n^2)
result = ""
for chunk in chunks:
    result += chunk

# 좋은 예: join 사용 O(n)
result = "".join(chunks)

# 전략 3: 로컬 변수 활용 (글로벌보다 빠름)
def fast():
    sqrt = math.sqrt  # 로컬 변수로 한번 바인딩
    return [sqrt(i) for i in range(10000)]

# 전략 4: __slots__ 사용 (대량 객체)
class Point:
    __slots__ = ('x', 'y')
    def __init__(self, x, y):
        self.x = x
        self.y = y
# __dict__ 대비 ~40-50% 메모리 절약
```

---

## Python 3.11 성능 개선

3.10 대비 평균 25%, 최대 60% 빠르다. 핵심: **특화 적응 인터프리터(PEP 659)**.

```python
# 타입을 일관되게 유지하라
# 나쁜 예: 혼합 타입 리스트 (특화 불가)
mixed = [1, 2.0, 3, 4.0]

# 좋은 예: 단일 타입 리스트 (특화 가능)
ints = [1, 2, 3, 4]
```

---

## JIT 컴파일러 (Python 3.13+)

```python
# Python 3.13의 실험적 JIT (copy-and-patch 방식)
# --enable-experimental-jit 빌드 옵션으로 활성화
# 현재 성능 향상은 미미하지만 향후 개선 예정

# 외부 JIT 대안: Numba (수치 계산 특화)
from numba import jit

@jit(nopython=True)
def monte_carlo_pi(n: int) -> float:
    count = 0
    for _ in range(n):
        x, y = random.random(), random.random()
        if x * x + y * y <= 1.0:
            count += 1
    return 4.0 * count / n
# 순수 Python 대비 10-100배 빠름
```
