# Python 언어 특화 가이드

> Python에서만 적용되는 관례, 패턴, 기법을 정리한 문서.
> 클린코드 범용 원칙(네이밍, 함수 설계, SOLID 등)은 cleancode.md에서 다룬다.

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

- `Optional[X]`는 `Union[X, None]`과 동등하다.
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

result: Union[Snack, Error] = Snack("Hotdog", {"mustard"})
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

### 1.6 제네릭과 TypeVar [단단한 파이썬] [파이썬 버전노트 3.12]

```python
# 3.11 이전
from typing import TypeVar, Generic
T = TypeVar('T')
def reverse(coll: list[T]) -> list[T]:
    return coll[::-1]

# 3.12+ 새 문법 (PEP 695)
def reverse[T](coll: list[T]) -> list[T]:
    return coll[::-1]

type Point = tuple[float, float]           # 타입 알리아스
type Point[T] = tuple[T, T]               # 제네릭 알리아스
```

### 1.7 컬렉션 타입 어노테이션 [단단한 파이썬]

```python
# 나쁜 예: 컬렉션 내부 타입 불명
def process(items: list) -> dict: ...

# 좋은 예: 컬렉션 내부 타입 명시
AuthorCount = dict[str, int]
def process(items: list[Cookbook]) -> AuthorCount: ...
```

### 1.8 @override 데코레이터 (3.12+) [파이썬 버전노트 3.12]

```python
from typing import override

class Base:
    def get_color(self) -> str:
        return "blue"

class GoodChild(Base):
    @override
    def get_color(self) -> str:
        return "yellow"

class BadChild(Base):
    @override
    def get_colour(self) -> str:  # 타입 체커 에러: 오타
        return "red"
```

---

## 2. 컬렉션 선택과 데이터 구조

### 2.1 목적에 맞는 컬렉션 선택 [단단한 파이썬]

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

### 2.2 딕셔너리 키 접근: get과 defaultdict [파이썬코딩의기술]

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

### 2.3 __missing__으로 키별 디폴트 값 생성 [파이썬코딩의기술]

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

### 2.4 정렬: key 파라미터와 튜플 비교 [파이썬코딩의기술]

```python
# 단일 기준
tools.sort(key=lambda x: x.name)

# 다중 기준: 튜플 사용, -로 내림차순 (숫자만)
power_tools.sort(key=lambda x: (-x.weight, x.name))
```

### 2.5 성능 특화 자료구조 [파이썬코딩의기술]

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

## 3. 함수 설계: Python 특화 기법

### 3.1 가변 디폴트 인자의 함정: None 사용 [파이썬코딩의기술]

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

### 3.2 위치 전용(/), 키워드 전용(*) 인자 [파이썬코딩의기술]

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

### 3.3 왈러스 연산자(:=)로 반복 제거 [파이썬코딩의기술]

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

### 3.4 None 반환 대신 예외 발생 [파이썬코딩의기술]

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

### 3.5 언패킹 활용 [파이썬코딩의기술]

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

## 4. 데코레이터

### 4.1 functools.wraps 필수 사용 [파이썬코딩의기술] [슬기로운 파이썬 트릭]

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

### 4.2 데코레이터에 인자 전달 [파이썬 클린코드 2nd]

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

### 4.3 클래스 데코레이터: 메타클래스 대안 [파이썬코딩의기술]

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

## 5. 디스크립터

### 5.1 디스크립터 프로토콜 [파이썬코딩의기술] [파이썬 클린코드 2nd]

디스크립터는 `__get__`, `__set__`, `__delete__`, `__set_name__` 중 하나 이상을 구현한 클래스이다. `@property`의 일반화이며, 재사용 가능한 애트리뷰트 로직에 사용한다.

```python
from weakref import WeakKeyDictionary

class Grade:
    def __init__(self):
        self._values = WeakKeyDictionary()  # 메모리 누수 방지

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return self._values.get(instance, 0)

    def __set__(self, instance, value):
        if not (0 <= value <= 100):
            raise ValueError('0~100 사이여야 합니다')
        self._values[instance] = value

class Exam:
    math_grade = Grade()      # 클래스 속성으로 정의
    writing_grade = Grade()
```

### 5.2 __set_name__으로 중복 제거 (3.6+) [파이썬코딩의기술]

```python
class Field:
    def __init__(self):
        self.name = None
        self.internal_name = None

    def __set_name__(self, owner, name):  # 클래스 정의 시 자동 호출
        self.name = name
        self.internal_name = '_' + name

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return getattr(instance, self.internal_name, '')

    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)

class Customer:
    first_name = Field()  # Field('first_name') 불필요
    last_name = Field()
```

### 5.3 디스크립터를 활용한 유효성 검사 [파이썬 클린코드 2nd]

```python
class Validation:
    def __init__(self, validation_function, error_msg):
        self.validation_function = validation_function
        self.error_msg = error_msg

    def __call__(self, value):
        if not self.validation_function(value):
            raise ValueError(f"{value!r} {self.error_msg}")

class Field:
    def __init__(self, *validations):
        self._name = None
        self.validations = validations

    def __set_name__(self, owner, name):
        self._name = name

    def __set__(self, instance, value):
        for v in self.validations:
            v(value)
        instance.__dict__[self._name] = value

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__[self._name]

class ClientClass:
    descriptor = Field(
        Validation(lambda x: isinstance(x, (int, float)), "는 숫자가 아님"),
        Validation(lambda x: x > 0, "는 0보다 작음"),
    )
```

---

## 6. @property와 애트리뷰트 접근

### 6.1 세터/게터 대신 평범한 애트리뷰트 [파이썬코딩의기술]

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

### 6.2 __getattr__과 __getattribute__ [파이썬코딩의기술]

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

## 7. 클래스 설계: Python 특화 패턴

### 7.1 __call__로 호출 가능한 객체 [파이썬코딩의기술]

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

### 7.2 @classmethod를 팩토리 메서드로 활용 [파이썬코딩의기술] [슬기로운 파이썬 트릭]

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

### 7.3 인스턴스 메서드 vs 클래스 메서드 vs 정적 메서드 [슬기로운 파이썬 트릭]

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

### 7.4 __repr__과 __str__ [슬기로운 파이썬 트릭] [파이썬코딩의기술]

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

### 7.5 비공개(__) 대신 보호(_) 애트리뷰트 [파이썬코딩의기술]

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

### 7.6 __init_subclass__로 하위 클래스 검증 (3.6+) [파이썬코딩의기술]

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

### 7.7 믹스인 클래스 [파이썬코딩의기술]

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

### 7.8 collections.abc로 커스텀 컨테이너 [파이썬코딩의기술] [단단한 파이썬]

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

## 8. Enum, dataclass, NamedTuple, Protocol, pydantic

### 8.1 Enum: 상수 그룹화 [단단한 파이썬]

```python
from enum import Enum, auto

class Position(Enum):
    CHEF = auto()
    SOUS_CHEF = auto()
    SERVER = auto()

# 비교
position = Position.CHEF
if position == Position.CHEF: ...

# 문자열 Enum
class Color(str, Enum):
    RED = 'red'
    BLUE = 'blue'
```

### 8.2 dataclass: 구조화된 데이터 [단단한 파이썬]

```python
from dataclasses import dataclass, field

@dataclass
class Dish:
    name: str
    price_in_cents: int
    description: str
    picture: Optional[str] = None
    tags: list[str] = field(default_factory=list)

# 자동 생성: __init__, __repr__, __eq__
# frozen=True로 불변 데이터클래스 가능
@dataclass(frozen=True)
class Point:
    x: float
    y: float
```

### 8.3 NamedTuple: 불변 레코드 [슬기로운 파이썬 트릭]

```python
from collections import namedtuple

Car = namedtuple('Car', ['color', 'mileage'])
car = Car('red', 3812)
car.color       # 이름으로 접근
car[0]          # 인덱스로도 접근
car._asdict()   # OrderedDict 변환

# typing 버전
from typing import NamedTuple
class Car(NamedTuple):
    color: str
    mileage: float
```

### 8.4 Protocol: 구조적 서브타이핑 (3.8+) [단단한 파이썬] [파이썬 타입 종류 요약]

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

# 프로토콜 합성
class StandardLunchEntry(Splittable, Shareable, Protocol):
    pass

# 런타임 체크
from typing import runtime_checkable

@runtime_checkable
class Splittable(Protocol):
    ...

isinstance(BLTSandwich(), Splittable)  # True
```

**타입 체크 4단계 (약 -> 강)**:
1. Duck Typing: 런타임에만 검증
2. Goose Typing: ABC + abstractmethod로 상속 강제
3. Static Typing: 타입 힌트 + 타입 체커(mypy)
4. Static Duck Typing: Protocol로 구조적 검증

### 8.5 pydantic: 런타임 데이터 검증 [단단한 파이썬]

외부 데이터(API, YAML 등)의 런타임 검증에 사용한다. pydantic은 파싱 라이브러리이다.

```python
from pydantic.dataclasses import dataclass
from pydantic import constr, PositiveInt, validator

@dataclass
class Restaurant:
    name: constr(regex=r'^[a-zA-Z0-9 ]*$', min_length=1, max_length=16)
    owner: constr(min_length=1)
    number_of_seats: PositiveInt
    employees: list[Employee]

    @validator('employees')
    def check_chef(cls, employees):
        if not any(e for e in employees if e.position == 'Chef'):
            raise ValueError('셰프가 최소 1명 필요합니다')
        return employees

# 검증 실패 시 ValidationError 자동 발생
try:
    r = Restaurant(name='Test', owner='A', number_of_seats=-5, employees=[])
except ValidationError:
    ...  # 자동 검증
```

주의: pydantic은 `float -> int` 등 자동 형 변환을 수행한다. 엄격한 타입이 필요하면 `StrictInt`, `StrictStr` 등을 사용하라.

---

## 9. 이터레이터, 제너레이터, 컴프리헨션

### 9.1 이터레이터 프로토콜 [슬기로운 파이썬 트릭] [파이썬 클린코드 2nd]

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

### 9.2 리스트 대신 제너레이터 [파이썬코딩의기술] [파이썬 클린코드 2nd]

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

### 9.3 제너레이터 식 [파이썬코딩의기술] [파이썬 클린코드 2nd]

```python
# 리스트 컴프리헨션 -> 메모리 전부 사용
total = sum([x ** 2 for x in range(10)])

# 제너레이터 식 -> 메모리 절약
total = sum(x ** 2 for x in range(10))

# 제너레이터 식 합성
it = (len(x) for x in open('file.txt'))
roots = ((x, x ** 0.5) for x in it)
```

### 9.4 yield from으로 제너레이터 합성 [파이썬코딩의기술]

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

### 9.5 send, throw 사용 금지 [파이썬코딩의기술]

제너레이터의 `send()`와 `throw()`는 양방향 통신을 제공하지만 가독성이 매우 나쁘다. 대신 이터레이터를 입력으로 전달하거나 상태를 가진 클래스를 사용하라.

### 9.6 itertools 활용 [파이썬코딩의기술]

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

---

## 10. 컨텍스트 매니저와 with문

### 10.1 커스텀 컨텍스트 매니저 [파이썬코딩의기술] [슬기로운 파이썬 트릭]

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

### 10.2 with문 활용 패턴 [파이썬코딩의기술] [슬기로운 파이썬 트릭]

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

## 11. 예외 처리

### 11.1 try/except/else/finally 각 블록 활용 [파이썬코딩의기술]

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

### 11.2 최상위 예외 클래스 정의 [파이썬코딩의기술]

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

### 11.3 warnings로 마이그레이션 안내 [파이썬코딩의기술]

```python
import warnings

def old_function(distance_units=None):
    if distance_units is None:
        warnings.warn(
            'distance_units 파라미터가 필요합니다',
            DeprecationWarning
        )
```

---

## 12. 동시성과 병렬성

### 12.1 GIL과 스레드 선택 기준 [파이썬코딩의기술]

- **GIL**: CPython에서 한 번에 하나의 스레드만 바이트코드 실행. CPU 바운드 작업은 스레드로 병렬화 불가.
- **스레드 사용**: 블로킹 I/O 시 (파일, 네트워크). GIL은 시스템 콜 전에 해제됨.
- **CPU 병렬화**: `subprocess`, `multiprocessing`, C 확장 사용.

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

### 12.2 ThreadPoolExecutor [파이썬코딩의기술]

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=10) as pool:
    future = pool.submit(task_function, *args)
    result = future.result()  # 예외도 자동 전파
```

### 12.3 asyncio 코루틴 [파이썬코딩의기술]

높은 I/O 동시성이 필요하면 코루틴을 사용하라. 시작 비용 함수 호출 수준, 메모리 1KB 미만.

```python
import asyncio

async def fetch_data(url):
    ...  # await로 비동기 I/O
    return data

async def main():
    results = await asyncio.gather(
        fetch_data(url1),
        fetch_data(url2),
    )
```

### 12.4 Queue로 스레드 간 작업 조율 [파이썬코딩의기술]

```python
from queue import Queue

queue = Queue(maxsize=10)  # 버퍼 크기 제한 -> 메모리 폭발 방지
queue.put(item)            # 가득 차면 블록
queue.get()                # 비어 있으면 블록
```

---

## 13. 파이썬다운 관용 표현

### 13.1 f-문자열 사용 [파이썬코딩의기술]

```python
# 나쁜 예: % 포매팅, str.format()
print('결과: %d' % value)
print('결과: {}'.format(value))

# 좋은 예: f-문자열 (3.6+)
print(f'결과: {value}')
print(f'{number:.{places}f}')  # 형식 지정도 가능
```

### 13.2 enumerate, zip 활용 [파이썬코딩의기술]

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

### 13.3 빈 컨테이너 검사 [파이썬코딩의기술]

```python
# 나쁜 예
if len(container) == 0: ...
if len(container) > 0: ...

# 좋은 예: 암묵적 불리언 평가
if not container: ...   # 비어 있음
if container: ...       # 비어 있지 않음
```

### 13.4 bytes와 str 분리 (유니코드 샌드위치) [파이썬코딩의기술]

인코딩/디코딩은 인터페이스의 가장 먼 경계에서 수행하라.

```python
def to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        return bytes_or_str.decode('utf-8')
    return bytes_or_str
```

### 13.5 for/while 뒤 else 금지 [파이썬코딩의기술]

루프 뒤 else 블록은 루프가 완료되면 실행된다. 직관에 반하므로 사용하지 마라.

### 13.6 밑줄 관례 [슬기로운 파이썬 트릭]

| 패턴 | 의미 |
|------|------|
| `_var` | 관례적 보호(protected). 와일드카드 import에서 제외 |
| `var_` | 파이썬 키워드와 이름 충돌 회피 (`class_`) |
| `__var` | 네임 맹글링. 하위 클래스 충돌 방지 전용 |
| `__var__` | 매직 메서드/던더. 파이썬 예약 |
| `_` | 임시/무시 변수 (`for _ in range(10)`) |

---

## 14. 디자인 패턴 (Python 구현)

### 14.1 팩토리 메서드 [Python 디자인패턴]

```python
from abc import ABC, abstractmethod

class PizzaStore(ABC):
    def order_pizza(self, type: str):
        pizza = self.create_pizza(type)  # 하위 클래스에서 결정
        pizza.prepare()
        pizza.bake()
        pizza.cut()
        pizza.box()
        return pizza

    @abstractmethod
    def create_pizza(self, type: str) -> Pizza:
        pass

class NYPizzaStore(PizzaStore):
    def create_pizza(self, type: str) -> Pizza:
        if type == 'cheese':
            return NYCheesePizza()
        ...
```

핵심: 객체 생성을 서브클래스에 위임하여 생성과 사용을 분리한다.

### 14.2 추상 팩토리 [Python 디자인패턴]

```python
class PizzaIngredientFactory(ABC):
    @abstractmethod
    def createDough(self) -> Dough: ...
    @abstractmethod
    def createSauce(self) -> Sauce: ...

class NYPizzaIngredientFactory(PizzaIngredientFactory):
    def createDough(self):
        return ThinCrustDough()
    def createSauce(self):
        return MarinaraSauce()

class CheesePizza(Pizza):
    def __init__(self, factory: PizzaIngredientFactory):
        self.factory = factory
    def prepare(self):
        self.dough = self.factory.createDough()
        self.sauce = self.factory.createSauce()
```

핵심: 인터페이스를 이용하여 서로 연관된 객체를 구상 클래스를 지정하지 않고 생성한다.

---

## 15. 테스트와 디버깅

### 15.1 unittest.mock 활용 [파이썬코딩의기술]

```python
from unittest.mock import Mock, ANY

mock = Mock(spec=get_animals)
mock.return_value = expected_data

result = mock('database', '미어캣')
mock.assert_called_once_with(ANY, '미어캣')

# 예외 모킹
mock.side_effect = MyError("문제 발생")
```

### 15.2 디버깅: repr 사용 [파이썬코딩의기술]

```python
# 나쁜 예: 타입 구분 불가
print(value)   # 5 (int? str?)

# 좋은 예: repr로 타입 명확히
print(repr(value))  # 5 또는 '5'
```

### 15.3 프로파일링 [파이썬코딩의기술]

최적화 전에 반드시 프로파일링하라.

```python
from cProfile import Profile
from pstats import Stats

profiler = Profile()
profiler.runcall(test_function)

stats = Stats(profiler)
stats.strip_dirs()
stats.sort_stats('cumulative')
stats.print_stats()
```

---

## 16. 독스트링과 문서화

### 16.1 독스트링 규칙 [파이썬코딩의기술]

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
- 타입 어노테이션과 중복되면 둘 중 하나만 유지

### 16.2 __doc__ 접근 [파이썬코딩의기술]

```python
print(find_anagrams.__doc__)  # 런타임에 독스트링 접근 가능
help(find_anagrams)            # 대화형에서 문서 확인
```

---

## 17. 정밀 연산

### 17.1 Decimal과 Fraction [파이썬코딩의기술]

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

## 부록: 주요 매직 메서드 요약

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
| `__add__` / `__mul__` 등 | 산술 연산 |
| `__bool__` | 불리언 변환 (`if obj:`) |
