# RFC 9457 Problem Details 형식으로 리팩토링

## RFC 9457 개요

RFC 9457 (Problem Details for HTTP APIs)은 HTTP API에서 에러 응답을 표현하기 위한 표준 형식이다. `Content-Type: application/problem+json`을 사용하며, 다음 필드를 정의한다:

| 필드 | 필수 | 설명 |
|------|------|------|
| `type` | 권장 | 에러 유형을 식별하는 URI |
| `title` | 권장 | 사람이 읽을 수 있는 에러 요약 |
| `status` | 권장 | HTTP 상태 코드 |
| `detail` | 선택 | 해당 에러 발생에 대한 구체적 설명 |
| `instance` | 선택 | 해당 에러 발생 건을 식별하는 URI |

이 외에 확장(extension) 필드를 자유롭게 추가할 수 있다.

---

## 변환 결과

### 404 Not Found

**기존:**
```json
{"error_code": "NOT_FOUND", "message": "User not found"}
```

**RFC 9457:**
```json
{
  "type": "https://api.example.com/problems/not-found",
  "title": "Not Found",
  "status": 404,
  "detail": "User not found"
}
```

---

### 400 Validation Error

**기존:**
```json
{"error_code": "VALIDATION_ERROR", "errors": [{"field": "email", "message": "Invalid format"}]}
```

**RFC 9457:**
```json
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Validation Error",
  "status": 400,
  "detail": "One or more fields failed validation.",
  "errors": [
    {
      "pointer": "/email",
      "detail": "Invalid format"
    }
  ]
}
```

> `errors`는 RFC 9457의 확장 필드이다. `pointer` 형식은 JSON Pointer(RFC 6901) 표기를 따른다.

---

### 401 Unauthorized

**기존:**
```json
{"error_code": "AUTH_FAILED", "message": "Invalid token"}
```

**RFC 9457:**
```json
{
  "type": "https://api.example.com/problems/authentication-failed",
  "title": "Authentication Failed",
  "status": 401,
  "detail": "Invalid token"
}
```

---

### 403 Forbidden

**기존:**
```json
{"error_code": "FORBIDDEN", "message": "Admin only"}
```

**RFC 9457:**
```json
{
  "type": "https://api.example.com/problems/forbidden",
  "title": "Forbidden",
  "status": 403,
  "detail": "Admin only"
}
```

---

### 409 Conflict

**기존:**
```json
{"error_code": "DUPLICATE", "message": "Email already exists"}
```

**RFC 9457:**
```json
{
  "type": "https://api.example.com/problems/conflict",
  "title": "Conflict",
  "status": 409,
  "detail": "Email already exists"
}
```

---

### 500 Internal Server Error

**기존:**
```json
{"error_code": "INTERNAL_ERROR", "message": "Something went wrong"}
```

**RFC 9457:**
```json
{
  "type": "https://api.example.com/problems/internal-error",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "Something went wrong"
}
```

---

## HTTP 응답 헤더

모든 에러 응답에 다음 Content-Type 헤더를 사용해야 한다:

```
Content-Type: application/problem+json
```

---

## 매핑 요약

| HTTP Status | 기존 `error_code` | RFC 9457 `type` (경로) | `title` |
|---|---|---|---|
| 404 | `NOT_FOUND` | `/problems/not-found` | Not Found |
| 400 | `VALIDATION_ERROR` | `/problems/validation-error` | Validation Error |
| 401 | `AUTH_FAILED` | `/problems/authentication-failed` | Authentication Failed |
| 403 | `FORBIDDEN` | `/problems/forbidden` | Forbidden |
| 409 | `DUPLICATE` | `/problems/conflict` | Conflict |
| 500 | `INTERNAL_ERROR` | `/problems/internal-error` | Internal Server Error |

---

## 적용 시 참고사항

1. **`type` URI는 실제 문서 URL로 운영하라.** 해당 URI에 접근하면 에러 유형에 대한 설명 문서가 반환되는 것이 권장된다.
2. **`type`을 생략하면 기본값은 `about:blank`이다.** 이 경우 `title`은 HTTP 상태 코드의 표준 문구와 동일해야 한다.
3. **`detail`에 민감 정보를 노출하지 마라.** 특히 500 에러에서 스택 트레이스나 내부 구현 세부사항을 포함하면 안 된다.
4. **확장 필드를 활용하라.** `errors` 배열(유효성 검증), `retryAfter`(429 Rate Limit) 등 도메인 특화 정보를 확장 필드로 추가할 수 있다.
