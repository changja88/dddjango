---
name: architecture-db
description: >
  Use when the user asks to design a database schema, model data,
  create an ERD, normalize tables, optimize queries, design indexes,
  choose isolation level, model hierarchical data, or handle table
  inheritance. Also use for any relational database design, schema
  modeling, normalization, index strategy, transaction, or query
  performance decision, including small changes like adding a column
  or choosing a primary key. Covers conceptual/logical/physical
  modeling, normalization, denormalization tradeoffs, B+Tree indexes,
  transaction isolation, EXPLAIN ANALYZE, hierarchy/inheritance, and
  polymorphic modeling. Focuses on general RDB principles. For Django
  ORM code use implementation-django; for domain modeling use
  architecture-ddd; for REST API design use architecture-api.
---

# 데이터베이스 설계 원칙

이 스킬은 개념적 모델링부터 물리적 최적화까지 관계형 데이터베이스 설계를
다룬다. 특정 벤더에 종속되지 않는 일반적인 RDB 원칙에 집중한다.

도메인 모델 설계(애그리거트, 바운디드 컨텍스트)에 대해서는 architecture-ddd에
위임한다. Django ORM 코드(QuerySet, select_related, 마이그레이션, PostgreSQL
기능)에 대해서는 implementation-django에 위임한다. REST API 설계 원칙
(엔드포인트, 페이지네이션, 상태 코드)에 대해서는 architecture-api에 위임한다.

**기본 요구사항 — 모든 모드에 적용:**
- 먼저 정규화하고, 측정된 성능이 요구할 때만 비정규화한다. 최적화 순서는:
  느린 쿼리 수정 -> 인덱스 -> 캐시 -> 비정규화.
- 모든 테이블에는 명확한 기본키가 필요하다. 자연키 후보가 없으면 대리키를
  선호한다.
- 인덱스 설계는 테이블 구조가 아닌 쿼리 워크로드를 따른다.

아래 섹션에서 다루는 주제를 작업할 때는 링크된 참조 파일을 읽고 상세한
규칙과 예시를 확인한다.

**참조 로딩 규칙:**
- 설계 모드: 스키마를 제안하기 전에 관련 참조를 먼저 읽는다.
- 리뷰 모드: 리뷰 결과를 확정하기 전에 인용된 모든 원칙의 참조를 읽는다.
- 리팩터링 모드: 변경 사항을 제시하기 전에 적용된 각 패턴의 참조를 읽는다.

## 응답 구조

모든 응답은 다음 구조를 따른다:

1. **[주요 내용]** -- 모드에 따른 코드, 리뷰, 리팩터링 결과
2. **[관련 스킬 참조]** -- 사용자의 다음 단계를 안내하는 연결점

이 스킬은 11개의 상호 연결된 스킬 체계의 일부이다.
사용자는 현재 작업 후 어떤 스킬을 호출해야 하는지 모르는 경우가
많으므로, 관련 스킬 참조가 워크플로우의 자연스러운 연결을 만든다.

ALWAYS use this exact template for the closing section:
```
---
> **관련 스킬 참조:**
> - [topic] → **[skill-name]** 스킬
```

## 운영 모드

사용자의 요청에 따라 모드를 선택한다:
- **설계**: 스키마, ERD, 인덱스 또는 데이터 모델을 처음부터 설계
- **리뷰**: 기존 스키마 또는 쿼리의 설계 위반 사항 평가
- **리팩터링**: 기존 스키마, 인덱스 또는 쿼리 개선

의도가 모호한 경우 설계 모드를 기본으로 한다.

요청이 여러 모드에 걸치는 경우(예: "리뷰하고 리팩터링해줘"), 리뷰를 먼저
적용한 후 같은 스키마에 리팩터링을 적용한다.

### 설계 모드

데이터베이스 스키마를 설계할 때 모든 원칙을 묵시적으로 적용한다. 원칙을
설명하는 인라인 주석 없이 깔끔한 스키마를 생성한다. 모델링 프로세스를 따른다:
요구사항 이해 -> 개념적(ERD) -> 논리적(정규화) -> 물리적(인덱스, 최적화).

설계를 제안하기 전에 관련 주제 영역의 참조 파일을 읽는다.

### 리뷰 모드

잘 설계된 스키마를 리뷰할 때는 개선 사항을 나열하기 전에 설계가 잘된 부분을
먼저 인정한다. 부실한 설계를 리뷰할 때는 가장 영향이 큰 문제부터 집중한다.

각 발견 사항은 다음 형식으로 작성한다:

```
[원칙] — 이것이 데이터 무결성이나 성능에 해를 끼치는 이유 설명
```

리뷰를 확정하기 전에 아래의 모든 항목을 검증한다. 누락된 항목이 있으면 사용자가 나중에 같은 문제를 다시 발견하게 된다.
- [ ] 누락되었거나 부적절한 기본키
- [ ] 문서화된 정당화 없는 정규화 위반 (1NF-3NF)
- [ ] 자주 조회되는 컬럼이나 JOIN 키에 누락된 인덱스
- [ ] 잘못된 컬럼 순서의 복합 인덱스
- [ ] 접근 계층의 N+1 쿼리 패턴
- [ ] 유스케이스에 맞지 않는 격리 수준
- [ ] 적절한 패턴 없이 저장된 계층적 데이터
- [ ] 참조 무결성 전략 없는 다형적 연관관계
- [ ] 성능 측정 전 조기 비정규화
- [ ] 누락된 외래키 제약 조건 또는 캐스케이딩 규칙

리뷰 결과를 확정하기 전에 인용된 모든 원칙의 참조를 읽어 정확성을 확인한다.

### 리팩터링 모드

스키마나 쿼리를 리팩터링할 때 변경 전/후를 보여주고 각 변경의 이유를 명시한다.
각 변경을 특정 원칙에 연결하여 근거를 추적할 수 있게 한다. 각 변경은 다음
형식으로 작성한다:

```
[Before]
<원래 스키마 또는 쿼리>

[After]
<개선된 스키마 또는 쿼리>

[Reason] 원칙 — 이 변경이 설계를 개선하는 이유 설명
```

변경 사항을 제시하기 전에 아래의 적용 가능한 모든 개선을 적용한다. 적용 가능한 항목을 건너뛰면 사용자가 추가 리팩토링을 해야 하므로 모두 적용한다.
- [ ] 관련 스킬 참조 포함 -- 사용자의 다음 워크플로우를 위한 스킬 연결
- [ ] 누락된 PK -> 적절한 기본키 추가
- [ ] 정규화 위반 -> 적절한 정규형으로 정규화
- [ ] 누락된 인덱스 -> 쿼리 워크로드 기반으로 인덱스 추가
- [ ] 잘못된 복합 인덱스 순서 -> 순서 변경 (동등 조건이 범위 조건보다 앞)
- [ ] N+1 쿼리 -> JOIN 또는 배치 로딩으로 변환
- [ ] 잘못된 격리 수준 -> 유스케이스에 맞게 조정
- [ ] 부실한 계층 표현 -> 적절한 패턴 적용
- [ ] 깨진 참조 무결성 -> 제약 조건 추가 또는 패턴 변경
- [ ] 조기 비정규화 -> 정규화된 형태로 복원
- [ ] 대형 테이블의 Seq Scan -> 커버링 또는 부분 인덱스 추가

변경 사항을 제시하기 전에 적용된 각 패턴의 참조를 읽는다.

형식이 개선의 깊이를 제한하지 않도록 한다. 스키마에 근본적인 재설계가
필요한 경우 먼저 전체 재설계를 적용한 후 위의 형식으로 변경 사항을 제시한다.

---

## 1. 모델링 프로세스

전체 워크플로: 요구사항 -> 개념적(ERD) -> 논리적(정규화) -> 물리적(인덱스,
최적화). 개념적 모델링이 가장 중요한 단계이다 — 이것을 올바르게 하면 나머지가
따라온다.

> Reference: `references/modeling.md`

---

## 2. 정규화와 비정규화

1NF부터 BCNF까지 특정 이상 현상을 제거한다. 먼저 정규화하고, 측정된 성능이
요구할 때만 비정규화한다. 네 가지 비정규화 기법: 테이블 병합, 파생 컬럼,
분할(수직/수평), 관계 단축.

> Reference: `references/normalization.md`

---

## 3. 인덱스와 성능

최적화 순서: 느린 쿼리 -> 인덱스 -> 캐시 -> 비정규화(최후의 수단). B+Tree는
리프 노드에 정렬된 데이터를 저장하고 형제 포인터로 범위 쿼리를 지원한다. 복합
인덱스는 최좌선 접두사 규칙을 따른다. 커버링 인덱스는 테이블 룩업을 제거한다.
부분 인덱스는 저장 공간과 유지 비용을 줄인다.

> Reference: `references/index-and-performance.md`

---

## 4. 트랜잭션과 격리

ACID 보장. Read Uncommitted부터 Serializable까지 네 가지 격리 수준. 높은
격리 수준 = 적은 이상 현상이지만 낮은 동시성. Read Committed가 대부분의
OLTP에 적합하다; Serializable은 재시도 로직이 필요하다.

> Reference: `references/transactions.md`

---

## 5. 쿼리 최적화

EXPLAIN ANALYZE 출력 읽기: cost, rows, actual time, buffers. 스캔 유형
(Seq -> Index -> Bitmap -> Index-Only). 조인 유형(Nested Loop, Hash, Merge).
N+1 문제: JOIN 또는 배치 로딩으로 감지하고 수정한다.

> Reference: `references/query-optimization.md`

---

## 6. 계층 패턴

트리 데이터를 위한 네 가지 패턴: Adjacency List(단순, CTE 필요), Nested Set
(빠른 읽기, 비싼 쓰기), Materialized Path(LIKE 쿼리), Closure Table(가장
유연, 추가 저장 공간).

> Reference: `references/hierarchy-patterns.md`

---

## 7. 상속과 다형성 패턴

세 가지 상속 매핑: Single Table(STI — 하나의 테이블, 타입 컬럼), Class Table
(CTI — 조인된 테이블), Concrete Table(TPC — 독립 테이블). 다중 부모 관계를
위한 다형적 연관관계.

> Reference: `references/inheritance-patterns.md`
