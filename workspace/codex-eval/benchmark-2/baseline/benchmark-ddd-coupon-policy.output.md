DDD 기준으로 쿠폰 정책은 “쿠폰이 무엇인가”보다 “할인을 적용할 수 있는 정책과 제약을 어떻게 일관되게 지킬 것인가”를 중심에 두는 게 좋습니다.

**Bounded Context**
`Promotion / Coupon Context`

주요 책임:

- 쿠폰 발급
- 쿠폰 사용 가능 여부 판단
- 할인 금액 계산
- 쿠폰 사용 기록
- 중복 사용 제한 검증

**Aggregate**
`Coupon`

쿠폰은 할인 정책과 사용 제약을 함께 가진 Aggregate Root로 둡니다.

```text
Coupon
- couponId
- name
- discountPolicy
- usagePolicy
- validityPeriod
- status
```

`Coupon` 내부에서 보장해야 하는 불변식:

- 만료된 쿠폰은 사용할 수 없다
- 비활성 쿠폰은 사용할 수 없다
- 최소 주문 금액 미만이면 사용할 수 없다
- 중복 사용 불가 쿠폰은 이미 사용된 주문/사용자에게 다시 적용할 수 없다
- 할인 금액은 주문 금액을 초과할 수 없다

**Value Object**

```text
Money
- amount
- currency

OrderAmount
- totalAmount

ValidityPeriod
- startsAt
- endsAt

DiscountPolicy
- FixedAmountDiscount
- RateDiscount

UsagePolicy
- minimumOrderAmount
- stackable
- perUserLimit
```

할인 정책은 Strategy 형태로 분리하는 게 좋습니다.

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
    def __init__(self, rate: float, max_discount: Money | None = None):
        self.rate = rate
        self.max_discount = max_discount

    def calculate(self, order_amount: Money) -> Money:
        discount = order_amount * self.rate

        if self.max_discount:
            discount = min(discount, self.max_discount)

        return min(discount, order_amount)
```

**Domain Service**
중복 사용 제한은 쿠폰 하나만 보고 판단하기 어렵습니다. 사용 이력이나 주문에 이미 적용된 쿠폰 목록이 필요하므로 Domain Service로 분리합니다.

```text
CouponApplicationService
- canApply(coupon, order, user)
- apply(coupon, order, user)
```

도메인 서비스 책임:

- 주문 금액 확인
- 기존 적용 쿠폰과 중복 가능 여부 확인
- 사용자별 사용 횟수 확인
- 할인 금액 계산
- 사용 기록 생성

**중복 사용 제한 모델링**

```text
UsagePolicy
- stackable: bool
```

규칙 예시:

```text
stackable = false
→ 같은 주문에 다른 쿠폰이 이미 있으면 적용 불가

stackable = true
→ 다른 쿠폰과 함께 사용 가능
```

더 정교하게 하려면 쿠폰 타입별 중복 제한도 가능합니다.

```text
CouponCombinationPolicy
- exclusive
- stackable_with_product_coupon
- stackable_with_shipping_coupon
```

**최소 주문 금액**

최소 주문 금액은 할인 정책이 아니라 사용 조건입니다.

```text
UsagePolicy.minimumOrderAmount
```

예시 규칙:

```python
if order.total_amount < coupon.usage_policy.minimum_order_amount:
    raise CouponCannotBeApplied("최소 주문 금액을 충족하지 않습니다.")
```

**도메인 흐름**

```text
1. 사용자가 주문에 쿠폰 적용 요청
2. Coupon 조회
3. Order 요약 정보 조회
4. CouponUsageHistory 조회
5. Coupon.canBeUsedNow(now) 검증
6. UsagePolicy 검증
7. 중복 사용 가능 여부 검증
8. DiscountPolicy로 할인 금액 계산
9. Order에 CouponDiscount 적용
10. CouponUsage 기록
```

**추천 구조**

```text
coupon/
- domain/
  - coupon.py
  - discount_policy.py
  - usage_policy.py
  - coupon_usage.py
  - money.py
- application/
  - apply_coupon_service.py
- infrastructure/
  - coupon_repository.py
  - coupon_usage_repository.py
```

핵심은 `정액/정률 할인`은 `DiscountPolicy`, `최소 주문 금액/중복 사용 제한`은 `UsagePolicy`로 분리하는 것입니다. 이렇게 나누면 할인 계산 로직과 쿠폰 사용 가능 조건이 섞이지 않아 정책 추가가 쉬워집니다.