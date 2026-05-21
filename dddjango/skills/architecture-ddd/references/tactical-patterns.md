# Tactical Patterns

Load this after strategic boundaries are clear and the task needs aggregate, entity, value object, service, specification, or domain model quality decisions.

## Value Objects

- Use value objects for concepts defined by their attributes rather than identity.
- Make them immutable and self-validating.
- Put behavior that belongs to the concept on the value object.
- Prefer value objects for meaningful domain concepts such as money, period, address, quantity, or policy threshold.

## Entities

- Use entities for concepts with identity and lifecycle.
- Compare entities by identity, not by every field.
- Keep entities inside an aggregate boundary. If a concept needs an independent consistency boundary, model it as a separate aggregate root rather than a free-floating entity.
- Avoid anemic models where entities are only data and all business behavior lives in procedural services.

## Aggregates

- An aggregate is a consistency boundary and usually a transaction boundary.
- Protect true invariants inside the aggregate.
- Keep aggregates as small as the invariant allows.
- Access members through the aggregate root.
- Reference other aggregates by ID, not by direct object graph, when crossing consistency boundaries.
- Use eventual consistency through events when a rule spans aggregate boundaries.

## Services

- Domain service: stateless domain rule that does not naturally belong to one aggregate or value object.
- Application service: orchestrates a use case, loads aggregates, starts transactions, calls domain behavior, and persists results.
- Do not put business rules in application services just because they coordinate several calls.
- Do not make aggregates depend on domain services or infrastructure services.
- In Django projects, keep the DDD modeling default as domain/application behavior that does not depend on ORM, HTTP, SDK, or schema details. A simplified Django package layout can be a later implementation tradeoff, but do not make Active Record mechanics the default aggregate boundary in this skill.
- Treat Routers, views, templates, and schemas as adapters. They may validate input and call use cases, but should not own core state transitions or policies.

## Repository And Specification Concepts

- Repository is a persistence boundary for aggregates, not for every child entity.
- Repository implementation and Unit of Work mechanics belong to implementation-pattern or Django implementation skills.
- Specification can express reusable business predicates for validation, selection, or construction when the rule deserves a name.

## Supple Design

- Use intention-revealing names for domain methods.
- Prefer side-effect-free behavior on value objects.
- State important invariants and postconditions explicitly.
- Split concepts along natural domain contours: things that change together stay together, things that change for different business reasons separate.
- Keep standalone domain classes when a concept can be understood without unnecessary collaborators.
- Prefer operations closed over the same value type when that makes the domain algebra clear, such as `Money + Money -> Money`.
