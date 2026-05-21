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
- If the request is primarily pytest, Django test client, fixture, factory, test double, browser automation, coverage, or detailed test implementation, use `implementation-test`; this skill states web render/form/HTMX/CSRF acceptance criteria when web implementation is also in scope.
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

- Template은 presentation-only로 유지한다. domain rule, state transition, pricing, permission policy, complex query decision을 template에 두지 않는다.
- View는 thin adapter로 유지한다. request handling, auth/permission, form/context orchestration, service/usecase call, response rendering을 조합한다.
- boilerplate를 줄이면 Generic CBV/TemplateView를 선호한다. custom flow가 함수로 더 명확하면 FBV를 사용한다.
- `ModelForm.Meta.fields`는 명시적으로 나열한다. 프로젝트가 명시적으로 허용하지 않으면 `fields = "__all__"`와 `exclude`를 피한다.
- 반복 UI fragment가 같은 의미로 함께 바뀔 때 includes/components로 분리한다.
- HTMX/AJAX endpoint는 web adapter로 다룬다. server-side domain behavior는 model/service boundary 뒤에 두고 CSRF 처리는 명시한다.
- Template/static 작업을 마치기 전 view/context code가 optional field의 `display-ready fallback values`를 제공하는지 확인한다. `None`, blank strings, and missing optional values는 렌더링 전에 project-standard `non-empty placeholders`로 변환한다.
- `Templates must render prepared display values`: Template은 raw domain field가 아니라 준비된 display value를 렌더링한다. Optional field가 보이면 empty value path를 context 또는 render test로 덮는다.
- `Changed static files must be referenced by the rendered page`: page-specific CSS/JS를 만들거나 수정하면 rendered page에서 참조되어야 한다. 참조되지 않는 page-specific asset은 unfinished work로 보고한다. 프로젝트에 render/template test가 있으면 실행한다.
- 실제 실행한 검증만 보고한다. render test, browser check, `collectstatic`, `check --deploy`, template test를 실행하지 않았으면 미실행으로 적는다.
