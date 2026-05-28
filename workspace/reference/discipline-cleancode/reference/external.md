# Python 클린코드: 외부 권위 자료 종합 가이드

> **목적**: 내부 자료(Clean Code, 구현 패턴, 객체지향의 사실과 오해, 파이썬 클린코드 2nd)에서 다루지 않은, 공식/권위 있는 외부 자료의 핵심 원칙과 기법을 Python 코드 예시와 함께 종합 정리한다.

---

## 목차

1. [PEP 문서 (Python 공식)](#1-pep-문서-python-공식)
2. [Refactoring (Martin Fowler)](#2-refactoring-martin-fowler)
3. [A Philosophy of Software Design (John Ousterhout)](#3-a-philosophy-of-software-design-john-ousterhout)
4. [Code Complete (Steve McConnell)](#4-code-complete-steve-mcconnell)
5. [The Pragmatic Programmer (Thomas & Hunt)](#5-the-pragmatic-programmer-thomas--hunt)
6. [Working Effectively with Legacy Code (Michael Feathers)](#6-working-effectively-with-legacy-code-michael-feathers)
7. [Google Python Style Guide](#7-google-python-style-guide)
8. [커뮤니티 베스트 프랙티스](#8-커뮤니티-베스트-프랙티스)

---

## 1. PEP 문서 (Python 공식)

### 1.1 PEP 20 -- The Zen of Python

> 출처: [PEP 20](https://peps.python.org/pep-0020/)

Tim Peters가 1999년에 작성한 Python 설계 철학의 20가지 격언 중 19가지가 기록됨. `import this`로 확인 가능.

```
Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
Special cases aren't special enough to break the rules.
Although practicality beats purity.
Errors should never pass silently.
Unless explicitly silenced.
In the face of ambiguity, refuse the temptation to guess.
There should be one-- and preferably only one --obvious way to do it.
Although that way may not be obvious at first unless you're Dutch.
Now is better than never.
Although never is often better than *right* now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those!
```

**클린코드에 직접 적용되는 핵심 격언들:**

| 격언 | 클린코드 적용 |
|------|-------------|
| Explicit is better than implicit | 암묵적 동작보다 명시적 코드를 작성하라 |
| Simple is better than complex | 단순한 해법이 있으면 복잡한 방식을 피하라 |
| Flat is better than nested | 깊은 중첩을 피하고 평탄한 구조를 유지하라 |
| Readability counts | 코드는 쓰는 횟수보다 읽는 횟수가 훨씬 많다 |
| Errors should never pass silently | 오류를 묵묵히 삼키지 마라 |
| There should be one obvious way | 한 가지 일을 하는 하나의 명확한 방법을 택하라 |
| If the implementation is hard to explain, it's a bad idea | 설명하기 어려운 구현은 나쁜 설계의 신호다 |

```python
# 나쁜 예: Implicit (암묵적)
def process(data, flag=True):
    if flag:
        return [x * 2 for x in data if x]  # flag가 뭘 의미하는지 불명확
    return data

# 좋은 예: Explicit (명시적)
def double_nonzero_values(values: list[int]) -> list[int]:
    return [value * 2 for value in values if value != 0]

def passthrough(values: list[int]) -> list[int]:
    return values
```

```python
# 나쁜 예: Nested (깊은 중첩)
def get_user_email(response):
    if response:
        if response.data:
            if response.data.user:
                if response.data.user.email:
                    return response.data.user.email
    return None

# 좋은 예: Flat (평탄한 구조) -- Guard Clause 사용
def get_user_email(response):
    if not response:
        return None
    if not response.data:
        return None
    if not response.data.user:
        return None
    return response.data.user.email
```

---

### 1.2 PEP 8 -- Style Guide for Python Code

> 출처: [PEP 8](https://peps.python.org/pep-0008/)

#### 1.2.1 코드 레이아웃

**들여쓰기**: 4칸 스페이스. 탭과 스페이스를 절대 혼용하지 않는다.

```python
# 좋은 예: 여는 구분자에 맞춘 정렬
foo = long_function_name(var_one, var_two,
                         var_three, var_four)

# 좋은 예: 행잉 인덴트 (4칸 추가 들여쓰기)
def long_function_name(
        var_one, var_two,
        var_three, var_four):
    print(var_one)
```

**최대 줄 길이**: 코드 79자, 주석/독스트링 72자.

```python
# 나쁜 예: 한 줄이 너무 긴 경우
result = some_function(argument_one, argument_two, argument_three, argument_four, argument_five, argument_six)

# 좋은 예: 백슬래시 또는 괄호를 이용한 줄 바꿈
result = some_function(
    argument_one, argument_two,
    argument_three, argument_four,
    argument_five, argument_six,
)
```

**빈 줄**: 최상위 정의(함수, 클래스) 사이에는 2줄, 클래스 내 메서드 사이에는 1줄.

#### 1.2.2 임포트 규칙

```python
# 나쁜 예: 한 줄에 여러 모듈
import os, sys
from math import *  # 와일드카드 임포트 금지

# 좋은 예: 한 줄에 하나, 그룹별 빈 줄 구분
import os
import sys

from third_party_lib import some_module

from my_project.utils import helper
```

**임포트 그룹 순서** (각 그룹 사이에 빈 줄):
1. 표준 라이브러리 (`os`, `sys`, `pathlib`)
2. 서드파티 라이브러리 (`requests`, `numpy`)
3. 로컬 프로젝트 모듈

**절대 임포트를 권장**하되, 복잡한 패키지 레이아웃에서는 명시적 상대 임포트도 허용.

```python
# 권장: 절대 임포트
from my_package.submodule import my_function

# 허용: 명시적 상대 임포트 (패키지 내부에서)
from .submodule import my_function

# 금지: 와일드카드 임포트
from module import *  # 네임스페이스를 오염시킨다
```

#### 1.2.3 공백 규칙

```python
# 나쁜 예
spam( ham[ 1 ], { eggs: 2 } )
x             = 1
long_variable = 2

# 좋은 예
spam(ham[1], {eggs: 2})
x = 1
long_variable = 2
```

```python
# 나쁜 예: 키워드 인자와 기본값에 공백
def complex(real, imag = 0.0):
    return magic(r = real, i = imag)

# 좋은 예
def complex(real, imag=0.0):
    return magic(r=real, i=imag)
```

**단, 어노테이션이 있는 기본값에는 공백을 넣는다:**
```python
def munge(sep: str = None): ...
def munge(input: AnyStr, sep: AnyStr = None, limit=1000): ...
```

#### 1.2.4 명명 규칙

| 대상 | 스타일 | 예시 |
|------|--------|------|
| 모듈 | snake_case | `my_module.py` |
| 패키지 | lowercase | `mypackage` |
| 클래스 | PascalCase | `MyClass` |
| 예외 | PascalCase + Error 접미사 | `ValueError` |
| 함수/메서드 | snake_case | `calculate_total()` |
| 변수 | snake_case | `user_count` |
| 상수 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 내부 사용 | `_` 접두사 | `_internal_helper()` |
| 이름 충돌 회피 | `_` 접미사 | `class_` |

#### 1.2.5 프로그래밍 권장사항

**싱글톤 비교는 `is`/`is not` 사용:**
```python
# 나쁜 예
if result == None:
    ...

# 좋은 예
if result is None:
    ...
```

**불리언 비교를 `==`로 하지 않는다:**
```python
# 나쁜 예
if greeting == True:
    ...
if greeting is True:  # 이것도 불필요
    ...

# 좋은 예
if greeting:
    ...
```

**`not ... is` 대신 `is not` 사용:**
```python
# 나쁜 예
if not foo is None:
    ...

# 좋은 예
if foo is not None:
    ...
```

**bare `except` 금지 -- 구체적인 예외를 명시하라:**
```python
# 나쁜 예
try:
    do_something()
except:
    pass

# 좋은 예
try:
    do_something()
except ValueError as e:
    logger.warning("Invalid value: %s", e)
```

**타입 비교에는 `isinstance()` 사용:**
```python
# 나쁜 예
if type(obj) is int:
    ...

# 좋은 예
if isinstance(obj, int):
    ...
```

**시퀀스의 비어있음 검사 -- 암묵적 falsiness 활용:**
```python
# 나쁜 예
if len(my_list) == 0:
    ...

# 좋은 예
if not my_list:
    ...
```

**문자열 접두사/접미사 검사:**
```python
# 나쁜 예
if foo[:3] == 'bar':
    ...

# 좋은 예
if foo.startswith('bar'):
    ...
```

---

### 1.3 PEP 257 -- Docstring Conventions

> 출처: [PEP 257](https://peps.python.org/pep-0257/)

**항상 `"""삼중 쌍따옴표"""`를 사용한다.**

#### 한 줄 독스트링

```python
def trim(s: str) -> str:
    """Remove leading and trailing whitespace."""
    return s.strip()
```

- 여는 `"""`와 닫는 `"""`가 같은 줄에 위치
- 마침표로 끝나는 명령형 문장 ("Do X and return Y.")
- 함수 시그니처를 반복하지 않는다

#### 여러 줄 독스트링

```python
def fetch_user(user_id: int) -> User:
    """Fetch a user by their unique identifier.

    Queries the database for the user matching the given ID.
    Raises UserNotFoundError if no matching user exists.

    Args:
        user_id: The unique identifier of the user to fetch.

    Returns:
        The User object corresponding to the given ID.

    Raises:
        UserNotFoundError: If no user with the given ID exists.
        DatabaseConnectionError: If the database is unreachable.
    """
    ...
```

- 요약 줄 + 빈 줄 + 상세 설명
- 닫는 `"""`는 별도의 줄에 위치
- 클래스 독스트링에는 공개 메서드와 인스턴스 변수 요약 포함

**독스트링 유형별 작성 대상:**

| 대상 | 내용 |
|------|------|
| 모듈 | 내보내는 클래스, 예외, 함수의 한 줄 요약 |
| 클래스 | 동작 요약, 공개 메서드, 인스턴스 변수 |
| 함수/메서드 | 동작, 인자, 반환값, 부작용, 예외, 호출 제약 |
| 스크립트 | "사용법" 메시지 (명령행 구문, 환경 변수, 파일) |

---

### 1.4 PEP 3107 / PEP 484 / PEP 526 -- 타입 힌트 체계

> 출처: [PEP 3107](https://peps.python.org/pep-3107/), [PEP 484](https://peps.python.org/pep-0484/), [PEP 526](https://peps.python.org/pep-0526/)

**PEP 3107** (Python 3.0): 함수 어노테이션의 문법적 기반 도입.
**PEP 484** (Python 3.5): 타입 힌트의 의미론적 표준화, `typing` 모듈 도입.
**PEP 526** (Python 3.6): 변수 어노테이션 문법 (`변수: 타입`) 도입.

#### 기본 문법

```python
# 함수 파라미터와 반환 타입 (PEP 484)
def greet(name: str) -> str:
    return f"Hello, {name}!"

# 변수 어노테이션 (PEP 526)
count: int = 0
names: list[str] = []
captain: str  # 초기값 없이 타입만 선언 가능
```

#### 고급 타입 힌트

```python
from typing import Optional, Union, Callable, TypeVar

# Optional: None이 될 수 있는 값
def find_user(user_id: int) -> Optional[User]:
    """User를 찾거나 None을 반환한다."""
    ...

# Union: 여러 타입 중 하나
def process(value: Union[str, int]) -> str:
    return str(value)

# Python 3.10+ 에서는 | 연산자 사용 가능
def process(value: str | int) -> str:
    return str(value)

# Callable: 콜백/함수 타입
def apply(func: Callable[[int, int], int], a: int, b: int) -> int:
    return func(a, b)

# TypeVar: 제네릭
T = TypeVar('T')

def first(items: list[T]) -> T:
    return items[0]
```

#### 클래스 변수 vs 인스턴스 변수 (PEP 526)

```python
from typing import ClassVar

class Starship:
    # 클래스 변수
    stats: ClassVar[dict[str, int]] = {}
    damage: ClassVar[int] = 10

    # 인스턴스 변수 (ClassVar 없음)
    shield: int
    name: str

    def __init__(self, name: str) -> None:
        self.name = name
        self.shield = 100
```

#### 타입 힌트 적용 원칙

- 타입 힌트는 **런타임에 무시**된다 -- 정적 분석 도구(mypy, pyright)용
- 공개 API에는 반드시 타입 힌트를 추가한다
- 내부 구현에서도 복잡한 로직에는 타입 힌트로 의도를 명확히 한다
- `Any`는 최후의 수단으로만 사용한다

---

## 2. Refactoring (Martin Fowler)

> 출처: "Refactoring: Improving the Design of Existing Code" 2nd Edition (Martin Fowler, 2018)
> 참고: [refactoring.com/catalog](https://refactoring.com/catalog/), [martinfowler.com/bliki/CodeSmell](https://martinfowler.com/bliki/CodeSmell.html)

### 2.1 코드 스멜 카탈로그

코드 스멜(code smell)은 더 깊은 문제를 나타내는 표면적 징후다. Kent Beck과 함께 정리한 이 목록은 리팩토링의 출발점이 된다.

#### 비대화 스멜 (Bloaters)

| 스멜 | 설명 | Python 예시 |
|------|------|-------------|
| **Long Method** | 메서드가 너무 길어 이해하기 어렵다 | 50줄 이상의 함수 |
| **Long Parameter List** | 파라미터가 너무 많다 | `def f(a, b, c, d, e, f, g):` |
| **Large Class** | 한 클래스가 너무 많은 책임을 진다 | 500줄 이상의 클래스 |
| **Primitive Obsession** | 원시 타입에 지나치게 의존한다 | 금액을 `float`로만 표현 |
| **Data Clumps** | 같은 데이터 그룹이 반복 등장한다 | `(x, y, z)` 좌표를 개별 변수로 전달 |

```python
# 코드 스멜: Primitive Obsession
def calculate_price(amount: float, currency: str) -> str:
    if currency == "USD":
        return f"${amount:.2f}"
    elif currency == "KRW":
        return f"{amount:,.0f}원"
    ...

# 리팩토링: 값 객체(Value Object) 도입
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def display(self) -> str:
        formats = {
            "USD": lambda a: f"${a:.2f}",
            "KRW": lambda a: f"{a:,.0f}원",
        }
        formatter = formats.get(self.currency, lambda a: f"{a} {self.currency}")
        return formatter(self.amount)
```

```python
# 코드 스멜: Data Clumps
def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

# 리팩토링: Introduce Parameter Object
@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        return ((other.x - self.x) ** 2 + (other.y - self.y) ** 2) ** 0.5
```

#### 객체지향 남용 스멜 (OO Abusers)

| 스멜 | 설명 |
|------|------|
| **Refused Bequest** | 하위 클래스가 상속받은 메서드/속성 중 일부만 사용 |
| **Alternative Classes with Different Interfaces** | 같은 일을 하지만 인터페이스가 다른 클래스들 |
| **Temporary Field** | 특정 상황에서만 사용되는 인스턴스 변수 |

```python
# 코드 스멜: Refused Bequest
class Animal:
    def walk(self): ...
    def swim(self): ...
    def fly(self): ...

class Dog(Animal):
    def walk(self): ...
    def swim(self): ...
    def fly(self):
        raise NotImplementedError  # 개는 날 수 없다 -- 거부된 유산

# 리팩토링: 인터페이스 분리 (Protocol 사용)
from typing import Protocol

class Walkable(Protocol):
    def walk(self) -> None: ...

class Swimmable(Protocol):
    def swim(self) -> None: ...

class Flyable(Protocol):
    def fly(self) -> None: ...

class Dog:
    def walk(self) -> None: ...
    def swim(self) -> None: ...
    # fly는 필요 없으므로 구현하지 않는다
```

#### 변경 방해 스멜 (Change Preventers)

| 스멜 | 설명 |
|------|------|
| **Divergent Change** | 하나의 클래스가 여러 이유로 변경된다 (SRP 위반) |
| **Shotgun Surgery** | 하나의 변경이 여러 클래스에 산발적으로 영향 |
| **Parallel Inheritance Hierarchies** | 한 계층에 클래스를 추가하면 다른 계층에도 추가해야 한다 |

```python
# 코드 스멜: Shotgun Surgery
# 세금 계산 방식이 바뀌면 여러 곳을 수정해야 한다
class Order:
    def total_with_tax(self):
        return self.subtotal * 1.1  # 세율 하드코딩

class Invoice:
    def tax_amount(self):
        return self.amount * 0.1  # 같은 세율이 다른 곳에도

class Report:
    def estimated_tax(self):
        return self.revenue * 0.1  # 또 여기에도

# 리팩토링: Move Method -- 세금 로직을 한 곳으로 집중
class TaxCalculator:
    RATE = 0.1

    @classmethod
    def calculate(cls, amount: float) -> float:
        return amount * cls.RATE

class Order:
    def total_with_tax(self):
        return self.subtotal + TaxCalculator.calculate(self.subtotal)
```

#### 불필요한 것들 (Dispensables)

| 스멜 | 설명 |
|------|------|
| **Speculative Generality** | "나중에 필요할지도 모른다"는 이유로 추가한 미사용 추상화 |
| **Dead Code** | 실행되지 않는 코드 |
| **Lazy Class** | 하는 일이 너무 적어 존재 이유가 없는 클래스 |
| **Duplicated Code** | 같은 코드 구조의 반복 |

```python
# 코드 스멜: Speculative Generality
class AbstractDataProcessor:
    """미래를 위해 만든 추상 클래스 -- 현재 구현체는 하나뿐"""
    def process(self, data): raise NotImplementedError
    def validate(self, data): raise NotImplementedError
    def transform(self, data): raise NotImplementedError
    def serialize(self, data): raise NotImplementedError

class CSVProcessor(AbstractDataProcessor):
    # 유일한 구현체
    ...

# 리팩토링: 실제로 필요할 때까지 추상화를 미룬다 (YAGNI)
class CSVProcessor:
    def process(self, data): ...
    # 두 번째 구현체가 필요해질 때 공통 인터페이스를 추출한다
```

#### 커플러 스멜 (Couplers)

| 스멜 | 설명 |
|------|------|
| **Feature Envy** | 메서드가 자기 클래스보다 다른 클래스의 데이터를 더 많이 사용 |
| **Middle Man** | 메서드 대부분이 다른 객체에 위임만 한다 |
| **Inappropriate Intimacy** | 두 클래스가 서로의 내부를 지나치게 탐색 |
| **Message Chains** | `a.b().c().d()` 식의 긴 호출 체인 (디미터 법칙 위반) |

```python
# 코드 스멜: Feature Envy
class OrderPrinter:
    def print_details(self, order):
        # order의 내부를 지나치게 탐색
        print(f"Customer: {order.customer.name}")
        print(f"Address: {order.customer.address.street}")
        print(f"Total: {order.total()}")
        print(f"Tax: {order.total() * order.tax_rate}")

# 리팩토링: Move Method -- 해당 데이터를 가진 객체에 로직을 이동
class Order:
    def format_details(self) -> str:
        return (
            f"Customer: {self.customer.name}\n"
            f"Address: {self.customer.format_address()}\n"
            f"Total: {self.total()}\n"
            f"Tax: {self.calculate_tax()}"
        )
```

### 2.2 주요 리팩토링 기법 카탈로그

> 출처: [refactoring.com/catalog](https://refactoring.com/catalog/)

#### 메서드 구성 (Composing Methods)

```python
# Extract Method: 코드 블록을 의미 있는 이름의 함수로 추출
# Before
def print_owing(self):
    # 배너 출력
    print("*" * 40)
    print("****** Customer Owes ******")
    print("*" * 40)

    # 미결 금액 계산
    outstanding = 0.0
    for order in self.orders:
        outstanding += order.amount

    # 상세 출력
    print(f"name: {self.name}")
    print(f"amount: {outstanding}")

# After
def print_owing(self):
    self._print_banner()
    outstanding = self._calculate_outstanding()
    self._print_details(outstanding)

def _print_banner(self):
    print("*" * 40)
    print("****** Customer Owes ******")
    print("*" * 40)

def _calculate_outstanding(self) -> float:
    return sum(order.amount for order in self.orders)

def _print_details(self, outstanding: float):
    print(f"name: {self.name}")
    print(f"amount: {outstanding}")
```

```python
# Replace Temp with Query: 임시 변수를 메서드 호출로 대체
# Before
def get_price(self):
    base_price = self.quantity * self.item_price
    if base_price > 1000:
        discount_factor = 0.95
    else:
        discount_factor = 0.98
    return base_price * discount_factor

# After
def get_price(self):
    return self._base_price * self._discount_factor

@property
def _base_price(self) -> float:
    return self.quantity * self.item_price

@property
def _discount_factor(self) -> float:
    return 0.95 if self._base_price > 1000 else 0.98
```

#### 조건문 단순화 (Simplifying Conditionals)

```python
# Decompose Conditional: 복잡한 조건을 의미 있는 함수로 분해
# Before
def calculate_charge(self, date, quantity):
    if date.month >= 6 and date.month <= 9:
        charge = quantity * self.summer_rate
    else:
        charge = quantity * self.winter_rate + self.winter_service_charge
    return charge

# After
def calculate_charge(self, date, quantity):
    if self._is_summer(date):
        return self._summer_charge(quantity)
    return self._winter_charge(quantity)

def _is_summer(self, date) -> bool:
    return 6 <= date.month <= 9

def _summer_charge(self, quantity) -> float:
    return quantity * self.summer_rate

def _winter_charge(self, quantity) -> float:
    return quantity * self.winter_rate + self.winter_service_charge
```

```python
# Replace Conditional with Polymorphism: 조건문을 다형성으로 대체
# Before
class Bird:
    def speed(self):
        if self.type == "european":
            return self._base_speed
        elif self.type == "african":
            return self._base_speed - self._load_factor * self.coconuts
        elif self.type == "norwegian_blue":
            return 0 if self.is_nailed else self._base_speed * self.voltage
        raise ValueError(f"Unknown bird type: {self.type}")

# After
class Bird:
    def speed(self) -> float:
        raise NotImplementedError

class EuropeanSwallow(Bird):
    def speed(self) -> float:
        return self._base_speed

class AfricanSwallow(Bird):
    def speed(self) -> float:
        return self._base_speed - self._load_factor * self.coconuts

class NorwegianBlueParrot(Bird):
    def speed(self) -> float:
        return 0 if self.is_nailed else self._base_speed * self.voltage
```

#### Replace Nested Conditional with Guard Clauses

```python
# Before
def get_pay_amount(self):
    if self.is_dead:
        result = self.dead_amount()
    else:
        if self.is_separated:
            result = self.separated_amount()
        else:
            if self.is_retired:
                result = self.retired_amount()
            else:
                result = self.normal_amount()
    return result

# After (Guard Clauses)
def get_pay_amount(self):
    if self.is_dead:
        return self.dead_amount()
    if self.is_separated:
        return self.separated_amount()
    if self.is_retired:
        return self.retired_amount()
    return self.normal_amount()
```

---

## 3. A Philosophy of Software Design (John Ousterhout)

> 출처: "A Philosophy of Software Design" 2nd Edition (John Ousterhout, 2021)
> 참고: [blog.pragmaticengineer.com](https://blog.pragmaticengineer.com/a-philosophy-of-software-design-review/)

### 3.1 복잡성의 본질

소프트웨어 설계의 근본 문제는 **복잡성 관리**다. 복잡성이란 시스템을 이해하고 수정하기 어렵게 만드는 구조적 특성이다.

#### 복잡성의 세 가지 발현

| 발현 | 설명 | Python 예시 |
|------|------|-------------|
| **Change Amplification** | 단순한 변경이 여러 곳의 수정을 요구 | 색상 상수가 10개 파일에 분산 |
| **Cognitive Load** | 한 작업을 완료하기 위해 알아야 할 것이 많다 | 함수 호출을 위해 5개 모듈의 상태를 이해해야 함 |
| **Unknown Unknowns** | 무엇을 해야 하는지, 제안된 해법이 올바른지조차 불분명 | 숨겨진 의존성이나 암묵적 규칙 |

#### 복잡성의 두 가지 근원

- **의존성(dependencies)**: 코드를 고립적으로 이해하고 수정할 수 없는 상태
- **모호성(obscurity)**: 중요한 정보가 명확하지 않은 상태

### 3.2 깊은 모듈 vs 얕은 모듈

**Ousterhout의 핵심 개념**: 최고의 모듈은 강력한 기능을 제공하면서 단순한 인터페이스를 갖는다.

```
깊은 모듈 (Deep Module)        얕은 모듈 (Shallow Module)
┌─────────┐                    ┌─────────────────────────┐
│Interface│ <- 단순             │        Interface        │ <- 복잡
├─────────┤                    ├─────────────────────────┤
│         │                    │ Implementation          │ <- 단순
│ Impl.   │ <- 복잡 (숨김)      └─────────────────────────┘
│         │
│         │
└─────────┘
```

```python
# 얕은 모듈: 인터페이스가 구현만큼 복잡하다
class FileReader:
    def open(self, path: str) -> None: ...
    def check_permissions(self, path: str) -> bool: ...
    def read_bytes(self, offset: int, length: int) -> bytes: ...
    def decode(self, data: bytes, encoding: str) -> str: ...
    def close(self) -> None: ...

# 사용하려면 호출자가 5단계를 전부 알아야 한다
reader = FileReader()
reader.open("data.txt")
if reader.check_permissions("data.txt"):
    raw = reader.read_bytes(0, 1024)
    text = reader.decode(raw, "utf-8")
    reader.close()

# 깊은 모듈: 단순한 인터페이스 뒤에 복잡성을 숨긴다
from pathlib import Path

def read_text(path: str, encoding: str = "utf-8") -> str:
    """파일을 읽어 텍스트로 반환한다. 권한, 인코딩, 리소스 정리를 내부에서 처리."""
    return Path(path).read_text(encoding=encoding)

# 호출자는 한 줄이면 된다
text = read_text("data.txt")
```

### 3.3 정보 은닉 (Information Hiding)

깊은 모듈을 달성하는 가장 중요한 기법이다. 설계 결정과 내부 정보를 인터페이스 뒤에 캡슐화하여 외부에 노출하지 않는다.

```python
# 나쁜 예: Information Leakage (정보 누출)
# 두 모듈이 같은 파일 형식 지식을 공유한다
class CSVReader:
    def read(self, path: str) -> list[list[str]]:
        with open(path) as f:
            # CSV 파싱 세부사항이 노출됨
            return [line.strip().split(",") for line in f]

class CSVWriter:
    def write(self, path: str, rows: list[list[str]]) -> None:
        with open(path, "w") as f:
            for row in rows:
                # 같은 CSV 형식 지식이 여기에도
                f.write(",".join(row) + "\n")

# 좋은 예: 형식 지식을 한 모듈에 집중
class CSVFormat:
    DELIMITER = ","
    LINE_ENDING = "\n"

    @classmethod
    def parse_row(cls, line: str) -> list[str]:
        return line.strip().split(cls.DELIMITER)

    @classmethod
    def format_row(cls, fields: list[str]) -> str:
        return cls.DELIMITER.join(fields) + cls.LINE_ENDING
```

### 3.4 전략적 프로그래밍 vs 전술적 프로그래밍

| 전술적 (Tactical) | 전략적 (Strategic) |
|-------------------|-------------------|
| "동작하면 된다, 다음 작업으로" | "훌륭한 설계를 만들자, 동작도 당연히 해야 한다" |
| 단기적 속도 | 장기적 생산성에 투자 |
| 복잡성 누적 -> 기능 추가 비용 증가 | 복잡성 통제 -> 지속적으로 빠른 기능 추가 |

**전술적 토네이도(Tactical Tornado)**: 다른 사람보다 훨씬 빠르게 코드를 쏟아내지만, 완전히 전술적(임기응변적)으로 작업하는 프로그래머. 그들이 남긴 코드는 다른 개발자가 유지보수해야 한다.

```python
# 전술적 프로그래밍: "일단 돌아가게 만들자"
def handle_request(req):
    # TODO: 나중에 리팩토링
    if req.get("type") == "A":
        data = req.get("data", {})
        result = data.get("value", 0) * 2
        if req.get("format") == "json":
            return {"result": result}
        return str(result)
    elif req.get("type") == "B":
        # A와 거의 같지만 약간 다름...
        data = req.get("data", {})
        result = data.get("value", 0) * 3  # 여기만 다름
        if req.get("format") == "json":
            return {"result": result}
        return str(result)
    # ... 계속 확장

# 전략적 프로그래밍: 설계에 투자
from dataclasses import dataclass
from typing import Protocol

class RequestHandler(Protocol):
    def compute(self, value: float) -> float: ...

@dataclass
class TypeAHandler:
    multiplier: float = 2.0
    def compute(self, value: float) -> float:
        return value * self.multiplier

@dataclass
class TypeBHandler:
    multiplier: float = 3.0
    def compute(self, value: float) -> float:
        return value * self.multiplier

class RequestRouter:
    def __init__(self):
        self._handlers: dict[str, RequestHandler] = {
            "A": TypeAHandler(),
            "B": TypeBHandler(),
        }

    def handle(self, req: dict) -> dict | str:
        handler = self._handlers.get(req.get("type", ""))
        if handler is None:
            raise ValueError(f"Unknown type: {req.get('type')}")
        value = req.get("data", {}).get("value", 0)
        result = handler.compute(value)
        if req.get("format") == "json":
            return {"result": result}
        return str(result)
```

### 3.5 오류를 존재에서 제거하기 (Define Errors Out of Existence)

예외 처리는 소프트웨어 시스템에서 **가장 큰 복잡성 원천 중 하나**다. 가능하다면 오류 조건 자체를 설계적으로 제거하라.

```python
# 나쁜 예: 오류 조건이 불필요하게 존재
class TextBuffer:
    def delete_selection(self):
        if not self.has_selection():
            raise NoSelectionError("Nothing is selected")
        # ... 삭제 로직

# 좋은 예: 오류를 존재에서 제거 -- 선택이 없으면 아무것도 하지 않는다
class TextBuffer:
    def delete_selection(self):
        """현재 선택 영역을 삭제한다. 선택이 없으면 아무것도 하지 않는다."""
        if not self.has_selection():
            return  # 예외 대신 정상 흐름으로 처리
        # ... 삭제 로직
```

### 3.6 설계의 레드 플래그

| 레드 플래그 | 설명 |
|------------|------|
| 얕은 모듈 | 인터페이스가 구현에 비해 지나치게 복잡 |
| 정보 누출 | 같은 지식이 여러 모듈에 분산 |
| 시간적 분해 | 실행 순서에 따라 모듈을 나눈 결과 정보가 분산 |
| 과도한 노출 | 내부 구현이 API에 불필요하게 드러남 |
| Pass-through 메서드 | 거의 아무것도 하지 않고 다른 메서드를 호출만 하는 메서드 |
| Pass-through 변수 | 긴 호출 체인을 통해 전달만 되는 변수 |

### 3.7 주석에 대한 관점

Ousterhout은 "좋은 코드는 주석이 필요 없다"는 통념에 **반대**한다.

- **인터페이스 주석**: 모듈의 전체적 동작, 인자, 반환값, 부작용, 예외를 문서화하라
- **구현 주석**: "무엇"이 아닌 "왜"를 설명하라
- **멤버 변수 주석**: 변수의 목적을 짧게라도 반드시 설명하라

```python
# 나쁜 주석: 코드를 반복 (무엇)
count += 1  # count를 1 증가시킨다

# 좋은 주석: 이유를 설명 (왜)
count += 1  # 재시도 횟수를 추적하여 최대 3회 초과 시 중단하기 위함
```

### 3.8 두 번 설계하라 (Design It Twice)

모든 주요 설계 결정에 대해 최소 **두 가지 근본적으로 다른 접근법**을 고려하라. 첫 번째 생각이 최선의 설계를 내놓을 가능성은 낮다.

---

## 4. Code Complete (Steve McConnell)

> 출처: "Code Complete: A Practical Handbook of Software Construction" 2nd Edition (Steve McConnell, 2004)
> 참고: [matthewjmiller.net/files/cc2e_checklists.pdf](https://www.matthewjmiller.net/files/cc2e_checklists.pdf)

### 4.1 소프트웨어의 제1 기술적 명령: 복잡성 관리

고품질 코드는 읽는 사람에게 **일관된 추상화 수준**을 노출하며, 명확한 경계로 구분된다. 본질적 복잡성(essential complexity)은 최소화하고, 우발적 복잡성(accidental complexity)의 확산을 방지한다.

### 4.2 변수 명명의 힘

> 출처: Code Complete, Chapter 11 "The Power of Variable Names"

**핵심 원칙**: 변수 이름은 그것이 나타내는 실체를 **완전하고 정확하게** 설명해야 한다.

**최적 길이**: 연구에 따르면 변수 이름의 최적 평균 길이는 **10-16자** (Gorla, Benander, Benander 연구), 루틴 이름은 **15-20자**다.

#### 불리언 변수 명명

```python
# 나쁜 예: True/False가 불명확
status = True
source_file = True

# 좋은 예: 이름 자체가 참/거짓을 암시
is_valid = True
has_permission = True
source_file_found = True
order_complete = False

# 나쁜 예: 부정형 이름 (이중 부정 발생)
not_found = True
if not not_found:  # 혼란스럽다
    ...

# 좋은 예: 긍정형 이름 사용
found = False
if found:
    ...
```

#### 루프 변수 명명

```python
# 허용: 짧은 루프에서 관례적 이름
for i in range(10):
    matrix[i] = 0

# 좋은 예: 긴 루프나 중첩 루프에서는 의미 있는 이름
for team_index, team in enumerate(teams):
    for player_index, player in enumerate(team.players):
        scores[team_index][player_index] = player.score
```

#### 한정자(Qualifier) 배치

```python
# 나쁜 예: 한정자가 앞에
total_revenue = ...
avg_revenue = ...
max_revenue = ...

# 좋은 예: 핵심 의미를 앞에, 한정자를 뒤에 (McConnell 권장)
revenue_total = ...
revenue_average = ...
revenue_max = ...
# 핵심 개념(revenue)이 항상 앞에 있으므로 그룹으로 인식 가능
```

#### `num` 사용 회피

```python
# 나쁜 예: num의 의미가 모호
num_customers = 5       # 총 수? 인덱스?
customer_num = 3        # 총 수? 인덱스?

# 좋은 예: 명확한 이름
customer_count = 5      # 총 수
customer_index = 3      # 인덱스
```

### 4.3 고품질 루틴 설계

#### 루틴을 만들어야 하는 이유

- 복잡성을 줄인다 (한 번에 한 가지에 집중)
- 이해하기 쉬운 추상화를 도입한다
- 코드 중복을 피한다
- 변경의 영향을 제한한다
- 코드를 숨긴다 (정보 은닉)
- 이식성을 높인다

#### 루틴의 결정 횟수(Decision Count)

한 루틴의 결정 횟수가 **10을 초과**하면 재설계를 고려하라.

```python
# 나쁜 예: 결정 횟수 과다 (10+ 분기)
def process_order(order):
    if order.status == "new":
        if order.payment_method == "credit":
            if order.amount > 1000:
                if order.customer.is_vip:
                    ...
                else:
                    ...
            else:
                ...
        elif order.payment_method == "debit":
            ...
        elif order.payment_method == "cash":
            ...
    elif order.status == "pending":
        ...
    # 결정이 10개를 초과한다

# 좋은 예: 전략 패턴 등으로 분해
class OrderProcessor:
    def __init__(self):
        self._status_handlers = {
            "new": self._handle_new,
            "pending": self._handle_pending,
        }

    def process(self, order):
        handler = self._status_handlers.get(order.status)
        if handler is None:
            raise ValueError(f"Unknown status: {order.status}")
        return handler(order)
```

### 4.4 방어적 프로그래밍

> 출처: Code Complete, Chapter 8 "Defensive Programming"

**핵심**: 잘못된 입력으로부터 프로그램을 보호하라. "외부"를 어디로 정할지 결정하고, 그 경계에서 데이터를 검증하라.

#### 단언(Assertion) vs 오류 처리

| 상황 | 기법 |
|------|------|
| 절대 발생해서는 안 되는 조건 | `assert` 사용 |
| 발생할 수 있는 예상된 조건 | 오류 처리 코드 사용 |
| 고신뢰성이 필요한 코드 | 둘 다 사용 |

```python
# Assertion: 개발 중 논리 오류 탐지
def calculate_discount(price: float, rate: float) -> float:
    assert 0.0 <= rate <= 1.0, f"Discount rate must be 0-1, got {rate}"
    assert price >= 0, f"Price must be non-negative, got {price}"
    return price * (1 - rate)

# 오류 처리: 외부 입력 검증
def parse_user_input(raw_rate: str) -> float:
    try:
        rate = float(raw_rate)
    except ValueError:
        raise InvalidInputError(f"'{raw_rate}' is not a valid number")
    if not 0.0 <= rate <= 1.0:
        raise InvalidInputError(f"Rate must be between 0 and 1, got {rate}")
    return rate
```

#### 정확성(Correctness) vs 견고성(Robustness)

- **정확성**: 부정확한 결과를 절대 반환하지 않는다 (안전 필수 시스템)
- **견고성**: 소프트웨어가 계속 작동하도록 최선을 다한다 (소비자 앱)

```python
# 정확성 우선 (안전 필수 시스템)
def calculate_medication_dose(weight_kg: float, dosage_per_kg: float) -> float:
    if weight_kg <= 0 or dosage_per_kg <= 0:
        raise CriticalError("Invalid medication calculation parameters")
    dose = weight_kg * dosage_per_kg
    if dose > MAX_SAFE_DOSE:
        raise CriticalError(f"Dose {dose}mg exceeds safety limit")
    return dose

# 견고성 우선 (소비자 앱)
def load_user_preferences(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_PREFERENCES  # 기본값으로 계속 동작
```

### 4.5 테이블 주도 방법 (Table-Driven Methods)

논리문(if/case) 대신 테이블에서 정보를 조회하는 기법. 거의 모든 논리적 선택을 테이블 조회로 대체할 수 있다.

```python
# 나쁜 예: 복잡한 조건 분기
def get_insurance_rate(age: int, gender: str, smoker: bool) -> float:
    if age < 18:
        if gender == "male":
            if smoker:
                return 0.05
            else:
                return 0.03
        else:
            if smoker:
                return 0.04
            else:
                return 0.02
    elif age < 35:
        # ... 계속
        pass

# 좋은 예: Table-Driven Method
INSURANCE_RATES = {
    # (age_group, gender, smoker): rate
    ("youth", "male", True): 0.05,
    ("youth", "male", False): 0.03,
    ("youth", "female", True): 0.04,
    ("youth", "female", False): 0.02,
    ("adult", "male", True): 0.08,
    ("adult", "male", False): 0.05,
    # ...
}

def _age_group(age: int) -> str:
    if age < 18:
        return "youth"
    if age < 35:
        return "adult"
    return "senior"

def get_insurance_rate(age: int, gender: str, smoker: bool) -> float:
    key = (_age_group(age), gender, smoker)
    rate = INSURANCE_RATES.get(key)
    if rate is None:
        raise ValueError(f"No rate defined for {key}")
    return rate
```

### 4.6 변수 스코프 최소화

**변수의 "생존 시간(live time)"을 최소화**하라. 변수가 선언된 후 마지막으로 참조되기까지의 거리가 짧을수록 좋다.

```python
# 나쁜 예: 변수가 너무 일찍 선언되어 생존 시간이 길다
def process_report():
    title = "Monthly Report"          # 여기서 선언
    header_style = "bold"             # 여기서 선언
    # ... 30줄의 데이터 처리 코드 ...
    print(f"<h1 style='{header_style}'>{title}</h1>")  # 여기서 사용

# 좋은 예: 사용 직전에 선언
def process_report():
    data = collect_data()
    analysis = analyze(data)
    # ... 데이터 처리 완료 ...
    title = "Monthly Report"          # 사용 직전에 선언
    header_style = "bold"
    print(f"<h1 style='{header_style}'>{title}</h1>")
```

---

## 5. The Pragmatic Programmer (Thomas & Hunt)

> 출처: "The Pragmatic Programmer: Your Journey to Mastery" 20th Anniversary Edition (David Thomas, Andrew Hunt, 2019)
> 참고: [pragprog.com/tips](https://pragprog.com/tips/)

### 5.1 DRY (Don't Repeat Yourself)

**모든 지식은 시스템 안에서 단일하고 모호하지 않은 권위 있는 표현을 가져야 한다.**

DRY는 단순한 코드 중복 금지가 아니다. **지식의 중복**을 금지하는 것이다. 같은 코드라도 서로 다른 지식을 표현한다면 중복이 아닐 수 있고, 다른 코드라도 같은 지식을 표현한다면 DRY 위반이다.

```python
# DRY 위반: 같은 검증 지식이 두 곳에
class UserValidator:
    def validate_age(self, age: int) -> bool:
        return 0 < age < 150

class UserForm:
    def is_valid_age(self, age: int) -> bool:
        return age > 0 and age < 150  # 같은 규칙의 다른 표현

# DRY 준수: 검증 규칙의 단일 소스
class AgePolicy:
    MIN_AGE = 0
    MAX_AGE = 150

    @classmethod
    def is_valid(cls, age: int) -> bool:
        return cls.MIN_AGE < age < cls.MAX_AGE

class UserValidator:
    def validate_age(self, age: int) -> bool:
        return AgePolicy.is_valid(age)
```

```python
# DRY가 아닌 경우: 우연히 같은 코드지만 다른 지식
def validate_user_age(age: int) -> bool:
    return 0 < age < 150  # 사용자 나이 정책

def validate_building_floors(floors: int) -> bool:
    return 0 < floors < 150  # 건물 층수 제한 -- 우연히 같은 범위

# 이 두 함수를 합치면 안 된다. 서로 다른 도메인 지식을 표현한다.
```

### 5.2 직교성 (Orthogonality)

**두 가지 이상의 것이 직교적이면, 하나의 변경이 다른 것에 영향을 주지 않는다.** 관련 없는 것들 사이의 영향을 제거하라.

```python
# 나쁜 예: 직교성 위반 -- UI 로직과 비즈니스 로직이 결합
class ReportGenerator:
    def generate(self, data: list[dict]) -> str:
        html = "<html><body>"
        total = sum(item["amount"] for item in data)
        tax = total * 0.1  # 비즈니스 로직
        html += f"<h1>Total: {total}</h1>"  # UI 로직
        html += f"<p>Tax: {tax}</p>"
        html += "</body></html>"
        return html

# 좋은 예: 직교적 분리
class TaxCalculator:
    RATE = 0.1
    def calculate(self, amount: float) -> float:
        return amount * self.RATE

class ReportData:
    def __init__(self, items: list[dict]):
        self.total = sum(item["amount"] for item in items)
        self.tax = TaxCalculator().calculate(self.total)

class HTMLReportRenderer:
    def render(self, report: ReportData) -> str:
        return (
            f"<html><body>"
            f"<h1>Total: {report.total}</h1>"
            f"<p>Tax: {report.tax}</p>"
            f"</body></html>"
        )
```

### 5.3 깨진 창문 이론 (Broken Window Theory)

하나의 깨진 창문(나쁜 설계, 잘못된 결정, 나쁜 코드)을 방치하면, 전체 소프트웨어가 빠르게 퇴화한다. **발견 즉시 수리하라.** 시간이 없다면 최소한 "판자로 막아 놓으라" (TODO 주석, 예외 발생 등).

```python
# 깨진 창문: 방치된 나쁜 코드
def calc(d):  # 이름 불명확
    x = d.get("v")  # 축약된 변수
    if x:
        return x * 1.1  # 매직 넘버
    return 0  # 에러 처리 없음
    # "어차피 다른 코드도 이 수준이니까..." -> 유리창이 더 깨진다

# 수리된 창문
TAX_RATE = 0.1

def calculate_total_with_tax(order_data: dict) -> float:
    """주문 데이터에서 세금 포함 총액을 계산한다."""
    amount = order_data.get("amount")
    if amount is None:
        raise ValueError("Order data must contain 'amount'")
    return amount * (1 + TAX_RATE)
```

### 5.4 추적탄 (Tracer Bullets)

프로토타입과 달리, 추적탄 코드는 **최종 시스템의 골격**이 된다. 요구사항에서 시스템의 어떤 측면까지 빠르고 가시적이며 반복적으로 도달하는 것이 목표다.

| 추적탄 (Tracer Bullet) | 프로토타입 (Prototype) |
|------------------------|----------------------|
| 최종 시스템의 일부가 된다 | 작성 후 버린다 |
| 가볍지만 완전하다 | 특정 측면만 탐구한다 |
| 실제 환경에서 동작한다 | 격리된 실험이다 |
| 점진적으로 살을 붙인다 | 정찰/정보 수집 역할 |

```python
# 추적탄: 끝에서 끝까지 동작하는 최소 구현
# (향후 각 레이어에 살을 붙인다)

# 1단계: API 끝점
from fastapi import FastAPI
app = FastAPI()

@app.get("/reports/{report_id}")
async def get_report(report_id: int):
    # 2단계: 서비스 레이어 (현재는 스텁)
    report = await report_service.find(report_id)
    # 3단계: 응답 변환
    return {"id": report.id, "title": report.title}

# 프로토타입과 다르게, 이 코드는 버리지 않는다.
# 각 레이어를 점진적으로 발전시킨다.
```

### 5.5 가역성 (Reversibility)

되돌리기 어려운 결정을 피하라. 추상화를 통해 핵심 결정을 교체 가능하게 만들라.

```python
# 나쁜 예: 특정 DB에 직접 결합
import psycopg2

class UserRepository:
    def find(self, user_id: int):
        conn = psycopg2.connect(...)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()

# 좋은 예: 추상화로 결정을 가역적으로 만듬
from typing import Protocol

class UserRepository(Protocol):
    def find(self, user_id: int) -> User | None: ...

class PostgresUserRepository:
    def find(self, user_id: int) -> User | None: ...

class MongoUserRepository:
    def find(self, user_id: int) -> User | None: ...

# DB를 바꿔도 UserRepository를 사용하는 코드는 변경 불필요
```

### 5.6 고무 오리 디버깅 (Rubber Duck Debugging)

문제를 다른 사람(또는 고무 오리)에게 **설명하는 과정**에서 해답을 발견한다. 코드를 한 줄씩 소리 내어 설명하면 암묵적 가정과 논리 오류가 드러난다.

### 5.7 기타 핵심 팁

| 팁 | 설명 |
|----|------|
| ETC (Easier to Change) | 좋은 설계의 핵심 가치 -- 변경하기 쉬운 코드 |
| 작은 걸음으로 (Take Small Steps) | 항상 작은 단위로 변경하고 확인하라 |
| 일찍 리팩토링하고 자주 리팩토링하라 | 문제를 발견하면 즉시 개선 |
| 최소 결합의 법칙 | 물어보지 말고 말하라 (Tell, Don't Ask) |
| 우연에 의한 프로그래밍을 피하라 | 코드가 왜 동작하는지 항상 이해하라 |

---

## 6. Working Effectively with Legacy Code (Michael Feathers)

> 출처: "Working Effectively with Legacy Code" (Michael Feathers, 2004)
> 참고: [understandlegacycode.com](https://understandlegacycode.com/blog/key-points-of-working-effectively-with-legacy-code/)

### 6.1 레거시 코드의 정의

> **레거시 코드란 테스트가 없는 코드다.**

아무리 잘 작성되었든, 아무리 예쁘고 객체지향적이고 잘 캡슐화되었든, 테스트가 없으면 레거시 코드다.

### 6.2 Seam 개념

**Seam**: 코드를 편집하지 않고도 동작을 변경할 수 있는 지점. 테스트를 삽입하기 위한 틈새를 찾는 핵심 개념.

| Seam 유형 | 설명 | Python 적용 |
|-----------|------|-------------|
| **Object Seam** | 인터페이스를 정의하고 프로덕션 객체를 테스트용 가짜 객체로 교체 | Protocol + 의존성 주입 |
| **Link Seam** | 구현 함수를 교체 | 모듈 수준 함수 교체 (monkeypatch) |

```python
# Object Seam: 의존성 주입으로 테스트 가능하게 만들기

# Before: 테스트 불가능 (외부 서비스에 직접 결합)
class OrderService:
    def place_order(self, order: Order) -> None:
        # 직접 이메일 전송 -- 테스트 시 실제 이메일이 발송됨
        import smtplib
        server = smtplib.SMTP("smtp.company.com")
        server.send_message(...)

# After: Object Seam 도입 (테스트 가능)
from typing import Protocol

class EmailSender(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...

class OrderService:
    def __init__(self, email_sender: EmailSender) -> None:
        self._email_sender = email_sender

    def place_order(self, order: Order) -> None:
        # ... 주문 처리 ...
        self._email_sender.send(
            to=order.customer_email,
            subject="Order Confirmation",
            body=f"Order {order.id} placed.",
        )

# 테스트에서 가짜 객체 사용
class FakeEmailSender:
    def __init__(self):
        self.sent_emails: list[tuple[str, str, str]] = []

    def send(self, to: str, subject: str, body: str) -> None:
        self.sent_emails.append((to, subject, body))

def test_place_order():
    sender = FakeEmailSender()
    service = OrderService(email_sender=sender)
    service.place_order(sample_order)
    assert len(sender.sent_emails) == 1
```

### 6.3 Sprout Method (발아 메서드)

새 기능을 추가할 때, 기존 코드를 수정하지 않고 **새 메서드로 작성**한 후 기존 코드에서 호출한다.

```python
# 기존 레거시 코드 (테스트 없음, 수정하기 위험)
class TransactionGate:
    def post_entries(self, entries: list) -> None:
        for entry in entries:
            entry.post_date = datetime.now()
            self._verify_entry(entry)
            self._persist(entry)

# 새 요구사항: 중복 항목 필터링 추가
# Sprout Method: 새 기능을 별도 메서드로 작성 (테스트 가능)
class TransactionGate:
    def post_entries(self, entries: list) -> None:
        unique_entries = self._remove_duplicates(entries)  # 새 메서드 호출
        for entry in unique_entries:
            entry.post_date = datetime.now()
            self._verify_entry(entry)
            self._persist(entry)

    def _remove_duplicates(self, entries: list) -> list:
        """중복 항목을 제거한다. (새 메서드 -- 단위 테스트 작성 가능)"""
        seen = set()
        unique = []
        for entry in entries:
            if entry.id not in seen:
                seen.add(entry.id)
                unique.append(entry)
        return unique
```

### 6.4 Wrap Method (감싸기 메서드)

기존 메서드를 래핑하여 전후에 새 동작을 추가한다.

```python
# 기존 메서드
class Employee:
    def pay(self) -> None:
        # 복잡한 급여 계산 로직 (레거시)
        ...

# Wrap Method: 기존 메서드를 감싸서 로깅 추가
class Employee:
    def pay(self) -> None:
        self._log_payment()       # 새 동작 (전)
        self._dispatch_pay()      # 기존 로직 (이름 변경)
        self._update_records()    # 새 동작 (후)

    def _dispatch_pay(self) -> None:
        # 원래 pay()의 로직 (이름만 변경)
        ...

    def _log_payment(self) -> None:
        """급여 지급 로깅 (새 메서드 -- 테스트 가능)"""
        ...

    def _update_records(self) -> None:
        """급여 기록 업데이트 (새 메서드 -- 테스트 가능)"""
        ...
```

### 6.5 특성화 테스트 (Characterization Tests)

"올바른 동작"을 검증하는 것이 아니라, **현재 동작을 포착**하는 테스트. 리팩토링 전에 안전망으로 작성한다.

```python
# 특성화 테스트: 레거시 함수의 현재 동작을 기록
def test_legacy_calculate_tax():
    """현재 동작을 포착한다. '올바른' 결과가 아닌 '현재' 결과를 기대한다."""
    # 이 값이 맞는지는 확실하지 않지만, 현재 이렇게 동작한다
    assert legacy_calculate_tax(1000) == 103.5
    assert legacy_calculate_tax(0) == 0
    assert legacy_calculate_tax(-500) == -51.75  # 음수 입력에 대한 현재 동작

    # 이 테스트가 있으면, 리팩토링 중 동작 변경을 즉시 감지할 수 있다
```

### 6.6 Sensing과 Separation

- **Sensing (감지)**: 코드가 계산하는 값에 접근하여 시스템의 다른 부분에 미치는 영향을 파악
- **Separation (분리)**: 테스트를 위해 코드를 의존성에서 분리

레거시 코드에서 테스트가 어려운 주요 원인은 **얽힌 의존성** 때문이다. Seam을 찾아 의존성을 끊고, 감지와 분리를 통해 테스트 가능한 코드로 전환한다.

---

## 7. Google Python Style Guide

> 출처: [google.github.io/styleguide/pyguide.html](https://google.github.io/styleguide/pyguide.html)

### 7.1 Python 언어 규칙

#### 예외 처리

```python
# 나쁜 예: 너무 큰 try 블록
try:
    data = fetch_data()
    processed = transform(data)
    result = calculate(processed)
    save(result)
    notify_user(result)
except Exception:
    log_error()

# 좋은 예: try 블록 최소화
data = fetch_data()
processed = transform(data)
try:
    result = calculate(processed)
except CalculationError as e:
    log_error(f"Calculation failed: {e}")
    raise
save(result)
notify_user(result)
```

- 내장 예외 클래스를 적극 활용한다
- `finally`를 사용하여 리소스를 정리한다
- 예외를 잡을 때 `,`(쉼표) 대신 `as`를 사용한다

#### 가변 전역 상태 (Mutable Global State) 회피

```python
# 나쁜 예: 가변 전역 상태
_cache = {}  # 모듈 수준 가변 딕셔너리

def get_user(user_id: int) -> User:
    if user_id not in _cache:
        _cache[user_id] = fetch_from_db(user_id)
    return _cache[user_id]

# 좋은 예: 클래스로 캡슐화, 내부 접근 제한
class _UserCache:
    def __init__(self) -> None:
        self._store: dict[int, User] = {}

    def get(self, user_id: int, fetcher: Callable) -> User:
        if user_id not in self._store:
            self._store[user_id] = fetcher(user_id)
        return self._store[user_id]

_user_cache = _UserCache()  # 내부용 (_접두사)

# 외부 접근은 공개 함수를 통해서만
def get_user(user_id: int) -> User:
    return _user_cache.get(user_id, fetch_from_db)
```

#### 컴프리헨션과 제너레이터

```python
# 나쁜 예: 복잡한 컴프리헨션 (다중 for/filter)
result = [
    transform(x)
    for sublist in nested_lists
    for x in sublist
    if x > 0
    if x % 2 == 0
]

# 좋은 예: 가독성 최적화 -- 복잡하면 일반 루프 사용
result = []
for sublist in nested_lists:
    for x in sublist:
        if x > 0 and x % 2 == 0:
            result.append(transform(x))

# 좋은 예: 단순한 컴프리헨션은 권장
squares = [x * x for x in range(10)]
even_values = {k: v for k, v in data.items() if v % 2 == 0}
```

**규칙**: 다중 `for` 절이나 필터 표현식은 금지. **간결함이 아닌 가독성을 최적화**하라.

#### 조건 표현식 (삼항 연산자)

```python
# 허용: 간단한 경우
x = 1 if condition else 2

# 금지: 복잡해지면 일반 if문 사용
# 나쁜 예
result = value if condition_a else (other if condition_b else default)

# 좋은 예
if condition_a:
    result = value
elif condition_b:
    result = other
else:
    result = default
```

#### 기본 인자 값

```python
# 나쁜 예: 가변 객체를 기본 인자로 사용
def append_to(element, target=[]):  # 위험! 호출 간에 공유됨
    target.append(element)
    return target

# 좋은 예: None을 기본값으로 사용
def append_to(element, target=None):
    if target is None:
        target = []
    target.append(element)
    return target
```

### 7.2 True/False 평가

```python
# 좋은 예: 암묵적 false 활용
if not users:          # 빈 리스트 검사
    ...
if not name:           # 빈 문자열 검사
    ...
if count:              # 0이 아닌 값 검사
    ...

# 중요 예외: None 검사는 반드시 명시적으로
if foo is None:        # 좋은 예
    ...
if not foo:            # 나쁜 예 -- foo가 0이나 []여도 True가 된다
    ...
```

### 7.3 Properties와 Decorator

```python
# 좋은 예: @property로 단순 접근자 구현
class Circle:
    def __init__(self, radius: float) -> None:
        self._radius = radius

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value

    @property
    def area(self) -> float:
        return 3.14159 * self._radius ** 2
```

- `@staticmethod`는 기존 라이브러리 API와의 통합이 강제되지 않는 한 사용하지 않는다
- `@classmethod`는 네임드 생성자(named constructor)나 클래스 전체에 영향을 주는 작업에만 사용한다

### 7.4 파워 피처 (Power Features) 회피

메타클래스, 바이트코드 접근, 런타임 컴파일, 동적 상속, 객체 부모 변경, 임포트 해킹, 리플렉션 등은 **피하라**. 처음에는 화려해 보이지만, 코드를 재방문할 때 이해와 디버깅이 훨씬 어렵다.

### 7.5 Google 스타일 독스트링

```python
def fetch_smalltable_rows(
    table_handle: smalltable.Table,
    keys: Sequence[bytes | str],
    require_all_keys: bool = False,
) -> Mapping[bytes, tuple[str, ...]]:
    """Fetches rows from a Smalltable.

    Retrieves rows pertaining to the given keys from the Table instance
    represented by table_handle. String keys will be UTF-8 encoded.

    Args:
        table_handle: An open smalltable.Table instance.
        keys: A sequence of strings representing the key of each table
            row to fetch. String keys will be UTF-8 encoded.
        require_all_keys: If True only rows with values set for all keys
            will be returned.

    Returns:
        A dict mapping keys to the corresponding table row data
        fetched. Each row is represented as a tuple of strings. For
        example:

        {b'Serak': ('Rigel VII', 'Preparer'),
         b'Zeli': ('Rigel VII', 'Sweeper')}

    Raises:
        google.cloud.smalltable.error.NotFoundError: If any of the
            required keys is missing, and require_all_keys is True.
    """
    ...
```

- 제너레이터 함수에서는 `Returns` 대신 `Yields`를 사용한다
- 요약 줄은 80자를 넘지 않으며 마침표, 물음표, 느낌표로 끝난다

### 7.6 수학적 코드의 예외

수학적으로 무거운 코드에서는 스타일 가이드를 위반하는 짧은 변수명이 허용된다. 단, **출처를 명시적으로 기록**해야 한다.

```python
# 허용: 수학적 표기법이 확립된 경우
def kalman_update(x: np.ndarray, P: np.ndarray, z: np.ndarray,
                  H: np.ndarray, R: np.ndarray) -> tuple:
    """Kalman filter measurement update step.

    Variable names follow standard Kalman filter notation:
    See: Thrun, S., "Probabilistic Robotics", Chapter 3.
    """
    # x: state vector, P: covariance, z: measurement
    # H: observation matrix, R: measurement noise
    y = z - H @ x
    S = H @ P @ H.T + R
    K = P @ H.T @ np.linalg.inv(S)
    x_new = x + K @ y
    P_new = (np.eye(len(x)) - K @ H) @ P
    return x_new, P_new
```

---

## 8. 커뮤니티 베스트 프랙티스

### 8.1 EAFP vs LBYL

> 출처: [Real Python - LBYL vs EAFP](https://realpython.com/python-lbyl-vs-eafp/), [Python 공식 용어집](https://docs.python.org/3/glossary.html)

**EAFP** (Easier to Ask Forgiveness than Permission): 먼저 시도하고, 실패하면 처리한다.
**LBYL** (Look Before You Leap): 수행 전에 사전 조건을 확인한다.

Python은 **EAFP를 선호**한다.

```python
# LBYL: 사전 확인
if os.path.exists(filepath):
    with open(filepath) as f:
        data = f.read()
else:
    data = ""
# 문제: 확인과 사용 사이에 파일이 삭제될 수 있다 (Race Condition)

# EAFP: 먼저 시도, 실패 시 처리 (Pythonic)
try:
    with open(filepath) as f:
        data = f.read()
except FileNotFoundError:
    data = ""
```

```python
# LBYL
if "key" in dictionary:
    value = dictionary["key"]
else:
    value = default

# EAFP (Pythonic)
try:
    value = dictionary["key"]
except KeyError:
    value = default

# 더 Pythonic: 내장 메서드 활용
value = dictionary.get("key", default)
```

**사용 지침:**
| 상황 | 권장 |
|------|------|
| 오류가 드물거나 예상되는 경우 | EAFP |
| 더 깔끔한 코드가 가능한 경우 | EAFP |
| 멀티스레드 환경 (Race Condition 방지) | EAFP |
| 확인이 실행보다 저렴한 경우 | LBYL |
| 예외가 너무 광범위하거나 느린 경우 | LBYL |
| 외부 조건 확인 (파일 존재 등) | 상황에 따라 선택 |

### 8.2 컨텍스트 매니저 적극 활용

> 출처: [Python 공식 문서 - with 문](https://docs.python.org/3/reference/compound_stmts.html#the-with-statement)

```python
# 나쁜 예: 리소스 수동 관리 (finally 누락 위험)
f = open("data.txt")
try:
    data = f.read()
finally:
    f.close()

# 좋은 예: 컨텍스트 매니저
with open("data.txt") as f:
    data = f.read()
# 예외가 발생해도 파일이 자동으로 닫힌다
```

```python
# 커스텀 컨텍스트 매니저: 타이밍 측정
import time
from contextlib import contextmanager

@contextmanager
def timer(label: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"{label}: {elapsed:.4f}s")

with timer("data processing"):
    heavy_computation()
```

### 8.3 f-string 활용 (Python 3.6+)

```python
name = "World"
count = 42

# 나쁜 예: 오래된 포맷팅
msg1 = "Hello, %s! Count: %d" % (name, count)
msg2 = "Hello, {}! Count: {}".format(name, count)

# 좋은 예: f-string (더 빠르고, 더 읽기 쉬움)
msg3 = f"Hello, {name}! Count: {count}"

# 디버깅용 (Python 3.8+): = 접미사
x = 42
print(f"{x = }")  # 출력: x = 42
```

### 8.4 dataclass 활용

```python
# 나쁜 예: 보일러플레이트 가득한 클래스
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y})"

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

# 좋은 예: dataclass
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    # __init__, __repr__, __eq__ 자동 생성

# 불변 값 객체가 필요하면 frozen=True
@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int
```

### 8.5 Enum 활용

```python
# 나쁜 예: 매직 문자열
def set_color(color: str):
    if color == "red":       # 오타 위험: "rde"
        ...
    elif color == "green":
        ...

# 좋은 예: Enum
from enum import Enum, auto

class Color(Enum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()

def set_color(color: Color):
    if color == Color.RED:   # IDE 자동완성, 오타 불가
        ...
```

### 8.6 구조적 패턴 매칭 (Python 3.10+)

```python
# 나쁜 예: 긴 if-elif 체인
def handle_command(command):
    if command["action"] == "move":
        x, y = command["x"], command["y"]
        move_player(x, y)
    elif command["action"] == "attack":
        target = command["target"]
        attack(target)
    elif command["action"] == "quit":
        quit_game()

# 좋은 예: match 문 (Python 3.10+)
def handle_command(command):
    match command:
        case {"action": "move", "x": x, "y": y}:
            move_player(x, y)
        case {"action": "attack", "target": target}:
            attack(target)
        case {"action": "quit"}:
            quit_game()
        case _:
            raise ValueError(f"Unknown command: {command}")
```

---

## 원칙 간 관계 맵

아래는 서로 다른 출처의 원칙들이 어떻게 연결되는지를 보여준다.

```
복잡성 관리 (근본 문제)
├── Code Complete: "소프트웨어의 제1 기술적 명령"
├── APoSD: 복잡성의 세 가지 발현
└── Zen of Python: "Simple is better than complex"

정보 은닉 / 캡슐화
├── APoSD: 깊은 모듈 vs 얕은 모듈
├── Code Complete: 추상화 수준의 일관성
├── Pragmatic Programmer: 직교성
└── Refactoring: Feature Envy, Inappropriate Intimacy 해소

변경 용이성
├── Pragmatic Programmer: ETC, DRY, 가역성
├── APoSD: 전략적 프로그래밍
├── Refactoring: Shotgun Surgery, Divergent Change 해소
└── Working with Legacy Code: Seam, Sprout, Wrap

이름 짓기의 중요성
├── PEP 8: 명명 규칙
├── Code Complete: 변수명 10-16자, 루틴명 15-20자
├── Google Style Guide: 서술적 이름
└── Zen of Python: "Readability counts"

테스트와 안전망
├── Working with Legacy Code: "테스트 없는 코드 = 레거시"
├── Working with Legacy Code: 특성화 테스트
├── Code Complete: 방어적 프로그래밍, 단언
└── Pragmatic Programmer: "깨진 창문을 수리하라"
```

---

## 참고 자료

### PEP 문서
- [PEP 8 -- Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [PEP 20 -- The Zen of Python](https://peps.python.org/pep-0020/)
- [PEP 257 -- Docstring Conventions](https://peps.python.org/pep-0257/)
- [PEP 3107 -- Function Annotations](https://peps.python.org/pep-3107/)
- [PEP 484 -- Type Hints](https://peps.python.org/pep-0484/)
- [PEP 526 -- Syntax for Variable Annotations](https://peps.python.org/pep-0526/)

### 서적
- Fowler, M. (2018). *Refactoring: Improving the Design of Existing Code* (2nd ed.). Addison-Wesley.
- Ousterhout, J. (2021). *A Philosophy of Software Design* (2nd ed.). Yaknyam Press.
- McConnell, S. (2004). *Code Complete: A Practical Handbook of Software Construction* (2nd ed.). Microsoft Press.
- Thomas, D. & Hunt, A. (2019). *The Pragmatic Programmer: Your Journey to Mastery* (20th Anniversary ed.). Addison-Wesley.
- Feathers, M. (2004). *Working Effectively with Legacy Code*. Prentice Hall.

### 온라인 자료
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Refactoring Catalog](https://refactoring.com/catalog/)
- [Real Python - LBYL vs EAFP](https://realpython.com/python-lbyl-vs-eafp/)
- [Real Python - How to Write Beautiful Python Code With PEP 8](https://realpython.com/python-pep8/)
- [Python 공식 문서 - typing 모듈](https://docs.python.org/3/library/typing.html)
- [Code Complete Checklists (PDF)](https://www.matthewjmiller.net/files/cc2e_checklists.pdf)
- [Understanding Legacy Code](https://understandlegacycode.com/blog/key-points-of-working-effectively-with-legacy-code/)
- [Code Smells Catalog](https://luzkan.github.io/smells/)
- [Pragmatic Programmer Tips](https://pragprog.com/tips/)
