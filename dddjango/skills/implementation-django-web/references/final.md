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

```python
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.urls import reverse_lazy


# Generic CBV: 보일러플레이트 최소화. queryset은 selector/Manager로 준비
class ArticleListView(ListView):
    queryset = Article.objects.published().select_related("author")
    paginate_by = 20
    context_object_name = "articles"


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    success_url = reverse_lazy("article-list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)  # durable invariant는 여기 몰지 않는다


# Mixin: 한 관심사만 담당, MRO는 왼쪽 -> 오른쪽
class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


# FBV: GET/POST 흐름이 명시적이어야 할 때
@login_required
@require_http_methods(["GET", "POST"])
def article_create(request):
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = create_article(author=request.user, **form.cleaned_data)  # service 호출
            return redirect("article-detail", pk=article.pk)
    else:
        form = ArticleForm()
    return render(request, "articles/create.html", {"form": form})
```

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

```html
{# 좋은 예: extends는 첫 비주석 줄, load는 알파벳순, 태그 안 한 칸 공백, block 이름 명시 #}
{% extends "base.html" %}

{% load i18n l10n static %}

{% block content %}
  <h1>{{ page_title }}</h1>
  {% if user.is_authenticated %}
    <p>{{ user.name }}</p>
  {% endif %}
{% endblock content %}
```

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

```python
from django import forms
from django.core.exceptions import ValidationError


# 검증 순서: Field.clean() -> clean_<field>() -> 교차 필드 clean()
class RegistrationForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("이미 등록된 이메일입니다.")
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("password_confirm"):
            raise ValidationError("비밀번호가 일치하지 않습니다.")
        return cleaned


# ModelForm: fields를 명시적으로 나열한다 ("__all__"/exclude는 의도치 않은 노출 위험)
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "body", "category"]
```

## 7. HTMX fragment와 AJAX

HTMX view는 web adapter다. 서버의 domain behavior는 model/service/usecase boundary에 두고, view는 request method, auth, permission, form/context orchestration, fragment 또는 redirect response를 조합한다. **[HTMX] [DDoc]**

기준:

- HTMX fragment template은 작게 유지하고, 여러 상태에서 의도적으로 재사용될 때만 공통 fragment로 둔다.
- state-changing HTMX/AJAX 요청도 non-HTMX POST와 같은 수준의 auth, permission, CSRF 검증을 적용한다.
- project가 non-JavaScript fallback을 기대하면 progressive enhancement path를 유지한다.
- JSON API처럼 resource contract, status matrix, schema, Problem Details가 필요해지면 `implementation-django-ninja` 또는 `architecture-api`로 넘긴다.
- HTMX-specific header나 response behavior는 view adapter의 UI contract로 취급하고 domain logic과 섞지 않는다.

```python
# 뷰: state-changing HTMX 요청도 일반 POST와 같은 auth/permission/CSRF를 적용한다
@login_required
@require_http_methods(["POST"])
def toggle_like(request, pk):
    article = get_object_or_404(Article, pk=pk)
    like_article(article=article, user=request.user)  # domain behavior는 service로
    return render(request, "articles/_like_button.html", {"article": article})
```

```html
{# 템플릿: CSRF 토큰을 hx-headers로 전달, fragment를 교체 #}
<button hx-post="{% url 'toggle-like' article.pk %}"
        hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'
        hx-swap="outerHTML">
  좋아요 {{ article.like_count }}
</button>
```

## 8. CSRF, XSS, security setting

`CsrfViewMiddleware`는 좁고 문서화된 예외가 없으면 유지한다. POST form에는 `{% csrf_token %}`을 사용한다. State-changing AJAX/HTMX 요청은 프로젝트의 header 또는 form pattern으로 CSRF token을 보낸다. `@csrf_exempt`는 대체 보호가 명확한 작은 경계에서만 사용한다. **[DDoc] [OWASP]**

기준:

- Django template autoescaping을 기본으로 신뢰한다.
- untrusted value를 JavaScript context에 직접 주입하지 않는다. 프로젝트의 escaping pattern을 따른다.
- `CSRF_COOKIE_HTTPONLY`는 AJAX token access를 어렵게 만들 수 있으므로 프로젝트 요구와 Django 문서의 caveat를 함께 고려한다.
- security middleware, session, CSRF, auth, message, frame option middleware ordering을 보존한다.
- security setting을 바꾸면 `python manage.py check --deploy` 실행 또는 미실행 사유를 보고한다.
- raw SQL이 web context 준비에 필요하면 user input을 SQL string에 보간하지 말고 parameterized query를 사용한다. QuerySet/Manager는 `implementation-django`, DB 성능 설계는 `architecture-db`로 넘긴다.

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
| HTMX 변경 | fragment response, method/auth/permission/CSRF, redirect/header behavior | API-like contract가 필요하면 `implementation-django-ninja`/`architecture-api`로 handoff |
| service 예외 처리(§11) | 도메인 예외→폼 재렌더(200), 미식별/영구→`handler500` 500.html, transient→503+`Retry-After`, HTMX→에러 fragment | 시스템 예외를 view가 자체 렌더하거나 사용자 예외를 500으로 보내면 §11 위반 |
| security setting 변경 | `check --deploy` 또는 project-specific security check | 실행하지 않으면 미실행 사유 |
| visible UI 변경 | browser check, screenshot, template/render test 중 가능한 증거 | browser 미실행을 실행한 것처럼 보고하지 않음 |

완료 보고에는 실제 실행한 명령, 테스트 대상, 실패/미실행 항목을 분리해 적는다. Validator나 test가 해당 requirement를 직접 덮는지 확인하지 않고 넓은 완료를 주장하지 않는다.

## 11. 서버렌더 에러 처리

Service/usecase가 던진 예외는 **출처로 분류**해 처리 자리를 가른다 — service가 raise한 도메인/애플리케이션 예외는 view가 잡아 사용자 언어로 변환하고(view-local), 인프라·프레임워크·미식별 예외(`OperationalError`·`IntegrityError`·미식별 `Exception`)는 view가 잡지 않고 전파해 중앙이 처리한다. "사용자가 행동을 바꿔 풀 수 있나"는 1차 분류 기준이 아니라(결제 거절·권한·동시성 충돌에서 흔들린다) 도메인 예외를 잡은 *뒤* 폼 재렌더냐 거부 안내냐를 정하는 2차 신호다. 이 절은 서버렌더 HTML 경로만 소유하며, JSON API 오류 표현과 섞지 않는다. **[DDoc] [dddjango-django]**

기준:

- **사용자 에러(도메인 예외)는 view-local 재렌더**: 비즈니스 규칙 위반(재고 부족·중복 등 service가 raise한 우리 타입)은 그 view에서 narrow `except <DomainError>`로 잡아 폼을 재렌더한다 — 입력 값을 보존하고 `messages.error`로 사유를 싣는다(status 200, POST 성공은 PRG redirect). `except Exception` 같은 광범위 catch는 금지다 — 인프라 예외가 사용자 메시지로 둔갑해 중앙 경로를 우회한다(`discipline-cleancode` 구체적 예외 처리).
- **사용자 에러를 `handler500`로 보내지 않는다**: `django.views.defaults.server_error(request, template_name="500.html")`는 **빈 Context**로 렌더하므로(시그니처가 `request`만 받는다) 도메인 메시지·폼 입력·필드 오류를 실을 수 없다. 사용자 에러를 `raise`해 500으로 보내면 "재고가 부족합니다" 같은 사유가 사용자에게 영영 안 보인다.
- **시스템 에러(미식별·영구장애)는 중앙 `handler500`**: view가 잡지 않고 전파하면 Django가 500으로 변환해 `handler500`(프로젝트 URLconf에 등록)이 `500.html`을 렌더한다. custom handler view는 **`request` 인자만** 받고 `HttpResponseServerError`를 반환한다 — `handler404`와 달리 `exception` 인자를 받지 않으므로 `def server_error(request, exception)`로 쓰면 호출 시 TypeError로 500 핸들러 자체가 깨진다. `500.html`은 프로젝트에 하나만 둔다(view마다 에러 페이지를 만들지 않는다).
- **transient 인프라 예외는 중앙에서 retryable**: DB 락·deadlock·serialization 같은 *재시도로 해소되는* 경합은 `process_exception(request, exception)` 미들웨어가 retryable(503+`Retry-After`)로 매핑한다 — `handler500`은 500 고정이라 503·헤더를 못 실으므로 미들웨어가 유일한 중앙 자리다. 현재 이 서버렌더 경계가 유일한 소비자이므로, retryable 판정은 Django HTML 미들웨어의 private predicate에 둔다. predicate는 원인 체인을 순환 없이 제한적으로 훑어 승인된 락·deadlock·serialization 신호와 PostgreSQL SQLSTATE만 인식하고, 원본 예외 문자열·SQL·secret을 응답이나 로그 메시지로 되돌려 주지 않는다. 영구장애(disk I/O·`no such table`·malformed)는 `None`을 반환해 `handler500`로 전파한다 — `OperationalError` 클래스 전체를 분기 없이 통째 503으로 올리면 영구장애를 retryable로 오분류해 재시도 루프가 영원히 못 고치는 장애를 두드린다. 미들웨어는 503 응답을 *반환*만 하고 도메인 폼을 `render`하지 않는다(폼 재렌더는 view-local 몫). 같은 분류 지식을 실제로 공유하는 Django 경계가 둘 이상 생긴 경우에만 `common/django/` 승격을 검토하며, 그 전에는 공통 추상화를 만들지 않는다.
- **계산된 transient는 도메인 마커 타입으로**: ACL·앱이 낙관락·CAS 재시도를 스스로 소진 판정한 경우(드라이버 예외 부재)는 인프라 예외를 합성하지 말고 협력 포트가 선언한 도메인 transient-마커(`StockContention` 등 retryable 의미)로 raise하며, 미들웨어가 *타입*으로 retryable 매핑한다(`discipline-houserules` §2).
- **응답 표현은 HTML 경계가 소유한다**: retryable *판정*과 *응답 표현*을 JSON API 경로와 공유하지 않는다. 서버렌더 transient는 이 절이 소유하고 HTML 503으로 내며, JSON 오류 schema·helper·응답 객체를 HTML 경로에 import하지 않는다.
- **HTMX 경로는 fragment로 응답한다**: HTMX 요청(`HX-Request` 헤더)에서 도메인 에러는 전체 `500.html`이 아니라 **에러 fragment를 swap**한다 — 전체 문서를 `hx-target` 자리에 주입하면 UI가 깨진다. view는 `request.headers.get("HX-Request")`로 분기해 에러 fragment(200/422)를 내고, 시스템 에러·503도 HTMX 맥락이면 명세된 에러 표면(`HX-Reswap` 또는 에러 fragment)으로 처리한다.
- **반복되는 처리 형태는 표준화**: 같은 `try → except <DomainError> → render(form, messages.error)`가 view마다 반복되면 단일 패턴(FBV) 또는 CBV `form_invalid()` 오버라이드로 묶는다. 도메인 예외가 많으면 공통 도메인 베이스를 한 except로 잡고 메시지 매핑 테이블을 쓴다(예외 종류마다 except 난립 금지 — ninja §6.2 대칭).

```python
# myproject/errors.py — 시스템 에러 중앙 처리 (프로젝트 urls.py: handler500 = "myproject.errors.server_error")
from django.shortcuts import render


def server_error(request):                       # request만 — handler404와 달리 exception 인자 없음
    return render(request, "500.html", status=500)   # 빈 Context — 도메인 데이터에 의존하지 않는다
```

```python
# myproject/middleware.py — transient만 중앙에서 retryable 503 (영구장애·미식별은 handler500로 전파)
from django.db import OperationalError
from django.shortcuts import render

from application.order.domain_layer.order.exception import StockContention  # 도메인 transient 마커


class TransientErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    @staticmethod
    def _is_retryable_db_error(exc: OperationalError) -> bool:
        # 이 HTML 경계의 private 분류기다. 순환 원인 체인도 안전하게 끝내며,
        # 승인된 경합 신호만 503으로 올린다. 예외 원문은 응답·로그에 노출하지 않는다.
        seen: set[int] = set()
        current: BaseException | None = exc
        for _ in range(8):  # wrapped driver causes are shallow; cap hostile/corrupt chains.
            if current is None or id(current) in seen:
                return False
            seen.add(id(current))
            message = str(current).lower()
            if any(
                signal in message
                for signal in (
                    "database is locked",
                    "database table is locked",
                    "deadlock detected",
                    "could not serialize access",
                )
            ):
                return True
            # PostgreSQL: 40001=serialization_failure, 40P01=deadlock_detected.
            code = getattr(current, "sqlstate", None) or getattr(current, "pgcode", None)
            if code in {"40001", "40P01"}:
                return True
            current = current.__cause__ or current.__context__
        return False

    def process_exception(self, request, exception):
        if isinstance(exception, OperationalError) and not self._is_retryable_db_error(exception):
            return None                          # 영구장애 → 전파해 handler500 (분기 필수)
        if isinstance(exception, (OperationalError, StockContention)):
            resp = render(request, "503.html", status=503)
            resp["Retry-After"] = "1"
            return resp                          # 503 반환만 — 폼 재렌더는 view-local 몫
        return None                              # 도메인·미식별 → view-local 또는 handler500
```

```python
# 뷰: 사용자 에러(도메인)는 view-local 재렌더, 시스템·transient는 안 잡고 전파
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from application.order.application_layer.place_order.command.place_order_command import place_order
from application.order.domain_layer.order.exception import InsufficientStock


@require_http_methods(["GET", "POST"])
def order_create(request):
    form = OrderForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            order = place_order(**form.cleaned_data)     # service bare 호출 — 인프라 예외는 전파
        except InsufficientStock as exc:                 # narrow — 도메인 예외만
            messages.error(request, str(exc))
            if request.headers.get("HX-Request"):
                return render(request, "orders/_form.html", {"form": form}, status=422)
            # full-page: 폼 인스턴스·입력 보존해 재렌더(200, 아래 공통 render)
        else:
            return redirect("order-detail", pk=order.id)  # PRG
    return render(request, "orders/create.html", {"form": form})
```
