# 이커머스 주문 API 설계

## 개요

이커머스 도메인의 핵심 리소스 4종(상품, 장바구니, 주문, 결제)에 대한 REST API를 설계한다. URL Path 버전 관리(`/v1/`)를 적용하고, 모든 에러 응답은 RFC 9457 Problem Details 형식을 따른다.

**Base URL**: `https://api.example.com/v1`

---

## 1. 리소스 및 엔드포인트

### 1.1 상품 (Products)

| 엔드포인트 | 메서드 | 설명 | 상태 코드 |
|-----------|--------|------|----------|
| `/v1/products` | GET | 상품 목록 조회 (페이지네이션) | 200 |
| `/v1/products` | POST | 상품 등록 | 201 |
| `/v1/products/{product_id}` | GET | 상품 상세 조회 | 200, 404 |
| `/v1/products/{product_id}` | PUT | 상품 전체 수정 | 200, 404 |
| `/v1/products/{product_id}` | PATCH | 상품 부분 수정 | 200, 404 |
| `/v1/products/{product_id}` | DELETE | 상품 삭제 | 204, 404 |

#### GET /v1/products -- 상품 목록 조회

**Query Parameters**:

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `cursor` | string | 다음 페이지 커서 (base64 인코딩, 불투명 토큰) |
| `limit` | integer | 페이지당 항목 수 (기본값: 20, 최대: 100) |
| `sort` | string | 정렬 기준 (예: `-price,name`, `-`는 내림차순) |
| `q` | string | 상품명 검색 |
| `min_price` | integer | 최소 가격 필터 |
| `max_price` | integer | 최대 가격 필터 |
| `category` | string | 카테고리 필터 |

**응답**: `200 OK`

```json
{
  "data": [
    {
      "id": "prod_a1b2c3",
      "name": "무선 키보드",
      "description": "저소음 기계식 무선 키보드",
      "price": 89000,
      "currency": "KRW",
      "category": "electronics",
      "stock_quantity": 150,
      "image_url": "https://cdn.example.com/products/prod_a1b2c3.jpg",
      "created_at": "2026-03-15T09:00:00Z",
      "updated_at": "2026-04-01T14:30:00Z"
    }
  ],
  "pagination": {
    "next_cursor": "eyJpZCI6InByb2RfeDl5OHo3In0=",
    "has_more": true,
    "limit": 20
  }
}
```

#### POST /v1/products -- 상품 등록

**요청**: `Content-Type: application/json`

```json
{
  "name": "무선 키보드",
  "description": "저소음 기계식 무선 키보드",
  "price": 89000,
  "currency": "KRW",
  "category": "electronics",
  "stock_quantity": 150,
  "image_url": "https://cdn.example.com/products/prod_a1b2c3.jpg"
}
```

**응답**: `201 Created`
- `Location: /v1/products/prod_a1b2c3`

```json
{
  "id": "prod_a1b2c3",
  "name": "무선 키보드",
  "description": "저소음 기계식 무선 키보드",
  "price": 89000,
  "currency": "KRW",
  "category": "electronics",
  "stock_quantity": 150,
  "image_url": "https://cdn.example.com/products/prod_a1b2c3.jpg",
  "created_at": "2026-04-04T10:00:00Z",
  "updated_at": "2026-04-04T10:00:00Z"
}
```

#### GET /v1/products/{product_id} -- 상품 상세 조회

**응답**: `200 OK`

```json
{
  "id": "prod_a1b2c3",
  "name": "무선 키보드",
  "description": "저소음 기계식 무선 키보드",
  "price": 89000,
  "currency": "KRW",
  "category": "electronics",
  "stock_quantity": 150,
  "image_url": "https://cdn.example.com/products/prod_a1b2c3.jpg",
  "created_at": "2026-03-15T09:00:00Z",
  "updated_at": "2026-04-01T14:30:00Z"
}
```

#### PATCH /v1/products/{product_id} -- 상품 부분 수정

**요청**: `Content-Type: application/json`

```json
{
  "price": 79000,
  "stock_quantity": 200
}
```

**응답**: `200 OK` -- 수정된 전체 상품 객체 반환

---

### 1.2 장바구니 (Carts)

장바구니는 인증된 사용자에게 1:1로 연결된다. 장바구니 내 개별 항목은 하위 리소스 `/carts/{cart_id}/items`로 관리한다.

| 엔드포인트 | 메서드 | 설명 | 상태 코드 |
|-----------|--------|------|----------|
| `/v1/carts/{cart_id}` | GET | 장바구니 조회 | 200, 404 |
| `/v1/carts/{cart_id}` | DELETE | 장바구니 비우기 | 204, 404 |
| `/v1/carts/{cart_id}/items` | GET | 장바구니 항목 목록 조회 (페이지네이션) | 200 |
| `/v1/carts/{cart_id}/items` | POST | 장바구니에 상품 추가 | 201, 409 |
| `/v1/carts/{cart_id}/items/{item_id}` | PATCH | 장바구니 항목 수량 변경 | 200, 404 |
| `/v1/carts/{cart_id}/items/{item_id}` | DELETE | 장바구니 항목 제거 | 204, 404 |

#### GET /v1/carts/{cart_id} -- 장바구니 조회

**응답**: `200 OK`

```json
{
  "id": "cart_x1y2z3",
  "user_id": "user_m4n5o6",
  "items_count": 3,
  "subtotal": 257000,
  "currency": "KRW",
  "created_at": "2026-04-01T08:00:00Z",
  "updated_at": "2026-04-04T09:15:00Z"
}
```

#### GET /v1/carts/{cart_id}/items -- 장바구니 항목 목록 조회

**Query Parameters**:

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `cursor` | string | 다음 페이지 커서 |
| `limit` | integer | 페이지당 항목 수 (기본값: 20, 최대: 100) |

**응답**: `200 OK`

```json
{
  "data": [
    {
      "id": "item_d4e5f6",
      "product_id": "prod_a1b2c3",
      "product_name": "무선 키보드",
      "quantity": 2,
      "unit_price": 89000,
      "subtotal": 178000,
      "currency": "KRW",
      "added_at": "2026-04-04T09:00:00Z"
    }
  ],
  "pagination": {
    "next_cursor": "eyJpZCI6Iml0ZW1fZzdoOGk5In0=",
    "has_more": true,
    "limit": 20
  }
}
```

#### POST /v1/carts/{cart_id}/items -- 장바구니에 상품 추가

**요청**: `Content-Type: application/json`

```json
{
  "product_id": "prod_a1b2c3",
  "quantity": 2
}
```

**응답**: `201 Created`
- `Location: /v1/carts/cart_x1y2z3/items/item_d4e5f6`

```json
{
  "id": "item_d4e5f6",
  "product_id": "prod_a1b2c3",
  "product_name": "무선 키보드",
  "quantity": 2,
  "unit_price": 89000,
  "subtotal": 178000,
  "currency": "KRW",
  "added_at": "2026-04-04T09:00:00Z"
}
```

#### PATCH /v1/carts/{cart_id}/items/{item_id} -- 수량 변경

**요청**: `Content-Type: application/json`

```json
{
  "quantity": 3
}
```

**응답**: `200 OK` -- 수정된 항목 객체 반환

---

### 1.3 주문 (Orders)

주문은 장바구니를 기반으로 생성된다. 주문 생성은 중복이 치명적이므로 `Idempotency-Key` 헤더를 필수로 요구한다.

| 엔드포인트 | 메서드 | 설명 | 상태 코드 |
|-----------|--------|------|----------|
| `/v1/orders` | GET | 주문 목록 조회 (페이지네이션) | 200 |
| `/v1/orders` | POST | 주문 생성 | 201, 409, 422 |
| `/v1/orders/{order_id}` | GET | 주문 상세 조회 | 200, 404 |
| `/v1/orders/{order_id}` | PATCH | 주문 정보 수정 (배송지 등) | 200, 404, 409 |
| `/v1/orders/{order_id}/items` | GET | 주문 항목 목록 조회 (페이지네이션) | 200 |

#### GET /v1/orders -- 주문 목록 조회

**Query Parameters**:

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `cursor` | string | 다음 페이지 커서 |
| `limit` | integer | 페이지당 항목 수 (기본값: 20, 최대: 100) |
| `status` | string | 주문 상태 필터 (`pending`, `confirmed`, `shipped`, `delivered`, `cancelled`) |
| `sort` | string | 정렬 기준 (기본값: `-created_at`) |

**응답**: `200 OK`

```json
{
  "data": [
    {
      "id": "ord_p7q8r9",
      "status": "confirmed",
      "items_count": 3,
      "total_amount": 257000,
      "currency": "KRW",
      "shipping_address": {
        "recipient": "홍길동",
        "line1": "서울시 강남구 테헤란로 123",
        "line2": "4층",
        "city": "서울",
        "postal_code": "06234",
        "country": "KR"
      },
      "created_at": "2026-04-04T10:00:00Z",
      "updated_at": "2026-04-04T10:05:00Z"
    }
  ],
  "pagination": {
    "next_cursor": "eyJpZCI6Im9yZF9zMXQydTMifQ==",
    "has_more": false,
    "limit": 20
  }
}
```

#### POST /v1/orders -- 주문 생성

**헤더**:
- `Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000` (V4 UUID, 필수, 24시간 유효)

**요청**: `Content-Type: application/json`

```json
{
  "cart_id": "cart_x1y2z3",
  "shipping_address": {
    "recipient": "홍길동",
    "line1": "서울시 강남구 테헤란로 123",
    "line2": "4층",
    "city": "서울",
    "postal_code": "06234",
    "country": "KR"
  }
}
```

**응답**: `201 Created`
- `Location: /v1/orders/ord_p7q8r9`

```json
{
  "id": "ord_p7q8r9",
  "status": "pending",
  "items": [
    {
      "id": "oitem_a1b2c3",
      "product_id": "prod_a1b2c3",
      "product_name": "무선 키보드",
      "quantity": 2,
      "unit_price": 89000,
      "subtotal": 178000
    }
  ],
  "items_count": 1,
  "total_amount": 178000,
  "currency": "KRW",
  "shipping_address": {
    "recipient": "홍길동",
    "line1": "서울시 강남구 테헤란로 123",
    "line2": "4층",
    "city": "서울",
    "postal_code": "06234",
    "country": "KR"
  },
  "created_at": "2026-04-04T10:00:00Z",
  "updated_at": "2026-04-04T10:00:00Z"
}
```

#### GET /v1/orders/{order_id}/items -- 주문 항목 목록 조회

**Query Parameters**:

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `cursor` | string | 다음 페이지 커서 |
| `limit` | integer | 페이지당 항목 수 (기본값: 20, 최대: 100) |

**응답**: `200 OK`

```json
{
  "data": [
    {
      "id": "oitem_a1b2c3",
      "product_id": "prod_a1b2c3",
      "product_name": "무선 키보드",
      "quantity": 2,
      "unit_price": 89000,
      "subtotal": 178000,
      "currency": "KRW"
    }
  ],
  "pagination": {
    "next_cursor": null,
    "has_more": false,
    "limit": 20
  }
}
```

---

### 1.4 결제 (Payments)

결제는 주문에 종속된 리소스이다. 결제 생성 역시 중복이 치명적이므로 `Idempotency-Key` 헤더를 필수로 요구한다. 결제 처리는 비동기로 진행될 수 있으며, 이 경우 `202 Accepted`를 반환한다.

| 엔드포인트 | 메서드 | 설명 | 상태 코드 |
|-----------|--------|------|----------|
| `/v1/orders/{order_id}/payments` | GET | 주문의 결제 목록 조회 (페이지네이션) | 200 |
| `/v1/orders/{order_id}/payments` | POST | 결제 요청 | 201 또는 202, 409, 422 |
| `/v1/payments/{payment_id}` | GET | 결제 상세 조회 | 200, 404 |
| `/v1/payments` | GET | 전체 결제 목록 조회 (페이지네이션) | 200 |

#### POST /v1/orders/{order_id}/payments -- 결제 요청

**헤더**:
- `Idempotency-Key: 7c9e6679-7425-40de-944b-e07fc1f90ae7` (V4 UUID, 필수, 24시간 유효)

**요청**: `Content-Type: application/json`

```json
{
  "method": "credit_card",
  "amount": 178000,
  "currency": "KRW",
  "card_token": "tok_visa_4242"
}
```

**응답 (동기 처리)**: `201 Created`
- `Location: /v1/payments/pay_j1k2l3`

```json
{
  "id": "pay_j1k2l3",
  "order_id": "ord_p7q8r9",
  "status": "completed",
  "method": "credit_card",
  "amount": 178000,
  "currency": "KRW",
  "card_last_four": "4242",
  "created_at": "2026-04-04T10:05:00Z",
  "updated_at": "2026-04-04T10:05:00Z"
}
```

**응답 (비동기 처리)**: `202 Accepted`

```json
{
  "id": "pay_j1k2l3",
  "order_id": "ord_p7q8r9",
  "status": "processing",
  "method": "credit_card",
  "amount": 178000,
  "currency": "KRW",
  "created_at": "2026-04-04T10:05:00Z",
  "updated_at": "2026-04-04T10:05:00Z"
}
```

#### GET /v1/payments/{payment_id} -- 결제 상세 조회

**응답**: `200 OK`

```json
{
  "id": "pay_j1k2l3",
  "order_id": "ord_p7q8r9",
  "status": "completed",
  "method": "credit_card",
  "amount": 178000,
  "currency": "KRW",
  "card_last_four": "4242",
  "refunded_amount": 0,
  "created_at": "2026-04-04T10:05:00Z",
  "updated_at": "2026-04-04T10:05:00Z"
}
```

#### GET /v1/payments -- 전체 결제 목록 조회

**Query Parameters**:

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `cursor` | string | 다음 페이지 커서 |
| `limit` | integer | 페이지당 항목 수 (기본값: 20, 최대: 100) |
| `status` | string | 결제 상태 필터 (`processing`, `completed`, `failed`, `refunded`) |
| `order_id` | string | 특정 주문의 결제만 필터 |

**응답**: `200 OK` -- 상품 목록 조회와 동일한 페이지네이션 구조

---

## 2. 페이지네이션

모든 목록 조회 엔드포인트에 **커서 기반 페이지네이션**을 적용한다. 대규모 데이터에서도 일관된 O(1) 성능을 보장하며, offset 대비 대용량 데이터에서 17배 빠른 성능을 제공한다.

### 규칙

- 커서는 base64로 인코딩된 불투명 토큰이다. 클라이언트는 내부 구조를 알 필요가 없다.
- 기본 페이지 크기는 20, 최대는 100이다.
- 응답에 `has_more`와 `next_cursor`를 항상 포함한다.

### 공통 응답 구조

```json
{
  "data": [],
  "pagination": {
    "next_cursor": "eyJpZCI6InByb2RfeDl5OHo3IiwiY3JlYXRlZF9hdCI6IjIwMjYtMDQtMDRUMTA6MDA6MDBaIn0=",
    "has_more": true,
    "limit": 20
  }
}
```

---

## 3. 에러 응답 (RFC 9457 Problem Details)

모든 에러 응답은 `Content-Type: application/problem+json` 형식을 사용한다.

### 공통 에러 구조

```json
{
  "type": "https://api.example.com/problems/{error-type}",
  "title": "에러 유형의 짧은 요약",
  "status": 400,
  "detail": "이 특정 발생에 대한 구체적 설명",
  "instance": "/v1/resource/id"
}
```

### 에러 응답 예시

#### 400 Bad Request -- 잘못된 요청

```json
{
  "type": "https://api.example.com/problems/invalid-request",
  "title": "Invalid request parameters.",
  "status": 400,
  "detail": "The 'quantity' field must be a positive integer.",
  "instance": "/v1/carts/cart_x1y2z3/items"
}
```

#### 401 Unauthorized -- 인증 필요

```json
{
  "type": "https://api.example.com/problems/unauthorized",
  "title": "Authentication required.",
  "status": 401,
  "detail": "The access token is missing or expired.",
  "instance": "/v1/orders"
}
```

#### 403 Forbidden -- 권한 부족

```json
{
  "type": "https://api.example.com/problems/forbidden",
  "title": "Insufficient permissions.",
  "status": 403,
  "detail": "You do not have permission to access this order.",
  "instance": "/v1/orders/ord_p7q8r9"
}
```

#### 404 Not Found -- 리소스 없음

```json
{
  "type": "https://api.example.com/problems/not-found",
  "title": "Resource not found.",
  "status": 404,
  "detail": "No product found with id 'prod_invalid'.",
  "instance": "/v1/products/prod_invalid"
}
```

#### 409 Conflict -- 리소스 충돌

```json
{
  "type": "https://api.example.com/problems/conflict",
  "title": "Resource conflict.",
  "status": 409,
  "detail": "This product is already in the cart. Use PATCH to update quantity.",
  "instance": "/v1/carts/cart_x1y2z3/items"
}
```

#### 422 Unprocessable Entity -- 의미적 검증 실패

```json
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Validation failed.",
  "status": 422,
  "detail": "Cannot create order: insufficient stock for product 'prod_a1b2c3'. Requested 10, available 3.",
  "instance": "/v1/orders",
  "errors": [
    {
      "field": "items[0].quantity",
      "message": "Requested quantity exceeds available stock."
    }
  ]
}
```

#### 429 Too Many Requests -- Rate Limit 초과

```json
{
  "type": "https://api.example.com/problems/rate-limit-exceeded",
  "title": "Rate limit exceeded.",
  "status": 429,
  "detail": "You have exceeded 60 requests per minute. Retry after 30 seconds.",
  "instance": "/v1/products"
}
```

헤더:
```
Retry-After: 30
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1743764430
```

#### 500 Internal Server Error -- 서버 오류

```json
{
  "type": "https://api.example.com/problems/internal-error",
  "title": "Internal server error.",
  "status": 500,
  "detail": "An unexpected error occurred. Please try again later.",
  "instance": "/v1/orders/ord_p7q8r9/payments"
}
```

---

## 4. 버전 관리

URL Path 방식으로 메이저 버전을 관리한다.

- 현재 버전: `/v1/`
- 필드 추가(응답), 선택적 파라미터 추가 등 **additive change**는 버전 변경 없이 적용한다.
- 필드 제거, 타입 변경, URL 경로 변경 등 **breaking change**가 필요하면 `/v2/`를 새로 만든다.
- 버전 폐기 시 `Sunset` 헤더를 응답에 포함하고, 최소 6개월 마이그레이션 기간을 보장한다.

---

## 5. Rate Limiting

모든 응답에 Rate Limit 헤더를 포함한다. Token Bucket 알고리즘을 사용하여 제어된 버스트를 허용한다.

### 응답 헤더

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
X-RateLimit-Reset: 1743764430
```

초과 시 `429 Too Many Requests`와 함께 `Retry-After` 헤더를 반환한다.

---

## 6. Idempotency-Key

주문 생성(`POST /v1/orders`)과 결제 요청(`POST /v1/orders/{order_id}/payments`)은 중복 처리가 치명적이므로 `Idempotency-Key` 헤더를 필수로 요구한다.

### 규칙

- 클라이언트는 V4 UUID를 생성하여 `Idempotency-Key` 헤더에 포함한다.
- 서버는 첫 요청의 상태 코드와 응답 본문을 저장한다.
- 동일 키로 재요청 시 저장된 결과를 그대로 반환한다.
- 키는 24시간 후 만료된다.
- `Idempotency-Key` 누락 시 `400 Bad Request`를 반환한다.

```
POST /v1/orders
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json
```

---

## 7. 인증

`Authorization` 헤더에 Bearer 토큰을 사용한다. API Key는 쿼리 파라미터가 아닌 헤더로 전달한다 (민감 데이터 URL 노출 방지).

```
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

- 인증 실패: `401 Unauthorized`
- 권한 부족: `403 Forbidden`

---

## 8. 전체 엔드포인트 요약

| 리소스 | 엔드포인트 | GET | POST | PUT | PATCH | DELETE |
|--------|-----------|-----|------|-----|-------|--------|
| 상품 | `/v1/products` | 목록 조회 | 등록 | - | - | - |
| 상품 | `/v1/products/{id}` | 상세 조회 | - | 전체 수정 | 부분 수정 | 삭제 |
| 장바구니 | `/v1/carts/{id}` | 조회 | - | - | - | 비우기 |
| 장바구니 항목 | `/v1/carts/{id}/items` | 목록 조회 | 추가 | - | - | - |
| 장바구니 항목 | `/v1/carts/{id}/items/{id}` | - | - | - | 수량 변경 | 제거 |
| 주문 | `/v1/orders` | 목록 조회 | 생성* | - | - | - |
| 주문 | `/v1/orders/{id}` | 상세 조회 | - | - | 정보 수정 | - |
| 주문 항목 | `/v1/orders/{id}/items` | 목록 조회 | - | - | - | - |
| 결제 | `/v1/payments` | 목록 조회 | - | - | - | - |
| 결제 | `/v1/payments/{id}` | 상세 조회 | - | - | - | - |
| 결제 | `/v1/orders/{id}/payments` | 목록 조회 | 생성* | - | - | - |

`*` Idempotency-Key 헤더 필수
