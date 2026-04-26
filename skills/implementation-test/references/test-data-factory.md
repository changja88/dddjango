# 테스트 데이터 팩토리 (factory_boy + Faker) 레퍼런스

factory_boy를 사용한 테스트 데이터 생성의 상세 규칙과 예시.

```bash
pip install factory_boy faker
```

factory_boy는 테스트 객체 생성을 위한 "청사진" 역할을 한다. JSON fixture 파일 대신 Python 코드로 테스트 데이터를 선언적으로 정의한다.

---

## 1. 기본 팩토리 정의

factory_boy는 테스트 객체 생성을 위한 "청사진" 역할을 한다. JSON fixture 파일 대신 Python 코드로 테스트 데이터를 선언적으로 정의한다.

```python
import factory
from factory import fuzzy
from myapp.models import User, Post, Comment

class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.LazyAttribute(
        lambda obj: f"{obj.first_name.lower()}.{obj.last_name.lower()}@example.com"
    )
    created_at = factory.LazyFunction(datetime.now)
    age = fuzzy.FuzzyInteger(18, 80)
```

---

## 2. 관계 처리: SubFactory, RelatedFactory

```python
class PostFactory(factory.Factory):
    class Meta:
        model = Post

    title = factory.Faker("sentence", nb_words=6)
    content = factory.Faker("paragraph", nb_sentences=5)
    author = factory.SubFactory(UserFactory)

class CommentFactory(factory.Factory):
    class Meta:
        model = Comment

    text = factory.Faker("sentence")
    post = factory.SubFactory(PostFactory)
    author = factory.SubFactory(UserFactory)

def test_comment_creation():
    comment = CommentFactory()
    assert comment.author is not None
    assert comment.post.author is not None

    specific_user = UserFactory(username="admin")
    comment = CommentFactory(author=specific_user)
    assert comment.author.username == "admin"
```

---

## 3. Trait: 변형 객체 생성

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

def test_order_states():
    pending = OrderFactory()
    assert pending.status == "pending"

    paid = OrderFactory(paid=True)
    assert paid.status == "paid"
    assert paid.paid_at is not None

    shipped = OrderFactory(shipped=True)
    assert shipped.status == "shipped"

    cancelled = OrderFactory(cancelled=True)
    assert cancelled.total_amount == 0
```

---

## 4. 배치 생성과 재현성

```python
def test_batch_creation():
    users = UserFactory.create_batch(10)
    assert len(users) == 10

    admins = UserFactory.create_batch(
        5,
        username=factory.Iterator(["admin1", "admin2", "admin3", "admin4", "admin5"]),
    )

def test_reproducible_data():
    """시드를 고정하여 재현 가능한 테스트 데이터"""
    import factory.random
    factory.random.reseed_random(42)

    user1 = UserFactory()
    factory.random.reseed_random(42)
    user2 = UserFactory()

    assert user1.first_name == user2.first_name
```

---

## 5. SQLAlchemy / Django ORM 통합

```python
# SQLAlchemy
class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Faker("email")

# Django
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "auth.User"
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Faker("email")
```

> 출처: [factory_boy 공식 문서](https://factoryboy.readthedocs.io/), [factory_boy Reference](https://factoryboy.readthedocs.io/en/stable/reference.html), [Using factory_boy with ORMs](https://factoryboy.readthedocs.io/en/stable/orms.html)
