현재 `/private/tmp/dddjango-codex-eval` 디렉터리가 비어 있고, 세션이 `read-only`라 파일을 생성하거나 수정할 수 없습니다. 아래는 일반적인 Django 앱 `orders` 기준 구현입니다.

`orders/serializers.py`

```python
from rest_framework import serializers

from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
```

`orders/views.py`

```python
from rest_framework.viewsets import ModelViewSet

from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all().order_by("-id")
    serializer_class = OrderSerializer
```

프로젝트 또는 앱의 `urls.py`

```python
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from orders.views import OrderViewSet

router = DefaultRouter()
router.register("orders", OrderViewSet, basename="order")

urlpatterns = [
    path("api/", include(router.urls)),
]
```

필요 조건:

```python
# settings.py
INSTALLED_APPS = [
    ...
    "rest_framework",
    "orders",
]
```

이렇게 하면 기본 엔드포인트는 다음처럼 열립니다.

- `GET /api/orders/`
- `POST /api/orders/`
- `GET /api/orders/{id}/`
- `PUT/PATCH /api/orders/{id}/`
- `DELETE /api/orders/{id}/`