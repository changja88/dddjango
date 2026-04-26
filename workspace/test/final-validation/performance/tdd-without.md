# TDD로 주문 생성(place_order) 기능 개발하기

## 개요

TDD(Test-Driven Development)의 핵심 사이클인 **Red-Green-Refactor**를 따라 Django 기반의 주문 생성 기능을 단계별로 개발한다. 각 단계에서 왜 그런 결정을 내리는지 함께 설명한다.

---

## 사전 준비: 도메인 분석

코드를 작성하기 전에 `place_order`가 무엇을 해야 하는지 정리한다.

**요구사항:**
1. 사용자가 장바구니에 담긴 상품으로 주문을 생성한다
2. 재고가 충분한지 확인한다
3. 총 금액을 계산한다
4. 주문 상태는 `PENDING`으로 시작한다
5. 재고가 부족하면 예외를 발생시킨다
6. 장바구니가 비어있으면 주문할 수 없다

---

## 사이클 1: 가장 단순한 주문 생성

### RED -- 실패하는 테스트 작성

TDD의 첫 번째 원칙: **테스트를 먼저 작성하고, 그 테스트가 실패하는 것을 확인한다.**

아직 아무 코드도 없는 상태에서 가장 단순한 시나리오부터 시작한다. "주문을 생성하면 Order 객체가 반환된다."

```python
# tests/test_place_order.py

from django.test import TestCase
from decimal import Decimal
from orders.models import Order, OrderItem, Product
from orders.services import place_order


class PlaceOrderTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="키보드",
            price=Decimal("89000"),
            stock=10,
        )

    def test_주문_생성시_order_객체가_반환된다(self):
        items = [{"product_id": self.product.id, "quantity": 1}]

        order = place_order(user_id=1, items=items)

        self.assertIsInstance(order, Order)
        self.assertEqual(order.status, "PENDING")
```

**왜 이렇게 하는가?**
- 가장 작고 단순한 동작 하나만 검증한다. "주문이 만들어지고, 상태가 PENDING이다."
- 아직 `orders/services.py`도 없으므로 `ImportError`로 실패한다.
- 이 실패를 확인하는 것이 중요하다. 테스트가 실제로 동작하는지, 올바른 이유로 실패하는지 확인해야 한다.

```
$ python manage.py test tests.test_place_order
ImportError: cannot import name 'place_order' from 'orders.services'
```

### GREEN -- 테스트를 통과시키는 최소한의 코드 작성

테스트를 통과시키기 위한 최소한의 코드만 작성한다. 완벽할 필요 없다.

```python
# orders/models.py

from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    stock = models.PositiveIntegerField(default=0)


class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
    ]

    user_id = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    total_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=0)
```

```python
# orders/services.py

from orders.models import Order, OrderItem, Product


def place_order(user_id: int, items: list[dict]) -> Order:
    order = Order.objects.create(user_id=user_id, status="PENDING")

    for item_data in items:
        product = Product.objects.get(id=item_data["product_id"])
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item_data["quantity"],
            unit_price=product.price,
        )

    return order
```

```
$ python manage.py test tests.test_place_order
OK (1 test)
```

**왜 이렇게 하는가?**
- "최소한의 코드"가 핵심이다. 재고 확인, 금액 계산 등은 아직 하지 않는다.
- 테스트가 요구하는 것만 구현한다: Order 생성, 상태 PENDING.
- 과도한 설계를 방지한다. 필요할 때 추가하면 된다.

### REFACTOR -- 정리

현재 단계에서는 코드가 단순하므로 리팩터링할 것이 없다. 넘어간다.

**왜 이렇게 하는가?**
- 리팩터링은 "필요할 때" 한다. 억지로 할 필요 없다.
- 중복이 없고, 의도가 명확하면 그대로 둔다.

---

## 사이클 2: 총 금액 계산

### RED -- 실패하는 테스트 작성

```python
# tests/test_place_order.py 에 추가

    def test_주문_총_금액이_올바르게_계산된다(self):
        product_a = self.product  # 89,000원
        product_b = Product.objects.create(
            name="마우스", price=Decimal("45000"), stock=5
        )
        items = [
            {"product_id": product_a.id, "quantity": 2},
            {"product_id": product_b.id, "quantity": 3},
        ]

        order = place_order(user_id=1, items=items)

        # 89000*2 + 45000*3 = 178000 + 135000 = 313000
        self.assertEqual(order.total_amount, Decimal("313000"))
```

```
$ python manage.py test tests.test_place_order
FAIL: test_주문_총_금액이_올바르게_계산된다
AssertionError: Decimal('0') != Decimal('313000')
```

**왜 이렇게 하는가?**
- 새로운 요구사항(총 금액 계산)을 테스트로 먼저 표현한다.
- 현재 코드는 `total_amount`를 계산하지 않으므로 기본값 0이 반환되어 실패한다.
- 테스트가 올바른 이유로 실패하는 것을 확인했다.

### GREEN -- 통과시키기

```python
# orders/services.py (수정)

from decimal import Decimal
from orders.models import Order, OrderItem, Product


def place_order(user_id: int, items: list[dict]) -> Order:
    order = Order.objects.create(user_id=user_id, status="PENDING")

    total = Decimal("0")
    for item_data in items:
        product = Product.objects.get(id=item_data["product_id"])
        line_total = product.price * item_data["quantity"]
        total += line_total
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item_data["quantity"],
            unit_price=product.price,
        )

    order.total_amount = total
    order.save()

    return order
```

```
$ python manage.py test tests.test_place_order
OK (2 tests)
```

**왜 이렇게 하는가?**
- 실패한 테스트를 통과시키기 위해 총 금액 계산 로직을 추가했다.
- 기존 테스트도 여전히 통과하는지 반드시 확인한다. 기존 기능을 깨뜨리면 안 된다.

### REFACTOR -- 정리

아직 큰 중복은 없지만, `place_order` 함수가 점점 커지고 있다. 일단 유지하고 다음 사이클에서 판단한다.

---

## 사이클 3: 재고 부족 시 예외 발생

### RED -- 실패하는 테스트 작성

```python
# tests/test_place_order.py 에 추가

from orders.exceptions import InsufficientStockError


class PlaceOrderStockTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="키보드", price=Decimal("89000"), stock=2
        )

    def test_재고_부족시_InsufficientStockError가_발생한다(self):
        items = [{"product_id": self.product.id, "quantity": 5}]

        with self.assertRaises(InsufficientStockError):
            place_order(user_id=1, items=items)

    def test_재고_부족시_주문이_생성되지_않는다(self):
        items = [{"product_id": self.product.id, "quantity": 5}]

        with self.assertRaises(InsufficientStockError):
            place_order(user_id=1, items=items)

        self.assertEqual(Order.objects.count(), 0)
```

```
$ python manage.py test tests.test_place_order
ImportError: cannot import name 'InsufficientStockError' from 'orders.exceptions'
```

**왜 이렇게 하는가?**
- 예외 상황을 명시적으로 테스트한다. "재고가 2개인데 5개를 주문하면 에러가 나야 한다."
- 두 번째 테스트는 더 중요하다: 에러가 나면 주문 자체가 DB에 남으면 안 된다 (트랜잭션 무결성).
- 이 두 테스트가 동시에 실패하는 것을 확인한다.

### GREEN -- 통과시키기

```python
# orders/exceptions.py

class InsufficientStockError(Exception):
    def __init__(self, product_name: str, requested: int, available: int):
        self.product_name = product_name
        self.requested = requested
        self.available = available
        super().__init__(
            f"재고 부족: {product_name} (요청: {requested}, 남은 재고: {available})"
        )
```

```python
# orders/services.py (수정)

from decimal import Decimal
from django.db import transaction
from orders.models import Order, OrderItem, Product
from orders.exceptions import InsufficientStockError


def place_order(user_id: int, items: list[dict]) -> Order:
    with transaction.atomic():
        order = Order.objects.create(user_id=user_id, status="PENDING")

        total = Decimal("0")
        for item_data in items:
            product = Product.objects.get(id=item_data["product_id"])
            quantity = item_data["quantity"]

            if product.stock < quantity:
                raise InsufficientStockError(
                    product_name=product.name,
                    requested=quantity,
                    available=product.stock,
                )

            line_total = product.price * quantity
            total += line_total
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.price,
            )

        order.total_amount = total
        order.save()

    return order
```

```
$ python manage.py test tests.test_place_order
OK (4 tests)
```

**왜 이렇게 하는가?**
- `transaction.atomic()`을 사용하여, 예외 발생 시 모든 DB 변경이 롤백된다.
- 예외 클래스에 구체적인 정보(상품명, 요청 수량, 가용 재고)를 담아서 디버깅과 사용자 피드백에 유용하게 만든다.
- 두 번째 테스트(`주문이_생성되지_않는다`)가 트랜잭션 롤백을 검증한다.

### REFACTOR -- 정리

이제 함수가 꽤 길어졌다. 재고 확인과 아이템 생성 로직을 분리한다.

```python
# orders/services.py (리팩터링)

from decimal import Decimal
from django.db import transaction
from orders.models import Order, OrderItem, Product
from orders.exceptions import InsufficientStockError


def _validate_stock(product: Product, quantity: int) -> None:
    if product.stock < quantity:
        raise InsufficientStockError(
            product_name=product.name,
            requested=quantity,
            available=product.stock,
        )


def _create_order_item(order: Order, product: Product, quantity: int) -> Decimal:
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=quantity,
        unit_price=product.price,
    )
    return product.price * quantity


def place_order(user_id: int, items: list[dict]) -> Order:
    with transaction.atomic():
        order = Order.objects.create(user_id=user_id, status="PENDING")

        total = Decimal("0")
        for item_data in items:
            product = Product.objects.get(id=item_data["product_id"])
            quantity = item_data["quantity"]

            _validate_stock(product, quantity)
            total += _create_order_item(order, product, quantity)

        order.total_amount = total
        order.save()

    return order
```

```
$ python manage.py test tests.test_place_order
OK (4 tests)
```

**왜 이렇게 하는가?**
- 리팩터링 후에도 모든 테스트가 통과하는 것이 핵심이다. 테스트가 안전망 역할을 한다.
- `_validate_stock`과 `_create_order_item`으로 분리하면 각 함수의 책임이 명확해진다.
- `place_order`는 이제 흐름(flow)만 관리하고, 세부 로직은 헬퍼에 위임한다.

---

## 사이클 4: 빈 장바구니 방어

### RED -- 실패하는 테스트 작성

```python
# tests/test_place_order.py 에 추가

class PlaceOrderValidationTest(TestCase):
    def test_빈_장바구니로_주문시_ValueError가_발생한다(self):
        with self.assertRaises(ValueError) as ctx:
            place_order(user_id=1, items=[])

        self.assertIn("비어있", str(ctx.exception))

    def test_빈_장바구니_주문시_order가_생성되지_않는다(self):
        with self.assertRaises(ValueError):
            place_order(user_id=1, items=[])

        self.assertEqual(Order.objects.count(), 0)
```

```
$ python manage.py test tests.test_place_order
FAIL: test_빈_장바구니로_주문시_ValueError가_발생한다
AssertionError: ValueError not raised
```

**왜 이렇게 하는가?**
- 엣지 케이스를 빠뜨리지 않기 위해 테스트를 먼저 작성한다.
- 빈 장바구니로 주문하면 불필요한 빈 Order 레코드가 생길 수 있다.
- 에러 메시지에 "비어있"이라는 문구가 포함되는지까지 검증하여 메시지 품질도 관리한다.

### GREEN -- 통과시키기

```python
# orders/services.py (수정 -- place_order 시작 부분)

def place_order(user_id: int, items: list[dict]) -> Order:
    if not items:
        raise ValueError("장바구니가 비어있습니다.")

    with transaction.atomic():
        order = Order.objects.create(user_id=user_id, status="PENDING")

        total = Decimal("0")
        for item_data in items:
            product = Product.objects.get(id=item_data["product_id"])
            quantity = item_data["quantity"]

            _validate_stock(product, quantity)
            total += _create_order_item(order, product, quantity)

        order.total_amount = total
        order.save()

    return order
```

```
$ python manage.py test tests.test_place_order
OK (6 tests)
```

**왜 이렇게 하는가?**
- `transaction.atomic()` 블록에 진입하기 전에 빈 장바구니를 거부한다.
- 불필요한 DB 연결 자체를 피하는 것이 효율적이다.

### REFACTOR

추가 정리 불필요. 넘어간다.

---

## 사이클 5: 재고 차감

### RED -- 실패하는 테스트 작성

```python
# tests/test_place_order.py 에 추가

class PlaceOrderStockDeductionTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="키보드", price=Decimal("89000"), stock=10
        )

    def test_주문_성공시_재고가_차감된다(self):
        items = [{"product_id": self.product.id, "quantity": 3}]

        place_order(user_id=1, items=items)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 7)

    def test_여러_상품_주문시_각_상품의_재고가_차감된다(self):
        product_b = Product.objects.create(
            name="마우스", price=Decimal("45000"), stock=5
        )
        items = [
            {"product_id": self.product.id, "quantity": 2},
            {"product_id": product_b.id, "quantity": 4},
        ]

        place_order(user_id=1, items=items)

        self.product.refresh_from_db()
        product_b.refresh_from_db()
        self.assertEqual(self.product.stock, 8)
        self.assertEqual(product_b.stock, 1)
```

```
$ python manage.py test tests.test_place_order
FAIL: test_주문_성공시_재고가_차감된다
AssertionError: 10 != 7
```

**왜 이렇게 하는가?**
- 주문이 성공하면 재고가 줄어야 한다. 이것은 비즈니스 규칙이다.
- `refresh_from_db()`로 DB에서 최신 값을 다시 읽어서 검증한다.
- 단일 상품과 복수 상품 케이스를 모두 테스트한다.

### GREEN -- 통과시키기

```python
# orders/services.py (_create_order_item 수정)

def _create_order_item(order: Order, product: Product, quantity: int) -> Decimal:
    product.stock -= quantity
    product.save(update_fields=["stock"])

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=quantity,
        unit_price=product.price,
    )
    return product.price * quantity
```

```
$ python manage.py test tests.test_place_order
OK (8 tests)
```

**왜 이렇게 하는가?**
- `update_fields=["stock"]`으로 stock 필드만 업데이트하여 불필요한 필드 덮어쓰기를 방지한다.
- 재고 차감이 `transaction.atomic()` 안에 있으므로, 중간에 에러가 나면 차감도 롤백된다.

### REFACTOR -- 동시성 안전하게

프로덕션 환경에서는 동시에 같은 상품을 주문할 수 있다. `select_for_update`를 적용한다.

```python
# orders/services.py (최종 리팩터링)

from decimal import Decimal
from django.db import transaction
from orders.models import Order, OrderItem, Product
from orders.exceptions import InsufficientStockError


def _validate_stock(product: Product, quantity: int) -> None:
    if product.stock < quantity:
        raise InsufficientStockError(
            product_name=product.name,
            requested=quantity,
            available=product.stock,
        )


def _create_order_item(order: Order, product: Product, quantity: int) -> Decimal:
    product.stock -= quantity
    product.save(update_fields=["stock"])

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=quantity,
        unit_price=product.price,
    )
    return product.price * quantity


def place_order(user_id: int, items: list[dict]) -> Order:
    if not items:
        raise ValueError("장바구니가 비어있습니다.")

    with transaction.atomic():
        order = Order.objects.create(user_id=user_id, status="PENDING")

        total = Decimal("0")
        for item_data in items:
            product = Product.objects.select_for_update().get(
                id=item_data["product_id"]
            )
            quantity = item_data["quantity"]

            _validate_stock(product, quantity)
            total += _create_order_item(order, product, quantity)

        order.total_amount = total
        order.save()

    return order
```

```
$ python manage.py test tests.test_place_order
OK (8 tests)
```

**왜 이렇게 하는가?**
- `select_for_update()`는 해당 row에 DB 레벨 잠금을 건다. 다른 트랜잭션이 같은 상품을 동시에 읽으려 하면 대기한다.
- 이렇게 하면 두 사용자가 동시에 마지막 1개를 주문하는 race condition을 방지할 수 있다.
- 리팩터링 후에도 기존 8개 테스트가 모두 통과하므로 안전하다.

---

## 최종 코드 정리

### orders/exceptions.py

```python
class InsufficientStockError(Exception):
    def __init__(self, product_name: str, requested: int, available: int):
        self.product_name = product_name
        self.requested = requested
        self.available = available
        super().__init__(
            f"재고 부족: {product_name} (요청: {requested}, 남은 재고: {available})"
        )
```

### orders/models.py

```python
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    stock = models.PositiveIntegerField(default=0)


class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
    ]

    user_id = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    total_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=0)
```

### orders/services.py

```python
from decimal import Decimal
from django.db import transaction
from orders.models import Order, OrderItem, Product
from orders.exceptions import InsufficientStockError


def _validate_stock(product: Product, quantity: int) -> None:
    if product.stock < quantity:
        raise InsufficientStockError(
            product_name=product.name,
            requested=quantity,
            available=product.stock,
        )


def _create_order_item(order: Order, product: Product, quantity: int) -> Decimal:
    product.stock -= quantity
    product.save(update_fields=["stock"])

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=quantity,
        unit_price=product.price,
    )
    return product.price * quantity


def place_order(user_id: int, items: list[dict]) -> Order:
    if not items:
        raise ValueError("장바구니가 비어있습니다.")

    with transaction.atomic():
        order = Order.objects.create(user_id=user_id, status="PENDING")

        total = Decimal("0")
        for item_data in items:
            product = Product.objects.select_for_update().get(
                id=item_data["product_id"]
            )
            quantity = item_data["quantity"]

            _validate_stock(product, quantity)
            total += _create_order_item(order, product, quantity)

        order.total_amount = total
        order.save()

    return order
```

### tests/test_place_order.py (전체)

```python
from decimal import Decimal
from django.test import TestCase
from orders.models import Order, Product
from orders.services import place_order
from orders.exceptions import InsufficientStockError


class PlaceOrderTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="키보드", price=Decimal("89000"), stock=10
        )

    def test_주문_생성시_order_객체가_반환된다(self):
        items = [{"product_id": self.product.id, "quantity": 1}]
        order = place_order(user_id=1, items=items)
        self.assertIsInstance(order, Order)
        self.assertEqual(order.status, "PENDING")

    def test_주문_총_금액이_올바르게_계산된다(self):
        product_b = Product.objects.create(
            name="마우스", price=Decimal("45000"), stock=5
        )
        items = [
            {"product_id": self.product.id, "quantity": 2},
            {"product_id": product_b.id, "quantity": 3},
        ]
        order = place_order(user_id=1, items=items)
        self.assertEqual(order.total_amount, Decimal("313000"))


class PlaceOrderStockTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="키보드", price=Decimal("89000"), stock=2
        )

    def test_재고_부족시_InsufficientStockError가_발생한다(self):
        items = [{"product_id": self.product.id, "quantity": 5}]
        with self.assertRaises(InsufficientStockError):
            place_order(user_id=1, items=items)

    def test_재고_부족시_주문이_생성되지_않는다(self):
        items = [{"product_id": self.product.id, "quantity": 5}]
        with self.assertRaises(InsufficientStockError):
            place_order(user_id=1, items=items)
        self.assertEqual(Order.objects.count(), 0)


class PlaceOrderValidationTest(TestCase):
    def test_빈_장바구니로_주문시_ValueError가_발생한다(self):
        with self.assertRaises(ValueError) as ctx:
            place_order(user_id=1, items=[])
        self.assertIn("비어있", str(ctx.exception))

    def test_빈_장바구니_주문시_order가_생성되지_않는다(self):
        with self.assertRaises(ValueError):
            place_order(user_id=1, items=[])
        self.assertEqual(Order.objects.count(), 0)


class PlaceOrderStockDeductionTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="키보드", price=Decimal("89000"), stock=10
        )

    def test_주문_성공시_재고가_차감된다(self):
        items = [{"product_id": self.product.id, "quantity": 3}]
        place_order(user_id=1, items=items)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 7)

    def test_여러_상품_주문시_각_상품의_재고가_차감된다(self):
        product_b = Product.objects.create(
            name="마우스", price=Decimal("45000"), stock=5
        )
        items = [
            {"product_id": self.product.id, "quantity": 2},
            {"product_id": product_b.id, "quantity": 4},
        ]
        place_order(user_id=1, items=items)
        self.product.refresh_from_db()
        product_b.refresh_from_db()
        self.assertEqual(self.product.stock, 8)
        self.assertEqual(product_b.stock, 1)
```

---

## TDD 사이클 요약

| 사이클 | RED (실패 테스트) | GREEN (통과) | REFACTOR (정리) |
|--------|------------------|-------------|-----------------|
| 1 | 주문 생성 + 상태 PENDING | 모델, 서비스 최소 구현 | 불필요 |
| 2 | 총 금액 계산 | 금액 합산 로직 추가 | 불필요 |
| 3 | 재고 부족 예외 + 트랜잭션 롤백 | 재고 검증 + atomic | 헬퍼 함수 분리 |
| 4 | 빈 장바구니 방어 | 사전 검증 추가 | 불필요 |
| 5 | 재고 차감 | stock 감소 + save | select_for_update 적용 |

## 핵심 교훈

1. **한 번에 하나의 실패만 다룬다** -- 여러 기능을 동시에 구현하려 하지 않는다.
2. **테스트가 요구하는 것만 구현한다** -- "나중에 필요할 것 같은" 코드를 미리 만들지 않는다(YAGNI).
3. **리팩터링은 녹색불 아래서만 한다** -- 모든 테스트가 통과하는 상태에서만 코드를 정리한다.
4. **테스트는 문서다** -- 한국어 메서드 이름(`test_재고_부족시_주문이_생성되지_않는다`)이 요구사항 문서 역할을 한다.
5. **엣지 케이스를 잊지 않는다** -- 빈 입력, 재고 부족 같은 경계 조건을 테스트가 강제한다.
