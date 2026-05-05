Fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, 현재 워크스페이스에도 fixture 파일이 없었습니다. 그래서 기존 코드 스타일에 맞춘 패치는 만들 수 없고, 빈 `orders` 앱에 적용 가능한 Django Ninja + DDD 예시 diff로 제안합니다.

```diff
diff --git a/orders/domain.py b/orders/domain.py
new file mode 100644
--- /dev/null
+++ b/orders/domain.py
@@ -0,0 +1,64 @@
+from dataclasses import dataclass
+from enum import StrEnum
+
+
+class OrderStatus(StrEnum):
+    PENDING_PAYMENT = "pending_payment"
+    PAID = "paid"
+    CANCEL_REQUESTED = "cancel_requested"
+
+
+class InvalidOrderStatusTransition(Exception):
+    pass
+
+
+@dataclass
+class Order:
+    id: int
+    status: OrderStatus
+
+    def mark_paid(self) -> None:
+        if self.status != OrderStatus.PENDING_PAYMENT:
+            raise InvalidOrderStatusTransition(
+                f"{self.status} 상태에서는 결제 완료로 변경할 수 없습니다."
+            )
+        self.status = OrderStatus.PAID
+
+    def request_cancel(self) -> None:
+        if self.status not in {
+            OrderStatus.PENDING_PAYMENT,
+            OrderStatus.PAID,
+        }:
+            raise InvalidOrderStatusTransition(
+                f"{self.status} 상태에서는 취소 요청할 수 없습니다."
+            )
+        self.status = OrderStatus.CANCEL_REQUESTED
+
+    def change_status(self, target_status: OrderStatus) -> None:
+        if target_status == self.status:
+            return
+
+        if target_status == OrderStatus.PAID:
+            self.mark_paid()
+            return
+
+        if target_status == OrderStatus.CANCEL_REQUESTED:
+            self.request_cancel()
+            return
+
+        raise InvalidOrderStatusTransition(
+            f"{self.status} 상태에서는 {target_status} 상태로 변경할 수 없습니다."
+        )
diff --git a/orders/models.py b/orders/models.py
new file mode 100644
--- /dev/null
+++ b/orders/models.py
@@ -0,0 +1,18 @@
+from django.db import models
+
+from .domain import OrderStatus
+
+
+class OrderModel(models.Model):
+    class Status(models.TextChoices):
+        PENDING_PAYMENT = OrderStatus.PENDING_PAYMENT.value, "결제 대기"
+        PAID = OrderStatus.PAID.value, "결제 완료"
+        CANCEL_REQUESTED = OrderStatus.CANCEL_REQUESTED.value, "취소 요청"
+
+    status = models.CharField(
+        max_length=32,
+        choices=Status.choices,
+        default=Status.PENDING_PAYMENT,
+    )
+    updated_at = models.DateTimeField(auto_now=True)
+
+    class Meta:
+        db_table = "orders"
diff --git a/orders/repositories.py b/orders/repositories.py
new file mode 100644
--- /dev/null
+++ b/orders/repositories.py
@@ -0,0 +1,31 @@
+from dataclasses import dataclass
+
+from .domain import Order, OrderStatus
+from .models import OrderModel
+
+
+class OrderNotFound(Exception):
+    pass
+
+
+@dataclass
+class DjangoOrderRepository:
+    def get(self, order_id: int) -> Order:
+        try:
+            row = OrderModel.objects.get(id=order_id)
+        except OrderModel.DoesNotExist as exc:
+            raise OrderNotFound from exc
+
+        return Order(
+            id=row.id,
+            status=OrderStatus(row.status),
+        )
+
+    def save(self, order: Order) -> None:
+        updated_count = OrderModel.objects.filter(id=order.id).update(
+            status=order.status.value,
+        )
+        if updated_count == 0:
+            raise OrderNotFound
diff --git a/orders/services.py b/orders/services.py
new file mode 100644
--- /dev/null
+++ b/orders/services.py
@@ -0,0 +1,19 @@
+from dataclasses import dataclass
+
+from django.db import transaction
+
+from .domain import Order, OrderStatus
+from .repositories import DjangoOrderRepository
+
+
+@dataclass
+class ChangeOrderStatusService:
+    repository: DjangoOrderRepository
+
+    @transaction.atomic
+    def execute(self, order_id: int, target_status: OrderStatus) -> Order:
+        order = self.repository.get(order_id)
+        order.change_status(target_status)
+        self.repository.save(order)
+        return order
diff --git a/orders/api.py b/orders/api.py
new file mode 100644
--- /dev/null
+++ b/orders/api.py
@@ -0,0 +1,47 @@
+from ninja import Router, Schema
+from ninja.errors import HttpError
+
+from .domain import InvalidOrderStatusTransition, OrderStatus
+from .repositories import DjangoOrderRepository, OrderNotFound
+from .services import ChangeOrderStatusService
+
+router = Router(tags=["orders"])
+
+
+class ChangeOrderStatusRequest(Schema):
+    status: OrderStatus
+
+
+class OrderResponse(Schema):
+    id: int
+    status: OrderStatus
+
+
+@router.patch("/{order_id}/status", response=OrderResponse)
+def change_order_status(request, order_id: int, payload: ChangeOrderStatusRequest):
+    service = ChangeOrderStatusService(
+        repository=DjangoOrderRepository(),
+    )
+
+    try:
+        order = service.execute(
+            order_id=order_id,
+            target_status=payload.status,
+        )
+    except OrderNotFound:
+        raise HttpError(404, "주문을 찾을 수 없습니다.")
+    except InvalidOrderStatusTransition as exc:
+        raise HttpError(409, str(exc))
+
+    return OrderResponse(
+        id=order.id,
+        status=order.status,
+    )
diff --git a/project/api.py b/project/api.py
new file mode 100644
--- /dev/null
+++ b/project/api.py
@@ -0,0 +1,8 @@
+from ninja import NinjaAPI
+
+from orders.api import router as orders_router
+
+api = NinjaAPI()
+api.add_router("/orders", orders_router)
```

상태 전이 기준은 이렇게 잡았습니다.

| 현재 상태 | 요청 상태 | 결과 |
|---|---|---|
| `pending_payment` | `paid` | 허용 |
| `pending_payment` | `cancel_requested` | 허용 |
| `paid` | `cancel_requested` | 허용 |
| `paid` | `pending_payment` | 거부 |
| `cancel_requested` | `paid` / `pending_payment` | 거부 |

핵심은 상태 전이 규칙을 `api.py`나 Django model에 두지 않고 `Order` 도메인 객체 안에 둔 점입니다. API는 입력/출력과 HTTP 에러 매핑만 담당하고, application service는 트랜잭션과 repository 협력만 담당합니다.