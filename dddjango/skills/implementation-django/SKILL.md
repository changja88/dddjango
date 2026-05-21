---
name: implementation-django
description: >
  Use for Django 5.x/LTS implementation: 모델/model, ORM/QuerySet/Manager, 서비스/셀렉터, migration/마이그레이션, transaction/트랜잭션, settings/설정, caching/캐시, security/보안, performance/성능, existing DRF maintenance/review, and Django integration test acceptance criteria. Use for 상태 컬럼 backfill, migration rollout, ORM 최적화, service layer, and legacy DRF serializer/viewset maintenance. Prefer architecture-api for REST contract design, architecture-implementation-patterns for repository/UoW/ports/outbox/service-layer pattern decisions, implementation-django-ninja for Router/Schema endpoints and greenfield DRF Serializer/ViewSet/APIView/DefaultRouter requests, implementation-django-web for TemplateView/templates/static/HTMX/CSRF, implementation-test for pytest/fixture/mock/factory/concurrency/coverage details, workflow-dddjango-subagents for subagent/subagents, 서브에이전트, 역할 분해, 병렬 검토, 책임 분배, or composite/risky Django/DDD work, and architecture-ddd or architecture-db when domain or DB contracts are undecided.
---

# Django Implementation

Use this skill to implement already-scoped Django work. Keep simple CRUD simple; do not force DDD, repository, workflow, or subagent structure onto small model, migration, service, or ORM changes.

## Routing

- If domain rules, state transitions, policies, invariants, or bounded context are unclear, use `architecture-ddd` before implementation.
- If schema, constraint, transaction isolation, locking, or rollout strategy is undecided, use `architecture-db` before writing migrations.
- If repository, Unit of Work, ports/adapters, outbox, ACL, or service-layer pattern choice is the main undecided decision, use `architecture-implementation-patterns` before concrete Django code.
- If the work is REST API contract design, use `architecture-api`; if it is Django Ninja Router/Schema endpoint implementation, use `implementation-django-ninja`.
- If the work is templates, static assets, TemplateView page composition, HTMX, or CSRF-aware frontend behavior, use `implementation-django-web`.
- If the work is pytest fixtures, mocks, factories, API test code, concurrency test mechanics, or coverage strategy, use `implementation-test`; this skill only states Django acceptance criteria unless it is implementing Django-side test hooks.
- If the user asks for subagents, 역할 분해, 병렬 검토, or 책임 분배, or the Django/DDD work is composite or risky across domain, DB, API, implementation, and tests, use `workflow-dddjango-subagents` first.

## Reference Loading

- Load only the reference file(s) relevant to the current Django implementation task.
- Read [models-orm.md](references/models-orm.md) for app layout, settings, model fields, validation, managers, QuerySets, and ORM-adjacent form, view, and signal boundaries.
- Read [services-selectors.md](references/services-selectors.md) for service layer, selector, application service, repository trade-off, and Django/DDD mapping choices.
- Read [migrations.md](references/migrations.md) for migration files, `RunPython`, `apps.get_model()`, `sqlmigrate`, backfill, expand/backfill/contract, and index rollout.
- Read [transactions-performance-security.md](references/transactions-performance-security.md) for `transaction.atomic()`, `on_commit()`, locking, query performance, caching, security, middleware, and Django test acceptance criteria.
- Read [coding-style-drf-maintenance.md](references/coding-style-drf-maintenance.md) for Django-specific coding style or existing DRF maintenance/review. Do not use it to choose DRF for new APIs.

## Runtime Rules

- Put business rules in model methods, domain/application services, or domain services; do not scatter core rules across views, forms, schemas, signals, or templates.
- Use Django model methods and QuerySets directly when the domain is simple. Add services/selectors when one use case spans models, views, transactions, external side effects, or repeated orchestration.
- Use custom QuerySet methods for chainable read predicates and selectors for larger read use cases.
- For risky writes, include a `Risky Write Consistency Block` that summarizes already-decided inputs for the concrete Django implementation: transaction owner, lock/idempotency strategy, DB constraint, `Idempotency-Key` API coordination when relevant, external side-effect timing, isolation/retry decision, and test or verification plan. If any item is undecided, hand it to the owning architecture, API, DB, pattern, or test skill instead of deciding it here.
- Keep migrations small and version controlled. Use historical models in data migrations and split operational rollouts into expand, backfill, and contract steps.
- For staged production migrations, state what can be rolled back safely, what should be forward-fixed after data writes or contract enforcement, and how idempotent/resumable backfills affect recovery.
- Prefer Django and Python conventions already present in the project; do not introduce a repository, UoW, or clean architecture layer unless complexity and testability justify it.
- Do not recommend DRF `Serializer`, `ViewSet`, `APIView`, or `DefaultRouter` as the standard for new APIs.
- When maintaining existing DRF code, treat serializers and viewsets as adapters: keep durable business rules, transaction ownership, side-effect timing, and DB invariants in model, service, selector, or database boundaries.
- Report only verification actually run. If tests, `sqlmigrate`, `check --deploy`, query-count checks, or migration checks were not run, say so.
