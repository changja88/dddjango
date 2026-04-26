# 주문 생성(place_order) TDD 개발

## 테스트 목록

시작 전에 구현해야 할 테스트를 먼저 정리한다.

```
[ ] 빈 주문(아이템 없음)은 실패한다
[ ] 단일 아이템 주문 생성
[ ] 여러 아이템 주문 생성
[ ] 주문 총액 계산
[ ] 재고 부족 시 주문 실패
[ ] 주문 생성 시 고유 ID 부여
```

가장 단순한 경우부터 시작하여, 알려진 것에서 미지의 것으로 이동한다.

---

## Cycle 1: 빈 주문은 실패한다

### RED -- 실패하는 테스트 작성

아무 일도 하지 않는 경우를 먼저 테스트한다. 빈 주문은 유효하지 않으므로 에러를 기대한다.

```python
import pytest


def test_place_order__empty_items__raises_error():
    # Arrange
    items = []

    # Act & Assert
    with pytest.raises(ValueError, match="주문 항목이 비어 있습니다"):
        place_order(items)
```

`place_order`가 존재하지 않으므로 `NameError`로 실패한다. 이것이 첫 번째 Red이다. 프로덕션 코드 없이 테스트만 존재하는 상태에서 실패를 확인하는 것이 핵심이다. 실패를 확인해야 테스트가 실제로 무언가를 검증하고 있다는 확신을 얻는다.

### GREEN -- 최소한의 코드로 통과

Fake It 전략을 사용한다. 테스트를 통과시키기에 충분한 최소한의 코드만 작성한다.

```python
def place_order(items: list) -> dict:
    if not items:
        raise ValueError("주문 항목이 비어 있습니다")
```

이 구현은 빈 리스트 검증만 처리한다. 반환 타입도 아직 정의하지 않는다. 지금은 오직 이 테스트를 통과시키는 것만이 목표다.

### REFACTOR -- 변경 없음

코드가 충분히 단순하므로 리팩터링할 중복이 없다. 다음 사이클로 넘어간다.

---

## Cycle 2: 단일 아이템 주문 생성

### RED -- 실패하는 테스트 작성

이제 실제로 주문이 생성되는 가장 단순한 성공 케이스를 테스트한다.

```python
def test_place_order__single_item__creates_order():
    # Arrange
    items = [{"product": "키보드", "quantity": 1, "price": 50_000}]

    # Act
    order = place_order(items)

    # Assert
    assert order["status"] == "created"
    assert order["items"] == items
    assert order["total"] == 50_000
```

`place_order`가 빈 리스트가 아닌 경우 아무것도 반환하지 않으므로 실패한다. Assert First 사고법으로 결과의 모습을 먼저 정의했다. order에 status, items, total이 있어야 한다는 것을 테스트가 설명한다.

### GREEN -- Fake It으로 통과

해결책의 전체 구조가 아직 불분명하므로, Fake It 전략으로 상수에 가까운 값을 반환한다.

```python
def place_order(items: list) -> dict:
    if not items:
        raise ValueError("주문 항목이 비어 있습니다")

    return {
        "status": "created",
        "items": items,
        "total": 50_000,
    }
```

`total`이 하드코딩되어 있다. 이것이 의도적인 Fake It이다. 초록 막대 상태에서 확신을 가지고 다음 단계를 진행할 수 있다.

### REFACTOR -- 변경 없음

하드코딩된 total은 다음 테스트가 일반화를 강제할 것이다. 지금은 건드리지 않는다.

---

## Cycle 3: 여러 아이템 주문 -- 총액 계산

### RED -- 삼각측량을 위한 두 번째 예제

Triangulation 전략이다. 두 번째 예제를 추가하여 하드코딩된 total의 일반화를 강제한다.

```python
def test_place_order__multiple_items__calculates_total():
    # Arrange
    items = [
        {"product": "키보드", "quantity": 1, "price": 50_000},
        {"product": "마우스", "quantity": 2, "price": 30_000},
    ]

    # Act
    order = place_order(items)

    # Assert
    assert order["total"] == 50_000 * 1 + 30_000 * 2
    assert len(order["items"]) == 2
```

기대값을 `110_000`이 아니라 `50_000 * 1 + 30_000 * 2`로 표현했다. 명백한 데이터 패턴으로 계산 과정을 드러낸다. total이 50_000으로 하드코딩되어 있으므로 이 테스트는 실패한다.

### GREEN -- 일반화

두 예제가 존재하므로 이제 추상화가 정당하다. 상수를 변수를 사용하는 수식으로 변환한다(Transformation Priority: constant -> scalar).

```python
def place_order(items: list) -> dict:
    if not items:
        raise ValueError("주문 항목이 비어 있습니다")

    total = sum(item["price"] * item["quantity"] for item in items)

    return {
        "status": "created",
        "items": items,
        "total": total,
    }
```

### REFACTOR -- 도메인 개념 추출

초록 막대 상태이므로 안전하게 리팩터링할 수 있다. 총액 계산 로직을 별도 함수로 추출하고, 데이터 구조를 데이터클래스로 명확히 한다.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class OrderItem:
    product: str
    quantity: int
    price: int

    @property
    def subtotal(self) -> int:
        return self.price * self.quantity


@dataclass(frozen=True)
class Order:
    order_id: str
    items: tuple[OrderItem, ...]
    status: str

    @property
    def total(self) -> int:
        return sum(item.subtotal for item in self.items)


def place_order(items: list[dict]) -> Order:
    if not items:
        raise ValueError("주문 항목이 비어 있습니다")

    order_items = tuple(OrderItem(**item) for item in items)

    return Order(
        order_id="",
        items=order_items,
        status="created",
    )
```

Value Object 패턴을 적용했다. `OrderItem`과 `Order`를 `frozen=True`로 불변 객체로 만들어 안전성을 확보한다. 총액 계산이 `Order.total` 프로퍼티로 이동하여 출력 기반 테스트가 가능해진다. 리팩터링 후 테스트도 새 인터페이스에 맞게 업데이트한다.

```python
def test_place_order__empty_items__raises_error():
    with pytest.raises(ValueError, match="주문 항목이 비어 있습니다"):
        place_order([])


def test_place_order__single_item__creates_order():
    items = [{"product": "키보드", "quantity": 1, "price": 50_000}]

    order = place_order(items)

    assert order.status == "created"
    assert len(order.items) == 1
    assert order.total == 50_000


def test_place_order__multiple_items__calculates_total():
    items = [
        {"product": "키보드", "quantity": 1, "price": 50_000},
        {"product": "마우스", "quantity": 2, "price": 30_000},
    ]

    order = place_order(items)

    assert order.total == 50_000 * 1 + 30_000 * 2
    assert len(order.items) == 2
```

모든 테스트가 통과하는 것을 확인한 후 다음 사이클로 넘어간다.

---

## Cycle 4: 재고 부족 시 주문 실패

### RED -- 외부 의존성 도입

재고 확인은 외부 시스템(재고 서비스)과의 통신이다. London 스쿨 접근법으로 Mock을 사용하여 외부 의존성을 격리한다.

```python
from unittest.mock import Mock


def test_place_order__insufficient_stock__raises_error():
    # Arrange
    stock_service = Mock()
    stock_service.check.return_value = False

    items = [{"product": "키보드", "quantity": 100, "price": 50_000}]

    # Act & Assert
    with pytest.raises(ValueError, match="재고가 부족합니다"):
        place_order(items, stock_service=stock_service)

    stock_service.check.assert_called_once_with("키보드", 100)
```

`place_order`가 `stock_service` 파라미터를 받지 않으므로 실패한다. Mock은 외부 시스템 격리에만 사용한다. 재고 서비스가 어떻게 호출되는지(커뮤니케이션 기반)를 검증하는 것이 이 경우 적절하다.

### GREEN -- 최소 구현

```python
def place_order(
    items: list[dict],
    stock_service=None,
) -> Order:
    if not items:
        raise ValueError("주문 항목이 비어 있습니다")

    order_items = tuple(OrderItem(**item) for item in items)

    if stock_service is not None:
        for item in order_items:
            if not stock_service.check(item.product, item.quantity):
                raise ValueError("재고가 부족합니다")

    return Order(
        order_id="",
        items=order_items,
        status="created",
    )
```

### REFACTOR -- 재고 확인 분리

재고 검증 로직을 별도 메서드로 추출한다.

```python
from dataclasses import dataclass
from typing import Protocol


class StockService(Protocol):
    def check(self, product: str, quantity: int) -> bool: ...


def _validate_stock(items: tuple[OrderItem, ...], stock_service: StockService) -> None:
    for item in items:
        if not stock_service.check(item.product, item.quantity):
            raise ValueError("재고가 부족합니다")


def place_order(
    items: list[dict],
    stock_service: StockService | None = None,
) -> Order:
    if not items:
        raise ValueError("주문 항목이 비어 있습니다")

    order_items = tuple(OrderItem(**item) for item in items)

    if stock_service is not None:
        _validate_stock(order_items, stock_service)

    return Order(
        order_id="",
        items=order_items,
        status="created",
    )
```

Protocol로 인터페이스를 명시하여 Mock의 spec으로도 활용 가능하게 했다. 모든 테스트가 통과한다.

---

## Cycle 5: 주문 생성 시 고유 ID 부여

### RED -- ID 생성

```python
def test_place_order__creates_unique_order_id():
    items = [{"product": "키보드", "quantity": 1, "price": 50_000}]

    order_1 = place_order(items)
    order_2 = place_order(items)

    assert order_1.order_id != ""
    assert order_2.order_id != ""
    assert order_1.order_id != order_2.order_id
```

`order_id`가 빈 문자열이므로 실패한다.

### GREEN -- Obvious Implementation

UUID 생성은 해결책이 명확하므로 Obvious Implementation 전략을 사용한다.

```python
import uuid


def place_order(
    items: list[dict],
    stock_service: StockService | None = None,
) -> Order:
    if not items:
        raise ValueError("주문 항목이 비어 있습니다")

    order_items = tuple(OrderItem(**item) for item in items)

    if stock_service is not None:
        _validate_stock(order_items, stock_service)

    return Order(
        order_id=str(uuid.uuid4()),
        items=order_items,
        status="created",
    )
```

### REFACTOR -- 변경 없음

구현이 단순하고 중복이 없다. 사이클 완료.

---

## 최종 코드

### 프로덕션 코드

```python
import uuid
from dataclasses import dataclass
from typing import Protocol


class StockService(Protocol):
    def check(self, product: str, quantity: int) -> bool: ...


@dataclass(frozen=True)
class OrderItem:
    product: str
    quantity: int
    price: int

    @property
    def subtotal(self) -> int:
        return self.price * self.quantity


@dataclass(frozen=True)
class Order:
    order_id: str
    items: tuple[OrderItem, ...]
    status: str

    @property
    def total(self) -> int:
        return sum(item.subtotal for item in self.items)


def _validate_stock(items: tuple[OrderItem, ...], stock_service: StockService) -> None:
    for item in items:
        if not stock_service.check(item.product, item.quantity):
            raise ValueError("재고가 부족합니다")


def place_order(
    items: list[dict],
    stock_service: StockService | None = None,
) -> Order:
    if not items:
        raise ValueError("주문 항목이 비어 있습니다")

    order_items = tuple(OrderItem(**item) for item in items)

    if stock_service is not None:
        _validate_stock(order_items, stock_service)

    return Order(
        order_id=str(uuid.uuid4()),
        items=order_items,
        status="created",
    )
```

### 테스트 코드

```python
import pytest
from unittest.mock import Mock

from order import place_order


class TestPlaceOrder:
    def test_place_order__empty_items__raises_error(self):
        with pytest.raises(ValueError, match="주문 항목이 비어 있습니다"):
            place_order([])

    def test_place_order__single_item__creates_order(self):
        items = [{"product": "키보드", "quantity": 1, "price": 50_000}]

        order = place_order(items)

        assert order.status == "created"
        assert len(order.items) == 1
        assert order.total == 50_000

    def test_place_order__multiple_items__calculates_total(self):
        items = [
            {"product": "키보드", "quantity": 1, "price": 50_000},
            {"product": "마우스", "quantity": 2, "price": 30_000},
        ]

        order = place_order(items)

        assert order.total == 50_000 * 1 + 30_000 * 2
        assert len(order.items) == 2

    def test_place_order__insufficient_stock__raises_error(self):
        stock_service = Mock()
        stock_service.check.return_value = False
        items = [{"product": "키보드", "quantity": 100, "price": 50_000}]

        with pytest.raises(ValueError, match="재고가 부족합니다"):
            place_order(items, stock_service=stock_service)

        stock_service.check.assert_called_once_with("키보드", 100)

    def test_place_order__creates_unique_order_id(self):
        items = [{"product": "키보드", "quantity": 1, "price": 50_000}]

        order_1 = place_order(items)
        order_2 = place_order(items)

        assert order_1.order_id != ""
        assert order_2.order_id != ""
        assert order_1.order_id != order_2.order_id
```

---

> **관련 스킬 참조:**
> - pytest 픽스처, parametrize, 모킹 기법 -> **implementation-test** 스킬
> - Order, OrderItem의 클린 코드 원칙 (SRP, 네이밍) -> **implementation-cleancode** 스킬
> - Django 모델로 확장 시 TestCase, pytest-django 설정 -> **implementation-django** 스킬
