**[주요 내용]**
**P0 — [Aggregate Boundary] `Order.checkout()`가 주문, 재고, 결제를 한 트랜잭션성 유스케이스로 합쳐버렸습니다.**
`Order`가 `item.product.stock`을 직접 검사하고 차감하는 순간 `Order` 애그리거트가 `Product/Inventory` 애그리거트 내부 상태를 변경합니다. 주문의 불변식은 “draft 상태에서 결제 준비 상태로 전이 가능하다”에 가깝고, 재고 불변식은 Inventory 쪽 책임입니다. 현재 구조는 작은 애그리거트 원칙을 깨고, 주문 모델이 재고 정책까지 알아야 해서 경계가 커집니다.

**P0 — [Clean Architecture / DIP] Django 모델이 `payment_gateway`라는 외부 의존성을 직접 호출합니다.**
`payment_gateway.prepare(self.total_amount)`는 인프라 I/O입니다. 도메인 모델 또는 Django ORM 모델 안에 외부 시스템 호출이 들어가면 테스트가 어려워지고, 결제 SDK 어휘가 도메인으로 침투하기 쉽습니다. 결제 준비는 Application Service가 `PaymentGateway` 포트에 의존해서 조율하고, 모델은 상태 전이만 담당하는 쪽이 맞습니다.

**P0 — [Transaction Boundary] 재고 차감, 결제 준비, 주문 저장 사이에 원자성이 없습니다.**
루프 중간에 `product.save()`가 성공한 뒤 결제 준비가 실패하면 재고만 줄어든 주문이 남을 수 있습니다. 반대로 결제 준비는 성공했는데 `self.save()`가 실패하면 외부 결제 상태와 DB 상태가 갈라집니다. 최소한 DB 변경은 `transaction.atomic()` 안에서 묶고, 외부 결제 호출은 `transaction.on_commit()` 또는 Outbox로 분리해야 합니다. 결제 준비가 반드시 DB 커밋 이후 실행되어야 하는 부수 효과라면 `on_commit`이 더 안전합니다.

**P1 — [Concurrency] 재고 차감이 레이스 컨디션에 취약합니다.**
`if item.product.stock < item.quantity` 후 `stock -= quantity`는 동시 checkout 두 건이 같은 재고를 읽으면 초과 판매를 만들 수 있습니다. 단순 수정으로는 `select_for_update()`로 재고 행을 잠그거나, 더 나은 구조에서는 Inventory 애그리거트/Repository에서 낙관적 잠금 또는 조건부 `UPDATE stock = stock - q WHERE stock >= q`를 사용해야 합니다.

**P1 — [Django QuerySet / N+1] `self.items.all()`과 `item.product` 접근은 N+1 쿼리 가능성이 큽니다.**
주문 품목 N개마다 `item.product` 조회가 추가될 수 있습니다. 이 메서드를 유지한다면 최소 `self.items.select_related("product")`가 필요합니다. 다만 클린 아키텍처 관점에서는 모델 메서드에서 ORM 최적화까지 책임지기보다, Application Service/Repository가 필요한 그래프를 명시적으로 로드하는 편이 낫습니다.

**P1 — [Testing] `assertNumQueries` 회귀 테스트가 필요합니다.**
checkout 경로는 품목 수에 따라 쿼리 수가 늘어나기 쉬운 성능 민감 경로입니다. `OrderItem` 1개와 10개 케이스를 비교해 쿼리 수가 선형 증가하지 않도록 `assertNumQueries` 테스트를 두는 게 좋습니다. 특히 `select_related/prefetch_related`가 빠지면 바로 깨지게 만들어야 합니다.

**P2 — [Domain Model] `status`와 예외가 원시 문자열/일반 `ValueError`입니다.**
`"draft"`, `"ready_to_pay"`는 `models.TextChoices`로 올리고, 전이 실패는 `InvalidOrderStatus`, 재고 부족은 `OutOfStock` 같은 도메인 예외로 분리하는 편이 의도가 명확합니다. `total_amount`도 장기적으로는 `Money` 값 객체가 맞지만, Django 모델 필드에서는 금액/통화 컬럼과 도메인 변환 계층을 분리하는 방식이 현실적입니다.

**최소 리팩터링 방향**

```python
from typing import Protocol

from django.db import transaction
from django.db.models import Prefetch


class PaymentGateway(Protocol):
    def prepare(self, order_id: int, amount: int) -> None: ...


class InvalidOrderStatus(Exception):
    pass


class OutOfStock(Exception):
    pass


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

    def mark_ready_to_pay(self):
        if self.status != self.Status.DRAFT:
            raise InvalidOrderStatus("order is not draft")
        self.status = self.Status.READY_TO_PAY


def checkout_order(order_id: int, payment_gateway: PaymentGateway) -> None:
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
            .get(id=order_id)
        )

        order.mark_ready_to_pay()

        products_to_update = []
        for item in order.items.all():
            product = item.product
            if product.stock < item.quantity:
                raise OutOfStock(f"product_id={product.id}")

            product.stock -= item.quantity
            products_to_update.append(product)

        Product.objects.bulk_update(products_to_update, ["stock"])
        order.save(update_fields=["status"])

        transaction.on_commit(
            lambda: payment_gateway.prepare(order.id, order.total_amount)
        )
```

이 코드는 완전한 DDD 구현은 아니지만, 최소 변경으로 책임을 분리합니다. 모델은 상태 전이만 담당하고, 유스케이스 조율은 `checkout_order()`가 맡고, 외부 결제 호출은 커밋 이후로 밀립니다. 다음 단계에서는 재고 차감을 `InventoryService` 또는 `InventoryRepository.reserve()`로 빼서 `Order`와 `Product/Inventory` 애그리거트 경계를 더 명확히 하는 것이 좋습니다.

테스트는 최소한 이 정도를 권합니다.

```python
def test_checkout_query_count_does_not_grow_with_items(self):
    order = create_order_with_items(count=10)

    with self.assertNumQueries(5):
        checkout_order(order.id, payment_gateway=FakePaymentGateway())
```

정확한 쿼리 수는 실제 모델 관계와 DB 락 사용 여부에 맞춰 조정해야 합니다. 핵심은 품목 수가 늘어도 `item.product` 때문에 쿼리가 선형 증가하지 않게 고정하는 것입니다.

---
> **관련 스킬 참조:**
> - 애그리거트/도메인 이벤트/값 객체 정리 → **architecture-ddd** 스킬
> - 포트/어댑터, Repository, Unit of Work 분리 → **architecture-implementation-patterns** 스킬
> - Django QuerySet 최적화와 `assertNumQueries` 테스트 → **implementation-django** 스킬