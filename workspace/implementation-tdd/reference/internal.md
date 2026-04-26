# TDD 개발 방법론 가이드

## 1. TDD 핵심 철학

### 1.1 TDD의 목표 [테스트주도 개발]

TDD의 궁극적 목표는 **작동하는 깔끔한 코드(clean code that works)** 이다.

- 예측 가능한 개발 방법이다. 끊임없이 발생할 버그에 대해 걱정하지 않고, 일이 언제 마무리될지 알 수 있다
- 코드가 가르쳐주는 모든 교훈을 학습할 기회를 갖게 된다. 처음 생각나는 대로 후딱 완료해 버리면 더 나은 것에 대해 생각할 기회를 잃게 된다

### 1.2 TDD를 해야 하는 이유: 용기 [테스트주도 개발]

TDD는 프로그래밍하면서 나타나는 **두려움을 관리하는 방법**이다.

- 두려움이란 "정말 어려운 문제라서 시작 단계인 지금은 어떻게 마무리될지 알 수 없군"하고 생각하는 합리적인 두려움을 말한다
- TDD란 프로그래밍 도중 내린 결정과 그 결정에 대한 피드백 사이의 간격을 인지하고, 이 간격을 통제할 수 있게 해주는 기술이다
- 단, 보안과 동시성은 TDD만으로 목표 달성을 기계적으로 보여주기 부족한 주제이다

---

## 2. TDD 사이클 (Red-Green-Refactor)

### 2.1 기본 사이클 [테스트주도 개발]

```
Red   --> 작은 테스트를 하나 추가하고 실패하는 것을 확인한다
Green --> 테스트를 통과시키기 위해 최소한의 코드를 작성한다
Refactor --> 중복을 제거하고 코드를 정리한다
```

상세 단계:

1. **테스트를 작성한다** -- 마음속에 있는 오퍼레이션이 코드에 어떤 식으로 나타나길 원하는지 생각해보라. 이야기를 써내려가는 것이다
2. **실행 가능하게 만든다** -- 빨리 초록 막대를 보는 것이 가장 중요하다. 깔끔한 해법이 명백히 보인다면 그것을 입력하라. 몇 분 걸릴 것 같으면 일단 적어 놓은 뒤에 원래 문제(초록 막대를 보는 것)로 돌아오자
3. **올바르게 만든다** -- 시스템이 작동하므로 직전에 저질렀던 죄악을 수습하자. 중복을 제거하고 초록 막대로 되돌리자

핵심: '작동하는 깔끔한 코드'에서 **작동하는 것부터 먼저 해결**하는 나누어서 정복하는(divide and conquer) 방식이다.

### 2.2 pytest로 보는 TDD 사이클

```python
# --- Red: 실패하는 테스트 작성 ---
def test_add():
    assert add(3, 4) == 7  # NameError: add가 아직 없다


# --- Green: 최소한의 구현 ---
def add(a, b):
    return 7  # 가짜로 구현하기 (상수 반환)


# --- Refactor: 올바른 구현으로 리팩토링 ---
def add(a, b):
    return a + b
```

---

## 3. 빨간 막대 패턴 (테스트를 언제, 어디에 작성할 것인가) [테스트주도 개발]

### 3.1 한 단계 테스트

목록에서 다음 테스트를 고를 때 기준: **새로운 무언가를 가르쳐 줄 수 있으며, 구현할 수 있다는 확신이 드는 테스트**를 고른다. 아는 것에서 모르는 것으로 방향을 잡는다.

### 3.2 시작 테스트

오퍼레이션이 **아무 일도 하지 않는 경우를 먼저 테스트**한다. 뭔가를 가르쳐 줄 수 있으면서도 빠르게 구현할 수 있는 테스트를 선택하라.

```python
def test_empty_cart_total():
    cart = ShoppingCart()
    assert cart.total() == 0  # 가장 단순한 경우부터 시작
```

### 3.3 설명 테스트

자동화된 테스트가 널리 쓰이게 하려면 **테스트를 통해 설명을 요청하고, 테스트를 통해 설명**해야 한다.

### 3.4 회귀 테스트 (regression test)

시스템 장애가 보고될 때 가장 먼저 할 일: 그 장애로 인하여 실패하는 테스트, 그리고 통과할 경우엔 장애가 수정되었다고 볼 수 있는 테스트를 작성한다.

```python
def test_division_by_zero_returns_error():
    """버그 리포트 #42: 0으로 나눌 때 ZeroDivisionError 대신 None 반환됨"""
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

### 3.5 테스트 목록

시작하기 전에 작성해야 할 **테스트 목록을 모두 적어 둘 것**. 테스트 코드는 테스트 대상이 되는 코드를 작성하기 직전에 작성하는 것이 좋다.

---

## 4. 초록 막대 패턴 (테스트를 통과시키는 전략) [테스트주도 개발]

### 4.1 가짜로 구현하기 (Fake It)

실패하는 테스트를 만든 후 첫 번째 구현은 **상수를 반환**하게 하여 일단 통과시킨다. 그 후 상수를 변수를 사용하는 수식으로 변경한다.

```python
# 단계 1: 상수 반환
def summary(run_count, fail_count):
    return "1 run, 0 failed"

# 단계 2: 일부 변수화
def summary(run_count, fail_count):
    return f"{run_count} run, 0 failed"

# 단계 3: 완전한 구현
def summary(run_count, fail_count):
    return f"{run_count} run, {fail_count} failed"
```

두 가지 효과:

- **심리학적 효과**: 초록 막대 상태에서 확신을 갖고 리팩토링할 수 있다
- **범위 조절**: 하나의 구체적인 예에서 시작해서 일반화하면 쓸데없는 고민으로 혼동하는 일을 예방한다

### 4.2 삼각측량 (Triangulation)

추상화 과정을 테스트로 주도할 때 최대한 보수적으로 하는 방법: **예가 두 개 이상일 때에만 추상화**한다.

```python
def test_plus():
    assert plus(3, 1) == 4
    assert plus(3, 4) == 7  # 두 번째 예에서 추상화


def plus(a, b):
    return a + b  # 두 예제가 있으므로 비로소 일반화
```

어떻게 올바르게 추상화할 것인지 감잡기 어려울 때 사용하면 좋다.

### 4.3 명백한 구현 (Obvious Implementation)

단순한 연산들은 그냥 구현해버린다. 어떻게 구현해야 할지 확신이 들면 그렇게 하는 것이 좋다.

---

## 5. 테스팅 패턴 [테스트주도 개발]

### 5.1 격리된 테스트

- 각각의 테스트는 서로 독립적이어야 하며, **실행 순서에서도 독립적**이어야 한다
- 테스트는 실행하기 위한 환경 세팅이 쉽고 빨라야 한다

### 5.2 단언 우선 (Assert First)

테스트를 작성할 때 **단언(assert)을 제일 먼저 쓰고 시작**한다. 완료될 때 통과해야 할 단언부터 작성하고, 거꾸로 올라가며 필요한 설정을 채운다.

```python
def test_complete_transaction():
    # 1단계: 단언부터 작성
    assert reply.content == "abc"
    assert reader.is_closed()

    # 2단계: reply는 어디서? -> reader에서
    reply = reader.read()

    # 3단계: reader는 어디서? -> 서버 접속
    reader = connect("localhost", DEFAULT_PORT)

    # 4단계: 서버를 먼저 열어야 한다
    server = Server(DEFAULT_PORT, "abc")
```

### 5.3 테스트 데이터

- 테스트를 읽을 때 쉽고 따라가기 좋을 만한 데이터를 사용하라
- 데이터 간에 차이가 있다면 그 속에 **어떤 의미가 있어야** 한다
- 동일한 상수를 여러 의미로 쓰지 마라 (예: `plus(2, 2)` 대신 `plus(2, 3)`)

### 5.4 명백한 데이터

테스트 자체에 예상되는 값과 실제 값을 포함하고, 이 둘 사이의 **관계를 드러내기 위해 노력**하라.

```python
# 나쁨: 49.25가 왜 정답인지 알 수 없다
assert exchange(100, "USD", "GBP") == 49.25

# 좋음: 계산 과정이 드러난다
assert exchange(100, "USD", "GBP") == 100 / 2 * (1 - 0.015)
```

### 5.5 모의 객체 (Mock Object)

비용이 많이 들거나 복잡한 리소스에 의존하는 객체를 테스트하려면 **상수를 반환하게끔 만든 속임수 버전의 리소스**를 만든다.

```python
from unittest.mock import Mock, ANY

# Mock 생성 및 반환값 설정
mock_db = Mock(spec=DatabaseConnection)
mock_db.query.return_value = [
    {"name": "점박이", "species": "미어캣"},
]

# 테스트 실행
result = get_animals(mock_db, "미어캣")

# 호출 검증
mock_db.query.assert_called_once_with(ANY, "미어캣")
assert result[0]["name"] == "점박이"
```

모의 객체의 또 다른 가치는 **가독성**에 있다. 사실적인 데이터로 가득 찬 데이터베이스를 사용한다면, 어떤 쿼리가 결과 14개를 되돌려야 한다고 적은 테스트를 보더라도 왜 14개가 올바른 답인지 알기 어렵다.

### 5.6 크래시 테스트 더미

발생하기 힘든 에러 상황을 테스트할 때, 실제 작업을 수행하는 대신 **예외를 발생시키기만 하는 특수 객체**를 만들어서 호출한다.

```python
from unittest.mock import Mock

def test_file_system_error():
    mock_file = Mock()
    mock_file.write.side_effect = IOError("디스크 가득 참")

    with pytest.raises(IOError):
        save_data(mock_file, "some data")
```

### 5.7 셀프 션트 (Self Shunt)

한 객체가 다른 객체와 올바르게 대화하는지 테스트하려면, 테스트 대상이 되는 객체가 원래 대화 상대가 아니라 **테스트 케이스 자체와 대화하도록** 만든다.

```python
class TestNotification:
    def setup_method(self):
        self.count = 0

    def on_event(self):
        self.count += 1

    def test_listener_called(self):
        result = TestResult()
        result.add_listener(self)  # 테스트 자체가 리스너 역할
        run_test(result)
        assert self.count == 1
```

### 5.8 로그 문자열

메시지의 호출 순서가 올바른지 검사하기 위해 로그 문자열에 메시지가 호출될 때마다 추가한다.

```python
def test_lifecycle_order():
    test = WasRun("test_method")
    result = TestResult()
    test.run(result)
    assert test.log == "setUp test_method tearDown"
```

옵저버를 구현하고 이벤트 통보가 원하는 순서대로 발생하는지 확인하고자 할 때 특히 유용하다.

### 5.9 깨진 테스트 / 깨끗한 체크인

- **혼자 프로그래밍**: 테스트가 깨진 상태로 끝마치면 다음에 어디서부터 시작할지 좋은 단서가 된다
- **팀 프로그래밍**: 테스트가 성공한 상태로 끝마친다

---

## 6. 디자인 패턴과 TDD [테스트주도 개발]

TDD의 각 단계에서 사용되는 디자인 패턴:

| 패턴 | 테스트 작성 | 리팩토링 |
|------|:----:|:----:|
| 커맨드 | O | |
| 값 객체 | O | |
| 널 객체 | | O |
| 템플릿 메서드 | | O |
| 플러거블 객체 | | O |
| 플러거블 셀렉터 | | O |
| 팩토리 메서드 | O | O |
| 임포스터 | O | O |
| 컴포지트 | O | O |
| 수집 매개 변수 | O | O |

### 6.1 값 객체 (Value Object)

객체가 생성된 이후 그 값이 절대 변하지 않게 하여 별칭 문제가 발생하지 않게 한다.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount: int
    currency: str

    def plus(self, other: "Money") -> "Money":
        assert self.currency == other.currency
        return Money(self.amount + other.amount, self.currency)


def test_money_immutable():
    five = Money(5, "USD")
    ten = five.plus(Money(5, "USD"))
    assert ten == Money(10, "USD")
    assert five == Money(5, "USD")  # 원본 불변
```

### 6.2 널 객체 (Null Object)

특별한 상황을 표현하는 새로운 객체를 만들어, 다른 정상적인 상황을 나타내는 객체와 동일한 프로토콜을 제공한다.

```python
class SecurityManager:
    def can_write(self, path: str) -> None:
        # 권한 검사 로직
        ...


class LaxSecurity:
    """널 객체: 보안 검사를 하지 않는 SecurityManager"""
    def can_write(self, path: str) -> None:
        pass  # 항상 허용


def get_security_manager() -> SecurityManager:
    if _security is None:
        return LaxSecurity()  # null 대신 널 객체 반환
    return _security
```

### 6.3 팩토리 메서드 (Factory Method)

생성자를 쓰는 대신 일반 메서드에서 객체를 생성하여 유연성을 확보한다.

```python
class Money:
    @staticmethod
    def dollar(amount: int) -> "Money":
        return Money(amount, "USD")

    @staticmethod
    def franc(amount: int) -> "Money":
        return Money(amount, "CHF")


def test_multiplication():
    five = Money.dollar(5)
    assert five.times(2) == Money.dollar(10)
```

---

## 7. 리팩토링 패턴 [테스트주도 개발]

### 7.1 차이점 일치시키기

비슷해 보이는 두 코드 조각을 합치려면, 두 코드가 **단계적으로 닮아가게끔 수정**한다. 완전히 동일해지면 둘을 합친다.

### 7.2 변화 격리하기

객체나 메서드의 일부만 바꾸려면, 일단 바꿔야 할 부분을 격리한다. 격리 방법에는 **메서드 추출하기**, 객체 추출하기, 메서드 객체 등이 있다.

### 7.3 데이터 이주시키기

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

### 7.4 메서드 추출하기

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

### 7.5 메서드 인라인

너무 꼬여있거나 산재한 제어 흐름을 단순화하려면, 메서드를 호출하는 부분을 **호출될 메서드의 본문으로 교체**한다. 제어 흐름을 이리저리 바꿔가며 실험해보기 위해 사용한다.

### 7.6 인터페이스 추출하기

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

### 7.7 메서드 옮기기

메서드를 원래 있어야 할 장소로 옮기려면, 어울리는 클래스에 메서드를 추가해주고 그것을 호출하게 하라.

### 7.8 메서드 객체

여러 개의 매개 변수와 지역 변수를 갖는 복잡한 메서드를 표현하려면, 메서드를 꺼내서 객체로 만든다.

---

## 참고 문헌

| 출처 | 다룬 내용 |
|------|---------|
| 테스트주도 개발 (Kent Beck) | TDD 사이클, 빨간/초록 막대 패턴, 테스팅 패턴, 디자인 패턴, 리팩토링 |
| 파이썬코딩의기술 (Brett Slatkin) | TestCase, setUp/tearDown, Mock, 의존 관계 캡슐화 |
