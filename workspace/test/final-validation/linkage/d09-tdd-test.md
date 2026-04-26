# D09: TDD 주문 서비스 - pytest 픽스처와 factory_boy 활용

> **Source Skill:** implementation-tdd (Writing mode)
> **Cross-referenced:** implementation-test (Section 3: pytest 픽스처, Section 8: 테스트 데이터 팩토리)
> **Prompt:** "TDD로 주문 서비스를 개발하고 있어. pytest 픽스처 구성이랑 factory_boy 활용법이 궁금한데?"

---

## 응답

TDD로 주문 서비스를 개발할 때, 픽스처와 팩토리는 Red-Green-Refactor 사이클의 **Arrange 단계**를 깔끔하게 만드는 핵심 도구다. 각 테스트가 독립적인 상태를 가지면서도 설정 코드가 의도를 가리지 않도록 구성한다.

### 1. pytest 픽스처 계층 구성

주문 서비스의 픽스처는 스코프에 따라 계층화한다. 격리가 필요한 도메인 객체는 `function` 스코프, 비용이 큰 인프라 리소스는 `session`/`module` 스코프를 사용한다.

```python
# conftest.py
import pytest


@pytest.fixture
def customer():
    """각 테스트마다 독립적인 고객 객체"""
    return Customer(name="홍길동", email="hong@example.com")


@pytest.fixture
def empty_order(customer):
    """의존성 주입: customer 픽스처를 조합"""
    return Order(customer=customer)


@pytest.fixture
def order_service(fake_payment_gateway, fake_inventory):
    """외부 의존성은 Fake로 주입"""
    return OrderService(
        payment_gateway=fake_payment_gateway,
        inventory=fake_inventory,
    )


@pytest.fixture
def fake_payment_gateway():
    """외부 결제 시스템의 Fake 구현"""
    return FakePaymentGateway(always_approve=True)


@pytest.fixture
def fake_inventory():
    """외부 재고 시스템의 Fake 구현"""
    return FakeInventory(default_stock=100)
```

핵심 원칙:
- `yield`를 사용하여 정리(teardown) 로직을 픽스처 안에 캡슐화한다
- 픽스처 간 조합으로 복잡한 객체 그래프를 구성한다
- 외부 의존성(결제, 재고)은 Mock이 아닌 Fake로 대체하여 리팩터링 내성을 확보한다
- 공유 픽스처는 `conftest.py` 계층에 배치한다

### 2. factory_boy로 테스트 데이터 선언

복잡한 주문 객체 그래프는 factory_boy로 선언적으로 생성한다. 각 테스트에서 필요한 속성만 오버라이드하여 **테스트 의도를 드러낸다**.

```python
# tests/factories.py
import factory
from factory import fuzzy
from datetime import datetime
from myapp.models import Customer, Order, OrderItem, Product


class CustomerFactory(factory.Factory):
    class Meta:
        model = Customer

    name = factory.Faker("name", locale="ko_KR")
    email = factory.Sequence(lambda n: f"customer_{n}@example.com")
    grade = "NORMAL"

    class Params:
        vip = factory.Trait(
            grade="VIP",
            name=factory.LazyAttribute(lambda o: f"VIP_{o.name}"),
        )


class ProductFactory(factory.Factory):
    class Meta:
        model = Product

    name = factory.Faker("word")
    price = fuzzy.FuzzyDecimal(1000, 50000, precision=0)
    stock = 100


class OrderItemFactory(factory.Factory):
    class Meta:
        model = OrderItem

    product = factory.SubFactory(ProductFactory)
    quantity = fuzzy.FuzzyInteger(1, 5)
    unit_price = factory.LazyAttribute(lambda o: o.product.price)


class OrderFactory(factory.Factory):
    class Meta:
        model = Order

    customer = factory.SubFactory(CustomerFactory)
    status = "pending"
    created_at = factory.LazyFunction(datetime.now)

    class Params:
        paid = factory.Trait(
            status="paid",
            paid_at=factory.LazyFunction(datetime.now),
        )
        shipped = factory.Trait(
            status="shipped",
            shipped_at=factory.LazyFunction(datetime.now),
            paid_at=factory.LazyFunction(datetime.now),
        )
        cancelled = factory.Trait(
            status="cancelled",
        )
```

### 3. TDD 사이클에서 픽스처와 팩토리 결합

Red-Green-Refactor 사이클 안에서 픽스처와 팩토리를 결합하여 사용한다. 픽스처가 팩토리를 감싸면 테스트 함수의 시그니처만으로 설정 의도가 전달된다.

```python
# conftest.py -- 팩토리를 픽스처로 감싸기
@pytest.fixture
def order_with_items():
    """주문 항목이 포함된 주문"""
    order = OrderFactory()
    items = OrderItemFactory.create_batch(3, order=order)
    order.items = items
    return order


@pytest.fixture
def vip_customer_order():
    """VIP 고객의 주문 -- Trait 활용"""
    return OrderFactory(customer=CustomerFactory(vip=True))
```

```python
# test_order_service.py -- TDD Red 단계
class TestOrderTotal:
    """주문 총액 계산"""

    def test_calculate_total__single_item__returns_unit_price_times_quantity(
        self, order_service
    ):
        order = OrderFactory()
        item = OrderItemFactory(unit_price=10000, quantity=3)
        order.items = [item]

        total = order_service.calculate_total(order)

        assert total == 10000 * 3

    def test_calculate_total__multiple_items__returns_sum_of_all(
        self, order_service
    ):
        order = OrderFactory()
        order.items = [
            OrderItemFactory(unit_price=10000, quantity=2),
            OrderItemFactory(unit_price=5000, quantity=1),
        ]

        total = order_service.calculate_total(order)

        assert total == 10000 * 2 + 5000 * 1

    def test_calculate_total__empty_order__returns_zero(self, order_service):
        order = OrderFactory()
        order.items = []

        total = order_service.calculate_total(order)

        assert total == 0


class TestOrderDiscount:
    """VIP 할인 정책"""

    def test_apply_discount__vip_customer__applies_10_percent(
        self, order_service
    ):
        order = OrderFactory(customer=CustomerFactory(vip=True))
        order.items = [OrderItemFactory(unit_price=10000, quantity=1)]

        discounted = order_service.apply_discount(order)

        assert discounted == 10000 * (1 - 0.10)

    def test_apply_discount__normal_customer__no_discount(
        self, order_service
    ):
        order = OrderFactory(customer=CustomerFactory(grade="NORMAL"))
        order.items = [OrderItemFactory(unit_price=10000, quantity=1)]

        discounted = order_service.apply_discount(order)

        assert discounted == 10000
```

핵심 포인트:
- **팩토리 기본값은 테스트와 무관한 필드를 채운다** -- 테스트에서는 관심 있는 속성만 오버라이드한다
- **Trait으로 객체 변형을 표현한다** -- `paid=True`, `vip=True`로 상태 전환을 선언적으로 표현한다
- **SubFactory로 관계를 자동 구성한다** -- 객체 그래프를 수동으로 조립하지 않는다
- **명백한 데이터** -- `10000 * 3`처럼 계산 과정이 드러나는 assert를 작성한다
- **테스트 격리** -- 각 테스트가 팩토리로 독립적인 객체를 생성하므로 공유 상태가 없다

---
> **관련 스킬 참조:**
> - pytest 픽스처 스코프, conftest 계층, parametrize 심화 -> **implementation-test** 스킬
> - Red-Green-Refactor 사이클, 테스트 선택 전략, 그린 바 패턴 -> **implementation-tdd** 스킬
> - Django ORM 통합 테스트, pytest-django 설정 -> **implementation-django** 스킬
> - 도메인 모델 설계 (Value Object, Entity) -> **implementation-cleancode** 스킬
