**주요 내용**

Fixture path `/Users/hyun/Desktop/dddjango/none`는 존재하지 않아 fixture 파일을 읽을 수 없었습니다. 현재 read-only sandbox라 파일 생성/pytest 실행은 하지 못했습니다. 아래는 실제 프로젝트에 적용할 수 있는 unified diff 예시입니다. RED 테스트가 요청 schema validation 실패와 성공 응답을 먼저 고정하고, GREEN 구현은 endpoint와 service 책임을 분리합니다.

```diff
diff --git a/tests/isolated/orders/test_order_api.py b/tests/isolated/orders/test_order_api.py
new file mode 100644
--- /dev/null
+++ b/tests/isolated/orders/test_order_api.py
@@
+import pytest
+from ninja.testing import TestClient
+
+from apps.orders.api import router
+
+
+@pytest.fixture
+def client() -> TestClient:
+    return TestClient(router)
+
+
+def test_create_order_when_quantity_is_invalid_returns_validation_error(
+    client: TestClient,
+) -> None:
+    # Arrange
+    payload = {"sku": "SKU-001", "quantity": 0}
+
+    # Act
+    response = client.post("/", json=payload)
+
+    # Assert
+    assert response.status_code == 422
+    assert "detail" in response.json()
+
+
+def test_create_order_when_payload_is_valid_returns_created_order(
+    client: TestClient,
+) -> None:
+    # Arrange
+    payload = {"sku": "SKU-001", "quantity": 2}
+
+    # Act
+    response = client.post("/", json=payload)
+
+    # Assert
+    assert response.status_code == 201
+    assert response.json() == {
+        "id": 1,
+        "sku": "SKU-001",
+        "quantity": 2,
+        "status": "created",
+    }
diff --git a/apps/orders/schemas.py b/apps/orders/schemas.py
new file mode 100644
--- /dev/null
+++ b/apps/orders/schemas.py
@@
+from ninja import Field, Schema
+
+
+class OrderCreateIn(Schema):
+    sku: str = Field(..., min_length=1)
+    quantity: int = Field(..., ge=1)
+
+
+class OrderOut(Schema):
+    id: int
+    sku: str
+    quantity: int
+    status: str
diff --git a/apps/orders/services.py b/apps/orders/services.py
new file mode 100644
--- /dev/null
+++ b/apps/orders/services.py
@@
+from dataclasses import dataclass
+
+
+@dataclass(frozen=True)
+class CreateOrderCommand:
+    sku: str
+    quantity: int
+
+
+@dataclass(frozen=True)
+class CreatedOrder:
+    id: int
+    sku: str
+    quantity: int
+    status: str
+
+
+def create_order(command: CreateOrderCommand) -> CreatedOrder:
+    return CreatedOrder(
+        id=1,
+        sku=command.sku,
+        quantity=command.quantity,
+        status="created",
+    )
diff --git a/apps/orders/api.py b/apps/orders/api.py
new file mode 100644
--- /dev/null
+++ b/apps/orders/api.py
@@
+from django.http import HttpRequest
+from ninja import Router
+
+from apps.orders.schemas import OrderCreateIn, OrderOut
+from apps.orders.services import CreateOrderCommand, create_order
+
+router = Router(tags=["orders"])
+
+
+@router.post("/", response={201: OrderOut})
+def create_order_endpoint(
+    request: HttpRequest,
+    payload: OrderCreateIn,
+) -> tuple[int, OrderOut]:
+    order = create_order(
+        CreateOrderCommand(
+            sku=payload.sku,
+            quantity=payload.quantity,
+        )
+    )
+    return 201, OrderOut(
+        id=order.id,
+        sku=order.sku,
+        quantity=order.quantity,
+        status=order.status,
+    )
diff --git a/config/api.py b/config/api.py
new file mode 100644
--- /dev/null
+++ b/config/api.py
@@
+from ninja import NinjaAPI
+
+from apps.orders.api import router as orders_router
+
+api = NinjaAPI()
+api.add_router("/orders/", orders_router)
diff --git a/config/urls.py b/config/urls.py
--- a/config/urls.py
+++ b/config/urls.py
@@
+from django.urls import path
+
+from config.api import api
+
+urlpatterns = [
+    path("api/", api.urls),
+]
```

**예상 RED 실패**

첫 테스트는 `apps.orders.api`가 없어서 import error로 실패합니다. 이후 API만 만들고 schema validation이 없으면 `quantity=0`이 422를 반환하지 않아 실패해야 합니다. 두 번째 테스트는 service와 endpoint가 없거나 201 응답 계약이 없어서 실패합니다.

**GREEN 최소 구현**

위 `schemas.py`, `services.py`, `api.py`가 최소 GREEN입니다. endpoint는 `HttpRequest`를 명시하고, 반환 타입도 `tuple[int, OrderOut]`로 고정했습니다. 입력 검증은 Ninja `Schema`가 담당하고, 주문 생성 유스케이스는 service가 담당합니다.

**REFACTOR 방향**

실제 DB가 생기면 `create_order()` 안에 ORM을 직접 흩뿌리지 말고 repository 또는 selector/service 경계로 옮기면 됩니다. 테스트는 `TestClient(router)`를 유지해 schema와 endpoint contract를 빠르게 검증하고, DB 저장까지 검증하는 테스트만 `pytest.mark.django_db`로 별도 추가하는 편이 현실적입니다.

**검증 명령**

실행하지 못했습니다. 실제 프로젝트에서는 아래 순서로 확인하세요.

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/orders/test_order_api.py -q
python manage.py check
```

---
> **관련 스킬 참조:**
> - Django Ninja endpoint 테스트와 Schema 검증 → **implementation-django-ninja** 스킬