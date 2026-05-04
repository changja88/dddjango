# 리팩토링 패턴 레퍼런스

TDD Green 단계 이후 코드 구조를 개선하기 위한 리팩토링 패턴 8가지를 정리한다.

---

## 차이점 일치시키기 (Reconcile Differences)

비슷해 보이는 두 코드 조각을 합치려면, 두 코드가 **단계적으로 닮아가게끔 수정**한다. 완전히 동일해지면 둘을 합친다.

---

## 변화 격리하기 (Isolate Change)

객체나 메서드의 일부만 바꾸려면, 일단 바꿔야 할 부분을 격리한다. 격리 방법에는 **메서드 추출하기**, 객체 추출하기, 메서드 객체 등이 있다.

---

## 데이터 이주시키기 (Migrate Data)

표현 양식을 변경하려면 **일시적으로 데이터를 중복**시킨다.

내부에서 외부로의 변화 단계:

1. 새로운 포맷의 인스턴스 변수를 추가한다
2. 기존 포맷의 인스턴스 변수를 세팅하는 모든 부분에서 새로운 인스턴스 변수도 세팅하게 만든다
3. 기존 변수를 사용하는 모든 곳에서 새 변수를 사용하게 만든다
4. 기존 포맷을 제거한다
5. 새 포맷에 맞게 외부 인터페이스를 변경한다

```python
# 단계 1-2: 데이터 중복
class TestSuite:
    def __init__(self):
        self.tests = []

    def add(self, test):
        self.test = test        # 기존 (곧 제거)
        self.tests.append(test)  # 신규

    # 단계 3: 새 변수 사용
    def run(self, result):
        for test in self.tests:
            test.run(result)

    # 단계 4: self.test 제거 완료
```

---

## 메서드 추출하기 (Extract Method)

길고 복잡한 메서드의 일부분을 **별도의 메서드로 분리**해내고 이를 호출하게 한다.

```python
# Before
def generate_report(data):
    # 데이터 검증 (20줄)
    ...
    # 포맷팅 (30줄)
    ...
    # 출력 (10줄)
    ...

# After
def generate_report(data):
    validated = validate_data(data)
    formatted = format_report(validated)
    output_report(formatted)
```

---

## 메서드 인라인 (Inline Method)

너무 꼬여있거나 산재한 제어 흐름을 단순화하려면, 메서드를 호출하는 부분을 **호출될 메서드의 본문으로 교체**한다.

---

## 인터페이스 추출하기 (Extract Interface)

오퍼레이션에 대한 두 번째 구현을 추가하려면, 공통되는 오퍼레이션을 담고 있는 **인터페이스(Protocol)**를 만든다.

```python
from typing import Protocol


class Repository(Protocol):
    def get(self, id: int) -> dict: ...
    def save(self, data: dict) -> None: ...


class PostgresRepository:
    def get(self, id: int) -> dict: ...
    def save(self, data: dict) -> None: ...


class InMemoryRepository:
    """테스트용 구현"""
    def __init__(self):
        self._store = {}

    def get(self, id: int) -> dict:
        return self._store[id]

    def save(self, data: dict) -> None:
        self._store[data["id"]] = data
```

---

## 메서드 옮기기 (Move Method)

메서드를 원래 있어야 할 장소로 옮기려면, 어울리는 클래스에 메서드를 추가해주고 그것을 호출하게 하라.

---

## 메서드 객체 (Method Object)

여러 개의 매개 변수와 지역 변수를 갖는 복잡한 메서드를 표현하려면, 메서드를 꺼내서 객체로 만든다.

---

> 출처: Kent Beck, 테스트주도 개발 §11
