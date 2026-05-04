**[주요 내용]**

지금 구조의 핵심 문제는 모델 메서드가 한 유스케이스 전체를 혼자 처리한다는 점입니다. 검증, 외부 API, 상태 전이, 영속화는 변경 이유가 서로 다르므로 한 메서드에 묶이면 테스트가 어렵고, 트랜잭션 롤백과 외부 호출의 정합성도 깨지기 쉽습니다.

리팩터링 방향은 이렇게 잡는 게 좋습니다.

```python
# Before
class Order(models.Model):
    def approve(self):
        if self.status != self.Status.PENDING:
            raise ValidationError("승인할 수 없습니다.")

        result = payment_client.approve(self.payment_key)

        if not result.ok:
            raise ValidationError("결제 승인 실패")

        self.status = self.Status.APPROVED
        self.approved_at = timezone.now()
        self.save()
```

```python
# After: models.py
class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "대기"
        APPROVED = "approved", "승인"
        FAILED = "failed", "실패"

    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.PENDING,
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    def approve(self, *, approved_at):
        if self.status != self.Status.PENDING:
            raise InvalidOrderState("대기 상태의 주문만 승인할 수 있습니다.")

        self.status = self.Status.APPROVED
        self.approved_at = approved_at
```

```python
# services.py
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone


def order_approve(*, order_id, payment_gateway):
    with transaction.atomic():
        order = get_object_or_404(Order.objects.select_for_update(), pk=order_id)

        payment_gateway.approve(payment_key=order.payment_key)

        order.approve(approved_at=timezone.now())
        order.full_clean()
        order.save(update_fields=["status", "approved_at"])

        transaction.on_commit(
            lambda: payment_gateway.notify_order_approved(order_id=order.id)
        )

    return order
```

```python
# selectors.py
def order_get_for_approval(*, order_id):
    return get_object_or_404(Order.objects.select_for_update(), pk=order_id)
```

**[Reason] SRP / CQS / Django Service Layer** -- 모델은 도메인 상태 전이와 불변식만 담당하고, 서비스 함수가 유스케이스 흐름을 조율합니다. `approve()`는 상태를 바꾸는 커맨드이므로 외부 API 결과를 조회하거나 저장까지 같이 처리하지 않는 편이 좋습니다.

**[Reason] 트랜잭션과 부수 효과 분리** -- 외부 API, 이메일, 알림 같은 되돌릴 수 없는 작업은 DB 트랜잭션과 조심스럽게 분리해야 합니다. 트랜잭션 성공 후에만 실행되어야 하는 알림은 `transaction.on_commit()`으로 넘기고, 결제 승인처럼 반드시 DB 상태 변경 전에 성공해야 하는 호출은 서비스 계층에서 명시적으로 호출합니다. 장애 복구와 재시도가 중요한 외부 연동이면 `on_commit`보다 Outbox 패턴을 검토하세요.

**[Reason] Django 관용성** -- Django에서는 모든 도메인에 Repository/UoW를 강제하기보다, 대부분은 `models.py`의 상태 전이 메서드 + `services.py`의 커맨드 함수 + `selectors.py`의 읽기 함수 조합이 실용적입니다. 도메인이 복잡해지고 외부 시스템이 많아질 때만 포트/어댑터나 Repository를 점진적으로 도입하는 편이 낫습니다.

구체적인 분리 기준은 다음처럼 두면 됩니다.

| 책임 | 둘 위치 |
|---|---|
| 입력 형식 검증 | Form, Django Ninja Schema, API 계층 |
| 모델 불변식 | `clean()` + `CheckConstraint` |
| 상태 전이 규칙 | 모델 메서드 `approve()`, `cancel()` |
| 유스케이스 조율 | `services.py`의 `order_approve()` |
| 읽기 쿼리 | `selectors.py` |
| 외부 API | 서비스에서 주입받는 gateway/client |
| 저장 | 서비스 계층에서 `save(update_fields=...)` |
| 커밋 후 알림 | `transaction.on_commit()` 또는 Outbox |

모델 메서드 이름도 `update_status("approved")`보다 `approve()`, `cancel()`, `fail_payment()`처럼 유비쿼터스 언어를 드러내는 명령형 이름이 좋습니다. 상태값은 문자열 튜플보다 `models.TextChoices`로 고정하고, 잘못된 상태 전이는 `ValidationError`를 뭉뚱그려 쓰기보다 `InvalidOrderState` 같은 도메인 예외로 표현하는 편이 테스트와 호출부 처리가 명확합니다.

외부 API 클라이언트는 모델에서 직접 import하지 말고 서비스 함수에 인자로 주입하세요. 그러면 테스트에서 fake gateway를 넣어 “API 성공”, “API 실패”, “DB 롤백 시 on_commit 미실행” 같은 케이스를 독립적으로 검증할 수 있습니다.

---
> **관련 스킬 참조:**
> - Django 서비스 레이어와 모델 리팩터링 → **implementation-django** 스킬
> - SRP/CQS/의존성 분리 → **implementation-cleancode** 스킬
> - 상태 전이와 애그리거트 책임 분리 → **architecture-ddd** 스킬