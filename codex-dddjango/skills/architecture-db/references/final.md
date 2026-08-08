# 데이터베이스 설계 종합 가이드

## 목차

1. [데이터베이스 모델링 프로세스](#1-데이터베이스-모델링-프로세스)
2. [개념적 데이터 모델링 (ERD)](#2-개념적-데이터-모델링-erd)
3. [정규화 (1NF — BCNF)](#3-정규화-1nf--bcnf)
4. [역정규화 (Denormalization)](#4-역정규화-denormalization)
5. [성능 최적화 순서](#5-성능-최적화-순서)
6. [인덱스 아키텍처: B+Tree](#6-인덱스-아키텍처-btree)
7. [인덱스 설계 베스트 프랙티스](#7-인덱스-설계-베스트-프랙티스)
8. [제약조건과 중복 방지](#8-제약조건과-중복-방지)
9. [트랜잭션, 격리 수준, 락](#9-트랜잭션-격리-수준-락)
10. [쿼리 최적화](#10-쿼리-최적화)
11. [운영 rollout, backfill, migration safety](#11-운영-rollout-backfill-migration-safety)
12. [데이터 모델링 패턴: 계층 구조](#12-데이터-모델링-패턴-계층-구조)
13. [데이터 모델링 패턴: 상속과 다형성](#13-데이터-모델링-패턴-상속과-다형성)
14. [참고 문헌](#14-참고-문헌)

---

## 1. 데이터베이스 모델링 프로세스

### 1.1 작업 순서

```
업무 파악 → 개념적 데이터 모델링 → 논리적 데이터 모델링 → 물리적 데이터 모델링
```

| 단계 | 핵심 활동 | 산출물 |
|------|----------|--------|
| 업무 파악 | 이해관계자 인터뷰, UI 프로토타입으로 합의 | 업무 기술서 |
| 개념적 모델링 | 엔티티, 관계, 속성 식별 | ERD |
| 논리적 모델링 | 정규화, 키 결정, 데이터 타입 | 논리 스키마 |
| 물리적 모델링 | 인덱스, 파티셔닝, 성능 최적화 | 물리 스키마 |

### 1.2 업무 파악 원칙

- **말을 믿지 말자** — UI를 만들어서 상호 일치된 합의안을 갖자
- 개념적 데이터 모델링이 가장 중요하다. 이것을 잘 했다면 이후 단계는 자연스럽게 따라온다

> 출처: 데이터베이스 모델링 [Go_Deeper]

---

## 2. 개념적 데이터 모델링 (ERD)

### 2.1 ERD 구성 요소

ERD(Entity Relationship Diagram)는 데이터 구조를 시각적으로 표현하는 언어다.

| ERD 요소 | 의미 | 물리 대응 |
|----------|------|----------|
| 속성 (Attribute) | 정보 | Column |
| 엔티티 (Entity) | 정보 그룹 | Table |
| 관계 (Relation) | 엔티티 간 연결 | PK, FK |

### 2.2 ERD 작성 원칙

1. 연관된 정보를 담고 있는 **덩어리를 찾는다**
2. 그룹별로 조회가 가능하고 조인에 유리하도록 **적절히 분리**한다
   - 하나의 큰 덩어리: 전체 조회 필요 + 중복 발생
   - 적절히 분리된 그룹: 그룹별 조회 가능 + 조인 활용

### 2.3 식별자 (Primary Key)

| 키 종류 | 설명 |
|---------|------|
| 후보키 (Candidate Key) | 식별자가 될 수 있는 키 |
| 기본키 (Primary Key) | 후보키 중에서 선택된 키 |
| 대체키 (Alternate Key) | 후보키 중에서 선택되지 않은 키 |
| 복합키 (Composite Key) | 두 가지 이상의 키가 합쳐져서 기본키가 된 경우 |

- 자연스럽게 기본키가 될 수 있는 컬럼이 없으면 **인조키(Surrogate Key)**를 만들어 사용한다

### 2.4 Cardinality (기수)

| 관계 | 설명 | 예시 |
|------|------|------|
| 1:1 | 한 엔티티가 다른 엔티티와 정확히 하나 대응 | 사용자 — 프로필 |
| 1:N | 한 엔티티가 여러 엔티티와 대응 | 부서 — 직원 |
| N:M | 양쪽 모두 여러 엔티티와 대응 | 학생 — 과목 (중간 테이블 필요) |

### 2.5 Optionality (선택성)

한쪽에 NULL이 올 수 있는지 여부를 나타낸다.

- **필수 (1 표기)**: 반드시 있어야 한다
- **선택 (O 표기)**: NULL일 수 있다
- 예: "주문은 반드시 고객이 있어야 하지만, 고객은 주문이 없을 수 있다"

> 출처: 데이터베이스 모델링 [Go_Deeper]

---

## 3. 정규화 (1NF — BCNF)

### 3.1 함수적 종속 (Functional Dependency)

속성 X가 속성 Y를 함수적으로 결정한다(X → Y)는 X의 각 값이 정확히 하나의 Y 값과 대응됨을 의미한다. 정규화의 이론적 기반이다.

### 3.2 정규형 정의

| 정규형 | 조건 | 제거하는 문제 |
|--------|------|-------------|
| **1NF** | 모든 컬럼이 원자값, 행이 고유 식별 가능, 반복 그룹 없음 | 중첩/반복 데이터 |
| **2NF** | 1NF + 부분 종속 제거 (비주요 속성이 전체 복합키에 종속) | 복합키의 일부에만 종속하는 속성 |
| **3NF** | 2NF + 이행 종속 제거 (비주요 속성이 다른 비주요 속성에 종속 불가) | A→B→C에서 A→C 이행 종속 |
| **BCNF** | 3NF + 모든 함수적 종속 X→Y에서 X가 슈퍼키 | 후보키가 아닌 결정자 |

### 3.3 정규형 위반 예시

**2NF 위반**: 복합키 (StudentID, CourseID)에서 StudentName이 StudentID에만 종속

```
수강 테이블 (StudentID, CourseID, StudentName, Grade)
                                   ^^^^^^^^^^^^^^^^
StudentName은 StudentID에만 종속 -> 부분 종속 위반

해결: 학생(StudentID, StudentName) + 수강(StudentID, CourseID, Grade)
```

**3NF 위반**: StudentID → DepartmentID → DepartmentName (이행 종속)

```
학생 테이블 (StudentID, DepartmentID, DepartmentName)
                                       ^^^^^^^^^^^^^^^
DepartmentName은 DepartmentID에 종속, StudentID에 이행 종속

해결: 학생(StudentID, DepartmentID) + 학과(DepartmentID, DepartmentName)
```

### 3.4 정규화 핵심 원칙

각 정규형은 특정 이상(갱신/삽입/삭제 anomaly)을 순차적으로 제거한다. 과도한 정규화는 JOIN 증가로 읽기 성능 저하, 과소 정규화는 데이터 불일치 유발. **언제 멈출지가 아키텍처 트레이드오프**이지만, 기본 원칙은 **정규화를 먼저 하고, 필요한 경우에만 역정규화**하는 것이다.

> 출처: DigitalOcean - Database Normalization, GeeksforGeeks - Normal Forms in DBMS, 데이터베이스 모델링 [Go_Deeper]

---

## 4. 역정규화 (Denormalization)

### 4.1 역정규화란

성능이나 개발 편의성을 위해 정규화를 의도적으로 거스르는 것이다.

- 정규화는 대체로 **쓰기**에 초점이 맞춰져 있다
- 정규화하면 표가 여러 개로 쪼개지고, 읽기 위해서는 **JOIN이 필요**하다 (비싼 작업)
- 역정규화는 **중복을 허용하여 JOIN을 없애서** 읽기 성능을 올리는 작업이다

### 4.2 핵심 원칙

**반드시 정규화를 먼저 하고, 필요한 경우에 역정규화한다. 읽기가 많다고 바로 역정규화하는 것은 잘못된 접근이다.**

### 4.3 역정규화 4가지 기법

| # | 기법 | 설명 | 대가 |
|---|------|------|------|
| 1 | **테이블 병합** | 조인이 자주 발생하는 테이블을 하나로 합침 | 데이터 중복, 갱신 복잡도 증가 |
| 2 | **파생 컬럼 추가** | 자주 발생하는 집계를 컬럼으로 추가 | 집계값 동기화 필요 |
| 3-1 | **수직 분할** | 용량이 큰 컬럼만 따로 테이블로 분리 | 조인 필요 (하지만 메인 테이블 경량화) |
| 3-2 | **수평 분할** | ID 범위 기준으로 다른 테이블로 분리 | 쿼리 라우팅 복잡 |
| 4 | **관계의 역정규화** | FK를 추가하여 조인 횟수를 줄이는 지름길 | FK 정합성 유지 필요 |

> 출처: 데이터베이스 모델링 [Go_Deeper]

---

## 5. 성능 최적화 순서

물리적 데이터 모델링 단계에서 성능이 핵심이다. 다음 순서를 반드시 지킨다:

```
1. 슬로우 쿼리 최적화    ← 가장 먼저 (비용 최소)
2. 인덱스 적용           ← 읽기 ↑, 쓰기 ↓ 트레이드오프
3. 애플리케이션 캐시 활용  ← DB 부하 감소
4. 역정규화              ← 최후의 보루 (대가가 크므로 반드시 위 방법을 모두 시도 후)
```

**핵심**: 일단 운영을 해봐야 알 수 있는 것들이 많다. 슬로우 쿼리를 찾아서 최적화하는 것부터 시작한다.

> 출처: 데이터베이스 모델링 [Go_Deeper]

---

## 6. 인덱스 아키텍처: B+Tree

대부분의 RDBMS(MySQL, PostgreSQL)가 사용하는 기본 인덱스 구조.

### 6.1 B+Tree 특징

- 트리 구조, Key 값으로 **정렬**
- Child 노드가 여러 개 (높은 팬아웃)
- 각 노드가 메모리가 아닌 **디스크**에 존재
- **실제 데이터는 리프 노드에만** 존재
- **Sibling 포인터** → Range 쿼리 가능

### 6.2 읽기

트리를 따라 루트 → 중간 노드 → 리프 노드로 내려가면 바로 데이터를 읽을 수 있다. O(log N) 복잡도.

### 6.3 쓰기

여러 번의 디스크 쓰기가 발생할 수 있다:

1. 새 노드 생성
2. 부모 노드 업데이트
3. 옆 노드에서 데이터 이동
4. 새 데이터 삽입

중간에 DB가 죽으면 데이터 오염 위험이 있으므로 **WAL(Write-Ahead Log)**을 사용한다: 실제 쓰기 전에 어떤 write를 할지 미리 기록하고, 그 다음 실제 업데이트를 진행한다.

### 6.4 인덱스의 근본 트레이드오프

**인덱스는 읽기 성능을 비약적으로 올리고, 쓰기 성능을 비관적으로 희생시킨다.**

모든 INSERT/UPDATE/DELETE는 관련된 모든 인덱스를 갱신해야 한다.

> 출처: B+Tree [Go_Deeper/Wiki/Database]

---

## 7. 인덱스 설계 베스트 프랙티스

### 7.1 복합 인덱스 컬럼 순서

복합 인덱스는 선언 순서대로 정렬된 B-tree이다.

**최좌선 접두사 규칙(Leftmost Prefix Rule)**: 인덱스 (A, B, C)는 (A), (A, B), (A, B, C) 필터 쿼리에 사용 가능하지만, (B)나 (C) 단독으로는 사용 불가.

**"가장 선택적인 컬럼을 먼저" 신화 깨기**: 올바른 규칙은 **가장 많은 쿼리를 서비스하도록** 순서를 정하는 것이다. **등호(=) 조건 컬럼을 범위 조건 컬럼보다 앞에** 배치한다.

```sql
-- 쿼리: WHERE status = 'active' AND created_at > '2024-01-01'
-- 좋음: 등호 컬럼 먼저
CREATE INDEX idx_status_created ON orders (status, created_at);

-- 나쁨: 범위 컬럼이 먼저 -> status 필터에 인덱스 활용 불가
CREATE INDEX idx_created_status ON orders (created_at, status);
```

### 7.2 커버링 인덱스 (Index-Only Scan)

쿼리에 필요한 **모든 컬럼을 인덱스에 포함**하면, 힙 테이블 접근 없이 인덱스만으로 데이터를 반환한다. 테이블 룩업 I/O를 제거하여 읽기 성능을 극적으로 개선한다.

```sql
-- 쿼리: SELECT email FROM users WHERE status = 'active'
-- 커버링 인덱스: 테이블 접근 불필요
CREATE INDEX idx_covering ON users (status) INCLUDE (email);
```

### 7.3 부분 인덱스 (Partial Index)

WHERE 절로 행의 **부분 집합만** 인덱싱한다.

```sql
-- soft-delete 패턴: 활성 레코드에만 유니크 제약
CREATE UNIQUE INDEX uq_email_active ON users (email) WHERE deleted_at IS NULL;
```

작은 인덱스 = 적은 저장소, 빠른 스캔, 저렴한 유지보수.

### 7.4 인덱스 설계 일반 원칙

| 원칙 | 설명 |
|------|------|
| 높은 카디널리티 우선 | boolean, gender 같은 저카디널리티 컬럼은 인덱싱 효과 낮음 |
| 읽기/쓰기 비율 고려 | 읽기 중심 → 인덱스 추가, 쓰기 중심 → 인덱스 최소화 |
| 미사용 인덱스 감사 | 정기적으로 사용되지 않는 인덱스 확인 후 삭제 |
| 단일 vs 복합 | RDBMS는 단일 인덱스를 조합(bitmap scan)할 수 있으므로, 복합 인덱스 전에 벤치마크 |

> 출처: [Use The Index, Luke](https://use-the-index-luke.com/), [Heroku - Efficient Use of PostgreSQL Indexes](https://devcenter.heroku.com/articles/postgresql-indexes)

---

## 8. 제약조건과 중복 방지

DB가 강제할 수 있는 불변식은 애플리케이션 validation만으로 남기지 않고 제약조건으로 보호한다. 제약조건은 도메인 규칙, 데이터 정합성, 중복 방지, 동시 요청 방어를 함께 담당한다.

### 8.1 제약조건 선택 기준

| 제약조건 | 사용 기준 | 주의 |
|----------|----------|------|
| Primary Key | 행의 안정적 식별자 | 자연키가 불안정하면 surrogate key 사용 |
| Foreign Key | 참조 무결성을 DB가 강제할 수 있는 관계 | 삭제 정책과 함께 결정 |
| Unique | 자연 유일성, duplicate prevention, idempotency key 저장 | NULL 처리와 partial unique 여부 확인 |
| Check | 단일 행 안에서 검증 가능한 값 범위와 상태 규칙 | 다른 행이나 외부 상태가 필요한 규칙에는 부적합 |
| Not Null | 필수 속성 또는 필수 관계 | 기존 데이터 backfill 후 적용 |

### 8.2 FK 삭제 정책

| 정책 | 적합한 경우 | 위험 |
|------|------------|------|
| Restrict/Protect | 참조 중인 데이터 삭제를 금지해야 함 | 삭제 작업이 실패할 수 있음 |
| Cascade | 부모 생명주기가 자식 생명주기를 완전히 소유 | 감사/복구 요구와 충돌 가능 |
| Set Null | 관계는 끊어도 자식 데이터는 보존 | nullable 의미가 도메인에 맞아야 함 |
| Soft Delete | 삭제 이력과 복구가 중요 | 모든 조회와 unique constraint에 삭제 상태 반영 필요 |

Cascade는 편의 기능이 아니라 소유권 결정이다. 감사, 결제, ledger, 권한처럼 이력 보존이 중요한 데이터에는 무심코 cascade를 쓰지 않는다.

**BC 경계 FK 금지**: FK는 *같은 바운디드 컨텍스트(앱) 안*에서만 쓴다 — 타 BC 모델을 `ForeignKey`로 참조하면 모듈 간 DB 결합(상류 테이블 형상·삭제정책이 하류로 누수, 마이그레이션이 상류에 묶임)이 생긴다. 타 BC는 ID 값 참조 + 앱 레벨/ACL 무결성으로 한다(`architecture-ddd` §3.3 규칙3 영속성 확장).

### 8.3 중복 방지와 멱등성 저장소

중복 방지는 같은 비즈니스 사건이 두 번 저장되거나 처리되는 것을 막는 설계다.

| 상황 | 권장 DB 장치 |
|------|--------------|
| 사용자 이메일, 주문 번호처럼 자연 유일성이 있음 | unique constraint 또는 partial unique index |
| soft-delete 후 활성 행만 유일해야 함 | `WHERE deleted_at IS NULL` partial unique index |
| 동일 요청 retry를 같은 결과로 재생해야 함 | idempotency key table + unique constraint |
| 같은 key로 다른 요청 본문이 들어오면 충돌이어야 함 | key scope + request fingerprint/hash 저장 |

Idempotency storage는 API 계약과 연결되지만, DB 설계에서는 최소한 다음을 정한다.

- key scope: caller, tenant, operation, resource owner 등 어떤 범위에서 unique한지
- storage owner/location: 어떤 테이블이 key와 처리 상태를 소유하는지
- unique constraint: 동시 요청 race를 DB가 막을 수 있는지
- request fingerprint: 같은 key의 다른 payload를 구분하는지
- response snapshot 또는 stable result reference: replay가 현재 상태 재조회가 아니라 최초 결과 재현인지
- retention/cleanup: 보관 기간과 cleanup이 unique constraint 의미를 깨지 않는지

### 8.4 제약조건 rollout 원칙

기존 데이터가 있는 테이블에 새 제약조건을 추가할 때는 데이터 정리와 rollout 순서를 먼저 설계한다.

1. 현재 데이터가 제약조건을 만족하는지 점검한다.
2. 필요한 경우 batch backfill 또는 cleanup을 먼저 수행한다.
3. 새 코드와 구 코드가 동시에 동작하는 compatibility window를 고려한다.
4. NOT NULL, unique, check constraint는 검증 실패와 rollback/forward-fix 방법을 정한 뒤 적용한다.

---

## 9. 트랜잭션, 격리 수준, 락

### 9.1 ACID

| 속성 | 의미 |
|------|------|
| **Atomicity** | 트랜잭션의 모든 연산이 성공하거나, 모두 실패 (전부 또는 전무) |
| **Consistency** | 트랜잭션 전후로 데이터베이스가 유효한 상태를 유지 |
| **Isolation** | 동시 트랜잭션이 서로 간섭하지 않음 |
| **Durability** | 커밋된 데이터는 시스템 장애 후에도 유지 |

### 9.2 이상 현상 (Phenomena)

| 현상 | 설명 |
|------|------|
| **Dirty Read** | 다른 트랜잭션이 아직 커밋하지 않은 데이터를 읽음 |
| **Non-Repeatable Read** | 같은 트랜잭션 내에서 같은 행을 두 번 읽었을 때 값이 다름 |
| **Phantom Read** | 같은 조건으로 두 번 조회했을 때 행의 집합이 다름 |
| **Serialization Anomaly** | 동시 트랜잭션의 결과가 어떤 직렬 실행 순서와도 일치하지 않음 |

### 9.3 4단계 격리 수준

| 격리 수준 | Dirty Read | Non-Repeatable Read | Phantom Read | 직렬화 이상 |
|-----------|:----------:|:-------------------:|:------------:|:-----------:|
| Read Uncommitted | 가능 | 가능 | 가능 | 가능 |
| **Read Committed** (일반 기본값) | 불가 | 가능 | 가능 | 가능 |
| Repeatable Read | 불가 | 불가 | 가능 | 가능 |
| Serializable | 불가 | 불가 | 불가 | 불가 |

### 9.4 실전 선택 가이드

| 격리 수준 | 적합한 경우 | 주의 |
|-----------|-----------|------|
| **Read Committed** | 대부분의 OLTP 애플리케이션 | 각 SQL 문이 새 스냅샷을 봄 |
| **Repeatable Read** | 일관된 읽기가 필요한 보고서/배치 | 직렬화 실패 시 재시도 필요 |
| **Serializable** | 정확성이 최우선인 금융/결제 | 직렬화 실패 시 반드시 재시도 로직 구현 |

**핵심**: 격리 수준이 높을수록 안전하지만, 동시성이 낮아지고 직렬화 실패가 발생할 수 있다. 필요 이상으로 높은 격리 수준은 불필요한 성능 저하를 초래한다.

### 9.5 락과 동시성 제어

격리 수준만으로 비즈니스 불변식이 보호되지 않으면 제약조건이나 명시적 락을 함께 설계한다.

| 전략 | 적합한 경우 | 주의 |
|------|------------|------|
| Unique constraint 기반 방어 | 중복 생성, 동일 key race, natural uniqueness | 충돌 시 예외/재시도/기존 결과 조회 정책 필요 |
| Optimistic locking | 충돌이 드물고 retry가 허용됨 | version 컬럼 또는 compare-and-swap 조건 필요 |
| Pessimistic row lock | 행 잠금 지원 엔진에서 경합이 잦은 핫 로우(동시 writer 다수) | SQLite no-op → 포터블/저경합은 위 Optimistic locking 우선; lock 순서·timeout·deadlock 대응 |
| Advisory lock | 여러 행이나 외부 key 단위로 임계 구역 필요 | lock key 설계와 해제 실패 대응 필요 |
| Serializable + retry | 정확성이 최우선이고 predicate race를 막아야 함 | serialization failure retry가 필수 |

락은 범위를 작게 유지한다. 트랜잭션 안에서 사용자 입력 대기, 외부 API 호출, 긴 배치 작업을 수행하면 lock hold time이 길어져 throughput과 장애 반경이 커진다.

**엔진 의존성 — 개발과 운영 DB가 다르면 명세에서 분기한다.** 위 표의 락 전략(특히 pessimistic row lock)은 **행 잠금을 지원하는 엔진**(PostgreSQL 등)을 전제한다. 개발에서 흔한 **SQLite는 `select_for_update`를 no-op으로 무시**하고(행 잠금 미지원), Django 기본 **DEFERRED begin**은 `atomic()` 안 SELECT→UPDATE 락 승격이 스레드 경합 시 데드락(`database is locked`)을 낸다. 따라서 락만으로 환경 무관 정확성이 성립하지 않는다 — 환경 무관 방어선은 **불변식 CHECK 백스톱(예: `stock>=0`) + 낙관적 `version`/CAS 조건부 원자 UPDATE**(`WHERE`엔 `version` 경합 가드만 담고 비즈니스 판정(예: `stock>=qty`)은 제외 — 아래 낙관적 동시성 메커니즘·`architecture-ddd` §3.2)이고, 락은 운영 엔진용으로 유지하되 SQLite 직렬화가 필요하면 begin 모드(IMMEDIATE)·`busy_timeout` 같은 **연결 설정을 명세가 명시**한다. Risky Write의 락·동시성은 *대상 엔진별 동작 차이까지* 설계에서 확정한다(§9.6).

**연결 설정의 경계 — stock `OPTIONS`만, 엔진 교체는 아니다.** 바로 위 '연결 설정 명시'는 Django가 공식 지원하는 **stock `OPTIONS`**에 한정된다 — SQLite `transaction_mode`(5.1+)로 begin 모드 지정, `timeout`으로 busy 대기, 그리고 안전 PRAGMA 화이트리스트(연결 튜닝으로 허용: `foreign_keys`·`busy_timeout`·`synchronous`·`cache_size`). **프로덕션 `ENGINE` 교체·커스텀 DB 백엔드(`DatabaseWrapper` 상속 등)는 '연결 설정 명시'에 포함되지 않는다** — 그것은 엔진의 트랜잭션·락·격리 *메커니즘*을 바꾸는 설계 결정이라 설계가 명시적으로 승인할 때만 허용되고, 구현이 환경 한계(sqlite 락)를 이유로 자기 판단으로 만들지 않는다(상속·런타임 몽키패치·`connection_created`·`init_command`·미들웨어·테스트 패치 등 *출처-불문* — `implementation-django` §16.4). 격리·락·동시성 의미를 바꾸는 PRAGMA(`read_uncommitted`·커스텀 begin 모드·`isolation_level`·`locking_mode`·`journal_mode`(WAL))도 화이트리스트 밖이라 같은 설계 승인을 받는다.

**낙관적 동시성 메커니즘(판정은 도메인이 소유).** 판정·불변식 소유는 도메인 책임이다 — 비즈니스 판정(예: `stock>=qty`, `balance>=amount`)을 SQL `WHERE`나 ORM 호출로 옮기면 같은 판정의 도메인 메서드가 프로덕션에서 호출되지 않는 죽은 코드가 되어 빈혈이 된다(원칙 `architecture-ddd` §3.2 빈혈 차단). 따라서 동시성 안전이 필요해도 판정을 SQL로 옮기지 않고, **리포지토리·영속화 계층은 도메인 메서드 결과만 저장하고 판정을 재수행하지 않는다**: 인프라엔 경합 가드만 둔다 — 낙관적 `version`/CAS 조건부 원자 UPDATE(`WHERE`엔 `version`만, 비즈니스 판정은 제외). 선언적 불변식 백스톱(`stock>=0` CHECK, 위 엔진 의존성 단락)은 최후 안전망으로 병행하되 이는 *불변식*이지 트랜잭션 입력 *판정*(`stock>=qty`)이 아니다. `QuerySet.update()`가 0행이면(`Model.save()`로 저장하면 이 경합 가드가 사라진다) 경합이므로 응용 서비스가 재조회 후 *도메인 메서드부터* 재실행한다(재시도 상한·격리 수준별 재시도는 §9.6 Isolation/retry, `version` 컬럼 추가는 §11 rollout backfill 안전을 따른다). `version`은 애그리거트 루트가 소유·증가시킨다. 낙관적 전제는 *충돌 희소*이므로, 고경합 핫 로우는 운영 엔진에서 비관적 락도 고려한다(처리량 트레이드오프는 위 락 범위 원칙).

### 9.6 Risky Write Consistency Block

주문, 결제, 재고, 예약, 환불, 권한, ledger처럼 중복이나 race가 치명적인 쓰기에는 다음 항목을 명시한다.

| 항목 | 결정 내용 |
|------|-----------|
| Transaction owner | 어떤 use case/service가 transaction boundary를 소유하는지 |
| Locking strategy | unique constraint, optimistic, pessimistic, advisory, serializable 중 무엇을 쓰는지 |
| Rule ownership | 판정·불변식을 도메인 애그리거트(또는 도메인 서비스)가 소유하고 리포지토리는 결과만 저장하는지 — 경합 가드(`version`) 외 비즈니스 판정을 SQL(예: `WHERE stock>=qty`)·ORM `update()`에 복제해 도메인 메서드를 죽이지 않는지(원칙 `architecture-ddd` §3.2, 메커니즘 위 §9.5) |
| Idempotency storage | key scope, table, unique constraint, request fingerprint, stored result(= 도메인/응용 outcome; HTTP status·응답 표현은 presentation이 소유·replay 매핑 — `architecture-api` §13.3·P1a) |
| API handoff | `Idempotency-Key` replay/conflict 계약은 `architecture-api`와 맞추는지 |
| Side-effect timing | 외부 결제, 알림, message publish를 commit 전/후 어디서 실행하는지 |
| Isolation/retry | isolation level, deadlock/timeout/serialization failure retry 기준 |
| Test criteria (candidate) | duplicate request, concurrent request, retry, rollback에서 보호할 위험·failure 후보와 근거. 자체로 테스트 의무가 아님 |

`Test criteria`는 `discipline-tdd` 입장 심사에 제출할 후보 목록이다. DB unique/race/rollback/CAS가 다른 boundary와 독립된 production failure이고 기존 권위 테스트가 보호하지 않을 때 coder가 `add`할 수 있다. HTTP 등 다른 boundary가 같은 제품 failure를 이미 잡고 후보에 독자 DB failure mechanism이 없으면 `reuse`하며 test artifact를 만들지 않는다. 현재 DB constraint·transaction·rollback·race·repository round-trip을 보호하는 유효한 기존 테스트는 보존한다.

**`add`된 동시성 테스트의 mechanics는 결정적으로.** concurrent request·CAS 경합 테스트가 입장 승인된 뒤에는 **결정적 CAS-충돌 주입(스파이)** 으로 증명하는 것을 기본으로 한다 — 실제 스레드·커스텀 DB 백엔드 없이 `version` 경합을 1회 주입해 재시도 수렴을 검증한다(`implementation-test` §20.5). 스레드 기반 race 재현(`implementation-test` §20.4)은 보조이며, 그것을 위해 연결 *메커니즘*을 커스텀 백엔드로 바꾸지 않는다(stock `OPTIONS`만 — §9.5 연결 설정 경계·`implementation-django` §16.4).

외부 결제, 알림, SDK 호출, message publish는 DB 트랜잭션 내부에서 실행하지 않는 것을 기본으로 한다. 같은 transaction에 묶어야 하는 명확한 이유가 없으면 commit 이후 handoff(`transaction.on_commit()`, domain event, outbox 등)를 사용한다. 메시지 유실이 허용되지 않으면 Outbox로 전달을 보장한다(§9.7).

> 출처: [PostgreSQL Documentation: Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html)

### 9.7 Commit 후 메시지 전달과 Outbox

DB 상태 변경과 외부 메시지 발행을 함께 해야 할 때, 둘은 서로 다른 시스템이라 원자적으로 묶이지 않는다. "DB 커밋 -> 브로커 발행" 순서는 커밋 후 발행 직전 장애 시 메시지가 유실되고, "브로커 발행 -> DB 커밋" 순서는 롤백 시 존재하지 않는 사실에 대한 메시지가 나간다. 이 **이중 쓰기(dual write)** 문제는 유실이 치명적일 때 Outbox로 해결한다.

**트랜잭셔널 Outbox**: 브로커에 직접 발행하는 대신, 발행할 메시지를 비즈니스 데이터와 **같은 트랜잭션**으로 outbox 테이블에 기록한다. 커밋되면 상태 변경과 보낼 메시지가 원자적으로 함께 남는다. 별도 **디스패처**가 미발행 행을 읽어 브로커에 발행하고 발행 표시한다.

| 항목 | 결정 내용 |
|------|-----------|
| Outbox 테이블 | `id`, aggregate 식별, `event_type`, `payload`, `created_at`, `published_at`(nullable), `retry_count`. 비즈니스 write와 동일 트랜잭션에서 기록 |
| 전달 보장 | 디스패처가 발행 후 표시 전에 죽으면 재시도 시 중복 발행 가능 -> **at-least-once**. exactly-once는 일반적으로 보장하지 않는다 |
| Consumer 멱등성 | at-least-once의 필연적 요구. 소비자는 event id 등으로 **중복 수신을 무시**할 수 있어야 한다(처리 기록 또는 unique 제약) |
| 재시도와 dead-letter | 발행 실패는 `retry_count` 증가 후 재시도. 한계 초과 메시지는 dead-letter로 격리해 무한 재시도와 head-of-line 정체를 막는다 |
| 디스패처 동시성 | 여러 디스패처가 같은 행을 집지 않도록 행 잠금(`FOR UPDATE SKIP LOCKED`)이나 단일 워커로 직렬화 |
| 순서 보장 | 전역 순서가 필요하면 aggregate 단위로 직렬화하거나 정렬 키를 둔다. 필요 없으면 명시적으로 포기한다 |

**Outbox를 피하는 경우**: 외부 부수효과가 없거나, 단순 in-process 후속 작업이라 `transaction.on_commit()`으로 충분하거나, 유실을 제품이 수용할 수 있을 때. 채택 여부의 도메인 측면은 `architecture-ddd` §3.7, Django 구체 구현은 `implementation-django` §16.5를 따른다.

---

## 10. 쿼리 최적화

### 10.1 EXPLAIN ANALYZE 읽기

```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- 출력 예시:
-- Index Scan using idx_email on users
--   (cost=0.42..8.44 rows=1 width=244)
--   (actual time=0.017..0.018 rows=1 loops=1)
--   Buffers: shared hit=4
-- Planning Time: 0.105 ms
-- Execution Time: 0.038 ms
```

| 항목 | 의미 |
|------|------|
| cost (시작..총) | 임의 단위의 예상 비용 (1.0 = 순차 디스크 페이지 1회 읽기) |
| rows | 예상 반환 행 수 |
| actual time | 실제 소요 시간 (ms) |
| Buffers: shared hit/read | 캐시 히트 vs 디스크 읽기 |

**핵심**: 예상 행(rows)과 실제 행(actual rows)이 크게 다르면 `ANALYZE` 실행하여 테이블 통계를 갱신한다.

### 10.2 스캔 유형

| 유형 | 설명 | 주의 |
|------|------|------|
| **Seq Scan** | 테이블의 모든 행을 순차 읽기 | 대형 테이블에서 경고 신호 |
| **Index Scan** | 인덱스로 행을 하나씩 접근 | 소수 행에 효율적 |
| **Bitmap Heap Scan** | 2단계: 인덱스로 위치 파악 → 물리 순서로 접근 | Index Scan과 Seq Scan 사이 |
| **Index-Only Scan** | 인덱스만으로 데이터 반환 (커버링 인덱스) | 가장 빠른 읽기 |

### 10.3 조인 유형

| 유형 | 적합한 경우 | 특징 |
|------|-----------|------|
| **Nested Loop** | 작은 외부 집합 + 인덱스된 내부 | 소규모 데이터에 최적 |
| **Hash Join** | 중·대형 비정렬 데이터 | 작은 테이블로 해시 테이블 생성 |
| **Merge Join** | 조인 키로 사전 정렬된 데이터 | 대규모 정렬 데이터에 효율적 |

### 10.4 N+1 문제

1개 쿼리로 N개 부모를 가져온 후, N개 추가 쿼리로 각 부모의 자식을 개별 조회하는 문제. ORM의 lazy loading이 주 원인.

```
-- N+1 발생 (1 + N 쿼리)
SELECT * FROM authors;                          -- 1회
SELECT * FROM books WHERE author_id = 1;        -- N회 반복
SELECT * FROM books WHERE author_id = 2;
...

-- 해결: JOIN 또는 IN 절 (1-2 쿼리)
SELECT * FROM authors a JOIN books b ON a.id = b.author_id;
-- 또는
SELECT * FROM authors;
SELECT * FROM books WHERE author_id IN (1, 2, 3, ...);
```

### 10.5 쿼리 최적화 일반 원칙

| 원칙 | 설명 |
|------|------|
| SELECT * 회피 | 필요한 컬럼만 지정 (커버링 인덱스 활용 가능) |
| WHERE 절 활용 | 가능한 한 DB 단에서 필터링 (애플리케이션 필터링 회피) |
| LIMIT 사용 | 결과 집합 크기 제한 |
| 서브쿼리 vs JOIN | 대부분 JOIN이 서브쿼리보다 효율적 (옵티마이저 의존) |

> 출처: [PostgreSQL Documentation: Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html), [Use The Index, Luke](https://use-the-index-luke.com/)

---

## 11. 운영 rollout, backfill, migration safety

Architecture-db는 migration file 구현법이 아니라 운영 중 데이터 구조를 바꾸는 안전한 순서와 DB 위험을 결정한다. Django `RunPython`, `apps.get_model()`, `sqlmigrate`, migration class 작성은 `implementation-django`로 넘긴다.

### 11.1 Expand / Backfill / Contract

운영 DB 변경은 기존 코드와 새 코드가 동시에 동작하는 시간을 고려한다.

| 단계 | 목적 | 예시 |
|------|------|------|
| Expand | 구 코드가 깨지지 않는 새 구조 추가 | nullable column, 새 table, 새 index 추가 |
| Backfill | 기존 데이터를 새 구조에 맞게 채움 | batch update, dual write, dark read 비교 |
| Contract | 호환성이 확인된 뒤 이전 구조 제거 또는 제약 강화 | NOT NULL, unique/check 검증, old column 제거 |

컬럼 rename이나 type 변경처럼 기존 코드와 충돌하기 쉬운 변경은 한 번에 바꾸지 않고 add/copy/switch/drop으로 쪼갠다.

### 11.2 Backfill 위험

대형 backfill은 데이터 정합성 문제뿐 아니라 운영 부하를 만든다.

- batch 크기와 pause 정책을 정한다.
- row lock, replication lag, long transaction, vacuum/autovacuum 영향 여부를 확인한다.
- 실패한 batch를 재실행해도 안전하도록 idempotent하게 만든다.
- 진행률, 오류율, lag, query latency를 모니터링한다.
- 부분 완료 상태에서 rollback할지 forward-fix할지 미리 정한다.

### 11.3 Index와 constraint lock risk

Index와 constraint 추가는 DB 종류와 옵션에 따라 쓰기를 막거나 지연시킬 수 있다.

| 변경 | 주요 위험 | 설계 기준 |
|------|----------|-----------|
| 새 index | write slowdown, index build lock, storage 증가 | online/concurrent 생성 필요 여부 확인 |
| unique constraint | 기존 중복 데이터 때문에 실패 | 사전 중복 탐지와 cleanup 필요 |
| NOT NULL | 기존 NULL 데이터 때문에 실패 | nullable 추가 -> backfill -> NOT NULL 순서 |
| check constraint | 기존 위반 데이터 때문에 실패 | 사전 검증과 점진적 validation 고려 |
| FK 추가 | orphan row 때문에 실패, 쓰기 비용 증가 | orphan cleanup과 cascade/delete 정책 결정 |

### 11.4 실패 대응

운영 변경 계획은 rollback만 적지 말고 forward-fix도 함께 검토한다.

| 실패 상황 | 대응 기준 |
|----------|-----------|
| backfill 일부 실패 | 안전한 재실행 key와 실패 row 격리 |
| constraint validation 실패 | 위반 데이터 report, cleanup, 재검증 |
| index creation 실패 | 기존 query plan 유지 여부, 재시도 시간대, cleanup |
| 새/구 코드 compatibility 문제 | feature flag, dual write/read switch, 빠른 disable 경로 |
| 성능 저하 | index 제거/재작성, batch 중단, query fallback |

### 11.5 Rollout 산출물

DB architecture 답변에서 운영 변경을 다루면 다음을 남긴다.

- 현재 데이터 위험
- expand/backfill/contract 순서
- lock/index/constraint 위험
- batch와 monitoring 기준
- rollback 또는 forward-fix 방식
- 구/신 애플리케이션 compatibility window
- 실제 실행한 검증 명령 또는 실행하지 않았다는 표시

> 출처: Stripe Engineering Blog - Online Migrations at Scale, PostgreSQL Documentation, Django migration best practices

---

## 12. 데이터 모델링 패턴: 계층 구조

조직도, 카테고리 트리, 댓글 스레드 등 계층 구조를 RDB에 표현하는 4가지 패턴.

### 12.1 패턴 비교

| 패턴 | INSERT | 이동 | 하위 트리 조회 | 조상 조회 | 저장 공간 |
|------|--------|------|--------------|---------|----------|
| **Adjacency List** | 쉬움 | 쉬움 | 재귀/CTE 필요 | 재귀/CTE 필요 | 최소 |
| **Nested Set** | 비쌈 (left/right 재작성) | 비쌈 | 단일 쿼리 (BETWEEN) | 단일 쿼리 | 최소 |
| **Materialized Path** | 쉬움 | 보통 (경로 갱신) | LIKE 'path%' | 경로 분할 | 보통 |
| **Closure Table** | 보통 (모든 경로 삽입) | 보통 | 단일 쿼리 | 단일 쿼리 | 높음 |

### 12.2 Adjacency List (인접 리스트)

가장 단순한 패턴. 각 행에 parent_id를 저장한다.

```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    parent_id INTEGER REFERENCES categories(id)
);

-- 하위 트리 조회: WITH RECURSIVE (CTE)
WITH RECURSIVE subtree AS (
    SELECT id, name, parent_id FROM categories WHERE id = 1
    UNION ALL
    SELECT c.id, c.name, c.parent_id
    FROM categories c JOIN subtree s ON c.parent_id = s.id
)
SELECT * FROM subtree;
```

### 12.3 Closure Table (폐쇄 테이블)

모든 조상-자손 쌍을 별도 테이블에 저장한다. 가장 유연하며 복잡한 계층 쿼리에 적합.

```sql
CREATE TABLE node_closure (
    ancestor_id INTEGER REFERENCES nodes(id),
    descendant_id INTEGER REFERENCES nodes(id),
    depth INTEGER,
    PRIMARY KEY (ancestor_id, descendant_id)
);

-- 트리 A -> B -> C일 때 저장되는 행:
-- (A, A, 0), (A, B, 1), (A, C, 2), (B, B, 0), (B, C, 1), (C, C, 0)

-- A의 모든 자손 조회 (재귀 불필요)
SELECT descendant_id FROM node_closure WHERE ancestor_id = 'A';

-- C의 모든 조상 조회
SELECT ancestor_id FROM node_closure WHERE descendant_id = 'C' AND depth > 0;
```

### 12.4 선택 가이드

| 상황 | 권장 패턴 |
|------|----------|
| 작은/단순 트리, 빈번한 갱신 | Adjacency List |
| 깊은 계층, 복잡한 조상/자손 쿼리 | Closure Table |
| 읽기 중심, 안정적 트리 | Nested Set |
| 단순 트리, 보통 수준 갱신 | Materialized Path |

> 출처: Martin Fowler, [Software Patterns Lexicon - Closure Table](https://softwarepatternslexicon.com/patterns-sql/4/2/4/)

---

## 13. 데이터 모델링 패턴: 상속과 다형성

객체지향의 상속 관계를 RDB에 매핑하는 3가지 패턴과 다형적 연관.

### 13.1 상속 패턴 비교

| 패턴 | 설명 | 적합 | 트레이드오프 |
|------|------|------|------------|
| **Single Table (STI)** | 모든 타입 한 테이블 + type 구분자 | 속성 80%+ 공유 | NULL 많음, 테이블 비대 |
| **Class Table (CTI)** | 계층별 테이블, 공유 PK로 조인 | 속성이 크게 다름, 무결성 중요 | JOIN 필요 |
| **Concrete Table (TPC)** | 구체 타입별 독립 테이블 | 타입이 완전 독립 | FK 제약 불가, 스키마 중복 |

### 13.2 Single Table Inheritance (STI)

```sql
CREATE TABLE vehicles (
    id INTEGER PRIMARY KEY,
    type VARCHAR(20) NOT NULL,  -- 'car', 'truck', 'motorcycle'
    brand VARCHAR(100),
    -- 공통 속성
    engine_cc INTEGER,
    -- car 전용
    trunk_capacity_liters INTEGER,
    -- truck 전용
    payload_tons DECIMAL,
    -- motorcycle 전용
    has_sidecar BOOLEAN
);
```

### 13.3 Class Table Inheritance (CTI)

```sql
CREATE TABLE vehicles (
    id INTEGER PRIMARY KEY,
    type VARCHAR(20) NOT NULL,
    brand VARCHAR(100),
    engine_cc INTEGER
);

CREATE TABLE cars (
    vehicle_id INTEGER PRIMARY KEY REFERENCES vehicles(id),
    trunk_capacity_liters INTEGER
);

CREATE TABLE trucks (
    vehicle_id INTEGER PRIMARY KEY REFERENCES vehicles(id),
    payload_tons DECIMAL
);
```

### 13.4 다형적 연관 (Polymorphic Associations)

하나의 자식 엔티티가 여러 부모 타입과 관계를 맺는 패턴.

```sql
CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    body TEXT,
    commentable_type VARCHAR(50),  -- 'Article', 'Video', 'Photo'
    commentable_id INTEGER         -- 해당 타입의 PK
);
```

**한계**: DB 레벨에서 FK 제약을 강제할 수 없다. 참조 무결성은 애플리케이션 레벨에서 보장해야 한다.

### 13.5 선택 가이드

| 상황 | 권장 패턴 |
|------|----------|
| 타입 간 속성 대부분 공유 | STI (단순, JOIN 없음) |
| 타입별 속성이 크게 다름, 데이터 무결성 중요 | CTI (정규화, FK 제약) |
| 타입이 완전 독립, 접근 패턴 다름 | TPC (성능 우선) |
| 여러 부모 타입에 댓글/태그 연결 | Polymorphic Association |

> 출처: Martin Fowler, [Single Table Inheritance](https://martinfowler.com/eaaCatalog/singleTableInheritance.html), [Class Table Inheritance](https://martinfowler.com/eaaCatalog/classTableInheritance.html)

---

## 14. 참고 문헌

| 출처 | 다룬 내용 |
|------|---------|
| Go_Deeper/Book/Database/데이터베이스 모델링 | 모델링 프로세스, ERD, 키, 역정규화, 성능 최적화 순서 |
| Go_Deeper/Wiki/Database/B+Tree | B+Tree 구조, WAL, 읽기/쓰기 특성 |
| DigitalOcean - Database Normalization | 1NF~BCNF 정의, 함수적 종속 |
| Use The Index, Luke | 복합 인덱스 순서, 커버링 인덱스, "가장 선택적 먼저" 신화 |
| PostgreSQL Documentation: Transaction Isolation | ACID, 격리 수준, 이상 현상 |
| PostgreSQL Documentation: Using EXPLAIN | EXPLAIN ANALYZE 읽기, 스캔/조인 유형 |
| Stripe Engineering Blog - Online Migrations at Scale | expand/backfill/contract, dual write/read, cleanup rollout |
| Django migration best practices | migration 구현 세부사항은 implementation-django 책임이라는 경계 |
| Stripe API / IETF Idempotency-Key 자료 | API 멱등성 계약과 DB 저장소 handoff |
| Martin Fowler - PoEAA | STI, CTI, TPC 상속 패턴 |
| Software Patterns Lexicon | Closure Table, Adjacency List 계층 패턴 |
