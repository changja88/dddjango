# htmx 표기법 — 요청 구동 VM·조각 응답·hx-* 규율

> **출처:** htmx.org(docs·reference — 속성·요청/응답 헤더·`responseHandling`·2.x 이전 안내) · docs.djangoproject.com(세션 직렬화·변경 감지·시그널 `dispatch_uid`·`AppConfig.ready`) — dddart implementation-riverpod(2026-06-12 확인 · 제1 규약 §9-13 · dddart 결정 2026-06-12: 자동 재시도 전역 OFF)의 web 이식.
> 본문 속 `(규약 §N)`은 **출처 표기**이며 로드 대상이 아니다. 로드 가능한 위임은 "스킬명 + §번호(또는 주제)"뿐.

---

## 목차

- §1. 버전·전제 — htmx 2.0.10 고정 판
- §2. 요청 구동 형태 — 페이지 view·조각 응답 (dddjango-web 화이트리스트)
- §3. 수명 표기 — 요청·세션·프로세스
- §4. hx-* 규율 — get/post/target/swap/trigger/headers/indicator
- §5. 표시 상태 — 첫 렌더·hx-indicator·오류 조각
- §6. 재조회 — 액션 응답 조각·HX-Trigger
- §7. View 측 표기 — view 함수·조각 템플릿
- §8. 재시도 정책 — 자동 재시도 없음 (dddjango-web 확정)
- §9. 금지 표면 — 인라인 JS 채널·확장·부스트
- §10. 백스톱 PU 연동 — 기계 집행 확보

---

## §1. 버전·전제 — htmx 2.0.10 고정 판

htmx는 **2.0.10 고정 판 한 파일**이다 — 새 설치는 `web/static/htmx/htmx.min.js` 하나이고 Coordinator가 G0에 공식 배포본(`https://unpkg.com/htmx.org@2.0.10/dist/htmx.min.js`)을 받아 설치한다. 기존 프로젝트에 `web/static/js/htmx.min.js`·`htmx.js`가 있으면 그 설치를 그대로 소비한다(브라운필드 — 판이 달라도 그대로) — 이중 설치·조용한 이동·판 올림 금지(백스톱 PJ2는 새로 더한 htmx 파일만 본다·PU1). G0가 확인한 실제 core 경로는 build-state `htmx_core_static`(예 `web/htmx/htmx.min.js` · 브라운필드 `web/js/htmx.min.js`)에 적히고 coder-web 입력으로 온다.

- 로드는 root_view의 한 줄 `<script src="{% static '<htmx_core_static>' %}" defer></script>` — `htmx_core_static` 경로 그대로다(새 설치면 `{% static 'web/htmx/htmx.min.js' %}` · implementation-django §2). 다른 경로를 짐작해 넣지 않는다 — 조각 응답에 다시 넣지 않는다.
- 2.x 기본값 중 dddjango-web에 닿는 것: 같은 출처 요청만(`selfRequestsOnly`) · **4xx·5xx 응답은 교체하지 않는다**(§5) · 204 응답은 교체하지 않는다 · 확장은 core 밖 별도 배포(§9) · 요청마다 `HX-Request: true` 헤더(조각 요청 식별 — implementation-test §4).
- 1.x 표기(`hx-on="click: …"` 옛 문법·`hx-ws`·`hx-sse` 속성)는 2.x에 없다 — 옛 예제를 옮겨 쓰지 않는다.

## §2. 요청 구동 형태 — 페이지 view·조각 응답 (dddjango-web 화이트리스트)

dddjango-web의 **요청 구동 형태는 둘**이다 — 상태의 자리가 ViewModel 변종(VM·SharedState·Service)과 root 2변종(root_vm·handler)뿐이고(허용 위치 닫힌 열거는 discipline-houserules §4), VM은 요청 하나가 만들고 응답과 함께 끝난다:

| 표기 | 응답 | dddjango-web의 자리 |
|---|---|---|
| 페이지 view `<화면>_view`가 `<화면>VM().build(…)` → `render(…, "<화면>_view.html", {"state": state})` | 페이지 HTML(root_view extends) | **표준 VM**(서버 조회 build — architecture-state §2) |
| 조각 응답 `<화면>_<조각>_fragment`가 같은 VM의 `build`·액션 메서드 → section 템플릿 render | 조각 HTML(HTMX 부분 교체 단위) | 조회 재렌더·재시도·액션 결과 |
| 임베드 첫 렌더 `<화면>_embed_fragment`가 자기 VM의 `build()` → 자기 본문 section render(셸 없음) | 조각 HTML | 다른 화면 안의 이 화면 자리(§7) — 조각 이름 규칙 안의 한 경우 |
| 서버 이벤트 스트림(SSE·WebSocket 구독) | — | 현재 표준 예 없음 — 쓰지 않는다 |

- **VM 밖에서 화면 값을 만드는 우회는 쓰지 않는다**: 커스텀 템플릿 태그·컨텍스트 프로세서로 BC 화면 값을 계산하는 자리는 dddjango-web 상태 어휘에 없다. 파생·조합 값은 State 필드나 State의 `@property`로 해소한다(architecture-state §3). root 셸의 `root_context`만 예외다(implementation-django §2).
- **`build(...) -> <화면>State`가 VM의 정식 시그니처다** — 조회 실패는 build가 `BadRequestResponse`를 raise하고 view(페이지·조각 함수)가 잡아 같은 section 템플릿을 맥락 `load_error`·`retry_href`로 그린다(에러 2채널 ①의 메커니즘 — §5·architecture-state §4). VM에 실패 전용 메서드·State 필드를 만들지 않는다.
- **이름 규칙**: VM `<화면>VM`(`<화면>_vm.py`)·State `<화면>State`·조각 응답 함수 `<화면>_<조각>_fragment`·조각 템플릿 `<화면>…_section.html`(discipline-houserules §4). VM 접미 `VM`은 PEP 8 약어 규칙(대문자 유지)에 맞는다.
- **입력은 메서드 인자, 공유 값은 생성자 인자**: 경로 인자·쿼리·POST 값은 view가 읽어 `build(channel_id)`·`leave_channel(channel_id)` 같은 메서드 인자로 넘긴다. 세션 매핑으로 만든 SharedState는 VM 생성자 인자로 넘긴다(`OrderListVM(cart=cart)` — §3). `or Default()` 폴백 주입 자리는 두지 않는다(architecture-state §2).

## §3. 수명 표기 — 요청·세션·프로세스

수명 표기는 **셋**이다 — 어느 변종이 어느 수명인가(VM=요청·SharedState=세션·Service·root handler=프로세스)는 **architecture-state §9가 소유**하고, 이 스킬은 표기만 소유한다:

| 수명 | 표기 | 자리 |
|---|---|---|
| 요청 (기본) | view 함수 안 지역 이름 `state: …State = <화면>VM().build(…)` — 응답과 함께 끝 | VM |
| 세션 (화면 그룹) | view가 `request.session`을 넘기고 SharedState가 `MutableMapping[str, object]`로 받아 `<bc>.<관심사>` 키만 읽고 쓴다 | SharedState |
| 프로세스 (web 전체) | `WebConfig.ready()` → `root_initializer`가 시그널 수신을 한 번 연결 | Service·root handler |

```python
# application/order/application_layer/shared_state/order_cart_shared_state.py — django import·request 낱말 없음
from collections.abc import MutableMapping

CART_KEY: str = "order.cart"  # <bc>.<관심사> — 세션 안 자기 자리


class OrderCartSharedState:
    """화면 그룹이 함께 보는 장바구니 — 세션 수명 + 명시적 reset."""

    EVENT: str = "order-cart"  # 값이 바뀐 응답이 싣는 HX-Trigger 이벤트 이름(§6)

    def __init__(self, session: MutableMapping[str, object]) -> None:
        self._session: MutableMapping[str, object] = session

    def item_ids(self) -> tuple[str, ...]:
        stored: object = self._session.get(CART_KEY)
        return tuple(stored) if isinstance(stored, list) else ()

    def add(self, item_id: str) -> None:
        self._session[CART_KEY] = [*self.item_ids(), item_id]  # 새 값을 대입한다 — 제자리 변경은 저장되지 않는다

    def reset(self) -> None:
        self._session.pop(CART_KEY, None)  # 자기 키만 지운다 — 세션 전체 비우기 금지
```

```python
# presentation_layer/view/order_list_view.py — 세션 매핑은 view가 넘긴다
def order_list_view(request: HttpRequest) -> HttpResponse:
    cart: OrderCartSharedState = OrderCartSharedState(session=request.session)
    state: OrderListState = OrderListVM(cart=cart).build()
    return render(request, "application/order/presentation_layer/view/order_list_view.html", {"state": state})
```

- **application_layer는 `request`를 모른다**: use_case·view_model·state·shared_state·service 파일은 `django` import(`django.utils` 제외)·`HttpRequest`·`HttpResponse*`·`request.` 토큰을 쓰지 않는다(백스톱 IM12). 세션은 매핑으로, API 신원은 `RootRequestHandler.process_view`가 contextvar에 심어(implementation-django §2·§4) VM도 `request`를 받지 않는다.
- **세션 값은 JSON 직렬화 가능한 원시값만**(`str`·`int`·`bool`·`list`·`dict`): 기본 세션 직렬화기가 JSON이라 dataclass는 넣을 수 없고, tuple은 list로 돌아온다. 세션은 **키 대입만 변경으로 감지**한다 — 저장된 list를 제자리에서 고치면 저장되지 않으므로 항상 새 값을 대입한다.
- 키는 `<bc>.<관심사>` 한 개 — 다른 BC의 키를 읽거나 지우지 않는다(타 BC SharedState 접근 금지 — architecture-state §7). reset은 자기 키만 지운다(`session.flush()`·`clear()`는 로그인 세션까지 지운다).
- **프로세스 수명 — Service의 시그널 연결은 root가 한다**: service 파일은 수신 메서드만 두고(django import 없음), 시그널 import·연결은 `root_initializer`가 `WebConfig.ready()`에서 한 번 한다:

```python
# application/member/application_layer/service/login_record_service.py — 비화면 이벤트 수신 (django import 없음)
class LoginRecordService:
    def on_logged_in(self, member_id: str) -> None:
        MemberUseCase().record_login(member_id)  # Model 방향은 UseCase만
```

```python
# root/initializer/root_initializer.py — 시동: 시그널 import·연결은 root 쪽
class RootInitializer:
    def start(self) -> None:
        user_logged_in.connect(_record_login, dispatch_uid="member.login_record_service")  # 중복 연결 방지


def _record_login(sender: type, user: AbstractBaseUser, **kwargs: object) -> None:
    LoginRecordService().on_logged_in(str(user.pk))  # 시그널 인자를 원시값으로 풀어 넘긴다
```

- `dispatch_uid`로 같은 수신이 두 번 연결되지 않게 한다 — `ready()`가 다시 불려도 한 번이다. 시그널 수신은 그 시그널을 보낸 요청 안에서 동기로 불린다(별도 스레드·큐가 아니다). 프로세스 수명은 워커 프로세스마다 따로다 — 워커 사이로 공유되는 상태를 모듈 전역에 두지 않는다.
- 화면 밖 조각의 «일시정지» 같은 축은 web에는 해당 없음 — 보이지 않는 조각은 요청이 없을 뿐이다.

## §4. hx-* 규율 — get/post/target/swap/trigger/headers/indicator

dddjango-web이 쓰는 hx-* 속성은 일곱이다 — 그 밖의 hx-* 가 필요해 보이면 명세가 정하지 않은 동작이니 설계 반송한다:

| 속성 | 자리 | 규율 |
|---|---|---|
| `hx-get` | 조회 재렌더(section 교체)·재시도·view 임베드 자리(§7) | 기본값. GET 응답은 서버 상태를 바꾸지 않는다. CSRF 토큰 불요 |
| `hx-post` | 액션(상태 변경) | `hx-headers`의 CSRF 토큰 필수 · 페이지와 같은 인증·권한 |
| `hx-target` | 교체 대상 | `#<id>` — 응답 section 템플릿의 루트 id와 맞춘다 |
| `hx-swap` | 교체 방식 | 조각 루트를 통째 바꾸면 `outerHTML`, 안쪽만이면 `innerHTML`(기본). 전환이 명세된 교체는 `swap:`/`settle:` 타이밍 수식어(§7) |
| `hx-trigger` | 발동 이벤트 | 기본 트리거로 충분하면 생략 · 이벤트 이름(+`from:`·`delay:` 수식어)만 — `[조건식]` 금지 · 공유 값 갱신 구독은 `<이벤트> from:body`(§6) · `load`는 임베드 자리 하나만(§7) |
| `hx-headers` | CSRF 토큰 | 정적 JSON 문자열만(`'{"X-CSRFToken": "{{ csrf_token }}"}'`) — `js:` 접두 금지 |
| `hx-indicator` | 요청 중 표시 | design_system 로딩 부품의 id(§5) |

- **URL은 State의 href**: `hx-get="{{ state.rows_href }}"`·`hx-post="{{ row.leave_href }}"` — VM이 navigator로 만든 href다. `{% url %}`·경로 리터럴을 쓰지 않는다(백스톱 NM13 — implementation-django §2).
- **요청 사이 가드 자리는 서버에 없다**: VM은 요청 하나 안에서 끝나므로 «처리 중 화면이 사라진 뒤의 VM»이 없다. 브라우저 쪽 수명(교체되는 노드·늦은 완료)을 UI JS가 다룰 때는 implementation-javascript §3·§4가 소유한다 — 이 경계를 잡는 백스톱은 없다(표기 규율로만).
- htmx·HTTP 관례 중 dddjango-web에 닿는 것: 조각이 첫 데이터를 스스로 부르지 않는다(첫 화면은 페이지 view가 State로 다 그린다 — `hx-trigger="load"`로 첫 화면 채우기 금지, 초기화는 build 자신의 일 · **유일한 예외는 다른 view를 임베드하는 자리 하나**(`load` 트리거) — 그 view의 첫 렌더는 그 view의 VM이 맡기 때문이다 · §7) / 입력 중 값(폼 입력)을 서버 상태로 옮기지 않는다(입력은 제출 때 view가 읽어 VM 인자로 — architecture-state §2) / GET 처리 중 쓰기 금지(GET은 다시 보내질 수 있다) / 조각 경로는 router 리터럴로만 / 부분 교체는 바뀐 부분만 담은 section을 대상으로.

## §5. 표시 상태 — 첫 렌더·hx-indicator·오류 조각

서버 렌더라 화면의 표시 상태는 넷이다:

| 상태 | 표기 |
|---|---|
| 데이터 | 페이지 view가 `build()`가 돌려준 State로 첫 렌더 — 첫 화면에는 로딩 상태가 없다(응답이 올 때 이미 데이터가 있다) |
| 요청 중(조각) | `hx-indicator="#<id>"`가 가리킨 design_system 로딩 부품에 htmx가 `htmx-request` 클래스를 붙인다 — 그 클래스에서 보이게 하는 규칙은 부품 CSS가 소유 |
| 조회 실패(채널 ①) | build의 raise → view(페이지·조각 함수)가 잡아 **같은 section 템플릿**을 맥락 `{"load_error": e, "retry_href": <Bc>Navigator.<화면>_<조각>_href(...)}`로 그린다 — section은 루트 요소(같은 `id`)를 유지하고 그 안에서 `error_feedback.html`을 include(재시도 단추 — §8). 공용 `error_feedback.html`을 조각 응답으로 바로 돌려주지 않는다 |
| 재조회 중 | 이전 조각을 화면에 둔 채 요청 — 응답이 와야 교체된다(화면이 비지 않는다) |

```python
# presentation_layer/view/channel_summary_view.py — 페이지·조각 함수가 같은 section으로 오류 자리를 그린다
_PAGE: str = "application/channel/presentation_layer/view/channel_summary_view.html"
_LIST_SECTION: str = "application/channel/presentation_layer/section/channel_summary_list_section.html"


def channel_summary_view(request: HttpRequest) -> HttpResponse:
    try:
        state: ChannelSummaryState = ChannelSummaryVM().build()
    except BadRequestResponse as error:  # 채널 ① — 맥락 키 load_error · retry_href(view가 navigator로 얻는다)
        return render(request, _PAGE, {"load_error": error, "retry_href": ChannelNavigator.channel_summary_list_href()})
    return render(request, _PAGE, {"state": state})


def channel_summary_list_fragment(request: HttpRequest) -> HttpResponse:  # 조회 재렌더·재시도 조각
    try:
        state: ChannelSummaryState = ChannelSummaryVM().build()
    except BadRequestResponse as error:
        return render(request, _LIST_SECTION, {"load_error": error, "retry_href": ChannelNavigator.channel_summary_list_href()})
    return render(request, _LIST_SECTION, {"state": state})
```

- 페이지 템플릿은 오류로 갈리지 않는다 — section include에 `load_error`·`retry_href`를 함께 넘겨 section이 자기 루트 안에서 갈린다(§7). 조각 응답도 같은 section이라 오류 응답 뒤에도 교체 대상 id가 살아 있다.
- `retry_href`는 그 section을 다시 받는 조각 주소다 — view가 navigator의 `<화면>_<조각>_href(...)`로 얻는다(presentation → navigator는 허용 — discipline-houserules §5). State에 `load_error`·`retry_href` 필드를 두지 않는다(조회 실패에는 State가 없다).

- **오류 조각은 200으로 돌려준다**: htmx 2의 기본 응답 처리는 4xx·5xx 응답을 **교체하지 않는다**(`htmx:responseError` 이벤트만 난다) — 조회 실패 조각을 4xx·5xx 상태로 돌려주면 화면에 그려지지 않는다. `render(…)`의 기본 상태 200을 그대로 쓴다.
- **액션 단추는 데이터 조각 안에만**: `hx-post` 단추는 데이터가 그려진 section 안에만 둔다 — 오류 부품·로딩 부품 안에 액션을 두지 않는다. 액션 메서드는 build가 데이터를 만든 화면에서만 불린다는 전제가 이것으로 선다.
- 채널 ②(액션 실패)는 응답 section이 `state.error`를 한 번 그리고 끝난다 — State가 요청 사이에 남지 않으므로 응답이 곧 명시 소비 단위다(architecture-state §4).
- build의 raise는 view까지 그대로 온다 — `BadRequestResponse`를 다른 예외로 바꿔 던지지 않는다.
- 같은 내용 재대입의 알림 생략 같은 축은 web에는 해당 없음 — 구독·재빌드가 없고 응답 하나가 State 하나를 그린다.

## §6. 재조회 — 액션 응답 조각·HX-Trigger

- **액션 성공 후 재조회**: 조각 응답 함수가 VM 액션 메서드를 부르고, 액션 메서드는 성공하면 `self.build()`로 다시 조회한 State를 돌려준다 — 그 State로 같은 section을 render한 응답이 곧 재조회 결과다(architecture-state §4 정식 예제 — 응답 한 번에 액션과 재조회가 끝난다).
- 재조회 중 이전 값 유지는 htmx 기본이다(응답 전까지 교체하지 않는다). 페이지 전체를 처음부터 다시 그려야 하면 응답 헤더 `HX-Refresh: true` — 일상 재조회에 쓰지 않는다.
- **조각 요청 뒤 다른 페이지로 가야 하면** view는 `redirect(href)`를 돌려준다 — `RootRequestHandler.__call__`이 조각(`HX-Request`) 요청의 3xx를 200 + `HX-Redirect: <Location>`으로 바꿔 htmx가 전체 페이지 이동을 한다(로그인 이동 포함 — 조각 자리에 다른 페이지가 끼지 않는다 · implementation-django §2·§6). 조각 view가 `HX-Redirect`를 손으로 만들지 않는다.
- **같은 BC의 다른 조각 갱신 — `HX-Trigger` 응답 헤더**: 공유 값(SharedState)을 보여 주는 다른 조각이 있으면, 변화를 일으킨 응답이 그 SharedState의 이벤트 이름을 `HX-Trigger` 헤더에 싣고, 그 조각이 `hx-trigger="<이벤트> from:body"`로 다시 요청한다(architecture-state §5·§8):

```python
def order_list_add_fragment(request: HttpRequest, item_id: str) -> HttpResponse:
    cart: OrderCartSharedState = OrderCartSharedState(session=request.session)
    state: OrderListState = OrderListVM(cart=cart).add_to_cart(item_id)
    response: HttpResponse = render(
        request, "application/order/presentation_layer/section/order_list_rows_section.html", {"state": state}
    )
    response.headers["HX-Trigger"] = OrderCartSharedState.EVENT  # 공유 값이 바뀌었다 — 보는 조각은 다시 요청
    return response
```

```django
{# 장바구니 뱃지 조각 — 이벤트 이름과 주소는 State가 준다 #}
<span id="order-cart-badge" hx-get="{{ state.cart_badge_href }}"
      hx-trigger="{{ state.cart_event }} from:body" hx-swap="outerHTML">{{ state.cart_count }}</span>
```

- 이벤트 이름은 SharedState 관심사 명사(`<bc>-<관심사>`)이고 SharedState 클래스 상수 한 곳에서 온다 — 템플릿은 State가 실어 준 값을 쓴다. 과거형 사건명(`cart-added`)은 쓰지 않는다(architecture-state §5).
- `HX-Trigger`에 값을 실은 JSON 형태(`{"order-cart": …}`)는 쓰지 않는다 — 이벤트는 "다시 요청하라"는 신호이고, 값은 다시 받은 조각이 서버에서 가져온다.
- 타 BC 조각의 갱신 이벤트를 발행하거나 구독하지 않는다(architecture-state §7·§8 — 표기가 있다고 채널이 열리는 게 아니다). root만 BC SharedState 이벤트를 구독할 수 있다.

## §7. View 측 표기 — view 함수·조각 템플릿

```django
{# presentation_layer/view/channel_summary_view.html #}
{% extends "root/scaffold/view/root_view.html" %}
{% block content %}
  <div data-testid="channel-summary-view">
    {# 조회 실패면 section이 load_error·retry_href로 자기 루트 안에서 갈린다 #}
    {% include "application/channel/presentation_layer/section/channel_summary_list_section.html" with state=state load_error=load_error retry_href=retry_href %}
  </div>
{% endblock content %}
```

```django
{# presentation_layer/section/channel_summary_list_section.html — 조회·재시도·hx-post 응답 단위 (루트 id = 교체 대상) #}
<section id="channel-summary-list">
  {% if load_error %}
    {% include "design_system/component/feedback/error_feedback.html" with error=load_error retry_href=retry_href target_id="channel-summary-list" only %}
  {% else %}
    {% if state.error and state.error.is_show %}
      {% include "design_system/component/feedback/error_feedback.html" with error=state.error only %}
    {% endif %}
    {% for row in state.rows %}
      <article>
        <h3>{{ row.name }}</h3>
        <button type="button"
                hx-post="{{ row.leave_href }}"
                hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'
                hx-target="#channel-summary-list" hx-swap="outerHTML"
                hx-indicator="#channel-summary-loading">나가기</button>
      </article>
    {% endfor %}
    {% include "design_system/component/loading/spinner_loading.html" with loading_id="channel-summary-loading" only %}
  {% endif %}
</section>
```

**view 임베드 자리** — 다른 view(같은 BC든 타 BC든)를 화면 안에 넣는 자리는 부모 템플릿의 요소 하나다. 주소는 부모 VM이 자식 BC navigator의 `<화면>_embed_href()`로 받아 State에 담고, 자식 view 모듈의 셸 없는 첫 렌더 함수 `<화면>_embed_fragment`가 자기 VM의 `build()`로 자기 본문 section을 렌더한다(부모는 자식 VM을 부르지 않는다):

```django
{# 부모 템플릿 — 임베드 자리 하나(load 트리거는 이 자리만) #}
<div hx-get="{{ state.channel_summary_embed_href }}" hx-trigger="load" hx-swap="outerHTML"></div>
```

```python
# 자식: presentation_layer/view/channel_summary_view.py — 셸 없는 첫 렌더 (<화면>_<조각>_fragment 이름 규칙 안 · NM17 그대로)
def channel_summary_embed_fragment(request: HttpRequest) -> HttpResponse:
    try:
        state: ChannelSummaryState = ChannelSummaryVM().build()
    except BadRequestResponse as error:  # 임베드도 같은 section이 오류·재시도 자리를 그린다
        return render(request, _LIST_SECTION, {"load_error": error, "retry_href": ChannelNavigator.channel_summary_list_href()})
    return render(request, _LIST_SECTION, {"state": state})
```

- 자리 요소는 `outerHTML`로 자식 section 루트와 통째로 바뀐다 — 그 뒤의 재조회·재시도·액션은 자식 section의 루트 id를 대상으로 한다. 임베드 응답은 root_view를 extends하지 않는다(셸 없음).
- 자리 요소는 비어 있거나 로딩 부품 하나만 둔다 — 자식 화면 내용을 부모가 미리 그리지 않는다.

- 페이지 view는 페이지 템플릿을, 조각 응답 함수는 section 템플릿을 render한다 — 조각 응답은 HTML이다(JSON 응답을 만들지 않는다). 조각 전용 라우트로 받고, 한 함수 안에서 `HX-Request` 헤더로 페이지·조각을 갈라 쓰지 않는다.
- `outerHTML` 교체 응답의 section은 **같은 id 루트를 다시 포함**한다 — 교체 뒤에도 다음 요청의 대상이 살아 있다.
- 행마다 다른 주소(`row.leave_href`)는 VM이 navigator로 만들어 State의 행 값에 담는다 — 템플릿이 id를 이어 붙여 주소를 만들지 않는다(§4).
- 요청 원소는 의미에 맞게 — 동작 단추는 `<button type="button">`, 이동은 `<a href>`. 조각 응답 함수에도 페이지와 같은 `@login_required`를 붙인다 — 미로그인 302는 `RootRequestHandler`가 200 + `HX-Redirect`로 바꿔 전체 로그인 이동이 된다(§6·implementation-django §6).
- **전환이 명세된 교체**: htmx는 교체 중 `htmx-swapping`(나가는 쪽)·`htmx-settling`(들어오는 쪽) 클래스를 붙인다 — 그 클래스에 CSS 전환을 걸고(`--duration-*`·`--easing-*` 토큰 — implementation-django §10) `hx-swap`에 `swap:`/`settle:` 수식어를 함께 단다(`hx-swap="outerHTML swap:200ms settle:100ms"`). 기본 swap 지연 0ms·settle 20ms로는 클래스가 전환보다 먼저 사라진다.
- **`request`를 view 밖으로 반출하지 않는다**: VM·SharedState·UseCase에 `HttpRequest`를 넘기지 않는다 — 필요한 값만 꺼내 인자로 넘긴다(§3). `request`를 필드로 들고 다니는 객체는 이 위반이다.
- 커스텀 템플릿 태그로 VM·UseCase를 부르는 우회는 쓰지 않는다 — view 함수 + 템플릿 둘로 전 화면을 덮는다(architecture-ui §3).

## §8. 재시도 정책 — 자동 재시도 없음 (dddjango-web 확정)

**htmx는 실패한 요청을 스스로 다시 보내지 않는다** — 자동 재시도 없음이 기본값이라 끄는 설정 줄이 필요 없다. 재시도 장치(확장·JS 재전송 루프·`htmx:responseError`에서 다시 요청)를 붙이지 않는다.

- 실패는 즉시 오류 분기(채널 ①)로 표면화하고, 재시도는 사용자의 명시 행동이다 — 오류 부품의 «다시 시도» 단추가 같은 조각을 `hx-get`으로 다시 요청한다(주소는 view가 navigator로 얻어 맥락에 실은 `retry_href` · 대상은 section 루트 id `target_id` — §5):

```django
{# design_system/component/feedback/error_feedback.html — retry_href가 있을 때만 다시 시도 #}
<div class="error-feedback" role="alert">
  <p class="error-feedback__message">{{ error.msg }}</p>
  {% if retry_href %}
    <button type="button" class="error-feedback__retry"
            hx-get="{{ retry_href }}" hx-target="#{{ target_id }}" hx-swap="outerHTML">다시 시도</button>
  {% endif %}
</div>
```
- 서버 쪽도 재시도하지 않는다 — safe_api_call은 한 번 부르고 결과를 Either로 돌려준다(in-process라 일시적 네트워크 실패가 없다 — implementation-django §4).
- 주기 조회(`hx-trigger="every 30s"`)는 재시도가 아니라 명세가 정하는 갱신 방식이다 — 명세에 없으면 두지 않는다.

## §9. 금지 표면 — 인라인 JS 채널·확장·부스트

- **인라인 JS 채널**: `hx-on*` 속성(`hx-on:click`·`hx-on::after-request`) · `hx-vals`/`hx-headers`의 `js:` 접두 · `hx-trigger`의 `[조건식]` — 셋 다 htmx가 실행하는 임의 JS다. `on*` 이벤트 속성(`onclick=`)·`javascript:` 주소·인라인 `<script>` 실행도 같은 금지다(백스톱 PU3). 승인된 브라우저 동작은 외부 기능 JS로 둔다(implementation-javascript).
- **htmx 확장**(`hx-ext`·확장 스크립트) — 2.x에서 core 밖 별도 배포라 고정 판 밖이다. 쓰지 않는다.
- **`hx-boost`** — 링크·폼 전체를 부분 교체로 바꿔 주소 이동·스크롤 리셋 의미론을 깬다(탭 재탭 2단 동작 — implementation-django §3). 쓰지 않는다.
- `hx-swap`의 `transition:true`(View Transitions) — 전환 채널은 htmx 교체 클래스 + CSS 하나로 단일화한다(§7).
- `hx-delete`·`hx-put`·`hx-patch` — 상태 변경은 `hx-post` 하나다(Django는 POST 바디만 `request.POST`로 읽고, CSRF 경로도 하나로 둔다).
- 자동 이스케이프 우회(`|safe`)로 조각 HTML을 끼워 넣지 않는다(백스톱 PU7) — 조각은 include·render로 조립한다.

## §10. 백스톱 PU 연동 — 기계 집행 확보

출력 안전은 백스톱 러너의 **PU 패밀리**가 게이트에서 기계 집행한다 — 따로 등록할 lint 플러그인이 없다(`python3 "${CLAUDE_PLUGIN_ROOT}"/scripts/backstop.py <대상 프로젝트 루트> --only pu` — 러너·게이트 의미론은 discipline-houserules §8).

이 스킬 규약과 직접 겹치는 검사(켜져 있으면 규약이 기계 집행된다):

| 검사 | 이 스킬·짝 스킬의 규약 |
|---|---|
| PU1 — 신규 JS 경로·형태(htmx legacy core 이름 신설·기능 JS 평면 경로·vendor 자리는 등재 공식 SDK 사본만) | §1 · implementation-django §11 |
| PU2 — 실행 태그(로컬 `{% static %}` 한 번·classic은 `defer`·`async`·조각 안 로드·CDN 금지 · 등재 SDK 태그는 `src`·`defer` 만·페이지 block 안에서 그 SDK 를 부르는 기능 JS 태그보다 앞) | §1 · §9 · implementation-django §11 |
| PU3 — 인라인 JS 채널(`on*`·`hx-on*`·`js:`·`[조건식]`·스크립트 스킴 주소) | §9 |
| PU6 — 여러 줄 `{# #}` 주석 누출 | implementation-django §6 |
| PU7 — 자동 이스케이프 우회(`|safe`·`autoescape off`·`mark_safe`) | §9 · implementation-django §6 |
| PU8 — JS 동적 실행·외부 로드 | implementation-javascript §8 |
| PJ2 — htmx core 단일 설치·고정 판 | §1 |
| NM13 — 템플릿 `{% url %}`·경로 리터럴 | §4 |
| IM12 — application_layer의 django·`request` 의존 | §3 · §7 |

- **러너가 못 잡는 것**: hx-* 주소가 State의 href에서 왔는지(값의 출처)·GET 조각이 쓰기를 하는지·이벤트 이름 규칙(명사 관심사)·오류 조각의 상태 200 — 표기 규율과 discipline-reviewer 감사로만 강제된다.
