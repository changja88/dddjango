# 범용 클린 코드 원칙 종합 가이드

> 이 문서는 다음 4권의 핵심 원칙을 언어 비종속적으로 종합한 것이다.
> 코드 예시는 Python으로 작성되었으나, 원칙 자체는 모든 프로그래밍 언어에 적용된다.
>
> **출처 약어:**
> - **[CC]** Clean Code (로버트 C. 마틴)
> - **[IP]** 켄트벡의 구현 패턴
> - **[OO]** 객체지향의 사실과 오해 (조영호)
> - **[PC]** 파이썬 클린코드 2nd (마리아노 아나야)

---

## 목차

1. [클린 코드란 무엇인가](#1-클린-코드란-무엇인가)
2. [이름 짓기 (Naming)](#2-이름-짓기-naming)
3. [함수와 메서드 설계](#3-함수와-메서드-설계)
4. [주석과 문서화](#4-주석과-문서화)
5. [코드 형식과 구조](#5-코드-형식과-구조)
6. [추상화와 캡슐화](#6-추상화와-캡슐화)
7. [객체 설계 원칙](#7-객체-설계-원칙)
8. [SOLID 원칙](#8-solid-원칙)
9. [상태 관리](#9-상태-관리)
10. [오류 처리](#10-오류-처리)
11. [중복 제거와 DRY](#11-중복-제거와-dry)
12. [협력과 의존성 관리](#12-협력과-의존성-관리)
13. [설계 철학과 프로세스](#13-설계-철학과-프로세스)

---

## 1. 클린 코드란 무엇인가

### 핵심 정의

클린 코드에 대한 정의는 대가들마다 표현이 다르지만 공통된 본질이 있다.

> "깨끗한 코드는 한 가지를 제대로 한다" -- 비야네 스트롭스트룹 **[CC]**

> "깨끗한 코드는 단순하고 직접적이다. 잘 쓴 문장처럼 읽힌다." -- 그래디 부치 **[CC]**

> "클린 코드인지 아닌지는 다른 엔지니어가 코드를 읽고 유지 관리할 수 있는지 여부에 달려 있다" **[PC]**

> "프로그래밍 언어의 진정한 의미는 아이디어를 다른 개발자에게 전달하는 것이다" **[PC]**

### 클린 코드의 세 가지 비결 [CC]

론 제프리스가 정리한 클린 코드의 핵심:

1. **중복 줄이기** -- 같은 작업을 반복하면 아이디어를 제대로 표현하지 못한 증거다
2. **표현력 높이기** -- 의미 있는 이름, 단일 책임 메서드
3. **초반부터 간단한 추상화 고려하기** -- 실제 구현을 감싸는 추상화

### 세 가지 가치 [IP]

켄트 벡은 훌륭한 프로그래밍의 공통 가치를 다음과 같이 정의한다:

- **커뮤니케이션** -- 코드를 쉽게 이해하고, 수정하고, 사용할 수 있는가
- **단순성** -- 복잡도를 낮춰 빠르게 이해할 수 있는가 (단, 과도한 단순화는 커뮤니케이션을 저해)
- **유연성** -- 변경에 대응할 수 있는가 (유연성은 복잡도를 증가시키므로 필요한 경우에만)

### 소프트웨어 비용 공식 [IP]

```
전체 비용 = 개발 비용 + 유지 비용
유지 비용 = 이해 비용 + 수정 비용 + 테스트 비용 + 설치 비용
```

**유지 비용이 대부분을 차지하며, 그중에서도 이해 비용이 핵심이다.**

---

## 2. 이름 짓기 (Naming)

### 2.1 의도를 분명히 밝혀라 [CC]

변수, 함수, 클래스 이름은 존재 이유, 수행 기능, 사용 방법에 모두 답해야 한다.
따로 주석이 필요하다면 의도를 분명히 드러내지 못했다는 뜻이다.

```python
# --- 나쁜 예 ---
d = 7  # 경과 일수

# --- 좋은 예 ---
elapsed_days_since_creation = 7
```

### 2.2 그릇된 정보를 피하라 [CC]

유사한 개념은 유사한 표기법을 사용하되, 실제와 다른 정보를 이름에 담지 마라.

```python
# --- 나쁜 예 ---
account_list = {}  # 실제로는 dict인데 list라고 명명

# --- 좋은 예 ---
accounts = {}
account_map = {}
```

### 2.3 의미 있게 구분하라 [CC]

불용어(Info, Data, a, the)를 사용하면 개념을 구분하지 못한 채 이름만 달리한 것이다.

```python
# --- 나쁜 예 ---
class ProductInfo: ...
class ProductData: ...  # Info와 Data는 아무것도 구분하지 못한다

# --- 좋은 예 ---
class Product: ...
class ProductDetail: ...  # 구체적으로 무엇이 다른지 이름에 반영
```

### 2.4 검색하기 쉬운 이름을 사용하라 [CC]

이름 길이는 범위 크기에 비례해야 한다.

```python
# --- 나쁜 예 ---
for i in range(34):
    s += t[i] * 4 / 5  # 4, 5, s, t가 무엇인지 알 수 없다

# --- 좋은 예 ---
WORK_DAYS_PER_WEEK = 5
for task_index in range(number_of_tasks):
    real_days = task_estimate[task_index] * real_days_per_ideal_day
    weekly_sum += real_days / WORK_DAYS_PER_WEEK
```

### 2.5 한 개념에 한 단어를 사용하라 [CC]

추상적인 개념 하나에 단어 하나를 선택해 고수한다.

```python
# --- 나쁜 예 ---
class UserRepository:
    def fetch_user(self): ...   # fetch

class OrderRepository:
    def retrieve_order(self): ...  # retrieve -- 같은 개념에 다른 단어

# --- 좋은 예 ---
class UserRepository:
    def get_user(self): ...

class OrderRepository:
    def get_order(self): ...  # 통일된 용어 사용
```

### 2.6 클래스 이름은 명사, 메서드 이름은 동사 [CC] [IP]

```python
# 클래스: 명사 또는 명사구
class Customer: ...
class AddressParser: ...

# 메서드: 동사 또는 동사구
def post_payment(self): ...
def delete_page(self): ...
```

### 2.7 의도 제시형 이름 [IP]

메서드 이름에는 의도만 전달하고 구현 전략은 담지 마라.

```python
# --- 나쁜 예 ---
def linear_search_customer(customer_id: str) -> Customer: ...

# --- 좋은 예 ---
def find_customer(customer_id: str) -> Customer: ...
```

### 2.8 역할 제시형 작명 [IP]

변수 이름은 연산에서의 역할을 반영하여 짓는다. 생명기간, 범위, 타입은 문맥에서 전달된다.

```python
# --- 나쁜 예 ---
temp_str_list = get_items()

# --- 좋은 예 ---
results = get_items()         # 컬렉터 역할
pending_count = len(queue)    # 카운터 역할
```

### 2.9 컬렉션은 복수형으로 [IP]

여러 데이터를 저장하는 변수는 복수형이어야 한다.

```python
# --- 나쁜 예 ---
member = [user1, user2, user3]

# --- 좋은 예 ---
members = [user1, user2, user3]
```

---

## 3. 함수와 메서드 설계

### 3.1 작게 만들어라 [CC]

함수를 만드는 첫째 규칙은 "작게!"이고, 둘째 규칙도 "더 작게!"이다.

```python
# --- 나쁜 예 ---
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

# --- 좋은 예 ---
def render_page(page_data, is_suite):
    if is_test_page(page_data):
        include_setup_and_teardown(page_data, is_suite)
    return page_data.get_html()
```

### 3.2 한 가지만 해라 [CC] [IP]

> "함수는 한 가지를 해야 한다. 그 한 가지를 잘 해야 한다. 그 한 가지만을 해야 한다." **[CC]**

의미 있는 이름으로 다른 함수를 추출할 수 있다면, 그 함수는 여러 작업을 하고 있다.

### 3.3 추상화 수준은 하나로 [CC] [IP]

한 함수 내의 모든 문장은 동일한 추상화 수준이어야 한다.

```python
# --- 나쁜 예 ---
def compute(self):
    self.input()
    self.flags |= 0x0080  # 갑자기 추상화 수준이 바뀜
    self.output()

# --- 좋은 예 ---
def compute(self):
    self.input()
    self.set_loaded_flag()  # 동일한 추상화 수준 유지
    self.output()
```

### 3.4 함수 인수는 최소로 [CC] [IP]

이상적인 인수 개수는 0개이다. 인수가 많으면 인수 객체를 만들어라.

```python
# --- 나쁜 예 ---
def make_circle(x: float, y: float, radius: float): ...

# --- 좋은 예 ---
def make_circle(center: Point, radius: float): ...
```

### 3.5 플래그 인수를 쓰지 마라 [CC]

플래그 인수는 함수가 여러 가지 일을 한다고 대놓고 선언하는 것이다.

```python
# --- 나쁜 예 ---
def render(is_suite: bool): ...

# --- 좋은 예 ---
def render_for_suite(): ...
def render_for_single_test(): ...
```

### 3.6 명령과 조회를 분리하라 [CC]

함수는 무언가를 수행하거나 무언가에 답하거나 둘 중 하나만 해야 한다.

```python
# --- 나쁜 예 ---
def set_attribute(name: str, value: str) -> bool:
    """속성을 설정하고 성공 여부를 반환"""
    ...

if set_attribute("username", "alice"):  # 설정인가? 확인인가?
    ...

# --- 좋은 예 ---
def attribute_exists(name: str) -> bool: ...
def set_attribute(name: str, value: str) -> None: ...

if attribute_exists("username"):
    set_attribute("username", "alice")
```

### 3.7 부수 효과를 일으키지 마라 [CC]

부수 효과는 시간적 결합(temporal coupling)이나 순서 종속성을 초래한다.

```python
# --- 나쁜 예 ---
def check_password(username: str, password: str) -> bool:
    user = find_user(username)
    if user and verify(user.encoded_phrase, password):
        session.initialize()  # 부수 효과! 이름에서 예측 불가
        return True
    return False

# --- 좋은 예 ---
def check_password(username: str, password: str) -> bool:
    user = find_user(username)
    return user and verify(user.encoded_phrase, password)

def login(username: str, password: str) -> bool:
    if check_password(username, password):
        session.initialize()
        return True
    return False
```

### 3.8 대칭성을 활용하라 [IP]

코드의 대칭성을 찾아내서 명확히 표현하면 읽기 수월해진다.

```python
# --- 나쁜 예 ---
def compute(self):
    self.input()
    self.helper.process(self)  # 비대칭적
    self.output()

# --- 좋은 예 ---
def compute(self):
    self.input()
    self.process()  # 대칭적 -- 모두 self에게 메시지
    self.output()

def process(self):
    self.helper.process(self)
```

---

## 4. 주석과 문서화

### 4.1 주석은 필요악이다 [CC] [IP]

> "주석은 코드로 의도를 표현하는 것에 실패했기 때문에 작성한다." **[CC]**

```python
# --- 나쁜 예 ---
# 직원에게 복지 혜택을 받을 자격이 있는지 검사한다
if employee.flags & HOURLY_FLAG and employee.age > 65:
    ...

# --- 좋은 예 ---
if employee.is_eligible_for_full_benefits():
    ...
```

### 4.2 코드 자체에서 얻을 수 없는 정보만 주석으로 [IP]

주석을 작성하고 코드와 주석 간 일관성을 유지하기 위해서는 비용이 발생하므로, 이를 정당화할 수 있는 경우에만 사용해야 한다.

### 4.3 유용한 주석의 유형 [CC]

- **법적인 주석** -- 저작권, 라이선스 정보
- **의도를 설명하는 주석** -- "왜" 이런 결정을 했는지
- **결과를 경고하는 주석** -- 스레드 안전성 경고 등
- **TODO 주석** -- 앞으로 할 일 (나쁜 코드의 핑계로 사용 금지)
- **중요성을 강조하는 주석** -- 대수롭지 않아 보이지만 중요한 것

### 4.4 나쁜 주석의 유형 [CC]

- 같은 이야기를 중복하는 주석
- 의무적으로 다는 주석
- 이력을 기록하는 주석 (소스 관리 시스템이 있다)
- 있으나 마나 한 주석 (당연한 사실 언급)
- 주석으로 처리한 코드 (그냥 삭제하라)

### 4.5 문서화와 주석은 다르다 [PC]

- **주석(comment)**: 가능한 한 적게. 코드 자체가 문서화되어야 한다.
- **문서(docstring)**: 컴포넌트의 동작 방식, 입출력 정보를 설명. "이유가 아니라 설명"이다.

---

## 5. 코드 형식과 구조

### 5.1 형식은 의사소통이다 [CC]

코드 형식은 의사소통의 일환이다. 구현 스타일과 가독성 수준은 유지보수 용이성과 확장성에 계속 영향을 미친다.

### 5.2 적절한 행 길이를 유지하라 [CC]

500줄이 넘지 않고 대부분 200줄 정도인 파일로도 커다란 시스템을 구축할 수 있다.

### 5.3 일관성이 핵심이다 [PC]

좋은 코드 레이아웃에서 가장 필요한 특성은 **일관성**이다. 코드가 일관되게 구조화되어 있으면 가독성이 높아지고 이해하기 쉬워진다.

### 5.4 자동화 도구를 활용하라 [PC]

포매팅, 린팅, 타입 검사를 자동화해야 한다. 이 모든 검사는 CI(지속적 통합)의 일부가 되어야 한다.

---

## 6. 추상화와 캡슐화

### 6.1 추상화를 통한 복잡성 극복 [OO]

> "현상은 복잡하다. 법칙은 단순하다. 버릴 게 무엇인지 알아내라." -- 파인만

추상화의 두 가지 방법:
1. 공통점을 취하고 차이점을 버리는 **일반화**
2. 불필요한 세부 사항을 제거하는 **단순화**

### 6.2 구현이 아니라 인터페이스에 맞춰 코딩하라 [IP] [OO]

> "설계상의 결정을 필요 이상으로 노출하지 말라" **[IP]**

```python
# --- 나쁜 예 ---
class ReportGenerator:
    def generate(self, data: list):
        mysql_conn = MySQLConnection()  # 구체적 구현에 의존
        mysql_conn.save(data)

# --- 좋은 예 ---
class ReportGenerator:
    def __init__(self, storage: StorageInterface):
        self._storage = storage

    def generate(self, data: list):
        self._storage.save(data)  # 인터페이스에 의존
```

### 6.3 상태를 캡슐화하라 [OO]

객체의 자율성은 내부와 외부를 명확하게 구분하는 것으로부터 나온다.

> "객체가 무엇(what)을 수행하는지는 알 수 있지만 어떻게(how) 수행하는지에 대해서는 알 수 없어야 한다." **[OO]**

```python
# --- 나쁜 예 ---
class BankAccount:
    def __init__(self):
        self.balance = 0  # 외부에서 직접 수정 가능

account = BankAccount()
account.balance = -1000  # 불변식 위반 가능

# --- 좋은 예 ---
class BankAccount:
    def __init__(self):
        self._balance = 0

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("입금액은 양수여야 합니다")
        self._balance += amount

    def get_balance(self) -> float:
        return self._balance
```

### 6.4 인터페이스와 구현의 분리 원칙 [OO]

> "객체를 구성하지만 공용 인터페이스에 포함되지 않는 모든 것이 구현에 포함된다." **[OO]**

객체 설계의 핵심은 외부에 공개되는 인터페이스와 내부에 감춰지는 구현을 명확하게 분리하는 것이다.

---

## 7. 객체 설계 원칙

### 7.1 행동이 상태를 결정한다 [OO]

상태를 먼저 결정하고 행동을 나중에 결정하면 설계에 나쁜 영향을 끼친다.

> "어떤 객체가 어떤 타입에 속하는지를 결정하는 것은 객체가 수행하는 행동이다." **[OO]**

```python
# --- 나쁜 예: 데이터 주도 설계 ---
class Employee:
    def __init__(self):
        self.name = ""
        self.salary = 0
        self.department = ""
    # 데이터를 먼저 정의하고 행동은 나중에...

# --- 좋은 예: 책임 주도 설계 ---
class Employee:
    def calculate_pay(self) -> Money: ...
    def report_hours(self) -> Hours: ...
    # 행동을 먼저 정의하고 필요한 데이터는 내부에 캡슐화
```

### 7.2 묻지 말고 시켜라 (Tell, Don't Ask) [OO]

어떻게 해야 하는지 묻지 말고 무엇을 해야 하는지 요청하라.

```python
# --- 나쁜 예: 물어보고 직접 처리 ---
if order.get_status() == "paid":
    order.set_status("shipped")
    warehouse.remove_stock(order.get_items())

# --- 좋은 예: 시키기 ---
order.ship(warehouse)  # 주문 객체가 자율적으로 처리
```

### 7.3 조건문을 다형성으로 대체하라 [CC] [IP]

중복되는 조건부 로직이나 분기문의 결과에 따라 로직이 달라지는 경우, 명시적인 조건문 대신 메시지(다형성)를 사용하는 것이 좋다.

```python
# --- 나쁜 예 ---
def calculate_pay(employee):
    if employee.type == "COMMISSIONED":
        return calculate_commissioned_pay(employee)
    elif employee.type == "HOURLY":
        return calculate_hourly_pay(employee)
    elif employee.type == "SALARIED":
        return calculate_salaried_pay(employee)

# --- 좋은 예 ---
class Employee:
    def calculate_pay(self) -> Money:
        raise NotImplementedError

class CommissionedEmployee(Employee):
    def calculate_pay(self) -> Money: ...

class HourlyEmployee(Employee):
    def calculate_pay(self) -> Money: ...

class SalariedEmployee(Employee):
    def calculate_pay(self) -> Money: ...
```

### 7.4 위임으로 유연성 확보 [IP]

하위클래스는 정적(생성 시점 결정)이지만 위임은 런타임에 변경 가능하다.

```python
# --- 나쁜 예: 조건문으로 도구 분기 ---
def mouse_down(self):
    if self.get_tool() == "SELECTING":
        ...
    elif self.get_tool() == "CREATING_RECTANGLE":
        ...

# --- 좋은 예: 위임 ---
def mouse_down(self):
    self.get_tool().mouse_down()  # 도구 객체에 위임
```

### 7.5 로직과 데이터를 함께 유지하라 [IP]

데이터와 그 데이터를 처리하는 로직을 밀접하게, 가급적 같은 메서드 혹은 같은 객체 내에 배치하라.

```python
# --- 나쁜 예 ---
def format_address(street, city, state, zipcode):
    return f"{street}, {city}, {state} {zipcode}"

# --- 좋은 예 ---
class Address:
    def __init__(self, street, city, state, zipcode):
        self.street = street
        self.city = city
        self.state = state
        self.zipcode = zipcode

    def format(self):
        return f"{self.street}, {self.city}, {self.state} {self.zipcode}"
```

### 7.6 변화율에 따라 분리하라 [IP]

함께 변하는 로직과 데이터는 함께 관리하고, 변화율이 다른 것은 분리한다.

```python
# --- 나쁜 예 ---
class Payment:
    def __init__(self, value, currency):
        self.value = value
        self.currency = currency  # value와 currency는 항상 함께 변한다

# --- 좋은 예 ---
class Money:
    def __init__(self, value, currency):
        self.value = value
        self.currency = currency

class Payment:
    def __init__(self, amount: Money):
        self.amount = amount  # 대칭적인 필드를 별도 객체로 분리
```

---

## 8. SOLID 원칙

### 8.1 단일 책임 원칙 (SRP) [PC] [CC]

클래스는 하나의 책임만 가져야 하며, 변경 이유도 단 하나여야 한다.

```python
# --- 나쁜 예 ---
class SystemMonitor:
    def load_activity(self): ...
    def identify_events(self): ...
    def stream_events(self): ...  # 세 가지 독립적 책임

# --- 좋은 예 ---
class ActivityLoader: ...
class EventIdentifier: ...
class EventStreamer: ...
```

> "만약 객체의 속성이나 메서드의 특성이 다른 클래스에서 발견되면 이들을 다른 곳으로 옮겨야 한다." **[PC]**

### 8.2 개방/폐쇄 원칙 (OCP) [PC] [CC]

확장에는 개방되고 수정에는 폐쇄되어야 한다. 새로운 요구사항이 생기면 새로운 것을 추가만 할 뿐 기존 코드는 그대로 유지해야 한다.

```python
# --- 나쁜 예 ---
class SystemMonitor:
    def identify_event(self):
        if self.event_data["before"]["session"] == 0 and \
           self.event_data["after"]["session"] == 1:
            return LoginEvent(self.event_data)
        # 새 이벤트마다 이 메서드를 수정해야 한다

# --- 좋은 예 ---
class Event:
    @staticmethod
    def meets_condition(event_data: dict) -> bool:
        return False

class LoginEvent(Event):
    @staticmethod
    def meets_condition(event_data: dict) -> bool:
        return (event_data["before"]["session"] == 0
                and event_data["after"]["session"] == 1)

class SystemMonitor:
    def identify_event(self):
        for event_cls in Event.__subclasses__():
            if event_cls.meets_condition(self.event_data):
                return event_cls(self.event_data)
        return UnknownEvent(self.event_data)
```

### 8.3 리스코프 치환 원칙 (LSP) [PC] [OO]

하위 클래스는 부모 클래스를 대체할 수 있어야 한다. 클라이언트는 사용하는 클래스의 계층 구조 변경에 대해 완전히 독립적이어야 한다.

```python
# --- 나쁜 예: LSP 위반 ---
class Event:
    def meets_condition(self, event_data: dict) -> bool:
        return False

class LoginEvent(Event):
    def meets_condition(self, event_data: list) -> bool:  # 파라미터 타입 변경!
        return bool(event_data)

# --- 좋은 예 ---
class LoginEvent(Event):
    def meets_condition(self, event_data: dict) -> bool:  # 부모와 동일한 서명
        return event_data.get("after", {}).get("session") == 1
```

### 8.4 인터페이스 분리 원칙 (ISP) [PC]

작은 인터페이스를 만들어라. 클라이언트가 필요하지 않은 메서드를 구현하도록 강제하지 마라.

```python
# --- 나쁜 예 ---
class EventParser:
    def from_xml(self): ...
    def from_json(self): ...  # 어떤 클래스는 둘 중 하나만 필요할 수 있다

# --- 좋은 예 ---
class XMLEventParser:
    def from_xml(self): ...

class JSONEventParser:
    def from_json(self): ...
```

### 8.5 의존성 역전 원칙 (DIP) [PC]

구체적 구현이 아닌 추상화에 의존하라. 세부 사항은 추상화에 의존해야 한다.

```python
# --- 나쁜 예 ---
class EventStreamer:
    def __init__(self):
        self._target = Syslog()  # 구체 클래스에 직접 의존

# --- 좋은 예 ---
class EventStreamer:
    def __init__(self, target: DataTargetClient):  # 인터페이스에 의존
        self._target = target

    def stream(self, events):
        for event in events:
            self._target.send(event.serialize())
```

> "일반적으로 구체적인 구현이 추상 컴포넌트보다 훨씬 더 자주 바뀔 것이다. 이런 이유로 추상화를 사용한다." **[PC]**

---

## 9. 상태 관리

### 9.1 변수의 범위와 생명주기를 일치시켜라 [IP]

변수의 범위와 생명기간은 가까운 것이 좋다. 같은 범위에서 정의된 변수들은 같은 생명기간을 갖는 것이 좋다.

```python
# --- 나쁜 예 ---
result = None  # 훨씬 나중에 사용될 변수를 미리 선언
# ... 100줄의 코드 ...
result = compute()

# --- 좋은 예 ---
# ... 100줄의 코드 ...
result = compute()  # 사용 직전에 선언
```

### 9.2 값 객체를 활용하라 [IP] [OO]

변치 않는 값을 표현할 때는 값 객체를 사용하라. 생성 후 상태가 변경되지 않아야 한다.

```python
# --- 나쁜 예: 가변 상태 ---
class Transaction:
    def __init__(self, value):
        self.value = value  # 외부에서 변경 가능

# --- 좋은 예: 값 객체 ---
from dataclasses import dataclass

@dataclass(frozen=True)
class Transaction:
    value: int
    credit_account: str
    debit_account: str
    # frozen=True로 불변 보장
```

### 9.3 상태 접근은 간접 접근을 기본으로 [IP]

내부에서는 직접 접근을 허용하되, 외부에서는 메서드를 통해 접근하라.

```python
# --- 나쁜 예 ---
class Rectangle:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.area = 0  # width/height와 의존 관계인데 직접 접근

# --- 좋은 예 ---
class Rectangle:
    def __init__(self, width, height):
        self._width = width
        self._height = height

    @property
    def area(self):
        return self._width * self._height
```

### 9.4 공용 상태 vs 가변 상태 [IP]

- **공용 상태**: 여러 연산에서 같은 데이터를 사용하는 경우 필드로 선언
- **가변 상태**: 인스턴스마다 전혀 다른 데이터 요소가 필요한 경우에만 맵으로 표현
- 가능하다면 공용 상태를 사용하는 것이 좋다

---

## 10. 오류 처리

### 10.1 오류 코드보다 예외를 사용하라 [CC]

오류 코드를 반환하면 호출자는 오류 코드를 곧바로 처리해야 하고, 명령/조회 분리 규칙을 위반한다.

```python
# --- 나쁜 예 ---
result = delete_page(page)
if result == E_OK:
    result = registry.delete_reference(page.name)
    if result == E_OK:
        ...

# --- 좋은 예 ---
try:
    delete_page(page)
    registry.delete_reference(page.name)
    config_keys.delete_key(page.name.make_key())
except Exception as e:
    logger.error(e)
```

### 10.2 Try/Catch 블록은 분리하라 [CC]

정상 동작과 오류 처리 동작을 분리하면 이해하고 수정하기 쉬워진다.

```python
# --- 좋은 예 ---
def delete(page):
    try:
        delete_page_and_all_references(page)
    except Exception as e:
        log_error(e)

def delete_page_and_all_references(page):
    delete_page(page)
    registry.delete_reference(page.name)
    config_keys.delete_key(page.name.make_key())
```

### 10.3 올바른 추상화 수준에서 예외를 처리하라 [PC]

예외는 함수가 캡슐화하고 있는 로직에 대한 것이어야 한다. 서로 다른 수준의 추상화를 혼합하지 마라.

### 10.4 보호절(Guard Clause)을 활용하라 [IP]

주요 흐름과 예외 흐름의 차이를 부각시켜라.

```python
# --- 나쁜 예 ---
def compute():
    server = get_server()
    if server is not None:
        client = server.get_client()
        if client is not None:
            request = client.get_request()
            if request is not None:
                process_request(request)

# --- 좋은 예 ---
def compute():
    server = get_server()
    if server is None: return
    client = server.get_client()
    if client is None: return
    request = client.get_request()
    if request is None: return
    process_request(request)
```

### 10.5 계약에 의한 디자인 (DbC) [PC]

사전조건과 사후조건을 명시적으로 정의하여 책임 소재를 명확히 하라.

```python
def add_positive_numbers(a: float, b: float) -> float:
    """양수 두 개를 더한다."""
    if a <= 0 or b <= 0:
        raise ValueError("입력 값은 양수여야 합니다")  # 사전 조건

    result = a + b

    assert result > 0, "결과 값은 양수여야 합니다"  # 사후 조건
    return result
```

---

## 11. 중복 제거와 DRY

### 11.1 중복은 모든 악의 근원이다 [CC] [IP] [PC]

> "어쩌면 중복은 소프트웨어에서 모든 악의 근원이다." **[CC]**

DRY(Do not Repeat Yourself): 코드에 있는 지식은 단 한번, 단 한 곳에 정의되어야 한다. **[PC]**

```python
# --- 나쁜 예 ---
def process_students(students):
    ranking = sorted(students, key=lambda s: s.passed * 11 - s.failed * 5)
    for student in ranking:
        score = student.passed * 11 - student.failed * 5  # 중복!
        print(f"{student.name}: {score}")

# --- 좋은 예 ---
def calculate_score(student) -> int:
    return student.passed * 11 - student.failed * 5

def process_students(students):
    ranking = sorted(students, key=calculate_score)
    for student in ranking:
        print(f"{student.name}: {calculate_score(student)}")
```

### 11.2 지역적 변화의 원칙 [IP]

코드를 수정할 때 함께 바꿔야 하는 부분을 최소화하라. 중복을 없애는 방법은 프로그램을 여러 작은 부분으로 나누는 것이다.

---

## 12. 협력과 의존성 관리

### 12.1 역할, 책임, 협력 [OO]

> "객체지향에서 가장 중요한 개념은 역할, 책임, 협력이다." **[OO]**

- **역할**: 대체 가능성을 의미한다 (다형성)
- **책임**: 객체가 아는 것(knowing)과 하는 것(doing)으로 구성
- **협력**: 역할과 책임을 조화롭게 연결

### 12.2 메시지가 인터페이스를 결정한다 [OO]

> "객체가 메시지를 선택하는 것이 아니라 메시지가 객체를 선택하게 해야 한다." **[OO]**

어떤 행위(메시지)가 필요한지 먼저 결정한 후에, 이 행위를 수행할 객체를 결정하라 (What/Who 사이클).

### 12.3 응집력과 결합력 [PC] [IP]

- **응집력(Cohesion)**: 높을수록 좋다. 작고 잘 정의된 목적을 가진 모듈
- **결합력(Coupling)**: 낮을수록 좋다. 객체 간 의존성 최소화

```python
# --- 나쁜 예: 높은 결합력 ---
class Order:
    def process(self):
        db = MySQLDatabase()  # 구체 클래스에 직접 의존
        db.save(self.data)
        email = SMTPEmailSender()  # 또 다른 구체 클래스에 직접 의존
        email.send(self.confirmation)

# --- 좋은 예: 낮은 결합력 ---
class Order:
    def __init__(self, repository: Repository, notifier: Notifier):
        self._repository = repository
        self._notifier = notifier

    def process(self):
        self._repository.save(self.data)
        self._notifier.send(self.confirmation)
```

### 12.4 상속보다 합성을 우선하라 [IP] [PC] [OO]

상속의 단점:
- 되돌리기 어렵다
- 하위 클래스는 상위 클래스에 강하게 결합된다
- 동적으로 변화하는 로직을 나타낼 수 없다

> "단지 부모 클래스에 있는 메서드를 공짜로 얻을 수 있기 때문에 상속을 하는 것은 좋지 않다." **[PC]**

```python
# --- 나쁜 예: 재사용만을 위한 상속 ---
class TransactionPolicy(collections.UserList):
    """리스트의 모든 메서드가 노출됨 -- 필요하지 않은 것까지"""
    pass

# --- 좋은 예: 합성 ---
class TransactionPolicy:
    def __init__(self):
        self._transactions = []

    def add(self, transaction):
        self._transactions.append(transaction)

    def __len__(self):
        return len(self._transactions)
```

---

## 13. 설계 철학과 프로세스

### 13.1 안정적인 구조 중심 설계 [OO]

기능을 중심으로 구조를 종속시키면 변경에 취약하다.
안정적인 구조(도메인 모델)를 중심으로 기능을 종속시켜야 한다.

> "도메인 모델이 안정적인 이유는 사용자가 도메인의 본질적인 측면을 가장 잘 이해하고 있기 때문이다." **[OO]**

### 13.2 책임 주도 설계 (RDD) [OO]

1. 시스템이 사용자에게 제공해야 하는 기능인 시스템 책임을 파악한다
2. 시스템 책임을 더 작은 책임으로 분할한다
3. 분할된 책임을 수행할 적절한 객체에 할당한다
4. 객체가 다른 객체의 도움이 필요하면 협력을 설계한다

### 13.3 세 가지 관점으로 클래스를 바라보라 [OO]

- **개념적 관점**: 도메인 안의 개념과 관계를 반영
- **명세 관점**: 객체가 협력을 위해 "무엇"을 할 수 있는가 (인터페이스)
- **구현 관점**: 객체의 책임을 "어떻게" 수행할 것인가

> "구현이 아니라 인터페이스에 대해 프로그래밍하라." -- GoF **[OO]**

### 13.4 YAGNI [PC]

유지보수 가능한 소프트웨어를 만드는 것은 미래의 요구사항을 예측하는 것이 아니다. 현재 요구사항을 잘 해결하고, 나중에 수정하기 쉽도록 작성하는 것이다.

### 13.5 함수를 어떻게 짜는가 [CC]

1. 처음에는 길고 복잡하다
2. 다듬고 또 다듬는다
3. 다듬는 와중에도 항상 단위 테스트는 통과한다

> "설계를 간단히 끝내고 최대한 빨리 구현에 돌입하라. 머릿속에 객체의 협력 구조가 번뜩인다면 그대로 코드를 구현하기 시작하라." **[OO]**

### 13.6 패턴은 절대적 진리가 아니다 [IP]

> "패턴은 절대적인 진리가 아니므로 상황에 따라 패턴을 적절히 변화시켜 사용해야 한다." **[IP]**

특정 상황에서 특정 패턴을 왜 쓰는지를 알아야 한다. 원칙을 명확하게 알고 있다면 새로운 패턴을 만들 수도 있다.

---

## 핵심 요약 체크리스트

| 범주 | 원칙 | 출처 |
|------|------|------|
| 이름 | 의도를 드러내는 이름을 사용하라 | [CC] [IP] |
| 이름 | 한 개념에 한 단어, 말장난 금지 | [CC] |
| 이름 | 클래스는 명사, 메서드는 동사 | [CC] [IP] |
| 함수 | 작게, 한 가지만, 추상화 수준 통일 | [CC] [IP] |
| 함수 | 인수 최소화, 플래그 인수 금지 | [CC] |
| 함수 | 명령/조회 분리, 부수 효과 금지 | [CC] |
| 주석 | 코드로 의도를 표현하고, 주석은 최소화 | [CC] [IP] [PC] |
| 객체 | 행동이 상태를 결정한다 | [OO] |
| 객체 | 캡슐화: what은 공개, how는 은닉 | [OO] [IP] |
| 객체 | 인터페이스에 맞춰 코딩하라 | [OO] [IP] |
| 객체 | 묻지 말고 시켜라 (Tell, Don't Ask) | [OO] |
| SOLID | 단일 책임, 개방/폐쇄, 리스코프 치환 | [PC] [CC] |
| SOLID | 인터페이스 분리, 의존성 역전 | [PC] |
| 설계 | 중복 제거 (DRY) | [CC] [IP] [PC] |
| 설계 | 로직과 데이터를 함께 유지 | [IP] |
| 설계 | 변화율에 따라 분리 | [IP] |
| 설계 | 안정적 구조 중심, 책임 주도 설계 | [OO] |
| 오류 | 예외 사용, Try/Catch 분리, 보호절 활용 | [CC] [IP] [PC] |
| 프로세스 | 일단 동작하게 만들고 다듬어라 | [CC] [OO] |
| 프로세스 | YAGNI: 현재에 집중하라 | [PC] |
