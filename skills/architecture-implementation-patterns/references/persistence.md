# 영속성 패턴

## 1. Data Mapper

> 출처: Martin Fowler, *Patterns of Enterprise Application Architecture* (2002)

> "A layer of Mappers that moves data between objects and a database while keeping them independent of each other and the mapper itself."

### 핵심 원칙: Persistence Ignorance

in-memory 객체는 **DB가 존재한다는 사실 자체를 모른다**. SQL 인터페이스 코드 없음, DB 스키마에 대한 지식 없음. Data Mapper 자체도 도메인 계층에 알려지지 않는다.

### Active Record와의 비교

| 기준 | Active Record | Data Mapper |
|---|---|---|
| 모델-DB 관계 | 강결합 (1:1, 같은 클래스) | 분리 (별도 매핑 레이어) |
| 적합한 경우 | CRUD 중심, 단순 로직 | 복잡한 비즈니스 로직 |
| 테스트 | DB 의존 | 독립 테스트 가능 |
| 스키마 유연성 | 제한적 | 높음 |
| 대표 구현 | Django ORM, Rails AR | SQLAlchemy Classical Mapping |

**적용 기준** (Fowler): 비즈니스 로직이 단순하면 Active Record, 복잡하면 (inheritance, strategies, 객체 그래프) Data Mapper가 필요하다.

### Cosmic Python의 원칙

> "Your ORM should import your model, and not the other way around."

- 일반적: 모델이 ORM에 의존 (ORM base class 상속)
- Data Mapper: ORM이 모델에 의존 (순수 도메인 클래스에 매핑)

---

## 2. Unit of Work

> 출처: Martin Fowler, *PoEAA* (2002)

> "Maintains a list of objects affected by a business transaction and coordinates the writing out of changes and the resolution of concurrency problems."

### 해결하는 문제

- 객체 변경 시마다 DB 호출하면 매우 작은 호출이 다수 발생
- 어떤 객체가 변경/추가/삭제되었는지 추적하지 않으면 일관성 유지 불가
- 트랜잭션을 열어두는 것은 비현실적

### 동작 방식

1. 비즈니스 트랜잭션 동안 변경된 객체를 추적
2. commit 시: 트랜잭션 열기 → 동시성 체크 → 변경분 DB 기록 → 커밋

### Repository와의 관계

| 패턴 | 역할 |
|---|---|
| Repository | **무엇을** 영속화할지 — 컬렉션 추상화 |
| Unit of Work | **언제/어떻게** 영속화할지 — 트랜잭션 추상화 |

실무에서 UoW가 Repository에 대한 접근을 제공하고, 트랜잭션 경계를 관리한다.

---

## 3. Repository

> 출처: Martin Fowler, *PoEAA* (2002) + Eric Evans, *DDD* (2003)

> "Mediates between the domain and data mapping layers using a collection-like interface for accessing domain objects."

### 핵심 특성

- **컬렉션처럼** 동작: `add()`, `remove()`, `get()`, `list()`
- DDD에서는 **Aggregate 당 하나의 Repository**
- DB 업데이트의 유일한 채널

### Cosmic Python의 구현 패턴

```python
from abc import ABC, abstractmethod


# Port: 도메인 계층에 위치
class AbstractBatchRepository(ABC):
    @abstractmethod
    def add(self, batch: Batch) -> None: ...

    @abstractmethod
    def get(self, reference: str) -> Batch | None: ...


# Adapter: 인프라 계층에 위치
class SqlAlchemyBatchRepository(AbstractBatchRepository):
    def __init__(self, session):
        self._session = session

    def add(self, batch: Batch) -> None:
        self._session.add(batch)

    def get(self, reference: str) -> Batch | None:
        return self._session.query(Batch).filter_by(reference=reference).first()


# 테스트용 Adapter
class FakeBatchRepository(AbstractBatchRepository):
    def __init__(self, batches: list[Batch] | None = None):
        self._batches = set(batches or [])

    def add(self, batch: Batch) -> None:
        self._batches.add(batch)

    def get(self, reference: str) -> Batch | None:
        return next((b for b in self._batches if b.reference == reference), None)
```

---

## 4. Identity Map

> 출처: Martin Fowler, *PoEAA* (2002)

> "Ensures that each object gets loaded only once by keeping every loaded object in a map."

### 2가지 이점

1. **참조 무결성**: 같은 DB 행에 대해 동일 객체 참조 보장
2. **성능 캐시**: DB 호출 감소

UoW 내부에 Identity Map이 포함되는 것이 일반적이다. SQLAlchemy Session이 대표적 예시.

---

## 5. Unit of Work + Repository 조합

```python
from abc import ABC, abstractmethod


class AbstractUnitOfWork(ABC):
    batches: AbstractBatchRepository

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.rollback()  # commit 안 했으면 자동 rollback

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    def __enter__(self):
        self._session = self._session_factory()
        self.batches = SqlAlchemyBatchRepository(self._session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self._session.close()

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()


# 사용 예시
def allocate(line: OrderLine, uow: AbstractUnitOfWork) -> str:
    with uow:
        batch = uow.batches.get("batch-001")
        batch.allocate(line)
        uow.commit()
        return batch.reference
```

### 트랜잭션 경계의 위치 — Repository 내부 commit 금지

**원칙**: 트랜잭션 경계는 **Use Case 수준(Application Service / Command
Handler)에서 결정**한다. Repository 내부 commit은 안티패턴이다.

```python
# 안티패턴 — Repository가 트랜잭션 경계 소유
class ErpStockRepository:
    def save(self, item):
        cursor.execute("UPDATE TB_INV_MASTER ...")
        conn.commit()                          # ← 금지

# 올바른 패턴 — Application Service가 commit
class ReserveStockHandler:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def handle(self, cmd: ReserveStockCommand) -> None:
        with self._uow:
            stock = self._uow.stock.get(cmd.code)
            stock.reserve(cmd.qty)             # 도메인 불변식 검증
            self._uow.stock.save(stock)        # save는 staging만, commit 안 함
            self._uow.commit()                 # ← 여기서 commit
        # 커밋 후 도메인 이벤트 디스패치
        for event in stock.collect_events():
            self._event_bus.dispatch(event)
```

**Repository 내부 commit이 만드는 3가지 문제:**
1. 다중 Aggregate를 원자적으로 갱신할 수 없다 (StockItem + StockReservation을
   같은 트랜잭션으로 묶지 못함)
2. 테스트에서 트랜잭션 롤백으로 격리 불가 — 각 save가 즉시 commit
3. 도메인 이벤트 디스패치 시점이 모호해진다 (commit 전 vs 후)

### Composition Root + Connection Pool

자격증명 하드코딩과 호출마다 새 client 생성을 막기 위해 **lru_cache 기반
싱글턴 client**를 Composition Root에 둔다.

```python
# 안티패턴
def reserve_stock(...):
    conn = cx_Oracle.connect("erp_user/pass@erp-db:1521/ERPDB")  # 매 호출 새 연결

# 올바른 패턴
from functools import lru_cache
from django.conf import settings

@lru_cache(maxsize=1)
def _erp_client() -> ErpOracleClient:
    """프로세스 생애주기 동안 단일 Client(Connection Pool) 공유."""
    return ErpOracleClient(
        dsn=settings.ERP_DSN,
        user=settings.ERP_USER,
        password=settings.ERP_PASSWORD,
        pool_min=2,
        pool_max=10,
    )

def build_reserve_stock_handler() -> ReserveStockHandler:
    return ReserveStockHandler(uow=ErpUnitOfWork(client=_erp_client()))
```

이 패턴은 (1) settings 외부화로 자격증명 누출 방지, (2) Connection Pool로
연결 비용 절감, (3) 테스트에서 `_erp_client()`를 monkeypatch로 Fake로 교체
가능하게 한다.

---

## 6. SQLAlchemy가 구현하는 패턴들

> 출처: Mike Bayer (zzzeek), SQLAlchemy 2.0 문서

| PoEAA 패턴 | SQLAlchemy 구현 |
|---|---|
| Data Mapper | `registry.map_imperatively()` (imperative/classical mapping) |
| Unit of Work | `Session` — 변경 추적, flush 시 일괄 반영 |
| Identity Map | `Session` 내부 — PK 기준 unique copy 유지 |
| Active Record-like | Declarative mapping (`DeclarativeBase` 상속) |

**Declarative vs Imperative**: 두 방식의 최종 결과는 동일하고 상호 운용 가능하다. Declarative는 편리하지만 Active Record에 가까운 느낌이고, Imperative(Classical)는 순수한 Data Mapper이다.

---

## 7. Django ORM에서의 고려사항

> 출처: Cosmic Python Appendix D

Django ORM은 Active Record 패턴이므로:

- SQLAlchemy의 classical mapper에 해당하는 메커니즘이 **존재하지 않음**
- Repository 적용 시 `to_domain()` / `from_domain()` **수동 변환 레이어** 필요
- UoW 적용 시 `transaction.set_autocommit(False)`로 수동 트랜잭션 관리
- 상당한 boilerplate 발생 — Django의 장점(admin, forms, migrations)을 잃을 수 있음

**실용적 권고**: 대부분의 Django 프로젝트에서는 **모델 메서드 + 서비스 함수**로 충분하다. 도메인이 정말 복잡해질 때만 점진적으로 도입한다. Django 프레임워크 관례는 **implementation-django** 스킬을 참조한다.

---

## 패턴 간 관계

```
Service Layer
  |
  v
Unit of Work ──── 트랜잭션 경계 관리 (commit / rollback)
  |
  ├── Repository ──── 컬렉션 추상화 (add / get / list)
  │       |
  │       v
  │   Data Mapper ──── 도메인 ↔ DB 변환
  │       |
  │       v
  │   Identity Map ──── 중복 로드 방지
  |
  v
Database
```
