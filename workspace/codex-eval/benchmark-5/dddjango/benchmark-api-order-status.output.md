지정 fixture `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, 현재 작업 디렉터리에도 읽을 프로젝트 파일이 없었습니다. 그래서 빈 Django 앱 기준의 예시 diff로 제시합니다. 전이는 `Order` 애그리거트가 막고, API는 Django Ninja `Router/Schema`, 응용 서비스는 트랜잭션과 저장소 조율만 담당합니다.

**Ubiquitous Language**

| 도메인 용어 | 코드 표현 | 금지 동의어 |
|---|---|---|
| 결제 대기 | `PAYMENT_WAITING` | `pending`, `ready` |
| 결제 완료 | `PAID`, `confirm_payment()` | `charge`, `settle` |
| 취소 요청 | `CANCELLATION_REQUESTED`, `request_cancellation()` | `delete`, `refund` |

```diff
diff --git a/apps/orders/domain.py b/apps/orders/domain.py
new file mode 100644
--- /dev/null
+++ b/apps/orders/domain.py
@@
+from abc import ABC, abstractmethod
+from dataclasses import dataclass, field
+from datetime import datetime
+from enum import StrEnum
+
+
+class OrderStatus(StrEnum):
+    PAYMENT_WAITING = "payment_waiting"
+    PAID = "paid"
+    CANCELLATION_REQUESTED = "cancellation_requested"
+
+
+class InvalidStateTransition(Exception): ...
+class OrderNotFound(Exception): ...
+class ConcurrencyError(Exception): ...
+
+
+@dataclass(frozen=True)
+class OrderId:
+    value: int
+
+    def __post_init__(self) -> None:
+        if self.value <= 0:
+            raise ValueError("order_id must be positive")
+
+
+@dataclass(frozen=True)
+class DomainEvent:
+    order_id: OrderId
+    occurred_at: datetime = field(default_factory=datetime.now)
+
+
+class PaymentConfirmed(DomainEvent): ...
+class CancellationRequested(DomainEvent): ...
+
+
+class AggregateRoot:
+    def __init__(self) -> None:
+        self._events: list[DomainEvent] = []
+
+    def _record_event(self, event: DomainEvent) -> None:
+        self._events.append(event)
+
+    def collect_events(self) -> list[DomainEvent]:
+        events, self._events = self._events, []
+        return events
+
+
+@dataclass
+class Order(AggregateRoot):
+    """Aggregate Root. 상태는 아래 메서드로만 변경한다."""
+
+    id: OrderId
+    status: OrderStatus
+    version: int = 0
+
+    def __post_init__(self) -> None:
+        AggregateRoot.__init__(self)
+
+    def confirm_payment(self) -> None:
+        if self.status != OrderStatus.PAYMENT_WAITING:
+            raise InvalidStateTransition("결제 대기 상태에서만 결제 완료 가능")
+        self.status = OrderStatus.PAID
+        self._record_event(PaymentConfirmed(order_id=self.id))
+
+    def request_cancellation(self) -> None:
+        if self.status not in {OrderStatus.PAYMENT_WAITING, OrderStatus.PAID}:
+            raise InvalidStateTransition("현재 상태에서는 취소 요청 불가")
+        self.status = OrderStatus.CANCELLATION_REQUESTED
+        self._record_event(CancellationRequested(order_id=self.id))
+
+
+class OrderRepository(ABC):
+    @abstractmethod
+    def get(self, order_id: OrderId) -> Order: ...
+
+    @abstractmethod
+    def save(self, order: Order) -> None: ...
diff --git a/apps/orders/services.py b/apps/orders/services.py
new file mode 100644
--- /dev/null
+++ b/apps/orders/services.py
@@
+from collections.abc import Callable
+
+from django.db import transaction
+
+from .domain import Order, OrderId, OrderRepository
+
+
+class OrderApplicationService:
+    def __init__(self, repo: OrderRepository, publish: Callable[[object], None]):
+        self.repo = repo
+        self.publish = publish
+
+    def confirm_payment(self, order_id: int) -> Order:
+        return self._change(order_id, lambda order: order.confirm_payment())
+
+    def request_cancellation(self, order_id: int) -> Order:
+        return self._change(order_id, lambda order: order.request_cancellation())
+
+    def _change(self, order_id: int, action: Callable[[Order], None]) -> Order:
+        with transaction.atomic():
+            order = self.repo.get(OrderId(order_id))
+            action(order)
+            self.repo.save(order)
+            events = order.collect_events()
+            transaction.on_commit(lambda: [self.publish(event) for event in events])
+        return order
diff --git a/apps/orders/api.py b/apps/orders/api.py
new file mode 100644
--- /dev/null
+++ b/apps/orders/api.py
@@
+from django.http import HttpRequest
+from ninja import Router, Schema
+
+from .domain import ConcurrencyError, InvalidStateTransition, OrderNotFound
+from .services import OrderApplicationService
+
+router = Router(tags=["orders"])
+
+
+class OrderOut(Schema):
+    id: int
+    status: str
+    version: int
+
+
+class ProblemDetail(Schema):
+    type: str = "about:blank"
+    title: str
+    status: int
+    detail: str
+    instance: str
+
+
+def get_order_service() -> OrderApplicationService:
+    ...
+
+
+def to_out(order) -> OrderOut:
+    return OrderOut(id=order.id.value, status=order.status.value, version=order.version)
+
+
+@router.post("/{int:order_id}/payment-confirmations", response={200: OrderOut, 404: ProblemDetail, 409: ProblemDetail})
+def confirm_payment(request: HttpRequest, order_id: int) -> tuple[int, OrderOut | ProblemDetail]:
+    try:
+        return 200, to_out(get_order_service().confirm_payment(order_id))
+    except OrderNotFound:
+        return 404, ProblemDetail(title="Order Not Found", status=404, detail="주문이 없습니다.", instance=request.path)
+    except (InvalidStateTransition, ConcurrencyError) as exc:
+        return 409, ProblemDetail(title="Order Conflict", status=409, detail=str(exc), instance=request.path)
+
+
+@router.post("/{int:order_id}/cancellation-requests", response={200: OrderOut, 404: ProblemDetail, 409: ProblemDetail})
+def request_cancellation(request: HttpRequest, order_id: int) -> tuple[int, OrderOut | ProblemDetail]:
+    try:
+        return 200, to_out(get_order_service().request_cancellation(order_id))
+    except OrderNotFound:
+        return 404, ProblemDetail(title="Order Not Found", status=404, detail="주문이 없습니다.", instance=request.path)
+    except (InvalidStateTransition, ConcurrencyError) as exc:
+        return 409, ProblemDetail(title="Order Conflict", status=409, detail=str(exc), instance=request.path)
```

`transaction.atomic()`은 도메인 전이, 저장, 커밋 후 이벤트 발행 예약을 하나의 경계로 묶기 위해 필요합니다. 실제 저장소에서는 `version` 컬럼으로 `WHERE id=? AND version=?` 업데이트를 수행해 낙관적 잠금을 적용하세요. 동일 주문에 충돌이 매우 잦으면 저장소 `get()`에서 `select_for_update()`를 쓰는 비관적 잠금으로 바꿀 수 있습니다.

검증은 이 환경에서 실행하지 못했습니다. 적용 후 `python manage.py check`, `pytest`를 실행하고, 전이 실패와 동시 수정 충돌 테스트를 추가하세요.

---
> **관련 스킬 참조:**
> - API 구현 → **implementation-django-ninja** 스킬
> - 상태 전이/애그리거트 → **architecture-ddd** 스킬
> - 트랜잭션/잠금 → **architecture-db** 스킬