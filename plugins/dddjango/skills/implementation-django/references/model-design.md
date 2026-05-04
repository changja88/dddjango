# 모델 설계 패턴

## Fat Model, Thin View 원칙 [TSD]

비즈니스 로직은 뷰가 아닌 모델(또는 서비스 레이어)에 둔다. Two Scoops of Django는 이를 **"Fat Models, Utility Modules, Thin Views, Stupid Templates"**로 정리한다.

```python
# 나쁜 예: 뷰에 비즈니스 로직 집중
class OrderView(View):
    def post(self, request):
        order = Order.objects.get(pk=request.POST["order_id"])
        if order.total > 100:
            order.discount = order.total * 0.1
        order.status = "confirmed"
        order.save()
        send_mail("Order confirmed", ..., [order.user.email])
        return redirect("order-detail", pk=order.pk)

# 좋은 예: 모델에 비즈니스 로직 캡슐화
class Order(models.Model):
    def confirm(self):
        """주문을 확정하고 할인을 적용한다."""
        if self.total > 100:
            self.discount = self.total * Decimal("0.1")
        self.status = self.Status.CONFIRMED
        self.save(update_fields=["discount", "status"])
        self.send_confirmation_email()

    def send_confirmation_email(self):
        send_mail("Order confirmed", ..., [self.user.email])

# 뷰는 얇게
class OrderConfirmView(View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        order.confirm()
        return redirect("order-detail", pk=order.pk)
```

단, 모델이 2000줄 이상으로 비대해지면 서비스 레이어 분리를 검토한다.

## 모델 상속 패턴 [DDoc]

### Abstract Base Class (추상 베이스 클래스) -- 권장

```python
# 좋은 예: 공통 필드를 추상 클래스로 추출
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # 테이블을 생성하지 않음

class Article(TimeStampedModel):
    title = models.CharField(max_length=200)
    body = models.TextField()
    # created_at, updated_at 자동 상속
```

- 테이블을 생성하지 않아 조인 비용이 없다.
- 여러 모델에서 공통 필드를 재사용할 때 가장 적합하다.

### Multi-table Inheritance -- 주의해서 사용

```python
# 주의: 각 모델마다 별도 테이블 생성 + 암묵적 OneToOneField
class Place(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=80)

class Restaurant(Place):  # place_ptr 자동 생성
    serves_pizza = models.BooleanField(default=False)
```

- 조회 시 자동으로 JOIN이 발생하여 성능 저하 가능.
- 대부분의 경우 **Abstract Base Class + 명시적 ForeignKey**가 더 낫다. [TSD]

### Proxy Model -- Python 레벨 동작 변경

```python
class Order(models.Model):
    status = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

class ExpensiveOrder(Order):
    """고가 주문만 필터링하는 프록시 모델."""
    class Meta:
        proxy = True

    objects = ExpensiveOrderManager()

    def apply_premium_discount(self):
        self.amount *= Decimal("0.95")
        self.save(update_fields=["amount"])
```

- 테이블 구조를 변경하지 않고 Python 레벨 동작(매니저, 메서드)만 변경한다.

## 필드 선택 가이드 [DDoc]

```python
# 나쁜 예: BooleanField 남발로 상태 폭발
class Task(models.Model):
    is_started = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    # is_started=True, is_completed=True, is_cancelled=True 같은
    # 불가능한 상태 조합이 가능

# 좋은 예: TextChoices로 상태를 하나의 필드에 표현
class Task(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        STARTED = "started", "Started"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.PENDING,
    )
```

- `CharField` + `TextChoices`는 DB에서 직접 읽을 때 가독성이 좋다.
- `JSONField`는 스키마 없는 데이터에만 사용하고, 구조화된 데이터에는 정규 필드를 사용한다.
- `DecimalField`를 금액에 사용하고, `FloatField`는 피한다.

## 모델 유효성 검증 [DDoc]

```python
class Event(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()

    def clean(self):
        """모델 레벨 교차 필드 유효성 검증."""
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError(
                {"end_date": "종료일은 시작일 이후여야 합니다."}
            )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F("start_date")),
                name="event_end_after_start",
            ),
        ]
```

- `clean()` 메서드로 Python 레벨 검증을 수행한다.
- `CheckConstraint`로 데이터베이스 레벨 제약도 함께 건다 (이중 방어).
- `full_clean()`은 `save()` 시 자동 호출되지 않으므로, 폼이나 API 입력 검증 계층(Django Ninja Schema 등)을 통해 호출되도록 한다.
