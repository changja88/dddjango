# pytest-django TestCase 선택 기준과 assertNumQueries 사용법

## 1. TestCase 선택 기준

pytest-django(및 Django 자체)는 세 가지 테스트 베이스 클래스를 제공한다. 각각 DB 처리 방식이 다르므로 테스트 목적에 맞게 선택해야 한다.

### 1-1. SimpleTestCase

```python
from django.test import SimpleTestCase

class TestPriceCalculation(SimpleTestCase):
    """DB를 전혀 사용하지 않는 순수 비즈니스 로직 테스트"""

    def test_discount_rate(self):
        # 모델 인스턴스를 직접 생성(save 호출 없이)하여 메서드만 검증
        product = Product(price=10000, discount_percent=20)
        assert product.discounted_price == 8000
```

| 특징 | 설명 |
|------|------|
| DB 접근 | 불가 (시도 시 에러) |
| 속도 | 가장 빠름 |
| 사용 시점 | 모델 메서드, 프로퍼티, 유틸 함수 등 DB 없이 검증 가능한 로직 |

### 1-2. TransactionTestCase

```python
from django.test import TransactionTestCase

class TestOrderWorkflow(TransactionTestCase):
    """트랜잭션 커밋/롤백 동작을 실제로 검증해야 할 때"""

    def test_atomic_order_creation(self):
        with self.assertRaises(IntegrityError):
            Order.objects.create(user=None)  # FK 제약 위반
        # 롤백 후 테이블이 비어있는지 확인
        assert Order.objects.count() == 0
```

| 특징 | 설명 |
|------|------|
| DB 접근 | 가능 |
| 정리 방식 | 테스트마다 TRUNCATE (실제 커밋 발생) |
| 속도 | 느림 |
| 사용 시점 | `transaction.atomic`, `on_commit`, `select_for_update` 등 트랜잭션 동작 자체를 테스트 |

### 1-3. TestCase

```python
from django.test import TestCase

class TestOrderModel(TestCase):
    """DB를 사용하는 일반적인 비즈니스 로직 테스트 (가장 많이 사용)"""

    @classmethod
    def setUpTestData(cls):
        # 클래스 단위로 한 번만 생성 -> 테스트 간 공유 (읽기 전용 권장)
        cls.user = User.objects.create_user(username="tester", password="pass")

    def test_create_order(self):
        order = Order.objects.create(user=self.user, total=50000)
        assert order.status == "pending"
```

| 특징 | 설명 |
|------|------|
| DB 접근 | 가능 |
| 정리 방식 | 테스트마다 ROLLBACK (커밋하지 않음) |
| 속도 | TransactionTestCase보다 훨씬 빠름 |
| 사용 시점 | DB CRUD가 필요한 대부분의 비즈니스 로직 테스트 |

### 선택 흐름 요약

```
DB 접근이 필요한가?
├── 아니오 -> SimpleTestCase
└── 예
    ├── 트랜잭션 커밋/롤백 자체를 테스트하는가?
    │   └── 예 -> TransactionTestCase
    └── 아니오 -> TestCase  (기본 선택)
```

---

## 2. pytest-django에서의 사용 (함수 기반)

pytest-django를 쓸 때는 클래스 없이 함수 기반 테스트를 작성하는 경우가 많다. 이때 DB 접근은 fixture/marker로 제어한다.

```python
import pytest

# --- DB 접근 불가 (SimpleTestCase와 동일) ---
def test_discount_calculation():
    product = Product(price=10000, discount_percent=20)
    assert product.discounted_price == 8000


# --- DB 접근 허용 (TestCase와 동일, 테스트마다 롤백) ---
@pytest.mark.django_db
def test_order_creation(user_factory):
    user = user_factory()
    order = Order.objects.create(user=user, total=50000)
    assert order.status == "pending"


# --- 실제 트랜잭션 사용 (TransactionTestCase와 동일) ---
@pytest.mark.django_db(transaction=True)
def test_atomic_block():
    with pytest.raises(IntegrityError):
        Order.objects.create(user=None)
    assert Order.objects.count() == 0
```

---

## 3. assertNumQueries 사용법

`assertNumQueries`는 특정 코드 블록이 정확히 N개의 SQL 쿼리를 실행하는지 검증한다. 비즈니스 로직이 의도치 않게 N+1 문제를 일으키거나, 불필요한 쿼리를 발생시키는 것을 방지하는 데 핵심적이다.

### 3-1. Django TestCase에서 사용

```python
from django.test import TestCase

class TestOrderQueries(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="tester")
        cls.category = Category.objects.create(name="Electronics")
        for i in range(5):
            Product.objects.create(name=f"Product {i}", category=cls.category)

    def test_list_products_query_count(self):
        """상품 목록 조회가 정확히 2개 쿼리로 완료되는지 검증"""
        # 1) Category 조회, 2) Product 조회 (select_related 사용 가정)
        with self.assertNumQueries(2):
            products = list(
                Product.objects.select_related("category").all()
            )
            # context manager 안에서 쿼리를 발생시키는 코드를 모두 실행해야 함
            for p in products:
                _ = p.category.name  # select_related 덕분에 추가 쿼리 없음
```

### 3-2. pytest-django에서 사용 (django_assert_num_queries fixture)

```python
import pytest

@pytest.mark.django_db
def test_list_products_query_count(django_assert_num_queries):
    """pytest-django가 제공하는 fixture 사용"""
    category = Category.objects.create(name="Electronics")
    for i in range(5):
        Product.objects.create(name=f"Product {i}", category=category)

    with django_assert_num_queries(2):
        products = list(
            Product.objects.select_related("category").all()
        )
        for p in products:
            _ = p.category.name
```

### 3-3. N+1 문제 검출 실전 예시

```python
class TestN1Detection(TestCase):

    @classmethod
    def setUpTestData(cls):
        author = Author.objects.create(name="Author")
        for i in range(10):
            Book.objects.create(title=f"Book {i}", author=author)

    def test_n_plus_1_without_prefetch(self):
        """prefetch 없이 접근하면 1 + N 쿼리 발생"""
        # 1(Book 목록) + 10(각 Book의 author 접근) = 11
        with self.assertNumQueries(11):
            books = list(Book.objects.all())
            for book in books:
                _ = book.author.name

    def test_optimized_with_select_related(self):
        """select_related 적용 후 1개 쿼리로 해결"""
        with self.assertNumQueries(1):
            books = list(Book.objects.select_related("author").all())
            for book in books:
                _ = book.author.name

    def test_optimized_with_prefetch_related(self):
        """역참조(M2M, FK reverse)에는 prefetch_related -> 2개 쿼리"""
        with self.assertNumQueries(2):
            authors = list(
                Author.objects.prefetch_related("books").all()
            )
            for author in authors:
                _ = list(author.books.all())
```

### 3-4. django_assert_max_num_queries (상한선 검증)

정확한 쿼리 수보다 "최대 N개 이하"를 보장하고 싶을 때 사용한다.

```python
@pytest.mark.django_db
def test_dashboard_max_queries(django_assert_max_num_queries):
    """대시보드 로딩이 10개 쿼리를 넘지 않는지 검증"""
    setup_dashboard_data()

    with django_assert_max_num_queries(10):
        response = call_dashboard_view()
        assert response.status_code == 200
```

---

## 4. 실전 팁 정리

### 4-1. setUpTestData vs setUp

```python
class TestExample(TestCase):

    @classmethod
    def setUpTestData(cls):
        # 클래스 전체에서 한 번만 실행. 읽기 전용 데이터에 적합.
        # 트랜잭션 롤백 대상이 아니므로 수정하면 다른 테스트에 영향.
        cls.shared_user = User.objects.create_user(username="shared")

    def setUp(self):
        # 매 테스트 메서드 실행 전마다 호출. 각 테스트가 수정할 데이터에 적합.
        self.order = Order.objects.create(user=self.shared_user, total=1000)
```

### 4-2. assertNumQueries 디버깅

쿼리 수가 예상과 다를 때 실제 발생한 SQL을 확인하는 방법:

```python
from django.test.utils import CaptureQueriesContext
from django.db import connection

def test_debug_queries(self):
    with CaptureQueriesContext(connection) as ctx:
        # 테스트 대상 코드 실행
        list(Product.objects.select_related("category").all())

    # 실제 실행된 쿼리 출력
    for i, query in enumerate(ctx.captured_queries):
        print(f"Query {i+1}: {query['sql']}")
        print(f"  Time: {query['time']}s")

    assert len(ctx.captured_queries) == 2
```

### 4-3. Factory Boy와 조합

```python
import factory
from django.test import TestCase

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Sequence(lambda n: f"user_{n}")

class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order
    user = factory.SubFactory(UserFactory)
    total = 10000

class TestOrderBusinessLogic(TestCase):

    def test_bulk_discount(self):
        """대량 주문 시 할인 적용 로직 + 쿼리 수 검증"""
        user = UserFactory()
        orders = OrderFactory.create_batch(5, user=user)

        with self.assertNumQueries(1):
            # 한 번의 쿼리로 해당 유저의 총 주문 금액 집계
            total = Order.objects.filter(user=user).aggregate(
                sum=Sum("total")
            )["sum"]

        assert total == 50000
```
