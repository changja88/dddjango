가능은 하지만, **주문 생성 로직을 전부 Django Ninja view에 넣는 것은 보통 권장하지 않습니다.** 특히 주문 생성은 대개 결제, 재고, 쿠폰, 배송지, 주문 상태, 트랜잭션, 중복 요청 방지 같은 규칙이 얽히기 쉽기 때문에 view가 빨리 비대해집니다.

Django Ninja 기준으로는 view는 보통 아래 정도에 머무는 게 좋습니다.

```python
@router.post("/orders")
def create_order(request, payload: CreateOrderIn):
    order = create_order_command(
        user=request.user,
        items=payload.items,
        shipping_address=payload.shipping_address,
        idempotency_key=request.headers.get("Idempotency-Key"),
    )
    return OrderOut.from_orm(order)
```

view가 담당하기 좋은 것:

- HTTP 요청/응답 처리
- 인증된 사용자 확인
- request schema 검증 결과 받기
- status code, response schema 결정
- header, query param, path param 처리

view 밖으로 빼는 게 좋은 것:

- 주문 가능 여부 판단
- 재고 차감
- 가격 계산
- 쿠폰/포인트 적용
- 결제 요청 또는 결제 예약
- `transaction.atomic()`
- 중복 주문 방지
- 주문 상태 전이
- 이벤트 발행, 알림 예약

서비스 레이어가 꼭 “거대한 Service 클래스”일 필요는 없습니다. Django에서는 단순 함수형 유스케이스가 더 나을 때도 많습니다.

```python
# orders/use_cases.py

@transaction.atomic
def create_order(*, user, items, shipping_address, idempotency_key=None):
    # validate business rules
    # calculate price
    # create order
    # create order lines
    # reserve/decrease stock
    # return order
```

다만 예외도 있습니다. 아래 정도라면 view에 직접 둬도 괜찮습니다.

- 단순 CRUD에 가깝다
- 도메인 규칙이 거의 없다
- 모델 하나 생성하고 끝난다
- 재사용 가능성이 낮다
- 트랜잭션 경계가 단순하다
- 테스트가 view 테스트만으로 충분하다

예를 들어 “메모 생성”, “배송 요청 초안 저장” 같은 수준이면 view 안에서 처리해도 됩니다. 하지만 **주문 생성**은 보통 단순 CRUD가 아니므로 분리하는 쪽이 낫습니다.

핵심 기준은 “서비스 레이어가 있어야 하느냐”가 아니라, **HTTP 관심사와 주문 도메인 규칙이 같은 이유로 바뀌는가**입니다. API 스펙 변경과 주문 정책 변경은 보통 다른 이유로 바뀝니다. 그래서 Django Ninja view에는 얇은 조율만 두고, 주문 생성 유스케이스는 별도 함수나 모듈로 분리하는 편이 테스트, 트랜잭션 관리, 재사용 면에서 더 안전합니다.