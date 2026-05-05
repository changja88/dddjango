**주요 내용**

1. **Critical — [Aggregate Boundary] `Order.checkout()`가 여러 애그리거트를 한 번에 수정합니다.**
   `Order`가 자신의 상태를 `ready_to_pay`로 바꾸는 것뿐 아니라 `Product.stock`까지 직접 차감합니다. 주문, 상품/재고, 결제는 변경 이유와 일관성 경계가 다릅니다. 특히 `item.product.stock -= ...`는 `Order` 애그리거트가 `Product` 또는 `Inventory` 애그리거트 내부 상태를 직접 만지는 구조입니다. DDD 관점에서는 `Order`는 “체크아웃 가능한가 / 상태 전이 가능한가”를 책임지고, 재고 예약/차감은 `Inventory` 쪽 정책 또는 애플리케이션 서비스가 조율해야 합니다.

2. **Critical — [Transaction Boundary] 부분 저장과 외부 부수 효과가 섞여 정합성이 깨질 수 있습니다.**
   루프 안에서 상품별로 `product.save()`가 실행됩니다. 세 번째 상품에서 재고 부족이 나면 앞선 상품 재고는 이미 차감됐을 수 있습니다. 또한 `payment_gateway.prepare()`가 DB 변경 중간에 호출되므로, 이후 `self.save()`가 실패하면 결제 준비는 됐지만 주문 상태는 바뀌지 않는 상태가 됩니다. Django에서는 최소한 `transaction.atomic()`으로 DB 변경을 묶고, 외부 API 호출은 가능하면 `transaction.on_commit()` 또는 결제/주문 상태 모델에 맞춘 Outbox로 분리해야 합니다.

3. **High — [Gateway Dependency] Django 모델이 외부 결제 게이트웨이에 직접 의존합니다.**
   `checkout(self, payment_gateway)`는 모델을 테스트하기 어렵게 만들고, 도메인 모델이 외부 시스템 호출 시점까지 알아야 합니다. Clean Architecture의 의존성 방향상 결제 게이트웨이는 포트/어댑터로 두고, 유스케이스 계층이 호출을 조율하는 편이 낫습니다. 모델 메서드는 `mark_ready_to_pay()` 같은 순수 상태 전이로 좁히는 것이 더 안정적입니다.

4. **High — [Concurrency] 재고 차감이 레이스 컨디션에 취약합니다.**
   `item.product.stock < item.quantity` 확인 후 `stock -= quantity` 저장은 동시에 두 체크아웃이 들어오면 둘 다 통과할 수 있습니다. 재고는 `select_for_update()`로 잠그거나, `F()` 표현식과 조건부 `UPDATE ... WHERE stock >= quantity`로 원자적으로 처리해야 합니다. 트래픽이 있는 주문/재고 경로라면 이건 기능 버그에 가깝습니다.

5. **High — [N+1 Query] `self.items.all()` 뒤 `item.product` 접근이 N+1을 만듭니다.**
   `items` 10개면 주문 품목 1쿼리 + 상품 10쿼리가 될 수 있습니다. 호출부에서 우연히 prefetch했는지에 기대면 회귀가 쉽습니다. 체크아웃 유스케이스는 `Prefetch("items", queryset=OrderItem.objects.select_related("product"))` 또는 별도 재고 조회 쿼리를 명시해야 합니다. 이 경로는 테스트에 `assertNumQueries`를 넣어야 합니다.

6. **Medium — [Domain Model] 상태와 금액이 원시 타입/매직 스트링입니다.**
   `status = "draft"` / `"ready_to_pay"`는 오타와 불가능한 상태를 막지 못합니다. Django 모델에서는 최소한 `TextChoices`를 쓰는 게 좋습니다. `total_amount`도 주문 품목 합계에서 파생되는 값이라면 직접 저장값과 품목 합계가 어긋날 수 있습니다. 도메인 중요도가 높다면 `Money(amount, currency)` 값 객체나 최소한 통화 정책이 필요합니다.

7. **Medium — [Domain Exceptions] `ValueError`가 유스케이스 의도를 흐립니다.**
   `"invalid status"`, `"out of stock"`은 호출자가 분기 처리하기 어렵습니다. `InvalidOrderStatus`, `OutOfStock` 같은 도메인 예외가 낫습니다.

**최소 리팩터링 방향**

Django 프로젝트에서 과한 Data Mapper까지 바로 가지 않는다면, 현실적인 1차 개선은 “모델은 상태 전이만, 서비스가 트랜잭션과 외부 의존성을 조율”하는 형태입니다.

```python
from typing import Protocol

from django.db import models, transaction
from django.db.models import Prefetch


class InvalidOrderStatus(Exception):
    pass


class OutOfStock(Exception):
    pass


class PaymentGateway(Protocol):
    def prepare(self, amount: int) -> None:
        ...


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
            raise InvalidOrderStatus("draft 상태에서만 결제 준비가 가능합니다.")
        self.status = self.Status.READY_TO_PAY
```

```python
from django.db import transaction
from django.db.models import Prefetch


def order_checkout(*, order_id: int, payment_gateway: PaymentGateway) -> None:
    with transaction.atomic():
        order = (
            Order.objects.select_for_update()
            .prefetch_related(
                Prefetch(
                    "items",
                    queryset=OrderItem.objects.select_related("product"),
                )
            )
            .get(id=order_id)
        )

        items = list(order.items.all())
        product_ids = [item.product_id for item in items]

        products_by_id = {
            product.id: product
            for product in Product.objects.select_for_update().filter(id__in=product_ids)
        }

        for item in items:
            product = products_by_id[item.product_id]
            if product.stock < item.quantity:
                raise OutOfStock(f"product_id={product.id}")

            product.stock -= item.quantity

        Product.objects.bulk_update(products_by_id.values(), ["stock"])

        order.mark_ready_to_pay()
        order.save(update_fields=["status"])

        transaction.on_commit(lambda: payment_gateway.prepare(order.total_amount))
```

이 코드는 완전한 DDD 구현이라기보다는, 현재 구조에서 가장 작은 비용으로 위험을 줄이는 형태입니다. 다만 결제 준비가 반드시 유실되면 안 되는 통합 이벤트라면 `transaction.on_commit()`보다 Outbox가 맞습니다. 결제 시스템 호출 결과가 주문 상태 전이에 영향을 준다면 `ready_to_pay` 전이가 아니라 `payment_preparation_requested` 같은 별도 상태/이벤트 모델을 두는 편이 더 정확합니다.

**테스트 보강 포인트**

```python
def test_checkout_prefetches_items_and_products(self):
    order = OrderFactory.create_with_items(count=3)

    with self.assertNumQueries(5):
        order_checkout(order_id=order.id, payment_gateway=FakePaymentGateway())
```

정확한 쿼리 수는 팩토리, DB, 구현에 따라 조정해야 하지만, 핵심은 체크아웃 경로에 `assertNumQueries`를 둬서 `item.product` N+1 회귀를 막는 것입니다. 동시성은 별도로 “재고 1개에 주문 2개 동시 체크아웃” 케이스를 트랜잭션 테스트로 검증해야 합니다.

---
> **관련 스킬 참조:**
> - 주문/재고/결제 경계 재설계 → **architecture-ddd** 스킬
> - 서비스 레이어, 트랜잭션, Repository/UoW 도입 판단 → **architecture-implementation-patterns** 스킬
> - Django ORM 최적화와 `assertNumQueries` 테스트 → **implementation-django** 스킬