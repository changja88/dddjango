# C03: Django 서비스 레이어에 TDD를 적용하면서 pytest fixture와 TestCase를 활용하려면?

**Skill:** implementation-tdd (Writing mode)
**Cross-skill references loaded:** implementation-test (pytest fixture), implementation-django (TestCase, 서비스 레이어)

## [주요 내용]

### TDD 사이클으로 서비스 레이어 개발

**테스트 목록 (Red Bar 패턴):**
1. 빈 주문 항목으로 주문 생성 시 실패
2. 단일 항목으로 주문 생성 성공
3. 여러 항목으로 주문 생성 시 총합 계산
4. 재고 부족 시 주문 실패

### conftest.py: pytest fixture + factory_boy (implementation-test 위임)

```python
# tests/conftest.py
import pytest
from tests.factories import CustomerFactory, ProductFactory

@pytest.fixture
def customer(db):
    return CustomerFactory()

@pytest.fixture
def product(db):
    return ProductFactory(price=1000, stock=10)
```

### Red: 실패하는 테스트 (Django TestCase와 pytest 혼합)

```python
# tests/orders/test_services.py
import pytest
from orders.services import order_create

@pytest.mark.django_db
def test_order_create_with_empty_items_fails():
    """빈 항목 목록으로 주문 생성 시 ValueError 발생"""
    with pytest.raises(ValueError, match="최소 한 개"):
        order_create(orderer_id=1, items=[])

@pytest.mark.django_db
def test_order_create_single_item(customer, product):
    """단일 항목 주문 생성 시 총합이 정확해야 한다"""
    order = order_create(
        orderer_id=customer.id,
        items=[{"product_id": product.id, "quantity": 2}],
    )
    assert order.total == 2000
    assert order.lines.count() == 1
```

### Green: 최소한의 서비스 구현

```python
# orders/services.py
from django.db import transaction

def order_create(*, orderer_id: int, items: list[dict]) -> Order:
    if not items:
        raise ValueError("최소 한 개 이상의 항목이 필요합니다")
    with transaction.atomic():
        order = Order.objects.create(orderer_id=orderer_id)
        total = 0
        for item in items:
            product = Product.objects.get(id=item["product_id"])
            line = OrderLine.objects.create(
                order=order, product=product, quantity=item["quantity"],
            )
            total += product.price * item["quantity"]
        order.total = total
        order.save(update_fields=["total"])
        return order
```

### assertNumQueries로 쿼리 성능 검증 (implementation-django 위임)

```python
@pytest.mark.django_db
def test_order_create_query_count(customer, product):
    """주문 생성이 예상 쿼리 수 이내여야 한다"""
    from django.test.utils import CaptureQueriesContext
    from django.db import connection

    with CaptureQueriesContext(connection) as ctx:
        order_create(orderer_id=customer.id, items=[{"product_id": product.id, "quantity": 1}])

    assert len(ctx) <= 5  # SELECT product + INSERT order + INSERT line + UPDATE order + SAVEPOINT
```

---
> **관련 스킬 참조:**
> - [pytest fixture, factory_boy] → **implementation-test** 스킬
> - [Django TestCase, assertNumQueries] → **implementation-django** 스킬
> - [Red-Green-Refactor 사이클] → 이 스킬 `references/red-green-refactor.md`
