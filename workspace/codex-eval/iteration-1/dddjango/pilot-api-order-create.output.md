**전제**

현재 `/private/tmp/dddjango-codex-eval` 디렉터리는 비어 있고 `config.toml`도 찾을 수 없었습니다. 그래서 기존 코드 스타일에 맞춘 파일 수정은 하지 않고, Django Ninja로 바로 옮길 수 있는 DDD 기준 설계로 제안합니다.

**추천 접근**

주문 생성은 `POST /v1/orders` 하나의 커맨드 API로 두고, 내부에서는 애플리케이션 서비스가 상품 조회, 재고 예약, 금액 계산, 결제 준비를 오케스트레이션합니다. 도메인 모델은 외부 결제사나 Django Ninja를 모르게 유지하고, 결제 준비는 `PaymentGatewayPort`를 통해 인프라 계층으로 격리합니다.

대안은 두 가지입니다. 첫째, 주문 생성과 결제 준비를 완전 동기로 처리하면 클라이언트가 단순하지만 결제사 장애에 취약합니다. 둘째, 주문만 만들고 결제 준비를 비동기로 처리하면 장애 내성이 좋지만 클라이언트가 폴링/웹훅을 다뤄야 합니다. 여기서는 “체크아웃 API”에 맞게 재고 예약과 결제 준비까지 동기 처리하되, 결제사 호출에는 provider idempotency key와 outbox/retry 기록을 남기는 방식을 추천합니다.

**API 계약**

`POST /v1/orders`

필수 헤더:

```http
Authorization: Bearer <token>
Idempotency-Key: <uuid-v4>
Content-Type: application/json
Accept: application/json
```

요청 본문:

```json
{
  "shipping_address_id": "addr_123",
  "items": [
    {"product_id": "prod_1", "quantity": 2},
    {"product_id": "prod_2", "quantity": 1}
  ],
  "coupon_code": "WELCOME10",
  "payment_method_type": "card",
  "return_url": "https://shop.example.com/orders/complete"
}
```

클라이언트는 `unit_price`, `line_total`, `total_amount`를 보내지 않습니다. 가격은 반드시 서버가 상품 가격 스냅샷으로 계산합니다.

성공 응답: `201 Created`

```http
Location: /v1/orders/ord_123
```

```json
{
  "id": "ord_123",
  "status": "payment_pending",
  "currency": "KRW",
  "items": [
    {
      "product_id": "prod_1",
      "product_name": "Keyboard",
      "quantity": 2,
      "unit_price": 50000,
      "line_total": 100000
    }
  ],
  "subtotal": 100000,
  "discount_total": 10000,
  "shipping_fee": 3000,
  "tax_total": 0,
  "total_amount": 93000,
  "payment": {
    "provider": "tosspayments",
    "payment_intent_id": "pi_123",
    "client_secret": "secret_abc",
    "expires_at": "2026-05-04T16:30:00+09:00"
  },
  "created_at": "2026-05-04T16:00:00+09:00"
}
```

**DDD 경계**

`orders` bounded context:

- `Order` aggregate root: 주문 상태 전이, 주문 라인, 총액 불변식 관리
- `OrderLine`: 상품명/단가/수량 가격 스냅샷 보관
- `Money`, `Quantity`, `OrderId`, `ProductId`: value object
- `OrderStatus`: `payment_pending`, `paid`, `cancelled`, `expired`
- 불변식: 주문 항목은 1개 이상, 수량은 양수, 총액은 라인 합계와 할인/배송비/세금 계산 결과와 일치

`inventory` bounded context:

- `StockItem` 또는 `InventoryReservation`
- 주문 생성 시 “재고 차감”보다 “재고 예약”을 먼저 수행
- 결제 성공 시 예약 확정, 결제 만료/취소 시 예약 해제
- 동시성은 DB row lock 또는 optimistic version으로 처리

`payments` bounded context:

- `PaymentPreparation` 또는 `PaymentIntent`
- 주문 생성 API에서는 결제 승인/매입이 아니라 결제 준비까지만 수행
- 실제 결제 완료는 결제사 웹훅으로 `paid` 전이

**애플리케이션 플로우**

1. 인증된 사용자와 `Idempotency-Key`를 검증합니다.
2. 같은 사용자, 같은 엔드포인트, 같은 키의 기존 결과가 있으면 저장된 응답을 반환합니다.
3. 같은 키에 다른 요청 본문이 들어오면 `409 Conflict`를 반환합니다.
4. 상품 목록을 조회하고 판매 가능 상태와 가격 스냅샷을 가져옵니다.
5. 재고를 잠그고 요청 수량만큼 예약 가능한지 확인합니다.
6. `PricingService`가 소계, 할인, 배송비, 세금, 총액을 계산합니다.
7. `Order` aggregate를 생성하고 재고 예약을 기록합니다.
8. 결제사에 payment intent/session을 생성합니다.
9. 주문 상태를 `payment_pending`으로 저장하고 `201 Created`를 반환합니다.

외부 결제사 호출은 도메인 모델 안에 넣지 않습니다. `CreateOrderService`가 `PaymentGatewayPort`를 호출하고, 인프라 어댑터가 실제 결제사 SDK/API를 담당합니다.

**Django Ninja 형태**

```python
router = Router(tags=["orders"], auth=AuthBearer())

@router.post(
    "",
    response={
        201: OrderCreatedOut,
        400: ProblemDetail,
        401: ProblemDetail,
        403: ProblemDetail,
        409: ProblemDetail,
        422: ProblemDetail,
        429: ProblemDetail,
        503: ProblemDetail,
    },
)
def create_order(
    request,
    payload: CreateOrderIn,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
) -> tuple[int, OrderCreatedOut]:
    command = CreateOrderCommand.from_request(
        user=request.auth,
        payload=payload,
        idempotency_key=idempotency_key,
    )
    result = create_order_service.handle(command)
    return 201, OrderCreatedOut.from_result(result)
```

스키마는 `Schema`를 사용하고, 모델 전체 필드 노출은 피합니다. 금액 필드는 정수 minor unit, 예를 들어 KRW면 원 단위 정수로 통일하는 편이 안전합니다.

**오류 설계**

모든 오류는 `application/problem+json` 형식으로 반환합니다.

재고 부족: `409 Conflict`

```json
{
  "type": "https://api.example.com/problems/insufficient-stock",
  "title": "Insufficient stock",
  "status": 409,
  "detail": "Requested quantity is not available.",
  "instance": "/v1/orders",
  "product_id": "prod_1",
  "requested_quantity": 3,
  "available_quantity": 1
}
```

주요 상태 코드:

- `400`: JSON 형식 오류, 잘못된 헤더
- `401`: 인증 없음 또는 토큰 오류
- `403`: 해당 배송지/고객으로 주문할 권한 없음
- `409`: 재고 부족, idempotency key 충돌, 동시성 충돌
- `422`: 빈 items, 중복 product_id, quantity 범위 오류, 판매 중지 상품
- `429`: 주문 생성 rate limit 초과
- `503`: 결제사 또는 재고 시스템 일시 장애

**권장 파일 구조**

```text
orders/
  api.py
  schemas.py
  application/
    create_order.py
    ports.py
  domain/
    models.py
    services.py
    events.py
  infrastructure/
    repositories.py
    payment_gateway.py

inventory/
  application/
  domain/
  infrastructure/

payments/
  api.py
  application/
  domain/
  infrastructure/
```

**테스트 기준**

핵심 테스트는 API보다 도메인/애플리케이션 서비스에 집중합니다.

- 빈 주문, 음수 수량, 중복 상품 검증
- 상품 가격이 클라이언트 입력 없이 서버 스냅샷으로 계산되는지
- 할인/배송비/세금 포함 총액 계산
- 재고 부족 시 주문과 결제 준비가 생성되지 않는지
- 동시 주문에서 oversell이 발생하지 않는지
- 같은 `Idempotency-Key` 재시도 시 같은 응답을 반환하는지
- 같은 키에 다른 본문이면 `409`인지
- 결제 준비 실패 시 예약 해제 또는 재시도 정책이 일관적인지
- 모든 오류가 RFC 9457 Problem Details 형식인지

---
> **관련 스킬 참조:**
> - Django Ninja Schema/Router 구현 → **implementation-django-ninja** 스킬
> - REST 상태 코드/멱등성/오류 형식 검토 → **architecture-api** 스킬
> - 주문 생성 테스트 작성 → **implementation-test** 스킬