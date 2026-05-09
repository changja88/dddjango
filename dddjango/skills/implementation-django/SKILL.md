---
name: implementation-django
description: >
  Use for Django 5.x/LTS implementation: 모델/model, ORM/QuerySet/Manager, 서비스/셀렉터, migration/마이그레이션, transaction/트랜잭션, settings, caching, security, performance, and Django integration test acceptance criteria. Use for 상태 컬럼 backfill, migration rollout, ORM 최적화, service layer. Prefer architecture-api for REST contract design, implementation-django-ninja for Router/Schema endpoints, implementation-django-web for templates/static, implementation-test for pytest/fixture/test code details, workflow-dddjango-subagents for composite or risky Django/DDD work, and architecture-ddd or architecture-db when domain or DB contracts are undecided.
---

# Django Implementation

Use this skill to implement already-scoped Django work. Keep simple CRUD simple; do not force DDD, repository, workflow, or subagent structure onto small model, migration, service, or ORM changes.

## Routing

- If domain rules, state transitions, policies, invariants, or bounded context are unclear, use `architecture-ddd` before implementation.
- If schema, constraint, transaction isolation, locking, or rollout strategy is undecided, use `architecture-db` before writing migrations.
- If the work is REST API contract design, use `architecture-api`; if it is Django Ninja Router/Schema endpoint implementation, use `implementation-django-ninja`.
- If the work is templates, static assets, TemplateView page composition, HTMX, or CSRF-aware frontend behavior, use `implementation-django-web`.
- If the work is pytest fixtures, mocks, factories, API test code, concurrency test mechanics, or coverage strategy, use `implementation-test`; this skill only states Django acceptance criteria unless it is implementing Django-side test hooks.
- If the user asks for subagents, 역할 분해, 병렬 검토, or 책임 분배, or the Django/DDD work is composite or risky across domain, DB, API, implementation, and tests, use `workflow-dddjango-subagents` first.

## Reference Loading

- Read [models-orm.md](references/models-orm.md) for app layout, settings, model fields, validation, managers, QuerySets, forms, views, and signal boundaries.
- Read [services-selectors.md](references/services-selectors.md) for service layer, selector, application service, repository trade-off, and Django/DDD mapping choices.
- Read [migrations.md](references/migrations.md) for migration files, `RunPython`, `apps.get_model()`, `sqlmigrate`, backfill, expand/backfill/contract, and index rollout.
- Read [transactions-performance-security.md](references/transactions-performance-security.md) for `transaction.atomic()`, `on_commit()`, locking, query performance, caching, security, middleware, and Django test acceptance criteria.

## Runtime Rules

- Put business rules in model methods, domain/application services, or domain services; do not scatter core rules across views, forms, schemas, signals, or templates.
- Use Django model methods and QuerySets directly when the domain is simple. Add services/selectors when one use case spans models, views, transactions, external side effects, or repeated orchestration.
- Use custom QuerySet methods for chainable read predicates and selectors for larger read use cases.
- For risky writes, include a `Risky Write Consistency Block` with transaction owner, lock/idempotency strategy, DB constraint, `Idempotency-Key` API coordination when relevant, external side-effect timing, isolation/retry decision, and test or verification plan.
- Keep migrations small and version controlled. Use historical models in data migrations and split operational rollouts into expand, backfill, and contract steps.
- Prefer Django and Python conventions already present in the project; do not introduce a repository, UoW, or clean architecture layer unless complexity and testability justify it.
- Do not recommend DRF `Serializer`, `ViewSet`, `APIView`, or `DefaultRouter` as the standard for new APIs.
- Report only verification actually run. If tests, `sqlmigrate`, `check --deploy`, query-count checks, or migration checks were not run, say so.
