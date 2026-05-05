Fixture path `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, 현재 작업 디렉터리에도 소스 파일이 없어 읽을 프로젝트 파일이 없습니다. 아래는 Django Ninja endpoint를 TDD로 추가하는 최소 예시 unified diff입니다. 핵심은 pytest가 먼저 `422 validation error`와 `201 success response`를 고정하고, 그에 맞춰 schema와 endpoint를 구현하는 흐름입니다.

```diff
diff --git a/shop/api.py b/shop/api.py
new file mode 100644
index 0000000..1b7c8a1
--- /dev/null
+++ b/shop/api.py
@@ -0,0 +1,31 @@
+from decimal import Decimal
+
+from ninja import NinjaAPI, Schema
+
+
+api = NinjaAPI()
+
+
+class CreateProductRequest(Schema):
+    name: str
+    price: Decimal
+
+
+class ProductResponse(Schema):
+    id: int
+    name: str
+    price: Decimal
+
+
+@api.post("/products", response={201: ProductResponse})
+def create_product(request, payload: CreateProductRequest):
+    return 201, {
+        "id": 1,
+        "name": payload.name,
+        "price": payload.price,
+    }
diff --git a/config/urls.py b/config/urls.py
index 1111111..2222222 100644
--- a/config/urls.py
+++ b/config/urls.py
@@ -1,6 +1,8 @@
 from django.contrib import admin
 from django.urls import path
 
+from shop.api import api
+
 urlpatterns = [
     path("admin/", admin.site.urls),
+    path("api/", api.urls),
 ]
diff --git a/tests/test_product_api.py b/tests/test_product_api.py
new file mode 100644
index 0000000..9fd2b63
--- /dev/null
+++ b/tests/test_product_api.py
@@ -0,0 +1,31 @@
+import pytest
+
+
+@pytest.mark.django_db
+def test_create_product_rejects_invalid_request_schema(client):
+    response = client.post(
+        "/api/products",
+        data={"name": "Keyboard"},
+        content_type="application/json",
+    )
+
+    assert response.status_code == 422
+
+    body = response.json()
+    assert body["detail"][0]["loc"] == ["body", "payload", "price"]
+    assert body["detail"][0]["type"] == "missing"
+
+
+@pytest.mark.django_db
+def test_create_product_returns_created_product(client):
+    response = client.post(
+        "/api/products",
+        data={
+            "name": "Keyboard",
+            "price": "129.99",
+        },
+        content_type="application/json",
+    )
+
+    assert response.status_code == 201
+    assert response.json() == {
+        "id": 1,
+        "name": "Keyboard",
+        "price": "129.99",
+    }
```

TDD 순서는 이렇게 잡으면 됩니다.

1. `test_create_product_rejects_invalid_request_schema` 먼저 작성  
2. 실패 확인: `/api/products` endpoint 없음 또는 validation 미동작  
3. `CreateProductRequest` schema와 endpoint 추가  
4. 성공 응답 테스트 작성  
5. 고정값 대신 실제 model 저장 로직으로 교체하면서 테스트 유지

실행 예시는:

```bash
pytest tests/test_product_api.py
```