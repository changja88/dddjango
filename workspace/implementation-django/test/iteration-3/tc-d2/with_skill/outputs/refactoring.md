# Signal Overuse Refactoring

## Change 1: User Profile 생성 -- 시그널 유지 (서드파티 모델)

```
[Before]
# users/signals.py
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

[After]
# users/signals.py
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

[Reason] Signals -- django.contrib.auth.User는 서드파티(Django 내장) 모델이므로 save()를
오버라이드할 수 없다. 시그널 사용이 적절한 케이스다. 함수명만 create_user_profile로
명확하게 변경한다.
```

## Change 2: 환영 이메일 발송 -- 시그널에서 서비스 함수로 이동

```
[Before]
# users/signals.py
@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        send_mail('환영합니다', '가입을 환영합니다.', 'noreply@site.com', [instance.email])

[After]
# users/services.py
def user_create(*, email: str, password: str, **extra_fields) -> User:
    """사용자를 생성하고 환영 이메일을 보낸다."""
    user = User.objects.create_user(email=email, password=password, **extra_fields)
    send_mail(
        "환영합니다",
        "가입을 환영합니다.",
        "noreply@site.com",
        [user.email],
    )
    return user

[Reason] Signals / Service Layer -- 환영 이메일은 사용자 생성이라는 비즈니스 흐름의 일부다.
시그널로 처리하면 암묵적 결합이 생기고, 테스트에서 이메일 발송을 제어하기 어렵다.
서비스 함수(user_create)에서 직접 호출하면 흐름이 명시적이고 테스트도 용이하다.
Profile 생성은 Change 1의 시그널이 처리하므로 서비스에서 중복 호출할 필요가 없다.
```

## Change 3: 주문 합계 계산 -- 시그널에서 모델 메서드로 이동

```
[Before]
# orders/signals.py
@receiver(post_save, sender=Order)
def update_order_total(sender, instance, **kwargs):
    total = instance.items.aggregate(
        total=Sum(F('price') * F('quantity'))
    )['total'] or 0
    if instance.total_amount != total:
        instance.total_amount = total
        instance.save()

[After]
# orders/models.py
class Order(models.Model):
    # ... fields ...

    def recalculate_total(self):
        """주문 항목 기반으로 총액을 재계산한다."""
        total = self.items.aggregate(
            total=Sum(F("price") * F("quantity"))
        )["total"] or 0
        if self.total_amount != total:
            self.total_amount = total
            self.save(update_fields=["total_amount"])

[Reason] Signals / Fat Model / Performance -- 같은 앱(orders) 내에서 시그널을 사용하는
것은 안티패턴이다. 모델 메서드로 옮기면 호출 흐름이 명시적이다. 또한 원본 시그널은
instance.save()에서 update_fields를 지정하지 않아 전체 필드를 UPDATE하고,
post_save 시그널이 재귀적으로 트리거될 위험이 있다. save(update_fields=["total_amount"])로
변경 필드만 업데이트하고 재귀를 방지한다.
```

## Change 4: 주문 알림 이메일 -- 시그널에서 서비스 함수로 이동

```
[Before]
# orders/signals.py
@receiver(post_save, sender=Order)
def send_order_notification(sender, instance, created, **kwargs):
    if created:
        send_mail('주문 알림', f'주문 {instance.id}', 'noreply@site.com',
                  [instance.user.email])

[After]
# orders/services.py
def order_create(*, user: User, items: list[dict]) -> Order:
    """주문을 생성하고, 합계를 계산하고, 알림을 보낸다."""
    order = Order.objects.create(user=user)
    order_items = [
        OrderItem(order=order, **item_data)
        for item_data in items
    ]
    OrderItem.objects.bulk_create(order_items)
    order.recalculate_total()
    send_mail(
        "주문 알림",
        f"주문 {order.id}",
        "noreply@site.com",
        [user.email],
    )
    return order

[Reason] Signals / Service Layer -- 주문 생성 알림은 비즈니스 흐름의 일부이므로 서비스
함수에서 명시적으로 호출한다. 시그널에서 이메일을 보내면 테스트나 관리자 일괄 생성 시
의도치 않은 이메일 발송이 발생한다. 서비스 함수를 사용하면 호출자가 완전한 흐름을
제어할 수 있다.
```

## Change 5: 상품 재고 차감 -- 시그널에서 서비스 함수로 이동

```
[Before]
# orders/signals.py
@receiver(post_save, sender=OrderItem)
def update_product_stock(sender, instance, created, **kwargs):
    if created:
        instance.product.stock -= instance.quantity
        instance.product.save()

[After]
# orders/services.py (order_create 서비스에 통합)
def order_create(*, user: User, items: list[dict]) -> Order:
    """주문을 생성하고, 재고를 차감하고, 합계를 계산하고, 알림을 보낸다."""
    order = Order.objects.create(user=user)
    order_items = [
        OrderItem(order=order, **item_data)
        for item_data in items
    ]
    OrderItem.objects.bulk_create(order_items)

    _deduct_stock(order_items)
    order.recalculate_total()

    send_mail(
        "주문 알림",
        f"주문 {order.id}",
        "noreply@site.com",
        [user.email],
    )
    return order


def _deduct_stock(order_items: list[OrderItem]) -> None:
    """주문 항목에 대해 상품 재고를 일괄 차감한다."""
    products_to_update = []
    for item in order_items:
        item.product.stock -= item.quantity
        products_to_update.append(item.product)
    Product.objects.bulk_update(products_to_update, fields=["stock"])

[Reason] Signals / Performance -- 같은 앱 내 시그널을 제거하고 서비스 함수로 통합한다.
원본은 OrderItem마다 개별 product.save()를 호출하여 N번의 UPDATE가 발생한다.
bulk_update로 변경하면 단 1회의 UPDATE 쿼리로 처리된다.
또한 save() 시 update_fields 없이 전체 필드를 덮어쓰는 문제도 해결된다.
```

## Change 6: 카테고리 상품 수 -- 시그널에서 DB 레벨 계산으로 전환

```
[Before]
# products/signals.py
@receiver(post_save, sender=Product)
def update_category_count(sender, instance, **kwargs):
    instance.category.product_count = Product.objects.filter(
        category=instance.category
    ).count()
    instance.category.save()

[After]
# products/models.py
class Category(models.Model):
    name = models.CharField(max_length=100)
    # product_count 필드를 제거하고, 필요할 때 annotate로 계산

# products/selectors.py
def category_list_with_counts():
    """카테고리 목록을 상품 수와 함께 반환한다."""
    return Category.objects.annotate(
        product_count=Count("product")
    ).order_by("name")

[Reason] Signals / QuerySet Patterns -- 비정규화 카운트를 시그널로 동기화하는 것은
경합 조건(race condition)을 유발하고, Product 삭제 시 갱신되지 않는 버그가 있다
(post_save만 연결되어 있으므로). annotate(Count(...))로 DB에서 직접 계산하면
항상 정확한 값을 얻을 수 있고, 별도의 동기화 로직이 필요 없다.
상품 수가 성능 병목이 되는 경우에만 GeneratedField나 캐싱을 고려한다.
```

---

## Complete Refactored Code

### users/signals.py

```python
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """서드파티 모델(User)에 대한 후크 -- 시그널이 적절하다."""
    if created:
        Profile.objects.create(user=instance)
```

### users/services.py

```python
from django.contrib.auth.models import User
from django.core.mail import send_mail


def user_create(*, email: str, password: str, **extra_fields) -> User:
    """사용자를 생성하고 환영 이메일을 보낸다."""
    user = User.objects.create_user(
        email=email,
        password=password,
        **extra_fields,
    )
    # Profile은 post_save 시그널이 자동 생성
    send_mail(
        "환영합니다",
        "가입을 환영합니다.",
        "noreply@site.com",
        [user.email],
    )
    return user
```

### orders/models.py

```python
from decimal import Decimal

from django.db import models
from django.db.models import F, Sum


class Order(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.pk}"

    def recalculate_total(self):
        """주문 항목 기반으로 총액을 재계산한다."""
        total = self.items.aggregate(
            total=Sum(F("price") * F("quantity"))
        )["total"] or Decimal("0")
        if self.total_amount != total:
            self.total_amount = total
            self.save(update_fields=["total_amount"])


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product} x {self.quantity}"
```

### orders/services.py

```python
from django.core.mail import send_mail
from django.db import transaction

from orders.models import Order, OrderItem
from products.models import Product


@transaction.atomic
def order_create(*, user, items: list[dict]) -> Order:
    """주문을 생성하고, 재고를 차감하고, 합계를 계산하고, 알림을 보낸다."""
    order = Order.objects.create(user=user)

    order_items = [
        OrderItem(order=order, **item_data)
        for item_data in items
    ]
    OrderItem.objects.bulk_create(order_items)

    _deduct_stock(order_items)
    order.recalculate_total()

    send_mail(
        "주문 알림",
        f"주문 {order.id}",
        "noreply@site.com",
        [user.email],
    )
    return order


def _deduct_stock(order_items: list[OrderItem]) -> None:
    """주문 항목에 대해 상품 재고를 일괄 차감한다."""
    products_to_update = []
    for item in order_items:
        item.product.stock -= item.quantity
        products_to_update.append(item.product)
    Product.objects.bulk_update(products_to_update, fields=["stock"])
```

### products/models.py

```python
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name
    # product_count 필드를 제거 -- annotate(Count("product"))로 대체


class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
```

### products/selectors.py

```python
from django.db.models import Count

from products.models import Category


def category_list_with_counts():
    """카테고리 목록을 상품 수와 함께 반환한다."""
    return Category.objects.annotate(
        product_count=Count("product")
    ).order_by("name")
```

### orders/signals.py -- 삭제

시그널 파일 전체가 불필요해졌으므로 삭제한다. 모든 로직이 `orders/services.py`와
`orders/models.py`로 이동되었다.

### products/signals.py -- 삭제

시그널 파일 전체가 불필요해졌으므로 삭제한다. 카테고리 상품 수는
`products/selectors.py`의 annotate로 대체되었다.
