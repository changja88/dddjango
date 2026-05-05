**주요 내용**

fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, 현재 작업 디렉터리도 비어 있어 pytest 실행과 파일 수정은 하지 못했습니다. 아래는 실제 프로젝트에 적용할 수 있는 TDD 흐름용 unified diff입니다. RED 테스트를 먼저 추가하고, 그 실패를 통과시키는 GREEN 최소 구현을 붙이는 순서입니다.

**RED: 실패 테스트**

예상 실패: `orders.domain`, `Order`, `OrderStatus`, `OrderCannotBeCancelledError`, `OrderApplicationService`가 아직 없어 import 단계에서 실패합니다.

```diff
diff --git a/tests/isolated/orders/test_cancel_order.py b/tests/isolated/orders/test_cancel_order.py
new file mode 100644
--- /dev/null
+++ b/tests/isolated/orders/test_cancel_order.py
@@ -0,0 +1,78 @@
+from dataclasses import dataclass
+
+import pytest
+
+from apps.orders.domain import (
+    Order,
+    OrderCannotBeCancelledError,
+    OrderId,
+    OrderStatus,
+)
+from apps.orders.services import OrderApplicationService
+
+
+class InMemoryOrderRepository:
+    def __init__(self, orders: list[Order]) -> None:
+        self.orders = {order.id: order for order in orders}
+
+    def find_by_id(self, order_id: OrderId) -> Order:
+        return self.orders[order_id]
+
+    def save(self, order: Order) -> None:
+        self.orders[order.id] = order
+
+
+@pytest.mark.parametrize("status", [OrderStatus.PENDING, OrderStatus.PAID])
+def test_cancel_order_cancellable_status_changes_to_cancelled(status: OrderStatus) -> None:
+    # Arrange
+    order = Order(id=OrderId("order-1"), status=status)
+    service = OrderApplicationService(InMemoryOrderRepository([order]))
+
+    # Act
+    result = service.cancel_order(OrderId("order-1"))
+
+    # Assert
+    assert result.status == OrderStatus.CANCELLED
+
+
+@pytest.mark.parametrize(
+    "status",
+    [OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.CANCELLED],
+)
+def test_cancel_order_non_cancellable_status_raises_error(status: OrderStatus) -> None:
+    # Arrange
+    order = Order(id=OrderId("order-1"), status=status)
+    service = OrderApplicationService(InMemoryOrderRepository([order]))
+
+    # Act / Assert
+    with pytest.raises(OrderCannotBeCancelledError):
+        service.cancel_order(OrderId("order-1"))
+
+
+def test_cancel_order_records_order_cancelled_event() -> None:
+    # Arrange
+    order = Order(id=OrderId("order-1"), status=OrderStatus.PAID)
+
+    # Act
+    order.cancel()
+
+    # Assert
+    assert [event.order_id for event in order.collect_events()] == [OrderId("order-1")]
```

**GREEN: 최소 구현**

```diff
diff --git a/apps/orders/domain.py b/apps/orders/domain.py
new file mode 100644
--- /dev/null
+++ b/apps/orders/domain.py
@@ -0,0 +1,61 @@
+from abc import ABC, abstractmethod
+from dataclasses import dataclass, field
+from enum import StrEnum
+
+
+@dataclass(frozen=True)
+class OrderId:
+    value: str
+
+    def __post_init__(self) -> None:
+        if not self.value:
+            raise ValueError("order id is required")
+
+
+class OrderStatus(StrEnum):
+    PENDING = "pending"
+    PAID = "paid"
+    SHIPPED = "shipped"
+    DELIVERED = "delivered"
+    CANCELLED = "cancelled"
+
+
+class OrderCannotBeCancelledError(Exception):
+    pass
+
+
+@dataclass(frozen=True)
+class OrderCancelledEvent:
+    order_id: OrderId
+
+
+@dataclass
+class Order:
+    """Aggregate Root. 취소는 PENDING/PAID 상태에서만 가능하다."""
+
+    id: OrderId
+    status: OrderStatus
+    _events: list[OrderCancelledEvent] = field(default_factory=list)
+
+    def cancel(self) -> None:
+        if self.status not in {OrderStatus.PENDING, OrderStatus.PAID}:
+            raise OrderCannotBeCancelledError
+
+        self.status = OrderStatus.CANCELLED
+        self._events.append(OrderCancelledEvent(order_id=self.id))
+
+    def collect_events(self) -> list[OrderCancelledEvent]:
+        events = list(self._events)
+        self._events.clear()
+        return events
+
+
+class OrderRepository(ABC):
+    @abstractmethod
+    def find_by_id(self, order_id: OrderId) -> Order:
+        raise NotImplementedError
+
+    @abstractmethod
+    def save(self, order: Order) -> None:
+        raise NotImplementedError
diff --git a/apps/orders/services.py b/apps/orders/services.py
new file mode 100644
--- /dev/null
+++ b/apps/orders/services.py
@@ -0,0 +1,17 @@
+from dataclasses import dataclass
+
+from apps.orders.domain import Order, OrderId, OrderRepository
+
+
+@dataclass(frozen=True)
+class CancelOrderResult:
+    order_id: OrderId
+    status: str
+
+
+class OrderApplicationService:
+    def __init__(self, orders: OrderRepository) -> None:
+        self.orders = orders
+
+    def cancel_order(self, order_id: OrderId) -> Order:
+        order = self.orders.find_by_id(order_id)
+        order.cancel()
+        self.orders.save(order)
+        return order
```

**REFACTOR 방향**

1. Django 모델이 있다면 `OrderRepository` 구현체를 ORM 어댑터로 분리하고, 도메인 `Order`와 Django `OrderModel` 변환을 명시합니다.
2. `OrderCannotBeCancelledError`를 API 계층에서는 409 Conflict Problem Details로 매핑합니다.
3. 환불, 재고 복구, 알림 같은 부수효과는 `OrderCancelledEvent`를 수집한 뒤 `transaction.on_commit()` 이후 처리합니다.
4. `OrderStatus`가 Django 모델에 들어가면 `TextChoices`로 맞추고 DB `CheckConstraint`를 추가합니다.

**검증 명령**

실행하지 못했습니다. 실제 프로젝트에서는 다음 순서로 확인하세요.

```bash
pytest tests/isolated/orders/test_cancel_order.py -q
python manage.py check
```

---
> **관련 스킬 참조:**
> - Django pytest/TDD 구현 → **implementation-tdd**, **implementation-test**, **implementation-django**, **architecture-ddd** 스킬