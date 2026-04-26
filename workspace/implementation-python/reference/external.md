# Python 언어 특화 가이드 (외부 자료)

> Python 공식 PEP, 권위 있는 서적, 최신 도구 생태계, 커뮤니티 자료에서 수집한 고급 패턴과 관례.
> 내부 자료(파이썬코딩의기술, 단단한 파이썬, 슬기로운 파이썬 트릭, 파이썬 클린코드 2nd, 객체지향 파이썬)와 중복되지 않는 내용에 집중한다.

---

## 1. 구조적 패턴 매칭 (match/case) — Python 3.10+

> 출처: [PEP 634](https://peps.python.org/pep-0634/) (명세), [PEP 635](https://peps.python.org/pep-0635/) (동기), [PEP 636](https://peps.python.org/pep-0636/) (튜토리얼)

### 1.1 패턴 매칭의 7가지 패턴 유형

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

### 1.2 클래스 패턴과 \_\_match\_args\_\_

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

### 1.3 매핑 패턴과 REST 캡처

매핑 패턴은 딕셔너리에서 필요한 키만 추출하며, 나머지 키는 무시된다. `**rest`로 나머지를 명시적으로 캡처할 수 있다.

```python
def handle_config(config: dict):
    match config:
        case {"database": {"host": host, "port": int(port)}, **rest}:
            print(f"DB: {host}:{port}, 추가 설정: {rest.keys()}")
        case {"database": {"host": host}}:
            print(f"DB: {host}, 기본 포트 사용")
```

### 1.4 패턴 매칭 실전 활용: 상태 머신

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

## 2. 고급 타입 시스템 — PEP 기반 최신 기능

### 2.1 ParamSpec: 데코레이터 시그니처 보존 [PEP 612]

> 출처: [PEP 612](https://peps.python.org/pep-0612/), [Python typing 공식 문서](https://docs.python.org/3/library/typing.html)

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

### 2.2 Concatenate: 매개변수 추가/제거 [PEP 612]

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

### 2.3 PEP 695: 새 타입 매개변수 문법 (Python 3.12+)

> 출처: [PEP 695](https://peps.python.org/pep-0695/), [What's New In Python 3.12](https://docs.python.org/3/whatsnew/3.12.html)

TypeVar를 전역 스코프에 선언해야 하는 번거로움과 공변/반공변의 복잡성을 제거한다.

```python
# === Python 3.11 이전: 장황한 문법 ===
from typing import TypeVar, Generic

T = TypeVar('T')
S = TypeVar('S', bound=str)    # 상한 제약
N = TypeVar('N', int, float)   # 값 제약

class Container(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value
    def get(self) -> T:
        return self.value

# === Python 3.12+: 간결한 새 문법 ===
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

### 2.4 TypeIs vs TypeGuard: 타입 좁히기 [PEP 742, PEP 647]

> 출처: [PEP 742](https://peps.python.org/pep-0742/), [Python 3.13 What's New](https://docs.python.org/3/whatsnew/3.13.html)

`TypeIs`(3.13+)는 `TypeGuard`(3.10+)의 개선판으로, if/else 양쪽 분기 모두에서 타입 좁히기가 가능하다.

```python
from typing import TypeGuard, TypeIs

# TypeGuard: if 분기에서만 좁히기 (else는 원래 타입 유지)
def is_str_list_guard(val: list[int | str]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)

# TypeIs: if/else 양쪽 모두 좁히기 (더 직관적)
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

### 2.5 TypeVarTuple과 Unpack: 가변 길이 제네릭 [PEP 646]

> 출처: [PEP 646](https://peps.python.org/pep-0646/), Python 3.11+

NumPy 같은 다차원 배열의 형상(shape)을 타입으로 표현할 수 있게 한다.

```python
from typing import TypeVarTuple, Unpack

Ts = TypeVarTuple('Ts')

# 3.11 문법
def broadcast(*arrays: Unpack[tuple[*Ts]]) -> None: ...

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

### 2.6 타입 매개변수 기본값 (Python 3.13+)

> 출처: [PEP 696](https://peps.python.org/pep-0696/), [Python 3.13 What's New](https://docs.python.org/3/whatsnew/3.13.html)

```python
from typing import TypeVar

# Python 3.13+: TypeVar에 기본값 지정
T = TypeVar('T', default=str)

class Container[T = str]:  # 3.13+ 문법으로도 가능
    def __init__(self, value: T) -> None:
        self.value = value

# T를 명시하지 않으면 str로 추론
c = Container("hello")  # Container[str]
c2 = Container[int](42)  # Container[int]
```

---

## 3. Protocol 심화 — 구조적 서브타이핑의 실전 활용

> 출처: [PEP 544](https://peps.python.org/pep-0544/), [typing 공식 문서](https://typing.python.org/en/latest/reference/protocols.html), [mypy Protocol 문서](https://mypy.readthedocs.io/en/stable/protocols.html)

내부 자료에서 Protocol 기본 사용법을 다뤘으나, 여기서는 PEP 544 전문의 고급 기능을 다룬다.

### 3.1 Protocol 합성과 확장

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

### 3.2 Protocol에 속성과 클래스 변수 정의

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

### 3.3 제네릭 Protocol

```python
from typing import Protocol, TypeVar

T = TypeVar('T')
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

### 3.4 @runtime_checkable의 한계

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

## 4. dataclass 심화 — PEP 557 이후 확장 기능

> 출처: [PEP 557](https://peps.python.org/pep-0557/), [Python dataclasses 공식 문서](https://docs.python.org/3/library/dataclasses.html), [Real Python](https://realpython.com/python-data-classes/)

내부 자료에서 기본 dataclass 사용법을 다뤘으나, 여기서는 3.10+ 추가 옵션과 고급 패턴을 다룬다.

### 4.1 slots=True: 메모리 최적화 (3.10+)

```python
from dataclasses import dataclass

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

### 4.2 kw_only: 키워드 전용 필드 (3.10+)

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

### 4.3 match_args와 패턴 매칭 통합 (3.10+)

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

### 4.4 __post_init__과 InitVar 고급 활용

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

### 4.5 frozen과 불변성 계층

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

    def __hash__(self) -> int:
        # frozen=True 시 __hash__ 자동 생성
        # dict 키, set 원소로 사용 가능
        return hash((self.amount, self.currency))

price = Money(1000, "KRW")
# price.amount = 2000  # FrozenInstanceError
```

---

## 5. PEG 파서와 f-문자열 개선

### 5.1 PEP 617: 새 PEG 파서의 영향

> 출처: [PEP 617](https://peps.python.org/pep-0617/)

Python 3.9에서 LL(1) 파서가 PEG(Parsing Expression Grammar) 파서로 교체되었다. 이 변경으로 이전에 문법적으로 불가능했던 구문이 가능해졌다.

- **좌측 재귀 지원**: PEG 파서는 좌측 재귀를 처리할 수 있어, match/case 같은 복잡한 새 문법을 추가할 수 있게 되었다
- **메모이제이션 캐시**: 파싱 성능 최적화를 위해 중간 결과를 캐싱한다
- **실질적 영향**: 더 나은 에러 메시지와 더 복잡한 문법 구조를 지원한다

### 5.2 f-문자열 제한 해제 (PEP 701, Python 3.12+)

> 출처: [PEP 701](https://peps.python.org/pep-0701/), [What's New In Python 3.12](https://docs.python.org/3/whatsnew/3.12.html)

PEG 파서 덕분에 f-문자열의 모든 제한이 사라졌다.

```python
# Python 3.11 이전: 불가능했던 것들

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
price = f"\N{POUND SIGN}{amount}"  # 3.12+ OK (유니코드 이름)

# 4. 중첩 f-문자열
data = {"key": "value"}
result = f"{f"{list(data.keys())[0]}"}"  # 3.12+ OK
```

---

## 6. @override와 @deprecated — 타입 시스템 기반 안전장치

### 6.1 PEP 698: @override 심화

> 출처: [PEP 698](https://peps.python.org/pep-0698/)

내부 자료에서 기본 사용법을 다뤘으나, 여기서는 프로퍼티/정적 메서드에의 적용과 실전 패턴을 다룬다.

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

    # 타입 체커 에러: 부모에 없는 메서드를 override로 표시
    @override
    def nonexistent(self) -> None:  # Error!
        pass
```

### 6.2 PEP 702: @deprecated — 타입 시스템으로 지원 중단 표시

> 출처: [PEP 702](https://peps.python.org/pep-0702/), Python 3.13+

`warnings.deprecated()`는 런타임 경고와 정적 타입 체커 진단을 동시에 제공한다.

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

---

## 7. 컴프리헨션 인라이닝과 성능 최적화

### 7.1 PEP 709: 컴프리헨션 인라이닝 (Python 3.12+)

> 출처: [PEP 709](https://peps.python.org/pep-0709/), [What's New In Python 3.12](https://docs.python.org/3/whatsnew/3.12.html)

Python 3.12부터 딕셔너리, 리스트, 집합 컴프리헨션이 인라인으로 실행된다. 더 이상 각 컴프리헨션마다 별도의 함수 객체와 프레임을 생성하지 않는다.

```python
# Python 3.11: 컴프리헨션마다 내부 함수 생성 (오버헤드)
# Python 3.12: 인라인 실행 (최대 2배 빠름)

# 마이크로벤치마크: ~2배 속도 향상
squares = [x**2 for x in range(1000)]

# 실제 코드 기반 벤치마크: ~11% 속도 향상
data = {k: v for k, v in zip(keys, values)}
```

**동작 변경 사항**:
- 트레이스백에 컴프리헨션 프레임이 더 이상 표시되지 않음
- 프로파일링에서 컴프리헨션이 함수 호출로 나타나지 않음
- 컴프리헨션 내부에서 `locals()` 호출 시 외부 변수도 포함됨
- 반복 변수의 격리는 여전히 유지됨 (외부 동명 변수를 덮어쓰지 않음)

```python
x = "outer"
result = [x for x in range(3)]  # 컴프리헨션의 x
print(x)  # "outer" — 격리 유지 (3.12에서도 동일)
```

### 7.2 Python 3.11 성능 개선: Specializing Adaptive Interpreter

> 출처: [What's New In Python 3.11](https://docs.python.org/3/whatsnew/3.11.html)

Python 3.11은 3.10 대비 평균 25%, 최대 60% 빠르다. 핵심 메커니즘은 **특화 적응 인터프리터**(PEP 659)이다.

```python
# 내부적으로 핫 코드 경로를 자동 특화
# 예: 타입이 일관된 루프는 타입 체크를 건너뛰는 특화 바이트코드 사용

def sum_ints(data: list[int]) -> int:
    total = 0
    for x in data:
        total += x  # 반복적으로 int + int -> 특화 BINARY_OP_ADD_INT
    return total

# 개발자가 할 일: 타입을 일관되게 유지하라
# 나쁜 예: 혼합 타입 리스트 (특화 불가)
mixed = [1, 2.0, 3, 4.0]

# 좋은 예: 단일 타입 리스트 (특화 가능)
ints = [1, 2, 3, 4]
```

---

## 8. Python 데이터 모델 심화 — Fluent Python 2nd Edition

> 출처: Fluent Python 2nd Edition (Luciano Ramalho, O'Reilly 2022)

### 8.1 연산자 오버로딩 규칙

Fluent Python 2nd Edition Ch.16에서 다루는 연산자 오버로딩의 핵심 규칙은 내부 자료에서 다루지 않는 고급 패턴이다.

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
    #    가변 객체: self를 변경하고 self 반환
    #    불변 객체: 새 객체 반환 (여기서는 불변으로 취급)
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
print(v1 + v2)      # Vector(4, 5)     — __add__
print(3 * v1)        # Vector(6, 12)    — __rmul__
print(v1 @ v2)       # 8                — __matmul__ (내적)
v1 += v2              # __iadd__
print(v1)             # Vector(4, 5)
```

**핵심 규칙**:
- `NotImplemented`를 반환하라 (raise가 아님). 파이썬이 역연산(`__radd__` 등)을 시도한다
- `__eq__`를 정의하면 `__hash__`는 `None`이 되므로, 해시 가능 객체는 `__hash__`도 정의하라
- `@` 연산자(PEP 465)는 `__matmul__`/`__rmatmul__`/`__imatmul__`로 구현한다

### 8.2 \_\_init\_subclass\_\_ 고급 활용: 플러그인 레지스트리

> 출처: Fluent Python 2nd Edition, Python Cookbook 3rd Edition (David Beazley)

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

### 8.3 디스크립터 심화: 검증 프레임워크 패턴

> 출처: Python 공식 Descriptor HowTo Guide (Raymond Hettinger)

Python 공식 Descriptor HowTo Guide에서 제시하는 패턴으로, 디스크립터와 메타클래스를 조합하여 선언적 검증을 구현한다.

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

---

## 9. 동시성 심화 — 최신 패턴

### 9.1 ExceptionGroup과 TaskGroup (Python 3.11+)

> 출처: [PEP 654](https://peps.python.org/pep-0654/), [What's New In Python 3.11](https://docs.python.org/3/whatsnew/3.11.html), [Real Python](https://realpython.com/python311-exception-groups/)

여러 비동기 작업에서 동시에 발생하는 예외를 구조적으로 처리한다.

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

### 9.2 Free-Threaded Python (Python 3.13+)

> 출처: [PEP 703](https://peps.python.org/pep-0703/), [Python 3.13 What's New](https://docs.python.org/3/whatsnew/3.13.html), [Python free-threading HOWTO](https://docs.python.org/3/howto/free-threading-python.html)

GIL을 비활성화하여 스레드 기반 진정한 병렬 실행을 가능하게 하는 실험적 기능이다.

```python
import sys
import threading

# GIL 상태 확인 (권장: sys._is_gil_enabled() 사용)
# 'free-threading' in sys.version은 비공식적 방법이므로 권장하지 않음
print(f"GIL 활성화 여부: {sys._is_gil_enabled()}")  # False면 free-threaded 모드
print(f"GIL 비활성화: {not sys._is_gil_enabled()}")

# CPU 바운드 작업 — 기존에는 스레드로 병렬화 불가했음
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

### 9.3 Subinterpreters (Python 3.14+)

> 출처: [PEP 734](https://peps.python.org/pep-0734/), [What's New In Python 3.14](https://docs.python.org/3/whatsnew/3.14.html)

GIL 없이 진정한 멀티코어 병렬성을 제공하는 공식 API가 표준 라이브러리에 추가되었다.

```python
import concurrent.interpreters as interpreters

# 각 인터프리터는 독립된 GIL을 가짐 (또는 free-threaded에서는 GIL 없음)
# multiprocessing과 달리 같은 프로세스 내에서 실행
interp = interpreters.create()
interp.exec("print('별도 인터프리터에서 실행')")
```

---

## 10. 성능 프로파일링과 최적화

> 출처: High Performance Python 2nd Edition (Micha Gorelick, Ian Ozsvald, O'Reilly 2020)

### 10.1 프로파일링 도구 계층

내부 자료에서 `cProfile` 기본 사용법을 다뤘으나, 여기서는 프로파일링 전략과 고급 도구를 다룬다.

```python
# === 1단계: cProfile로 함수 수준 병목 식별 ===
# python -m cProfile -o output.prof my_script.py
# 또는 코드 내에서:
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

### 10.2 성능 최적화 전략 (High Performance Python)

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

### 10.3 JIT 컴파일러 (Python 3.13+)

> 출처: [PEP 744](https://peps.python.org/pep-0744/), [Python 3.13 What's New](https://docs.python.org/3/whatsnew/3.13.html)

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

## 11. pydantic v2 — 런타임 검증의 새 표준

> 출처: [pydantic v2 공식 문서](https://docs.pydantic.dev/latest/), [Migration Guide](https://docs.pydantic.dev/latest/migration/)

내부 자료에서 pydantic v1 스타일을 다뤘으나, v2는 Rust 기반 코어로 4-50배 빨라졌고 API가 크게 변경되었다.

### 11.1 v1 vs v2 주요 API 변경

```python
# === v1 (지원 중단) ===
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

# === v2 (현재) ===
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

### 11.2 model_validator: 모델 수준 검증

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

### 11.3 Strict Mode: 타입 강제 변환 제어

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

## 12. Ruff — 통합 린터/포매터

> 출처: [Ruff 공식 문서](https://docs.astral.sh/ruff/), [Ruff GitHub](https://github.com/astral-sh/ruff)

Ruff는 Rust로 작성된 초고속 Python 린터/포매터로, 약 50개 flake8 플러그인의 규칙을 재구현하며, Flake8, Black, isort 등을 대체한다. 기존 도구 대비 10-100배 빠르다.

### 12.1 권장 pyproject.toml 설정

```toml
[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
# 명시적으로 선택 (extend-select보다 권장)
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

# 포매터와 충돌하는 규칙 비활성화
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

### 12.2 Ruff의 핵심 규칙 카테고리

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

## 13. mypy/pyright 최신 기능

> 출처: [mypy 문서](https://mypy.readthedocs.io/en/stable/), [pyright 설정 가이드](https://microsoft.github.io/pyright/), [PEP 742](https://peps.python.org/pep-0742/)

### 13.1 mypy strict 모드 설정

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

### 13.2 pyright strict 모드

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

### 13.3 타입 좁히기(Type Narrowing) 패턴

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

## 14. Repository 패턴과 Unit of Work — Python 특화 구현

> 출처: Architecture Patterns with Python (Harry Percival, Bob Gregory, O'Reilly 2020)

아키텍처 문서와 겹치지 않는 **Python 특화** 구현 기법에 집중한다.

### 14.1 ABC 기반 Repository 포트

```python
from abc import ABC, abstractmethod
from typing import Protocol

# 포트 (인터페이스): ABC 또는 Protocol 사용
class AbstractRepository(ABC):
    @abstractmethod
    def add(self, entity) -> None: ...

    @abstractmethod
    def get(self, reference: str): ...

# Protocol 버전 (상속 불필요)
class RepositoryProtocol(Protocol):
    def add(self, entity) -> None: ...
    def get(self, reference: str): ...

# 어댑터: 실제 구현
class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, entity) -> None:
        self.session.add(entity)

    def get(self, reference: str):
        return self.session.query(Product).filter_by(sku=reference).first()

# 테스트용 가짜 구현
class FakeRepository(AbstractRepository):
    def __init__(self, entities=None):
        self._entities = set(entities or [])

    def add(self, entity) -> None:
        self._entities.add(entity)

    def get(self, reference: str):
        return next((e for e in self._entities if e.sku == reference), None)
```

### 14.2 컨텍스트 매니저로 Unit of Work

```python
from abc import ABC, abstractmethod

class AbstractUnitOfWork(ABC):
    products: AbstractRepository

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()

    @abstractmethod
    def commit(self): ...

    @abstractmethod
    def rollback(self): ...

class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.products = SqlAlchemyRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

# 서비스 레이어에서 사용
def allocate(order_line, uow: AbstractUnitOfWork) -> str:
    with uow:
        product = uow.products.get(order_line.sku)
        if product is None:
            raise InvalidSku(f"유효하지 않은 SKU: {order_line.sku}")
        batch_ref = product.allocate(order_line)
        uow.commit()
    return batch_ref
```

---

## 15. Python 3.14 주요 변경사항

> 출처: [What's New In Python 3.14](https://docs.python.org/3/whatsnew/3.14.html)

### 15.1 어노테이션 지연 평가 (PEP 649)

```python
# Python 3.14: 어노테이션이 더 이상 즉시 평가되지 않음
# from __future__ import annotations 없이도 전방 참조 가능

class Tree:
    def __init__(self, left: 'Tree | None', right: 'Tree | None'):
        ...

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

### 15.2 Template Strings (t-strings) — PEP 750

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
def safe_sql(template: Template) -> str:
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

### 15.3 Subinterpreters와 concurrent.interpreters

```python
import concurrent.interpreters

# 서브인터프리터는 같은 프로세스 내에서 독립된 Python 인터프리터
# multiprocessing과 달리 프로세스 생성 오버헤드 없음
# 각 인터프리터는 독립된 GIL -> 진정한 병렬 실행

interp = concurrent.interpreters.create()
interp.exec("result = sum(range(10_000_000))")

# 인터프리터 간 데이터 교환은 직렬화 필요
# (공유 메모리는 없지만 프로세스 간 통신보다 가벼움)
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

---

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

---

## 출처

### PEP 문서
- [PEP 544 — Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- [PEP 557 — Data Classes](https://peps.python.org/pep-0557/)
- [PEP 612 — Parameter Specification Variables](https://peps.python.org/pep-0612/)
- [PEP 617 — New PEG parser for CPython](https://peps.python.org/pep-0617/)
- [PEP 634 — Structural Pattern Matching: Specification](https://peps.python.org/pep-0634/)
- [PEP 636 — Structural Pattern Matching: Tutorial](https://peps.python.org/pep-0636/)
- [PEP 695 — Type Parameter Syntax](https://peps.python.org/pep-0695/)
- [PEP 698 — Override Decorator for Static Typing](https://peps.python.org/pep-0698/)
- [PEP 702 — Marking deprecations using the type system](https://peps.python.org/pep-0702/)
- [PEP 709 — Inlined comprehensions](https://peps.python.org/pep-0709/)
- [PEP 742 — Narrowing types with TypeIs](https://peps.python.org/pep-0742/)

### Python 공식 문서
- [What's New In Python 3.11](https://docs.python.org/3/whatsnew/3.11.html)
- [What's New In Python 3.12](https://docs.python.org/3/whatsnew/3.12.html)
- [What's New In Python 3.13](https://docs.python.org/3/whatsnew/3.13.html)
- [What's New In Python 3.14](https://docs.python.org/3/whatsnew/3.14.html)
- [typing 모듈 공식 문서](https://docs.python.org/3/library/typing.html)
- [dataclasses 공식 문서](https://docs.python.org/3/library/dataclasses.html)
- [Python free-threading HOWTO](https://docs.python.org/3/howto/free-threading-python.html)

### 서적
- Fluent Python 2nd Edition — Luciano Ramalho (O'Reilly, 2022)
- Python Cookbook 3rd Edition — David Beazley, Brian K. Jones (O'Reilly, 2013)
- Architecture Patterns with Python — Harry Percival, Bob Gregory (O'Reilly, 2020)
- High Performance Python 2nd Edition — Micha Gorelick, Ian Ozsvald (O'Reilly, 2020)

### 도구 문서
- [Ruff 공식 문서](https://docs.astral.sh/ruff/)
- [mypy 문서](https://mypy.readthedocs.io/en/stable/)
- [pyright 문서](https://microsoft.github.io/pyright/)
- [pydantic v2 문서](https://docs.pydantic.dev/latest/)
- [pydantic v2 Migration Guide](https://docs.pydantic.dev/latest/migration/)

### 커뮤니티
- [Real Python — Python 3.13: Free Threading and a JIT Compiler](https://realpython.com/python313-free-threading-jit/)
- [Real Python — Structural Pattern Matching](https://realpython.com/structural-pattern-matching/)
- [Real Python — Python 3.12 New Features](https://realpython.com/python312-new-features/)
- [typing 공식 사양 — Protocols](https://typing.python.org/en/latest/reference/protocols.html)
