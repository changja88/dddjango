---
name: architecture-ddd
description: Use for DDD/domain modeling: subdomain classification, bounded contexts, context maps, ubiquitous language, aggregates, entities, value objects, invariants, domain events, domain services, use cases, and consistency boundaries. Use for 도메인 규칙, 상태 전이, 정책, 불변식, 하위 도메인, 바운디드 컨텍스트, 유비쿼터스 언어, 애그리거트, 컨텍스트 맵, 도메인 이벤트. Prefer workflow-dddjango-subagents for composite/subagent/서브에이전트, 역할 분해, 병렬 검토, 책임 분배, or dddjango workflow requests, architecture-db for schema/transactions, architecture-api for REST contracts, architecture-implementation-patterns for ports/adapters/CQRS/outbox structure, and implementation skills for Django code.
---

# DDD Architecture

Use this skill to turn business language and state changes into domain boundaries, model candidates, invariants, and handoffs. DDD here starts with strategic design before tactical patterns.

## Routing

- If the user explicitly asks for subagents, subagent/subagents, 서브에이전트, 역할 분해, 병렬 검토, 책임 분배, or dddjango workflow in a Django task, use `workflow-dddjango-subagents` first.
- If the question is mainly DB schema, constraints, indexes, transaction isolation, locking, or rollout risk, use `architecture-db`; use this skill first only when the domain invariant or aggregate boundary is unclear.
- If the question is mainly REST resources, URL shape, status codes, Problem Details, pagination, idempotency, or OpenAPI, use `architecture-api`; use this skill first only when domain terms or use cases are unclear.
- If the question is mainly layered/clean/hexagonal structure, ports/adapters, repository/UoW implementation, CQRS, outbox, ACL, or dependency direction, use `architecture-implementation-patterns` after the DDD model is clear.
- If the user asks for Django models, migrations, routers, views, templates, or tests and the domain rules are already clear, use the relevant implementation skill directly.
- For simple CRUD or a tiny wording explanation with no meaningful domain policy, do not force aggregates, context maps, or event storming.

## Reference Loading

- Read [strategic-design.md](references/strategic-design.md) for subdomain classification, problem vs solution space, ubiquitous language, bounded contexts, distillation, event storming, and team topology.
- Read [context-map.md](references/context-map.md) for context relationships, upstream/downstream direction, Partnership, Shared Kernel, Customer-Supplier, Conformist, ACL, OHS, Published Language, and Separated Ways.
- Read [tactical-patterns.md](references/tactical-patterns.md) for value objects, entities, aggregates, repositories as aggregate persistence concepts, domain services, application services, specifications, and supple design.
- Read [domain-events.md](references/domain-events.md) for domain events, dispatch timing, consistency boundaries, outbox decision points, event sourcing, saga, and integration-event boundaries.

## Runtime Rules

- Start with strategic design: subdomains, bounded contexts, ubiquitous language, and context relationships before applying tactical patterns.
- Separate problem space from solution space: discover domains and subdomains; design bounded contexts and model boundaries.
- Classify core, supporting, and generic subdomains so implementation strength matches business value and complexity.
- Keep ubiquitous language scoped to a bounded context. Same words may mean different things in different contexts.
- Design aggregates around true invariants and consistency boundaries. Keep them small, expose behavior through the root, and reference other aggregates by ID.
- Prefer real domain behavior in entities and value objects over anemic data structures plus procedural services.
- Use domain services for stateless domain rules that do not naturally belong to one aggregate; application services orchestrate use cases and transactions without owning business rules.
- When mapping toward Django, do not require a separate pure domain model by default. Django models can carry simple domain behavior; separate domain and infrastructure when ORM lifecycle, lazy loading, HTTP, SDKs, or framework details obscure the rules.
- If the target design puts core business rules in a Router, view, template, serializer/schema, or other adapter, identify it as a boundary problem and move the rule to domain or application responsibility before implementation.
- When raising domain events, state what happened, who consumes it if known, and whether dispatch happens before commit, after commit, or through an outbox-style handoff.
- Return concrete design decisions: subdomain type, bounded context, context-map relationship, key terms, aggregate candidates, invariants, events, consistency boundary, and use case candidates.
- Do not write Django model, Router, migration, or test code unless the user separately asks for implementation after the domain model is decided.
- Only report tests, validation, review, browser checks, or subagent work that was actually executed. If not executed, say so.
