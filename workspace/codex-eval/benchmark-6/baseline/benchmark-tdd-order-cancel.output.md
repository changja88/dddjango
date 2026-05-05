`/Users/hyun/Desktop/dddjango/none`는 존재하지 않아 읽을 수 없었습니다. 대신 인접 fixture인 `/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop`를 읽었습니다. 현재 `Order.cancel()`은 이미 일부 구현되어 있지만, HTTP 취소 API의 실패 응답과 pytest 기반 커버리지가 부족합니다.

**1. 실패 테스트 추가**

```diff
diff --git a/pytest.ini b/pytest.ini
new file mode 100644
index 0000000..b8e3f4a
--- /dev/null
+++ b/pytest.ini
@@ -0,0 +1,3 @@
+[pytest]
+DJANGO_SETTINGS_MODULE = config.settings
+python_files = tests.py test_*.py *_tests.py
diff --git a/shop/orders/tests.py b/shop/orders/tests.py
index 8d2d9c1..1bb35e4 100644
--- a/shop/orders/tests.py
+++ b/shop/orders/tests.py
@@ -1,14 +1,78 @@
-from django.test import TestCase
+import json
+
+import pytest
 
 from shop.orders.models import Order
 
 
-class OrderModelTests(TestCase):
-    def test_cancel_sets_status(self):
-        order = Order.objects.create(
-            customer_email="buyer@example.com",
-            total_amount="100.00",
-        )
+pytestmark = pytest.mark.django_db
+
+
+def create_order(**overrides):
+    data = {
+        "customer_email": "buyer@example.com",
+        "total_amount": "100.00",
+    }
+    data.update(overrides)
+    return Order.objects.create(**data)
+
+
+def test_cancel_sets_status_reason_and_timestamp():
+    order = create_order()
 
-        order.cancel(reason="customer request", actor_email="ops@example.com")
+    order.cancel(reason="customer request", actor_email="ops@example.com")
 
-        self.assertEqual(order.status, Order.STATUS_CANCELLED)
+    order.refresh_from_db()
+    assert order.status == Order.STATUS_CANCELLED
+    assert order.cancel_reason == "customer request by ops@example.com"
+    assert order.cancelled_at is not None
+
+
+def test_cancel_requires_non_blank_reason():
+    order = create_order()
+
+    with pytest.raises(ValueError, match="cancel reason is required"):
+        order.cancel(reason="   ", actor_email="ops@example.com")
+
+
+def test_cancelled_order_is_idempotent():
+    order = create_order()
+    order.cancel(reason="customer request", actor_email="ops@example.com")
+    first_cancelled_at = order.cancelled_at
+
+    order.cancel(reason="second reason", actor_email="other@example.com")
+
+    order.refresh_from_db()
+    assert order.cancel_reason == "customer request by ops@example.com"
+    assert order.cancelled_at == first_cancelled_at
+
+
+def test_cancel_api_returns_200_for_valid_request(client):
+    order = create_order()
+
+    response = client.post(
+        f"/orders/{order.id}/cancel/",
+        data=json.dumps(
+            {
+                "reason": "customer request",
+                "actor_email": "ops@example.com",
+            }
+        ),
+        content_type="application/json",
+    )
+
+    assert response.status_code == 200
+    assert response.json() == {"id": order.id, "status": Order.STATUS_CANCELLED}
+
+
+def test_cancel_api_returns_400_for_blank_reason(client):
+    order = create_order()
+
+    response = client.post(
+        f"/orders/{order.id}/cancel/",
+        data=json.dumps({"reason": "   "}),
+        content_type="application/json",
+    )
+
+    assert response.status_code == 400
+    assert response.json() == {"error": "cancel reason is required"}
+
+
+def test_cancel_api_returns_409_for_shipped_order(client):
+    order = create_order(status=Order.STATUS_SHIPPED)
+
+    response = client.post(
+        f"/orders/{order.id}/cancel/",
+        data=json.dumps({"reason": "customer request"}),
+        content_type="application/json",
+    )
+
+    assert response.status_code == 409
+    assert response.json() == {"error": "shipped orders cannot be cancelled"}
```

이 시점의 기대 흐름:

```bash
pytest shop/orders/tests.py
```

현재 코드에서는 공백 사유 검증과 API 에러 응답 테스트가 실패합니다.

**2. 최소 구현**

```diff
diff --git a/shop/orders/models.py b/shop/orders/models.py
index 5c3bd7a..4cc0dd1 100644
--- a/shop/orders/models.py
+++ b/shop/orders/models.py
@@ -14,12 +14,13 @@ class Order(models.Model):
     created_at = models.DateTimeField(auto_now_add=True)
 
     def cancel(self, reason: str, actor_email: str) -> None:
+        reason = reason.strip()
+        if not reason:
+            raise ValueError("cancel reason is required")
         if self.status == self.STATUS_SHIPPED:
             raise ValueError("shipped orders cannot be cancelled")
         if self.status == self.STATUS_CANCELLED:
             return
-        if not reason:
-            raise ValueError("cancel reason is required")
         self.status = self.STATUS_CANCELLED
         self.cancel_reason = f"{reason} by {actor_email}"
         self.cancelled_at = timezone.now()
diff --git a/shop/orders/views.py b/shop/orders/views.py
index 2cf4d3d..15a6f67 100644
--- a/shop/orders/views.py
+++ b/shop/orders/views.py
@@ -10,12 +10,20 @@ from shop.orders.models import Order, Product, Reservation
 @require_POST
 def cancel_order(request, order_id):
     payload = json.loads(request.body or "{}")
-    order = Order.objects.get(id=order_id)
-    order.cancel(
-        reason=payload.get("reason", ""),
-        actor_email=payload.get("actor_email", "system@example.com"),
-    )
-    return JsonResponse({"id": order.id, "status": order.status})
+    order = Order.objects.get(id=order_id)
+
+    try:
+        order.cancel(
+            reason=payload.get("reason", ""),
+            actor_email=payload.get("actor_email", "system@example.com"),
+        )
+    except ValueError as exc:
+        message = str(exc)
+        status = 409 if message == "shipped orders cannot be cancelled" else 400
+        return JsonResponse({"error": message}, status=status)
+
+    return JsonResponse({
+        "id": order.id,
+        "status": order.status,
+    })
```

이 단계는 테스트를 통과시키기 위한 최소 변경입니다. 도메인 규칙은 `Order.cancel()`에 두고, view는 HTTP 상태 코드 변환만 담당합니다.

**3. 리팩터링 방향**

테스트가 통과한 뒤에는 문자열 비교로 HTTP 상태를 결정하는 부분을 분리하는 게 다음 단계입니다.

```diff
diff --git a/shop/orders/services.py b/shop/orders/services.py
new file mode 100644
index 0000000..0d06e95
--- /dev/null
+++ b/shop/orders/services.py
@@ -0,0 +1,17 @@
+from shop.orders.models import Order
+
+
+class OrderCancellationError(Exception):
+    status_code = 400
+
+
+class ShippedOrderCancellationError(OrderCancellationError):
+    status_code = 409
+
+
+def cancel_order(order: Order, *, reason: str, actor_email: str) -> None:
+    try:
+        order.cancel(reason=reason, actor_email=actor_email)
+    except ValueError as exc:
+        if str(exc) == "shipped orders cannot be cancelled":
+            raise ShippedOrderCancellationError(str(exc)) from exc
+        raise OrderCancellationError(str(exc)) from exc
diff --git a/shop/orders/views.py b/shop/orders/views.py
index 15a6f67..08300d1 100644
--- a/shop/orders/views.py
+++ b/shop/orders/views.py
@@ -5,7 +5,8 @@ from django.http import JsonResponse
 from django.views.decorators.http import require_POST
 
 from shop.orders.models import Order, Product, Reservation
+from shop.orders.services import OrderCancellationError, cancel_order as cancel_order_service
 
 
 @require_POST
@@ -14,14 +15,13 @@ def cancel_order(request, order_id):
     order = Order.objects.get(id=order_id)
 
     try:
-        order.cancel(
+        cancel_order_service(
+            order,
             reason=payload.get("reason", ""),
             actor_email=payload.get("actor_email", "system@example.com"),
         )
-    except ValueError as exc:
-        message = str(exc)
-        status = 409 if message == "shipped orders cannot be cancelled" else 400
-        return JsonResponse({"error": message}, status=status)
+    except OrderCancellationError as exc:
+        return JsonResponse({"error": str(exc)}, status=exc.status_code)
 
     return JsonResponse({
         "id": order.id,
```

핵심 순서는 이렇게 잡으면 됩니다.

1. pytest로 취소 도메인 규칙과 API 응답 계약을 먼저 고정한다.
2. `Order.cancel()`의 공백 사유 검증과 view의 에러 응답만 최소 구현한다.
3. 테스트 통과 후 문자열 기반 분기와 HTTP 변환 책임을 `services.py`로 옮겨 view를 얇게 만든다.

읽기 전용 sandbox라 테스트 실행과 파일 수정은 하지 않았습니다.