---
name: architecture-implementation-patterns
description: Provisional until dedicated source reference exists; use fallback sources for DDD implementation architecture patterns: layered architecture, clean architecture, hexagonal/ports-adapters, dependency direction, repository, Unit of Work, CQRS, event sourcing, outbox, ACL, saga, and legacy integration. Use for 헥사고날, 클린 아키텍처, 의존성 역전, repository/UoW, outbox, ACL, 프로젝트 구조. Prefer workflow-dddjango-subagents for composite/subagent Django work, architecture-ddd when domain boundaries are unclear, architecture-db for schema/transactions, architecture-api for REST/API contracts, status codes, Problem Details, idempotency, versioning, or OpenAPI, and implementation skills for concrete Django/Python code.
---

# Implementation Patterns

This skill is provisional. A dedicated `workspace/reference/architecture-implementation-patterns/reference/final.md` source does not exist yet.

Source policy decision: `allow-provisional-with-fallback`. Use the fallback scope below without presenting it as a finalized dedicated reference:

- `workspace/reference/architecture-ddd/reference/final.md` for layered architecture, DIP, ports/adapters, CQRS, package structure, repository/UoW, event sourcing, saga, ACL, and integration events.
- `workspace/reference/implementation-django/reference/final.md` for Django project/app structure, Fat Model/Thin View, service/selectors, and pragmatic Django vs DDD trade-offs.
- `workspace/reference/implementation-python/reference/final.md` for Protocol boundaries and repository/UoW placeholder guidance.
- `workspace/docs/ddd-implementation-standard.md` and product docs for Django-specific boundary and transaction decisions.

Use this skill after the DDD model is clear and before concrete Django/Python code when architecture pattern choice will affect dependency direction, adapters, persistence boundaries, or integration reliability.

## Routing

- If the user explicitly asks for subagents, subagent/subagents, 서브에이전트, 역할 분해, 병렬 검토, 책임 분배, or dddjango workflow in a Django task, use `workflow-dddjango-subagents` first.
- If subdomains, bounded contexts, ubiquitous language, aggregates, or invariants are unclear, use `architecture-ddd` before choosing implementation patterns.
- If the main question is table design, constraints, indexes, locking, isolation, rollout constraints, or operational migration safety, use `architecture-db`.
- If the main question is REST resource design, status codes, Problem Details, idempotency key behavior, pagination, versioning, or OpenAPI, use `architecture-api`.
- If the user asks to edit Django model, service, selector, migration, Router, template, or Python code after the pattern is already decided, use the relevant implementation skill.
- For simple CRUD, a small field rename, or a short explanation, do not introduce repository/UoW, hexagonal layers, CQRS, outbox, or ACL unless the scenario has a real boundary or consistency need.

## Reference Loading

- Read [pattern-selection.md](references/pattern-selection.md) for when to choose or avoid layered, clean, hexagonal, CQRS, event sourcing, saga, transaction script, or Django-native structures.
- Read [ports-adapters.md](references/ports-adapters.md) for dependency direction, ports, adapters, Protocol/ABC boundaries, Django adapter boundaries, and ACL placement.
- Read [repository-uow.md](references/repository-uow.md) for repository and Unit of Work decisions, Django service/selectors, QuerySet trade-offs, and testability costs.
- Read [outbox-acl.md](references/outbox-acl.md) for outbox, domain vs integration events, external side-effect timing, ACL, and legacy/upstream model protection.

## Runtime Rules

- Choose the lightest pattern that protects the domain boundary, dependency direction, or consistency requirement.
- Keep strategy before structure: do not select repository, UoW, CQRS, or outbox before aggregate, invariant, use case, and integration boundaries are known.
- Default Django path for many projects is model methods plus services/selectors. Add repository/UoW or pure domain separation only when the benefit exceeds Django integration cost.
- Keep domain/application code independent from infrastructure details. Frameworks, ORM calls, SDK clients, HTTP requests, and environment access belong in adapters or infrastructure.
- Treat CQRS, event sourcing, saga, outbox, and ACL as conditional tools, not as default architecture.
- For external side effects, state whether the effect runs after commit, through an outbox-style handoff, or through another reliable integration boundary.
- For risky writes, identify transaction owner and side-effect/reliability boundary, then hand off DB locking/isolation, API idempotency behavior, and integration/concurrency tests to the owning skills.
- If source limits affect a recommendation, say the skill is using fallback sources and identify the assumption.
- Only report tests, validation, review, browser checks, or subagent work that was actually executed. If not executed, say so.
