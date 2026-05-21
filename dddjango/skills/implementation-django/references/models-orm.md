# Models And ORM

Use this reference for Django app layout, settings access, models, fields, validation, QuerySets, managers, and ORM-adjacent form, view, and signal boundaries. For API Router/Schema work use `implementation-django-ninja`; for server-rendered page composition, templates/static/frontend work, HTMX, and web form implementation use `implementation-django-web`.

Source basis: Django official docs/design philosophies, Two Scoops of Django, Django for Professionals.

## Project And Settings

- Prefer a conventional split such as `config/settings/base.py`, `local.py`, `production.py`, and `test.py` when a project already follows or needs that layout.
- Keep apps aligned to cohesive domain concepts such as `orders`, `payments`, or `users`. Reconsider an app that cannot be described in one sentence or creates circular dependencies.
- Do not hardcode secrets in settings. Read secrets and environment-specific values from environment variables through the project’s existing configuration tool.
- Avoid settings access at module import time when the value can be resolved lazily inside a function or method.

## Model Design

- Keep model information needed to understand an object close to the model: fields, metadata, managers, string representation, URLs, and domain methods.
- Use model methods for simple behavior that naturally belongs to one model. Move orchestration to services when behavior spans models, external systems, or transactions.
- Use `TextChoices` or `IntegerChoices` for finite states instead of multiple booleans that permit impossible combinations.
- Use `DecimalField` for money and avoid `FloatField` for monetary values.
- Use `JSONField` only for genuinely schemaless data; prefer relational fields for structured domain data.
- Prefer abstract base classes for shared fields. Use multi-table inheritance only with a clear reason for the extra joins. Use proxy models for alternate Python behavior over the same table.

## Django 5.x Notes

- Use `db_default` when a default must be computed by the database rather than Python, including paths such as bulk inserts where the SQL `DEFAULT` matters.
- Use `GeneratedField` only when the derived value belongs in the database model and the project accepts stored vs virtual generated-column trade-offs.
- Treat Django 5.2 composite primary keys as constrained: existing models cannot be migrated to composite PKs directly, foreign keys to composite-PK models are limited, and admin support is not available.
- Prefer Django 5.2 LTS behavior for new baseline guidance unless the project pins another supported Django version.

## Validation And Constraints

- Use `clean()` for Python-level cross-field validation where it fits the existing project style.
- Add DB constraints for invariants the database must protect, such as `CheckConstraint`, `UniqueConstraint`, and explicit indexes.
- Remember `save()` does not automatically call `full_clean()`. Ensure forms, services, or explicit code paths invoke validation when needed.
- Keep form validation responsible for user input shape and presentation errors; keep domain invariants in model/service/DB boundaries when they must hold outside the form.

## QuerySet And Manager

- Put chainable read predicates on custom QuerySet methods, then expose them through `as_manager()` or a thin manager.
- Use `select_related()` for `ForeignKey` and `OneToOneField`.
- Use `prefetch_related()` for `ManyToManyField` and reverse foreign keys.
- Use `Prefetch()` when the prefetched relation needs its own filtered or ordered QuerySet.
- Use `only()` and `defer()` only when profiling shows large field or conversion cost; they can add hidden lazy queries.
- Use `values()` and `values_list()` for projection queries that do not need model instances.
- Treat `annotate()` and `filter()` order as meaningful. Use `alias()` when a calculated expression is needed only for filtering or ordering.
- Use `bulk_create()`, `bulk_update()`, and QuerySet `update()` for large batch operations when model `save()` hooks and per-instance validation are not required.

## Views, Forms, And Signals

- Keep views thin: request parsing, permission checks, orchestration call, response/redirect.
- Use FBV when the view is simple. Use CBV or mixins only when they reduce real duplication or match existing project style.
- Use signals for third-party model hooks, avoiding circular dependencies, or applying one handler across many models.
- Do not use signals as hidden control flow inside the same app when an explicit service call or model method is clearer.
- Avoid putting durable business rules in views, forms, signals, templates, or API schemas.
