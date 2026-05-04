이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다. `ModelSerializer/ViewSet/DefaultRouter` 요청은 아래처럼 `Schema`/`Router`/`NinjaAPI.add_router()`로 전환합니다. 현재 워크스페이스가 읽기 전용이고 파일도 비어 있어 직접 생성은 못 했습니다.

가정: `orders.models.Order`에 `id`, `customer` FK, `status`, `total_amount`, `created_at`, `updated_at` 필드가 있습니다.

`orders/schemas.py`

```python
from datetime import datetime
from decimal import Decimal
from typing import Optional

from ninja import Schema


class OrderOut(Schema):
    id: int
    customer_id: int
    status: str
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime


class OrderCreateIn(Schema):
    customer_id: int
    status: str = "pending"
    total_amount: Decimal


class OrderUpdateIn(Schema):
    customer_id: Optional[int] = None
    status: Optional[str] = None
    total_amount: Optional[Decimal] = None


class ProblemDetail(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str
```

`orders/api.py`

```python
from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import CursorPagination, paginate

from .models import Order
from .schemas import OrderCreateIn, OrderOut, OrderUpdateIn, ProblemDetail

router = Router(tags=["orders"])


@router.get("", response=List[OrderOut])
@paginate(CursorPagination, ordering=("-created_at", "-id"), page_size=50)
def list_orders(request, status: str | None = None):
    qs = Order.objects.select_related("customer").order_by("-created_at", "-id")
    if status is not None:
        qs = qs.filter(status=status)
    return qs


@router.post("", response={201: OrderOut, 400: ProblemDetail})
def create_order(request, payload: OrderCreateIn):
    order = Order.objects.create(**payload.dict())
    return 201, order


@router.get("/{order_id}", response={200: OrderOut, 404: ProblemDetail})
def get_order(request, order_id: int):
    return get_object_or_404(
        Order.objects.select_related("customer"),
        id=order_id,
    )


@router.patch("/{order_id}", response={200: OrderOut, 404: ProblemDetail})
def update_order(request, order_id: int, payload: OrderUpdateIn):
    order = get_object_or_404(Order, id=order_id)
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(order, field, value)
    order.save(update_fields=[*payload.dict(exclude_unset=True).keys(), "updated_at"])
    return order


@router.delete("/{order_id}", response={204: None, 404: ProblemDetail})
def delete_order(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return 204, None
```

`config/api.py`

```python
from ninja import NinjaAPI

from orders.api import router as orders_router

api = NinjaAPI(title="Order API", version="1.0.0")
api.add_router("/orders", orders_router)
```

`config/urls.py`

```python
from django.urls import path

from .api import api

urlpatterns = [
    path("api/", api.urls),
]
```

검증은 제가 실행하지 못했습니다. 적용 후 아래를 확인하면 됩니다.

```bash
python manage.py check
python manage.py test orders
python manage.py runserver
```

확인 URL:

```text
GET    /api/orders
POST   /api/orders
GET    /api/orders/{order_id}
PATCH  /api/orders/{order_id}
DELETE /api/orders/{order_id}
GET    /api/docs
```

---
> **관련 스킬 참조:**
> - Django Ninja API 구현 → **implementation-django-ninja** 스킬
> - REST URL/상태 코드 설계 → **architecture-api** 스킬