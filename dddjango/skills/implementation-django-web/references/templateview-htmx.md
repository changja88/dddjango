# TemplateView, Forms, And HTMX

Use this reference for TemplateView, CBV/FBV choice, context preparation, forms, HTMX fragments, and thin web adapters.

## View Choice

- Use `TemplateView` for read-only pages where context preparation is the main task.
- Use Generic CBV such as `ListView`, `DetailView`, `CreateView`, `UpdateView`, or `FormView` when it removes ordinary CRUD/form boilerplate.
- Use FBV for custom flows where a function is clearer than class hooks.
- For FBVs, keep `request` as the first parameter.
- Avoid deep mixin chains. If a CBV needs many mixins or hook overrides, reconsider whether an FBV or service boundary is clearer.
- Remember that CBV mixins resolve left to right through Python MRO; keep each mixin to one concern.

## URLs

- Keep URL patterns loosely coupled from Python function or class names.
- Avoid file extensions in page URLs unless the project has an explicit compatibility reason.

## Context And Query Shape

- Build context explicitly and keep template variable names aligned with page language.
- Put reusable read logic in selectors or QuerySet methods when it is shared or performance-sensitive.
- Use `select_related()`/`prefetch_related()` before rendering lists that traverse relationships.
- Do not perform hidden database work from templates by passing underprepared objects into loops.

## Auth And Permissions

- Apply view-level auth and permission checks before rendering protected pages.
- For FBVs, use project-standard decorators such as `login_required` and `permission_required`.
- For CBVs, use project-standard mixins such as `LoginRequiredMixin` and `PermissionRequiredMixin`.
- Keep permission policy out of templates; templates may show or hide UI from prepared context but must not own authorization decisions.

## Forms

- Keep form validation responsible for input shape and presentation errors.
- Respect Django form validation order: field cleaning, field-specific `clean_<fieldname>()`, then form-wide `clean()`.
- Put durable domain invariants in model/service/DB boundaries when they must hold outside the form.
- Reuse custom validators when the same input validation belongs in both forms and model fields.
- Use explicit `ModelForm.Meta.fields`; avoid `fields = "__all__"` and `exclude` because new model fields can become accidentally editable or unintentionally exposed.
- Keep POST handling and redirects clear; use POST/Redirect/GET when it prevents duplicate submissions for ordinary web forms.

## HTMX And Fragments

- Treat HTMX views as web adapters. Keep business behavior in services/models and return fragments or redirects as the UI contract requires.
- Keep fragment templates small and reusable only when the same fragment is intentionally rendered in multiple states.
- Validate request method, auth, and permissions exactly as for non-HTMX views.
- Keep progressive enhancement in mind when the project expects non-JavaScript fallback.
- Coordinate API-like JSON behavior with `implementation-django-ninja` instead of turning HTMX views into ad hoc REST APIs.
