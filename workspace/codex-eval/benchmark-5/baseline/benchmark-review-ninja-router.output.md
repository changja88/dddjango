지정 경로 `/Users/hyun/Desktop/dddjango/none`은 없어서, 실제 fixture인 `/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop`를 읽고 리뷰했습니다. fixture에는 쿠폰/결제 준비 코드는 없지만, 같은 문제 유형인 재고 예약 로직이 HTTP 함수 안에 섞여 있습니다.

**Findings**

1. [views.py](/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/shop/orders/views.py:21)의 `reserve_inventory`가 transport layer를 넘어 유스케이스를 직접 수행합니다.  
   요청 파싱, idempotency header 읽기, DB row lock, 재고 검증, 재고 차감, 예약 생성, HTTP 응답 생성이 한 함수에 있습니다. 쿠폰 계산과 결제 준비까지 같은 router 함수에 들어가면 주문 생성 유스케이스의 변경 이유가 모두 API 파일로 몰립니다. 쿠폰 정책 변경, 결제 PG 변경, 재고 동시성 변경이 전부 router 수정을 요구하게 됩니다.

2. [views.py](/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/shop/orders/views.py:28)의 트랜잭션 경계가 API 계층에 박혀 있습니다.  
   `transaction.atomic()`과 `select_for_update()` 자체는 필요할 수 있지만, 어디까지 원자적으로 묶을지는 주문/재고 예약 유스케이스의 정책입니다. router가 이 결정을 가지면 API 외부에서 같은 기능을 재사용하기 어렵고, 테스트도 HTTP 또는 Django view 중심으로만 흘러갑니다.

3. [views.py](/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/shop/orders/views.py:31)의 재고 규칙이 `Product` 바깥에 새고 있습니다.  
   `product.stock_quantity < quantity`, `product.stock_quantity -= quantity`처럼 내부 필드를 직접 조작합니다. 재고 차감 가능 여부, 수량 검증, 비활성 상품 처리, 예약 중복 처리 같은 불변식이 늘어나면 호출부마다 같은 규칙을 반복하게 됩니다.

4. [views.py](/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/shop/orders/views.py:26)와 [models.py](/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/shop/orders/models.py:45)의 idempotency가 이름만 있고 보장되지 않습니다.  
   `idempotency_key`를 저장하지만 unique constraint나 “이미 처리된 요청이면 기존 예약 반환” 흐름이 없습니다. 동일 요청 재시도 시 재고가 중복 차감될 수 있습니다.

5. [views.py](/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/shop/orders/views.py:23)의 입력 검증과 오류 표준이 취약합니다.  
   `payload["product_id"]`, `int(payload["quantity"])`, `Order.objects.get()` 실패가 그대로 예외로 터집니다. Django Ninja라면 `Schema`로 요청 검증을 맡기고, 도메인 예외를 API 계층에서 400/404/409 같은 표준 응답으로 변환하는 편이 맞습니다.

6. [api_drf.py](/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/shop/orders/api_drf.py:1)에 DRF 구현이 남아 있습니다.  
   프로젝트 기준이 Django Ninja라면 `rest_framework` serializer/APIView는 제거하거나 Ninja `Schema`/`Router`로 전환해야 합니다.

**개선 방향**

router는 얇게 두고 책임을 이렇게 나누는 것이 좋습니다.

- `api/router.py`: Django Ninja `Router`, request/response `Schema`, 인증, HTTP status 매핑
- `application/services.py`: `ReserveInventoryService`, `CreateOrderCheckoutService` 같은 유스케이스 조율
- `domain`: 재고 차감 규칙, 쿠폰 할인 정책, 주문 금액 계산 같은 비즈니스 규칙
- `infrastructure/repositories.py`: Django ORM 조회, `select_for_update()`, 저장, idempotency 조회

예시 흐름은 이 정도가 적절합니다.

```python
@router.post("/{order_id}/reservations", response={201: ReservationOut, 409: ErrorOut})
def reserve_inventory(request, order_id: int, payload: ReserveInventoryIn):
    command = ReserveInventoryCommand(
        order_id=order_id,
        product_id=payload.product_id,
        quantity=payload.quantity,
        idempotency_key=request.headers.get("Idempotency-Key", ""),
    )
    result = reserve_inventory_service().reserve(command)
    return 201, ReservationOut.from_result(result)
```

핵심은 router가 “무엇을 호출할지”만 알고, “재고를 어떻게 차감하고 쿠폰을 어떻게 계산하며 결제를 어떤 순서로 준비할지”는 application service가 소유하게 하는 것입니다. 다만 단순 CRUD나 조회 API까지 억지로 service를 만들 필요는 없습니다. 지금처럼 재고, 쿠폰, 결제, 트랜잭션, idempotency가 함께 등장하는 쓰기 유스케이스는 분리할 가치가 충분합니다.