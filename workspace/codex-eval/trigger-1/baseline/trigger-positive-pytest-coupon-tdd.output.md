현재 `/private/tmp/dddjango-codex-eval`은 빈 디렉터리이고 read-only 샌드박스라 파일 생성/수정과 `pytest` 실행을 할 수 없었습니다. 그래서 실제 구현 완료라고 말할 수는 없습니다. 대신 TDD 흐름대로 바로 옮길 수 있는 최소 패치를 정리합니다.

**RED 테스트 예시**

`tests/isolated/orders/test_coupon_apply.py`

```python
import pytest
from django.utils import timezone

from apps.orders.models import Coupon, Order
from apps.orders.services import apply_coupon
from apps.orders.exceptions import InvalidCouponError


pytestmark = pytest.mark.django_db


def test_apply_coupon_valid_fixed_coupon_updates_order_total():
    # Arrange
    order = Order.objects.create(subtotal=10000)
    Coupon.objects.create(code="SAVE3000", discount_amount=3000, is_active=True)

    # Act
    result = apply_coupon(order_id=order.id, code="SAVE3000")

    # Assert
    order.refresh_from_db()
    assert result.discount_amount == 3000
    assert order.discount_amount == 3000
    assert order.total_amount == 7000
    assert order.coupon.code == "SAVE3000"


def test_apply_coupon_inactive_coupon_raises_invalid_coupon_error():
    # Arrange
    order = Order.objects.create(subtotal=10000)
    Coupon.objects.create(code="SAVE3000", discount_amount=3000, is_active=False)

    # Act / Assert
    with pytest.raises(InvalidCouponError):
        apply_coupon(order_id=order.id, code="SAVE3000")


def test_apply_coupon_discount_never_makes_total_negative():
    # Arrange
    order = Order.objects.create(subtotal=2000)
    Coupon.objects.create(code="SAVE3000", discount_amount=3000, is_active=True)

    # Act
    result = apply_coupon(order_id=order.id, code="SAVE3000")

    # Assert
    order.refresh_from_db()
    assert result.discount_amount == 2000
    assert order.total_amount == 0
```

예상 실패 이유: 아직 `apps.orders.models.Coupon`, `Order`, `apps.orders.services.apply_coupon`, `InvalidCouponError`가 없거나 동작이 구현되지 않았기 때문에 RED가 됩니다.

**GREEN 최소 구현**

`apps/orders/exceptions.py`

```python
class InvalidCouponError(ValueError):
    pass
```

`apps/orders/models.py`

```python
from django.core.validators import MinValueValidator
from django.db import models


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_amount = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]
        indexes = [models.Index(fields=["code"])]

    def __str__(self):
        return self.code


class Order(models.Model):
    subtotal = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    coupon = models.ForeignKey(
        Coupon,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
    )
    discount_amount = models.PositiveIntegerField(default=0)
    total_amount = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-id"]

    def apply_discount(self, coupon):
        discount = min(self.subtotal, coupon.discount_amount)
        self.coupon = coupon
        self.discount_amount = discount
        self.total_amount = self.subtotal - discount
        return discount
```

`apps/orders/services.py`

```python
from dataclasses import dataclass

from django.db import transaction

from apps.orders.exceptions import InvalidCouponError
from apps.orders.models import Coupon, Order


@dataclass(frozen=True)
class ApplyCouponResult:
    order_id: int
    coupon_code: str
    discount_amount: int
    total_amount: int


@transaction.atomic
def apply_coupon(*, order_id: int, code: str) -> ApplyCouponResult:
    order = Order.objects.select_for_update().get(id=order_id)

    try:
        coupon = Coupon.objects.get(code=code)
    except Coupon.DoesNotExist as exc:
        raise InvalidCouponError("사용할 수 없는 쿠폰입니다.") from exc

    if not coupon.is_active:
        raise InvalidCouponError("사용할 수 없는 쿠폰입니다.")

    discount = order.apply_discount(coupon)
    order.save(update_fields=["coupon", "discount_amount", "total_amount"])

    return ApplyCouponResult(
        order_id=order.id,
        coupon_code=coupon.code,
        discount_amount=discount,
        total_amount=order.total_amount,
    )
```

**REFACTOR 방향**

다음 TDD 사이클에서 `Coupon.is_active` BooleanField는 `status = TextChoices(...)`로 바꾸는 게 좋습니다. 만료일, 최소 주문 금액, 사용 횟수 제한, 퍼센트 할인까지 추가되면 `Coupon.can_apply_to(order, now)`와 `Coupon.calculate_discount(order)`로 모델 메서드를 분리하고, 동시 사용량 제한은 `select_for_update()`로 쿠폰 행을 잠근 뒤 처리하세요.

실행 명령:

```bash
pytest tests/isolated/orders/test_coupon_apply.py -q
```

실제 실행은 하지 못했습니다. 현재 작업 디렉터리에 Django 프로젝트 파일이 없고 파일 쓰기 권한도 없습니다.

---
> **관련 스킬 참조:**
> - Django 구현 패턴 → **implementation-django** 스킬
> - pytest 테스트 작성 → **implementation-test** 스킬
> - Red-Green-Refactor 진행 → **implementation-tdd** 스킬