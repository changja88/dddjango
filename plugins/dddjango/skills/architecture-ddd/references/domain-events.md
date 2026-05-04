# 도메인 이벤트와 Specification 패턴

## 3.7 도메인 이벤트 (Domain Event)

> 출처: [B][C], Jimmy Bogard, Cosmic Python
> **[의사결정 #7] External 채택**: UoW 커밋 전후 디스패치 타이밍을 명시한다.

비즈니스 도메인에서 발생한 중요한 사건을 나타낸다. 애그리거트 커맨드 실행의 결과로 발행된다.

**이벤트 수집 -> 디스패치 패턴:**
1. 애그리거트 안에 `_domain_events` 리스트를 두고 이벤트를 수집한다
2. Unit of Work가 커밋 **직전**(동일 트랜잭션 내 부수 효과) 또는 **직후**(외부 통합)에 디스패치한다
3. 디스패치 타이밍이 명시되지 않으면 이벤트 유실이나 트랜잭션 불일치가 발생한다

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, List, Type


@dataclass(frozen=True)
class DomainEvent:
    """도메인 이벤트 기본 클래스"""
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ItemAddedToCart(DomainEvent):
    cart_id: str = ""
    product_id: str = ""
    quantity: int = 0


@dataclass(frozen=True)
class CartCheckedOut(DomainEvent):
    cart_id: str = ""
    total_amount: int = 0


class AggregateRoot:
    """이벤트 수집 기능을 가진 애그리거트 루트 기반 클래스"""

    def __init__(self):
        self._domain_events: List[DomainEvent] = []

    def _raise_event(self, event: DomainEvent) -> None:
        """이벤트를 내부 컬렉션에 수집 (즉시 발행하지 않음)"""
        self._domain_events.append(event)

    @property
    def domain_events(self) -> List[DomainEvent]:
        return list(self._domain_events)

    def clear_events(self) -> None:
        self._domain_events.clear()


# === 이벤트 디스패처와 Unit of Work 연동 ===

class EventBus:
    """인프로세스 이벤트 버스 -- 이벤트 타입별 핸들러 등록 및 디스패치"""

    def __init__(self):
        self._handlers: Dict[Type[DomainEvent], List[Callable]] = {}

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers.get(type(event), []):
            handler(event)


class UnitOfWork:
    """Unit of Work -- 트랜잭션 경계에서 이벤트를 디스패치"""

    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus

    def commit(self) -> None:
        ...  # DB 커밋 로직

    def _dispatch_events(self, aggregate: AggregateRoot) -> None:
        """커밋 직전에 수집된 이벤트를 디스패치"""
        for event in aggregate.domain_events:
            self._event_bus.publish(event)
        aggregate.clear_events()
```

### Outbox 패턴

이벤트의 신뢰성 있는 발행을 보장하기 위해, 이벤트를 애그리거트와 같은 트랜잭션에서 Outbox 테이블에 저장하고, 별도 프로세스가 Outbox에서 이벤트를 읽어 메시지 브로커에 발행한다.

```python
@dataclass
class OutboxMessage:
    """Outbox 테이블에 저장되는 메시지"""
    id: str
    aggregate_type: str
    aggregate_id: str
    event_type: str
    payload: str         # JSON 직렬화된 이벤트 데이터
    created_at: datetime
    published: bool = False


class OutboxProcessor:
    """별도 프로세스/스케줄러: Outbox에서 미발행 메시지를 읽어 브로커에 발행"""

    def __init__(self, outbox_repo: "OutboxRepository", broker: "MessageBroker"):
        self._repo = outbox_repo
        self._broker = broker

    def process(self) -> None:
        messages = self._repo.find_unpublished()
        for msg in messages:
            self._broker.publish(topic=msg.event_type, message=msg.payload)
            msg.published = True
            self._repo.update(msg)
```

## 3.8 Specification 패턴

> 출처: Eric Evans & Martin Fowler, "Specifications" (1997)

비즈니스 규칙을 독립적인 객체로 캡슐화하고, 논리 연산(AND, OR, NOT)으로 조합할 수 있게 하는 패턴이다.

### 세 가지 용도

| 용도 | 설명 | 예시 |
|------|------|------|
| 검증 (Validation) | 객체가 비즈니스 규칙을 만족하는지 확인 | `eligible_for_premium.is_satisfied_by(customer)` |
| 선택 (Selection/Query) | 컬렉션에서 조건에 맞는 객체를 필터링 | `[c for c in customers if spec.is_satisfied_by(c)]` |
| 생성 (Construction) | 규칙을 만족하는 새 객체를 생성하도록 빌더에 전달 | 팩토리가 Specification을 참조하여 기본값 결정 |

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar("T")


class Specification(ABC, Generic[T]):
    """Specification 패턴 기본 클래스"""

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        ...

    def __and__(self, other: Specification[T]) -> AndSpecification[T]:
        return AndSpecification(self, other)

    def __or__(self, other: Specification[T]) -> OrSpecification[T]:
        return OrSpecification(self, other)

    def __invert__(self) -> NotSpecification[T]:
        return NotSpecification(self)


class AndSpecification(Specification[T]):
    def __init__(self, left: Specification[T], right: Specification[T]):
        self._left = left
        self._right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return (
            self._left.is_satisfied_by(candidate)
            and self._right.is_satisfied_by(candidate)
        )


class OrSpecification(Specification[T]):
    def __init__(self, left: Specification[T], right: Specification[T]):
        self._left = left
        self._right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return (
            self._left.is_satisfied_by(candidate)
            or self._right.is_satisfied_by(candidate)
        )


class NotSpecification(Specification[T]):
    def __init__(self, spec: Specification[T]):
        self._spec = spec

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self._spec.is_satisfied_by(candidate)


# 실무 적용 예시
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Customer:
    id: str
    name: str
    total_purchases: int
    registered_at: datetime
    is_verified: bool


class IsVerified(Specification[Customer]):
    def is_satisfied_by(self, customer: Customer) -> bool:
        return customer.is_verified


class HasMinimumPurchases(Specification[Customer]):
    def __init__(self, minimum: int):
        self._minimum = minimum

    def is_satisfied_by(self, customer: Customer) -> bool:
        return customer.total_purchases >= self._minimum


class RegisteredMoreThanDaysAgo(Specification[Customer]):
    def __init__(self, days: int):
        self._days = days

    def is_satisfied_by(self, customer: Customer) -> bool:
        cutoff = datetime.now() - timedelta(days=self._days)
        return customer.registered_at <= cutoff


# 조합하여 복합 비즈니스 규칙 생성
eligible_for_premium = (
    IsVerified()
    & HasMinimumPurchases(minimum=100_000)
    & RegisteredMoreThanDaysAgo(days=90)
)
```
