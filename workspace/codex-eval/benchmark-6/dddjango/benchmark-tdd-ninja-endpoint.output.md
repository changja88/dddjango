Fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, 현재 workspace에도 파일이 없어 pytest를 실행하거나 파일을 수정하지 못했습니다. 아래는 그대로 적용 가능한 **RED 테스트 → GREEN 구현 → REFACTOR 방향**의 unified diff 예시입니다. Django Ninja `TestClient`로 validation 실패와 성공 응답을 먼저 검증하고, endpoint는 HTTP/schema 책임만, service는 유스케이스 책임만 갖게 분리합니다.

**[주요 내용]**

```diff
diff --git a/products/tests/isolated/test_products_api.py b/products/tests/isolated/test_products_api.py
new file mode 100644
--- /dev/null
+++ b/products/tests/isolated/test_products_api.py
@@ -0,0 +1,41 @@
+import pytest
+from ninja.testing import TestClient
+
+from products.api import router
+from products.services import CreatedProduct
+
+
+@pytest.fixture
+def client() -> TestClient:
+    return TestClient(router)
+
+
+def test_create_product_invalid_payload_returns_validation_error(client: TestClient) -> None:
+    # Arrange
+    payload = {"name": "", "price": -100}
+
+    # Act
+    response = client.post("/", json=payload)
+
+    # Assert
+    assert response.status_code == 422
+    body = response.json()
+    assert "detail" in body
+    assert any(error["loc"][-1] == "name" for error in body["detail"])
+    assert any(error["loc"][-1] == "price" for error in body["detail"])
+
+
+def test_create_product_valid_payload_returns_created_product(
+    client: TestClient,
+    monkeypatch: pytest.MonkeyPatch,
+) -> None:
+    # Arrange
+    def fake_create_product(*, name: str, price: int) -> CreatedProduct:
+        return CreatedProduct(id=1, name=name, price=price)
+
+    monkeypatch.setattr("products.api.create_product", fake_create_product)
+    payload = {"name": "Keyboard", "price": 39000}
+
+    # Act
+    response = client.post("/", json=payload)
+
+    # Assert
+    assert response.status_code == 201
+    assert response.json() == {"id": 1, "name": "Keyboard", "price": 39000}
diff --git a/products/schemas.py b/products/schemas.py
new file mode 100644
--- /dev/null
+++ b/products/schemas.py
@@ -0,0 +1,13 @@
+from ninja import Field, Schema
+
+
+class CreateProductRequest(Schema):
+    name: str = Field(..., min_length=1, max_length=120)
+    price: int = Field(..., gt=0)
+
+
+class ProductResponse(Schema):
+    id: int
+    name: str
+    price: int
diff --git a/products/services.py b/products/services.py
new file mode 100644
--- /dev/null
+++ b/products/services.py
@@ -0,0 +1,16 @@
+from dataclasses import dataclass
+
+
+@dataclass(frozen=True)
+class CreatedProduct:
+    id: int
+    name: str
+    price: int
+
+
+def create_product(*, name: str, price: int) -> CreatedProduct:
+    return CreatedProduct(
+        id=1,
+        name=name,
+        price=price,
+    )
diff --git a/products/api.py b/products/api.py
new file mode 100644
--- /dev/null
+++ b/products/api.py
@@ -0,0 +1,17 @@
+from django.http import HttpRequest
+from ninja import Router
+
+from products.schemas import CreateProductRequest, ProductResponse
+from products.services import create_product
+
+router = Router()
+
+
+@router.post("/", response={201: ProductResponse})
+def create_product_endpoint(
+    request: HttpRequest,
+    payload: CreateProductRequest,
+) -> tuple[int, ProductResponse]:
+    product = create_product(name=payload.name, price=payload.price)
+    return 201, ProductResponse(id=product.id, name=product.name, price=product.price)
```

**RED**

먼저 `products/tests/isolated/test_products_api.py`만 추가해서 실행합니다.

예상 실패:
- `products.api`, `products.schemas`, `products.services`가 없어서 import 실패
- 또는 schema validation이 없으면 invalid payload가 `422`를 반환하지 않음
- endpoint가 service 결과를 응답 schema로 변환하지 않으면 성공 응답 assertion 실패

**GREEN**

`schemas.py`, `services.py`, `api.py`를 추가합니다. 핵심은 요청 검증은 `CreateProductRequest`가 맡고, endpoint는 `create_product()` service를 호출한 뒤 `ProductResponse`로 변환하는 것입니다. sync endpoint라서 첫 인자는 `request: HttpRequest`, 반환 타입은 `tuple[int, ProductResponse]`로 명시했습니다.

**REFACTOR**

실제 프로젝트에서는 `create_product()` 안의 `id=1` fake 구현을 DB repository 또는 application service로 바꿉니다. endpoint 테스트는 지금처럼 service를 monkeypatch해서 HTTP/schema 계약만 빠르게 검증하고, service 테스트는 별도 `tests/isolated/unit/test_products_service.py`에서 fake repository로 비즈니스 규칙을 검증하는 구성이 좋습니다.

실행은 이 환경에서 하지 못했습니다. 실제 프로젝트에서는 다음 순서로 돌리면 됩니다.

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest products/tests/isolated/test_products_api.py -q
python manage.py check
```

---
> **관련 스킬 참조:**
> - Django Ninja endpoint/API 구현 → **implementation-django-ninja** 스킬
> - pytest endpoint 테스트와 fixture 구성 → **implementation-test** 스킬
> - Red-Green-Refactor 진행 → **implementation-tdd** 스킬