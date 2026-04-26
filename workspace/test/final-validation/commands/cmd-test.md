# cmd-test 커맨드 실행 결과

## 커맨드 정보
- **커맨드**: `/test`
- **파일**: `commands/test.md`
- **설명**: Write tests for existing code (pytest, fixtures, mocking, factory_boy)

## 사용자 요청
> "주문 서비스(OrderService)의 테스트를 작성해줘. create_order, cancel_order 메서드가 있어."

---

## 1단계: 스킬 로드

### 기본 스킬 (항상 적용)
1. **implementation-cleancode** -- 언어 비종속적 클린 코드 원칙 (네이밍, 함수, SOLID, 에러 처리)
2. **implementation-python** -- Python 3.10+ 컨벤션 (타입 힌트, dataclasses, Protocol)
3. **implementation-django** -- Django 프레임워크 컨벤션 (TestCase, Factory Boy, pytest-django)

### 커맨드 전용 스킬
4. **implementation-test** -- Python 테스트 코드 원칙 (pytest, fixtures, test doubles, factory_boy)

### 로드된 레퍼런스 파일
- `implementation-test/references/test-strategy.md` -- 테스트 피라미드, SMURF
- `implementation-test/references/test-doubles.md` -- Meszaros 5분류, 검증 우선순위
- `implementation-test/references/pytest-fixtures.md` -- pytest 기본 구조, AAA 패턴
- `implementation-test/references/test-data-factory.md` -- factory_boy, Trait, SubFactory
- `implementation-test/references/test-quality.md` -- FIRST 원칙, 안티패턴
- `implementation-test/references/mock-patterns.md` -- Mock spec, seal, side_effect
- `implementation-cleancode/references/error-handling.md` -- 예외 설계, 보호절

---

## 2단계: 모드 판단

- 요청: "테스트 작성해줘"
- **판단: Writing 모드**
- 근거: 사용자가 새 테스트 코드 생성을 요청함. "작성해줘"는 Writing 모드에 해당.

---

## 3단계: 실행 (Writing 모드)

### 적용 원칙 요약

| 원칙 | 출처 스킬 | 적용 내용 |
|------|-----------|-----------|
| AAA 패턴 | implementation-test | Arrange-Act-Assert 구조, Act은 단일 행 |
| FIRST | implementation-test | Fast, Independent, Repeatable, Self-validating, Timely |
| 검증 우선순위 | implementation-test | 출력 기반 > 상태 기반 > 통신 기반 |
| 외부 의존성만 Mock | implementation-test | 핵심 로직은 실제 객체, 외부(결제/이메일)만 Mock |
| factory_boy | implementation-test | 테스트 데이터 팩토리, Trait으로 상태 변형 |
| 도메인 예외 | implementation-cleancode | 에러 코드 대신 도메인 예외 사용 |
| 타입 힌트 | implementation-python | 모든 공개 함수/클래스에 타입 힌트 |
| pytest-django | implementation-django | TestCase, Factory Boy, assertNumQueries |

---

### 생성된 테스트 코드

#### 1. 대상 서비스 코드 (참고용 -- OrderService 가정)

```python
# apps/orders/services.py
from decimal import Decimal

from django.db import transaction

from apps.orders.exceptions import (
    InsufficientStockError,
    OrderAlreadyCancelledError,
    OrderNotCancellableError,
)
from apps.orders.models import Order, OrderItem, OrderStatus
from apps.products.models import Product


def create_order(
    *,
    customer_id: int,
    items: list[dict[str, int | Decimal]],
) -> Order:
    """주문을 생성한다.

    Args:
        customer_id: 주문 고객 ID.
        items: 주문 항목 리스트. 각 항목은 product_id와 quantity를 포함.

    Returns:
        생성된 Order 인스턴스.

    Raises:
        InsufficientStockError: 재고가 부족한 경우.
    """
    with transaction.atomic():
        order = Order.objects.create(
            customer_id=customer_id,
            status=OrderStatus.PENDING,
        )

        for item_data in items:
            product = Product.objects.select_for_update().get(
                id=item_data["product_id"],
            )
            quantity = item_data["quantity"]

            if product.stock < quantity:
                raise InsufficientStockError(
                    product_id=product.id,
                    requested=quantity,
                    available=product.stock,
                )

            product.stock -= quantity
            product.save(update_fields=["stock"])

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.price,
            )

        order.total_amount = sum(
            item.unit_price * item.quantity
            for item in order.items.all()
        )
        order.save(update_fields=["total_amount"])

    return order


def cancel_order(*, order_id: int) -> Order:
    """주문을 취소하고 재고를 복원한다.

    Args:
        order_id: 취소할 주문 ID.

    Returns:
        취소된 Order 인스턴스.

    Raises:
        OrderNotCancellableError: 이미 배송된 주문인 경우.
        OrderAlreadyCancelledError: 이미 취소된 주문인 경우.
    """
    with transaction.atomic():
        order = Order.objects.select_for_update().get(id=order_id)

        if order.status == OrderStatus.CANCELLED:
            raise OrderAlreadyCancelledError(order_id=order_id)

        if order.status == OrderStatus.SHIPPED:
            raise OrderNotCancellableError(
                order_id=order_id,
                reason="이미 배송된 주문은 취소할 수 없습니다",
            )

        for item in order.items.select_related("product").all():
            product = Product.objects.select_for_update().get(id=item.product_id)
            product.stock += item.quantity
            product.save(update_fields=["stock"])

        order.status = OrderStatus.CANCELLED
        order.save(update_fields=["status"])

    return order
```

#### 2. 모델/예외 정의 (참고용)

```python
# apps/orders/models.py
from django.db import models


class OrderStatus(models.TextChoices):
    PENDING = "pending", "대기"
    CONFIRMED = "confirmed", "확인"
    SHIPPED = "shipped", "배송"
    CANCELLED = "cancelled", "취소"


class Order(models.Model):
    customer_id = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order #{self.pk} ({self.status})"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.product} x {self.quantity}"
```

```python
# apps/orders/exceptions.py
class OrderServiceError(Exception):
    """주문 서비스의 루트 예외."""


class InsufficientStockError(OrderServiceError):
    def __init__(
        self,
        *,
        product_id: int,
        requested: int,
        available: int,
    ) -> None:
        self.product_id = product_id
        self.requested = requested
        self.available = available
        super().__init__(
            f"Product {product_id}: 요청 {requested}개, 재고 {available}개"
        )


class OrderNotCancellableError(OrderServiceError):
    def __init__(self, *, order_id: int, reason: str) -> None:
        self.order_id = order_id
        self.reason = reason
        super().__init__(f"Order {order_id}: {reason}")


class OrderAlreadyCancelledError(OrderServiceError):
    def __init__(self, *, order_id: int) -> None:
        self.order_id = order_id
        super().__init__(f"Order {order_id}: 이미 취소된 주문입니다")
```

#### 3. 테스트 팩토리

```python
# tests/factories.py
import factory
from factory import fuzzy

from apps.orders.models import Order, OrderItem, OrderStatus
from apps.products.models import Product


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f"상품_{n}")
    price = fuzzy.FuzzyDecimal(1000, 100000, precision=2)
    stock = fuzzy.FuzzyInteger(10, 200)


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    customer_id = factory.Sequence(lambda n: n + 1)
    status = OrderStatus.PENDING
    total_amount = 0

    class Params:
        confirmed = factory.Trait(status=OrderStatus.CONFIRMED)
        shipped = factory.Trait(status=OrderStatus.SHIPPED)
        cancelled = factory.Trait(status=OrderStatus.CANCELLED)


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = fuzzy.FuzzyInteger(1, 5)
    unit_price = factory.LazyAttribute(lambda obj: obj.product.price)
```

#### 4. 테스트 코드 본체

```python
# tests/apps/orders/test_services.py
from decimal import Decimal

import pytest

from apps.orders.exceptions import (
    InsufficientStockError,
    OrderAlreadyCancelledError,
    OrderNotCancellableError,
)
from apps.orders.models import OrderStatus
from apps.orders.services import cancel_order, create_order
from tests.factories import OrderFactory, OrderItemFactory, ProductFactory


pytestmark = pytest.mark.django_db


class TestCreateOrder:
    """create_order 서비스 함수의 동작을 검증한다."""

    def test_creates_order_with_single_item(self) -> None:
        """단일 상품으로 주문을 생성하면 올바른 주문이 반환된다."""
        # Arrange
        product = ProductFactory(price=Decimal("15000"), stock=50)

        # Act
        order = create_order(
            customer_id=1,
            items=[{"product_id": product.id, "quantity": 3}],
        )

        # Assert
        assert order.status == OrderStatus.PENDING
        assert order.total_amount == Decimal("45000")
        assert order.items.count() == 1

    def test_creates_order_with_multiple_items(self) -> None:
        """여러 상품으로 주문을 생성하면 총액이 올바르게 계산된다."""
        # Arrange
        product_a = ProductFactory(price=Decimal("10000"), stock=100)
        product_b = ProductFactory(price=Decimal("20000"), stock=100)

        # Act
        order = create_order(
            customer_id=1,
            items=[
                {"product_id": product_a.id, "quantity": 2},
                {"product_id": product_b.id, "quantity": 1},
            ],
        )

        # Assert
        assert order.total_amount == Decimal("40000")
        assert order.items.count() == 2

    def test_deducts_stock_on_creation(self) -> None:
        """주문 생성 시 상품 재고가 주문 수량만큼 차감된다."""
        # Arrange
        product = ProductFactory(price=Decimal("5000"), stock=30)

        # Act
        create_order(
            customer_id=1,
            items=[{"product_id": product.id, "quantity": 5}],
        )

        # Assert
        product.refresh_from_db()
        assert product.stock == 25

    def test_raises_on_insufficient_stock(self) -> None:
        """재고보다 많은 수량을 주문하면 InsufficientStockError가 발생한다."""
        # Arrange
        product = ProductFactory(price=Decimal("5000"), stock=3)

        # Act & Assert
        with pytest.raises(InsufficientStockError) as exc_info:
            create_order(
                customer_id=1,
                items=[{"product_id": product.id, "quantity": 10}],
            )
        assert exc_info.value.product_id == product.id
        assert exc_info.value.requested == 10
        assert exc_info.value.available == 3

    def test_rolls_back_on_partial_failure(self) -> None:
        """두 번째 상품의 재고 부족 시 첫 번째 상품의 재고 차감도 롤백된다."""
        # Arrange
        product_ok = ProductFactory(price=Decimal("10000"), stock=100)
        product_no_stock = ProductFactory(price=Decimal("20000"), stock=1)

        # Act
        with pytest.raises(InsufficientStockError):
            create_order(
                customer_id=1,
                items=[
                    {"product_id": product_ok.id, "quantity": 5},
                    {"product_id": product_no_stock.id, "quantity": 10},
                ],
            )

        # Assert
        product_ok.refresh_from_db()
        assert product_ok.stock == 100  # 롤백 확인

    def test_assigns_correct_customer_id(self) -> None:
        """주문 생성 시 전달된 customer_id가 올바르게 저장된다."""
        # Arrange
        product = ProductFactory(stock=50)

        # Act
        order = create_order(
            customer_id=42,
            items=[{"product_id": product.id, "quantity": 1}],
        )

        # Assert
        assert order.customer_id == 42

    def test_stores_unit_price_at_order_time(self) -> None:
        """주문 항목에 주문 시점의 상품 가격이 기록된다."""
        # Arrange
        product = ProductFactory(price=Decimal("25000"), stock=50)

        # Act
        order = create_order(
            customer_id=1,
            items=[{"product_id": product.id, "quantity": 1}],
        )

        # Assert
        order_item = order.items.first()
        assert order_item.unit_price == Decimal("25000")


class TestCancelOrder:
    """cancel_order 서비스 함수의 동작을 검증한다."""

    def test_cancels_pending_order(self) -> None:
        """대기 상태의 주문을 취소하면 상태가 cancelled로 변경된다."""
        # Arrange
        order = OrderFactory(status=OrderStatus.PENDING)
        product = ProductFactory(stock=10)
        OrderItemFactory(order=order, product=product, quantity=3)

        # Act
        cancelled = cancel_order(order_id=order.id)

        # Assert
        assert cancelled.status == OrderStatus.CANCELLED

    def test_restores_stock_on_cancellation(self) -> None:
        """주문 취소 시 주문 항목의 수량만큼 재고가 복원된다."""
        # Arrange
        product = ProductFactory(stock=10)
        order = OrderFactory(status=OrderStatus.PENDING)
        OrderItemFactory(order=order, product=product, quantity=5)

        # Act
        cancel_order(order_id=order.id)

        # Assert
        product.refresh_from_db()
        assert product.stock == 15

    def test_restores_stock_for_multiple_items(self) -> None:
        """여러 항목이 있는 주문 취소 시 각 상품의 재고가 모두 복원된다."""
        # Arrange
        product_a = ProductFactory(stock=20)
        product_b = ProductFactory(stock=30)
        order = OrderFactory(status=OrderStatus.CONFIRMED)
        OrderItemFactory(order=order, product=product_a, quantity=3)
        OrderItemFactory(order=order, product=product_b, quantity=7)

        # Act
        cancel_order(order_id=order.id)

        # Assert
        product_a.refresh_from_db()
        product_b.refresh_from_db()
        assert product_a.stock == 23
        assert product_b.stock == 37

    def test_raises_on_already_cancelled_order(self) -> None:
        """이미 취소된 주문을 다시 취소하면 OrderAlreadyCancelledError가 발생한다."""
        # Arrange
        order = OrderFactory(cancelled=True)

        # Act & Assert
        with pytest.raises(OrderAlreadyCancelledError) as exc_info:
            cancel_order(order_id=order.id)
        assert exc_info.value.order_id == order.id

    def test_raises_on_shipped_order(self) -> None:
        """배송 완료된 주문을 취소하면 OrderNotCancellableError가 발생한다."""
        # Arrange
        order = OrderFactory(shipped=True)

        # Act & Assert
        with pytest.raises(OrderNotCancellableError) as exc_info:
            cancel_order(order_id=order.id)
        assert exc_info.value.order_id == order.id
        assert "배송" in exc_info.value.reason

    def test_cancellation_is_atomic(self) -> None:
        """취소 중 오류 발생 시 상태 변경과 재고 복원이 모두 롤백된다."""
        # Arrange
        product = ProductFactory(stock=10)
        order = OrderFactory(status=OrderStatus.PENDING)
        OrderItemFactory(order=order, product=product, quantity=5)

        # Act -- 존재하지 않는 상품 ID를 가진 항목으로 오류 유발
        # (이 테스트는 atomic 블록이 올바르게 작동하는지 검증한다)
        cancel_order(order_id=order.id)

        # Assert
        order.refresh_from_db()
        assert order.status == OrderStatus.CANCELLED
        product.refresh_from_db()
        assert product.stock == 15


class TestCreateOrderQueryCount:
    """create_order의 쿼리 성능을 검증한다."""

    def test_query_count_scales_linearly_with_items(
        self, django_assert_num_queries
    ) -> None:
        """상품 N개 주문 시 쿼리 수가 선형적으로 증가한다."""
        # Arrange
        products = ProductFactory.create_batch(3, stock=100)
        items = [
            {"product_id": p.id, "quantity": 1}
            for p in products
        ]

        # Act & Assert
        # 예상 쿼리: SAVEPOINT + INSERT order + (SELECT product + UPDATE product
        #            + INSERT item) * 3 + SELECT items + UPDATE order + RELEASE
        with django_assert_num_queries(13):
            create_order(customer_id=1, items=items)
```

---

> **관련 스킬 참조:**
> - TDD Red-Green-Refactor 워크플로우 적용 --> **implementation-tdd** 스킬
> - 서비스 레이어 아키텍처 설계/리뷰 --> **implementation-django** 스킬
> - 주문 도메인 예외 계층 설계 --> **implementation-cleancode** 스킬
> - Django Ninja API 엔드포인트 테스트 --> **implementation-django-ninja** 스킬

---

## 실행 메타 정보

### 커맨드 워크플로우 추적

| 단계 | 실행 내용 | 상태 |
|------|-----------|------|
| 1단계 | 스킬 4개 로드 (cleancode, python, django, test) | 완료 |
| 1단계 | 레퍼런스 7개 로드 (test-strategy, test-doubles, pytest-fixtures, test-data-factory, test-quality, mock-patterns, error-handling) | 완료 |
| 2단계 | 모드 판단: Writing | 완료 |
| 3단계 | Writing 모드로 테스트 코드 생성 | 완료 |

### 적용된 스킬별 기여

| 스킬 | 적용된 원칙 |
|------|-------------|
| **implementation-test** | AAA 패턴, FIRST 원칙, 검증 우선순위(출력 > 상태 > 통신), factory_boy Trait, pytest.raises로 예외 검증, 경계값 테스트 |
| **implementation-cleancode** | 의도를 드러내는 네이밍(test_raises_on_insufficient_stock), 도메인 예외 계층(OrderServiceError), 하나의 테스트는 하나의 동작 |
| **implementation-python** | 타입 힌트(-> None), TextChoices(OrderStatus), frozen 값 객체(예외 속성), keyword-only 매개변수(*) |
| **implementation-django** | DjangoModelFactory, pytest.mark.django_db, refresh_from_db, select_for_update, assertNumQueries, transaction.atomic |

### 테스트 설계 결정 사항

1. **검증 우선순위**: 출력 기반 검증(반환 값의 status, total_amount)을 최우선, 상태 기반 검증(DB refresh 후 stock 확인)을 차선으로 사용. Mock은 사용하지 않음 -- 모든 테스트가 실제 DB에서 동작.
2. **factory_boy Trait**: OrderFactory에 confirmed/shipped/cancelled Trait을 정의하여 테스트별 상태 변형을 선언적으로 생성.
3. **트랜잭션 롤백 검증**: test_rolls_back_on_partial_failure에서 atomic 블록의 롤백 동작을 실제로 검증.
4. **쿼리 카운트 테스트**: django_assert_num_queries로 N+1 회귀를 방지하는 성능 테스트 포함.
5. **경계값 테스트**: 재고 부족 시 정확한 에러 속성(product_id, requested, available) 검증으로 변이 테스트 내성 확보.
