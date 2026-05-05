**Severity-Ranked Findings**
`[High] Aggregate boundary violation` -- `Order.checkout()`가 `OrderItem`을 넘어 `Product.stock`까지 직접 변경합니다. `Product`/재고가 별도 애그리거트라면 `Order` 애그리거트가 다른 애그리거트의 내부 상태를 같은 메서드에서 수정하는 구조입니다. `Order`는 “draft에서 ready_to_pay로 전이 가능한가” 같은 주문 불변식만 보호하고, 재고 차감/예약은 `Inventory` 또는 재고 애플리케이션 서비스가 맡는 편이 경계가 명확합니다.

`[High] Gateway dependency leak` -- Django 모델 메서드가 `payment_gateway.prepare(...)`를 직접 호출합니다. 모델이 외부 결제 시스템, SDK 어휘, 네트워크 I/O에 묶이면 도메인 규칙 테스트가 어려워지고 클린 아키텍처의 의존성 방향이 깨집니다. 결제 게이트웨이는 포트/어댑터로 두고, 호출은 애플리케이션 서비스가 조율해야 합니다. `Order`는 상태 전이만 수행하는 게 맞습니다.

`[High] Transaction/race condition` -- 재고 확인과 차감이 원자적으로 보호되지 않습니다. 동시에 두 체크아웃이 실행되면 둘 다 `stock >= quantity`를 통과하고 초과 판매가 날 수 있습니다. 최소한 `transaction.atomic()` 안에서 관련 행을 잠그거나, 낙관적 잠금/version 또는 조건부 `UPDATE stock = stock - quantity WHERE stock >= quantity` 계열로 처리해야 합니다. 또한 외부 결제 호출은 DB 트랜잭션 안에 넣으면 롤백/재시도/타임아웃 경계가 꼬이므로 `transaction.on_commit()` 또는 outbox가 더 안전합니다.

`[Medium] N+1 query risk` -- `for item in self.items.all():` 후 `item.product.stock`에 접근하면 `OrderItem`마다 `Product` 조회가 추가될 수 있습니다. `item.product.save()`도 item 수만큼 개별 UPDATE를 만듭니다. 서비스 레이어에서 `select_related("product")`, `prefetch_related(...)`, `select_for_update()` 또는 bulk/조건부 업데이트 전략을 명시해야 합니다.

`[Medium] assertNumQueries regression test missing` -- 이 코드는 항목 수가 늘수록 쿼리 수가 선형으로 늘 가능성이 큽니다. 체크아웃 경로는 성능/정합성 모두 중요하므로 테스트에서 `assertNumQueries`로 쿼리 수를 고정하고, N+1 회귀를 잡아야 합니다.

`[Low] Domain expressiveness` -- `status = "draft"` / `"ready_to_pay"`는 매직 스트링입니다. Django 모델이라면 `TextChoices`를 쓰고, 상태 전이는 `mark_ready_to_pay()` 같은 의도 드러나는 메서드로 제한하는 편이 낫습니다. `ValueError`도 호출자가 구분하기 어려우므로 `InvalidOrderStatus`, `InsufficientStock` 같은 도메인 예외가 더 명확합니다.

**Minimal Refactoring Sketch**
```python
from typing import Protocol

from django.db import models, transaction


class InvalidOrderStatus(Exception):
    pass


class InsufficientStock(Exception):
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
            raise InvalidOrderStatus("order must be draft")

        self.status = self.Status.READY_TO_PAY


class PaymentGateway(Protocol):
    def prepare(self, amount: int) -> None:
        ...


def checkout_order(order_id: int, payment_gateway: PaymentGateway) -> None:
    with transaction.atomic():
        order = (
            Order.objects.select_for_update()
            .prefetch_related("items__product")
            .get(id=order_id)
        )

        order.mark_ready_to_pay()

        products_to_update = []
        for item in order.items.all():
            product = item.product
            if product.stock < item.quantity:
                raise InsufficientStock("out of stock")

            product.stock -= item.quantity
            products_to_update.append(product)

        Product.objects.bulk_update(products_to_update, ["stock"])
        order.save(update_fields=["status"])

        transaction.on_commit(
            lambda: payment_gateway.prepare(order.total_amount)
        )
```

이 코드는 “최소 수정” 예시입니다. 더 엄격하게 하려면 재고를 `Product` 직접 변경이 아니라 `InventoryService.reserve(order_id, lines)` 같은 별도 유스케이스로 빼고, 결제 준비도 `PaymentRequested` 이벤트/outbox로 연결하는 쪽이 애그리거트 경계가 더 선명합니다.

**Query Test Sketch**
```python
def test_checkout_query_count(self):
    order = OrderFactory.create_with_items(count=3)

    with self.assertNumQueries(6):
        checkout_order(order.id, FakePaymentGateway())
```

정확한 숫자는 실제 factory, FK 로딩, DB 제약, bulk 전략에 따라 조정해야 합니다. 핵심은 “item 수가 3에서 30으로 늘어도 쿼리 수가 선형 증가하지 않는다”를 테스트로 고정하는 것입니다.

---
> **관련 스킬 참조:**
> - 애그리거트/도메인 이벤트 경계 재설계 → **architecture-ddd** 스킬
> - 포트/어댑터, UoW, outbox 적용 → **architecture-implementation-patterns** 스킬
> - Django ORM 트랜잭션/N+1 테스트 구체화 → **implementation-django** 스킬