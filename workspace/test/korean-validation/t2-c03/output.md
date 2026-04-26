# Django 서비스 레이어 TDD 개발 가이드

Django 서비스 레이어에서 비즈니스 로직을 TDD로 개발하는 방법을 Red-Green-Refactor 사이클을 따라 안내한다. pytest fixture와 Django TestCase를 활용하여 서비스 함수를 점진적으로 구축한다.

---

## 테스트 목록

TDD는 코딩을 시작하기 전에 테스트 목록을 먼저 작성한다. 주문 확정(order_confirm) 서비스를 예제로 사용한다.

```
테스트 목록:
[ ] 대기 중인 주문을 확정하면 상태가 CONFIRMED로 변경된다
[ ] 확정된 주문에 confirmed_at이 설정된다
[ ] 대기 중이 아닌 주문을 확정하면 ValidationError가 발생한다
[ ] 주문 확정 시 창고에 알림이 전송된다
[ ] 트랜잭션 롤백 시 알림이 전송되지 않는다
```

---

## 사이클 1: 가장 단순한 경우 -- 상태 변경

### Red: 실패하는 테스트 작성

가장 단순하면서 새로운 것을 가르쳐주는 테스트부터 시작한다. 서비스 함수가 아직 존재하지 않으므로 ImportError로 실패한다.

```python
# tests/test_order_services.py
import pytest
from django.test import TestCase

from apps.orders.factories import OrderFactory
from apps.orders.models import Order
from apps.orders.services import order_confirm


class TestOrderConfirm(TestCase):
    def test_pending_order__confirm__status_changes_to_confirmed(self):
        """대기 중인 주문을 확정하면 상태가 CONFIRMED로 변경된다."""
        order = OrderFactory(status=Order.Status.PENDING)

        result = order_confirm(order=order)

        self.assertEqual(result.status, Order.Status.CONFIRMED)
```

이 테스트는 AAA 패턴을 따른다. Arrange(팩토리로 대기 중인 주문 생성), Act(서비스 함수 호출), Assert(상태 검증). 테스트 이름은 `[대상]__[조건]__[기대 행위]` 규칙을 따른다.

### Green: 최소한의 코드로 통과

Fake It 전략을 사용하여 상수를 반환하는 것으로 시작할 수도 있지만, 상태 변경은 Obvious Implementation이 명확하다.

```python
# apps/orders/services.py
from apps.orders.models import Order


def order_confirm(*, order: Order) -> Order:
    order.status = Order.Status.CONFIRMED
    order.save(update_fields=["status"])
    return order
```

서비스 함수는 `<entity>_<action>` 네이밍을 따르고, 키워드 전용 인자(`*`)를 사용한다.

### Refactor

현재 단계에서는 중복이 없으므로 리팩터링할 것이 없다. 다음 테스트로 진행한다.

---

## 사이클 2: confirmed_at 타임스탬프

### Red

```python
# tests/test_order_services.py
import time_machine
from django.utils import timezone


class TestOrderConfirm(TestCase):
    def test_pending_order__confirm__status_changes_to_confirmed(self):
        """대기 중인 주문을 확정하면 상태가 CONFIRMED로 변경된다."""
        order = OrderFactory(status=Order.Status.PENDING)

        result = order_confirm(order=order)

        self.assertEqual(result.status, Order.Status.CONFIRMED)

    @time_machine.travel("2026-04-05 10:00:00", tick=False)
    def test_pending_order__confirm__sets_confirmed_at(self):
        """확정된 주문에 confirmed_at이 현재 시각으로 설정된다."""
        order = OrderFactory(status=Order.Status.PENDING)

        result = order_confirm(order=order)

        self.assertEqual(result.confirmed_at, timezone.now())
```

시간 의존 테스트에는 time-machine을 사용한다. `tick=False`로 시간을 고정하여 비교를 결정적으로 만든다.

### Green

```python
# apps/orders/services.py
from django.utils import timezone

from apps.orders.models import Order


def order_confirm(*, order: Order) -> Order:
    order.status = Order.Status.CONFIRMED
    order.confirmed_at = timezone.now()
    order.save(update_fields=["status", "confirmed_at"])
    return order
```

### Refactor

두 테스트가 동일한 Arrange(팩토리 생성)를 반복한다. pytest fixture로 추출한다. Django TestCase와 pytest fixture를 함께 사용하려면 pytest-django를 활용한다.

```python
# tests/test_order_services.py
import pytest
import time_machine
from django.utils import timezone

from apps.orders.factories import OrderFactory
from apps.orders.models import Order
from apps.orders.services import order_confirm


@pytest.fixture
def pending_order(db):
    return OrderFactory(status=Order.Status.PENDING)


@pytest.mark.django_db
class TestOrderConfirm:
    def test_pending_order__confirm__status_changes_to_confirmed(
        self, pending_order
    ):
        """대기 중인 주문을 확정하면 상태가 CONFIRMED로 변경된다."""
        result = order_confirm(order=pending_order)

        assert result.status == Order.Status.CONFIRMED

    @time_machine.travel("2026-04-05 10:00:00", tick=False)
    def test_pending_order__confirm__sets_confirmed_at(self, pending_order):
        """확정된 주문에 confirmed_at이 현재 시각으로 설정된다."""
        result = order_confirm(order=pending_order)

        assert result.confirmed_at == timezone.now()
```

`@pytest.mark.django_db`로 DB 접근을 명시하고, pytest fixture로 설정 코드의 중복을 제거했다. 출력 기반/상태 기반 검증(assert)을 사용하여 리팩터링 내성을 높인다.

---

## 사이클 3: 유효하지 않은 상태 -- 에러 경로

### Red

```python
@pytest.mark.django_db
class TestOrderConfirm:
    # ... 기존 테스트 ...

    def test_non_pending_order__confirm__raises_validation_error(self):
        """대기 중이 아닌 주문을 확정하면 ValidationError가 발생한다."""
        shipped_order = OrderFactory(status=Order.Status.SHIPPED)

        with pytest.raises(ValidationError, match="확정할 수 없는 상태"):
            order_confirm(order=shipped_order)
```

### Green

```python
# apps/orders/services.py
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.orders.models import Order


def order_confirm(*, order: Order) -> Order:
    if order.status != Order.Status.PENDING:
        raise ValidationError("확정할 수 없는 상태입니다.")

    order.status = Order.Status.CONFIRMED
    order.confirmed_at = timezone.now()
    order.save(update_fields=["status", "confirmed_at"])
    return order
```

### Refactor

가드 절이 추가되었지만 함수가 여전히 작고 명확하므로 추가 리팩터링은 불필요하다.

---

## 사이클 4: 외부 의존성 -- 창고 알림

외부 시스템(알림)과의 통합에는 London 학파 접근을 사용한다. 외부 의존성은 Mock으로 격리하고, 행위(메시지 전송)를 검증한다.

### Red

```python
from unittest.mock import Mock, patch


@pytest.mark.django_db
class TestOrderConfirm:
    # ... 기존 테스트 ...

    def test_pending_order__confirm__notifies_warehouse(self, pending_order):
        """주문 확정 시 창고에 알림이 전송된다."""
        mock_notify = Mock()

        with patch(
            "apps.orders.services.notify_warehouse", mock_notify
        ):
            order_confirm(order=pending_order)

        mock_notify.assert_called_once_with(order=pending_order)
```

### Green

```python
# apps/orders/services.py
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.orders.models import Order
from apps.orders.notifications import notify_warehouse


def order_confirm(*, order: Order) -> Order:
    if order.status != Order.Status.PENDING:
        raise ValidationError("확정할 수 없는 상태입니다.")

    order.status = Order.Status.CONFIRMED
    order.confirmed_at = timezone.now()
    order.save(update_fields=["status", "confirmed_at"])

    notify_warehouse(order=order)
    return order
```

### Refactor

알림은 되돌릴 수 없는 부수 효과이다. 트랜잭션이 롤백되면 알림이 전송되면 안 된다. `transaction.on_commit()`으로 감싸야 한다. 이 리팩터링은 다음 테스트가 주도한다.

---

## 사이클 5: 트랜잭션 안전성

### Red

```python
from django.test import TestCase


class TestOrderConfirmTransactionSafety(TestCase):
    def test_rollback__confirm__does_not_notify_warehouse(self):
        """트랜잭션 롤백 시 창고 알림이 전송되지 않는다."""
        order = OrderFactory(status=Order.Status.PENDING)
        mock_notify = Mock()

        with patch(
            "apps.orders.services.notify_warehouse", mock_notify
        ):
            try:
                with transaction.atomic():
                    order_confirm(order=order)
                    raise Exception("강제 롤백")
            except Exception:
                pass

        mock_notify.assert_not_called()
```

이 테스트는 `TestCase`를 사용한다. Django의 `TestCase`는 트랜잭션을 감싸서 `on_commit` 콜백의 동작을 올바르게 검증할 수 있다.

### Green

```python
# apps/orders/services.py
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.orders.models import Order
from apps.orders.notifications import notify_warehouse


def order_confirm(*, order: Order) -> Order:
    if order.status != Order.Status.PENDING:
        raise ValidationError("확정할 수 없는 상태입니다.")

    with transaction.atomic():
        order.status = Order.Status.CONFIRMED
        order.confirmed_at = timezone.now()
        order.save(update_fields=["status", "confirmed_at"])

    transaction.on_commit(lambda: notify_warehouse(order=order))
    return order
```

`transaction.atomic()`으로 DB 작업을 묶고, `transaction.on_commit()`으로 알림을 트랜잭션 커밋 이후에 실행한다.

---

## 최종 코드

### 서비스

```python
# apps/orders/services.py
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.orders.models import Order
from apps.orders.notifications import notify_warehouse


def order_confirm(*, order: Order) -> Order:
    if order.status != Order.Status.PENDING:
        raise ValidationError("확정할 수 없는 상태입니다.")

    with transaction.atomic():
        order.status = Order.Status.CONFIRMED
        order.confirmed_at = timezone.now()
        order.save(update_fields=["status", "confirmed_at"])

    transaction.on_commit(lambda: notify_warehouse(order=order))
    return order
```

### 팩토리

```python
# apps/orders/factories.py
import factory
from factory.django import DjangoModelFactory

from apps.orders.models import Order


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory("apps.users.factories.UserFactory")
    status = Order.Status.PENDING
    total = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)

    class Params:
        confirmed = factory.Trait(
            status=Order.Status.CONFIRMED,
            confirmed_at=factory.LazyFunction(lambda: timezone.now()),
        )
```

### 테스트

```python
# tests/test_order_services.py
import pytest
import time_machine
from django.core.exceptions import ValidationError
from django.db import transaction
from django.test import TestCase
from unittest.mock import Mock, patch

from django.utils import timezone

from apps.orders.factories import OrderFactory
from apps.orders.models import Order
from apps.orders.services import order_confirm


@pytest.fixture
def pending_order(db):
    return OrderFactory(status=Order.Status.PENDING)


@pytest.mark.django_db
class TestOrderConfirm:
    def test_pending_order__confirm__status_changes_to_confirmed(
        self, pending_order
    ):
        """대기 중인 주문을 확정하면 상태가 CONFIRMED로 변경된다."""
        result = order_confirm(order=pending_order)

        assert result.status == Order.Status.CONFIRMED

    @time_machine.travel("2026-04-05 10:00:00", tick=False)
    def test_pending_order__confirm__sets_confirmed_at(self, pending_order):
        """확정된 주문에 confirmed_at이 현재 시각으로 설정된다."""
        result = order_confirm(order=pending_order)

        assert result.confirmed_at == timezone.now()

    def test_non_pending_order__confirm__raises_validation_error(self):
        """대기 중이 아닌 주문을 확정하면 ValidationError가 발생한다."""
        shipped_order = OrderFactory(status=Order.Status.SHIPPED)

        with pytest.raises(ValidationError, match="확정할 수 없는 상태"):
            order_confirm(order=shipped_order)

    def test_pending_order__confirm__notifies_warehouse(self, pending_order):
        """주문 확정 시 창고에 알림이 전송된다."""
        mock_notify = Mock()

        with patch(
            "apps.orders.services.notify_warehouse", mock_notify
        ):
            order_confirm(order=pending_order)

        mock_notify.assert_called_once_with(order=pending_order)


class TestOrderConfirmTransactionSafety(TestCase):
    def test_rollback__confirm__does_not_notify_warehouse(self):
        """트랜잭션 롤백 시 창고 알림이 전송되지 않는다."""
        order = OrderFactory(status=Order.Status.PENDING)
        mock_notify = Mock()

        with patch(
            "apps.orders.services.notify_warehouse", mock_notify
        ):
            try:
                with transaction.atomic():
                    order_confirm(order=order)
                    raise Exception("강제 롤백")
            except Exception:
                pass

        mock_notify.assert_not_called()
```

---

## 적용된 TDD 원칙 요약

| 원칙 | 적용 |
|------|------|
| **테스트 목록** | 코딩 전에 5개의 테스트를 미리 식별 |
| **시작 테스트** | 가장 단순한 경우(상태 변경)부터 시작 |
| **한 단계 테스트** | 단순한 것에서 복잡한 것(외부 의존성)으로 진행 |
| **Obvious Implementation** | 상태 변경은 구현이 명확하여 바로 작성 |
| **Classical 학파** | 순수 도메인 로직(상태, 검증)에는 실제 객체 사용 |
| **London 학파** | 외부 의존성(알림)에는 Mock으로 격리 |
| **출력/상태 기반 검증** | 반환 값과 객체 상태를 우선 검증 |
| **커뮤니케이션 기반 검증** | 외부 의존성 호출에만 Mock 검증 사용 |
| **AAA 패턴** | 모든 테스트가 Arrange-Act-Assert 구조 |
| **테스트 격리** | pytest fixture로 독립적인 상태 보장 |

---

## 교차 참조

- 테스트 코드 작성 기법(pytest fixture, 모킹, Factory Boy, parametrize)에 대한 자세한 가이드는 **implementation-test** 스킬을 참조하세요.
- Django 테스트 컨벤션(TestCase 선택, pytest-django, assertNumQueries)에 대한 자세한 가이드는 **implementation-django** 스킬을 참조하세요.
- 클린 코드 원칙(네이밍, SOLID, 함수 설계)에 대한 자세한 가이드는 **implementation-cleancode** 스킬을 참조하세요.
- Python 특화 컨벤션(타입 힌트, dataclasses, async)에 대한 자세한 가이드는 **implementation-python** 스킬을 참조하세요.
