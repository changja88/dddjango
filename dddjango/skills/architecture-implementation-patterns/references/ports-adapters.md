# Ports And Adapters

Load this when dependency direction, clean/hexagonal structure, port ownership, adapter placement, Protocol/ABC contracts, or ACL placement is the main question.

## Dependency Direction

- Domain owns domain concepts, state transitions, and invariants.
- Application owns use case orchestration and depends on domain concepts plus stable roles.
- Infrastructure implements external details such as ORM, SDKs, message brokers, filesystem, cache, and environment access.
- Interface adapters convert HTTP, CLI, admin, task queue, or message input into application calls.
- Dependencies point inward toward domain/application policy.

## Layer Responsibilities

| Layer | Allowed responsibility | Forbidden responsibility |
|---|---|---|
| presentation/interface | HTTP, CLI, admin, task, message input conversion, auth wiring, response mapping | core state transition or aggregate invariant ownership |
| application | use case orchestration, transaction boundary, repository/port calls, DTO mapping | direct dependency on framework request/response types |
| domain | entity, value object, aggregate, domain service, invariant, domain event | ORM, SDK, HTTP, filesystem, environment detail |
| infrastructure | ORM, SDK, broker, cache, filesystem, external API adapter implementation | forcing domain language to follow external models |

## Port Ownership

- Define a port only when application/domain needs a stable role independent from an external detail.
- Name ports by role, not by technology: `PaymentGateway`, not `StripeClient`.
- Keep port methods narrow and use domain/application DTOs, value objects, or identifiers.
- Use Python `Protocol` when structural typing improves test doubles or type checking.
- Use ABC when explicit inheritance, runtime registration, or shared base behavior is useful.

Do not create an interface for every class. Direct dependency is acceptable for simple, stable, internal collaborators.

## Adapter Boundaries

- Routers, views, templates, forms, schemas, serializers, management commands, Celery tasks, and external message handlers are interface adapters.
- ORM repositories, SDK clients, broker publishers, cache/filesystem adapters, and settings/env readers are infrastructure adapters.
- Adapters may validate input, authenticate/authorize, translate DTOs, call use cases, and map responses.
- Adapters should not own core state transitions, policies, or aggregate invariants.
- Infrastructure adapters translate ORM/SDK details into application/domain-facing roles.

## Anticorruption Layer Placement

- Use ACL when an upstream or legacy model uses language that conflicts with the downstream bounded context.
- Put translation at the boundary, not throughout the domain model.
- Translate both data shape and meaning: statuses, units, identifiers, lifecycle semantics.
- If the integration contract is public to many consumers, coordinate with `architecture-api` for published language and versioning.
