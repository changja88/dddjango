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
- **이동 의미론**: 링크 이동(`<a href>` — 브라우저 기록에 쌓기)·redirect 응답(요청 결과를 다른 주소로 교체 — POST 뒤 PRG)·HTMX 부분 교체(기록 불변 — implementation-htmx §7) 셋이다. 일반 이동은 이름 기반이며 navigator가 `reverse(<Bc>Routes.…)`로 href를 만든다. 기본 홈 목적지 한 건만 architecture-ui §6의 소유 router 상수를 소유 navigator가 가공 없이 반환한다(타 BC는 그 navigator 호출 · 폴백 금지). `reverse`·`redirect`에 문자열 리터럴을 넘기지 않는다(백스톱 NM13). view의 redirect는 `redirect(state.next_href)` 하나다 — 조각(HTMX) 요청의 3xx 응답은 `RootRequestHandler`가 200 + `HX-Redirect: <Location>`으로 바꿔 htmx가 전체 이동하게 한다(아래 게이트).
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
- **문서 셸·탭** — `root/scaffold/view/root_view.html`이 기본 문서 셸이다. 제품 선언이 없으면 모든 페이지가 extends하고, 선언 BC의 페이지는 자기 제품 셸만 extends한다(탭 프레임 — 페이지가 셸을 가리키는 방향은 Django 템플릿 상속의 방향이라 BC가 root를 아는 유일한 예외 — discipline-houserules §5):

```django
{# root/scaffold/view/root_view.html — 문서 셸 (탭 프레임) #}
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

제품 선언이 있으면 flat의 `root_view.html`과 own의 `root_<제품>_view.html`은 모두 위와 같은 독립 문서이며 어떤 템플릿도 extends하지 않는다(백스톱 IM26). own 셸의 예: `root/scaffold/view/root_console_view.html`은 자기 `design_system/console/foundation/`의 표준 7파일 다음에 `design_system/console/theme/app_theme.css`만 링크하고, 틀 CSS는 `web/root/root_console_view.css`다(기존 `root_vm.py`·`root_state.py`를 함께 쓴다).

탭 href는 RootVM이 만든다 — context processor `root_context(request)`가 `request.session`과 현재 BC(`request.resolver_match.namespaces[0]`)를 RootVM에 넘기고, RootVM이 root의 탭 표(BC → 탭)로 탭마다 `href`·`is_current`를 채운다: 현재 탭은 그 탭 첫 화면 href, 다른 탭은 세션 `root.tab_last`의 마지막 경로(없으면 첫 화면 — §3). 탭 기록은 `RootRequestHandler.process_view`가 적는다(아래) — BC는 탭 기록을 모른다(architecture-state §10 "거의 빈 VM").

- **top-level redirect(게이트)의 자리** — 요청 수명 handler `RootRequestHandler`(미들웨어 — `MIDDLEWARE` 등록은 G0 점검)의 `process_view(request, view_func, view_args, view_kwargs)`다. **view 모듈이 `web.`으로 시작할 때만** 게이트·세션 신원 이월·탭 기록(§3)을 한다 — 같은 프로세스 API 호출(§4)이 닿는 백엔드 view(모듈이 `web.` 밖)에는 아무것도 하지 않으므로 middleware → RootVM → UseCase → Client → middleware 재진입이 끊긴다(테스트 `Client`도 미들웨어를 그대로 지난다). 게이트 여부는 root_vm이 UseCase를 직접 호출해 얻는다(architecture-state §10 — UseCase에 `request`를 넘기지 않는다). 신원 contextvar는 `process_view`에서 set하고 그 토큰을 `request`에 두었다가 `__call__`의 응답 뒤 reset한다:

```python
# root/handler/root_request_handler.py — 요청 수명 handler
SESSION_TOKEN_META: str = "web.root.session_token"  # process_view가 둔 contextvar 토큰의 자리(request.META)


class RootRequestHandler:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self._get_response: Callable[[HttpRequest], HttpResponse] = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        try:
            response: HttpResponse = self._get_response(request)  # URL 해석 → process_view → view
        finally:
            token: object = request.META.pop(SESSION_TOKEN_META, None)
            if isinstance(token, Token):
                SESSION_KEY.reset(token)  # 응답 뒤 신원을 되돌린다 — 같은 스레드의 다음 요청으로 새지 않게
        is_fragment: bool = request.headers.get("HX-Request") == "true"
        if is_fragment and 300 <= response.status_code < 400 and "Location" in response:
            return HttpResponse(headers={"HX-Redirect": response["Location"]})  # 조각 요청의 3xx(로그인 포함) → 전체 이동
        return response

    def process_view(
        self,
        request: HttpRequest,
        view_func: Callable[..., HttpResponse],
        view_args: tuple[object, ...],
        view_kwargs: dict[str, object],
    ) -> HttpResponse | None:
        if not view_func.__module__.startswith("web."):
            return None  # 백엔드 view(같은 프로세스 API 호출 포함) — 아무것도 하지 않는다(재진입 차단)
        session_key: str | None = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
        request.META[SESSION_TOKEN_META] = SESSION_KEY.set(session_key)  # 세션 신원 이월(§4)
        gate_href: str | None = RootVM(session=request.session).gate_href(request.path)  # root_vm이 UseCase로 판정
        if gate_href is not None and request.path != gate_href:
            return redirect(gate_href)  # 조각 요청이면 __call__이 HX-Redirect로 바꾼다
        if request.method == "GET" and request.headers.get("HX-Request") != "true":
            self._record_tab(request)  # web 페이지 GET만 탭 기록(§3)
        return None

    def _record_tab(self, request: HttpRequest) -> None:
        namespaces: list[str] = request.resolver_match.namespaces if request.resolver_match else []
        tab: str | None = TAB_OF_BC.get(namespaces[0]) if namespaces else None
        if tab is None:
            return
        stored: object = request.session.get(TAB_LAST_KEY)
        last_paths: dict[str, str] = dict(stored) if isinstance(stored, dict) else {}
        last_paths[tab] = request.get_full_path()
        request.session[TAB_LAST_KEY] = last_paths  # 새 dict 대입 — 제자리 변경은 세션이 저장하지 않는다
```

- 데코레이터(`@login_required`)는 `functools.wraps`로 `__module__`을 보존하므로 판정이 그대로 선다. `request.session`을 쓰므로 `MIDDLEWARE`에서 `SessionMiddleware`·`AuthenticationMiddleware` 뒤에 둔다.
- `__call__`의 3xx 변환은 조각 view의 `@login_required`(미로그인 302)·게이트 redirect·view의 `redirect(…)`에 똑같이 걸린다 — 로그인 페이지가 조각 자리에 끼어들지 않고 전체 이동한다(§6). 조각 view의 `@login_required`는 그대로 둔다.

- **전환**: 페이지 이동 전환은 두지 않는다(브라우저 기본 이동). 조각 교체 전환은 implementation-htmx §7의 `htmx-swapping`·`htmx-settling` 클래스 + `--duration-*`·`--easing-*` 토큰이다 — router는 전환 연출을 갖지 않아 design_system을 참조하지 않는다(architecture-ui §6).
- Django 판 메모: 본문 표기(`path`·`reverse`·`redirect`·`app_name` 네임스페이스·미들웨어 판형)는 4.2~5.x에서 같다.

## §3. 탭 재탭 2단 동작 — 규약 §10-5 ④ 확정 (root_view 소유)

**확정(2026-06-12 사용자 — 규약 §10-5 ④): 현재 탭을 재탭하면 ① 탭 안 중첩 화면에 들어가 있으면 탭 첫 화면으로 복귀(스택 리셋) ② 이미 첫 화면이면 스크롤 최상단.** 다른 탭으로 가는 일반 탭 전환은 **그 탭의 마지막 위치를 복원**한다(재탭만 초기화한다). 전부 root(root_view·RootVM·RootRequestHandler)가 처리하고 **BC는 무관여**다 — 신호를 듣지도, 스크립트를 받지도, 탭 기록을 알지도 않는다(규약 §9-11).

**web에서의 메커니즘 — 탭 href를 둘로 가른다**: ⓐ `RootRequestHandler.process_view`가 web 페이지 GET(`HX-Request` 아님)마다 세션 `root.tab_last`의 그 탭 자리에 `request.get_full_path()`를 적는다(탭 = 그 view의 URL 네임스페이스 첫 마디 = BC → root의 탭 표 — §2). ⓑ RootVM이 탭 href를 만든다 — **현재 탭은 그 탭 첫 화면 href**, **다른 탭은 세션의 마지막 경로**(없으면 첫 화면). 그래서 ① 현재 탭 중첩 화면(`/channels/ch-1/`)에서 탭을 누르면 첫 화면(`/channels/`)으로 돌아가고 ② 첫 화면에서 누르면 같은 주소로 새로 이동해 맨 위에서 다시 그린다(스크롤 복원은 뒤로·앞으로 이동과 새로고침에만 걸리고 링크 이동에는 걸리지 않는다) ③ 다른 탭에서 이 탭을 누르면 마지막에 보던 주소(`/channels/ch-1/`)로 돌아온다:

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
        tabs: tuple[RootTab, ...] = tuple(
            RootTab(
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

```django
{# root_view.html 탭 — href는 RootVM이 고른 값(현재 탭 = 첫 화면 · 다른 탭 = 마지막 경로) #}
<a href="{{ tab.href }}"{% if tab.is_current %} aria-current="page"{% endif %}>{{ tab.label }}</a>
```

- **BC 화면의 전제(유일한 접점 — "아무것도 하지 않기")**: 화면 최상위에 별도 스크롤 컨테이너(높이 고정 + `overflow: auto` 래퍼)를 두지 않는다 — 문서 스크롤이 기본이라 새 이동이 맨 위에서 시작한다. 내부 스크롤 패널을 쓰는 화면은 그 패널만 재탭 스크롤톱이 무반응이 된다(의도된 트레이드오프 — BC에 결합을 만들지 않는 것이 우선).
- **탭 링크에 `hx-get`·`hx-boost`를 붙이지 않는다** — 부분 교체로 바꾸면 주소 이동·스크롤 리셋이 사라져 같은 동작을 JS로 다시 만들게 된다. 탭 기록도 페이지 GET에만 적히므로(조각 요청 제외) 조각 교체는 마지막 경로를 바꾸지 않는다.
- 세션 값은 JSON 직렬화 가능한 원시값이라 `root.tab_last`는 `{탭: 경로}` dict 하나다 — 키 대입만 변경으로 저장되므로 항상 새 dict를 대입한다(implementation-htmx §3).
- **재탭 신호 버스(과거 HaffHaff `scroll_to_top_notifier` — BC가 전역 신호를 listen)는 비채택**이다: 금지 채널의 재생산(architecture-state §8). web에서는 전역 JS 이벤트로 BC 스크립트에 재탭을 알리는 형태가 그 재생산이다.
- 상태바 탭 같은 기기 셸 동작은 web에는 해당 없음(브라우저가 소유한다). 2단 동작·전환 복원의 브라우저 확인(중첩 화면에서 탭 → 첫 화면 URL · 첫 화면 스크롤 뒤 탭 → 맨 위 · A 상세 → B → A 탭 → A 상세)은 골격 구현 시 1회.

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
- 백엔드 경로 리터럴의 유일 거처는 DataSource 모듈 상수다 — VM·view·템플릿에 백엔드 URL이 나타나면 위반이다. 경로에 값을 넣을 땐 `urllib.parse.quote`.
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

부품 CSS는 그 부품을 쓰는 페이지 템플릿의 `{% block head %}`에서 `{% static 'design_system/[<제품>/]component/<군>/<파일>.css' %}`로 한 번 링크한다 — 조각 응답에는 `<link>`를 넣지 않는다(조각은 이미 링크된 페이지 안에서 교체된다).

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
- 페이지는 이 section을 평소처럼 include한다(`{% include "application/chart/presentation_layer/section/chart_app_bar_section.html" with state=state %}`) — 부품 CSS(`app_bar.css`)는 위와 같이 페이지 `{% block head %}`에서 링크한다.

**조각 CSS** — presentation 조각(view·section·widget) CSS는 `web/static/application/[<area>/]<bc>/<조각 stem>.css`(템플릿과 같은 stem · 필요한 조각만), root scaffold 조각 CSS는 `web/static/root/<조각 stem>.css`다 — `.py` 옆이 아니라 static 쪽에 둔다(discipline-houserules §1). 링크는 페이지의 `{% block head %}`에서 `{% static 'web/application/<bc>/<stem>.css' %}`.

- `design_system/[<제품>/]util/`은 시각 동작 헬퍼 CSS(미디어쿼리 묶음·스크롤 동작)다 — 토큰을 정의하지 않는다.

## §11. 공식 SDK 사본 — static/vendor

- **외부 JS 는 G1 승인·등재된 공식 플랫폼 SDK 뿐이다**(discipline-houserules §9) — 사본은 `web/static/vendor/<sdk_id>/<파일>` 하나(판 폴더 없음 · 판 올림은 같은 자리 바꿔 쓰기)이고 등재 목록은 `web/sdk_registry.json` 이다. 내려받기·복사·판 올림·등재·복원·제거는 Coordinator 가 `sdk_vendor.py` 로만, 목록·사본만 담은 `chore(web-sdk):` 격리 커밋으로 한다 — coder 는 `web/static/vendor/**`·`web/sdk_registry.json` 을 읽기만 한다(섞이면 백스톱 WV10). 명세에 없는 라이브러리·SDK 기능이 필요해 보이면 파일 복사·CDN·동적 로드로 우회하지 않고 설계로 반송한다.
- 실행 태그는 그 SDK 를 쓰는 페이지의 `{% block scripts %}` 안에서, 그 SDK 를 부르는 기능 JS보다 **앞에** `src`·`defer` 만 달아 한 번 둔다: `<script src="{% static 'web/vendor/<sdk_id>/<파일>' %}" defer></script>`(모든 페이지가 쓰면 `root_view.html` 의 `{% block scripts %}` 여는 줄 앞 · root_view·페이지 중복 금지). CDN 실행 태그(`<script src="https://…">`)·`async`·`type`·조각 안 실행 태그는 쓰지 않는다(백스톱 PU2 · WV6).
- 공개 키는 settings 값만 출처다 — `common/` 의 설정 읽기(django.conf — application_layer 는 django 를 모른다) → VM 이 state 에 담고 → 템플릿이 escape 된 data 속성(`data-<키>="{{ state.<키> }}"` — 값은 순수 `{{ … }}` 하나 · 백스톱 WV7)·`json_script` 로 넘긴다. settings 에 공개 설정 이름이 없으면 Coordinator 가 G1 승인 하에 선택형(빈 문자열 = 미설정)으로 배선한다.
- htmx core는 이 절 밖이다 — Coordinator가 G0에서 실제 core 경로를 확인해 build-state `htmx_core_static`에 적고(새 설치는 `web/static/htmx/htmx.min.js` 2.0.10 하나 · 브라운필드는 기존 경로), 문서 셸이 그 경로를 로드한다(§2·implementation-htmx §1). 소비 표기(전역 이름·초기화·호출 시점)는 implementation-javascript §8.
- Python 패키지는 호스트의 의존 선언(requirements·pyproject)에 버전 고정(`==`)으로 추가한다 — 무핀 설치로 resolve된 실버전.
