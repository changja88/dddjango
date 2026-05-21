# Coding Style And Existing DRF Maintenance

Use this reference for Django-specific coding style and for maintaining existing DRF code. Do not use it to choose DRF for new APIs; route new REST contracts to `architecture-api` and Django Ninja endpoint work to `implementation-django-ninja`.

Source basis: Django coding style, Django official docs, Django REST Framework docs.

## Django Coding Style

- Follow the project formatter first. When no stricter project rule exists, use Django-style Python formatting with 4-space indentation and Black-compatible line length.
- Keep imports grouped as future, standard library, third-party, Django components, local Django components, then try/except compatibility imports when needed.
- Keep f-strings simple. Move complex expressions, function calls, or translation-sensitive text out of the f-string.
- Order model members predictably: fields, managers, class `Meta`, dunder methods, `save()`/`delete()`, then custom methods unless the project has a stronger convention.
- In templates, use 2-space indentation, quote attribute values, and name closing blocks when nested blocks become hard to scan.
- For views, keep the first argument named `request` and keep request parsing, permission checks, orchestration calls, and response formatting explicit.

## Existing DRF Maintenance

- Treat DRF serializers, viewsets, APIViews, and routers as adapter code around Django-side behavior.
- In existing DRF code, split read/write serializers when field exposure, validation, or query shape differs by action.
- Avoid `fields = "__all__"` in serializers for the same reason it is risky in ModelForms: accidental field exposure.
- Keep durable business rules, state transitions, transaction ownership, external side-effect timing, and DB invariants in model methods, services, selectors, or database constraints.
- When reviewing a DRF viewset action, check whether it delegates to a reusable model/service boundary instead of hiding core behavior in the adapter.
- Do not migrate a working DRF surface to Django Ninja unless the user explicitly asks or a separate migration plan justifies it.
