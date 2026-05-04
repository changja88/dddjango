`/private/tmp/dddjango-codex-eval` 안에는 현재 `config.toml`이나 프로젝트 파일이 없어서, Django 주문 도메인을 가정한 TDD 흐름으로 정리합니다.

**1. 실패 테스트 작성**

먼저 “취소 가능한 주문은 취소된다”는 가장 작은 동작부터 고정합니다.

```python
# tests/test_order_cancel.py
import pytest

from orders.models import Order


@pytest.mark.django_db
def test_paid_order_can_be_cancelled():
    order = Order.objects.create(
        status=Order.Status.PAID,
    )

    order.cancel()

    assert order.status == Order.Status.CANCELLED
```

추가로 정책 테스트도 먼저 둡니다.

```python
@pytest.mark.django_db
def test_shipped_order_cannot_be_cancelled():
    order = Order.objects.create(
        status=Order.Status.SHIPPED,
    )

    with pytest.raises(ValueError, match="cannot be cancelled"):
        order.cancel()

    order.refresh_from_db()
    assert order.status == Order.Status.SHIPPED
```

이 시점에는 `cancel()`이 없거나 동작하지 않으므로 테스트가 실패해야 합니다.

```bash
pytest
```

예상 실패:

```text
AttributeError: 'Order' object has no attribute 'cancel'
```

**2. 최소 구현**

테스트를 통과시키는 만큼만 모델에 구현합니다.

```python
# orders/models.py
from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        SHIPPED = "shipped", "Shipped"
        CANCELLED = "cancelled", "Cancelled"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    def cancel(self):
        if self.status == self.Status.SHIPPED:
            raise ValueError("This order cannot be cancelled")

        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])
```

다시 실행합니다.

```bash
pytest
```

테스트가 통과하면 다음 정책을 테스트로 추가합니다.

```python
@pytest.mark.django_db
def test_cancelled_order_cannot_be_cancelled_again():
    order = Order.objects.create(
        status=Order.Status.CANCELLED,
    )

    with pytest.raises(ValueError, match="cannot be cancelled"):
        order.cancel()
```

그 다음 최소 구현을 확장합니다.

```python
def cancel(self):
    if self.status in [self.Status.SHIPPED, self.Status.CANCELLED]:
        raise ValueError("This order cannot be cancelled")

    self.status = self.Status.CANCELLED
    self.save(update_fields=["status"])
```

**3. 리팩터링 방향**

테스트가 초록색이 된 뒤에만 구조를 다듬습니다.

```python
class Order(models.Model):
    ...

    CANCELLABLE_STATUSES = {
        Status.PENDING,
        Status.PAID,
    }

    def can_cancel(self):
        return self.status in self.CANCELLABLE_STATUSES

    def cancel(self):
        if not self.can_cancel():
            raise ValueError("This order cannot be cancelled")

        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])
```

테스트도 의도를 더 분명히 만들 수 있습니다.

```python
@pytest.mark.django_db
@pytest.mark.parametrize("status", [
    Order.Status.PENDING,
    Order.Status.PAID,
])
def test_cancellable_order_can_be_cancelled(status):
    order = Order.objects.create(status=status)

    order.cancel()

    assert order.status == Order.Status.CANCELLED


@pytest.mark.django_db
@pytest.mark.parametrize("status", [
    Order.Status.SHIPPED,
    Order.Status.CANCELLED,
])
def test_uncancellable_order_cannot_be_cancelled(status):
    order = Order.objects.create(status=status)

    with pytest.raises(ValueError, match="cannot be cancelled"):
        order.cancel()
```

흐름은 이렇게 잡으면 됩니다.

1. 실패 테스트: “어떤 상태의 주문이 취소되는가 / 취소되면 안 되는가”를 먼저 명시
2. 최소 구현: `cancel()` 메서드와 상태 변경만 구현
3. 리팩터링: `can_cancel()` 분리, 상태 목록 상수화, 중복 테스트는 `parametrize`로 정리

핵심은 “정책을 테스트로 먼저 고정하고, 구현은 테스트를 통과할 만큼만 키우는 것”입니다.