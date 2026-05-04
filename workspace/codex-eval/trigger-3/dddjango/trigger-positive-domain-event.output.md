**주요 내용**

주문 완료는 `Order` 애그리거트의 상태 전이 결과다. 따라서 이벤트는 뷰나 Django `post_save` 시그널에서 만들지 말고, `Order.complete()` 같은 도메인 메서드 안에서 **기록**한다. 실제 발행은 애그리거트 저장 트랜잭션이 커밋된 뒤에 한다.

**Ubiquitous Language**

| 도메인 용어 | 정의 | 코드 표현 | 금지 동의어 |
|---|---|---|---|
| 주문 완료 | 결제/주문 불변식이 충족되어 주문이 완료 상태가 된 사건 | `OrderCompleted`, `order.complete()` | `paid_save`, `post_save_order`, `charge_success` |
| 도메인 이벤트 | 주문 BC 내부에서 발생한 비즈니스 사건 | `domain/events/internal/` | 외부 메시지 payload |
| 통합 이벤트 | 다른 BC/외부 시스템에 공개하는 계약 | `published_language/OrderCompletedV1` | 내부 모델 그대로 노출 |

권장 구조:

```text
apps/orders/
  domain/
    model/order/order.py
    events/internal/order_completed.py
    events/published_language/order_completed_v1.py
  application/
    services.py
  infrastructure/
    repositories.py
    outbox.py
    event_bus.py
```

핵심 모델은 이렇게 둔다.

```python
# apps/orders/domain/model/order/order.py
from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID

class OrderStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELED = "canceled"

@dataclass
class AggregateRoot:
    _events: list[object] = field(default_factory=list, init=False)

    def _record_event(self, event: object) -> None:
        self._events.append(event)

    def collect_events(self) -> list[object]:
        events, self._events = self._events, []
        return events

@dataclass
class Order(AggregateRoot):
    """Aggregate Root.

    Invariant:
    - 주문은 결제 확인 전 완료될 수 없다.
    - 완료된 주문은 다시 완료될 수 없다.
    """
    id: UUID
    customer_id: UUID
    status: OrderStatus
    total_amount_krw: int

    def complete(self) -> None:
        if self.status == OrderStatus.COMPLETED:
            return
        if self.status != OrderStatus.PENDING:
            raise InvalidOrderState("완료할 수 없는 주문 상태입니다.")

        self.status = OrderStatus.COMPLETED
        self._record_event(
            OrderCompleted(
                order_id=self.id,
                customer_id=self.customer_id,
                total_amount_krw=self.total_amount_krw,
            )
        )
```

```python
# apps/orders/domain/events/internal/order_completed.py
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

@dataclass(frozen=True)
class OrderCompleted:
    order_id: UUID
    customer_id: UUID
    total_amount_krw: int
    occurred_at: datetime = field(default_factory=datetime.utcnow)
```

Django 서비스 레이어에서 트랜잭션과 발행 시점을 통제한다.

```python
# apps/orders/application/services.py
from django.db import transaction

def complete_order(order_id):
    with transaction.atomic():
        order = order_repository.get(order_id)
        order.complete()
        order_repository.save(order)

        events = order.collect_events()

        transaction.on_commit(
            lambda: domain_event_bus.publish_many(events)
        )
```

이 방식은 **같은 Django 프로세스 안의 내부 후속 처리**에 적합하다. 예: 주문 완료 후 내부 프로젝션 갱신, 앱 내부 알림 생성, 로컬 캐시 무효화. `transaction.on_commit()`을 쓰면 DB 롤백 시 이벤트가 발행되지 않는다.

다만 다른 BC, 메시지 브로커, 이메일/알림, ERP 연동처럼 실패 재시도가 필요한 작업은 `on_commit()` 직접 발행보다 Outbox가 낫다.

```python
# transaction.atomic() 내부
events = order.collect_events()
outbox.save_many(
    OrderCompletedV1.from_domain_event(event)
    for event in events
)
```

```python
# apps/orders/domain/events/published_language/order_completed_v1.py
@dataclass(frozen=True)
class OrderCompletedV1:
    event_type: str
    schema_version: str
    order_id: str
    customer_id: str
    total_amount_krw: int

    @classmethod
    def from_domain_event(cls, event: OrderCompleted) -> "OrderCompletedV1":
        return cls(
            event_type="order.completed.v1",
            schema_version="1.0",
            order_id=str(event.order_id),
            customer_id=str(event.customer_id),
            total_amount_krw=event.total_amount_krw,
        )
```

정리하면 기준은 이렇다.

| 목적 | 이벤트 | 발행 시점 | Django 위치 |
|---|---|---|---|
| 주문 BC 내부 반응 | Domain Event | `transaction.on_commit()` 이후 | `domain_event_bus` |
| 다른 BC/외부 시스템 통합 | Integration Event | Outbox 저장 후 relay가 발행 | `infrastructure/outbox.py` |
| DB와 반드시 같이 성공해야 하는 내부 변경 | 이벤트보다 같은 트랜잭션 내 명시 호출 고려 | `atomic()` 내부 | application service |

Outbox는 at-least-once delivery를 보장한다. 컨슈머는 `event_id` 기반 dedup 또는 “이미 주문 완료 처리됨” 같은 도메인 상태 검사로 멱등성을 처리해야 한다.

검증은 최소한 다음을 둔다.

```python
def test_complete_order_records_event_after_state_change():
    order.complete()

    assert order.status == OrderStatus.COMPLETED
    assert isinstance(order.collect_events()[0], OrderCompleted)

def test_order_completed_event_is_not_published_before_commit(db):
    with transaction.atomic():
        complete_order(order_id)
        assert domain_event_bus.not_called()
```

---
> **관련 스킬 참조:**
> - 도메인 이벤트/애그리거트 설계 → **architecture-ddd** 스킬
> - Outbox와 트랜잭션 후 발행 구조 → **architecture-implementation-patterns** 스킬
> - Django 서비스 레이어와 `transaction.on_commit` → **implementation-django** 스킬