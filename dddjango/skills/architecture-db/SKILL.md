---
name: architecture-db
description: >
  Use for relational database architecture: ERD, conceptual/logical/physical modeling, normalization/denormalization, primary/foreign keys, unique/check/not-null constraints, cascade behavior, composite/covering/partial indexes, transactions, isolation, locking, concurrency, idempotency storage, duplicate prevention, query performance, EXPLAIN ANALYZE, hierarchy/inheritance modeling, rollout constraints, backfill/index-lock risk, migration safety. Use for ERD, 정규화, 인덱스, 제약조건, transaction/트랜잭션, locking, 동시성, 멱등성 저장, 중복 요청 방지, 부분 인덱스, EXPLAIN ANALYZE, 운영 마이그레이션, 상태 컬럼 backfill, NOT NULL 전환, rolling deploy, migration risk. Prefer workflow-dddjango-subagents for coordinated multi-role implementation or review, architecture-ddd when invariants are unclear, architecture-implementation-patterns for repository/UoW/outbox/CQRS/hexagonal/dependency direction, architecture-api for REST contracts, and implementation-django for concrete migration files.
---

# DB Architecture

Use this skill to design relational data structures that protect domain invariants and support query/write patterns. This skill decides the database shape and operational constraints; it does not write concrete Django migration files.

## Routing

- If the user asks for coordinated implementation or review across multiple role areas, or asks for subagents, 서브에이전트, 역할 분해, 병렬 검토, 책임 분배, or dddjango workflow, use `workflow-dddjango-subagents` first.
- Keep direct DB design questions here, including risky transaction, locking, isolation, uniqueness, idempotency storage, backfill, and index-lock examples, when the user is asking for database architecture rather than multi-role implementation.
- If aggregate boundaries, domain invariants, ubiquitous language, or state transitions are unclear, use `architecture-ddd` before designing the schema.
- If the main work is repository/UoW, outbox architecture, CQRS, hexagonal/ports-adapters, ACL, or dependency direction, use `architecture-implementation-patterns`; keep concrete storage, constraints, and transaction choices here.
- If the main work is REST resources, status codes, Problem Details, pagination, versioning, `Idempotency-Key` contract, or OpenAPI, use `architecture-api`; keep DB storage implications here.
- If the user asks to implement Django `models.py`, `RunPython`, `apps.get_model()`, `sqlmigrate`, or migration files, use `implementation-django` after DB design is clear.
- If the user asks for pytest integration/concurrency tests, use `implementation-test` after DB invariants and transaction criteria are known.
- For a simple field rename or local CRUD model with no invariant/rollout risk, do not force full ERD, locking, or migration strategy ceremony.

## Reference Loading

- Read [schema-modeling.md](references/schema-modeling.md) for modeling process, ERD, keys, cardinality, optionality, normalization, denormalization, hierarchy, and inheritance/polymorphism.
- Read [constraints-indexes.md](references/constraints-indexes.md) for PK/FK/unique/check/not-null decisions, cascade implications, B+Tree trade-offs, composite/covering/partial indexes, and index write cost.
- Read [transactions-locking.md](references/transactions-locking.md) for ACID, isolation levels, concurrency phenomena, locking strategy, risky write consistency, and side-effect timing handoffs.
- Read [rollout-constraints.md](references/rollout-constraints.md) for EXPLAIN ANALYZE, query optimization, N+1, backfill/index-lock risk, expand/backfill/contract rollout, and rollback considerations.

## Runtime Rules

- Start from domain invariants, aggregates/entities, query patterns, write contention, and rollout constraints; do not let ORM convenience erase DB invariants.
- Model conceptually first, then logical schema, then physical indexes/partitioning/performance choices.
- Normalize first to remove update/insert/delete anomalies; denormalize only for measured read pressure or clear operational need.
- Use database constraints for invariants the database can enforce: primary keys, foreign keys, unique, check, not null, and appropriate cascade rules.
- Design indexes from actual query shapes and write cost. Explain composite index order and when covering or partial indexes apply.
- For risky writes, include a `Risky Write Consistency Block` with transaction owner, locking strategy, uniqueness/idempotency storage, API idempotency handoff, side-effect timing, isolation/retry, and integration/concurrency test criteria.
- For operational changes, separate DB design from concrete Django migration implementation; hand off migration file details to `implementation-django`.
- Report only tests, validation, review, browser checks, or subagent work that was actually executed. If not executed, say so.
