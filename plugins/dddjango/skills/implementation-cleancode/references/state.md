# 상태 관리 레퍼런스

변수 범위, 생명주기, 값 객체, 상태 접근 방식에 관한 규칙과 예시를 다룬다.

---

### 1.1 변수의 범위와 생명주기를 최소화하라 [IP] [CodeC]

변수는 사용 직전에 선언하라. 선언 후 마지막으로 참조되기까지의
거리("생존 시간")가 짧을수록 좋다.

```python
# bad — 사용 시점보다 훨씬 전에 선언
result = None
# ... 100줄의 코드 ...
result = compute()

# good — 사용 직전에 선언
# ... 100줄의 코드 ...
result = compute()
```

### 1.2 값 객체를 활용하라 [IP] [OO]

변치 않는 값을 표현할 때는 값 객체를 사용하라. 생성 후 상태가 변경되지 않아야 한다.

```python
# bad — 가변 상태
class Transaction:
    def __init__(self, value):
        self.value = value  # 외부에서 변경 가능

# good — 값 객체
from dataclasses import dataclass

@dataclass(frozen=True)
class Transaction:
    value: int
    credit_account: str
    debit_account: str
```

### 1.3 상태 접근은 간접 접근을 기본으로 [IP]

내부에서는 직접 접근을 허용하되, 외부에서는 메서드나 프로퍼티를 통해 접근하라.

```python
# bad — 의존 관계가 있는 상태가 외부에 노출
class Rectangle:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.area = 0  # width/height와 수동으로 동기화해야 함

# good — 계산 프로퍼티
class Rectangle:
    def __init__(self, width, height):
        self._width = width
        self._height = height

    @property
    def area(self):
        return self._width * self._height
```

### 1.4 공용 상태 vs 가변 상태 [IP]

- **공용 상태**: 여러 연산에서 같은 데이터를 사용하는 경우 -- 필드로 선언
- **가변 상태**: 인스턴스마다 전혀 다른 데이터 요소가 필요한 경우 -- 맵으로 표현
- 가능하다면 공용 상태를 사용하는 것이 더 단순하다
