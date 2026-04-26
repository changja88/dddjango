# T27: TemplateView에서 N+1 해결을 위한 select_related과 모델 설계

**Skill:** implementation-django-web (Writing mode)
**Cross-skill references loaded:** implementation-django (QuerySet, 모델 설계)

## [주요 내용]

### 모델 설계 (implementation-django 위임)

```python
# orders/models.py
from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "대기중"
        SHIPPED = "shipped", "배송중"
        DELIVERED = "delivered", "배송완료"

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk}"
```

### N+1 해결이 적용된 TemplateView

```python
# web/views/orders/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class OrderListView(LoginRequiredMixin, TemplateView):
    template_name = "orders/orders_root.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # select_related: ForeignKey(Customer) JOIN으로 N+1 방지
        ctx["orders"] = (
            Order.objects
            .select_related("customer")
            .filter(customer__user=self.request.user)
            .order_by("-created_at")[:20]
        )
        return ctx
```

### 선택 기준 (implementation-django 위임)

| 관계 유형 | 사용할 메서드 |
|-----------|-------------|
| ForeignKey, OneToOneField | `select_related()` |
| ManyToManyField, 역참조 FK | `prefetch_related()` |
| 조건부 프리페치 | `Prefetch()` 객체 |

`assertNumQueries`로 쿼리 수를 테스트에서 검증한다.

---
> **관련 스킬 참조:**
> - [QuerySet 최적화, select_related/prefetch_related] → **implementation-django** 스킬
> - [모델 설계, TextChoices] → **implementation-django** 스킬
> - [테스트에서 assertNumQueries] → **implementation-test** 스킬
