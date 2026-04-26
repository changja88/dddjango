# TDD Red-Green-Refactor 사이클에서 pytest fixture와 factory_boy로 테스트 데이터 구성하기

TDD에서 테스트 데이터 구성은 **Arrange 단계의 핵심**이다. Red 단계에서 실패하는 테스트를 작성할 때 데이터를 어떻게 준비하느냐가 테스트의 유지보수성과 가독성을 결정한다. pytest fixture로 테스트 격리와 공유 설정을 관리하고, factory_boy로 복잡한 객체 그래프를 선언적으로 생성한다.

---

## 1. pytest fixture: 테스트 격리의 기본 단위

TDD에서 각 테스트는 서로 독립적이어야 한다. 공유 가변 상태는 Erratic Test(불안정 테스트)의 근본 원인이다. fixture는 각 테스트에 독립적인 상태를 주입하여 이 문제를 해결한다.

### 기본 fixture 패턴

```python
import pytest


@pytest.fixture
def empty_cart():
    """각 테스트마다 새로운 장바구니를 생성한다."""
    return ShoppingCart()


def test_empty_cart_total(empty_cart):
    assert empty_cart.total() == 0


def test_add_item_to_cart(empty_cart):
    empty_cart.add(Item("사과", price=1000))
    assert empty_cart.total() == 1000
```

각 테스트 함수가 호출될 때마다 `empty_cart` fixture는 새로운 `ShoppingCart` 인스턴스를 생성한다. 테스트 간 상태가 공유되지 않는다.

### yield를 사용한 설정/정리(teardown)

외부 리소스가 관여할 때는 `yield`로 정리 로직을 보장한다.

```python
@pytest.fixture
def db_connection():
    """테스트 전 DB 연결, 테스트 후 해제."""
    conn = create_test_database()
    conn.connect()
    yield conn
    conn.disconnect()
```

### 스코프 선택 기준

| 스코프 | 용도 | TDD에서의 역할 |
|--------|------|----------------|
| `function` (기본값) | 테스트별 격리 | Red-Green-Refactor 각 사이클의 독립성 보장 |
| `module` | 비용이 큰 리소스 공유 | DB 서버처럼 초기화가 느린 리소스 |
| `session` | 전체 테스트 세션에서 한 번 | 앱 인스턴스, 컨테이너 기동 |

```python
@pytest.fixture(scope="module")
def database_server():
    """모듈당 한 번만 실행 -- 비싼 자원 초기화."""
    server = start_database_server()
    yield server
    server.shutdown()


@pytest.fixture
def db_session(database_server):
    """각 테스트마다 새 세션 -- 격리 보장."""
    session = database_server.new_session()
    yield session
    session.rollback()
    session.close()
```

### conftest.py로 fixture 공유

여러 테스트 모듈에서 공통으로 사용하는 fixture는 `conftest.py`에 정의한다.

```python
# tests/conftest.py
import pytest


@pytest.fixture(scope="session")
def app():
    """세션 전체에서 공유되는 앱 인스턴스."""
    app = create_app(testing=True)
    yield app


@pytest.fixture
def client(app):
    """각 테스트마다 새로운 테스트 클라이언트."""
    return app.test_client()
```

---

## 2. factory_boy: 복잡한 테스트 데이터의 선언적 생성

TDD에서 테스트 데이터는 **의미가 있어야** 한다. 데이터 간 차이가 있다면 그 차이에 의미가 담겨야 하고, 테스트를 읽을 때 쉽고 따라가기 좋아야 한다. factory_boy는 이를 선언적으로 달성한다.

### 기본 팩토리 정의

```python
import factory
from factory import fuzzy
from myapp.models import User, Post


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.LazyAttribute(
        lambda obj: f"{obj.first_name.lower()}.{obj.last_name.lower()}@example.com"
    )
    age = fuzzy.FuzzyInteger(18, 80)
```

주요 필드 유형의 역할:

| 필드 유형 | 용도 |
|-----------|------|
| `Sequence` | 고유한 값 생성 (`user_0`, `user_1`, ...) |
| `Faker` | 현실적인 무작위 데이터 |
| `LazyAttribute` | 다른 필드에 의존하는 계산된 값 |
| `FuzzyInteger` | 범위 내 무작위 정수 |
| `LazyFunction` | 호출 시점에 평가되는 함수 |

### 관계 처리: SubFactory

객체 그래프가 복잡해질 때 `SubFactory`로 연관 객체를 자동 생성한다.

```python
class PostFactory(factory.Factory):
    class Meta:
        model = Post

    title = factory.Faker("sentence", nb_words=6)
    content = factory.Faker("paragraph", nb_sentences=5)
    author = factory.SubFactory(UserFactory)


def test_post_has_author():
    post = PostFactory()
    assert post.author is not None
    assert post.author.username.startswith("user_")
```

특정 값을 오버라이드할 때는 생성 시점에 지정한다.

```python
def test_post_by_specific_author():
    admin = UserFactory(username="admin")
    post = PostFactory(author=admin)
    assert post.author.username == "admin"
```

### Trait: 상태별 변형 객체

TDD에서 다양한 상태를 테스트할 때, Trait으로 객체의 변형을 선언적으로 정의한다.

```python
class OrderFactory(factory.Factory):
    class Meta:
        model = Order

    status = "pending"
    total_amount = fuzzy.FuzzyDecimal(10.0, 500.0)
    shipped_at = None
    paid_at = None

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
            total_amount=0,
        )
```

각 상태별 테스트가 명확해진다.

```python
def test_pending_order_has_no_payment():
    order = OrderFactory()
    assert order.status == "pending"
    assert order.paid_at is None


def test_paid_order_has_payment_timestamp():
    order = OrderFactory(paid=True)
    assert order.status == "paid"
    assert order.paid_at is not None


def test_cancelled_order_has_zero_total():
    order = OrderFactory(cancelled=True)
    assert order.total_amount == 0
```

### 배치 생성

여러 객체가 필요한 시나리오에서는 `create_batch`를 사용한다.

```python
def test_user_list_pagination():
    users = UserFactory.create_batch(25)
    page = paginate(users, page=1, per_page=10)
    assert len(page.items) == 10
    assert page.total == 25
```

---

## 3. TDD 사이클에서의 실전 적용

Red-Green-Refactor 사이클에서 fixture와 factory_boy가 어떻게 결합되는지 할인 계산 서비스를 예로 본다.

### Red: 실패하는 테스트 작성

Assert First 사고법으로 목적부터 정한다. "골드 회원이 3년 이상이면 15% 할인"을 검증하고 싶다.

```python
# tests/conftest.py
import pytest


@pytest.fixture
def discount_service():
    return DiscountService()
```

```python
# tests/factories.py
import factory


class UserFactory(factory.Factory):
    class Meta:
        model = User

    membership = "standard"
    joined_years_ago = 0

    class Params:
        gold_veteran = factory.Trait(
            membership="gold",
            joined_years_ago=3,
        )


class ProductFactory(factory.Factory):
    class Meta:
        model = Product

    price = factory.fuzzy.FuzzyDecimal(10.0, 1000.0)
    category = "general"
```

```python
# tests/test_discount.py
def test_gold_veteran_gets_fifteen_percent_discount(discount_service):
    # --- Arrange ---
    user = UserFactory(gold_veteran=True)
    product = ProductFactory(price=100.00, category="electronics")

    # --- Act ---
    discount = discount_service.calculate(user, product)

    # --- Assert ---
    assert discount.percentage == 15.0
    assert discount.final_price == 85.00
```

이 테스트는 `DiscountService`, `User`, `Product` 등이 아직 없으므로 실패한다 (Red).

### Green: 최소한의 구현

테스트를 통과시키기에 충분한 만큼만 구현한다.

```python
@dataclass
class Discount:
    percentage: float
    final_price: float


class DiscountService:
    def calculate(self, user, product):
        if user.membership == "gold" and user.joined_years_ago >= 3:
            pct = 15.0
            return Discount(percentage=pct, final_price=product.price * (1 - pct / 100))
        return Discount(percentage=0.0, final_price=product.price)
```

### Refactor: 중복 제거 및 정리

그린 바 상태에서 리팩터링한다. 이 시점에서 다음 테스트를 추가하여 Triangulation으로 구현을 일반화할 수도 있다.

```python
def test_standard_member_gets_no_discount(discount_service):
    user = UserFactory()  # 기본값: standard, 0년
    product = ProductFactory(price=100.00)

    discount = discount_service.calculate(user, product)

    assert discount.percentage == 0.0
    assert discount.final_price == 100.00


def test_new_gold_member_gets_five_percent_discount(discount_service):
    user = UserFactory(membership="gold", joined_years_ago=1)
    product = ProductFactory(price=200.00)

    discount = discount_service.calculate(user, product)

    assert discount.percentage == 5.0
    assert discount.final_price == 190.00
```

---

## 4. ORM 통합 (SQLAlchemy / Django)

실제 프로젝트에서는 factory_boy를 ORM과 통합하여 DB에 직접 데이터를 생성한다.

```python
# SQLAlchemy 통합
class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Faker("email")


# Django 통합
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "auth.User"
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Faker("email")
```

---

## 5. 핵심 원칙 요약

| 원칙 | 적용 방법 |
|------|-----------|
| **테스트 격리** | fixture의 function 스코프로 각 테스트에 독립적 상태 제공 |
| **의미 있는 데이터** | factory_boy의 Trait으로 테스트 시나리오별 의미가 명확한 변형 생성 |
| **Excessive Setup 방지** | 팩토리에 기본값을 정의하고 테스트에서는 관심 있는 필드만 오버라이드 |
| **명백한 데이터** | 테스트에서 예상 값과 실제 값의 관계가 드러나도록 데이터 구성 |
| **검증 우선순위** | 출력 기반 > 상태 기반 > 커뮤니케이션 기반 순으로 선호 |
| **AAA 패턴** | Arrange(fixture + factory) - Act(단일 행위) - Assert(결과 검증) |

---

> **관련 스킬 참조:**
> - [Red-Green-Refactor 사이클, 테스트 선택, 그린 바 전략] --> **implementation-tdd** 스킬
> - [pytest 설정, 마커, 플러그인, Mock 패턴, Hypothesis] --> **implementation-test** 스킬
> - [Django TestCase, pytest-django 통합] --> **implementation-django** 스킬
> - [Python dataclass, 타입 힌트 컨벤션] --> **implementation-python** 스킬
> - [클린 코드 원칙, SOLID] --> **implementation-cleancode** 스킬
