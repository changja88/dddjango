Fixture 경로(`/Users/hyun/Desktop/dddjango/none`)는 존재하지 않아 읽을 파일이 없었습니다. 아래는 기존 코드가 없는 전제에서 `orders` 앱에 적용할 수 있는 핵심 unified diff 예시입니다.

**주요 내용**
상태 전이는 API가 직접 `status = ...`로 바꾸지 않고 `DomainOrder.transition_to()`에 둡니다. 응용 서비스는 트랜잭션, 조회, 저장만 조율합니다.

| 도메인 용어 | 코드 표현 | 금지 동의어 |
|---|---|---|
| 결제 대기 | `PAYMENT_WAITING` | `pending`, `ready` |
| 결제 완료 | `PAID`, `PaymentConfirmed` | `charged`, `approved` |
| 취소 요청 | `CANCELLATION_REQUESTED` | `cancelled`, `refund` |

```diff
diff --git a/orders/domain.py b/orders/domain.py
new file mode 100644
--- /dev/null
+++ b/orders/domain.py
@@
+from dataclasses import dataclass, field
+from datetime import datetime
+from enum import StrEnum
+from abc import ABC, abstractmethod
+
+
+class OrderStatus(StrEnum):
+    PAYMENT_WAITING = "payment_waiting"
+    PAID = "paid"
+    CANCELLATION_REQUESTED = "cancellation_requested"
+
+
+class InvalidOrderStatusTransition(Exception):
+    pass
+
+
+@dataclass(frozen=True)
+class PaymentConfirmed:
+    order_id: int
+    occurred_at: datetime
+
+
+@dataclass
+class DomainOrder:
+    """Aggregate Root.
+
+    Invariant: 상태 변경은 허용된 전이표를 통해서만 가능하다.
+    """
+    id: int
+    status: OrderStatus
+    _events: list[object] = field(default_factory=list)
+
+    _allowed = {
+        OrderStatus.PAYMENT_WAITING: {
+            OrderStatus.PAID,
+            OrderStatus.CANCELLATION_REQUESTED,
+        },
+        OrderStatus.PAID: {OrderStatus.CANCELLATION_REQUESTED},
+        OrderStatus.CANCELLATION_REQUESTED: set(),
+    }
+
+    def transition_to(self, target: OrderStatus) -> None:
+        if target not in self._allowed[self.status]:
+            raise InvalidOrderStatusTransition(
+                f"{self.status.value} -> {target.value} 전이는 허용되지 않습니다"
+            )
+        self.status = target
+        if target == OrderStatus.PAID:
+            self._events.append(PaymentConfirmed(self.id, datetime.now()))
+
+    def collect_events(self) -> list[object]:
+        events, self._events = self._events, []
+        return events
+
+
+class OrderRepository(ABC):
+    @abstractmethod
+    def get_for_status_change(self, order_id: int) -> DomainOrder | None:
+        ...
+
+    @abstractmethod
+    def save(self, order: DomainOrder) -> None:
+        ...
diff --git a/orders/application.py b/orders/application.py
new file mode 100644
--- /dev/null
+++ b/orders/application.py
@@
+from django.db import transaction
+
+from .domain import DomainOrder, OrderRepository, OrderStatus
+
+
+class OrderNotFound(Exception):
+    pass
+
+
+class OrderStatusApplicationService:
+    def __init__(self, orders: OrderRepository) -> None:
+        self.orders = orders
+
+    def change_status(self, order_id: int, target: OrderStatus) -> DomainOrder:
+        with transaction.atomic():
+            order = self.orders.get_for_status_change(order_id)
+            if order is None:
+                raise OrderNotFound
+            order.transition_to(target)
+            self.orders.save(order)
+            return order
diff --git a/orders/api.py b/orders/api.py
new file mode 100644
--- /dev/null
+++ b/orders/api.py
@@
+from django.http import HttpRequest
+from ninja import Router, Schema
+from ninja.errors import HttpError
+
+from .application import OrderNotFound, OrderStatusApplicationService
+from .domain import InvalidOrderStatusTransition, OrderStatus
+from .repository import DjangoOrderRepository
+
+router = Router(tags=["orders"])
+
+
+class OrderStatusChangeIn(Schema):
+    target_status: OrderStatus
+
+
+class OrderStatusOut(Schema):
+    id: int
+    status: OrderStatus
+
+
+@router.patch("/{order_id}/status", response=OrderStatusOut)
+def change_order_status(
+    request: HttpRequest,
+    order_id: int,
+    payload: OrderStatusChangeIn,
+) -> OrderStatusOut:
+    service = OrderStatusApplicationService(DjangoOrderRepository())
+    try:
+        order = service.change_status(order_id, payload.target_status)
+    except OrderNotFound:
+        raise HttpError(404, "주문을 찾을 수 없습니다")
+    except InvalidOrderStatusTransition as exc:
+        raise HttpError(409, str(exc))
+    return OrderStatusOut(id=order.id, status=order.status)
diff --git a/orders/repository.py b/orders/repository.py
new file mode 100644
--- /dev/null
+++ b/orders/repository.py
@@
+from .domain import DomainOrder, OrderRepository, OrderStatus
+from .models import Order
+
+
+class DjangoOrderRepository(OrderRepository):
+    def get_for_status_change(self, order_id: int) -> DomainOrder | None:
+        orm_order = Order.objects.select_for_update().filter(id=order_id).first()
+        if orm_order is None:
+            return None
+        return DomainOrder(id=orm_order.id, status=OrderStatus(orm_order.status))
+
+    def save(self, order: DomainOrder) -> None:
+        Order.objects.filter(id=order.id).update(status=order.status.value)
```

`PATCH /orders/{order_id}/status`는 `status` 하위 리소스를 부분 변경하는 형태라 URL에 동사를 넣지 않습니다. 응답 코드는 성공 `200`, 없는 주문 `404`, 허용되지 않는 전이 `409 Conflict`가 적절합니다.

`transaction.atomic()`과 `select_for_update()`가 필요한 이유는 동일 주문에 대해 “결제 완료”와 “취소 요청”이 동시에 들어올 수 있기 때문입니다. row lock 없이 두 요청이 같은 이전 상태를 보고 모두 전이 검증을 통과하면 마지막 저장이 앞선 결정을 덮어쓸 수 있습니다. 충돌이 낮고 성능을 더 중시하면 `version` 컬럼 기반 낙관적 잠금으로 바꿀 수 있습니다.

검증은 읽기 전용 sandbox라 실행하지 않았습니다. 적용 후 최소 확인 명령은 다음입니다.

```bash
python manage.py check
python manage.py test orders
```

---
> **관련 스킬 참조:**
> - API 오류를 RFC 9457 Problem Details로 통일 → **implementation-django-ninja** 스킬
> - 상태 전이 테스트와 애그리거트 불변식 보강 → **architecture-ddd** 스킬