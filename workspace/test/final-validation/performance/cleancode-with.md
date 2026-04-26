# Refactoring: `process_order`

이 코드에는 여러 클린 코드 위반이 중첩되어 있다. 단일 함수가 가격 계산, 배송비 결정, DB 저장, 메일 발송, 로깅을 모두 수행하며, 타입 기반 조건문(`order_data['type']`)이 확장을 막고, 원시 dict를 직접 변경(mutate)하는 구조다. 근본적인 재설계를 적용한 후 개별 변경 사항을 제시한다.

---

## 변경 1 -- 하나의 함수가 너무 많은 일을 한다

**[Before]**
```python
def process_order(order_data, db, mailer, logger):
    if order_data['type'] == 'standard':
        total = 0
        for item in order_data['items']:
            if item['quantity'] > 0:
                price = item['price'] * item['quantity']
                if item.get('discount'):
                    price = price * (1 - item['discount'] / 100)
                total += price
        if total > 100000:
            order_data['shipping'] = 0
        else:
            order_data['shipping'] = 3000
        order_data['total'] = total + order_data['shipping']
        db.save(order_data)
        mailer.send(order_data['email'], f'주문 완료: {order_data["total"]}원')
        logger.info(f'Order processed: {order_data["total"]}')
        return order_data
    elif order_data['type'] == 'subscription':
        # similar but different logic...
        pass
```

**[After]**
```python
def process_order(order: Order, processor: OrderProcessor) -> Order:
    completed_order = processor.process(order)
    return completed_order
```

**[Reason]** 함수는 하나의 추상화 수준에서 하나의 일만 한다 [CC 1.2] -- 원래 함수는 가격 계산, 배송비 결정, 영속화, 알림, 로깅이라는 다섯 가지 서로 다른 책임을 하나의 함수에서 수행했다. 각 책임을 별도의 함수/클래스로 분리하여 변경 이유를 하나로 한정한다.

---

## 변경 2 -- 원시 dict를 가변 데이터로 사용

**[Before]**
```python
order_data['shipping'] = 0
order_data['total'] = total + order_data['shipping']
```

**[After]**
```python
@dataclass(frozen=True)
class OrderItem:
    price: int
    quantity: int
    discount_percent: float = 0.0

@dataclass(frozen=True)
class Order:
    order_type: str
    items: tuple[OrderItem, ...]
    email: str
```

**[Reason]** 값 객체를 활용하라 [IP] / Primitive Obsession 제거 [Ref] -- 원시 dict는 어떤 키가 존재하는지, 값의 타입이 무엇인지 코드를 읽어봐야만 알 수 있다. `frozen=True` dataclass로 변환하면 구조가 명시적이고 불변성이 보장되며, 타입 힌트로 IDE 지원을 받을 수 있다.

---

## 변경 3 -- 타입 기반 반복 조건문을 Strategy 패턴으로 대체

**[Before]**
```python
if order_data['type'] == 'standard':
    # standard 처리 로직...
elif order_data['type'] == 'subscription':
    # subscription 처리 로직...
```

**[After]**
```python
class OrderStrategy(Protocol):
    def calculate_total(self, items: tuple[OrderItem, ...]) -> int: ...
    def calculate_shipping(self, subtotal: int) -> int: ...

class StandardOrderStrategy:
    def calculate_total(self, items: tuple[OrderItem, ...]) -> int:
        return sum(
            _calculate_item_price(item)
            for item in items
            if item.quantity > 0
        )

    def calculate_shipping(self, subtotal: int) -> int:
        return 0 if subtotal > FREE_SHIPPING_THRESHOLD else STANDARD_SHIPPING_FEE
```

**[Reason]** 타입 기반 반복 조건문을 Strategy로 대체 [GoF Strategy] / 개방-폐쇄 원칙 [OCP] -- `if/elif` 체인은 새로운 주문 타입을 추가할 때마다 기존 함수를 수정해야 한다. Strategy 패턴으로 각 주문 타입의 계산 로직을 캡슐화하면, 새로운 타입 추가 시 새 클래스만 작성하면 된다.

---

## 변경 4 -- 매직 넘버를 이름 있는 상수로 추출

**[Before]**
```python
if total > 100000:
    order_data['shipping'] = 0
else:
    order_data['shipping'] = 3000
```

**[After]**
```python
FREE_SHIPPING_THRESHOLD: Final[int] = 100_000
STANDARD_SHIPPING_FEE: Final[int] = 3_000
```

**[Reason]** 매직 넘버를 이름 있는 상수로 [CC] [CodeC] -- `100000`과 `3000`은 비즈니스 규칙을 인코딩하지만 이름이 없어 의미를 즉시 파악할 수 없다. 이름 있는 상수로 추출하면 의도가 명확해지고, 값 변경 시 단일 지점만 수정하면 된다.

---

## 변경 5 -- 숨겨진 부수 효과를 별도의 커맨드로 추출

**[Before]**
```python
db.save(order_data)
mailer.send(order_data['email'], f'주문 완료: {order_data["total"]}원')
logger.info(f'Order processed: {order_data["total"]}')
```

**[After]**
```python
class OrderProcessor:
    def __init__(
        self,
        strategy: OrderStrategy,
        repository: OrderRepository,
        notifier: OrderNotifier,
        logger: OrderLogger,
    ) -> None:
        self._strategy = strategy
        self._repository = repository
        self._notifier = notifier
        self._logger = logger

    def process(self, order: Order) -> CompletedOrder:
        completed = self._calculate(order)
        self._save(completed)
        self._notify(completed)
        return completed
```

**[Reason]** 명령과 조회 분리 [CC 1.6] / 부수 효과를 일으키지 마라 [CC 1.7] / SRP [SOLID] -- 계산(순수 함수)과 부수 효과(저장, 알림)를 분리하여 각각 독립적으로 테스트할 수 있게 한다. 의존성을 Protocol로 주입받아 테스트 시 목(mock) 객체로 교체 가능하다.

---

## 변경 6 -- 테스트 불가능한 의존성을 Protocol로 주입

**[Before]**
```python
def process_order(order_data, db, mailer, logger):
```

**[After]**
```python
class OrderRepository(Protocol):
    def save(self, order: "CompletedOrder") -> None: ...

class OrderNotifier(Protocol):
    def notify_completion(self, order: "CompletedOrder") -> None: ...

class OrderLogger(Protocol):
    def log_processed(self, order: "CompletedOrder") -> None: ...
```

**[Reason]** 의존성 역전 원칙 [DIP] / 테스트 불가능한 의존성을 Protocol로 주입 -- 원래 코드는 `db`, `mailer`, `logger`의 구체적인 인터페이스에 암묵적으로 의존했다. Protocol을 명시하면 계약이 코드에 드러나고, 테스트 시 가짜 구현을 쉽게 주입할 수 있다.

---

## 변경 7 -- 중첩된 조건문을 가드 절로 평탄화

**[Before]**
```python
for item in order_data['items']:
    if item['quantity'] > 0:
        price = item['price'] * item['quantity']
        if item.get('discount'):
            price = price * (1 - item['discount'] / 100)
        total += price
```

**[After]**
```python
def _calculate_item_price(item: OrderItem) -> int:
    if item.quantity <= 0:
        return 0
    subtotal = item.price * item.quantity
    if item.discount_percent == 0.0:
        return subtotal
    return int(subtotal * (1 - item.discount_percent / 100))
```

**[Reason]** 가드 절로 중첩 조건문 평탄화 [Ref] / Extract Method [Ref] -- 중첩된 `if`를 가드 절로 반전시키면 "정상 흐름"이 주 경로가 되어 읽기 쉬워진다. 단일 아이템의 가격 계산을 별도 함수로 추출하여 단위 테스트가 가능해진다.

---

## 전체 리팩토링 결과

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Protocol


# -- 상수 --

FREE_SHIPPING_THRESHOLD: Final[int] = 100_000
STANDARD_SHIPPING_FEE: Final[int] = 3_000


# -- 값 객체 --

@dataclass(frozen=True)
class OrderItem:
    price: int
    quantity: int
    discount_percent: float = 0.0


@dataclass(frozen=True)
class Order:
    order_type: str
    items: tuple[OrderItem, ...]
    email: str


@dataclass(frozen=True)
class CompletedOrder:
    order: Order
    subtotal: int
    shipping: int

    @property
    def total(self) -> int:
        return self.subtotal + self.shipping


# -- 의존성 Protocol --

class OrderRepository(Protocol):
    def save(self, order: CompletedOrder) -> None: ...


class OrderNotifier(Protocol):
    def notify_completion(self, order: CompletedOrder) -> None: ...


class OrderLogger(Protocol):
    def log_processed(self, order: CompletedOrder) -> None: ...


# -- 전략 --

class OrderStrategy(Protocol):
    def calculate_total(self, items: tuple[OrderItem, ...]) -> int: ...
    def calculate_shipping(self, subtotal: int) -> int: ...


def _calculate_item_price(item: OrderItem) -> int:
    if item.quantity <= 0:
        return 0
    subtotal = item.price * item.quantity
    if item.discount_percent == 0.0:
        return subtotal
    return int(subtotal * (1 - item.discount_percent / 100))


class StandardOrderStrategy:
    def calculate_total(self, items: tuple[OrderItem, ...]) -> int:
        return sum(_calculate_item_price(item) for item in items)

    def calculate_shipping(self, subtotal: int) -> int:
        if subtotal > FREE_SHIPPING_THRESHOLD:
            return 0
        return STANDARD_SHIPPING_FEE


class SubscriptionOrderStrategy:
    """구독 주문 전략 -- 비즈니스 규칙에 맞게 구현한다."""

    def calculate_total(self, items: tuple[OrderItem, ...]) -> int:
        return sum(_calculate_item_price(item) for item in items)

    def calculate_shipping(self, subtotal: int) -> int:
        return 0  # 구독은 배송비 무료


# -- 전략 팩토리 --

_STRATEGY_MAP: dict[str, type[OrderStrategy]] = {
    "standard": StandardOrderStrategy,
    "subscription": SubscriptionOrderStrategy,
}


def get_order_strategy(order_type: str) -> OrderStrategy:
    strategy_cls = _STRATEGY_MAP.get(order_type)
    if strategy_cls is None:
        raise ValueError(f"지원하지 않는 주문 타입: {order_type}")
    return strategy_cls()


# -- 주문 처리기 --

class OrderProcessor:
    def __init__(
        self,
        strategy: OrderStrategy,
        repository: OrderRepository,
        notifier: OrderNotifier,
        logger: OrderLogger,
    ) -> None:
        self._strategy = strategy
        self._repository = repository
        self._notifier = notifier
        self._logger = logger

    def process(self, order: Order) -> CompletedOrder:
        completed = self._calculate(order)
        self._save(completed)
        self._notify(completed)
        return completed

    def _calculate(self, order: Order) -> CompletedOrder:
        subtotal = self._strategy.calculate_total(order.items)
        shipping = self._strategy.calculate_shipping(subtotal)
        return CompletedOrder(order=order, subtotal=subtotal, shipping=shipping)

    def _save(self, order: CompletedOrder) -> None:
        self._repository.save(order)

    def _notify(self, order: CompletedOrder) -> None:
        self._notifier.notify_completion(order)
        self._logger.log_processed(order)


# -- 사용 예시 --

def process_order(
    order: Order,
    repository: OrderRepository,
    notifier: OrderNotifier,
    logger: OrderLogger,
) -> CompletedOrder:
    strategy = get_order_strategy(order.order_type)
    processor = OrderProcessor(strategy, repository, notifier, logger)
    return processor.process(order)
```

---

> **관련 스킬 참조:**
> - Protocol 기반 의존성 주입의 Python 구현 상세 --> **implementation-python** 스킬
> - 리팩토링 후 테스트 작성 (CompletedOrder 계산 검증, Mock 주입 테스트) --> **testing** 스킬
> - 주문 처리 도메인 모델의 아키텍처 레이어 배치 --> **architecture** 스킬
