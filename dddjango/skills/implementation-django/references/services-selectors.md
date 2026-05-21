# Services And Selectors

Use this reference when a Django change needs a service layer, selector, application service, repository trade-off, or Django/DDD mapping decision.

Source basis: Two Scoops of Django, HackSoft Django Styleguide, Architecture Patterns with Python.

## When To Add A Service

Start with Django model methods and QuerySets for simple work. Add a service when one or more of these are true:

- A use case updates or coordinates multiple models.
- The same business flow is duplicated across views, commands, APIs, or jobs.
- The flow owns a transaction boundary.
- External side effects such as email, payment, files, or message publishing are involved.
- A model is becoming difficult to understand because orchestration and persistence details are mixed with domain behavior.

## Service Shape

- Prefer explicit function names such as `<entity>_<action>`: `order_confirm`, `user_create`, `article_publish`.
- Accept keyword-only inputs when it clarifies the use case contract.
- Return the domain object, result DTO, or identifier that the caller actually needs.
- Keep request, response, schema, serializer, and template objects out of service signatures.
- Put transaction ownership in the service when the use case must be atomic.
- Move external side effects after commit with `transaction.on_commit()` when the side effect must not happen for rolled-back writes.

## Selector Shape

- Use selectors for reusable read use cases that are larger than one chainable QuerySet predicate.
- Return a QuerySet when the caller should continue filtering, paginating, prefetching, or counting.
- Materialize to lists or DTOs only when the use case requires a stable snapshot or non-ORM return shape.
- Keep select/prefetch decisions near the selector when they are part of the read contract.

## DDD Mapping In Django

- Treat Django ORM models as domain objects when invariants are simple and model methods express behavior clearly.
- Separate domain objects from ORM models only when ORM lifecycle, lazy loading, field types, or infrastructure concerns obscure the domain model.
- Use application services to coordinate loading, domain method calls, transactions, and persistence.
- Keep core business decisions in entities, value objects, aggregate methods, or domain services rather than in application services.
- Create a domain service only when a rule does not naturally belong to one entity or value object.

## Repository Trade-Off

- Do not create a repository just to wrap simple QuerySet calls.
- Consider a repository when the domain is complex, a fake repository would materially improve tests, or persistence details must be hidden behind a stable domain-oriented collection.
- If a repository is introduced, keep the interface narrow and domain-oriented. Avoid leaking arbitrary QuerySet power through it.
- Do not introduce Unit of Work or port/adapter layers unless the architecture decision has already justified the extra boundary.

## Review Questions

- Is the rule owned by the model/domain object, service, selector, or database for a clear reason?
- Is a simple Django model method enough?
- Does a service hide HTTP, form, schema, and task-runner details from the use case?
- Are side effects and transactions ordered so rollback cannot leave external systems inconsistent?
- Does the design avoid both fat views and unnecessary architecture layers?
