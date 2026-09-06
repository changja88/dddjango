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

1. **비교 기준 확인** — 최초 준비/검증 시 [`design-evidence.md`](design-evidence.md)의 기계 인터페이스를 읽는다. `design-input.json`의 전체 case·scope_refs·entrypoint와 manifests·원본 captures·구체 승인 출처를 직접 받으며 Coordinator의 현재 inputs 성공을 확인한다. JSON의 경로와 hashes는 원본 내용을 요약하는 형상 명세가 아니다. `visual-check.md`의 선택 화면·상태·viewport·동결 렌더를 읽는다. 재개·변경 작업도 이 기준 버전으로 대조한다. 다른 버전의 컴포넌트 내부 값을 과거 시안의 값으로 간주하지 않으며, 원본이 없는 항목은 확인 불가로 구별한다. HTML 파일만 있고 실제 렌더나 대응 스크린샷이 없으면 시각 구현 입력이 아직 준비되지 않은 것이다. 소스를 렌더 결과로 간주하지 않고 Coordinator에 부족한 입력을 돌려준다.
2. **요소 대응** — 보이는 요소와 조건부 요소의 현재 상태를 확인한다. 화면 경계·컨테이너 폭/높이·여백·flex spacer·정렬·형제 순서·타이포·장식·구분선·아이콘·component variant가 대조 대상이다. 외부 캔버스/목업과 앱 화면 경계는 선택된 렌더와 소스 근거로 구별한다. 고정 치수를 목업으로 단정하거나 다른 content-max·뷰포트 정렬로 재해석하지 않는다. 다른 viewport의 반응형 거동은 확인된 요구를 따른다.
3. **정확한 시각 값 등록** — 원본 값과 같은 기존 토큰은 재사용한다. 필요한 값이 없으면 출처(파일·요소·상태/실측)를 붙여 `tokens.css`에 새 토큰을 등록한다. 가까운 크기·행간·색·padding으로 반올림하지 않는다. 이미지뿐인 시안의 측정값은 추정임을 표시하고 대조한다. 토큰 개수의 일치는 요소별 매핑의 증거가 아니다.
4. **구조 재구축·자산 배선** — 마크업은 3단 분해로 다시 작성하고, 같은 외형·variant를 지원하는 기존 component를 재사용한다. 자산은 manifest의 검증된 로컬 파일로 배선한다(§7). 원본 JS·JSX는 렌더 근거로 보관할 수 있으나 앱 코드로 직수입하지 않는다.
5. **실제 출력 확인** — 변경 페이지/fragment를 실제 Django 설정과 design-input의 해당 요구 case별로 렌더해 출력 내용을 확인한다. 함수 호출 성공·문자열 길이만 확인하고 HTML을 버리지 않는다. 브라우저에서 이미지·폰트 로드, 문구/주석 누출, viewport별 화면 전체, 관련 상태·상호작용을 확인한다. 실행 명령/URL·상태·viewport·스크린샷·발견과 수정 후 재확인을 보고하고 Coordinator가 `visual-check.md`에 통합한다.

**스타일 적용 근거** — 위 2~5를 변경 범위의 요소·variant·상태별로 연결한다: `원본 위치·시각 값/효과 구성 → 사용 토큰·구현 위치 → 실제 적용 확인·차이/미검증`. 원본이 정한 색·타이포·간격과 배경·테두리·투명도·그림자·필터 등 효과 구성을 대조하며, 복합 효과의 각 층과 자식/가상 요소, 상태별 덮어쓰기를 빠뜨리지 않는다. 토큰 하나를 사용했다는 사실은 전체 조합을 재현했다는 증거가 아니다. 풀 밖 값은 step 3으로 등록하고, 필요한 토큰·자식 요소 파일이 슬라이스 밖이면 Coordinator가 소유 파일 슬라이스를 재개하도록 반송한다. 효과를 생략해 슬라이스를 닫지 않는다.

이 근거는 기존 코더 보고에 남겨 `visual-check.md`의 요소 대조에 연결한다. 모든 CSS 속성의 개별 행이나 미사용 토큰 전량 소비를 요구하지 않는다. 동일 component·variant·상태의 근거는 적용 화면을 적어 재사용하고, 구현 위치의 토큰/합성 값을 풀어 원본과 대조한다. 다른 토큰 이름·등가 CSS 구성도 같은 외형이면 허용한다. 계산된 스타일은 적용 확인에 활용하되 가림·클리핑·주변 효과를 포함한 실제 렌더 대조를 대신하지 않는다. 원본 근거가 없는 항목을 근접 토큰으로 채우거나 코드 대조만으로 시각 검증 완료로 바꾸지 않는다.

- 시안의 형상과 승인 명세가 충돌하면 반송한다. **외형을 변경할 근거는 명세의 해당 이탈 행과 그 구체적 결정 근거**다(architecture-web §1). 보고했다는 사실이나 포괄적 명세 승인은 누락된 변경의 승인이 아니다.
- 사용자 요구로 조건부 요소를 표시/숨기기로 정했다면 그 결정 상태를 재현한다. 소스에 선언돼 있다는 이유만으로 숨김 요소를 표시하지 않는다.
- 재현 불가한 자산·효과는 실패 원인과 가능한 복구/대체를 보고하고, 해당 이탈 결정 후 구현한다. 기술 제약이 자동으로 삭제·placeholder 사용을 승인하지 않는다.
- 시안이 애초에 없으면 기존 design_system과 사용자 요구로 자체 설계한다. 수집 실패와 이 정상 경로를 구별한다. 정적 화면 한정에서는 시안의 데이터성 텍스트를 견본 값으로 유지한다.
- 영구 테스트 파일을 만들지 않는 정책은 임시 렌더·브라우저 검증을 금지하지 않는다. 임시 실행 코드는 폐기해도 결과·스크린샷·미실행 사유는 산출물 폴더에 남긴다. 브라우저 실행이 불가하면 검증 상태는 `미검증`이며 완료 근거를 대신 만들지 않는다.

**완료 증거** — Coordinator가 실제 관찰 회차의 fingerprint 출력으로 `visual-evidence.json`을 작성한다. 비교 산문은 `visual-check.md`에 두며 모든 요구 case와 동일 viewport를 연결한다. 원본/구현 캡처는 각각 실제 생성한 별도 파일이다. 시안 대상 최종 완료는 visual 게이트와 독립 시각 감사 통과 후이며 미검증 사용자 수락으로 verified를 만들지 않는다. 변경 후에는 영향 case 재관찰·재감사와 영향 없는 case의 독립 재사용 확인을 거쳐 현재 회차를 확정한다. hash 교체만으로 새 관찰을 만들지 않는다. 아직 화면이 없는 데이터 슬라이스는 visual 비적용이다.

**실제 API 자산** — case에 사용자가 지정한 환경·endpoint·identity/src JSON Pointer를 연결한다. 그 환경의 실제 응답과 브라우저 요청 src·로드·영상 재생 증가를 원문으로 남겨 Coordinator에 전달한다(`design-evidence.md`의 media 계약). 임시 DB seed·샘플은 격리 기능 test에만 사용하고 실제 사용자 프리뷰에 넣지 않는다. API/인증/재생 실패는 해당 범위와 필요한 외부 조건을 구체 보고하며 blocked/unverified 또는 failed로 남긴다. 민감 응답·서명 URL은 로컬 비공개 증거에만 보존하고 credentials/headers를 기록하지 않는다.

## §3. 삼총사 표기 — view·view_model·state

역할 규율(view 진입점뿐·VM 서버 표시 판정 유일 자리·state 불변·forms↔VM 분담)은 architecture-web §3 소유 — 여기는 각 파일의 표기다.

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
- Django 짧은 주석 `{# … #}`는 한 줄만 쓴다. 여러 줄은 `{% comment %}…{% endcomment %}`로 감싼다. 여러 줄 `{# … #}`는 그대로 응답에 새어 나온다(WP6).
- block은 역할이 드러나는 이름을 붙이고 `{% endblock content %}`처럼 이름으로 닫는다.
- `{% load %}`는 여러 라이브러리를 알파벳순으로 유지한다.
- `{{ variable }}`·`{% tag %}` 안에는 한 칸 공백을 둔다.
- 템플릿은 **state만 참조**하고 표시 분기만 한다 — 계산·필터링·정렬이 필요하면 VM으로 가져간다. *왜*: 템플릿에 숨은 판단은 리뷰·재사용 어느 쪽에서도 안 보인다.
- URL은 `{% url %}`, 정적 자원은 `{% static %}` — 경로 하드코딩 금지.
- 일반 POST form 안에는 `{% csrf_token %}`을 둔다 — HTMX 요청의 토큰은 §5의 `hx-headers`.
- `|safe`는 근거 있는 신뢰 콘텐츠에 한해 최소로 쓴다.
- `base/base.html`의 입장 목록은 discipline-web-houserules의 판별 절차(undecidable-web §6)가 단독 소유한다 — 공통 문서 골격·내비 셸 외 화면 어휘 금지.
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

- 서버 요청·교체는 htmx 허용 속성 목록으로 표기한다 — `hx-get`·`hx-post`(URL은 `{% url %}`), `hx-target`(교체될 요소 선택자), `hx-swap`(교체 방식 — 조각 내부 교체는 기본 `innerHTML`, 요소 자체 교체는 `outerHTML` · 전환이 명세된 교체는 `swap:`/`settle:` 타이밍 수식어를 함께 — §7 모션 · `transition:true`는 금지), `hx-headers`(state-changing의 CSRF 토큰 — `js:` 접두 금지), `hx-trigger`(발동 이벤트 — 기본 트리거로 충분하면 생략 · 이벤트 이름만, `[조건식]` 대괄호 JS 금지).
- method 의미론을 지킨다 — 조회 재렌더는 `hx-get`, state-changing은 `hx-post`.
- state-changing(`hx-post`) 요청의 CSRF는 `hx-headers`의 토큰으로 보낸다 — 조회(`hx-get`)에는 붙이지 않는다.
- state-changing 요청도 페이지 요청과 같은 auth·permission·CSRF를 통과해야 한다 — HTMX라고 보호 수준을 낮추지 않는다.
- 페이지 템플릿이 section을 include할 때는 state를 명시 전달한다 — `{% include "..." with state=state %}` 판형. `only` 의무는 widget·component include 한정이다(§6).
- fragment 응답은 소속 view가 해당 section 템플릿을 render한 HTML이다 — JSON 응답을 만들지 않는다.
- **UI JS는 승인된 UI 동작 계약만 구현한다.** `static/js/<기능>.js`에 기능당 한 파일을 두고 native HTML/CSS로 충분하면 만들지 않는다. DOM·이벤트·자원 수명·키보드·실패 표기는 implementation-javascript를 따른다. 업무 권한·금액·저장 판정·별도 업무 API 호출·SPA 상태 계층은 금지다.
- 신규 HTMX core는 `static/htmx/htmx.min.js`이며 기존 `static/js/htmx.min.js`·`htmx.js`는 브라운필드 설치로만 소비한다. 중복 설치·조용한 이동/업그레이드·CDN 실행 태그 금지. motion.js는 기존 조건 설치와 byte 고정 판형을 유지한다(houserules §5⑤).

```html
{# order_list_rows.html을 소유한 화면 어디서든 — 조회 재렌더 트리거 판형(hx-get — CSRF 토큰 불요) #}
<button hx-get="{% url 'orders:order_list_rows' %}"
        hx-target="#order-rows" hx-swap="outerHTML">새로고침</button>
```


**선언 조각과 로드.** HTMX 선언을 `static/htmx/<기능>.html`에 기능당 하나로 모으고 페이지/section에서 Django include로 렌더한다. web 루트가 기존 TEMPLATES DIRS에 있으므로 include 인자는 `static/htmx/...`다. public static 원문에는 비밀·사용자별 렌더 결과를 저장하지 않는다. 서버 값은 include 렌더 시 전달하며 데이터·권한·CSRF·fragment 응답은 소속 view/section이 유지한다. `{% static 'web/htmx/...' %}` URL을 업무 fragment endpoint로 쓰지 않는다. 새 finder·middleware·템플릿 엔진은 만들지 않는다.

```html
{# static/htmx/order_refresh.html — 재사용하는 요청 선언; 실제 응답은 section #}
<button type="button" hx-get="{% url 'orders:order_list_rows' %}"
        hx-target="#order-rows" hx-swap="outerHTML">새로고침</button>
```

```html
{# order_list의 section 또는 페이지 #}
{% include "static/htmx/order_refresh.html" with state=state %}
{# order_list_rows.html 자체가 id="order-rows" root를 포함한다 #}
{% include "orders/order_list/section/order_list_rows.html" with state=state %}
```

실제 outerHTML 응답의 section은 같은 `id="order-rows"` root를 포함하도록 작성한다. include 파일은 응답 소유자나 새 템플릿 계층이 아니다. state-changing 선언에서는 렌더 시 CSRF를 명시 전달하고 escape된 `hx-headers` 값으로 소비한다.

기능 실행 태그는 base의 공통 로드 또는 페이지의 범용 scripts block에 외부 static 참조로 페이지당 한 번만 둔다. 해당 파일의 실재·응답을 확인한다. fragment와 선언 조각에는 실행 script가 없다. classic은 `defer`, 기존 module 방식은 허용하고 `async`로 순서를 깨지 않는다. inline 실행 JS·on* handler·hx-on·js:·hx-trigger 조건식은 계속 금지한다.

```html
{# base/base.html — core는 설치된 경로를 한 번 로드; 신규 표준 #}
<script src="{% static 'web/htmx/htmx.min.js' %}" defer></script>
{% block scripts %}{% endblock scripts %}
```

```html
{# 페이지의 범용 scripts block — fragment에 복제하지 않는다 #}
{% block scripts %}
  <script src="{% static 'web/js/password_visibility.js' %}" defer></script>
{% endblock scripts %}
```

서버 구조화 데이터는 `{{ state.ui_data|json_script:"ui-data" }}`의 비실행 JSON을 외부 JS에서 textContent→JSON.parse로 소비한다. 단일 값은 정상 escape된 quoted `data-*` 속성으로 충분할 수 있다. 반복 UI라면 JSON id도 유일하게 정한다. 수동 JSON 조립·템플릿 값의 실행 소스 보간은 금지다.

## §6. widget·design_system component 표기

widget(영역 재사용 조각)과 design_system component(전역 순수 부품)는 **명시 context로만** 산다 — `{% include %}`에 `with … only`를 붙인다. `only`는 widget·component include 한정 의무다(페이지→section include는 §5의 state 명시 전달 판형) — *왜*: 화면 비전속 조각이 암묵 context 상속에 기대면 어느 화면에서 어떤 변수로 사는지 추적할 수 없게 된다.

```html
{% include "design_system/component/badge/count_badge.html" with count=state.order_count tone="primary" only %}
```

- widget 파일명에 화면 이름을 넣지 않는다 — 화면 이름이 필요해졌다면 그것은 section이다(판별 architecture-web §2·승격 §5).
- component는 부품군 폴더 1차(`component/<부품군>/<component>.html`)에 둔다 — `component/` 직속 파일 금지.
- component에는 BC 어휘 금지 — «order»·«member» 같은 도메인 이름이 필요하면 그것은 component가 아니라 widget 또는 section이다.

## §7. 토큰·CSS·에셋 표기

**토큰.** `design_system/foundation/tokens.css`가 `:root` custom properties로 색·타이포·간격·radius·그림자·모션 값(`--duration-*`·`--ease-*` 류)을 정의한다. CSS와 템플릿의 스타일 값은 `var(--…)`만 쓴다 — 리터럴(`#2563eb`·`14px` 직접 기입) 금지. *왜*: 시안 값이 토큰 한 곳에 모여야 충실도 대조와 일괄 변경이 성립한다. 시안 절단 산출물(design-tokens.json)의 기존 토큰은 이름·값을 보존해 쓴다. 풀에 없는 정확한 시안 값은 §2에 따라 출처를 붙여 신규 토큰으로 등록한다. 임의 시각 값 발명과 근접 토큰 대체는 금지다. tokens.css가 `{% static %}` 경유로 서빙되는 것은 STATICFILES_DIRS 프리픽스 튜플 배선이 전제다 — 배선은 커맨드 Phase 0 소관(§1 handoff).

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

**베이스 리셋.** 화면 CSS의 리셋 절은 box-sizing·html/body 여백 0과 함께 **UA 기본 스타일 정규화**를 포함한다 — 최소 `p { margin: 0; }` 등 문단·제목류 기본 마진 0. *왜*: 시안(컴포넌트 렌더·디자인 산출물)은 문단 기본 마진이 없는 세계라, `<p>`를 쓰는 순간 브라우저 UA 마진이 시안에 없는 간격을 만든다 — 필요한 간격은 리셋 위에 토큰으로 명시한다.

**모션.** 근거는 설계 명세의 동적 표현 처분(architecture-web §8)뿐이다 — 명세에 없는 모션 발명 금지·«한계» 항목 구현 금지. **처분 표가 지정한 셀렉터·`@keyframes` 명·`data-motion` 토큰을 그대로 쓴다 — 개명·발명 금지**(`check_motion_spec`은 CSS/keyframes·data-motion의 정적 대조를 보조한다 — 이 이름들이 조인 키다. UI JS의 실제 모션·누락/발명 전수성은 정적 검사로 증명하지 않는다).

- **상태 규칙**(`:hover`·`:focus-visible`·`transition`)은 해당 요소의 화면 CSS·component CSS에 직접 쓴다 — duration·easing 값은 tokens.css의 `var()` 참조.
- **`@keyframes`**: 공용(스피너·페이드 류 재사용 모션)은 `design_system/foundation/motion.css`에 `motion-*` 이름으로, 화면 전속은 그 화면 CSS에 `<view>_` 접두로 둔다. motion.css에는 custom property 정의 금지 — keyframes·유틸 클래스 선언만(중간값 리터럴은 허용).
- **htmx 교체 전환**: `htmx-swapping`(퇴장)·`htmx-settling`(진입)·`htmx-request`(요청 중 — 로딩 표시) 클래스에 CSS transition을 건다. 전환이 명세된 교체는 **`hx-swap`에 `swap:`/`settle:` 타이밍 수식어가 필수**다 — 예 `hx-swap="innerHTML swap:200ms settle:100ms"`. *왜*: htmx 기본은 swap 0ms·settle 20ms라 수식어 없이는 클래스가 transition보다 먼저 사라져 전환이 보이지 않는다. `hx-swap`의 `transition:true`(View Transitions)는 금지 — 전환 채널은 CSS 클래스 하나로 단일화한다.
- **UI JS 모션**: `ui-js` 채택 행의 `static/js/<기능>.js :: [data-<root>]`를 UI 동작 계약과 일치시킨다. 필요한 시각 값은 CSS 토큰으로 읽고 초기 발동·적용되는 실제 swap·자원 정리·감속 선호 경로를 브라우저로 검증한다. 러너 파일을 확장해 넣지 않는다.
- **러너 소비**(motion.js가 설치된 빌드만): 명세가 «러너»로 채택한 항목만 요소에 `data-motion="<모션명>"`을 선언한다 — 러너가 뷰포트 진입 시 `motion-in` 클래스를 부여한다(one-shot). **초기 은닉은 `html.motion-ready` 하위 셀렉터 + `@media (prefers-reduced-motion: no-preference)` 안에서만** 쓴다 — 판형: `@media (prefers-reduced-motion: no-preference){ html.motion-ready [data-motion]{ opacity:0; } html.motion-ready [data-motion].motion-in{ opacity:1; transition: opacity var(--duration-reveal) var(--ease-out); } }`. *왜*: 러너 실패·차단·감속 선호 사용자에게 콘텐츠가 영구 숨김되지 않는다(motion-ready 없는 문서에서 은닉 규칙은 발화하지 않는다).
- **base.html 로드 태그 판형**(base 입장은 `undecidable-web.md` §6): `<link rel="stylesheet" href="{% static 'design_system/foundation/motion.css' %}">` — tokens.css 다음 줄. motion.js가 설치된 빌드만 `<script src="{% static 'web/js/motion.js' %}" defer></script>` — htmx 태그 다음 줄·`defer` 필수.

**배치 거동(고정 오버레이).** 근거는 설계 명세의 배치 거동 결정(architecture-web §8)이다 — 명세에 없는 고정 요소 발명 금지.

- 스크롤 중 화면에 붙는 바·헤더는 `position: sticky`(+`top`/`bottom` 명시)를 기본으로 한다. sticky는 **가장 가까운 스크롤 컨테이너**에 고정된다 — 따라서 sticky 요소와 그것이 붙어야 할 스크롤포트(문서 스크롤이면 뷰포트, 내부 스크롤 패널이면 그 패널) **사이의 중간 조상**에는 스크롤 컨테이너를 만드는 overflow 값(`hidden`·`auto`·`scroll` — 어느 축이든)을 두지 않는다. 의도한 스크롤 컨테이너 자체의 `overflow: auto|scroll`은 정당하다 — 그 안에 고정하려는 sticky의 기준이 바로 그것이다. *왜*: 선언(`position: sticky; bottom: 0`)이 정확해도 셸·래퍼의 overflow 한 줄이 기준 스크롤포트를 가로채 조용히 무력화한다 — 무력화된 바는 문서 끝에서는 보이므로 «끝까지 스크롤» 확인으로는 못 잡는다.
- 래퍼·셸의 가로 삐짐 클립이 필요하면 `overflow-x: clip`을 쓴다 — 스크롤 컨테이너를 만들지 않는 유일한 클립이다(타 축의 visible 강등 없음). 단 `hidden`과 달리 BFC를 만들지 않으므로 필요 시 `display: flow-root`를 병용하고, 단일 축 clip에는 `overflow-clip-margin`이 적용되지 않는다. html/body **단독**의 `overflow-x: hidden`은 뷰포트로 전파되어 무해하나 일관성 위해 clip을 쓴다.
- 말줄임(`overflow: hidden`+`text-overflow: ellipsis`) 리프·카드 이미지 클립처럼 **사슬 밖** 사용은 그대로 정당하다 — 금칙은 sticky/fixed와 스크롤포트 사이의 중간 조상에만 적용된다.
- 문서 흐름 밖 전역 오버레이(모달 류)만 `fixed`로 한다. **fixed 요소의 조상 사슬에 transform·filter·backdrop-filter·`will-change: transform`이 있으면 containing block을 빼앗겨 무력화된다** — 진입 모션의 transform이 조상에 남지 않게 한다(모션 판형과의 인터롭).
- sticky/fixed 바는 불투명 배경 토큰 필수 — 아래로 지나가는 콘텐츠가 비치지 않게 한다.

**이미지·파일.** 시안 파일은 Coordinator가 실제 바이트를 수집해 `design-ref/`에 보관한다. 수집 manifest는 출처·로컬 경로·크기·SHA-256·성공/실패 사유를 담는다. 렌더용 CSS·JS·JSX·폰트 등 원본 의존성과 앱에 배선할 자산을 구별한다. 이미지 인벤토리는 `asset-manifest.json`이며 성공 여부와 무관하게 전달받는다. `failed/skipped`는 이미지 없음이 아니다.

이미지는 manifest의 해당 문서·해소된 출처 행으로 조인해 검증된 `local_path`를 그대로 쓴다. 착지는 `web/static/images/`, `{% static %}` 인자는 프로젝트 경로의 `web/static/`를 static 프리픽스 `web/`로 바꾼 값이다(예: `web/static/images/logo.png` → `{% static 'web/images/logo.png' %}`). source CSS의 이미지 `url()`도 이 매핑을 따라 배선한다. 폰트·다운로드 파일이 필요하면 `web/static/fonts/`·`web/static/files/`에 검증된 파일을 복사하고 출처→배선 경로를 같은 검증 기록에 남긴다. 골격으로 미리 만들지는 않는다.

파일 존재·HTTP 200·CSS 선언만으로 로드를 판정하지 않는다. 브라우저에서 이미지 decode/naturalWidth, 네트워크 오류, 실제 폰트 face·weight 로드와 적용을 확인한다. 폰트 URL을 기억으로 조립하지 말고 원본 선언/실제 응답을 따른다. 선언만 된 폰트 이름이나 시스템 fallback을 원본 폰트 성공으로 보고하지 않는다. 수집기가 다루지 못한 동적 src·inline SVG·component 장식도 렌더와 대조해 처리한다. manifest의 행 수가 전체 시각 요소 수는 아니다.

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
    response: HttpResponse = client.get(f"/api/payments/{quote(order_number)}")  # URL 근거: server-contract.json
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
