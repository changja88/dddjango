# T34 (Test 33): pytest에서 Red-Green-Refactor TDD 방법론을 적용하려면?

**Skill:** implementation-test (Writing mode)
**Cross-skill references loaded:** implementation-tdd (Red-Green-Refactor 사이클)

## [주요 내용]

TDD 방법론(implementation-tdd 위임)의 Red-Green-Refactor 사이클을 pytest 테스트 코드 기법으로 구현한다.

### Red: 실패하는 테스트 작성 (pytest)

```python
import pytest

def test_calculate_total_empty_cart():
    """빈 카트의 합계는 0이어야 한다 -- null 연산부터 시작"""
    cart = ShoppingCart()
    assert cart.total() == 0

def test_calculate_total_single_item():
    cart = ShoppingCart()
    cart.add(Product("Widget", price=1000), quantity=2)
    assert cart.total() == 2000
```

### Green: 최소한의 구현

```python
class ShoppingCart:
    def __init__(self):
        self._items: list[tuple[Product, int]] = []

    def add(self, product: Product, quantity: int) -> None:
        self._items.append((product, quantity))

    def total(self) -> int:
        return sum(p.price * q for p, q in self._items)
```

### Refactor: pytest fixture로 설정 정리

```python
@pytest.fixture
def cart():
    return ShoppingCart()

@pytest.fixture
def widget():
    return Product("Widget", price=1000)

def test_empty_cart_total(cart):
    assert cart.total() == 0

def test_single_item_total(cart, widget):
    cart.add(widget, quantity=2)
    assert cart.total() == 2000

@pytest.mark.parametrize("qty,expected", [
    (1, 1000),
    (5, 5000),
    (0, 0),
])
def test_various_quantities(cart, widget, qty, expected):
    cart.add(widget, quantity=qty)
    assert cart.total() == expected
```

핵심 원칙: AAA 구조(Arrange-Act-Assert)를 따르고, 각 테스트는 하나의 동작을 검증한다. 출력 기반 검증(반환 값 assert)을 선호한다.

---
> **관련 스킬 참조:**
> - [Red-Green-Refactor, TDD 스쿨, 테스트 선택] → **implementation-tdd** 스킬
> - [factory_boy, Hypothesis] → 이 스킬 `references/test-data-factory.md`
> - [클린 코드 원칙, 네이밍] → **implementation-cleancode** 스킬
