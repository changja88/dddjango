Fixture 확인 결과, 케이스의 `fixture`가 `none`이고 `/Users/hyun/Desktop/dddjango/none` 경로도 존재하지 않아 실제 코드 라인 기준 리뷰는 할 수 없었습니다. 대신 주어진 상황 기준의 리뷰 findings로 정리합니다.

**Findings**

1. **High: Ninja router가 유스케이스와 도메인 규칙을 직접 소유함**
   
   Django Ninja router 함수 안에서 재고 차감, 쿠폰 계산, 결제 준비를 모두 처리하면 router가 transport layer 역할을 벗어납니다. router는 요청 Schema 검증, 인증 사용자 식별, application service 호출, 응답 Schema 변환, 예외 매핑 정도에 머무는 편이 좋습니다.

   개선 방향:
   ```python
   @router.post("/checkout", response={201: CheckoutOut, 400: ErrorOut})
   def checkout(request, payload: CheckoutIn):
       command = CheckoutCommand(
           user_id=request.user.id,
           items=payload.items,
           coupon_code=payload.coupon_code,
           idempotency_key=payload.idempotency_key,
       )
       result = checkout_service.checkout(command)
       return 201, CheckoutOut.from_result(result)
   ```

2. **High: 재고 차감이 동시성에 취약할 가능성이 큼**
   
   router에서 `product.stock -= quantity` 같은 방식으로 처리하면 동시에 주문이 들어올 때 초과 판매가 발생할 수 있습니다. 재고는 단순 차감보다 “예약/확정/해제” 흐름으로 모델링하고, DB 트랜잭션 안에서 `select_for_update()` 또는 조건부 `UPDATE ... WHERE stock >= quantity`로 보호해야 합니다.

   개선 방향:
   - `InventoryService.reserve(items, order_id)`로 분리
   - 트랜잭션 안에서 재고 검증과 예약 기록 생성
   - 중복 요청 방지를 위해 `idempotency_key` 저장
   - 결제 실패 시 예약 해제 또는 만료 처리

3. **High: 결제 준비와 DB 변경이 한 함수에 섞이면 실패 복구가 불명확함**
   
   재고 차감 후 결제 준비가 실패하면 재고를 되돌려야 하는지, 주문은 어떤 상태로 남는지, 쿠폰 사용은 롤백되는지 명확하지 않습니다. 특히 외부 PG 호출을 DB 트랜잭션 안에서 오래 붙잡으면 락 경합이 커질 수 있습니다.

   개선 방향:
   - 주문을 `PENDING_PAYMENT` 상태로 생성
   - 재고는 예약 상태로 잡음
   - 결제 준비는 `PaymentGateway` 포트로 감쌈
   - 결제 실패 시 예약 해제/주문 실패 처리
   - PG 호출에는 idempotency key 사용

4. **Medium: 쿠폰 계산 규칙이 흩어지고 테스트가 어려워짐**
   
   쿠폰 유효기간, 최소 주문 금액, 중복 사용 여부, 할인 한도, 할인 후 금액 0원 미만 방지 같은 규칙이 router에 들어가면 재사용과 테스트가 어려워집니다.

   개선 방향:
   ```python
   class CouponPolicy:
       def apply(self, subtotal: Money, coupon: Coupon | None, user: User) -> DiscountResult:
           ...
   ```

   작은 프로젝트라면 별도 policy class까지 만들지 않고 `CouponService.calculate_discount(...)` 정도로 시작해도 됩니다. 중요한 기준은 “Ninja router 밖에서 독립 테스트 가능해야 한다”는 점입니다.

5. **Medium: 변경 이유가 다른 코드가 한 곳에 모여 변경 범위가 커짐**
   
   재고 정책 변경, 쿠폰 정책 변경, PG 교체, 응답 포맷 변경은 서로 다른 이유로 바뀝니다. 그런데 모두 router 함수에 있으면 작은 정책 변경도 API 함수 전체를 건드리게 됩니다.

   개선 구조:
   ```text
   shop/orders/api.py                  # Django Ninja router
   shop/orders/application/checkout.py # CheckoutService, CheckoutCommand
   shop/orders/domain/coupon_policy.py # 쿠폰 계산 규칙
   shop/inventory/services.py          # 재고 예약/차감
   shop/payments/gateway.py            # 결제 준비 포트
   ```

6. **Medium: 테스트 범위가 API 테스트로 과도하게 몰림**
   
   비즈니스 로직이 router에 있으면 쿠폰 계산, 재고 부족, 결제 실패, 중복 요청 같은 케이스를 모두 HTTP 테스트로만 검증하게 됩니다. 느리고 원인 파악도 어렵습니다.

   개선 방향:
   - router 테스트: Schema validation, status code, 예외 매핑
   - application service 테스트: checkout 성공/실패 흐름
   - domain policy 테스트: 쿠폰 계산
   - inventory 테스트: 동시성/재고 부족
   - payment gateway는 mock/fake 사용

**권장 리팩터링 방향**

router는 얇게 두고 `CheckoutService`가 유스케이스를 조율하게 하세요. 다만 모든 것을 처음부터 DDD 디렉터리로 크게 쪼갤 필요는 없습니다. 현재 문제가 “router에 모든 로직이 몰림”이라면 1차 개선은 다음 정도면 충분합니다.

```python
class CheckoutService:
    def checkout(self, command: CheckoutCommand) -> CheckoutResult:
        with transaction.atomic():
            order = self.order_repository.create_pending(command.user_id)
            reserved_items = self.inventory_service.reserve(command.items, order.id)
            discount = self.coupon_policy.apply(command.coupon_code, reserved_items, command.user_id)
            order.set_total(reserved_items.total - discount.amount)
            self.order_repository.save(order)

        payment = self.payment_gateway.prepare(
            order_id=order.id,
            amount=order.total_amount,
            idempotency_key=command.idempotency_key,
        )
        return CheckoutResult(order=order, payment=payment)
```

핵심은 router를 “입출력 변환 계층”으로 제한하고, 재고/쿠폰/결제 각각의 변경 이유를 application service와 domain policy/port로 분리하는 것입니다. 단순한 기능이면 과도한 인터페이스를 만들지 말고, 먼저 `CheckoutService + CouponPolicy + InventoryService + PaymentGateway` 정도의 좁은 분리부터 시작하는 게 현실적입니다.