이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다. 현재 워크스페이스가 비어 있고 읽기 전용이라 파일을 직접 생성하지 못했습니다. 아래는 `orders` 앱에 붙여 넣을 수 있는 `Schema`/`Router` 기반 주문 API입니다.

**`orders/schemas.py`**
```python
from datetime import datetime
from decimal import Decimal

from ninja import ModelSchema, Schema

from .models import Order


class OrderOut(ModelSchema):
    class Meta:
        model = Order
        fields = ["id", "customer_id", "status", "total_amount", "created_at"]


class OrderCreate(Schema):
    customer_id: int
    status: str
    total_amount: Decimal


class OrderUpdate(Schema):
    customer_id: int
    status: str
    total_amount: Decimal


class OrderPatch(Schema):
    customer_id: int | None = None
    status: str | None = None
    total_amount: Decimal | None = None
```

**`orders/api.py`**
```python
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from .models import Order
from .schemas import OrderCreate, OrderOut, OrderPatch, OrderUpdate

router = Router(tags=["orders"])


@router.get("", response=list[OrderOut])
def list_orders(request: HttpRequest) -> list[Order]:
    return list(Order.objects.order_by("-created_at"))


@router.post("", response={201: OrderOut})
def create_order(request: HttpRequest, payload: OrderCreate) -> tuple[int, Order]:
    order = Order.objects.create(**payload.dict())
    return 201, order


@router.get("/{order_id}", response=OrderOut)
def get_order(request: HttpRequest, order_id: int) -> Order:
    return get_object_or_404(Order, id=order_id)


@router.put("/{order_id}", response=OrderOut)
def update_order(request: HttpRequest, order_id: int, payload: OrderUpdate) -> Order:
    order = get_object_or_404(Order, id=order_id)

    for field, value in payload.dict().items():
        setattr(order, field, value)

    order.save(update_fields=["customer_id", "status", "total_amount"])
    return order


@router.patch("/{order_id}", response=OrderOut)
def patch_order(request: HttpRequest, order_id: int, payload: OrderPatch) -> Order:
    order = get_object_or_404(Order, id=order_id)
    update_data = payload.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(order, field, value)

    order.save(update_fields=list(update_data.keys()))
    return order


@router.delete("/{order_id}", response={204: None})
def delete_order(request: HttpRequest, order_id: int) -> tuple[int, None]:
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return 204, None
```

**`config/api.py`**
```python
from ninja import NinjaAPI

from orders.api import router as orders_router

api = NinjaAPI(title="Order API", version="1.0.0")
api.add_router("/orders", orders_router)
```

**`config/urls.py`**
```python
from django.urls import path

from .api import api

urlpatterns = [
    path("api/", api.urls),
]
```

검증은 읽기 전용 세션이라 실행하지 못했습니다. 적용 후 아래를 실행하세요.

```bash
python manage.py check
python manage.py test
```

---
> **관련 스킬 참조:**
> - Django Ninja API 구현 → **implementation-django-ninja** 스킬