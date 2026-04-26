# Django TestCase vs TransactionTestCase: 트랜잭션 롤백과 테스트 격리

## 핵심 차이: 테스트 격리 방식

Django는 테스트 간 DB 상태를 격리하기 위해 두 가지 다른 전략을 사용한다.

### TestCase -- 트랜잭션 롤백 격리 (기본 선택)

`TestCase`는 각 테스트를 `atomic()` 블록으로 감싼다. 테스트 내에서 생성된 모든 DB 데이터는 실제로 커밋되지 않고, 테스트가 끝나면 롤백된다. 데이터가 디스크에 쓰이지 않으므로 빠르다.

```python
from django.test import TestCase

class OrderModelTest(TestCase):
    """각 테스트는 암묵적 트랜잭션 안에서 실행되고, 끝나면 롤백된다."""

    def test_confirm_applies_discount(self):
        # Arrange
        order = Order.objects.create(total=Decimal("200"), user=self.user)

        # Act
        order.confirm()

        # Assert
        order.refresh_from_db()
        assert order.discount == Decimal("20.0")
        # 이 데이터는 테스트 종료 시 롤백된다 -- 다른 테스트에 영향 없음

    def test_confirm_sets_status(self):
        order = Order.objects.create(total=Decimal("50"), user=self.user)

        order.confirm()

        order.refresh_from_db()
        assert order.status == Order.Status.CONFIRMED
        # 위 테스트의 order와 완전히 독립적
```

**동작 원리:**
1. Django가 테스트 시작 전에 `SAVEPOINT` 생성
2. 테스트 코드 실행 (INSERT, UPDATE 등 모두 트랜잭션 안에서 발생)
3. 테스트 종료 후 `ROLLBACK TO SAVEPOINT` 실행
4. 데이터가 커밋된 적 없으므로 다음 테스트는 깨끗한 DB에서 시작

**제약:** 테스트 코드 안에서 실제 트랜잭션 커밋이 일어나지 않기 때문에, 트랜잭션 커밋에 의존하는 기능은 테스트할 수 없다.

### TransactionTestCase -- 실제 커밋 + TRUNCATE 격리

`TransactionTestCase`는 트랜잭션을 감싸지 않는다. 각 테스트의 DB 조작이 실제로 커밋된다. 테스트 종료 후 테이블을 `TRUNCATE`(또는 `DELETE`)하여 초기화한다.

```python
from django.test import TransactionTestCase
from django.db import transaction

class InventoryTransactionTest(TransactionTestCase):
    """실제 트랜잭션 동작을 검증해야 할 때만 사용한다."""

    def test_concurrent_stock_update_with_select_for_update(self):
        # Arrange
        product = Product.objects.create(name="Widget", stock=10)

        # Act -- select_for_update()는 실제 트랜잭션 커밋이 필요하다
        with transaction.atomic():
            locked = Product.objects.select_for_update().get(pk=product.pk)
            locked.stock -= 3
            locked.save()

        # Assert
        product.refresh_from_db()
        assert product.stock == 7

    def test_on_commit_callback_fires(self):
        """transaction.on_commit()은 실제 커밋이 발생해야 콜백이 실행된다."""
        callback_called = []

        with transaction.atomic():
            Order.objects.create(total=Decimal("100"), user=self.user)
            transaction.on_commit(lambda: callback_called.append(True))

        # TestCase에서는 실제 커밋이 일어나지 않아 이 assert가 실패한다
        assert callback_called == [True]
```

## 언제 무엇을 쓰는가

| 상황 | 선택 | 이유 |
|------|------|------|
| 모델 CRUD, 비즈니스 로직 | `TestCase` | 빠르고 격리됨 |
| `select_for_update()` | `TransactionTestCase` | 실제 잠금은 커밋된 트랜잭션 필요 |
| `transaction.on_commit()` 콜백 | `TransactionTestCase` | 실제 커밋이 있어야 콜백 실행 |
| DB 트리거, 시그널 with DB | `TransactionTestCase` | 트리거는 커밋 후 동작하는 경우 있음 |
| `assertNumQueries` 검증 | `TestCase` | 롤백 방식이어도 쿼리 수 측정 가능 |
| Selenium/브라우저 테스트 | `LiveServerTestCase` | 별도 스레드에서 실제 서버 실행 |

## pytest-django에서의 동일한 구분

```python
import pytest

# TestCase 방식 (기본) -- 트랜잭션 롤백
@pytest.mark.django_db
def test_article_publish(article_factory):
    article = article_factory()
    article.publish()
    article.refresh_from_db()
    assert article.status == Article.Status.PUBLISHED

# TransactionTestCase 방식 -- transaction=True 지정
@pytest.mark.django_db(transaction=True)
def test_on_commit_sends_email(user_factory, mailoutbox):
    with transaction.atomic():
        user = user_factory()
        transaction.on_commit(lambda: send_welcome_email(user))
    assert len(mailoutbox) == 1
```

`@pytest.mark.django_db`의 기본값은 `transaction=False`로, `TestCase`와 동일한 롤백 방식이다. `transaction=True`를 명시하면 `TransactionTestCase`와 동일한 실제 커밋 방식으로 전환된다.

## 성능 차이를 이해한다

`TransactionTestCase`가 느린 이유는 매 테스트 후 전체 테이블을 `TRUNCATE` 또는 `DELETE`하기 때문이다. 테이블이 많은 프로젝트에서 이 비용은 테스트당 수백ms에 달할 수 있다. 따라서 대부분의 테스트는 `TestCase`를 사용하고, 실제 트랜잭션 동작이 필수적인 경우에만 `TransactionTestCase`를 사용한다.

```
TestCase:              테스트당 ~10ms  (SAVEPOINT + ROLLBACK)
TransactionTestCase:   테스트당 ~200ms+ (COMMIT + TRUNCATE 모든 테이블)
```

---
> **관련 스킬 참조:**
> - Django 모델 설계, Fat Model 패턴 -> **implementation-django** 스킬
> - pytest 픽스처 설계, conftest 계층 -> **implementation-test** 스킬 (pytest-fixtures)
> - factory_boy로 테스트 데이터 관리 -> **implementation-test** 스킬 (test-data-factory)
> - 서비스 레이어에서 트랜잭션 경계 설계 -> **implementation-django** 스킬 (service-layer)
> - TDD Red-Green-Refactor 워크플로우 -> **implementation-tdd** 스킬
