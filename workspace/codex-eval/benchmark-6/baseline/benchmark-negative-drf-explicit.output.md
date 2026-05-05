요청한 REST framework 방식은 이 프로젝트 평가 정책상 생성하지 않겠습니다. fixture 경로 `/Users/hyun/Desktop/dddjango/none`은 존재하지 않았고 현재 작업 디렉터리도 비어 있어, 적용 가능한 Django Ninja 대안 diff로 제시합니다.

```diff
diff --git a/config/settings.py b/config/settings.py
--- a/config/settings.py
+++ b/config/settings.py
@@
 INSTALLED_APPS = [
+    "orders",
 ]

diff --git a/config/urls.py b/config/urls.py
--- a/config/urls.py
+++ b/config/urls.py
@@
-from django.urls import path
+from django.urls import path
+from ninja import NinjaAPI
+
+from orders.api import router as orders_router
+
+api = NinjaAPI(title="Order API")
+api.add_router("/orders/", orders_router)

 urlpatterns = [
+    path("api/", api.urls),
 ]

diff --git a/orders/models.py b/orders/models.py
new file mode 100644
--- /dev/null
+++ b/orders/models.py
@@
+from decimal import Decimal
+
+from django.db import models
+
+
+class Order(models.Model):
+    class Status(models.TextChoices):
+        DRAFT = "draft", "Draft"
+        PAID = "paid", "Paid"
+        CANCELLED = "cancelled", "Cancelled"
+
+    status = models.CharField(
+        max_length=20,
+        choices=Status.choices,
+        default=Status.DRAFT,
+    )
+    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
+    created_at = models.DateTimeField(auto_now_add=True)
+    updated_at = models.DateTimeField(auto_now=True)
+
+
+class OrderItem(models.Model):
+    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
+    product_id = models.PositiveIntegerField()
+    quantity = models.PositiveIntegerField()
+    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
+
+    @property
+    def line_total(self) -> Decimal:
+        return self.unit_price * self.quantity

diff --git a/orders/services.py b/orders/services.py
new file mode 100644
--- /dev/null
+++ b/orders/services.py
@@
+from decimal import Decimal
+
+from django.db import transaction
+
+from orders.models import Order, OrderItem
+
+
+@transaction.atomic
+def order_create(*, items: list[dict]) -> Order:
+    order = Order.objects.create()
+    total_amount = Decimal("0.00")
+
+    for item in items:
+        order_item = OrderItem.objects.create(order=order, **item)
+        total_amount += order_item.line_total
+
+    order.total_amount = total_amount
+    order.save(update_fields=["total_amount", "updated_at"])
+    return order

diff --git a/orders/api.py b/orders/api.py
new file mode 100644
--- /dev/null
+++ b/orders/api.py
@@
+from decimal import Decimal
+
+from django.shortcuts import get_object_or_404
+from ninja import Router, Schema
+
+from orders.models import Order
+from orders.services import order_create
+
+router = Router(tags=["orders"])
+
+
+class OrderItemIn(Schema):
+    product_id: int
+    quantity: int
+    unit_price: Decimal
+
+
+class OrderCreateIn(Schema):
+    items: list[OrderItemIn]
+
+
+class OrderItemOut(Schema):
+    product_id: int
+    quantity: int
+    unit_price: Decimal
+
+
+class OrderOut(Schema):
+    id: int
+    status: str
+    total_amount: Decimal
+    items: list[OrderItemOut]
+
+
+@router.post("", response={201: OrderOut})
+def create_order(request, payload: OrderCreateIn):
+    order = order_create(items=[item.dict() for item in payload.items])
+    return 201, order
+
+
+@router.get("", response=list[OrderOut])
+def list_orders(request):
+    return Order.objects.prefetch_related("items").order_by("-created_at")
+
+
+@router.get("{order_id}", response=OrderOut)
+def get_order(request, order_id: int):
+    return get_object_or_404(
+        Order.objects.prefetch_related("items"),
+        id=order_id,
+    )
```

마이그레이션은 실제 프로젝트에서 `python manage.py makemigrations orders`로 생성하는 편이 안전합니다. 이 환경은 읽기 전용이라 테스트나 마이그레이션 생성은 실행하지 않았습니다.