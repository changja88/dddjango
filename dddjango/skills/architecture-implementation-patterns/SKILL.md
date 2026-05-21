---
name: architecture-implementation-patterns
description: >
  Use for DDD implementation architecture patterns: layered/계층, clean/클린 아키텍처, hexagonal/헥사고날, ports-adapters/포트-어댑터/포트/어댑터, dependency direction/DIP/의존성 방향/의존성 역전, repository/UoW/레포지토리, CQRS, event sourcing, saga/사가, outbox/아웃박스, ACL, service layer/서비스 레이어, 구현 구조, 아키텍처 패턴, and 프로젝트 구조. Use for risky-write pattern decisions in payment/inventory/reservation/refund/permission/ledger flows: transaction owner, side-effect timing, outbox/saga/ACL handoff, and whether uniqueness/idempotency storage is needed. Prefer workflow-dddjango-subagents for coordinated work, subagents, role decomposition, parallel review, responsibility distribution, or dddjango workflow; architecture-ddd when domain boundaries are unclear; architecture-db for schema/transactions/locking/idempotency storage details; architecture-api for REST contracts/Idempotency-Key; and implementation skills for concrete Django/Python/test code. Do not use for simple CRUD or tiny edits with no real boundary, consistency, or replaceability need.
---

# Implementation Patterns

Use this skill after the DDD model is clear and before concrete Django/Python code when architecture pattern choice will affect dependency direction, adapters, persistence boundaries, or integration reliability.

This skill owns pattern-level decisions: Django-native structure, service layer, layered/clean/hexagonal architecture, ports/adapters, repository, Unit of Work, CQRS, event sourcing, saga, outbox, ACL, or no extra pattern.

## Routing

- If the user asks for coordinated implementation or review across multiple role areas, or asks for subagents, 서브에이전트, 역할 분해, 병렬 검토, 책임 분배, or dddjango workflow, use `workflow-dddjango-subagents` first.
- Keep direct pattern-selection questions here when the user is deciding whether to use layered, clean, hexagonal, repository/UoW, service layer, outbox, saga, ACL, CQRS, event sourcing, or a simpler Django-native structure.
- If subdomains, bounded contexts, ubiquitous language, aggregates, or invariants are unclear, use `architecture-ddd` before choosing implementation patterns.
- If the main question is table design, constraints, indexes, locking, isolation, idempotency storage, rollout constraints, or operational migration safety, use `architecture-db`.
- If the main question is REST resource design, status codes, Problem Details, `Idempotency-Key`, pagination, versioning, or OpenAPI, use `architecture-api`.
- If the user asks to edit Django model, service, selector, migration, Router, template, Python code, or tests after the pattern is already decided, use `implementation-django`, `implementation-django-ninja`, `implementation-django-web`, `implementation-python`, or `implementation-test` as appropriate.
- If the main question is source/reference governance, runtime cache sync, metadata alignment, leakage, validation coverage, or eval traceability for skills or references, use `source-reference-audit`.
- For simple CRUD, a small field rename, or a short explanation, do not introduce repository/UoW, hexagonal layers, CQRS, outbox, saga, event sourcing, or ACL unless the scenario has a real boundary, consistency, or replaceability need.

## Reference Loading

- Load only the reference file(s) relevant to the current implementation architecture task.
- Read [pattern-selection.md](references/pattern-selection.md) for the selection order and when to choose or avoid layered, clean, hexagonal, CQRS, event sourcing, saga, service layer, straightforward service functions, or Django-native structures.
- Read [ports-adapters.md](references/ports-adapters.md) for dependency direction, ports, adapters, Protocol/ABC boundaries, Django adapter boundaries, and ACL placement.
- Read [repository-uow.md](references/repository-uow.md) for repository, Unit of Work, Django service/selectors, QuerySet trade-offs, and data mapper decisions.
- Read [outbox-acl.md](references/outbox-acl.md) for domain vs integration events, outbox, external side-effect timing, event sourcing, saga, ACL, and risky write handoff.

## Runtime Rules

- Choose the lightest pattern that protects the domain boundary, dependency direction, consistency requirement, integration reliability, or test seam.
- Keep strategy before structure: do not select repository, UoW, CQRS, event sourcing, saga, outbox, or ACL before aggregate, invariant, use case, and integration boundaries are known.
- Default Django path for many projects is model methods plus services/selectors. Add repository/UoW or pure domain separation only when the benefit exceeds Django integration cost.
- Keep domain/application code independent from infrastructure details. Frameworks, ORM calls, SDK clients, HTTP requests, filesystem, cache, and environment access belong in adapters or infrastructure.
- Treat CQRS, event sourcing, saga, outbox, and ACL as conditional tools, not as default architecture.
- For external side effects, state whether the effect runs after commit, through an outbox-style handoff, as a saga step, or through another reliable integration boundary.
- For risky writes, output a visible section or table titled `Risky Write Consistency Block`. This skill owns the pattern decision: Django-native transaction, service layer, port/adapter, outbox, saga, ACL, or no extra pattern. State the transaction owner or owning use case, side-effect timing or reliability boundary, and whether uniqueness/idempotency storage is needed, then hand off concrete DB locking/isolation/retry, `Idempotency-Key`/status code/Problem Details API behavior, and integration/concurrency tests to the owning skills.
- Only report tests, validation, review, browser checks, Serena usage, or subagent work that was actually executed. If not executed, say so.
