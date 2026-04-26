# T37 (Test 36): Django TestCase 선택 기준과 assertNumQueries 사용법

**Skill:** implementation-test (Writing mode)
**Cross-skill references loaded:** implementation-django (TestCase, assertNumQueries, QuerySet 최적화)

## [주요 내용]

### TestCase 클래스 선택 기준 (implementation-django 위임)

| 클래스 | 용도 | DB 사용 | 트랜잭션 |
|--------|------|---------|----------|
| `SimpleTestCase` | DB 불필요한 순수 로직 | X | X |
| `TestCase` | 대부분의 테스트 (기본) | O | 각 테스트를 트랜잭션으로 래핑 |
| `TransactionTestCase` | 트랜잭션 동작 테스트 | O | 실제 커밋/롤백 |
| `LiveServerTestCase` | E2E (Selenium 등) | O | 별도 서버 스레드 |

### assertNumQueries로 N+1 회귀 방지

```python
from django.test import TestCase
from orders.models import Order

class OrderQueryTest(TestCase):
    def setUp(self):
        customer = CustomerFactory()
        OrderFactory.create_batch(5, customer=customer)

    def test_list_orders_with_select_related(self):
        """select_related로 N+1 없이 1개 쿼리만 실행해야 한다"""
        with self.assertNumQueries(1):
            orders = list(
                Order.objects
                .select_related("customer")
                .all()
            )
            # 추가 쿼리 없이 customer 접근 가능
            for order in orders:
                _ = order.customer.name

    def test_list_orders_without_select_related_causes_n_plus_1(self):
        """select_related 없으면 6개 쿼리 (1 + N)가 실행된다"""
        with self.assertNumQueries(6):  # 1 (orders) + 5 (customer each)
            orders = list(Order.objects.all())
            for order in orders:
                _ = order.customer.name
```

### pytest-django와 함께 사용

```python
import pytest
from django.test.utils import CaptureQueriesContext
from django.db import connection

@pytest.mark.django_db
def test_optimized_query_count():
    """pytest-django에서 쿼리 수 검증"""
    CustomerFactory()
    OrderFactory.create_batch(3)

    with CaptureQueriesContext(connection) as ctx:
        list(Order.objects.select_related("customer").all())

    assert len(ctx) == 1
```

핵심: 성능 크리티컬 경로에서 `assertNumQueries`를 사용하여 쿼리 회귀를 자동으로 잡는다.

---
> **관련 스킬 참조:**
> - [Django TestCase, QuerySet 최적화] → **implementation-django** 스킬
> - [factory_boy로 테스트 데이터 생성] → 이 스킬 `references/test-data-factory.md`
> - [TDD에서 테스트 품질 기둥] → **implementation-tdd** 스킬
