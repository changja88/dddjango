# 이커머스 주문 API 설계

## 공통 사항

### Base URL

```
https://api.example.com/v1
```

### 인증

모든 요청에 `Authorization: Bearer <token>` 헤더를 포함한다.

### 공통 페이지네이션 형식

목록 조회 API는 쿼리 파라미터로 페이지네이션을 지원한다.

**요청 파라미터:**

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `page` | integer | 1 | 페이지 번호 (1부터 시작) |
| `size` | integer | 20 | 페이지당 항목 수 (최대 100) |
| `sort` | string | - | 정렬 기준 (예: `created_at:desc`) |

**응답 형식:**

```json
{
  "data": [],
  "pagination": {
    "page": 1,
    "size": 20,
    "total_items": 150,
    "total_pages": 8
  }
}
```

### 공통 에러 응답 형식

모든 에러 응답은 다음 표준 형식을 따른다.

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "요청한 리소스를 찾을 수 없습니다.",
    "details": [
      {
        "field": "product_id",
        "reason": "존재하지 않는 상품 ID입니다."
      }
    ]
  }
}
```

**공통 에러 코드:**

| HTTP 상태 코드 | 에러 코드 | 설명 |
|----------------|-----------|------|
| 400 | `INVALID_REQUEST` | 요청 형식이 올바르지 않음 |
| 400 | `VALIDATION_FAILED` | 입력 값 검증 실패 |
| 401 | `UNAUTHORIZED` | 인증 토큰이 없거나 유효하지 않음 |
| 403 | `FORBIDDEN` | 해당 리소스에 대한 접근 권한 없음 |
| 404 | `RESOURCE_NOT_FOUND` | 요청한 리소스를 찾을 수 없음 |
| 409 | `CONFLICT` | 리소스 상태 충돌 |
| 422 | `UNPROCESSABLE_ENTITY` | 요청은 유효하지만 처리할 수 없음 |
| 429 | `RATE_LIMIT_EXCEEDED` | 요청 횟수 초과 |
| 500 | `INTERNAL_ERROR` | 서버 내부 오류 |

---

## 1. 상품 (Products)

### 1.1 상품 목록 조회

```
GET /products
```

**쿼리 파라미터:**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `page` | integer | N | 페이지 번호 |
| `size` | integer | N | 페이지당 항목 수 |
| `category` | string | N | 카테고리 필터 |
| `min_price` | integer | N | 최소 가격 필터 |
| `max_price` | integer | N | 최대 가격 필터 |
| `sort` | string | N | 정렬 (`price:asc`, `created_at:desc`) |
| `q` | string | N | 상품명 검색 키워드 |

**응답: `200 OK`**

```json
{
  "data": [
    {
      "id": "prod_abc123",
      "name": "무선 블루투스 이어폰",
      "description": "고음질 무선 이어폰",
      "price": 59000,
      "currency": "KRW",
      "category": "electronics",
      "stock": 150,
      "images": [
        "https://cdn.example.com/products/prod_abc123/1.jpg"
      ],
      "status": "active",
      "created_at": "2026-03-01T09:00:00Z",
      "updated_at": "2026-03-15T14:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total_items": 85,
    "total_pages": 5
  }
}
```

### 1.2 상품 상세 조회

```
GET /products/{product_id}
```

**응답: `200 OK`**

```json
{
  "data": {
    "id": "prod_abc123",
    "name": "무선 블루투스 이어폰",
    "description": "고음질 무선 이어폰",
    "price": 59000,
    "currency": "KRW",
    "category": "electronics",
    "stock": 150,
    "images": [
      "https://cdn.example.com/products/prod_abc123/1.jpg",
      "https://cdn.example.com/products/prod_abc123/2.jpg"
    ],
    "options": [
      {
        "name": "color",
        "values": ["black", "white"]
      }
    ],
    "status": "active",
    "created_at": "2026-03-01T09:00:00Z",
    "updated_at": "2026-03-15T14:30:00Z"
  }
}
```

**에러 응답:**

| 상태 코드 | 에러 코드 | 조건 |
|-----------|-----------|------|
| 404 | `RESOURCE_NOT_FOUND` | 상품 ID가 존재하지 않음 |

### 1.3 상품 등록 (관리자)

```
POST /products
```

**요청 본문:**

```json
{
  "name": "무선 블루투스 이어폰",
  "description": "고음질 무선 이어폰",
  "price": 59000,
  "currency": "KRW",
  "category": "electronics",
  "stock": 150,
  "images": ["https://cdn.example.com/products/new/1.jpg"],
  "options": [
    {
      "name": "color",
      "values": ["black", "white"]
    }
  ]
}
```

**응답: `201 Created`**

```json
{
  "data": {
    "id": "prod_abc123",
    "name": "무선 블루투스 이어폰",
    "description": "고음질 무선 이어폰",
    "price": 59000,
    "currency": "KRW",
    "category": "electronics",
    "stock": 150,
    "images": ["https://cdn.example.com/products/new/1.jpg"],
    "options": [
      {
        "name": "color",
        "values": ["black", "white"]
      }
    ],
    "status": "active",
    "created_at": "2026-04-04T09:00:00Z",
    "updated_at": "2026-04-04T09:00:00Z"
  }
}
```

**에러 응답:**

| 상태 코드 | 에러 코드 | 조건 |
|-----------|-----------|------|
| 400 | `VALIDATION_FAILED` | 필수 필드 누락 또는 유효하지 않은 값 |
| 403 | `FORBIDDEN` | 관리자 권한 없음 |

### 1.4 상품 수정 (관리자)

```
PATCH /products/{product_id}
```

**요청 본문 (변경할 필드만 포함):**

```json
{
  "price": 49000,
  "stock": 200
}
```

**응답: `200 OK`** -- 수정된 상품 전체 객체 반환

**에러 응답:**

| 상태 코드 | 에러 코드 | 조건 |
|-----------|-----------|------|
| 400 | `VALIDATION_FAILED` | 유효하지 않은 값 |
| 404 | `RESOURCE_NOT_FOUND` | 상품 ID가 존재하지 않음 |

### 1.5 상품 삭제 (관리자)

```
DELETE /products/{product_id}
```

**응답: `204 No Content`** -- 응답 본문 없음

**에러 응답:**

| 상태 코드 | 에러 코드 | 조건 |
|-----------|-----------|------|
| 404 | `RESOURCE_NOT_FOUND` | 상품 ID가 존재하지 않음 |
| 409 | `CONFLICT` | 진행 중인 주문에 포함된 상품 |

---

## 2. 장바구니 (Cart)

장바구니는 인증된 사용자별로 하나씩 존재한다.

### 2.1 장바구니 조회

```
GET /cart
```

**응답: `200 OK`**

```json
{
  "data": {
    "id": "cart_xyz789",
    "items": [
      {
        "id": "ci_001",
        "product_id": "prod_abc123",
        "product_name": "무선 블루투스 이어폰",
        "option": { "color": "black" },
        "quantity": 2,
        "unit_price": 59000,
        "subtotal": 118000
      }
    ],
    "total_items": 2,
    "total_price": 118000,
    "currency": "KRW",
    "updated_at": "2026-04-04T10:00:00Z"
  }
}
```

### 2.2 장바구니에 상품 추가

```
POST /cart/items
```

**요청 본문:**

```json
{
  "product_id": "prod_abc123",
  "quantity": 2,
  "option": { "color": "black" }
}
```

**응답: `201 Created`** -- 업데이트된 장바구니 전체 객체 반환

**에러 응답:**

| 상태 코드 | 에러 코드 | 조건 |
|-----------|-----------|------|
| 400 | `VALIDATION_FAILED` | 수량이 0 이하 |
| 404 | `RESOURCE_NOT_FOUND` | 상품 ID가 존재하지 않음 |
| 422 | `UNPROCESSABLE_ENTITY` | 재고 부족 |

### 2.3 장바구니 항목 수량 변경

```
PATCH /cart/items/{item_id}
```

**요청 본문:**

```json
{
  "quantity": 3
}
```

**응답: `200 OK`** -- 업데이트된 장바구니 전체 객체 반환

**에러 응답:**

| 상태 코드 | 에러 코드 | 조건 |
|-----------|-----------|------|
| 400 | `VALIDATION_FAILED` | 수량이 0 이하 |
| 404 | `RESOURCE_NOT_FOUND` | 장바구니 항목 ID가 존재하지 않음 |
| 422 | `UNPROCESSABLE_ENTITY` | 재고 부족 |

### 2.4 장바구니 항목 삭제

```
DELETE /cart/items/{item_id}
```

**응답: `204 No Content`**

**에러 응답:**

| 상태 코드 | 에러 코드 | 조건 |
|-----------|-----------|------|
| 404 | `RESOURCE_NOT_FOUND` | 장바구니 항목 ID가 존재하지 않음 |

### 2.5 장바구니 비우기

```
DELETE /cart
```

**응답: `204 No Content`**

---

## 3. 주문 (Orders)

### 3.1 주문 목록 조회

```
GET /orders
```

**쿼리 파라미터:**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `page` | integer | N | 페이지 번호 |
| `size` | integer | N | 페이지당 항목 수 |
| `status` | string | N | 주문 상태 필터 |
| `from_date` | string (ISO 8601) | N | 시작 날짜 |
| `to_date` | string (ISO 8601) | N | 종료 날짜 |
| `sort` | string | N | 정렬 (`created_at:desc`) |

**응답: `200 OK`**

```json
{
  "data": [
    {
      "id": "ord_def456",
      "status": "confirmed",
      "items": [
        {
          "product_id": "prod_abc123",
          "product_name": "무선 블루투스 이어폰",
          "option": { "color": "black" },
          "quantity": 2,
          "unit_price": 59000,
          "subtotal": 118000
        }
      ],
      "shipping_address": {
        "recipient": "홍길동",
        "phone": "010-1234-5678",
        "address_line1": "서울시 강남구 테헤란로 123",
        "address_line2": "4층",
        "postal_code": "06234"
      },
      "total_price": 118000,
      "shipping_fee": 3000,
      "grand_total": 121000,
      "currency": "KRW",
      "created_at": "2026-04-04T11:00:00Z",
      "updated_at": "2026-04-04T11:05:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total_items": 12,
    "total_pages": 1
  }
}
```

### 3.2 주문 상세 조회

```
GET /orders/{order_id}
```

**응답: `200 OK`**

```json
{
  "data": {
    "id": "ord_def456",
    "status": "confirmed",
    "items": [
      {
        "product_id": "prod_abc123",
        "product_name": "무선 블루투스 이어폰",
        "option": { "color": "black" },
        "quantity": 2,
        "unit_price": 59000,
        "subtotal": 118000
      }
    ],
    "shipping_address": {
      "recipient": "홍길동",
      "phone": "010-1234-5678",
      "address_line1": "서울시 강남구 테헤란로 123",
      "address_line2": "4층",
      "postal_code": "06234"
    },
    "total_price": 118000,
    "shipping_fee": 3000,
    "discount": 0,
    "grand_total": 121000,
    "currency": "KRW",
    "payment": {
      "id": "pay_ghi789",
      "method": "card",
      "status": "completed"
    },
    "tracking": {
      "carrier": "CJ대한통운",
      "tracking_number": "1234567890",
      "status": "in_transit"
    },
    "created_at": "2026-04-04T11:00:00Z",
    "updated_at": "2026-04-04T11:05:00Z"
  }
}
```

**에러 응답:**

| 상태 코드 | 에러 코드 | 조건 |
|-----------|-----------|------|
| 404 | `RESOURCE_NOT_FOUND` | 주문 ID가 존재하지 않음 |
| 403 | `FORBIDDEN` | 다른 사용자의 주문 조회 시도 |

### 3.3 주문 생성

```
POST /orders
```

**요청 본문:**

```json
{
  "items": [
    {
      "product_id": "prod_abc123",
      "quantity": 2,
      "option": { "color": "black" }
    }
  ],
  "shipping_address": {
    "recipient": "홍길동",
    "phone": "010-1234-5678",
    "address_line1": "서울시 강남구 테헤란로 123",
    "address_line2": "4층",
    "postal_code": "06234"
  },
  "payment_method": "card",
  "coupon_code": "SPRING2026"
}
```

**응답: `201 Created`**

```json
{
  "data": {
    "id": "ord_def456",
    "status": "pending_payment",
    "items": [
      {
        "product_id": "prod_abc123",
        "product_name": "무선 블루투스 이어폰",
        "option": { "color": "black" },
        "quantity": 2,
        "unit_price": 59000,
        "subtotal": 118000
      }
    ],
    "shipping_address": {
      "recipient": "홍길동",
      "phone": "010-1234-5678",
      "address_line1": "서울시 강남구 테헤란로 123",
      "address_line2": "4층",
      "postal_code": "06234"
    },
    "total_price": 118000,
    "shipping_fee": 3000,
    "discount": 5000,
    "grand_total": 116000,
    "currency": "KRW",
    "payment": {
      "id": "pay_ghi789",
      "method": "card",
      "status": "pending",
      "checkout_url": "https://pay.example.com/checkout/pay_ghi789"
    },
    "created_at": "2026-04-04T11:00:00Z",
    "updated_at": "2026-04-04T11:00:00Z"
  }
}
```

**에러 응답:**

| 상태 코드 | 에러 코드 | 조건 |
|-----------|-----------|------|
| 400 | `VALIDATION_FAILED` | 필수 필드 누락 또는 유효하지 않은 값 |
| 422 | `UNPROCESSABLE_ENTITY` | 재고 부족 또는 유효하지 않은 쿠폰 |

### 3.4 주문 취소

```
POST /orders/{order_id}/cancel
```

**요청 본문:**

```json
{
  "reason": "단순 변심"
}
```

**응답: `200 OK`**

```json
{
  "data": {
    "id": "ord_def456",
    "status": "cancelled",
    "cancel_reason": "단순 변심",
    "refund": {
      "amount": 116000,
      "status": "processing"
    },
    "updated_at": "2026-04-04T12:00:00Z"
  }
}
```

**에러 응답:**

| 상태 코드 | 에러 코드 | 조건 |
|-----------|-----------|------|
| 404 | `RESOURCE_NOT_FOUND` | 주문 ID가 존재하지 않음 |
| 409 | `CONFLICT` | 이미 배송 중이거나 취소할 수 없는 상태 |

**주문 상태 전이:**

```
pending_payment -> confirmed -> processing -> shipped -> delivered
      |                |
      v                v
  cancelled        cancelled
```

| 상태 | 설명 |
|------|------|
| `pending_payment` | 결제 대기 중 |
| `confirmed` | 결제 완료, 주문 확인 |
| `processing` | 상품 준비 중 |
| `shipped` | 배송 중 |
| `delivered` | 배송 완료 |
| `cancelled` | 주문 취소 |

---

## 4. 결제 (Payments)

### 4.1 결제 목록 조회

```
GET /payments
```

**쿼리 파라미터:**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `page` | integer | N | 페이지 번호 |
| `size` | integer | N | 페이지당 항목 수 |
| `status` | string | N | 결제 상태 필터 |
| `method` | string | N | 결제 수단 필터 |
| `from_date` | string (ISO 8601) | N | 시작 날짜 |
| `to_date` | string (ISO 8601) | N | 종료 날짜 |

**응답: `200 OK`**

```json
{
  "data": [
    {
      "id": "pay_ghi789",
      "order_id": "ord_def456",
      "method": "card",
      "amount": 116000,
      "currency": "KRW",
      "status": "completed",
      "paid_at": "2026-04-04T11:02:00Z",
      "created_at": "2026-04-04T11:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total_items": 5,
    "total_pages": 1
  }
}
```

### 4.2 결제 상세 조회

```
GET /payments/{payment_id}
```

**응답: `200 OK`**

```json
{
  "data": {
    "id": "pay_ghi789",
    "order_id": "ord_def456",
    "method": "card",
    "card_info": {
      "issuer": "삼성카드",
      "last_four": "1234",
      "installment_months": 0
    },
    "amount": 116000,
    "currency": "KRW",
    "status": "completed",
    "receipt_url": "https://pay.example.com/receipt/pay_ghi789",
    "paid_at": "2026-04-04T11:02:00Z",
    "created_at": "2026-04-04T11:00:00Z"
  }
}
```

**에러 응답:**

| 상태 코드 | 에러 코드 | 조건 |
|-----------|-----------|------|
| 404 | `RESOURCE_NOT_FOUND` | 결제 ID가 존재하지 않음 |

### 4.3 결제 승인 확인

주문 생성 후 PG사 결제 완료 콜백을 처리한다.

```
POST /payments/{payment_id}/confirm
```

**요청 본문:**

```json
{
  "pg_token": "pgtoken_abc123",
  "pg_transaction_id": "txn_9876543210"
}
```

**응답: `200 OK`**

```json
{
  "data": {
    "id": "pay_ghi789",
    "order_id": "ord_def456",
    "amount": 116000,
    "currency": "KRW",
    "status": "completed",
    "pg_transaction_id": "txn_9876543210",
    "paid_at": "2026-04-04T11:02:00Z"
  }
}
```

**에러 응답:**

| 상태 코드 | 에러 코드 | 조건 |
|-----------|-----------|------|
| 400 | `INVALID_REQUEST` | PG 토큰이 유효하지 않음 |
| 404 | `RESOURCE_NOT_FOUND` | 결제 ID가 존재하지 않음 |
| 409 | `CONFLICT` | 이미 완료된 결제 |

### 4.4 환불 요청

```
POST /payments/{payment_id}/refund
```

**요청 본문:**

```json
{
  "amount": 116000,
  "reason": "주문 취소에 따른 환불"
}
```

**응답: `201 Created`**

```json
{
  "data": {
    "id": "ref_jkl012",
    "payment_id": "pay_ghi789",
    "amount": 116000,
    "currency": "KRW",
    "reason": "주문 취소에 따른 환불",
    "status": "processing",
    "created_at": "2026-04-04T12:00:00Z"
  }
}
```

**에러 응답:**

| 상태 코드 | 에러 코드 | 조건 |
|-----------|-----------|------|
| 400 | `VALIDATION_FAILED` | 환불 금액이 결제 금액 초과 |
| 404 | `RESOURCE_NOT_FOUND` | 결제 ID가 존재하지 않음 |
| 409 | `CONFLICT` | 이미 환불 완료된 결제 |
| 422 | `UNPROCESSABLE_ENTITY` | 환불 불가능한 결제 상태 |

**결제 상태:**

| 상태 | 설명 |
|------|------|
| `pending` | 결제 대기 |
| `completed` | 결제 완료 |
| `failed` | 결제 실패 |
| `refunded` | 전액 환불 |
| `partially_refunded` | 부분 환불 |

---

## 엔드포인트 요약

| 리소스 | 메서드 | 엔드포인트 | 설명 | 성공 코드 |
|--------|--------|------------|------|-----------|
| 상품 | GET | `/products` | 상품 목록 조회 | 200 |
| 상품 | GET | `/products/{id}` | 상품 상세 조회 | 200 |
| 상품 | POST | `/products` | 상품 등록 | 201 |
| 상품 | PATCH | `/products/{id}` | 상품 수정 | 200 |
| 상품 | DELETE | `/products/{id}` | 상품 삭제 | 204 |
| 장바구니 | GET | `/cart` | 장바구니 조회 | 200 |
| 장바구니 | POST | `/cart/items` | 장바구니 상품 추가 | 201 |
| 장바구니 | PATCH | `/cart/items/{id}` | 장바구니 수량 변경 | 200 |
| 장바구니 | DELETE | `/cart/items/{id}` | 장바구니 항목 삭제 | 204 |
| 장바구니 | DELETE | `/cart` | 장바구니 비우기 | 204 |
| 주문 | GET | `/orders` | 주문 목록 조회 | 200 |
| 주문 | GET | `/orders/{id}` | 주문 상세 조회 | 200 |
| 주문 | POST | `/orders` | 주문 생성 | 201 |
| 주문 | POST | `/orders/{id}/cancel` | 주문 취소 | 200 |
| 결제 | GET | `/payments` | 결제 목록 조회 | 200 |
| 결제 | GET | `/payments/{id}` | 결제 상세 조회 | 200 |
| 결제 | POST | `/payments/{id}/confirm` | 결제 승인 확인 | 200 |
| 결제 | POST | `/payments/{id}/refund` | 환불 요청 | 201 |
