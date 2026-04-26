# Payment API Design

## 1. API Overview

결제 생성, 결제 확인, 환불 세 가지 핵심 기능을 제공하는 RESTful API다. 모든 결제 변경 요청은 멱등성 키를 통해 중복 처리를 방지하며, Rate Limiting으로 과도한 요청을 차단한다.

---

## 2. Base URL & Common Headers

```
Base URL: https://api.example.com/v1
```

| Header | Required | Description |
|---|---|---|
| `Authorization` | Yes | `Bearer {api_key}` |
| `Idempotency-Key` | Yes (POST/PUT) | UUID v4. 동일 키로 재요청 시 동일 결과 반환 |
| `Content-Type` | Yes | `application/json` |

---

## 3. Endpoints

### 3.1 결제 생성 (Create Payment)

```
POST /v1/payments
```

**Request**

```json
{
  "amount": 50000,
  "currency": "KRW",
  "method": "card",
  "card": {
    "number_token": "tok_abc123",
    "installment_months": 0
  },
  "order_id": "order-20260404-001",
  "description": "Premium Plan 구독",
  "metadata": {
    "user_id": "user-789",
    "plan": "premium"
  }
}
```

**Response: 201 Created**

```json
{
  "id": "pay_1a2b3c4d5e",
  "status": "pending",
  "amount": 50000,
  "currency": "KRW",
  "method": "card",
  "order_id": "order-20260404-001",
  "description": "Premium Plan 구독",
  "idempotency_key": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-04-04T10:00:00Z",
  "metadata": {
    "user_id": "user-789",
    "plan": "premium"
  }
}
```

### 3.2 결제 확인 (Confirm Payment)

```
POST /v1/payments/{payment_id}/confirm
```

**Request**

```json
{
  "payment_id": "pay_1a2b3c4d5e",
  "amount": 50000
}
```

`amount` 필드는 결제 생성 시 금액과 일치해야 한다. 불일치 시 결제를 거부하여 금액 변조를 방지한다.

**Response: 200 OK**

```json
{
  "id": "pay_1a2b3c4d5e",
  "status": "confirmed",
  "amount": 50000,
  "currency": "KRW",
  "method": "card",
  "paid_at": "2026-04-04T10:00:05Z",
  "receipt_url": "https://api.example.com/receipts/pay_1a2b3c4d5e"
}
```

### 3.3 환불 (Refund)

```
POST /v1/payments/{payment_id}/refunds
```

**Request**

```json
{
  "amount": 50000,
  "reason": "customer_request"
}
```

`amount`를 생략하면 전액 환불, 지정하면 부분 환불이다.

**Response: 201 Created**

```json
{
  "id": "ref_9z8y7x6w",
  "payment_id": "pay_1a2b3c4d5e",
  "status": "processing",
  "amount": 50000,
  "reason": "customer_request",
  "created_at": "2026-04-04T12:00:00Z"
}
```

---

## 4. Payment Status Lifecycle

```
  [pending] ---confirm---> [confirmed] ---refund---> [refunded]
      |                        |
      |---cancel/expire--->  [cancelled]
      |                        |
      |---fail----------->  [failed]       [partially_refunded]
```

| Status | Description |
|---|---|
| `pending` | 결제 생성됨. 아직 확인 전 |
| `confirmed` | 결제 승인 완료 |
| `failed` | 결제 실패 |
| `cancelled` | 결제 취소됨 |
| `refunded` | 전액 환불 완료 |
| `partially_refunded` | 부분 환불 완료 |

---

## 5. Idempotency (멱등성 처리)

### 5.1 동작 원리

멱등성은 동일한 요청을 여러 번 보내도 결과가 한 번만 적용되는 것을 보장한다. 네트워크 오류로 응답을 받지 못한 클라이언트가 안전하게 재시도할 수 있다.

```
Client                          Server
  |                               |
  |-- POST /payments ------------>|
  |   Idempotency-Key: abc-123    |  1. Key "abc-123" 저장, 결제 처리
  |                               |
  |<-- 201 Created (pay_xxx) -----|
  |                               |
  |   (네트워크 오류로 응답 유실)    |
  |                               |
  |-- POST /payments ------------>|
  |   Idempotency-Key: abc-123    |  2. Key "abc-123" 이미 존재 -> 저장된 응답 반환
  |                               |
  |<-- 201 Created (pay_xxx) -----|  동일한 payment_id, 중복 결제 없음
```

### 5.2 구현 규칙

| Rule | Detail |
|---|---|
| Key 형식 | UUID v4 (`550e8400-e29b-41d4-a716-446655440000`) |
| 유효 기간 | 24시간. 이후 동일 키로 새 요청 가능 |
| 저장 내용 | 요청 해시, 응답 상태 코드, 응답 본문 |
| 충돌 감지 | 동일 키로 다른 요청 본문이 오면 `409 Conflict` 반환 |
| 적용 대상 | `POST`, `PUT` 요청. `GET`, `DELETE`는 본질적으로 멱등 |

### 5.3 서버 측 처리 흐름

```
요청 수신
  |
  v
Idempotency-Key 존재?
  |
  +-- No --> 요청 본문 해시 + Key 저장 --> 결제 처리 --> 응답 저장 후 반환
  |
  +-- Yes --> 저장된 요청 해시와 현재 요청 해시 비교
                |
                +-- 일치 --> 저장된 응답 그대로 반환 (재처리 없음)
                |
                +-- 불일치 --> 409 Conflict 반환
```

### 5.4 멱등성 키 저장소

```
Table: idempotency_keys
+------------------+-------------+--------------------------------------+
| Column           | Type        | Description                          |
+------------------+-------------+--------------------------------------+
| idempotency_key  | VARCHAR(64) | PK. 클라이언트가 전송한 UUID         |
| request_hash     | VARCHAR(64) | 요청 본문의 SHA-256 해시             |
| response_code    | INTEGER     | 저장된 HTTP 응답 코드                |
| response_body    | JSONB       | 저장된 응답 본문                     |
| created_at       | TIMESTAMP   | 생성 시각                            |
| expires_at       | TIMESTAMP   | 만료 시각 (created_at + 24h)         |
+------------------+-------------+--------------------------------------+
```

### 5.5 처리 중 요청에 대한 동시성 제어

결제 처리가 진행 중인 상태에서 동일 멱등성 키로 재요청이 들어올 수 있다. 이 경우 이중 결제를 방지해야 한다.

```
요청 수신
  |
  v
DB에서 idempotency_key로 SELECT FOR UPDATE (행 잠금)
  |
  +-- 행 없음 --> INSERT (status='processing') --> 결제 처리 --> UPDATE (status='done', 응답 저장)
  |
  +-- 행 있음, status='done' --> 저장된 응답 반환
  |
  +-- 행 있음, status='processing' --> 423 Locked 반환 (클라이언트에 재시도 요청)
```

---

## 6. Rate Limiting

### 6.1 정책

| Tier | Limit | Window | 대상 |
|---|---|---|---|
| Standard | 100 req | 1분 | API 키 기준 |
| Payment Create | 20 req | 1분 | API 키 기준, 결제 생성만 |
| Per-IP | 30 req | 1분 | IP 기준 (인증 없는 요청) |

### 6.2 응답 헤더

모든 응답에 Rate Limit 상태를 포함한다.

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1743760860
```

### 6.3 초과 시 응답

```
HTTP/1.1 429 Too Many Requests
Retry-After: 32
```

```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Retry after 32 seconds.",
    "retry_after": 32
  }
}
```

### 6.4 구현: Sliding Window Counter

Token Bucket이나 Fixed Window 대신 Sliding Window Counter를 사용한다. Fixed Window의 경계 시점 폭주 문제를 방지하면서 메모리 효율이 좋다.

```
현재 시각: 12:01:20 (윈도우: 1분)
이전 윈도우 (12:00:00~12:00:59): 요청 60건
현재 윈도우 (12:01:00~12:01:59): 요청 15건 (경과 비율 20/60 = 33%)

가중 합산 = 60 * (1 - 0.33) + 15 = 40.2 + 15 = 55.2건
Limit 100 기준 -> 허용
```

---

## 7. Error Responses

모든 에러는 동일한 구조를 따른다.

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

| HTTP Status | Error Code | Description |
|---|---|---|
| 400 | `invalid_request` | 필수 필드 누락, 유효하지 않은 값 |
| 401 | `unauthorized` | API 키 누락 또는 만료 |
| 404 | `payment_not_found` | 존재하지 않는 결제 ID |
| 409 | `idempotency_conflict` | 동일 멱등성 키에 다른 요청 본문 |
| 409 | `invalid_state_transition` | 현재 상태에서 불가능한 전환 (예: failed -> confirmed) |
| 422 | `amount_mismatch` | 확인 금액과 생성 금액 불일치 |
| 422 | `refund_exceeds_amount` | 환불 금액이 결제 금액 초과 |
| 423 | `payment_processing` | 동일 결제가 처리 중. 잠시 후 재시도 |
| 429 | `rate_limit_exceeded` | 요청 한도 초과 |
| 500 | `internal_error` | 서버 내부 오류 |

---

## 8. Retry Strategy (클라이언트 가이드)

네트워크 오류나 5xx 응답 시 클라이언트는 다음 전략으로 재시도한다.

| Attempt | Delay | Description |
|---|---|---|
| 1 | 즉시 | 첫 요청 |
| 2 | 1초 | 첫 번째 재시도 |
| 3 | 2초 | 두 번째 재시도 |
| 4 | 4초 | 세 번째 재시도 |
| 5 | 8초 | 네 번째 재시도 (최종) |

- Exponential backoff + jitter 적용 (실제 대기 = delay * (0.5 + random(0, 0.5)))
- `Idempotency-Key`를 동일하게 유지하여 중복 결제 방지
- `429` 응답 시 `Retry-After` 헤더 값만큼 대기
- `4xx` 응답(429 제외)은 재시도하지 않음 (요청 자체가 잘못됨)

---

## 9. Database Schema

```sql
CREATE TABLE payments (
    id              VARCHAR(20)  PRIMARY KEY,  -- "pay_" prefix + random
    order_id        VARCHAR(64)  NOT NULL,
    amount          BIGINT       NOT NULL,      -- 최소 단위 (원)
    currency        VARCHAR(3)   NOT NULL DEFAULT 'KRW',
    status          VARCHAR(24)  NOT NULL DEFAULT 'pending',
    method          VARCHAR(16)  NOT NULL,
    description     TEXT,
    metadata        JSONB,
    idempotency_key VARCHAR(64)  UNIQUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    confirmed_at    TIMESTAMPTZ,
    failed_at       TIMESTAMPTZ,
    CONSTRAINT chk_amount CHECK (amount > 0),
    CONSTRAINT chk_status CHECK (status IN (
        'pending', 'confirmed', 'failed', 'cancelled',
        'refunded', 'partially_refunded'
    ))
);

CREATE TABLE refunds (
    id              VARCHAR(20)  PRIMARY KEY,  -- "ref_" prefix + random
    payment_id      VARCHAR(20)  NOT NULL REFERENCES payments(id),
    amount          BIGINT       NOT NULL,
    reason          VARCHAR(32),
    status          VARCHAR(16)  NOT NULL DEFAULT 'processing',
    idempotency_key VARCHAR(64)  UNIQUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    CONSTRAINT chk_refund_amount CHECK (amount > 0),
    CONSTRAINT chk_refund_status CHECK (status IN (
        'processing', 'completed', 'failed'
    ))
);

CREATE TABLE idempotency_keys (
    idempotency_key VARCHAR(64)  PRIMARY KEY,
    request_hash    VARCHAR(64)  NOT NULL,
    status          VARCHAR(16)  NOT NULL DEFAULT 'processing',
    response_code   INTEGER,
    response_body   JSONB,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ  NOT NULL,
    CONSTRAINT chk_idem_status CHECK (status IN ('processing', 'done'))
);

CREATE INDEX idx_payments_order_id ON payments(order_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_refunds_payment_id ON refunds(payment_id);
CREATE INDEX idx_idempotency_expires ON idempotency_keys(expires_at);
```

---

## 10. Confirm Payment - 서버 처리 흐름

결제 확인은 결제가 정확히 한 번만 처리되도록 보장하는 핵심 단계다.

```
POST /v1/payments/{id}/confirm 수신
  |
  v
1. 멱등성 키 확인 (Section 5.3 흐름)
  |
  v
2. payments 테이블에서 SELECT FOR UPDATE (행 잠금)
  |
  +-- 존재하지 않음 --> 404 반환
  |
  +-- status != 'pending' --> 409 invalid_state_transition 반환
  |
  v
3. 요청 amount와 DB amount 비교
  |
  +-- 불일치 --> 422 amount_mismatch 반환
  |
  v
4. 외부 PG사 결제 승인 API 호출
  |
  +-- 실패 --> status='failed' 업데이트, 에러 반환
  |
  +-- 성공 --> status='confirmed', confirmed_at=NOW() 업데이트
  |
  v
5. 멱등성 키에 응답 저장 (status='done')
  |
  v
6. 201 응답 반환
```

---

## 11. Refund - 서버 처리 흐름

```
POST /v1/payments/{id}/refunds 수신
  |
  v
1. 멱등성 키 확인
  |
  v
2. payments 테이블에서 SELECT FOR UPDATE
  |
  +-- status NOT IN ('confirmed', 'partially_refunded') --> 409 반환
  |
  v
3. 기존 환불 합산 + 요청 금액 <= 결제 금액 검증
  |
  +-- 초과 --> 422 refund_exceeds_amount 반환
  |
  v
4. refunds 테이블에 INSERT (status='processing')
  |
  v
5. 외부 PG사 환불 API 호출
  |
  +-- 실패 --> refund status='failed', 에러 반환
  |
  +-- 성공 --> refund status='completed'
  |
  v
6. 환불 합산 == 결제 금액?
  |
  +-- Yes --> payment status='refunded'
  +-- No  --> payment status='partially_refunded'
  |
  v
7. 응답 반환
```

---

## 12. Summary

| Concern | Solution |
|---|---|
| 중복 결제 방지 | `Idempotency-Key` 헤더 + 요청 해시 비교 + DB 행 잠금 |
| 한 번만 처리 | `SELECT FOR UPDATE`로 상태 전이 원자성 보장 |
| 네트워크 오류 재시도 | 동일 멱등성 키로 재요청 시 저장된 응답 반환 |
| 동시 요청 보호 | 처리 중 상태 관리 + `423 Locked` 응답 |
| 과도한 요청 차단 | Sliding Window Counter 기반 Rate Limiting |
| 금액 변조 방지 | Confirm 시 amount 검증 |
| 안전한 재시도 | Exponential backoff + jitter 가이드 |
