# implementation-django-web Rubric

## Skill Scope

`implementation-django-web`은 Django template/static/frontend 작업을 구현하거나 평가하는 스킬이다. 평가 대상은 `TemplateView`, function/class-based view context, template inheritance, base template, include/component partial, static CSS/JS, HTMX, CSRF for AJAX, render verification, and web-facing tests.

책임 경계:

- REST API Router/Schema, status code, Problem Details 구현은 `implementation-django-ninja`가 담당한다.
- REST 계약 설계는 `architecture-api`가 담당한다.
- 도메인 규칙, 상태 전이, 가격/권한 정책은 template/view adapter가 아니라 domain/application/Django service boundary에 둔다.
- DB schema/migration/transaction 판단은 `architecture-db`와 `implementation-django`가 담당한다.
- UI가 단순 표시라면 DDD aggregate나 workflow를 새로 만들지 않는다.

## Source Status

provisional

Dedicated Django Web source reference is not yet available. Fallback sources:

- `workspace/docs/spec.md`
- `workspace/docs/skill-contracts.md`
- `workspace/docs/plugin-structure.md`
- `workspace/docs/reference-index.md`
- `workspace/reference/implementation-django/reference/final.md` template/view/static sections

The rubric must explicitly allow this provisional state and must not claim a complete dedicated Django Web reference exists.

## Trigger Examples

- "Django TemplateView 기반 주문 상세 페이지를 추가해줘."
- "base template, include, static CSS 구조를 정리해줘."
- "HTMX partial update와 CSRF for AJAX를 Django template에서 처리해줘."
- "Django template에 도메인 로직이 들어간 부분을 view/service 경계로 빼줘."
- "collectstatic/ManifestStaticFilesStorage/WhiteNoise 영향까지 확인해줘."

## Anti-Trigger Examples

- "주문 생성 API를 Django Ninja로 구현해줘." -> `implementation-django-ninja`
- "REST endpoint status code와 Problem Details 계약을 설계해줘." -> `architecture-api`
- "Order model migration을 작성해줘." -> `implementation-django`
- "주문 정책 aggregate와 invariant를 설계해줘." -> `architecture-ddd`
- "Python dataclass/Enum으로 상태 전이를 고쳐줘." -> `implementation-python`
- "Django Ninja Router가 무엇인지 짧게 설명해줘." -> direct answer; no web skill

## Skill-Specific Hard Gates

- **Business logic in adapter**: template, TemplateView, form handler, or HTMX endpoint owns core business rules or state transitions.
- **Provisional misrepresentation**: presents Django Web source coverage as complete without fallback limitation.
- **API responsibility leak**: REST API Router/Schema/status/error implementation is handled as web/template work.
- **CSRF/AJAX safety missing**: scenario includes AJAX/HTMX state-changing requests and omits CSRF handling.
- **Static/template deployment omission**: scenario explicitly asks production static handling and answer omits collectstatic/storage/WhiteNoise or equivalent deployment notes.
- **Verification honesty**: claims browser render, template test, screenshot, collectstatic, or test execution without evidence.
- **Workflow over-application**: simple template/static edits trigger full DDD role map.

## Analytic Criteria

Use `common_rubric.md` scoring anchors. Core dimensions for this skill:

- **Implementation Pragmatism**: 5 when the solution uses Django template/view/static conventions, keeps context preparation explicit, and avoids unnecessary frontend architecture.
- **Maintainability**: 5 when template inheritance, includes, static assets, and view context are split by change reason and kept understandable.
- **Test And Verification**: 5 when rendered output, template selection/context, CSRF/HTMX behavior, and static assumptions are verified or clearly marked not run.
- **Workflow Fit**: 5 when simple display work stays direct and domain/API concerns are routed only when actually present.
- **Domain Reasoning**: applicable only when domain rules leak into views/templates; 5 requires moving or preserving rules at the correct boundary.
- **Skill Design And Progressive Disclosure**: applicable for skill authoring; 5 requires provisional status and fallback source boundaries.

Score 1 if the output places domain policy in a template, implements an API Router as web work, or claims render/browser verification without evidence.

## Reference-Derived Additions

Required reference coverage:

- Django template philosophy: presentation and presentation-related logic only.
- View context should prepare display data without owning business state transitions.
- Template inheritance and includes should reduce repeated markup without hiding domain decisions in presentation.
- Static files and deployment storage must be considered when the scenario asks for production behavior.
- HTMX/AJAX state-changing flows must include CSRF and server-side validation responsibilities.
- Provisional source limitation must be explicit; fallback source is Django reference template/view/static material.
- DDD overuse is a failure for simple display-only work.

## Required Public Fixtures

Positive prompt:

```text
Django TemplateView 기반 주문 상세 페이지를 추가하고 template/static 구조를 dddjango 기준으로 정리해줘. HTMX로 상태 갱신 버튼도 붙일 수 있는지 검토해줘.
```

Negative prompt:

```text
주문 생성 REST API를 새로 만들어줘. Django template 파일에 처리 로직을 넣어도 괜찮아.
```

Additional public fixtures may include existing templates, views, URL config, static layout, rendered HTML, screenshots, or failing template tests. Public materials must not include expected routing, hidden hard gates, scoring notes, or private expected answer.

## Private Grader Key Notes

Expected routing:

- Positive prompt: `implementation-django-web`; add `implementation-django` only if view/service code or model query changes are required.
- Negative prompt: route REST API work to `architecture-api`/`implementation-django-ninja`; reject template-owned business/API logic.

Expected answer evidence:

- Template/View split is explicit; template renders prepared data and presentation states.
- HTMX/AJAX path discusses CSRF, method, URL, server-side validation, and response partials when applicable.
- Static structure and deployment notes appear when requested.
- Tests or render verification are included or honestly not run.
- Provisional source status is preserved in skill/rubric validation contexts.

Failure criteria:

- Domain state transition or order creation logic is implemented inside template or view adapter.
- REST API implementation is treated as template work.
- CSRF is omitted for scenario-required AJAX/HTMX write.
- Public eval packet leaks expected routing or failure criteria.
- Render/screenshot/test execution is claimed without evidence.

Applicable hard gates: `Business logic in adapter`, `Provisional misrepresentation`, `Verification honesty`, `Workflow over-application`, plus CSRF/static omissions when scenario-required.

## Reference Loading Expectations

- Load `workspace/docs/skill-contracts.md`, `workspace/docs/reference-index.md`, and `workspace/docs/plugin-structure.md` for source status and responsibility boundaries.
- Load `workspace/reference/implementation-django/reference/final.md` only for Django view/template/static guidance.
- Load `workspace/docs/workflow.md` only for composite work; simple display work should not trigger full role decomposition.
- Load API or DB references only when the prompt introduces REST contracts, model/migration, or transaction decisions.
- Do not claim a dedicated `implementation-django-web` source reference exists until it is created.

## Raw Artifact Checklist

- Template files, includes, base template changes, and static CSS/JS paths.
- View/URL/context code and any service boundary used to avoid template business logic.
- HTMX/AJAX request/response snippets and CSRF handling when applicable.
- Rendered HTML, screenshot, template test, or browser verification output when claimed.
- Static deployment notes for collectstatic/storage when scenario requires them.
- Explicit "Not run" section for omitted render/test/browser commands.

## Scenario Tags

Primary tags: `django-web`, `view-adapter`, `simple`, `test`, `review`, `provisional`, `negative-simple`.

Usually N/A unless combined with other work: `api`, `django-ninja`, `db`, `migration`, `risky-write`, `composite-workflow`, `runtime`, `skill-folder`.

## Do Not Penalize

- Not designing aggregates for display-only template work.
- Not adding a frontend build pipeline when static CSS/JS is sufficient.
- Marking REST API or persistence changes as follow-up for the correct skill.
- Using a simple function-based view when it is clearer than a class-based view.
- Stating provisional source limitations instead of inventing dedicated Django Web reference authority.
