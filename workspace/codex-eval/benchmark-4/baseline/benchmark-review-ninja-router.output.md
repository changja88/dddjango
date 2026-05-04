**주요 내용**

저장소가 비어 있어 실제 코드 라인 기준 리뷰는 못 했습니다. 다만 “Django Ninja router 함수 안에서 재고 차감, 쿠폰 계산, 결제 준비를 모두 처리”하는 구조라면 핵심 문제는 꽤 명확합니다.

**Findings**

1. **[Fat Endpoint] -- 라우터가 유스케이스 조율과 도메인 규칙을 모두 떠안고 있음**  
   Django Ninja 라우터는 HTTP 요청/응답, Schema 검증, 인증, 상태 코드 매핑 정도에 머물러야 합니다. 재고 차감, 쿠폰 적용 가능 여부, 결제 준비 같은 업무 규칙이 라우터에 있으면 테스트가 API 테스트로만 몰리고, 같은 주문 생성 로직을 관리자/배치/메시지 컨슈머에서 재사용하기 어렵습니다.

2. **[Transaction Boundary] -- 재고 차감과 쿠폰 사용, 주문 생성이 원자적으로 보장되지 않을 가능성**  
   주문 준비 중 일부만 성공하면 재고는 줄었는데 결제 준비가 실패하거나, 쿠폰은 사용 처리됐는데 주문이 생성되지 않는 상태가 생깁니다. 최소한 주문 생성, 쿠폰 예약/사용, 재고 예약은 `transaction.atomic()` 안에서 명확한 순서와 롤백 정책을 가져야 합니다.

3. **[Concurrency] -- 재고 차감은 동시성 버그가 나기 쉬움**  
   단순히 `product.stock -= quantity; product.save()` 형태라면 동시 주문에서 음수 재고나 초과 판매가 발생할 수 있습니다. `select_for_update()`로 재고 행을 잠그거나, `F()` expression과 조건부 update로 `stock >= quantity`를 보장해야 합니다. 실패 시 `409 Conflict` 또는 `422 Unprocessable Entity`로 표준화하는 편이 좋습니다.

4. **[Idempotency] -- 결제 준비 POST가 재시도에 취약함**  
   결제 준비 API는 클라이언트/네트워크 재시도로 중복 호출될 가능성이 높습니다. 멱등성 키 없이 매번 재고 차감, 쿠폰 적용, payment intent 생성을 반복하면 중복 주문이나 중복 차감이 발생합니다. `Idempotency-Key`를 받아 같은 요청은 같은 주문/결제 준비 결과를 반환해야 합니다.

5. **[External IO in Transaction] -- 결제사 호출을 DB 트랜잭션 안에서 하면 위험함**  
   결제 준비가 외부 PG API 호출이라면 DB 락을 잡은 상태로 네트워크 I/O를 기다리게 됩니다. 반대로 트랜잭션 밖에서 먼저 호출하면 DB 저장 실패 시 결제 준비 객체만 남을 수 있습니다. 보통은 내부 주문/결제준비 레코드를 먼저 만들고 커밋한 뒤, 외부 결제 준비는 별도 단계 또는 outbox/task로 처리합니다.

6. **[Domain Boundary] -- 주문, 재고, 쿠폰, 결제가 한 애그리거트처럼 섞임**  
   DDD 관점에서는 주문, 재고, 쿠폰, 결제는 서로 다른 불변식을 가진 경계입니다. 하나의 라우터 함수에서 직접 모델들을 모두 수정하면 경계가 흐려지고 변경 영향이 커집니다. 라우터 → application service → domain service/repository 형태로 조율 책임을 분리하는 편이 낫습니다.

7. **[Error Format] -- 예외 처리가 비표준일 가능성**  
   재고 부족, 쿠폰 만료, 결제 준비 실패는 각각 의미가 다른 오류입니다. 문자열 `raise Exception`이나 임의 JSON 대신 RFC 9457 Problem Details 형태로 일관되게 내려야 클라이언트가 안정적으로 분기할 수 있습니다.

**개선 방향**

권장 구조는 라우터를 얇게 만들고, 주문 생성 유스케이스를 응용 서비스로 빼는 것입니다.

```python
@router.post("/orders", response={201: OrderCheckoutOut})
def create_order(request, payload: CreateOrderIn) -> tuple[int, OrderCheckoutOut]:
    result = checkout_service.prepare_checkout(
        customer_id=request.user.id,
        command=payload.to_command(),
        idempotency_key=request.headers.get("Idempotency-Key"),
    )
    return 201, OrderCheckoutOut.from_domain(result)
```

서비스 쪽 책임은 이렇게 나누는 게 좋습니다.

- `CheckoutApplicationService`: 주문 생성 흐름 조율, 트랜잭션 경계, 멱등성 처리
- `InventoryService` 또는 `InventoryRepository`: 재고 예약/차감, 락/조건부 update
- `CouponPolicy` 또는 `CouponService`: 쿠폰 적용 가능 여부와 할인 금액 계산
- `PaymentPreparationService`: 내부 결제 준비 레코드 생성, PG 호출 분리
- `Problem Details` 예외 매핑: `OutOfStock`, `CouponNotApplicable`, `PaymentPreparationFailed`

가장 먼저 고칠 부분은 재고 차감입니다. 음수 재고 방지와 중복 요청 방지를 테스트로 고정한 뒤, 라우터 로직을 서비스로 옮기면 구조 개선 효과가 큽니다.

---
> **관련 스킬 참조:**
> - Django Ninja 라우터/Schema/API 에러 정리 → **implementation-django-ninja** 스킬
> - 주문/재고/쿠폰/결제 경계 재설계 → **architecture-ddd** 스킬
> - 재고 차감 트랜잭션/락/인덱스 설계 → **architecture-db** 스킬