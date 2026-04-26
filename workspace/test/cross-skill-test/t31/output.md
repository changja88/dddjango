# T31 (Test 30): TDD 중 pytest fixture와 factory_boy 테스트 데이터 구성

**Skill:** implementation-tdd (Writing mode)
**Cross-skill references loaded:** implementation-test (pytest fixture, factory_boy)

## [주요 내용]

### TDD 사이클에서 테스트 데이터의 역할

Red 단계에서 테스트를 작성할 때, 명확한 테스트 데이터가 테스트 의도를 드러낸다. factory_boy는 복잡한 객체 그래프를 선언적으로 생성하여 Arrange 단계를 간결하게 만든다.

### pytest fixture + factory_boy 통합 (implementation-test 위임)

```python
# conftest.py
import pytest
import factory
from orders.models import Order, Customer

class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer
    name = factory.Faker("name")
    email = factory.Faker("email")

class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order
    customer = factory.SubFactory(CustomerFactory)
    status = "pending"
    total = factory.fuzzy.FuzzyDecimal(10.0, 500.0)

    class Params:
        shipped = factory.Trait(status="shipped")
        cancelled = factory.Trait(status="cancelled", total=0)

@pytest.fixture
def customer():
    return CustomerFactory()

@pytest.fixture
def pending_order(customer):
    return OrderFactory(customer=customer)
```

### TDD Red-Green-Refactor 사이클

```python
# --- Red: 실패하는 테스트 ---
def test_cancel_order_returns_zero_total(pending_order):
    """주문 취소 시 total이 0이 되어야 한다"""
    # Act
    pending_order.cancel()
    # Assert
    assert pending_order.total == 0
    assert pending_order.status == "cancelled"

# --- Green: 최소한의 구현 ---
class Order:
    def cancel(self):
        self.status = "cancelled"
        self.total = 0

# --- Refactor: Trait으로 테스트 데이터 정리 ---
def test_cancelled_order_state():
    order = OrderFactory(cancelled=True)
    assert order.status == "cancelled"
    assert order.total == 0
```

핵심: fixture는 공통 설정, factory는 변형 데이터, parametrize는 단순 반복에 사용한다.

---
> **관련 스킬 참조:**
> - [pytest fixture, factory_boy, parametrize] → **implementation-test** 스킬
> - [Red-Green-Refactor 사이클] → 이 스킬 `references/red-green-refactor.md`
> - [Django TestCase, pytest-django] → **implementation-django** 스킬
