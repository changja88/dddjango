**[주요 내용]**

Fixture 확인 결과, 지정된 경로 `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고 `/private/tmp/dddjango-codex-eval`도 비어 있었습니다. 그래서 실제 파일 기준 diff는 만들 수 없고, 현재 설명된 문제에 맞춘 적용 예시 diff를 제안합니다.

핵심 방향은 모델 메서드를 “순수 도메인 규칙 + 상태 전이”까지만 남기는 것입니다. 외부 API 호출, 트랜잭션, `save()`는 응용 서비스로 옮깁니다.

```diff
diff --git a/orders/models.py b/orders/models.py
--- a/orders/models.py
+++ b/orders/models.py
@@
 class Order(models.Model):
@@
-    def approve_payment(self):
-        if self.status != self.Status.PENDING:
-            raise ValueError("Only pending orders can be paid")
-
-        response = payment_client.approve(
-            order_id=self.id,
-            amount=self.total_amount,
-        )
-
-        if not response.ok:
-            self.status = self.Status.PAYMENT_FAILED
-            self.save(update_fields=["status", "updated_at"])
-            return False
-
-        self.status = self.Status.PAID
-        self.payment_transaction_id = response.transaction_id
-        self.save(update_fields=[
-            "status",
-            "payment_transaction_id",
-            "updated_at",
-        ])
-        return True
+    def mark_payment_approved(self, transaction_id: str) -> None:
+        if self.status != self.Status.PENDING:
+            raise OrderPaymentStateError("pending 주문만 결제 승인할 수 있습니다")
+
+        self.status = self.Status.PAID
+        self.payment_transaction_id = transaction_id
+
+    def mark_payment_failed(self) -> None:
+        if self.status != self.Status.PENDING:
+            raise OrderPaymentStateError("pending 주문만 결제 실패 처리할 수 있습니다")
+
+        self.status = self.Status.PAYMENT_FAILED
+
+
+class OrderPaymentStateError(Exception):
+    pass
diff --git a/orders/services.py b/orders/services.py
new file mode 100644
--- /dev/null
+++ b/orders/services.py
@@
+from django.db import transaction
+
+from orders.models import Order
+
+
+def approve_order_payment(order_id: int, payment_gateway) -> None:
+    order = Order.objects.get(id=order_id)
+
+    payment_result = payment_gateway.approve(
+        order_id=order.id,
+        amount=order.total_amount,
+    )
+
+    with transaction.atomic():
+        order = Order.objects.select_for_update().get(id=order_id)
+
+        if payment_result.is_approved:
+            order.mark_payment_approved(payment_result.transaction_id)
+            update_fields = ["status", "payment_transaction_id", "updated_at"]
+        else:
+            order.mark_payment_failed()
+            update_fields = ["status", "updated_at"]
+
+        order.save(update_fields=update_fields)
```

**Before / After / Reason**

[Before]  
모델 메서드가 검증, 외부 결제 API 호출, 상태 변경, 저장을 한 번에 수행합니다.

[After]  
모델은 `mark_payment_approved()` / `mark_payment_failed()`처럼 도메인 상태 전이만 담당합니다. 외부 API 호출과 DB 저장은 `approve_order_payment()` 서비스가 조율합니다.

[Reason] Clean Code / DDD / Django  
도메인 규칙과 부작용을 분리하면 모델 메서드는 DB나 네트워크 없이 단위 테스트할 수 있습니다. 외부 API 클라이언트 교체도 모델 변경 없이 서비스 또는 gateway 어댑터 변경으로 끝납니다. Django 관점에서도 외부 API 호출과 `save()`가 섞인 Fat Model보다는 서비스 레이어가 트랜잭션 경계를 명시하는 편이 안전합니다.

**작은 리팩터링 순서**

1. 현재 모델 메서드에 대한 characterization test를 먼저 추가합니다. 성공, 실패, 이미 처리된 주문 상태를 고정합니다.
2. 모델 메서드 안의 상태 검증과 상태 변경을 `mark_*` 메서드로 추출합니다. 이 단계에서는 동작을 바꾸지 않습니다.
3. 외부 API 호출을 `payment_gateway`로 감싸고 서비스 함수에 주입합니다.
4. 모델 메서드 안의 `save()`를 제거하고, 서비스에서 `transaction.atomic()`과 `save(update_fields=...)`를 담당하게 합니다.
5. 외부 API가 DB 커밋 이후 실행되어야 하는 알림성 부작용이면 `transaction.on_commit()`으로 옮깁니다. 결제 승인처럼 결과가 상태 전이에 필요한 호출은 서비스에서 명시적으로 실행합니다.

**검증**

읽기 전용이라 실행은 하지 않았습니다. 적용 후 최소 검증은 아래 정도가 필요합니다.

```bash
python manage.py test orders
python manage.py check
```

추가로 모델 단위 테스트는 DB 없이 `mark_payment_approved()`의 상태 전이와 예외만 검증하고, 서비스 테스트는 fake `payment_gateway`로 승인/실패 흐름과 `save(update_fields=...)` 결과를 확인하면 됩니다.

---
> **관련 스킬 참조:**
> - Django 서비스 레이어와 트랜잭션 경계 → **implementation-django** 스킬
> - 부작용과 도메인 규칙 분리 → **implementation-cleancode** 스킬
> - 외부 API를 도메인 밖으로 격리 → **architecture-implementation-patterns** 스킬