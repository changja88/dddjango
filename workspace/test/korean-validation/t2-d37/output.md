# Django 모델 비즈니스 로직 테스트: TestCase 선택과 assertNumQueries

## TestCase 선택 기준

Django는 네 가지 TestCase 클래스를 제공하며, 테스트 대상에 따라 올바른 클래스를 선택해야 테스트 속도와 신뢰성을 모두 확보할 수 있다.

| 클래스 | 특징 | 사용 시나리오 |
|--------|------|-------------|
| `SimpleTestCase` | DB 접근 불가, 가장 빠름 | 유틸리티 함수, 폼 검증 테스트 |
| `TestCase` | 트랜잭션 롤백으로 격리, 빠름 | **대부분의 테스트** |
| `TransactionTestCase` | 실제 트랜잭션 커밋, 느림 | `select_for_update()`, DB 트리거 테스트 |
| `LiveServerTestCase` | 실제 서버 실행 | Selenium 통합 테스트 |

### 선택 판단 흐름

1. DB 접근이 필요 없는가? -> `SimpleTestCase`
2. 트랜잭션 동작 자체를 테스트하는가? -> `TransactionTestCase`
3. 브라우저 통합 테스트인가? -> `LiveServerTestCase`
4. 그 외 모든 경우 -> `TestCase`

**핵심**: `TestCase`는 각 테스트를 트랜잭션으로 감싸고 롤백하므로, 실제 COMMIT이 발생하지 않아 빠르다. 모델의 비즈니스 로직 테스트는 대부분 `TestCase`가 적합하다.

### pytest-django에서의 사용

pytest-django를 사용할 때는 `@pytest.mark.django_db` 마커로 DB 접근을 명시한다. 이 마커는 기본적으로 `TestCase`와 동일한 트랜잭션 롤백 방식으로 동작한다.

```python
import pytest

@pytest.mark.django_db
class TestOrderModel:
    def test_confirm_sets_status(self):
        order = OrderFactory()
        order.confirm()
        order.refresh_from_db()
        assert order.status == Order.Status.CONFIRMED

    def test_confirm_applies_discount_for_large_order(self):
        order = OrderFactory(total=Decimal("150.00"))
        order.confirm()
        order.refresh_from_db()
        assert order.discount == Decimal("15.00")
```

실제 트랜잭션 커밋이 필요한 경우 `transaction=True` 옵션을 사용한다.

```python
@pytest.mark.django_db(transaction=True)
def test_select_for_update_locks_row():
    """select_for_update()가 실제로 행을 잠그는지 검증."""
    order = OrderFactory(status=Order.Status.PENDING)
    # 실제 트랜잭션 커밋이 필요한 테스트 로직
    ...
```

---

## assertNumQueries 사용법

`assertNumQueries`는 특정 코드 블록에서 실행되는 SQL 쿼리 수를 검증하여 N+1 쿼리 회귀를 방지한다. 성능 크리티컬 경로에서는 반드시 사용해야 한다.

### Django TestCase 스타일

```python
from django.test import TestCase

class ArticleModelTest(TestCase):
    def test_publish_executes_single_query(self):
        """publish()가 정확히 1개의 UPDATE 쿼리를 실행하는지 검증."""
        article = ArticleFactory()

        with self.assertNumQueries(1):
            article.publish()

    def test_bulk_publish_avoids_n_plus_one(self):
        """10개 기사를 일괄 발행할 때 쿼리 수가 기사 수에 비례하지 않는지 검증."""
        articles = ArticleFactory.create_batch(10)

        with self.assertNumQueries(1):
            Article.objects.filter(
                pk__in=[a.pk for a in articles]
            ).update(status=Article.Status.PUBLISHED)
```

### pytest-django 스타일

pytest-django에서는 `django_assert_num_queries` 픽스처를 사용한다.

```python
import pytest

@pytest.mark.django_db
class TestArticleQueries:
    def test_publish_executes_single_query(self, django_assert_num_queries):
        """publish()가 정확히 1개의 UPDATE 쿼리를 실행하는지 검증."""
        article = ArticleFactory()

        with django_assert_num_queries(1):
            article.publish()

    def test_published_list_with_author_avoids_n_plus_one(
        self, django_assert_num_queries
    ):
        """발행된 기사 목록을 작성자와 함께 조회할 때 N+1이 발생하지 않는지 검증."""
        ArticleFactory.create_batch(5, published=True)

        with django_assert_num_queries(1):
            list(
                Article.objects.published()
                .select_related("author")
                .values_list("title", "author__username")
            )
```

### assertNumQueries 적용 가이드라인

**언제 사용하는가:**
- 커스텀 QuerySet 메서드가 예상한 수의 쿼리만 실행하는지 검증할 때
- `select_related`/`prefetch_related`가 제대로 적용되었는지 확인할 때
- 모델 메서드의 `save(update_fields=...)`가 불필요한 쿼리를 생성하지 않는지 검증할 때
- 벌크 작업이 개별 쿼리로 분해되지 않는지 확인할 때

**주의사항:**
- 정확한 쿼리 수에 과도하게 결합하지 않는다. Django 버전 업그레이드 시 내부 쿼리 수가 변할 수 있다.
- 쿼리 수보다 "N에 비례하지 않는다"는 속성이 더 중요한 경우, 데이터 수를 늘려도 쿼리 수가 일정한지 검증하는 방식을 고려한다.

```python
@pytest.mark.django_db
def test_published_list_query_count_is_constant(django_assert_num_queries):
    """기사 수가 늘어도 쿼리 수가 일정한지 검증."""
    ArticleFactory.create_batch(3, published=True)
    with django_assert_num_queries(1) as captured:
        list(Article.objects.published().select_related("author"))

    # 기사 수를 늘려도 동일한 쿼리 수
    ArticleFactory.create_batch(7, published=True)
    with django_assert_num_queries(1):
        list(Article.objects.published().select_related("author"))
```

---

## 모델 비즈니스 로직 테스트 종합 예시

모든 테스트는 AAA(Arrange-Act-Assert) 구조를 따르며, 하나의 동작만 검증한다.

```python
import pytest
from decimal import Decimal
from django.test import TestCase

# === Django TestCase 스타일 ===

class OrderModelTest(TestCase):
    def test_confirm_sets_status_to_confirmed(self):
        """confirm()이 상태를 CONFIRMED로 변경하는지 검증."""
        order = OrderFactory(status=Order.Status.PENDING)

        order.confirm()

        order.refresh_from_db()
        assert order.status == Order.Status.CONFIRMED

    def test_confirm_applies_discount_when_total_exceeds_threshold(self):
        """총액이 100을 초과하면 10% 할인을 적용하는지 검증."""
        order = OrderFactory(total=Decimal("150.00"))

        order.confirm()

        order.refresh_from_db()
        assert order.discount == Decimal("15.00")

    def test_confirm_skips_discount_when_total_at_boundary(self):
        """총액이 정확히 100이면 할인을 적용하지 않는지 검증 (경계 값)."""
        order = OrderFactory(total=Decimal("100.00"))

        order.confirm()

        order.refresh_from_db()
        assert order.discount == Decimal("0")

    def test_confirm_saves_only_changed_fields(self):
        """confirm()이 변경된 필드만 업데이트하는지 쿼리 수로 검증."""
        order = OrderFactory()

        with self.assertNumQueries(1):
            order.confirm()


# === pytest-django 스타일 ===

@pytest.mark.django_db
class TestOrderModel:
    def test_cancel_sets_status_to_cancelled(self):
        """cancel()이 상태를 CANCELLED로 변경하는지 검증."""
        order = OrderFactory(status=Order.Status.CONFIRMED)

        order.cancel()

        order.refresh_from_db()
        assert order.status == Order.Status.CANCELLED

    def test_cancel_raises_on_already_cancelled(self):
        """이미 취소된 주문에 cancel()을 호출하면 예외가 발생하는지 검증."""
        order = OrderFactory(status=Order.Status.CANCELLED)

        with pytest.raises(ValueError, match="이미 취소된 주문"):
            order.cancel()

    def test_total_calculation_uses_single_query(self, django_assert_num_queries):
        """주문 총액 계산이 단일 쿼리로 수행되는지 검증."""
        order = OrderFactory()
        OrderItemFactory.create_batch(5, order=order)

        with django_assert_num_queries(1):
            order.calculate_total()
```

### 검증 방식 선택

모델 비즈니스 로직 테스트에서는 검증 우선순위를 따른다:

1. **출력 기반** (반환 값): `assert order.calculate_total() == Decimal("250.00")`
2. **상태 기반** (객체 상태): `order.confirm(); assert order.status == Order.Status.CONFIRMED`
3. **통신 기반** (Mock): 이메일 발송 같은 외부 의존성에만 사용

```python
@pytest.mark.django_db
def test_confirm_sends_notification_email(mocker):
    """confirm()이 확인 이메일을 발송하는지 검증 (외부 의존성만 Mock)."""
    mock_send = mocker.patch("apps.orders.models.send_mail")
    order = OrderFactory()

    order.confirm()

    mock_send.assert_called_once_with(
        "Order confirmed",
        mocker.ANY,
        [order.user.email],
    )
```

### Django 공식 어설션 규칙

```python
# assertIs(x, True)를 사용한다 -- 타입까지 검증
self.assertIs(article.is_published, True)

# assertTrue()는 피한다 -- truthy 값도 통과
# self.assertTrue(article.is_published)  # 1, "yes" 등도 통과

# assertRaisesMessage()로 에러 메시지까지 검증한다
with self.assertRaisesMessage(ValidationError, "이미 등록된 이메일"):
    form.clean_email()
```

---

## 참조

- Django 모델 설계 패턴(Fat Model, Thin View, 서비스 레이어 분리)에 대한 자세한 가이드는 **implementation-django** 스킬을 참조하세요.
- TDD 방법론(Red-Green-Refactor)에 대한 자세한 가이드는 **implementation-tdd** 스킬을 참조하세요.
- Factory Boy를 활용한 테스트 데이터 생성에 대한 자세한 가이드는 **implementation-test** 스킬(Section 8: 테스트 데이터 팩토리)을 참조하세요.
- 클린 코드 원칙에 대한 자세한 가이드는 **implementation-cleancode** 스킬을 참조하세요.
