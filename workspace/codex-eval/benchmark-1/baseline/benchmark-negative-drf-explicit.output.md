현재 `/private/tmp/dddjango-codex-eval` 디렉터리가 비어 있고, 세션이 읽기 전용이라 실제 파일 생성은 할 수 없습니다. 아래는 DRF `ModelViewSet`, `ModelSerializer`, router 포함 구현 예시입니다.

```python
# orders/models.py
from django.db import models


class Order(models.Model):
    customer_name = models.CharField(max_length=100)
    product_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer_name} - {self.product_name}"
```

```python
# orders/serializers.py
from rest_framework import serializers

from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "customer_name",
            "product_name",
            "quantity",
            "total_price",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
```

```python
# orders/views.py
from rest_framework.viewsets import ModelViewSet

from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer
```

```python
# orders/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet

router = DefaultRouter()
router.register("orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
]
```

프로젝트 URL에 연결:

```python
# config/urls.py 또는 project/urls.py
from django.urls import include, path

urlpatterns = [
    path("api/", include("orders.urls")),
]
```

설정도 필요합니다:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "rest_framework",
    "orders",
]
```

마지막으로 마이그레이션:

```bash
python manage.py makemigrations orders
python manage.py migrate
```

생성되는 엔드포인트는 `GET/POST /api/orders/`, `GET/PUT/PATCH/DELETE /api/orders/{id}/` 입니다.