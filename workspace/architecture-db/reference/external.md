# 데이터베이스 설계 — 외부 자료

---

## 1. 정규화 (1NF — BCNF)

**함수적 종속(Functional Dependency)**: 속성 X가 속성 Y를 함수적으로 결정한다 (X → Y)는 X의 각 값이 정확히 하나의 Y 값과 대응됨을 의미한다.

| 정규형 | 조건 | 위반 예시 |
|--------|------|----------|
| **1NF** | 모든 컬럼이 원자값, 행이 고유 식별 가능, 반복 그룹 없음 | 하나의 컬럼에 여러 값 저장 |
| **2NF** | 1NF + 부분 종속 제거 (모든 비주요 속성이 전체 기본키에 종속) | 복합키 (StudentID, CourseID)에서 StudentName이 StudentID에만 종속 |
| **3NF** | 2NF + 이행 종속 제거 (비주요 속성이 다른 비주요 속성에 종속 불가) | StudentID → CourseID → Instructor |
| **BCNF** | 3NF + 모든 함수적 종속 X → Y에서 X가 슈퍼키 | 3NF보다 엄격, 후보키가 아닌 결정자 제거 |

**핵심**: 각 정규형은 특정 이상(갱신/삽입/삭제)을 순차적으로 제거한다. 과도한 정규화는 JOIN 증가로 읽기 성능 저하, 과소 정규화는 데이터 불일치 유발. 언제 멈출지가 아키텍처 트레이드오프다.

> 출처: [DigitalOcean - Database Normalization](https://www.digitalocean.com/community/tutorials/database-normalization), [GeeksforGeeks - Normal Forms in DBMS](https://www.geeksforgeeks.org/dbms/normal-forms-in-dbms/)

---

## 2. 인덱스 설계 베스트 프랙티스

### 2.1 복합 인덱스 컬럼 순서

복합 인덱스는 선언 순서대로 정렬된 B-tree이다.

**최좌선 접두사 규칙(Leftmost Prefix Rule)**: 인덱스 (A, B, C)는 (A), (A, B), (A, B, C) 필터 쿼리에 사용 가능하지만, (B)나 (C) 단독으로는 사용 불가.

**"가장 선택적인 컬럼을 먼저" 신화 깨기**: 올바른 규칙은 가장 많은 쿼리를 서비스하도록 순서를 정하는 것이다. 등호(=) 조건 컬럼을 범위 조건 컬럼보다 앞에 배치한다.

### 2.2 커버링 인덱스 (Index-Only Scan)

쿼리에 필요한 모든 컬럼을 인덱스에 포함하면, 힙 테이블 접근 없이 인덱스만으로 데이터를 반환한다. 테이블 룩업 I/O를 제거하여 읽기 성능을 극적으로 개선한다.

### 2.3 부분 인덱스 (Partial Index)

WHERE 절로 행의 부분 집합만 인덱싱한다:

```sql
-- soft-delete 패턴: 활성 레코드에만 유니크 제약
CREATE UNIQUE INDEX uq_email_active ON users (email) WHERE deleted_at IS NULL;
```

작은 인덱스 = 적은 저장소, 빠른 스캔, 저렴한 유지보수.

### 2.4 일반 원칙

- 높은 카디널리티 컬럼이 인덱싱에 유리 (boolean, gender는 피함)
- 인덱스는 읽기를 빠르게 하지만 쓰기를 느리게 함 — INSERT/UPDATE/DELETE마다 관련 인덱스 갱신
- 미사용 인덱스는 정기 감사 후 삭제

> 출처: [Use The Index, Luke](https://use-the-index-luke.com/), [Heroku - Efficient Use of PostgreSQL Indexes](https://devcenter.heroku.com/articles/postgresql-indexes)

---

## 3. 트랜잭션 격리 수준

### 3.1 ACID

- **Atomicity**: 전부 또는 전무
- **Consistency**: 유효한 상태 전이
- **Isolation**: 동시 트랜잭션이 간섭하지 않음
- **Durability**: 커밋된 데이터는 장애 후에도 유지

### 3.2 4단계 격리 수준 (PostgreSQL 기준)

| 격리 수준 | Dirty Read | Non-Repeatable Read | Phantom Read | 직렬화 이상 |
|-----------|:----------:|:-------------------:|:------------:|:-----------:|
| Read Uncommitted | PG에서 불가 | 가능 | 가능 | 가능 |
| **Read Committed** (기본값) | 불가 | 가능 | 가능 | 가능 |
| Repeatable Read | 불가 | 불가 | PG에서 불가 | 가능 |
| Serializable | 불가 | 불가 | 불가 | 불가 |

### 3.3 실전 가이드

- **Read Committed** (기본값): 각 SQL 문이 커밋된 데이터의 새로운 스냅샷을 본다. 대부분의 애플리케이션에 적합.
- **Repeatable Read**: 트랜잭션 시작 시 스냅샷 고정. 같은 트랜잭션 내에서 일관된 읽기. PostgreSQL은 이 수준에서 Phantom Read도 방지 (SQL 표준 초과).
- **Serializable**: SSI(Serializable Snapshot Isolation) 사용. 직렬 실행과 동일한 결과 보장. 반드시 직렬화 실패 시 재시도 로직 구현 필요.

```python
# Serializable 격리 수준에서의 재시도 패턴
from sqlalchemy import text

def execute_with_retry(session, operation, max_retries=3):
    for attempt in range(max_retries):
        try:
            session.execute(text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))
            result = operation(session)
            session.commit()
            return result
        except OperationalError as e:
            session.rollback()
            if "could not serialize" in str(e) and attempt < max_retries - 1:
                continue
            raise
```

> 출처: [PostgreSQL Documentation: Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html)

---

## 4. 데이터베이스 마이그레이션

### 4.1 Expand-and-Contract 패턴

```
1. Expand   : 새 구조 추가 (기존 코드 영향 없음)
2. Migrate  : 양쪽에 쓰기 + 데이터 백필 + 읽기 전환
3. Contract : 기존 구조 제거
```

핵심: 모든 마이그레이션은 현재 실행 중인 애플리케이션 코드와 하위 호환되어야 한다. 롤링 배포 중 두 버전의 애플리케이션이 동시에 동작해야 한다.

### 4.2 Stripe의 4단계 마이그레이션 패턴

| 단계 | 설명 |
|------|------|
| 1. Dual Writing | 기존+신규 테이블에 동시 쓰기. 기존 데이터 백필 |
| 2. Dark Reading | 양쪽에서 읽기 실행, 결과 비교 (Scientist 패턴). 불일치 시 알림 |
| 3. Switch Reads | 모든 읽기를 신규 테이블로 전환 |
| 4. Cleanup | 기존 쓰기 경로 제거, 기존 구조 삭제 |

### 4.3 절대 하지 말 것

- 컬럼 이름을 한 단계에서 변경하지 않는다 → add/copy/switch/drop 패턴 사용
- 스키마 변경과 코드 배포를 결합하지 않는다

### 4.4 온라인 스키마 변경 도구

| 도구 | 대상 | 방식 |
|------|------|------|
| gh-ost (GitHub) | MySQL | 트리거 없이 바이너리 로그 스트림 사용 |
| pt-online-schema-change (Percona) | MySQL | 트리거 기반 |
| pgroll (Xata) | PostgreSQL | Expand-contract 자동화 + 가상 스키마 |

> 출처: [Stripe Engineering Blog - Online Migrations at Scale](https://stripe.com/blog/online-migrations), [gh-ost](https://github.com/github/gh-ost)

---

## 5. 쿼리 최적화

### 5.1 EXPLAIN ANALYZE 읽기

```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- 출력 해석:
-- Seq Scan on users (cost=0.00..445.00 rows=1 width=244) (actual time=0.017..0.051 rows=1 loops=1)
--                     ^시작비용  ^총비용   ^예상행  ^폭       ^실제시간            ^실제행  ^반복횟수
```

- **cost**: 임의 단위 (1.0 = 순차 디스크 페이지 1회 읽기)
- **예상 행 vs 실제 행**이 크게 다르면 `ANALYZE` 실행하여 통계 갱신

### 5.2 스캔 유형

| 유형 | 설명 | 주의 |
|------|------|------|
| Seq Scan | 모든 행 읽기 | 대형 테이블에서 경고 신호 |
| Index Scan | 인덱스로 행 접근 | 소수 행에 효율적 |
| Bitmap Heap Scan | 2단계: 인덱스로 위치 파악 → 물리 순서로 행 접근 | 중간 범위 |

### 5.3 조인 유형

| 유형 | 적합한 경우 |
|------|-----------|
| Nested Loop | 작은 외부 집합 + 인덱스된 내부 |
| Hash Join | 중·대형 비정렬 데이터 |
| Merge Join | 조인 키로 사전 정렬된 데이터 |

### 5.4 N+1 문제

1개 쿼리로 N개 부모를 가져온 후, N개 추가 쿼리로 자식을 가져오는 문제.

| 해결책 | 방식 |
|--------|------|
| JOIN FETCH | 단일 쿼리로 부모+자식 조인 |
| 배치 로딩 | 부모 1쿼리 + 자식 1쿼리 (`WHERE parent_id IN (...)`) |
| Django | `select_related` (FK JOIN) / `prefetch_related` (별도 쿼리) |
| SQLAlchemy | `joinedload` / `selectinload` |

> 출처: [PostgreSQL Documentation: Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html), [Use The Index, Luke](https://use-the-index-luke.com/)

---

## 6. 데이터 모델링 패턴

### 6.1 계층 구조 패턴

| 패턴 | INSERT | 이동 | 하위 트리 조회 | 조상 조회 | 저장 |
|------|--------|------|--------------|---------|------|
| **Adjacency List** | 쉬움 | 쉬움 | 재귀/CTE 필요 | 재귀/CTE 필요 | 최소 |
| **Nested Set** | 비쌈 (left/right 재작성) | 비쌈 | 단일 쿼리 (BETWEEN) | 단일 쿼리 | 최소 |
| **Materialized Path** | 쉬움 | 보통 (경로 갱신) | LIKE 'path%' | 경로 분할 | 보통 |
| **Closure Table** | 보통 (모든 경로 삽입) | 보통 | 단일 쿼리 | 단일 쿼리 | 높음 |

**권장**: 작은/단순 트리 → Adjacency List, 깊은 계층+복잡 쿼리 → Closure Table, 읽기 중심 안정 트리 → Nested Set.

### 6.2 상속/다형성 패턴

| 패턴 | 설명 | 적합 | 트레이드오프 |
|------|------|------|------------|
| **Single Table (STI)** | 모든 타입 한 테이블 + type 구분자 | 속성 80%+ 공유 | NULL 많음, 테이블 비대 |
| **Class Table (CTI)** | 계층별 테이블, 공유 PK로 조인 | 속성이 크게 다름 | JOIN 필요 |
| **Concrete Table (TPC)** | 구체 타입별 독립 테이블 | 타입이 완전 독립 | FK 제약 불가, 스키마 중복 |

### 6.3 다형적 연관 (Polymorphic Associations)

하나의 자식 엔티티가 여러 부모 타입과 관계:
- `commentable_id` (FK) + `commentable_type` (구분자)
- **한계**: DB 레벨 FK 제약 불가 → 애플리케이션 레벨 검증 필요

> 출처: Martin Fowler, [Single Table Inheritance](https://martinfowler.com/eaaCatalog/singleTableInheritance.html), [Class Table Inheritance](https://martinfowler.com/eaaCatalog/classTableInheritance.html)

---

## 7. 커넥션 풀링

### 7.1 왜 필요한가

PostgreSQL은 연결당 OS 프로세스를 fork한다 (경량 쿼리 ~5-10MB, 중량 쿼리 ~15-20MB). 풀링 없이 1000개 동시 요청 = 1000개 PostgreSQL 프로세스.

### 7.2 최적 연결 수 공식

```
optimal_connections = (core_count × 2) + effective_spindle_count
```

- `core_count`: 물리 코어만 (하이퍼스레드 제외)
- 일반 가이드: CPU 코어 수의 3-5배 (4코어 서버 → 12-20 활성 연결)
- **연결이 많다고 처리량이 높아지지 않는다** — 컨텍스트 스위칭이 성능을 저하시킨다

### 7.3 SQLAlchemy 풀 설정

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://...",
    pool_size=5,          # 풀 내 영구 연결 수
    max_overflow=10,      # 추가 임시 연결 (최대 = pool_size + max_overflow)
    pool_timeout=30,      # 연결 대기 타임아웃 (초)
    pool_recycle=1800,    # 연결 재활용 주기 (초, DB의 wait_timeout보다 짧게)
    pool_pre_ping=True,   # 사용 전 SELECT 1로 연결 유효성 검사
)
```

### 7.4 PgBouncer

| 모드 | 설명 | 적합 |
|------|------|------|
| Transaction | 트랜잭션 후 서버 연결 반환 | 웹/API (최대 연결 절감) |
| Session | 클라이언트 세션 동안 유지 | Prepared statement, advisory lock 필요 |

PgBouncer 사용 시 SQLAlchemy에서 `NullPool` 사용 (이중 풀링 방지).

> 출처: [PostgreSQL Wiki - Number of Database Connections](https://wiki.postgresql.org/wiki/Number_Of_Database_Connections), [SQLAlchemy 2.0 - Connection Pooling](https://docs.sqlalchemy.org/en/20/core/pooling.html), [PgBouncer Configuration](https://www.pgbouncer.org/config.html)
