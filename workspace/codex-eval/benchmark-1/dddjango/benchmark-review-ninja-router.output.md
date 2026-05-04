실제 코드가 없어서 라인 단위 리뷰는 못 하지만, 설명한 구조만으로도 핵심 문제는 분명합니다. 주문 생성처럼 “재고 차감 + 쿠폰 계산 + 결제 준비”가 한 유스케이스로 묶이는 것은 자연스럽지만, 그 세부 로직이 Django Ninja router 함수 안에 직접 들어가면 API 계층이 도메인, 트랜잭션, 외부 결제 인프라까지 모두 떠안게 됩니다.

**주요 리뷰**

잘된 점부터 보면, 이 로직을 하나의 요청 흐름에서 처리하려는 의도 자체는 맞습니다. 사용자는 “주문/결제 준비”라는 하나의 API를 호출하고 싶어 하지, 재고 API, 쿠폰 API, 결제 API를 따로 조합하고 싶어 하지는 않습니다. 문제는 유스케이스의 조율 위치가 router 함수라는 점입니다.

[Convention: Fat endpoint] -- Django Ninja router는 요청 Schema 검증, 인증, 응답 변환, 응용 서비스 호출 정도만 담당해야 합니다. router 안에서 재고 차감, 쿠폰 규칙, 결제 준비를 직접 처리하면 표현 계층이 비즈니스 규칙을 소유하게 되어 테스트와 변경이 어려워집니다.

[Principle: 단일 책임 위반] -- 재고 차감은 Inventory 관심사, 쿠폰 계산은 Promotion 관심사, 결제 준비는 Payment 관심사입니다. 한 함수가 세 결정을 모두 알면 쿠폰 정책 변경, 재고 정책 변경, PG 연동 변경이 모두 API 함수 변경으로 번집니다.

[DDD: 바운디드 컨텍스트 혼합] -- `Order`, `Inventory`, `Coupon/Promotion`, `Payment`는 서로 다른 모델 언어와 불변식을 가질 가능성이 높습니다. 하나의 router 함수가 이 컨텍스트의 내부 모델을 모두 만지는 구조는 경계를 흐립니다.

[DDD: 애그리거트 경계 과대화] -- 주문 생성 시 여러 애그리거트를 한 트랜잭션에서 직접 수정하면 락 범위가 커지고 결합도가 높아집니다. 특히 `Order`, `InventoryReservation`, `CouponRedemption`, `PaymentIntent`는 각각 별도 애그리거트 후보입니다.

[DB: 동시성 위험] -- “재고 확인 후 차감”을 일반 조회와 저장으로 구현하면 overselling이 발생할 수 있습니다. 재고는 `select_for_update()` 또는 `F()` 기반 조건부 update처럼 원자적 방식으로 보호해야 합니다. 여러 상품을 잠글 때는 항상 같은 순서로 잠가 데드락 가능성을 낮춰야 합니다.

[API: 멱등성 누락 위험] -- 주문/결제 준비 POST는 네트워크 재시도 시 중복 주문, 중복 재고 차감, 중복 결제 intent 생성을 만들 수 있습니다. `Idempotency-Key`를 받아 첫 응답을 저장하고 같은 키의 재요청에는 같은 결과를 반환해야 합니다.

[Transaction: 외부 결제 호출 위치] -- PG 결제 준비 API 호출을 DB 트랜잭션 안에서 직접 수행하면 트랜잭션이 외부 네트워크 지연에 묶입니다. DB 커밋 후 실행해야 하는 외부 부수효과는 `transaction.on_commit()` 또는 outbox/event handler로 분리하는 쪽이 안전합니다.

[Error handling: 도메인 예외 부재] -- `raise Exception`, `return {"error": ...}` 같은 방식이면 클라이언트가 실패 원인을 안정적으로 처리하기 어렵습니다. `OutOfStockError`, `InvalidCouponError`, `PaymentPreparationFailedError` 같은 도메인 예외를 만들고 Django Ninja exception handler에서 RFC 9457 Problem Details로 변환하는 구조가 좋습니다.

**개선 방향**

router는 얇게 두고, 유스케이스는 응용 서비스로 옮기세요.

```python
@router.post(
    "/orders",
    response={201: OrderCheckoutResponse},
    auth=django_auth,
)
def create_order(
    request,
    payload: CreateOrderRequest,
    idempotency_key: IdempotencyKeyHeader,
) -> tuple[int, OrderCheckoutResponse]:
    result = checkout_service.prepare_checkout(
        command=PrepareCheckoutCommand(
            customer_id=request.user.id,
            items=payload.items,
            coupon_code=payload.coupon_code,
            idempotency_key=idempotency_key,
        )
    )
    return 201, OrderCheckoutResponse.from_result(result)
```

응용 서비스는 유스케이스를 조율하되, 규칙 자체는 도메인 객체/도메인 서비스에 위임합니다.

```python
class CheckoutApplicationService:
    def prepare_checkout(self, command: PrepareCheckoutCommand) -> CheckoutResult:
        return self._idempotency.run_once(
            key=command.idempotency_key,
            operation=lambda: self._prepare_checkout(command),
        )

    def _prepare_checkout(self, command: PrepareCheckoutCommand) -> CheckoutResult:
        with transaction.atomic():
            order = self._order_factory.create(command.customer_id, command.items)
            discount = self._discount_service.calculate(order, command.coupon_code)

            order.apply_discount(discount)
            reservation = self._inventory_service.reserve(order.lines)
            payment = self._payment_service.create_pending_intent(order.payable_amount)

            self._orders.save(order)
            self._inventory_reservations.save(reservation)
            self._payments.save(payment)

            transaction.on_commit(
                lambda: self._event_bus.publish_all(order.collect_domain_events())
            )

        return CheckoutResult(order_id=order.id, payment_id=payment.id)
```

도메인 모델 기준으로는 이렇게 나누는 편이 자연스럽습니다.

| 용어 | 권장 소유 컨텍스트 | 금지 동의어/주의 |
|---|---|---|
| `Order` | Ordering/Sales | payment나 inventory 상태를 직접 소유하지 않기 |
| `InventoryReservation` | Inventory | 단순 `stock -= qty`를 주문 로직에 흩뿌리지 않기 |
| `CouponRedemption` | Promotion | router에서 할인 금액 직접 계산하지 않기 |
| `PaymentIntent` | Payment | DB 트랜잭션 안에서 PG 네트워크 호출하지 않기 |

Aggregate Root와 불변식은 명시하세요.

```python
@dataclass
class Order:
    """Aggregate Root.

    Invariants:
    - 주문 항목은 1개 이상이어야 한다.
    - 할인 후 결제 금액은 0보다 작을 수 없다.
    - 결제 준비 전 주문 금액은 확정되어야 한다.
    """
    id: OrderId
    customer_id: CustomerId
    lines: list[OrderLine]
    _events: list[object] = field(default_factory=list)

    def apply_discount(self, discount: Money) -> None:
        ...
```

값 객체는 불변으로 두고 검증을 내부에 넣으세요.

```python
@dataclass(frozen=True)
class Money:
    amount: int
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise InvalidMoneyError("Money cannot be negative")
```

이벤트는 과거형으로 이름 붙입니다.

```python
@dataclass(frozen=True)
class OrderPlacedEvent:
    order_id: OrderId
    customer_id: CustomerId


@dataclass(frozen=True)
class InventoryReservedEvent:
    order_id: OrderId
    reservation_id: InventoryReservationId


@dataclass(frozen=True)
class PaymentIntentCreatedEvent:
    order_id: OrderId
    payment_intent_id: PaymentIntentId
```

정리하면, API는 “주문 결제 준비 요청을 받는다”까지만 알고, 실제 흐름은 `CheckoutApplicationService`가 조율해야 합니다. 재고, 쿠폰, 결제는 각각 도메인 서비스나 애그리거트로 분리하고, 재고 차감은 원자적 DB 갱신으로 보호하며, 결제/주문 POST에는 멱등성 키와 표준 오류 응답을 붙이는 방향이 좋습니다.

---
> **관련 스킬 참조:**
> - Django Ninja router/API 구현 → **implementation-django-ninja** 스킬
> - 주문/재고/쿠폰/결제 경계 설계 → **architecture-ddd** 스킬
> - 트랜잭션/락/재고 동시성 → **architecture-db** 스킬
> - Fat endpoint 리팩터링 → **implementation-cleancode** 스킬