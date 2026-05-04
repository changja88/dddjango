현재 `/private/tmp/dddjango-codex-eval`에는 `config.toml`이나 Django 코드가 없어서, 레포 맞춤 설계 대신 일반적인 Django + DDD 기준 구조로 제안합니다.

DDD 기준에서는 **주문 완료 자체는 도메인 모델의 책임**이고, **이벤트 저장/발행/외부 메시지 전송은 애플리케이션 계층 또는 인프라 계층의 책임**으로 나누는 게 좋습니다.

**권장 구조**

```text
orders/
  domain/
    models.py          # Order aggregate
    events.py          # OrderCompleted 같은 domain event
    repositories.py    # Repository interface
  application/
    services.py        # CompleteOrderService
    event_bus.py       # DomainEventBus interface
  infrastructure/
    django_models.py   # Django ORM model
    repositories.py    # DjangoOrderRepository
    event_bus.py       # Celery/Kafka/SNS 등 실제 발행 구현
    outbox.py          # Outbox 저장 모델/퍼블리셔
  views.py             # HTTP entrypoint
```

핵심 흐름은 다음이 좋습니다.

```text
View
 -> Application Service
   -> Order.complete()
      -> OrderCompleted domain event 생성
   -> Repository.save(order)
   -> transaction.on_commit(...)
      -> EventBus.publish(events)
```

도메인 이벤트는 Django signal보다 명시적인 객체로 두는 편이 DDD에 더 잘 맞습니다.

```python
# orders/domain/events.py
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class OrderCompleted:
    order_id: UUID
    user_id: UUID
    completed_at: datetime
```

Aggregate는 상태 변경과 이벤트 기록만 담당합니다.

```python
# orders/domain/models.py
from django.utils import timezone
from .events import OrderCompleted


class Order:
    def __init__(self, id, user_id, status):
        self.id = id
        self.user_id = user_id
        self.status = status
        self._events = []

    def complete(self):
        if self.status == "COMPLETED":
            return

        if self.status != "PAID":
            raise ValueError("Only paid orders can be completed")

        self.status = "COMPLETED"
        self._events.append(
            OrderCompleted(
                order_id=self.id,
                user_id=self.user_id,
                completed_at=timezone.now(),
            )
        )

    def pull_events(self):
        events = self._events[:]
        self._events.clear()
        return events
```

Application Service는 트랜잭션 경계를 잡고, 커밋 이후 이벤트를 발행합니다.

```python
# orders/application/services.py
from django.db import transaction


class CompleteOrderService:
    def __init__(self, order_repository, event_bus):
        self.order_repository = order_repository
        self.event_bus = event_bus

    def execute(self, order_id):
        with transaction.atomic():
            order = self.order_repository.get(order_id)
            order.complete()

            events = order.pull_events()
            self.order_repository.save(order)

            transaction.on_commit(
                lambda: self.event_bus.publish_all(events)
            )
```

단, 외부 브로커로 반드시 전달되어야 하는 이벤트라면 `transaction.on_commit`만으로는 부족할 수 있습니다. 프로세스가 커밋 직후 죽으면 이벤트가 유실될 수 있기 때문입니다. 운영 환경에서는 **Transactional Outbox 패턴**을 추천합니다.

```text
transaction.atomic()
  1. Order 상태 저장
  2. OutboxEvent row 저장
commit

별도 worker
  1. 미발행 OutboxEvent 조회
  2. Kafka/Celery/SNS/RabbitMQ 등에 publish
  3. published_at 기록
```

정리하면:

- `Order.complete()`에서 `OrderCompleted` 이벤트를 만든다.
- Django View나 Serializer에서 이벤트를 만들지 않는다.
- Django signal은 숨은 흐름이 많아 핵심 도메인 이벤트에는 비추천한다.
- 단순 내부 후처리는 `transaction.on_commit`으로 충분하다.
- 외부 시스템 연동, 결제/배송/알림처럼 유실되면 안 되는 경우는 Outbox 패턴을 쓴다.
- 이벤트 핸들러는 주문 도메인의 핵심 로직을 직접 바꾸지 않고, 알림/배송요청/분석로그 같은 후속 작업을 담당하게 둔다.