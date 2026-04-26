# 주문(Order) Bounded Context REST API 설계

## 1. URL 구조 원칙

### 1.1 기본 규칙

| 원칙 | 설명 |
|------|------|
| 리소스는 명사, 복수형 | `/orders` (O) / `/order` (X) / `/getOrder` (X) |
| Aggregate Root만 최상위 리소스로 노출 | Order가 Aggregate Root이므로 `/orders`가 진입점 |
| 내부 Entity는 중첩 경로로 표현 | OrderLine은 `/orders/{id}/lines`로 접근 |
| 도메인 행위(Command)는 동사 하위 리소스로 표현 | CRUD로 환원 불가능한 비즈니스 액션에 한정 |
| API 버전은 URL prefix로 관리 | `/api/v1/orders` |

### 1.2 Bounded Context 경계와 URL

```
/api/v1/orders/**        -- 주문 Context 소유
/api/v1/payments/**      -- 결제 Context 소유 (별도 서비스)
/api/v1/products/**      -- 상품 Context 소유 (별도 서비스)
```

주문 Context는 `/api/v1/orders` 하위만 책임진다. 결제, 상품 등 다른 Context의 데이터가 필요하면 내부적으로 ACL(Anti-Corruption Layer)을 통해 조회하되, 해당 데이터를 자신의 URL 아래에 노출하지 않는다.

---

## 2. 엔드포인트 상세 설계

### 2.1 주문 Aggregate Root

| Method | URL | 용도 | 요청 Body |
|--------|-----|------|-----------|
| `POST` | `/api/v1/orders` | 주문 생성 (PlaceOrder Command) | `PlaceOrderRequest` |
| `GET` | `/api/v1/orders/{orderId}` | 단건 주문 조회 | - |
| `GET` | `/api/v1/orders` | 주문 목록 조회 (필터/페이징) | - |
| `DELETE` | `/api/v1/orders/{orderId}` | 주문 삭제 (논리 삭제) | - |

### 2.2 주문 상태 전이 (도메인 행위)

CRUD로 환원할 수 없는 비즈니스 액션은 별도 하위 리소스로 모델링한다. `PATCH /orders/{id}` 에 상태값을 넘기는 방식은 도메인 의도가 드러나지 않으므로 피한다.

| Method | URL | 용도 | 비고 |
|--------|-----|------|------|
| `POST` | `/api/v1/orders/{orderId}/confirm` | 주문 확정 | 판매자/시스템이 주문을 승인 |
| `POST` | `/api/v1/orders/{orderId}/cancel` | 주문 취소 | 취소 사유를 Body에 포함 |
| `POST` | `/api/v1/orders/{orderId}/ship` | 배송 시작 | 운송장 정보를 Body에 포함 |
| `POST` | `/api/v1/orders/{orderId}/complete` | 주문 완료 | 수령 확인 |
| `POST` | `/api/v1/orders/{orderId}/return` | 반품 요청 | 반품 사유를 Body에 포함 |

> 왜 POST인가: 이 액션들은 멱등하지 않은(non-idempotent) 도메인 커맨드다. 동일 요청을 두 번 보내면 이미 전이된 상태에서 다시 전이를 시도하므로 409 Conflict가 발생해야 한다. PUT은 "전체 교체"라는 HTTP 의미론과 맞지 않으므로 POST가 적합하다.

### 2.3 주문 항목 (OrderLine -- 하위 Entity)

| Method | URL | 용도 |
|--------|-----|------|
| `GET` | `/api/v1/orders/{orderId}/lines` | 주문 항목 목록 조회 |
| `GET` | `/api/v1/orders/{orderId}/lines/{lineId}` | 주문 항목 단건 조회 |
| `PATCH` | `/api/v1/orders/{orderId}/lines/{lineId}` | 주문 항목 수정 (수량 변경 등) |

> OrderLine은 Order Aggregate 내부 Entity이므로 독립적인 생성/삭제 엔드포인트를 두지 않는다. 항목 추가/제거는 Order 수준의 커맨드로 처리하는 것이 Aggregate 불변식을 보장한다.

### 2.4 주문 이력/이벤트 (읽기 전용)

| Method | URL | 용도 |
|--------|-----|------|
| `GET` | `/api/v1/orders/{orderId}/events` | 주문 상태 변경 이력 조회 |

### 2.5 목록 조회 쿼리 파라미터

```
GET /api/v1/orders?status=CONFIRMED&from=2026-04-01&to=2026-04-05&page=0&size=20&sort=createdAt,desc
```

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `status` | string | 주문 상태 필터 (PLACED, CONFIRMED, SHIPPED, COMPLETED, CANCELLED, RETURNED) |
| `from` | date | 주문일 시작 범위 (ISO 8601) |
| `to` | date | 주문일 종료 범위 (ISO 8601) |
| `customerId` | string | 고객 ID 필터 |
| `page` | int | 페이지 번호 (0-based) |
| `size` | int | 페이지 크기 (기본 20, 최대 100) |
| `sort` | string | 정렬 기준 (예: `createdAt,desc`) |

---

## 3. HTTP 상태 코드 설계

### 3.1 성공 응답

| 상태 코드 | 사용 장면 | 적용 엔드포인트 예시 |
|-----------|-----------|---------------------|
| `200 OK` | 조회 성공, 업데이트 성공 | `GET /orders/{id}`, `PATCH /orders/{id}/lines/{lineId}` |
| `201 Created` | 리소스 생성 성공 | `POST /orders` |
| `204 No Content` | 삭제 성공, Body 없는 성공 | `DELETE /orders/{id}` |

> `201 Created` 응답 시 `Location` 헤더에 생성된 리소스의 URI를 포함한다.
> ```
> HTTP/1.1 201 Created
> Location: /api/v1/orders/ord-20260405-0001
> ```

### 3.2 도메인 행위(Command) 응답

| 상태 코드 | 사용 장면 | 적용 엔드포인트 예시 |
|-----------|-----------|---------------------|
| `200 OK` | 상태 전이 성공, 변경된 리소스 반환 | `POST /orders/{id}/confirm` |
| `202 Accepted` | 비동기 처리가 접수된 경우 | 결제 연동이 오래 걸릴 때 |

> 동기 처리라면 `200`으로 변경된 Order 상태를 즉시 반환한다. 비동기 처리라면 `202`와 함께 폴링 가능한 URI를 반환한다.

### 3.3 클라이언트 오류

| 상태 코드 | 의미 | 발생 조건 |
|-----------|------|-----------|
| `400 Bad Request` | 요청 형식 오류 | 필수 필드 누락, 잘못된 JSON, 유효성 검증 실패 |
| `401 Unauthorized` | 인증 실패 | 토큰 없음, 토큰 만료 |
| `403 Forbidden` | 인가 실패 | 타인의 주문에 접근 시도 |
| `404 Not Found` | 리소스 없음 | 존재하지 않는 orderId |
| `409 Conflict` | 도메인 규칙 위반, 상태 충돌 | 이미 취소된 주문을 다시 취소, 재고 부족, 낙관적 잠금 충돌 |
| `422 Unprocessable Entity` | 요청 형식은 정상이나 도메인 로직 위반 | 주문 최소 금액 미달, 배송 불가 지역 |

### 3.4 400 vs 409 vs 422 판단 기준

```
요청 파싱/바인딩 실패?
  --> 400 Bad Request (JSON 문법 오류, 필수 필드 누락, 타입 불일치)

요청은 유효하지만 현재 리소스 상태와 충돌?
  --> 409 Conflict (이미 CANCELLED인 주문에 ship 요청, 낙관적 잠금 버전 불일치)

요청은 유효하고 상태 충돌은 아니지만 비즈니스 규칙 위반?
  --> 422 Unprocessable Entity (최소 주문 금액 미달, 주문 항목 0개)
```

### 3.5 서버 오류

| 상태 코드 | 의미 | 발생 조건 |
|-----------|------|-----------|
| `500 Internal Server Error` | 예상치 못한 서버 오류 | 처리되지 않은 예외 |
| `502 Bad Gateway` | 외부 서비스 호출 실패 | 결제 Context, 상품 Context 통신 실패 |
| `503 Service Unavailable` | 일시적 서비스 불가 | 서킷브레이커 Open 상태 |

---

## 4. 오류 응답 Body 표준 형식

모든 오류 응답은 아래 형식을 따른다. RFC 9457 (Problem Details for HTTP APIs) 기반이다.

```json
{
  "type": "https://api.example.com/errors/order-already-cancelled",
  "title": "Order Already Cancelled",
  "status": 409,
  "detail": "주문 ord-20260405-0001은 이미 취소된 상태입니다.",
  "instance": "/api/v1/orders/ord-20260405-0001/cancel",
  "timestamp": "2026-04-05T14:30:00Z",
  "errors": []
}
```

유효성 검증 오류(400, 422)일 때 `errors` 배열에 필드별 상세를 포함한다.

```json
{
  "type": "https://api.example.com/errors/validation-failed",
  "title": "Validation Failed",
  "status": 400,
  "detail": "요청 데이터가 유효하지 않습니다.",
  "instance": "/api/v1/orders",
  "timestamp": "2026-04-05T14:30:00Z",
  "errors": [
    {
      "field": "shippingAddress.zipCode",
      "rejected": "999",
      "message": "우편번호는 5자리여야 합니다."
    },
    {
      "field": "lines",
      "rejected": [],
      "message": "주문 항목은 1개 이상이어야 합니다."
    }
  ]
}
```

---

## 5. 전체 엔드포인트 요약

```
POST   /api/v1/orders                              주문 생성         201 | 400, 422
GET    /api/v1/orders                              주문 목록 조회     200
GET    /api/v1/orders/{orderId}                    주문 단건 조회     200 | 404
DELETE /api/v1/orders/{orderId}                    주문 삭제         204 | 404, 409

POST   /api/v1/orders/{orderId}/confirm            주문 확정         200 | 404, 409
POST   /api/v1/orders/{orderId}/cancel             주문 취소         200 | 404, 409
POST   /api/v1/orders/{orderId}/ship               배송 시작         200 | 404, 409
POST   /api/v1/orders/{orderId}/complete            주문 완료         200 | 404, 409
POST   /api/v1/orders/{orderId}/return             반품 요청         200 | 404, 409

GET    /api/v1/orders/{orderId}/lines              주문 항목 목록     200 | 404
GET    /api/v1/orders/{orderId}/lines/{lineId}     주문 항목 단건     200 | 404
PATCH  /api/v1/orders/{orderId}/lines/{lineId}     주문 항목 수정     200 | 400, 404, 409

GET    /api/v1/orders/{orderId}/events             주문 이력 조회     200 | 404
```

---

## 6. 설계 판단 근거

### Q. 왜 `/orders/{id}/cancel` 이고 `PATCH /orders/{id}` 가 아닌가?

`PATCH`로 `{ "status": "CANCELLED" }` 를 보내는 방식은 기술적으로 가능하지만, 도메인 의도를 숨긴다. 취소에는 취소 사유, 환불 정책 적용, 재고 복원 등 부수 효과가 따른다. 이를 단순 필드 업데이트로 표현하면 API 소비자가 비즈니스 규칙을 이해하기 어렵고, 서버 측에서도 "어떤 필드 조합이 들어오면 어떤 커맨드를 실행할지"를 분기해야 하는 복잡성이 생긴다. 명시적 커맨드 엔드포인트가 Intent-Revealing Interface 원칙에 부합한다.

### Q. 왜 하위 Entity(OrderLine)의 생성/삭제는 없는가?

DDD에서 Aggregate Root를 통하지 않는 내부 Entity 조작은 불변식(invariant) 위반 위험이 있다. 예를 들어, 주문 항목을 직접 삭제하면 "주문은 최소 1개 항목을 가져야 한다"는 불변식을 깨뜨릴 수 있다. 항목 추가/제거는 Order 수준의 커맨드(`POST /orders/{id}/add-line`, `POST /orders/{id}/remove-line`)로 모델링하거나, 주문 생성/수정 시 전체 항목 목록을 함께 전달하는 방식이 안전하다.

### Q. 왜 `404`와 `409`를 구분하는가?

- `404`는 리소스 자체가 존재하지 않을 때 사용한다. 클라이언트가 URL을 잘못 구성했거나 삭제된 리소스에 접근한 경우다.
- `409`는 리소스는 존재하지만 현재 상태에서 요청된 행위를 수행할 수 없을 때 사용한다. 클라이언트는 리소스 상태를 다시 조회한 뒤 적절한 액션을 취할 수 있다.

이 구분이 있어야 클라이언트가 오류 복구 전략을 올바르게 수립할 수 있다.
