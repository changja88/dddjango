# API 설계 리뷰

## 1. 주문 목록 조회 — 성능 문제

### 현재 설계

```
GET /api/v1/orders?page=1&per_page=50
```

```json
{
  "data": [...],
  "page": 1,
  "per_page": 50,
  "total": 1000000,
  "total_pages": 20000
}
```

### 문제점

**offset 기반 페이지네이션은 100만 건 규모 테이블에서 심각한 성능 저하를 유발한다.**

- `OFFSET 999950`처럼 뒤쪽 페이지를 요청하면 DB는 앞의 999,950건을 모두 스캔한 후 버린다. 페이지가 뒤로 갈수록 응답 시간이 선형으로 증가한다.
- `SELECT COUNT(*)`로 `total`을 매 요청마다 계산하는 것도 100만 건 테이블에서는 비용이 크다. InnoDB 기준 full table scan이 필요할 수 있다.
- `total_pages: 20000`은 실질적으로 사용자가 탐색할 수 없는 범위다. 이 정보를 매번 계산해서 내려줄 실익이 없다.

### 개선안: cursor 기반 페이지네이션

```
GET /api/v1/orders?cursor=eyJpZCI6NDU2fQ&limit=50
```

```json
{
  "data": [...],
  "next_cursor": "eyJpZCI6NTA2fQ",
  "has_more": true
}
```

- `WHERE id > :last_id ORDER BY id LIMIT 50` 형태로 동작하므로 인덱스를 타고 어떤 페이지든 일정한 성능을 보장한다.
- `total` 계산을 제거하여 불필요한 COUNT 쿼리를 없앤다.
- 만약 관리자 화면 등에서 전체 건수가 반드시 필요하다면, 별도 엔드포인트(`GET /api/v1/orders/count`)로 분리하거나 캐싱된 근사값을 제공한다.

---

## 2. 주문 생성 — 중복 주문 문제

### 현재 설계

```
POST /api/v1/orders
{"product_id": 123, "quantity": 2}
```

### 문제점

**멱등성 보장이 없어서 네트워크 재시도 시 중복 주문이 발생한다.**

- 클라이언트가 타임아웃 후 동일 요청을 재전송하면 서버는 이를 새로운 주문으로 처리한다.
- 모바일 환경이나 불안정한 네트워크에서 이 문제가 빈번하게 발생한다.
- 결제와 연동된 주문이라면 중복 과금으로 이어질 수 있어 비즈니스 리스크가 크다.

### 개선안: Idempotency Key 도입

```
POST /api/v1/orders
Headers:
  Idempotency-Key: "550e8400-e29b-41d4-a716-446655440000"

Body:
{"product_id": 123, "quantity": 2}
```

- 클라이언트가 UUID 기반의 `Idempotency-Key`를 헤더로 전송한다.
- 서버는 이 키를 일정 기간(예: 24시간) 저장하고, 동일 키로 재요청이 오면 기존 응답을 그대로 반환한다.
- 응답 코드도 구분한다: 최초 생성 시 `201 Created`, 중복 요청 시 `200 OK` (또는 `409 Conflict`로 알려주는 방식도 가능).
- Stripe, PayPal 등 결제 API에서 검증된 패턴이다.

서버 측 처리 흐름:

```
1. Idempotency-Key로 기존 처리 결과 조회
2. 존재하면 -> 저장된 응답 반환
3. 없으면 -> 주문 생성 처리 + 키와 응답을 저장
```

---

## 3. 주문 상태 변경 — 과도한 페이로드 문제

### 현재 설계

```
PUT /api/v1/orders/456
{"id": 456, "product_id": 123, "quantity": 2, "status": "confirmed", ...전체 필드}
```

### 문제점

**PUT은 리소스 전체 교체(full replacement) 시맨틱이므로, 상태 하나만 바꾸려 해도 전체 필드를 보내야 한다.**

- 클라이언트가 최신 상태를 모두 알아야 하므로, 먼저 GET으로 조회 후 수정하여 PUT하는 2단계 호출이 강제된다.
- 동시 수정 시 마지막 쓰기가 이기는(last-write-wins) 문제가 발생한다. A가 조회한 뒤 B가 수정하고, A가 이전 데이터 기반으로 PUT하면 B의 변경이 사라진다.
- URL path에 이미 `456`이 있는데 body에도 `id: 456`을 보내는 것은 불일치 가능성을 만든다.

### 개선안 A: PATCH로 부분 수정

```
PATCH /api/v1/orders/456
{"status": "confirmed"}
```

- 변경할 필드만 보내면 되므로 페이로드가 최소화된다.
- body에서 `id` 필드를 제거한다. 리소스 식별은 URL path가 담당한다.

### 개선안 B: 상태 전이를 별도 리소스로 모델링

주문 상태 변경이 단순 필드 업데이트가 아니라 비즈니스 로직(검증, 알림, 이력 기록)을 수반한다면, 이를 명시적인 액션으로 설계하는 것이 적합하다.

```
POST /api/v1/orders/456/confirm
POST /api/v1/orders/456/cancel
POST /api/v1/orders/456/ship
```

또는 상태 전이 이력을 리소스로 관리:

```
POST /api/v1/orders/456/transitions
{"action": "confirm", "reason": "Payment verified"}
```

- 허용되지 않는 상태 전이를 서버에서 명확히 거부할 수 있다 (예: "shipped" 상태에서 "confirmed"로 되돌리기 시도 시 `422 Unprocessable Entity`).
- 상태 변경 이력이 자동으로 남는다.

---

## 4. 추가 지적 사항

### 4.1 동시성 제어 부재

PUT/PATCH 어느 쪽이든 동시 수정 충돌을 감지할 방법이 없다. `ETag` 또는 `If-Match` 헤더를 활용한 낙관적 잠금(optimistic locking)을 도입해야 한다.

```
# 조회 시 ETag 반환
GET /api/v1/orders/456
ETag: "a1b2c3d4"

# 수정 시 If-Match로 검증
PATCH /api/v1/orders/456
If-Match: "a1b2c3d4"
{"status": "confirmed"}

# 충돌 시
412 Precondition Failed
```

### 4.2 에러 응답 형식 미정의

에러 시 어떤 형식으로 응답하는지 정의가 없다. RFC 7807(Problem Details) 형식을 권장한다.

```json
{
  "type": "https://api.example.com/errors/invalid-state-transition",
  "title": "Invalid State Transition",
  "status": 422,
  "detail": "Cannot transition from 'shipped' to 'confirmed'",
  "instance": "/api/v1/orders/456"
}
```

### 4.3 필터링/정렬 기준 부재

주문 목록 조회 시 필터링과 정렬 파라미터가 없다. 100만 건 테이블에서 전체를 순회하게 만드는 원인이 될 수 있다.

```
GET /api/v1/orders?status=pending&created_after=2026-04-01&sort=-created_at&limit=50
```

---

## 요약

| 문제 | 원인 | 개선 |
|---|---|---|
| 성능 저하 | offset 페이지네이션 + 매번 COUNT | cursor 기반 페이지네이션, total 제거 또는 캐싱 |
| 중복 주문 | 멱등성 미보장 | Idempotency-Key 헤더 도입 |
| 과도한 페이로드 | PUT 전체 교체 시맨틱 | PATCH 부분 수정 또는 상태 전이 전용 엔드포인트 |
| 동시 수정 충돌 | 낙관적 잠금 없음 | ETag / If-Match 도입 |
