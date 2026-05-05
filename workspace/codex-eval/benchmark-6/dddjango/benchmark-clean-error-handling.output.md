Fixture 확인 결과 `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, 현재 워크스페이스에도 읽을 프로젝트 파일이 없습니다. 아래는 Django Ninja 공식 `@api.exception_handler`/`create_response` 패턴과 RFC 9457 Problem Details 기준으로 만든 팀 표준 diff입니다. 핵심은 **도메인 예외는 HTTP를 모르고**, **API 어댑터만 HTTP status/problem response를 안다**는 경계입니다.

```diff
diff --git a/apps/orders/domain/exceptions.py b/apps/orders/domain/exceptions.py
new file mode 100644
--- /dev/null
+++ b/apps/orders/domain/exceptions.py
@@
+class DomainError(Exception):
+    code = "domain_error"
+    message = "Domain rule violation."
+
+    def __init__(self, message: str | None = None) -> None:
+        super().__init__(message or self.message)
+
+
+class OrderNotFound(DomainError):
+    code = "order_not_found"
+    message = "Order was not found."
+
+
+class OrderAlreadyPaid(DomainError):
+    code = "order_already_paid"
+    message = "Order is already paid."
diff --git a/config/api_errors.py b/config/api_errors.py
new file mode 100644
--- /dev/null
+++ b/config/api_errors.py
@@
+from dataclasses import dataclass
+from http import HTTPStatus
+
+from django.http import HttpRequest, JsonResponse
+from ninja import NinjaAPI, Schema
+
+from apps.orders.domain.exceptions import (
+    DomainError,
+    OrderAlreadyPaid,
+    OrderNotFound,
+)
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
+class ErrorSpec:
+    status: HTTPStatus
+    title: str
+    type: str
+
+
+DOMAIN_ERROR_SPECS: dict[type[DomainError], ErrorSpec] = {
+    OrderNotFound: ErrorSpec(
+        status=HTTPStatus.NOT_FOUND,
+        title="Order not found",
+        type="https://api.example.com/problems/order-not-found",
+    ),
+    OrderAlreadyPaid: ErrorSpec(
+        status=HTTPStatus.CONFLICT,
+        title="Order already paid",
+        type="https://api.example.com/problems/order-already-paid",
+    ),
+}
+
+
+def register_error_handlers(api: NinjaAPI) -> None:
+    @api.exception_handler(DomainError)
+    def handle_domain_error(
+        request: HttpRequest,
+        exc: DomainError,
+    ) -> JsonResponse:
+        spec = DOMAIN_ERROR_SPECS.get(
+            type(exc),
+            ErrorSpec(
+                status=HTTPStatus.UNPROCESSABLE_ENTITY,
+                title="Domain rule violation",
+                type="https://api.example.com/problems/domain-rule-violation",
+            ),
+        )
+        problem = ProblemDetail(
+            type=spec.type,
+            title=spec.title,
+            status=spec.status.value,
+            detail=str(exc),
+            instance=request.path,
+            code=exc.code,
+        )
+        return JsonResponse(
+            problem.model_dump(),
+            status=problem.status,
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
+from config.api_errors import ProblemDetail
+
+router = Router(tags=["orders"])
+
+
+class PayOrderIn(Schema):
+    amount: int
+
+
+class OrderOut(Schema):
+    id: int
+    status: str
+
+
+@router.post(
+    "/{order_id}/payments",
+    response={200: OrderOut, 404: ProblemDetail, 409: ProblemDetail},
+)
+def pay_order(
+    request: HttpRequest,
+    order_id: int,
+    payload: PayOrderIn,
+) -> OrderOut:
+    return pay_order_service(order_id=order_id, amount=payload.amount)
```

표준 규칙은 이렇게 고정하면 됩니다.

1. `DomainError` 계층에는 `status`, `response`, `HttpError`, `JsonResponse`를 넣지 않는다.
2. HTTP 상태와 Problem Details 변환은 `config/api_errors.py` 같은 transport 계층에서만 한다.
3. 상태 충돌은 `409`, 의미적으로 처리할 수 없는 요청은 `422`, 존재하지 않는 리소스는 `404`로 매핑한다.
4. 모든 API 오류 응답은 `application/problem+json`과 `type/title/status/detail/instance`를 유지한다.
5. sync endpoint는 항상 `request: HttpRequest`와 명시적 반환 타입을 쓴다.
6. 목록 응답은 `list[SomeSchema]`를 쓰고 `from typing import list`는 쓰지 않는다.

검증은 적용 후 최소한 아래를 실행하세요.

```bash
python manage.py check
pytest
```

에러 핸들러 테스트에는 `Content-Type`이 `application/problem+json`으로 시작하는지, `status` 필드가 실제 HTTP status와 같은지, 도메인 예외별 `code`가 안정적으로 내려가는지를 넣으면 됩니다.

참고: Django Ninja error handling 공식 문서 `https://django-ninja.dev/guides/errors/`

---
> **관련 스킬 참조:**
> - Django Ninja API 오류 처리 → **implementation-django-ninja** 스킬