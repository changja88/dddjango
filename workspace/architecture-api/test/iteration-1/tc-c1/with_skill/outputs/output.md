# API 엔드포인트 RESTful 리팩토링

## 리팩토링 체크리스트

- [x] Verbs in URLs → RENAME to noun-based resources
- [x] Wrong method → CHANGE to correct HTTP method
- [x] Wrong status codes → FIX to semantic codes
- [x] Custom error format → CONVERT to RFC 9457
- [x] Singular collection names → PLURALIZE
- [x] Unbounded list endpoints → ADD pagination
- [x] No versioning → ADD version strategy
- [ ] Breaking changes → MOVE to new version (해당 없음 -- 신규 리팩토링)
- [ ] Sensitive data in URL → MOVE to header or body (해당 없음)
- [x] Non-idempotent critical POST → ADD Idempotency-Key

---

## 전체 비교 요약

| Before | After | Method |
|--------|-------|--------|
| `POST /api/createProduct` | `POST /api/v1/products` | POST |
| `GET /api/getProductById/123` | `GET /api/v1/products/123` | GET |
| `POST /api/updateProduct/123` | `PATCH /api/v1/products/123` | PATCH |
| `POST /api/removeProduct/123` | `DELETE /api/v1/products/123` | DELETE |
| `GET /api/searchProducts?q=...` | `GET /api/v1/products?q=...` | GET |
| `POST /api/addToCart/123` | `POST /api/v1/cart/items` | POST |
| `GET /api/getCartItems` | `GET /api/v1/cart/items` | GET |
| `POST /api/checkout` | `POST /api/v1/orders` | POST |

---

## 개별 변경 사항

### 1. 상품 등록

```
[Before]
POST /api/createProduct

[After]
POST /api/v1/products
→ 201 Created
→ Location: /api/v1/products/{id}

[Reason] URL/리소스 설계 + HTTP 메서드 — URL에 동사(create)를 넣지 않는다.
리소스는 명사(products)로 표현하고, 생성 행위는 POST 메서드가 담당한다.
성공 시 201 Created와 함께 Location 헤더로 새 리소스 URI를 반환한다.
```

**요청/응답 예시:**

```http
POST /api/v1/products HTTP/1.1
Content-Type: application/json

{
  "name": "무선 키보드",
  "price": 45000,
  "category": "electronics"
}
```

```http
HTTP/1.1 201 Created
Location: /api/v1/products/456
Content-Type: application/json

{
  "id": 456,
  "name": "무선 키보드",
  "price": 45000,
  "category": "electronics",
  "created_at": "2026-04-04T10:00:00Z"
}
```

---

### 2. 상품 조회

```
[Before]
GET /api/getProductById/123

[After]
GET /api/v1/products/123
→ 200 OK

[Reason] URL/리소스 설계 — URL에 동사(get)와 구현 세부사항(ById)을 넣지 않는다.
리소스 식별자(/products/123)만으로 단건 조회가 명확히 표현된다.
GET 메서드가 조회 행위를 담당하므로 URL에 행위를 중복 기술할 필요가 없다.
```

**요청/응답 예시:**

```http
GET /api/v1/products/123 HTTP/1.1
Accept: application/json
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 123,
  "name": "무선 키보드",
  "price": 45000,
  "category": "electronics",
  "created_at": "2026-04-04T10:00:00Z"
}
```

---

### 3. 상품 수정

```
[Before]
POST /api/updateProduct/123

[After]
PATCH /api/v1/products/123
→ 200 OK

[Reason] HTTP 메서드 + URL/리소스 설계 — 부분 수정은 PATCH, 전체 교체는 PUT이다.
POST는 자원 생성에 사용하며, 수정 행위에 POST를 쓰면 멱등성 의미가 왜곡된다.
URL의 동사(update)도 제거하고, PATCH 메서드가 수정 행위를 담당하도록 한다.
```

**요청/응답 예시:**

```http
PATCH /api/v1/products/123 HTTP/1.1
Content-Type: application/json

{
  "price": 39000
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 123,
  "name": "무선 키보드",
  "price": 39000,
  "category": "electronics",
  "created_at": "2026-04-04T10:00:00Z"
}
```

---

### 4. 상품 삭제

```
[Before]
POST /api/removeProduct/123

[After]
DELETE /api/v1/products/123
→ 204 No Content

[Reason] HTTP 메서드 + URL/리소스 설계 — 삭제는 DELETE 메서드를 사용한다.
DELETE는 멱등하므로 반복 요청에도 동일한 효과를 보장한다.
POST를 삭제에 사용하면 의미가 불명확하고 멱등성도 보장되지 않는다.
성공 시 204 No Content로 응답 본문 없이 반환한다.
```

**요청/응답 예시:**

```http
DELETE /api/v1/products/123 HTTP/1.1
```

```http
HTTP/1.1 204 No Content
```

---

### 5. 상품 검색

```
[Before]
GET /api/searchProducts?q=...

[After]
GET /api/v1/products?q=...
→ 200 OK (페이지네이션 포함)

[Reason] URL/리소스 설계 + 페이지네이션 — 검색은 컬렉션 리소스에 대한
쿼리 파라미터 필터링으로 표현한다. URL에 동사(search)를 넣지 않는다.
목록 조회이므로 커서 기반 페이지네이션을 추가하여 무한 결과 방지한다.
```

**요청/응답 예시:**

```http
GET /api/v1/products?q=keyboard&limit=25 HTTP/1.1
Accept: application/json
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "data": [
    {
      "id": 123,
      "name": "무선 키보드",
      "price": 45000,
      "category": "electronics"
    }
  ],
  "pagination": {
    "next_cursor": "eyJpZCI6IDEyM30=",
    "has_more": true,
    "limit": 25
  }
}
```

---

### 6. 장바구니 추가

```
[Before]
POST /api/addToCart/123

[After]
POST /api/v1/cart/items
→ 201 Created

[Reason] URL/리소스 설계 — 장바구니(cart)의 하위 리소스인 아이템(items)에
상품을 추가하는 것이므로 계층적 리소스 구조로 표현한다.
URL에 동사(add)를 넣지 않고, 상품 ID는 요청 본문에 포함한다.
상품 ID를 URL에 넣으면 장바구니 리소스의 식별자와 혼동된다.
```

**요청/응답 예시:**

```http
POST /api/v1/cart/items HTTP/1.1
Content-Type: application/json

{
  "product_id": 123,
  "quantity": 1
}
```

```http
HTTP/1.1 201 Created
Location: /api/v1/cart/items/789
Content-Type: application/json

{
  "id": 789,
  "product_id": 123,
  "name": "무선 키보드",
  "price": 45000,
  "quantity": 1
}
```

---

### 7. 장바구니 조회

```
[Before]
GET /api/getCartItems

[After]
GET /api/v1/cart/items
→ 200 OK

[Reason] URL/리소스 설계 — URL에 동사(get)를 넣지 않는다.
GET 메서드가 조회 행위를 담당하므로 리소스 경로만으로 충분하다.
장바구니(cart)의 하위 리소스(items)로 계층 구조를 명확히 한다.
```

**요청/응답 예시:**

```http
GET /api/v1/cart/items HTTP/1.1
Accept: application/json
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "data": [
    {
      "id": 789,
      "product_id": 123,
      "name": "무선 키보드",
      "price": 45000,
      "quantity": 1
    }
  ],
  "total_price": 45000,
  "total_items": 1
}
```

---

### 8. 결제 진행

```
[Before]
POST /api/checkout

[After]
POST /api/v1/orders
Idempotency-Key: <UUID v4>
→ 201 Created

[Reason] URL/리소스 설계 + 멱등성 키 — checkout은 동사이므로 리소스 명사로
바꾼다. 결제의 결과물은 주문(order)이므로 주문 리소스를 생성하는 것으로
모델링한다. 결제는 중복이 치명적인 POST 엔드포인트이므로 Idempotency-Key
헤더를 필수로 요구하여 네트워크 장애 시 중복 주문을 방지한다.
```

**요청/응답 예시:**

```http
POST /api/v1/orders HTTP/1.1
Content-Type: application/json
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000

{
  "shipping_address_id": 42,
  "payment_method_id": 7
}
```

```http
HTTP/1.1 201 Created
Location: /api/v1/orders/1001
Content-Type: application/json

{
  "id": 1001,
  "status": "pending",
  "items": [
    {
      "product_id": 123,
      "name": "무선 키보드",
      "price": 45000,
      "quantity": 1
    }
  ],
  "total_price": 45000,
  "created_at": "2026-04-04T10:30:00Z"
}
```

---

## 공통 설계 원칙

### 버전 관리

URL Path 방식(`/api/v1/`)을 적용한다. 가시성이 높고 라우팅이 단순하여 가장 널리 채택된 전략이다.

- 메이저 변경(필드 제거, 타입 변경 등)은 `/api/v2/`로 새 버전 생성
- 추가적 변경(필드 추가, 선택 파라미터 추가)은 동일 버전 내에서 처리
- Sunset 헤더로 구버전 만료 일정 고지, 최소 6개월 마이그레이션 기간 보장

### 페이지네이션

목록 조회 엔드포인트(`GET /api/v1/products`)에 커서 기반 페이지네이션을 적용한다.

```
GET /api/v1/products?limit=25&cursor=eyJpZCI6IDEyM30=
```

- 커서는 base64로 인코딩하여 불투명하게 유지
- 응답에 `has_more`와 `next_cursor`를 포함
- 대규모 데이터에서 offset 대비 17배 빠른 성능

### 에러 응답 (RFC 9457)

모든 에러 응답은 RFC 9457 Problem Details 형식을 사용한다.

```json
HTTP/1.1 404 Not Found
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/resource-not-found",
  "title": "Resource not found.",
  "status": 404,
  "detail": "Product with id 999 does not exist.",
  "instance": "/api/v1/products/999"
}
```

```json
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Validation failed.",
  "status": 422,
  "detail": "One or more fields have invalid values.",
  "instance": "/api/v1/products",
  "errors": [
    {"field": "price", "message": "Must be a positive number."},
    {"field": "name", "message": "Must not be blank."}
  ]
}
```

### 멱등성 키

결제(`POST /api/v1/orders`)에 `Idempotency-Key` 헤더를 필수로 적용한다.

- 클라이언트가 V4 UUID를 생성하여 요청 헤더에 포함
- 서버가 첫 요청의 상태 코드와 응답 본문을 저장
- 동일 키의 후속 요청은 저장된 결과를 재반환
- 키는 24시간 후 만료

### 상태 코드 정리

| 동작 | 성공 코드 | 주요 실패 코드 |
|------|----------|--------------|
| `POST` 생성 | 201 Created | 400, 409, 422 |
| `GET` 조회 | 200 OK | 404 |
| `PATCH` 수정 | 200 OK | 400, 404, 422 |
| `DELETE` 삭제 | 204 No Content | 404 |
| 인증 실패 | -- | 401 Unauthorized |
| 권한 부족 | -- | 403 Forbidden |
| Rate limit 초과 | -- | 429 Too Many Requests |
