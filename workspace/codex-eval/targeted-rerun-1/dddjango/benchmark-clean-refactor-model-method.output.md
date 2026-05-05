**[주요 내용]**

현재 메서드의 문제는 “한 메서드가 네 가지 변경 이유”를 가진다는 점입니다.

| 책임 | 바뀌는 이유 | 위치 |
|---|---|---|
| 도메인 검증 | 업무 규칙 변경 | model 또는 domain method |
| 상태 변경 | 상태 전이 규칙 변경 | model method |
| 외부 API 호출 | 업체/SDK/HTTP 계약 변경 | gateway/adapter |
| `save()`/transaction | 저장 방식, 동시성, 배포 정책 변경 | application service |

모델에는 **순수 도메인 규칙과 상태 전이만** 남기는 게 좋습니다. 외부 API 호출과 `save()`는 모델 밖으로 빼세요.

```python
# Before
class Order(models.Model):
    def approve_payment(self, card_token: str) -> None:
        if self.status != self.Status.PENDING:
            raise ValidationError("결제 대기 상태가 아닙니다.")

        response = payment_client.charge(card_token, self.total_price)

        if not response.approved:
            self.status = self.Status.PAYMENT_FAILED
            self.save(update_fields=["status"])
            return

        self.payment_key = response.payment_key
        self.status = self.Status.PAID
        self.save(update_fields=["payment_key", "status"])
```

리팩터링 후 모델은 외부 세계를 모르게 합니다.

```python
# orders/models.py
class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        PAID = "paid"
        PAYMENT_FAILED = "payment_failed"

    def mark_paid(self, payment_key: str) -> None:
        if self.status != self.Status.PENDING:
            raise OrderNotPayableError

        self.payment_key = payment_key
        self.status = self.Status.PAID

    def mark_payment_failed(self) -> None:
        if self.status != self.Status.PENDING:
            raise OrderNotPayableError

        self.status = self.Status.PAYMENT_FAILED
```

외부 API는 포트로 감싸고, SDK 응답은 도메인 어휘로 번역합니다.

```python
# orders/ports.py
from typing import Protocol

class PaymentGateway(Protocol):
    def charge(self, *, order_id: int, amount: int, token: str) -> "PaymentResult": ...
```

```python
# orders/services.py
from django.db import transaction

def order_approve_payment(
    *,
    order_id: int,
    card_token: str,
    payment_gateway: PaymentGateway,
) -> None:
    with transaction.atomic():
        order = Order.objects.select_for_update().get(id=order_id)

        result = payment_gateway.charge(
            order_id=order.id,
            amount=order.total_price,
            token=card_token,
        )

        if result.approved:
            order.mark_paid(result.payment_key)
            order.save(update_fields=["payment_key", "status"])
        else:
            order.mark_payment_failed()
            order.save(update_fields=["status"])
```

단, 외부 API가 “DB 커밋 이후에만 실행되어야 하는 부작용”이라면 `transaction.on_commit()`을 사용합니다. 예를 들어 알림, 웹훅 발행, 이메일, 외부 시스템 동기화는 모델이나 트랜잭션 내부에서 바로 호출하지 않습니다.

```python
with transaction.atomic():
    order.mark_paid(payment_key)
    order.save(update_fields=["payment_key", "status"])

    transaction.on_commit(
        lambda: external_notifier.payment_approved(order.id)
    )
```

추천하는 작은 리팩터링 순서는 이렇습니다.

1. 현재 모델 메서드에서 외부 API 호출을 먼저 gateway 함수로 감싼다. 동작은 그대로 둔다.
2. SDK 응답 객체를 모델에 넘기지 않고 `PaymentResult` 같은 내부 결과 객체로 번역한다.
3. 모델 메서드를 `mark_paid()`, `mark_payment_failed()`처럼 저장하지 않는 상태 전이 메서드로 바꾼다.
4. 기존 호출부에 application service를 만들고 `gateway 호출 → model 상태 전이 → save` 순서로 옮긴다.
5. `save(update_fields=...)`, `transaction.atomic()`, 필요 시 `select_for_update()` 또는 낙관적 잠금을 서비스 경계에 둔다.
6. 외부 알림성 부작용은 `transaction.on_commit()`으로 커밋 이후 실행한다.

검증은 최소한 아래를 잡으면 됩니다.

```bash
python manage.py check
pytest tests/orders/test_order_domain.py
pytest tests/orders/test_order_payment_service.py
```

테스트 포인트는 세 가지입니다.

- `Order.mark_paid()`는 외부 API와 DB 없이 순수하게 상태만 바꾼다.
- 결제 실패/성공 시 service가 fake gateway를 사용해 올바른 상태와 `save()` 결과를 만든다.
- 커밋 이후 부작용은 `transaction.on_commit()` 경로로만 실행된다.

---
> **관련 스킬 참조:**
> - Django service layer / transaction 경계 → **implementation-django** 스킬
> - 도메인 규칙과 외부 시스템 분리 → **architecture-implementation-patterns** 스킬
> - 상태 전이와 불변식 모델링 → **architecture-ddd** 스킬