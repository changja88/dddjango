# CQRS (Command Query Responsibility Segregation)

## 1. CQS에서 CQRS로

### CQS (Command-Query Separation)

> 출처: Bertrand Meyer, *Object-Oriented Software Construction* (1988)

> "Asking a question should not change the answer."

메서드 수준의 원칙: 모든 메서드는 **Command**(상태 변경, 값 반환 없음) 또는 **Query**(값 반환, 상태 변경 없음) 중 하나여야 한다. 분산 시스템에서 Query는 본질적으로 멱등(idempotent)이지만 Command는 그렇지 않다는 점에서 더욱 중요해진다.

### CQRS

> 출처: Greg Young (2010)

> "CQRS is simply the creation of two objects where there was previously only one. The separation occurs based upon whether the methods are a command or a query."

CQS를 **메서드 수준에서 모델(객체) 수준으로 확장**한 것이다. 하나의 객체를 Command 객체와 Query 객체 두 개로 분리한다.

---

## 2. 핵심 원칙

### CQRS는 최상위 아키텍처가 아니다

> "CQRS is not a top-level architecture. CQRS can be called an architectural pattern." — Greg Young

시스템 전체에 적용하지 않고, **특정 Bounded Context 내에서 선택적으로 적용**한다.

### Command Model vs Query Model

| 측면 | Command Model (Write) | Query Model (Read) |
|---|---|---|
| 목적 | 비즈니스 로직, 검증, 불변식 보호 | 데이터 표현 최적화 |
| 구조 | Aggregate 패턴, 도메인 로직 포함 | DTO, 비정규화된 뷰, 도메인 로직 없음 |
| 최적화 대상 | 일관성, 트랜잭션 무결성 | 쿼리 성능, 프레젠테이션 |

### Task-Based UI와의 관계

CQRS는 CRUD에서 벗어나 **비즈니스 의도를 표현하는 Command** 중심으로 전환을 가능하게 한다. "Set ReservationStatus to Reserved" 대신 "Book hotel room"으로 표현한다.

---

## 3. 구현 수준 (Martin Fowler의 구분)

> 출처: Martin Fowler, *bliki: CQRS* (2011)

### 수준 1: 동일 DB, 분리된 모델

```
[Client] → [Command Model] → [Database] ← [Query Model] ← [Client]
```

- 읽기/쓰기의 in-memory 모델만 분리, 같은 DB 공유
- 동기화 문제 없음, 가장 낮은 복잡도

### 수준 2: 별도 DB

```
[Client] → [Write Model] → [Write DB] --events→ [Read DB] ← [Read Model] ← [Client]
```

- 읽기/쓰기를 독립적으로 스케일링
- 저장소 기술을 다르게 선택 가능 (Write: RDBMS, Read: Document DB)
- **Eventual Consistency** 발생

### 수준 3: Event 기반

- Write 모델이 모든 업데이트에 대해 이벤트를 생성
- Read 모델을 MemoryImage로 구성 (DB 접근 최소화)
- Event Sourcing과 자연스럽게 결합

---

## 4. Event Sourcing과의 관계

> "You can use CQRS without Event Sourcing, but with Event Sourcing you must use CQRS." — Greg Young

| 조합 | 실용성 |
|---|---|
| CQRS 단독 (전통 RDBMS) | 완전히 실용적 |
| Event Sourcing + CQRS | 시너지 — Event Store가 Write Model, Projection이 Read Model |
| Event Sourcing 단독 | 비실용적 — 쿼리 성능 문제로 CQRS가 사실상 필수 |

---

## 5. 적용 판단 기준

### 적합한 경우 (Microsoft Azure Architecture Center)

- 여러 사용자가 동시에 동일 데이터를 수정하는 **협업 환경**
- 복잡한 프로세스를 안내하는 **Task-based UI**
- 읽기 >> 쓰기 **비대칭 부하**에서 독립 스케일링 필요
- 읽기/쓰기 팀 분리가 가능한 **팀 구조**
- 비즈니스 규칙이 자주 변경되는 **진화하는 시스템**

### 부적합한 경우

- 도메인이나 비즈니스 규칙이 **단순**할 때
- 단순한 CRUD 스타일 UI로 **충분**할 때
- 시스템 **전체**에 적용하려 할 때 (안티패턴)

### Fowler의 경고

> "For most systems CQRS adds risky complexity."

적합하지 않은 도메인에 CQRS를 사용하면 복잡성이 증가하여 생산성이 떨어지고 위험이 높아진다. DDD의 혜택을 받을 수 있는 **복잡한 도메인에만** 적합하다.

---

## 6. 코드 구조 예시

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


# === Command Side ===

@dataclass(frozen=True)
class RateProduct:
    """Command: 비즈니스 의도를 표현"""
    product_id: str
    user_id: str
    rating: int


class ProductCommandHandler:
    """Command를 받아 Aggregate를 통해 비즈니스 로직 실행"""

    def __init__(self, repository: "ProductRepository"):
        self._repository = repository

    def handle_rate_product(self, command: RateProduct) -> None:
        product = self._repository.get(command.product_id)
        product.rate(command.user_id, command.rating)
        self._repository.save(product)


# === Query Side ===

@dataclass(frozen=True)
class ProductDisplay:
    """Query 결과: 프레젠테이션에 최적화된 DTO"""
    product_id: str
    name: str
    average_rating: float
    review_count: int


class ProductQueryService(ABC):
    """Read Model: 도메인 로직 없이 데이터 조회"""

    @abstractmethod
    def find_by_id(self, product_id: str) -> ProductDisplay: ...

    @abstractmethod
    def find_top_rated(self, limit: int = 10) -> list[ProductDisplay]: ...
```
