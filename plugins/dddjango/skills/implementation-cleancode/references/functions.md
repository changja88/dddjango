# 함수 설계 레퍼런스

함수 수준의 설계와 깊은 모듈 설계에 대한 상세 규칙과 예시.
함수를 작성, 리뷰, 리팩토링하거나 모듈 인터페이스를 설계할 때 참조한다.

---

## 목차

1. [함수 설계](#1-함수-설계)
2. [깊은 모듈 설계](#2-깊은-모듈-설계)

---

## 1. 함수 설계

### 1.1 함수는 작게, 모듈은 깊게 [CC] [APoSD]

**함수 수준**: 의미 있는 이름으로 다른 함수를 추출할 수 있다면,
그 함수는 여러 작업을 하고 있다. **[CC]**

**모듈/클래스 수준**: 최고의 모듈은 단순한 인터페이스 뒤에 강력한 기능을
숨기는 "깊은 모듈"이다. 과도하게 작은 공개 클래스는 인터페이스가
구현만큼 복잡한 "얕은 모듈"이 된다. **[APoSD]**

**통합 가이드라인**: 공개 인터페이스는 깊게 설계하되,
내부 구현은 작은 private 함수로 분해한다.

```python
# bad — 하나의 함수가 너무 많은 일을 한다
def render_page(page_data, is_suite):
    is_test_page = page_data.has_attribute("Test")
    if is_test_page:
        test_page = page_data.get_wiki_page()
        new_content = ""
        new_content += include_setup_pages(test_page, is_suite)
        new_content += page_data.get_content()
        new_content += include_teardown_pages(test_page, is_suite)
        page_data.set_content(new_content)
    return page_data.get_html()

# good — 작은 함수로 분해
def render_page(page_data, is_suite):
    if is_test_page(page_data):
        include_setup_and_teardown(page_data, is_suite)
    return page_data.get_html()
```

```python
# bad — 얕은 모듈: 인터페이스가 구현만큼 복잡
class FileReader:
    def open(self, path): ...
    def check_permissions(self, path): ...
    def read_bytes(self, offset, length): ...
    def decode(self, data, encoding): ...
    def close(self): ...

# good — 깊은 모듈: 단순한 인터페이스 뒤에 복잡성을 숨김
def read_text(path: str, encoding: str = "utf-8") -> str:
    return Path(path).read_text(encoding=encoding)
```

### 1.2 한 가지만 해라 [CC] [IP]

함수는 한 가지 작업을, 하나의 추상화 수준에서 수행한다.
의미 있는 이름으로 하위 함수를 추출할 수 있다면 여러 작업을 하고 있는 것이다.

### 1.3 추상화 수준은 하나로 [CC] [IP]

한 함수 내의 모든 문장은 동일한 추상화 수준이어야 한다.

```python
# bad — 추상화 수준이 혼재
def compute(self):
    self.input()
    self.flags |= 0x0080  # 갑자기 저수준 세부사항
    self.output()

# good
def compute(self):
    self.input()
    self.set_loaded_flag()
    self.output()
```

### 1.4 함수 인수는 최소로 [CC] [IP]

이상적인 인수 개수는 0개이다. 관련 인수들은 객체로 묶어라.

```python
# bad
def make_circle(x: float, y: float, radius: float): ...

# good
def make_circle(center: Point, radius: float): ...
```

### 1.5 플래그 인수를 쓰지 마라 [CC]

불리언 파라미터는 함수가 두 가지 일을 한다는 선언이다. 분리하라.

```python
# bad
def render(is_suite: bool): ...

# good
def render_for_suite(): ...
def render_for_single_test(): ...
```

### 1.6 명령과 조회를 분리하라 [CC]

함수는 무언가를 수행하거나 무언가에 답하거나 둘 중 하나만 해야 한다.

```python
# bad — 둘 다 수행
def set_attribute(name: str, value: str) -> bool: ...

# good
def attribute_exists(name: str) -> bool: ...
def set_attribute(name: str, value: str) -> None: ...
```

### 1.7 부수 효과를 일으키지 마라 [CC]

함수 이름은 함수의 전체 동작과 일치해야 한다.

```python
# bad — check_password가 세션까지 초기화
def check_password(username, password):
    user = find_user(username)
    if user and verify(user.encoded_phrase, password):
        session.initialize()  # 숨겨진 부수 효과
        return True
    return False

# good — 책임 분리
def check_password(username, password):
    user = find_user(username)
    return user and verify(user.encoded_phrase, password)

def login(username, password):
    if check_password(username, password):
        session.initialize()
        return True
    return False
```

### 1.8 대칭성을 활용하라 [IP]

코드의 대칭성을 찾아내서 명확히 표현하면 읽기 수월해진다.

```python
# bad — 비대칭적
def compute(self):
    self.input()
    self.helper.process(self)
    self.output()

# good — 대칭적
def compute(self):
    self.input()
    self.process()
    self.output()
```

### 1.9 루틴의 결정 횟수 제한 [CodeC]

한 루틴의 분기 결정이 약 10을 초과하면 재설계를 고려하라.
전략 패턴, 테이블 기반 디스패치, 분해 등을 활용한다.

---

## 2. 깊은 모듈 설계

### 2.1 깊은 모듈 vs 얕은 모듈 [APoSD]

최고의 모듈은 강력한 기능을 제공하면서 단순한 인터페이스를 갖는다.

```
깊은 모듈 (Deep Module)        얕은 모듈 (Shallow Module)
+---------+                  +-------------------------+
|Interface| <- 단순           |        Interface        | <- 복잡
+---------+                  +-------------------------+
|         |                  | Implementation          | <- 단순
| Impl.   | <- 복잡 (숨김)    +-------------------------+
|         |
+---------+
```

### 2.2 전략적 프로그래밍 vs 전술적 프로그래밍 [APoSD]

| 전술적 (Tactical)                  | 전략적 (Strategic)                         |
|------------------------------------|--------------------------------------------|
| "동작하면 된다, 다음 작업으로"       | "훌륭한 설계를 만들자, 동작도 당연히 해야 한다" |
| 단기적 속도                         | 장기적 생산성에 투자                         |
| 복잡성 누적                         | 복잡성 통제                                 |

**전술적 토네이도(Tactical Tornado)** -- 다른 사람보다 훨씬 빠르게 코드를
쏟아내지만, 완전히 전술적으로 작업하는 프로그래머. 그들이 남긴 코드는
다른 개발자가 유지보수해야 한다. 이 패턴을 피하라.

### 2.3 설계의 레드 플래그 [APoSD]

| 레드 플래그              | 설명                                               |
|-------------------------|----------------------------------------------------|
| 얕은 모듈               | 인터페이스가 구현에 비해 지나치게 복잡                   |
| 정보 누출               | 같은 지식이 여러 모듈에 분산                           |
| 시간적 분해             | 실행 순서에 따라 모듈을 나눈 결과 정보가 분산            |
| 과도한 노출             | 내부 구현이 API에 불필요하게 드러남                     |
| Pass-through 메서드     | 거의 아무것도 하지 않고 다른 메서드를 호출만 하는 메서드   |
| Pass-through 변수       | 긴 호출 체인을 통해 전달만 되는 변수                    |
