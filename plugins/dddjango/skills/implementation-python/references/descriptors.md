# 디스크립터와 @property

재사용 가능한 애트리뷰트 접근 로직을 위한 디스크립터 프로토콜과
`@property` 사용법을 정리한다.

---

## 세터/게터 대신 평범한 애트리뷰트

파이썬에서 명시적 세터/게터는 파이썬답지 않다. 단순 공개 애트리뷰트로 시작하고,
나중에 로직이 필요하면 `@property`로 전환하라.

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

---

## 디스크립터 프로토콜

디스크립터는 `__get__`, `__set__`, `__delete__`, `__set_name__` 중 하나 이상을
구현한 클래스이다. `@property`의 일반화이며, **재사용 가능한** 애트리뷰트 로직에
사용한다.

---

## 검증 디스크립터 프레임워크: ABC 기반 패턴

Python 공식 Descriptor HowTo Guide 패턴을 기본으로 사용한다.
`instance.__dict__` 직접 저장이 더 단순하고 공식 가이드의 권장 패턴이다.

```python
from abc import ABC, abstractmethod

class Validator(ABC):
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
```

> **레거시 참고**: `WeakKeyDictionary`를 사용한 패턴도 존재하지만,
> `__set_name__`(3.6+) 이후로는 `instance.__dict__` 직접 저장이 권장된다.

---

## __getattr__과 __getattribute__

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
