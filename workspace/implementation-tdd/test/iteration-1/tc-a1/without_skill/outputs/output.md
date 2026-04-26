# TDD 장바구니 기능 구현 - Red-Green-Refactor

Python `pytest`를 사용하여 TDD의 Red-Green-Refactor 사이클을 단계별로 진행한다.

---

## 사이클 1: 빈 장바구니 생성

### RED - 실패하는 테스트 작성

```python
# test_cart.py

from cart import ShoppingCart


class TestShoppingCart:
    def test_new_cart_is_empty(self):
        cart = ShoppingCart()
        assert cart.items == []
        assert cart.total_price() == 0
```

**실행 결과:**
```
E   ModuleNotFoundError: No module named 'cart'
FAILED
```

테스트가 실패한다. `cart` 모듈이 존재하지 않기 때문이다.

### GREEN - 테스트를 통과하는 최소한의 코드 작성

```python
# cart.py

class ShoppingCart:
    def __init__(self):
        self.items = []

    def total_price(self):
        return 0
```

**실행 결과:**
```
test_cart.py::TestShoppingCart::test_new_cart_is_empty PASSED
```

### REFACTOR

이 단계에서는 리팩터링할 것이 없다. 다음 사이클로 넘어간다.

---

## 사이클 2: 상품 추가

### RED - 실패하는 테스트 작성

```python
# test_cart.py

def test_add_item(self):
    cart = ShoppingCart()
    cart.add_item("Python 책", 25000, 1)
    assert len(cart.items) == 1
    assert cart.items[0]["name"] == "Python 책"
    assert cart.items[0]["price"] == 25000
    assert cart.items[0]["quantity"] == 1

def test_add_multiple_items(self):
    cart = ShoppingCart()
    cart.add_item("Python 책", 25000, 1)
    cart.add_item("키보드", 80000, 1)
    assert len(cart.items) == 2
```

**실행 결과:**
```
E   AttributeError: 'ShoppingCart' object has no attribute 'add_item'
FAILED
```

### GREEN - 테스트를 통과하는 최소한의 코드 작성

```python
# cart.py

class ShoppingCart:
    def __init__(self):
        self.items = []

    def add_item(self, name: str, price: int, quantity: int):
        self.items.append({
            "name": name,
            "price": price,
            "quantity": quantity,
        })

    def total_price(self):
        return 0
```

**실행 결과:**
```
test_cart.py::TestShoppingCart::test_new_cart_is_empty PASSED
test_cart.py::TestShoppingCart::test_add_item PASSED
test_cart.py::TestShoppingCart::test_add_multiple_items PASSED
```

### REFACTOR

동일 상품을 추가할 때 수량만 증가시키도록 개선한다. 먼저 테스트를 추가한다.

```python
def test_add_same_item_increases_quantity(self):
    cart = ShoppingCart()
    cart.add_item("Python 책", 25000, 1)
    cart.add_item("Python 책", 25000, 2)
    assert len(cart.items) == 1
    assert cart.items[0]["quantity"] == 3
```

그리고 `add_item`을 리팩터링한다.

```python
def add_item(self, name: str, price: int, quantity: int):
    for item in self.items:
        if item["name"] == name:
            item["quantity"] += quantity
            return
    self.items.append({
        "name": name,
        "price": price,
        "quantity": quantity,
    })
```

**실행 결과:**
```
test_cart.py::TestShoppingCart::test_new_cart_is_empty PASSED
test_cart.py::TestShoppingCart::test_add_item PASSED
test_cart.py::TestShoppingCart::test_add_multiple_items PASSED
test_cart.py::TestShoppingCart::test_add_same_item_increases_quantity PASSED
```

---

## 사이클 3: 상품 제거

### RED - 실패하는 테스트 작성

```python
def test_remove_item(self):
    cart = ShoppingCart()
    cart.add_item("Python 책", 25000, 1)
    cart.add_item("키보드", 80000, 1)
    cart.remove_item("Python 책")
    assert len(cart.items) == 1
    assert cart.items[0]["name"] == "키보드"

def test_remove_nonexistent_item_raises_error(self):
    cart = ShoppingCart()
    with pytest.raises(ValueError, match="상품을 찾을 수 없습니다"):
        cart.remove_item("없는 상품")
```

**실행 결과:**
```
E   AttributeError: 'ShoppingCart' object has no attribute 'remove_item'
FAILED
```

### GREEN - 테스트를 통과하는 최소한의 코드 작성

```python
def remove_item(self, name: str):
    for i, item in enumerate(self.items):
        if item["name"] == name:
            self.items.pop(i)
            return
    raise ValueError("상품을 찾을 수 없습니다")
```

**실행 결과:**
```
test_cart.py::TestShoppingCart::test_new_cart_is_empty PASSED
test_cart.py::TestShoppingCart::test_add_item PASSED
test_cart.py::TestShoppingCart::test_add_multiple_items PASSED
test_cart.py::TestShoppingCart::test_add_same_item_increases_quantity PASSED
test_cart.py::TestShoppingCart::test_remove_item PASSED
test_cart.py::TestShoppingCart::test_remove_nonexistent_item_raises_error PASSED
```

### REFACTOR

이 단계에서는 리팩터링할 것이 없다. 코드가 깔끔하다.

---

## 사이클 4: 수량 변경

### RED - 실패하는 테스트 작성

```python
def test_update_quantity(self):
    cart = ShoppingCart()
    cart.add_item("Python 책", 25000, 1)
    cart.update_quantity("Python 책", 5)
    assert cart.items[0]["quantity"] == 5

def test_update_quantity_to_zero_removes_item(self):
    cart = ShoppingCart()
    cart.add_item("Python 책", 25000, 1)
    cart.update_quantity("Python 책", 0)
    assert len(cart.items) == 0

def test_update_quantity_negative_raises_error(self):
    cart = ShoppingCart()
    cart.add_item("Python 책", 25000, 1)
    with pytest.raises(ValueError, match="수량은 0 이상이어야 합니다"):
        cart.update_quantity("Python 책", -1)

def test_update_quantity_nonexistent_item_raises_error(self):
    cart = ShoppingCart()
    with pytest.raises(ValueError, match="상품을 찾을 수 없습니다"):
        cart.update_quantity("없는 상품", 3)
```

**실행 결과:**
```
E   AttributeError: 'ShoppingCart' object has no attribute 'update_quantity'
FAILED
```

### GREEN - 테스트를 통과하는 최소한의 코드 작성

```python
def update_quantity(self, name: str, quantity: int):
    if quantity < 0:
        raise ValueError("수량은 0 이상이어야 합니다")
    for i, item in enumerate(self.items):
        if item["name"] == name:
            if quantity == 0:
                self.items.pop(i)
            else:
                item["quantity"] = quantity
            return
    raise ValueError("상품을 찾을 수 없습니다")
```

**실행 결과:**
```
test_cart.py::TestShoppingCart::test_new_cart_is_empty PASSED
test_cart.py::TestShoppingCart::test_add_item PASSED
test_cart.py::TestShoppingCart::test_add_multiple_items PASSED
test_cart.py::TestShoppingCart::test_add_same_item_increases_quantity PASSED
test_cart.py::TestShoppingCart::test_remove_item PASSED
test_cart.py::TestShoppingCart::test_remove_nonexistent_item_raises_error PASSED
test_cart.py::TestShoppingCart::test_update_quantity PASSED
test_cart.py::TestShoppingCart::test_update_quantity_to_zero_removes_item PASSED
test_cart.py::TestShoppingCart::test_update_quantity_negative_raises_error PASSED
test_cart.py::TestShoppingCart::test_update_quantity_nonexistent_item_raises_error PASSED
```

### REFACTOR

상품을 이름으로 찾는 로직이 `add_item`, `remove_item`, `update_quantity`에서 반복된다. 헬퍼 메서드로 추출한다.

```python
def _find_item(self, name: str):
    """이름으로 상품을 찾아 (인덱스, 아이템) 튜플을 반환한다. 없으면 None."""
    for i, item in enumerate(self.items):
        if item["name"] == name:
            return i, item
    return None

def add_item(self, name: str, price: int, quantity: int):
    result = self._find_item(name)
    if result:
        _, item = result
        item["quantity"] += quantity
    else:
        self.items.append({
            "name": name,
            "price": price,
            "quantity": quantity,
        })

def remove_item(self, name: str):
    result = self._find_item(name)
    if result is None:
        raise ValueError("상품을 찾을 수 없습니다")
    index, _ = result
    self.items.pop(index)

def update_quantity(self, name: str, quantity: int):
    if quantity < 0:
        raise ValueError("수량은 0 이상이어야 합니다")
    result = self._find_item(name)
    if result is None:
        raise ValueError("상품을 찾을 수 없습니다")
    index, item = result
    if quantity == 0:
        self.items.pop(index)
    else:
        item["quantity"] = quantity
```

리팩터링 후 모든 테스트를 재실행한다.

**실행 결과:**
```
10 passed
```

모든 테스트가 통과한다. 리팩터링이 기존 동작을 깨뜨리지 않았다.

---

## 사이클 5: 총 금액 계산

### RED - 실패하는 테스트 작성

```python
def test_total_price_single_item(self):
    cart = ShoppingCart()
    cart.add_item("Python 책", 25000, 2)
    assert cart.total_price() == 50000

def test_total_price_multiple_items(self):
    cart = ShoppingCart()
    cart.add_item("Python 책", 25000, 2)
    cart.add_item("키보드", 80000, 1)
    assert cart.total_price() == 130000

def test_total_price_after_remove(self):
    cart = ShoppingCart()
    cart.add_item("Python 책", 25000, 2)
    cart.add_item("키보드", 80000, 1)
    cart.remove_item("키보드")
    assert cart.total_price() == 50000
```

**실행 결과:**
```
E   AssertionError: assert 0 == 50000
FAILED
```

`total_price()`가 항상 0을 반환하므로 실패한다.

### GREEN - 테스트를 통과하는 최소한의 코드 작성

```python
def total_price(self):
    return sum(item["price"] * item["quantity"] for item in self.items)
```

**실행 결과:**
```
test_cart.py::TestShoppingCart::test_new_cart_is_empty PASSED
test_cart.py::TestShoppingCart::test_add_item PASSED
test_cart.py::TestShoppingCart::test_add_multiple_items PASSED
test_cart.py::TestShoppingCart::test_add_same_item_increases_quantity PASSED
test_cart.py::TestShoppingCart::test_remove_item PASSED
test_cart.py::TestShoppingCart::test_remove_nonexistent_item_raises_error PASSED
test_cart.py::TestShoppingCart::test_update_quantity PASSED
test_cart.py::TestShoppingCart::test_update_quantity_to_zero_removes_item PASSED
test_cart.py::TestShoppingCart::test_update_quantity_negative_raises_error PASSED
test_cart.py::TestShoppingCart::test_update_quantity_nonexistent_item_raises_error PASSED
test_cart.py::TestShoppingCart::test_total_price_single_item PASSED
test_cart.py::TestShoppingCart::test_total_price_multiple_items PASSED
test_cart.py::TestShoppingCart::test_total_price_after_remove PASSED
```

### REFACTOR

`total_price` 구현이 이미 깔끔하다. 리팩터링할 것이 없다.

---

## 사이클 6: 배송비 계산 (10만원 이상 무료, 미만 3000원)

### RED - 실패하는 테스트 작성

```python
def test_shipping_fee_under_100000(self):
    cart = ShoppingCart()
    cart.add_item("Python 책", 25000, 1)
    assert cart.shipping_fee() == 3000

def test_shipping_fee_exactly_100000(self):
    cart = ShoppingCart()
    cart.add_item("키보드", 100000, 1)
    assert cart.shipping_fee() == 0

def test_shipping_fee_over_100000(self):
    cart = ShoppingCart()
    cart.add_item("Python 책", 25000, 2)
    cart.add_item("키보드", 80000, 1)
    assert cart.shipping_fee() == 0

def test_shipping_fee_empty_cart(self):
    cart = ShoppingCart()
    assert cart.shipping_fee() == 0
```

**실행 결과:**
```
E   AttributeError: 'ShoppingCart' object has no attribute 'shipping_fee'
FAILED
```

### GREEN - 테스트를 통과하는 최소한의 코드 작성

```python
def shipping_fee(self):
    if not self.items:
        return 0
    if self.total_price() >= 100000:
        return 0
    return 3000
```

**실행 결과:**
```
test_cart.py::TestShoppingCart::test_new_cart_is_empty PASSED
test_cart.py::TestShoppingCart::test_add_item PASSED
test_cart.py::TestShoppingCart::test_add_multiple_items PASSED
test_cart.py::TestShoppingCart::test_add_same_item_increases_quantity PASSED
test_cart.py::TestShoppingCart::test_remove_item PASSED
test_cart.py::TestShoppingCart::test_remove_nonexistent_item_raises_error PASSED
test_cart.py::TestShoppingCart::test_update_quantity PASSED
test_cart.py::TestShoppingCart::test_update_quantity_to_zero_removes_item PASSED
test_cart.py::TestShoppingCart::test_update_quantity_negative_raises_error PASSED
test_cart.py::TestShoppingCart::test_update_quantity_nonexistent_item_raises_error PASSED
test_cart.py::TestShoppingCart::test_total_price_single_item PASSED
test_cart.py::TestShoppingCart::test_total_price_multiple_items PASSED
test_cart.py::TestShoppingCart::test_total_price_after_remove PASSED
test_cart.py::TestShoppingCart::test_shipping_fee_under_100000 PASSED
test_cart.py::TestShoppingCart::test_shipping_fee_exactly_100000 PASSED
test_cart.py::TestShoppingCart::test_shipping_fee_over_100000 PASSED
test_cart.py::TestShoppingCart::test_shipping_fee_empty_cart PASSED
```

### REFACTOR

매직 넘버를 상수로 추출하고, 배송비를 포함한 최종 결제 금액 메서드를 추가한다.

```python
class ShoppingCart:
    FREE_SHIPPING_THRESHOLD = 100000
    SHIPPING_FEE = 3000

    # ... (기존 코드)

    def shipping_fee(self):
        if not self.items:
            return 0
        if self.total_price() >= self.FREE_SHIPPING_THRESHOLD:
            return 0
        return self.SHIPPING_FEE

    def checkout_price(self):
        return self.total_price() + self.shipping_fee()
```

`checkout_price` 테스트도 추가한다.

```python
def test_checkout_price_with_shipping(self):
    cart = ShoppingCart()
    cart.add_item("Python 책", 25000, 1)
    assert cart.checkout_price() == 28000  # 25000 + 3000

def test_checkout_price_free_shipping(self):
    cart = ShoppingCart()
    cart.add_item("키보드", 120000, 1)
    assert cart.checkout_price() == 120000  # 배송비 무료
```

**실행 결과:**
```
19 passed
```

---

## 최종 코드

### cart.py

```python
class ShoppingCart:
    FREE_SHIPPING_THRESHOLD = 100000
    SHIPPING_FEE = 3000

    def __init__(self):
        self.items: list[dict] = []

    def _find_item(self, name: str) -> tuple[int, dict] | None:
        """이름으로 상품을 찾아 (인덱스, 아이템) 튜플을 반환한다. 없으면 None."""
        for i, item in enumerate(self.items):
            if item["name"] == name:
                return i, item
        return None

    def add_item(self, name: str, price: int, quantity: int) -> None:
        """상품을 추가한다. 동일 상품이 이미 있으면 수량만 증가시킨다."""
        result = self._find_item(name)
        if result:
            _, item = result
            item["quantity"] += quantity
        else:
            self.items.append({
                "name": name,
                "price": price,
                "quantity": quantity,
            })

    def remove_item(self, name: str) -> None:
        """상품을 제거한다. 존재하지 않으면 ValueError를 발생시킨다."""
        result = self._find_item(name)
        if result is None:
            raise ValueError("상품을 찾을 수 없습니다")
        index, _ = result
        self.items.pop(index)

    def update_quantity(self, name: str, quantity: int) -> None:
        """상품 수량을 변경한다. 0이면 제거, 음수면 ValueError를 발생시킨다."""
        if quantity < 0:
            raise ValueError("수량은 0 이상이어야 합니다")
        result = self._find_item(name)
        if result is None:
            raise ValueError("상품을 찾을 수 없습니다")
        index, item = result
        if quantity == 0:
            self.items.pop(index)
        else:
            item["quantity"] = quantity

    def total_price(self) -> int:
        """장바구니 상품 총 금액을 반환한다."""
        return sum(item["price"] * item["quantity"] for item in self.items)

    def shipping_fee(self) -> int:
        """배송비를 반환한다. 10만원 이상이면 무료, 미만이면 3000원."""
        if not self.items:
            return 0
        if self.total_price() >= self.FREE_SHIPPING_THRESHOLD:
            return 0
        return self.SHIPPING_FEE

    def checkout_price(self) -> int:
        """배송비를 포함한 최종 결제 금액을 반환한다."""
        return self.total_price() + self.shipping_fee()
```

### test_cart.py

```python
import pytest

from cart import ShoppingCart


class TestShoppingCart:
    # --- 빈 장바구니 ---
    def test_new_cart_is_empty(self):
        cart = ShoppingCart()
        assert cart.items == []
        assert cart.total_price() == 0

    # --- 상품 추가 ---
    def test_add_item(self):
        cart = ShoppingCart()
        cart.add_item("Python 책", 25000, 1)
        assert len(cart.items) == 1
        assert cart.items[0]["name"] == "Python 책"
        assert cart.items[0]["price"] == 25000
        assert cart.items[0]["quantity"] == 1

    def test_add_multiple_items(self):
        cart = ShoppingCart()
        cart.add_item("Python 책", 25000, 1)
        cart.add_item("키보드", 80000, 1)
        assert len(cart.items) == 2

    def test_add_same_item_increases_quantity(self):
        cart = ShoppingCart()
        cart.add_item("Python 책", 25000, 1)
        cart.add_item("Python 책", 25000, 2)
        assert len(cart.items) == 1
        assert cart.items[0]["quantity"] == 3

    # --- 상품 제거 ---
    def test_remove_item(self):
        cart = ShoppingCart()
        cart.add_item("Python 책", 25000, 1)
        cart.add_item("키보드", 80000, 1)
        cart.remove_item("Python 책")
        assert len(cart.items) == 1
        assert cart.items[0]["name"] == "키보드"

    def test_remove_nonexistent_item_raises_error(self):
        cart = ShoppingCart()
        with pytest.raises(ValueError, match="상품을 찾을 수 없습니다"):
            cart.remove_item("없는 상품")

    # --- 수량 변경 ---
    def test_update_quantity(self):
        cart = ShoppingCart()
        cart.add_item("Python 책", 25000, 1)
        cart.update_quantity("Python 책", 5)
        assert cart.items[0]["quantity"] == 5

    def test_update_quantity_to_zero_removes_item(self):
        cart = ShoppingCart()
        cart.add_item("Python 책", 25000, 1)
        cart.update_quantity("Python 책", 0)
        assert len(cart.items) == 0

    def test_update_quantity_negative_raises_error(self):
        cart = ShoppingCart()
        cart.add_item("Python 책", 25000, 1)
        with pytest.raises(ValueError, match="수량은 0 이상이어야 합니다"):
            cart.update_quantity("Python 책", -1)

    def test_update_quantity_nonexistent_item_raises_error(self):
        cart = ShoppingCart()
        with pytest.raises(ValueError, match="상품을 찾을 수 없습니다"):
            cart.update_quantity("없는 상품", 3)

    # --- 총 금액 계산 ---
    def test_total_price_single_item(self):
        cart = ShoppingCart()
        cart.add_item("Python 책", 25000, 2)
        assert cart.total_price() == 50000

    def test_total_price_multiple_items(self):
        cart = ShoppingCart()
        cart.add_item("Python 책", 25000, 2)
        cart.add_item("키보드", 80000, 1)
        assert cart.total_price() == 130000

    def test_total_price_after_remove(self):
        cart = ShoppingCart()
        cart.add_item("Python 책", 25000, 2)
        cart.add_item("키보드", 80000, 1)
        cart.remove_item("키보드")
        assert cart.total_price() == 50000

    # --- 배송비 ---
    def test_shipping_fee_under_100000(self):
        cart = ShoppingCart()
        cart.add_item("Python 책", 25000, 1)
        assert cart.shipping_fee() == 3000

    def test_shipping_fee_exactly_100000(self):
        cart = ShoppingCart()
        cart.add_item("키보드", 100000, 1)
        assert cart.shipping_fee() == 0

    def test_shipping_fee_over_100000(self):
        cart = ShoppingCart()
        cart.add_item("Python 책", 25000, 2)
        cart.add_item("키보드", 80000, 1)
        assert cart.shipping_fee() == 0

    def test_shipping_fee_empty_cart(self):
        cart = ShoppingCart()
        assert cart.shipping_fee() == 0

    # --- 최종 결제 금액 ---
    def test_checkout_price_with_shipping(self):
        cart = ShoppingCart()
        cart.add_item("Python 책", 25000, 1)
        assert cart.checkout_price() == 28000

    def test_checkout_price_free_shipping(self):
        cart = ShoppingCart()
        cart.add_item("키보드", 120000, 1)
        assert cart.checkout_price() == 120000
```

---

## TDD 사이클 요약

| 사이클 | 기능 | RED (실패) | GREEN (통과) | REFACTOR |
|--------|------|-----------|-------------|----------|
| 1 | 빈 장바구니 생성 | 모듈 없음 | `ShoppingCart` 클래스 생성 | - |
| 2 | 상품 추가 | `add_item` 없음 | `add_item` 구현 | 동일 상품 수량 합산 |
| 3 | 상품 제거 | `remove_item` 없음 | `remove_item` 구현 | - |
| 4 | 수량 변경 | `update_quantity` 없음 | `update_quantity` 구현 | `_find_item` 헬퍼 추출 |
| 5 | 총 금액 계산 | 항상 0 반환 | `sum()` 계산 구현 | - |
| 6 | 배송비 계산 | `shipping_fee` 없음 | 조건부 배송비 구현 | 상수 추출, `checkout_price` 추가 |

**최종 결과: 19 tests passed**
