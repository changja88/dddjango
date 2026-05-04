현재 디렉터리에 파일이 없어 실제 코드 기준이 아니라, Django + pytest에서 주문 취소 기능을 TDD로 추가하는 표준 흐름으로 작성합니다.

**1. 실패 테스트 작성**

먼저 “취소 가능한 주문은 취소된다”는 비즈니스 규칙부터 테스트합니다.

```python
# tests/test_order_cancel.py
import pytest

from orders.models import Order


@pytest.mark.django_db
def test_paid_order_can_be_cancelled():
    order = Order.objects.create(
        status=Order.Status.PAID,
        total_price=10000,
    )

    order.cancel()

    order.refresh_from_db()
    assert order.status == Order.Status.CANCELLED
```

실행:

```bash
pytest
```

예상 실패:

```text
AttributeError: 'Order' object has no attribute 'cancel'
```

이 실패는 좋습니다. 아직 `cancel()` 동작이 없다는 사실을 테스트가 정확히 말해줍니다.

**2. 최소 구현**

테스트를 통과시키는 가장 작은 구현만 추가합니다.

```python
# orders/models.py
from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
    )
    total_price = models.PositiveIntegerField()

    def cancel(self):
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])
```

다시 실행:

```bash
pytest
```

이제 첫 테스트는 통과해야 합니다.

**3. 규칙 추가: 이미 취소된 주문은 다시 취소할 수 없다**

다음 비즈니스 규칙을 실패 테스트로 추가합니다.

```python
@pytest.mark.django_db
def test_cancelled_order_cannot_be_cancelled_again():
    order = Order.objects.create(
        status=Order.Status.CANCELLED,
        total_price=10000,
    )

    with pytest.raises(ValueError, match="already cancelled"):
        order.cancel()
```

예상 실패:

```text
Failed: DID NOT RAISE <class 'ValueError'>
```

최소 구현:

```python
def cancel(self):
    if self.status == self.Status.CANCELLED:
        raise ValueError("Order is already cancelled")

    self.status = self.Status.CANCELLED
    self.save(update_fields=["status"])
```

**4. 규칙 추가: 배송 중인 주문은 취소할 수 없다**

상태를 확장하고 테스트를 먼저 추가합니다.

```python
@pytest.mark.django_db
def test_shipped_order_cannot_be_cancelled():
    order = Order.objects.create(
        status=Order.Status.SHIPPED,
        total_price=10000,
    )

    with pytest.raises(ValueError, match="cannot be cancelled"):
        order.cancel()
```

최소 구현:

```python
class Status(models.TextChoices):
    PAID = "paid", "Paid"
    SHIPPED = "shipped", "Shipped"
    CANCELLED = "cancelled", "Cancelled"
```

```python
def cancel(self):
    if self.status == self.Status.CANCELLED:
        raise ValueError("Order is already cancelled")

    if self.status == self.Status.SHIPPED:
        raise ValueError("Shipped order cannot be cancelled")

    self.status = self.Status.CANCELLED
    self.save(update_fields=["status"])
```

**5. 리팩터링 방향**

테스트가 통과한 뒤에만 구조를 정리합니다.

```python
class Order(models.Model):
    class Status(models.TextChoices):
        PAID = "paid", "Paid"
        SHIPPED = "shipped", "Shipped"
        CANCELLED = "cancelled", "Cancelled"

    CANCELLABLE_STATUSES = {
        Status.PAID,
    }

    status = models.CharField(max_length=20, choices=Status.choices)
    total_price = models.PositiveIntegerField()

    def cancel(self):
        if not self.can_cancel():
            raise ValueError("Order cannot be cancelled")

        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])

    def can_cancel(self):
        return self.status in self.CANCELLABLE_STATUSES
```

테스트도 메시지 세부 구현에 덜 묶이게 정리할 수 있습니다.

```python
@pytest.mark.django_db
@pytest.mark.parametrize("status", [
    Order.Status.CANCELLED,
    Order.Status.SHIPPED,
])
def test_non_cancellable_order_cannot_be_cancelled(status):
    order = Order.objects.create(
        status=status,
        total_price=10000,
    )

    with pytest.raises(ValueError):
        order.cancel()
```

흐름은 이렇게 잡으면 됩니다.

1. `cancel()`이 없어서 실패하는 테스트 작성
2. 상태를 `CANCELLED`로 바꾸는 최소 구현
3. “이미 취소됨”, “배송 중” 같은 금지 조건을 테스트로 하나씩 추가
4. 조건문이 늘어나면 `can_cancel()`이나 상태 정책으로 리팩터링
5. 서비스 레이어, 환불, 재고 복구, 이벤트 발행은 별도 테스트로 확장