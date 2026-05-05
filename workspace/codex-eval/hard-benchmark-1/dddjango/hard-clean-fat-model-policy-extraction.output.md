**[주요 내용]**

핵심 분리는 이렇게 잡는 게 좋습니다: `Order`는 주문 상태 불변식만 지키고, 수수료 계산은 정책 객체, PG/알림은 포트와 어댑터, 전체 유스케이스 순서는 application service가 조율합니다.

```python
# Before: orders/models.py
class Order(models.Model):
    def cancel(self):
        if self.status == "shipped":
            raise ValueError("cannot cancel")
        fee = self.calculate_fee()
        result = self.call_pg("cancel", fee)
        self.status = "cancelled"
        self.save()
        self.notify("cancelled")
        return result

    def refund(self): ...
    def calculate_fee(self): ...
    def notify(self, event): ...
    def call_pg(self, action, amount): ...
```

```text
After
orders/
  domain/
    exceptions.py
    value_objects.py
    policies.py
  models.py
  application/
    services.py
    ports.py
  infrastructure/
    payment_gateway.py
    notifier.py
```

**1. `cancel` 분리**

```python
# orders/models.py
class Order(models.Model):
    class Status(models.TextChoices):
        PAID = "paid"
        CANCELLED = "cancelled"
        REFUNDED = "refunded"
        SHIPPED = "shipped"

    def cancel(self, fee: Money) -> None:
        if self.status == self.Status.SHIPPED:
            raise OrderNotCancelable(self.id)
        if self.status == self.Status.CANCELLED:
            return

        self.cancel_fee_amount = fee.amount
        self.cancel_fee_currency = fee.currency
        self.status = self.Status.CANCELLED
```

**Reason — 책임 분리:** `Order.cancel()`은 “취소 가능한가, 취소되면 상태와 수수료가 어떻게 남는가”만 담당합니다. PG 호출, 저장, 알림은 변경 이유가 다르므로 모델 밖으로 나갑니다.

**2. `refund` 분리**

```python
class Order(models.Model):
    def mark_refunded(self, amount: Money) -> None:
        if self.status != self.Status.CANCELLED:
            raise OrderNotRefundable(self.id)
        self.refunded_amount = amount.amount
        self.status = self.Status.REFUNDED
```

환불 흐름은 application service가 담당합니다.

```python
class CancelOrderService:
    def __init__(
        self,
        orders: OrderRepository,
        fee_policy: CancellationFeePolicy,
        payment_gateway: PaymentGateway,
        notifier: OrderNotifier,
    ):
        self.orders = orders
        self.fee_policy = fee_policy
        self.payment_gateway = payment_gateway
        self.notifier = notifier

    def cancel(self, order_id: OrderId) -> None:
        order = self.orders.get(order_id)
        fee = self.fee_policy.calculate(order)

        with transaction.atomic():
            order.cancel(fee)
            self.orders.save(order)
            transaction.on_commit(lambda: self.notifier.cancelled(order.id))
```

PG 호출까지 동기 처리해야 한다면 `Order`가 아니라 service에서 합니다. 다만 DB 트랜잭션 안에서 외부 API를 오래 붙잡지 않도록, 보통은 `CancelRequested` 저장 후 `on_commit` 또는 outbox worker가 PG를 호출하게 두는 편이 안전합니다.

**3. `calculate_fee` → 정책 객체**

```python
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "KRW"

    def __post_init__(self):
        if self.amount < 0:
            raise InvalidMoney(self.amount)

@dataclass(frozen=True)
class OrderId:
    value: int

class CancellationFeePolicy:
    def calculate(self, order: Order) -> Money:
        if order.is_within_free_cancel_window():
            return Money(Decimal("0"))
        return Money(order.total_amount * Decimal("0.10"))
```

**Reason — 정책 객체:** 수수료율, 무료 취소 기간, 회원 등급별 정책은 주문 상태 전이와 다른 이유로 바뀝니다. `CancellationFeePolicy`는 DB/PG 없이 순수 단위 테스트가 가능합니다.

**4. `notify` → 포트**

```python
class OrderNotifier(Protocol):
    def cancelled(self, order_id: int) -> None: ...
    def refunded(self, order_id: int) -> None: ...
```

Django 이메일, Slack, Kakao 알림은 `infrastructure/notifier.py`에서 구현합니다. 호출은 `transaction.on_commit()` 뒤로 밀어 DB 롤백 후 알림이 나가는 회귀를 막습니다.

**5. `call_pg` → PG 포트/어댑터**

```python
class PaymentGateway(Protocol):
    def cancel_payment(self, order_id: OrderId, fee: Money) -> None: ...
    def refund_payment(self, order_id: OrderId, amount: Money) -> None: ...
```

Toss/Stripe 같은 SDK 응답 필드명은 `infrastructure/payment_gateway.py` 안에 가둡니다. 도메인에는 `charge_id`, `payment_token` 같은 PG 어휘를 넣지 않습니다.

**도메인 예외**

```python
class OrderDomainError(Exception): pass
class OrderNotCancelable(OrderDomainError): pass
class OrderNotRefundable(OrderDomainError): pass
class InvalidMoney(OrderDomainError): pass
```

**테스트 방향**

RED:
```python
def test_cancellation_fee_policy_after_free_window_returns_10_percent(order):
    fee = CancellationFeePolicy().calculate(order)

    assert fee == Money(Decimal("1000"))
```

```python
def test_cancel_order_when_shipped_raises_domain_error(order):
    order.status = Order.Status.SHIPPED

    with pytest.raises(OrderNotCancelable):
        order.cancel(Money(Decimal("0")))
```

```python
def test_cancel_service_saves_order_without_calling_notifier_before_commit(fake_orders, fake_notifier):
    service.cancel(OrderId(1))

    assert fake_orders.saved.status == Order.Status.CANCELLED
```

회귀 테스트는 세 층으로 둡니다: 정책 객체는 DB 없는 unit test, `Order.cancel/mark_refunded`는 상태 전이 unit test, application service는 `FakeRepository/FakeGateway/FakeNotifier`로 orchestration test. Django 통합 테스트에서는 `transaction.on_commit`, `assertNumQueries`, 실제 모델 저장 필드만 검증합니다.

실행 예:
```bash
pytest tests/isolated/orders/domain -q
pytest tests/isolated/orders/application -q
pytest tests/isolated/orders/integration -q
```

---
> **관련 스킬 참조:**
> - Django 서비스 레이어와 트랜잭션 경계 → **implementation-django** 스킬
> - 정책 객체, 값 객체, 도메인 예외 설계 → **architecture-ddd** 스킬