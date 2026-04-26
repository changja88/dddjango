# 주문 관리 REST API 설계

## 1. 리소스 식별

주문 관리 도메인에서 핵심 리소스를 식별한다.

| 리소스 | 설명 |
|--------|------|
| **Order** | 주문 자체 (상태, 총액, 고객 참조) |
| **Order Item** | 주문에 포함된 개별 상품 항목 |
| **Order Event** | 주문 상태 변경 이력 (배송, 취소 등) |

---

## 2. URL 구조

리소스는 명사, 복수형, kebab-case 소문자로 구성한다. URL에 동사를 넣지 않으며 최대 3단계 깊이를 유지한다.

```
/v1/orders                          # 주문 컬렉션
/v1/orders/{order_id}               # 주문 단건
/v1/orders/{order_id}/items         # 주문 항목 컬렉션
/v1/orders/{order_id}/items/{item_id}  # 주문 항목 단건
/v1/orders/{order_id}/events        # 주문 상태 변경 이력
```

URL path에 메이저 버전(`/v1/`)을 포함하여 버저닝한다. 후행 슬래시는 사용하지 않는다.

### 필터링, 정렬, 검색

필터링과 정렬은 쿼리 파라미터를 통해 처리한다.

```
GET /v1/orders?status=shipped&min_total=10000       # 필터링
GET /v1/orders?sort=-created_at,total               # 정렬 (- = DESC)
GET /v1/orders?fields=id,status,total,created_at    # 필드 선택
GET /v1/orders?q=ORDR-2026-0401                     # 검색
GET /v1/orders?created_after=2026-01-01&created_before=2026-03-31  # 날짜 범위
```

---

## 3. HTTP 메서드와 엔드포인트 매트릭스

| 엔드포인트 | POST | GET | PUT | PATCH | DELETE |
|------------|------|-----|-----|-------|--------|
| `/v1/orders` | 주문 생성 | 주문 목록 조회 | -- | -- | -- |
| `/v1/orders/{id}` | -- | 주문 단건 조회 | 주문 전체 교체 | 주문 부분 수정 | 주문 취소(삭제) |
| `/v1/orders/{id}/items` | 항목 추가 | 항목 목록 조회 | -- | -- | -- |
| `/v1/orders/{id}/items/{item_id}` | -- | 항목 단건 조회 | 항목 교체 | 항목 수량 수정 | 항목 제거 |
| `/v1/orders/{id}/events` | -- | 이력 조회 | -- | -- | -- |

### 각 엔드포인트 상세

#### 주문 생성

```
POST /v1/orders
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{
  "customer_id": "cust_abc123",
  "items": [
    {
      "product_id": "prod_xyz789",
      "quantity": 2
    }
  ],
  "shipping_address": {
    "street": "강남대로 123",
    "city": "서울",
    "postal_code": "06000"
  }
}
```

주문 생성은 중복이 치명적인 POST이므로 `Idempotency-Key` 헤더를 필수로 요구한다. 클라이언트가 V4 UUID를 생성하며, 서버는 24시간 동안 키를 보관하여 동일 키의 재요청에 저장된 응답을 반환한다.

#### 주문 조회

```
GET /v1/orders/{order_id}
```

#### 주문 부분 수정 (상태 변경 등)

```
PATCH /v1/orders/{order_id}
Content-Type: application/json

{
  "shipping_address": {
    "street": "테헤란로 456"
  }
}
```

PATCH는 전달된 필드만 수정한다. 주문 상태 변경(예: 확인, 배송)도 PATCH로 처리한다.

#### 주문 삭제(취소)

```
DELETE /v1/orders/{order_id}
```

---

## 4. 상태 코드

### 성공 응답

| 코드 | 의미 | 사용 시점 |
|------|------|-----------|
| `200 OK` | GET, PUT, PATCH 성공 | 주문 조회, 주문 수정 성공 |
| `201 Created` | POST로 자원 생성 성공 | 주문 생성 성공. `Location: /v1/orders/{id}` 헤더 포함 |
| `204 No Content` | DELETE 성공 | 주문 취소 성공. 응답 본문 없음 |

### 클라이언트 오류

| 코드 | 의미 | 사용 시점 |
|------|------|-----------|
| `400 Bad Request` | 잘못된 요청 형식 | JSON 파싱 실패, 필수 필드 누락 |
| `401 Unauthorized` | 인증 필요 | 토큰 없음 또는 만료 |
| `403 Forbidden` | 인가 부족 | 다른 고객의 주문에 접근 시도 |
| `404 Not Found` | 자원 없음 | 존재하지 않는 주문 ID |
| `409 Conflict` | 자원 충돌 | 이미 취소된 주문을 다시 취소, 동시 수정 충돌 |
| `422 Unprocessable Entity` | 의미적 오류 | 문법은 맞지만 재고 부족, 최소 주문 금액 미달 |
| `429 Too Many Requests` | Rate Limit 초과 | `Retry-After` 헤더와 함께 반환 |

### 서버 오류

| 코드 | 의미 | 사용 시점 |
|------|------|-----------|
| `500 Internal Server Error` | 서버 내부 오류 | 예기치 않은 서버 문제 |
| `503 Service Unavailable` | 일시적 과부하 | 정비 또는 과부하 시 `Retry-After` 헤더 포함 |

---

## 5. 에러 응답 형식 (RFC 9457 Problem Details)

모든 에러 응답은 `Content-Type: application/problem+json`으로 RFC 9457 형식을 일관되게 사용한다.

### 유효성 검증 실패 (400)

```json
HTTP/1.1 400 Bad Request
Content-Type: application/problem+json

{
  "type": "https://api.example.com/probs/validation-error",
  "title": "Validation failed.",
  "status": 400,
  "detail": "요청 본문에 필수 필드가 누락되었습니다.",
  "instance": "/v1/orders",
  "errors": [
    {
      "field": "customer_id",
      "message": "customer_id는 필수입니다."
    },
    {
      "field": "items",
      "message": "최소 1개의 항목이 필요합니다."
    }
  ]
}
```

`errors` 배열은 확장 필드로, 여러 유효성 검증 오류를 한 번에 전달한다.

### 자원 미발견 (404)

```json
HTTP/1.1 404 Not Found
Content-Type: application/problem+json

{
  "type": "https://api.example.com/probs/not-found",
  "title": "Resource not found.",
  "status": 404,
  "detail": "주문 ord_abc123을 찾을 수 없습니다.",
  "instance": "/v1/orders/ord_abc123"
}
```

### 비즈니스 규칙 위반 (422)

```json
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/problem+json

{
  "type": "https://api.example.com/probs/insufficient-stock",
  "title": "Insufficient stock.",
  "status": 422,
  "detail": "상품 prod_xyz789의 재고가 2개 부족합니다.",
  "instance": "/v1/orders",
  "product_id": "prod_xyz789",
  "requested": 5,
  "available": 3
}
```

### 충돌 (409)

```json
HTTP/1.1 409 Conflict
Content-Type: application/problem+json

{
  "type": "https://api.example.com/probs/order-already-cancelled",
  "title": "Order already cancelled.",
  "status": 409,
  "detail": "주문 ord_abc123은 이미 2026-04-05에 취소되었습니다.",
  "instance": "/v1/orders/ord_abc123"
}
```

### Rate Limit 초과 (429)

```json
HTTP/1.1 429 Too Many Requests
Content-Type: application/problem+json
Retry-After: 30
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1743955200

{
  "type": "https://api.example.com/probs/rate-limit-exceeded",
  "title": "Rate limit exceeded.",
  "status": 429,
  "detail": "요청 한도를 초과했습니다. 30초 후에 다시 시도하세요."
}
```

---

## 6. 페이지네이션

주문 목록 엔드포인트에는 Cursor 기반 페이지네이션을 적용한다. 대규모 데이터에서 Offset 방식보다 17배 빠르며, 삽입/삭제 시 누락이나 중복 없이 일관성을 유지한다.

### 요청

```
GET /v1/orders?limit=25&cursor=eyJjcmVhdGVkX2F0IjoiMjAyNi0wNC0wNVQxMDowMDowMFoiLCJpZCI6Im9yZF9hYmMxMjMifQ==
```

- `limit`: 페이지당 결과 수 (기본 25, 최대 100)
- `cursor`: 불투명한 base64 인코딩 토큰. 내부적으로 `created_at` + `id` 조합을 사용한다.

### 응답

```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "data": [
    {
      "id": "ord_def456",
      "customer_id": "cust_abc123",
      "status": "confirmed",
      "total": 35000,
      "created_at": "2026-04-05T11:30:00Z"
    },
    {
      "id": "ord_ghi789",
      "customer_id": "cust_abc123",
      "status": "shipped",
      "total": 52000,
      "created_at": "2026-04-05T10:15:00Z"
    }
  ],
  "pagination": {
    "has_more": true,
    "next_cursor": "eyJjcmVhdGVkX2F0IjoiMjAyNi0wNC0wNVQxMDoxNTowMFoiLCJpZCI6Im9yZF9naGk3ODkifQ=="
  }
}
```

- `has_more`: 다음 페이지 존재 여부
- `next_cursor`: 다음 페이지 조회에 사용할 커서 토큰. `has_more`가 `false`이면 생략한다.

클라이언트는 커서를 불투명 토큰으로 취급하며, 내부 구조에 의존하지 않는다.

---

## 7. 성공 응답 형식

### 단건 조회 (GET /v1/orders/{id})

```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "ord_abc123",
  "customer_id": "cust_abc123",
  "status": "confirmed",
  "total": 35000,
  "currency": "KRW",
  "items": [
    {
      "id": "item_001",
      "product_id": "prod_xyz789",
      "name": "무선 키보드",
      "quantity": 2,
      "unit_price": 15000,
      "subtotal": 30000
    },
    {
      "id": "item_002",
      "product_id": "prod_uvw456",
      "name": "마우스 패드",
      "quantity": 1,
      "unit_price": 5000,
      "subtotal": 5000
    }
  ],
  "shipping_address": {
    "street": "강남대로 123",
    "city": "서울",
    "postal_code": "06000"
  },
  "created_at": "2026-04-05T10:00:00Z",
  "updated_at": "2026-04-05T11:30:00Z"
}
```

### 생성 성공 (POST /v1/orders)

```json
HTTP/1.1 201 Created
Content-Type: application/json
Location: /v1/orders/ord_abc123

{
  "id": "ord_abc123",
  "customer_id": "cust_abc123",
  "status": "pending",
  "total": 35000,
  "currency": "KRW",
  "items": [...],
  "created_at": "2026-04-05T10:00:00Z",
  "updated_at": "2026-04-05T10:00:00Z"
}
```

`Location` 헤더에 새로 생성된 주문의 URI를 포함한다.

---

## 8. 전체 엔드포인트 요약

| 메서드 | 엔드포인트 | 설명 | 성공 코드 | Idempotency-Key |
|--------|-----------|------|-----------|:---:|
| `POST` | `/v1/orders` | 주문 생성 | `201` | 필수 |
| `GET` | `/v1/orders` | 주문 목록 (cursor 페이지네이션) | `200` | -- |
| `GET` | `/v1/orders/{id}` | 주문 단건 조회 | `200` | -- |
| `PUT` | `/v1/orders/{id}` | 주문 전체 교체 | `200` | -- |
| `PATCH` | `/v1/orders/{id}` | 주문 부분 수정 | `200` | -- |
| `DELETE` | `/v1/orders/{id}` | 주문 취소 | `204` | -- |
| `POST` | `/v1/orders/{id}/items` | 주문 항목 추가 | `201` | 권장 |
| `GET` | `/v1/orders/{id}/items` | 주문 항목 목록 | `200` | -- |
| `GET` | `/v1/orders/{id}/items/{item_id}` | 주문 항목 단건 조회 | `200` | -- |
| `PUT` | `/v1/orders/{id}/items/{item_id}` | 주문 항목 교체 | `200` | -- |
| `PATCH` | `/v1/orders/{id}/items/{item_id}` | 주문 항목 수량 수정 | `200` | -- |
| `DELETE` | `/v1/orders/{id}/items/{item_id}` | 주문 항목 제거 | `204` | -- |
| `GET` | `/v1/orders/{id}/events` | 주문 상태 변경 이력 | `200` | -- |

---

> **관련 스킬 참조:**
> - [Django Ninja로 이 API를 구현] --> **implementation-django-ninja** 스킬
> - [주문 테이블 스키마 설계 (정규화, 인덱스)] --> **architecture-db** 스킬
