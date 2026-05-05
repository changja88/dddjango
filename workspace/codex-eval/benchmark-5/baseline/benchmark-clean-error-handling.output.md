지정된 fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 현재 환경에 없었습니다. 대신 접근 가능한 trigger 파일을 확인했고, 해당 케이스가 `Fixture: none`인 “Django Ninja 공통 에러 응답 표준” 요청임을 확인했습니다.

아래 표준은 Django Ninja 공식 문서의 `@api.exception_handler(...)`, `api.create_response(...)`, 기본 `ValidationError` 처리 확장 방식을 기준으로 잡았습니다. 참고: [Django Ninja Handling errors](https://django-ninja.dev/guides/errors/), [Django Ninja Authentication custom exceptions](https://django-ninja.dev/guides/authentication/).

```diff
diff --git a/docs/api-error-standard.md b/docs/api-error-standard.md
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/docs/api-error-standard.md
@@ -0,0 +1,152 @@
+# Django Ninja API Error Standard
+
+## 목표
+
+Django Ninja API는 domain exception을 HTTP 세부사항과 직접 결합하지 않는다.
+도메인 계층은 비즈니스 실패의 의미만 표현하고, API 계층이 이를 일관된 error response로 변환한다.
+
+## 계층별 책임
+
+### Domain
+
+도메인 계층은 HTTP status, Django request, Ninja response를 알지 않는다.
+
+도메인 예외는 다음 정보만 가진다.
+
+- `code`: 클라이언트와 로그에서 안정적으로 사용할 에러 식별자
+- `message`: 외부에 노출 가능한 기본 메시지
+- `params`: 메시지 구성이나 디버깅에 필요한 안전한 값
+
+예:
+
+```python
+class DomainError(Exception):
+    code = "domain_error"
+    message = "Domain rule was violated."
+
+    def __init__(self, message: str | None = None, **params):
+        self.message = message or self.message
+        self.params = params
+        super().__init__(self.message)
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
+```
+
+금지:
+
+- domain exception 안에 `status_code`를 넣지 않는다.
+- domain exception 안에서 `HttpError`, `Http404`, `HttpResponse`를 만들지 않는다.
+- endpoint에서 domain exception을 매번 `try/except`로 감싸지 않는다.
+
+## API Error Response Shape
+
+모든 API 에러 응답은 아래 구조를 따른다.
+
+```json
+{
+  "error": {
+    "code": "order_not_found",
+    "message": "Order was not found.",
+    "details": {},
+    "request_id": "optional-request-id"
+  }
+}
+```
+
+필드 규칙:
+
+- `code`: stable machine-readable code
+- `message`: client-safe human-readable message
+- `details`: validation field errors, safe params, conflict 대상 등 구조화된 부가 정보
+- `request_id`: middleware나 header에서 얻을 수 있을 때만 포함
+
+내부 예외 메시지, traceback, DB 오류 원문, 외부 SDK 오류 원문은 응답에 그대로 노출하지 않는다.
+
+## Domain Error와 HTTP Status 매핑
+
+HTTP status는 API adapter 계층에서만 결정한다.
+
+```python
+DOMAIN_ERROR_STATUS = {
+    "order_not_found": 404,
+    "order_already_paid": 409,
+    "insufficient_stock": 409,
+    "invalid_order_state": 422,
+}
+```
+
+기본값:
+
+- 알 수 없는 `DomainError`: `400`
+- 인증 실패: `401`
+- 권한 실패: `403`
+- 리소스 없음: `404`
+- 상태 충돌: `409`
+- 입력 형식 또는 도메인 검증 실패: `422`
+- 예상하지 못한 서버 오류: `500`
+
+## Django Ninja 연결 방식
+
+Ninja API 생성 위치에서 전역 exception handler를 등록한다.
+
+```python
+from django.http import Http404
+from ninja import NinjaAPI
+from ninja.errors import AuthenticationError, AuthorizationError, ValidationError
+
+from common.domain_errors import DomainError
+
+
+api = NinjaAPI()
+
+
+def error_body(
+    *,
+    code: str,
+    message: str,
+    details: dict | list | None = None,
+    request_id: str | None = None,
+) -> dict:
+    body = {
+        "error": {
+            "code": code,
+            "message": message,
+            "details": details or {},
+        }
+    }
+    if request_id:
+        body["error"]["request_id"] = request_id
+    return body
+
+
+def get_request_id(request) -> str | None:
+    return getattr(request, "request_id", None) or request.headers.get("X-Request-ID")
+
+
+@api.exception_handler(DomainError)
+def handle_domain_error(request, exc: DomainError):
+    status = DOMAIN_ERROR_STATUS.get(exc.code, 400)
+    return api.create_response(
+        request,
+        error_body(
+            code=exc.code,
+            message=exc.message,
+            details=exc.params,
+            request_id=get_request_id(request),
+        ),
+        status=status,
+    )
+
+
+@api.exception_handler(ValidationError)
+def handle_validation_error(request, exc: ValidationError):
+    return api.create_response(
+        request,
+        error_body(
+            code="validation_error",
+            message="Request validation failed.",
+            details=exc.errors,
+            request_id=get_request_id(request),
+        ),
+        status=422,
+    )
+
+
+@api.exception_handler(Http404)
+def handle_not_found(request, exc: Http404):
+    return api.create_response(
+        request,
+        error_body(
+            code="not_found",
+            message="Resource was not found.",
+            request_id=get_request_id(request),
+        ),
+        status=404,
+    )
+
+
+@api.exception_handler(AuthenticationError)
+def handle_authentication_error(request, exc: AuthenticationError):
+    return api.create_response(
+        request,
+        error_body(code="authentication_failed", message="Authentication failed."),
+        status=401,
+    )
+
+
+@api.exception_handler(AuthorizationError)
+def handle_authorization_error(request, exc: AuthorizationError):
+    return api.create_response(
+        request,
+        error_body(code="permission_denied", message="Permission denied."),
+        status=403,
+    )
+```
+
+## Endpoint 작성 규칙
+
+Endpoint는 성공 흐름만 명확히 표현한다.
+
+```python
+@router.post("/orders")
+def create_order(request, payload: CreateOrderIn):
+    order = create_order_service(
+        user_id=request.auth.id,
+        command=payload.to_command(),
+    )
+    return OrderOut.from_domain(order)
+```
+
+권장:
+
+- endpoint에서 domain exception을 HTTP response로 직접 바꾸지 않는다.
+- service/application 계층은 domain exception을 그대로 올린다.
+- 외부 SDK, DB, network 오류는 application/infrastructure 경계에서 의미 있는 application/domain error로 감싸거나, 예상하지 못한 오류로 로깅되게 둔다.
+
+## 테스트 표준
+
+최소 테스트:
+
+- 각 domain exception이 정해진 status와 `error.code`로 응답되는지
+- validation error가 동일한 response envelope을 따르는지
+- endpoint에 `try/except DomainError`가 반복되지 않는지
+- 500 응답이 내부 예외 메시지를 노출하지 않는지
+
+예:
+
+```python
+def test_order_not_found_returns_standard_error(client):
+    response = client.get("/api/orders/not-existing")
+
+    assert response.status_code == 404
+    assert response.json() == {
+        "error": {
+            "code": "order_not_found",
+            "message": "Order was not found.",
+            "details": {},
+        }
+    }
+```
+
+## Clean Code 판단 기준
+
+- 변경 이유 분리: domain exception은 비즈니스 의미 때문에 바뀌고, HTTP 매핑은 API 정책 때문에 바뀐다.
+- 캡슐화: 호출부가 예외 내부 구조를 해석해 각자 response를 만들지 않는다.
+- 낮은 결합: domain은 Django/Ninja를 import하지 않는다.
+- 단순성: 처음부터 거대한 에러 프레임워크를 만들지 않고, `DomainError` + 전역 handler + status mapping으로 시작한다.
+- 명시성: `code`, `message`, `details`를 고정해 클라이언트가 예측 가능하게 처리한다.
```

핵심 기준은 하나입니다. **도메인 예외는 “무슨 비즈니스 규칙이 실패했는지”만 말하고, API 계층의 Ninja exception handler가 “그 실패를 어떤 HTTP 응답으로 보낼지”를 결정합니다.** 이렇게 두면 도메인 모델은 깨끗하게 유지되고, 응답 포맷 변경도 API 경계 한 곳에서 처리됩니다.