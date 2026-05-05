지정된 fixture path `/Users/hyun/Desktop/dddjango/none`는 존재하지 않아 읽을 파일이 없었습니다. 읽기 전용 환경이므로 아래는 적용용 unified diff 예시입니다.

```diff
diff --git a/orders/api.py b/orders/api.py
new file mode 100644
index 0000000..1f2a3b4
--- /dev/null
+++ b/orders/api.py
@@ -0,0 +1,32 @@
+from ninja import NinjaAPI, Schema
+from pydantic import Field
+
+
+api = NinjaAPI()
+
+
+class CreateOrderIn(Schema):
+    product_name: str = Field(min_length=1)
+    quantity: int = Field(gt=0)
+
+
+class OrderOut(Schema):
+    id: int
+    product_name: str
+    quantity: int
+    status: str
+
+
+@api.post("/orders", response={201: OrderOut})
+def create_order(request, payload: CreateOrderIn):
+    return 201, {
+        "id": 1,
+        "product_name": payload.product_name,
+        "quantity": payload.quantity,
+        "status": "created",
+    }
diff --git a/config/urls.py b/config/urls.py
index 1111111..2222222 100644
--- a/config/urls.py
+++ b/config/urls.py
@@ -1,6 +1,7 @@
 from django.contrib import admin
 from django.urls import path
+from orders.api import api
 
 urlpatterns = [
     path("admin/", admin.site.urls),
+    path("api/", api.urls),
 ]
diff --git a/tests/test_orders_api.py b/tests/test_orders_api.py
new file mode 100644
index 0000000..5c6d7e8
--- /dev/null
+++ b/tests/test_orders_api.py
@@ -0,0 +1,36 @@
+import pytest
+from ninja.testing import TestClient
+
+from orders.api import api
+
+
+pytestmark = pytest.mark.django_db
+
+
+client = TestClient(api)
+
+
+def test_create_order_returns_created_order():
+    response = client.post(
+        "/orders",
+        json={
+            "product_name": "Keyboard",
+            "quantity": 2,
+        },
+    )
+
+    assert response.status_code == 201
+    assert response.json() == {
+        "id": 1,
+        "product_name": "Keyboard",
+        "quantity": 2,
+        "status": "created",
+    }
+
+
+def test_create_order_rejects_invalid_quantity():
+    response = client.post(
+        "/orders",
+        json={
+            "product_name": "Keyboard",
+            "quantity": 0,
+        },
+    )
+
+    assert response.status_code == 422
+    assert any(
+        error["loc"][-1] == "quantity"
+        for error in response.json()["detail"]
+    )
```

TDD 흐름은 먼저 `tests/test_orders_api.py`를 추가해 실패를 확인한 뒤, `orders/api.py`의 schema와 endpoint를 최소 구현해서 통과시키는 방식입니다. `quantity: int = Field(gt=0)`가 요청 schema validation을 담당하고, 성공 케이스는 `201`과 `OrderOut` 응답 schema를 검증합니다.