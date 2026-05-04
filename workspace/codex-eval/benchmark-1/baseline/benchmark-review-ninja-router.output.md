작업 디렉터리가 비어 있어 실제 파일/라인 기준 리뷰는 못 했습니다. 대신 “Django Ninja router 함수 안에서 재고 차감, 쿠폰 계산, 결제 준비를 모두 처리”하는 구조 자체를 기준으로 보면 핵심 문제는 명확합니다.

**주요 내용**

[Fat Endpoint] -- Router가 HTTP 입출력, 재고 정책, 쿠폰 정책, 결제 준비까지 모두 알고 있으면 API 계층이 유스케이스/도메인 계층을 침범합니다. Django Ninja router는 `Schema` 검증, 인증, 응답 변환, 예외 매핑 정도에 머물고, 주문 생성 흐름은 application service로 내려야 합니다.

[트랜잭션 경계 불명확] -- 재고 차감, 쿠폰 사용, 주문 생성, 결제 준비는 실패 지점이 다릅니다. 하나의 함수에서 순서대로 처리하면 중간 실패 시 “재고는 줄었는데 결제 준비 실패”, “쿠폰은 사용 처리됐는데 주문 실패” 같은 부분 완료 상태가 생기기 쉽습니다. DB 변경은 `transaction.atomic()` 안에서 묶고, 외부 결제 호출은 DB 트랜잭션 안에 오래 잡아두지 않는 방향이 낫습니다.

[동시성 위험] -- 재고 차감이 단순히 `product.stock -= qty; save()` 형태라면 동시 주문에서 oversell이 발생할 수 있습니다. `select_for_update()` 또는 조건부 `UPDATE ... WHERE stock >= qty` 방식으로 재고 불변식을 DB 레벨에서 보호해야 합니다.

[멱등성 누락] -- 결제 준비/주문 생성 POST는 네트워크 재시도, 프론트 중복 클릭, PG 콜백 재시도에 취약합니다. `Idempotency-Key`를 받아 같은 요청이 중복 처리되지 않도록 주문/결제 준비 결과를 재사용해야 합니다.

[DDD 경계 위반] -- 재고, 쿠폰, 결제는 각각 정책과 실패 모델이 다른 바운디드 컨텍스트 후보입니다. Router에서 직접 엮으면 컨텍스트 간 결합이 강해지고, 쿠폰 할인 규칙 변경이나 결제사 교체가 API 함수 수정으로 번집니다.

[도메인 규칙 위치 부적절] -- 쿠폰 할인 계산이 router 안에 있으면 테스트가 API 테스트로만 가능해집니다. `CouponPolicy`, `PricingService`, `Order.place()` 같은 도메인 객체/서비스로 분리해야 할인 한도, 중복 사용, 만료, 최소 주문 금액 같은 규칙을 단위 테스트할 수 있습니다.

[외부 결제 의존성 결합] -- 결제 준비 로직이 PG SDK를 router에서 직접 호출하면 장애 격리와 테스트가 어렵습니다. `PaymentGateway` 포트 인터페이스를 두고 인프라 구현체에서 PG를 호출하게 분리하는 편이 좋습니다.

[에러 응답 일관성 부족 가능성] -- 재고 부족, 쿠폰 불가, 결제 준비 실패는 각각 `409 Conflict`, `422 Unprocessable Entity`, `502/503` 계열로 구분될 수 있습니다. 커스텀 dict를 흩뿌리기보다 RFC 9457 Problem Details 형식으로 매핑하는 예외 핸들러를 두는 게 좋습니다.

개선 방향은 이렇게 잡는 게 현실적입니다.

```python
@router.post(
    "/orders",
    response={201: OrderCreatedOut},
    auth=auth,
)
def create_order(
    request: HttpRequest,
    payload: CreateOrderIn,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
) -> tuple[int, OrderCreatedOut]:
    result = order_checkout_service.prepare_order(
        customer_id=request.auth.id,
        command=CreateOrderCommand.from_schema(payload),
        idempotency_key=idempotency_key,
    )
    return 201, OrderCreatedOut.from_domain(result)
```

안쪽 구조는 다음처럼 분리하는 것을 권합니다.

```text
api/router.py
  - Schema 검증
  - 인증 사용자 식별
  - application service 호출
  - 응답/예외 변환

application/order_checkout_service.py
  - 유스케이스 조율
  - transaction.atomic()
  - repository 호출
  - 도메인 이벤트 기록

domain/order.py
  - 주문 불변식
  - 주문 생성/확정/취소 상태 전이

domain/coupon_policy.py
  - 쿠폰 적용 가능 여부
  - 할인 금액 계산

domain/inventory.py
  - 재고 예약/차감 불변식

infrastructure/payment_gateway.py
  - PG 결제 준비 호출
```

트랜잭션 흐름은 보통 이렇게 나눕니다.

```text
1. Idempotency-Key 확인
2. 상품/재고 row lock 또는 조건부 update
3. 쿠폰 유효성 검증 및 사용 예약
4. 주문 PENDING_PAYMENT 생성
5. 결제 준비 요청 생성 정보 저장
6. DB transaction commit
7. PG 결제 준비 호출
8. 성공 시 payment_ready 정보 저장, 실패 시 주문/예약 보상 처리
```

중요한 점은 “결제 완료 전 실제 재고 차감”보다 “재고 예약” 모델이 더 안전한 경우가 많다는 것입니다. 결제 실패/타임아웃/이탈을 고려해 `reserved_until`을 두고 만료된 예약을 해제하는 방식이 운영에서 다루기 쉽습니다.

테스트는 최소한 다음 케이스가 필요합니다.

```text
- 재고 부족이면 주문이 생성되지 않는다
- 동시 주문에서도 재고가 음수가 되지 않는다
- 쿠폰 만료/최소 주문 금액 미달/중복 사용을 거부한다
- 결제 준비 실패 시 주문 상태와 재고/쿠폰 예약 상태가 일관된다
- 같은 Idempotency-Key 재요청은 같은 주문/결제 준비 결과를 반환한다
```

요약하면, router 안의 절차형 코드를 “API 어댑터 → 주문 체크아웃 application service → 도메인 정책/애그리거트 → repository/payment gateway”로 분리하는 게 핵심입니다. 가장 먼저 할 일은 결제 호출을 포함한 긴 router 함수를 application service로 옮기고, 재고 차감과 쿠폰 계산을 각각 독립 테스트 가능한 도메인 정책으로 빼는 것입니다.

---
> **관련 스킬 참조:**
> - Django Ninja Router/Schema/API 에러 처리 → **implementation-django-ninja** 스킬
> - 주문/재고/쿠폰/결제 경계와 애그리거트 설계 → **architecture-ddd** 스킬
> - POST 멱등성, 상태 코드, Problem Details → **architecture-api** 스킬