**Findings**

1. **Critical — [Transaction / Consistency]**
   `checkout()`가 `Product.stock` 여러 건 수정, PG 준비 호출, `Order.status` 저장을 하나의 명시적 트랜잭션 없이 처리합니다. 중간에 `payment_gateway.prepare()` 또는 마지막 `self.save()`가 실패하면 일부 상품 재고만 차감된 주문이 남을 수 있습니다. 반대로 트랜잭션 안에서 PG 같은 외부 I/O를 직접 호출하면 롤백 불가능한 부수 효과가 DB 상태와 어긋날 수 있습니다.
   최소 수정: DB 변경은 `transaction.atomic()`으로 묶고, 외부 호출은 `transaction.on_commit()` 또는 Outbox/비동기 핸들러로 커밋 후 실행하세요.

2. **Critical — [Aggregate Boundary]**
   `Order`가 `self.items -> item.product -> product.stock`까지 따라가서 `Product` 상태를 직접 변경합니다. 주문, 상품, 재고는 보통 서로 다른 애그리거트입니다. 주문 애그리거트가 상품/재고 애그리거트 내부 상태를 직접 수정하면 “하나의 트랜잭션에서 하나의 애그리거트만 수정한다”는 경계가 깨지고, 재고 불변식이 `Order.checkout()` 안으로 새어 나옵니다.
   최소 수정: `Order`는 “결제 준비 상태로 전이”만 책임지고, 재고 차감/예약은 `InventoryService` 또는 `StockItem.reserve()` 같은 재고 경계에서 처리하세요.

3. **Critical — [Concurrency / Stock Oversell]**
   `if item.product.stock < item.quantity` 검사 후 `stock -= quantity`는 동시 요청에서 oversell이 납니다. 두 트랜잭션이 같은 stock 값을 읽고 둘 다 통과할 수 있습니다.
   최소 수정: 재고 행을 `select_for_update()`로 잠그거나, 조건부 `UPDATE ... WHERE stock >= quantity` + `F()` expression으로 원자적으로 차감하세요. 충돌이 잦은 재고 경로라면 비관적 잠금이 실용적입니다.

4. **High — [Gateway Dependency / Clean Architecture]**
   Django 모델 메서드가 `payment_gateway.prepare()`를 직접 호출합니다. 모델이 외부 PG 포트의 실행 시점, 실패 방식, 멱등성 정책을 알게 되어 도메인/영속성 객체와 인프라 통합 흐름이 섞입니다.
   최소 수정: `payment_gateway`는 애플리케이션 서비스의 의존성으로 두고, 도메인 모델은 상태 전이와 불변식만 담당하게 하세요. 포트는 사용하는 계층이 소유하고, 어댑터가 실제 PG SDK를 감싸는 구조가 좋습니다.

5. **High — [N+1 Query]**
   `for item in self.items.all(): item.product.stock`는 `items` 1쿼리 + 각 item마다 product 조회 N쿼리가 될 수 있습니다. 모델 인스턴스 메서드 안에서는 호출자가 `prefetch_related()`를 했는지 보장하기도 어렵습니다.
   최소 수정: checkout 유스케이스 진입점에서 `Order.objects.prefetch_related(Prefetch("items", queryset=OrderItem.objects.select_related("product")))`로 로딩하거나, 재고 서비스가 필요한 stock row만 한 번에 조회하게 하세요. 회귀 방지로 `assertNumQueries` 테스트를 추가해야 합니다.

6. **Medium — [Domain Invariant / Primitive Obsession]**
   `status = "draft"`와 `"ready_to_pay"` 매직 문자열, `ValueError`, `total_amount` 원시 정수는 도메인 규칙을 흐리게 합니다. 특히 `total_amount`가 item 합계와 일치한다는 불변식이 코드에 없습니다.
   최소 수정: `Order.Status(TextChoices)`, `InvalidOrderStatus`, `InsufficientStock` 같은 도메인 예외, 가능하면 `Money` 값 객체 또는 최소한 금액 계산 책임을 한 곳으로 모으세요.

**Minimal Refactoring Direction**

```python
# models.py
class Order(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        READY_TO_PAY = "ready_to_pay", "Ready to pay"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    def mark_ready_to_pay(self) -> None:
        if self.status != self.Status.DRAFT:
            raise InvalidOrderStatus("draft 상태에서만 결제 준비가 가능합니다")
        self.status = self.Status.READY_TO_PAY
```

```python
# services.py
from django.db import transaction
from django.db.models import F, Prefetch

def order_checkout(*, order_id: int, payment_gateway: PaymentGateway) -> None:
    with transaction.atomic():
        order = (
            Order.objects
            .select_for_update()
            .prefetch_related(
                Prefetch(
                    "items",
                    queryset=OrderItem.objects.select_related("product"),
                )
            )
            .get(pk=order_id)
        )

        for item in order.items.all():
            updated = (
                Product.objects
                .filter(pk=item.product_id, stock__gte=item.quantity)
                .update(stock=F("stock") - item.quantity)
            )
            if updated != 1:
                raise InsufficientStock("재고가 부족합니다")

        order.mark_ready_to_pay()
        order.save(update_fields=["status"])

        transaction.on_commit(
            lambda: payment_gateway.prepare(order.total_amount)
        )
```

이 코드는 “최소 이동” 버전입니다. 더 DDD에 가깝게 가려면 `Product.stock` 직접 수정도 제거하고 `StockItem.reserve(order_id, quantity)` 또는 `InventoryService.reserve_items(...)`로 재고 경계를 분리하는 편이 맞습니다.

**Query Test**

```python
def test_order_checkout_query_count(self):
    order = OrderFactory()
    OrderItemFactory.create_batch(3, order=order)

    with self.assertNumQueries(6):
        order_checkout(order_id=order.id, payment_gateway=FakePaymentGateway())
```

실제 쿼리 수는 모델/락/프리페치 구조에 맞춰 조정해야 합니다. 핵심은 `items` 수가 3개에서 30개로 늘어도 쿼리 수가 선형 증가하지 않도록 고정하는 것입니다.

---
> **관련 스킬 참조:**
> - 애그리거트 경계·도메인 이벤트 → **architecture-ddd** 스킬
> - 포트/어댑터·UoW·Outbox → **architecture-implementation-patterns** 스킬
> - Django 서비스 레이어·QuerySet 최적화 → **implementation-django** 스킬