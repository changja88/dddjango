# 데이터베이스 아키텍처 Internal vs External 리뷰

> Internal: 데이터베이스 모델링 [DM], B+Tree/LSM_Tree [IDX], Clean Architecture [CA]
> External: DigitalOcean/GeeksforGeeks [Norm], Use The Index Luke/Heroku [Index], PostgreSQL Docs [PG], Stripe Blog [Stripe], Martin Fowler [Fowler], SQLAlchemy Docs [SA], PgBouncer Docs [PgB]

---

## A. Conflicts (상호 충돌)

### [A-1] 역정규화 접근 태도

**상충 유형**: 불일치

| | Internal | External |
|---|---------|----------|
| 출처 | 데이터베이스 모델링 [DM] | DigitalOcean/GeeksforGeeks [Norm] |
| 주장 | "반드시 정규화를 먼저 하고, 필요한 경우에 역정규화한다. 읽기가 많다고 바로 역정규화하는 것은 잘못된 접근이다" | "과도한 정규화는 JOIN 증가로 읽기 성능 저하, 과소 정규화는 데이터 불일치 유발. 언제 멈출지가 아키텍처 트레이드오프다" |

**분석**: 직접 모순은 아니다. Internal은 "정규화 먼저, 역정규화는 최후의 보루"라는 강한 원칙을 제시하고, External은 "어디서 멈출지가 트레이드오프"라는 실용적 관점을 제시한다. Internal이 더 보수적이고 방어적이며, External이 더 균형 잡힌 시각이다.

**추천**: 병합 (Internal의 "정규화 우선" 원칙을 기본으로 하되, External의 트레이드오프 관점을 추가하여 "맹목적 정규화"도 경계)

---

### [A-2] 성능 최적화에서 역정규화의 위치

**상충 유형**: 불일치

| | Internal | External |
|---|---------|----------|
| 출처 | 데이터베이스 모델링 [DM] | (External에서 명시적 순서 없음) |
| 주장 | 최적화 순서: 슬로우 쿼리 최적화 -> 인덱스 -> 캐시 -> 역정규화(최후의 보루) | 인덱스 설계, 쿼리 최적화, 커넥션 풀링 등을 개별 주제로 다루며, 명시적 우선순위 순서를 제시하지 않음 |

**분석**: External은 각 최적화 기법을 독립된 섹션으로 다루며 적용 순서를 제시하지 않는다. Internal의 4단계 순서(쿼리 -> 인덱스 -> 캐시 -> 역정규화)는 실전적으로 유용한 가이드라인이다.

**추천**: Internal 채택 (명시적 최적화 순서는 의사결정에 매우 유용하며, External의 각 기법 상세 내용으로 보충)

---

### [A-3] 인덱스 설계 깊이와 관점

**상충 유형**: 보완적 불일치

| | Internal | External |
|---|---------|----------|
| 출처 | B+Tree/LSM_Tree [IDX] | Use The Index Luke/Heroku [Index] |
| 주장 | 인덱스의 내부 구조(B+Tree, LSM Tree)와 동작 원리에 집중. "읽기 성능을 비약적으로 올리고, 쓰기 성능을 비관적으로 희생시킨다" | 실전 인덱스 설계 패턴에 집중. 복합 인덱스 순서, 커버링 인덱스, 부분 인덱스 등 구체적 기법 제시 |

**분석**: 충돌이 아닌 보완 관계. Internal은 "왜 인덱스가 이렇게 동작하는가"를, External은 "어떻게 인덱스를 설계하는가"를 다룬다. 두 관점 모두 필요하다.

**추천**: 병합 (Internal의 구조 이해를 기반 지식으로, External의 설계 패턴을 실전 가이드로 배치)

---

## B. Overlaps (중복)

### [B-1] 정규화 개념

| 항목 | Internal | External |
|------|---------|----------|
| 범위 | 정규화의 목적과 역정규화 사례 4가지 | 1NF~BCNF 각 정규형의 조건, 위반 예시, 함수적 종속 정의 |
| 일관성 | 일관됨 |
| 상세도 | External이 훨씬 상세 (각 정규형별 조건과 예시) |

**추천**: 병합 유지 -- Internal의 프로세스 관점(왜 정규화를 하는가, 역정규화는 언제)과 External의 기술 관점(각 정규형 정의와 조건)은 상호 보완적

### [B-2] 인덱스의 읽기/쓰기 트레이드오프

| 항목 | Internal | External |
|------|---------|----------|
| 범위 | "읽기 성능을 비약적으로 올리고, 쓰기 성능을 비관적으로 희생시킨다" | "인덱스는 읽기를 빠르게 하지만 쓰기를 느리게 함 -- INSERT/UPDATE/DELETE마다 관련 인덱스 갱신" |
| 일관성 | 완전히 일관됨 |

**추천**: 중복 허용 -- 동일한 핵심 원리를 다른 맥락(구조 이해 vs 설계 지침)에서 언급하므로 강조 효과

### [B-3] ERD / 데이터 모델링

| 항목 | Internal | External |
|------|---------|----------|
| 범위 | ERD 작성법, 키 종류, Cardinality, Optionality | 계층 구조 패턴(Adjacency List, Closure Table 등), 상속 패턴(STI, CTI, TPC) |
| 일관성 | 일관됨 (다른 측면을 다룸) |

**추천**: 병합 유지 -- Internal은 기본 모델링 프로세스, External은 고급 모델링 패턴으로 단계적 구성 가능

---

## C. Decisions Needed (사용자 결정 필요)

### [C-1] 스킬의 데이터베이스 범위

Internal은 일반론(RDBMS + NoSQL 비교), External은 PostgreSQL 중심(격리 수준, PgBouncer, EXPLAIN ANALYZE 모두 PostgreSQL 기준).

**결정 필요**:
1. PostgreSQL 전용 스킬로 할 것인가, 데이터베이스 비의존적(DB-agnostic) 스킬로 할 것인가?
2. MySQL 관련 내용(gh-ost, pt-online-schema-change)은 유지할 것인가, 제거할 것인가?

---

### [C-2] NoSQL 패턴의 포함 범위

Internal은 LSM Tree(Cassandra, LevelDB, RocksDB)를 상세히 다루지만, External은 관계형 DB에만 집중한다.

**결정 필요**:
3. LSM Tree/NoSQL 내용을 architecture-db 스킬에 포함할 것인가, 별도 스킬로 분리할 것인가?
4. NoSQL 데이터 모델링 패턴(Document, Key-Value, Wide-Column, Graph)을 추가할 것인가?

---

### [C-3] ORM 코드 예시의 깊이

External에 SQLAlchemy 커넥션 풀 설정, Django select_related/prefetch_related, SQLAlchemy joinedload/selectinload 등 ORM 코드가 포함되어 있다.

**결정 필요**:
5. ORM별 코드 예시를 architecture-db에 포함할 것인가, implementation-django/implementation-python 등 구현 스킬로 이동할 것인가?
6. SQLAlchemy와 Django ORM 중 하나만 다룰 것인가, 둘 다 다룰 것인가?

---

### [C-4] 마이그레이션 패턴의 소속

External의 마이그레이션 섹션(Expand-and-Contract, Stripe 4단계, 온라인 스키마 변경 도구)은 아키텍처와 구현의 경계에 있다.

**결정 필요**:
7. Expand-and-Contract 같은 전략적 마이그레이션 패턴은 architecture-db에, Alembic/Django migrations 같은 도구별 가이드는 implementation 스킬에 배치하는 것이 맞는가?
8. 온라인 스키마 변경 도구(gh-ost, pgroll)는 architecture-db에 포함할 것인가?

---

### [C-5] Clean Architecture의 "데이터베이스는 세부사항" 원칙의 위치

Internal 섹션 6은 Robert C. Martin의 "데이터베이스는 세부사항"이라는 아키텍처 원칙을 다룬다. 이것은 DB 설계보다는 소프트웨어 아키텍처 원칙에 가깝다.

**결정 필요**:
9. 이 내용을 architecture-db에 유지할 것인가, architecture-cleanarchitecture 같은 별도 스킬로 이동할 것인가?
10. DB 스킬 내에서 이 원칙을 어떤 위치에 배치할 것인가? (서론? 별도 섹션? 부록?)

---

### [C-6] 커넥션 풀링의 소속

External의 커넥션 풀링 섹션은 인프라/운영에 가까운 내용이다.

**결정 필요**:
11. 커넥션 풀링을 architecture-db에 포함할 것인가, infrastructure/deployment 스킬로 분리할 것인가?

---

## D. Gaps (양쪽 모두에서 누락된 주제)

### [D-1] 파티셔닝 전략

Internal이 수평/수직 분할을 역정규화 사례로 짧게 언급하지만, 실전 파티셔닝 전략(Range, Hash, List partitioning)과 설계 기준이 없다. 대용량 테이블 운영에 필수적인 주제.

### [D-2] 락(Locking)과 동시성 제어

External이 트랜잭션 격리 수준을 다루지만, 행 수준 락, 테이블 락, Advisory Lock, 낙관적/비관적 락킹 패턴 등 실전 동시성 제어 가이드가 없다.

### [D-3] Soft Delete vs Hard Delete 패턴

External이 부분 인덱스에서 soft-delete를 예시로 언급하지만, soft delete 패턴의 설계 트레이드오프(쿼리 복잡도, 인덱스 영향, GDPR 준수)를 체계적으로 다루지 않는다.

### [D-4] 감사(Audit) 패턴

변경 이력 추적(audit trail)은 엔터프라이즈 DB 설계에서 매우 빈번한 요구사항이지만, 양쪽 모두 다루지 않는다. 트리거 기반, 이벤트 소싱, 히스토리 테이블 등.

### [D-5] 멀티테넌시(Multi-tenancy) 패턴

SaaS 아키텍처의 핵심 DB 설계 주제. 스키마 분리, 행 수준 분리(tenant_id), 데이터베이스 분리 등의 패턴과 트레이드오프.

### [D-6] 읽기 복제와 CQRS

읽기/쓰기 분리, Read Replica 패턴, CQRS(Command Query Responsibility Segregation)는 스케일링의 기본 패턴이지만 양쪽 모두 누락.

### [D-7] JSON/JSONB 컬럼 설계 가이드

PostgreSQL의 JSONB 사용이 일반화되었으나, 언제 정규 컬럼 대신 JSON을 사용할지, JSON 인덱싱(GIN) 전략 등이 없다.

### [D-8] 데이터베이스 테스트 전략

테스트 DB 격리, 트랜잭션 롤백 패턴, 팩토리/픽스처 설계 등 DB 관련 테스트 전략이 양쪽 모두 누락.

---

## 요약

### Conflicts

| 번호 | 주제 | 상충 유형 | 추천 |
|------|------|-----------|------|
| A-1 | 역정규화 접근 태도 | 불일치 | 병합 |
| A-2 | 성능 최적화 순서 | 불일치 | Internal |
| A-3 | 인덱스 설계 깊이와 관점 | 보완적 불일치 | 병합 |

**총 3건** (직접 모순 0건, 불일치 3건) -- 심각한 충돌은 없으며 관점과 깊이의 차이

### Decisions

| 번호 | 결정 사항 | 영향 범위 |
|------|----------|----------|
| 1-2 | DB 범위: PostgreSQL 전용 vs DB-agnostic | 스킬 전체 |
| 3-4 | NoSQL 포함 여부 | 스킬 범위 |
| 5-6 | ORM 코드 예시 깊이 | 타 스킬과 경계 |
| 7-8 | 마이그레이션 패턴 소속 | 타 스킬과 경계 |
| 9-10 | Clean Architecture 원칙 위치 | 스킬 구조 |
| 11 | 커넥션 풀링 소속 | 타 스킬과 경계 |

**총 11건의 결정 필요**

### Gaps

| 번호 | 누락 주제 | 중요도 |
|------|----------|--------|
| D-1 | 파티셔닝 전략 | 높음 |
| D-2 | 락과 동시성 제어 | 높음 |
| D-3 | Soft Delete 패턴 | 중간 |
| D-4 | 감사(Audit) 패턴 | 중간 |
| D-5 | 멀티테넌시 패턴 | 중간 |
| D-6 | 읽기 복제와 CQRS | 높음 |
| D-7 | JSON/JSONB 설계 | 중간 |
| D-8 | 데이터베이스 테스트 전략 | 중간 |

**총 8건의 Gap** (높음 3건, 중간 5건)
