# DRF -> Django Ninja Refactoring

## Original (DRF)

```python
from rest_framework import serializers, viewsets, permissions

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
```

## Refactored (Django Ninja)

### schemas.py

```python
from ninja import ModelSchema
from .models import Order


class OrderSchema(ModelSchema):
    class Meta:
        model = Order
        fields = "__all__"


class OrderCreateSchema(ModelSchema):
    class Meta:
        model = Order
        exclude = ["id"]
```

### api.py

```python
from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.security import django_auth

from .models import Order
from .schemas import OrderCreateSchema, OrderSchema

router = Router(tags=["orders"], auth=django_auth)


@router.get("/", response=List[OrderSchema])
def list_orders(request):
    return Order.objects.all()


@router.get("/{order_id}", response=OrderSchema)
def get_order(request, order_id: int):
    return get_object_or_404(Order, id=order_id)


@router.post("/", response={201: OrderSchema})
def create_order(request, payload: OrderCreateSchema):
    order = Order.objects.create(**payload.dict())
    return 201, order


@router.put("/{order_id}", response=OrderSchema)
def update_order(request, order_id: int, payload: OrderCreateSchema):
    order = get_object_or_404(Order, id=order_id)
    for attr, value in payload.dict().items():
        setattr(order, attr, value)
    order.save()
    return order


@router.patch("/{order_id}", response=OrderSchema)
def patch_order(request, order_id: int, payload: OrderCreateSchema):
    order = get_object_or_404(Order, id=order_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(order, attr, value)
    order.save()
    return order


@router.delete("/{order_id}", response={204: None})
def delete_order(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return 204, None
```

### urls.py (router registration)

```python
from ninja import NinjaAPI
from orders.api import router as orders_router

api = NinjaAPI()
api.add_router("/orders", orders_router)
```

## Key Changes

| DRF | Django Ninja |
|---|---|
| `ModelSerializer` | `ModelSchema` (Pydantic-based) |
| `ModelViewSet` (class-based) | `Router` + function-based endpoints |
| `permissions.IsAuthenticated` | `auth=django_auth` on Router |
| `fields = '__all__'` in serializer | `fields = "__all__"` in schema Meta |
| Implicit CRUD via ViewSet | Explicit endpoint per operation |
| URL routing via `DefaultRouter` | `api.add_router()` for mounting |

## Notes

- `django_auth` uses Django's built-in session authentication and checks `request.user.is_authenticated`, matching the original `IsAuthenticated` behavior.
- `ModelSchema` generates Pydantic fields from the Django model, replacing DRF's `ModelSerializer`.
- `OrderCreateSchema` excludes `id` so it is not required on create/update payloads.
- `exclude_unset=True` in `patch_order` enables true partial updates, only modifying fields the client actually sent.
