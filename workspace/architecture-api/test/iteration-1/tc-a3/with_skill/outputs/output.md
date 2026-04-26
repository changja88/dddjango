# Payment API Design

## Resources

| Resource | Description |
|----------|-------------|
| `payments` | 결제 리소스. 결제 생성, 조회, 확인을 담당 |
| `payments/{id}/refunds` | 환불 리소스. 특정 결제에 대한 환불을 담당 |

---

## Endpoints

| Method | URL | Description | Idempotent |
|--------|-----|-------------|:----------:|
| POST | `/v1/payments` | 결제 생성 | X (Idempotency-Key 필수) |
| GET | `/v1/payments/{payment_id}` | 결제 단건 조회 | O |
| POST | `/v1/payments/{payment_id}/confirm` | 결제 확인(캡처) | X (Idempotency-Key 필수) |
| POST | `/v1/payments/{payment_id}/refunds` | 환불 생성 | X (Idempotency-Key 필수) |
| GET | `/v1/payments/{payment_id}/refunds` | 환불 목록 조회 | O |
| GET | `/v1/payments/{payment_id}/refunds/{refund_id}` | 환불 단건 조회 | O |

> **Note**: `confirm`은 URL에 동사가 포함된 예외 케이스다. 결제 확인은 단순한 상태 변경이 아니라 외부 PG사와의 통신을 수반하는 프로세스성 액션이므로, POST + 동사 형태를 허용한다. 이는 Stripe의 `/v1/payment_intents/{id}/confirm` 패턴과 동일하다.

---

## 1. 결제 생성

### Request

```
POST /v1/payments
Authorization: Bearer {token}
Content-Type: application/json
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
```

```json
{
  "amount": 50000,
  "currency": "KRW",
  "payment_method": "card",
  "description": "프리미엄 구독 결제",
  "metadata": {
    "order_id": "ORD-20260404-001"
  }
}
```

### Response -- 201 Created

```
HTTP/2 201 Created
Content-Type: application/json
Location: /v1/payments/pay_1234567890
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1743724800
```

```json
{
  "id": "pay_1234567890",
  "status": "pending",
  "amount": 50000,
  "currency": "KRW",
  "payment_method": "card",
  "description": "프리미엄 구독 결제",
  "metadata": {
    "order_id": "ORD-20260404-001"
  },
  "created_at": "2026-04-04T10:00:00Z",
  "confirmed_at": null,
  "refunded_amount": 0
}
```

---

## 2. 결제 조회

### Request

```
GET /v1/payments/pay_1234567890
Authorization: Bearer {token}
```

### Response -- 200 OK

```
HTTP/2 200 OK
Content-Type: application/json
Cache-Control: no-store
```

```json
{
  "id": "pay_1234567890",
  "status": "confirmed",
  "amount": 50000,
  "currency": "KRW",
  "payment_method": "card",
  "description": "프리미엄 구독 결제",
  "metadata": {
    "order_id": "ORD-20260404-001"
  },
  "created_at": "2026-04-04T10:00:00Z",
  "confirmed_at": "2026-04-04T10:00:05Z",
  "refunded_amount": 0
}
```

---

## 3. 결제 확인 (Confirm/Capture)

### Request

```
POST /v1/payments/pay_1234567890/confirm
Authorization: Bearer {token}
Content-Type: application/json
Idempotency-Key: 660e8400-e29b-41d4-a716-446655440001
```

```json
{
  "payment_method_details": {
    "card_number_token": "tok_abc123"
  }
}
```

### Response -- 200 OK

```
HTTP/2 200 OK
Content-Type: application/json
```

```json
{
  "id": "pay_1234567890",
  "status": "confirmed",
  "amount": 50000,
  "currency": "KRW",
  "payment_method": "card",
  "description": "프리미엄 구독 결제",
  "metadata": {
    "order_id": "ORD-20260404-001"
  },
  "created_at": "2026-04-04T10:00:00Z",
  "confirmed_at": "2026-04-04T10:00:05Z",
  "refunded_amount": 0
}
```

---

## 4. 환불 생성

### Request

```
POST /v1/payments/pay_1234567890/refunds
Authorization: Bearer {token}
Content-Type: application/json
Idempotency-Key: 770e8400-e29b-41d4-a716-446655440002
```

```json
{
  "amount": 50000,
  "reason": "customer_request"
}
```

> `amount`를 생략하면 전액 환불. 부분 환불 시 금액을 명시한다.

### Response -- 201 Created

```
HTTP/2 201 Created
Content-Type: application/json
Location: /v1/payments/pay_1234567890/refunds/ref_9876543210
```

```json
{
  "id": "ref_9876543210",
  "payment_id": "pay_1234567890",
  "status": "pending",
  "amount": 50000,
  "reason": "customer_request",
  "created_at": "2026-04-04T11:00:00Z"
}
```

---

## 5. 환불 목록 조회

### Request

```
GET /v1/payments/pay_1234567890/refunds?limit=20&cursor=eyJpZCI6MTB9
Authorization: Bearer {token}
```

### Response -- 200 OK

```json
{
  "data": [
    {
      "id": "ref_9876543210",
      "payment_id": "pay_1234567890",
      "status": "succeeded",
      "amount": 50000,
      "reason": "customer_request",
      "created_at": "2026-04-04T11:00:00Z"
    }
  ],
  "has_more": false,
  "next_cursor": null
}
```

---

## Idempotency (멱등성)

### 적용 대상

결제 생성, 결제 확인, 환불 생성 -- 모든 POST 엔드포인트에 `Idempotency-Key` 헤더를 필수로 요구한다.

### 동작 방식

```
Client                          Server
  |                               |
  |-- POST /v1/payments --------->|
  |   Idempotency-Key: uuid-abc  |
  |                               |-- Key "uuid-abc" 조회
  |                               |-- 없음 -> 결제 처리
  |                               |-- Key + 상태코드 + 응답 저장
  |<-- 201 Created ---------------|
  |                               |
  |   (네트워크 오류, 응답 미수신)  |
  |                               |
  |-- POST /v1/payments --------->|  (동일 요청 재시도)
  |   Idempotency-Key: uuid-abc  |
  |                               |-- Key "uuid-abc" 조회
  |                               |-- 있음 -> 저장된 응답 반환
  |<-- 201 Created (저장된 응답) --|
```

### 규칙

| 규칙 | 설명 |
|------|------|
| 키 형식 | V4 UUID 권장 |
| 키 만료 | 24시간 후 만료 |
| 저장소 | 내구성 있는 저장소 (DB 또는 Redis) |
| 저장 내용 | 키, HTTP 상태 코드, 응답 본문 |
| 동시 요청 | 동일 키의 동시 요청은 하나만 처리하고 나머지는 409 반환 |
| 키 누락 | `Idempotency-Key` 헤더 없이 POST 시 400 반환 |
| 키 재사용 + 다른 본문 | 동일 키로 다른 요청 본문을 보낼 경우 422 반환 |

### Idempotency-Key 누락 시 에러

```
HTTP/2 400 Bad Request
Content-Type: application/problem+json
```

```json
{
  "type": "https://api.example.com/problems/missing-idempotency-key",
  "title": "Idempotency-Key header is required.",
  "status": 400,
  "detail": "POST /v1/payments requires an Idempotency-Key header to prevent duplicate charges.",
  "instance": "/v1/payments"
}
```

### 동일 키 + 다른 요청 본문

```
HTTP/2 422 Unprocessable Entity
Content-Type: application/problem+json
```

```json
{
  "type": "https://api.example.com/problems/idempotency-key-reuse",
  "title": "Idempotency key already used with different parameters.",
  "status": 422,
  "detail": "The Idempotency-Key 'uuid-abc' was already used with a different request body. Generate a new key for a new request.",
  "instance": "/v1/payments"
}
```

### Race Condition 처리

```
HTTP/2 409 Conflict
Content-Type: application/problem+json
```

```json
{
  "type": "https://api.example.com/problems/idempotency-key-in-progress",
  "title": "A request with this idempotency key is already being processed.",
  "status": 409,
  "detail": "Another request with Idempotency-Key 'uuid-abc' is currently in progress. Please retry after a short delay.",
  "instance": "/v1/payments"
}
```

---

## Rate Limiting

### 정책

| Tier | 대상 | 제한 | 알고리즘 |
|------|------|------|----------|
| Standard | 일반 API 키 | 100 req/min | Token Bucket |
| Premium | 프리미엄 API 키 | 1000 req/min | Token Bucket |

> Token Bucket을 선택한 이유: 퍼블릭 API의 기본 알고리즘으로, 제어된 버스트를 허용하면서 평균 요청률을 제한한다.

### 응답 헤더

모든 응답에 Rate Limit 헤더를 포함한다.

```
X-RateLimit-Limit: 100          # 윈도우 내 최대 요청 수
X-RateLimit-Remaining: 56       # 남은 요청 수
X-RateLimit-Reset: 1743724800   # 리셋 시각 (UTC epoch seconds)
```

### 429 Too Many Requests

```
HTTP/2 429 Too Many Requests
Content-Type: application/problem+json
Retry-After: 30
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1743724800
```

```json
{
  "type": "https://api.example.com/problems/rate-limit-exceeded",
  "title": "Rate limit exceeded.",
  "status": 429,
  "detail": "You have exceeded the rate limit of 100 requests per minute. Retry after 30 seconds.",
  "instance": "/v1/payments"
}
```

### 적용 순서

Rate Limit 검사는 인증 직후, 비용이 큰 작업(DB 조회, PG사 통신) 이전에 수행한다.

```
Request -> Authentication -> Rate Limit Check -> Business Logic -> Response
```

---

## Error Responses

모든 에러 응답은 RFC 9457 Problem Details 형식을 사용한다.

### 인증 실패 -- 401

```
HTTP/2 401 Unauthorized
Content-Type: application/problem+json
WWW-Authenticate: Bearer
```

```json
{
  "type": "https://api.example.com/problems/unauthorized",
  "title": "Authentication required.",
  "status": 401,
  "detail": "The provided API key is invalid or expired.",
  "instance": "/v1/payments"
}
```

### 권한 부족 -- 403

```json
{
  "type": "https://api.example.com/problems/forbidden",
  "title": "Insufficient permissions.",
  "status": 403,
  "detail": "Your API key does not have permission to create refunds.",
  "instance": "/v1/payments/pay_1234567890/refunds"
}
```

### 결제 없음 -- 404

```json
{
  "type": "https://api.example.com/problems/not-found",
  "title": "Payment not found.",
  "status": 404,
  "detail": "No payment exists with id 'pay_9999999999'.",
  "instance": "/v1/payments/pay_9999999999"
}
```

### 유효성 검증 실패 -- 422

```json
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Validation failed.",
  "status": 422,
  "detail": "The request body contains invalid fields.",
  "instance": "/v1/payments",
  "errors": [
    {
      "field": "amount",
      "message": "Amount must be a positive integer."
    },
    {
      "field": "currency",
      "message": "Currency 'ABC' is not supported."
    }
  ]
}
```

### 환불 금액 초과 -- 422

```json
{
  "type": "https://api.example.com/problems/refund-exceeds-payment",
  "title": "Refund amount exceeds payment.",
  "status": 422,
  "detail": "Requested refund of 60000 KRW exceeds the remaining refundable amount of 50000 KRW.",
  "instance": "/v1/payments/pay_1234567890/refunds"
}
```

### 이미 확인된 결제를 다시 확인 -- 409

```json
{
  "type": "https://api.example.com/problems/payment-already-confirmed",
  "title": "Payment already confirmed.",
  "status": 409,
  "detail": "Payment 'pay_1234567890' has already been confirmed and cannot be confirmed again.",
  "instance": "/v1/payments/pay_1234567890/confirm"
}
```

---

## Payment Status Flow

```
pending -> confirmed -> partially_refunded -> refunded
                     \-> refund_failed
pending -> failed
pending -> cancelled
```

| Status | Description |
|--------|-------------|
| `pending` | 결제 생성됨, 아직 확인되지 않음 |
| `confirmed` | 결제 확인(캡처) 완료 |
| `partially_refunded` | 부분 환불 처리됨 |
| `refunded` | 전액 환불 완료 |
| `failed` | 결제 실패 (PG사 거절 등) |
| `cancelled` | 확인 전 취소됨 |

---

## Versioning

URL path 방식으로 메이저 버전을 관리한다 (`/v1/`). 모든 엔드포인트는 `/v1/` 접두사를 포함하며, breaking change가 필요할 경우 `/v2/`로 새 버전을 생성한다.

- 응답에 필드를 추가하는 것은 non-breaking change이므로 버전을 올리지 않는다
- 필드 제거, 이름 변경, 타입 변경은 breaking change이므로 새 버전이 필요하다
- 클라이언트는 인식하지 못하는 필드를 무시해야 한다

---

## Authentication

Bearer Token (JWT) 방식을 사용한다. 모든 요청에 `Authorization` 헤더를 포함해야 한다.

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

- API 키는 쿼리 파라미터에 포함하지 않는다 (URL은 서버/프록시 로그에 기록됨)
- 모든 통신은 HTTPS를 사용한다

---

## Client-Side Retry Guide

| 조건 | 재시도 가능 | 전략 |
|------|:----------:|------|
| 네트워크 타임아웃 | O | 동일 Idempotency-Key로 재시도 |
| 5xx 서버 에러 | O | exponential backoff + 동일 Idempotency-Key |
| 429 Rate Limited | O | Retry-After 헤더 값만큼 대기 후 재시도 |
| 4xx 클라이언트 에러 | X | 요청을 수정해야 함 |
| 201/200 성공 | X | 완료 |
