# 클래스 설계: Python 특화 패턴

Python 특유의 클래스 설계 기법과 연산자 오버로딩을 정리한다.

---

## __call__로 호출 가능한 객체

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

---

## @classmethod를 팩토리 메서드로 활용

파이썬은 `__init__` 하나만 허용한다. 대체 생성자가 필요하면 `@classmethod`를
사용하라.

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
```

---

## 인스턴스/클래스/정적 메서드

```python
class MyClass:
    def method(self):            # 인스턴스 메서드: self로 객체 상태 접근
        ...

    @classmethod
    def classmethod(cls):        # 클래스 메서드: cls로 클래스 상태 접근
        ...                      # 팩토리 메서드에 적합

    @staticmethod
    def staticmethod():          # 정적 메서드: 상태 접근 불가
        ...                      # 독립적 유틸리티
```

---

## __repr__과 __str__

모든 클래스에 최소한 `__repr__`은 구현하라. `__str__`이 없으면 `__repr__`이 대신
사용된다.

```python
class Car:
    def __init__(self, color, mileage):
        self.color = color
        self.mileage = mileage

    def __repr__(self):
        return f'{self.__class__.__name__}({self.color!r}, {self.mileage!r})'

    def __str__(self):
        return f'{self.color} 차 ({self.mileage}km)'
```

---

## 비공개(__) 대신 보호(_) 애트리뷰트

```python
# 나쁜 예: 이중 밑줄 남용
class MyClass:
    def __init__(self):
        self.__private = 42  # 네임 맹글링: _MyClass__private

# 좋은 예: 단일 밑줄 관례
class MyClass:
    def __init__(self):
        self._protected = 42
```

- `__var`: 네임 맹글링 발생. 하위 클래스 필드명 충돌 방지에만 사용하라.
- `_var`: 관례적 보호. 외부에서 사용 시 주의하라는 의미.

---

## __init_subclass__로 하위 클래스 검증 (3.6+)

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

---

## __init_subclass__ 고급 활용: 플러그인 레지스트리

```python
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

plugin = PluginBase.create("json")  # JSONPlugin 인스턴스
```

---

## 믹스인 클래스

자체 애트리뷰트 정의 없이 메서드만 제공하는 클래스. `__init__` 호출 불필요.

```python
class ToDictMixin:
    def to_dict(self):
        return self._traverse_dict(self.__dict__)

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

---

## collections.abc로 커스텀 컨테이너

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

## 연산자 오버로딩

```python
class Vector:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        return NotImplemented  # raise가 아님!

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Vector(self.x * scalar, self.y * scalar)
        return NotImplemented

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __eq__(self, other):
        if isinstance(other, Vector):
            return self.x == other.x and self.y == other.y
        return NotImplemented
```

**핵심 규칙**:
- `NotImplemented`를 **반환**하라 (raise가 아님). Python이 역연산을 시도한다.
- `__eq__`를 정의하면 `__hash__`는 `None`이 되므로, 해시 가능 객체는
  `__hash__`도 정의하라.
- `@` 연산자(PEP 465)는 `__matmul__`/`__rmatmul__`/`__imatmul__`로 구현한다.
