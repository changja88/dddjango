**[주요 내용]**

지정된 fixture 경로 `/Users/hyun/Desktop/dddjango/none`가 존재하지 않았고, `/private/tmp/dddjango-codex-eval`도 비어 있어 실제 파일 기반 diff는 만들 수 없었습니다. 아래는 해당 문제에 바로 적용할 수 있는 최소 리팩터링 방향입니다.

핵심 문제는 Django model method가 `검증 -> 외부 API 호출 -> 상태 변경 -> save()`를 한 번에 처리한다는 점입니다. 모델에는 순수 도메인 규칙과 상태 전이만 남기고, 외부 API 호출과 저장 트랜잭션은 application service로 올리는 편이 맞습니다.

```diff
diff --git a/orders/models.py b/orders/models.py
--- a/orders/models.py
+++ b/orders/models.py
@@
 class Order(models.Model):
@@
-    def confirm(self, payment_client):
-        if self.status != self.Status.READY:
-            raise ValueError("order is not ready")
-        if self.total_amount <= 0:
-            raise ValueError("invalid amount")
-
-        payment_client.capture(
-            payment_key=self.payment_key,
-            amount=self.total_amount,
-        )
-
-        self.status = self.Status.CONFIRMED
-        self.save()
+    def confirm(self) -> None:
+        if self.status != self.Status.READY:
+            raise OrderNotReadyError()
+        if self.total_amount <= 0:
+            raise InvalidOrderAmountError()
+
+        self.status = self.Status.CONFIRMED
+
+
+class OrderNotReadyError(Exception):
+    pass
+
+
+class InvalidOrderAmountError(Exception):
+    pass
diff --git a/orders/services.py b/orders/services.py
new file mode 100644
--- /dev/null
+++ b/orders/services.py
@@
+from django.db import transaction
+
+from .models import Order
+
+
+def confirm_order(*, order_id: int, payment_gateway) -> Order:
+    with transaction.atomic():
+        order = Order.objects.select_for_update().get(id=order_id)
+
+        payment_gateway.capture(
+            payment_key=order.payment_key,
+            amount=order.total_amount,
+        )
+
+        order.confirm()
+        order.full_clean()
+        order.save(update_fields=["status"])
+
+    return order
diff --git a/orders/gateways.py b/orders/gateways.py
new file mode 100644
--- /dev/null
+++ b/orders/gateways.py
@@
+from typing import Protocol
+
+
+class PaymentGateway(Protocol):
+    def capture(self, *, payment_key: str, amount: int) -> None:
+        ...
```

[Reason] Clean Code / DDD / Django Convention -- `Order.confirm()`은 이제 “주문은 언제 확정 가능한가”라는 순수 도메인 규칙과 상태 전이만 담당합니다. 외부 API 호출, 트랜잭션, ORM 저장은 `confirm_order()` 유스케이스가 조율합니다. 모델에서 `payment_client`를 제거했기 때문에 SDK 교체와 테스트가 쉬워집니다.

작게 나누는 적용 순서는 다음이 좋습니다.

1. 먼저 모델 메서드에서 외부 API 호출만 제거하고 service 함수로 옮깁니다.
2. 그 다음 모델 메서드의 `save()`를 제거하고 호출부에서 `save(update_fields=...)`를 하게 만듭니다.
3. `ValueError`나 문자열 에러를 도메인 예외로 교체합니다.
4. 테스트를 모델 단위와 service 단위로 분리합니다. 모델 테스트는 DB/API 없이 상태 전이만 검증하고, service 테스트는 gateway mock과 저장 여부를 검증합니다.
5. 외부 API가 “트랜잭션 성공 후 알림/동기화” 성격이면 `transaction.on_commit()`으로 미룹니다. 결제 승인처럼 상태 변경의 선행 조건이면 service에서 호출하되 모델 안으로 넣지는 않습니다.

검증 단계:

```bash
python manage.py test orders
python manage.py check
```

fixture가 없어 실제 실행은 하지 못했습니다. 실제 코드가 있으면 위 diff를 파일명과 도메인 용어에 맞춰 더 좁은 unified diff로 바꾸는 게 다음 단계입니다.

---
> **관련 스킬 참조:**
> - Django model/service 경계 → **implementation-django** 스킬
> - 순수 도메인 규칙과 부작용 분리 → **architecture-ddd** 스킬
> - 외부 API 격리와 포트/어댑터 → **architecture-implementation-patterns** 스킬