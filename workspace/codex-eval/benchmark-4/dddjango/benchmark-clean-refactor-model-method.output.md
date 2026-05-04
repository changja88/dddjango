**주요 내용**

핵심 방향은 `Django model method = 순수 도메인 규칙 + 상태 전이`까지만 남기고, `외부 API 호출`, `트랜잭션`, `save()`는 애플리케이션 서비스로 올리는 것입니다. 지금 구조는 CQS 위반입니다. 한 메서드가 “검증한다”, “외부 시스템을 호출한다”, “상태를 바꾼다”, “저장한다”를 동시에 하므로 테스트도 어렵고 실패 지점도 숨겨집니다.

[Before]

```python
class Order(models.Model):
    def confirm(self) -> None:
        if self.status != self.Status.REQUESTED:
            raise ValidationError("invalid status")

        external_api.notify_order_confirmed(self.id)

        self.status = self.Status.CONFIRMED
        self.confirmed_at = timezone.now()
        self.save()
```

[After]

```python
class InvalidOrderState(Exception):
    pass


class Order(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        CONFIRMED = "confirmed", "Confirmed"

    def confirm(self, confirmed_at: datetime) -> None:
        if self.status != self.Status.REQUESTED:
            raise InvalidOrderState("order must be requested before confirmation")

        self.status = self.Status.CONFIRMED
        self.confirmed_at = confirmed_at
```

```python
class OrderNotifier(Protocol):
    def order_confirmed(self, order_id: int) -> None:
        ...


@transaction.atomic
def confirm_order(order_id: int, notifier: OrderNotifier) -> None:
    order = (
        Order.objects
        .select_for_update()
        .get(id=order_id)
    )

    order.confirm(confirmed_at=timezone.now())
    order.full_clean()
    order.save(update_fields=["status", "confirmed_at", "updated_at"])

    transaction.on_commit(lambda: notifier.order_confirmed(order.id))
```

[Reason] Clean Code / DDD / Django Convention -- 모델은 도메인 불변식과 상태 전이만 담당합니다. 외부 API는 포트 `OrderNotifier` 뒤로 숨기고, 실제 호출은 트랜잭션 커밋 이후 `transaction.on_commit()`에서 실행합니다. 이렇게 해야 DB 롤백 후 외부 알림만 나가는 불일치를 피할 수 있습니다.

검증도 한곳에 몰지 말고 성격별로 나누는 편이 좋습니다.

| 검증 종류 | 위치 |
|---|---|
| 요청 형식, 필수값, 타입 | Form, Django Ninja Schema |
| 도메인 불변식, 상태 전이 | 모델 메서드 또는 값 객체 |
| DB 수준 제약 | `CheckConstraint`, `UniqueConstraint` |
| 외부 API 응답 검증 | 인프라 어댑터 또는 애플리케이션 서비스 |

작게 리팩터링하는 순서는 이렇게 잡는 게 안전합니다.

1. 현재 모델 메서드의 기존 동작을 테스트로 고정합니다. 성공, 잘못된 상태, 외부 API 실패, 저장 여부를 분리해서 잡습니다.
2. 외부 API 호출을 `Protocol` 인터페이스와 어댑터 클래스로 추출합니다. 아직 호출 위치는 바꾸지 않아도 됩니다.
3. 모델 메서드에서 `save()`를 제거하고 상태 변경만 남깁니다. 메서드 이름도 `validate_and_call_and_save()`식이 아니라 `confirm()`, `cancel()`, `mark_paid()`처럼 도메인 동사로 바꿉니다.
4. `confirm_order()` 같은 애플리케이션 서비스를 만들고 `transaction.atomic`, row lock, `full_clean()`, `save(update_fields=...)`를 그쪽으로 옮깁니다.
5. 알림, 이메일, 외부 동기화 같은 부수 효과는 `transaction.on_commit()`으로 이동합니다. 결제 승인처럼 외부 결과가 상태 전이를 결정하는 작업은 멱등성 키나 outbox까지 검토합니다.
6. 모델 단위 테스트는 외부 API mock 없이 돌리고, 서비스 테스트에서만 notifier mock과 트랜잭션 후 콜백을 검증합니다.

검증 단계는 최소한 이 정도가 필요합니다.

```python
def test_order_confirm_changes_state_without_saving_or_calling_api():
    order = Order(status=Order.Status.REQUESTED)

    order.confirm(confirmed_at=timezone.now())

    assert order.status == Order.Status.CONFIRMED


def test_confirm_order_calls_notifier_after_commit(db, mocker):
    notifier = mocker.Mock(spec=OrderNotifier)
    order = Order.objects.create(status=Order.Status.REQUESTED)

    with TestCase.captureOnCommitCallbacks(execute=True):
        confirm_order(order.id, notifier)

    notifier.order_confirmed.assert_called_once_with(order.id)
```

실행 확인:

```bash
python manage.py test
python manage.py check
```

---
> **관련 스킬 참조:**
> - 모델에서 부작용 제거와 서비스 레이어 분리 → **implementation-django** 스킬
> - 순수 도메인 규칙과 상태 전이 설계 → **architecture-ddd** 스킬
> - 외부 API를 포트/어댑터로 격리 → **architecture-implementation-patterns** 스킬