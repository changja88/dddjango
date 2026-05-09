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

## Comments And Documentation

- Prefer code that expresses what it does; use comments sparingly to explain why a non-obvious decision exists.
- Public interfaces should document inputs, outputs, side effects, exceptions, and calling constraints when those are not obvious.
- Delete stale comments and commented-out code; version control preserves history.

## Review Output

- For reviews, list findings first, ordered by severity, with file/line evidence.
- Distinguish correctness risk, behavior regression, maintainability risk, missing tests, and style-only notes.
- If no issues are found, say so and mention residual test or verification gaps.
