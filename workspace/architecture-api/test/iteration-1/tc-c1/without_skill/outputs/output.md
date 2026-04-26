# RESTful API 리팩토링

## 기존 API

```
POST /api/createProduct         → 상품 등록
GET  /api/getProductById/123    → 상품 조회
POST /api/updateProduct/123     → 상품 수정
POST /api/removeProduct/123     → 상품 삭제
GET  /api/searchProducts?q=...  → 상품 검색
POST /api/addToCart/123         → 장바구니 추가
GET  /api/getCartItems          → 장바구니 조회
POST /api/checkout              → 결제 진행
```

## 리팩토링된 API

### 상품 (Products)

| 메서드 | 엔드포인트 | 설명 | 비고 |
|--------|-----------|------|------|
| POST | `/api/products` | 상품 등록 | 요청 본문에 상품 데이터 포함 |
| GET | `/api/products/{id}` | 상품 조회 | 경로 파라미터로 ID 전달 |
| PUT | `/api/products/{id}` | 상품 전체 수정 | 리소스 전체 교체 |
| PATCH | `/api/products/{id}` | 상품 부분 수정 | 일부 필드만 변경 시 |
| DELETE | `/api/products/{id}` | 상품 삭제 | — |
| GET | `/api/products?q=...` | 상품 검색 | 쿼리 파라미터로 필터링 |

### 장바구니 (Cart)

| 메서드 | 엔드포인트 | 설명 | 비고 |
|--------|-----------|------|------|
| POST | `/api/cart/items` | 장바구니에 상품 추가 | 요청 본문에 `productId`, `quantity` 포함 |
| GET | `/api/cart/items` | 장바구니 항목 조회 | — |
| DELETE | `/api/cart/items/{itemId}` | 장바구니 항목 삭제 | (추가 권장) |
| PATCH | `/api/cart/items/{itemId}` | 장바구니 항목 수량 변경 | (추가 권장) |

### 주문 (Orders)

| 메서드 | 엔드포인트 | 설명 | 비고 |
|--------|-----------|------|------|
| POST | `/api/orders` | 주문 생성 (결제 진행) | 장바구니 기반 주문 생성 |

## 변경 사항 요약

### 1. URL에서 동사 제거

REST에서 URL은 리소스(명사)를 나타내고, HTTP 메서드가 행위를 표현한다.

- `createProduct` -> `POST /products` (POST 자체가 "생성"을 의미)
- `getProductById` -> `GET /products/{id}` (GET 자체가 "조회"를 의미)
- `removeProduct` -> `DELETE /products/{id}` (DELETE 자체가 "삭제"를 의미)

### 2. 올바른 HTTP 메서드 사용

| 기존 | 변경 | 이유 |
|------|------|------|
| `POST /updateProduct` | `PUT` 또는 `PATCH` | 수정은 POST가 아니라 PUT/PATCH가 의미적으로 정확 |
| `POST /removeProduct` | `DELETE` | 삭제 행위는 DELETE 메서드로 표현 |
| `GET /searchProducts` | `GET /products?q=` | 검색은 별도 엔드포인트가 아니라 컬렉션 리소스에 필터를 적용하는 것 |

### 3. 리소스 중심의 계층 구조

장바구니 항목은 `/cart/items`로 구성하여 리소스 간 관계를 URL 구조로 표현했다. `checkout`은 주문 리소스 생성(`POST /orders`)으로 모델링하여, 행위가 아닌 리소스 생성으로 전환했다.

### 4. 복수형 명사 사용

컬렉션 리소스는 복수형(`products`, `items`, `orders`)으로 통일하여 일관성을 확보했다.

## 응답 상태 코드 가이드

| 상황 | 상태 코드 |
|------|----------|
| 리소스 생성 성공 | `201 Created` |
| 조회/수정 성공 | `200 OK` |
| 삭제 성공 | `204 No Content` |
| 잘못된 요청 | `400 Bad Request` |
| 리소스 없음 | `404 Not Found` |
| 인증 실패 | `401 Unauthorized` |
| 서버 오류 | `500 Internal Server Error` |
