# Transactions, Performance, Security, And Tests

Use this reference for transaction boundaries, consistency, query performance, caching, security settings, raw SQL, middleware, and Django-specific test acceptance criteria.

Source basis: Django official docs, Architecture Patterns with Python, OWASP Django Security Cheat Sheet.

## Transactions And Consistency

- Treat the use case as the transaction boundary. Use `transaction.atomic()` around the smallest block that must commit or roll back together.
- Use `select_for_update()` only when pessimistic locking is needed and the test/database setup can exercise it.
- Prefer unique constraints and idempotency storage for duplicate-write prevention that the database must enforce.
- Schedule external side effects with `transaction.on_commit()` when sending before commit would be incorrect.
- For cross-aggregate consistency, question the aggregate boundary first; then consider domain events, eventual consistency, and outbox patterns.

For risky writes, output a `Risky Write Consistency Block` that records:

- transaction owner
- locking strategy
- uniqueness or idempotency storage
- `Idempotency-Key` API behavior, coordinated with `architecture-api` and `implementation-django-ninja` when the risky write is exposed over HTTP
- external side-effect timing
- isolation and retry assumptions
- integration or concurrency test expectation

## Query Performance

- Look for N+1 queries and fix them with `select_related()`, `prefetch_related()`, or `Prefetch()`.
- Use `assertNumQueries` for query-count regressions when performance is part of the acceptance criteria.
- Use `exists()` for existence checks and `count()` for database counts instead of materializing QuerySets.
- Use `save(update_fields=[...])` for narrow updates where it avoids overwriting unrelated columns and improves write cost.
- Profile before aggressive `only()`, `defer()`, index, or caching changes.
- Use `EXPLAIN ANALYZE` or the project’s DB tooling when changing indexes or complex queries.

## Caching

- Cache only data whose read frequency, computation cost, and staleness tolerance justify it.
- Choose the smallest effective cache level: per-view, template fragment, or low-level cache.
- Include version or timestamp information in cache keys when it makes invalidation safer.
- Avoid local memory cache assumptions in multiprocess production deployments.
- Document invalidation ownership whenever writes and cached reads are both touched.

## Security

- Keep Django’s CSRF, XSS, SQL injection, and clickjacking protections enabled unless there is a narrowly justified exception.
- Use `check --deploy` or project deployment checks when security settings are changed.
- Do not mark strings safe or use `mark_safe()` without a trusted source and escaping decision.
- Use parameterized queries for `raw()` and `extra()`; never interpolate user input into SQL strings.
- In production settings, verify HTTPS redirect, HSTS, secure cookies, proxy SSL header, content type sniffing, and frame options according to the deployment environment.
- Keep authentication and permission checks close to the adapter boundary, but keep core authorization rules reusable when multiple entry points need them.

## Middleware

- Keep middleware lightweight because it runs on every request.
- Preserve Django middleware ordering constraints, especially security, sessions, CSRF, auth, messages, and frame options.
- Give each custom middleware one concern and clear exception behavior.

## Django Test Acceptance

- Use Django `TestCase` for most DB-backed tests and `TransactionTestCase` when commit behavior, locks, or database triggers must be exercised.
- Use `pytest.mark.django_db` when pytest-django tests access the database.
- Use factories or fixtures to express domain state clearly.
- For Django implementation work, state the acceptance tests needed for model behavior, service flows, migrations, constraints, transactions, query counts, or security settings.
- When the current task only implements code and another role owns tests, report the test expectations rather than claiming tests were executed.
