fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 존재하지 않아 읽을 파일이 없었습니다. 아래는 읽기 전용 환경 기준으로 바로 복사 가능한 표준 diff입니다.

```diff
diff --git a/apps/orders/domain/exceptions.py b/apps/orders/domain/exceptions.py
new file mode 100644
--- /dev/null
+++ b/apps/orders/domain/exceptions.py
@@
+class DomainError(Exception):
+    code = "domain_error"
+    message = "Domain rule was violated."
+
+    def __init__(self, message: str | None = None) -> None:
+        self.message = message or self.message
+        super().__init__(self.message)
+
+
+class OrderAlreadyPaid(DomainError):
+    code = "order_already_paid"
+    message = "이미 결제된 주문입니다."
+
+
+class OrderNotFound(DomainError):
+    code = "order_not_found"
+    message = "주문을 찾을 수 없습니다."
diff --git a/config/api_errors.py b/config/api_errors.py
new file mode 100644
--- /dev/null
+++ b/config/api_errors.py
@@
+from dataclasses import dataclass
+
+from django.http import HttpRequest, JsonResponse
+from ninja import NinjaAPI, Schema
+
+from apps.orders.domain.exceptions import DomainError, OrderAlreadyPaid, OrderNotFound
+
+
+class ProblemDetail(Schema):
+    type: str
+    title: str
+    status: int
+    detail: str
+    instance: str
+    code: str
+
+
+@dataclass(frozen=True)
+class ProblemSpec:
+    status: int
+    type: str
+    title: str
+
+
+DOMAIN_PROBLEMS: dict[type[DomainError], ProblemSpec] = {
+    OrderNotFound: ProblemSpec(
+        status=404,
+        type="https://api.example.com/problems/order-not-found",
+        title="Order Not Found",
+    ),
+    OrderAlreadyPaid: ProblemSpec(
+        status=409,
+        type="https://api.example.com/problems/order-already-paid",
+        title="Order Already Paid",
+    ),
+}
+
+
+def register_error_handlers(api: NinjaAPI) -> None:
+    @api.exception_handler(DomainError)
+    def handle_domain_error(request: HttpRequest, exc: DomainError) -> JsonResponse:
+        spec = DOMAIN_PROBLEMS.get(
+            type(exc),
+            ProblemSpec(
+                status=422,
+                type="https://api.example.com/problems/domain-error",
+                title="Domain Error",
+            ),
+        )
+        problem = ProblemDetail(
+            type=spec.type,
+            title=spec.title,
+            status=spec.status,
+            detail=exc.message,
+            instance=request.path,
+            code=exc.code,
+        )
+        return JsonResponse(
+            problem.model_dump(),
+            status=spec.status,
+            content_type="application/problem+json",
+        )
diff --git a/config/api.py b/config/api.py
new file mode 100644
--- /dev/null
+++ b/config/api.py
@@
+from ninja import NinjaAPI
+
+from apps.orders.api import router as orders_router
+from config.api_errors import register_error_handlers
+
+
+api = NinjaAPI()
+register_error_handlers(api)
+api.add_router("/orders/", orders_router)
diff --git a/apps/orders/api.py b/apps/orders/api.py
new file mode 100644
--- /dev/null
+++ b/apps/orders/api.py
@@
+from django.http import HttpRequest
+from ninja import Router, Schema
+
+from apps.orders.application import pay_order
+
+
+router = Router(tags=["orders"])
+
+
+class PayOrderIn(Schema):
+    payment_key: str
+
+
+class OrderOut(Schema):
+    id: int
+    status: str
+
+
+@router.post("/{order_id}/payment", response={200: OrderOut})
+def pay(request: HttpRequest, order_id: int, payload: PayOrderIn) -> OrderOut:
+    return pay_order(order_id=order_id, payment_key=payload.payment_key)
diff --git a/tests/test_api_errors.py b/tests/test_api_errors.py
new file mode 100644
--- /dev/null
+++ b/tests/test_api_errors.py
@@
+from django.http import HttpRequest
+from ninja import NinjaAPI
+from ninja.testing import TestClient
+
+from apps.orders.domain.exceptions import OrderAlreadyPaid
+from config.api_errors import register_error_handlers
+
+
+api = NinjaAPI()
+register_error_handlers(api)
+
+
+@api.get("/boom")
+def boom(request: HttpRequest) -> dict[str, bool]:
+    raise OrderAlreadyPaid()
+
+
+def test_domain_error_is_problem_detail() -> None:
+    response = TestClient(api).get("/boom")
+
+    assert response.status_code == 409
+    assert response["content-type"] == "application/problem+json"
+    assert response.json()["code"] == "order_already_paid"
```

**팀 표준**
- 도메인 계층은 `DomainError`만 발생시킨다. HTTP status, RFC 9457 `type`, `title`은 알지 않는다.
- API 전송 계층은 `@api.exception_handler(DomainError)`에서만 Problem Details로 변환한다.
- 새 도메인 예외를 추가하면 `DOMAIN_PROBLEMS`에 transport 매핑을 추가한다.
- 클라이언트 분기는 메시지가 아니라 안정적인 `code`로 한다.
- sync Ninja endpoint는 항상 `request: HttpRequest`와 명시적 반환 타입을 둔다.
- 목록 응답은 `list[Schema]`를 쓰고 `from typing import list`는 쓰지 않는다.

**검증**
```bash
python manage.py check
pytest tests/test_api_errors.py
```

---
> **관련 스킬 참조:**
> - Django Ninja API 오류 표준화 → **implementation-django-ninja** 스킬