# web 구현 표기 — 시안 재현·삼총사·템플릿·HTMX·client·urls

> `web/` 트리 코드의 표기법 정본. 본문 속 위임은 «스킬명 + §번호(또는 주제)» 형이며 그것만 로드 대상이다. 무엇을 어느 조각에 담는가는 architecture-web, 파일의 자리·이름은 discipline-web-houserules 소유 — 여기는 그 자리에 놓일 코드를 어떻게 쓰는가다.

---

## 목차

- §1. 책임 범위와 handoff
- §2. 시안 재현 절차 — 재현이지 직수입이 아니다
- §3. 삼총사 표기 — view·view_model·state
- §4. 템플릿 표기
- §5. section·HTMX 표기
- §6. widget·design_system component 표기
- §7. 토큰·CSS·에셋 표기
- §8. client 표기 — in-process HTTP
- §9. urls 표기

---

## §1. 책임 범위와 handoff

이 스킬은 `web/` 트리에 놓이는 코드의 **표기법** 전반을 소유한다 — HTML 템플릿, 삼총사 `.py`(view·view_model·state)와 form, section·widget·design_system 조각, client, urls. «이 파일 안의 코드를 어떻게 쓰나»는 여기서 답하고, 그 외는 넘긴다:

| 질문 | 소유 |
|---|---|
| 무엇을 view/section/widget 어느 조각에 담나 — 판별·승격·계약 소비 절차 | `architecture-web`(판별 §2·승격 §5·계약 소비 §6) |
| 파일을 어느 폴더에 어떤 이름으로 만드나 — 트리·명명 사실 | `discipline-web-houserules` |
| 명명·함수 형태·캡슐화·중복 같은 보편 규율 | `discipline-cleancode` |
| 호스트 배선 — INSTALLED_APPS·TEMPLATES DIRS·STATICFILES_DIRS 프리픽스 튜플·ROOT_URLCONF include·ALLOWED_HOSTS("testserver" 포함)·htmx vendored 설치 | **Coordinator** — 커맨드 Phase 0 전제조건 검사 |
| BC 안 서버렌더 — driven_layer templates·Django admin | **비관할** — dddjango 플러그인 소관. 이 스킬의 관할은 `web/` 트리뿐이다 |

## §2. 시안 재현 절차 — 재현이지 직수입이 아니다

시안은 2형식으로 온다 — **디자인 이미지** 또는 **시안 HTML**(클로드 디자인 산출물, 또는 카피 대상 웹페이지). 어느 형식이든 시안은 *외형*의 근거이지 *코드*의 근거가 아니다. **시안 HTML의 마크업·클래스·인라인 스타일을 복붙하지 않는다** — *왜*: 직수입한 코드는 토큰·3단 분해·design_system 규범 밖에서 살아 유지 불능 섬이 된다.

절차:

1. **외형 관찰** — 렌더 결과 기준으로 배치·그룹핑·정렬·간격·반복을 읽는다. 시안 HTML도 소스가 아니라 렌더된 생김새가 관찰 대상이다.
2. **시각 값 추출** — 색·타이포·간격·radius·그림자를 `design_system/foundation/tokens.css`에 토큰으로 등록하고, 이후 그 토큰만 쓴다(§7).
3. **구조 재구축** — 마크업 구조는 시안에서 베끼지 않고 3단 분해(architecture-web §2)로 새로 세운다.
4. **이미지** — asset-manifest 경유로만 가져온다(§7).
5. **재사용 조각 대조** — 시안의 반복 요소는 기존 `design_system/component/`와 대조해, 있으면 그것을 쓰고 새로 만들지 않는다.

- 형상 근거는 산출물 폴더의 **동결 시안**이다 — 재현도 충실도 대조도 동결본 기준이며, 원본 웹페이지를 매번 다시 여는 것이 아니다.
- **보이는 요소는 빠짐없이 재현한다** — 시안에 보이는 요소를 임의로 생략하지 않는다. `<img>`의 위치·형제 순서도 시안 그대로다.
- 명세에 배치 서술이 없는 것은 정상이다 — 반송 사유가 아니다. 형상 근거는 산문이 아니라 시안이다.
- 시안이 없으면 coder-web 재량 + 기존 design_system 관례로 짓는다 — placeholder나 임의 발명으로 빈 곳을 조용히 채우지 않는다.
- 시안이 있는데 재현 불가한 요소(입수 불가 폰트·동적 효과 등)는 근사로 처리하되, **무엇이 근사인지 보고에 표면화한다** — 조용한 저하 금지.

## §3. 삼총사 표기 — view·view_model·state

역할 규율(view 진입점뿐·VM 표시 판정 유일 자리·state 불변·forms↔VM 분담)은 architecture-web §3 소유 — 여기는 각 파일의 표기다.

**`<view>_view.py` — 진입점 판형.** 함수 뷰로 고정한다 — *왜*: 진입점에 상속 계층이 필요할 만큼의 로직이 있으면 이미 규율 위반이다. 하는 일은 URL 바인딩·form 수신·세션 쿠키 추출(`request.COOKIES.get(settings.SESSION_COOKIE_NAME)` — VM에 전달, §8 신원 이월)·VM 호출·render, 그리고 fragment 분기까지가 전부다 — 판단하지 않는다. fragment 분기는 `request.headers.get("HX-Request")` 검사 또는 fragment 전용 라우트(§9) 중 하나로 하고, 한 화면 안에서 방식을 섞지 않는다.

**view auth 표기.** 로그인 요구 화면은 view 함수에 `@login_required`를 붙인다 — 미인증 요청은 `settings.LOGIN_URL`로 redirect되는 판형이다. 페이지 라우트와 fragment 라우트에 동일하게 붙인다 — fragment만 열려 있으면 보호가 우회된다.

**`<view>_view_model.py` — 조립 표기.** 생성자 또는 모듈 수준 조립 함수가 client(§8)를 호출하고, 응답 모델을 받아 state로 조립해 반환한다. view가 추출한 `session_key: str | None`을 인자로 받아 client 함수에 그대로 이월한다(§8) — VM은 세션을 해석하지 않고 운반만 한다. 계약 예외는 여기서 수신해 표시 상태(에러 문구·빈 목록 등)로 번역한다 — 예외를 view나 템플릿까지 흘리지 않는다.

**`<view>_form.py` — 입력 form 표기.** 입력 form이 있는 화면만 `form/` 종류 폴더에 조건 생성한다. 클래스명은 `<View>Form`이다 — 예: `order_create_form.py`의 `OrderCreateForm`. 입력 검증은 form이 소유하고(필드 clean·`is_valid()`), 표시 상태는 VM이 소유한다(분담 규율의 정본은 architecture-web §3). view가 form을 수신·검증해 valid면 `form.cleaned_data`를 VM에 넘기고, invalid면 form을 state의 form 필드에 담아 재렌더한다 — 템플릿은 그 필드로 form을 렌더한다. VM이 입력 검증을 재현하거나 form이 표시 상태를 조립하면 분담 위반이다.

**`<view>_state.py` — 표시 상태 표기.** `@dataclass(frozen=True)`. state 필드는 프리미티브(str·int·bool과 그 리스트)와 중첩 dataclass — 단 예외로 Django Form 1종 허용(검증 실패 재렌더 시 form을 state 필드로 운반, 템플릿은 그 필드로 form 렌더). 포매팅(가격 문자열·날짜 표기)은 state를 만드는 VM에서 끝낸다.

```python
# order_list_state.py
from dataclasses import dataclass


@dataclass(frozen=True)
class OrderRow:
    number: str
    total_display: str  # "12,000원" — 포매팅은 VM에서 완료


@dataclass(frozen=True)
class OrderListState:
    rows: list[OrderRow]
    error_message: str | None
```

Python 최소 관용구: 타입 힌트는 전면이다 — 모든 함수 매개변수·반환값과 모든 이름의 첫 대입에 붙인다. 모듈·함수는 snake_case, 클래스는 PascalCase, 상수는 UPPER_SNAKE. 공개 함수·클래스에는 한 줄 독스트링을 단다. 줄 길이·포맷은 대상 프로젝트의 기존 포매터 관례를 따른다(없으면 PEP 8) — 이 두 규칙은 discipline-cleancode가 이리로 위임한다. 그 이상의 언어·설계 규율은 `discipline-cleancode`.

## §4. 템플릿 표기

- `{% extends %}`는 첫 번째 비주석 줄에 둔다.
- block은 역할이 드러나는 이름을 붙이고 `{% endblock content %}`처럼 이름으로 닫는다.
- `{% load %}`는 여러 라이브러리를 알파벳순으로 유지한다.
- `{{ variable }}`·`{% tag %}` 안에는 한 칸 공백을 둔다.
- 템플릿은 **state만 참조**하고 표시 분기만 한다 — 계산·필터링·정렬이 필요하면 VM으로 가져간다. *왜*: 템플릿에 숨은 판단은 리뷰·재사용 어느 쪽에서도 안 보인다.
- URL은 `{% url %}`, 정적 자원은 `{% static %}` — 경로 하드코딩 금지.
- 일반 POST form 안에는 `{% csrf_token %}`을 둔다 — HTMX 요청의 토큰은 §5의 `hx-headers`.
- `|safe`는 근거 있는 신뢰 콘텐츠에 한해 최소로 쓴다.
- `base/base.html`은 «거의 빈» 골격이다 — 공통 문서 구조·내비 셸·공통 block만 두고, 화면 내용이 base로 새면 위반이다.
- 병치 템플릿(base/·화면 폴더의 .html)을 `{% extends %}`·`{% include %}` 경로로 찾는 것은 TEMPLATES `DIRS` 배선이 전제다 — 배선은 커맨드 Phase 0 소관(§1 handoff).

```html
{% extends "base/base.html" %}

{% block content %}
  {% if state.error_message %}
    <p class="notice-error">{{ state.error_message }}</p>
  {% endif %}
{% endblock content %}
```

## §5. section·HTMX 표기

section은 화면 전속 조각이자 HTMX 부분 재렌더 단위다(역할 규율은 architecture-web §4). 파일명은 `<view>_<section>.html` — 화면 접두 필수.

- 동작은 htmx 허용 속성 목록으로만 표기한다 — `hx-get`·`hx-post`(URL은 `{% url %}`), `hx-target`(교체될 요소 선택자), `hx-swap`(교체 방식 — 조각 내부 교체는 기본 `innerHTML`, 요소 자체 교체는 `outerHTML`), `hx-headers`(state-changing의 CSRF 토큰), `hx-trigger`(발동 이벤트 — 기본 트리거로 충분하면 생략).
- method 의미론을 지킨다 — 조회 재렌더는 `hx-get`, state-changing은 `hx-post`.
- state-changing(`hx-post`) 요청의 CSRF는 `hx-headers`의 토큰으로 보낸다 — 조회(`hx-get`)에는 붙이지 않는다.
- state-changing 요청도 페이지 요청과 같은 auth·permission·CSRF를 통과해야 한다 — HTMX라고 보호 수준을 낮추지 않는다.
- 페이지 템플릿이 section을 include할 때는 state를 명시 전달한다 — `{% include "..." with state=state %}` 판형. `only` 의무는 widget·component include 한정이다(§6).
- fragment 응답은 소속 view가 해당 section 템플릿을 render한 HTML이다 — JSON 응답을 만들지 않는다.
- **커스텀 JS 금지.** 동작은 htmx 속성으로만 표현하고, 템플릿 inline `<script>` 금지, `web/**`에 `.js` 파일 신설 금지 — *왜*: 이 플러그인의 기술 표면은 순수 HTML+HTMX+CSS이며, 백스톱이 위반을 기계 차단한다.
- htmx 자체는 `static/js/`의 vendored 단일 파일이 유일한 JS다 — CDN `<script src>` 금지.

```html
{# order_list_rows.html을 소유한 화면 어디서든 — 조회 재렌더 트리거 판형(hx-get — CSRF 토큰 불요) #}
<button hx-get="{% url 'orders:order_list_rows' %}"
        hx-target="#order-rows" hx-swap="outerHTML">새로고침</button>
```

## §6. widget·design_system component 표기

widget(영역 재사용 조각)과 design_system component(전역 순수 부품)는 **명시 context로만** 산다 — `{% include %}`에 `with … only`를 붙인다. `only`는 widget·component include 한정 의무다(페이지→section include는 §5의 state 명시 전달 판형) — *왜*: 화면 비전속 조각이 암묵 context 상속에 기대면 어느 화면에서 어떤 변수로 사는지 추적할 수 없게 된다.

```html
{% include "design_system/component/badge/count_badge.html" with count=state.order_count tone="primary" only %}
```

- widget 파일명에 화면 이름을 넣지 않는다 — 화면 이름이 필요해졌다면 그것은 section이다(판별 architecture-web §2·승격 §5).
- component는 부품군 폴더 1차(`component/<부품군>/<component>.html`)에 둔다 — `component/` 직속 파일 금지.
- component에는 BC 어휘 금지 — «order»·«member» 같은 도메인 이름이 필요하면 그것은 component가 아니라 widget 또는 section이다.

## §7. 토큰·CSS·에셋 표기

**토큰.** `design_system/foundation/tokens.css`가 `:root` custom properties로 색·타이포·간격·radius·그림자를 정의한다. CSS와 템플릿의 스타일 값은 `var(--…)`만 쓴다 — 리터럴(`#2563eb`·`14px` 직접 기입) 금지. *왜*: 시안 값이 토큰 한 곳에 모여야 충실도 대조와 일괄 변경이 성립한다. 시안 절단 산출물(tokens.css 초안)이 있으면 그 토큰 이름을 그대로 쓴다 — 발명 금지. tokens.css가 `{% static %}` 경유로 서빙되는 것은 STATICFILES_DIRS 프리픽스 튜플 배선이 전제다 — 배선은 커맨드 Phase 0 소관(§1 handoff).

```css
:root {
  --color-primary: #2563eb;
  --space-md: 1rem;
  --radius-card: 0.5rem;
}

.card {
  border-radius: var(--radius-card);
  padding: var(--space-md);
}
```

**이미지.** 시안의 정적 이미지는 동결 단계(fetch_images)가 `static/images/`에 내려받아 `asset-manifest.json`(src→`local_path`→`token` 매핑·단일 SSOT)으로 절단한다. 명세가 가리킨 이미지는 manifest의 **같은 `src` 행**으로 조인해 `local_path`를 정확 값 그대로 가져온다 — 추정·눈대중·발명 금지(server-contract를 경량본에서 인용하듯). `token` 열은 web에서 소비하지 않는다 — 추출 도구 산출 호환용이다. 템플릿 배선은 `local_path`를 `{% static %}` 경유로 참조하는 것만이고 raw 경로 문자열은 금지다. manifest가 없으면 이 항목은 적용되지 않는다 — 없는 이미지를 placeholder로 조용히 채우지 않는다.

## §8. client 표기 — in-process HTTP

in-process 호출 메커니즘은 `django.test.Client`로 고정한다 — *왜*: Django가 제공하는 유일한 완전 in-process HTTP 호출기라서다. 네트워크를 타지 않으면서 URL 라우팅·미들웨어·인증을 통과한다. CSRF는 여기 없다 — CSRF는 브라우저→web view 경계에서 1회 검증되고(웹 폼·hx 요청의 토큰, §4·§5), client의 내부 호출은 CSRF 검사 대상이 아니다(`enforce_csrf_checks` 기본값 유지).

- client는 `Client(raise_request_exception=False)`로 생성한다 — *왜*: 백엔드 미처리 예외를 원시 관통 대신 500 응답으로 수신해 계약 예외로 변환하기 위해서다.
- 각 `<capability>_client.py`가 client를 직접 만들어 호출한다 — 공통 호출기·베이스 클래스 없음.
- client 인스턴스는 호출 함수 안에서 생성한다 — 모듈 전역 공유 금지. *왜*: client는 쿠키·세션을 보유하므로 공유하면 요청 간 상태가 샌다. 매 호출 생성 비용은 인지하되 감수한다 — in-process 객체 생성이라 미미하고, 상태 격리가 우선이다.
- **신원 이월.** view가 `request.COOKIES`에서 추출한 세션 쿠키 값이 VM 경유로 client 함수에 `session_key: str | None` 인자로 도착한다(§3). client는 `client.cookies[settings.SESSION_COOKIE_NAME] = session_key`로 심는다 — None이면 미설정, 즉 익명 호출이다.
- URL 경로에 값을 조립할 때는 `urllib.parse.quote`로 인코딩한다.
- 응답 JSON은 파싱해 `response/`의 dataclass 응답 모델로 변환해 반환한다 — dict를 VM으로 흘리지 않는다. 변환은 응답 모델의 `from_json` classmethod가 소유하며, 누락 키·타입 불일치는 계약 예외로 raise한다 — 조용한 기본값 채움 금지.
- 비정상 상태코드·계약 위반 응답은 `exception.py`의 계약 예외로 변환해 raise한다 — VM은 예외 타입만 알고 상태코드를 모른다.
- **계약의 단일 근거는 산출물 폴더의 `server-contract.json` 경량본이다** — URL·필드·상태코드를 훈련 기억이나 추측으로 쓰지 않는다. 경량본에 없는 API가 필요하면 구현하지 말고 «/dddjango로 발주»로 보고한다.
- BC API URL 리터럴의 유일 거처는 client 모듈이다 — VM·view·템플릿에 백엔드 URL이 나타나면 위반이다.
- 호스트 배선(`ALLOWED_HOSTS`에 "testserver" 포함 등)은 커맨드 Phase 0 전제조건 검사 소관이다 — §1 handoff.

```python
# payment_client.py
from urllib.parse import quote

from django.conf import settings
from django.test import Client

from web.client.payment.exception import PaymentContractError, PaymentNotFoundError
from web.client.payment.response.payment_response import PaymentResponse


def fetch_payment(order_number: str, session_key: str | None) -> PaymentResponse:
    """주문 번호로 결제 정보를 조회한다."""
    client: Client = Client(raise_request_exception=False)
    if session_key is not None:
        client.cookies[settings.SESSION_COOKIE_NAME] = session_key
    response = client.get(f"/api/payments/{quote(order_number)}")  # URL 근거: server-contract.json
    if response.status_code == 404:
        raise PaymentNotFoundError(order_number)
    if response.status_code != 200:
        raise PaymentContractError(response.status_code)
    return PaymentResponse.from_json(response.json())
```

## §9. urls 표기

라우트 리터럴 단일 출처 규율은 architecture-web §7 소유 — 여기는 표기다.

- 영역 `urls.py`가 그 영역의 `path()`와 `name`을 정의한다 — fragment 전용 라우트(§3·§5)도 소속 화면과 같은 영역 urls에 둔다.
- 웹 루트 `web/urls.py`는 영역 urls를 `include()`로 합산만 한다 — 루트에 직접 `path()`를 정의하지 않는다.
- 영역 urls 머리에 `app_name = "<screen_area>"` 네임스페이스를 선언한다.
- name 참조는 항상 네임스페이스 경유다 — 템플릿은 `{% url 'orders:order_list' %}`, 파이썬은 `reverse("orders:order_list")`. 경로 문자열 하드코딩 금지는 §4와 같다.
- name은 화면 개념 이름을 따르고, fragment 라우트는 `order_list_rows`처럼 «화면_조각» 형으로 소속을 드러낸다.
