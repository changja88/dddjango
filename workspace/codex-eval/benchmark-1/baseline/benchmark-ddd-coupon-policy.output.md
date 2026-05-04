현재 `/private/tmp/dddjango-codex-eval`에는 `config.toml`이나 소스 파일이 보이지 않아 코드 수정은 하지 못했습니다. 대신 DDD 기준으로 쿠폰 정책 도메인 설계를 정리합니다.

**Bounded Context**
쿠폰은 `Coupon` 컨텍스트로 분리하는 게 적절합니다.

주요 책임:

- 쿠폰 발급/조회
- 쿠폰 사용 가능 여부 판단
- 할인 금액 계산
- 쿠폰 사용 처리
- 중복 사용 제한 검증

주문 생성 자체는 `Order` 컨텍스트의 책임이고, 쿠폰 컨텍스트는 “이 주문에 이 쿠폰을 적용할 수 있는가?”와 “얼마를 할인하는가?”만 책임집니다.

**Aggregate**
핵심 Aggregate Root는 `Coupon`입니다.

```text
Coupon
- id
- code
- discount_policy
- minimum_order_amount
- stacking_policy
- usage_limit_policy
- valid_period
- status
```

쿠폰 사용 이력은 별도 Aggregate로 두는 편이 좋습니다.

```text
CouponRedemption
- id
- coupon_id
- user_id
- order_id
- discounted_amount
- redeemed_at
```

`Coupon` 하나에 사용 이력을 전부 포함하면 사용량이 커질수록 Aggregate가 비대해집니다. 따라서 사용 가능 여부 판단 시 Repository나 Domain Service가 사용 이력을 조회하도록 분리합니다.

**Value Objects**

```text
Money
- amount
- currency

DiscountPolicy
- FixedAmountDiscount
- RateDiscount

MinimumOrderAmount
- amount

StackingPolicy
- exclusive
- stackable

ValidPeriod
- starts_at
- ends_at
```

할인 정책은 정액/정률을 다형성으로 분리합니다.

```python
class DiscountPolicy:
    def calculate(self, order_amount: Money) -> Money:
        raise NotImplementedError


class FixedAmountDiscount(DiscountPolicy):
    def __init__(self, amount: Money):
        self.amount = amount

    def calculate(self, order_amount: Money) -> Money:
        return min(self.amount, order_amount)


class RateDiscount(DiscountPolicy):
    def __init__(self, rate: Decimal, max_discount: Money | None = None):
        self.rate = rate
        self.max_discount = max_discount

    def calculate(self, order_amount: Money) -> Money:
        discount = order_amount * self.rate
        if self.max_discount:
            return min(discount, self.max_discount)
        return discount
```

**Domain Rules**

쿠폰 적용 가능 조건은 다음처럼 도메인 규칙으로 둡니다.

```text
Coupon.apply(order_snapshot, user_coupon_context)

검증:
1. 쿠폰이 활성 상태인가
2. 유효 기간 안인가
3. 주문 금액이 최소 주문 금액 이상인가
4. 이미 사용한 쿠폰인가
5. 중복 사용 제한에 위배되지 않는가
6. 할인 금액이 주문 금액을 초과하지 않는가
```

주문 전체 객체를 직접 넘기기보다는 쿠폰 도메인에 필요한 값만 담은 Snapshot을 넘기는 편이 결합도가 낮습니다.

```python
@dataclass(frozen=True)
class OrderCouponSnapshot:
    order_id: str
    user_id: str
    total_amount: Money
    applied_coupon_ids: list[str]
```

**Coupon Aggregate 예시**

```python
class Coupon:
    def calculate_discount(
        self,
        order: OrderCouponSnapshot,
        redemption_context: CouponRedemptionContext,
    ) -> Money:
        self._validate_applicable(order, redemption_context)
        return self.discount_policy.calculate(order.total_amount)

    def _validate_applicable(
        self,
        order: OrderCouponSnapshot,
        context: CouponRedemptionContext,
    ) -> None:
        if not self.status.is_active():
            raise CouponNotActive()

        if not self.valid_period.includes(context.now):
            raise CouponExpired()

        if order.total_amount < self.minimum_order_amount:
            raise MinimumOrderAmountNotMet()

        if context.has_user_already_used_coupon:
            raise CouponAlreadyUsed()

        if self.stacking_policy.is_exclusive and order.applied_coupon_ids:
            raise CouponCannotBeStacked()
```

**중복 사용 제한**
중복 사용 제한은 두 종류로 나누는 게 명확합니다.

```text
1. 동일 쿠폰 재사용 제한
   - 한 사용자가 같은 쿠폰을 한 번만 사용할 수 있음

2. 주문 내 중복 적용 제한
   - exclusive 쿠폰이면 다른 쿠폰과 함께 적용 불가
   - stackable 쿠폰이면 허용
```

정책 객체로 표현하면 확장하기 쉽습니다.

```python
class StackingPolicy:
    def __init__(self, stackable: bool):
        self.stackable = stackable

    def validate(self, already_applied_coupon_ids: list[str]) -> None:
        if not self.stackable and already_applied_coupon_ids:
            raise CouponCannotBeStacked()
```

**Domain Service**
사용 이력, 주문 내 쿠폰 조합 검증처럼 여러 Aggregate가 필요한 판단은 Domain Service에 둡니다.

```text
CouponApplicationService  # Application Service
  -> CouponRepository
  -> CouponRedemptionRepository
  -> CouponApplicabilityChecker  # Domain Service
```

```python
class CouponApplicabilityChecker:
    def check(
        self,
        coupon: Coupon,
        order: OrderCouponSnapshot,
        redemption_context: CouponRedemptionContext,
    ) -> Money:
        return coupon.calculate_discount(order, redemption_context)
```

**Application Flow**

```text
ApplyCouponUseCase
1. 주문 스냅샷 조회
2. 쿠폰 조회
3. 사용 이력 조회
4. CouponRedemptionContext 생성
5. Coupon.calculate_discount(...)
6. 주문 컨텍스트에 할인 적용 요청
```

쿠폰 컨텍스트가 주문을 직접 변경하지 않고, 계산 결과를 반환하는 구조가 좋습니다.

```text
Coupon Context:
- 이 쿠폰은 사용 가능하다
- 할인 금액은 5,000원이다

Order Context:
- 이 할인 금액을 주문에 반영한다
```

**추천 모델 구조**

```text
coupon/
  domain/
    coupon.py
    discount_policy.py
    stacking_policy.py
    money.py
    redemption.py
    exceptions.py
  application/
    apply_coupon_use_case.py
  infrastructure/
    django_coupon_repository.py
    django_redemption_repository.py
  models.py
```

핵심은 `Coupon`이 할인 계산과 자체 정책 검증을 책임지고, 사용 이력처럼 외부 조회가 필요한 정보는 `CouponRedemptionContext`로 주입받는 것입니다. 이렇게 하면 정액 할인, 정률 할인, 최소 주문 금액, 중복 사용 제한을 도메인 규칙으로 명확하게 분리할 수 있습니다.