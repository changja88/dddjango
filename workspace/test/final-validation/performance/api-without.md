# 주문 관리 REST API 설계

## 1. 기본 정보

| 항목 | 값 |
|------|-----|
| Base URL | `https://api.example.com/v1` |
| 인증 | Bearer Token (JWT) |
| Content-Type | `application/json` |
| API 버전 관리 | URL Path 방식 (`/v1/`, `/v2/`) |

---

## 2. URL 구조 및 HTTP 메서드

### 2.1 주문 (Orders)

| 메서드 | URL | 설명 |
|--------|-----|------|
| `GET` | `/orders` | 주문 목록 조회 |
| `POST` | `/orders` | 새 주문 생성 |
| `GET` | `/orders/{order_id}` | 주문 상세 조회 |
| `PUT` | `/orders/{order_id}` | 주문 전체 수정 |
| `PATCH` | `/orders/{order_id}` | 주문 부분 수정 |
| `DELETE` | `/orders/{order_id}` | 주문 삭제 (소프트 삭제) |

### 2.2 주문 상태 변경 (Order Status)

| 메서드 | URL | 설명 |
|--------|-----|------|
| `POST` | `/orders/{order_id}/confirm` | 주문 확정 |
| `POST` | `/orders/{order_id}/cancel` | 주문 취소 |
| `POST` | `/orders/{order_id}/ship` | 배송 시작 |
| `POST` | `/orders/{order_id}/deliver` | 배송 완료 |
| `POST` | `/orders/{order_id}/refund` | 환불 처리 |

### 2.3 주문 항목 (Order Items)

| 메서드 | URL | 설명 |
|--------|-----|------|
| `GET` | `/orders/{order_id}/items` | 주문 항목 목록 조회 |
| `POST` | `/orders/{order_id}/items` | 주문 항목 추가 |
| `GET` | `/orders/{order_id}/items/{item_id}` | 주문 항목 상세 조회 |
| `PATCH` | `/orders/{order_id}/items/{item_id}` | 주문 항목 수정 (수량 등) |
| `DELETE` | `/orders/{order_id}/items/{item_id}` | 주문 항목 삭제 |

### 2.4 주문 이력 (Order History)

| 메서드 | URL | 설명 |
|--------|-----|------|
| `GET` | `/orders/{order_id}/history` | 주문 상태 변경 이력 조회 |

---

## 3. 주문 상태 흐름 (State Machine)

```
PENDING --> CONFIRMED --> SHIPPING --> DELIVERED
  |            |
  v            v
CANCELLED   CANCELLED
               |
               v
            REFUNDED
```

유효한 상태 값:

| 상태 | 설명 |
|------|------|
| `pending` | 주문 접수 (결제 대기) |
| `confirmed` | 주문 확정 (결제 완료) |
| `shipping` | 배송 중 |
| `delivered` | 배송 완료 |
| `cancelled` | 주문 취소 |
| `refunded` | 환불 완료 |

---

## 4. 요청/응답 형식

### 4.1 주문 생성 요청

```http
POST /v1/orders
Content-Type: application/json
Authorization: Bearer {token}
```

```json
{
  "customer_id": 12345,
  "shipping_address": {
    "name": "홍길동",
    "phone": "010-1234-5678",
    "zip_code": "06100",
    "address": "서울특별시 강남구 테헤란로 123",
    "detail": "4층 402호"
  },
  "items": [
    {
      "product_id": 1001,
      "quantity": 2,
      "price": 29000
    },
    {
      "product_id": 1005,
      "quantity": 1,
      "price": 15000
    }
  ],
  "payment_method": "card",
  "note": "부재 시 문 앞에 놓아주세요"
}
```

### 4.2 주문 상세 응답

```http
GET /v1/orders/550e8400-e29b-41d4-a716-446655440000
```

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "order_number": "ORD-20260406-0001",
  "status": "confirmed",
  "customer_id": 12345,
  "shipping_address": {
    "name": "홍길동",
    "phone": "010-1234-5678",
    "zip_code": "06100",
    "address": "서울특별시 강남구 테헤란로 123",
    "detail": "4층 402호"
  },
  "items": [
    {
      "id": 1,
      "product_id": 1001,
      "product_name": "무선 키보드",
      "quantity": 2,
      "unit_price": 29000,
      "subtotal": 58000
    },
    {
      "id": 2,
      "product_id": 1005,
      "product_name": "마우스 패드",
      "quantity": 1,
      "unit_price": 15000,
      "subtotal": 15000
    }
  ],
  "subtotal": 73000,
  "shipping_fee": 3000,
  "discount": 0,
  "total": 76000,
  "payment_method": "card",
  "note": "부재 시 문 앞에 놓아주세요",
  "created_at": "2026-04-06T10:30:00+09:00",
  "updated_at": "2026-04-06T10:35:00+09:00",
  "confirmed_at": "2026-04-06T10:35:00+09:00",
  "shipped_at": null,
  "delivered_at": null
}
```

### 4.3 주문 부분 수정 요청

```http
PATCH /v1/orders/550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json
Authorization: Bearer {token}
```

```json
{
  "shipping_address": {
    "detail": "5층 501호"
  },
  "note": "경비실에 맡겨주세요"
}
```

---

## 5. 페이지네이션

커서 기반 페이지네이션을 기본으로 사용한다. 대량 데이터에서 오프셋 방식보다 일관된 성능을 보장한다.

### 5.1 요청 파라미터

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `cursor` | string | null | 다음 페이지 커서 (이전 응답의 `next_cursor`) |
| `limit` | integer | 20 | 페이지당 항목 수 (최대 100) |
| `sort` | string | `-created_at` | 정렬 기준 (`-`는 내림차순) |

### 5.2 필터링 파라미터

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `status` | string | 주문 상태 필터 (`confirmed`, `shipping` 등) |
| `customer_id` | integer | 고객 ID 필터 |
| `created_after` | datetime | 생성일 시작 범위 (ISO 8601) |
| `created_before` | datetime | 생성일 종료 범위 (ISO 8601) |
| `min_total` | integer | 최소 주문 금액 |
| `max_total` | integer | 최대 주문 금액 |
| `q` | string | 주문번호 또는 고객명 검색 |

### 5.3 요청 예시

```http
GET /v1/orders?status=shipping&limit=10&sort=-created_at
GET /v1/orders?cursor=eyJpZCI6IDEwMH0&limit=10
GET /v1/orders?created_after=2026-04-01T00:00:00+09:00&created_before=2026-04-06T23:59:59+09:00
```

### 5.4 목록 응답 형식

```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "order_number": "ORD-20260406-0001",
      "status": "shipping",
      "customer_id": 12345,
      "customer_name": "홍길동",
      "item_count": 2,
      "total": 76000,
      "created_at": "2026-04-06T10:30:00+09:00"
    }
  ],
  "pagination": {
    "next_cursor": "eyJpZCI6IDEwMH0",
    "prev_cursor": "eyJpZCI6IDkwfQ",
    "has_next": true,
    "has_prev": false,
    "limit": 10,
    "total_count": 254
  }
}
```

---

## 6. HTTP 상태 코드

### 6.1 성공 응답

| 상태 코드 | 의미 | 사용 상황 |
|-----------|------|-----------|
| `200 OK` | 성공 | GET, PUT, PATCH 성공 |
| `201 Created` | 생성 완료 | POST로 리소스 생성 성공 |
| `204 No Content` | 본문 없는 성공 | DELETE 성공 |

### 6.2 클라이언트 에러

| 상태 코드 | 의미 | 사용 상황 |
|-----------|------|-----------|
| `400 Bad Request` | 잘못된 요청 | 유효성 검증 실패, 잘못된 파라미터 |
| `401 Unauthorized` | 인증 실패 | 토큰 없음 또는 만료 |
| `403 Forbidden` | 권한 없음 | 다른 사용자의 주문 접근 시도 |
| `404 Not Found` | 리소스 없음 | 존재하지 않는 주문 조회 |
| `409 Conflict` | 상태 충돌 | 이미 취소된 주문을 다시 취소 시도 |
| `422 Unprocessable Entity` | 처리 불가 | 비즈니스 로직 위반 (재고 부족 등) |
| `429 Too Many Requests` | 요청 초과 | Rate Limit 초과 |

### 6.3 서버 에러

| 상태 코드 | 의미 | 사용 상황 |
|-----------|------|-----------|
| `500 Internal Server Error` | 서버 내부 오류 | 예상치 못한 서버 오류 |
| `502 Bad Gateway` | 게이트웨이 오류 | 외부 결제 서비스 연동 실패 |
| `503 Service Unavailable` | 서비스 불가 | 서버 점검 중 |

---

## 7. 에러 응답 형식

모든 에러 응답은 동일한 형식을 따른다.

### 7.1 기본 에러 형식

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "요청 데이터가 유효하지 않습니다.",
    "details": [
      {
        "field": "items[0].quantity",
        "message": "수량은 1 이상이어야 합니다.",
        "rejected_value": 0
      },
      {
        "field": "shipping_address.phone",
        "message": "올바른 전화번호 형식이 아닙니다.",
        "rejected_value": "1234"
      }
    ],
    "timestamp": "2026-04-06T10:30:00+09:00",
    "request_id": "req_abc123def456"
  }
}
```

### 7.2 에러 코드 목록

| 에러 코드 | HTTP 상태 | 설명 |
|-----------|-----------|------|
| `VALIDATION_ERROR` | 400 | 입력값 유효성 검증 실패 |
| `INVALID_PARAMETER` | 400 | 쿼리 파라미터 오류 |
| `AUTHENTICATION_REQUIRED` | 401 | 인증 토큰 누락 |
| `TOKEN_EXPIRED` | 401 | 인증 토큰 만료 |
| `PERMISSION_DENIED` | 403 | 접근 권한 없음 |
| `ORDER_NOT_FOUND` | 404 | 주문을 찾을 수 없음 |
| `ITEM_NOT_FOUND` | 404 | 주문 항목을 찾을 수 없음 |
| `INVALID_STATUS_TRANSITION` | 409 | 유효하지 않은 상태 전환 |
| `DUPLICATE_ORDER` | 409 | 중복 주문 (멱등성 키 충돌) |
| `INSUFFICIENT_STOCK` | 422 | 재고 부족 |
| `ORDER_NOT_CANCELLABLE` | 422 | 취소 불가능한 상태 |
| `PAYMENT_FAILED` | 422 | 결제 처리 실패 |
| `RATE_LIMIT_EXCEEDED` | 429 | 요청 한도 초과 |
| `INTERNAL_ERROR` | 500 | 서버 내부 오류 |
| `EXTERNAL_SERVICE_ERROR` | 502 | 외부 서비스 연동 오류 |

### 7.3 상태 전환 에러 예시

```json
{
  "error": {
    "code": "INVALID_STATUS_TRANSITION",
    "message": "현재 상태에서 요청한 상태로 전환할 수 없습니다.",
    "details": [
      {
        "field": "status",
        "message": "'cancelled' 상태에서 'shipping' 상태로 전환할 수 없습니다.",
        "current_status": "cancelled",
        "requested_status": "shipping",
        "allowed_transitions": []
      }
    ],
    "timestamp": "2026-04-06T10:30:00+09:00",
    "request_id": "req_xyz789ghi012"
  }
}
```

---

## 8. 요청/응답 헤더

### 8.1 요청 헤더

| 헤더 | 필수 | 설명 |
|------|------|------|
| `Authorization` | Y | `Bearer {jwt_token}` |
| `Content-Type` | Y (POST/PUT/PATCH) | `application/json` |
| `Accept` | N | `application/json` (기본값) |
| `Idempotency-Key` | N (POST 권장) | 멱등성 보장 키 (UUID) |
| `Accept-Language` | N | 응답 언어 (`ko`, `en`) |

### 8.2 응답 헤더

| 헤더 | 설명 |
|------|------|
| `X-Request-Id` | 요청 추적 ID |
| `X-RateLimit-Limit` | 분당 최대 허용 요청 수 |
| `X-RateLimit-Remaining` | 남은 요청 수 |
| `X-RateLimit-Reset` | 제한 초기화 시간 (Unix timestamp) |
| `Link` | 페이지네이션 링크 (RFC 5988) |

---

## 9. Django 모델 구조 (참고)

```python
from django.db import models
import uuid


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "주문 접수"
        CONFIRMED = "confirmed", "주문 확정"
        SHIPPING = "shipping", "배송 중"
        DELIVERED = "delivered", "배송 완료"
        CANCELLED = "cancelled", "주문 취소"
        REFUNDED = "refunded", "환불 완료"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=30, unique=True, db_index=True)
    customer = models.ForeignKey("Customer", on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    shipping_name = models.CharField(max_length=50)
    shipping_phone = models.CharField(max_length=20)
    shipping_zip_code = models.CharField(max_length=10)
    shipping_address = models.CharField(max_length=200)
    shipping_detail = models.CharField(max_length=100, blank=True)

    subtotal = models.PositiveIntegerField(default=0)
    shipping_fee = models.PositiveIntegerField(default=0)
    discount = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)

    payment_method = models.CharField(max_length=20)
    note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["customer", "-created_at"]),
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("Product", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    class Meta:
        unique_together = ["order", "product"]


class OrderHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="history")
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
```

---

## 10. Django URL 설정 (참고)

```python
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 주문 CRUD
    path("orders", views.OrderListCreateView.as_view()),
    path("orders/<uuid:order_id>", views.OrderDetailView.as_view()),

    # 주문 상태 변경
    path("orders/<uuid:order_id>/confirm", views.OrderConfirmView.as_view()),
    path("orders/<uuid:order_id>/cancel", views.OrderCancelView.as_view()),
    path("orders/<uuid:order_id>/ship", views.OrderShipView.as_view()),
    path("orders/<uuid:order_id>/deliver", views.OrderDeliverView.as_view()),
    path("orders/<uuid:order_id>/refund", views.OrderRefundView.as_view()),

    # 주문 항목
    path("orders/<uuid:order_id>/items", views.OrderItemListCreateView.as_view()),
    path("orders/<uuid:order_id>/items/<int:item_id>", views.OrderItemDetailView.as_view()),

    # 주문 이력
    path("orders/<uuid:order_id>/history", views.OrderHistoryListView.as_view()),
]
```

---

## 설계 원칙 요약

1. **RESTful 규칙 준수** -- 리소스 중심 URL, 적절한 HTTP 메서드 사용
2. **일관된 응답 형식** -- 목록은 `data` + `pagination`, 에러는 `error` 래퍼
3. **커서 기반 페이지네이션** -- 대규모 데이터에서 안정적인 성능
4. **상세한 에러 코드** -- HTTP 상태 코드 + 애플리케이션 에러 코드 이중 구조
5. **멱등성 보장** -- `Idempotency-Key` 헤더로 중복 주문 방지
6. **소프트 삭제** -- 주문 데이터는 물리 삭제하지 않고 `is_deleted` 플래그 사용
7. **상태 머신** -- 유효한 상태 전환만 허용하여 데이터 무결성 보장
8. **감사 추적** -- `OrderHistory`로 모든 상태 변경 이력 기록
