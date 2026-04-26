# 구현 패턴

## 6.1 패키지 구조

> **[의사결정 #8] External 채택**: 4계층 명확 분리를 기본으로 한다.

```
my_project/
├── src/
│   ├── ordering/                    # 바운디드 컨텍스트: 주문
│   │   ├── domain/                  # 도메인 계층 (의존성 없음)
│   │   │   ├── __init__.py
│   │   │   ├── model.py             # 엔티티, 값 객체, 애그리거트
│   │   │   ├── events.py            # 도메인 이벤트 정의
│   │   │   ├── commands.py          # 커맨드 정의
│   │   │   ├── specifications.py    # Specification 패턴
│   │   │   └── repository.py        # 리포지토리 인터페이스 (ABC)
│   │   │
│   │   ├── application/             # 응용 계층
│   │   │   ├── __init__.py
│   │   │   ├── services.py          # 유스케이스/응용 서비스
│   │   │   ├── handlers.py          # 커맨드/이벤트 핸들러
│   │   │   └── unit_of_work.py      # UoW 인터페이스
│   │   │
│   │   ├── infrastructure/          # 인프라 계층
│   │   │   ├── __init__.py
│   │   │   ├── orm.py               # SQLAlchemy 매핑
│   │   │   ├── repository.py        # 리포지토리 구현체
│   │   │   ├── unit_of_work.py      # UoW 구현체
│   │   │   └── event_publisher.py   # 이벤트 발행 구현
│   │   │
│   │   └── interface/               # 표현 계층 (입력 어댑터)
│   │       ├── __init__.py
│   │       ├── api.py               # REST API (FastAPI/Flask)
│   │       └── schemas.py           # 요청/응답 스키마
│   │
│   ├── inventory/                   # 바운디드 컨텍스트: 재고
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   └── interface/
│   │
│   └── shared_kernel/               # 공유 커널 (공통 값 객체)
│       ├── __init__.py
│       ├── money.py
│       └── events.py                # 통합 이벤트 기반 클래스
│
├── tests/
│   ├── unit/                        # 도메인 로직 단위 테스트
│   ├── integration/                 # 인프라 통합 테스트
│   └── e2e/                         # 엔드투엔드 테스트
│
└── pyproject.toml
```

**핵심 의존성 규칙:**
- `domain/` -- 어디에도 의존하지 않는다. 순수 Python만 사용
- `application/` -- `domain/`에만 의존한다
- `infrastructure/` -- `domain/`과 `application/`에 의존한다 (인터페이스 구현)
- `interface/` -- `application/`에 의존한다 (유스케이스 호출)

> Django 등 프레임워크 제약 시 [A]의 간소화된 구조(`views/`, `services/`, `domain/`, `infrastructure/`)를 차선으로 허용한다.

## 6.2 SQLAlchemy Data Mapper 패턴

> 출처: Cosmic Python

ORM은 도메인 모델을 임포트해야 하며, 도메인 모델이 ORM에 의존해서는 안 된다. Data Mapper 패턴의 상세 구현은 **architecture-implementation-patterns** 스킬을 참조한다.

## 6.3 Repository + Unit of Work 패턴

> 출처: Cosmic Python

```python
from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.orm import Session


# 도메인 계층: 추상 리포지토리
class AbstractBatchRepository(ABC):
    @abstractmethod
    def add(self, batch: Batch) -> None: ...

    @abstractmethod
    def get(self, reference: str) -> Optional[Batch]: ...


# 인프라 계층: SQLAlchemy 구현
class SqlAlchemyBatchRepository(AbstractBatchRepository):
    def __init__(self, session: Session):
        self._session = session

    def add(self, batch: Batch) -> None:
        self._session.add(batch)

    def get(self, reference: str) -> Optional[Batch]:
        return (
            self._session.query(Batch)
            .filter_by(reference=reference)
            .first()
        )


# Unit of Work: 트랜잭션 경계 관리
class AbstractUnitOfWork(ABC):
    batches: AbstractBatchRepository

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.rollback()

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    def __enter__(self):
        self._session: Session = self._session_factory()
        self.batches = SqlAlchemyBatchRepository(self._session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self._session.close()

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()


# 사용 예시: 응용 서비스에서 UoW 사용
class AllocationService:
    def allocate(self, line: OrderLine, uow: AbstractUnitOfWork) -> str:
        with uow:
            batch = uow.batches.get("batch-001")
            if batch is None:
                raise ValueError("배치를 찾을 수 없습니다")
            batch.allocate(line)
            uow.commit()
            return batch.reference
```

## 6.4 Event Sourcing

> 출처: Greg Young, Martin Fowler

> "Event Sourcing의 정의: 언제든 애플리케이션 상태를 날려버리고 이벤트 로그에서 자신 있게 재구축할 수 있다." -- Martin Fowler

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from uuid import uuid4


@dataclass(frozen=True)
class DomainEvent:
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class AccountOpened(DomainEvent):
    account_id: str = ""
    owner_name: str = ""
    initial_balance: int = 0


@dataclass(frozen=True)
class MoneyDeposited(DomainEvent):
    account_id: str = ""
    amount: int = 0


@dataclass(frozen=True)
class MoneyWithdrawn(DomainEvent):
    account_id: str = ""
    amount: int = 0


class EventSourcedAggregate(ABC):
    """이벤트 소싱 기반 애그리거트 루트의 기반 클래스"""

    def __init__(self):
        self._uncommitted_events: List[DomainEvent] = []
        self._version: int = 0

    def _apply(self, event: DomainEvent) -> None:
        self._route_event(event)
        self._uncommitted_events.append(event)
        self._version += 1

    @abstractmethod
    def _route_event(self, event: DomainEvent) -> None:
        ...

    def load_from_history(self, events: List[DomainEvent]) -> None:
        """저장된 이벤트를 순서대로 재생하여 상태를 복원"""
        for event in events:
            self._route_event(event)
            self._version += 1

    @property
    def uncommitted_events(self) -> List[DomainEvent]:
        return list(self._uncommitted_events)

    def clear_events(self) -> None:
        self._uncommitted_events.clear()


class BankAccount(EventSourcedAggregate):
    """이벤트 소싱 기반 은행 계좌 애그리거트"""

    def __init__(self):
        super().__init__()
        self.account_id: str = ""
        self.owner_name: str = ""
        self.balance: int = 0

    # --- 커맨드 메서드: 비즈니스 규칙 검증 후 이벤트 생성 ---

    def open(self, account_id: str, owner: str, initial_balance: int) -> None:
        if initial_balance < 0:
            raise ValueError("초기 잔액은 0 이상이어야 합니다")
        self._apply(AccountOpened(
            account_id=account_id,
            owner_name=owner,
            initial_balance=initial_balance,
        ))

    def deposit(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("입금액은 0보다 커야 합니다")
        self._apply(MoneyDeposited(account_id=self.account_id, amount=amount))

    def withdraw(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("출금액은 0보다 커야 합니다")
        if amount > self.balance:
            raise ValueError("잔액이 부족합니다")
        self._apply(MoneyWithdrawn(account_id=self.account_id, amount=amount))

    # --- 이벤트 핸들러: 이벤트를 적용하여 상태를 변경 (부작용 없음) ---

    def _route_event(self, event: DomainEvent) -> None:
        if isinstance(event, AccountOpened):
            self.account_id = event.account_id
            self.owner_name = event.owner_name
            self.balance = event.initial_balance
        elif isinstance(event, MoneyDeposited):
            self.balance += event.amount
        elif isinstance(event, MoneyWithdrawn):
            self.balance -= event.amount
```

## 6.5 Saga 패턴 (분산 트랜잭션)

> 출처: Hector Garcia-Molina & Kenneth Salem, "Sagas" (1987)

여러 애그리거트/서비스에 걸친 비즈니스 트랜잭션을 관리하는 패턴이다.

| 방식 | 설명 | 장점 | 단점 |
|------|------|------|------|
| Choreography | 각 서비스가 이벤트를 발행/구독하여 자율 실행 | 단순, 느슨한 결합 | 순환 의존 위험, 흐름 파악 어려움 |
| Orchestration | 중앙 오케스트레이터가 각 서비스에 지시 | 흐름이 명확, 서비스 추가 용이 | 오케스트레이터에 로직 집중 |

핵심은 **보상 트랜잭션(Compensating Transaction)**이다. 중간 단계가 실패하면, 이미 완료된 단계를 되돌리는 보상 행동을 실행한다. 보상 트랜잭션은 반드시 멱등성(idempotent)이 있어야 한다.

```python
from dataclasses import dataclass
from enum import Enum
from typing import List
import logging

logger = logging.getLogger(__name__)


class StepStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATED = "compensated"


@dataclass
class SagaStep:
    name: str
    action: callable
    compensation: callable
    status: StepStatus = StepStatus.PENDING


class SagaOrchestrator:
    """Saga 오케스트레이터: 단계별 실행과 보상을 관리"""

    def __init__(self, steps: List[SagaStep]):
        self._steps = steps
        self._completed_steps: List[SagaStep] = []

    def execute(self) -> bool:
        for step in self._steps:
            try:
                logger.info(f"실행 중: {step.name}")
                step.action()
                step.status = StepStatus.COMPLETED
                self._completed_steps.append(step)
            except Exception as e:
                logger.error(f"실패: {step.name} - {e}")
                step.status = StepStatus.FAILED
                self._compensate()
                return False
        return True

    def _compensate(self) -> None:
        """완료된 단계를 역순으로 보상"""
        for step in reversed(self._completed_steps):
            try:
                logger.info(f"보상 중: {step.name}")
                step.compensation()
                step.status = StepStatus.COMPENSATED
            except Exception as e:
                logger.error(f"보상 실패: {step.name} - {e}")
```

## 6.6 단순한 비즈니스 로직 패턴

> 출처: [B]

DDD의 전술 패턴이 모든 상황에 적합하지 않다. 단순한 비즈니스 로직을 위한 패턴도 알아야 한다.

**트랜잭션 스크립트** -- 절차지향 스크립트로 비즈니스 로직을 구현한다. 지원 하위 도메인에 적합하다.

```python
class FileConversionScript:
    """트랜잭션 스크립트 패턴 [B]
    - 단순한 절차지향 스크립트
    - 지원 하위 도메인, ETL 등에 적합
    """

    def convert_json_to_xml(self, job_id: str) -> None:
        db.start_transaction()
        try:
            job = db.load_next_job(job_id)
            json_data = load_file(job.source)
            xml_data = convert_json_to_xml(json_data)
            write_file(job.destination, xml_data)
            db.mark_job_as_completed(job)
            db.commit()
        except Exception:
            db.rollback()
            raise
```

## 6.7 마이크로서비스와 DDD

> 출처: Microsoft Learn -- Tactical DDD for Microservices

바운디드 컨텍스트는 마이크로서비스의 자연스러운 경계가 된다. 각 마이크로서비스는 하나의 바운디드 컨텍스트에 대응하며, 자체 데이터베이스를 소유하고, 다른 서비스와는 API 또는 이벤트로 통신한다.

| 컨텍스트 매핑 패턴 | 마이크로서비스 통합 방식 |
|----------------|-------------------|
| OHS + Published Language | REST API, gRPC, GraphQL |
| ACL | API Gateway, 어댑터 서비스 |
| Event-Driven | 메시지 브로커 (Kafka, RabbitMQ) |
| Shared Kernel | 공유 라이브러리 (최소화 필수) |
| Separate Ways | 기능 중복 허용 |

### 통합 이벤트와 도메인 이벤트의 구분

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class IntegrationEvent:
    """바운디드 컨텍스트 간 통신을 위한 통합 이벤트
    도메인 이벤트(내부용)와 달리, Published Language로 직렬화된다."""
    event_id: str
    event_type: str
    occurred_at: datetime
    source_context: str
    payload: dict


# 재고 컨텍스트의 ACL: 통합 이벤트를 내부 도메인 커맨드로 변환
class InventoryACL:
    """재고 컨텍스트의 충돌 방지 계층:
    주문 컨텍스트의 통합 이벤트를 재고 도메인의 언어로 번역"""

    def translate_order_completed(self, event: IntegrationEvent) -> list:
        commands = []
        for item in event.payload["items"]:
            commands.append({
                "type": "decrease_stock",
                "sku": item["sku"],
                "quantity": item["quantity"],
                "reason": f"주문 {event.payload['order_id']} 확정",
            })
        return commands
```
