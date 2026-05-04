# 객체 설계 원칙 레퍼런스

책임 주도 설계, 다형성, 위임 등 객체 설계와 관련된 규칙과 예시를 다룬다.

---

### 2.1 행동이 상태를 결정한다 [OO]

상태가 아니라 책임으로 객체를 설계하라. 행동을 먼저 정의한다.

```python
# bad — 데이터 주도 설계
class Employee:
    def __init__(self):
        self.name = ""
        self.salary = 0
        self.department = ""

# good — 책임 주도 설계
class Employee:
    def calculate_pay(self) -> Money: ...
    def report_hours(self) -> Hours: ...
```

### 2.2 묻지 말고 시켜라 (Tell, Don't Ask) [OO]

어떻게 해야 하는지 묻지 말고 무엇을 해야 하는지 요청하라.

```python
# bad — 물어보고 직접 처리
if order.get_status() == "paid":
    order.set_status("shipped")
    warehouse.remove_stock(order.get_items())

# good — 시키기
order.ship(warehouse)
```

### 2.3 조건문을 다형성으로 대체하라 [CC] [IP]

중복되는 조건부 로직이 타입에 따라 분기하는 경우,
명시적 조건문 대신 다형성을 사용한다.

```python
# bad
def calculate_pay(employee):
    if employee.type == "COMMISSIONED":
        return calculate_commissioned_pay(employee)
    elif employee.type == "HOURLY":
        return calculate_hourly_pay(employee)

# good
class Employee:
    def calculate_pay(self) -> Money:
        raise NotImplementedError

class CommissionedEmployee(Employee):
    def calculate_pay(self) -> Money: ...

class HourlyEmployee(Employee):
    def calculate_pay(self) -> Money: ...
```

### 2.4 위임으로 유연성 확보 [IP]

하위클래스는 정적(생성 시점 결정)이지만 위임은 런타임에 변경 가능하다.

```python
# bad — 조건문으로 도구 분기
def mouse_down(self):
    if self.get_tool() == "SELECTING": ...
    elif self.get_tool() == "CREATING_RECTANGLE": ...

# good — 위임
def mouse_down(self):
    self.get_tool().mouse_down()
```

### 2.5 로직과 데이터를 함께 유지하라 [IP]

데이터와 그 데이터를 처리하는 로직을 같은 객체 내에 배치하라.

```python
# bad — 로직과 데이터가 분리됨
def format_address(street, city, state, zipcode):
    return f"{street}, {city}, {state} {zipcode}"

# good
class Address:
    def __init__(self, street, city, state, zipcode):
        self.street = street
        self.city = city
        self.state = state
        self.zipcode = zipcode

    def format(self):
        return f"{self.street}, {self.city}, {self.state} {self.zipcode}"
```

### 2.6 변화율에 따라 분리하라 [IP]

함께 변하는 것은 함께 두고, 변화율이 다른 것은 분리한다.

```python
# bad — value와 currency가 항상 함께 변하는데 Payment에 흩어져 있다
class Payment:
    def __init__(self, value, currency):
        self.value = value
        self.currency = currency

# good — 함께 변하는 필드를 Money로 분리
class Money:
    def __init__(self, value, currency):
        self.value = value
        self.currency = currency

class Payment:
    def __init__(self, amount: Money):
        self.amount = amount
```
