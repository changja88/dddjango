작업 디렉터리에 `config.toml`이 없어서 파일 기반 구현은 하지 못했고, DDD 기준 설계안으로 정리합니다.

**Bounded Context**
쿠폰은 `Coupon Context`로 분리하는 것이 좋습니다.

주요 책임:

- 쿠폰 정의
- 쿠폰 발급
- 쿠폰 사용 가능 여부 판단
- 할인 금액 계산
- 쿠폰 사용 처리

주문 금액, 상품, 회원 등은 외부 컨텍스트의 값만 참조하고 직접 소유하지 않습니다.

**Aggregate**
핵심 Aggregate는 `Coupon` 또는 `IssuedCoupon`입니다.

실무적으로는 다음처럼 나누는 편이 안전합니다.

```text
CouponPolicy
- 쿠폰 정책 정의
- 할인 방식
- 최소 주문 금액
- 중복 사용 가능 여부
- 유효 기간

IssuedCoupon
- 회원에게 발급된 쿠폰
- 사용 여부
- 사용 시점
```

`CouponPolicy`는 정책 템플릿이고, `IssuedCoupon`은 실제 사용 가능한 쿠폰 인스턴스입니다.

**Entity / Value Object**

```text
CouponPolicy
- id
- name
- discountPolicy
- minimumOrderAmount
- stackable
- validPeriod
- status

IssuedCoupon
- id
- couponPolicyId
- memberId
- used
- usedAt
```

Value Object:

```text
Money
- amount

DiscountPolicy
- FixedAmountDiscount
- RateDiscount

MinimumOrderAmount
- amount

ValidPeriod
- startsAt
- endsAt
```

**할인 정책**

```python
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    amount: Decimal

    def is_less_than(self, other: "Money") -> bool:
        return self.amount < other.amount

    def subtract(self, other: "Money") -> "Money":
        return Money(max(Decimal("0"), self.amount - other.amount))


class DiscountPolicy:
    def calculate(self, order_amount: Money) -> Money:
        raise NotImplementedError


@dataclass(frozen=True)
class FixedAmountDiscount(DiscountPolicy):
    amount: Money

    def calculate(self, order_amount: Money) -> Money:
        return Money(min(order_amount.amount, self.amount.amount))


@dataclass(frozen=True)
class RateDiscount(DiscountPolicy):
    rate: Decimal  # 예: 0.10 = 10%

    def calculate(self, order_amount: Money) -> Money:
        return Money(order_amount.amount * self.rate)
```

**CouponPolicy Aggregate**

```python
@dataclass
class CouponPolicy:
    id: str
    name: str
    discount_policy: DiscountPolicy
    minimum_order_amount: Money
    stackable: bool
    active: bool

    def validate_applicable(self, order_amount: Money):
        if not self.active:
            raise CouponNotApplicable("비활성화된 쿠폰입니다.")

        if order_amount.is_less_than(self.minimum_order_amount):
            raise CouponNotApplicable("최소 주문 금액을 충족하지 않았습니다.")

    def calculate_discount(self, order_amount: Money) -> Money:
        self.validate_applicable(order_amount)
        return self.discount_policy.calculate(order_amount)
```

**IssuedCoupon Aggregate**

```python
@dataclass
class IssuedCoupon:
    id: str
    coupon_policy_id: str
    member_id: str
    used: bool = False

    def use(self):
        if self.used:
            raise CouponAlreadyUsed("이미 사용된 쿠폰입니다.")
        self.used = True
```

**중복 사용 제한**
중복 사용 여부는 단일 쿠폰만 보면 판단할 수 없으므로 Domain Service로 분리하는 게 적절합니다.

```python
class CouponUsageService:
    def validate_stackable(self, policies: list[CouponPolicy]):
        non_stackable = [p for p in policies if not p.stackable]

        if len(policies) > 1 and non_stackable:
            raise CouponNotApplicable("중복 사용이 불가능한 쿠폰이 포함되어 있습니다.")
```

**사용 흐름**

```text
1. 주문 컨텍스트에서 주문 금액을 Coupon Context에 전달
2. IssuedCoupon 조회
3. CouponPolicy 조회
4. 쿠폰 소유자 확인
5. 사용 여부 확인
6. 최소 주문 금액 검증
7. 중복 사용 가능 여부 검증
8. 할인 금액 계산
9. IssuedCoupon.use()
10. CouponUsed 이벤트 발행
```

**Domain Event**

```text
CouponIssued
CouponUsed
CouponExpired
```

`CouponUsed` 이벤트는 주문 컨텍스트에서 결제 금액 확정, 회계/정산 컨텍스트에서 할인 내역 기록 등에 사용할 수 있습니다.

**핵심 규칙 요약**

- 정액 할인은 주문 금액보다 클 수 없고, 최대 할인액은 주문 금액으로 제한
- 정률 할인은 `rate`를 Value Object로 두고 `0 < rate <= 1` 검증
- 최소 주문 금액은 쿠폰 정책의 불변 규칙으로 관리
- 중복 사용 제한은 여러 쿠폰 조합을 봐야 하므로 Domain Service에서 판단
- 발급 쿠폰의 사용 여부는 `IssuedCoupon` Aggregate가 책임짐