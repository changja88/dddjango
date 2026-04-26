# 주문 취소(cancel_order) TDD 개발 -- Red-Green-Refactor

## 테스트 목록

도메인 규칙 "배송 시작 전에만 취소 가능"을 기반으로 테스트 목록을 작성한다.

```
[ ] 주문이 PENDING 상태일 때 취소하면 CANCELLED 상태가 된다
[ ] 주문이 CONFIRMED 상태일 때 취소하면 CANCELLED 상태가 된다
[ ] 주문이 SHIPPED 상태일 때 취소하면 예외가 발생한다
[ ] 주문이 DELIVERED 상태일 때 취소하면 예외가 발생한다
[ ] 이미 CANCELLED 상태인 주문을 취소하면 예외가 발생한다
[ ] 주문 취소 시 취소 시각이 기록된다
```

순수 도메인 로직이므로 Classical(Inside-Out) 접근법으로, 도메인 모델 내부부터 시작하여 서비스 레이어로 확장한다.

---

## Cycle 1: 가장 단순한 경우 -- PENDING 주문 취소

### Red

```python
# tests/test_order.py
import pytest
from orders.models import Order, OrderStatus


class TestCancelOrder:
    def test_cancel__pending_order__becomes_cancelled(self):
        order = Order(status=OrderStatus.PENDING)

        order.cancel()

        assert order.status == OrderStatus.CANCELLED
```

이 테스트는 `Order`, `OrderStatus`, `cancel()` 메서드가 모두 없으므로 실패한다.

### Green

```python
# orders/models.py
from django.db import models


class OrderStatus(models.TextChoices):
    PENDING = "PENDING", "대기"
    CANCELLED = "CANCELLED", "취소"


class Order(models.Model):
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
    )

    def cancel(self):
        self.status = OrderStatus.CANCELLED
```

최소한의 코드로 테스트를 통과시킨다. 아직 배송 상태 검증은 없다 -- 그것을 요구하는 테스트가 없기 때문이다.

### Refactor

현재 코드가 충분히 단순하므로 리팩터링할 것이 없다. 다음 사이클로 진행한다.

---

## Cycle 2: CONFIRMED 상태 취소

### Red

```python
def test_cancel__confirmed_order__becomes_cancelled(self):
    order = Order(status=OrderStatus.CONFIRMED)

    order.cancel()

    assert order.status == OrderStatus.CANCELLED
```

`OrderStatus.CONFIRMED`가 없으므로 실패한다.

### Green

```python
class OrderStatus(models.TextChoices):
    PENDING = "PENDING", "대기"
    CONFIRMED = "CONFIRMED", "확인"
    CANCELLED = "CANCELLED", "취소"
```

`CONFIRMED`를 추가하면 기존 `cancel()` 구현이 그대로 통과시킨다. 상태와 무관하게 `CANCELLED`로 변경하기 때문이다.

### Refactor

두 테스트가 같은 패턴이므로 아직 리팩터링이 필요하지 않다. 다음 사이클에서 삼각측량이 추상화를 강제할 것이다.

---

## Cycle 3: 핵심 도메인 규칙 -- SHIPPED 상태 취소 거부

### Red

```python
from orders.exceptions import OrderCancelError


def test_cancel__shipped_order__raises_error(self):
    order = Order(status=OrderStatus.SHIPPED)

    with pytest.raises(OrderCancelError, match="배송 시작 후에는 취소할 수 없습니다"):
        order.cancel()
```

현재 `cancel()`은 무조건 상태를 변경하므로 예외 없이 통과하여 테스트가 실패한다.

### Green

```python
# orders/exceptions.py
class OrderCancelError(Exception):
    pass


# orders/models.py
class OrderStatus(models.TextChoices):
    PENDING = "PENDING", "대기"
    CONFIRMED = "CONFIRMED", "확인"
    SHIPPED = "SHIPPED", "배송중"
    CANCELLED = "CANCELLED", "취소"


class Order(models.Model):
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
    )

    _CANCELLABLE_STATUSES = {OrderStatus.PENDING, OrderStatus.CONFIRMED}

    def cancel(self):
        if self.status not in self._CANCELLABLE_STATUSES:
            raise OrderCancelError("배송 시작 후에는 취소할 수 없습니다")
        self.status = OrderStatus.CANCELLED
```

삼각측량에 의해 일반화가 강제되었다. 두 가지 경우(취소 가능 / 취소 불가)가 존재하므로 `_CANCELLABLE_STATUSES` 집합으로 추상화한다.

### Refactor

`_CANCELLABLE_STATUSES`를 도입하여 조건문이 선언적으로 바뀌었다. 새로운 상태가 추가되더라도 집합에 추가/제거만 하면 된다.

---

## Cycle 4: DELIVERED 상태 취소 거부

### Red

```python
def test_cancel__delivered_order__raises_error(self):
    order = Order(status=OrderStatus.DELIVERED)

    with pytest.raises(OrderCancelError, match="배송 시작 후에는 취소할 수 없습니다"):
        order.cancel()
```

### Green

```python
class OrderStatus(models.TextChoices):
    PENDING = "PENDING", "대기"
    CONFIRMED = "CONFIRMED", "확인"
    SHIPPED = "SHIPPED", "배송중"
    DELIVERED = "DELIVERED", "배송완료"
    CANCELLED = "CANCELLED", "취소"
```

`DELIVERED`를 추가하면 기존 `_CANCELLABLE_STATUSES` 로직이 자동으로 거부한다. 테스트 통과.

### Refactor

리팩터링 불필요. 설계가 Open-Closed Principle을 따르고 있다.

---

## Cycle 5: 이미 취소된 주문 재취소 방지

### Red

```python
def test_cancel__already_cancelled_order__raises_error(self):
    order = Order(status=OrderStatus.CANCELLED)

    with pytest.raises(OrderCancelError, match="이미 취소된 주문입니다"):
        order.cancel()
```

현재 구현은 `CANCELLED`가 `_CANCELLABLE_STATUSES`에 없으므로 "배송 시작 후에는 취소할 수 없습니다" 메시지를 반환한다. 메시지가 다르므로 테스트 실패.

### Green

```python
def cancel(self):
    if self.status == OrderStatus.CANCELLED:
        raise OrderCancelError("이미 취소된 주문입니다")
    if self.status not in self._CANCELLABLE_STATUSES:
        raise OrderCancelError("배송 시작 후에는 취소할 수 없습니다")
    self.status = OrderStatus.CANCELLED
```

### Refactor

검증 순서가 명확하다: 이미 취소 확인 -> 취소 가능 상태 확인 -> 상태 변경. 이 순서가 도메인 규칙을 잘 표현한다.

---

## Cycle 6: 취소 시각 기록

### Red

```python
from django.utils import timezone
from unittest.mock import patch


def test_cancel__records_cancelled_at_timestamp(self):
    order = Order(status=OrderStatus.PENDING)
    fixed_now = timezone.make_aware(timezone.datetime(2026, 4, 6, 12, 0, 0))

    with patch("django.utils.timezone.now", return_value=fixed_now):
        order.cancel()

    assert order.cancelled_at == fixed_now
```

`cancelled_at` 필드가 없으므로 실패한다.

### Green

```python
class Order(models.Model):
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
    )
    cancelled_at = models.DateTimeField(null=True, blank=True)

    _CANCELLABLE_STATUSES = {OrderStatus.PENDING, OrderStatus.CONFIRMED}

    def cancel(self):
        if self.status == OrderStatus.CANCELLED:
            raise OrderCancelError("이미 취소된 주문입니다")
        if self.status not in self._CANCELLABLE_STATUSES:
            raise OrderCancelError("배송 시작 후에는 취소할 수 없습니다")
        self.status = OrderStatus.CANCELLED
        self.cancelled_at = timezone.now()
```

### Refactor

모델이 도메인 규칙을 직접 캡슐화하고 있다. 이제 서비스 레이어로 확장한다.

---

## Cycle 7: 서비스 레이어 -- 영속성 포함 취소

도메인 모델에 규칙이 캡슐화되었으므로, 서비스 레이어는 조회/저장/트랜잭션 책임만 갖는다.

### Red

```python
# tests/test_order_service.py
import pytest
from django.test import TestCase
from orders.models import Order, OrderStatus
from orders.services import cancel_order
from orders.exceptions import OrderCancelError


class TestCancelOrderService(TestCase):
    def test_cancel_order__existing_pending_order__saves_cancelled_state(self):
        order = Order.objects.create(status=OrderStatus.PENDING)

        cancel_order(order_id=order.id)

        order.refresh_from_db()
        assert order.status == OrderStatus.CANCELLED
        assert order.cancelled_at is not None

    def test_cancel_order__shipped_order__raises_and_does_not_modify(self):
        order = Order.objects.create(status=OrderStatus.SHIPPED)

        with pytest.raises(OrderCancelError):
            cancel_order(order_id=order.id)

        order.refresh_from_db()
        assert order.status == OrderStatus.SHIPPED

    def test_cancel_order__nonexistent_order__raises_not_found(self):
        with pytest.raises(Order.DoesNotExist):
            cancel_order(order_id=99999)
```

`cancel_order` 함수가 없으므로 실패한다.

### Green

```python
# orders/services.py
from django.db import transaction
from orders.models import Order


@transaction.atomic
def cancel_order(order_id: int) -> Order:
    order = Order.objects.select_for_update().get(id=order_id)
    order.cancel()
    order.save(update_fields=["status", "cancelled_at"])
    return order
```

서비스 함수는 얇다. 도메인 규칙은 모델의 `cancel()` 메서드에 있으며, 서비스는 트랜잭션과 영속성만 담당한다. `select_for_update()`로 동시성 문제를 방지한다.

### Refactor

서비스 레이어가 충분히 얇으므로 추가 리팩터링이 불필요하다.

---

## 최종 코드

### orders/exceptions.py

```python
class OrderCancelError(Exception):
    pass
```

### orders/models.py

```python
from django.db import models
from django.utils import timezone

from orders.exceptions import OrderCancelError


class OrderStatus(models.TextChoices):
    PENDING = "PENDING", "대기"
    CONFIRMED = "CONFIRMED", "확인"
    SHIPPED = "SHIPPED", "배송중"
    DELIVERED = "DELIVERED", "배송완료"
    CANCELLED = "CANCELLED", "취소"


class Order(models.Model):
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
    )
    cancelled_at = models.DateTimeField(null=True, blank=True)

    _CANCELLABLE_STATUSES = {OrderStatus.PENDING, OrderStatus.CONFIRMED}

    def cancel(self):
        if self.status == OrderStatus.CANCELLED:
            raise OrderCancelError("이미 취소된 주문입니다")
        if self.status not in self._CANCELLABLE_STATUSES:
            raise OrderCancelError("배송 시작 후에는 취소할 수 없습니다")
        self.status = OrderStatus.CANCELLED
        self.cancelled_at = timezone.now()

    class Meta:
        db_table = "orders"
```

### orders/services.py

```python
from django.db import transaction

from orders.models import Order


@transaction.atomic
def cancel_order(order_id: int) -> Order:
    order = Order.objects.select_for_update().get(id=order_id)
    order.cancel()
    order.save(update_fields=["status", "cancelled_at"])
    return order
```

### tests/test_order.py

```python
import pytest
from unittest.mock import patch

from django.utils import timezone

from orders.exceptions import OrderCancelError
from orders.models import Order, OrderStatus


class TestCancelOrder:
    def test_cancel__pending_order__becomes_cancelled(self):
        order = Order(status=OrderStatus.PENDING)

        order.cancel()

        assert order.status == OrderStatus.CANCELLED

    def test_cancel__confirmed_order__becomes_cancelled(self):
        order = Order(status=OrderStatus.CONFIRMED)

        order.cancel()

        assert order.status == OrderStatus.CANCELLED

    def test_cancel__shipped_order__raises_error(self):
        order = Order(status=OrderStatus.SHIPPED)

        with pytest.raises(OrderCancelError, match="배송 시작 후에는 취소할 수 없습니다"):
            order.cancel()

    def test_cancel__delivered_order__raises_error(self):
        order = Order(status=OrderStatus.DELIVERED)

        with pytest.raises(OrderCancelError, match="배송 시작 후에는 취소할 수 없습니다"):
            order.cancel()

    def test_cancel__already_cancelled_order__raises_error(self):
        order = Order(status=OrderStatus.CANCELLED)

        with pytest.raises(OrderCancelError, match="이미 취소된 주문입니다"):
            order.cancel()

    def test_cancel__records_cancelled_at_timestamp(self):
        order = Order(status=OrderStatus.PENDING)
        fixed_now = timezone.make_aware(timezone.datetime(2026, 4, 6, 12, 0, 0))

        with patch("django.utils.timezone.now", return_value=fixed_now):
            order.cancel()

        assert order.cancelled_at == fixed_now
```

### tests/test_order_service.py

```python
import pytest
from django.test import TestCase

from orders.exceptions import OrderCancelError
from orders.models import Order, OrderStatus
from orders.services import cancel_order


class TestCancelOrderService(TestCase):
    def test_cancel_order__existing_pending_order__saves_cancelled_state(self):
        order = Order.objects.create(status=OrderStatus.PENDING)

        cancel_order(order_id=order.id)

        order.refresh_from_db()
        assert order.status == OrderStatus.CANCELLED
        assert order.cancelled_at is not None

    def test_cancel_order__shipped_order__raises_and_does_not_modify(self):
        order = Order.objects.create(status=OrderStatus.SHIPPED)

        with pytest.raises(OrderCancelError):
            cancel_order(order_id=order.id)

        order.refresh_from_db()
        assert order.status == OrderStatus.SHIPPED

    def test_cancel_order__nonexistent_order__raises_not_found(self):
        with pytest.raises(Order.DoesNotExist):
            cancel_order(order_id=99999)
```

---
> **관련 스킬 참조:**
> - Django 모델 설계(TextChoices, select_for_update, update_fields) -> **implementation-django** 스킬
> - pytest 픽스처, TestCase, 모킹 기법 -> **implementation-test** 스킬
> - 도메인 예외 설계, 서비스 레이어 패턴 -> **implementation-cleancode** 스킬
