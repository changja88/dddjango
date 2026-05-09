# Ports And Adapters

This reference is provisional and uses fallback sources until a dedicated implementation-patterns reference exists.

Load this when dependency direction, clean/hexagonal structure, port ownership, adapter placement, Protocol/ABC contracts, or ACL placement is the main question.

## Dependency Direction

- Domain owns domain concepts and rules.
- Application owns use case orchestration and depends on domain abstractions.
- Infrastructure implements external details such as ORM, SDKs, message brokers, filesystem, cache, and environment access.
- Interface adapters convert HTTP, CLI, admin, task queue, or message input into application calls.
- Dependencies should point inward toward domain/application policy.

## Port Ownership

- Define a port only when the application/domain needs a stable role independent from an external detail.
- Name ports by role, not by technology: `PaymentGateway`, not `StripeClient`.
- Keep port methods narrow and use domain/application DTOs or value objects.
- Use Python `Protocol` for structural seams when it improves type checking and test doubles.
- Use ABCs when explicit inheritance or runtime registration is useful.

Do not create an interface for every class. A direct dependency is acceptable for simple, stable, internal collaborators.

## Adapter Boundaries

- Routers, views, templates, forms, schemas, serializers, management commands, Celery tasks, and external message handlers are adapters.
- Adapters may validate input, authenticate/authorize, translate DTOs, call use cases, and map responses.
- Adapters should not own core state transitions, policies, or aggregate invariants.
- Infrastructure adapters should translate ORM/SDK details into application/domain-facing roles.

## Anticorruption Layer

- Use ACL when an upstream or legacy model uses language that conflicts with the downstream bounded context.
- Put translation at the boundary, not throughout the domain model.
- Translate both data shape and meaning: statuses, units, identifiers, and lifecycle semantics.
- If the integration contract is public to many consumers, coordinate with `architecture-api` for Published Language and versioning.
