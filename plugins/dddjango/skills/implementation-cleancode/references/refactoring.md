# 협력, 의존성, 리팩토링 레퍼런스

## 목차

1. [협력과 의존성 관리 (14장)](#1-협력과-의존성-관리)
2. [리팩토링 (15장)](#2-리팩토링)

---

## 1. 협력과 의존성 관리

### 1.1 역할, 책임, 협력 [OO]

- **역할** -- 대체 가능성을 의미한다 (다형성)
- **책임** -- 객체가 아는 것(knowing)과 하는 것(doing)으로 구성
- **협력** -- 역할과 책임을 조화롭게 연결

어떤 행위(메시지)가 필요한지 먼저 결정한 후에, 이 행위를 수행할 객체를
결정하라 (What/Who 사이클).

### 1.2 응집력과 결합력 [PC] [IP]

- **응집력(Cohesion)** (높을수록 좋다) -- 작고 잘 정의된 목적을 가진 모듈
- **결합력(Coupling)** (낮을수록 좋다) -- 객체 간 의존성 최소화

```python
# bad — 높은 결합력
class Order:
    def process(self):
        db = MySQLDatabase()
        db.save(self.data)
        email = SMTPEmailSender()
        email.send(self.confirmation)

# good — 낮은 결합력 (의존성 주입)
class Order:
    def __init__(self, repository: Repository, notifier: Notifier):
        self._repository = repository
        self._notifier = notifier

    def process(self):
        self._repository.save(self.data)
        self._notifier.send(self.confirmation)
```

### 1.3 상속보다 합성을 우선하라 [IP] [PC] [OO]

상속의 단점: 되돌리기 어렵고, 하위 클래스가 상위 클래스에 강하게 결합되며,
동적으로 변화하는 로직을 나타낼 수 없다.

```python
# bad — 재사용만을 위한 상속
class TransactionPolicy(collections.UserList):
    pass  # 리스트의 모든 메서드가 노출됨, 필요하지 않은 것까지

# good — 합성
class TransactionPolicy:
    def __init__(self):
        self._transactions = []

    def add(self, transaction):
        self._transactions.append(transaction)

    def __len__(self):
        return len(self._transactions)
```

### 1.4 직교성 (Orthogonality) [PP]

두 가지 이상의 것이 직교적이면, 하나의 변경이 다른 것에 영향을 주지 않는다.
관련 없는 것들 사이의 결합을 제거하라.

```python
# bad — UI 로직과 비즈니스 로직이 결합
class ReportGenerator:
    def generate(self, data):
        html = "<html><body>"
        total = sum(item["amount"] for item in data)
        tax = total * 0.1
        html += f"<h1>Total: {total}</h1><p>Tax: {tax}</p>"
        html += "</body></html>"
        return html

# good — 직교적 분리
class TaxCalculator:
    RATE = 0.1
    def calculate(self, amount: float) -> float:
        return amount * self.RATE

class ReportData:
    def __init__(self, items):
        self.total = sum(item["amount"] for item in items)
        self.tax = TaxCalculator().calculate(self.total)

class HTMLReportRenderer:
    def render(self, report: ReportData) -> str:
        return (f"<html><body>"
                f"<h1>Total: {report.total}</h1>"
                f"<p>Tax: {report.tax}</p>"
                f"</body></html>")
```

### 1.5 가역성 (Reversibility) [PP]

되돌리기 어려운 결정을 피하라. 추상화를 통해 변동이 큰 의존성을 교체 가능하게 만들라.

```python
# bad — 특정 DB에 직접 결합
class UserRepository:
    def find(self, user_id):
        conn = psycopg2.connect(...)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()

# good — 추상 인터페이스로 교체 가능
class UserRepository(Protocol):
    def find(self, user_id: int) -> User | None: ...

class PostgresUserRepository:
    def find(self, user_id: int) -> User | None: ...

class MongoUserRepository:
    def find(self, user_id: int) -> User | None: ...
```

---

## 2. 리팩토링

### 2.1 코드 스멜 카탈로그 [Ref]

코드 스멜은 더 깊은 문제를 나타내는 표면적 징후다. 리팩토링의 출발점이 된다.

#### 비대화 스멜 (Bloaters)

| 스멜                   | 설명                                         |
|------------------------|----------------------------------------------|
| Long Method            | 메서드가 너무 길어 이해하기 어렵다               |
| Long Parameter List    | 파라미터가 너무 많다                            |
| Large Class            | 한 클래스가 너무 많은 책임을 진다                |
| Primitive Obsession    | 원시 타입에 지나치게 의존한다                    |
| Data Clumps            | 같은 데이터 그룹이 반복 등장한다                 |

```python
# Primitive Obsession -> 값 객체(Value Object) 도입
# bad
def calculate_price(amount: float, currency: str) -> str:
    if currency == "USD": return f"${amount:.2f}"
    elif currency == "KRW": return f"{amount:,.0f}원"

# good
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str
    def display(self) -> str:
        formats = {"USD": lambda a: f"${a:.2f}", "KRW": lambda a: f"{a:,.0f}원"}
        return formats.get(self.currency, lambda a: f"{a} {self.currency}")(self.amount)
```

```python
# Data Clumps -> 매개변수 객체(Parameter Object) 도입
# bad
def distance(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

# good
@dataclass(frozen=True)
class Point:
    x: float
    y: float
    def distance_to(self, other: "Point") -> float:
        return ((other.x - self.x) ** 2 + (other.y - self.y) ** 2) ** 0.5
```

#### 객체지향 남용 스멜 (OO Abusers)

| 스멜                     | 설명                                            |
|--------------------------|-------------------------------------------------|
| Refused Bequest          | 하위 클래스가 상속받은 인터페이스 중 일부만 사용     |
| Alternative Interfaces   | 같은 일을 하지만 메서드 이름이 다른 클래스들         |
| Temporary Field          | 특정 상황에서만 사용되는 인스턴스 변수              |

```python
# Refused Bequest -> 인터페이스 분리
# bad
class Animal:
    def walk(self): ...
    def swim(self): ...
    def fly(self): ...

class Dog(Animal):
    def fly(self): raise NotImplementedError

# good
class Walkable(Protocol):
    def walk(self) -> None: ...
class Swimmable(Protocol):
    def swim(self) -> None: ...

class Dog:
    def walk(self) -> None: ...
    def swim(self) -> None: ...
```

#### 변경 방해 스멜 (Change Preventers)

| 스멜                        | 설명                                          |
|-----------------------------|-----------------------------------------------|
| Divergent Change            | 하나의 클래스가 여러 이유로 변경된다 (SRP 위반)    |
| Shotgun Surgery             | 하나의 변경이 여러 클래스에 산발적으로 영향         |
| Parallel Inheritance        | 한 계층에 추가하면 다른 계층에도 추가해야 한다      |

```python
# Shotgun Surgery -> Move Method로 한 곳에 집중
# bad
class Order:
    def total_with_tax(self):
        return self.subtotal * 1.1
class Invoice:
    def tax_amount(self):
        return self.amount * 0.1

# good
class TaxCalculator:
    RATE = 0.1
    @classmethod
    def calculate(cls, amount: float) -> float:
        return amount * cls.RATE
```

#### 불필요한 것들 (Dispensables)

| 스멜                      | 설명                                          |
|---------------------------|-----------------------------------------------|
| Speculative Generality    | "나중에 필요할지도 모른다"는 미사용 추상화         |
| Dead Code                 | 실행되지 않는 코드                              |
| Lazy Class                | 하는 일이 너무 적어 존재 이유가 없는 클래스        |
| Duplicated Code           | 같은 코드 구조의 반복                           |

#### 커플러 스멜 (Couplers)

| 스멜                      | 설명                                          |
|---------------------------|-----------------------------------------------|
| Feature Envy              | 메서드가 자기 클래스보다 다른 클래스의 데이터를 더 많이 사용 |
| Middle Man                | 메서드 대부분이 다른 객체에 위임만 한다             |
| Inappropriate Intimacy    | 두 클래스가 서로의 내부를 지나치게 탐색             |
| Message Chains            | `a.b().c().d()` 식의 긴 호출 체인               |

```python
# Feature Envy -> Move Method
# bad
class OrderPrinter:
    def print_details(self, order):
        print(f"Customer: {order.customer.name}")
        print(f"Total: {order.total()}")
        print(f"Tax: {order.total() * order.tax_rate}")

# good
class Order:
    def format_details(self) -> str:
        return (f"Customer: {self.customer.name}\n"
                f"Total: {self.total()}\n"
                f"Tax: {self.calculate_tax()}")
```

### 2.2 주요 리팩토링 기법 [Ref]

#### Extract Method

```python
# before
def print_owing(self):
    print("*" * 40)
    print("****** Customer Owes ******")
    print("*" * 40)
    outstanding = sum(o.amount for o in self.orders)
    print(f"name: {self.name}")
    print(f"amount: {outstanding}")

# after
def print_owing(self):
    self._print_banner()
    outstanding = self._calculate_outstanding()
    self._print_details(outstanding)
```

#### Replace Temp with Query

```python
# before
def get_price(self):
    base_price = self.quantity * self.item_price
    discount_factor = 0.95 if base_price > 1000 else 0.98
    return base_price * discount_factor

# after
def get_price(self):
    return self._base_price * self._discount_factor

@property
def _base_price(self):
    return self.quantity * self.item_price

@property
def _discount_factor(self):
    return 0.95 if self._base_price > 1000 else 0.98
```

#### Decompose Conditional

```python
# before
def calculate_charge(self, date, quantity):
    if date.month >= 6 and date.month <= 9:
        charge = quantity * self.summer_rate
    else:
        charge = quantity * self.winter_rate + self.winter_service_charge
    return charge

# after
def calculate_charge(self, date, quantity):
    if self._is_summer(date):
        return self._summer_charge(quantity)
    return self._winter_charge(quantity)
```

#### Replace Nested Conditional with Guard Clauses

```python
# before
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

# after
def get_pay_amount(self):
    if self.is_dead: return self.dead_amount()
    if self.is_separated: return self.separated_amount()
    if self.is_retired: return self.retired_amount()
    return self.normal_amount()
```

#### 테이블 주도 방법 (Table-Driven Methods) [CodeC]

논리문(if/case) 대신 테이블(딕셔너리)에서 정보를 조회하는 기법.
거의 모든 복잡한 조건 분기를 테이블 조회로 대체할 수 있다.

```python
# bad — 중첩된 조건문
def get_insurance_rate(age, gender, smoker):
    if age < 18:
        if gender == "male":
            if smoker: return 0.05
            else: return 0.03
        ...

# good — 테이블 기반
INSURANCE_RATES = {
    ("youth", "male", True): 0.05,
    ("youth", "male", False): 0.03,
    ("youth", "female", True): 0.04,
    ("youth", "female", False): 0.02,
}

def _age_group(age: int) -> str:
    if age < 18: return "youth"
    if age < 35: return "adult"
    return "senior"

def get_insurance_rate(age, gender, smoker):
    key = (_age_group(age), gender, smoker)
    rate = INSURANCE_RATES.get(key)
    if rate is None:
        raise ValueError(f"No rate for {key}")
    return rate
```
