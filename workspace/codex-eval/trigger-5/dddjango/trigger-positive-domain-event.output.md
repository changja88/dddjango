**[주요 내용]**

DDD 기준으로는 “주문 완료”를 `Order` 애그리거트의 상태 전이로 만들고, 애그리거트가 **Domain Event를 기록**하게 둡니다. 즉시 Kafka/Celery/이메일을 호출하지 않습니다. 발행은 Application Service가 트랜잭션 경계에서 조율합니다.

| 도메인 용어 | 정의 | 코드 표현 | 금지 동의어 |
|---|---|---|---|
| 주문 완료 | 주문이 결제 확정 후 이행 가능한 상태가 된 사건 | `order.complete()`, `OrderCompleted` | `status="done"` 직접 할당 |
| 도메인 이벤트 | 주문 BC 내부에서 발생한 비즈니스 사실 | `OrderCompleted` | Kafka message, webhook payload |
| 통합 이벤트 | BC 밖으로 내보내는 공개 계약 | `OrderCompletedV1` | 내부 ORM 필드 전체 노출 |

권장 위치는 다음처럼 둡니다.

```text
apps/orders/
  domain/
    model/order/root.py
    events/internal.py
    events/published_language.py
    shared/aggregate_root.py
  application/
    services/complete_order.py
  infrastructure/
    persistence/django_order_repository.py
    outbox_relay.py
  models.py
```

핵심은 Domain Event와 Integration Event를 분리하는 것입니다.

```python
# domain/shared/aggregate_root.py
class AggregateRoot:
    def __init__(self) -> None:
        self._domain_events = []

    def _record_event(self, event) -> None:
        self._domain_events.append(event)

    def collect_events(self) -> list:
        events, self._domain_events = self._domain_events, []
        return events
```

```python
# domain/events/internal.py
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class OrderCompleted:
    order_id: str
    customer_id: str
    occurred_at: datetime
```

```python
# domain/events/published_language.py
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class OrderCompletedV1:
    event_id: str
    event_type: str
    schema_version: str
    occurred_at: datetime
    order_id: str
    customer_id: str
    total_amount_krw: int
```

```python
# domain/model/order/root.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Order(AggregateRoot):
    """
    Aggregate Root: Order
    INV-1: PAID 상태의 주문만 완료할 수 있다.
    INV-2: 완료된 주문은 다시 완료될 수 없다.
    """
    id: str
    customer_id: str
    status: str
    total_amount_krw: int
    version: int = 0

    def complete(self) -> None:
        if self.status == "COMPLETED":
            return
        if self.status != "PAID":
            raise InvalidOrderState("PAID 상태에서만 주문 완료 가능")

        self.status = "COMPLETED"
        self._record_event(
            OrderCompleted(
                order_id=self.id,
                customer_id=self.customer_id,
                occurred_at=datetime.now(),
            )
        )
```

Application Service가 트랜잭션과 발행 시점을 책임집니다.

```python
# application/services/complete_order.py
from django.db import transaction

class CompleteOrderService:
    def __init__(self, orders, outbox):
        self.orders = orders
        self.outbox = outbox

    def complete(self, order_id: str) -> None:
        with transaction.atomic():
            order = self.orders.get(order_id)
            order.complete()
            self.orders.save(order)  # 낙관적 잠금: version 조건 UPDATE

            for event in order.collect_events():
                if isinstance(event, OrderCompleted):
                    self.outbox.add(OrderCompletedV1.from_domain(event, order))
```

발행 기준은 이렇게 잡는 게 현실적입니다.

| 상황 | 선택 |
|---|---|
| 같은 Django 프로세스 내부 후처리, 손실 허용 가능 | `transaction.on_commit()` |
| 이메일/Celery enqueue처럼 커밋 후 실행 필요 | `transaction.on_commit(lambda: task.delay(...))` |
| 주문 완료를 배송/정산/CRM 등 다른 BC로 전달 | **Outbox + Relay** |
| Kafka/SNS/RabbitMQ 같은 외부 브로커 발행 | **Outbox 필수** |

`transaction.on_commit()`은 커밋 후 콜백일 뿐 영속 큐가 아닙니다. 프로세스가 죽으면 콜백이 유실될 수 있으므로, 주문 완료처럼 다른 BC가 의존하는 통합 이벤트는 `Order` 저장과 `OutboxMessage` 저장을 같은 트랜잭션에 넣고, 별도 Relay가 발행해야 합니다.

Outbox는 at-least-once delivery를 보장합니다. 컨슈머는 `event_id` 기반 Dedup 테이블 또는 도메인 상태 검사로 멱등성을 처리해야 합니다.

검증은 최소한 다음을 둡니다.

```python
def test_complete_order_records_domain_event():
    order = paid_order()
    order.complete()

    assert order.status == "COMPLETED"
    assert isinstance(order.collect_events()[0], OrderCompleted)


def test_complete_order_writes_outbox_after_state_change(db):
    service.complete(order_id)

    assert OrderModel.objects.get(id=order_id).status == "COMPLETED"
    assert OutboxMessage.objects.filter(
        event_type="order.completed.v1",
    ).exists()
```

요약하면, 도메인 모델은 “사건을 기록”하고, Application Service는 “트랜잭션 안에서 저장 및 Outbox 적재”를 하며, 실제 외부 발행은 “커밋 이후 Relay”가 담당하는 구조가 가장 안전합니다.

---
> **관련 스킬 참조:**
> - Django 구현·트랜잭션·서비스 레이어 → **implementation-django** 스킬