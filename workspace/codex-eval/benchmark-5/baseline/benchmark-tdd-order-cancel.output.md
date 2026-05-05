지정된 `/Users/hyun/Desktop/dddjango/none` 경로는 없어서 직접 읽을 수 없었습니다. 대신 실제 fixture로 보이는 `/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop`를 읽었습니다. 현재 `Order.cancel()`은 이미 있지만, `cancel_order` view는 도메인 예외를 HTTP 응답으로 바꾸지 않아 빈 사유나 배송 완료 주문 취소가 500으로 터질 수 있습니다.

아래는 read-only 환경용 TDD 흐름입니다.

**1. RED: 실패 테스트 추가**

```diff
diff --git a/shop/orders/tests.py b/shop/orders/tests.py
index 4a2a9d1..9d4f7f1 100644
--- a/shop/orders/tests.py
+++ b/shop/orders/tests.py
@@ -1,17 +1,68 @@
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
+@pytest.fixture
+def pending_order():
+    return Order.objects.create(
+        customer_email="buyer@example.com",
+        total_amount="100.00",
+    )
+
+
+@pytest.mark.django_db
+def test_cancel_sets_status_reason_actor_and_timestamp(pending_order):
+    pending_order.cancel(
+        reason="customer request",
+        actor_email="ops@example.com",
+    )
+
+    pending_order.refresh_from_db()
+
+    assert pending_order.status == Order.STATUS_CANCELLED
+    assert pending_order.cancel_reason == "customer request by ops@example.com"
+    assert pending_order.cancelled_at is not None
+
+
+@pytest.mark.django_db
+def test_cancel_requires_reason(pending_order):
+    with pytest.raises(ValueError, match="cancel reason is required"):
+        pending_order.cancel(reason="", actor_email="ops@example.com")
+
+
+@pytest.mark.django_db
+def test_shipped_order_cannot_be_cancelled():
+    order = Order.objects.create(
+        customer_email="buyer@example.com",
+        total_amount="100.00",
+        status=Order.STATUS_SHIPPED,
+    )
+
+    with pytest.raises(ValueError, match="shipped orders cannot be cancelled"):
+        order.cancel(reason="customer request", actor_email="ops@example.com")
+
+
+@pytest.mark.django_db
+def test_cancel_endpoint_returns_400_when_reason_is_missing(client, pending_order):
+    response = client.post(
+        f"/orders/{pending_order.id}/cancel/",
+        data=json.dumps({"actor_email": "ops@example.com"}),
+        content_type="application/json",
+    )
+
+    assert response.status_code == 400
+    assert response.json() == {"error": "cancel reason is required"}
+
+
+@pytest.mark.django_db
+def test_cancel_endpoint_returns_409_when_order_is_shipped(client):
+    order = Order.objects.create(
+        customer_email="buyer@example.com",
+        total_amount="100.00",
+        status=Order.STATUS_SHIPPED,
+    )
 
-        order.cancel(reason="customer request", actor_email="ops@example.com")
+    response = client.post(
+        f"/orders/{order.id}/cancel/",
+        data=json.dumps({"reason": "customer request", "actor_email": "ops@example.com"}),
+        content_type="application/json",
+    )
 
-        self.assertEqual(order.status, Order.STATUS_CANCELLED)
+    assert response.status_code == 409
+    assert response.json() == {"error": "shipped orders cannot be cancelled"}
```

예상 RED: 마지막 두 endpoint 테스트가 실패합니다. 현재 view가 `ValueError`를 잡지 않아 400/409 대신 500을 냅니다.

**2. GREEN: 최소 구현**

```diff
diff --git a/shop/orders/views.py b/shop/orders/views.py
index 8f0a1de..0ef7f4a 100644
--- a/shop/orders/views.py
+++ b/shop/orders/views.py
@@ -11,12 +11,20 @@ from shop.orders.models import Order, Product, Reservation
 @require_POST
 def cancel_order(request, order_id):
     payload = json.loads(request.body or "{}")
     order = Order.objects.get(id=order_id)
-    order.cancel(
-        reason=payload.get("reason", ""),
-        actor_email=payload.get("actor_email", "system@example.com"),
-    )
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
     return JsonResponse({"id": order.id, "status": order.status})
```

실행 명령:

```bash
DJANGO_SETTINGS_MODULE=config.settings pytest shop/orders/tests.py -q
```

**3. REFACTOR 방향**

현재 최소 구현은 통과 목적에는 충분하지만, 문자열 비교로 HTTP status를 정하는 부분은 약합니다. 다음 단계에서는 `ValueError` 대신 `CancelReasonRequired`와 `OrderCannotBeCancelled` 같은 명시적 예외를 두고, view는 예외 타입별로 400/409를 매핑하는 정도가 좋습니다.

또 `Order.cancel()`은 주문 불변식과 상태 전이를 객체 안에 둔 현재 방향이 맞습니다. API layer는 JSON 파싱, 예외 변환, 응답 생성만 맡기고, 취소 가능 여부와 취소 시점 기록은 `Order` 안에 남기는 쪽이 변경 이유가 분리됩니다.