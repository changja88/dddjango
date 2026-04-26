# 데이터 모델링: dataclass, Enum, NamedTuple, pydantic

Python에서 데이터를 표현하는 핵심 도구들을 정리한다.

---

## Enum: 상수 그룹화

```python
from enum import Enum, auto

class Position(Enum):
    CHEF = auto()
    SOUS_CHEF = auto()
    SERVER = auto()

# 문자열 Enum
class Color(str, Enum):
    RED = 'red'
    BLUE = 'blue'
```

매직 문자열이나 정수 상수 대신 Enum을 사용하라. 타입 안전성과 가독성을 모두 확보한다.

---

## dataclass 기본

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

---

## dataclass 옵션

### slots=True: 메모리 최적화 (3.10+)

```python
@dataclass(slots=True)
class PointSlots:
    x: float
    y: float

# __dict__ 대비 20-50% 메모리 절약. 수백만 인스턴스 생성 시 유의미.
```

### frozen=True: 불변 값 객체

```python
@dataclass(frozen=True)
class Money:
    amount: int
    currency: str

    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("통화 불일치")
        return Money(self.amount + other.amount, self.currency)

# price.amount = 2000  -> FrozenInstanceError
```

### kw_only=True: 키워드 전용 필드 (3.10+)

```python
@dataclass(kw_only=True)
class Config:
    host: str
    port: int = 8080
    debug: bool = False

# Config("localhost")  -> TypeError
Config(host="localhost")  # OK

# 부분 적용: 특정 필드만 kw_only
@dataclass
class User:
    name: str                                    # 위치 인자 가능
    email: str                                   # 위치 인자 가능
    role: str = field(default="user", kw_only=True)  # 키워드 전용
```

---

## __post_init__과 InitVar

```python
from dataclasses import dataclass, field, InitVar

@dataclass
class Temperature:
    celsius: float
    fahrenheit: float = field(init=False)
    scale: InitVar[str] = "C"  # __init__에만 존재, 인스턴스 속성이 아님

    def __post_init__(self, scale: str):
        if scale == "F":
            self.celsius = (self.celsius - 32) * 5 / 9
        self.fahrenheit = self.celsius * 9 / 5 + 32
```

---

## NamedTuple: 불변 레코드

```python
from typing import NamedTuple

class Car(NamedTuple):
    color: str
    mileage: float

car = Car('red', 3812)
car.color       # 이름으로 접근
car[0]          # 인덱스로도 접근
car._asdict()   # dict 변환
```

**dataclass vs NamedTuple 선택 기준**:
- 가변 데이터, 메서드가 필요하면 -> `@dataclass`
- 불변 + 튜플 호환(인덱싱, 언패킹)이 필요하면 -> `NamedTuple`
- 불변 값 객체(메서드 포함)면 -> `@dataclass(frozen=True)`

---

## 컬렉션 선택 가이드

| 컬렉션 | 특성 | 용도 |
|--------|------|------|
| `list` | 변경 가능, 순서 있음 | 반복, 동적 인덱싱 |
| `tuple` | 불변, 순서 있음 | 고정 크기 데이터 |
| `set` | 순서 없음, 중복 불가 | 멤버십 테스트, 중복 제거 |
| `dict` | 키-값 매핑, 삽입 순서 보존 | 키 기반 조회 |
| `deque` | 양방향 O(1) 삽입/삭제 | FIFO 큐 |
| `defaultdict` | 키 없을 때 기본값 자동 생성 | 그룹핑, 카운팅 |
| `frozenset` | 불변 세트 | 딕셔너리 키, 해시 가능한 세트 |
| `Counter` | 요소 카운팅 특화 | 빈도 분석 |

---

## pydantic v2: 런타임 검증

### v1 vs v2 주요 변경

```python
# === v1 (지원 중단) ===
from pydantic import BaseModel, validator
class UserV1(BaseModel):
    class Config:
        frozen = True
    @validator('age')
    def check_age(cls, v): ...
    data = user.dict()
    user = UserV1.parse_obj({})

# === v2 (현재) -- 권장 ===
from pydantic import BaseModel, ConfigDict, field_validator
class UserV2(BaseModel):
    model_config = ConfigDict(frozen=True)
    @field_validator('age')
    @classmethod
    def check_age(cls, v: int) -> int: ...
    data = user.model_dump()
    user = UserV2.model_validate({})
```

### model_validator: 모델 수준 검증

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
```

### Strict Mode: 타입 강제 변환 제어

```python
from pydantic import BaseModel, ConfigDict, Field

class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True)
    count: int

# StrictModel(count="42")  -> ValidationError

# 필드별 strict 제어
class MixedModel(BaseModel):
    model_config = ConfigDict(strict=True)
    id: int                              # strict
    score: float = Field(strict=False)   # 이 필드만 lax
```
