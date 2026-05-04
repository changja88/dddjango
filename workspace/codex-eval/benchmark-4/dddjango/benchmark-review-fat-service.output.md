**주요 내용**

좋은 점부터 보면, `CheckoutService.checkout()`가 “체크아웃 유스케이스를 조율한다”는 경계 자체는 자연스럽습니다. `payment_gateway`도 직접 import하지 않고 인자로 받는 점은 테스트 가능성 측면에서 나쁘지 않습니다.

다만 현재 구현은 책임이 많습니다. 특히 위험도 순서로 보면 아래가 핵심입니다.

1. **[동시성 / DB 무결성] -- 재고 차감이 레이스 컨디션에 취약함**

```python
product = Product.objects.get(id=item["product_id"])
if product.stock < item["quantity"]:
    raise ValueError("out of stock")
product.stock -= item["quantity"]
product.save()
```

동시에 두 요청이 같은 `stock=1`을 읽으면 둘 다 통과할 수 있습니다. `save()`도 전체 필드 저장이라 다른 변경을 덮을 수 있습니다. 체크아웃에서 가장 치명적인 문제는 “서비스 책임 과다”보다 “재고 불변식이 DB 트랜잭션으로 보호되지 않음”입니다.

최소 개선은 `transaction.atomic()` 안에서 재고 row를 잠그거나, 조건부 `UPDATE stock = stock - qty WHERE stock >= qty`를 쓰는 것입니다. 핫 아이템이면 `select_for_update()`가 단순하고 명확합니다.

2. **[트랜잭션 경계] -- 중간 실패 시 주문/재고/결제가 불일치할 수 있음**

현재는 `Order.objects.create()` 후 재고를 저장하고, 쿠폰 조회나 gateway 호출이 실패하면 부분 변경이 남을 수 있습니다. 주문 생성, 주문 라인 생성, 재고 예약, 총액 저장은 하나의 DB 트랜잭션이어야 합니다.

반대로 외부 gateway 호출을 DB 트랜잭션 안에 길게 넣으면 락 보유 시간이 늘어납니다. 보통은 주문을 `PENDING_PAYMENT`로 저장하고 `transaction.on_commit()` 또는 outbox로 결제 준비를 넘깁니다. 결제 결과는 별도 단계에서 `PAID`/`PAYMENT_FAILED`로 전이시키는 편이 안전합니다.

3. **[책임 과다 / SRP] -- 서비스가 도메인 규칙을 직접 모두 알고 있음**

이 메서드는 다음 책임을 동시에 가집니다.

- 주문 생성
- 상품 조회
- 재고 검증과 차감
- 가격 합산
- 쿠폰 적용
- 결제 준비
- 영속성 저장 순서 결정

서비스는 유스케이스 조율자에 머무르고, 불변식은 더 가까운 객체로 내려가는 게 좋습니다. 예를 들어 `Product.reserve(quantity)`, `Coupon.apply(total)`, `Order.add_line(...)`, `Order.apply_discount(...)`처럼요. 거대한 헥사고날 계층까지는 필요 없고, 우선 “재고/금액/쿠폰 규칙”만 모델 메서드나 작은 정책 객체로 빼면 충분합니다.

4. **[ORM Query] -- 루프 내 개별 조회/저장으로 성능과 일관성이 약함**

`items` 개수만큼 `Product.objects.get()`과 `product.save()`가 반복됩니다. 상품 수가 늘면 쿼리가 선형 증가합니다. 또한 같은 `product_id`가 중복으로 들어오면 계산과 차감이 꼬일 수 있습니다. 먼저 item을 product_id 기준으로 합산하고, 필요한 상품을 한 번에 조회해야 합니다.

5. **[외부 Gateway 의존성] -- 인터페이스는 있지만 도메인 의도가 약함**

`payment_gateway.prepare(total)`은 기술적 동작 이름에 가깝고, 실패/멱등성/요청 식별자가 드러나지 않습니다. 최소한 애플리케이션 서비스가 의존하는 포트를 명시하는 편이 좋습니다.

```python
class PaymentGateway(Protocol):
    def prepare_payment(self, *, order_id: int, amount: Decimal, idempotency_key: str) -> None:
        ...
```

**최소 개선 방향**

```python
@transaction.atomic
def checkout(self, user, items, coupon_code, payment_gateway):
    normalized_items = normalize_items(items)

    products = (
        Product.objects
        .select_for_update()
        .filter(id__in=normalized_items.keys())
    )
    products_by_id = {product.id: product for product in products}

    order = Order.objects.create(user=user, status=Order.Status.PENDING_PAYMENT)
    total = Decimal("0")

    for product_id, quantity in normalized_items.items():
        product = products_by_id[product_id]
        product.reserve(quantity)
        total += product.price * quantity

    if coupon_code:
        coupon = Coupon.objects.get(code=coupon_code)
        total = coupon.apply_to(total)

    Product.objects.bulk_update(products_by_id.values(), ["stock"])
    order.total_amount = total
    order.save(update_fields=["total_amount", "status"])

    transaction.on_commit(
        lambda: payment_gateway.prepare_payment(
            order_id=order.id,
            amount=order.total_amount,
            idempotency_key=f"checkout:{order.id}",
        )
    )
    return order
```

**검증해야 할 테스트**

- 동시 checkout 2건이 같은 마지막 재고를 구매할 때 하나만 성공하는지
- 쿠폰 조회 실패 또는 재고 부족 시 주문/재고 변경이 rollback 되는지
- `assertNumQueries`로 상품 수 증가 시 쿼리가 과도하게 늘지 않는지
- gateway 실패가 DB 트랜잭션을 깨지 않고 주문 상태로 추적되는지
- 같은 요청 재시도 시 결제 준비가 멱등적으로 처리되는지

---
> **관련 스킬 참조:**
> - 재고/주문/결제 Aggregate 경계와 불변식 → **architecture-ddd** 스킬
> - 트랜잭션, 포트, outbox/on_commit 선택 → **architecture-implementation-patterns** 스킬
> - Django ORM 동시성/쿼리 최적화 → **implementation-django** 스킬