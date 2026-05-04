**주요 내용**

가정: 쿠폰 할인 기준 금액은 `주문 상품 합계`이며 배송비와 결제 수단 할인은 제외합니다. 주문 컨텍스트의 `Order`를 쿠폰 모델 안으로 직접 들고 오지 않고, `OrderSnapshot` 값 객체로 필요한 금액과 주문자 ID만 전달합니다.

추천 설계는 `CouponPolicy`와 `CouponRedemption`을 분리하는 방식입니다. `CouponPolicy`는 “이 쿠폰이 어떤 할인 규칙을 가지는가”를 책임지고, `CouponRedemption`은 “누가 어떤 주문에 이 쿠폰을 실제로 사용했는가”를 책임집니다. 하나의 `Coupon` 애그리거트에 사용 이력 전체를 넣으면 중복 사용 제한은 쉬워 보이지만 애그리거트가 커지고 주문량 증가에 취약합니다.

**전략적 설계**

| 구분 | 설계 |
|---|---|
| 바운디드 컨텍스트 | `Coupon / Promotion Context` |
| 서브도메인 | 지원 또는 핵심. 개인화 프로모션이 경쟁력이라면 핵심, 단순 쿠폰이면 지원 |
| 주문 컨텍스트 관계 | `Customer-Supplier` + `Published Language`. 주문은 쿠폰 컨텍스트에 할인 가능 여부를 요청 |
| 고객 컨텍스트 관계 | `Conformist` 또는 `ACL`. 쿠폰은 고객 상세 객체 대신 `CustomerId`만 사용 |
| 결제 컨텍스트 관계 | 직접 연결하지 않음. 결제 실패/취소 이벤트를 통해 사용 예약을 해제 |

**유비쿼터스 언어**

| 도메인 용어 | 정의 | 코드 표현 | 금지 동의어 |
|---|---|---|---|
| 쿠폰 정책 | 쿠폰의 할인 방식과 사용 조건 | `CouponPolicy` | `CouponMaster`, `DiscountData` |
| 정액 할인 | 고정 금액을 차감하는 할인 | `FixedAmountDiscount` | `amount_type=1` |
| 정률 할인 | 주문 금액의 비율을 차감하는 할인 | `RateDiscount` | `percent`, `ratio_int` |
| 최소 주문 금액 | 쿠폰 적용에 필요한 주문 기준 금액 | `minimum_order_amount` | `min_price`, `threshold` |
| 중복 사용 제한 | 같은 주문 또는 고객에게 함께/반복 적용 가능한지에 대한 규칙 | `StackingPolicy`, `RedemptionPolicy` | `dup_yn`, `multi_use_flag` |
| 사용 예약 | 결제 전 쿠폰 사용권을 잠시 점유 | `reserve()` | `hold`, `lock_coupon` |
| 사용 확정 | 주문 확정 후 쿠폰 사용 완료 | `redeem()` | `consume`, `use_flag=Y` |
| 사용 해제 | 결제 실패/주문 취소로 예약을 취소 | `release()` | `rollback`, `undo` |

**애그리거트**

`CouponPolicy`가 할인 규칙의 Aggregate Root입니다.

불변식:
- 할인 규칙은 정액 또는 정률 중 하나여야 한다.
- 최소 주문 금액은 0 이상이어야 한다.
- 정률 할인은 0% 초과, 100% 이하여야 한다.
- 정액 할인은 0원 초과여야 한다.
- 중복 불가 쿠폰은 이미 적용된 다른 중복 불가 쿠폰과 함께 적용될 수 없다.
- 주문 금액이 최소 주문 금액보다 작으면 할인 견적을 만들 수 없다.

`CouponRedemption`이 사용 이력의 Aggregate Root입니다.

불변식:
- 같은 `coupon_policy_id + customer_id + order_id`는 한 번만 예약될 수 있다.
- `RESERVED -> REDEEMED` 또는 `RESERVED -> RELEASED`만 허용한다.
- 이미 확정된 사용 이력은 해제할 수 없다.
- 중복 사용 제한이 고객 단위라면 `coupon_policy_id + customer_id` 유니크 제약을 둔다.

**값 객체와 도메인 모델 스케치**

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
from uuid import UUID


class CouponDomainError(Exception): ...
class MinimumOrderAmountNotMet(CouponDomainError): ...
class CouponCannotBeStacked(CouponDomainError): ...
class InvalidDiscountPolicy(CouponDomainError): ...
class InvalidRedemptionTransition(CouponDomainError): ...


@dataclass(frozen=True, slots=True)
class Money:
    amount: int
    currency: str = "KRW"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise InvalidDiscountPolicy("금액은 0 이상이어야 합니다")
        if not self.currency:
            raise InvalidDiscountPolicy("통화는 필수입니다")

    def subtract_floor_zero(self, other: "Money") -> "Money":
        self._ensure_same_currency(other)
        return Money(max(0, self.amount - other.amount), self.currency)

    def _ensure_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise InvalidDiscountPolicy("통화가 다릅니다")


@dataclass(frozen=True, slots=True)
class DiscountRate:
    value: float

    def __post_init__(self) -> None:
        if self.value <= 0 or self.value > 1:
            raise InvalidDiscountPolicy("정률 할인은 0 초과 1 이하이어야 합니다")


@dataclass(frozen=True, slots=True)
class OrderSnapshot:
    order_id: UUID
    customer_id: UUID
    merchandise_total: Money
    applied_coupon_policy_ids: tuple[UUID, ...] = ()
```

```python
class StackingPolicy(Enum):
    EXCLUSIVE = "exclusive"
    STACKABLE = "stackable"


class DiscountRule(ABC):
    @abstractmethod
    def calculate(self, base_amount: Money) -> Money: ...


@dataclass(frozen=True, slots=True)
class FixedAmountDiscount(DiscountRule):
    amount: Money

    def __post_init__(self) -> None:
        if self.amount.amount <= 0:
            raise InvalidDiscountPolicy("정액 할인 금액은 0보다 커야 합니다")

    def calculate(self, base_amount: Money) -> Money:
        self.amount._ensure_same_currency(base_amount)
        return Money(min(self.amount.amount, base_amount.amount), base_amount.currency)


@dataclass(frozen=True, slots=True)
class RateDiscount(DiscountRule):
    rate: DiscountRate

    def calculate(self, base_amount: Money) -> Money:
        return Money(int(base_amount.amount * self.rate.value), base_amount.currency)
```

```python
@dataclass(frozen=True)
class CouponQuoted:
    coupon_policy_id: UUID
    order_id: UUID
    discount_amount: Money
    occurred_at: datetime = field(default_factory=datetime.now)


class AggregateRoot:
    def __init__(self) -> None:
        self._domain_events: list[object] = []

    def _record_event(self, event: object) -> None:
        self._domain_events.append(event)

    def collect_events(self) -> list[object]:
        events, self._domain_events = self._domain_events, []
        return events


@dataclass
class CouponPolicy(AggregateRoot):
    """Aggregate Root: 쿠폰 할인 조건의 일관성 경계.

    Invariants:
    - 최소 주문 금액 미만 주문에는 적용할 수 없다.
    - EXCLUSIVE 쿠폰은 다른 쿠폰과 함께 적용할 수 없다.
    - 할인액은 주문 상품 합계를 초과하지 않는다.
    """
    id: UUID
    code: str
    discount_rule: DiscountRule
    minimum_order_amount: Money
    stacking_policy: StackingPolicy
    version: int = 0

    def quote(self, order: OrderSnapshot) -> Money:
        if order.merchandise_total.amount < self.minimum_order_amount.amount:
            raise MinimumOrderAmountNotMet("최소 주문 금액을 충족하지 못했습니다")
        if self.stacking_policy == StackingPolicy.EXCLUSIVE and order.applied_coupon_policy_ids:
            raise CouponCannotBeStacked("중복 사용이 제한된 쿠폰입니다")

        discount = self.discount_rule.calculate(order.merchandise_total)
        self._record_event(CouponQuoted(self.id, order.order_id, discount))
        return discount
```

**사용 예약/확정 흐름**

```python
class RedemptionStatus(Enum):
    RESERVED = "reserved"
    REDEEMED = "redeemed"
    RELEASED = "released"


@dataclass(frozen=True)
class CouponReserved:
    redemption_id: UUID
    coupon_policy_id: UUID
    order_id: UUID
    customer_id: UUID
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class CouponRedeemed:
    redemption_id: UUID
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass
class CouponRedemption(AggregateRoot):
    """Aggregate Root: 쿠폰 사용 라이프사이클의 일관성 경계.

    Invariants:
    - 예약된 쿠폰만 사용 확정할 수 있다.
    - 예약된 쿠폰만 해제할 수 있다.
    - 확정된 사용 이력은 되돌리지 않는다.
    """
    id: UUID
    coupon_policy_id: UUID
    order_id: UUID
    customer_id: UUID
    discount_amount: Money
    status: RedemptionStatus = RedemptionStatus.RESERVED
    version: int = 0

    def redeem(self) -> None:
        if self.status != RedemptionStatus.RESERVED:
            raise InvalidRedemptionTransition("예약 상태에서만 사용 확정할 수 있습니다")
        self.status = RedemptionStatus.REDEEMED
        self._record_event(CouponRedeemed(self.id))

    def release(self) -> None:
        if self.status != RedemptionStatus.RESERVED:
            raise InvalidRedemptionTransition("예약 상태에서만 해제할 수 있습니다")
        self.status = RedemptionStatus.RELEASED
```

**리포지토리와 응용 서비스**

리포지토리는 도메인 계층에 ABC로 둡니다. 구현체는 Django ORM 어댑터에서 담당하고, `save()` 내부에서 `commit()`하지 않습니다. 트랜잭션은 Unit of Work 또는 응용 서비스 경계에서 관리합니다.

```python
class CouponPolicyRepository(ABC):
    @abstractmethod
    def find_by_code(self, code: str) -> CouponPolicy | None: ...

    @abstractmethod
    def save(self, policy: CouponPolicy) -> None: ...


class CouponRedemptionRepository(ABC):
    @abstractmethod
    def exists_active_for(self, coupon_policy_id: UUID, customer_id: UUID, order_id: UUID) -> bool: ...

    @abstractmethod
    def save(self, redemption: CouponRedemption) -> None: ...


class CouponApplicationService:
    def apply_coupon(self, code: str, order: OrderSnapshot) -> Money:
        policy = self._coupon_policies.find_by_code(code)
        if policy is None:
            raise CouponDomainError("쿠폰을 찾을 수 없습니다")

        if self._redemptions.exists_active_for(policy.id, order.customer_id, order.order_id):
            raise CouponCannotBeStacked("이미 사용 예약된 쿠폰입니다")

        discount = policy.quote(order)
        redemption = CouponRedemption.create_reserved(
            policy_id=policy.id,
            order_id=order.order_id,
            customer_id=order.customer_id,
            discount_amount=discount,
        )

        self._redemptions.save(redemption)
        self._coupon_policies.save(policy)
        return discount
```

핵심은 “할인 계산”과 “사용 이력”을 분리하는 것입니다. 정액/정률/최소 주문 금액은 `CouponPolicy` 내부 불변식이고, 중복 사용 제한은 `CouponPolicy.quote()`의 중복 적용 검증과 `CouponRedemptionRepository`의 활성 사용 이력 검증, 그리고 저장소의 유니크 제약으로 한 번 더 보호합니다.

---
> **관련 스킬 참조:**
> - DB 유니크 제약·인덱스·낙관적 잠금 설계 → **architecture-db** 스킬
> - Django ORM 매핑과 Repository 구현 → **implementation-django** 스킬
> - 쿠폰 적용 API 설계 → **architecture-api**, **implementation-django-ninja** 스킬