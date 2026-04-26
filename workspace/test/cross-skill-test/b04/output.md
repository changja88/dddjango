# B04: TDD로 calculate_shipping_cost 함수 개발 + pytest fixture 작성

**Skill:** implementation-tdd (Writing mode)
**Cross-skill references loaded:** implementation-test (pytest fixture, factory_boy)

**Target function:**
```python
def calculate_shipping_cost(order: Order, destination: Address) -> Money:
    pass
```

## [주요 내용]

### 1. 테스트 목록 (Red Bar 패턴)

1. 빈 주문 -> 배송비 0
2. 국내 배송 기본 요금 3000원
3. 주문 금액 50,000원 이상 -> 무료 배송
4. 해외 배송 -> 15,000원
5. 제주도 배송 -> 추가 3,000원

### 2. pytest fixture 정의 (implementation-test 위임)

```python
# conftest.py
import pytest
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    amount: int
    currency: str = "KRW"

@dataclass(frozen=True)
class Address:
    city: str
    country: str = "KR"
    is_island: bool = False

@dataclass
class Order:
    total: Money
    items: list = None

@pytest.fixture
def domestic_address():
    return Address(city="서울", country="KR")

@pytest.fixture
def jeju_address():
    return Address(city="제주", country="KR", is_island=True)

@pytest.fixture
def international_address():
    return Address(city="Tokyo", country="JP")

@pytest.fixture
def cheap_order():
    return Order(total=Money(10000))

@pytest.fixture
def expensive_order():
    return Order(total=Money(50000))
```

### 3. Red: 실패하는 테스트들

```python
def test_domestic_shipping_base_cost(cheap_order, domestic_address):
    result = calculate_shipping_cost(cheap_order, domestic_address)
    assert result == Money(3000)

def test_free_shipping_over_threshold(expensive_order, domestic_address):
    result = calculate_shipping_cost(expensive_order, domestic_address)
    assert result == Money(0)

def test_international_shipping(cheap_order, international_address):
    result = calculate_shipping_cost(cheap_order, international_address)
    assert result == Money(15000)

def test_jeju_surcharge(cheap_order, jeju_address):
    result = calculate_shipping_cost(cheap_order, jeju_address)
    assert result == Money(6000)  # 기본 3000 + 제주 추가 3000
```

### 4. Green: 최소한의 구현

```python
FREE_SHIPPING_THRESHOLD = 50000
DOMESTIC_BASE = 3000
ISLAND_SURCHARGE = 3000
INTERNATIONAL_BASE = 15000

def calculate_shipping_cost(order: Order, destination: Address) -> Money:
    if order.total.amount >= FREE_SHIPPING_THRESHOLD and destination.country == "KR":
        return Money(0)

    if destination.country != "KR":
        return Money(INTERNATIONAL_BASE)

    base = DOMESTIC_BASE
    if destination.is_island:
        base += ISLAND_SURCHARGE
    return Money(base)
```

### 5. Refactor: 경계값 테스트 추가

```python
@pytest.mark.parametrize("amount,expected", [
    (49999, 3000),   # 경계 바로 아래
    (50000, 0),      # 정확히 경계
    (50001, 0),      # 경계 바로 위
])
def test_free_shipping_boundary(amount, expected, domestic_address):
    order = Order(total=Money(amount))
    result = calculate_shipping_cost(order, domestic_address)
    assert result == Money(expected)
```

---
> **관련 스킬 참조:**
> - [pytest fixture, parametrize, factory_boy] → **implementation-test** 스킬
> - [Value Object (Money, Address)] → 이 스킬 `references/design-patterns-tdd.md`
> - [도메인 서비스 설계] → **architecture-ddd** 스킬
