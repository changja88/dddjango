# 시그널 사용 가이드라인

## 시그널을 사용해야 하는 경우 [DDoc]

```python
# 좋은 예 1: 서드파티 라이브러리 모델에 후크 (코드를 직접 수정 불가)
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# 좋은 예 2: 순환 의존 방지
# app_a가 app_b에 의존하는데, app_b에서 app_a의 동작을 트리거해야 할 때
# app_b는 시그널을 보내고, app_a는 리시버를 연결한다.
```

**시그널이 적절한 경우:**
- 제어할 수 없는 서드파티 모델에 반응할 때
- 순환 의존을 만들지 않고 앱 간 통신이 필요할 때
- 많은 수의 모델에 같은 핸들러를 일괄 적용할 때

## 시그널을 피해야 하는 경우 (안티패턴) [HS]

```python
# 나쁜 예: 같은 앱 내에서 시그널 사용 -- 직접 호출이 더 명확
@receiver(post_save, sender=Order)
def send_order_email(sender, instance, created, **kwargs):
    if created:
        send_confirmation_email(instance)

# 좋은 예: save() 오버라이드 또는 서비스 함수에서 직접 호출
class Order(models.Model):
    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            send_confirmation_email(self)

# 또는 서비스 레이어에서
def order_create(*, user, items):
    order = Order.objects.create(user=user)
    order.add_items(items)
    send_confirmation_email(order)
    return order
```

**시그널을 피해야 하는 경우:**
- 두 컴포넌트가 이미 결합되어 있을 때 -- 시그널은 진정한 디커플링이 아닌 암묵적 결합만 만든다.
- `save()`/`delete()` 오버라이드로 충분할 때.
- `request_started`/`request_finished`는 미들웨어로 대체 가능.
- 시그널은 **동기적**으로 실행되며, 예외가 발생하면 트리거한 함수로 전파된다.
