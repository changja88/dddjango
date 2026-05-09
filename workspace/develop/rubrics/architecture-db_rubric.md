# architecture-db Rubric

## Skill Scope

`architecture-db`는 도메인 모델을 지지하는 관계형 데이터베이스 설계를 담당하는 스킬이다. 평가 대상은 conceptual/logical/physical schema, ERD, normalization/denormalization, PK/FK, unique/check/not-null constraints, cascade/nullability, indexes, transaction boundary, isolation, locking, idempotency storage, query performance, EXPLAIN planning, and operational rollout constraints.

책임 경계:

- Django migration file implementation, `RunPython`, `apps.get_model()`, and `sqlmigrate` execution are owned by `implementation-django`.
- Domain aggregate/invariant discovery is owned by `architecture-ddd`; DB design supports those invariants.
- REST API idempotency/status/error contract is owned by `architecture-api`; DB may define storage support.
- ORM convenience alone must not weaken DB invariants.
- NoSQL, connection pooling, and low-level migration tool mechanics are out of scope unless the prompt explicitly includes them.

## Source Status

ready

Canonical sources:

- `workspace/docs/spec.md`
- `workspace/docs/ddd-implementation-standard.md`
- `workspace/docs/skill-contracts.md`
- `workspace/docs/workflow.md`
- `workspace/docs/reference-index.md`
- `workspace/reference/architecture-db/reference/final.md`

## Trigger Examples

- "주문과 주문 항목 테이블 schema, FK, unique constraint를 설계해줘."
- "중복 주문 방지를 위한 idempotency key 저장 구조와 unique constraint를 정해줘."
- "재고 차감과 예약 확정의 transaction isolation과 locking 전략을 설계해줘."
- "운영 중 status 컬럼 backfill, NOT NULL, index rollout 계획을 세워줘."
- "이 조회 패턴에 필요한 index와 정규화/역정규화 trade-off를 판단해줘."

## Anti-Trigger Examples

- "Django migration 파일을 실제로 작성해줘." -> `implementation-django`
- "주문 aggregate와 invariant를 먼저 정해줘." -> `architecture-ddd`
- "주문 생성 API의 status code와 Problem Details를 설계해줘." -> `architecture-api`
- "Ninja Router와 Schema를 구현해줘." -> `implementation-django-ninja`
- "pytest fixture를 작성해줘." -> `implementation-test`
- "간단한 모델 필드 rename만 해줘." -> `implementation-django`; no DB architecture ceremony unless production rollout risk exists

## Skill-Specific Hard Gates

- **Scenario-required consistency decision missing**: risky write/concurrency case omits transaction owner, locking/unique/idempotency, isolation/retry, side-effect timing handoff, or test criteria.
- **Risky Write Consistency Block missing**: product-docs risky write case lacks the required named consistency decisions.
- **Operational migration safety missing**: production migration plan omits expand/migrate/contract, rolling deploy compatibility, or lock/backfill/index risk.
- **Invariant not backed by DB**: domain invariant that needs DB enforcement lacks constraint, unique index, transaction, or stated reason for application-only enforcement.
- **Index trade-off missing**: index recommendation lacks query pattern and write-cost reasoning.
- **Migration implementation leakage**: rubric expects DB agent to write concrete Django migration operations instead of handing implementation to `implementation-django`.
- **Verification honesty**: claims EXPLAIN, migration, test, or subagent validation without evidence.

## Analytic Criteria

Use `common_rubric.md` scoring anchors. Core dimensions for this skill:

- **Data And API Consistency**: 5 when schema, constraints, indexes, transactions, idempotency storage, and API/storage implications align with scenario facts.
- **Implementation Pragmatism**: 5 when DB design balances normalization, performance, rollout risk, and Django implementation cost.
- **Test And Verification**: 5 when consistency, migration, query, and concurrency verification criteria are concrete and execution status is honest.
- **Domain Reasoning**: 5 when DB artifacts support aggregate/invariant decisions without redefining the domain model.
- **Workflow Fit**: 5 when operational/risky cases get handoff-ready DB decisions and simple cases stay lightweight.

Score 1 if the answer relies on ORM validation for critical uniqueness/consistency without explaining DB enforcement or trade-off.

## Reference-Derived Additions

Required reference coverage:

- Model from business understanding to conceptual, logical, and physical schema.
- Normalize first; denormalize only with query/performance evidence and synchronization cost.
- PK/FK, optionality, cardinality, unique/check/not-null constraints protect data meaning.
- Index design must reference query pattern, cardinality/selectivity, sort/range behavior, and write cost.
- Transaction/isolation/locking decisions must match anomaly risk.
- Idempotency storage needs key, owner, uniqueness, replay/conflict behavior handoff to API when relevant.
- Operational rollout considers backfill, nullable-to-not-null, concurrent index/lock risk, rolling deploy, and rollback.

## Required Public Fixtures

Positive prompt:

```text
재고 차감과 예약 확정이 동시에 들어오는 상황에서 DB schema, transaction boundary, locking, idempotency 저장 구조를 설계해줘.
```

Negative prompt:

```text
Order 모델의 memo 필드를 note로 바꾸는 작은 Django 수정만 해줘. 운영 DB 설계 리뷰나 subagent 계획은 필요 없어.
```

Additional public fixtures may include domain rules, query patterns, existing schema, migration constraints, EXPLAIN output, or production rollout constraints. Public materials must not expose expected locking strategy, hidden scoring notes, or private failure criteria.

## Private Grader Key Notes

Expected routing:

- Positive prompt: `architecture-db`; add `architecture-ddd` if invariant is unclear and `implementation-django` for migration implementation.
- Negative prompt: direct `implementation-django`; DB architecture only if rollout risk is explicitly present.

Expected answer evidence:

- Risky write case includes transaction owner, locking or unique/idempotency decision, isolation/retry, and test criteria.
- Schema/constraint/index decisions map to domain invariant and query pattern.
- Operational migration cases include expand/backfill/contract and rolling deploy notes.
- API idempotency behavior is handed to `architecture-api` while storage support is designed here.

Failure criteria:

- Missing consistency block for risky write product-docs case.
- No DB constraint/storage support for required uniqueness without justification.
- Production migration jumps to NOT NULL/index with no rollout plan.
- Indexes are suggested without query/write trade-off.
- Public eval packet leaks expected DB strategy or private criteria.

Applicable hard gates: `Scenario-required consistency decision missing`, `Risky Write Consistency Block missing`, `Operational migration safety missing`, `Verification honesty`, and `Workflow over-application` for simple negatives.

## Reference Loading Expectations

- Load `workspace/reference/architecture-db/reference/final.md` for schema, normalization, index, transaction, isolation, and performance criteria.
- Load `workspace/docs/ddd-implementation-standard.md` for risky write consistency block requirements.
- Load DDD reference when invariants are ambiguous.
- Load API reference when idempotency behavior or error semantics must be specified.
- Load Django reference only when migration implementation or ORM details are in scope.

## Raw Artifact Checklist

- ERD/table/column/relationship proposal or schema diff.
- Constraint/index list with reasons and query patterns.
- Transaction, isolation, locking, idempotency storage decisions.
- Risky Write Consistency Block when applicable.
- Migration rollout notes and DB/Django implementation handoff.
- EXPLAIN/query/migration/test command output when claimed, or explicit "Not run" list.

## Scenario Tags

Primary tags: `db`, `migration`, `concurrency`, `risky-write`, `test`, `review`, `negative-simple`.

Usually N/A unless combined with other work: `api`, `django-ninja`, `django-web`, `runtime`, `skill-folder`.

## Do Not Penalize

- Deferring concrete Django migration code to `implementation-django`.
- Not over-specifying isolation/locking when there is no concurrent invariant risk.
- Choosing application-level validation only when DB enforcement is impossible or clearly traded off.
- Avoiding denormalization until query evidence justifies it.
- Keeping simple field rename guidance lightweight when production rollout risk is absent.
