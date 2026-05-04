도메인 의도는 `Order.checkout()` 안에 모여 있어서 “주문을 체크아웃한다”는 유스케이스는 읽힙니다. 다만 클린 아키텍처 관점에서는 이 메서드가 엔티티, ORM, 트랜잭션, 재고 저장, 외부 결제 준비를 한 번에 처리해서 경계가 크게 무너져 있습니다.

**주요 리뷰**

| 심각도 | 위치 | 문제 |
|---|---|---|
| High | `checkout(payment_gateway)` | **DIP / Dependency Rule** — Django 모델이 외부 결제 게이트웨이를 직접 호출합니다. 도메인 모델 또는 영속성 모델이 인프라 세부사항을 알게 되어 테스트와 교체가 어려워집니다. 결제는 `PaymentPort` 같은 인터페이스를 애플리케이션 서비스가 호출하는 쪽이 낫습니다. |
| High | `item.product.stock -= item.quantity; save()` | **SRP** — 주문 모델이 주문 상태 전이뿐 아니라 재고 차감과 상품 저장까지 책임집니다. 재고 정책이 바뀌면 `Order`가 바뀌고, 주문 정책이 바뀌어도 `Order`가 바뀝니다. 재고 예약/차감은 `InventoryService` 또는 별도 도메인 서비스로 분리하는 편이 안전합니다. |
| High | 전체 `checkout()` | **Transaction Boundary** — 재고 차감 후 결제 준비 또는 주문 저장이 실패하면 부분 변경이 남을 수 있습니다. 또한 동시 체크아웃에서 `stock` 검증과 차감 사이에 경쟁 조건이 생깁니다. Django에서는 유스케이스 레벨에서 `transaction.atomic()`과 `select_for_update()` 같은 잠금 전략이 필요합니다. |
| High | `self.items.all()` | **Clean Architecture Boundary** — 도메인 행위가 ORM reverse manager에 직접 의존합니다. 이 코드는 DB가 있어야만 실행되므로 순수 단위 테스트가 어렵고, 도메인 규칙을 Django 밖에서 재사용하기 어렵습니다. |
| Medium | `status = CharField(..., default="draft")` | **명확성 / 정보 은닉** — `"draft"`, `"ready_to_pay"`가 문자열 매직 값입니다. 가능한 상태와 전이를 `Enum`/`TextChoices`로 명시해야 오타와 불법 전이를 줄일 수 있습니다. |
| Medium | `total_amount` | **중복된 지식** — 주문 금액이 `OrderItem`들의 가격/수량에서 계산되는 값이라면 저장된 `total_amount`는 쉽게 불일치합니다. 저장이 필요하다면 “언제 스냅샷되는 금액인지”를 정책으로 분리해야 합니다. |
| Medium | `ValueError("invalid status")` | **도메인 예외** — 호출자는 상태 오류와 재고 부족을 구분하기 어렵습니다. `InvalidOrderStatus`, `InsufficientStock` 같은 도메인 예외가 낫습니다. |
| Medium | `checkout()` 메서드 길이와 추상화 | **Function / SRP** — 상태 검증, 재고 검증, 재고 저장, 결제 준비, 주문 저장이 한 메서드에 섞여 있습니다. 같은 추상화 수준의 메시지로 분해해야 변경 지점이 선명해집니다. |

**권장 방향**

클린 아키텍처에 가깝게 가려면 `Order` 모델은 최소한의 상태 전이와 불변식만 맡기고, 체크아웃 유스케이스는 애플리케이션 서비스로 올리는 편이 좋습니다.

```python
class Order(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        READY_TO_PAY = "ready_to_pay", "Ready to pay"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    def mark_ready_to_pay(self) -> None:
        if self.status != self.Status.DRAFT:
            raise InvalidOrderStatus(self.status)
        self.status = self.Status.READY_TO_PAY
```

```python
class CheckoutOrder:
    def __init__(self, inventory, payment_gateway, order_repository):
        self.inventory = inventory
        self.payment_gateway = payment_gateway
        self.order_repository = order_repository

    def execute(self, order_id: int) -> None:
        with transaction.atomic():
            order = self.order_repository.get_for_update(order_id)
            items = self.order_repository.list_items_for_update(order)

            self.inventory.reserve(items)
            self.payment_gateway.prepare(order.total_amount)

            order.mark_ready_to_pay()
            self.order_repository.save(order)
```

핵심은 `Order.checkout()`를 “모든 것을 수행하는 모델 메서드”로 두지 않는 것입니다. Django 모델은 영속성 모델이므로 도메인 규칙 일부를 담을 수는 있지만, 외부 IO, 트랜잭션 경계, 여러 aggregate 변경, 결제/재고 orchestration은 application use case가 맡는 쪽이 더 깨끗합니다.

**테스트 관점에서 꼭 확인할 것**

`draft`가 아닌 주문은 체크아웃 불가, 재고 부족 시 어떤 변경도 저장되지 않음, 결제 준비 실패 시 재고와 주문 상태가 롤백됨, 동시 체크아웃에서 재고가 음수가 되지 않음, 상태 값 오타가 불가능함을 테스트해야 합니다.

---
> **관련 스킬 참조:**
> - Django 유스케이스/서비스 계층 테스트 → **dddjango:implementation-test** 스킬