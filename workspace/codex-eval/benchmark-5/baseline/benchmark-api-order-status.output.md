지정된 fixture path `/Users/hyun/Desktop/dddjango/none`는 존재하지 않아 읽을 파일이 없었습니다. 그래서 특정 코드베이스 스타일에는 맞추지 못했고, 읽기 전용 조건에 맞춰 “추가 적용 가능한 예시 diff”로 제안합니다.

```diff
diff --git a/orders/domain/order.py b/orders/domain/order.py
new file mode 100644
--- /dev/null
+++ b/orders/domain/order.py
@@ -0,0 +1,69 @@
+from dataclasses import dataclass
+from enum import StrEnum
+
+
+class OrderStatus(StrEnum):
+    PAYMENT_PENDING = "payment_pending"
+    PAID = "paid"
+    CANCEL_REQUESTED = "cancel_requested"
+
+
+class OrderStatusTransitionError(Exception):
+    pass
+
+
+@dataclass
+class Order:
+    id: int
+    status: OrderStatus
+
+    def mark_paid(self) -> None:
+        if self.status != OrderStatus.PAYMENT_PENDING:
+            raise OrderStatusTransitionError("결제 대기 상태의 주문만 결제 완료로 변경할 수 있습니다.")
+        self.status = OrderStatus.PAID
+
+    def request_cancel(self) -> None:
+        if self.status not in {OrderStatus.PAYMENT_PENDING, OrderStatus.PAID}:
+            raise OrderStatusTransitionError("취소 요청할 수 없는 주문 상태입니다.")
+        self.status = OrderStatus.CANCEL_REQUESTED
+
+    def change_status(self, target_status: OrderStatus) -> None:
+        if target_status == OrderStatus.PAID:
+            self.mark_paid()
+            return
+
+        if target_status == OrderStatus.CANCEL_REQUESTED:
+            self.request_cancel()
+            return
+
+        if target_status == self.status:
+            return
+
+        raise OrderStatusTransitionError("허용되지 않은 주문 상태 변경입니다.")
diff --git a/orders/application/change_order_status.py b/orders/application/change_order_status.py
new file mode 100644
--- /dev/null
+++ b/orders/application/change_order_status.py
@@ -0,0 +1,34 @@
+from dataclasses import dataclass
+from typing import Protocol
+
+from orders.domain.order import Order, OrderStatus
+
+
+class OrderNotFound(Exception):
+    pass
+
+
+class OrderRepository(Protocol):
+    def get(self, order_id: int) -> Order | None:
+        ...
+
+    def save(self, order: Order) -> None:
+        ...
+
+
+@dataclass(frozen=True)
+class ChangeOrderStatusCommand:
+    order_id: int
+    target_status: OrderStatus
+
+
+class ChangeOrderStatusUseCase:
+    def __init__(self, orders: OrderRepository):
+        self.orders = orders
+
+    def execute(self, command: ChangeOrderStatusCommand) -> Order:
+        order = self.orders.get(command.order_id)
+        if order is None:
+            raise OrderNotFound
+
+        order.change_status(command.target_status)
+        self.orders.save(order)
+        return order
diff --git a/orders/infra/models.py b/orders/infra/models.py
new file mode 100644
--- /dev/null
+++ b/orders/infra/models.py
@@ -0,0 +1,16 @@
+from django.db import models
+
+from orders.domain.order import OrderStatus
+
+
+class OrderModel(models.Model):
+    class Status(models.TextChoices):
+        PAYMENT_PENDING = OrderStatus.PAYMENT_PENDING.value, "결제 대기"
+        PAID = OrderStatus.PAID.value, "결제 완료"
+        CANCEL_REQUESTED = OrderStatus.CANCEL_REQUESTED.value, "취소 요청"
+
+    status = models.CharField(
+        max_length=32,
+        choices=Status.choices,
+        default=Status.PAYMENT_PENDING,
+    )
+    updated_at = models.DateTimeField(auto_now=True)
diff --git a/orders/infra/repositories.py b/orders/infra/repositories.py
new file mode 100644
--- /dev/null
+++ b/orders/infra/repositories.py
@@ -0,0 +1,26 @@
+from django.db import transaction
+
+from orders.domain.order import Order, OrderStatus
+from orders.infra.models import OrderModel
+
+
+class DjangoOrderRepository:
+    def get(self, order_id: int) -> Order | None:
+        row = (
+            OrderModel.objects
+            .select_for_update()
+            .filter(id=order_id)
+            .first()
+        )
+        if row is None:
+            return None
+
+        return Order(
+            id=row.id,
+            status=OrderStatus(row.status),
+        )
+
+    def save(self, order: Order) -> None:
+        OrderModel.objects.filter(id=order.id).update(status=order.status.value)
+
+    @staticmethod
+    def atomic():
+        return transaction.atomic()
diff --git a/orders/api/schemas.py b/orders/api/schemas.py
new file mode 100644
--- /dev/null
+++ b/orders/api/schemas.py
@@ -0,0 +1,15 @@
+from ninja import Schema
+
+from orders.domain.order import OrderStatus
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
+class ErrorResponse(Schema):
+    detail: str
diff --git a/orders/api/router.py b/orders/api/router.py
new file mode 100644
--- /dev/null
+++ b/orders/api/router.py
@@ -0,0 +1,42 @@
+from ninja import Router
+
+from orders.api.schemas import ChangeOrderStatusRequest, ErrorResponse, OrderResponse
+from orders.application.change_order_status import (
+    ChangeOrderStatusCommand,
+    ChangeOrderStatusUseCase,
+    OrderNotFound,
+)
+from orders.domain.order import OrderStatusTransitionError
+from orders.infra.repositories import DjangoOrderRepository
+
+router = Router(tags=["orders"])
+
+
+@router.patch(
+    "/orders/{order_id}/status",
+    response={
+        200: OrderResponse,
+        400: ErrorResponse,
+        404: ErrorResponse,
+    },
+)
+def change_order_status(request, order_id: int, payload: ChangeOrderStatusRequest):
+    repository = DjangoOrderRepository()
+    use_case = ChangeOrderStatusUseCase(repository)
+
+    try:
+        with repository.atomic():
+            order = use_case.execute(
+                ChangeOrderStatusCommand(
+                    order_id=order_id,
+                    target_status=payload.status,
+                )
+            )
+    except OrderNotFound:
+        return 404, {"detail": "주문을 찾을 수 없습니다."}
+    except OrderStatusTransitionError as exc:
+        return 400, {"detail": str(exc)}
+
+    return 200, {
+        "id": order.id,
+        "status": order.status,
+    }
```

상태 전이 기준은 다음처럼 둡니다.

```text
payment_pending -> paid
payment_pending -> cancel_requested
paid            -> cancel_requested
cancel_requested 상태에서는 추가 상태 변경 불가
```

DDD 기준으로 핵심 규칙은 `Order` 도메인 객체 안에 두고, Django ORM은 `DjangoOrderRepository`에 격리했습니다. API는 요청/응답 변환과 HTTP 에러 매핑만 담당하고, 실제 상태 변경 판단은 `ChangeOrderStatusUseCase`와 도메인 모델이 처리합니다.