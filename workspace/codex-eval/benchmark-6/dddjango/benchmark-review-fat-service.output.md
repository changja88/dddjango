Fixture path `/Users/hyun/Desktop/dddjango/none`는 존재하지 않아 fixture 파일은 읽을 수 없었습니다 (`find: No such file or directory`). 제공된 코드 기준으로 리뷰합니다.

**Findings**

1. **High — [Concurrency / DB Transaction] 재고 차감이 레이스 컨디션에 취약합니다.**  
   `product.stock < quantity` 확인 후 `product.stock -= quantity; save()` 사이에 다른 checkout이 끼어들면 재고가 음수가 되거나 초과 판매될 수 있습니다. 또한 주문 생성, 재고 차감, 쿠폰 적용, 결제 준비가 하나의 원자적 단위로 묶여 있지 않아 중간 실패 시 부분 반영됩니다.

2. **High — [External Gateway Dependency] DB 트랜잭션과 외부 gateway 호출 경계가 불명확합니다.**  
   `payment_gateway.prepare(total)`가 실패하면 이미 재고가 저장됐을 수 있고, 반대로 트랜잭션 안에서 외부 API를 호출하면 DB lock을 오래 잡습니다. 결제 준비가 “외부 부수효과”라면 `transaction.on_commit()` 이후 실행하거나, payment intent 생성과 order 상태 전이를 명확히 분리해야 합니다.

3. **Medium — [Responsibility] `CheckoutService.checkout()`가 유스케이스 조율, 상품 조회, 재고 정책, 쿠폰 조회/계산, 결제 gateway 호출, 영속성까지 모두 압축하고 있습니다.**  
   서비스가 아예 필요 없다는 뜻은 아닙니다. Checkout은 여러 모델을 조율하므로 application service로 두는 것은 자연스럽습니다. 문제는 도메인 규칙인 “재고 예약 가능 여부”, “총액 계산”, “쿠폰 할인 적용”까지 절차 코드로 흩어져 변경 이유가 섞인 점입니다.

4. **Medium — [ORM Query] 루프 안의 `Product.objects.get()`은 item 수만큼 쿼리를 발생시킵니다.**  
   작은 장바구니에서는 치명적이지 않지만 checkout 경로는 핵심 쓰기 경로입니다. `id__in`으로 한 번에 조회하고, 재고 차감 대상은 lock을 잡아 처리하는 편이 낫습니다. `Coupon.objects.get()`도 `DoesNotExist`가 그대로 올라가 사용자/도메인 예외와 섞입니다.

5. **Low — [Domain Error] `ValueError("out of stock")`는 호출자가 의미 있게 처리하기 어렵습니다.**  
   `OutOfStock`, `InvalidCoupon` 같은 도메인 예외가 더 명확합니다.

**최소 개선 방향**

거대한 계층 구조를 만들기보다, 우선 checkout 트랜잭션과 재고 차감 책임만 분리하는 정도가 적절합니다.

```python
from django.db import transaction

class OutOfStock(Exception):
    pass

class CheckoutService:
    def checkout(self, user, items, coupon_code, payment_gateway):
        with transaction.atomic():
            products = {
                p.id: p
                for p in Product.objects.select_for_update().filter(
                    id__in=[item["product_id"] for item in items]
                )
            }

            order = Order.objects.create(user=user)
            total = 0

            for item in items:
                product = products[item["product_id"]]
                quantity = item["quantity"]

                if product.stock < quantity:
                    raise OutOfStock(product.id)

                product.stock -= quantity
                total += product.price * quantity

            Product.objects.bulk_update(products.values(), ["stock"])

            if coupon_code:
                coupon = Coupon.objects.get(code=coupon_code)
                total -= coupon.discount_amount

            order.total_amount = total
            order.save(update_fields=["total_amount"])

            transaction.on_commit(lambda: payment_gateway.prepare(total))

        return order
```

이 코드는 완성 설계라기보다 현재 코드의 가장 큰 위험을 줄이는 1차 개선안입니다. 다만 `payment_gateway.prepare()` 결과가 order 상태에 반드시 필요하다면 `on_commit`만으로는 부족하고, `Order.status = PAYMENT_PENDING/PREPARED/FAILED` 같은 명시적 상태 전이와 재시도 가능한 payment 작업으로 분리해야 합니다.

**Verification Steps**

- 동시 checkout 테스트: 같은 product stock=1에 대해 동시에 quantity=1 요청 2개를 실행하고 하나만 성공하는지 확인.
- 쿼리 회귀 테스트: item N개 checkout 시 product 조회가 N회로 늘지 않도록 `assertNumQueries`로 보호.
- gateway 실패 테스트: `payment_gateway.prepare()`가 예외를 내도 DB 트랜잭션 커밋/롤백 정책이 의도와 일치하는지 확인.
- 쿠폰/재고 예외 테스트: 품절, 존재하지 않는 coupon, 누락된 product id가 도메인 예외로 처리되는지 확인.

---
> **관련 스킬 참조:**
> - Django ORM 트랜잭션/쿼리 개선 → **implementation-django** 스킬
> - 책임 분리와 gateway 경계 설계 → **architecture-implementation-patterns** 스킬