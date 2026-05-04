**권장 결론**

`OrderManager`, `OrderService`, `OrderUseCase`를 모두 허용하면 이름이 계층을 설명하지 못합니다. 팀 규칙은 이렇게 잡는 게 낫습니다.

| 이름 | 허용 기준 | 금지 |
|---|---|---|
| `OrderManager` | Django `models.Manager` / `QuerySet` 전용 | 주문 생성, 결제, 취소 같은 유스케이스 처리 |
| `OrderService` | 가급적 금지. 꼭 쓰면 `DomainService`인지 `ApplicationService`인지 suffix로 명확화 | 모든 주문 로직을 넣는 God Service |
| `OrderUseCase` | 금지. 너무 넓음 | 엔티티 단위 UseCase 이름 |
| `PlaceOrderUseCase` | 복잡한 DDD 유스케이스 조율 | 단순 CRUD에 남발 |
| `OrderPricingPolicy`, `OrderCancellationPolicy` | 도메인 규칙 객체 | ORM, transaction, 외부 API 호출 |

**책임 기준**

`Manager`는 Django ORM 확장입니다. DB 조회/필터/생성 헬퍼까지만 둡니다.

```python
class OrderQuerySet(models.QuerySet):
    def awaiting_payment(self):
        return self.filter(status=Order.Status.AWAITING_PAYMENT)


class OrderManager(models.Manager.from_queryset(OrderQuerySet)):
    pass
```

여기에는 `pay()`, `cancel()`, `send_confirmation_email()` 같은 비즈니스 흐름을 넣지 않습니다.

`UseCase` 또는 `ApplicationService`는 애플리케이션 흐름을 조율합니다. 트랜잭션, Repository/ORM 로딩, 도메인 메서드 호출, 저장, `transaction.on_commit()` 같은 부수효과 연결이 책임입니다. 도메인 규칙 자체는 직접 계산하지 않습니다.

```python
class PlaceOrderUseCase:
    def __call__(self, command: PlaceOrderCommand) -> OrderId:
        with transaction.atomic():
            order = Order.place(
                customer_id=command.customer_id,
                lines=command.lines,
            )
            self.orders.save(order)

            transaction.on_commit(
                lambda: self.events.publish(order.collect_events())
            )

        return order.id
```

`Domain Service`는 특정 Entity/Value Object에 자연스럽게 들어가지 않는 순수 도메인 규칙입니다. ORM, Django settings, HTTP, email, transaction을 몰라야 합니다. 이름도 `OrderService`보다 `OrderPricingPolicy`, `ShippingFeeCalculator`, `OrderCancellationPolicy`처럼 구체화합니다.

**프로젝트 규모별 규칙**

작은 CRUD Django 앱:
`UseCase` 클래스를 만들지 않습니다. 모델 메서드, 커스텀 `QuerySet/Manager`, `selectors.py`, `services.py` 함수로 충분합니다.

```python
# services.py
def order_cancel(order: Order, *, reason: str) -> None:
    order.cancel(reason)
    order.save(update_fields=["status", "cancelled_reason", "updated_at"])
```

중간 규모:
쓰기 흐름은 `services.py`의 동사형 함수로 둡니다. 읽기는 `selectors.py`로 분리합니다. 클래스형 `OrderService`는 만들지 않습니다.

```python
# selectors.py
def order_list_for_customer(customer_id: int) -> QuerySet[Order]:
    return Order.objects.filter(customer_id=customer_id)
```

복잡한 DDD/결제/재고/배송 연동:
UseCase를 도입합니다. 단, 이름은 엔티티명이 아니라 업무 명령이어야 합니다.

- `PlaceOrderUseCase`
- `CancelOrderUseCase`
- `ConfirmPaymentUseCase`
- `RequestRefundUseCase`

**팀 네이밍 룰**

1. Django ORM 확장은 반드시 `*Manager`, `*QuerySet`.
2. 읽기 전용 조회는 `selectors.py`에 `order_get`, `order_list_for_customer`처럼 둔다.
3. 단순 쓰기 작업은 `services.py`에 `<entity>_<verb>` 함수명으로 둔다.
4. 복잡한 쓰기 흐름만 `*UseCase`를 쓴다.
5. `OrderService`, `OrderUseCase`, `OrderManager`처럼 엔티티 단위로 넓은 이름은 금지한다.
6. 도메인 규칙 객체는 `*Policy`, `*Calculator`, `*Specification`처럼 역할이 드러나게 쓴다.
7. 유스케이스 메서드는 보통 `__call__` 하나로 유지한다. 여러 public method가 필요하면 클래스가 너무 넓은 신호다.

**검증 기준**

```bash
rg "class .*Service|class .*UseCase|class .*Manager" apps/
rg "transaction.atomic|on_commit|requests\.|send_mail" apps/orders/
```

확인할 것:

- `Manager` 안에 transaction, email, 외부 API 호출이 없어야 합니다.
- `UseCase` 이름이 `OrderUseCase`처럼 넓지 않아야 합니다.
- `Service`가 있다면 `PricingPolicy`, `CancellationPolicy`처럼 더 구체적인 이름으로 바꿀 수 있는지 봅니다.
- 도메인 객체가 할 수 있는 일을 `Service`가 대신하고 있다면 모델/값 객체 메서드로 옮깁니다.

---
> **관련 스킬 참조:**
> - DDD 계층 책임과 Django 서비스 레이어 정리 → **architecture-ddd**, **implementation-django**, **implementation-cleancode** 스킬