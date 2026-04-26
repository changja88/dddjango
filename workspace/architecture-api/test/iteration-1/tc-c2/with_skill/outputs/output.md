# RFC 9457 Problem Details 리팩토링

모든 에러 응답을 RFC 9457 Problem Details 형식으로 변환한다.
`Content-Type`은 `application/problem+json`을 사용해야 한다.

---

## 1. 404 Not Found

```
[Before]
```
```json
{
  "error_code": "NOT_FOUND",
  "message": "User not found"
}
```

```
[After]
```
```json
HTTP/1.1 404 Not Found
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/resource-not-found",
  "title": "Resource not found.",
  "status": 404,
  "detail": "User not found.",
  "instance": "/users/12345"
}
```

```
[Reason] RFC 9457 Problem Details — 커스텀 error_code/message 구조를 표준 필드(type, title, status, detail, instance)로 대체한다. type URI는 문제 유형을 문서화하는 안정적 식별자이고, title은 유형별 재사용 가능한 요약, detail은 이 특정 발생에 대한 설명이다.
```

---

## 2. 400 Bad Request (유효성 검증)

```
[Before]
```
```json
{
  "error_code": "VALIDATION_ERROR",
  "errors": [
    {"field": "email", "message": "Invalid format"}
  ]
}
```

```
[After]
```
```json
HTTP/1.1 400 Bad Request
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Request validation failed.",
  "status": 400,
  "detail": "One or more fields failed validation.",
  "instance": "/users",
  "errors": [
    {
      "field": "email",
      "message": "Invalid format"
    }
  ]
}
```

```
[Reason] RFC 9457 Problem Details (확장 필드) — 표준 5개 필드로 기본 구조를 맞추고, 필드별 상세 검증 오류는 errors 확장 필드로 포함한다. RFC 9457은 문제 유형 정의에 따라 확장 필드를 추가할 수 있으며, 클라이언트는 인식하지 못하는 확장 필드를 무시해야 한다.
```

---

## 3. 401 Unauthorized

```
[Before]
```
```json
{
  "error_code": "AUTH_FAILED",
  "message": "Invalid token"
}
```

```
[After]
```
```json
HTTP/1.1 401 Unauthorized
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/authentication-required",
  "title": "Authentication required.",
  "status": 401,
  "detail": "The provided token is invalid or has expired.",
  "instance": "/users/me"
}
```

```
[Reason] RFC 9457 Problem Details — 401은 인증(authentication) 실패를 의미한다. type URI를 통해 인증 관련 문서 페이지로 연결할 수 있고, detail에서 이 특정 실패의 원인을 서술한다. 커스텀 error_code 기반 분기 대신 type URI 기반으로 클라이언트가 문제 유형을 판별하도록 표준화한다.
```

---

## 4. 403 Forbidden

```
[Before]
```
```json
{
  "error_code": "FORBIDDEN",
  "message": "Admin only"
}
```

```
[After]
```
```json
HTTP/1.1 403 Forbidden
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/insufficient-permissions",
  "title": "Insufficient permissions.",
  "status": 403,
  "detail": "This action requires admin role.",
  "instance": "/admin/settings"
}
```

```
[Reason] RFC 9457 Problem Details — 403은 인가(authorization) 부족을 의미한다(누구인지는 알지만 권한 없음). title은 유형 단위로 재사용 가능한 요약이고, detail에서 구체적으로 어떤 권한이 필요한지 이 특정 발생을 설명한다.
```

---

## 5. 409 Conflict

```
[Before]
```
```json
{
  "error_code": "DUPLICATE",
  "message": "Email already exists"
}
```

```
[After]
```
```json
HTTP/1.1 409 Conflict
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/resource-conflict",
  "title": "Resource conflict.",
  "status": 409,
  "detail": "A user with this email address already exists.",
  "instance": "/users"
}
```

```
[Reason] RFC 9457 Problem Details — 409는 자원 충돌(중복 생성, 동시 수정)을 나타낸다. type URI로 충돌 해결 방법을 문서화할 수 있고, detail에서 어떤 필드가 충돌을 일으켰는지 구체적으로 설명한다.
```

---

## 6. 500 Internal Server Error

```
[Before]
```
```json
{
  "error_code": "INTERNAL_ERROR",
  "message": "Something went wrong"
}
```

```
[After]
```
```json
HTTP/1.1 500 Internal Server Error
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/internal-error",
  "title": "Internal server error.",
  "status": 500,
  "detail": "An unexpected error occurred. Please try again later.",
  "instance": "/orders/789"
}
```

```
[Reason] RFC 9457 Problem Details — 500은 서버 내부 문제를 나타내며, 재시도 시 성공할 수 있다. detail에 서버 내부 구현 정보(스택 트레이스, DB 오류 등)를 노출하지 않도록 주의한다. instance를 통해 운영팀이 특정 발생을 추적할 수 있다.
```

---

## 변환 요약

| 변환 전 | 변환 후 | 비고 |
|---------|---------|------|
| `error_code` | `type` (URI) | 문자열 코드 대신 문서화 가능한 URI 식별자 사용 |
| `message` | `title` + `detail` | 유형 요약(title)과 특정 발생 설명(detail)을 분리 |
| (없음) | `status` | HTTP 상태 코드를 본문에도 포함하여 일관성 확보 |
| (없음) | `instance` | 특정 발생을 식별하는 URI 추가 |
| `errors` (커스텀 배열) | `errors` (확장 필드) | RFC 9457 확장 필드로 유효성 검증 상세 정보 유지 |
| `Content-Type: application/json` | `Content-Type: application/problem+json` | RFC 9457 전용 미디어 타입 |

### 핵심 원칙

- **`type`은 안정적 URI**: 클라이언트가 문제 유형을 프로그래밍적으로 판별하는 데 사용하며, 해당 URI는 사람이 읽을 수 있는 문서로 연결되어야 한다.
- **`title`은 유형, `detail`은 발생**: 동일한 type을 가진 에러는 동일한 title을 가지되, detail은 각 발생마다 다를 수 있다.
- **모든 API 에러 응답에 일관되게 적용**: 에러 형식이 엔드포인트마다 다르면 클라이언트의 에러 처리 로직이 복잡해진다. RFC 9457을 전체 API에 걸쳐 단일 형식으로 사용한다.
- **확장 필드 활용**: 유효성 검증 에러의 필드별 상세 정보처럼, 표준 필드만으로 부족한 경우 확장 필드를 추가할 수 있다.
