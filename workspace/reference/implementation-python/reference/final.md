# Python 언어 특화 가이드

## P1 Source Sufficiency

| field | value |
|---|---|
| purpose | Python implementation quality decisions: typing, protocols, dataclasses, enums, context managers, exceptions, decorators, async/concurrency choices, pydantic boundaries, and Python-version gates. |
| use when | Python language semantics, type hints, runtime validation boundary, or idiomatic implementation details are the main concern. |
| exclude/handoff | Do not use as the source for domain modeling, REST contracts, DB consistency, Django framework behavior, or pytest/TDD methodology except for Python mechanics. |
| core criteria | Prefer official Python docs and PEPs for language behavior; make types and side effects explicit; use modern features only within project version gates; use pydantic/runtime validation at boundaries rather than as domain truth. |
| source priority | 1 Python official docs, PEPs, typing spec, and tool official docs; 2 primary project docs for pydantic/Ruff/mypy/pyright; 3 reputable Python books and articles; 4 unsupported memory is not accepted. |
| P1 classification | sufficient |

> Python에서만 적용되는 관례, 패턴, 기법을 정리한 문서.
> 클린코드 범용 원칙(네이밍, 함수 설계, SOLID 등)은 `workspace/reference/discipline-cleancode/reference/final.md`에서 다룬다.
> Python 3.10+ 이후 도입된 기능을 적극 채택하며, 최신 패턴을 기본으로 제시한다.

---

## 1. 타입 힌트와 타입 시스템

### 1.1 타입 어노테이션 기본 [단단한 파이썬] [파이썬코딩의기술]

타입 어노테이션은 변수에 요구되는 타입을 알려주는 추가 구문이며, 런타임에 실제로 사용되지는 않는다. 목적은 코드를 읽는 사람과 타입 체커에게 타입 정보를 전달하는 것이다.

```python
# 나쁜 예: 타입 정보 없음
def close_kitchen(point_in_time):
    if point_in_time >= closing_time():
        close_kitchen()

# 좋은 예: 타입 어노테이션으로 의도 전달
def close_kitchen(point_in_time: datetime) -> None:
    if point_in_time >= closing_time():
        close_kitchen()
```

- 파이썬은 동적이면서 타입 제약이 강한(strongly typed) 언어다. 묵시적 형 변환이 거의 없다.
- 타입 어노테이션을 사용하면 점진적 타입 지정(gradual typing)이 가능하다.
- 타입 체커: mypy, pyright, pyre, pytype

### 1.2 Optional과 None 처리 [단단한 파이썬]

None은 모든 변수에 할당될 수 있어서 "10억 달러짜리 실수"라 불린다. Optional 타입으로 None의 존재를 명시하라.

```python
# 나쁜 예: None 반환 가능성이 시그니처에 안 보임
def find_user(user_id: int) -> User:
    ...  # None을 반환할 수도 있음

# 좋은 예: Optional로 None 가능성 명시
from typing import Optional

def find_user(user_id: int) -> Optional[User]:
    ...  # None 또는 User 반환

# 호출 측에서 반드시 None 체크 필요
user = find_user(42)
if user is not None:
    user.activate()
```

- `Optional[X]`는 `Union[X, None]`과 동등하다. Python 3.10+에서는 `X | None`을 사용할 수 있다.
- mypy `--strict-optional` 옵션으로 None 처리를 강제하라.

### 1.3 Union과 합 타입으로 상태 공간 제어 [단단한 파이썬]

곱 타입(Product Type)은 모든 필드 조합을 허용하여 유효하지 않은 상태가 생긴다. 합 타입(Sum Type)을 사용해 비정상 상태를 배제하라.

```python
# 나쁜 예: 곱 타입 - 유효하지 않은 조합 가능
@dataclass
class Snack:
    name: str
    condiments: set[str]
    error_code: int       # 성공 시에도 존재
    dispensed_of: bool     # 성공 시에도 존재

# 좋은 예: 합 타입 - 비정상 상태 배제
@dataclass
class Snack:
    name: str
    condiments: set[str]

@dataclass
class Error:
    error_code: int
    dispensed_of: bool

result: Snack | Error = Snack("Hotdog", {"mustard"})  # 3.10+ 문법
```

### 1.4 Literal, Final, NewType [단단한 파이썬]

```python
from typing import Literal, Final, NewType

# Literal: 값의 종류 제한 (3.8+)
@dataclass
class Error:
    error_code: Literal[1, 2, 4, 5]

# Final: 불변 상수 (3.8+)
VENDOR_NAME: Final = "Viafore's Auto-Dog"

# NewType: 타입 안전한 별도 타입 생성
UserId = NewType("UserId", int)
def get_user(user_id: UserId) -> str: ...
get_user(UserId(42))  # OK
get_user(42)           # 타입 체커 에러
```

### 1.5 TypedDict: 이종 딕셔너리 타입 지정 [단단한 파이썬]

외부 API, JSON 등 이종 데이터를 담는 딕셔너리에는 TypedDict를 사용하라.

```python
# 나쁜 예: 구조 알 수 없음
data = get_nutrition_from_api(name)
print(data['fat']['value'])  # 키가 뭐가 있는지 모름

# 좋은 예: TypedDict로 구조 명시
class NutritionInfo(TypedDict):
    value: int
    unit: str

class RecipeNutrition(TypedDict):
    calories: NutritionInfo
    fat: NutritionInfo
```

### 1.6 제네릭과 TypeVar [단단한 파이썬] [PEP 695]

```python
# 3.11 이전 (레거시 참고)
from typing import TypeVar, Generic
T = TypeVar('T')
def reverse(coll: list[T]) -> list[T]:
    return coll[::-1]

# 3.12+ 새 문법 (PEP 695) — 권장
def reverse[T](coll: list[T]) -> list[T]:
    return coll[::-1]

type Point = tuple[float, float]           # 타입 알리아스
type Point[T] = tuple[T, T]               # 제네릭 알리아스
```

### 1.7 PEP 695: 새 타입 매개변수 문법 (Python 3.12+) [PEP 695]

TypeVar를 전역 스코프에 선언해야 하는 번거로움과 공변/반공변의 복잡성을 제거한다.

```python
# === Python 3.11 이전: 장황한 문법 (레거시 참고) ===
from typing import TypeVar, Generic
T = TypeVar('T')
S = TypeVar('S', bound=str)    # 상한 제약
N = TypeVar('N', int, float)   # 값 제약

class Container(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value
    def get(self) -> T:
        return self.value

# === Python 3.12+: 간결한 새 문법 — 권장 ===
class Container[T]:
    def __init__(self, value: T) -> None:
        self.value = value
    def get(self) -> T:
        return self.value

# 상한 제약 (bound)
def longest[S: str](a: S, b: S) -> S:
    return a if len(a) >= len(b) else b

# 값 제약 (constrained)
def add[N: (int, float)](a: N, b: N) -> N:
    return a + b

# type 문으로 타입 앨리어스 선언 (지연 평가)
type Vector[T] = list[T]
type Matrix[T] = list[Vector[T]]
type RecursiveList[T] = T | list['RecursiveList[T]']  # 순환 참조 가능
```

### 1.8 컬렉션 타입 어노테이션 [단단한 파이썬]

```python
# 나쁜 예: 컬렉션 내부 타입 불명
def process(items: list) -> dict: ...

# 좋은 예: 컬렉션 내부 타입 명시 (3.9+ 내장 타입 사용)
AuthorCount = dict[str, int]
def process(items: list[Cookbook]) -> AuthorCount: ...
```

### 1.9 @override 데코레이터 (3.12+) [PEP 698]

```python
from typing import override

class Base:
    @property
    def name(self) -> str:
        return "base"

    @staticmethod
    def create() -> 'Base':
        return Base()

    @classmethod
    def from_config(cls, config: dict) -> 'Base':
        return cls()

    def get_color(self) -> str:
        return "blue"

class Child(Base):
    # @property에도 적용 가능
    @property
    @override
    def name(self) -> str:
        return "child"

    # @staticmethod에도 적용 가능
    @staticmethod
    @override
    def create() -> 'Child':
        return Child()

    # @classmethod에도 적용 가능
    @classmethod
    @override
    def from_config(cls, config: dict) -> 'Child':
        return cls()

    @override
    def get_color(self) -> str:
        return "yellow"

    # 타입 체커 에러: 부모에 없는 메서드를 override로 표시
    @override
    def nonexistent(self) -> None:  # Error!
        pass
```

### 1.10 ParamSpec: 데코레이터 시그니처 보존 [PEP 612]

기존 `Callable`로는 데코레이터가 감싼 함수의 매개변수 타입을 전달할 수 없었다. `ParamSpec`은 이 문제를 해결한다.

```python
from typing import Callable, ParamSpec, TypeVar
from functools import wraps
import time

P = ParamSpec('P')
R = TypeVar('R')

# 나쁜 예: 매개변수 타입 정보 손실
def timer_bad(func: Callable[..., R]) -> Callable[..., R]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> R:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__}: {time.perf_counter() - start:.4f}s")
        return result
    return wrapper

# 좋은 예: ParamSpec으로 시그니처 완전 보존
def timer(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__}: {time.perf_counter() - start:.4f}s")
        return result
    return wrapper

@timer
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"

# 타입 체커가 greet(name: str, greeting: str = "Hello") -> str 시그니처를 정확히 인식
```

### 1.11 Concatenate: 매개변수 추가/제거 [PEP 612]

`Concatenate`는 데코레이터가 원래 함수에 매개변수를 추가하거나 제거할 때 사용한다.

```python
from typing import Callable, Concatenate, ParamSpec, TypeVar

P = ParamSpec('P')
R = TypeVar('R')

class Request:
    user: str

# 첫 번째 인자로 Request를 추가하는 데코레이터
def with_request(
    func: Callable[P, R]
) -> Callable[Concatenate[Request, P], R]:
    def wrapper(request: Request, *args: P.args, **kwargs: P.kwargs) -> R:
        print(f"User: {request.user}")
        return func(*args, **kwargs)
    return wrapper

@with_request
def get_data(query: str) -> list[str]:
    return [query]

# get_data의 시그니처: (request: Request, query: str) -> list[str]
```

### 1.12 TypeIs vs TypeGuard: 타입 좁히기 [PEP 742, PEP 647]

`TypeIs`(3.13+)는 `TypeGuard`(3.10+)의 개선판으로, if/else 양쪽 분기 모두에서 타입 좁히기가 가능하다.

```python
from typing import TypeGuard, TypeIs

# TypeGuard (3.10+): if 분기에서만 좁히기 (else는 원래 타입 유지)
def is_str_list_guard(val: list[int | str]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)

# TypeIs (3.13+): if/else 양쪽 모두 좁히기 — 권장
def is_str_list(val: list[int | str]) -> TypeIs[list[str]]:
    return all(isinstance(x, str) for x in val)

def process(data: list[int | str]) -> None:
    if is_str_list(data):
        # TypeIs: data는 list[str]로 좁혀짐
        print(data[0].upper())
    else:
        # TypeIs: data는 list[int]로 좁혀짐 (TypeGuard는 여기서 좁히지 못함)
        print(data[0] + 1)
```

**권장**: 대부분의 경우 `TypeIs`를 사용하라. `TypeGuard`는 입력 타입과 출력 타입이 호환되지 않는 특수한 경우에만 사용한다.

### 1.13 TypeVarTuple과 Unpack: 가변 길이 제네릭 [PEP 646]

NumPy 같은 다차원 배열의 형상(shape)을 타입으로 표현할 수 있게 한다.

```python
from typing import TypeVarTuple, Unpack

# 3.12+ 새 문법
def broadcast[*Ts](*arrays: *tuple[*Ts]) -> None: ...

# 실용 예: 다차원 배열 형상 안전성
class Array[*Shape]:
    def __init__(self, data: list) -> None:
        self.data = data

    def reshape[*NewShape](self, *shape: *NewShape) -> 'Array[*NewShape]': ...

# 컴파일 타임에 형상 불일치 감지
a: Array[int, int, int] = Array([[[1, 2], [3, 4]]])  # 3D
```

### 1.14 타입 매개변수 기본값 (Python 3.13+) [PEP 696]

```python
# Python 3.13+: TypeVar에 기본값 지정
class Container[T = str]:
    def __init__(self, value: T) -> None:
        self.value = value

# T를 명시하지 않으면 str로 추론
c = Container("hello")  # Container[str]
c2 = Container[int](42)  # Container[int]
```

---

## 2. 구조적 패턴 매칭 (match/case) -- Python 3.10+

> 출처: [PEP 634](https://peps.python.org/pep-0634/) (명세), [PEP 635](https://peps.python.org/pep-0635/) (동기), [PEP 636](https://peps.python.org/pep-0636/) (튜토리얼)

### 2.1 패턴 매칭의 7가지 패턴 유형

`match/case`는 단순 switch문이 아니라 **구조적 분해(destructuring)**를 핵심으로 하는 제어 흐름이다. 중첩 패턴과 가드를 조합하면 복잡한 데이터 구조를 선언적으로 다룰 수 있다.

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

def describe(obj):
    match obj:
        # 1. 리터럴 패턴: 정확한 값 매칭
        case 0:
            return "영"

        # 2. OR 패턴: | 로 여러 패턴 결합
        case 401 | 403 | 404:
            return "HTTP 에러"

        # 3. 캡처 패턴: 변수에 값 바인딩
        case int(n) if n < 0:      # 가드와 결합
            return f"음수: {n}"

        # 4. 시퀀스 패턴: 리스트/튜플 분해 + 별표 캡처
        case [first, *rest]:
            return f"첫 번째: {first}, 나머지 {len(rest)}개"

        # 5. 매핑 패턴: 딕셔너리 키-값 매칭
        case {"action": "move", "direction": d}:
            return f"이동: {d}"

        # 6. 클래스 패턴: 타입 + 속성 분해
        case Point(x=0, y=y_val):
            return f"Y축 위: y={y_val}"

        # 7. 와일드카드: 모든 것에 매칭
        case _:
            return "알 수 없음"
```

### 2.2 클래스 패턴과 \_\_match\_args\_\_

`__match_args__`를 정의하면 위치 인자로 클래스 패턴을 사용할 수 있다. `dataclass`는 자동으로 이를 생성한다.

```python
# 나쁜 예: isinstance 체인
def process(cmd):
    if isinstance(cmd, MoveCommand):
        if cmd.direction == "north":
            ...
    elif isinstance(cmd, QuitCommand):
        ...

# 좋은 예: match/case로 선언적 분기
def process(cmd):
    match cmd:
        case MoveCommand(direction="north", steps=n):
            move_north(n)
        case MoveCommand(direction=d, steps=n) if n > 10:
            print(f"너무 먼 거리: {d} {n}칸")
        case QuitCommand():
            sys.exit(0)
```

### 2.3 매핑 패턴과 REST 캡처

매핑 패턴은 딕셔너리에서 필요한 키만 추출하며, 나머지 키는 무시된다. `**rest`로 나머지를 명시적으로 캡처할 수 있다.

```python
def handle_config(config: dict):
    match config:
        case {"database": {"host": host, "port": int(port)}, **rest}:
            print(f"DB: {host}:{port}, 추가 설정: {rest.keys()}")
        case {"database": {"host": host}}:
            print(f"DB: {host}, 기본 포트 사용")
```

### 2.4 패턴 매칭 실전 활용: 상태 머신

```python
# Fluent Python 2nd에서 권장하는 패턴: 데이터 클래스 + match/case로 명령 처리
@dataclass
class Event:
    kind: str
    payload: dict

def handle_event(event: Event, state: str) -> str:
    match (state, event):
        case ("idle", Event(kind="start", payload={"task": task})):
            print(f"작업 시작: {task}")
            return "running"
        case ("running", Event(kind="complete")):
            return "idle"
        case ("running", Event(kind="error", payload={"code": code})):
            print(f"에러 코드: {code}")
            return "failed"
        case (_, Event(kind="reset")):
            return "idle"
        case _:
            raise ValueError(f"예기치 않은 상태 전이: {state}")
```

---

## 3. 컬렉션 선택과 데이터 구조

### 3.1 목적에 맞는 컬렉션 선택 [단단한 파이썬]

| 컬렉션 | 특성 | 용도 |
|--------|------|------|
| `list` | 변경 가능, 순서 있음, 중복 허용 | 반복, 동적 인덱싱 |
| `tuple` | 불변, 순서 있음 | 고정 크기 데이터, 정적 인덱싱 |
| `set` | 변경 가능, 순서 없음, 중복 불가 | 멤버십 테스트, 중복 제거 |
| `dict` | 키-값 매핑, 삽입 순서 보존 (3.7+) | 키 기반 조회 |
| `deque` | 양방향 큐, O(1) 양쪽 삽입/삭제 | FIFO 큐, 생산자-소비자 |
| `defaultdict` | 키 없을 때 기본값 자동 생성 | 그룹핑, 카운팅 |
| `frozenset` | 불변 세트 | 딕셔너리 키, 해시 가능한 세트 |
| `Counter` | 요소 카운팅 특화 딕셔너리 | 빈도 분석 |

### 3.2 딕셔너리 키 접근: get과 defaultdict [파이썬코딩의기술]

```python
# 나쁜 예: KeyError 처리 or in 검사
if key in votes:
    names = votes[key]
else:
    votes[key] = names = []
names.append(who)

# 좋은 예: get + 왈러스
if (names := votes.get(key)) is None:
    votes[key] = names = []
names.append(who)

# 더 좋은 예: defaultdict (내부 상태 관리 시)
from collections import defaultdict
votes = defaultdict(list)
votes[key].append(who)
```

### 3.3 __missing__으로 키별 디폴트 값 생성 [파이썬코딩의기술]

defaultdict의 팩토리 함수는 인자를 받을 수 없다. 키에 따라 다른 디폴트 값이 필요하면 dict를 상속하고 `__missing__`을 구현하라.

```python
class Pictures(dict):
    def __missing__(self, key):
        value = open_picture(key)
        self[key] = value
        return value

pictures = Pictures()
handle = pictures[path]  # 없으면 __missing__ 호출
```

### 3.4 정렬: key 파라미터와 튜플 비교 [파이썬코딩의기술]

```python
# 단일 기준
tools.sort(key=lambda x: x.name)

# 다중 기준: 튜플 사용, -로 내림차순 (숫자만)
power_tools.sort(key=lambda x: (-x.weight, x.name))
```

### 3.5 성능 특화 자료구조 [파이썬코딩의기술]

```python
from collections import deque
from bisect import bisect_left
from heapq import heappush, heappop

# deque: 양방향 O(1) - FIFO 큐에 list 대신 사용
queue = deque()
queue.append(item)       # 오른쪽 삽입
queue.popleft()          # 왼쪽 제거 (list.pop(0)은 O(n))

# bisect: 정렬된 시퀀스에서 이진 검색
index = bisect_left(sorted_data, target)

# heapq: 우선순위 큐 - O(log n) 삽입/삭제
heap = []
heappush(heap, (priority, item))
_, item = heappop(heap)
```

---

## 4. 함수 설계: Python 특화 기법

### 4.1 가변 디폴트 인자의 함정: None 사용 [파이썬코딩의기술]

디폴트 인자는 함수 정의 시 단 한 번만 평가된다. 가변 객체를 디폴트로 쓰면 호출 간에 공유된다.

```python
# 나쁜 예: 가변 디폴트 인자
def append_to(element, target=[]):
    target.append(element)
    return target

def log(message, when=datetime.now()):  # 정의 시점의 시간 고정
    print(f'{when}: {message}')

# 좋은 예: None + 독스트링
def append_to(element, target=None):
    """target의 디폴트 값은 빈 리스트이다."""
    if target is None:
        target = []
    target.append(element)
    return target
```

### 4.2 위치 전용(/), 키워드 전용(*) 인자 [파이썬코딩의기술]

```python
# / 왼쪽: 위치 전용, * 오른쪽: 키워드 전용
def safe_division(numerator, denominator, /, *,
                  ignore_overflow=False,
                  ignore_zero_division=False):
    ...

safe_division(2, 5)                          # OK
safe_division(2, 5, ignore_overflow=True)     # OK
safe_division(numerator=2, denominator=5)     # 에러: 위치 전용
safe_division(2, 5, True)                     # 에러: 키워드 전용
```

### 4.3 왈러스 연산자(:=)로 반복 제거 [파이썬코딩의기술]

```python
# 나쁜 예: 변수 할당과 조건 분리
count = fresh_fruit.get('leamon', 0)
if count:
    make_lemonade(count)

# 좋은 예: 대입식으로 통합 (3.8+)
if count := fresh_fruit.get('leamon', 0):
    make_lemonade(count)

# 컴프리헨션 안에서도 사용
found = {
    name: batches
    for name in order
    if (batches := get_batches(stock.get(name, 0), 8))
}
```

### 4.4 None 반환 대신 예외 발생 [파이썬코딩의기술]

```python
# 나쁜 예: None 반환 - 0과 구분 불가
def careful_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None

# 좋은 예: 예외 발생 + 타입 힌트
def careful_divide(a: float, b: float) -> float:
    """Raises: ValueError: b가 0일 때"""
    try:
        return a / b
    except ZeroDivisionError:
        raise ValueError('잘못된 입력')
```

### 4.5 언패킹 활용 [파이썬코딩의기술]

```python
# 인덱스 대신 언패킹
first, second = item

# 스왑
a[i-1], a[i] = a[i], a[i-1]

# 별표 식(starred expression)
oldest, second, *others = sorted_ages

# 반환값 4개 이상이면 클래스/namedtuple 사용
# 나쁜 예
min, max, avg, med, cnt = get_stats(lengths)
# 좋은 예
stats = get_stats(lengths)  # Stats 객체 반환
```

---

## 5. 데코레이터

### 5.1 functools.wraps 필수 사용 [파이썬코딩의기술] [슬기로운 파이썬 트릭]

데코레이터를 적용하면 원래 함수의 메타데이터(이름, 독스트링)가 사라진다. `@wraps`로 보존하라.

```python
from functools import wraps

# 나쁜 예: 메타데이터 손실
def trace(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result
    return wrapper

# 좋은 예: @wraps로 메타데이터 보존
def trace(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result
    return wrapper
```

### 5.2 데코레이터에 인자 전달 [파이썬 클린코드 2nd]

```python
# 방법 1: 3단 중첩 함수
def with_retry(retries_limit=3, allowed_exceptions=None):
    allowed_exceptions = allowed_exceptions or (Exception,)
    def retry(operation):
        @wraps(operation)
        def wrapped(*args, **kwargs):
            last_raised = None
            for _ in range(retries_limit):
                try:
                    return operation(*args, **kwargs)
                except allowed_exceptions as e:
                    last_raised = e
            raise last_raised
        return wrapped
    return retry

@with_retry(retries_limit=5)
def run_operation(): ...

# 방법 2: 클래스 데코레이터 (가독성 더 좋음)
class Serialization:
    def __init__(self, **transformations):
        self.serializer = EventSerializer(transformations)
    def __call__(self, event_class):
        def serialize_method(event_instance):
            return self.serializer.serialize(event_instance)
        event_class.serialize = serialize_method
        return event_class

@Serialization(username=show_original, password=hide_field)
@dataclass
class LoginEvent: ...
```

### 5.3 클래스 데코레이터: 메타클래스 대안 [파이썬코딩의기술]

합성 가능한 클래스 확장이 필요하면 메타클래스보다 클래스 데코레이터를 사용하라.

```python
def trace(kclass):
    for key in dir(kclass):
        value = getattr(kclass, key)
        if isinstance(value, trace_types):
            setattr(kclass, key, trace_func(value))
    return kclass

@trace
class TraceDict(dict):
    ...
```

---

## 6. 디스크립터

### 6.1 디스크립터 프로토콜 [파이썬코딩의기술] [파이썬 클린코드 2nd]

디스크립터는 `__get__`, `__set__`, `__delete__`, `__set_name__` 중 하나 이상을 구현한 클래스이다. `@property`의 일반화이며, 재사용 가능한 애트리뷰트 로직에 사용한다.

### 6.2 디스크립터 검증 프레임워크: ABC 기반 패턴 [Python 공식 Descriptor HowTo Guide]

> **의사결정 #5**: External 채택. Python 공식 Descriptor HowTo Guide 패턴을 기본으로 사용한다.
> `instance.__dict__` 직접 저장이 더 단순하고 공식 가이드의 권장 패턴이다. `WeakKeyDictionary`는 `__set_name__` 이전 시대의 우회 방법이다.

```python
from abc import ABC, abstractmethod

class Validator(ABC):
    """Descriptor HowTo Guide 스타일: 재사용 가능한 검증 디스크립터 기반 클래스"""
    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        self.validate(value)
        setattr(obj, self.private_name, value)

    @abstractmethod
    def validate(self, value): ...

class String(Validator):
    def __init__(self, minsize=0, maxsize=None):
        self.minsize = minsize
        self.maxsize = maxsize

    def validate(self, value):
        if not isinstance(value, str):
            raise TypeError(f"str 타입이 필요합니다: {value!r}")
        if len(value) < self.minsize:
            raise ValueError(f"최소 {self.minsize}자 이상 필요합니다")
        if self.maxsize is not None and len(value) > self.maxsize:
            raise ValueError(f"최대 {self.maxsize}자까지 허용됩니다")

class Number(Validator):
    def __init__(self, minvalue=None, maxvalue=None):
        self.minvalue = minvalue
        self.maxvalue = maxvalue

    def validate(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"숫자 타입이 필요합니다: {value!r}")
        if self.minvalue is not None and value < self.minvalue:
            raise ValueError(f"최솟값 {self.minvalue} 이상이어야 합니다")
        if self.maxvalue is not None and value > self.maxvalue:
            raise ValueError(f"최댓값 {self.maxvalue} 이하여야 합니다")

class OneOf(Validator):
    def __init__(self, *options):
        self.options = set(options)

    def validate(self, value):
        if value not in self.options:
            raise ValueError(f"{self.options} 중 하나여야 합니다: {value!r}")

# 선언적 사용
class Employee:
    name = String(minsize=2, maxsize=30)
    age = Number(minvalue=18, maxvalue=99)
    department = OneOf("engineering", "design", "product")

emp = Employee()
emp.name = "Kim"           # OK
emp.age = 25               # OK
emp.department = "engineering"  # OK
# emp.name = ""            # ValueError
# emp.age = 15             # ValueError
```

> **레거시 참고**: 과거 `WeakKeyDictionary`를 사용한 디스크립터 패턴도 존재하지만, `__set_name__`(3.6+)이 도입된 이후로는 `instance.__dict__`에 직접 저장하는 공식 패턴이 권장된다.

---

## 7. @property와 애트리뷰트 접근

### 7.1 세터/게터 대신 평범한 애트리뷰트 [파이썬코딩의기술]

파이썬에서 명시적 세터/게터는 파이썬답지 않다. 단순 공개 애트리뷰트로 시작하고, 나중에 로직이 필요하면 `@property`로 전환하라.

```python
# 나쁜 예: 자바 스타일 getter/setter
class OldStyle:
    def __init__(self):
        self._voltage = 0
    def get_voltage(self):
        return self._voltage
    def set_voltage(self, value):
        self._voltage = value

# 좋은 예: @property
class VoltageResistance:
    def __init__(self, ohms):
        self._voltage = 0
        self.ohms = ohms

    @property
    def voltage(self):
        return self._voltage

    @voltage.setter
    def voltage(self, voltage):
        self._voltage = voltage
        self.current = self._voltage / self.ohms
```

### 7.2 __getattr__과 __getattribute__ [파이썬코딩의기술]

- `__getattr__`: 인스턴스 딕셔너리에 없는 애트리뷰트 접근 시에만 호출 (지연 로딩)
- `__getattribute__`: 모든 애트리뷰트 접근마다 호출 (프록시, 검증)

```python
class LazyRecord:
    def __init__(self):
        self.exists = 5

    def __getattr__(self, name):
        value = f'{name}을 위한 값'
        setattr(self, name, value)  # 다음부터는 __getattr__ 미호출
        return value

data = LazyRecord()
data.exists  # 5 (__getattr__ 미호출)
data.foo     # 'foo을 위한 값' (__getattr__ 호출, 이후 캐시)
```

---

## 8. 클래스 설계: Python 특화 패턴

### 8.1 __call__로 호출 가능한 객체 [파이썬코딩의기술]

상태를 유지하는 훅이 필요하면 클로저 대신 `__call__`을 구현한 클래스를 사용하라.

```python
class BetterCountMissing:
    def __init__(self):
        self.added = 0

    def __call__(self):
        self.added += 1
        return 0

counter = BetterCountMissing()
result = defaultdict(counter, current)  # 함수 자리에 사용 가능
```

### 8.2 @classmethod를 팩토리 메서드로 활용 [파이썬코딩의기술] [슬기로운 파이썬 트릭]

파이썬은 `__init__` 하나만 허용한다. 대체 생성자가 필요하면 `@classmethod`를 사용하라.

```python
class Pizza:
    def __init__(self, ingredients):
        self.ingredients = ingredients

    @classmethod
    def margherita(cls):
        return cls(['mozzarella', 'tomatoes'])

    @classmethod
    def prosciutto(cls):
        return cls(['mozzarella', 'tomatoes', 'ham'])

pizza = Pizza.margherita()  # 대체 생성자
```

### 8.3 인스턴스 메서드 vs 클래스 메서드 vs 정적 메서드 [슬기로운 파이썬 트릭]

```python
class MyClass:
    def method(self):            # 인스턴스 메서드: self로 객체 상태 접근
        ...

    @classmethod
    def classmethod(cls):        # 클래스 메서드: cls로 클래스 상태 접근
        ...                      # 팩토리 메서드에 적합

    @staticmethod
    def staticmethod():          # 정적 메서드: 상태 접근 불가
        ...                      # 독립적 유틸리티, 테스트 용이
```

### 8.4 __repr__과 __str__ [슬기로운 파이썬 트릭] [파이썬코딩의기술]

모든 클래스에 최소한 `__repr__`은 구현하라. `__str__`이 없으면 `__repr__`이 대신 사용된다.

```python
class Car:
    def __init__(self, color, mileage):
        self.color = color
        self.mileage = mileage

    def __repr__(self):
        return f'{self.__class__.__name__}({self.color!r}, {self.mileage!r})'

    def __str__(self):
        return f'{self.color} 차 ({self.mileage}km)'

car = Car('red', 37281)
print(car)      # __str__: red 차 (37281km)
print(repr(car)) # __repr__: Car('red', 37281)
print([car])     # 컨테이너 내부는 항상 __repr__
```

### 8.5 비공개(__) 대신 보호(_) 애트리뷰트 [파이썬코딩의기술]

```python
# 나쁜 예: 이중 밑줄 남용
class MyClass:
    def __init__(self):
        self.__private = 42  # 네임 맹글링 발생: _MyClass__private

# 좋은 예: 단일 밑줄 관례
class MyClass:
    def __init__(self):
        self._protected = 42  # 관례적 보호 필드
```

- `__var`: 네임 맹글링 발생. 하위 클래스 필드명 충돌 방지에만 사용하라.
- `_var`: 관례적 보호. 외부에서 사용 시 주의하라는 의미.
- 파이썬 모토: "우리는 모두 책임질 줄 아는 성인이다."

### 8.6 __init_subclass__로 하위 클래스 검증 (3.6+) [파이썬코딩의기술]

메타클래스 대신 `__init_subclass__`를 사용하라. 더 단순하고 합성 가능하다.

```python
class BetterPolygon:
    sides = None

    def __init_subclass__(cls):
        super().__init_subclass__()
        if cls.sides < 3:
            raise ValueError('다각형 변은 3개 이상이어야 합니다')

class Hexagon(BetterPolygon):
    sides = 6   # OK

class Line(BetterPolygon):
    sides = 2   # ValueError 발생 (클래스 정의 시점!)
```

### 8.7 __init_subclass__ 고급 활용: 플러그인 레지스트리 [Fluent Python 2nd]

```python
# 메타클래스 없이 플러그인 자동 등록 패턴
class PluginBase:
    _registry: dict[str, type] = {}

    def __init_subclass__(cls, *, plugin_name: str = "", **kwargs):
        super().__init_subclass__(**kwargs)
        name = plugin_name or cls.__name__.lower()
        PluginBase._registry[name] = cls

    @classmethod
    def create(cls, name: str, **kwargs):
        plugin_cls = cls._registry.get(name)
        if plugin_cls is None:
            raise ValueError(f"알 수 없는 플러그인: {name}")
        return plugin_cls(**kwargs)

class JSONPlugin(PluginBase, plugin_name="json"):
    def process(self, data): ...

class XMLPlugin(PluginBase, plugin_name="xml"):
    def process(self, data): ...

# 사용
plugin = PluginBase.create("json")  # JSONPlugin 인스턴스
print(PluginBase._registry)         # {'json': <class JSONPlugin>, 'xml': <class XMLPlugin>}
```

### 8.8 믹스인 클래스 [파이썬코딩의기술]

자체 애트리뷰트 정의 없이 메서드만 제공하는 클래스. `__init__` 호출 불필요.

```python
class ToDictMixin:
    def to_dict(self):
        return self._traverse_dict(self.__dict__)
    ...

class JsonMixin:
    @classmethod
    def from_json(cls, data):
        kwargs = json.loads(data)
        return cls(**kwargs)
    def to_json(self):
        return json.dumps(self.to_dict())

class DatacenterRack(ToDictMixin, JsonMixin):
    ...
```

### 8.9 collections.abc로 커스텀 컨테이너 [파이썬코딩의기술] [단단한 파이썬]

커스텀 컨테이너를 만들 때 `collections.abc`를 상속하면 필수 메서드 누락을 방지한다.

```python
from collections.abc import Sequence

class BadType(Sequence):
    pass  # TypeError: __getitem__, __len__ 미구현

# dict 오버라이딩은 dict 대신 UserDict 사용
from collections import UserDict
class MyDict(UserDict):
    def __getitem__(self, key):
        ...  # 안전하게 오버라이딩 가능
```

---

## 9. Protocol 심화 -- 구조적 서브타이핑의 실전 활용

> 출처: [PEP 544](https://peps.python.org/pep-0544/), [typing 공식 문서](https://typing.python.org/en/latest/reference/protocols.html), [mypy Protocol 문서](https://mypy.readthedocs.io/en/stable/protocols.html)

### 9.1 Protocol 기본 [단단한 파이썬]

덕 타이핑과 타입 체커를 연결하는 핵심 기능. 상속 없이 구조(메서드/속성)만으로 타입을 만족시킨다.

```python
from typing import Protocol

class Splittable(Protocol):
    cost: int
    name: str
    def split_in_half(self) -> tuple['Splittable', 'Splittable']: ...

# BLTSandwich는 Splittable을 상속하지 않지만 구조가 맞으면 통과
class BLTSandwich:
    def __init__(self):
        self.cost = 6
        self.name = 'BLT'
    def split_in_half(self):
        return (BLTSandwich(), BLTSandwich())

def split_dish(dish: Splittable) -> tuple[Splittable, Splittable]:
    return dish.split_in_half()  # BLTSandwich 전달 가능
```

**타입 체크 4단계 (약 -> 강)**:
1. Duck Typing: 런타임에만 검증
2. Goose Typing: ABC + abstractmethod로 상속 강제
3. Static Typing: 타입 힌트 + 타입 체커(mypy)
4. Static Duck Typing: Protocol로 구조적 검증

### 9.2 Protocol 합성과 확장 [PEP 544]

프로토콜끼리 합성하거나 일반 클래스에서 프로토콜을 확장할 수 있다.

```python
from typing import Protocol, runtime_checkable

class Readable(Protocol):
    def read(self, n: int = -1) -> bytes: ...

class Writable(Protocol):
    def write(self, data: bytes) -> int: ...

# 프로토콜 합성: 두 프로토콜을 모두 만족해야 함
class ReadWritable(Readable, Writable, Protocol):
    pass

# 비프로토콜 클래스에서 프로토콜 상속 (명시적 구현)
class SocketStream(Readable):
    """Readable을 명시적으로 구현. 구조적 매칭도 여전히 동작."""
    def read(self, n: int = -1) -> bytes:
        return b""
```

### 9.3 Protocol에 속성과 클래스 변수 정의 [PEP 544]

```python
from typing import Protocol, ClassVar

class Configurable(Protocol):
    # 인스턴스 속성 (읽기 전용)
    @property
    def name(self) -> str: ...

    # 인스턴스 속성 (읽기/쓰기)
    timeout: int

    # 클래스 변수
    max_retries: ClassVar[int]
```

### 9.4 제네릭 Protocol [PEP 544]

```python
from typing import Protocol, TypeVar

T_co = TypeVar('T_co', covariant=True)

class SupportsLessThan(Protocol):
    def __lt__(self, other: 'SupportsLessThan') -> bool: ...

class Comparable(Protocol[T_co]):
    """공변 제네릭 프로토콜: 비교 가능한 타입"""
    def compare(self, other: T_co) -> int: ...

# 3.12+ 문법
class Sortable[T: SupportsLessThan](Protocol):
    def sort(self) -> list[T]: ...
```

### 9.5 @runtime_checkable의 한계 [PEP 544]

```python
@runtime_checkable
class HasClose(Protocol):
    def close(self) -> None: ...

class FakeCloser:
    def close(self, force: bool = False) -> str:
        return "closed"

# 주의: isinstance는 메서드 시그니처를 검사하지 않음
assert isinstance(FakeCloser(), HasClose)  # True! 시그니처 불일치인데도 통과

# 따라서 runtime_checkable은 "이 메서드가 존재하는가"만 확인
# 정확한 타입 검증은 반드시 정적 타입 체커(mypy/pyright)에 의존하라
```

---

## 10. Enum, dataclass, NamedTuple

### 10.1 Enum/StrEnum: 상수 그룹화 [단단한 파이썬] [Python 공식 문서]

```python
from enum import Enum, StrEnum, auto

class Position(Enum):
    CHEF = auto()
    SOUS_CHEF = auto()
    SERVER = auto()

# 비교
position = Position.CHEF
if position == Position.CHEF: ...

# 문자열 Enum (Python 3.11+)
class Color(StrEnum):
    RED = 'red'
    BLUE = 'blue'

# Python 3.10 이하 또는 target 제약이 있으면 str, Enum 조합 사용
class LegacyColor(str, Enum):
    RED = 'red'
    BLUE = 'blue'
```

- 의미 있는 유한 상태는 임의 문자열보다 `Enum` 또는 `StrEnum`으로 표현한다.
- 직렬화 값이 문자열이어야 하고 프로젝트 target이 Python 3.11+이면 `StrEnum`을 우선 고려한다.
- Python target이나 의존성 제약 때문에 `StrEnum`을 사용할 수 없으면 `str, Enum` 조합을 사용한다.
- 값 집합이 작고 지역적인 분기 표현이면 `Literal`도 가능하지만, 상태에 의미나 동작이 붙으면 `Enum`/`StrEnum`이 더 안정적이다.
- 승격 판정(무엇을 Enum으로 만들지)·리터럴 허용 목록·소비 규율의 소유자는 `discipline-cleancode` §2.14다 — 요지: 닫힌 집합을 분기·판정에 쓰면 1곳째부터 집합 단위 타입으로(낱개 모듈 상수 나열 금지), 선언된 값의 비교·분기·대입은 심볼로만(`state == State.ACTIVE`). 비교는 `==`를 쓴다 — `is`는 문자열 Enum 값이 경계에서 plain str로 흐를 때 수화 누락 시 조용한 False를 만든다.
- **파생 분류 집합**(terminal set 등)의 지식은 enum이 소유한다 — 1순위는 프로퍼티(`@property def is_terminal(self) -> bool: ...`), 여러 원소를 묶는 상수가 필요하면 enum과 같은 모듈의 `frozenset`(원소는 심볼). 소비처 모듈마다 임의 frozenset을 재정의하지 않는다.
- `Literal` vs `Enum` 분업(PEP 586): 위의 "지역적 분기 표현이면 `Literal` 가능"은 유지하되, 도메인 개념의 값 집합(상태·종류)은 Enum, 외부 API의 값 의존 계약(`open`의 mode처럼 인자 값에 따라 시그니처가 갈리는 자리)은 `Literal`로 가른다. `Literal`로 잠긴 인자 자리의 리터럴은 타입 체커가 검증하므로 허용이다.

### 10.2 dataclass 기본 [단단한 파이썬]

```python
from dataclasses import dataclass, field

@dataclass
class Dish:
    name: str
    price_in_cents: int
    description: str
    picture: str | None = None
    tags: list[str] = field(default_factory=list)

# 자동 생성: __init__, __repr__, __eq__
```

### 10.3 dataclass(slots=True): 메모리 최적화 (3.10+) [Python dataclasses 공식 문서]

> **의사결정 #7**: External 채택. `dataclass(slots=True)` 사용을 권장한다.

```python
# 나쁜 예: 기본 __dict__ 사용 (인스턴스당 ~200 bytes 오버헤드)
@dataclass
class PointDict:
    x: float
    y: float

# 좋은 예: slots로 메모리 절약 (20-50% 감소)
@dataclass(slots=True)
class PointSlots:
    x: float
    y: float

# 수백만 인스턴스 생성 시 차이가 크다
# PointDict: ~170 bytes/instance vs PointSlots: ~96 bytes/instance
```

**주의**: `slots=True`는 새로운 클래스를 반환한다. 다중 상속 시 `__slots__`가 충돌하면 에러가 발생할 수 있다.

### 10.4 dataclass(frozen=True)와 불변성 계층 [단단한 파이썬] [Python dataclasses 공식 문서]

```python
@dataclass(frozen=True)
class Money:
    amount: int
    currency: str

    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("통화 불일치")
        # frozen이므로 새 객체를 반환해야 함
        return Money(self.amount + other.amount, self.currency)

price = Money(1000, "KRW")
# price.amount = 2000  # FrozenInstanceError
```

### 10.5 dataclass(kw_only=True): 키워드 전용 필드 (3.10+) [Python dataclasses 공식 문서]

```python
@dataclass(kw_only=True)
class Config:
    host: str
    port: int = 8080
    debug: bool = False

# Config("localhost")  # TypeError: 위치 인자 불가
Config(host="localhost")  # OK

# 부분 적용: 특정 필드만 kw_only
from dataclasses import field

@dataclass
class User:
    name: str                                    # 위치 인자 가능
    email: str                                   # 위치 인자 가능
    role: str = field(default="user", kw_only=True)  # 키워드 전용
```

### 10.6 match_args와 패턴 매칭 통합 (3.10+) [Python dataclasses 공식 문서]

```python
@dataclass
class Command:
    action: str
    target: str
    count: int = 1
    # 자동 생성: __match_args__ = ('action', 'target', 'count')

cmd = Command("move", "north", 3)

# match/case에서 위치 인자로 분해 가능
match cmd:
    case Command("move", direction, n) if n > 0:
        print(f"{direction}로 {n}칸 이동")
    case Command("attack", target):
        print(f"{target} 공격")
```

### 10.7 __post_init__과 InitVar 고급 활용 [Python dataclasses 공식 문서]

```python
from dataclasses import dataclass, field, InitVar

@dataclass
class Temperature:
    celsius: float
    fahrenheit: float = field(init=False)  # __init__에서 제외
    scale: InitVar[str] = "C"              # __init__에만 존재, 인스턴스 속성이 아님

    def __post_init__(self, scale: str):
        if scale == "F":
            # 화씨로 입력받은 경우 섭씨로 변환
            self.celsius = (self.celsius - 32) * 5 / 9
        self.fahrenheit = self.celsius * 9 / 5 + 32

t1 = Temperature(100)            # 섭씨 100도
t2 = Temperature(212, scale="F") # 화씨 212도 -> 섭씨 100도
assert t1.celsius == t2.celsius
```

### 10.8 NamedTuple: 불변 레코드 [슬기로운 파이썬 트릭]

```python
# typing 버전 — 권장
from typing import NamedTuple
class Car(NamedTuple):
    color: str
    mileage: float

car = Car('red', 3812)
car.color       # 이름으로 접근
car[0]          # 인덱스로도 접근
car._asdict()   # dict 변환
```

---

## 11. 연산자 오버로딩과 Python 데이터 모델 심화

> 출처: Fluent Python 2nd Edition (Luciano Ramalho, O'Reilly 2022)

### 11.1 연산자 오버로딩 규칙 [Fluent Python 2nd]

```python
import math

class Vector:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    # 1. __add__: 좌항 덧셈. NotImplemented 반환으로 역연산에 위임
    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        return NotImplemented  # 절대 raise하지 말 것!

    # 2. __radd__: 우항 덧셈. other + self 형태일 때 호출
    def __radd__(self, other):
        return self.__add__(other)

    # 3. __iadd__: += 증강 할당
    def __iadd__(self, other):
        return self.__add__(other)

    # 4. __mul__과 __rmul__: 스칼라 곱
    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Vector(self.x * scalar, self.y * scalar)
        return NotImplemented

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    # 5. __matmul__ (@): 행렬 곱/내적 (PEP 465)
    def __matmul__(self, other):
        if isinstance(other, Vector):
            return self.x * other.x + self.y * other.y
        return NotImplemented

    # 6. 비교 연산: __eq__는 대칭적, __lt__는 __gt__의 반영
    def __eq__(self, other):
        if isinstance(other, Vector):
            return self.x == other.x and self.y == other.y
        return NotImplemented

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def __bool__(self):
        return bool(abs(self))

    def __repr__(self):
        return f"Vector({self.x!r}, {self.y!r})"

# 사용 예
v1 = Vector(2, 4)
v2 = Vector(2, 1)
print(v1 + v2)      # Vector(4, 5)     -- __add__
print(3 * v1)        # Vector(6, 12)    -- __rmul__
print(v1 @ v2)       # 8                -- __matmul__ (내적)
```

**핵심 규칙**:
- `NotImplemented`를 반환하라 (raise가 아님). 파이썬이 역연산(`__radd__` 등)을 시도한다
- `__eq__`를 정의하면 `__hash__`는 `None`이 되므로, 해시 가능 객체는 `__hash__`도 정의하라
- `@` 연산자(PEP 465)는 `__matmul__`/`__rmatmul__`/`__imatmul__`로 구현한다

---

## 12. pydantic v2 -- 런타임 검증의 새 표준

> 출처: [pydantic v2 공식 문서](https://docs.pydantic.dev/latest/), [Migration Guide](https://docs.pydantic.dev/latest/migration/)
>
> **의사결정 #1**: External 채택. pydantic v2 API를 사용한다. v1 API는 공식 지원 중단되었다.

### 12.0 pydantic v2 boundary 결정

pydantic v2는 외부 입력과 런타임 검증 경계에서 사용한다. API payload, 외부 JSON, config, settings-like data, message payload처럼 시스템 밖에서 들어오거나 시스템 밖으로 나가는 데이터의 shape와 coercion을 명시하는 데 적합하다.

도메인 모델의 기본 표현을 pydantic으로 고정하지 않는다. durable domain invariant는 value object, entity, aggregate, domain service, application service처럼 해당 규칙을 소유한 경계에 둔다. pydantic validator는 boundary validation과 parsing을 담당하고, 상태 전이, 금액 계산, 권한 정책, 주문/결제 같은 도메인 규칙을 대신 소유하지 않는다.

- `BaseModel`은 외부 DTO, config, 런타임 boundary 검증에 우선 사용한다.
- 내부 domain object가 dataclass, 일반 class, Django model, aggregate로 이미 표현되어 있으면 pydantic 모델을 중복 domain model로 만들지 않는다.
- validation error는 adapter/API/config loading layer에서 domain/application error로 변환한다. raw pydantic error shape가 도메인 규칙의 일부가 되지 않게 한다.
- coercion이 잘못된 입력을 숨기면 strict mode를 켠다. 단, 외부 계약상 문자열 숫자처럼 의도한 coercion을 받는 필드는 field-level로 허용한다.
- Django Ninja Schema가 API serialization boundary를 이미 소유하면 별도 pydantic DTO를 추가하기 전에 `implementation-django-ninja` 기준과 충돌하지 않는지 확인한다.

### 12.1 v1 vs v2 주요 API 변경

```python
# === v1 (지원 중단 -- 레거시 참고만) ===
from pydantic import BaseModel, validator

class UserV1(BaseModel):
    name: str
    age: int

    class Config:
        frozen = True

    @validator('age')
    def check_age(cls, v):
        if v < 0:
            raise ValueError("음수 불가")
        return v

    data = user.dict()          # dict() 메서드
    user = UserV1.parse_obj({}) # parse_obj()

# === v2 (현재) -- 권장 ===
from pydantic import BaseModel, ConfigDict, field_validator

class UserV2(BaseModel):
    model_config = ConfigDict(frozen=True)  # Config 클래스 -> ConfigDict

    name: str
    age: int

    @field_validator('age')  # @validator -> @field_validator
    @classmethod
    def check_age(cls, v: int) -> int:
        if v < 0:
            raise ValueError("음수 불가")
        return v

    data = user.model_dump()          # dict() -> model_dump()
    user = UserV2.model_validate({})  # parse_obj() -> model_validate()
```

### 12.2 model_validator: 모델 수준 검증

```python
from pydantic import BaseModel, model_validator

class DateRange(BaseModel):
    start: str
    end: str

    @model_validator(mode='after')
    def check_date_order(self) -> 'DateRange':
        if self.start > self.end:
            raise ValueError("시작일이 종료일보다 늦을 수 없습니다")
        return self

    @model_validator(mode='before')
    @classmethod
    def normalize_dates(cls, data: dict) -> dict:
        """모든 필드가 파싱되기 전에 데이터를 정규화"""
        if isinstance(data, dict) and 'date_range' in data:
            start, end = data['date_range'].split('~')
            data['start'] = start.strip()
            data['end'] = end.strip()
        return data
```

### 12.3 Strict Mode: 타입 강제 변환 제어

```python
from pydantic import BaseModel, ConfigDict, Field

# 나쁜 예 (v2 기본): 암묵적 형변환 허용
class LaxModel(BaseModel):
    count: int

LaxModel(count="42")  # OK: "42" -> 42 자동 변환

# 좋은 예: strict 모드로 타입 정확성 강제
class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True)
    count: int

# StrictModel(count="42")  # ValidationError: int 타입이어야 함

# 필드별 strict 제어
class MixedModel(BaseModel):
    model_config = ConfigDict(strict=True)
    id: int                              # strict
    name: str                            # strict
    score: float = Field(strict=False)   # 이 필드만 lax
```

---

## 13. 이터레이터, 제너레이터, 컴프리헨션

### 13.1 이터레이터 프로토콜 [슬기로운 파이썬 트릭] [파이썬 클린코드 2nd]

`for x in obj` 는 내부적으로 `iter(obj)` -> `__iter__()` 호출 후 `next()` -> `__next__()` 반복이다.

```python
class BoundedRepeater:
    def __init__(self, value, max_repeats):
        self.value = value
        self.max_repeats = max_repeats
        self.count = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.count >= self.max_repeats:
            raise StopIteration
        self.count += 1
        return self.value
```

### 13.2 리스트 대신 제너레이터 [파이썬코딩의기술] [파이썬 클린코드 2nd]

```python
# 나쁜 예: 전체를 메모리에 적재
def load_purchases(filename):
    purchases = []
    with open(filename) as f:
        for line in f:
            purchases.append(float(line))
    return purchases

# 좋은 예: 제너레이터로 지연 평가
def load_purchases(filename):
    with open(filename) as f:
        for line in f:
            yield float(line)
```

### 13.3 제너레이터 식 [파이썬코딩의기술]

```python
# 리스트 컴프리헨션 -> 메모리 전부 사용
total = sum([x ** 2 for x in range(10)])

# 제너레이터 식 -> 메모리 절약
total = sum(x ** 2 for x in range(10))

# 제너레이터 식 합성
it = (len(x) for x in open('file.txt'))
roots = ((x, x ** 0.5) for x in it)
```

### 13.4 yield from으로 제너레이터 합성 [파이썬코딩의기술]

```python
# 나쁜 예: 반복적인 for + yield
def animate():
    for delta in move(4, 5.0):
        yield delta
    for delta in pause(3):
        yield delta

# 좋은 예: yield from
def animate():
    yield from move(4, 5.0)
    yield from pause(3)
```

### 13.5 send, throw 사용 금지 [파이썬코딩의기술]

제너레이터의 `send()`와 `throw()`는 양방향 통신을 제공하지만 가독성이 매우 나쁘다. 대신 이터레이터를 입력으로 전달하거나 상태를 가진 클래스를 사용하라.

### 13.6 itertools 활용 [파이썬코딩의기술]

```python
import itertools

# 연결: chain, cycle, repeat, tee, zip_longest
itertools.chain([1,2], [3,4])        # 1,2,3,4
itertools.zip_longest([1,2], [3])    # (1,3), (2,None)

# 필터: islice, takewhile, dropwhile, filterfalse
itertools.islice(values, 2, 8, 2)    # 슬라이싱 (복사 없음)
itertools.takewhile(lambda x: x<7, values)

# 조합: product, permutations, combinations
itertools.product([1,2], ['a','b'])  # 데카르트 곱
itertools.combinations([1,2,3], 2)   # 조합

# 누적: accumulate
itertools.accumulate([1,2,3,4])      # 1,3,6,10
```

### 13.7 컴프리헨션 인라이닝 (Python 3.12+) [PEP 709]

Python 3.12부터 딕셔너리, 리스트, 집합 컴프리헨션이 인라인으로 실행된다. 더 이상 각 컴프리헨션마다 별도의 함수 객체와 프레임을 생성하지 않는다.

```python
# Python 3.11: 컴프리헨션마다 내부 함수 생성 (오버헤드)
# Python 3.12: 인라인 실행 (최대 2배 빠름)
squares = [x**2 for x in range(1000)]

# 실제 코드 기반 벤치마크: ~11% 속도 향상
data = {k: v for k, v in zip(keys, values)}
```

**동작 변경 사항**:
- 반복 변수의 격리는 여전히 유지됨 (외부 동명 변수를 덮어쓰지 않음)
- 트레이스백에 컴프리헨션 프레임이 더 이상 표시되지 않음

```python
x = "outer"
result = [x for x in range(3)]  # 컴프리헨션의 x
print(x)  # "outer" -- 격리 유지 (3.12에서도 동일)
```

---

## 14. 컨텍스트 매니저와 with문

### 14.1 커스텀 컨텍스트 매니저 [파이썬코딩의기술] [슬기로운 파이썬 트릭]

```python
# 방법 1: 클래스 기반 (__enter__, __exit__)
class ManagedFile:
    def __init__(self, name):
        self.name = name
    def __enter__(self):
        self.file = open(self.name, 'w')
        return self.file
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()

# 방법 2: contextmanager 데코레이터 (더 간결)
from contextlib import contextmanager

@contextmanager
def managed_file(name):
    try:
        f = open(name, 'w')
        yield f
    finally:
        f.close()

with managed_file('test.txt') as f:
    f.write('hello')
```

### 14.2 with문 활용 패턴 [파이썬코딩의기술] [슬기로운 파이썬 트릭]

```python
# Lock 관리
with threading.Lock():
    ...  # 자동 acquire/release

# 임시 로그 레벨 변경
@contextmanager
def debug_logging(level):
    logger = logging.getLogger()
    old_level = logger.getEffectiveLevel()
    logger.setLevel(level)
    try:
        yield
    finally:
        logger.setLevel(old_level)

with debug_logging(logging.DEBUG):
    my_function()  # 임시로 DEBUG 레벨
```

---

## 15. 예외 처리

### 15.1 try/except/else/finally 각 블록 활용 [파이썬코딩의기술]

```python
try:
    data = read_file(path)
except FileNotFoundError:
    data = default_data          # 예상된 예외 처리
else:
    process(data)                # try 성공 시에만 실행
finally:
    cleanup()                    # 항상 실행
```

### 15.2 최상위 예외 클래스 정의 [파이썬코딩의기술]

API 모듈에는 최상위 Exception을 정의하여 모든 모듈 예외가 이를 상속하게 하라.

```python
# my_module/exceptions.py
class MyModuleError(Exception):
    """모듈의 최상위 예외"""

class InvalidInputError(MyModuleError): ...
class DatabaseError(MyModuleError): ...

# 사용 측
try:
    my_module.do_something()
except my_module.MyModuleError:
    ...  # 모듈의 모든 에러를 한번에 잡을 수 있음
```

### 15.3 @deprecated로 지원 중단 표시 (3.13+) [PEP 702]

> **의사결정 #4**: External 채택. Python 3.13+에서는 `@deprecated`를 사용한다.

```python
from warnings import deprecated
from typing import overload

# 클래스 지원 중단
@deprecated("Use UserV2 instead")
class UserV1:
    pass

# 함수 지원 중단
@deprecated("Use fetch_data_v2() instead")
def fetch_data(url: str) -> bytes:
    return b""

# 오버로드 일부만 지원 중단
@overload
@deprecated("int 인자는 더 이상 지원하지 않습니다. str을 사용하세요.")
def process(value: int) -> str: ...

@overload
def process(value: str) -> str: ...

def process(value: int | str) -> str:
    return str(value)

# 사용 시:
UserV1()       # 런타임: DeprecationWarning + 타입 체커 경고
fetch_data("")  # 런타임: DeprecationWarning + 타입 체커 경고
process(42)     # 런타임: DeprecationWarning + 타입 체커 경고
process("ok")   # 경고 없음
```

**핵심**: `__deprecated__` 속성이 자동으로 추가되어 런타임에서도 지원 중단 메시지에 접근할 수 있다.

> **레거시 참고**: 3.13 미만에서는 `warnings.warn(DeprecationWarning)`을 사용한다. 단, 이 방법은 런타임 경고만 발생하며 타입 체커와 연동되지 않는다.

---

## 16. 동시성과 병렬성

### 16.1 GIL과 스레드 선택 기준 [파이썬코딩의기술]

- **GIL**: CPython에서 한 번에 하나의 스레드만 바이트코드 실행.
- **스레드 사용**: 블로킹 I/O 시 (파일, 네트워크). GIL은 시스템 콜 전에 해제됨.
- **CPU 병렬화**: 기본적으로 `multiprocessing`이나 C 확장 사용. Free-threaded 빌드(3.13+)에서는 스레드도 가능.

```python
# 블로킹 I/O -> 스레드 OK
from threading import Thread
threads = [Thread(target=slow_io_call) for _ in range(5)]
for t in threads: t.start()

# 스레드 간 데이터 경합 -> Lock 필수
from threading import Lock
class LockingCounter:
    def __init__(self):
        self.lock = Lock()
        self.count = 0
    def increment(self, offset):
        with self.lock:
            self.count += offset
```

### 16.2 asyncio.TaskGroup: 구조적 동시성 (3.11+) [PEP 654]

> **의사결정 #3**: External 채택. Python 3.11+에서는 `asyncio.TaskGroup`을 기본 패턴으로 권장한다.

```python
import asyncio

# 나쁜 예: asyncio.gather에서 첫 번째 에러만 표면화
async def old_style():
    results = await asyncio.gather(
        fetch_user(),
        fetch_orders(),
        return_exceptions=True  # 예외가 결과에 섞임
    )

# 좋은 예: TaskGroup으로 구조적 동시성 (3.11+)
async def new_style():
    async with asyncio.TaskGroup() as tg:
        user_task = tg.create_task(fetch_user())
        orders_task = tg.create_task(fetch_orders())
    # 모든 태스크 완료 후 여기에 도달
    # 예외 발생 시 ExceptionGroup으로 묶여서 전파
    return user_task.result(), orders_task.result()

# ExceptionGroup 처리: except* 구문
async def handle_errors():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(might_fail_a())
            tg.create_task(might_fail_b())
    except* ValueError as eg:
        # ValueError 서브그룹만 처리
        for exc in eg.exceptions:
            print(f"값 에러: {exc}")
    except* OSError as eg:
        # OSError 서브그룹만 처리
        for exc in eg.exceptions:
            print(f"OS 에러: {exc}")
```

> **레거시 참고**: 3.11 미만에서는 `asyncio.gather`가 유효하지만, `return_exceptions=True` 사용 시 예외가 결과에 섞이고 첫 번째 에러만 표면화되는 문제가 있다.

### 16.3 Free-Threaded Python (3.13+) [PEP 703]

> **의사결정 #2**: External 채택. Python 3.13+의 Free-threading을 반영한다.

GIL을 비활성화하여 스레드 기반 진정한 병렬 실행을 가능하게 하는 실험적 기능이다.

```python
import sys
import threading

# GIL 상태 확인
print(f"GIL 활성화 여부: {sys._is_gil_enabled()}")  # False면 free-threaded 모드

# CPU 바운드 작업 -- 기존에는 스레드로 병렬화 불가했음
def cpu_intensive(n: int) -> int:
    return sum(i * i for i in range(n))

# Free-threaded 빌드에서는 실제 병렬 실행
threads = [
    threading.Thread(target=cpu_intensive, args=(10_000_000,))
    for _ in range(4)
]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

**현재 상태 (3.13)**:
- 실험적 기능: `python3.13t` 별도 실행 파일 또는 `--disable-gil` 빌드 옵션 필요
- 단일 스레드 성능이 다소 하락 (3.14에서 5-10%로 개선)
- 런타임에서 `PYTHON_GIL=0` 환경 변수 또는 `-X gil=0` 옵션으로 제어
- 모든 C 확장이 호환되는 것은 아님

### 16.4 Subinterpreters (Python 3.14+) [PEP 734]

GIL 없이 진정한 멀티코어 병렬성을 제공하는 공식 API가 표준 라이브러리에 추가되었다.

```python
import concurrent.interpreters as interpreters

# 각 인터프리터는 독립된 GIL을 가짐 (또는 free-threaded에서는 GIL 없음)
# multiprocessing과 달리 같은 프로세스 내에서 실행
interp = interpreters.create()
interp.exec("print('별도 인터프리터에서 실행')")

# 인터프리터 간 데이터 교환은 직렬화 필요
# (공유 메모리는 없지만 프로세스 간 통신보다 가벼움)
```

### 16.5 ThreadPoolExecutor [파이썬코딩의기술]

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=10) as pool:
    future = pool.submit(task_function, *args)
    result = future.result()  # 예외도 자동 전파
```

### 16.6 Queue로 스레드 간 작업 조율 [파이썬코딩의기술]

```python
from queue import Queue

queue = Queue(maxsize=10)  # 버퍼 크기 제한 -> 메모리 폭발 방지
queue.put(item)            # 가득 차면 블록
queue.get()                # 비어 있으면 블록
```

---

## 17. 성능 프로파일링과 최적화

> 출처: High Performance Python 2nd Edition (Micha Gorelick, Ian Ozsvald, O'Reilly 2020)
>
> **의사결정 #6**: External 채택. 3단계 프로파일링 체계를 사용한다.

### 17.1 프로파일링 도구 계층

```python
# === 1단계: cProfile로 함수 수준 병목 식별 ===
# python -m cProfile -o output.prof my_script.py
import cProfile
cProfile.run('main()', 'output.prof')

# === 2단계: line_profiler로 라인 수준 분석 ===
# pip install line_profiler
# @profile 데코레이터를 병목 함수에 추가
@profile  # line_profiler가 인식하는 데코레이터
def expensive_function(data):
    result = []                          # Line 1: 0.1ms
    for item in data:                    # Line 2: 0.2ms
        processed = complex_calc(item)   # Line 3: 850ms  <-- 병목!
        result.append(processed)         # Line 4: 0.3ms
    return result
# kernprof -l -v my_script.py

# === 3단계: memory_profiler로 메모리 사용량 분석 ===
# pip install memory-profiler
from memory_profiler import profile as mem_profile

@mem_profile
def memory_heavy():
    a = [1] * (10 ** 6)        # +7.6 MiB
    b = [2] * (2 * 10 ** 7)    # +152.6 MiB
    del b                       # -152.6 MiB
    return a
```

### 17.2 성능 최적화 전략 [High Performance Python 2nd]

```python
# 전략 1: 올바른 자료구조 선택
# 나쁜 예: 리스트에서 멤버십 체크 O(n)
large_list = list(range(1_000_000))
999_999 in large_list  # ~14ms

# 좋은 예: 세트로 멤버십 체크 O(1)
large_set = set(range(1_000_000))
999_999 in large_set  # ~0.05ms

# 전략 2: 불필요한 객체 생성 회피
# 나쁜 예: 문자열 반복 연결 O(n^2)
result = ""
for chunk in chunks:
    result += chunk

# 좋은 예: join 사용 O(n)
result = "".join(chunks)

# 전략 3: 로컬 변수 활용 (글로벌보다 빠름)
# 나쁜 예
import math
def slow():
    return [math.sqrt(i) for i in range(10000)]

# 좋은 예: 로컬 바인딩
def fast():
    sqrt = math.sqrt  # 로컬 변수로 한번 바인딩
    return [sqrt(i) for i in range(10000)]

# 전략 4: __slots__ 사용 (대량 객체)
class Point:
    __slots__ = ('x', 'y')
    def __init__(self, x, y):
        self.x = x
        self.y = y
# __dict__ 대비 ~40-50% 메모리 절약, 속성 접근 속도 향상
```

### 17.3 Python 3.11 성능 개선: Specializing Adaptive Interpreter [PEP 659]

Python 3.11은 3.10 대비 평균 25%, 최대 60% 빠르다. 핵심 메커니즘은 **특화 적응 인터프리터**이다.

```python
# 개발자가 할 일: 타입을 일관되게 유지하라
# 나쁜 예: 혼합 타입 리스트 (특화 불가)
mixed = [1, 2.0, 3, 4.0]

# 좋은 예: 단일 타입 리스트 (특화 가능)
ints = [1, 2, 3, 4]
```

### 17.4 JIT 컴파일러 (Python 3.13+) [PEP 744]

```python
# Python 3.13의 실험적 JIT (copy-and-patch 방식)
# --enable-experimental-jit 빌드 옵션으로 활성화
# 현재 성능 향상은 미미하지만, 향후 릴리스에서 개선 예정

# 외부 JIT 대안:
# 1. Numba: 수치 계산 특화 JIT
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

---

## 18. f-문자열 개선과 PEG 파서

### 18.1 f-문자열 제한 해제 (PEP 701, Python 3.12+)

PEG 파서(3.9+) 덕분에 f-문자열의 모든 제한이 사라졌다.

```python
# Python 3.12+: 이전에 불가능했던 것들

# 1. 동일 따옴표 재사용
songs = ["Yesterday", "Hey Jude"]
result = f"{''.join(songs)}"  # 3.12+ OK

# 2. 여러 줄 + 인라인 주석
query = f"""
    SELECT *
    FROM users
    WHERE active = {
        True  # 활성 사용자만
    }
"""

# 3. 백슬래시와 표현식 내부 사용 (3.12+)
words = ["hello", "world"]
result = f"{'\n'.join(words)}"     # 3.12+ OK (표현식 내부 백슬래시)

# 4. 중첩 f-문자열
data = {"key": "value"}
result = f"{f"{list(data.keys())[0]}"}"  # 3.12+ OK
```

---

## 19. 파이썬다운 관용 표현

### 19.1 f-문자열 사용 [파이썬코딩의기술]

```python
# 나쁜 예: % 포매팅, str.format()
print('결과: %d' % value)
print('결과: {}'.format(value))

# 좋은 예: f-문자열 (3.6+)
print(f'결과: {value}')
print(f'{number:.{places}f}')  # 형식 지정도 가능
```

### 19.2 enumerate, zip 활용 [파이썬코딩의기술]

```python
# 나쁜 예
for i in range(len(names)):
    name = names[i]

# 좋은 예
for i, name in enumerate(names, 1):  # 시작 인덱스 지정 가능
    ...

for name, count in zip(names, counts):  # 나란히 순회
    ...

# 길이 다른 경우
from itertools import zip_longest
for name, count in zip_longest(names, counts, fillvalue=0):
    ...
```

### 19.3 빈 컨테이너 검사 [파이썬코딩의기술]

```python
# 나쁜 예
if len(container) == 0: ...
if len(container) > 0: ...

# 좋은 예: 암묵적 불리언 평가
if not container: ...   # 비어 있음
if container: ...       # 비어 있지 않음
```

### 19.4 bytes와 str 분리 (유니코드 샌드위치) [파이썬코딩의기술]

인코딩/디코딩은 인터페이스의 가장 먼 경계에서 수행하라.

```python
def to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        return bytes_or_str.decode('utf-8')
    return bytes_or_str
```

### 19.5 for/while 뒤 else 금지 [파이썬코딩의기술]

루프 뒤 else 블록은 루프가 완료되면 실행된다. 직관에 반하므로 사용하지 마라.

### 19.6 명명 규칙 [PEP 8] [슬기로운 파이썬 트릭]

| 대상 | 스타일 | 예시 |
|------|--------|------|
| 모듈 | snake_case | `my_module.py` |
| 패키지 | lowercase | `mypackage` |
| 클래스 | PascalCase | `MyClass` |
| 예외 | PascalCase + Error 접미사 | `ValueError` |
| 함수/메서드 | snake_case | `calculate_total()` |
| 변수 | snake_case | `user_count` |
| 상수 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |

밑줄 관례:

| 패턴 | 의미 |
|------|------|
| `_var` | 관례적 보호(protected). 와일드카드 import에서 제외 |
| `var_` | 파이썬 키워드와 이름 충돌 회피 (`class_`) |
| `__var` | 네임 맹글링. 하위 클래스 충돌 방지 전용 |
| `__var__` | 매직 메서드/던더. 파이썬 예약 |
| `_` | 임시/무시 변수 (`for _ in range(10)`) |

---

## 20. 디자인 패턴 (Python 고유 구현)

범용 디자인 패턴의 개념은 `workspace/reference/discipline-cleancode/reference/final.md`를 참조한다.

### 20.1 `__init_subclass__` 레지스트리 패턴

```python
class Handler:
    _registry: dict[str, type["Handler"]] = {}

    def __init_subclass__(cls, *, kind: str, **kwargs):
        super().__init_subclass__(**kwargs)
        Handler._registry[kind] = cls

    @classmethod
    def create(cls, kind: str, **kwargs) -> "Handler":
        return cls._registry[kind](**kwargs)

class JsonHandler(Handler, kind="json"):
    def handle(self, data): ...

class XmlHandler(Handler, kind="xml"):
    def handle(self, data): ...

handler = Handler.create("json")  # JsonHandler 인스턴스
```

### 20.2 Protocol 기반 디스패치

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Renderable(Protocol):
    def render(self) -> str: ...

def render_all(items: list[Renderable]) -> list[str]:
    return [item.render() for item in items]

# 어떤 클래스든 render() 메서드만 있으면 Renderable로 인정 (덕 타이핑)
```

### 20.3 `@dataclass` + 팩토리 조합

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Config:
    host: str
    port: int
    debug: bool = False

    @classmethod
    def from_env(cls) -> "Config":
        import os
        return cls(
            host=os.environ.get("HOST", "localhost"),
            port=int(os.environ.get("PORT", "8000")),
            debug=os.environ.get("DEBUG", "").lower() == "true",
        )

config = Config.from_env()
```

---

## 21. Repository / Unit of Work

Repository, Unit of Work, 핵사고날(포트/어댑터), CQRS, outbox, ACL 등 구조 패턴의 선택 기준은 `architecture-ddd`(§5 아키텍처, §6 구현 패턴)가 소유하고, Django ORM 환경에서의 적용은 `implementation-django`(§16 서비스 레이어)가 담당한다. 이 문서는 그 패턴들을 표현할 때 쓰는 Python 경계 도구(`Protocol`/ABC, 타입 기반 협력)만 다룬다.

---

## 22. Ruff -- 통합 린터/포매터

> 출처: [Ruff 공식 문서](https://docs.astral.sh/ruff/)

Ruff는 Rust로 작성된 초고속 Python 린터/포매터로, 약 50개 flake8 플러그인의 규칙을 재구현하며, Flake8, Black, isort 등을 대체한다. 기존 도구 대비 10-100배 빠르다.

### 22.1 권장 pyproject.toml 설정

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

### 22.2 Ruff의 핵심 규칙 카테고리

```python
# UP (pyupgrade): 구버전 패턴을 최신 문법으로 자동 변환
# 나쁜 예 (UP006): typing.List 사용
from typing import List, Dict, Optional
def f(x: List[int]) -> Dict[str, int]: ...

# 좋은 예: 내장 타입 사용 (3.9+)
def f(x: list[int]) -> dict[str, int]: ...

# 나쁜 예 (UP007): Union 대신 | 사용 가능
from typing import Union
x: Union[int, str]

# 좋은 예: X | Y 문법 (3.10+)
x: int | str

# B (bugbear): 미묘한 버그 감지
# B006: 가변 디폴트 인자
def bad(items: list[int] = []):  # B006!
    ...

# B007: 루프 변수 미사용
for x in range(10):  # B007: x 미사용 -> for _ in range(10)
    do_something()

# SIM (simplify): 불필요한 복잡성 제거
# SIM102: 중첩 if 통합
if a:
    if b:   # -> if a and b:
        ...

# SIM108: if-else를 삼항으로
if cond:
    x = a
else:
    x = b
# -> x = a if cond else b
```

---

## 23. mypy/pyright 최신 기능

> 출처: [mypy 문서](https://mypy.readthedocs.io/en/stable/), [pyright 설정 가이드](https://microsoft.github.io/pyright/)

### 23.1 mypy strict 모드 설정

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.12"
strict = true

# strict는 아래를 모두 활성화:
# warn_return_any, warn_unused_configs, disallow_any_generics,
# disallow_subclassing_any, disallow_untyped_calls,
# disallow_untyped_defs, disallow_incomplete_defs,
# check_untyped_defs, no_implicit_optional,
# warn_redundant_casts, warn_unused_ignores, no_implicit_reexport

# 점진적 도입: 모듈별 설정
[[tool.mypy.overrides]]
module = "legacy_code.*"
ignore_errors = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

### 23.2 pyright strict 모드

```json
// pyrightconfig.json
{
    "pythonVersion": "3.12",
    "typeCheckingMode": "strict",
    "reportMissingTypeStubs": "warning",
    "reportUnusedImport": "error",
    "reportUnusedVariable": "warning"
}
```

### 23.3 타입 좁히기(Type Narrowing) 패턴

```python
from typing import assert_never

# 1. isinstance 좁히기
def process(value: int | str | list) -> str:
    if isinstance(value, int):
        return str(value)       # value: int
    elif isinstance(value, str):
        return value.upper()    # value: str
    elif isinstance(value, list):
        return str(len(value))  # value: list
    else:
        assert_never(value)     # 도달 불가 보장 (3.11+)

# 2. 패턴 매칭에서의 타입 좁히기
def handle(event: str | int | None) -> str:
    match event:
        case str(s):
            return s.upper()    # s: str
        case int(n):
            return str(n)       # n: int
        case None:
            return "none"

# 3. 판별 유니온 (Discriminated Union)
from dataclasses import dataclass
from typing import Literal

@dataclass
class Success:
    status: Literal["ok"]
    data: str

@dataclass
class Error:
    status: Literal["error"]
    message: str

type Result = Success | Error

def handle_result(result: Result) -> str:
    match result:
        case Success(data=d):
            return d
        case Error(message=m):
            return f"에러: {m}"
```

---

## 24. 테스트

테스트와 디버깅은 `workspace/reference/implementation-test/reference/final.md`를 참조한다.

---

## 25. 디버깅 기법 [파이썬코딩의기술]

### 25.1 repr 문자열 활용

디버깅을 할 때 `print`를 사용한다면 `repr`을 호출해서 타입이 다른 경우에도 명확히 차이를 볼 수 있게 만들어야 한다.

```python
print(repr(5))    # 5
print(repr('5'))  # '5'

# 커스텀 클래스에 __repr__ 정의
class Money:
    def __repr__(self):
        return f"Money({self.amount!r}, {self.currency!r})"
```

### 25.2 pdb 대화형 디버거

```python
def compute(data):
    result = transform(data)
    breakpoint()  # 여기서 대화형 디버거 시작
    return finalize(result)
```

주요 명령어:

| 명령 | 설명 |
|-----|------|
| `where` | 현재 호출 스택 출력 |
| `up` / `down` | 호출 스택에서 이동 |
| `step` | 다음 줄 실행 (함수 내부 진입) |
| `next` | 다음 줄 실행 (함수 호출 건너뜀) |
| `return` | 현재 함수 반환까지 실행 |
| `continue` | 다음 중단점까지 계속 |
| `quit` | 디버거 종료 |

사후 디버깅: `python -m pdb -c continue program.py`

---

## 26. 독스트링과 문서화

### 26.1 독스트링 규칙 [파이썬코딩의기술]

```python
def find_anagrams(word: str) -> list[str]:
    """주어진 단어의 모든 어구전철을 찾는다.

    이 함수는 딕셔너리 파일의 전체 내용을 메모리에
    로드하기 때문에 실행 속도가 느릴 수 있다.

    Args:
        word: 대상 단어. 빈 문자열이면 빈 리스트 반환.

    Returns:
        어구전철 리스트. 매치가 없으면 빈 리스트.
    """
```

- 모듈: 첫 줄에 목적, 이후 공개 함수/클래스 목록
- 클래스: 목적 + 중요 공개 애트리뷰트/메서드
- 함수: 목적 + Args + Returns + Raises
- 스크립트: 사용법(usage) 메시지 — 명령행 구문, 환경 변수, 입출력 파일
- 타입 어노테이션과 중복되면 둘 중 하나만 유지

---

## 27. 정밀 연산

### 27.1 Decimal과 Fraction [파이썬코딩의기술]

```python
from decimal import Decimal, ROUND_UP

# 나쁜 예: IEEE 754 부동소수점 오차
rate = 1.45
cost = rate * 222 / 60  # 5.364999999...

# 좋은 예: Decimal (str 생성자 필수)
rate = Decimal('1.45')
cost = rate * Decimal('222') / Decimal('60')

# 반올림
rounded = cost.quantize(Decimal('0.01'), rounding=ROUND_UP)
```

---

## 28. Python 3.14 주요 변경사항

> 출처: [What's New In Python 3.14](https://docs.python.org/3/whatsnew/3.14.html)

### 28.1 어노테이션 지연 평가 (PEP 649)

```python
# Python 3.14: 어노테이션이 더 이상 즉시 평가되지 않음
# from __future__ import annotations 없이도 전방 참조 가능

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

### 28.2 Template Strings (t-strings) -- PEP 750

```python
from string.templatelib import Template

name = "World"

# f-string: 즉시 문자열로 평가
f_result = f"Hello, {name}!"  # "Hello, World!"

# t-string: Template 객체 반환 (지연 처리)
t_result = t"Hello, {name}!"  # Template 객체

# 핵심 차이: t-string은 값을 즉시 결합하지 않음
# -> 보간(interpolation) 전에 검증/이스케이프 가능

# SQL 인젝션 방지 예시
def safe_sql(template: Template) -> tuple[str, list[object]]:
    parts = []
    params = []
    for item in template:
        if isinstance(item, str):
            parts.append(item)
        else:
            parts.append("?")
            params.append(item.value)  # 파라미터화
    return "".join(parts), params

user_input = "'; DROP TABLE users; --"
query, params = safe_sql(t"SELECT * FROM users WHERE name = {user_input}")
# query: "SELECT * FROM users WHERE name = ?"
# params: ["'; DROP TABLE users; --"]  -- 안전하게 파라미터화
```

---

## 부록 A: Python 3.10-3.14 핵심 변경사항 요약

| 버전 | 핵심 기능 | PEP |
|------|----------|-----|
| 3.10 | match/case, 타입 유니온 `X \| Y`, ParamSpec | 634/635/636, 604, 612 |
| 3.11 | ExceptionGroup, TaskGroup, tomllib, 25% 성능 향상 | 654, 680, 659 |
| 3.12 | type 문, 제네릭 `def f[T]()`, f-string 제한 해제, 컴프리헨션 인라이닝 | 695, 701, 709 |
| 3.13 | Free-threading(실험), JIT(실험), TypeIs, @deprecated, REPL 개선 | 703, 744, 742, 702 |
| 3.14 | 어노테이션 지연 평가, t-strings, subinterpreters, Zstandard 압축 | 649, 750, 734, 784 |

## 부록 B: 타입 시스템 진화 요약

| 기능 | 도입 버전 | PEP | 용도 |
|------|----------|-----|------|
| `TypeGuard` | 3.10 | 647 | 사용자 정의 타입 가드 (if만 좁히기) |
| `ParamSpec` | 3.10 | 612 | 데코레이터 매개변수 타입 보존 |
| `TypeVarTuple` | 3.11 | 646 | 가변 길이 제네릭 |
| `type` 문 | 3.12 | 695 | 지연 평가 타입 앨리어스 |
| `def f[T]()` | 3.12 | 695 | 간결한 제네릭 문법 |
| `@override` | 3.12 | 698 | 오버라이드 안전성 검증 |
| `TypeIs` | 3.13 | 742 | 양방향 타입 좁히기 |
| `@deprecated` | 3.13 | 702 | 지원 중단 표시 |
| TypeVar 기본값 | 3.13 | 696 | 제네릭 타입 기본값 |
| 어노테이션 지연 평가 | 3.14 | 649 | 전방 참조 자연스러운 지원 |

## 부록 C: 주요 매직 메서드 요약

| 매직 메서드 | 용도 |
|------------|------|
| `__init__` | 생성자 |
| `__repr__` / `__str__` | 문자열 표현 (디버깅 / 사용자용) |
| `__call__` | 인스턴스를 함수처럼 호출 |
| `__iter__` / `__next__` | 이터레이터 프로토콜 |
| `__getitem__` / `__setitem__` | 인덱싱, 슬라이싱 |
| `__getattr__` / `__getattribute__` | 애트리뷰트 접근 훅 |
| `__get__` / `__set__` / `__set_name__` | 디스크립터 프로토콜 |
| `__enter__` / `__exit__` | 컨텍스트 매니저 (with문) |
| `__init_subclass__` | 하위 클래스 정의 시 훅 |
| `__missing__` | dict 키 미존재 시 훅 |
| `__eq__` / `__lt__` / `__hash__` | 비교, 해싱 |
| `__len__` / `__contains__` | 길이, 멤버십 테스트 |
| `__add__` / `__radd__` / `__iadd__` | 산술 연산 (좌항/우항/증강) |
| `__mul__` / `__matmul__` | 곱셈, 행렬 곱 |
| `__bool__` | 불리언 변환 (`if obj:`) |

---

## 출처

### PEP 문서
- [PEP 544 -- Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- [PEP 557 -- Data Classes](https://peps.python.org/pep-0557/)
- [PEP 612 -- Parameter Specification Variables](https://peps.python.org/pep-0612/)
- [PEP 617 -- New PEG parser for CPython](https://peps.python.org/pep-0617/)
- [PEP 634 -- Structural Pattern Matching: Specification](https://peps.python.org/pep-0634/)
- [PEP 636 -- Structural Pattern Matching: Tutorial](https://peps.python.org/pep-0636/)
- [PEP 646 -- Variadic Generics](https://peps.python.org/pep-0646/)
- [PEP 649 -- Deferred Evaluation Of Annotations](https://peps.python.org/pep-0649/)
- [PEP 654 -- Exception Groups and except*](https://peps.python.org/pep-0654/)
- [PEP 695 -- Type Parameter Syntax](https://peps.python.org/pep-0695/)
- [PEP 696 -- Type Defaults for TypeVarLikes](https://peps.python.org/pep-0696/)
- [PEP 698 -- Override Decorator for Static Typing](https://peps.python.org/pep-0698/)
- [PEP 701 -- Syntactic formalization of f-strings](https://peps.python.org/pep-0701/)
- [PEP 702 -- Marking deprecations using the type system](https://peps.python.org/pep-0702/)
- [PEP 703 -- Making the Global Interpreter Lock Optional](https://peps.python.org/pep-0703/)
- [PEP 709 -- Inlined comprehensions](https://peps.python.org/pep-0709/)
- [PEP 734 -- Multiple Interpreters in the Stdlib](https://peps.python.org/pep-0734/)
- [PEP 742 -- Narrowing types with TypeIs](https://peps.python.org/pep-0742/)
- [PEP 744 -- JIT Compilation](https://peps.python.org/pep-0744/)
- [PEP 750 -- Template Strings](https://peps.python.org/pep-0750/)

### Python 공식 문서
- [What's New In Python 3.11](https://docs.python.org/3/whatsnew/3.11.html)
- [What's New In Python 3.12](https://docs.python.org/3/whatsnew/3.12.html)
- [What's New In Python 3.13](https://docs.python.org/3/whatsnew/3.13.html)
- [What's New In Python 3.14](https://docs.python.org/3/whatsnew/3.14.html)
- [typing 모듈 공식 문서](https://docs.python.org/3/library/typing.html)
- [dataclasses 공식 문서](https://docs.python.org/3/library/dataclasses.html)
- [Python free-threading HOWTO](https://docs.python.org/3/howto/free-threading-python.html)
- [Python Descriptor HowTo Guide](https://docs.python.org/3/howto/descriptor.html)

### 서적
- 단단한 파이썬 -- Patrick Viafore
- 파이썬코딩의기술 (Effective Python) -- Brett Slatkin
- 슬기로운 파이썬 트릭 -- Dan Bader
- 파이썬 클린코드 2nd -- Mariano Anaya
- Fluent Python 2nd Edition -- Luciano Ramalho (O'Reilly, 2022)
- Python Cookbook 3rd Edition -- David Beazley, Brian K. Jones (O'Reilly, 2013)
- Architecture Patterns with Python -- Harry Percival, Bob Gregory (O'Reilly, 2020)
- High Performance Python 2nd Edition -- Micha Gorelick, Ian Ozsvald (O'Reilly, 2020)

### 도구 문서
- [Ruff 공식 문서](https://docs.astral.sh/ruff/)
- [mypy 문서](https://mypy.readthedocs.io/en/stable/)
- [pyright 문서](https://microsoft.github.io/pyright/)
- [pydantic v2 문서](https://docs.pydantic.dev/latest/)
- [pydantic v2 Migration Guide](https://docs.pydantic.dev/latest/migration/)

### 커뮤니티
- [Real Python -- Python 3.13: Free Threading and a JIT Compiler](https://realpython.com/python313-free-threading-jit/)
- [Real Python -- Structural Pattern Matching](https://realpython.com/structural-pattern-matching/)
- [Real Python -- Python 3.12 New Features](https://realpython.com/python312-new-features/)
- [typing 공식 사양 -- Protocols](https://typing.python.org/en/latest/reference/protocols.html)
