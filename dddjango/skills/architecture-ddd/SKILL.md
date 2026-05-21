---
name: architecture-ddd
description: >
  Use for DDD/domain modeling: subdomains, problem vs solution space, bounded contexts, context maps, ubiquitous language, event storming, team-boundary discovery, aggregates, entities, value objects, invariants, domain events/services, use cases, and consistency boundaries. Use for DDD 설계, 도메인 모델링, 서브도메인, 문제 공간/솔루션 공간, 도메인 규칙, 도메인 정책, 상태 전이, 이벤트 스토밍, 유스케이스/사용 사례, 도메인 서비스, 엔티티, 값 객체, 불변식, 바운디드 컨텍스트, 컨텍스트 맵, 유비쿼터스 언어, 애그리거트, 도메인 이벤트, 일관성 경계. Prefer workflow-dddjango-subagents for composite/risky/subagent work, architecture-db for schema/transactions, architecture-api for REST contracts, architecture-implementation-patterns for ports/adapters/CQRS/outbox, and implementation skills for Django code. Do not use for simple CRUD, tiny wording explanations, typo-only edits, or already-scoped implementation with no meaningful domain policy.
---

# DDD Architecture

Use this skill to turn business language and state changes into domain boundaries, model candidates, invariants, and handoffs. DDD here starts with strategic design before tactical patterns.

## Routing

- If the user explicitly asks for subagents, subagent/subagents, 서브에이전트, 역할 분해, 병렬 검토, 책임 분배, or dddjango workflow in a Django task, use `workflow-dddjango-subagents` first.
- If the work is composite or risky across domain rules, DB schema/transactions, REST contracts, Django implementation, and tests, use `workflow-dddjango-subagents` first.
- If the question is mainly DB schema, constraints, indexes, transaction isolation, locking, or rollout risk, use `architecture-db`; use this skill first only when the domain invariant or aggregate boundary is unclear.
- If the question is mainly REST resources, URL shape, status codes, Problem Details, pagination, idempotency, or OpenAPI, use `architecture-api`; use this skill first only when domain terms or use cases are unclear.
- If the question is mainly layered/clean/hexagonal structure, ports/adapters, repository/UoW implementation, CQRS, outbox, ACL, or dependency direction, use `architecture-implementation-patterns` after the DDD model is clear.
- If the user asks for Django models, migrations, routers, views, templates, pytest mechanics, or TDD sequencing and the domain rules are already clear, use the relevant implementation or TDD skill directly.
- For simple CRUD or a tiny wording explanation with no meaningful domain policy, do not force aggregates, context maps, or event storming.

## Reference Loading

- Load only the reference file(s) relevant to the current DDD modeling task.
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
- If aggregate-owned lifecycle state protects an invariant, do not expose it as an externally mutable public field. Expose read-only observations or query methods, and change state only through aggregate behavior methods.
- Keep neighboring contexts such as availability, inventory, payment, or shipping outside the aggregate. Represent them with IDs, boundary calls, domain events, or after-commit handoffs rather than child entities or shared mutable collections.
- Prefer real domain behavior in entities and value objects over anemic data structures plus procedural services.
- Use domain services for stateless domain rules that do not naturally belong to one aggregate; application services orchestrate create/load/save, transactions, and boundary handoffs without owning business rules or lifecycle state transitions.
- When mapping toward Django or another framework, keep the DDD default as a domain/application model that does not depend on infrastructure details. A simplified Django folder structure can be a pragmatic implementation handoff, but do not treat an ORM model as the default aggregate model during DDD design unless a later implementation skill explicitly accepts that tradeoff.
- If the target design puts core business rules in a Router, view, template, serializer/schema, or other adapter, identify it as a boundary problem and move the rule to domain or application responsibility before implementation.
- When raising domain events, state what happened, who consumes it if known, and whether dispatch happens before commit, after commit, or through an outbox-style handoff.
- For risky writes, state the DDD-owned invariant, aggregate boundary, consistency boundary, domain event, and domain-level side-effect timing. Hand pattern choices such as repository/UoW, outbox, saga, ACL, and transaction-owner structure to `architecture-implementation-patterns`; hand locking, idempotency storage, and isolation/retry to `architecture-db`; hand `Idempotency-Key` behavior to `architecture-api`; hand integration/concurrency test criteria to `implementation-test` or `workflow-dddjango-subagents` unless the current step explicitly owns those decisions. For explicitly small in-memory fixtures or pure unit-test exercises, do not invent repository/UoW/hexagonal/DB machinery; state the limitation instead.
- Return concrete design decisions: subdomain type, bounded context, context-map relationship, key terms, aggregate candidates, invariants, events, consistency boundary, and use case candidates.
- Do not write Django model, Router, migration, or test code during DDD-only modeling. In combined work, make the DDD decisions first and hand implementation to the relevant skills or assigned implementation step.
- Only report tests, validation, review, browser checks, or subagent work that was actually executed. If not executed, say so.
