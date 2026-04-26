# Signal 과도 사용 리팩토링

## 문제 진단

기존 코드는 6개의 `post_save` 시그널을 사용하고 있으며, 다음과 같은 문제가 있다:

1. **흐름 추적 불가** -- 시그널은 암묵적 호출이라 `User.save()`를 호출했을 때 프로필 생성과 이메일 발송이 일어난다는 사실을 코드만 보고 알 수 없다.
2. **무한 루프 위험** -- `update_order_total`에서 `instance.save()`를 다시 호출하므로 시그널이 재귀적으로 트리거된다.
3. **테스트 어려움** -- 시그널이 전역으로 등록되어 있어 단위 테스트 시 의도하지 않은 부수 효과(이메일 발송, 재고 차감 등)가 발생한다.
4. **단일 책임 원칙 위반** -- 모델 저장이라는 하나의 이벤트에 여러 무관한 로직(알림, 재고, 집계)이 결합되어 있다.

## 리팩토링 원칙

- **명시적 호출 > 암묵적 시그널** -- 비즈니스 로직은 서비스 레이어에서 명시적으로 호출한다.
- **시그널은 디커플링이 필요한 경우에만** -- 서드파티 앱 연동처럼 소스 코드를 수정할 수 없는 경우에만 시그널을 사용한다.
- **계산 가능한 값은 저장하지 않는다** -- `total_amount`, `product_count`처럼 매번 계산 가능한 값은 프로퍼티나 쿼리로 대체한다.

## 리팩토링 결과

### 1. 서비스 레이어 도입 (`services.py`)

```python
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F, Sum


class UserService:
    @staticmethod
    @transaction.atomic
    def create_user(**kwargs):
        from .models import Profile, User

        user = User.objects.create_user(**kwargs)
        Profile.objects.create(user=user)
        send_mail(
            "환영합니다",
            "가입을 환영합니다.",
            "noreply@site.com",
            [user.email],
        )
        return user


class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order(user, items_data):
        from .models import Order, OrderItem

        order = Order.objects.create(user=user)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
            item_data["product"].stock = F("stock") - item_data["quantity"]
            item_data["product"].save(update_fields=["stock"])

        order.total_amount = order.calculate_total()
        order.save(update_fields=["total_amount"])

        send_mail(
            "주문 알림",
            f"주문 {order.id}",
            "noreply@site.com",
            [user.email],
        )
        return order
```

### 2. 모델 수정 (`models.py`)

```python
from django.db.models import F, Sum


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calculate_total(self):
        return (
            self.items.aggregate(total=Sum(F("price") * F("quantity")))["total"] or 0
        )


class Category(models.Model):
    name = models.CharField(max_length=100)

    @property
    def product_count(self):
        return self.product_set.count()
```

### 3. 시그널 파일 (`signals.py`)

```python
# signals.py -- 시그널 전부 제거
# 모든 로직이 서비스 레이어로 이동했으므로 이 파일은 비어 있다.
```

### 4. 뷰 수정 예시 (`views.py`)

```python
from .services import OrderService, UserService


class SignUpView(View):
    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = UserService.create_user(**form.cleaned_data)
            return redirect("home")
        return render(request, "signup.html", {"form": form})


class OrderCreateView(View):
    def post(self, request):
        items_data = parse_order_items(request.POST)
        order = OrderService.create_order(user=request.user, items_data=items_data)
        return redirect("order_detail", pk=order.pk)
```

## 변경 요약

| 기존 시그널 | 리팩토링 결과 | 이유 |
|---|---|---|
| `create_profile` (User post_save) | `UserService.create_user()` | 유저 생성은 우리 코드가 직접 제어하므로 명시적 호출이 적합 |
| `send_welcome_email` (User post_save) | `UserService.create_user()` | 이메일 발송은 비즈니스 로직이므로 서비스 레이어에 위치 |
| `update_order_total` (Order post_save) | `Order.calculate_total()` + 서비스 레이어 | 무한 루프 위험 제거, 계산 로직을 모델 메서드로 분리 |
| `send_order_notification` (Order post_save) | `OrderService.create_order()` | 알림은 주문 생성 흐름의 일부로 명시적 호출 |
| `update_product_stock` (OrderItem post_save) | `OrderService.create_order()` | 재고 차감은 주문 트랜잭션 안에서 F-expression으로 처리 |
| `update_category_count` (Product post_save) | `Category.product_count` 프로퍼티 | 별도 필드 저장 불필요, 매번 count 쿼리로 충분 |
