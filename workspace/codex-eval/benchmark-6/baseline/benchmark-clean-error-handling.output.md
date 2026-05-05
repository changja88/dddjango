fixture를 확인하려 했지만 `/Users/hyun/Desktop/dddjango/none` 경로가 존재하지 않았고, `/private/tmp/dddjango-codex-eval` 안에도 파일이 없습니다. 그래서 특정 코드 수정 대신 Django Ninja 프로젝트에 바로 적용할 수 있는 표준안을 unified diff 형태로 제시합니다.

```diff
diff --git a/docs/api-error-standard.md b/docs/api-error-standard.md
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/docs/api-error-standard.md
@@ -0,0 +1,142 @@
+# Domain Exception과 API Error Response 연결 표준
+
+## 원칙
+
+도메인 계층은 HTTP, Django Ninja, status code, response schema를 알지 않는다.
+도메인 예외는 비즈니스 실패의 의미만 표현한다.
+
+API 계층은 도메인 예외를 HTTP 응답으로 변환하는 책임만 가진다.
+이 변환은 endpoint마다 반복하지 않고 Ninja exception handler에 모은다.
+
+## 계층별 책임
+
+### Domain
+
+도메인 예외는 다음 정보만 가진다.
+
+- `code`: 안정적인 기계 판독용 에러 코드
+- `message`: 로그와 기본 응답에 쓸 수 있는 설명
+- `details`: 선택적인 구조화 정보
+
+도메인 예외에 넣지 않는다.
+
+- HTTP status code
+- Django `HttpRequest`
+- Ninja response schema
+- serializer / schema validation detail
+- 번역된 UI 문구
+
+예:
+
+```python
+class DomainError(Exception):
+    code = "DOMAIN_ERROR"
+    message = "Domain rule violated."
+
+    def __init__(self, message: str | None = None, *, details: dict | None = None):
+        self.message = message or self.message
+        self.details = details or {}
+        super().__init__(self.message)
+
+
+class OrderNotFound(DomainError):
+    code = "ORDER_NOT_FOUND"
+    message = "Order not found."
+
+
+class OrderAlreadyPaid(DomainError):
+    code = "ORDER_ALREADY_PAID"
+    message = "Order is already paid."
+```
+
+## API Error Response 형식
+
+모든 API 에러 응답은 같은 envelope를 사용한다.
+
+```json
+{
+  "error": {
+    "code": "ORDER_NOT_FOUND",
+    "message": "Order not found.",
+    "details": {},
+    "request_id": "optional-request-id"
+  }
+}
+```
+
+규칙:
+
+- `code`는 클라이언트가 분기할 수 있는 안정적인 값이다.
+- `message`는 사용자에게 그대로 노출 가능한 수준으로만 쓴다.
+- 내부 예외 메시지, SQL, stack trace, 환경 정보는 응답에 넣지 않는다.
+- `details`는 필드 오류나 제한값처럼 클라이언트가 처리 가능한 구조화 정보에만 쓴다.
+
+## Domain Error와 HTTP Status 매핑
+
+HTTP status는 API 계층에서 매핑한다.
+
+```python
+from dataclasses import dataclass
+
+
+@dataclass(frozen=True)
+class ApiErrorSpec:
+    status: int
+    public_message: str | None = None
+
+
+DOMAIN_ERROR_SPECS: dict[str, ApiErrorSpec] = {
+    "ORDER_NOT_FOUND": ApiErrorSpec(status=404),
+    "ORDER_ALREADY_PAID": ApiErrorSpec(status=409),
+}
+
+
+DEFAULT_DOMAIN_ERROR_SPEC = ApiErrorSpec(
+    status=400,
+    public_message="The request violates a business rule.",
+)
+```
+
+기준:
+
+- 리소스 없음: `404`
+- 현재 상태와 충돌: `409`
+- 권한 없음: `403`
+- 인증 필요: `401`
+- 입력 형식 오류: `422`
+- 도메인 규칙 위반이지만 더 구체적 의미가 없을 때: `400`
+- 예상하지 못한 서버 오류: `500`
+
+## Django Ninja Exception Handler
+
+endpoint에서는 도메인 예외를 잡지 않는다.
+Ninja API 객체에 중앙 handler를 등록한다.
+
+```python
+from ninja import NinjaAPI
+
+api = NinjaAPI()
+
+
+def build_error_response(
+    *,
+    code: str,
+    message: str,
+    details: dict | None = None,
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
+@api.exception_handler(DomainError)
+def handle_domain_error(request, exc: DomainError):
+    spec = DOMAIN_ERROR_SPECS.get(exc.code, DEFAULT_DOMAIN_ERROR_SPEC)
+    message = spec.public_message or exc.message
+
+    return api.create_response(
+        request,
+        build_error_response(
+            code=exc.code,
+            message=message,
+            details=exc.details,
+            request_id=getattr(request, "request_id", None),
+        ),
+        status=spec.status,
+    )
+```
+
+## Endpoint 작성 기준
+
+endpoint는 성공 흐름만 읽히게 둔다.
+
+```python
+@router.post("/orders/{order_id}/pay")
+def pay_order(request, order_id: int):
+    result = pay_order_service(order_id=order_id)
+    return result
+```
+
+피한다:
+
+```python
+@router.post("/orders/{order_id}/pay")
+def pay_order(request, order_id: int):
+    try:
+        return pay_order_service(order_id=order_id)
+    except OrderAlreadyPaid:
+        raise HttpError(409, "Order is already paid.")
+```
+
+## Validation Error와 Domain Error 구분
+
+입력 schema가 틀린 경우는 validation error다.
+비즈니스 규칙을 만족하지 못한 경우는 domain error다.
+
+예:
+
+- `amount`가 문자열임: validation error
+- `amount`가 잔액보다 큼: domain error
+- `order_id` 형식이 틀림: validation error
+- 해당 주문이 없음: domain error
+
+## 로깅 기준
+
+domain error는 일반적으로 warning 또는 info로 기록한다.
+예상하지 못한 exception은 error로 기록하고 응답은 일반화한다.
+
+```python
+@api.exception_handler(Exception)
+def handle_unexpected_error(request, exc: Exception):
+    logger.exception("Unexpected API error")
+    return api.create_response(
+        request,
+        build_error_response(
+            code="INTERNAL_SERVER_ERROR",
+            message="Internal server error.",
+            request_id=getattr(request, "request_id", None),
+        ),
+        status=500,
+    )
+```
+
+## 테스트 기준
+
+최소 테스트:
+
+- 도메인 예외가 정해진 HTTP status로 변환되는지
+- 응답 body가 표준 envelope를 따르는지
+- 알 수 없는 domain error가 기본 status와 message로 변환되는지
+- 예상하지 못한 exception이 내부 정보를 노출하지 않는지
+- validation error와 domain error 응답 형식이 일관적인지
+
+## 판단 기준
+
+새 도메인 예외를 추가할 때는 먼저 다음을 확인한다.
+
+- 클라이언트가 별도로 분기해야 하는 실패인가?
+- 기존 에러 코드로 의미를 충분히 표현할 수 없는가?
+- HTTP status가 도메인 계층이 아니라 API 계층에서 결정되는가?
+- 응답 message가 내부 구현을 노출하지 않는가?
+
+불필요한 예외 클래스를 늘리지 않는다.
+같은 비즈니스 실패이고 `details`만 다른 경우에는 같은 예외를 재사용한다.
```

핵심 표준은 이겁니다: **domain exception은 비즈니스 의미만 담고, API 계층의 중앙 exception handler가 HTTP status와 response shape로 번역합니다.** endpoint마다 `try/except`로 `HttpError`를 던지기 시작하면 도메인 규칙과 전송 계층이 섞이고, 에러 응답 형식도 빠르게 불일치합니다.