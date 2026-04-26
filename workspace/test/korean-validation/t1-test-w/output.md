# Django 모델 비즈니스 로직 테스트: TestCase 선택과 assertNumQueries

## TestCase 선택 기준

Django는 네 가지 TestCase 클래스를 제공하며, 테스트 시나리오에 따라 올바른 클래스를 선택해야 한다.

| 클래스 | 특징 | 사용 시나리오 |
|--------|------|-------------|
| `SimpleTestCase` | DB 접근 불가, 가장 빠름 | 유틸리티 함수, 폼 검증, 순수 비즈니스 로직 |
| `TestCase` | 트랜잭션 롤백으로 격리, 빠름 | **대부분의 모델 비즈니스 로직 테스트** |
| `TransactionTestCase` | 실제 트랜잭션 커밋, 느림 | `select_for_update()`, DB 트리거, 시그널 테스트 |
| `LiveServerTestCase` | 실제 서버 실행 | Selenium 통합 테스트 |

모델 비즈니스 로직을 테스트할 때는 **`TestCase`가 기본 선택**이다. `TestCase`는 각 테스트를 트랜잭션으로 감싸고 끝나면 롤백하므로, 테스트 간 DB 상태가 격리되면서도 실제 `TRUNCATE`보다 빠르다.

```python
from django.test import TestCase
from django.utils import timezone


class OrderModelTest(TestCase):
    """Order 모델의 비즈니스 로직을 검증한다."""

    def setUp(self):
        self.user = UserFactory()

    def test_confirm_applies_discount_for_high_value_order(self):
        """100 초과 주문에 10% 할인을 적용한다."""
        # Arrange
        order = OrderFactory(user=self.user, total=Decimal("200.00"))

        # Act
        order.confirm()

        # Assert
        order.refresh_from_db()
        self.assertEqual(order.discount, Decimal("20.00"))
        self.assertEqual(order.status, Order.Status.CONFIRMED)

    def test_confirm_no_discount_for_low_value_order(self):
        """100 이하 주문에는 할인을 적용하지 않는다."""
        order = OrderFactory(user=self.user, total=Decimal("50.00"))

        order.confirm()

        order.refresh_from_db()
        self.assertEqual(order.discount, Decimal("0"))
        self.assertEqual(order.status, Order.Status.CONFIRMED)
```

### pytest-django를 사용하는 경우

pytest 스타일에서는 `@pytest.mark.django_db`로 DB 접근을 명시한다. 이 마커는 내부적으로 `TestCase`와 동일한 트랜잭션 롤백 방식을 사용한다. 실제 트랜잭션 커밋이 필요하면 `transaction=True` 옵션을 추가한다.

```python
import pytest
from decimal import Decimal


@pytest.mark.django_db
class TestOrderModel:
    """Order 모델의 비즈니스 로직을 검증한다."""

    def test_confirm_applies_discount_for_high_value_order(self):
        """100 초과 주문에 10% 할인을 적용한다."""
        order = OrderFactory(total=Decimal("200.00"))

        order.confirm()

        order.refresh_from_db()
        assert order.discount == Decimal("20.00")
        assert order.status == Order.Status.CONFIRMED

    def test_confirm_no_discount_for_low_value_order(self):
        """100 이하 주문에는 할인을 적용하지 않는다."""
        order = OrderFactory(total=Decimal("50.00"))

        order.confirm()

        order.refresh_from_db()
        assert order.discount == Decimal("0")
        assert order.status == Order.Status.CONFIRMED


@pytest.mark.django_db(transaction=True)
def test_concurrent_stock_update():
    """select_for_update가 동시 재고 차감을 안전하게 처리한다."""
    product = ProductFactory(stock=10)
    product.deduct_stock(3)
    product.refresh_from_db()
    assert product.stock == 7
```

### TestCase 선택 판단 흐름

1. DB 접근이 필요 없는가? -- `SimpleTestCase`
2. DB 접근이 필요하지만 트랜잭션 커밋 동작은 불필요한가? -- `TestCase` (기본)
3. `select_for_update()`, DB 트리거, `on_commit()` 콜백을 테스트하는가? -- `TransactionTestCase`
4. 브라우저 기반 E2E 테스트인가? -- `LiveServerTestCase`

---

## assertNumQueries 사용법

`assertNumQueries`는 특정 코드 블록이 실행하는 SQL 쿼리 수를 검증하는 컨텍스트 매니저다. N+1 문제 같은 쿼리 수 회귀를 테스트 레벨에서 방지한다.

### 기본 사용법

```python
from django.test import TestCase


class ArticleQueryTest(TestCase):
    def test_article_list_avoids_n_plus_one(self):
        """select_related로 N+1 없이 목록을 조회한다."""
        # Arrange
        ArticleFactory.create_batch(50)

        # Act & Assert
        with self.assertNumQueries(1):
            articles = list(
                Article.objects.select_related("author").all()
            )

        self.assertEqual(len(articles), 50)
```

### pytest-django에서 사용

pytest-django에서는 `django_assert_num_queries` 픽스처를 사용한다.

```python
import pytest


@pytest.mark.django_db
def test_article_list_query_count(django_assert_num_queries):
    """목록 조회가 2개 쿼리 이내인지 검증한다."""
    ArticleFactory.create_batch(30, published=True)

    with django_assert_num_queries(2):
        articles = list(
            Article.objects.select_related("author")
            .prefetch_related("tags")
            .published()
        )

    assert len(articles) == 30
```

### 실전 패턴: 모델 메서드의 쿼리 수 검증

모델 비즈니스 로직이 내부적으로 실행하는 쿼리 수를 고정하여, 이후 코드 변경으로 인한 쿼리 증가를 방지한다.

```python
class OrderModelTest(TestCase):
    def test_confirm_executes_expected_queries(self):
        """confirm()은 정확히 1번의 UPDATE를 실행한다."""
        order = OrderFactory()

        with self.assertNumQueries(1):
            order.confirm()
            # confirm() 내부: self.save(update_fields=["discount", "status"])

    def test_get_order_summary_with_items(self):
        """주문 요약 조회 시 쿼리가 2개를 넘지 않는다."""
        order = OrderFactory()
        OrderItemFactory.create_batch(10, order=order)

        with self.assertNumQueries(2):
            # 1: SELECT order, 2: SELECT order_items (prefetch)
            summary = Order.objects.prefetch_related("items").get(pk=order.pk)
            list(summary.items.all())
```

### assertNumQueries가 실패할 때 디버깅

`assertNumQueries`가 기대와 다른 쿼리 수를 보고하면, 실행된 쿼리를 확인하여 원인을 파악한다.

```python
from django.test.utils import CaptureQueriesContext
from django.db import connection


class DebugQueryTest(TestCase):
    def test_debug_unexpected_queries(self):
        """실행된 쿼리를 캡처하여 문제를 진단한다."""
        order = OrderFactory()
        OrderItemFactory.create_batch(5, order=order)

        with CaptureQueriesContext(connection) as ctx:
            summary = order.get_summary()

        # 각 쿼리의 SQL을 출력하여 확인
        for i, query in enumerate(ctx.captured_queries):
            print(f"Query {i + 1}: {query['sql']}")

        # 기대 쿼리 수를 확인한 후 assertNumQueries로 고정
        self.assertEqual(len(ctx.captured_queries), 2)
```

---

## Factory Boy를 활용한 테스트 데이터 설정

모델 비즈니스 로직 테스트에서 `factory_boy`를 사용하면 설정 코드를 줄이고 테스트 의도를 명확하게 한다.

```python
import factory
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    total = factory.fuzzy.FuzzyDecimal(10.0, 500.0)
    status = Order.Status.PENDING
    discount = Decimal("0")

    class Params:
        confirmed = factory.Trait(
            status=Order.Status.CONFIRMED,
            discount=factory.LazyAttribute(
                lambda obj: obj.total * Decimal("0.1") if obj.total > 100 else Decimal("0")
            ),
        )


class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = factory.fuzzy.FuzzyInteger(1, 5)
```

`Trait`로 특정 상태의 객체를 간결하게 생성하고, `SubFactory`로 관련 객체를 자동 생성한다. 테스트에서는 검증 대상과 직접 관련된 속성만 명시적으로 전달한다.

---

## 검증 우선순위 적용

모델 비즈니스 로직 테스트에서는 검증 우선순위를 따른다.

1. **출력 기반** (반환 값) -- 메서드가 값을 반환하면 이것을 먼저 검증한다.
2. **상태 기반** (객체 상태) -- `refresh_from_db()` 후 모델 필드를 검증한다.
3. **통신 기반** (Mock) -- 이메일 발송, 외부 API 호출 같은 외부 의존성만 Mock한다.

```python
class OrderModelTest(TestCase):
    def test_confirm_sends_email(self):
        """confirm()이 확인 이메일을 발송한다."""
        order = OrderFactory()

        with patch.object(order, "send_confirmation_email") as mock_email:
            order.confirm()

        # 상태 기반: 모델 상태를 먼저 검증
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.CONFIRMED)

        # 통신 기반: 외부 의존성(이메일) 호출을 검증
        mock_email.assert_called_once()
```

핵심 비즈니스 로직(`confirm()`의 할인 계산, 상태 변경)은 실제 객체로 테스트하고, 외부 의존성(`send_confirmation_email`)만 Mock한다.

---

Django 테스트의 전체적인 패턴과 모델 설계에 대한 자세한 가이드는 **implementation-django** 스킬을 참조하세요.
테스트 데이터 팩토리(factory_boy)의 고급 패턴에 대한 자세한 가이드는 **implementation-test** 스킬의 테스트 데이터 팩토리 섹션을 참조하세요.
TDD 방법론(Red-Green-Refactor)에 대한 자세한 가이드는 **implementation-tdd** 스킬을 참조하세요.
