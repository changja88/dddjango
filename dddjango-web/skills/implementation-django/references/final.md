# Django 표기법 — urls·api_client·템플릿·정적 자산·CSS

> **출처:** docs.djangoproject.com(URL dispatcher·`reverse`·`redirect`·미들웨어·테스트 `Client`·템플릿 언어·CSRF·staticfiles) · htmx.org(응답 헤더 `HX-Redirect`) · HTML Living Standard(내비게이션·스크롤 복원) · MDN(`@font-face`·custom properties) — dddart implementation-flutter(2026-06-12 확인 · 제1 규약 §9-11·§10-5 ④ · dddart 결정 2026-06-12: ④ 2단 동작)의 web 이식.
> 본문 속 `(규약 §N)`은 **출처 표기**이며 로드 대상이 아니다. 로드 가능한 위임은 "스킬명 + §번호(또는 주제)"뿐.

---

## 목차

- §1. 버전·전제
- §2. urls 표기 — path·Routes·navigator·문서 셸·게이트·전환
- §3. 탭 재탭 2단 동작 — 규약 §10-5 ④ 확정 (root_view 소유)
- §4. api_client·DataSource 표기 — 실패 종류·세션 이월
- §5. 로컬 저장 — hive_ce 자리
- §6. 템플릿·요청 수명·CSRF — 표지·VM 수명·대화 표시·템플릿 표기
- §7. 테스트 표기 → discipline-test·implementation-test로 이전
- §8. 정적 이미지 에셋 — `{% static %}`·web/static/images
- §9. 레이아웃 형상 — 시안 충실 재현
- §10. CSS 표기 — foundation 변수·theme·부품/조각 CSS
- §11. 공식 SDK 사본 — static/vendor

---

## §1. 버전·전제

Django는 호스트 lock 판(4.2 LTS 이상 — 테스트 클라이언트 `headers=` 인자가 4.2부터) · htmx 2.0.10 고정 판(implementation-htmx §1) · pytest·pytest-django(implementation-test §1). 기존 프로젝트의 lock 버전이 우선이고, 이 문서의 표기는 위 라인에서 동작한다. 호스트 연결 설정(`INSTALLED_APPS`·`TEMPLATES`·`STATICFILES_DIRS`·루트 urls include·`MIDDLEWARE`·`ALLOWED_HOSTS`)은 Coordinator G0 점검 소관이다 — 이 스킬은 그 연결 위에서 쓰는 코드의 표기다. 백엔드 코드(`application/`·`framework/`·settings·urls 연결 밖)는 고치지 않는다(§4).

## §2. urls 표기 — path·Routes·navigator·문서 셸·게이트·전환

**path·Routes** — 라우팅 짝의 역할·리터럴 단일 출처 규율은 architecture-ui §6 소유, 여기는 표기:

```python
# application/channel/channel_router.py — URL path·name 리터럴은 이 파일 안에서만
from django.urls import URLPattern, path

from web.application.channel.presentation_layer.view.channel_detail_view import channel_detail_view
from web.application.channel.presentation_layer.view.channel_summary_view import (
    channel_summary_embed_fragment,
    channel_summary_leave_fragment,
    channel_summary_list_fragment,
    channel_summary_view,
)

app_name: str = "channel"  # URL 네임스페이스 = BC명


class ChannelRoutes:
    """channel BC의 URL name — reverse·redirect가 참조하는 유일한 상수."""

    SUMMARY: str = "channel:summary"
    SUMMARY_LIST: str = "channel:summary_list"
    SUMMARY_LEAVE: str = "channel:summary_leave"
    SUMMARY_EMBED: str = "channel:summary_embed"
    DETAIL: str = "channel:detail"


urlpatterns: list[URLPattern] = [
    path("channels/", channel_summary_view, name="summary"),
    path("channels/list/", channel_summary_list_fragment, name="summary_list"),  # 조각 응답 라우트(조회 재렌더·재시도)
    path("channels/embed/", channel_summary_embed_fragment, name="summary_embed"),  # 임베드 첫 렌더(셸 없음)
    path("channels/<str:channel_id>/", channel_detail_view, name="detail"),  # <변환기:이름> = 경로 인자
    path("channels/<str:channel_id>/leave/", channel_summary_leave_fragment, name="summary_leave"),  # 액션 조각
]
```

- 경로 인자는 변환기(`<str:…>`·`<int:…>`·`<slug:…>`)로 받고 view 함수의 키워드 인자로 들어온다. 쿼리는 view가 `request.GET`에서 읽는다(입력 읽기는 view 소유 — architecture-state §2). 라우트당 view 함수 하나 — 페이지는 `<화면>_view`, 조각은 `<화면>_<조각>_fragment`(discipline-houserules §4). 고정 경로(`channels/list/`)는 같은 자리의 변환기 경로(`channels/<str:channel_id>/`)보다 **앞에** 둔다 — Django는 위에서부터 처음 맞는 path를 쓴다.
- **임베드 라우트**: 다른 화면(같은 BC든 타 BC든)이 이 화면을 임베드할 수 있으면 셸 없는 첫 렌더 함수 `<화면>_embed_fragment`와 그 라우트를 둔다 — 이 화면의 VM `build()`로 자기 본문 section을 렌더한다(부모는 자식 VM을 부르지 않는다 · 자리 표기는 implementation-htmx §7). 주소는 navigator의 `<화면>_embed_href()`다.
- **이동 의미론**: 링크 이동(`<a href>` — 브라우저 기록에 쌓기)·redirect 응답(요청 결과를 다른 주소로 교체 — POST 뒤 PRG)·HTMX 부분 교체(기록 불변 — implementation-htmx §7) 셋이고, 지속 셸(아래 «지속 셸»)에는 넷째로 **부스트 이동**이 있다 — 주소·기록은 링크 이동과 같고(같은 주소면 대체) 문서·머리·탭 막대·본문 틀은 남고 `<main id="root-content">` 안만 바뀐다(‹뒤로›·‹앞으로›도 같다 — 사본 없이 서버에서 받아 `<main>` 안만). 일반 이동은 이름 기반이며 navigator가 `reverse(<Bc>Routes.…)`로 href를 만든다. 기본 홈 목적지 한 건만 architecture-ui §6의 소유 router 상수를 소유 navigator가 가공 없이 반환한다(타 BC는 그 navigator 호출 · 폴백 금지). `reverse`·`redirect`에 문자열 리터럴을 넘기지 않는다(백스톱 NM13). view의 redirect는 `redirect(state.next_href)` 하나다 — 조각(HTMX) 요청의 3xx 응답은 `RootRequestHandler`가 200 + `HX-Redirect: <Location>`으로 바꿔 htmx가 전체 이동하게 한다(아래 게이트).
- **요청 없는 호출**: 일반 이동 주소는 `reverse()`가 활성 URLconf의 이름 등록으로 계산하고, 기본 홈 주소 한 건은 이름 역참조 없이 반환하므로 **`request` 없이 같은 결과를 낸다** — navigator 정적 헬퍼를 VM에서 부르는 것(architecture-state §2·architecture-ui §6)의 공식 근거.
- **navigator — router는 헬퍼 함수 안에서 import한다**:

```python
# application/channel/channel_navigator.py — 일반 이동은 이름 기반, View import 금지
from django.urls import reverse


class ChannelNavigator:
    @staticmethod
    def channel_detail_href(channel_id: str) -> str:
        from web.application.channel.channel_router import ChannelRoutes  # 함수 안 import — 순환 사슬 끊기

        return reverse(ChannelRoutes.DETAIL, kwargs={"channel_id": channel_id})

    @staticmethod
    def channel_summary_list_href() -> str:  # <화면>_<조각>_href — 조각 재요청(재시도) 주소
        from web.application.channel.channel_router import ChannelRoutes

        return reverse(ChannelRoutes.SUMMARY_LIST)

    @staticmethod
    def channel_summary_embed_href() -> str:  # <화면>_embed_href — 다른 화면의 임베드 자리 주소
        from web.application.channel.channel_router import ChannelRoutes

        return reverse(ChannelRoutes.SUMMARY_EMBED)
```

기본 홈 목적지 소유 BC를 `landing`으로 명세한 경우의 예다(소유 BC 이름을 규약으로 고정하지 않는다). 활성 URLconf에 home 이름이 없어도 아래 반환은 성공하며, 일반 named href의 누락은 `NoReverseMatch`로 남는다 — 예외 주소로 폴백하지 않는다.

```python
# application/landing/landing_router.py — 기본 홈 주소의 단일 출처
DEFAULT_HOME_URL: str = "/"

# application/landing/landing_navigator.py
class LandingNavigator:
    @staticmethod
    def default_home_href() -> str:
        from web.application.landing.landing_router import DEFAULT_HOME_URL

        return DEFAULT_HOME_URL  # 가공 없이 반환

# 다른 BC는 router가 아니라 이 navigator를 호출한다.
```

`<bc>_router.py`는 path 바인딩 때문에 view를 import하고, view→VM→navigator로 이어진다. navigator가 모듈 머리에서 router를 import하면 첫 import에서 router가 아직 `ChannelRoutes`를 정의하기 전이라 `ImportError`(부분 초기화 모듈)가 난다 — 그래서 **router import는 navigator 헬퍼 함수 안에 둔다**(호출 시점에는 urlconf가 다 올라와 있다). 이 자리가 dddjango-web의 정당한 함수 안 import다 — 국소 `ruff.toml`(discipline-houserules §3)에 `PLC0415`(import-outside-toplevel)를 켜지 않는다. `<Bc>Routes`를 별도 파일로 빼서 사슬을 끊지 않는다(architecture-ui §6).

- **템플릿은 URL을 만들지 않는다**: `{% url %}`·`href="/…"` 경로 리터럴을 쓰지 않고 State가 준 href를 쓴다(`<a href="{{ state.detail_href }}">` — 백스톱 NM13). 정적 파일만 `{% static %}`(§8).
- **문서 셸·탭** — `root/scaffold/view/root_view.html`이 기본 문서 셸이다. 탭 셸은 두 꼴이다 — **지속 셸**(새로 짓는 탭 셸의 기본 · 탭 막대는 탭 이동·‹뒤로›에도 남고 본문만 바뀜 · 앱 탭 바 · dddart `StatefulShellRoute` 대응 · 아래 «지속 셸») · **문서 이동 셸**(아래 예 · 이미 지은 셸을 G1 에서 바꾸지 않았으면 그대로 둔다 — 탭 = 브라우저 이동). 제품 선언이 없으면 모든 페이지가 extends하고, 선언 BC의 페이지는 자기 제품 셸만 extends한다(탭 프레임 — 페이지가 셸을 가리키는 방향은 Django 템플릿 상속의 방향이라 BC가 root를 아는 유일한 예외 — discipline-houserules §5):

```django
{# root/scaffold/view/root_view.html — 문서 이동 셸(이미 지은 셸 · 탭 = 브라우저 이동) #}
{% load static %}
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  {# foundation 7 파일(app_color.css … app_asset.css)을 한 줄씩 링크한 뒤 theme #}
  <link rel="stylesheet" href="{% static 'design_system/foundation/app_color.css' %}">
  <link rel="stylesheet" href="{% static 'design_system/theme/app_theme.css' %}">
  <link rel="stylesheet" href="{% static 'web/root/root_view.css' %}">
  {# htmx core — build-state htmx_core_static 경로 그대로(새 설치 web/htmx/htmx.min.js · 브라운필드 예 web/js/htmx.min.js) #}
  <script src="{% static 'web/htmx/htmx.min.js' %}" defer></script>
  {% block head %}{% endblock head %}
</head>
<body data-testid="root-view">
  <main>{% block content %}{% endblock content %}</main>
  <nav class="root-tab-bar">
    {% for tab in root_state.tabs %}
      <a href="{{ tab.href }}"{% if tab.is_current %} aria-current="page"{% endif %}>{{ tab.label }}</a>
    {% endfor %}
  </nav>
  {% block scripts %}{% endblock scripts %}
</body>
</html>
```

제품 선언이 있으면 flat의 `root_view.html`과 own의 `root_<제품>_view.html`은 모두 위와 같은 독립 문서이며 어떤 템플릿도 extends하지 않는다(백스톱 IM26). own 셸의 예: `root/scaffold/view/root_shop_view.html`은 자기 `design_system/shop/foundation/`의 표준 7파일 다음에 `design_system/shop/theme/app_theme.css`만 링크하고, 틀 CSS는 `web/root/root_shop_view.css`다(기존 `root_vm.py`·`root_state.py`를 함께 쓴다).

**지속 셸(새로 짓는 탭 셸의 기본)** — 탭 막대 `<nav>` 하나에 `hx-boost` 를 달고, 부스트 · 복원 응답은 `RootRequestHandler` 가 응답 머리로 `<main>` 안만 바꾸게 한다(아래 처리기 표). 앱처럼 막대는 탭 이동 · ‹뒤로› · ‹앞으로›에도 같은 요소로 남고, 같은 탭을 이미 첫 화면에서 다시 누르면 요청 없이 맨 위로 간다. 화면 HTML 사본은 브라우저에 남기지 않는다(`historyCacheSize` 0).

```django
{# root/scaffold/view/root_view.html — 지속 셸: 머리 · 탭 막대 · 본문 틀은 남고 <main> 안만 바뀐다 #}
{% load static %}
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="htmx-config" content='{"historyCacheSize":0}'>
  <title>{% block title %}채널{% endblock title %}</title>
  {# foundation 7 → theme → 틀 CSS → 부품 · util · 조각 CSS(경로 순) — 이 제품 화면이 쓰는 CSS 전부를 한 번 · 꼬리 ?v= 는 머리 판(배포 뒤 캐시를 비켜 간다) #}
  <link rel="stylesheet" href="{% static 'design_system/foundation/app_color.css' %}?v={{ root_state.shell_rev }}">
  {# … foundation 나머지 여섯 … #}
  <link rel="stylesheet" href="{% static 'design_system/theme/app_theme.css' %}?v={{ root_state.shell_rev }}">
  <link rel="stylesheet" href="{% static 'web/root/root_view.css' %}?v={{ root_state.shell_rev }}">
  <link rel="stylesheet" href="{% static 'design_system/component/dialog/confirm_dialog.css' %}?v={{ root_state.shell_rev }}">
  <link rel="stylesheet" href="{% static 'web/application/channel/channel_summary_view.css' %}?v={{ root_state.shell_rev }}">
  {# htmx core → root_shell.js → 등재 SDK → 기능 JS(경로 순) — 문서 수명 한 번 · 모두 defer #}
  <script src="{% static 'web/htmx/htmx.min.js' %}?v={{ root_state.shell_rev }}" defer></script>
  <script src="{% static 'web/js/root_shell.js' %}?v={{ root_state.shell_rev }}" defer></script>
  <script src="{% static 'web/js/password_visibility.js' %}?v={{ root_state.shell_rev }}" defer></script>
</head>
<body data-testid="root-view" data-root-shell="root_view@{{ root_state.shell_rev }}">
  <main id="root-content" hx-history-elt>
    {% block content %}{% endblock content %}
    <template>
      <div id="root-tab-items" class="root-tab-bar__items" hx-swap-oob="innerHTML">
        {% for tab in root_state.tabs %}
          <a id="root-tab-{{ tab.key }}" class="root-tab-bar__tab root-tab-bar__tab--{{ tab.key }}{% if tab.is_current %} root-tab-bar__tab--current{% endif %}"
             href="{{ tab.href }}"{% if tab.is_current %} aria-current="page"{% endif %}>{{ tab.label }}</a>
        {% endfor %}
      </div>
    </template>
  </main>
  <nav id="root-tab-bar" class="root-tab-bar" hx-boost="true" hx-sync="this:replace">
    <div id="root-tab-items" class="root-tab-bar__items">
      {% for tab in root_state.tabs %}
        <a id="root-tab-{{ tab.key }}" class="root-tab-bar__tab root-tab-bar__tab--{{ tab.key }}{% if tab.is_current %} root-tab-bar__tab--current{% endif %}"
           href="{{ tab.href }}"{% if tab.is_current %} aria-current="page"{% endif %}>{{ tab.label }}</a>
      {% endfor %}
    </div>
  </nav>
</body>
</html>
```

- htmx core 줄은 build-state `htmx_core_static` 경로다(새 설치 `web/htmx/htmx.min.js` · 브라운필드 `web/js/htmx.min.js` 등 — 지속 셸이면 그 파일이 2.0.10 이어야 한다 · implementation-htmx §1).
- 첫 문서: `<template>` 안은 그려지지 않고(문서 트리 밖 — id 겹침 없음) htmx 도 처리하지 않는다. 탭 막대는 `<nav>` 안의 목록으로 그려진다.
- 부스트 응답(같은 셸): core 가 template 안 OOB 를 처리해 살아 있는 `#root-tab-items` 의 **자식만** 바꾸고(막대 요소는 그대로) template 를 지운 뒤, `HX-Reselect: #root-content > *` 로 응답 `<main>` 의 자식을 골라 살아 있는 `<main>` 안에 넣는다. 응답의 `<nav>` 는 버려진다. OOB 로 새로 놓인 탭 링크는 정착(20ms) 뒤에야 부스트가 걸린다 — 그 사이 누름은 문서 이동이다(안전한 쪽).
- 복원 응답(‹뒤로›·‹앞으로›): core 가 응답을 `[hx-history-elt],[data-hx-history-elt]`(= 응답 `<main>`)로 좁히고 그 안 template OOB 를 같은 방식으로 처리한 뒤 `<main>` 안을 바꾼다 — 탭 목록 · 제목도 함께 맞는다.
- **root 가 요청마다 바뀌는 자료를 화면 JS 에 줘야 하면** `<main>` 안 · `{% block content %}` 앞에 `{{ root_state.<값>|json_script:"root-<이름>" }}` 한 줄씩 둔다 — 탭 이동마다 본문과 함께 바뀐다. body 바로 아래에 두면 첫 문서 값으로 굳는다(꼴 ⑫ 위반). 읽는 JS 는 `htmx:load` 마다 다시 읽는다(implementation-javascript §3 «지속 셸의 수명» P4).
- 탭 목록 반복문이 두 번이다(첫 문서용 · OOB 용) — 새 파일을 만들지 않으려는 것이다(discipline-houserules §4). 두 반복문의 글자가 같은지는 꼴 ⑨ 가 본다.
- 페이지는 지금처럼 셸을 extends 하고 `{% block title %}` · `{% block content %}` 만 채운다(중간 base 를 거쳐도 된다 — 그 사슬 전체와 그 사슬이 include 하는 템플릿이 지속 셸 소속이다 · 백스톱 SH3). `{% block head %}` · `{% block scripts %}` 는 셸에 없다(정의하면 죽은 글 — SH3).
- 백스톱 SH1 이 부스트 `<a>` 를 허용하는 «화면»은 이 소속 안에서 셋이다: ① 지속 셸 제품의 `presentation_layer/{view,section,widget}/` 조각과 `root/scaffold/view/` 조각(제품 선언이 없을 때 — 선언이 있으면 root 조각은 ③ 으로만) — 어디서 그려지든 ② 지속 셸 제품의 개념 폴더 한 단 아래(`presentation_layer/<개념>/section/` 등) view · section · widget ③ 사슬과 사슬이 글자 include 로 거듭 그리는 템플릿 — 옛 배치 · 다른 제품 템플릿 포함 · `application/` 아래는 view · section · widget(개념 폴더 한 단까지)만(include 대상이 extends 하는 부모 쪽은 따르지 않는다 · design_system 부품 · `common/` 은 화면이 아니다). ② · ③ 가운데 표준 문서 이동 셸 화면도 글자 extends · include 로 그리는 템플릿은 화면으로 세지 않는다.
  - SH1 이 막지만 규칙상 허용인 꼴: 변수 include 로만 그리는 옛 조각(글자 include 로 고친다) · hx-get 응답으로만 지속 화면에 들어가는 옛 조각 · 조각 레이아웃 부모가 include 하는 조각(카드 base 꼴) — 이 둘은 검사기 이의로 올린다.
  - SH1 이 통과시키지만 위반일 수 있는 꼴: ① 자리 조각을 문서 이동 셸 화면도 그리는 경우 · 옛 문서 레이아웃(표준 셸 밖)이 함께 그리는 조각 · 문서 화면이 SH1 이 못 보는 길(변수 include · 변수 extends · hx-get 조각 응답)로 함께 그리는 조각(지속 제품 · 옛 배치 · 다른 제품 모두) — 감수가 그 링크가 지속 셸 아래에서만 그려지는지 확인한다.
- **별칭 한 계약**: 이 꼴의 `hx-*` 는 모두 `data-hx-*` 별칭으로 써도 된다 — htmx · 서버 판별(아래 처리기의 `HISTORY_ELT_ATTRS`) · 백스톱 SH 가 같게 받는다. 같은 요소에 두 이름을 함께 쓰면 값이 같아야 한다(htmx 는 `hx-` 값을 먼저 읽는다). 표준 글은 `hx-*` 로 쓴다.

**지속 셸의 고정 꼴**(백스톱 SH2 가 본다 — `hx-*` 는 `data-hx-*` 별칭도 같은 속성으로 본다):

- ① `<meta name="htmx-config">` 하나 · 값 = `{"historyCacheSize":0}`(JSON 파싱 뒤 같음).
- ② `<title>{% block title %}<기본값 — 비지 않음>{% endblock title %}</title>`.
- ③ 실행 `<script>` · `<link rel="stylesheet">` 는 모두 `<head>` 안.
- ④ 실행 태그 순서 = htmx core → `web/js/root_shell.js` → 등재 SDK → 기능 JS(모두 `defer`).
- ⑤ block 은 `title` · `content` 둘뿐(`head` · `scripts` 없음 · 탭 막대를 block 으로 감싸지 않음 — 내비를 숨기는 화면은 다른 셸이다).
- ⑥ `<body>` 에 `data-root-shell="<셸 stem>@{{ root_state.shell_rev }}"` 정확히 · 그 밖 body 속성은 정적 값만.
- ⑦ `<main id="root-content">` + `hx-history-elt`(또는 별칭 · 둘 다)(그 밖 속성은 정적 `class` · `data-testid` 만)의 자식 = (선택) 셸 자료 `{{ … |json_script:"root-…" }}` 줄들 → `{% block content %}` → 마지막 `<template>`(안에 `<div id="root-tab-items" … hx-swap-oob="innerHTML">` 하나).
- ⑧ `<nav id="root-tab-bar" … hx-boost="true" hx-sync="this:replace">` 는 `<main>` 다음 형제 · 그 밖 hx-* 없음.
- ⑨ nav 안 `<div id="root-tab-items">` 의 안쪽 글자 = template 안 것과 같음(들여쓰기 · 줄바꿈 차이는 무시).
- ⑩ 탭 링크 = `<a id="root-tab-{{ tab.key }}" … href="{{ tab.href }}">` · 링크에 hx-* 없음 · 고른 탭은 `aria-current="page"`.
- ⑪ 셸 어디에도 `hx-target` · `hx-select` · `hx-swap` · `hx-select-oob` · `hx-headers` · `hx-disinherit` · `hx-vals` · `hx-history`(속성 이름 그대로 — `hx-history-elt` 와 다름 · 있으면 `root_shell.js` 가 되돌릴 history state 사본이 없다) 없음.
- ⑫ **`<body>` 의 자식은 `<main>` · `<nav>` 둘뿐** — 그 밖 요소 · `{% include %}` · 템플릿 변수 · 텍스트 없음.
- ⑬ **머리의 모든 `<link rel="stylesheet">` `href` · `<script>` `src` = `{% static '<경로>' %}?v={{ root_state.shell_rev }}`** 정확히.

탭 막대 틀 CSS — 막대는 남는 요소이고 상태는 고른 탭 class 에서 읽는다:

```css
/* web/static/root/root_view.css — 지속 셸 틀 */
.root-tab-bar { transition: padding-top var(--duration-base) var(--easing-standard), padding-bottom var(--duration-base) var(--easing-standard); }  /* 전환은 물리 속성으로 — WebKit 은 padding-block 전환을 그리지 않는다 */
.root-tab-bar:has(.root-tab-bar__tab--chat.root-tab-bar__tab--current) { padding-block: var(--spacing-1); }
.root-tab-bar__tab { transition: background-color var(--duration-base) var(--easing-standard); }
.root-tab-bar__tab--current { background-color: var(--color-primary); }
.root-tab-bar__tab.htmx-request { opacity: 0.6; }  /* 누른 즉시 표시 — htmx 상태 class 는 접두 class 와 겹쳐서만 */
@media (prefers-reduced-motion: reduce) { .root-tab-bar, .root-tab-bar__tab { transition: none; } }
```

- **막대(`<nav>`)의 움직임**은 막대 요소가 남아 있으므로 `:has()` 결과가 바뀌는 순간 보통 CSS 전환으로 돈다 — 정착 20ms 와 무관하다. `:has()` 는 Chromium 105 · Safari 15.4 · Firefox 121 부터다(못 쓰는 옛 브라우저는 크기만 안 바뀐다).
- **전환 속성은 물리 속성으로 적는다**: 값은 논리 축약 `padding-block` 으로 써도 되지만 `transition` 목록에는 `padding-top` · `padding-bottom` 을 적는다 — WebKit 은 `padding-block` 전환을 그리지 않는다.
- **탭 링크 안의 움직임**은 링크가 새 요소라 htmx 정착에 기댄다(같은 id 새 링크에 옛 `class` · `style` · `width` · `height` 를 먼저 입혔다가 정착 지연 뒤 새 값). 그래서 움직이는 상태 선택자는 정착되는 class(`root-tab-bar__tab--current` · `--<key>`)로 쓴다 — `aria-current` 는 접근성 값으로 함께 두되 움직임의 선택자로 쓰지 않는다.
- **공유 머리**(백스톱 SH4 가 완비 · 중복 · 순서를 본다): 셸 머리가 싣는 것 = 그 제품 foundation 7(color · typography · spacing · radius · shadow · duration · asset 순) → theme → 틀 CSS(`static/root/<셸 stem>.css`) → 그 제품의 `component/**/*.css` · `util/*.css` + 그 제품 BC 의 `static/application/[<area>/]<bc>/**/*.css` + 그 셸을 extends 하는 root 게이트 화면의 `static/root/<stem>.css`(경로 순 한 줄씩) → **htmx core**(`htmx_core_static`) → **`static/js/root_shell.js`** → 그 제품 기능 JS 가 부르는 등재 SDK → **기능 JS = `static/js/*.js` 전부에서 htmx core · `root_shell.js` 를 뺀 것**(경로 순). 옛 배치 CSS · JS(이관 중)는 넣어도 되지만(순서 자유 · theme 뒤) 중복 · 없는 파일은 안 된다. 경로 순으로 못 박는 것은 여러 작업이 같은 셸 머리에 줄을 더해도 «두 줄 모두 넣고 다시 정렬»로 풀리게 하려는 것이다 — SH4 발견 문구가 넣을 줄을 그대로 낸다. 첫 열기에 그 제품 자산을 한꺼번에 받는 대신 탭 이동마다 CSS 를 새로 받지 않아 무서식 화면이 없다. 한 문서에 그 제품의 조각 CSS 가 모두 실리므로 맨 선택자와, 같은 BEM block 을 둘 이상 파일이 첫 복합 선택자로 정의하는 겹침을 SH5 가 막는다(완료 조건 = 검출 대상 위반 0 + 판독 불가 `[info]` · 알려진 미탐 감사 완료). JS 의 제품 소속은 없다 — 제품이 여럿이면 다른 제품 기능 JS 도 실린다(root 없는 화면에서 무해하게 — implementation-javascript §3 «지속 셸의 수명» P6).
- **자산 주소 `?v=`**: 머리 판(`root_state.shell_rev` — §3 «지속 셸이면»)이 바뀌면 주소가 바뀌어 정적 캐시(`expires` 등)를 비켜 간다 · 정적 서버는 꼬리를 무시하고 같은 파일을 준다. CSS 안의 `url()`(글꼴 · 그림)은 꼬리가 없다(알려진 한계). 정적 주소(`{% static %}` 결과)에 이미 `?` 꼬리가 붙는 저장소는 이 꼴을 못 쓴다(G0 점검).

**`root_shell.js` — 지속 셸의 root 소유 JS**(`web/static/js/root_shell.js` · 아래 글 그대로 · 고칠 값 없음 — 셸이 htmx core 바로 뒤에 싣는다):

```javascript
// web/static/js/root_shell.js — 지속 셸: 셸 표지 · 이동 번호 머리 · 이동 하나만(누름 시작 철회 · 철회 구간 · 적용 직전 지킴 · 문서 떠남)
//                                · 떠난 화면의 조각 요청 끊기 · 화면 밖 요청 요소의 지연 교체 없앰 · 맨 위 보이기 · 기능 history state 보전 · 재탭 ② · 실패 길
(() => {
  const here = () => location.pathname + location.search;
  const mark = () => document.body.dataset.rootShell || "";
  if (!mark()) return;  // 셸 표지가 없다(표지를 걷어 되돌린 판 · 문서 이동 셸) — 아무것도 하지 않는다(defer 라 body 가 있다)
  const clock = () => Math.floor(performance.timeOrigin + performance.now());  // 한 문서 안에서는 기기 시계를 돌려도 줄지 않는다
  let navSeq = 0;
  const nextSeq = () => String((navSeq = Math.max(clock(), navSeq + 1)));  // 늘 커지는 이동 번호
  let boost = null;  // 진행 중 부스트 XHR
  let restore = null;  // 진행 중 복원 XHR — htmx 는 복원 요청을 내부 자료에 걸지 않아 hx-sync · htmx:abort 가 닿지 않는다
  let depth = 0;  // 철회 구간 깊이 — 이 구간(동기) 안에서 core 가 대기 큐로 다시 연 부스트는 철회된 이동이다
  let leaving = false;  // 사용자가 고른 문서 이동이 시작됨 — 끊긴 XHR 의 error · 실패로 다른 이동을 일으키지 않는다
  let discarded = false;  // 적용 직전 지킴이 버린 복원 — 그 복원의 완료 이벤트를 기능 JS 에 알리지 않는다
  let saved;  // htmx 가 {htmx:true} 로 덮기 직전 그 항목의 state
  let screen = 0;  // 화면 세대 — root 이동(부스트 · 실제 복원)이 <main> 안을 바꿀 때마다 1 늘어난다
  const pending = new Map();  // 진행 중 조각(부스트 아닌) 요청 XHR → 그 요청을 시작한 화면 세대 — 화면이 바뀌면 앞 세대 것을 모두 끊는다

  const cancel = (xhr) => {
    if (xhr && xhr.readyState !== XMLHttpRequest.DONE) xhr.abort();  // 끝나지 않은 것만 — abort 이벤트는 그 자리에서(동기) 난다
  };
  const withdraw = () => {  // 진행 중 복원 · 부스트를 거둔다 — 그 abort 안에서 core 가 대기 큐를 다시 열면 아래 두 리스너가 막는다
    depth += 1;
    try {
      cancel(restore);
      cancel(boost);
    } finally {
      depth -= 1;
    }
    restore = null;
    boost = null;
  };
  const isBoostLink = (elt) => elt instanceof HTMLAnchorElement  // SH1 이 지키는 꼴 — 탭 막대 링크 · hx-boost="true" 를 직접 단 <a>
    && elt.matches('#root-tab-bar a[href], a[href][hx-boost="true"], a[href][data-hx-boost="true"]')
    && !elt.matches('[hx-boost="false"], [data-hx-boost="false"]');
  const leavesDocument = (event) => {  // 이 창의 문서를 떠나는 기본 동작인가(새 창 · 내려받기 · 같은 문서 앵커 · 대화상자 폼은 아님)
    if (event.type === "submit") {
      const form = event.target;
      if (!(form instanceof HTMLFormElement)) return false;
      const target = event.submitter?.getAttribute("formtarget") ?? form.getAttribute("target") ?? "";
      const method = (event.submitter?.getAttribute("formmethod") ?? form.getAttribute("method") ?? "get").toLowerCase();
      return method !== "dialog" && (target === "" || target === "_self");
    }
    const link = event.target instanceof Element ? event.target.closest("a[href]") : null;
    if (!link || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return false;
    if (link.hasAttribute("download") || !(link.target === "" || link.target === "_self") || !/^https?:$/.test(link.protocol)) return false;
    return !(link.hash && link.href.split("#")[0] === location.href.split("#")[0]);
  };
  const leave = () => {
    leaving = true;
    withdraw();
  };
  const leaveOnMove = (event) => {  // core 가 이 응답으로 문서를 옮긴다(HX-Redirect · HX-Refresh) — 교체 전 첫 자리 · 취소된 응답(이동 없음)은 떠남이 아니다
    const xhr = event.detail.xhr;
    if (!event.defaultPrevented && (xhr.getResponseHeader("HX-Redirect") || xhr.getResponseHeader("HX-Refresh") === "true")) leave();
  };
  const outsideScreen = (node) => {  // 붙어 있고 화면(<main> 의 자식 트리) 밖인 요소 — body · <main> 자신 · 막대: root 이동 뒤에도 문서에 남는다
    const content = document.getElementById("root-content");
    return node instanceof Node && node.isConnected && !(content && node !== content && content.contains(node));
  };

  const first = history.state;  // 첫 문서 항목에도 htmx 표지 — 기능 JS 가 state 를 펼쳐 복사할 때 표지가 따라가게(H2)
  if (first === null || (typeof first === "object" && !first.htmx)) history.replaceState({ ...first, htmx: true }, "", location.href);

  window.addEventListener("popstate", withdraw);  // 셸 머리 defer — htmx 의 window.onpopstate(DOMContentLoaded) · 기능 JS 보다 먼저 돈다
  window.addEventListener("pagehide", () => { leaving = true; });
  window.addEventListener("pageshow", () => { leaving = false; });
  window.navigation?.addEventListener("navigate", (event) => {  // 기능 JS 의 location.assign 등 — Navigation API 가 있는 엔진만
    if (!event.destination.sameDocument && event.downloadRequest === null) leave();
  });
  for (const type of ["click", "submit"]) {
    window.addEventListener(type, (event) => {  // 버블 끝 — 막히지 않은 이 창의 문서 이동이면 진행 중 이동을 거둔다
      if (!event.defaultPrevented && leavesDocument(event)) leave();
    });
  }
  document.addEventListener("root:leave", leave);  // 기능 JS 가 JS 로 문서를 옮기기 바로 앞의 알림(P11) — Navigation API 와 무관하게 선다
  window.addEventListener("htmx:before-on-load", leaveOnMove);  // 붙은 요청 요소의 응답 — 케밥 이름 · 창 버블: core 는 camel 이름이 취소되지 않았을 때만
  //                                                              이 이름을 같은 detail 로 이어 내므로 기능 JS 가 취소한 응답(이동 없음)은 여기 오지 않는다

  document.addEventListener("click", (event) => {  // 재탭 ② — 이미 그 탭 첫 화면이면 요청 없이 맨 위로(앱과 같음)
    const link = event.target instanceof Element ? event.target.closest("#root-tab-bar a[href]") : null;
    if (!link || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    if (leaving || restore || link.getAttribute("aria-current") !== "page") return;  // 문서 이동 · 복원 중이면 아래 confirm 갈래로
    if (link.origin !== location.origin || link.pathname + link.search !== here()) return;  // 중첩 화면 = 재탭 ① → 첫 화면 부스트
    event.preventDefault();
    event.stopPropagation();  // 포착 단계 — 링크 위 core 부스트 리스너까지 가지 않는다
    withdraw();  // 진행 중 부스트(다른 탭으로 가던 것)는 거둔다 — 주소 · 화면은 아직 이 화면이다
    window.scrollTo({ top: 0, behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth" });  // "auto" 는 CSS scroll-behavior 를 따르므로 값을 정해 준다
  }, true);

  document.addEventListener("htmx:confirm", (event) => {  // 부스트 누름의 시작 — core 가 hx-sync · 대기 큐를 고르기 전
    if (!isBoostLink(event.detail.elt)) return;
    if (depth > 0) {
      event.preventDefault();  // 철회 구간 안 = core 가 큐에서 다시 연 철회된 이동(사용자 입력은 이 동기 구간에 들어오지 않는다)
      return;
    }
    if (leaving) {  // 문서 이동이 진행 중 — 이 누름도 문서 이동으로(새 이동이 앞 이동을 대체 · 마지막 누름이 이김)
      event.preventDefault();
      window.location.assign(event.detail.elt.href);
      return;
    }
    withdraw();  // 앞 이동을 거둬 같은 링크의 대기 큐가 생기지 않게 — 화면 안 링크도 «새 누름이 대체»
  });
  document.addEventListener("htmx:configRequest", (event) => {
    if (!event.detail.boosted) return;
    event.detail.headers["X-Root-Shell"] = mark();
    event.detail.headers["X-Root-Nav"] = nextSeq();
  });
  document.addEventListener("htmx:beforeRequest", (event) => {
    if (!event.detail.boosted) {  // 조각 요청 — 요청 요소가 body 여도(HX-Location 후속 · source 없는 htmx.ajax) 이 화면에서 시작한 요청이다
      if (depth > 0) {
        event.preventDefault();  // 철회 구간 안 = 끊은 조각 요청의 대기 큐가 다시 연 앞 화면 요청 — core 는 보내지 않고 잠금을 푼다
        return;
      }
      const xhr = event.detail.xhr;
      const source = event.detail.elt;  // 요청 요소(= requestConfig.elt)
      const target = event.detail.target;  // core 가 htmx:beforeSwap 을 내는 요소 — HX-Retarget 이 와도 요청 시작 때 잡은 이 대상에서 낸다
      const onMove = (load) => {  // 조각 교체로 떨어진 요청 요소의 응답은 창까지 오지 않는다 — 그 요소에 직접 단 리스너는 돈다
        if (load.detail.xhr === xhr && !source.isConnected) leaveOnMove(load);
      };
      const noDelay = (swap) => {  // 화면 밖에 붙은 요청 요소(body 등)의 지연 교체는 root 이동이 거두지 못하고 OOB 를 문서에서 찾는다 — 지연을 없앤다
        if (swap.detail.xhr === xhr && outsideScreen(source)) swap.detail.swapOverride = `${swap.detail.swapOverride ?? ""} swap:0ms`.trim();  // 마지막 swap: 이 이긴다
      };
      source.addEventListener("htmx:before-on-load", onMove);
      target.addEventListener("htmx:beforeSwap", noDelay);
      pending.set(xhr, screen);
      xhr.addEventListener("loadend", () => {
        pending.delete(xhr);
        source.removeEventListener("htmx:before-on-load", onMove);
        target.removeEventListener("htmx:beforeSwap", noDelay);
      });
      return;
    }
    if (depth > 0) {
      event.preventDefault();  // 같은 지킴의 두 번째 자리 — core 는 취소된 요청을 보내지 않고 잠금을 푼다
      return;
    }
    const xhr = event.detail.xhr;
    const path = event.detail.pathInfo.requestPath;
    if (boost !== xhr) withdraw();
    leaving = false;
    boost = xhr;
    xhr.addEventListener("error", () => { if (!leaving) window.location.assign(path); });  // 연결 실패 → 문서 이동(누른 요소가 떨어져 나가도 듣는다)
    xhr.addEventListener("loadend", () => { if (boost === xhr) boost = null; });
  });
  window.addEventListener("htmx:afterSwap", (event) => {  // root 이동(부스트 · 실제 복원)이 <main> 안을 바꾼 직후 — 창 포착이라 다른 afterSwap 리스너보다 먼저 ·
    if (event.target.id !== "root-content") return;      // 버린 복원은 떼어 낸 <main> 이라 오지 않는다
    screen += 1;
    depth += 1;  // 끊는 동안 core 가 대기 큐로 다시 연 앞 화면 조각 요청은 위 beforeRequest 가 막는다
    try {
      for (const [xhr, born] of pending) {
        if (born < screen) {  // 앞 화면에서 시작한 조각 요청 — 요청 요소 · 대상이 아직 붙어 있어도 끊는다(늦은 HX-Redirect · HX-Refresh · OOB 가 새 화면을 덮지 않게 — 문서 이동 셸에서는 새 문서와 함께 모두 버려졌다)
          pending.delete(xhr);
          cancel(xhr);
        }
      }
    } finally {
      depth -= 1;
    }
    if (event.detail.boosted) window.scrollTo({ top: 0, left: 0, behavior: "instant" });  // 부스트 = 맨 위 — 교체 직후 그 자리에서 · CSS scroll-behavior 를 비켜 감(core 와 같음 · core 정착 스크롤은 show:none 으로 끔)
  }, true);

  document.addEventListener("htmx:beforeHistorySave", () => { saved = history.state; });
  const keep = () => {  // htmx 의 replaceState({htmx:true}) 직후 · 같은 항목이 아직 현재일 때 그 항목의 기능 state 를 표지와 함께 되돌린다
    const state = saved;
    saved = undefined;
    if (state && typeof state === "object" && Object.keys(state).some((key) => key !== "htmx")) {
      history.replaceState({ ...state, htmx: true }, "", location.href);
    }
  };
  document.addEventListener("htmx:beforeHistoryUpdate", keep);  // 부스트로 떠나는 항목 — push 직전

  document.addEventListener("htmx:historyCacheMiss", (event) => {  // 뒤로 · 앞으로로 도착한 항목(사본이 없어 늘 여기로 온다)
    keep();
    withdraw();
    leaving = false;
    const xhr = event.detail.xhr;  // open 뒤 · send 앞 — 머리를 더할 수 있다
    restore = xhr;
    xhr.setRequestHeader("X-Root-Shell", mark());
    xhr.setRequestHeader("X-Root-Nav", nextSeq());
    xhr.addEventListener("error", () => { if (!leaving) window.location.reload(); });  // 복원 요청에는 onerror 가 없다
    xhr.addEventListener("loadend", () => { if (restore === xhr) restore = null; });
  });
  document.addEventListener("htmx:historyCacheMissLoad", (event) => {
    if (event.detail.path === here()) return;
    // 목적지가 지금 주소가 아니다(복원 중 기능 JS 가 다른 주소로 옮김) — 이 응답을 버린다. core 는 반환값을 보지 않지만 detail 이
    // core 의 요청 기록 그 자체라 교체 자리 · 응답 · 경로를 바꾸면 떼어 낸 요소에 빈 본문을 넣고 지금 주소를 기록한다.
    event.detail.historyElt = document.createElement("main");
    event.detail.response = "<main hx-history-elt></main>";
    event.detail.path = here();
    discarded = true;
    queueMicrotask(() => { discarded = false; });  // 같은 onload 안에서 이어 나는 완료 이벤트 둘(camel · kebab)이 지난 뒤
  });
  for (const type of ["htmx:historyRestore", "htmx:history-restore"]) {
    window.addEventListener(type, (event) => { if (discarded) event.stopImmediatePropagation(); }, true);  // 버린 복원은 «복원됨»으로 알리지 않는다
  }
  document.addEventListener("htmx:historyCacheMissLoadError", () => { if (!leaving) window.location.reload(); });  // 409 · 그 밖 실패 → 지금 주소를 문서로
})();
```

**지킴의 근거 — htmx 2.0.10 이벤트 계약**(지속 셸은 core 2.0.10 이 전제다 — implementation-htmx §1):

- *누름 시작 철회 · 대기 큐*: htmx 는 부스트 링크 누름에서 `htmx:confirm` 을 먼저 내고 그 뒤에 `hx-sync` · 대기 큐를 고른다. 그 자리에서 앞 이동을 `abort()` 하면 진행 중 요청이 비어 새 요청이 큐 없이 열린다 — 화면 안 링크를 요청 중 다시 눌러도 둘째가 큐에 들지 않는다(탭 막대의 `this:replace` 와 같은 «새 누름이 대체»).
- *철회 구간*: 끝나지 않은 XHR 의 `abort()` 는 abort 이벤트를 그 자리에서(동기) 내고, htmx 는 그 안에서 대기 큐의 맨 앞을 다시 부른다 — 다시 불린 요청의 `htmx:confirm` · `htmx:beforeRequest` 는 `depth > 0` 구간 안이라 취소된다(취소된 confirm 은 요청 없이 끝나고, 취소된 beforeRequest 는 보내지 않고 잠금을 푼다). 사용자 입력은 이 동기 구간에 끼어들 수 없어 «구간 안 = 철회된 큐 · 구간 밖 = 새 사용자 이동» 이 정확히 갈린다. 기능 JS 가 abort 관련 이벤트 안에서 동기로 연 요청도 같은 구간이라 막힌다(철회된 이동의 부수 효과).
- *이동 하나만*: 새 이동의 시작 넷 — popstate(기능 JS 의 `history.back()` 포함) · 부스트 누름 · 복원 시작(`htmx:historyCacheMiss`) · 문서 이동 — 모두에서 진행 중 복원 · 부스트를 거둔다. 복원 요청은 htmx 내부 자료에 걸리지 않아 `hx-sync` · `htmx:abort` 가 닿지 않으므로 root 가 직접 거둔다. 문서 이동이 진행 중일 때의 부스트 누름은 문서 이동으로 낸다(마지막 누름이 이김 — 문서 이동 셸에서 탭 누름이 새 문서 이동이던 것과 같은 결과). popstate 리스너는 셸 머리(defer)에서 등록돼 htmx 의 `window.onpopstate` · 기능 JS 리스너보다 먼저 돈다.
- *문서 떠남*: 막히지 않은 같은 창 링크 · 폼 제출(창 버블 단계에서 `defaultPrevented` 가 거짓) · Navigation API 가 있는 엔진의 문서 간 `navigate` · 기능 JS 의 `root:leave` 알림 · htmx 가 여는 문서 이동(`HX-Redirect` · `HX-Refresh` — 창 버블의 케밥 이름 `htmx:before-on-load` 에서 응답 머리로 · 조각 교체로 떨어진 요청 요소의 응답은 그 요소에 직접 단 리스너로)에서 `leaving` 을 세우고 진행 중 이동을 거둔다 — 늦은 부스트가 새 문서 전에 그려지지 않고, 엔진이 문서를 내리며 끊은 XHR 에 `error` 를 내도 `assign` · `reload` 가 사용자 이동을 덮지 않는다. htmx 는 camel 이름(`htmx:beforeOnLoad`)이 취소되지 않았을 때만 케밥 이름을 이어 내므로 기능 JS 가 취소한 응답(이동 없음)은 떠남으로 읽지 않는다. `pagehide` 도 `leaving` 을 세우고 `pageshow` · 새 root 이동 시작이 푼다. 남는 것(`root:leave` 를 빠뜨린 JS 이동 · 주소창 · 새로고침 단추 같은 브라우저 UI 이동)은 판정이 틀려도 진행 중 이동을 거둘 뿐이다(다음 이동에서 풀림).
- *떠난 화면의 조각 요청*: 교체로 빠지는 옛 요소의 진행 중 XHR 은 htmx 가 끊지 않고, 그 응답 처리는 요소가 문서에 붙었는지 보지 않는다 — 늦은 `HX-Redirect` · `HX-Refresh` · OOB 가 새 화면을 덮을 수 있다(문서 이동 셸에서는 새 문서와 함께 모두 버려졌다). 그래서 root 는 조각 요청을 시작한 화면 세대로 모으고(`htmx:beforeRequest` — 요청 요소가 `body` 인 `HX-Location` 후속 요청 · `source` 없는 `htmx.ajax` 포함), root 이동이 `<main>` 을 실제로 바꾼 직후(창 포착 `htmx:afterSwap` — 기능 JS 의 afterSwap 리스너보다 먼저) 앞 세대 XHR 을 모두 끊는다. 끊는 동안 `body` 대기 큐가 다시 연 앞 화면 요청은 같은 `depth` 구간이 막는다. 새 화면의 요청(`hx-trigger="load"` · `htmx:load` 연결)은 정착 일에서 나므로 새 세대다. 새 화면이 그려지기 **전**에 온 응답은 적용된다(문서 이동 셸의 «새 문서가 들어서기 전» 창과 같다) · 서버는 끊긴 요청도 끝까지 처리한다.
- *화면 밖 요청 요소의 지연 교체*: 응답이 이미 와 `swap:` 지연 타이머로 미뤄진 교체는 끊을 수 없다. 그 교체는 OOB 대상을 요청 요소의 뿌리에서 찾으므로, 화면 안 요청 요소는 root 이동 뒤 떨어진 조각 안에 머물지만 `body` · `<main>` 자신 · 막대처럼 화면 밖에 붙은 요청 요소의 OOB 는 새 화면 · 셸의 같은 id(`#root-tab-items` 등)를 덮는다. 그래서 root 는 그런 요청의 교체 대상에 직접 단 `htmx:beforeSwap` 에서 `swapOverride` 끝에 ` swap:0ms` 를 붙인다(htmx 는 마지막 `swap:` 을 쓴다 · 교체 방식은 그대로) — 그 요청의 전환 연출은 없어진다. 화면 안 요청 요소는 건드리지 않는다(implementation-htmx §7 의 전환 그대로). 그래서 `htmx.ajax` 는 그 화면 root 안 요소를 `source` 로 준다(implementation-javascript §3 «지속 셸의 수명» P3). 남는 것(규칙 밖): 화면 안 요소가 셸 id 를 `hx-target` 으로 삼은 지연 교체 · 기능 JS 가 그 요청의 `swapOverride` 를 다시 바꿈.
- *맨 위 보이기*: 처리기가 `HX-Reswap: innerHTML show:none` 으로 htmx 의 정착 뒤 스크롤을 끄고, root 가 교체 직후(`htmx:afterSwap`) `behavior: "instant"` 로 문서 맨 위로 보낸다 — 철회 뒤 늦게 돌 스크롤 타이머가 남지 않고 프로젝트 CSS 의 `scroll-behavior` 를 비켜 간다. 링크 주소에 `#앵커` 가 있으면 htmx 정착이 그 자리로 보낸다.
- *적용 직전 지킴*: 복원이 가는 중 기능 JS 가 `pushState` · `replaceState` 로 다른 주소로 옮기면 `htmx:historyCacheMissLoad` 에서 목적지(경로+쿼리) ≠ 지금 주소다 — 그 이벤트의 detail 은 htmx 의 요청 기록 그 객체라 교체 자리 · 응답 · 경로를 바꿔 응답을 버리고(떼어 낸 `<main>` 에 빈 본문 · 막대 · 제목 그대로) 지금 주소를 기록한다. 버린 복원의 완료 이벤트(`htmx:historyRestore` · `htmx:history-restore`)는 창 포착 단계에서 막아 기능 JS 에 «복원됨» 으로 알리지 않는다. 이동 식별은 경로+쿼리다 — 같은 주소 `replaceState`(흔한 항목 stamp)면 응답을 적용한다(«주소 = 본문 = 고른 탭»).
- *history state 보전*: htmx 는 이동 때 현재 항목을 `replaceState({htmx:true})` 로 덮는다 — root 가 `htmx:beforeHistorySave` 에서 그 항목의 state 를 잡아 두었다가 떠나는 항목(`htmx:beforeHistoryUpdate` — push 직전)과 도착 항목(`htmx:historyCacheMiss`)에 표지와 함께 되돌린다(`replaceState` 는 항목 키를 바꾸지 않는다). 같은 주소 부스트는 그 항목의 기능 state 를 지운다 — 그 항목을 새로 시작하는 것이라 되돌리지 않는다(같은 주소 링크 = 새 문서이던 문서 이동 셸과 같음). `hx-history="false"` 가 있으면 되돌릴 사본이 없다(꼴 ⑪ · 백스톱 SH1).
- *재탭 ②*: 포착 단계 document 리스너라 링크 위 htmx 부스트 리스너보다 먼저 돈다 — 요청 0 · 기록 무변. 조건은 «고른 탭 · 그 href 의 경로+쿼리 = 지금 주소 · 진행 중 복원 · 문서 이동 없음» 이고, 진행 중인 것이 부스트면 그 부스트를 거두고 맨 위로 간다(화면 상태 유지). 초점은 누른 탭에 그대로 둔다.
- *실패 길*: 부스트 연결 실패 → 그 주소를 문서로 · 복원 연결 실패 · 409 · 그 밖 실패 → 지금 주소를 새로 엶 — 셋 다 문서 떠남 중이면 하지 않는다. 실패 표시를 더 친절하게 하려면 명세가 승인한 UI JS 가 같은 이벤트를 듣는다.
- *켜짐 조건*: body 표지가 없으면 아무 리스너도 걸지 않는다 — 표지를 걷은 셸에 이 파일 줄이 남아도 문서 이동 셸과 같다.
- 이 파일은 명세가 승인하는 UI 기능 JS 가 아니라 지속 셸의 일부다(root 소유) — 백스톱은 내용을 보지 않고 discipline 감수가 «위 글과 같음» 을 본다. 같은 동작을 기능 JS 로 다시 만들지 않는다.

- 제품 선언이 있으면 own 제품 셸(`root_<제품>_view.html`)도 같은 꼴이고 표지는 `data-root-shell="root_<제품>_view@{{ root_state.shell_rev }}"` 다. id 는 모든 셸이 같다 — 다른 셸끼리는 표지가 달라 처리기가 전체 이동으로 보낸다.
- **셸 전환은 기능 슬라이스다**(문서 이동 셸 → 지속 셸은 동작이 바뀐다 — 슬라이스 0 · 리팩토링 모드로 하지 않는다) · **표지는 마지막 슬라이스에 단다**: 앞 슬라이스(문서 이동 셸 그대로)가 CSS 겹침 해소 · 기능 JS 수명 이관(implementation-javascript §3 «지속 셸의 수명» — `root:leave` 알림은 문서 이동 셸에서도 무해해 앞 슬라이스에 넣는다) · root 코드(`shell_rev` · `RootTabState.key` · 처리기 · `write_tab` 처분 옮김 · `root_shell.js` 파일 · 틀 CSS 상태를 class 로)를 먼저 하고, 마지막 슬라이스가 셸 꼴 · 공유 머리 · `?v=` · 표지 · 그 제품 페이지(사슬 · include 포함)의 `{% block head %}` · `{% block scripts %}` · 본문 안 실행 태그 걷기 · body 자료를 `<main>` 안으로 옮기기 · root 브라우저 시험을 한다.
- **앱과 다른 점**(웹 한계 · 지속 셸이 택한 미지원 범위 — 막대 유지 · 재탭 ② · 탭 안 중첩 이동은 앱과 같다):
  - 탭별 화면 상태 · 스크롤을 기억하지 않는다 — 탭마다 마지막 주소만 기억하고 서버가 다시 그린다(맨 위).
  - ‹뒤로› 순서는 브라우저 기록 하나다 — 지나온 순서대로 탭을 넘나든다(막대를 다시 그리지 않는 것만 앱과 같다).
  - 재탭 ①(중첩 화면에서 같은 탭)은 첫 화면으로의 push 다 — 기록에 중첩 화면이 남는다.
  - 첫 반응은 서버 왕복 뒤다 — 누른 탭에 즉시 눌림 표시(`htmx-request`)만 주고 고른 탭 상태를 응답 전에 바꾸지 않는다.
  - 본문 교체를 넘어 살아야 하는 전역 알림(토스트) 자리가 셸에 없다(꼴 ⑫) — 알림은 본문 안에서 그 화면과 함께 사라진다.
  - ‹뒤로›로 돌아간 화면은 서버가 다시 그린다 — 입력 글 · 펼침 · 기능 JS 상태가 없다(기능이 입력을 지켜야 하면 그 기능의 명세가 정한다).
  - 화면 읽기 프로그램에 «새 화면» 알림이 없다(본문만 바뀜) — 명세가 필요하면 live 영역을 정한다.
- **지속 셸 후보 표지 셋**: `<body>` 의 `data-root-shell` · `<nav>` 의 `hx-boost` · `<main>` 의 `hx-history-elt`(`data-hx-*` 별칭 포함). 표준 셸 파일에 하나라도 있으면 지속 셸 후보로 보고 백스톱 SH2 가 나머지 꼴을 모두 본다 — 일부만 있으면 blocker(런타임은 판별이 서지 않아 모든 이동이 전체 이동으로 내려앉는다). 표준 셸 밖 템플릿(옛 `base/base.html` 등)에는 표지를 달지 않는다(SH1).
- **되돌리기**: 셸의 후보 표지 셋을 모두 걷으면 문서 이동 셸이다 — `root_shell.js` 줄도 함께 걷는다(남아도 body 표지가 없으면 그 파일은 아무 리스너도 걸지 않는다). 셸 방식 바꾸기는 G1 결정이다.

탭 href는 RootVM이 만든다 — context processor `root_context(request)`가 `request.session`과 현재 BC(`request.resolver_match.namespaces[0]`)를 RootVM에 넘기고, RootVM이 root의 탭 표(BC → 탭)로 탭마다 `href`·`is_current`를 채운다: 현재 탭은 그 탭 첫 화면 href, 다른 탭은 세션 `root.tab_last`의 마지막 경로(없으면 첫 화면 — §3). 탭 기록은 `RootRequestHandler` 가 응답 뒤 세션 저장 바로 앞에서 적는다(아래) — BC는 탭 기록을 모른다(architecture-state §10 "거의 빈 VM"). 지속 셸이면 RootState 는 `shell_rev`(머리 판 — `root_initializer.shell_rev()` 가 시동 때 정한 값)를, RootTabState 는 `key` 를 함께 싣는다(§3 «지속 셸이면»).

- **top-level redirect(게이트)의 자리** — 요청 수명 handler `RootRequestHandler`(미들웨어 — `MIDDLEWARE` 등록은 G0 점검)의 `process_view(request, view_func, view_args, view_kwargs)`다. **view 모듈이 `web.`으로 시작할 때만** 게이트·세션 신원 이월·탭 기록(§3)을 한다 — 같은 프로세스 API 호출(§4)이 닿는 백엔드 view(모듈이 `web.` 밖)에는 아무것도 하지 않으므로 middleware → RootVM → UseCase → Client → middleware 재진입이 끊긴다(테스트 `Client`도 미들웨어를 그대로 지난다). 게이트 여부는 root_vm이 UseCase를 직접 호출해 얻는다(architecture-state §10 — UseCase에 `request`를 넘기지 않는다). 신원 contextvar는 `process_view`에서 set하고 그 토큰을 `request`에 두었다가 `__call__`의 응답 뒤 reset한다. 지속 셸의 부스트 · 복원 요청은 아래 표의 계약이다:

| 요청 \ 응답 | 같은 셸 · 같은 판 200 | 3xx(게이트 · 로그인 · redirect) | 4xx · 5xx | 200 이지만 다른 셸 · 셸 없음 · 판 다름 · `<main>` 틀 없음 · html 아님 · 스트리밍 · 압축 |
|---|---|---|---|---|
| 문서 GET | 그대로 | 그대로 | 그대로 | 그대로 |
| 조각(`HX-Request`만) | 그대로 | 200 + `HX-Redirect: <Location>`(원 응답 고쳐 씀 — 쿠키 보존) | 그대로(htmx 는 교체 안 함) | 그대로 |
| 부스트(`HX-Boosted`) | `HX-Retarget: #root-content` · `HX-Reswap: <BOOST_SWAP>` · `HX-Reselect: #root-content > *` · 같은 주소면 `HX-Replace-Url` · `no-store` · 탭 기록(이동 번호 조건) | 200 + `HX-Redirect: <Location>` | 원 상태 + `HX-Redirect: <요청 주소>` | 원 상태 + `HX-Redirect: <요청 주소>` |
| 복원(`HX-History-Restore-Request`) | 그대로 + `no-store` · 탭 기록(이동 번호 조건) | **409**(Location 지움) | **409**(4xx) · **5xx 는 그 상태 그대로**(Django 는 5xx 응답의 세션을 저장하지 않는다 — 409 로 바꾸면 그것을 비켜 간다 · `root_shell.js` 는 상태와 무관하게 새로 엶) | **409** |
| **모든 web view GET 응답**(위 넷 전부) | `Vary: HX-Request` 를 더함 | 〃 | 〃 | 〃 |

- **판별(`_same_shell`)** — 실제 시작 태그로: 요청 머리 `X-Root-Shell` 이 있고 · 응답 200 · 스트리밍 아님 · `Content-Encoding` 없음 · **미디어 형식이 정확히 `text/html`**(`;` 앞을 소문자로 — `text/htmlx` 는 아님) 이고 · 응답을 `html.parser.HTMLParser` 로 읽어 **첫 `<body>` 시작 태그의 `data-root-shell` 값 = 요청 머리 값** · 그 뒤 **첫 `<main>` 시작 태그가 `id="root-content"` 이고 `hx-history-elt` 또는 `data-hx-history-elt` 를 가짐**일 때만. 주석 · `<script>` · `<style>` 본문 안 글자는 시작 태그가 아니다. **같은 속성이 둘이면 첫 값**(브라우저와 같음 — `dict(attrs)` 의 마지막 값이 아님). **첫 `<main>` 앞에 `<textarea>` 시작 태그가 있으면 거절**(파이썬 판에 따라 그 안 글자를 태그로 읽을 수 있다 — 셸 꼴에는 그 자리에 `textarea` 가 없다). 제목은 Django 자동 이스케이프라 태그 글자가 생기지 않는다(`|safe` 제목은 한계). 본문 전체를 문자열로 푼 뒤 파싱은 첫 `<main>` 에서 멈춘다(푸는 비용은 본문 크기만큼). 주석 속 표지(`<!-- data-root-shell="…" --><body>셸 없는 화면</body>`)는 body 표지 없음 · `<main>` 없음으로 전체 이동이다.
- **캐시 분리**: web view(`process_view` 가 web 으로 본 요청)의 GET 응답에는 **모두** `Vary: HX-Request`. 처리기가 HX 머리에 따라 바꾼 응답(부스트 · 복원 · 전체 이동 변환)은 `Cache-Control: no-store` 도. 남는 틈: URL 해석 단계 404(view 없음)의 문서 응답은 Vary 가 없다 — Django 기본 404 는 신선도가 없어 캐시되지 않는다.
- 같은 주소 재탭(진행 중 이동이 있어 재탭 ② 갈래를 타지 않은 경우 · 같은 주소 화면 안 링크): `HX-Current-URL` 경로+쿼리 == 요청 경로+쿼리 → `HX-Replace-Url`(브라우저 기본 링크 이동과 같은 기록 대체).
- 부스트 · 복원 갈래는 web view 여부와 무관하게 돈다(URL 해석 404 · 백엔드 주소로 가는 부스트도 전체 이동으로 내려앉게) · `Vary` · 탭 기록은 web view 에만. 전체 이동 변환은 GET 을 한 번 더 보낸다(XHR 한 번 + 문서 한 번) — 드문 길(오류 · 다른 셸 · 게이트 · 배포 직후)에만이고 GET 은 쓰기를 하지 않는다(implementation-htmx §4).
- BC 는 부스트 · 복원을 모른다 — 페이지 view 는 늘 전체 문서를 돌려주고 `HX-Request` 로 가르지 않는다(implementation-htmx §7).

**탭 기록 — 세션 저장 직전 한 자리**(두 셸 공통): 기준은 «문서 이동 셸보다 나빠지지 않음» 이다 — 늦게 끝난 옛 요청(브라우저는 버렸지만 서버는 끝까지 돈다)이 시작 때 읽은 세션 사본을 저장해 새 기록을 되돌리는 경합은 문서 이동 셸에도 있고(요청마다 저장하는 설정이면 늘), 그 위에서 할 수 있는 만큼 줄인다. 이 요청이 탭 기록을 바꾸려는 의도는 적힌 순서대로 쓰기 목록(`request.META[TAB_WRITES_META]`) 하나에 모은다 — ① **자기 탭 기록**: `process_view` 가 게이트를 지난 web 페이지 GET(문서 GET · 부스트 · 복원)에 «(탭, 경로)» 를 넣는다. 저장된 세션이 없는 요청(새 익명 · 만료 쿠키)은 같은 기록을 view 앞 사본에도 바로 적는다(다툴 저장 값이 없다 — 그 요청의 `flush()` 가 함께 지우고, 다른 탭을 넣었다 지우면 그 탭만 빠진다) ② **root 처분**: root 의 다른 코드가 이 요청에서 다른 탭 기록을 고치거나(검증된 복귀 주소) 지워야 하면 `write_tab(request, 탭, 경로 | None)` 을 부른다 — 세션 사본에도 바로 반영해(이 요청의 화면이 그 값을 읽음) 목록에 «처분» 으로 넣는다. 그 탭이 사본에도 이 요청의 쓰기 목록에도 없을 때의 지움은 빈 동작이라 넣지 않는다(목록에만 있는 자기 탭 기록 뒤의 지움은 넣는다 — 문서 이동 셸에서는 그 기록이 사본에 있어 뒤의 지움이 지웠다). `write_tab` 은 `_record_page` 앞에서만 부른다(view 앞 처분 · `__call__` 의 `get_response` 뒤 응답 쪽 처분 모두 — 뒤에 부르면 목록 밖이다). `root.tab_last` · `root.nav_seq` 를 세션에 쓰는 코드는 `write_tab` · `process_view`(키 없는 세션의 view 앞 기록) · `_record_page` 셋뿐이다(그 밖에서 직접 쓰면 아래 합침이 그 값을 모른다).

실제 저장 값은 `__call__` 끝 `_record_page` 한 자리에서 정한다(그 뒤 세션 저장까지는 `SessionMiddleware` 와 처리기 사이 미들웨어의 응답 처리뿐 — ms). 그 자리에서 세션 **저장소**를 다시 읽어(`SessionStore(session_key)` — 이 요청의 사본이 아님) 최신 `root.nav_seq` · `root.tab_last` 를 얻고, 쓰기 목록을 적힌 순서대로 그 위에 다시 놓는다 — 우선순위는 저장소 최신 값 < 이 요청의 쓰기(나중 것이 이김) · 이 요청이 건드리지 않은 탭은 최신 값 그대로 · **사본 통째 덮기는 하지 않는다**(낡은 사본 경합이 되살아난다). 자기 탭 기록은 문서 GET 이면 늘, 부스트 · 복원이면 응답이 같은 셸 200 이고 요청 머리 `X-Root-Nav` 가 최신 번호보다 클 때만 놓는다(늦은 이동은 건너뜀 — 놓은 부스트 · 복원은 그 번호를 쓰고, 문서 GET 은 번호를 지워 순서를 새로 시작한다). root 처분은 늦은 이동이어도 늘 놓는다(이동 순서가 아니라 이 요청이 확인한 사실의 판정이다). 놓은 것이 없는 늦은 이동은 쓰지 않되, 이 요청의 세션 사본이 어차피 저장되면(`SESSION_SAVE_EVERY_REQUEST` 또는 다른 코드가 켠 `request.session.modified`) 최신 값을 사본에 옮겨 둔다 — 저장될 옛 사본이 새 기록을 되돌리지 않게. 빈 값은 지운다(빈 기록 · 번호 0 으로 빈 세션을 채워 새 세션을 만들지 않게). 쓰기 목록이 빈 요청(탭 기록과 무관한 조각 · POST · 백엔드 view)은 저장소를 읽지 않는다.

**세션 키 없음 · 세션 종료 지킴**: «끝냄» 을 사본의 바뀜 표시 · 빈 내용으로 추론하지 않고 응답 때 세션 키로만 가른다 — 키가 없으면 다시 놓지 않고 저장소도 읽지 않는다. 키가 없는 길은 둘뿐이다: 저장된 세션 없이 시작해 그대로인 요청(기록은 이미 view 앞 사본에 있다 — 만료 쿠키로 온 요청도 이 갈래다) · 저장소에서 읽은 세션을 이 요청이 `flush()`(`logout()` 안) · 빈 세션 객체 교체로 끝낸 요청(다시 놓으면 끝낸 세션이 새 세션으로 되살아난다). 키는 있는데 다시 읽은 저장소에 그 세션이 없으면(다른 요청 · 백엔드가 끝냄) 쓰지도 옮기지도 않는다. 응답의 세션 쿠키 지움은 표식이 아니다(키가 남으면 바깥 `SessionMiddleware` 가 다시 저장하고 쿠키를 다시 단다 — 다시 놓는다). `flush()` 뒤 새 키로 갈아탄 요청(`login()` 의 `cycle_key()` 등)은 끝낸 것이 아니다 — 그 새 세션의 저장소 값 위에 놓는다. 실제 저장은 바깥 `SessionMiddleware` 가 한다(modified 또는 요청마다 저장 · 5xx 는 저장 안 함) — 처리기는 저장을 일으키지도 막지도 않는다. 남는 틈(다시 읽기와 저장 사이 · 문서 GET 대 그보다 늦게 끝난 부스트 · 조각 · POST 의 늦은 사본 저장 · 서명 쿠키 세션 엔진 · 같은 세션의 다른 키)은 문서 이동 셸과 같은 수준이다 — 세션 엔진 · 설정은 G0 이 host 상태에 적는다. 탭 기록 쓰기가 있는 요청(탭에 속한 페이지 요청 · root 처분이 있는 요청)마다 저장소를 한 번 더 읽는다(DB 세션이면 SELECT 한 번 — 알려진 대가). 이동 번호는 문서 안에서 줄지 않는 시계라 같은 세션의 브라우저 탭 둘이 섞이면 «나중에 누른 쪽이 이김» 으로 정리된다.

handler(문서 이동 셸에도 같다 — 부스트 · 복원이 오지 않을 뿐):

```python
# root/handler/root_request_handler.py — 요청 수명 handler(게이트 · 신원 이월 · 3xx 변환의 쿠키 보존 · 캐시 분리 · 탭 기록 · 지속 셸 갈래)
# import 줄은 적지 않는다 — 새로 쓰는 이름: dataclass · HTMLParser · import_module ·
# SplitResult · urlsplit · SessionBase · patch_cache_control · patch_vary_headers

SESSION_TOKEN_META: str = "web.root.session_token"  # process_view 가 둔 contextvar 토큰의 자리
TAB_WRITES_META: str = "web.root.tab_writes"  # 이 요청의 탭 기록 쓰기(적힌 순서) — 실제 저장 값은 __call__ 끝 한 자리(_record_page)
SHELL_HEADER: str = "X-Root-Shell"  # root_shell.js 가 부스트 · 복원 요청에 싣는 그 문서의 셸 표지(<셸 stem>@<머리 판>)
NAV_HEADER: str = "X-Root-Nav"  # root_shell.js 가 싣는 이동 번호(한 문서 안에서 늘 커진다)
NAV_SEQ_KEY: str = "root.nav_seq"  # 세션 — 탭 기록을 적은 마지막 부스트 · 복원의 이동 번호(문서 GET 이 지운다)
HISTORY_ELT_ATTRS: frozenset[str] = frozenset({"hx-history-elt", "data-hx-history-elt"})  # htmx 와 같은 별칭 계약
BOOST_SWAP: str = "innerHTML show:none"  # 부스트 교체 방식 — 맨 위 보이기는 root_shell.js 가 교체 직후에(htmx 정착 스크롤은 끔 —
#                                         철회 뒤 늦게 도는 스크롤이 남지 않게) · 정착 시간을 바꿀 때는 이 상수만 바꾼다


@dataclass(frozen=True, slots=True, kw_only=True)
class _TabWrite:
    tab: str
    path: str | None  # None = 그 탭 기록을 지움
    own: bool  # 이 페이지 요청의 자기 탭 기록(받아들인 이동일 때만 놓음) — 거짓이면 root 처분(늘 놓음 · 사본에도 목록에도 없는 탭의 지움은 목록에 없음)


class RootRequestHandler:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self._get_response: Callable[[HttpRequest], HttpResponse] = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        token: object = None
        try:
            response: HttpResponse = self._get_response(request)  # URL 해석 → process_view → view
        finally:
            token = request.META.pop(SESSION_TOKEN_META, None)
            if isinstance(token, Token):
                SESSION_KEY.reset(token)
        restoring: bool = request.headers.get("HX-History-Restore-Request") == "true"
        boosted: bool = not restoring and request.headers.get("HX-Boosted") == "true"
        accepted: bool = (restoring or boosted) and _same_shell(request, response)  # 같은 셸 · 같은 판으로 받아들일 응답
        if restoring:
            response = _restored(response, accepted)  # 복원 요청은 HX-Redirect 를 읽지 않는다 — 먼저 가른다
        elif boosted:
            response = _boosted(request, response, accepted)  # 탭 이동 · 화면 안 부스트 링크
        elif request.headers.get("HX-Request") == "true" and 300 <= response.status_code < 400 and "Location" in response:
            response = _full_navigation(response, response["Location"])  # 조각 요청의 3xx(로그인 포함) → 전체 이동
        if isinstance(token, Token) and request.method == "GET":
            patch_vary_headers(response, ("HX-Request",))  # web view 응답 전부 — 캐시된 문서 응답이 부스트 · 복원 XHR 에 쓰이지 않게
        # 응답 쪽 root 처분(write_tab)은 여기, _record_page 앞에 둔다 — 뒤에 두면 쓰기 목록 밖이다
        _record_page(request, response, accepted)  # 탭 기록 — 세션 저장(바깥 SessionMiddleware) 바로 앞 한 자리
        return response

    def process_view(self, request, view_func, view_args, view_kwargs) -> HttpResponse | None:
        if not view_func.__module__.startswith("web."):
            return None  # 백엔드 view(같은 프로세스 API 호출 포함) — 아무것도 하지 않는다(재진입 차단)
        session_key: str | None = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
        request.META[SESSION_TOKEN_META] = SESSION_KEY.set(session_key)  # 세션 신원 이월(§4)
        gate_href: str | None = RootVM(session=request.session).gate_href(request.path)
        if gate_href is not None and request.path != gate_href:
            return redirect(gate_href)  # 조각 · 부스트면 __call__ 이 HX-Redirect 로, 복원이면 409 로 바꾼다 · 탭 기록 없음
        if request.method == "GET" and _is_page_request(request):
            tab: str | None = _tab_of(request)
            if tab is not None:
                path: str = request.get_full_path()
                _tab_writes(request).append(_TabWrite(tab=tab, path=path, own=True))  # 저장된 세션이면 놓는 것은 응답 뒤(_record_page)
                if not _has_stored_session(request.session):
                    _apply_to_copy(request.session, tab, path)  # 새 익명 · 만료 쿠키 — 다툴 저장 값이 없어 문서 이동 셸처럼 view 앞 사본에
        return None


def write_tab(request: HttpRequest, tab: str, path: str | None) -> None:
    """root 처분 — 이 요청에서 탭 기록을 고치거나(path) 지운다(None). 세션 사본에 바로 반영하고(이 요청의 화면이 읽음)
    쓰기 목록에 남긴다 — _record_page 가 저장소 최신 값 위에 다시 놓는다(늦은 이동이어도 · 사본 통째 덮기 없음).
    _record_page 앞에서만 부른다(view 앞 · __call__ 의 get_response 뒤 응답 쪽 처분 모두 — 뒤에 부르면 목록 밖이다)."""
    stored: object = request.session.get(TAB_LAST_KEY)
    writes: list[_TabWrite] = _tab_writes(request)
    if path is None and not (isinstance(stored, dict) and tab in stored) and not any(write.tab == tab for write in writes):
        return  # 사본에도 이 요청의 쓰기 목록에도 없는 탭의 지움 — 빈 동작이라 처분으로 남기지 않는다(문서 이동 셸의 pop 도 저장 표시를
        #         세우지 않았다). 목록에만 있는 자기 탭 기록(저장된 세션)은 문서 이동 셸에서 사본에 있었다 — 그 뒤 지움은 남긴다
    _apply_to_copy(request.session, tab, path)
    writes.append(_TabWrite(tab=tab, path=path, own=False))


def _apply_to_copy(session: SessionBase, tab: str, path: str | None) -> None:
    """이 요청의 세션 사본에 탭 기록 하나를 놓는다(None = 지움)."""
    stored: object = session.get(TAB_LAST_KEY)
    last_paths: dict[str, str] = dict(stored) if isinstance(stored, dict) else {}
    if path is None:
        last_paths.pop(tab, None)
    else:
        last_paths[tab] = path
    _put(session, TAB_LAST_KEY, last_paths)


def _has_stored_session(session: SessionBase) -> bool:
    """이 요청이 저장소에서 읽은 세션이 있는가 — 사본을 먼저 읽는다(만료 · 없는 세션 쿠키면 읽는 동안 키가 빈다).
    서명 쿠키 엔진은 키가 쿠키 글자 그대로라 늘 참이다(그 엔진의 저장소 = 이 요청의 쿠키 — 문서 이동 셸과 같은 수준)."""
    session.keys()
    return session.session_key is not None


def _tab_writes(request: HttpRequest) -> list[_TabWrite]:
    found: object = request.META.get(TAB_WRITES_META)
    if isinstance(found, list):
        return found
    writes: list[_TabWrite] = []
    request.META[TAB_WRITES_META] = writes
    return writes


def _is_page_request(request: HttpRequest) -> bool:
    """문서 GET · 부스트 · 복원 — 조각 요청(HX-Request 만)은 페이지 요청이 아니다."""
    return (request.headers.get("HX-Request") != "true" or request.headers.get("HX-Boosted") == "true"
            or request.headers.get("HX-History-Restore-Request") == "true")


def _tab_of(request: HttpRequest) -> str | None:
    namespaces: list[str] = request.resolver_match.namespaces if request.resolver_match else []
    return TAB_OF_BC.get(namespaces[0]) if namespaces else None


def _boosted(request: HttpRequest, response: HttpResponse, accepted: bool) -> HttpResponse:
    if 300 <= response.status_code < 400 and "Location" in response:
        return _full_navigation(response, response["Location"])  # 게이트 · 로그인 · view 의 redirect
    if not accepted:
        return _full_navigation(response, request.get_full_path())  # 오류 · 다른 셸 · 셸 없는 화면 · 머리 판 바뀜
    response["HX-Retarget"] = "#root-content"
    response["HX-Reswap"] = BOOST_SWAP
    response["HX-Reselect"] = "#root-content > *"
    current: SplitResult = urlsplit(request.headers.get("HX-Current-URL", ""))
    if current.path + (f"?{current.query}" if current.query else "") == request.get_full_path():
        response["HX-Replace-Url"] = request.get_full_path()  # 같은 주소 = 기록 대체(브라우저 기본 링크 이동과 같게)
    return _uncached(response)


def _restored(response: HttpResponse, accepted: bool) -> HttpResponse:
    if not accepted and response.status_code < 500:  # 5xx 는 그대로 — Django 는 5xx 응답의 세션을 저장하지 않는다(409 로 바꾸면 그것을 비켜 간다)
        response.status_code = 409  # 복원 요청은 HX-Redirect 를 읽지 않는다 — root_shell.js 가 문서를 새로 연다(상태 무관)
        if response.has_header("Location"):
            del response["Location"]
    return _uncached(response)


def _record_page(request: HttpRequest, response: HttpResponse, accepted: bool) -> None:
    """탭 기록 — 이 요청의 탭 기록 쓰기를 세션 저장소의 최신 값 위에 적힌 순서대로 다시 놓아 이 요청의 세션 사본에 둔다.
    우선순위: 저장소 최신 값 < 이 요청의 쓰기(나중 것이 이김) · 자기 탭은 받아들인 이동만 · root 처분은 늘.
    응답 때 세션 키가 없으면 다시 놓지 않는다 — 사본의 modified · 빈 내용으로 «끝냄» 을 추론하지 않는다.
    남는 틈(다시 읽기와 세션 저장 사이 · 서명 쿠키 엔진 · 다른 세션 키)은 문서 이동 셸과 같은 수준이다."""
    found: object = request.META.pop(TAB_WRITES_META, None)
    writes: list[_TabWrite] = found if isinstance(found, list) else []
    key: str | None = request.session.session_key
    if not writes or key is None:
        # 키가 없는 길은 둘뿐 — ① 저장된 세션 없이 시작해 그대로(새 익명 · 만료 쿠키): 쓰기는 이미 view 앞 · 그 자리에서 사본에
        # 적힌 순서 그대로다(문서 이동 셸과 같음 — 그 요청의 flush 는 함께 지웠다) ② 저장소에서 읽은 세션을 이 요청이 끝냄(flush() ·
        # logout() · 빈 세션 객체로 교체 — 살아 있는 키를 None 으로 만드는 길은 이것뿐): 다시 놓으면 끝낸 세션이 새 세션으로 되살아난다
        return
    stored: tuple[int, dict[str, str]] | None = _stored_tabs(key)
    if stored is None:
        return  # 저장소에 이 세션이 없다(다른 요청 · 백엔드가 끝냄) — 되살리지 않는다
    stored_seq: int = stored[0]
    last_paths: dict[str, str] = dict(stored[1])
    navigating: bool = request.headers.get("HX-Request") == "true"  # 부스트 · 복원(문서 GET 이 아님)
    seq: int = _nav_seq(request)
    own_ok: bool = not navigating or (accepted and seq > stored_seq)  # 자기 탭 기록을 놓을 이동인가(늦은 이동은 아님)
    placed: bool = False
    own_placed: bool = False
    write: _TabWrite
    for write in writes:
        if write.own and not own_ok:
            continue  # 늦은 이동의 자기 탭 기록 — 놓지 않는다(root 처분은 그대로 놓는다)
        if write.path is None:
            last_paths.pop(write.tab, None)
        else:
            last_paths[write.tab] = write.path
        placed = True
        own_placed = own_placed or write.own
    if not placed and not (settings.SESSION_SAVE_EVERY_REQUEST or request.session.modified):
        return  # 놓은 것이 없고 저장도 일어나지 않는다 — 세션을 건드리지 않는다
    _put(request.session, TAB_LAST_KEY, last_paths)  # 새 dict 대입 — 제자리 변경은 세션이 저장하지 않는다
    if own_placed:
        _put(request.session, NAV_SEQ_KEY, seq if navigating else 0)  # 문서 GET 은 번호를 지워 순서를 새로 시작(시계 되돌림이 풀림)
    else:
        _put(request.session, NAV_SEQ_KEY, stored_seq)  # 이 요청의 이동이 없거나 늦음 — 저장될 사본이 최신 번호를 싣게


def _put(session: SessionBase, key: str, value: object) -> None:
    """빈 값은 지운다 — 빈 기록 · 번호 0 으로 빈 세션을 채워 새 세션을 만들지 않게(없는 키를 지우면 modified 도 켜지지 않는다)."""
    if value:
        session[key] = value
    else:
        session.pop(key, None)


def _stored_tabs(key: str) -> tuple[int, dict[str, str]] | None:
    """세션 저장소에 지금 적힌 이동 번호 · 탭 기록 — 이 요청이 시작할 때 읽은 사본이 아니라 저장소에서 다시 읽는다.
    저장소에 이 세션이 없으면 None · 서명 쿠키 엔진은 저장소가 이 요청의 쿠키라 다시 읽어도 같은 사본이다."""
    fresh: SessionBase = import_module(settings.SESSION_ENGINE).SessionStore(session_key=key)
    seq: object = fresh.get(NAV_SEQ_KEY)
    last: object = fresh.get(TAB_LAST_KEY)
    if fresh.session_key is None:
        return None  # db · cache · file 엔진은 읽다가 그 세션을 못 찾으면 키를 비운다
    return (seq if isinstance(seq, int) else 0), (dict(last) if isinstance(last, dict) else {})


class _ProbeDone(Exception):
    """첫 <main> 시작 태그를 읽었다 — 나머지 본문은 읽지 않는다."""


class _ShellProbe(HTMLParser):
    """응답의 실제 시작 태그만 본다 — 주석 · script · style 본문 안의 글자는 태그가 아니다. 같은 속성이 둘이면 첫 값."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.body_mark: str | None = None
        self.content_root: bool = False
        self.raw_text: bool = False  # 첫 <main> 앞 <textarea> — 그 안 글자를 태그로 읽는 판이 있어 판별을 거절한다

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        names: dict[str, str | None] = {}
        for name, value in attrs:
            names.setdefault(name, value)  # 첫 값(브라우저와 같음)
        if tag == "textarea":
            self.raw_text = True
        elif tag == "body" and self.body_mark is None:
            self.body_mark = names.get("data-root-shell") or ""
        elif tag == "main" and self.body_mark is not None:
            self.content_root = names.get("id") == "root-content" and not HISTORY_ELT_ATTRS.isdisjoint(names)
            raise _ProbeDone


def _same_shell(request: HttpRequest, response: HttpResponse) -> bool:
    """응답이 요청한 문서와 같은 지속 셸 · 같은 머리 판으로 그린 온전한 페이지인가 — 실제 <body> 표지와 본문 틀로 가른다."""
    mark: str = request.headers.get(SHELL_HEADER, "")
    media_type: str = response.get("Content-Type", "").split(";")[0].strip().lower()
    if (not mark or response.status_code != 200 or response.streaming or response.has_header("Content-Encoding")
            or media_type != "text/html"):
        return False
    probe: _ShellProbe = _ShellProbe()
    try:
        probe.feed(response.content.decode(response.charset or "utf-8", "replace"))
        probe.close()
    except _ProbeDone:
        pass
    return not probe.raw_text and probe.body_mark == mark and probe.content_root


def _nav_seq(request: HttpRequest) -> int:
    raw: str = request.headers.get(NAV_HEADER, "")
    return int(raw) if raw.isdigit() else 0


def _full_navigation(response: HttpResponse, location: str) -> HttpResponse:
    """원 응답을 «전체 이동» 응답으로 고친다 — 쿠키 · 머리를 버리지 않는다(htmx 는 HX-Redirect 를 상태와 무관하게 먼저 읽는다)."""
    if 300 <= response.status_code < 400:
        response.status_code = 200  # 3xx 는 브라우저 XHR 이 스스로 따라가므로 200 으로
        del response["Location"]
    response["HX-Redirect"] = location
    return _uncached(response)


def _uncached(response: HttpResponse) -> HttpResponse:
    patch_vary_headers(response, ("HX-Request",))
    patch_cache_control(response, no_store=True)  # HX-Boosted · HX-Current-URL · 셸 표지 · 이동 번호에 따라 달라지는 응답
    return response
```

- 데코레이터(`@login_required`)는 `functools.wraps`로 `__module__`을 보존하므로 판정이 그대로 선다. `request.session`을 쓰므로 `MIDDLEWARE`에서 `SessionMiddleware`·`AuthenticationMiddleware` 뒤에 둔다.
- `__call__`의 3xx 변환은 조각 view의 `@login_required`(미로그인 302)·게이트 redirect·view의 `redirect(…)`에 똑같이 걸린다 — 로그인 페이지가 조각 자리에 끼어들지 않고 전체 이동한다(§6). 조각 view의 `@login_required`는 그대로 둔다.
- 변환은 원 응답을 고쳐 쓴다 — view 가 단 쿠키 · 머리를 버리지 않는다.
- 지속 셸이 있으면 이 handler 보다 안쪽(`MIDDLEWARE` 에서 뒤)에 응답 본문을 바꾸는 미들웨어(GZip 등)를 두지 않는다 — 셸 판별이 응답의 시작 태그를 읽는다(G0 점검).
- web view 의 GET 응답에는 모두 `Vary: HX-Request` 를, 처리기가 HX 요청에 따라 바꾼 응답에는 `Cache-Control: no-store` 도 단다.
- 탭 기록은 `__call__` 끝 한 자리(`_record_page`)에서 세션 저장소를 다시 읽고 이 요청의 탭 기록 쓰기(자기 탭 · root 처분)를 적힌 순서대로 그 최신 값 위에 다시 놓는다(위 «탭 기록») — root 가 이 요청에서 탭 기록을 고치거나 지우는 처분은 `write_tab` 으로만 하고 `_record_page` 앞에서 부른다(응답 쪽 처분도 `__call__` 에서 `_record_page` 호출 전). 사본을 통째로 덮지 않는다.

- **전환**: 문서 이동 셸은 페이지 이동 전환을 두지 않는다(브라우저 기본 이동). 지속 셸은 본문 전환을 두지 않고(앱 탭 전환과 같음), 탭 막대 · 탭별 모습의 상태 변화만 CSS 전환으로 움직인다 — 막대 요소는 남으므로 그 상태는 고른 탭 class 를 `:has()` 로 읽어 정하고, 새로 놓이는 탭 링크 안의 움직임은 htmx 정착으로 이어진다 — 그래서 움직이는 상태 선택자는 BEM `--` class 로 쓰고 `aria-current` 는 접근성 값으로만 둔다(`--duration-*` · `--easing-*` 토큰 · `prefers-reduced-motion` 에서 끔). `transition` 목록에는 물리 속성(`padding-top` · `padding-bottom` 등)을 적는다 — WebKit 은 논리 축약 `padding-block` 의 전환을 그리지 않는다. 조각 교체 전환은 두 셸 모두 implementation-htmx §7의 `htmx-swapping`·`htmx-settling` 클래스 + 토큰이다 — router는 전환 연출을 갖지 않아 design_system을 참조하지 않는다(architecture-ui §6).
- Django 판 메모: 본문 표기(`path`·`reverse`·`redirect`·`app_name` 네임스페이스·미들웨어 판형)는 4.2~5.x에서 같다.

## §3. 탭 재탭 2단 동작 — 규약 §10-5 ④ 확정 (root_view 소유)

**확정(2026-06-12 사용자 — 규약 §10-5 ④): 현재 탭을 재탭하면 ① 탭 안 중첩 화면에 들어가 있으면 탭 첫 화면으로 복귀(스택 리셋) ② 이미 첫 화면이면 스크롤 최상단.** 다른 탭으로 가는 일반 탭 전환은 **그 탭의 마지막 위치를 복원**한다(재탭만 초기화한다). 전부 root(root_view·RootVM·RootRequestHandler)가 처리하고 **BC는 무관여**다 — 신호를 듣지도, 스크립트를 받지도, 탭 기록을 알지도 않는다(규약 §9-11).

**web에서의 메커니즘 — 탭 href를 둘로 가른다**: ⓐ `RootRequestHandler` 가 web 페이지 요청이 끝날 때(`__call__` 끝 — 세션 저장 바로 앞) 세션 저장소의 최신 기록 위에 그 탭 자리(`request.get_full_path()`)와 이 요청의 root 처분(`write_tab`)을 적힌 순서대로 놓는다(문서 GET · 지속 셸의 부스트 이동 · ‹뒤로›·‹앞으로› 복원 — 부스트 · 복원은 응답이 같은 셸이고 이동 번호가 클 때 · 조각 요청 제외 · 저장된 세션이 없는 요청은 view 앞 사본에 · 응답 때 세션 키가 없으면 쓰지 않음 · 탭 = 그 view의 URL 네임스페이스 첫 마디 = BC → root의 탭 표 — §2). ⓑ RootVM이 탭 href를 만든다 — **현재 탭은 그 탭 첫 화면 href**, **다른 탭은 세션의 마지막 경로**(없으면 첫 화면). 그래서 ① 현재 탭 중첩 화면(`/channels/ch-1/`)에서 탭을 누르면 첫 화면(`/channels/`)으로 돌아가고 ② 첫 화면에서 누르면 같은 주소로 새로 이동해 맨 위에서 다시 그린다(스크롤 복원은 뒤로·앞으로 이동과 새로고침에만 걸리고 링크 이동에는 걸리지 않는다 · 지속 셸은 앱 · dddart 와 같이 요청 없이 문서 스크롤만 맨 위로 — 화면 상태가 남는다 · `root_shell.js` · 진행 중 이동이 있으면 같은 주소 부스트로 앞 이동을 거둔다) ③ 다른 탭에서 이 탭을 누르면 마지막에 보던 주소(`/channels/ch-1/`)로 돌아온다:

```python
# root/scaffold/view_model/root_vm.py — root의 탭 표·탭 href
TAB_LAST_KEY: str = "root.tab_last"  # 세션 키 — 탭 → 마지막 경로
TAB_OF_BC: dict[str, str] = {"channel": "channel", "chat": "channel", "member": "my"}  # root의 탭 표: BC → 탭
TAB_LABELS: dict[str, str] = {"channel": "채널", "my": "내 정보"}


class RootVM:
    """거의 빈 VM — 탭·게이트 같은 web 전역 표시 상태만."""

    def __init__(self, session: MutableMapping[str, object]) -> None:
        self._session: MutableMapping[str, object] = session

    def build(self, current_bc: str | None) -> RootState:
        stored: object = self._session.get(TAB_LAST_KEY)
        last_paths: dict[str, str] = dict(stored) if isinstance(stored, dict) else {}
        current_tab: str | None = TAB_OF_BC.get(current_bc) if current_bc is not None else None
        first_hrefs: dict[str, str] = {
            "channel": ChannelNavigator.channel_summary_href(),
            "my": MemberNavigator.my_page_href(),
        }
        tabs: tuple[RootTabState, ...] = tuple(
            RootTabState(
                label=TAB_LABELS[tab],
                href=first_href if tab == current_tab else last_paths.get(tab, first_href),  # 재탭 = 첫 화면 · 전환 = 복원
                is_current=tab == current_tab,
            )
            for tab, first_href in first_hrefs.items()
        )
        return RootState(tabs=tabs)


def root_context(request: HttpRequest) -> dict[str, RootState]:
    """문서 셸에 RootState를 준다 — settings TEMPLATES context_processors 대상."""
    namespaces: list[str] = request.resolver_match.namespaces if request.resolver_match else []
    return {"root_state": RootVM(session=request.session).build(namespaces[0] if namespaces else None)}
```

탭 한 칸의 표시 상태는 `root/scaffold/state/root_tab_state.py` 의 `RootTabState`(`label` · `href` · `is_current`)이고 `RootState` 는 `root_state.py` 에 따로 둔다(한 파일 한 클래스 — 백스톱 NM3). **지속 셸이면** RootTabState 는 `key`, RootState 는 머리 판 `shell_rev` 를 더한다 — 문서 이동 셸의 RootVM · RootState 는 위 그대로 둔다:

```python
# root/scaffold/state/root_tab_state.py — 지속 셸이면 key 를 더한다
@dataclass(frozen=True, slots=True, kw_only=True)
class RootTabState:
    key: str  # 탭 표의 키 — 지속 셸 탭 링크 id · class 수식 재료
    label: str
    href: str
    is_current: bool
```

```python
# root/scaffold/state/root_state.py — 지속 셸이면 shell_rev 를 더한다
@dataclass(frozen=True, slots=True, kw_only=True)
class RootState:
    tabs: tuple[RootTabState, ...]
    shell_rev: str  # 지속 셸 머리 판 — <body data-root-shell="<셸 stem>@<판>"> 의 뒤쪽 · 머리 자산 주소의 ?v=
```

- RootVM 은 `RootTabState(key=tab, label=…, href=…, is_current=…)` 와 `return RootState(tabs=tabs, shell_rev=shell_rev())` 로 채운다(`from web.root.initializer.root_initializer import shell_rev` — 탭 href 규칙은 그대로).
- `shell_rev()` 는 `root/initializer/root_initializer.py` 의 함수다 — `RootInitializer.start()`(`WebConfig.ready()`)가 한 번 불러 값을 정하고(`functools.cache`), `RootVM.build` 는 그 값을 읽기만 한다(VM = 표시 상태만 · 요청 안 파일 I/O 없음):

```python
# root/initializer/root_initializer.py — 지속 셸이면 더하는 것
@functools.cache
def shell_rev() -> str:
    """지속 셸 머리 판 — 셸 템플릿 · design_system CSS · web/static CSS·JS 내용 해시 앞 12자(프로세스 상수 · 시동 때 한 번).
    배포가 머리 자산을 바꾸면 값이 바뀌어 ① 배포 전에 열린 문서의 부스트 · 복원은 전체 이동 ② 머리 자산 주소의 ?v= 가 바뀐다."""
    web_root: Path = Path(__file__).resolve().parents[2]  # web/root/initializer/root_initializer.py → web/
    files: list[Path] = sorted([*web_root.glob("root/scaffold/view/root*_view.html"),
                                *web_root.glob("design_system/**/*.css"),
                                *web_root.glob("static/**/*.css"), *web_root.glob("static/**/*.js")])
    chunks: list[bytes] = [path.relative_to(web_root).as_posix().encode() + b"\0" + path.read_bytes() for path in files]
    return hashlib.sha256(b"\0".join(chunks)).hexdigest()[:12]


class RootInitializer:
    def start(self) -> None:
        ...  # 기존 시동(시그널 연결 등)
        shell_rev()  # 지속 셸 머리 판을 시동 때 정한다(요청 안에서 파일을 읽지 않게)
```

- 프로세스 상수다(요청 사이 상태가 아님 · 워커마다 같은 파일이면 같은 값). 개발 서버는 CSS 만 바꾸면 재시작 전까지 옛 판이다(알려진 한계). 롤링 배포 창에서 옛 · 새 워커가 섞이면 판이 달라 전체 이동이 되풀이될 수 있다(배포 창 동안만).

```django
{# root_view.html 탭 — href는 RootVM이 고른 값(현재 탭 = 첫 화면 · 다른 탭 = 마지막 경로) #}
{# 지속 셸이면 탭 링크에 id root-tab-<탭 키> · class 수식 — §2 «지속 셸» #}
<a href="{{ tab.href }}"{% if tab.is_current %} aria-current="page"{% endif %}>{{ tab.label }}</a>
```

- **BC 화면의 전제(유일한 접점 — "아무것도 하지 않기")**: 화면 최상위에 별도 스크롤 컨테이너(높이 고정 + `overflow: auto` 래퍼)를 두지 않는다 — 문서 스크롤이 기본이라 새 이동이 맨 위에서 시작한다. 내부 스크롤 패널을 쓰는 화면은 그 패널만 재탭 스크롤톱이 무반응이 된다(의도된 트레이드오프 — BC에 결합을 만들지 않는 것이 우선). 지속 셸의 재탭 ② 는 요청 없이 문서 맨 위로(화면 상태 유지) · 부스트 이동은 교체 직후 `root_shell.js` 가 문서를 맨 위로 보낸다(htmx 정착 스크롤은 `show:none` 으로 끔).
- **탭 링크에 `hx-get`을 붙이지 않는다 — 탭 링크의 `hx-boost` 는 지속 셸의 탭 막대 `<nav>` 에 단다**(화면 안 같은 제품 링크는 implementation-htmx §9 · §2 «지속 셸» · 백스톱 SH1 · `data-hx-boost` 별칭도 같은 속성이다). 문서 이동 셸의 탭은 브라우저 이동이다. 지속 셸의 부스트 이동은 주소 쌓기를 htmx core 가 하고, 교체 자리 · 같은 주소의 기록 대체 · 탭 기록 · 실패의 전체 이동은 `RootRequestHandler` 가, 진행 중 이동 거두기 · 떠난 화면의 조각 요청 끊기 · 화면 밖 요청 요소(`body` 등)의 지연 교체 없앰 · 본문 맨 위 · 재탭 ②(요청 없이 맨 위로) · history state 보전은 `root_shell.js` 가 한다 — 같은 동작을 기능 JS 로 다시 만들지 않는다. 조각 요청(`hx-get`)은 주소 · 기록을 바꾸지 않으므로 탭 기록에 적히지 않는다.
- 세션 값은 JSON 직렬화 가능한 원시값이라 `root.tab_last`는 `{탭: 경로}` dict 하나다 — 키 대입만 변경으로 저장되므로 항상 새 dict를 대입한다(implementation-htmx §3).
- **재탭 신호 버스(과거 HaffHaff `scroll_to_top_notifier` — BC가 전역 신호를 listen)는 비채택**이다: 금지 채널의 재생산(architecture-state §8). web에서는 전역 JS 이벤트로 BC 스크립트에 재탭을 알리는 형태가 그 재생산이다.
- 상태바 탭 같은 기기 셸 동작은 web에는 해당 없음(브라우저가 소유한다). 2단 동작·전환 복원의 브라우저 확인(중첩 화면에서 탭 → 첫 화면 URL · 첫 화면 스크롤 뒤 탭 → 맨 위 · A 상세 → B → A 탭 → A 상세)은 골격 구현 시 1회. 지속 셸이면 root 브라우저 시험 하나와 root 처리기 시험 하나(implementation-test §4 «지속 셸의 root 시험»)가 이 확인을 남긴다.

## §4. api_client·DataSource 표기 — 실패 종류·세션 이월

**실패 종류**(safe_api_call 분기의 근거 — 계약 자체는 architecture-data §2 소유): in-process 호출이라 실패 종류가 셋이다:

| 종류 | 생기는 자리 | safe_api_call 분기 |
|---|---|---|
| 상태코드 실패 | 백엔드가 2xx 밖(4xx·5xx) 응답 — 바디에 서버 에러 봉투 | `ApiStatusError`(`.status_code`·`.body`) → 봉투면 `BadRequestResponse.from_json`, 아니면 `unknown` |
| 백엔드 미처리 예외 | `raise_request_exception=False`라 원시 예외가 아니라 500 응답으로 온다 | 상태코드 실패와 같은 갈래 |
| JSON 파싱·필드 | `response.json()`의 `ValueError` · `from_json`의 `KeyError`·`TypeError`·`ValueError` | `parse` |

타임아웃·연결 실패·인증서·취소 종류는 없다(같은 프로세스 호출) — `timeout` 분기를 만들지 않는다.

**api_client·세션 이월**:

```python
# common/network/api_client.py — in-process 백엔드 호출기 (BC·root를 모른다)
from contextvars import ContextVar

from django.conf import settings
from django.http import HttpResponse
from django.test import Client

from web.common.network.api_status_error import ApiStatusError

SESSION_KEY: ContextVar[str | None] = ContextVar("session_key", default=None)  # root_request_handler가 web view 요청마다 심는다


class ApiClient:
    """백엔드 API를 같은 프로세스에서 부른다 — 2xx면 JSON, 아니면 ApiStatusError."""

    def get(self, path: str) -> object:
        return self._send(self._client().get(path))

    def post(self, path: str, body: dict[str, object]) -> object:
        return self._send(self._client().post(path, data=body, content_type="application/json"))

    def _client(self) -> Client:
        client: Client = Client(raise_request_exception=False)  # 매 호출 생성 — 쿠키·세션이 요청 사이로 새지 않게
        session_key: str | None = SESSION_KEY.get()
        if session_key is not None:
            client.cookies[settings.SESSION_COOKIE_NAME] = session_key  # 세션 신원 이월 — None이면 익명 호출
        return client

    def _send(self, response: HttpResponse) -> object:
        is_json: bool = response.headers.get("Content-Type", "").startswith("application/json")
        if not 200 <= response.status_code < 300:
            raise ApiStatusError(status_code=response.status_code, body=response.json() if is_json else None)
        return response.json() if is_json else None
```

```python
# common/network/api_status_error.py — 상태코드 실패 (한 파일 한 클래스)
@dataclass(frozen=True, slots=True, kw_only=True)
class ApiStatusError(Exception):
    status_code: int
    body: object  # 응답 JSON — JSON이 아니면 None
```

- `django.test.Client`는 Django가 주는 유일한 완전 in-process HTTP 호출기다 — 네트워크를 타지 않으면서 URL 라우팅·미들웨어·인증을 지난다. `ALLOWED_HOSTS`에 `"testserver"`가 있어야 400이 아니다(G0 점검).
- **세션 이월은 쿠키 부착 같은 횡단 관심사에 한정한다** — 실패 정규화는 safe_api_call(단일 출구 — architecture-data §2)의 일이다. 정규화 지점이 둘이 되면 충돌한다. contextvar는 `RootRequestHandler.process_view`가 web view 요청에서만 심고 `__call__`이 응답 뒤 되돌린다(§2) — 이 호출이 닿는 백엔드 view에서는 handler가 아무것도 하지 않아 재진입이 없다. common은 BC·root를 모른다(콜백 주입 원칙 — discipline-houserules §6).
- CSRF는 여기 없다 — in-process 호출은 CSRF 검사 대상이 아니다(`enforce_csrf_checks=False` 기본). CSRF는 브라우저→web view 경계에서 한 번 검증된다(§6).

**DataSource** — 엔드포인트 정의(직반환 계약은 architecture-data §4 소유):

```python
# application/channel/infra_layer/data_source/channel_data_source.py
from urllib.parse import quote

from web.application.channel.domain_layer.channel.channel import Channel
from web.common.network.api_client import ApiClient
from web.common.util.json_field import json_field

CHANNELS_PATH: str = "/api/channels"  # 경로 근거: server-contract.json 경량본 (architecture-data §7)


class ChannelDataSource:
    def __init__(self, client: ApiClient) -> None:
        self._client: ApiClient = client

    def get_channels(self) -> list[Channel]:
        data: object = self._client.get(CHANNELS_PATH)
        return [Channel.from_json(item) for item in json_field(data, "channels", list)]  # 응답 모양이 다르면 TypeError·KeyError

    def get_channel(self, channel_id: str) -> Channel:
        return Channel.from_json(self._client.get(f"{CHANNELS_PATH}/{quote(channel_id)}"))

    def create_channel(self, channel: Channel) -> Channel:
        return Channel.from_json(self._client.post(CHANNELS_PATH, channel.to_json()))
```

- 반환은 도메인 엔티티 직반환(`Channel`·`list[Channel]`·`None`) — `HttpResponse`·dict를 Repo로 올리지 않는다. 실패는 raise로 두고 Repo의 `safe_api_call`이 Either로 정규화한다(architecture-data §2·§3).
- 백엔드 경로 리터럴의 유일 거처는 DataSource 모듈 상수다 — VM·view·템플릿에 백엔드 URL이 나타나면 위반이다(Python 코드에서 들어온 요청의 경로를 비교만 하는 글자 — 함수 인자 `request` 의 `request.path` 등과 `==`·`startswith`·`in (…)`(튜플·리스트·집합에 든 글자), 비교 말고는 그 경로 값을 읽지 않을 때(출처가 확인된 독립 `logging` 로그 문장의 인자는 예외) — 는 API 호출 주소가 아니다). 경로에 값을 넣을 땐 `urllib.parse.quote`.
- 계약의 단일 근거는 산출물 폴더의 `server-contract.json` 경량본이다(architecture-data §7) — URL·필드·상태코드를 훈련 기억이나 추측으로 쓰지 않는다. 필요한 API가 없으면 백엔드 코드를 고치지 않고 가정 계약으로 짓고(`계약 위험` — architecture-data §8) 실제 API는 `/dddjango`로 요청하라고 안내한다.

## §5. 로컬 저장 — hive_ce 자리

web에는 해당 없음 — 서버 렌더라 BC 데이터를 브라우저·디스크에 쌓는 로컬 저장 층이 없다(architecture-data §5).

## §6. 템플릿·요청 수명·CSRF — 표지·VM 수명·대화 표시·템플릿 표기

**템플릿 표지 — `data-testid`**: 테스트가 집는 슬롯·항목에는 *역할*을 가리키는 고정 `data-testid`를 단다(문구·순번이 아니라 역할 — architecture-ui §3 짝 규약). view 템플릿의 최상위 요소는 `data-testid="<화면>-view"`다(implementation-test §7 render-smoke). 목록 항목의 식별 값(날짜 등)은 부품 안에서 계산하지 않고 **include하는 쪽이 `with`로 넘긴다** — 값 계산이 부품 밖에 있어야 부품이 일관되고, 테스트가 집는 표지와도 양립한다.

**요청 수명 — VM은 요청마다 새로** — "입력 읽기는 View 소유"(architecture-state §2)의 프레임워크 근거: view 함수가 요청마다 VM을 만들고 응답과 함께 버린다. 요청 사이에 살아야 할 값을 VM·모듈 전역·클래스 속성에 두지 않는다 — Django는 여러 스레드·여러 워커 프로세스에서 요청을 동시에 처리하므로 모듈 전역 값은 요청 사이로 새고 워커마다 갈린다. 화면 그룹 사이 값은 SharedState(세션 — implementation-htmx §3):

```python
def channel_detail_view(request: HttpRequest, channel_id: str) -> HttpResponse:
    state: ChannelDetailState = ChannelDetailVM().build(channel_id)  # 요청마다 생성 — 입력은 VM 메서드 인자로
    return render(request, "application/channel/presentation_layer/view/channel_detail_view.html", {"state": state})
```

- 입력 중 값(폼 요소의 현재 값·포커스)은 브라우저가 들고 있다. 제출된 값은 view가 `request.POST`·`request.GET`에서 읽어 VM 메서드 인자로 넘긴다. Django `forms.Form` 층은 두지 않는다 — 입력의 업무 검증은 도메인(VO·애그리거트 메서드)·VM이 맡는다.
- view `.py` 안에서 `render`·`HttpResponse`·`redirect`를 부르는 것은 주 view 함수와 `<화면>_<조각>_fragment` 함수뿐이다(백스톱 NM17) · view는 자기 VM만 부른다(백스톱 NM9).

**다이얼로그·시트의 표시** — view 템플릿이 응답 State로 design_system 부품을 include해 그린다(부품이 전역 진입 함수로 스스로를 띄우는 `show()` 경로 금지는 architecture-ui §7 소유):

```django
{% include "design_system/component/feedback/error_feedback.html" with error=state.error only %}
{% include "design_system/component/dialog/confirm_dialog.html" with title=state.confirm_title action_href=state.confirm_href only %}
```

- 열림 상태로 그리는 `<dialog open>`은 JS가 필요 없다. 초점 가두기가 필요한 모달(`showModal()`)은 승인된 UI JS의 일이다(implementation-javascript §6).

**요청 사이의 공백** — VM 쪽 비동기 뒤 가드 같은 자리는 없다: VM은 요청 하나 안에서 끝나 «화면이 사라진 뒤의 VM»이 없다. 늦은 응답과 사라진 화면의 문제는 브라우저 쪽이다 — 조각 교체는 implementation-htmx §4, UI JS의 늦은 완료는 implementation-javascript §4.

**CSRF·인증**:

- 상태를 바꾸는 요청은 POST뿐이고 페이지 요청과 같은 인증·권한·CSRF를 지난다 — HTMX라고 보호 수준을 낮추지 않는다.
- 일반 `<form method="post">` 안에는 `{% csrf_token %}`을 둔다. HTMX `hx-post`의 토큰은 `hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'`로 보낸다(정적 JSON 값 — `js:` 접두 금지 · implementation-htmx §7). 조회(`hx-get`)에는 붙이지 않는다.
- 로그인 요구 화면은 view 함수에 `@login_required` — 페이지 라우트와 조각 라우트에 똑같이 붙인다(조각만 열려 있으면 보호가 우회된다). 조각 요청의 미로그인 302는 `RootRequestHandler.__call__`이 200 + `HX-Redirect: <Location>`으로 바꾸므로 로그인 페이지가 조각 자리에 교체되지 않고 전체 페이지 이동이 된다(§2) — 조각 view에서 따로 처리하지 않는다.

**템플릿 표기**:

- **extends 대상은 둘뿐이다**: 페이지 템플릿(`<화면>_view.html`·root 게이트 화면 `root_<게이트>_view.html`) → 문서 셸만(선언이 없으면 `root/scaffold/view/root_view.html`, 제품 선언 BC의 페이지는 자기 제품 셸만) · 조각 템플릿(section·widget·design_system component) → `design_system/[<제품>/]component/**/*.html`만(제품 뿌리는 선언이 있을 때만 · 공용 부품의 마크업 자리 채우기 — §10 slot 부품). 조각이 문서 셸을 extends하거나 페이지가 component를 extends하지 않는다(백스톱 IM26). `{% extends %}`는 그 템플릿의 첫 비주석 줄에 둔다.
- Django 짧은 주석 `{# … #}`는 한 줄만 쓴다 — 여러 줄은 `{% comment %}…{% endcomment %}`. 여러 줄 `{# … #}`는 응답에 그대로 새어 나온다(백스톱 PU6).
- block은 역할 이름으로 열고 이름으로 닫는다(`{% endblock content %}`). `{% load %}`는 알파벳순 — ui_extension 필터는 builtins 조립이라 `{% load %}` 없이 쓴다(architecture-ui §5). `{{ variable }}`·`{% tag %}` 안쪽에 한 칸 공백.
- 템플릿은 **State만 참조**하고 표시 분기만 한다 — 계산·필터링·정렬은 VM으로 가져간다(`dictsort`·산수 필터로 판정하지 않는다). *왜*: 템플릿에 숨은 판단은 리뷰·재사용 어느 쪽에서도 안 보인다.
- 출력은 자동 이스케이프된 `{{ }}`로만 — `|safe`·`{% autoescape off %}`·Python `mark_safe`는 쓰지 않는다(백스톱 PU7). 마크업이 필요하면 조각 템플릿으로 조립한다.
- 템플릿 경로는 TEMPLATES `DIRS`의 web 뿌리 기준이다(`application/<bc>/presentation_layer/section/<화면>…_section.html`) — 배선은 G0 점검.
- section include는 State를 명시 전달(`with state=state`), widget·component include는 `with … only` — 화면 비전속 조각이 암묵 context 상속에 기대면 어느 화면의 어떤 변수로 사는지 추적할 수 없다. 공용 부품에 **값만** 넘기면 이 include(`with … only`)이고, **마크업**을 부품의 정해진 자리에 넣어야 하면 그 조각 템플릿이 부품을 extends하고 block만 채운다(§10 slot 부품) — 템플릿 이름을 변수로 넘겨 include하거나 커스텀 템플릿 태그로 끼우지 않는다.
- 템플릿의 `style` 속성·`<style>` 블록에도 색·글자 리터럴을 쓰지 않는다(백스톱 NM10) — 스타일은 CSS 파일(§10)에 둔다.

## §7. 테스트 표기 → discipline-test·implementation-test로 이전

테스트 표기는 전용 스킬 2종으로 이전했다(2026-06-17 — feedback-008). **무엇을 테스트할지·오라클·비-vacuity·단언 FORM(구별·순서·위치·탭)은 `discipline-test`**, **Django 메커니즘(VM 대체 가짜 주입·테스트 클라이언트와 HTML 단언·HTMX 요청 헤더·`unittest.mock` 더블·날짜 주입·브라우저 테스트·외부 이미지 고정)은 `implementation-test`** 소유다. coder는 행위 검증 테스트를 쓸 때 이 두 스킬을 로드한다(green 래칫·신규 BC TG1 차단은 coder 산출 규율). 요청 수명·CSRF는 §6.

## §8. 정적 이미지 에셋 — `{% static %}`·web/static/images

시안의 `<img>`(로고·일러스트 등 정적 래스터)는 Phase 0 `fetch_images`가 `web/static/images/`로 다운로드하고 `asset-manifest.json`(src→`local_path`→`token` 매핑·단일 SSOT)으로 절단한다. coder는 명세가 가리킨 이미지를 manifest의 **같은 `src` 행**으로 조인해 정확 값을 가져온다(추정·눈대중 금지 — server-contract를 경량본에서 인용하듯).

- **경로**: 템플릿 `<img>`는 `{% static %}`로 쓴다 — 인자는 manifest `local_path`의 `web/static/`을 static 접두 `web/`로 바꾼 값이다(`web/static/images/logo.png` → `{% static 'web/images/logo.png' %}` — 발명 금지). `/static/…` 절대 URL·시안 원본 URL을 박지 않는다(`{% static %}`가 경로의 단일 경유 — 색 리터럴→`--color-*`와 평행). CSS의 배경 이미지는 `app_asset.css`의 `--asset-<token>`(manifest의 `token`)에 두고 `var(--asset-<token>)`로 참조한다 — 조각 CSS에 raw `url(…)` 경로를 박지 않는다(architecture-ui §7).
- **정적 자리 선언**: `STATICFILES_DIRS`의 `("web", <web>/static)` 접두 튜플 한 줄이 `web/static/` 전체를 덮는다 — 이미지가 늘어도 설정을 다시 고치지 않는다(파일별 나열 불요 — 배선은 Coordinator G0 점검). 파일은 manifest `local_path` 그대로 둔다(새 하위 폴더를 만들지 않는다).
- **배선**: `<img src="{% static 'web/images/<파일>' %}" alt="…">`로 쓴다. **치수는 강제하지 않는다** — `width`·`height`는 시안이 명시한 경우에만 둔다(글리프 아이콘[Material Symbols 리거처 — architecture-ui §5]과 정적 래스터는 다른 트랙·이미지 *크기*는 크기연결 트랙[architecture-ui §8]이지 에셋 *경로* 트랙이 아니다).
- `has_design_images`가 없으면(manifest 부재) 이 절은 적용되지 않는다 — 없는 이미지를 placeholder로 조용히 채우지 않는다.

## §9. 레이아웃 형상 — 시안 충실 재현

화면의 *형상*(요소가 세로로 쌓이나/가로로 놓이나·그룹핑·정렬·간격)은 코퍼스가 규정하지 않는다. `design-ref/`의 동결 화면 시안이 형상의 단일 근거이며 너는 그것을 **빠짐없이** Django 템플릿 + CSS로 재현한다. 명세는 *무엇을*(분해·토큰·이미지)을 정하고 *어떻게 배치*는 정하지 않는다 — 배치는 시안에 있다.

- **형상 근거는 동결 화면 파일(텍스트)**: PNG가 아니라 `design-ref/`의 동결 화면 파일에서 컨테이너 구조를 읽는다(예: `flex-col` → 조각 CSS의 `display: flex; flex-direction: column`. *이건 예시이지 닫힌 목록이 아니다* — 시안의 모든 배치 단서를 충실히 옮긴다). 텍스트 형식 파일이므로 이미지 비보장 엔진에서도 동일하게 읽힌다.
- **재현이지 직수입이 아니다**: 동결 화면 파일에서 *형상*을 읽어 우리 템플릿(view/section/widget·design_system 부품)과 조각 CSS·토큰으로 짠다 — 화면 파일 HTML·유틸리티 클래스 목록(Tailwind 등)을 그대로 복붙하거나 디자인툴 생성 코드·런타임을 직수입하지 않는다(기존 경계 유지).
- **형상은 명세가 아니라 시안 소관**: 명세 화면 절에 축·배치가 없는 것은 정상이다(architecture-ui §8) — 반송하지 말고 시안에서 형상을 가져온다.
- **이미지(`<img>`)도 형상의 일부**: `<img>`의 컨테이너 내 위치·형제 순서도 시안 그대로 재현한다. §8(에셋)이 *무엇을 어떤 경로로* 가져올지 정하고, *어디에 놓일지*는 이 형상 규율(시안 `<img>` 자리)이 정한다 — 배선만 하고 시안 위치를 흘리지 않는다. (별도 매핑 표 아님 — 시안 재현 의무의 명시.)

## §10. CSS 표기 — foundation 변수·theme·부품/조각 CSS

아래 `design_system/[<제품>/]…` 표기의 제품 부분은 제품 선언이 있을 때 own 뿌리에만 붙인다(없으면 기존 평면 경로). 각 제품은 자기 foundation·theme·component·util을 쓴다.

**foundation 변수 7파일** — `design_system/[<제품>/]foundation/app_color.css`·`app_typography.css`·`app_spacing.css`·`app_radius.css`·`app_shadow.css`·`app_duration.css`·`app_asset.css`. 각 파일은 `:root { … }`에 custom property만 정의하고, 접두는 파일별이다(`--color-*`·`--typography-*`·`--spacing-*`·`--radius-*`·`--shadow-*`·`--duration-*`/`--easing-*`·`--asset-*` — discipline-houserules §4):

```css
/* design_system/foundation/app_color.css */
:root {
  --color-primary: #2563eb;
  --color-weather-clear: #f5b301;
}

/* design_system/foundation/app_typography.css — font 줄임 묶음 값 */
:root {
  --typography-title: 700 1.25rem/1.4 "Pretendard", sans-serif;
}
```

- `--typography-*`는 `font` 줄임 묶음 값이다 — 쓰는 쪽은 `font: var(--typography-title)`이고, 같은 규칙에서 그 뒤에 `font-*`를 다시 선언하지 않는다(architecture-ui §8).
- **리터럴은 foundation 안에서만**: 색(`#…`·`rgb()`·`hsl()`)·글자(`font`·`font-size`·`font-family`·`font-weight`·`line-height`) 리터럴은 `design_system/[<제품>/]foundation/*.css` 밖에서 쓰지 않는다 — 조각 CSS·부품 CSS·템플릿 `style`·`<style>` 전부(백스톱 NM10). 연출 시간도 `--duration-*`·`--easing-*` 토큰이다(architecture-ui §7). `font-size`는 아이콘 글리프에도 foundation 토큰으로 쓴다. 글리프 크기는 `app_spacing.css`의 `--spacing-icon-*`로 정의하고 `font-size: var(--spacing-icon-*)`로 인용한다. `width`·박스 `height` 등 비-typography 크기는 architecture-ui §8의 추출값 직접 인용 규칙을 따른다. 신규 색은 architect가 토큰을 추가한다.

**theme — 문서 전역 기본값** — `design_system/[<제품>/]theme/app_theme.css`가 foundation 토큰으로 브라우저 기본 여백 초기화·웹폰트 `@font-face`·`body` 글꼴·색을 조립한다(architecture-ui §7). 문서 셸이 foundation 7파일 다음에 한 번 링크한다(제품 선언이 있으면 자기 제품 것만 — §2):

```css
/* design_system/theme/app_theme.css */
@font-face {
  font-family: "Pretendard";
  src: url("../../web/fonts/pretendard-regular.woff2") format("woff2");  /* web/static/fonts/ 의 파일 */
  font-weight: 400;
  font-display: swap;
}

*, *::before, *::after { box-sizing: border-box; }
html, body, h1, h2, h3, h4, p, ul, ol, figure, blockquote { margin: 0; }

body {
  font: var(--typography-body);
  color: var(--color-on-surface);
  background: var(--color-surface);
}
```

- **초기화**: *왜* — 시안(디자인 도구 렌더)은 문단·제목 기본 여백이 없는 세계라, `<p>`·`<h2>`를 쓰는 순간 브라우저 기본 여백이 시안에 없는 간격을 만든다 — 필요한 간격은 초기화 위에 `--spacing-*`로 명시한다. 화면·부품 CSS가 각자 기본 여백을 지우거나 글꼴을 선언하지 않는다.
- 제품 선언이 있으면 own theme의 상대 `url()`은 뿌리가 한 칸 깊다 — 위 평면 예의 `../../web/fonts/…`는 `../../../web/fonts/…`로 맞춘다.
- **웹폰트**: 폰트 파일은 `web/static/fonts/`에 둔다(필요할 때만). 출처는 시안의 원본 폰트 선언·실제 응답이다 — 폰트 URL을 기억으로 조립하지 않는다. `@font-face`의 face 이름 선언은 theme의 일이고, 그 이름을 쓰는 글자 묶음 값은 foundation `--typography-*`다.

**부품 CSS** — design_system component는 템플릿 옆에 같은 stem으로 둔다(`component/dialog/confirm_dialog.html` + `confirm_dialog.css`). 제품 선언이 있으면 평면 공용 마크업을 쓸 수 있고, CSS는 자기 제품 뿌리의 같은 군·같은 이름이다. 클래스 접두는 `<수식>-<군>`이다(`.confirm-dialog`·`.confirm-dialog__title`·`.confirm-dialog--danger`). 상태는 BEM `--` 수식 또는 `[aria-*]`·`[data-*]` 속성 선택자로 쓴다 — `.is-active` 같은 무접두 상태 클래스는 쓰지 않는다(백스톱 NM12). htmx가 붙이는 상태 클래스(`htmx-request`·`htmx-indicator`·`htmx-settling`·`htmx-swapping`·`htmx-added`)만 접두 붙은 클래스와 겹친 선택자(`.spinner-loading.htmx-request`)로 쓸 수 있다:

```css
/* design_system/component/dialog/confirm_dialog.css */
.confirm-dialog { border-radius: var(--radius-card); box-shadow: var(--shadow-overlay); }
.confirm-dialog__title { font: var(--typography-title); color: var(--color-on-surface); }
.confirm-dialog--danger .confirm-dialog__title { color: var(--color-danger); }
.confirm-dialog[aria-busy="true"] { opacity: 0.6; }
```

부품 CSS는 그 부품을 쓰는 페이지 템플릿의 `{% block head %}`에서 `{% static 'design_system/[<제품>/]component/<군>/<파일>.css' %}`로 한 번 링크한다 — 조각 응답에는 `<link>`를 넣지 않는다(조각은 이미 링크된 페이지 안에서 교체된다) — 지속 셸이면 페이지가 아니라 셸 `<head>` 가 주소 꼬리 `?v={{ root_state.shell_rev }}` 와 함께 한 번 싣는다(§2 «지속 셸» · 백스톱 SH4).

문서가 쓰는 부품(상속 사슬·include 닫힘 — 부품 안의 부품·slot 부품 포함) 가운데 CSS 파일이 있는 것은 모두 그 문서 머리에 실린다 — 페이지 `{% block head %}`, 그 셸의 모든 화면이 쓰면 셸 `<head>`, 머리에서 싣는 화면 CSS의 무조건 `@import` 닫힘도 실림이다. 백스톱 CS1은 이번 변경이 새로 빠뜨린 (문서, CSS) 쌍마다 blocker를 낸다. 본문 link·인쇄 전용·disabled·alternate link·`template`·`noscript` 안 link·일반 `url()`·미디어 질의나 `supports()`가 붙은 import·CSS 규칙 뒤 import는 실림이 아니다(`@import`는 첫 `{` 앞에서 꼬리 없음·`all`·`screen`만). 지속 셸 문서도 같은 계산이며 면제하지 않는다 — 같은 누락을 SH4와 CS1이 함께 낼 수 있다. 조각 응답(임베드·hx-get으로만 들어오는 조각)이 쓰는 부품 CSS는 그 조각을 받는 문서가 싣는다. 명세 «부품 CSS 표»의 받는 문서 칸은 감수가 미검증을 닫는 근거다(러너가 표를 읽지 않는다). 조건 안 머리 link로만 실리면 `미검증(조건부)`, 문서에 닿지 않는 조각 뿌리는 `미검증(조각)`, 글자 대입으로 풀 수 없는 extends·include와 가린 변수, HTML·현재/기준점 파일 판독 실패는 받는 문서 이름의 `미검증(못 읽음)`이다. 부품 CSS link는 문서 머리에 literal `{% static '…' %}`로 쓴다. CS1은 이 형식 또는 맨 앞이 `/`인 literal 주소 가운데 `.`·`..`를 접은 결과가 `/static/` 아래인 것만 실림으로 센다(맨 앞 `/` 없는 글자 주소는 페이지 주소 기준이라 실림이 아니다). 변수·별칭·다른 표현식과 rel·media·disabled·href 속성 안 동적 토큰(주소 꼬리의 변수 포함 — 지속 셸 SH4 꼬리 `?v={{ root_state.shell_rev }}` 하나만 떼고 읽는다)은 `미검증(못 읽음)`의 `동적 link 주소`로 남고 필요 CSS는 충족하지 않는다 — 누락은 literal 교정 줄과 함께 blocker다. `with`의 글자 대입은 include 자리에서 풀고 `block.super`는 필터 없음 또는 `|safe`만 link까지 잇는다. 다른 super 필터는 부모 block의 부품 요구만 세고 그 안 link는 실림으로 세지 않는다(머리에서는 `block.super 필터 판독 불가`). href 안 Django 토큰의 따옴표를 보존하고 심볼릭 링크의 두 트리 대상을 각각 읽는다. 동적 link 주소의 못 읽음은 살아 있는 머리 link에서만 보고한다(동적 rel은 stylesheet 여부도 확정하지 않는다) — 본문·죽은 link와 rel이 글자인 stylesheet 아닌 link는 미검증 후보 밖이다. 상세 게이트·출력·승인 유입은 discipline-houserules §8을 따른다.

**slot 부품 — 마크업 자리 채우기** — 공용 부품이 값이 아니라 *마크업*(앞쪽 아이콘·동작 단추 묶음 같은 자리)을 받아야 하면, 부품이 이름 붙은 `{% block <자리> %}기본값{% endblock <자리> %}`을 내놓고 쓰는 쪽 조각 템플릿(section·widget·design_system component)이 첫 줄에서 그 부품을 `{% extends %}`한 뒤 block만 채운다. block 이름은 부품 접두를 붙여(`app_bar_actions`) 다른 부품·셸의 block과 겹치지 않게 한다:

```django
{# design_system/component/bar/app_bar.html — slot 부품: block이 자리, block 안이 기본값 #}
<header class="app-bar">
  <div class="app-bar__leading">{% block app_bar_leading %}<span class="app-bar__spacer"></span>{% endblock app_bar_leading %}</div>
  <h1 class="app-bar__title">{% block app_bar_title %}{% endblock app_bar_title %}</h1>
  <div class="app-bar__actions">{% block app_bar_actions %}{% endblock app_bar_actions %}</div>
</header>
```

```django
{% extends "design_system/component/bar/app_bar.html" %}
{# application/chart/presentation_layer/section/chart_app_bar_section.html — app_bar의 채워진 사례 하나 #}
{% block app_bar_title %}{{ state.title }}{% endblock app_bar_title %}
{% block app_bar_actions %}
  {% include "design_system/component/button/icon_button.html" with icon="settings" href=state.settings_href only %}
{% endblock app_bar_actions %}
```

- 쓰는 쪽 조각 파일은 **extends한 부품 하나의 채워진 사례**다 — 같은 파일 안에 block 밖 마크업·두 번째 extends를 두지 않는다(Django는 자식 템플릿의 block 밖 내용을 조용히 버린다). 채우지 않은 block은 부품의 기본값이 그대로 나온다.
- block 안에서는 그 조각의 맥락(section이면 include가 넘긴 `state`)을 쓴다 — 부품 템플릿 자신은 BC 어휘·`state`를 모르고 자리와 기본값만 안다(architecture-ui §7). 자리 안에 다른 부품을 값으로 넣을 땐 다시 `include … with … only`다.
- 페이지는 이 section을 평소처럼 include한다(`{% include "application/chart/presentation_layer/section/chart_app_bar_section.html" with state=state %}`) — 부품 CSS(`app_bar.css`)는 위와 같이 페이지 `{% block head %}`에서 링크한다(지속 셸이면 페이지가 아니라 셸 `<head>` 가 주소 꼬리 `?v={{ root_state.shell_rev }}` 와 함께 한 번 싣는다 — §2 «지속 셸» · 백스톱 SH4).

**조각 CSS** — presentation 조각(view·section·widget) CSS는 `web/static/application/[<area>/]<bc>/<조각 stem>.css`(템플릿과 같은 stem · 필요한 조각만), root scaffold 조각 CSS는 `web/static/root/<조각 stem>.css`다 — `.py` 옆이 아니라 static 쪽에 둔다(discipline-houserules §1). 링크는 페이지의 `{% block head %}`에서 `{% static 'web/application/<bc>/<stem>.css' %}` — 지속 셸이면 페이지가 아니라 셸 `<head>` 가 주소 꼬리 `?v={{ root_state.shell_rev }}` 와 함께 한 번 싣는다(§2 «지속 셸» · 백스톱 SH4 · 한 문서에 그 제품의 조각 CSS 가 모두 실리므로 맨 선택자와, 같은 BEM block 을 둘 이상 파일이 정의하는 겹침은 SH5 가 막는다).

- `design_system/[<제품>/]util/`은 시각 동작 헬퍼 CSS(미디어쿼리 묶음·스크롤 동작)다 — 토큰을 정의하지 않는다.

## §11. 공식 SDK 사본 — static/vendor

- **외부 JS 는 G1 승인·등재된 공식 플랫폼 SDK 뿐이다**(discipline-houserules §9) — 사본은 `web/static/vendor/<sdk_id>/<파일>` 하나(판 폴더 없음 · 판 올림은 같은 자리 바꿔 쓰기)이고 등재 목록은 `web/sdk_registry.json` 이다. 내려받기·복사·판 올림·등재·복원·제거는 Coordinator 가 `sdk_vendor.py` 로만, 목록·사본만 담은 `chore(web-sdk):` 격리 커밋으로 한다 — coder 는 `web/static/vendor/**`·`web/sdk_registry.json` 을 읽기만 한다(섞이면 백스톱 WV10). 명세에 없는 라이브러리·SDK 기능이 필요해 보이면 파일 복사·CDN·동적 로드로 우회하지 않고 설계로 반송한다.
- 실행 태그는 그 SDK 를 쓰는 페이지의 `{% block scripts %}` 안에서, 그 SDK 를 부르는 기능 JS보다 **앞에** `src`·`defer` 만 달아 한 번 둔다: `<script src="{% static 'web/vendor/<sdk_id>/<파일>' %}" defer></script>`(모든 페이지가 쓰면 `root_view.html` 의 `{% block scripts %}` 여는 줄 앞 · root_view·페이지 중복 금지 · 지속 셸이면 셸 `<head>` 의 `root_shell.js` 뒤 · 그 SDK 를 부르는 기능 JS 태그 앞 · 주소 꼬리 `?v={{ root_state.shell_rev }}` — 페이지에는 두지 않는다). CDN 실행 태그(`<script src="https://…">`)·`async`·`type`·조각 안 실행 태그는 쓰지 않는다(백스톱 PU2 · WV6).
- 공개 키는 settings 값만 출처다 — `common/` 의 설정 읽기(django.conf — application_layer 는 django 를 모른다) → VM 이 state 에 담고 → 템플릿이 escape 된 data 속성(`data-<키>="{{ state.<키> }}"` — 값은 순수 `{{ … }}` 하나 · 백스톱 WV7)·`json_script` 로 넘긴다. settings 에 공개 설정 이름이 없으면 Coordinator 가 G1 승인 하에 선택형(빈 문자열 = 미설정)으로 배선한다.
- htmx core는 이 절 밖이다 — Coordinator가 G0에서 실제 core 경로를 확인해 build-state `htmx_core_static`에 적고(새 설치는 `web/static/htmx/htmx.min.js` 2.0.10 하나 · 브라운필드는 기존 경로), 문서 셸이 그 경로를 로드한다(§2·implementation-htmx §1). 소비 표기(전역 이름·초기화·호출 시점)는 implementation-javascript §8.
- Python 패키지는 호스트의 의존 선언(requirements·pyproject)에 버전 고정(`==`)으로 추가한다 — 무핀 설치로 resolve된 실버전.
