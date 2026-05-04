[주요 내용]

실제 저장소에는 읽을 수 있는 코드가 없어 구조 기준으로 리뷰합니다. 설명한 형태라면 가장 큰 문제는 Django Ninja `Router` 함수가 transport layer를 넘어 use case, 도메인 규칙, 인프라 연동까지 모두 떠안고 있다는 점입니다.

| 문제 | 왜 위험한가 | 개선 방향 |
|---|---|---|
| [Django Ninja Convention] Fat endpoint | 라우터가 요청 파싱, 재고 차감, 쿠폰 계산, 결제 준비, 응답 조립을 모두 처리하면 테스트가 API 호출 중심으로만 가능해지고 변경 영향이 커집니다. | 라우터는 `Schema` 검증, 인증, application service 호출, 응답 변환만 담당하게 둡니다. |
| [DDD] 도메인 규칙 위치 불명확 | “쿠폰 적용 가능 조건”, “재고 차감 가능 수량”, “주문 금액 계산”이 라우터에 있으면 도메인 언어가 HTTP 코드에 묻히고 재사용이 어렵습니다. | `CouponPolicy`, `InventoryPolicy`, `Order` 같은 도메인 객체/정책으로 분리합니다. |
| [Architecture] 트랜잭션 경계가 흐림 | 재고 차감과 주문 생성은 DB 일관성이 필요한데, 결제 PG 호출까지 같은 라우터 흐름에 섞이면 실패 보상과 재시도가 모호해집니다. | application service가 `transaction.atomic()` 경계를 잡고, 외부 결제 준비는 adapter/outbox/on_commit 기준으로 분리합니다. |
| [Clean Code] 함수가 여러 추상화 수준을 섞음 | `payload` 파싱, ORM 업데이트, 할인 계산, PG 요청 생성이 한 함수에 있으면 “무엇을 하는 use case인지”보다 “어떻게 하는지”가 먼저 보입니다. | `prepare_checkout()`이라는 깊은 인터페이스 뒤에 세부 절차를 숨깁니다. |
| [API] 멱등성/오류 응답 누락 가능성 | 결제 준비 POST는 중복 호출될 수 있습니다. 재고가 두 번 차감되거나 쿠폰이 중복 사용될 수 있습니다. | `Idempotency-Key`를 받고, 재고 부족/쿠폰 불가/결제 준비 실패는 RFC 9457 Problem Details 형태로 매핑합니다. |

권장 구조는 이 정도면 충분합니다. 작은 기능이라도 “재고 + 쿠폰 + 결제”는 최소 3개 정책/외부 관심사를 조율하므로 service layer는 정당합니다. 다만 처음부터 완전한 헥사고날, CQRS, Saga까지 강제할 필요는 없습니다.

```python
# orders/api.py
router = Router(auth=django_auth)

@router.post("/checkouts", response={201: CheckoutPreparedOut})
def prepare_checkout(
    request,
    payload: CheckoutPrepareIn,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
):
    result = checkout_service.prepare(
        user_id=request.user.id,
        command=payload.to_command(),
        idempotency_key=idempotency_key,
    )
    return 201, CheckoutPreparedOut.from_result(result)
```

```python
# orders/application/services.py
class CheckoutApplicationService:
    def prepare(self, user_id: int, command: CheckoutCommand, idempotency_key: str):
        with transaction.atomic():
            order = Order.create(user_id=user_id, lines=command.lines)

            discount = self.coupon_policy.calculate(
                coupon_code=command.coupon_code,
                order=order,
            )
            order.apply_discount(discount)

            self.inventory_policy.reserve(order.lines)
            self.order_repository.save(order, idempotency_key=idempotency_key)

        return self.payment_preparer.prepare(order_id=order.id)
```

```python
# orders/domain/policies.py
class CouponPolicy:
    def calculate(self, coupon_code: str | None, order: Order) -> Money:
        ...

class InventoryPolicy:
    def reserve(self, lines: list[OrderLine]) -> None:
        ...
```

기준은 이렇게 잡으면 됩니다.

1. 라우터: HTTP, 인증, `Schema`, status code, service 호출만.
2. Application service: use case 조율, 트랜잭션 경계, repository/adapter 호출.
3. Domain policy/model: 쿠폰 계산, 금액 계산, 재고 예약 가능 여부 같은 비즈니스 규칙.
4. Infrastructure adapter: ORM repository, PG 결제 준비, 외부 API 호출.
5. 작은 기능 기준: 단일 모델 CRUD면 라우터+selector/service 함수 정도로 충분합니다. 여러 애그리거트나 외부 시스템이 얽히면 application service와 domain policy를 분리합니다.

검증은 다음이 핵심입니다.

```bash
python manage.py test orders.tests.test_checkout_service
python manage.py test orders.tests.test_checkout_api
```

테스트에는 재고 부족, 쿠폰 불가, 중복 `Idempotency-Key`, 결제 준비 실패, 동시 재고 차감 경쟁 조건을 포함해야 합니다.

---
> **관련 스킬 참조:**
> - Django Ninja Router/Schema 리팩터링 → **implementation-django-ninja** 스킬
> - application service와 domain policy 분리 → **architecture-implementation-patterns** 스킬
> - 주문·재고·쿠폰 도메인 규칙 모델링 → **architecture-ddd** 스킬