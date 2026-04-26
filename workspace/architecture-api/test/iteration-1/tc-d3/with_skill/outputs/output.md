# API 리뷰: 주문(Order) API

## 리뷰 요약

현재 API는 URL 구조와 버전 관리(v1) 측면에서 기본적인 REST 규약을 따르고 있다. 리소스명이 복수 명사(`/orders`)이고, HTTP 메서드도 올바른 목적에 사용되고 있다. 그러나 성능, 안정성, 사용성에 직접적으로 영향을 미치는 세 가지 핵심 문제가 있으며, 이것들이 피드백에서 언급된 증상의 정확한 원인이다.

---

## 리뷰 체크리스트

- [x] URL 경로의 동사 사용 -- 해당 없음. `/orders`는 명사 기반으로 올바르다.
- [x] 잘못된 HTTP 메서드 -- **문제 발견.** 상태만 변경하는 데 PUT(전체 교체)을 사용하고 있다.
- [x] 일관되지 않거나 잘못된 상태 코드 -- 응답 명세가 없어 확인 불가. 에러 응답 형식과 함께 검토 필요.
- [x] 누락되거나 비표준인 에러 응답 형식 -- 에러 응답 명세가 제시되지 않았다. RFC 9457 적용 여부 확인 필요.
- [x] 컬렉션 리소스의 단수 명사 사용 -- 해당 없음. `orders`는 복수형으로 올바르다.
- [x] 목록 엔드포인트의 페이지네이션 누락 -- 페이지네이션이 존재하지만, **방식에 심각한 성능 문제가 있다.**
- [x] 버전 관리 전략 없음 -- URL path 기반 `/v1/`이 적용되어 있어 올바르다.
- [x] 버전 변경 없는 breaking change -- 현재 시점에서는 해당 없음.
- [x] 쿼리 파라미터의 민감한 데이터 -- 해당 없음.
- [x] 중요한 POST 엔드포인트의 멱등성 처리 누락 -- **문제 발견.** 주문 생성에 멱등성 키가 없다.

---

## 발견 사항

### 1. [Pagination] -- 100만 건 테이블에서 offset 기반 페이지네이션으로 인한 성능 저하

```
GET /api/v1/orders?page=1&per_page=50
```

이것이 "성능이 느리다"는 피드백의 직접적인 원인이다.

Offset 기반 페이지네이션은 `OFFSET N` 만큼의 행을 읽고 버리는 방식이므로, 페이지 번호가 커질수록 DB가 스캔해야 하는 행 수가 선형적으로 증가한다. 100만 건 테이블에서 `page=19000`을 요청하면 DB는 95만 행을 읽고 버린 후 50행만 반환한다. PostgreSQL 기준 100만 건에서 cursor 기반 페이지네이션이 offset 기반보다 **17배 빠르다.**

또한 응답에 `total: 1000000`을 매번 반환하는 것은 매 요청마다 `SELECT COUNT(*)` 쿼리를 실행하게 되어 추가적인 성능 비용을 발생시킨다.

**권장 변경:**

```
# Cursor 기반 페이지네이션으로 전환
GET /api/v1/orders?limit=50&starting_after=order_abc123

# 응답
{
  "data": [...],
  "has_more": true,
  "next_cursor": "eyJpZCI6MTIzNH0="   # base64 인코딩된 불투명 커서
}
```

- 인덱싱된 불변 유니크 필드(타임스탬프 + ID 조합)를 커서로 사용한다.
- 커서를 base64로 인코딩하여 클라이언트가 내부 구조를 모르도록 한다.
- `total`과 `total_pages`를 제거하고 `has_more`로 대체하여 COUNT 쿼리를 없앤다.
- 페이지 번호 기반 랜덤 접근이 반드시 필요한 관리자 화면이라면 offset을 유지하되, 공개 API나 일반 사용자 목록은 cursor 방식으로 전환한다.

---

### 2. [Idempotency] -- 주문 생성 POST에 멱등성 키가 없어 중복 주문 발생

```
POST /api/v1/orders
{"product_id": 123, "quantity": 2}
```

이것이 "가끔 중복 주문이 발생한다"는 피드백의 직접적인 원인이다.

POST는 본질적으로 멱등하지 않다. 네트워크 타임아웃이나 클라이언트 재시도 시 서버가 이미 주문을 생성했지만 응답이 유실된 경우, 동일 요청이 두 번 처리되어 중복 주문이 만들어진다. 주문은 중복이 치명적인 리소스(결제 발생)이므로 Idempotency-Key 패턴이 필수적이다.

**권장 변경:**

```
POST /api/v1/orders
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{"product_id": 123, "quantity": 2}
```

동작 방식:
1. 클라이언트가 V4 UUID로 고유 키를 생성하여 `Idempotency-Key` 헤더에 포함한다.
2. 서버가 첫 요청 처리 후 상태 코드 + 응답 본문을 키와 함께 저장한다 (DB 또는 Redis).
3. 동일 키의 후속 요청에는 저장된 결과를 그대로 반환한다.
4. 키는 24시간 후 만료한다.
5. 동일 키의 동시 요청(race condition)은 하나만 처리하고 나머지는 `409 Conflict`를 반환한다.

---

### 3. [HTTP Methods] -- 상태만 변경하는데 PUT(전체 교체)을 사용

```
PUT /api/v1/orders/456
{"id": 456, "product_id": 123, "quantity": 2, "status": "confirmed", ...전체 필드}
```

이것이 "상태만 바꾸려는데 전체 필드를 보내야 해서 불편하다"는 피드백의 직접적인 원인이다.

PUT은 리소스의 **전체 교체**를 의미하므로 모든 필드를 포함해야 한다. 누락된 필드는 기본값 또는 NULL로 초기화될 수 있다. 반면 PATCH는 **부분 수정**으로, 변경할 필드만 전송하면 된다. 상태 필드 하나만 바꾸는 시나리오에서는 PATCH가 올바른 메서드다.

**권장 변경:**

```
PATCH /api/v1/orders/456
Content-Type: application/json

{"status": "confirmed"}
```

- PATCH는 변경하려는 필드만 전송하면 된다.
- 클라이언트가 현재 리소스 상태를 먼저 GET으로 조회한 후 전체를 보낼 필요가 없다.
- PUT은 클라이언트가 리소스 전체 상태를 알고 있고 이를 완전히 교체하려는 경우에만 사용한다.
- 필요하다면 PUT과 PATCH를 모두 지원할 수 있다. PUT은 전체 교체, PATCH는 부분 수정으로 역할을 명확히 구분한다.

---

## 에러 응답 형식 (추가 권장)

제시된 API에 에러 응답 형식이 명시되어 있지 않다. 모든 에러 응답에 RFC 9457 Problem Details 형식을 일관되게 적용할 것을 권장한다.

```json
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/invalid-quantity",
  "title": "Invalid order quantity.",
  "status": 422,
  "detail": "Quantity must be at least 1. Received: 0.",
  "instance": "/api/v1/orders"
}
```

---

## 개선 후 전체 API 설계

```
# 주문 목록 (cursor 기반)
GET /api/v1/orders?limit=50&starting_after=order_abc123

응답:
{
  "data": [...],
  "has_more": true,
  "next_cursor": "eyJpZCI6MTIzNH0="
}

# 주문 생성 (멱등성 키 포함)
POST /api/v1/orders
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{"product_id": 123, "quantity": 2}

응답: 201 Created
Location: /api/v1/orders/789

# 주문 상태 변경 (부분 수정)
PATCH /api/v1/orders/456
Content-Type: application/json

{"status": "confirmed"}

응답: 200 OK
```

각 변경이 피드백의 어떤 증상을 해결하는지 정리하면:

| 피드백 | 원인 | 해결 |
|--------|------|------|
| 성능이 느리다 | Offset 기반 페이지네이션 + COUNT 쿼리 | Cursor 기반 전환, `has_more` 사용 |
| 중복 주문이 발생한다 | POST 멱등성 미처리 | `Idempotency-Key` 헤더 도입 |
| 전체 필드를 보내야 한다 | PUT(전체 교체) 사용 | PATCH(부분 수정)로 전환 |
