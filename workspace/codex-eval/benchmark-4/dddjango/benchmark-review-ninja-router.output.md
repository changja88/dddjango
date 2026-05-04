**리뷰 결과**

실제 저장소에는 router 코드가 없어 파일/라인 단위 리뷰는 못 했습니다. 현재 평가는 “Django Ninja router 함수 안에서 재고 차감, 쿠폰 계산, 결제 준비를 모두 처리한다”는 구조 기준입니다. 잘된 점은 하나 있습니다. 이 흐름은 “주문/체크아웃 준비”라는 명확한 유스케이스 경계가 보입니다. 다만 그 경계가 router 안에 들어간 것이 핵심 문제입니다.

[Convention: Fat Router] -- Django Ninja `Router`는 HTTP 요청/응답, 인증, Schema 검증, 상태 코드 매핑을 맡는 transport layer로 제한해야 합니다. 재고 차감, 쿠폰 할인, 결제 준비는 비즈니스 흐름이므로 router에 있으면 API 변경이 도메인 로직 변경으로 번지고, 같은 로직을 관리자/배치/이벤트 핸들러에서 재사용하기 어렵습니다.

[Pattern: Application Service 부재] -- 재고, 쿠폰, 결제는 여러 도메인 객체와 외부 시스템을 조율하는 use case입니다. 이 조율은 `CheckoutApplicationService` 같은 application service가 가져야 합니다. router는 `service.prepare_checkout(command)`를 호출하고 결과를 응답 Schema로 변환하는 정도가 적절합니다.

[DDD: Domain Policy 누락] -- 쿠폰 계산 규칙은 `CouponPolicy`, 재고 예약/차감 규칙은 `StockPolicy` 또는 `StockItem.reserve()` 같은 도메인 메서드로 분리해야 합니다. router에 `if coupon.type == ...`, `if stock < qty ...`가 들어가면 정책 변경 시 API 함수가 계속 커지고 테스트도 transport fixture에 묶입니다.

[Transaction Boundary] -- 재고 차감과 주문/결제 준비 상태 저장이 같은 트랜잭션 경계에 있어야 하는데, router에서 직접 처리하면 `transaction.atomic()` 범위와 외부 PG 호출 시점이 흐려집니다. 특히 DB 커밋 전 PG 호출은 결제는 준비됐는데 주문 저장이 실패하는 불일치를 만들 수 있습니다. 외부 결제 준비는 커밋 후 `transaction.on_commit()` 또는 outbox로 넘기는 기준을 세워야 합니다.

[Concurrency] -- 재고 차감은 레이스 컨디션에 취약합니다. 단순히 `product.stock -= qty; product.save()`를 router에서 수행하면 동시 요청에서 음수 재고가 발생할 수 있습니다. Django ORM에서는 최소한 `F()` expression, 조건부 update, 낙관적 잠금, 또는 핫 아이템이면 의도적인 `select_for_update()`가 필요합니다.

[API Design: Idempotency] -- 주문/결제 준비 POST는 비멱등 경로입니다. 네트워크 재시도 시 재고가 두 번 차감되거나 쿠폰이 중복 사용될 수 있습니다. `Idempotency-Key` 헤더를 받아 dedup 테이블 또는 요청 기록으로 같은 요청을 한 번만 처리해야 합니다.

개선 방향은 이 정도 구조가 적절합니다.

```python
# api.py
router = Router(tags=["checkout"])

@router.post("/checkouts", response={201: CheckoutOut})
def prepare_checkout(request, payload: CheckoutIn) -> tuple[int, CheckoutOut]:
    command = PrepareCheckoutCommand.from_schema(
        user_id=request.user.id,
        payload=payload,
        idempotency_key=request.headers.get("Idempotency-Key"),
    )
    result = checkout_service.prepare(command)
    return 201, CheckoutOut.from_result(result)
```

```python
# application/services.py
class CheckoutApplicationService:
    def prepare(self, command: PrepareCheckoutCommand) -> CheckoutResult:
        with transaction.atomic():
            order = self.orders.create_draft(command.user_id, command.items)
            discount = self.coupon_policy.calculate(order, command.coupon_code)
            self.stock_service.reserve(order.lines)
            order.apply_discount(discount)
            self.orders.save(order)

            transaction.on_commit(
                lambda: self.payment_gateway.prepare(order.id, order.total)
            )

        return CheckoutResult(order_id=order.id, amount=order.total)
```

작은 기능에서는 과하게 쪼개지 않아도 됩니다. 기준은 간단합니다. 단일 모델 CRUD이거나 규칙이 거의 없으면 router + selector/service 함수 하나로 충분합니다. 하지만 지금처럼 재고, 쿠폰, 결제처럼 변경 이유가 다른 책임이 섞이고 트랜잭션/외부 I/O/동시성이 함께 등장하면 application service와 domain policy 분리가 필요합니다.

검증 단계는 다음을 권합니다.

```bash
pytest tests/application/test_checkout_service.py
pytest tests/api/test_checkout_api.py
pytest tests/domain/test_coupon_policy.py
pytest tests/domain/test_stock_reservation.py
```

추가로 동시 재고 차감 테스트와 `Idempotency-Key` 재시도 테스트를 반드시 넣어야 합니다.

---
> **관련 스킬 참조:**
> - Django Ninja Router/Schema 분리 → **implementation-django-ninja** 스킬
> - application service와 domain policy 분리 → **architecture-implementation-patterns** 스킬
> - 재고/쿠폰/결제 도메인 규칙 모델링 → **architecture-ddd** 스킬