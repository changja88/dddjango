# Responsibility

Use this reference for responsibility separation, change reasons, cohesion/coupling, responsibility-driven design, comments, and review output.

## Clean Code Goal

- Optimize for communication, simplicity, and only the flexibility that current evidence justifies.
- Manage complexity by reducing change amplification, cognitive load, and hidden unknowns.
- Preserve behavior and domain meaning while improving understandability.

## Responsibility

- Group code that changes for the same reason; separate code that changes for different reasons.
- Judge responsibility by domain rule, I/O, persistence, rendering, notification, or orchestration concerns, not by line count alone.
- Keep role, responsibility, and collaboration explicit: decide the message/behavior first, then the object or function that should own it.
- High cohesion and low coupling matter more than an even distribution of methods across files.
- In Django/dddjango work, do not bury business rules in views, routers, schemas, or templates.

## Django/dddjango Boundary Smells

- Fat Model: model methods may own local invariants and state questions, but not unrelated external I/O, notification, reporting, permission, or use-case orchestration.
- Fat View/Router: Django views, DRF views, and Django Ninja routers should translate framework input/output and delegate policy or workflow to intention-revealing application/domain code.
- Fat Schema/Serializer: schema and serializer code should not become a hidden place for DB reads, state transitions, price calculations, or external calls.
- Template business logic: templates, template tags, includes, and HTMX partials should render decisions already made elsewhere instead of calculating domain policy.
- Service dumping ground: moving all code into `services.py` is not enough. Split by use case, domain behavior, query/read model, or integration responsibility when those change for different reasons.
- Escalate out of this skill when the right owner depends on aggregate boundaries, transaction/locking/idempotency, REST contract shape, or concrete ORM/API implementation.

## Comments And Documentation

- Prefer code that expresses what it does; use comments sparingly to explain why a non-obvious decision exists.
- Public interfaces should document inputs, outputs, side effects, exceptions, and calling constraints when those are not obvious.
- Delete stale comments and commented-out code; version control preserves history.

## Review Output

- For reviews, list findings first, ordered by severity, with file/line evidence.
- Distinguish correctness risk, behavior regression, maintainability risk, missing tests, and style-only notes.
- If no issues are found, say so and mention residual test or verification gaps.
