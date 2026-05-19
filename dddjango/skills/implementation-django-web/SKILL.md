---
name: implementation-django-web
description: >
  Provisional until dedicated source reference exists; use with fallback source for Django web/template/static implementation: TemplateView, templates, base template, component includes, static files, CSS/JS, HTMX, CSRF for AJAX, web forms, view auth/permissions, and web render acceptance checks. Use for Django 페이지, 템플릿/정적 파일, 화면 폼, 렌더링 확인, TemplateView 주문 상세, HTMX/CSRF. Do not use for REST API/Router/Schema or ORM/마이그레이션/트랜잭션 중심 작업; prefer implementation-django-ninja or architecture-api for APIs, implementation-django or architecture-db for ORM/DB work, implementation-test for pytest/browser mechanics, and workflow-dddjango-subagents for 복합/위험 작업 or subagent work.
---

# Django Web Implementation

This skill is provisional. Dedicated Django Web source reference does not exist yet; use the fallback source named below and verify exact frontend/static tooling against the project’s installed packages and existing layout.

## Fallback Source

- Treat the dedicated Django Web reference as absent. The fallback source scope is the dddjango `implementation-django/reference/final.md` sections for URL design, template philosophy/style, view philosophy/style, thin views, CBV/FBV, forms, CSRF/XSS security, raw SQL safety in view/query contexts, view auth/permissions, secure settings, and middleware.
- Use dddjango product decisions for this skill’s first-class ownership of static files, CSS/JS, HTMX, and CSRF-aware AJAX; those areas do not yet have a dedicated source reference. The bundled runtime summaries below are the working references for agents using this skill.

## Routing

- If the request is an undecided REST contract, HTTP status, API auth, content negotiation, pagination, Problem Details, or OpenAPI design task, use `architecture-api`.
- If the request is REST API implementation with Router, Schema, Problem Details API error, or OpenAPI wiring, use `implementation-django-ninja`.
- If DB schema, transaction, locking, rollout constraint, or migration design drives the work, use `architecture-db`; if ORM models, services, selectors, transactions, or migration files are the main implementation work, use `implementation-django`.
- If the request is primarily pytest, Django test client, fixture, factory, test double, browser automation, coverage, or detailed test implementation, use `implementation-test`; this skill states web render/form/HTMX/CSRF acceptance criteria when web implementation is also in scope.
- If domain rules, state transitions, policies, invariants, or bounded context are unclear, use `architecture-ddd` before web implementation.
- If the user explicitly asks for subagents, role decomposition, parallel review, or responsibility splitting, use `workflow-dddjango-subagents` first.
- If the work combines DDD, DB/API, Django implementation, templates/static, and tests in a risky feature, use `workflow-dddjango-subagents` first.
- For a tiny template text change or a short Django template explanation, answer or edit directly without DDD/workflow ceremony.
- Korean trigger boundary: `템플릿`, `정적 파일`, `화면`, `폼`, `렌더링`, `HTMX`, `CSRF` belong here; `REST API/Router/Schema`는 `implementation-django-ninja` 또는 `architecture-api`, `ORM/마이그레이션/트랜잭션`은 `implementation-django` 또는 `architecture-db`, `복합/위험 작업`은 `workflow-dddjango-subagents`로 보낸다.

## Reference Loading

- Load only the reference file(s) relevant to the current web task.
- Read [templates.md](references/templates.md) for template inheritance, base templates, includes, template style, and keeping templates presentation-only.
- Read [static-assets.md](references/static-assets.md) for static file organization, CSS/JS placement, collectstatic/manifest concerns, and asset checks.
- Read [templateview-htmx.md](references/templateview-htmx.md) for TemplateView, FBV/CBV choice, context preparation, forms, HTMX fragments, and thin views.
- Read [csrf-ajax.md](references/csrf-ajax.md) for CSRF, AJAX/HTMX request safety, XSS, secure cookies, middleware, and verification.

## Runtime Rules

- Keep templates presentation-only. Do not put domain rules, state transitions, pricing, permission policy, or complex query decisions in templates.
- Keep views thin: request handling, permission checks, form/context orchestration, service/usecase call, and response rendering.
- Prefer Generic CBV/TemplateView when it removes boilerplate; use FBV when the flow is custom and clearer as a function.
- Use explicit `ModelForm.Meta.fields`; avoid `fields = "__all__"` and `exclude` unless the project explicitly accepts that exposure.
- Keep reusable UI fragments in includes/components when it reduces meaningful duplication.
- Treat HTMX/AJAX endpoints as web adapters; keep server-side domain behavior behind model/service boundaries and keep CSRF handling explicit.
- Before finishing template/static work, check that view/context code provides display-ready fallback values for optional fields, templates render display values instead of raw domain fields, changed static files are referenced by the rendered page or reported as unused, and a render/template test was run when the project has one.
- Report only verification actually run. If render tests, browser checks, `collectstatic`, `check --deploy`, or template tests were not run, say so.
