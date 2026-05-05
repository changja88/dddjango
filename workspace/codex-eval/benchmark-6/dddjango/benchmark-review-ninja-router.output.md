Fixture 확인 결과: `/Users/hyun/Desktop/dddjango/none` 경로가 존재하지 않고, `/private/tmp/dddjango-codex-eval`에도 읽을 fixture 파일이 없습니다. 따라서 파일/라인 기반 지적은 할 수 없고, 사용자가 설명한 구조에 대한 리뷰 findings로 답합니다.

**Review Findings**

1. **[Django Ninja: Router 책임 초과] -- 높음**  
   Router 함수가 재고 차감, 쿠폰 계산, 결제 준비를 모두 처리하면 transport layer가 유스케이스와 도메인 규칙까지 소유합니다. Router는 `Schema` 검증, 인증, HTTP 상태/에러 매핑, application service 호출까지만 담당해야 합니다. 지금 구조는 같은 주문 생성 로직을 CLI, admin action, celery task, 테스트에서 재사용하기 어렵습니다.

2. **[Transaction Boundary] -- 높음**  
   재고 차감과 쿠폰 사용은 DB 트랜잭션으로 묶어야 하지만, 결제 준비가 외부 PG 호출이면 같은 `transaction.atomic()` 안에 넣으면 안 됩니다. 롤백되어도 외부 호출은 되돌릴 수 없고, 반대로 외부 호출 실패 시 이미 재고가 차감될 수 있습니다. DB 상태 변경은 application service에서 원자적으로 처리하고, 외부 결제 준비는 `transaction.on_commit()` 또는 명시적 payment adapter 단계로 분리해야 합니다.

3. **[Domain Policy 누수] -- 중간**  
   쿠폰 할인 가능 조건, 최소 주문 금액, 중복 사용 제한, 재고 차감 가능 수량 같은 규칙이 Router 안에 있으면 API 입출력 코드와 비즈니스 정책이 함께 바뀝니다. `CouponPolicy`, `InventoryReservationPolicy`처럼 도메인 정책으로 분리하거나, 작은 기능이면 최소한 application service 내부 private 함수로 감춰야 합니다.

4. **[Concurrency / Idempotency] -- 중간**  
   주문 생성 POST는 재시도 가능성이 높습니다. `Idempotency-Key` 없이 재고 차감과 결제 준비가 실행되면 중복 주문, 중복 재고 차감, 중복 결제 준비가 발생할 수 있습니다. 재고는 `F()` update나 명시적 잠금/낙관적 버전으로 경쟁 조건을 막고, POST에는 idempotency 저장소를 둬야 합니다.

5. **[API Error Contract] -- 중간**  
   도메인 실패를 Router에서 `{"error": ...}` 식으로 직접 만들면 응답 형식이 흩어집니다. `OutOfStock`, `CouponNotApplicable`, `PaymentPreparationFailed` 같은 도메인/application 예외를 던지고, API boundary에서 RFC 9457 Problem Details로 매핑하는 편이 낫습니다.

**개선 방향 예시**

```diff
diff --git a/orders/api.py b/orders/api.py
--- a/orders/api.py
+++ b/orders/api.py
@@
+from django.http import HttpRequest
+from ninja import Router
+
+from .schemas import CheckoutIn, CheckoutOut
+from .services import checkout_order
+
 router = Router()
 
-@router.post("/checkout")
-def checkout(request, payload):
-    # 재고 차감 + 쿠폰 계산 + 결제 준비를 모두 처리
-    ...
+@router.post("/checkout", response={201: CheckoutOut})
+def checkout(request: HttpRequest, payload: CheckoutIn) -> tuple[int, CheckoutOut]:
+    result = checkout_order(
+        user=request.user,
+        command=payload.to_command(),
+        idempotency_key=request.headers.get("Idempotency-Key", ""),
+    )
+    return 201, CheckoutOut.from_result(result)
diff --git a/orders/services.py b/orders/services.py
new file mode 100644
--- /dev/null
+++ b/orders/services.py
@@
+from django.db import transaction
+
+def checkout_order(*, user, command, idempotency_key: str):
+    with transaction.atomic():
+        order = order_create(user=user, items=command.items)
+        discount = coupon_policy_apply(order=order, coupon_code=command.coupon_code)
+        inventory_reserve(order=order)
+        payment_request = payment_prepare_request(order=order, discount=discount)
+
+    transaction.on_commit(lambda: payment_prepare(payment_request))
+    return order
```

작은 기능이라면 Repository/UoW까지 바로 도입하지 않아도 됩니다. 기준은 단순합니다: 한 API에서만 쓰이고 DB 모델 1~2개만 건드리면 `services.py` 함수 + 모델 메서드로 충분합니다. 여러 API/배치에서 재사용되거나 재고, 쿠폰, 결제 규칙이 독립적으로 바뀌기 시작하면 application service와 domain policy를 명시적으로 분리하세요.

**Verification Steps**

- `python manage.py check`
- `pytest`
- 주문 재시도 테스트: 같은 `Idempotency-Key`로 두 번 호출해 재고가 한 번만 차감되는지 확인
- 결제 준비 실패 테스트: 실패 시 주문/재고/쿠폰 상태가 의도한 상태로 남는지 확인

---
> **관련 스킬 참조:**
> - Django Ninja API 분리 → **implementation-django-ninja** 스킬
> - application service / domain policy 경계 → **architecture-implementation-patterns** 스킬