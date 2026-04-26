# 주문 Bounded Context REST API 엔드포인트 설계

## 운영 모드: 설계

---

## 1. 전략적 설계 전제

REST API 설계에 앞서 바운디드 컨텍스트 경계를 먼저 확인한다. 전략적 설계가 전술적 패턴보다 선행해야 하며, API 설계도 이 원칙의 연장선에 있다.

**주문(Ordering) Bounded Context의 범위:**
- 주문 애그리거트(Order)가 루트이며, OrderLineItem과 ShippingInfo는 내부 구성요소이다
- Member, Product 등 외부 애그리거트는 ID로만 참조한다 (Vernon 규칙 3)
- 재고 차감, 포인트 적립 등은 도메인 이벤트를 통한 결과적 일관성으로 처리한다 (Vernon 규칙 4)

**컨텍스트 맵 기준 이 API의 성격:**
- 주문 컨텍스트는 **오픈 호스트 서비스(OHS) + 발행된 언어(Published Language)** 패턴으로 외부에 REST API를 제공한다
- 다운스트림 컨텍스트(결제, 배송, 재고)는 이 API를 통해 주문 정보에 접근하거나, 도메인 이벤트를 구독한다

---

## 2. 리소스 식별

유비쿼터스 언어를 API 리소스명에 반영한다. `updateStatus()` 대신 `confirm()`, `cancel()`, `ship()`처럼 비즈니스 의도를 드러내는 이름을 사용하는 원칙을 URL 설계에도 적용한다.

| 도메인 개념 | API 리소스 | 설명 |
|------------|-----------|------|
| 주문 (Order) | `/orders` | 애그리거트 루트 -- 주요 리소스 |
| 주문 항목 (OrderLineItem) | `/orders/{id}/items` | 애그리거트 내부 구성요소 -- 하위 리소스 |
| 배송 정보 (ShippingInfo) | `/orders/{id}/shipping-info` | 애그리거트 내부 값 객체 -- 하위 리소스 |
| 주문 상태 전이 | `/orders/{id}/confirm`, `/orders/{id}/cancel`, `/orders/{id}/ship` | 도메인 커맨드에 대응하는 액션 리소스 |

---

## 3. URL 구조

### 3.1 기본 CRUD 엔드포인트

```
# 컬렉션: 복수 명사, kebab-case 소문자, 후행 슬래시 없음
GET    /v1/orders                      # 주문 목록 조회
POST   /v1/orders                      # 주문 생성 (접수)
GET    /v1/orders/{order_id}           # 주문 단건 조회
DELETE /v1/orders/{order_id}           # 주문 삭제 (관리자 전용)
```

### 3.2 하위 리소스 (최대 3단계 깊이 준수)

```
# 주문 항목 -- 애그리거트 내부 구성요소
GET    /v1/orders/{order_id}/items             # 주문 항목 목록
GET    /v1/orders/{order_id}/items/{item_id}   # 주문 항목 단건 (3단계 -- 허용)

# 배송 정보 -- 값 객체 (단건만 존재)
GET    /v1/orders/{order_id}/shipping-info     # 배송 정보 조회
PUT    /v1/orders/{order_id}/shipping-info     # 배송 정보 전체 교체
```

### 3.3 도메인 커맨드 (상태 전이 액션)

DDD에서 애그리거트의 상태 전이는 명시적인 도메인 커맨드로 표현된다. REST의 "동사 금지" 원칙과 DDD의 "의도를 드러내는 인터페이스" 원칙 사이에서, 상태 전이처럼 단순 CRUD로 표현할 수 없는 비즈니스 행위는 POST + 액션 하위 리소스로 설계한다.

```
# 주문 확정 -- Order.place() / Order.confirm()에 대응
POST   /v1/orders/{order_id}/confirm

# 주문 취소 -- Order.cancel()에 대응
POST   /v1/orders/{order_id}/cancel

# 출고 처리 -- Order.ship()에 대응
POST   /v1/orders/{order_id}/ship
```

**설계 근거:**
- `PATCH /v1/orders/{order_id}` + `{"status": "confirmed"}`는 빈약한 도메인 모델(setter 기반)을 조장한다
- `POST /v1/orders/{order_id}/confirm`은 도메인 커맨드와 1:1로 매핑되어 유비쿼터스 언어를 API에 직접 반영한다
- 각 액션은 고유한 비즈니스 규칙과 검증 로직을 가지므로 별도 엔드포인트가 적합하다

### 3.4 필터링, 정렬, 검색

```
GET /v1/orders?status=preparing                     # 상태 필터
GET /v1/orders?status=shipped&min-total=10000       # 복합 필터
GET /v1/orders?sort=-created_at,total               # 정렬 (- = DESC)
GET /v1/orders?fields=id,status,total               # 필드 선택
GET /v1/orders?customer-id=cust-123                 # 특정 고객의 주문
GET /v1/orders?created-after=2026-01-01             # 날짜 범위
GET /v1/orders?cursor=eyJpZCI6MTAwfQ&limit=25       # 커서 기반 페이지네이션
```

### 3.5 전체 URL 맵

| 메서드 | URL | 설명 | 요청 본문 |
|--------|-----|------|----------|
| `POST` | `/v1/orders` | 주문 생성 | 주문자ID, 상품 목록, 배송 정보 |
| `GET` | `/v1/orders` | 주문 목록 조회 | -- |
| `GET` | `/v1/orders/{order_id}` | 주문 단건 조회 | -- |
| `DELETE` | `/v1/orders/{order_id}` | 주문 삭제 | -- |
| `GET` | `/v1/orders/{order_id}/items` | 주문 항목 목록 | -- |
| `GET` | `/v1/orders/{order_id}/shipping-info` | 배송 정보 조회 | -- |
| `PUT` | `/v1/orders/{order_id}/shipping-info` | 배송 정보 변경 | 수령인, 전화번호, 주소 |
| `POST` | `/v1/orders/{order_id}/confirm` | 주문 확정 | -- (또는 결제 정보) |
| `POST` | `/v1/orders/{order_id}/cancel` | 주문 취소 | 취소 사유 (선택) |
| `POST` | `/v1/orders/{order_id}/ship` | 출고 처리 | 운송장 번호 (선택) |

---

## 4. HTTP 상태 코드 설계

### 4.1 성공 응답 (2xx)

| 엔드포인트 | 상태 코드 | 설명 |
|-----------|----------|------|
| `POST /v1/orders` | **201 Created** | 주문 생성 성공. `Location: /v1/orders/{new_id}` 헤더 포함 |
| `GET /v1/orders` | **200 OK** | 목록 조회 성공 |
| `GET /v1/orders/{id}` | **200 OK** | 단건 조회 성공 |
| `PUT /v1/orders/{id}/shipping-info` | **200 OK** | 배송 정보 교체 성공 (변경된 리소스 반환) |
| `DELETE /v1/orders/{id}` | **204 No Content** | 삭제 성공. 응답 본문 없음 |
| `POST /v1/orders/{id}/confirm` | **200 OK** | 상태 전이 성공 (변경된 주문 반환) |
| `POST /v1/orders/{id}/cancel` | **200 OK** | 취소 성공 (변경된 주문 반환) |
| `POST /v1/orders/{id}/ship` | **200 OK** | 출고 처리 성공 (변경된 주문 반환) |

> **비동기 처리가 필요한 경우**: 주문 생성이 결제 확인까지 포함하여 즉시 완료되지 않는 구조라면 `202 Accepted`를 사용하고, 폴링용 URL을 `Location` 헤더에 제공한다.

### 4.2 클라이언트 오류 응답 (4xx)

| 상태 코드 | 발생 조건 | 예시 |
|----------|----------|------|
| **400 Bad Request** | 요청 형식 오류, 필수 필드 누락 | 주문 항목 없이 POST 요청 |
| **401 Unauthorized** | 인증되지 않은 요청 | 토큰 없음 또는 만료 |
| **403 Forbidden** | 인가 부족 | 다른 사용자의 주문 취소 시도, 관리자 전용 삭제 |
| **404 Not Found** | 리소스 없음 | 존재하지 않는 order_id |
| **409 Conflict** | 비즈니스 규칙 충돌 | 이미 출고된 주문을 다시 확정 시도, 중복 주문 |
| **422 Unprocessable Entity** | 문법은 맞지만 의미적 처리 불가 | 수량이 0인 주문 항목, 유효하지 않은 주소 형식 |
| **429 Too Many Requests** | Rate Limit 초과 | `Retry-After` 헤더와 함께 반환 |

### 4.3 서버 오류 응답 (5xx)

| 상태 코드 | 발생 조건 |
|----------|----------|
| **500 Internal Server Error** | 서버 내부 오류 |
| **503 Service Unavailable** | 일시적 과부하 또는 정비. `Retry-After` 헤더 포함 |

### 4.4 도메인 커맨드별 상태 코드 상세 매핑

DDD 애그리거트의 비즈니스 규칙 위반은 상황에 따라 적절한 4xx 코드로 변환한다.

```
POST /v1/orders/{id}/confirm

  성공:
    200 OK -- 주문이 "preparing" 상태로 전이

  실패:
    404 Not Found   -- order_id가 존재하지 않음
    409 Conflict     -- "결제 대기 상태에서만 확정할 수 있습니다"
                        (현재 상태가 payment_waiting이 아닌 경우)
```

```
POST /v1/orders/{id}/cancel

  성공:
    200 OK -- 주문이 취소됨

  실패:
    404 Not Found   -- order_id가 존재하지 않음
    409 Conflict     -- "이미 출고된 주문은 취소할 수 없습니다"
                        (출고 후 취소 불가 규칙)
```

```
POST /v1/orders/{id}/ship

  성공:
    200 OK -- 주문이 "shipped" 상태로 전이

  실패:
    404 Not Found   -- order_id가 존재하지 않음
    409 Conflict     -- "준비 상태에서만 출고할 수 있습니다"
                        (현재 상태가 preparing이 아닌 경우)
```

```
PUT /v1/orders/{id}/shipping-info

  성공:
    200 OK -- 배송 정보가 교체됨

  실패:
    404 Not Found   -- order_id가 존재하지 않음
    409 Conflict     -- "배송지를 변경할 수 없는 상태입니다"
                        (이미 출고 이후)
    422 Unprocessable Entity -- 주소 형식 유효성 검증 실패
```

### 4.5 409 vs 422 구분 기준

| 코드 | 사용 기준 | 주문 컨텍스트 예시 |
|------|----------|----------------|
| **409 Conflict** | 리소스의 현재 **상태**와 요청이 충돌 | 이미 출고된 주문 취소, 이미 확정된 주문 재확정 |
| **422 Unprocessable Entity** | 요청 데이터의 **의미적** 유효성 실패 | 수량 0인 주문 항목, 잘못된 주소 형식, 존재하지 않는 상품 ID |

---

## 5. 오류 응답 형식 (RFC 9457 Problem Details)

모든 오류 응답은 RFC 9457 형식을 일관되게 적용한다.

### 5.1 비즈니스 규칙 위반 (409)

```json
HTTP/1.1 409 Conflict
Content-Type: application/problem+json

{
  "type": "https://api.example.com/probs/order-state-conflict",
  "title": "Order state does not allow this action.",
  "status": 409,
  "detail": "주문 ORD-20260405-001은 현재 'shipped' 상태이므로 취소할 수 없습니다. 'payment_waiting' 또는 'preparing' 상태에서만 취소가 가능합니다.",
  "instance": "/v1/orders/ORD-20260405-001/cancel",
  "current_status": "shipped",
  "allowed_statuses": ["payment_waiting", "preparing"]
}
```

### 5.2 유효성 검증 실패 (422)

```json
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/problem+json

{
  "type": "https://api.example.com/probs/validation-error",
  "title": "Validation failed.",
  "status": 422,
  "detail": "주문 요청에 유효하지 않은 필드가 있습니다.",
  "instance": "/v1/orders",
  "errors": [
    {
      "field": "items[0].quantity",
      "reason": "최소 한 개 이상이어야 합니다",
      "rejected_value": 0
    },
    {
      "field": "shipping_address.zipcode",
      "reason": "5자리 숫자 형식이어야 합니다",
      "rejected_value": "ABC"
    }
  ]
}
```

### 5.3 인증 실패 (401)

```json
HTTP/1.1 401 Unauthorized
Content-Type: application/problem+json
WWW-Authenticate: Bearer

{
  "type": "https://api.example.com/probs/authentication-required",
  "title": "Authentication required.",
  "status": 401,
  "detail": "유효한 인증 토큰이 필요합니다.",
  "instance": "/v1/orders"
}
```

### 5.4 인가 부족 (403)

```json
HTTP/1.1 403 Forbidden
Content-Type: application/problem+json

{
  "type": "https://api.example.com/probs/insufficient-permission",
  "title": "You do not have permission to perform this action.",
  "status": 403,
  "detail": "주문 ORD-20260405-001은 다른 사용자의 주문이므로 취소할 수 없습니다.",
  "instance": "/v1/orders/ORD-20260405-001/cancel"
}
```

---

## 6. 멱등성 처리

주문 생성(`POST /v1/orders`)은 멱등하지 않으므로, 중복 주문 방지를 위해 Idempotency-Key 패턴을 적용한다.

```
POST /v1/orders
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{
  "orderer_id": "cust-123",
  "items": [...],
  "shipping_address": {...}
}
```

- 클라이언트가 V4 UUID로 고유 키를 생성한다
- 서버는 첫 요청의 상태 코드 + 응답 본문을 저장한다
- 동일 키의 후속 요청은 저장된 결과를 반환한다
- 키는 24시간 후 만료한다

상태 전이 액션(`/confirm`, `/cancel`, `/ship`)은 POST이지만, 도메인 모델의 상태 검증이 자연스러운 멱등성을 제공한다. 이미 확정된 주문에 다시 확정 요청을 보내면 409로 거부되므로 중복 처리 위험이 없다.

---

## 7. 버저닝

URL 경로에 메이저 버전을 포함한다 (`/v1/`). 호환성을 깨는 변경이 필요할 때만 `/v2/`를 도입하며, 추가적 변경(필드 추가, 선택적 파라미터 추가)은 버전을 올리지 않는다.

```
/v1/orders          # 현재 버전
/v2/orders          # 호환성 깨는 변경 시에만 도입
```

---

## 8. 스킬 상호 참조

- Django Ninja를 사용한 Router/Schema 구현에 대한 상세 가이드는 **implementation-django-ninja** 스킬을 참조하세요.
- 페이지네이션 패턴(Cursor, Offset, Keyset) 선택에 대한 상세 가이드는 **architecture-api** 스킬의 페이지네이션 참조를 참조하세요.
- 인증/인가 방식(API Key, OAuth 2.0, JWT) 선택에 대한 상세 가이드는 **architecture-api** 스킬의 인증 참조를 참조하세요.
- 헥사고날/클린/CQRS 등 아키텍처 패턴 선택에 대한 상세 가이드는 **architecture-implementation-patterns** 스킬을 참조하세요.
- 주문 테이블 스키마, 인덱스 설계에 대한 상세 가이드는 **architecture-db** 스킬을 참조하세요.
- 애그리거트 설계, 도메인 이벤트, 값 객체 등 전술적 패턴에 대한 상세 가이드는 **architecture-ddd** 스킬을 참조하세요.
