이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다. 현재 `/private/tmp/dddjango-codex-eval`은 비어 있고 읽기 전용이라 파일 생성은 못 했습니다. 아래는 `orders` 앱과 `Order` 모델이 있다고 가정한 Ninja 대체 구현입니다.

**[주요 내용]**

`orders/schemas.py`

```python
from datetime import datetime
from decimal import Decimal
from typing import Optional

from ninja import ModelSchema, Schema

from .models import Order


class ProblemDetails(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str


class OrderOut(ModelSchema):
    class Meta:
        model = Order
        fields = ["id", "customer_id", "status", "total_amount", "created_at", "updated_at"]


class OrderCreateIn(Schema):
    customer_id: int
    status: str
    total_amount: Decimal


class OrderUpdateIn(Schema):
    customer_id: int
    status: str
    total_amount: Decimal


class OrderPatchIn(Schema):
    customer_id: Optional[int] = None
    status: Optional[str] = None
    total_amount: Optional[Decimal] = None
```

`orders/api.py`

```python
from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import LimitOffsetPagination, paginate

from .models import Order
from .schemas import OrderCreateIn, OrderOut, OrderPatchIn, OrderUpdateIn, ProblemDetails

router = Router(tags=["orders"])


def problem(status: int, title: str, detail: str, instance: str) -> ProblemDetails:
    return ProblemDetails(title=title, status=status, detail=detail, instance=instance)


@router.get("", response=List[OrderOut])
@paginate(LimitOffsetPagination)
def list_orders(request):
    return Order.objects.all().order_by("-id")


@router.post("", response={201: OrderOut, 422: ProblemDetails})
def create_order(request, payload: OrderCreateIn):
    order = Order.objects.create(**payload.dict())
    return 201, order


@router.get("/{order_id}", response={200: OrderOut, 404: ProblemDetails})
def get_order(request, order_id: int):
    order = Order.objects.filter(id=order_id).first()
    if order is None:
        return 404, problem(404, "Order not found", f"Order {order_id} does not exist.", request.path)
    return order


@router.put("/{order_id}", response={200: OrderOut, 404: ProblemDetails})
def update_order(request, order_id: int, payload: OrderUpdateIn):
    order = Order.objects.filter(id=order_id).first()
    if order is None:
        return 404, problem(404, "Order not found", f"Order {order_id} does not exist.", request.path)

    for field, value in payload.dict().items():
        setattr(order, field, value)
    order.save(update_fields=["customer_id", "status", "total_amount", "updated_at"])
    return order


@router.patch("/{order_id}", response={200: OrderOut, 404: ProblemDetails})
def patch_order(request, order_id: int, payload: OrderPatchIn):
    order = Order.objects.filter(id=order_id).first()
    if order is None:
        return 404, problem(404, "Order not found", f"Order {order_id} does not exist.", request.path)

    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    order.save(update_fields=[*update_data.keys(), "updated_at"])
    return order


@router.delete("/{order_id}", response={204: None, 404: ProblemDetails})
def delete_order(request, order_id: int):
    deleted, _ = Order.objects.filter(id=order_id).delete()
    if deleted == 0:
        return 404, problem(404, "Order not found", f"Order {order_id} does not exist.", request.path)
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

검증은 이 환경에서 실행하지 못했습니다. 실제 프로젝트에서는 아래를 확인하세요.

```bash
python manage.py check
python manage.py test
python manage.py runserver
```

엔드포인트는 `GET /api/orders`, `POST /api/orders`, `GET /api/orders/{order_id}`, `PUT/PATCH/DELETE /api/orders/{order_id}` 형태입니다.

---
> **관련 스킬 참조:**
> - Django Ninja API 구현 → **implementation-django-ninja** 스킬
> - REST URL/상태 코드 설계 → **architecture-api** 스킬