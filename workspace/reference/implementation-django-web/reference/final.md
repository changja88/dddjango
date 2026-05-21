# Django Web 구현 가이드

> Django template, TemplateView/Generic CBV, web form, static asset, HTMX fragment, CSRF-aware AJAX, render acceptance check를 위한 전용 source reference다.
> Django 모델, ORM, 마이그레이션, 트랜잭션, 서비스/셀렉터 일반 구현은 `workspace/reference/implementation-django/reference/final.md`가 소유한다.
> REST API 계약과 Django Ninja 구현은 각각 `workspace/reference/architecture-api/reference/final.md`, `workspace/reference/implementation-django-ninja/reference/final.md` 기준을 따른다.
>
> **출처 약어:**
> - **[DDoc]** Django 공식 문서 (https://docs.djangoproject.com/)
> - **[DDP]** Django Design Philosophies (https://docs.djangoproject.com/en/5.2/misc/design-philosophies/)
> - **[DCS]** Django Coding Style (https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/)
> - **[TSD]** Two Scoops of Django 3.x
> - **[HS]** HackSoft Django Styleguide
> - **[OWASP]** Django Security Cheat Sheet (https://cheatsheetseries.owasp.org/cheatsheets/Django_Security_Cheat_Sheet.html)
> - **[HTMX]** htmx 공식 문서 (https://htmx.org/docs/)
> - **[dddjango-django]** `workspace/reference/implementation-django/reference/final.md`

---

## 1. 책임 범위와 handoff

`implementation-django-web`은 서버 렌더링 웹 화면 구현을 담당한다. 포함 범위는 TemplateView, Generic CBV/FBV 선택, templates, base template, includes/components, static files, CSS/JS, web forms, HTMX fragment, AJAX/HTMX CSRF, view auth/permission, render acceptance checks다.

다음 경우에는 다른 reference 또는 skill로 넘긴다.

| 상황 | 넘길 곳 | 기준 |
|---|---|---|
| REST resource, HTTP status, Problem Details, OpenAPI 계약 | architecture-api | 화면 fragment가 아니라 API 계약이 중심일 때 |
| Django Ninja Router/Schema/API 구현 | implementation-django-ninja | JSON API endpoint 구현이 중심일 때 |
| 모델, QuerySet, Manager, migration, transaction | implementation-django | 데이터 구조와 ORM 동작이 중심일 때 |
| DB locking, isolation, index, rollout/backfill | architecture-db | 저장소 일관성이나 운영 DB 리스크가 중심일 때 |
| pytest fixture, test double, detailed test mechanics | implementation-test | 테스트 도구 구현 자체가 중심일 때 |
| 도메인 상태 전이, 정책, 불변식 | architecture-ddd | 화면 전에 도메인 규칙 결정이 필요할 때 |

웹 view와 template은 domain behavior를 소유하지 않는다. view는 request handling, auth/permission, form/context orchestration, service/usecase 호출, response rendering을 조합한다. template은 presentation과 presentation-related branching만 담당한다. **[DDP] [dddjango-django]**

## 2. TemplateView, Generic CBV, FBV 선택

TemplateView는 읽기 전용 페이지에서 context 준비가 주요 작업일 때 적합하다. ListView, DetailView, CreateView, UpdateView, FormView 같은 Generic CBV는 일반 CRUD나 form flow의 보일러플레이트를 줄일 때 사용한다. 복잡한 custom flow는 FBV가 더 명시적이면 FBV를 선택한다. **[DDoc] [TSD] [dddjango-django]**

선택 기준:

| 상황 | 권장 | 주의 |
|---|---|---|
| static/about/dashboard 같은 read-only page | TemplateView | context_data에서 표시 값을 준비한다. |
| 목록/상세 조회 | ListView/DetailView | relationship traversal은 view/query layer에서 `select_related()`/`prefetch_related()`를 검토한다. |
| 생성/수정 form | FormView/CreateView/UpdateView | `form_valid()`에 durable domain invariant를 몰아넣지 않는다. |
| method별 custom branch가 많은 flow | FBV | `request`를 첫 번째 인자로 두고 GET/POST 흐름을 분명히 한다. |
| mixin이 깊어지는 CBV | 재검토 | mixin은 한 관심사만 담당하고 MRO 복잡도가 커지면 FBV나 service boundary를 고려한다. |

view는 thin adapter로 유지한다. 반복되는 read logic이나 성능에 민감한 query shape은 selector, QuerySet, Manager로 옮긴다. 쓰기 유스케이스나 여러 모델에 걸친 동작은 service/usecase boundary로 옮긴다. **[HS] [dddjango-django]**

## 3. Context 준비와 표시 값

Template에 raw domain object를 그대로 넘겨 template이 fallback, 권한, query shape, domain rule을 결정하게 만들지 않는다. view, context builder, selector, view-model helper에서 화면 언어에 맞는 이름과 표시 값을 준비한다.

필수 기준:

- Optional field를 화면에 표시하면 `None`, blank string, missing value를 project-standard placeholder로 변환한 값을 context에 넣는다.
- template은 준비된 display value를 렌더링하고, domain field의 raw fallback을 직접 결정하지 않는다.
- optional display path는 render 또는 context test로 확인한다. 프로젝트가 `None`과 blank string을 구분하면 둘 다 확인한다.
- 목록 화면에서 relationship을 순회하면 view/query layer에서 N+1 query 위험을 먼저 검토한다.
- template variable 이름은 화면 언어와 맞춘다. 내부 모델 필드 이름을 그대로 노출할 필요는 없다.

## 4. Templates, base template, includes/components

Template은 presentation과 presentation-related branching을 맡는다. 가격 계산, 상태 전이, permission policy, 복잡한 data selection, hidden database work는 template에 두지 않는다. **[DDP] [DCS]**

Base template 기준:

- 프로젝트가 template inheritance를 사용하면 공통 document structure, navigation, global asset, 공통 block을 base template에 둔다.
- `{% extends %}`는 첫 번째 비주석 줄에 둔다.
- block은 역할이 드러나게 이름을 붙이고 `{% endblock content %}`처럼 block 이름으로 닫는다.
- page-specific CSS/JS는 프로젝트의 static convention에 맞는 block에서 opt in한다.

Includes/components 기준:

- 같은 의미의 UI fragment가 반복되고 함께 바뀔 때 include/component로 분리한다.
- include context는 필요한 변수만 명시적으로 전달한다.
- 짧은 snippet을 모두 include로 만들지 않는다. 재사용이 이해와 일관성을 실제로 높일 때만 분리한다.

Template style 기준:

- `{{ variable }}`, `{% tag %}` 안에는 한 칸 공백을 둔다.
- 여러 template library를 load하면 알파벳순으로 유지한다.
- HTML template indentation은 프로젝트 관례를 따르며, Django source style은 2칸 들여쓰기를 사용한다.
- `{% load static %}`과 `{% static 'path/to/file.css' %}`를 사용한다.
- `|safe`, `mark_safe()`는 trusted/sanitized content에 한해 의도와 근거가 있을 때만 사용한다.

## 5. Static files, CSS, JavaScript

Static asset은 프로젝트의 기존 pipeline을 따른다. app-specific asset은 프로젝트가 `app/static/app_name/...` 구조를 쓰는 경우 앱 가까이에 둔다. shared design-system 또는 global asset은 기존 shared static 위치를 따른다. **[DDoc] [dddjango-django]**

기준:

- hardcoded static URL 대신 `{% static %}`를 사용한다.
- page-specific CSS/JS를 만들거나 수정하면 같은 변경에서 rendered template에 연결한다.
- rendered page가 참조하지 않는 page-specific asset은 unfinished work로 본다.
- inline script는 작고 template-local일 때만 허용한다. domain data transformation을 template JavaScript에 넣지 않는다.
- `STATIC_URL`, `STATIC_ROOT`, `STATICFILES_DIRS`, storage backend, WhiteNoise, bundler, manifest/static hashing 등은 프로젝트 기존 설정을 따른다.
- deployment asset resolution을 바꾸거나 manifest/static hashing과 관련된 변경이면 `collectstatic` 실행 또는 미실행 사유를 보고한다.

## 6. Web forms와 POST flow

Form은 input shape, presentation error, user-facing validation message를 담당한다. durable domain invariant는 model/service/DB boundary에서도 보장되어야 한다. **[DDoc] [TSD] [dddjango-django]**

기준:

- Django form validation order는 field cleaning, `clean_<fieldname>()`, form-wide `clean()` 순서다.
- `ModelForm.Meta.fields`는 명시적으로 나열한다.
- `fields = "__all__"`와 `exclude`는 새 model field가 의도치 않게 editable/exposed 될 수 있으므로 프로젝트가 명시적으로 받아들이는 경우가 아니면 피한다.
- 같은 input validation이 form과 model field에 함께 필요하면 custom validator 재사용을 검토한다.
- 일반 web form은 중복 제출을 줄이기 위해 POST/Redirect/GET을 기본 선택지로 둔다.
- invalid POST는 form error와 입력 값을 사용자가 회복할 수 있게 렌더링한다.

## 7. HTMX fragment와 AJAX

HTMX view는 web adapter다. 서버의 domain behavior는 model/service/usecase boundary에 두고, view는 request method, auth, permission, form/context orchestration, fragment 또는 redirect response를 조합한다. **[HTMX] [DDoc]**

기준:

- HTMX fragment template은 작게 유지하고, 여러 상태에서 의도적으로 재사용될 때만 공통 fragment로 둔다.
- state-changing HTMX/AJAX 요청도 non-HTMX POST와 같은 수준의 auth, permission, CSRF 검증을 적용한다.
- project가 non-JavaScript fallback을 기대하면 progressive enhancement path를 유지한다.
- JSON API처럼 resource contract, status matrix, schema, Problem Details가 필요해지면 `implementation-django-ninja` 또는 `architecture-api`로 넘긴다.
- HTMX-specific header나 response behavior는 view adapter의 UI contract로 취급하고 domain logic과 섞지 않는다.

## 8. CSRF, XSS, security setting

`CsrfViewMiddleware`는 좁고 문서화된 예외가 없으면 유지한다. POST form에는 `{% csrf_token %}`을 사용한다. State-changing AJAX/HTMX 요청은 프로젝트의 header 또는 form pattern으로 CSRF token을 보낸다. `@csrf_exempt`는 대체 보호가 명확한 작은 경계에서만 사용한다. **[DDoc] [OWASP]**

기준:

- Django template autoescaping을 기본으로 신뢰한다.
- untrusted value를 JavaScript context에 직접 주입하지 않는다. 프로젝트의 escaping pattern을 따른다.
- `CSRF_COOKIE_HTTPONLY`는 AJAX token access를 어렵게 만들 수 있으므로 프로젝트 요구와 Django 문서의 caveat를 함께 고려한다.
- security middleware, session, CSRF, auth, message, frame option middleware ordering을 보존한다.
- security setting을 바꾸면 `python manage.py check --deploy` 실행 또는 미실행 사유를 보고한다.
- raw SQL이 web context 준비에 필요하면 user input을 SQL string에 보간하지 말고 parameterized query를 사용한다. QuerySet/Manager나 DB 성능 설계는 owning skill로 넘긴다.

## 9. View auth와 permission

Protected page는 render 전에 view-level auth와 permission을 확인한다. Template은 prepared context에 따라 버튼이나 링크를 숨길 수 있지만 authorization decision을 소유하지 않는다. **[DDoc] [dddjango-django]**

기준:

- FBV는 프로젝트 표준 `login_required`, `permission_required`, method decorator를 사용한다.
- CBV는 `LoginRequiredMixin`, `PermissionRequiredMixin` 또는 프로젝트 표준 mixin을 사용한다.
- permission policy가 domain rule과 결합되어 있으면 architecture-ddd 또는 application service boundary에서 먼저 결정한다.
- unauthorized, forbidden, redirect behavior는 프로젝트 표준과 테스트 기대에 맞춘다.

## 10. Render acceptance checks

Web 구현을 마칠 때는 실행한 검증만 보고한다. render/browser/collectstatic/security check를 실행하지 않았다면 미실행으로 명시한다.

권장 검증 행렬:

| 변경 유형 | 기대 증거 | gap 보고 기준 |
|---|---|---|
| template/context 변경 | render test, Django test client response, context assertion | 테스트가 없으면 수동 render 확인 여부와 미실행 사유 |
| optional display value | `None`, blank string, missing optional path의 context/render assertion | raw field fallback을 template에 둔 경우 unfinished |
| static CSS/JS 변경 | rendered HTML의 static reference, referenced path existence | changed asset이 rendered page에서 참조되지 않으면 unfinished |
| form 변경 | GET, valid POST, invalid POST, redirect, form error assertion | CSRF/auth/permission path 미확인 시 residual risk |
| HTMX 변경 | fragment response, method/auth/permission/CSRF, redirect/header behavior | API-like contract가 필요하면 owning skill로 handoff |
| security setting 변경 | `check --deploy` 또는 project-specific security check | 실행하지 않으면 미실행 사유 |
| visible UI 변경 | browser check, screenshot, template/render test 중 가능한 증거 | browser 미실행을 실행한 것처럼 보고하지 않음 |

완료 보고에는 실제 실행한 명령, 테스트 대상, 실패/미실행 항목을 분리해 적는다. Validator나 test가 해당 requirement를 직접 덮는지 확인하지 않고 넓은 완료를 주장하지 않는다.
