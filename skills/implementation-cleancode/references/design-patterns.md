# 디자인 패턴 레퍼런스

10장(디자인 패턴)에 대한 상세 규칙과 예시.
코드에서 디자인 패턴을 적용, 인식, 평가할 때 참조한다.
원칙 자체는 언어 비종속적이며, 코드 예시는 Python으로 작성되었다.

---

## 목차

1. [팩토리 메서드 (Factory Method)](#1-팩토리-메서드-factory-method-gof)
2. [추상 팩토리 (Abstract Factory)](#2-추상-팩토리-abstract-factory-gof)
3. [값 객체 (Value Object)](#3-값-객체-value-object-kent-beck)
4. [널 객체 (Null Object)](#4-널-객체-null-object-kent-beck)
5. [전략 패턴 (Strategy)](#5-전략-패턴-strategy-gof)
6. [옵저버 패턴 (Observer)](#6-옵저버-패턴-observer-gof)
7. [템플릿 메서드 (Template Method)](#7-템플릿-메서드-template-method-gof-kent-beck)
8. [플러거블 객체 (Pluggable Object)](#8-플러거블-객체-pluggable-object-kent-beck)

---

## 1. 팩토리 메서드 (Factory Method) [GoF]

객체 생성을 서브클래스에 위임하여, 생성할 구체 클래스를 결정하는 코드와
사용하는 코드를 분리한다. OCP를 준수하여 새로운 타입 추가 시 기존 코드를
수정하지 않는다.

```python
# bad — 생성 로직이 조건문에 직접 묶임
class NotificationService:
    def send(self, type_: str, message: str) -> None:
        if type_ == "email":
            print(f"Email: {message}")
        elif type_ == "sms":
            print(f"SMS: {message}")

# good — 팩토리 메서드로 생성 위임
from abc import ABC, abstractmethod

class Notification(ABC):
    @abstractmethod
    def send(self, message: str) -> None: ...

class EmailNotification(Notification):
    def send(self, message: str) -> None:
        print(f"Email: {message}")

class SMSNotification(Notification):
    def send(self, message: str) -> None:
        print(f"SMS: {message}")

class NotificationFactory(ABC):
    @abstractmethod
    def create(self) -> Notification: ...

class EmailFactory(NotificationFactory):
    def create(self) -> Notification:
        return EmailNotification()

class SMSFactory(NotificationFactory):
    def create(self) -> Notification:
        return SMSNotification()

def notify(factory: NotificationFactory, message: str) -> None:
    notification = factory.create()
    notification.send(message)
```

---

## 2. 추상 팩토리 (Abstract Factory) [GoF]

연관된 객체군을 구상 클래스 이름 없이 생성한다.
상속보다 구성(composition)을 선호하며, 팩토리를 교체하면 제품군 전체가 일관되게 바뀐다.

```python
# bad — 구상 클래스에 직접 의존
class Application:
    def __init__(self):
        self.button = WindowsButton()
        self.checkbox = WindowsCheckbox()

# good — 추상 팩토리로 제품군 생성
class GUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button: ...
    @abstractmethod
    def create_checkbox(self) -> Checkbox: ...

class WindowsFactory(GUIFactory):
    def create_button(self) -> Button:
        return WindowsButton()
    def create_checkbox(self) -> Checkbox:
        return WindowsCheckbox()

class MacFactory(GUIFactory):
    def create_button(self) -> Button:
        return MacButton()
    def create_checkbox(self) -> Checkbox:
        return MacCheckbox()

class Application:
    def __init__(self, factory: GUIFactory):
        self.button = factory.create_button()
        self.checkbox = factory.create_checkbox()
```

---

## 3. 값 객체 (Value Object) [Kent Beck]

불변이며 동등성(equality)으로 비교하는 객체다.
별칭(aliasing) 문제를 원천 차단하고, 도메인 개념을 명확하게 표현한다.

```python
# bad — 원시 타입으로 도메인 개념 표현 (원시 타입 집착)
price = 1000
currency = "KRW"  # price와 currency의 관계가 암묵적

# good — 값 객체로 도메인 개념 캡슐화
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    amount: int
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("금액은 음수일 수 없다")

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("통화가 다르면 합산할 수 없다")
        return Money(self.amount + other.amount, self.currency)

price = Money(1000, "KRW")
total = price.add(Money(500, "KRW"))  # Money(1500, "KRW")
```

---

## 4. 널 객체 (Null Object) [Kent Beck]

None 검사를 반복하는 대신, 아무 일도 하지 않는 객체를 사용한다.
다형성을 활용하여 조건문을 제거하고 코드 흐름을 단순화한다.

```python
# bad — None 검사가 곳곳에 산재
class UserService:
    def process(self):
        logger = self.get_logger()
        if logger is not None:
            logger.info("처리 시작")
        self._do_work()
        if logger is not None:
            logger.info("처리 완료")

# good — 널 객체로 None 검사 제거
class NullLogger:
    def info(self, msg: str) -> None:
        pass
    def error(self, msg: str) -> None:
        pass

class UserService:
    def __init__(self, logger=None):
        self._logger = logger or NullLogger()

    def process(self):
        self._logger.info("처리 시작")
        self._do_work()
        self._logger.info("처리 완료")
```

---

## 5. 전략 패턴 (Strategy) [GoF]

알고리즘을 인터페이스 뒤에 캡슐화하여 런타임에 교체할 수 있게 한다.
조건문 체인을 다형성으로 대체하며, 새로운 전략 추가 시 기존 코드를 수정하지 않는다.

```python
# bad — 조건문으로 알고리즘 분기
def calculate_discount(price: int, method: str) -> int:
    if method == "fixed":
        return price - 1000
    elif method == "percent":
        return int(price * 0.9)
    elif method == "vip":
        return int(price * 0.8)

# good — 전략 패턴으로 알고리즘 캡슐화
from typing import Protocol

class DiscountStrategy(Protocol):
    def apply(self, price: int) -> int: ...

class FixedDiscount:
    def __init__(self, amount: int = 1000):
        self._amount = amount
    def apply(self, price: int) -> int:
        return price - self._amount

class PercentDiscount:
    def __init__(self, rate: float = 0.1):
        self._rate = rate
    def apply(self, price: int) -> int:
        return int(price * (1 - self._rate))

def calculate_discount(price: int, strategy: DiscountStrategy) -> int:
    return strategy.apply(price)
```

---

## 6. 옵저버 패턴 (Observer) [GoF]

객체의 상태 변경을 관찰자들에게 자동으로 통보한다.
발행자와 구독자를 느슨하게 결합하여, 서로의 구체적인 구현을 알 필요 없이 협력한다.

```python
# bad — 직접 호출로 강한 결합
class Order:
    def complete(self):
        self._status = "completed"
        EmailService().send_confirmation(self)
        InventoryService().update_stock(self)

# good — 옵저버 패턴으로 느슨한 결합
from typing import Protocol

class OrderObserver(Protocol):
    def on_order_completed(self, order: "Order") -> None: ...

class Order:
    def __init__(self):
        self._observers: list[OrderObserver] = []

    def add_observer(self, observer: OrderObserver) -> None:
        self._observers.append(observer)

    def complete(self):
        self._status = "completed"
        for observer in self._observers:
            observer.on_order_completed(self)

class EmailNotifier:
    def on_order_completed(self, order):
        print(f"확인 메일 발송: {order}")

class StockUpdater:
    def on_order_completed(self, order):
        print(f"재고 갱신: {order}")
```

---

## 7. 템플릿 메서드 (Template Method) [GoF] [Kent Beck]

알고리즘의 전체 순서(골격)를 상위 클래스에서 고정하고,
각 단계의 구체적 구현은 하위 클래스에서 정의한다.
공통 흐름의 중복을 제거하면서 세부 동작을 유연하게 변경할 수 있다.

```python
# bad — 흐름이 각 클래스에 중복
class CSVExporter:
    def export(self, data):
        header = ",".join(data[0].keys())
        rows = [",".join(map(str, d.values())) for d in data]
        return header + "\n" + "\n".join(rows)

class JSONExporter:
    def export(self, data):
        import json
        return json.dumps(data, ensure_ascii=False)

# good — 템플릿 메서드로 흐름 고정
from abc import ABC, abstractmethod

class DataExporter(ABC):
    def export(self, data: list) -> str:
        header = self.build_header(data)
        body = self.build_body(data)
        return self.assemble(header, body)

    @abstractmethod
    def build_header(self, data: list) -> str: ...
    @abstractmethod
    def build_body(self, data: list) -> str: ...

    def assemble(self, header: str, body: str) -> str:
        return f"{header}\n{body}" if header else body

class CSVExporter(DataExporter):
    def build_header(self, data):
        return ",".join(data[0].keys())
    def build_body(self, data):
        return "\n".join(",".join(map(str, d.values())) for d in data)

class JSONExporter(DataExporter):
    def build_header(self, data):
        return ""
    def build_body(self, data):
        import json
        return json.dumps(data, ensure_ascii=False)
```

---

## 8. 플러거블 객체 (Pluggable Object) [Kent Beck]

동일한 조건문이 두 번 이상 반복되면, 조건 분기를 객체로 대체한다.
조건을 생성 시점에 한 번만 결정하고 이후에는 다형성으로 해결한다.

```python
# bad — 같은 조건문이 여러 메서드에 반복
class GraphEditor:
    def __init__(self, mode: str):
        self.mode = mode

    def on_mouse_down(self, x, y):
        if self.mode == "select":
            self._start_selection(x, y)
        elif self.mode == "draw":
            self._start_drawing(x, y)

    def on_mouse_up(self, x, y):
        if self.mode == "select":
            self._finish_selection(x, y)
        elif self.mode == "draw":
            self._finish_drawing(x, y)

# good — 플러거블 객체로 조건문 제거
from typing import Protocol

class Tool(Protocol):
    def on_mouse_down(self, x: int, y: int) -> None: ...
    def on_mouse_up(self, x: int, y: int) -> None: ...

class SelectionTool:
    def on_mouse_down(self, x, y):
        print(f"선택 시작: ({x}, {y})")
    def on_mouse_up(self, x, y):
        print(f"선택 완료: ({x}, {y})")

class DrawingTool:
    def on_mouse_down(self, x, y):
        print(f"그리기 시작: ({x}, {y})")
    def on_mouse_up(self, x, y):
        print(f"그리기 완료: ({x}, {y})")

class GraphEditor:
    def __init__(self, tool: Tool):
        self._tool = tool

    def on_mouse_down(self, x, y):
        self._tool.on_mouse_down(x, y)

    def on_mouse_up(self, x, y):
        self._tool.on_mouse_up(x, y)
```
