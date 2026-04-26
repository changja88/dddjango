# TDD로 장바구니(ShoppingCart) 구현

## 테스트 목록

구현 전에 필요한 테스트를 모두 적어 둔다.

```
[x] 빈 장바구니의 총 금액은 0이다
[x] 상품을 하나 추가하면 총 금액이 상품 가격이다
[x] 서로 다른 상품 여러 개를 추가하면 총 금액은 합산이다
[x] 같은 상품을 여러 번 추가하면 수량이 누적된다
[x] 상품을 제거할 수 있다
[x] 존재하지 않는 상품 제거 시 에러
[x] 상품 수량을 변경할 수 있다
[x] 수량을 0으로 변경하면 상품이 제거된다
[x] 수량을 음수로 변경하면 에러
[x] 10만원 이상이면 배송비 무료
[x] 10만원 미만이면 배송비 3000원
[x] 빈 장바구니의 배송비는 3000원
```

---

## Cycle 1: 빈 장바구니의 총 금액

### RED -- 실패하는 테스트 작성

```python
# test_cart.py

def test_empty_cart_total():
    cart = ShoppingCart()
    assert cart.total() == 0
```

```
$ pytest test_cart.py
E   NameError: name 'ShoppingCart' is not defined
FAILED
```

### GREEN -- 최소한의 코드로 통과

```python
# cart.py

class ShoppingCart:
    def total(self):
        return 0
```

```python
# test_cart.py
from cart import ShoppingCart

def test_empty_cart_total():
    cart = ShoppingCart()
    assert cart.total() == 0
```

```
$ pytest test_cart.py
PASSED (1 passed)
```

### REFACTOR

리팩토링 대상 없음. 다음 사이클로 진행.

---

## Cycle 2: 상품 하나 추가

### RED

```python
def test_add_single_item():
    cart = ShoppingCart()
    cart.add("사과", 1500)
    assert cart.total() == 1500
```

```
$ pytest test_cart.py
E   TypeError: ShoppingCart.add() ...
FAILED
```

### GREEN

Fake It -- 상수를 반환하여 일단 통과시킨다.

```python
class ShoppingCart:
    def __init__(self):
        self._items = {}

    def add(self, name, price):
        self._items[name] = {"price": price, "quantity": 1}

    def total(self):
        return sum(
            item["price"] * item["quantity"]
            for item in self._items.values()
        )
```

```
$ pytest test_cart.py
PASSED (2 passed)
```

### REFACTOR

리팩토링 대상 없음. 구현이 아직 작으므로 다음으로 진행.

---

## Cycle 3: 서로 다른 상품 여러 개

### RED

```python
def test_add_multiple_different_items():
    cart = ShoppingCart()
    cart.add("사과", 1500)
    cart.add("우유", 3000)
    assert cart.total() == 4500
```

```
$ pytest test_cart.py
PASSED (3 passed)
```

이미 통과한다. Cycle 2의 구현이 이미 여러 상품을 처리하기 때문이다. 삼각측량 확인 완료. 다음 테스트로 진행.

---

## Cycle 4: 같은 상품 여러 번 추가 시 수량 누적

### RED

```python
def test_add_same_item_increases_quantity():
    cart = ShoppingCart()
    cart.add("사과", 1500)
    cart.add("사과", 1500)
    assert cart.total() == 3000
```

```
$ pytest test_cart.py
E   AssertionError: assert 1500 != 3000
FAILED
```

현재 `add`는 같은 이름으로 추가하면 덮어쓰기 때문에 수량이 1로 유지된다.

### GREEN

```python
def add(self, name, price):
    if name in self._items:
        self._items[name]["quantity"] += 1
    else:
        self._items[name] = {"price": price, "quantity": 1}
```

```
$ pytest test_cart.py
PASSED (4 passed)
```

### REFACTOR

`_items`의 값으로 딕셔너리를 사용하고 있다. 이 구조가 반복되므로 나중에 데이터 클래스로 추출할 후보이다. 현 단계에서는 아직 충분히 단순하므로 유지한다.

---

## Cycle 5: 상품 제거

### RED

```python
def test_remove_item():
    cart = ShoppingCart()
    cart.add("사과", 1500)
    cart.add("우유", 3000)
    cart.remove("사과")
    assert cart.total() == 3000
```

```
$ pytest test_cart.py
E   AttributeError: 'ShoppingCart' object has no attribute 'remove'
FAILED
```

### GREEN

```python
def remove(self, name):
    del self._items[name]
```

```
$ pytest test_cart.py
PASSED (5 passed)
```

### REFACTOR

리팩토링 대상 없음.

---

## Cycle 6: 존재하지 않는 상품 제거 시 에러

### RED

```python
import pytest

def test_remove_nonexistent_item_raises():
    cart = ShoppingCart()
    with pytest.raises(KeyError):
        cart.remove("바나나")
```

```
$ pytest test_cart.py
PASSED (6 passed)
```

`del self._items[name]`이 이미 `KeyError`를 발생시킨다. 테스트가 곧바로 통과한다. 행위가 이미 올바르므로 다음으로 진행.

---

## Cycle 7: 수량 변경

### RED

```python
def test_update_quantity():
    cart = ShoppingCart()
    cart.add("사과", 1500)
    cart.update_quantity("사과", 5)
    assert cart.total() == 7500
```

```
$ pytest test_cart.py
E   AttributeError: 'ShoppingCart' object has no attribute 'update_quantity'
FAILED
```

### GREEN

```python
def update_quantity(self, name, quantity):
    self._items[name]["quantity"] = quantity
```

```
$ pytest test_cart.py
PASSED (7 passed)
```

### REFACTOR

리팩토링 대상 없음.

---

## Cycle 8: 수량을 0으로 변경하면 상품 제거

### RED

```python
def test_update_quantity_to_zero_removes_item():
    cart = ShoppingCart()
    cart.add("사과", 1500)
    cart.update_quantity("사과", 0)
    assert cart.total() == 0
```

```
$ pytest test_cart.py
PASSED (8 passed)
```

수량 0이면 `price * 0 == 0`이므로 total은 이미 0을 반환한다. 그러나 상품이 장바구니에 "남아 있는" 상태다. 명세를 더 엄밀하게 표현하기 위해 테스트를 보강한다.

```python
def test_update_quantity_to_zero_removes_item():
    cart = ShoppingCart()
    cart.add("사과", 1500)
    cart.add("우유", 3000)
    cart.update_quantity("사과", 0)
    assert cart.total() == 3000
    with pytest.raises(KeyError):
        cart.remove("사과")  # 이미 제거되었으므로 KeyError
```

```
$ pytest test_cart.py
E   KeyError not raised -- "사과"가 아직 _items에 남아있다
FAILED
```

### GREEN

```python
def update_quantity(self, name, quantity):
    if quantity == 0:
        del self._items[name]
    else:
        self._items[name]["quantity"] = quantity
```

```
$ pytest test_cart.py
PASSED (8 passed)
```

### REFACTOR

`update_quantity`에서 `del self._items[name]`이 `remove`와 중복된다. `remove`를 재사용한다.

```python
def update_quantity(self, name, quantity):
    if quantity == 0:
        self.remove(name)
    else:
        self._items[name]["quantity"] = quantity
```

```
$ pytest test_cart.py
PASSED (8 passed)
```

---

## Cycle 9: 수량을 음수로 변경하면 에러

### RED

```python
def test_update_quantity_negative_raises():
    cart = ShoppingCart()
    cart.add("사과", 1500)
    with pytest.raises(ValueError, match="수량은 0 이상"):
        cart.update_quantity("사과", -1)
```

```
$ pytest test_cart.py
E   ValueError not raised
FAILED
```

### GREEN

```python
def update_quantity(self, name, quantity):
    if quantity < 0:
        raise ValueError("수량은 0 이상이어야 합니다")
    if quantity == 0:
        self.remove(name)
    else:
        self._items[name]["quantity"] = quantity
```

```
$ pytest test_cart.py
PASSED (9 passed)
```

### REFACTOR

리팩토링 대상 없음.

---

## Cycle 10: 10만원 이상이면 배송비 무료

### RED

```python
def test_shipping_fee_free_when_total_gte_100000():
    cart = ShoppingCart()
    cart.add("노트북 거치대", 50000)
    cart.add("키보드", 50000)
    assert cart.total() == 100000
    assert cart.shipping_fee() == 0
```

```
$ pytest test_cart.py
E   AttributeError: 'ShoppingCart' object has no attribute 'shipping_fee'
FAILED
```

### GREEN

Fake It -- 상수를 반환한다.

```python
def shipping_fee(self):
    return 0
```

```
$ pytest test_cart.py
PASSED (10 passed)
```

이 상수 반환은 아직 일반화되지 않았다. 삼각측량을 위해 두 번째 예제가 필요하다. 다음 사이클로 진행.

---

## Cycle 11: 10만원 미만이면 배송비 3000원

### RED

삼각측량 -- 두 번째 예제로 일반화를 강제한다.

```python
def test_shipping_fee_3000_when_total_lt_100000():
    cart = ShoppingCart()
    cart.add("볼펜", 2000)
    assert cart.total() == 2000
    assert cart.shipping_fee() == 3000
```

```
$ pytest test_cart.py
E   AssertionError: assert 0 != 3000
FAILED
```

### GREEN

Obvious Implementation -- 조건이 명백하다.

```python
def shipping_fee(self):
    if self.total() >= 100000:
        return 0
    return 3000
```

```
$ pytest test_cart.py
PASSED (11 passed)
```

### REFACTOR

매직 넘버를 상수로 추출한다.

```python
FREE_SHIPPING_THRESHOLD = 100_000
SHIPPING_FEE = 3_000

class ShoppingCart:
    # ...

    def shipping_fee(self):
        if self.total() >= FREE_SHIPPING_THRESHOLD:
            return 0
        return SHIPPING_FEE
```

```
$ pytest test_cart.py
PASSED (11 passed)
```

---

## Cycle 12: 빈 장바구니의 배송비

### RED

```python
def test_empty_cart_shipping_fee():
    cart = ShoppingCart()
    assert cart.shipping_fee() == 3000
```

```
$ pytest test_cart.py
PASSED (12 passed)
```

빈 장바구니의 total은 0이고, 0 < 100,000이므로 배송비 3000원이 이미 반환된다. 테스트 통과.

---

## 최종 코드

### cart.py

```python
FREE_SHIPPING_THRESHOLD = 100_000
SHIPPING_FEE = 3_000


class ShoppingCart:
    def __init__(self):
        self._items = {}

    def add(self, name, price):
        if name in self._items:
            self._items[name]["quantity"] += 1
        else:
            self._items[name] = {"price": price, "quantity": 1}

    def remove(self, name):
        del self._items[name]

    def update_quantity(self, name, quantity):
        if quantity < 0:
            raise ValueError("수량은 0 이상이어야 합니다")
        if quantity == 0:
            self.remove(name)
        else:
            self._items[name]["quantity"] = quantity

    def total(self):
        return sum(
            item["price"] * item["quantity"]
            for item in self._items.values()
        )

    def shipping_fee(self):
        if self.total() >= FREE_SHIPPING_THRESHOLD:
            return 0
        return SHIPPING_FEE
```

### test_cart.py

```python
import pytest
from cart import ShoppingCart


def test_empty_cart_total():
    cart = ShoppingCart()
    assert cart.total() == 0


def test_add_single_item():
    cart = ShoppingCart()
    cart.add("사과", 1500)
    assert cart.total() == 1500


def test_add_multiple_different_items():
    cart = ShoppingCart()
    cart.add("사과", 1500)
    cart.add("우유", 3000)
    assert cart.total() == 4500


def test_add_same_item_increases_quantity():
    cart = ShoppingCart()
    cart.add("사과", 1500)
    cart.add("사과", 1500)
    assert cart.total() == 3000


def test_remove_item():
    cart = ShoppingCart()
    cart.add("사과", 1500)
    cart.add("우유", 3000)
    cart.remove("사과")
    assert cart.total() == 3000


def test_remove_nonexistent_item_raises():
    cart = ShoppingCart()
    with pytest.raises(KeyError):
        cart.remove("바나나")


def test_update_quantity():
    cart = ShoppingCart()
    cart.add("사과", 1500)
    cart.update_quantity("사과", 5)
    assert cart.total() == 7500


def test_update_quantity_to_zero_removes_item():
    cart = ShoppingCart()
    cart.add("사과", 1500)
    cart.add("우유", 3000)
    cart.update_quantity("사과", 0)
    assert cart.total() == 3000
    with pytest.raises(KeyError):
        cart.remove("사과")


def test_update_quantity_negative_raises():
    cart = ShoppingCart()
    cart.add("사과", 1500)
    with pytest.raises(ValueError, match="수량은 0 이상"):
        cart.update_quantity("사과", -1)


def test_shipping_fee_free_when_total_gte_100000():
    cart = ShoppingCart()
    cart.add("노트북 거치대", 50000)
    cart.add("키보드", 50000)
    assert cart.total() == 100000
    assert cart.shipping_fee() == 0


def test_shipping_fee_3000_when_total_lt_100000():
    cart = ShoppingCart()
    cart.add("볼펜", 2000)
    assert cart.total() == 2000
    assert cart.shipping_fee() == 3000


def test_empty_cart_shipping_fee():
    cart = ShoppingCart()
    assert cart.shipping_fee() == 3000
```

---

## 적용된 TDD 원칙 요약

| 사이클 | 적용 패턴 | 설명 |
|:----:|-----------|------|
| 1 | 시작 테스트 | 빈 장바구니(아무 일도 하지 않는 경우)부터 시작 |
| 2 | Obvious Implementation | add/total 구현이 명백하므로 바로 구현 |
| 3 | 삼각측량 확인 | 이미 통과하는 테스트로 기존 구현 검증 |
| 4 | constant -> scalar 변환 | 수량 1 고정에서 누적으로 일반화 |
| 6 | 회귀 테스트 | 경계 조건(존재하지 않는 상품) 확인 |
| 8 | 중복 제거 리팩토링 | update_quantity에서 remove 재사용 |
| 10-11 | Fake It -> 삼각측량 | 상수 반환 후 두 번째 예제로 일반화 강제 |
| 11 | 매직 넘버 추출 | FREE_SHIPPING_THRESHOLD, SHIPPING_FEE 상수화 |
