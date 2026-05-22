---
name: implementation-django-web
description: >
  Use for Django server-rendered web implementation: TemplateView, Generic CBV/FBV, ListView/DetailView/CreateView/UpdateView/FormView, templates, base template, component includes, static files, CSS/JS, HTMX, CSRF for AJAX, web forms, view auth/permissions, and web render acceptance checks. Use for Django 페이지, 템플릿/정적 파일, 화면 폼, 렌더링 확인, TemplateView/CBV/FBV 주문 상세, HTMX/CSRF. Do not use for REST API/Router/Schema or ORM/마이그레이션/트랜잭션 중심 작업; prefer implementation-django-ninja or architecture-api for APIs, implementation-django or architecture-db for ORM/DB work, implementation-test for pytest/browser mechanics, and workflow-dddjango-subagents for 복합/위험 작업 or subagent work.
---

# Django Web 구현

이 skill은 Django 서버 렌더링 화면 구현을 담당한다. TemplateView, Generic CBV/FBV 선택, templates, base template, includes/components, static files, CSS/JS, web forms, HTMX fragment, CSRF-aware AJAX, view auth/permission, render acceptance checks를 다룬다. 정확한 frontend/static pipeline은 항상 대상 프로젝트의 설치 패키지와 기존 layout을 먼저 따른다.

## 라우팅

- If the request is an undecided REST contract, HTTP status, API auth, content negotiation, pagination, Problem Details, or OpenAPI design task, use `architecture-api`.
- If the request is REST API implementation with Router, Schema, Problem Details API error, or OpenAPI wiring, use `implementation-django-ninja`.
- If DB schema, transaction, locking, rollout constraint, or migration design drives the work, use `architecture-db`; if ORM models, services, selectors, transactions, or migration files are the main implementation work, use `implementation-django`.
- If the request is primarily pytest, Django test client, fixture, factory, test double, browser automation mechanics, coverage, or detailed test implementation, use `implementation-test`. This skill owns web implementation acceptance criteria and states when render/browser evidence is needed for templates, forms, HTMX, CSRF, and static assets.
- If domain rules, state transitions, policies, invariants, or bounded context are unclear, use `architecture-ddd` before web implementation.
- If the user explicitly asks for subagents, role decomposition, parallel review, or responsibility splitting, use `workflow-dddjango-subagents` first.
- If the work combines DDD, DB/API, Django implementation, templates/static, and tests in a risky feature, use `workflow-dddjango-subagents` first.
- For a tiny template text change or a short Django template explanation, answer or edit directly without DDD/workflow ceremony.
- Korean trigger boundary: `템플릿`, `정적 파일`, `화면`, `폼`, `렌더링`, `HTMX`, `CSRF` belong here; `REST API/Router/Schema`는 `implementation-django-ninja` 또는 `architecture-api`, `ORM/마이그레이션/트랜잭션`은 `implementation-django` 또는 `architecture-db`, `복합/위험 작업`은 `workflow-dddjango-subagents`로 보낸다.

## Reference Loading

현재 작업에 필요한 bundled reference만 읽는다.

- [templates.md](references/templates.md): template inheritance, base template, includes/components, template style, presentation-only template
- [static-assets.md](references/static-assets.md): static file organization, CSS/JS placement, collectstatic/manifest concerns, asset checks
- [templateview-htmx.md](references/templateview-htmx.md): TemplateView, Generic CBV/FBV choice, context preparation, forms, HTMX fragments, thin views, auth/permissions
- [csrf-ajax.md](references/csrf-ajax.md): CSRF, AJAX/HTMX request safety, XSS, secure cookies, middleware, verification

## Runtime Rules

- Template은 presentation-only로 유지하고, View는 request/auth/form/context/service call/response rendering을 조합하는 thin web adapter로 유지한다. 세부 template 기준은 [templates.md](references/templates.md)를 따른다.
- TemplateView/Generic CBV/FBV, web form, context preparation, HTMX fragment 선택은 프로젝트 관례와 흐름의 명확성을 기준으로 한다. 세부 기준은 [templateview-htmx.md](references/templateview-htmx.md)를 따른다.
- Static asset은 프로젝트 pipeline과 rendered page 연결을 함께 확인한다. 세부 기준은 [static-assets.md](references/static-assets.md)를 따른다.
- CSRF/AJAX/HTMX 안전성, XSS, security setting, middleware 관련 변경은 [csrf-ajax.md](references/csrf-ajax.md)를 따른다.
- Render/static acceptance는 bundled reference 기준에 따라 확인한다. Optional display value는 `None`, blank string, missing optional value를 template 전에 표시용 값으로 준비하고, template은 준비된 표시 값을 렌더링하며, 변경한 page-specific static file은 rendered page에서 참조되는지 확인한다.
- Web 구현 완료 시 render/form/HTMX/static/security acceptance evidence가 필요한지 판단하고, detailed pytest fixture, browser automation harness, coverage, test double mechanics는 `implementation-test`로 넘긴다.
- 실제 실행한 검증만 보고한다. render test, browser check, `collectstatic`, `check --deploy`, template test를 실행하지 않았으면 미실행으로 적는다.
