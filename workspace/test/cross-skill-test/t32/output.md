# T32 (Test 31): TDD Refactor에서 God Class 분리와 Strategy 패턴 적용

**Skill:** implementation-tdd (Refactoring mode)
**Cross-skill references loaded:** implementation-cleancode (SOLID, God Class), design-patterns-tdd

## [주요 내용]

### God Class 징후

Refactor 단계에서 God Class를 발견하면, 테스트가 모두 그린인 상태에서 분리한다. God Class는 단일 책임 원칙(SRP) 위반이며 테스트를 어렵게 만든다.

### Strategy 패턴으로 분리 (TDD Refactor 단계)

[Before]
```python
class OrderProcessor:
    """God Class: 할인, 배송비, 세금, 결제를 모두 처리"""
    def process(self, order):
        if order.country == "KR":
            discount = order.total * 0.1
        elif order.country == "US":
            discount = order.total * 0.05
        # ... 50줄의 배송비 계산
        # ... 30줄의 세금 계산
        # ... 40줄의 결제 처리
```

[After]
```python
from typing import Protocol
from dataclasses import dataclass

class DiscountStrategy(Protocol):
    def calculate(self, order: Order) -> Money: ...

@dataclass(frozen=True)
class KoreanDiscount:
    rate: float = 0.1
    def calculate(self, order: Order) -> Money:
        return Money(int(order.total.amount * self.rate))

@dataclass(frozen=True)
class USDiscount:
    rate: float = 0.05
    def calculate(self, order: Order) -> Money:
        return Money(int(order.total.amount * self.rate))

class OrderProcessor:
    def __init__(self, discount: DiscountStrategy):
        self._discount = discount

    def calculate_discount(self, order: Order) -> Money:
        return self._discount.calculate(order)
```

[Reason] TDD Refactor + SRP -- 그린 바 상태에서 God Class를 Strategy 패턴으로 분리하면 각 전략을 독립적으로 테스트할 수 있다. Protocol(implementation-cleancode 위임)로 인터페이스를 정의하고, frozen dataclass로 값 객체 불변성을 보장한다.

### 분리 후 테스트

```python
def test_korean_discount():
    strategy = KoreanDiscount()
    order = OrderFactory(total=Money(10000))
    assert strategy.calculate(order) == Money(1000)

def test_us_discount():
    strategy = USDiscount()
    order = OrderFactory(total=Money(10000))
    assert strategy.calculate(order) == Money(500)
```

---
> **관련 스킬 참조:**
> - [SOLID, SRP, God Class 안티패턴] → **implementation-cleancode** 스킬
> - [Value Object, Factory Method 패턴] → 이 스킬 `references/design-patterns-tdd.md`
> - [Protocol, dataclass] → **implementation-python** 스킬
