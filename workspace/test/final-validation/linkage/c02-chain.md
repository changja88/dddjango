# 주문 관리: 웹 페이지 + REST API 이중 인터페이스 설계

## 프로젝트 구조

서비스 레이어를 공유하면서 웹(Django 템플릿)과 API(Django Ninja)를 분리하는
Two Scoops 레이아웃이다. 핵심은 `orders/services.py`와 `orders/selectors.py`가
단일 진실의 원천(single source of truth)이 되고, 웹 뷰와 API 엔드포인트 모두
이 레이어를 호출하는 구조다.

```
repository_root/
    config/
        __init__.py
        settings/
            __init__.py
            base.py
            local.py
            production.py
            test.py
        urls.py
        api.py                   # NinjaAPI 인스턴스, 라우터 합성
        wsgi.py
        asgi.py
    apps/
        orders/
            __init__.py
            models.py            # Order, OrderItem 모델
            services.py          # 쓰기(Command) 로직
            selectors.py         # 읽기(Query) 로직
            schemas.py           # Django Ninja Schema
            api.py               # Django Ninja Router
            forms.py             # Django ModelForm
            admin.py
            tests/
                __init__.py
                test_models.py
                test_services.py
                test_api.py
                test_views.py
    web/
        view_urls.py             # 웹 뷰 URL 패턴
        views/
            __init__.py
            orders/
                __init__.py
                views.py         # TemplateView 기반 주문 페이지
        templates/
            base.html
            orders/
                orders_root.html
                order_detail.html
                order_create.html
    manage.py
```

`apps/orders/`는 도메인 로직(모델, 서비스, 셀렉터)과 API를 담당하고,
`web/`은 프레젠테이션 계층(템플릿, 웹 뷰)을 담당한다.

## 모델

```python
# apps/orders/models.py
from decimal import Decimal

from django.conf import settings
from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        SHIPPED = "shipped", "Shipped"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.DRAFT,
        db_default=Status.DRAFT,
    )
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0")
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(total_amount__gte=0),
                name="order_total_non_negative",
            ),
        ]

    def __str__(self):
        return f"Order #{self.pk} ({self.get_status_display()})"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name="orderitem_quantity_positive",
            ),
        ]

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"
```

## 서비스 레이어 (공유)

서비스는 쓰기 로직, 셀렉터는 읽기 로직을 담당한다. 웹 뷰와 API 엔드포인트
모두 이 함수들을 호출한다.

```python
# apps/orders/services.py
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import Order, OrderItem


def order_create(
    *,
    user,
    items: list[dict],
    note: str = "",
) -> Order:
    with transaction.atomic():
        order = Order.objects.create(user=user, note=note)
        order_items = [
            OrderItem(
                order=order,
                product_name=item["product_name"],
                quantity=item["quantity"],
                unit_price=Decimal(str(item["unit_price"])),
            )
            for item in items
        ]
        OrderItem.objects.bulk_create(order_items)
        order.total_amount = sum(
            i.quantity * i.unit_price for i in order_items
        )
        order.save(update_fields=["total_amount"])
    return order


def order_confirm(*, order: Order) -> Order:
    if order.status != Order.Status.DRAFT:
        raise ValidationError("확정할 수 없는 상태입니다.")
    order.status = Order.Status.CONFIRMED
    order.save(update_fields=["status", "updated_at"])
    transaction.on_commit(lambda: _send_order_confirmation(order))
    return order


def order_cancel(*, order: Order) -> Order:
    non_cancellable = {Order.Status.SHIPPED, Order.Status.CANCELLED}
    if order.status in non_cancellable:
        raise ValidationError("취소할 수 없는 상태입니다.")
    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status", "updated_at"])
    return order


def _send_order_confirmation(order: Order) -> None:
    pass  # 이메일/알림 발송
```

```python
# apps/orders/selectors.py
from django.db.models import QuerySet

from .models import Order


def order_list(*, user, status: str | None = None) -> QuerySet[Order]:
    qs = Order.objects.filter(user=user).select_related("user")
    if status:
        qs = qs.filter(status=status)
    return qs


def order_detail(*, pk: int, user) -> Order:
    return (
        Order.objects.select_related("user")
        .prefetch_related("items")
        .get(pk=pk, user=user)
    )
```

## API 인터페이스 (Django Ninja)

```python
# apps/orders/schemas.py
from datetime import datetime
from decimal import Decimal

from ninja import ModelSchema, Schema

from .models import Order, OrderItem


class OrderItemIn(Schema):
    product_name: str
    quantity: int
    unit_price: Decimal


class OrderItemOut(ModelSchema):
    class Meta:
        model = OrderItem
        fields = ["id", "product_name", "quantity", "unit_price"]


class OrderIn(Schema):
    items: list[OrderItemIn]
    note: str = ""


class OrderOut(ModelSchema):
    items: list[OrderItemOut] = []

    class Meta:
        model = Order
        fields = ["id", "status", "total_amount", "note", "created_at"]

    @staticmethod
    def resolve_items(obj):
        return obj.items.all()


class OrderListOut(ModelSchema):
    class Meta:
        model = Order
        fields = ["id", "status", "total_amount", "created_at"]
```

```python
# apps/orders/api.py
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import LimitOffsetPagination, paginate

from . import selectors, services
from .models import Order
from .schemas import OrderIn, OrderListOut, OrderOut

router = Router(tags=["orders"])


@router.get("/", response=list[OrderListOut])
@paginate(LimitOffsetPagination)
def list_orders(request, status: str | None = None):
    return selectors.order_list(user=request.user, status=status)


@router.get("/{order_id}", response=OrderOut)
def get_order(request, order_id: int):
    return selectors.order_detail(pk=order_id, user=request.user)


@router.post("/", response={201: OrderOut})
def create_order(request, payload: OrderIn):
    order = services.order_create(
        user=request.user,
        items=[item.dict() for item in payload.items],
        note=payload.note,
    )
    return 201, selectors.order_detail(pk=order.pk, user=request.user)


@router.post("/{order_id}/confirm", response=OrderOut)
def confirm_order(request, order_id: int):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    services.order_confirm(order=order)
    return selectors.order_detail(pk=order.pk, user=request.user)


@router.post("/{order_id}/cancel", response=OrderOut)
def cancel_order(request, order_id: int):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    services.order_cancel(order=order)
    return selectors.order_detail(pk=order.pk, user=request.user)
```

```python
# config/api.py
from ninja import NinjaAPI

from apps.orders.api import router as orders_router

api = NinjaAPI()
api.add_router("/orders/", orders_router)
```

```python
# config/urls.py
from django.contrib import admin
from django.urls import path

from .api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
```

## 웹 인터페이스 (Django 템플릿)

웹 뷰는 동일한 서비스/셀렉터 함수를 직접 호출한다.
모놀리스 프로젝트에서는 Internal API Client 패턴(HTTP 왕복)보다
직접 서비스 호출이 성능과 단순성 모두에서 유리하다.

```python
# web/views/orders/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView

from apps.orders import selectors, services
from apps.orders.forms import OrderCreateForm
from apps.orders.models import Order


class OrderListView(LoginRequiredMixin, TemplateView):
    template_name = "orders/orders_root.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        status = self.request.GET.get("status")
        ctx["orders"] = selectors.order_list(
            user=self.request.user, status=status
        )
        ctx["status_choices"] = Order.Status.choices
        return ctx


class OrderDetailView(LoginRequiredMixin, TemplateView):
    template_name = "orders/order_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["order"] = selectors.order_detail(
            pk=kwargs["pk"], user=self.request.user
        )
        return ctx


class OrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = OrderCreateForm()
        return self._render(request, form)

    def post(self, request):
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = services.order_create(
                user=request.user,
                items=form.cleaned_data["items"],
                note=form.cleaned_data["note"],
            )
            return redirect("web:order-detail", pk=order.pk)
        return self._render(request, form)

    def _render(self, request, form):
        from django.template.response import TemplateResponse

        return TemplateResponse(
            request, "orders/order_create.html", {"form": form}
        )


class OrderConfirmView(LoginRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        try:
            services.order_confirm(order=order)
        except ValidationError as e:
            from django.contrib import messages

            messages.error(request, str(e.message))
        return redirect("web:order-detail", pk=pk)


class OrderCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        try:
            services.order_cancel(order=order)
        except ValidationError as e:
            from django.contrib import messages

            messages.error(request, str(e.message))
        return redirect("web:order-detail", pk=pk)
```

```python
# web/view_urls.py
from django.urls import path

from .views.orders.views import (
    OrderCancelView,
    OrderConfirmView,
    OrderCreateView,
    OrderDetailView,
    OrderListView,
)

app_name = "web"

urlpatterns = [
    path("orders/", OrderListView.as_view(), name="orders"),
    path("orders/create/", OrderCreateView.as_view(), name="order-create"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path(
        "orders/<int:pk>/confirm/",
        OrderConfirmView.as_view(),
        name="order-confirm",
    ),
    path(
        "orders/<int:pk>/cancel/",
        OrderCancelView.as_view(),
        name="order-cancel",
    ),
]
```

```python
# config/urls.py (최종)
from django.contrib import admin
from django.urls import include, path

from .api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("", include("web.view_urls")),
]
```

## 핵심 설계 원칙 요약

| 레이어 | 역할 | 위치 |
|--------|------|------|
| 모델 | DB 스키마, 필드 검증, `__str__` | `apps/orders/models.py` |
| 서비스 | 쓰기 비즈니스 로직, 트랜잭션 | `apps/orders/services.py` |
| 셀렉터 | 읽기 쿼리 로직 | `apps/orders/selectors.py` |
| API | Schema 검증, HTTP 응답, 페이지네이션 | `apps/orders/schemas.py`, `api.py` |
| 웹 뷰 | 템플릿 렌더링, 폼 처리, 리다이렉트 | `web/views/orders/views.py` |

웹 뷰와 API 엔드포인트 모두 서비스/셀렉터를 직접 호출하므로,
비즈니스 로직이 한 곳에만 존재한다. 새로운 규칙(할인 정책, 상태
전이 제한 등)을 추가할 때 서비스 함수만 수정하면 두 인터페이스에
동시에 반영된다.

---
> **관련 스킬 참조:**
> - Django Ninja Schema, Router, 인증, 페이지네이션 패턴 → **implementation-django-ninja** 스킬
> - Django 템플릿 상속, 컴포넌트 합성, 정적 파일, TemplateView 패턴 → **implementation-django-web** 스킬
> - REST API 설계 원칙(엔드포인트 네이밍, 상태 코드, 버저닝) → **architecture-api** 스킬
> - 헥사고날 아키텍처, CQRS 등 고급 아키텍처 패턴 → **architecture-implementation-patterns** 스킬
> - Python 타입 힌트, dataclasses, async 패턴 → **implementation-python** 스킬
