이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다. 요청하신 `ModelSerializer`, `ModelViewSet`, `DefaultRouter` 역할은 각각 Django Ninja `ModelSchema`, `Router`, `NinjaAPI.add_router()`로 변환합니다.

현재 workspace는 프로젝트 파일이 없고 읽기 전용이라 파일 생성/수정/테스트 실행은 못 했습니다. 아래는 `orders.Order` 모델이 이미 있다고 가정한 TDD 순서의 붙여넣기용 코드입니다.

**RED: pytest**

`tests/test_orders_api.py`

```python
import pytest
from django.urls import reverse
from ninja.testing import TestClient

from config.api import api
from orders.models import Order


@pytest.mark.django_db
def test_list_orders_returns_authenticated_users_orders(django_user_model):
    user = django_user_model.objects.create_user(
        username="buyer",
        password="password",
    )
    other_user = django_user_model.objects.create_user(username="other")
    owned_order = Order.objects.create(user=user, status=Order.Status.PENDING)
    Order.objects.create(user=other_user, status=Order.Status.PENDING)

    client = TestClient(api)
    client.force_login(user)

    response = client.get("/orders/")

    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["id"] == owned_order.id


@pytest.mark.django_db
def test_create_order_creates_order_for_authenticated_user(django_user_model):
    user = django_user_model.objects.create_user(username="buyer")
    client = TestClient(api)
    client.force_login(user)

    response = client.post(
        "/orders/",
        json={
            "memo": "문 앞에 놓아주세요.",
        },
    )

    assert response.status_code == 201
    order = Order.objects.get(id=response.json()["id"])
    assert order.user == user
    assert order.memo == "문 앞에 놓아주세요."
    assert order.status == Order.Status.PENDING


@pytest.mark.django_db
def test_delete_order_returns_204(django_user_model):
    user = django_user_model.objects.create_user(username="buyer")
    order = Order.objects.create(user=user, status=Order.Status.PENDING)

    client = TestClient(api)
    client.force_login(user)

    response = client.delete(f"/orders/{order.id}")

    assert response.status_code == 204
    assert not Order.objects.filter(id=order.id).exists()
```

예상 RED 실패 이유: `config.api`, `orders.api`, `orders.schemas`, `orders.selectors` 또는 주문 API 라우터가 아직 없어서 import/404 실패가 납니다.

**GREEN: Django Ninja 구현**

`orders/schemas.py`

```python
from datetime import datetime
from typing import Optional

from ninja import ModelSchema, Schema

from orders.models import Order


class ProblemDetailSchema(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str


class OrderCreateSchema(Schema):
    memo: str = ""


class OrderUpdateSchema(Schema):
    memo: Optional[str] = None
    status: Optional[str] = None


class OrderOutSchema(ModelSchema):
    class Meta:
        model = Order
        fields = ["id", "status", "memo", "created_at", "updated_at"]
```

`orders/selectors.py`

```python
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet

from orders.models import Order


def order_list_for_user(user) -> QuerySet[Order]:
    return (
        Order.objects.filter(user=user)
        .select_related("user")
        .order_by("-created_at", "-id")
    )


def order_get_for_user(user, order_id: int) -> Order:
    return get_object_or_404(order_list_for_user(user), id=order_id)
```

`orders/api.py`

```python
from typing import List

from django.db import transaction
from ninja import Router
from ninja.pagination import PageNumberPagination, paginate
from ninja.security import django_auth

from orders.models import Order
from orders.schemas import (
    OrderCreateSchema,
    OrderOutSchema,
    OrderUpdateSchema,
    ProblemDetailSchema,
)
from orders.selectors import order_get_for_user, order_list_for_user

router = Router(auth=django_auth, tags=["orders"])


@router.get(
    "/",
    response=List[OrderOutSchema],
)
@paginate(PageNumberPagination, page_size=20)
def list_orders(request):
    return order_list_for_user(request.user)


@router.post(
    "/",
    response={201: OrderOutSchema},
)
def create_order(request, payload: OrderCreateSchema):
    order = Order.objects.create(
        user=request.user,
        status=Order.Status.PENDING,
        memo=payload.memo,
    )
    return 201, order


@router.get(
    "/{order_id}",
    response={200: OrderOutSchema, 404: ProblemDetailSchema},
)
def get_order(request, order_id: int):
    return order_get_for_user(request.user, order_id)


@router.patch(
    "/{order_id}",
    response={200: OrderOutSchema, 404: ProblemDetailSchema},
)
def update_order(request, order_id: int, payload: OrderUpdateSchema):
    order = order_get_for_user(request.user, order_id)
    update_data = payload.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(order, field, value)

    if update_data:
        order.full_clean()
        order.save(update_fields=[*update_data.keys(), "updated_at"])

    return order


@router.delete(
    "/{order_id}",
    response={204: None, 404: ProblemDetailSchema},
)
def delete_order(request, order_id: int):
    order = order_get_for_user(request.user, order_id)

    with transaction.atomic():
        order.delete()

    return 204, None
```

`config/api.py`

```python
from ninja import NinjaAPI

from orders.api import router as orders_router

api = NinjaAPI(title="Order API")
api.add_router("/orders/", orders_router)
```

`config/urls.py`

```python
from django.contrib import admin
from django.urls import path

from config.api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
```

실행 가능한 환경에서는 아래 순서로 확인하면 됩니다.

```bash
pytest tests/test_orders_api.py
python manage.py check
```

REFACTOR 방향은 주문 생성이 결제, 재고, 알림 같은 부수효과를 갖기 시작할 때 `orders/services.py`로 `order_create()`를 추출하고, 외부 알림은 `transaction.on_commit()` 안에서 호출하도록 분리하는 쪽입니다.

---
> **관련 스킬 참조:**
> - Django Ninja API 구현/테스트 → **implementation-django-ninja** 스킬
> - 주문 도메인 모델/서비스 레이어 → **implementation-django** 스킬