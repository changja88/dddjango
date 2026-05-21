# TemplateView, Forms, And HTMX

이 reference는 TemplateView, CBV/FBV 선택, context preparation, forms, HTMX fragments, thin web adapter를 다룬다.

## View Choice

- Context 준비가 주요 작업인 read-only page에는 `TemplateView`를 사용한다.
- 일반 CRUD/form boilerplate를 줄이면 `ListView`, `DetailView`, `CreateView`, `UpdateView`, `FormView` 같은 Generic CBV를 사용한다.
- Function flow가 class hook보다 명확한 custom flow에는 FBV를 사용한다.
- FBV의 첫 번째 parameter는 `request`로 둔다.
- 깊은 mixin chain을 피한다. CBV가 많은 mixin이나 hook override를 요구하면 FBV 또는 service boundary가 더 명확한지 재검토한다.
- CBV mixin은 Python MRO에 따라 왼쪽에서 오른쪽으로 resolve된다. 각 mixin은 하나의 concern만 담당한다.

## URLs

- URL pattern은 Python function/class name과 느슨하게 결합한다.
- 프로젝트에 compatibility reason이 없으면 page URL에 file extension을 넣지 않는다.

## Context And Query Shape

- Context는 명시적으로 만들고 template variable name은 page language와 맞춘다.
- Optional display field는 view/context builder/view-model helper에서 normalize한다. `None`, blank string, missing optional value를 display-ready placeholder로 변환한 뒤 template은 prepared display value를 렌더링한다.
- Optional field가 화면에 보이면 render 또는 context test에서 empty display state를 확인한다. 프로젝트가 `None`과 blank string을 구분하면 둘 다 확인한다.
- Shared 또는 performance-sensitive read logic은 selector 또는 QuerySet method에 둔다.
- Relationship을 순회하는 list를 렌더링하기 전 `select_related()`/`prefetch_related()`를 검토한다.
- Underprepared object를 loop에 넘겨 template에서 hidden database work가 발생하게 하지 않는다.

## Auth And Permissions

- Protected page는 render 전에 view-level auth와 permission check를 적용한다.
- FBV는 프로젝트 표준 decorator인 `login_required`, `permission_required` 등을 사용한다.
- CBV는 프로젝트 표준 mixin인 `LoginRequiredMixin`, `PermissionRequiredMixin` 등을 사용한다.
- Permission policy를 template에 두지 않는다. Template은 prepared context에 따라 UI를 show/hide할 수 있지만 authorization decision을 소유하지 않는다.
- Unauthorized, forbidden, redirect behavior는 프로젝트 표준과 테스트 기대에 맞춘다.

## Forms

- Form validation은 input shape와 presentation error를 담당한다.
- Django form validation order는 field cleaning, field-specific `clean_<fieldname>()`, form-wide `clean()` 순서다.
- Form 밖에서도 지켜야 하는 durable domain invariant는 model/service/DB boundary에 둔다.
- 같은 input validation이 form과 model field 양쪽에 필요하면 custom validator를 재사용한다.
- `ModelForm.Meta.fields`는 명시적으로 나열한다. `fields = "__all__"`와 `exclude`는 새 model field가 의도치 않게 editable/exposed 될 수 있으므로 피한다.
- 일반 web form은 중복 제출을 줄이면 POST/Redirect/GET을 사용한다.
- Invalid POST는 form error와 입력 값을 사용자가 회복할 수 있게 렌더링한다.

## HTMX And Fragments

- HTMX view는 web adapter로 다룬다. Business behavior는 service/model에 두고 fragment 또는 redirect를 UI contract에 맞게 반환한다.
- Fragment template은 작게 유지한다. 같은 fragment가 여러 상태에서 의도적으로 렌더링될 때만 재사용한다.
- Request method, auth, permission은 non-HTMX view와 같은 수준으로 검증한다.
- 프로젝트가 non-JavaScript fallback을 기대하면 progressive enhancement path를 유지한다.
- API-like JSON behavior는 `implementation-django-ninja`와 조율한다. HTMX view를 ad hoc REST API로 바꾸지 않는다.
