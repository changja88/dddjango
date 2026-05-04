# 타입 힌트와 타입 시스템

Python 타입 시스템의 핵심 기능과 현대적 사용법을 정리한다.

---

## 타입 어노테이션 기본

타입 어노테이션은 코드를 읽는 사람과 타입 체커(mypy, pyright)에게 타입 정보를 전달한다.
런타임에는 강제되지 않는다.

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

---

## Optional과 None 처리

None은 "10억 달러짜리 실수"라 불린다. Optional 타입으로 None의 존재를 명시하라.

```python
# 나쁜 예: None 반환 가능성이 시그니처에 안 보임
def find_user(user_id: int) -> User: ...

# 좋은 예: 3.10+ 문법
def find_user(user_id: int) -> User | None: ...
```

- `Optional[X]`는 `X | None`과 동등하다. **3.10+에서는 `X | None`을 사용하라.**
- mypy `--strict-optional`으로 None 처리를 강제하라.

---

## Union과 합 타입

곱 타입(Product Type)은 유효하지 않은 상태를 허용한다.
합 타입(Sum Type)을 사용해 비정상 상태를 배제하라.

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

result: Snack | Error = Snack("Hotdog", {"mustard"})
```

---

## Literal, Final, NewType

```python
from typing import Literal, Final, NewType

# Literal: 값의 종류 제한
@dataclass
class Error:
    error_code: Literal[1, 2, 4, 5]

# Final: 불변 상수
VENDOR_NAME: Final = "Viafore's Auto-Dog"

# NewType: 타입 안전한 별도 타입 생성
UserId = NewType("UserId", int)
def get_user(user_id: UserId) -> str: ...
get_user(UserId(42))  # OK
get_user(42)           # 타입 체커 에러
```

---

## TypedDict: 이종 딕셔너리

외부 API, JSON 등 이종 데이터를 담는 딕셔너리에 사용한다.

```python
class NutritionInfo(TypedDict):
    value: int
    unit: str

class RecipeNutrition(TypedDict):
    calories: NutritionInfo
    fat: NutritionInfo
```

---

## 제네릭과 PEP 695 (3.12+)

TypeVar를 전역 스코프에 선언해야 하는 번거로움을 제거한다.

```python
# 3.11 이전 (레거시)
from typing import TypeVar, Generic
T = TypeVar('T')
class Container(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value

# 3.12+ 새 문법 -- 권장
class Container[T]:
    def __init__(self, value: T) -> None:
        self.value = value

# 상한 제약 (bound)
def longest[S: str](a: S, b: S) -> S:
    return a if len(a) >= len(b) else b

# 값 제약 (constrained)
def add[N: (int, float)](a: N, b: N) -> N:
    return a + b

# type 문으로 타입 앨리어스 선언 (지연 평가)
type Vector[T] = list[T]
type Matrix[T] = list[Vector[T]]
```

---

## @override (3.12+)

부모에 없는 메서드를 실수로 override하면 타입 체커가 에러를 발생시킨다.

```python
from typing import override

class Base:
    def get_color(self) -> str:
        return "blue"

class Child(Base):
    @override
    def get_color(self) -> str:
        return "yellow"

    @override
    def nonexistent(self) -> None:  # 타입 체커 에러!
        pass
```

---

## ParamSpec과 Concatenate

데코레이터가 감싼 함수의 매개변수 타입을 보존한다.

```python
from typing import Callable, ParamSpec, TypeVar
from functools import wraps

P = ParamSpec('P')
R = TypeVar('R')

# 나쁜 예: 매개변수 타입 정보 손실
def timer_bad(func: Callable[..., R]) -> Callable[..., R]: ...

# 좋은 예: ParamSpec으로 시그니처 완전 보존
def timer(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        result = func(*args, **kwargs)
        return result
    return wrapper
```

`Concatenate`는 데코레이터가 매개변수를 추가/제거할 때 사용한다.

```python
from typing import Concatenate

def with_request(
    func: Callable[P, R]
) -> Callable[Concatenate[Request, P], R]: ...
```

---

## TypeIs vs TypeGuard

`TypeIs`(3.13+)는 if/else 양쪽 분기 모두에서 타입 좁히기가 가능하다.

```python
from typing import TypeIs

def is_str_list(val: list[int | str]) -> TypeIs[list[str]]:
    return all(isinstance(x, str) for x in val)

def process(data: list[int | str]) -> None:
    if is_str_list(data):
        print(data[0].upper())   # data: list[str]
    else:
        print(data[0] + 1)       # data: list[int] (TypeIs만 가능)
```

대부분의 경우 `TypeIs`를 사용하라. `TypeGuard`는 입력/출력 타입이 호환되지 않는
특수한 경우에만 사용한다.

---

## Protocol: 구조적 서브타이핑

덕 타이핑과 타입 체커를 연결한다. 상속 없이 구조(메서드/속성)만으로 타입을 만족시킨다.

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
```

### Protocol 합성

```python
class Readable(Protocol):
    def read(self, n: int = -1) -> bytes: ...

class Writable(Protocol):
    def write(self, data: bytes) -> int: ...

class ReadWritable(Readable, Writable, Protocol):
    pass
```

### 제네릭 Protocol

```python
class Comparable(Protocol[T_co]):
    def compare(self, other: T_co) -> int: ...

# 3.12+ 문법
class Sortable[T: SupportsLessThan](Protocol):
    def sort(self) -> list[T]: ...
```

### @runtime_checkable의 한계

`isinstance`는 메서드 **존재** 여부만 확인하고 시그니처는 검사하지 않는다.
정확한 타입 검증은 반드시 정적 타입 체커에 의존하라.

---

## TypeVar 기본값 (3.13+)

```python
class Container[T = str]:
    def __init__(self, value: T) -> None:
        self.value = value

c = Container("hello")    # Container[str]
c2 = Container[int](42)   # Container[int]
```

---

## 타입 좁히기(Type Narrowing) 패턴

```python
from typing import assert_never

def process(value: int | str | list) -> str:
    if isinstance(value, int):
        return str(value)
    elif isinstance(value, str):
        return value.upper()
    elif isinstance(value, list):
        return str(len(value))
    else:
        assert_never(value)  # 도달 불가 보장 (3.11+)
```

### 판별 유니온 (Discriminated Union)

```python
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
