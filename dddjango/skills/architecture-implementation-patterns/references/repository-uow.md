# Repository And Unit Of Work

This reference is provisional and uses fallback sources until a dedicated implementation-patterns reference exists.

Load this when deciding whether to introduce repository, Unit of Work, data mapper, service/selectors, or Django ORM direct access.

## Repository Decision

Use repository when:

- persistence should be expressed as aggregate collection operations;
- tests benefit from fake repositories around application services;
- domain/application code should not know ORM or QuerySet details;
- persistence mapping is complex enough that a translation boundary helps.

Avoid repository when:

- it only wraps `Model.objects.filter(...)` without changing language or responsibility;
- QuerySet composition is the real business need;
- Django model methods plus service/selectors are clearer;
- the domain is simple CRUD or supporting-domain workflow.

Repositories should be aggregate-oriented. Do not create separate repositories for every child entity by default.

## Unit Of Work Decision

Use Unit of Work when the use case needs an explicit transaction boundary across repositories or adapters.

In Django, `transaction.atomic()` is often the practical unit-of-work tool. A custom UoW abstraction is only worth the cost when it clarifies use case boundaries, improves testing, or decouples persistence implementation.

External side effects should not run inside the DB transaction unless the system can tolerate rollback mismatch. Prefer post-commit hooks or outbox-style handoff when reliability matters.

## Django Service And Selector Path

- Use services for write/use-case operations that coordinate multiple models, external services, or transactions.
- Use selectors for read/query logic and QuerySet optimization.
- Keep naming searchable and role-based.
- Keep business policies in model/domain behavior or domain services; services coordinate rather than own the policy.

## Data Mapper Split

Split ORM and domain models when:

- a rich domain model needs fast pure unit tests;
- ORM lifecycle or lazy loading would leak into rules;
- schema shape differs from domain language;
- external systems or persistence details force awkward domain objects.

Keep them together when the rule is simple and Django model behavior is explicit.
