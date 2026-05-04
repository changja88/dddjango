**리뷰 결론**

주문 생성 로직을 전부 Django Ninja view에 넣는 것은 “가능”하지만, 실서비스 기준으로는 보통 권장하지 않습니다. 주문 생성은 단순 CRUD가 아니라 재고 확인, 가격 스냅샷, 할인/쿠폰, 배송지 검증, 결제 준비, 중복 요청 방지, 트랜잭션, 도메인 예외 처리가 묶이는 유스케이스라서 view에 넣으면 금방 fat endpoint가 됩니다.

좋은 방향은 view를 HTTP 어댑터로 얇게 두는 것입니다. 즉 Django Ninja view는 요청 Schema 검증, 인증 사용자 확인, 헤더 읽기, 응답 status/schema 매핑 정도만 담당하고, 주문 생성 유스케이스는 `create_order(...)` 같은 application/service 함수로 분리하는 편이 낫습니다.

**주요 발견사항**

`[Fat endpoint]` -- 주문 생성 전체를 view에 넣으면 HTTP 관심사와 도메인 규칙이 섞입니다. 같은 주문 생성 로직을 관리자 액션, Celery task, 내부 배치, 다른 API 버전에서 재사용하기 어려워지고 테스트도 “API를 쏴야만 검증되는” 형태가 됩니다.

`[Transaction boundary]` -- 주문 생성은 보통 `Order`, `OrderLine`, 재고 차감, 쿠폰 사용, 결제 intent 생성 같은 여러 변경을 하나의 원자적 작업으로 묶어야 합니다. 이 경계는 view보다 service/use case 안에 두는 편이 명확합니다.

`[Idempotency]` -- `POST /orders`는 기본적으로 멱등하지 않습니다. 네트워크 재시도 때문에 같은 주문이 중복 생성될 수 있으므로, 주문 생성 API는 `Idempotency-Key` 처리를 고려해야 합니다. 이 로직도 view에 있으면 지저분해지고 레이스 컨디션 처리가 흩어지기 쉽습니다.

`[Domain invariants]` -- “판매 가능한 상품인가”, “가격은 주문 시점 기준으로 고정되는가”, “재고가 부족하면 어떤 예외인가”, “쿠폰은 언제 사용 처리되는가” 같은 규칙은 HTTP 계층의 규칙이 아닙니다. 서비스나 도메인 객체 쪽에 있어야 중복과 누락이 줄어듭니다.

`[Django Ninja convention]` -- Django Ninja endpoint는 `Schema`, 타입 힌트, `Router` 데코레이터, 명시적 response schema를 갖는 얇은 함수가 가장 다루기 좋습니다. 복잡한 생성 로직까지 endpoint 함수에 넣는 것은 관용적인 API 계층 분리와 맞지 않습니다.

**허용 가능한 경우**

아래 정도라면 view에 직접 넣어도 큰 문제는 아닙니다.

- 프로토타입 또는 throwaway 코드
- 주문이 실제 도메인 주문이 아니라 단일 모델 row 생성에 가까움
- 재고, 결제, 할인, 배송, 멱등성, 외부 호출이 없음
- 같은 로직을 다른 진입점에서 재사용할 가능성이 낮음

다만 “주문 생성”이라는 이름이 붙는 순간 대부분은 이 범위를 빨리 벗어납니다.

**추천 구조**

```python
# orders/api.py
@router.post("/orders", response={201: OrderOut, 409: ProblemDetail})
def create_order_endpoint(
    request,
    payload: CreateOrderIn,
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
):
    try:
        order = create_order(
            customer=request.user,
            command=payload.to_command(),
            idempotency_key=idempotency_key,
        )
    except OrderConflict as exc:
        return 409, problem_detail(exc)

    return 201, order
```

```python
# orders/services.py
@transaction.atomic
def create_order(
    *,
    customer: User,
    command: CreateOrderCommand,
    idempotency_key: str | None,
) -> Order:
    # validate customer/product/stock
    # lock inventory rows
    # snapshot prices
    # create order and lines
    # reserve stock / coupon / payment intent
    # store idempotency result
    return order
```

핵심은 “service layer를 무조건 만들자”가 아니라, **주문 생성이라는 유스케이스의 변경 이유를 HTTP view에서 분리하자**입니다. 단순 pass-through service는 의미가 없지만, 주문 생성처럼 규칙과 트랜잭션이 있는 작업은 service/use case 계층이 실제 복잡도를 숨기는 깊은 모듈이 됩니다.

---
> **관련 스킬 참조:**
> - Django Ninja API 구현 → **dddjango:implementation-django-ninja** 스킬
> - API 멱등성/상태 코드 설계 → **dddjango:architecture-api** 스킬
> - fat view 리팩토링/책임 분리 → **dddjango:implementation-cleancode** 스킬