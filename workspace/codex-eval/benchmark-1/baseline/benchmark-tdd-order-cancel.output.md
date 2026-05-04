현재 `/private/tmp/dddjango-codex-eval`에는 파일이 없어 실제 코드에 맞춘 패치는 할 수 없었습니다. 대신 Django + pytest 기준으로 주문 취소 기능을 TDD로 진행하는 흐름을 예시로 정리합니다.

**1. 실패 테스트 작성**

먼저 “취소 가능한 주문은 취소된다”는 가장 작은 행동부터 테스트합니다.

```python
# tests/test_cancel_order.py
import pytest

from orders.models import Order
from orders.services import cancel_order


@pytest.mark.django_db
def test_cancel_pending_order():
    order = Order.objects.create(status=Order.Status.PENDING)

    cancel_order(order.id)

    order.refresh_from_db()
    assert order.status == Order.Status.CANCELED
```

이 시점에는 `cancel_order`가 없거나 상태 변경 로직이 없어 pytest가 실패해야 합니다.

```bash
pytest
```

예상 실패:

```text
ImportError: cannot import name 'cancel_order'
```

**2. 최소 구현**

테스트를 통과시키는 만큼만 구현합니다.

```python
# orders/services.py
from orders.models import Order


def cancel_order(order_id: int) -> None:
    order = Order.objects.get(id=order_id)
    order.status = Order.Status.CANCELED
    order.save(update_fields=["status"])
```

모델에 상태값이 없다면 최소 상태 enum도 추가합니다.

```python
# orders/models.py
from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CANCELED = "canceled", "Canceled"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
```

다시 실행합니다.

```bash
pytest
```

**3. 다음 실패 테스트 추가**

이제 취소할 수 없는 주문 규칙을 추가합니다. 예를 들어 이미 배송된 주문은 취소할 수 없다고 가정합니다.

```python
import pytest

from orders.models import Order
from orders.services import cancel_order, OrderCannotBeCanceled


@pytest.mark.django_db
def test_cannot_cancel_shipped_order():
    order = Order.objects.create(status=Order.Status.SHIPPED)

    with pytest.raises(OrderCannotBeCanceled):
        cancel_order(order.id)

    order.refresh_from_db()
    assert order.status == Order.Status.SHIPPED
```

최소 구현:

```python
# orders/services.py
from orders.models import Order


class OrderCannotBeCanceled(Exception):
    pass


def cancel_order(order_id: int) -> None:
    order = Order.objects.get(id=order_id)

    if order.status == Order.Status.SHIPPED:
        raise OrderCannotBeCanceled

    order.status = Order.Status.CANCELED
    order.save(update_fields=["status"])
```

모델에는 상태 추가:

```python
class Status(models.TextChoices):
    PENDING = "pending", "Pending"
    SHIPPED = "shipped", "Shipped"
    CANCELED = "canceled", "Canceled"
```

**4. 리팩터링 방향**

테스트가 통과한 뒤에만 구조를 정리합니다.

```python
# orders/models.py
class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        SHIPPED = "shipped", "Shipped"
        CANCELED = "canceled", "Canceled"

    status = models.CharField(max_length=20, choices=Status.choices)

    def can_cancel(self) -> bool:
        return self.status in {
            self.Status.PENDING,
            self.Status.PAID,
        }

    def cancel(self) -> None:
        if not self.can_cancel():
            raise OrderCannotBeCanceled

        self.status = self.Status.CANCELED
```

서비스는 orchestration만 담당하게 줄입니다.

```python
# orders/services.py
from django.db import transaction

from orders.models import Order


class OrderCannotBeCanceled(Exception):
    pass


@transaction.atomic
def cancel_order(order_id: int) -> None:
    order = Order.objects.select_for_update().get(id=order_id)
    order.cancel()
    order.save(update_fields=["status"])
```

TDD 순서는 이렇게 잡으면 됩니다.

1. 취소 가능한 주문 테스트 작성
2. 실패 확인
3. 상태를 `CANCELED`로 바꾸는 최소 구현
4. 배송 완료 주문 취소 불가 테스트 추가
5. 예외 처리 최소 구현
6. 중복 규칙을 `Order.can_cancel()` / `Order.cancel()`로 이동
7. 동시성 위험이 있으면 `transaction.atomic()`과 `select_for_update()` 적용
8. 환불, 재고 복구, 취소 이력 같은 부가 효과는 각각 별도 실패 테스트로 추가