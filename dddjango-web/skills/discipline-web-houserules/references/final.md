# dddjango-web 표준 파일트리

> **출처:** dddjango-web 통합 스펙(2026-08-23) §1.3㉠ web 표준 트리 v3.2 · 확정 결정 대장 D1~D12(D12는 v2 — 2026-08-24 모션 축) · dddart discipline-houserules(검증 판형).
> 본문 속 `(D숫자)`는 **출처 표기**(결정 대장 번호)이며 로드 대상이 아니다 — 규칙 자체는 본문에 자족적으로 서술된다. 로드 가능한 위임은 두 가지뿐: 타 스킬은 "스킬명 + 주제", 동봉 파일은 `undecidable-web.md`.

---

## 목차

- §1. 표준 트리 (전문)
- §2. 성장 규칙 — 영역·개념 1차·종류 2차
- §3. 골격 완비 규칙 — 비어 있어도 형태를 유지한다
- §4. 명명 규약 총괄표
- §5. 참조·import 방향 — 격리
- §6. 입장 위치 답 — widget·component·section·view
- §7. 백스톱 연동 — 러너·게이트
- §8. 표기 표준화 — 브라운필드 관행 교정 사전

---

## §1. 표준 트리 (전문)

4원칙: ① **기준은 dddart 검증 판형의 현지화다** — 운영 검증된 dddart 표준 트리를 Django 서버렌더 표현계층으로 옮긴 것이며, 사용자가 명시적으로 확정한 결정 대장(D1~D12)이 우선한다 ② **web은 «내부의 외부 클라이언트»다 — Model이 없다.** 같은 저장소의 `web/`에 살지만 백엔드 BC의 실물 API 계약(URL+JSON)만 소비한다 — domain·use_case·infra 계층을 소유하지도 import하지도 않는다 ③ **요청 구동 MVVM + HTMX** — 지식은 view → VM → client 한 방향, 상주 상태·구독(watch) 없음, 갱신 표준은 HTMX 부분 재렌더 ④ **파일트리가 곧 규약이다** — 어떤 파일을 어디에 어떤 이름으로 만드는지가 핵심 강제다.

```text
web/
  urls.py                              # 전 영역 urls 합산 (root_router 번역)
  apps.py
  base/
    base.html                          # 공통 문서 골격·내비 셸 (root_scaffold 번역 — «거의 빈» 규범)
  <screen_area>/                       # 내비게이션 영역
    urls.py                            # 영역 path·name 리터럴 단일 출처
    <view>/                            # 화면 개념 1차 — 예: order_list/
      view/
        <view>_view.py                 # 진입점 — URL 바인딩·VM 호출·render·fragment 소유
        <view>.html                    # 페이지 템플릿
      view_model/
        <view>_view_model.py           # VM — client 호출·표시 상태 조립
      state/
        <view>_state.py                # 표시 상태 dataclass
      form/
        <view>_form.py                 # 입력 검증 Django Form — 입력 form이 있는 화면만 생성(조건 생성)
      section/
        <view>_<section>.html          # 화면 전속 조각 — HTMX 재렌더 단위·접두 필수
    widget/
      <widget>.html                    # 영역 재사용 조각 — 화면 비전속·명시 context만
  client/
    <bounded_context>/
      <capability>_client.py           # 계약 클라이언트 — in-process HTTP, api 표면만
      response/
        <response>_response.py         # web 소유 응답 모델
      exception.py                     # 계약 오류 표현
  design_system/
    foundation/
      tokens.css                       # 색·타이포·간격·모션 토큰
      motion.css                       # 공용 keyframes·모션 유틸(motion-*) — 값 정의는 tokens.css
    component/
      <부품군>/
        <component>.html               # BC 어휘 없는 순수 부품 — 부품군 1차·직속 금지
  static/
    css/  js/                          # htmx 포함 (js는 vendored 2종 — htmx·motion[조건 설치] — D12v2)
    images/                            # 시안 이미지 착지 (fetch 도구·asset-manifest 배선)
    fonts/                             # 폰트 파일이 필요한 경우만 생성
    files/                             # 다운로드 파일이 필요한 경우만 생성
```

읽는 법:

- `<screen_area>`(아래 표에서는 `<area>`) = **내비게이션 영역** — 전역 내비에서 한 묶음으로 노출되는 단위다(도메인 경계·백엔드 BC 경계가 아니다). `<view>` = **화면 개념**(예: `order_list`). `<bounded_context>`(아래 표에서는 `<bc>`) = 계약을 제공하는 백엔드 BC명, `<capability>` = 그 BC 계약에서 web이 소비하는 능력 묶음.
- **공존**: 대상 프로젝트 저장소 최상위에서 `web/`은 백엔드 표준 트리(`application/`·`framework/`·`<project>/`)와 **공존**한다. 두 세계는 트리 위치로 기계 구분되며, 연결은 실물 API 계약(URL+JSON)뿐이다(§5).
- 페이지 템플릿(`<view>.html`)은 `view/` 폴더에 `.py`와 병치한다 — 화면의 진입 코드와 페이지 템플릿은 한 폴더에서 함께 읽힌다.
- `form/`은 **조건 생성**이다 — 입력 form이 있는 화면만 `<view>_form.py`를 만든다(골격 완비 비대상 — §3, exception.py 판형). `static/fonts/`·`static/files/`는 검증된 폰트·다운로드 파일이 필요할 때만 생성한다(골격 필수 아님). `static/images/`는 **시안 이미지 착지** 칸이다(fetch 도구·asset-manifest 배선 — 에셋 규율은 implementation-ui 소유).
- `motion.css`는 **공용 모션의 거처**다 — 공용 `@keyframes`·모션 유틸 클래스(`motion-*` 명명·화면 어휘 금지)만 오고, custom property 정의는 모션 값(`--duration-*`·`--ease-*` 류) 포함 전부 `tokens.css`다. **화면 전속 `@keyframes`는 그 화면 CSS(`static/css/`)에 `<view>_` 접두로** 둔다 — 화면 어휘를 design_system에 넣지 않는다. `static/js/`의 `motion.js`는 동적 표현 발동 러너(vendored 고정물 — §5⑤)로, 설계 명세가 러너 분류 항목을 채택한 빌드에만 설치된다(**조건 설치**).
- 각 폴더에 담기는 코드의 내용 규칙(동작 규율)은 architecture-web 소유다: 3단 판별 §2 / 삼총사 규율 §3 / section·widget §4 / 승격·이동 §5 / 계약 소비 §6 / 라우팅 §7 / design_system 사용 §8. 구현 표기는 implementation-ui 소유. 이 문서는 **어떤 폴더·파일·이름이 존재해야 하는가(사실)** 를 소유한다.

**base/ 핵심 사실**: `base.html`은 «거의 빈» 규범이다 — 공통 문서 골격·내비 셸·전역 게이트만 오고, 화면 어휘가 등장하지 않는다(판별 절차는 `undecidable-web.md` §6).

**`<screen_area>` 핵심 사실**: 영역 직속에 오는 것은 `urls.py`·`widget/`·화면 개념 폴더뿐이다 — 그 외 직속 파일 금지(마커 파일 `__init__.py`·`.gitkeep`은 명시 예외 — §3)·영역 중첩 금지(1단)·빈 영역 금지. 영역·화면 이름에 컨테이너명(web·base·client·design_system·static)과 종류명(view·view_model·state·form·section·widget)을 쓰지 않는다. 영역 신설·귀속 판정은 에이전트 재량이 아니다 — `undecidable-web.md` §4(G0 배치축 3선택).

## §2. 성장 규칙 — 영역·개념 1차·종류 2차

분할 축은 셋이다: **영역(`<screen_area>`) 1차 → 화면 개념(`<view>`) 1차 → 종류 폴더 2차**.

- **화면 개념 폴더는 처음부터 만든다** — 영역의 첫 화면이라도 `<screen_area>/<view>/` 아래 종류 4폴더(`view/`·`view_model/`·`state/`·`section/`)로 시작한다. 종류 폴더 `form/`은 **조건 생성** — 입력 form이 있는 화면만 만든다(§3). 영역 직속에 화면 파일을 평면으로 두는 단계는 없다.
- **다른 화면 개념이 등장하면 새 `<view>/` 폴더다** — 기존 화면 폴더에 section·state를 얹지 않는다. ("두 번째 개념" 등장의 식별·판별 배정은 `undecidable-web.md` §5.)
- **widget/은 영역 수준이다** — 화면 개념 폴더 안에 `widget/`을 만들지 않는다. 화면 전속 조각은 그 화면 `section/`, 영역 재사용 조각만 `widget/`.
- **같은 개념은 위치가 달라도 같은 철자(어순 포함)** — `<view>` 접두는 `.py`·템플릿·urls name 전부에서 동일 철자다. `order_list` ↔ `list_order` 같은 어순 불일치 금지. (철자 일치의 판별 배정은 `undecidable-web.md` §5.)
- `client/`는 BC 1차 — 같은 BC의 capability가 늘면 `client/<bc>/` 안에 `<capability>_client.py` 파일이 는다. BC 폴더를 capability마다 쪼개지 않는다.
- `design_system/component/`는 부품군 1차 — 직속 파일 금지. 분류 안 되는 부품이 생기면 새 부품군 폴더를 만든다(정크드로어 군 금지).

## §3. 골격 완비 규칙 — 비어 있어도 형태를 유지한다

신규 단위(영역·화면 개념·client BC 폴더)를 만들면 표준 폴더를 항상 생성한다 — 비어 있어도 둔다. 트리의 형태 자체가 규약이므로 빈 폴더가 "이런 종류가 올 자리"라는 안내 역할을 한다. 폴더는 무조건, 코드는 필요할 때만.

| 단위 | 항상 생성 (전부) |
|---|---|
| `web/` 컨테이너 최초 | `urls.py`·`apps.py`·`base/base.html`·`design_system/foundation/tokens.css`·`design_system/foundation/motion.css`·`design_system/component/`·`static/css/`·`static/js/`(vendored htmx 파일)·`static/images/` |
| 신규 `<screen_area>/` | `urls.py` + `widget/` |
| 신규 `<view>/` (화면 개념) | `view/`·`view_model/`·`state/`·`section/` 종류 4폴더 전부 — `form/`은 입력 form이 있는 화면에서 첫 Form 때 생성(골격 대상 아님, exception.py 판형) |
| 신규 `client/<bc>/` | `<capability>_client.py` + `response/` — `exception.py`는 첫 계약 오류 표현 때 생성(골격 대상 아님) |

- `static/js/`의 vendored JS: htmx 파일 실물의 입수·설치는 Coordinator의 web 배선 전제조건(ⓕ) 소관 — 골격 검사는 **htmx 존재만** 본다. `motion.js`는 조건 설치(명세의 러너 채택 항목 ≥1일 때 Coordinator가 플러그인 판형을 복사 — 커맨드 소관)라 골격·존재 검사 대상이 아니다 — 존재하면 순수성 검사(§5⑤)가 판형 일치를 검증한다.
- **마커 파일**: Python 패키지 폴더(`.py`가 사는 곳 — `view/`·`view_model/`·`state/`·`form/`·`client/` 계열)는 비어 있어도 `__init__.py`를 둔다. HTML 전용 폴더(`section/`·`widget/`·`design_system/component/`)는 git이 빈 디렉터리를 추적하지 않으므로 비면 `.gitkeep`을 둔다. 두 마커 파일은 «직속 파일 금지»의 명시 예외다.
- design_system은 foundation·component **2칸 시작** — `theme/`·`util/`은 *만들지 않는 칸*이다. 실수요가 생기면 그때 증설하고, 미리 파지 않는다.
- **영구 test/ 없음** — 생성 앱의 `web/`에 `test/`·`test_*.py`·빈 테스트 파일을 만들지 않는다. 임시 Django 렌더·브라우저 smoke는 implementation-ui §2에 따라 실제 수행하고, 실행 결과와 스크린샷은 산출물 폴더에 보존한다. 기존 프로젝트의 적용 가능한 검사는 함께 실행한다. 플러그인 자체의 회귀 픽스처는 이 생성 앱 규칙의 대상이 아니다.
- `base/`는 `base.html` 하나로 시작한다 — base에 무엇이 들어갈 수 있는지는 `undecidable-web.md` §6(«거의 빈» 규범)이 판별한다.

## §4. 명명 규약 총괄표

공통 원칙:

1. **파일명 = snake_case.** `.py` 파일은 주 클래스 하나 — 클래스명은 파일명의 PascalCase 대응(`order_list_view_model.py` → `OrderListViewModel`). **예외**: 고정 이름 파일(`urls.py`·`exception.py`)과 함수 뷰 파일(`<view>_view.py` — 주 이름은 동명 함수)은 주 클래스 규칙의 예외다. 템플릿·CSS는 클래스가 없으므로 파일명 자체가 계약이다.
2. **종류는 폴더가 결정하고, 접미사가 그것을 재확인한다.** 접미사 판별은 긴 것 우선 — `_view_model.py`는 view_model 종류이지 view 종류가 아니다.
3. **삼총사 + 페이지 템플릿은 같은 접두 `<view>`**: `<view>_view.py` ↔ `<view>_view_model.py` ↔ `<view>_state.py` ↔ `<view>.html` 1:1:1:1 대응. **접두 `<view>`는 view 파일 stem에서 `_view`를 뗀 것이다** — 접두에 `_view`를 끼운 `order_list_view_view_model.py` 류 금지. 검사 방향은 **VM 기준** — VM이 존재하면 같은 접두의 view·state·페이지 템플릿이 대응해야 하며, 상태 조립이 필요 없는 정적 화면(약관·안내)은 view+템플릿만으로 허용(판별은 `undecidable-web.md` §1).
4. **section은 소속 view 접두 필수**(`<view>_<section>.html`), **widget·component 이름에는 view 이름 금지**.

총괄표:

| 위치 | 이름 기준 | 파일명 | 예시 |
|---|---|---|---|
| `web/` 직속 | 고정 | `urls.py` | `web/urls.py` — 전 영역 urls include 합산 |
| `web/` 직속 | 고정 | `apps.py` | AppConfig 클래스 `WebConfig` |
| `base/` | 고정 | `base.html` | 공통 문서 골격·내비 셸 (§1 base 핵심 사실) |
| `<area>/` 직속 | 고정 | `urls.py` | `web/orders/urls.py` — 영역 path·name 리터럴 단일 출처 |
| `<area>/urls.py`의 `name=` | 화면 개념 | 페이지 `<view>` · fragment `<view>_<조각>` | `name="order_list"` · fragment `name="order_list_filter_bar"` — 리터럴 거처는 §5④ |
| `<view>/view/` | 화면 개념 | `<view>_view.py` | `order_list_view.py` → **함수** `order_list_view` — 함수 뷰 고정(CBV 아님) |
| `<view>/view/` (페이지 템플릿) | 화면 개념 — view와 동일 접두 | `<view>.html` | `order_list.html` |
| `<view>/view_model/` | 화면 — view와 동일 접두 | `<view>_view_model.py` | `order_list_view_model.py` → 클래스 `OrderListViewModel`(모듈 수준 조립 함수 허용) |
| `<view>/state/` | 화면 — view와 동일 접두 | `<view>_state.py` | `order_list_state.py` → dataclass `OrderListState` |
| `<view>/form/` | 화면 — view와 동일 접두 | `<view>_form.py` | `order_list_form.py` → 클래스 `OrderListForm` — 입력 form이 있는 화면만(조건 생성 — §3) |
| `<view>/section/` | **소속 view 접두 필수** | `<view>_<section>.html` | `order_list_filter_bar.html` |
| `<area>/widget/` | 부품 — **view 이름 금지** | `<widget>.html` | `order_status_badge.html` |
| `client/<bc>/` | 계약 능력(capability) | `<capability>_client.py` | `order_query_client.py` → 클래스 `OrderQueryClient` |
| `client/<bc>/response/` | 응답 모델 | `<response>_response.py` | `order_summary_response.py` → 클래스 `OrderSummaryResponse` |
| `client/<bc>/` | 고정 | `exception.py` | 계약 오류 표현 `*Exception` 모음 |
| `design_system/foundation/` | 고정 | `tokens.css` | CSS 커스텀 프로퍼티(`--color-*`·`--space-*`·`--duration-*`·`--ease-*` 류) — 시각 값(모션 값 포함)의 단일 출처 |
| `design_system/foundation/` | 고정 | `motion.css` | 공용 `@keyframes`·모션 유틸 클래스 — 이름은 `motion-*` 고정(화면 어휘 금지)·custom property 정의 금지(값은 tokens.css, keyframes 중간값 리터럴만 허용) |
| `design_system/component/<부품군>/` | 수식·변형 | `<component>.html` | `button/primary_button.html` |
| `static/js/` | **vendored 닫힌 2종** — 원명 그대로 | (vendored 파일) | `htmx.min.js`·`motion.js`(조건 설치 — 플러그인 판형 그대로) — 커스텀 `.js`·타 라이브러리 신설 금지(§5⑤) |
| `static/css/` | 기능·범위 | `<이름>.css` | 파일명 snake_case — 시각 값은 tokens.css의 `var()` 참조·화면 전속 `@keyframes`는 `<view>_` 접두 |
| `static/images/` | 시안 자산 | `<이름>_<내용hash>.<확장자>` — snake_case | 절단 도구가 정한 manifest 경로를 그대로 사용(에셋 규율은 implementation-ui 소유) |
| `static/fonts/`·`static/files/` | 폰트·다운로드 파일 | `<이름>.<확장자>` — snake_case | 필요 시 검증된 파일만 복사·출처/배선 매핑 기록(implementation-ui §7) |

- 부품군 폴더 = 파일 접미사 — `button/` 안은 `*_button.html`. 축약(`btn`)·직속 파일·정크드로어 군(`widget/`·`etc/`) 금지.
- 접미사는 전체 표기다 — `_view_model.py`를 `_vm.py`로, `_state.py`를 `_st.py`로 축약하지 않는다.
- 라우트 path·name 문자열 리터럴의 자리는 §5④가 규정한다 — 이름은 여기서, 거처는 §5에서.

## §5. 참조·import 방향 — 격리

이 절의 **기계 판별 가능 부분이 백스톱 검사 대상**이다(§7 — WI·WP 패밀리). ⑥의 의미부(템플릿은 state만 읽는다·widget 명시 context 류)는 기계가 못 보는 영역으로, discipline-reviewer-web 감사 소관이다.

① **`web/**`에서 `application.`·`framework.` 내부 import 0** — driving_layer의 schema·타입 import도 금지다. 두 세계의 계약은 URL+JSON뿐이다(D5·D7). 필요한 API가 없으면 web에서 가정하거나 백엔드를 고치지 말고 **«/dddjango로 발주»를 안내**한다. — *왜* — import 한 줄이 생기는 순간 계약이 코드 결합으로 바뀌어, «내부의 외부 클라이언트»가 그냥 내부가 된다.

② **API 호출 코드는 client/ 전속** — view·VM·템플릿에서 HTTP 호출을 직접 수행하지 않는다. VM이 client를 호출하고, view는 VM만 호출한다.

③ **client가 부르는 URL은 백엔드 driving_layer api 표면 패턴만** — 백엔드의 서버렌더 페이지·admin·내부 경로를 호출하지 않는다.

④ **라우트 리터럴의 유일 거처 2곳** — web 자신의 path·name 리터럴은 `urls.py`뿐이다(영역 리터럴은 `<screen_area>/urls.py`, `web/urls.py`는 영역 include 합산만). 그 외 어디서든 — 템플릿 href·hx-get·redirect — `{% url %}`/`reverse`의 **이름만** 참조한다. BC API URL 리터럴은 그 계약의 client 모듈이 유일 거처다 — VM·view·템플릿에 API URL 문자열이 보이면 위반이다.

⑤ **D12 v2 순수성 — 커스텀 JavaScript 금지, JS는 vendored 닫힌 2파일**: `web/**`에 `.js` 파일 신설 금지 — 허용은 `static/js/`의 vendored `htmx.min.js`와 `motion.js`(동적 표현 발동 러너·조건 설치)뿐이고, **다른 JS 라이브러리의 vendored 추가도 금지**(닫힌 열거 — «vendored 형태면 된다»가 아니다). `motion.js`는 플러그인 판형 그대로만 둔다 — 수정·확장은 위반이며 백스톱이 판형 해시로 대조한다. 템플릿 inline `<script>` 금지 — 로드 태그는 base.html의 `{% static %}` 정확 경로 2종만이다(`undecidable-web.md` §6). **htmx 속성의 JS 채널도 금지다**: `hx-on*`, `hx-vals`/`hx-headers`의 `js:` 접두, `hx-trigger`의 `[조건식]`. 동작은 HTMX 속성·CSS 모션·`data-motion` 선언으로 표현하고, 그걸로 표현 불가한 동작 요구(패럴랙스·제스처 추종 류)는 우회 스크립트를 짜지 말고 설계로 반송한다.

⑥ **지식은 view → VM → client 한 방향** — 역방향 참조(client가 VM을, VM이 view·템플릿을 아는 것) 금지. **템플릿은 state만 읽는다** — 템플릿에서 VM 메서드 호출·client 접근 금지, widget에는 명시 context만 넘긴다.

⑦ **수평 격리 — 타 영역 widget `{% include %}` 금지**: widget은 소속 영역 안에서만 include한다. 교차 영역 재사용이 필요하면 BC 어휘를 탈피해 design_system 승격을 경유한다(절차는 architecture-web §5). 탈피 불가하면 설계로 반송한다 — 복제 금지(같은 조각을 두 영역에 복사하지 않는다).

- 템플릿 조각 합성 채널은 `{% include %}` 하나다 — 커스텀 templatetags 신설 금지. section·widget·component 모두 include로 합성한다.
- 템플릿 상속 채널은 base.html `{% extends %}` 하나다 — extends하는 층은 페이지 템플릿(`<view>.html`)뿐이고, section·widget·component는 extends 없는 조각이다.

## §6. 입장 위치 답 — widget·component·section·view

판별 **순서**는 architecture-web §2(3단 판별)가 **단독 소유**한다 — 상태 조립을 먼저 묻는다. 이 절은 판별 결론별 **위치 답**만 소유한다:

- 자기 표시 상태의 조립이 필요한 조각 → **view 삼총사** — 새 `<view>/` 폴더.
- 한 화면 전속 조각(받은 state 렌더만으로 성립) → 그 화면 `section/`.
- 영역 재사용 조각이고 BC 어휘를 보유 → `<screen_area>/widget/`.
- 재사용 조각인데 BC 어휘가 없음(순수 시각 부품) → `design_system/component/<부품군>/`.

- BC 어휘 "보유"는 import 없이 이름·문자열만으로도 성립한다 — "보유"·"전속"·"상태 조립"의 판별 절차는 `undecidable-web.md` §1~§3.
- 승격·이동 절차는 architecture-web §5 위임.
- `client/` 입장은 판별 대상이 아니다 — API 호출 코드는 언제나 client/ 전속이다(§5②).

## §7. 백스톱 연동 — 러너·게이트

dddjango-web 파이프라인은 이 하우스룰의 기계 판별 가능 부분을 **결정적 러너**가 게이트에서 검사한다(개별 검사의 열거·모사는 금지 — 검사 의미가 바뀌면 러너가 단일 출처):

```
python "${CLAUDE_PLUGIN_ROOT}"/scripts/backstop.py <대상 프로젝트 루트> [--diff-base <commit>] [--all]
```

(파이프라인에서는 Coordinator가 플러그인 루트를 해소해 호출한다 — 에이전트가 경로를 추측하지 않는다.)

- 검사 패밀리 4종: **WS(구조·골격) · WI(격리 — §5) · WN(명명 — §4) · WP(순수성 — D12)**. 발견은 전부 blocker — 일괄 반송.
- **exit 계약**: 0 = 통과 / 1 = 미실행(전제 실패 — 통과가 아니다) / 2 = blocker 발견·일괄 반송.
- **게이트 의미론**: 구조·명명은 **added**(새로 만든 파일·디렉터리)만, 격리·순수성은 touched 파일의 **added 줄**만, 골격 완비는 **신규 단위**(영역·화면 개념·client BC 폴더)만. → **레거시(기존 drift)에는 불발화한다** — "새 코드부터 표준" 원칙의 기계 집행.
- `--all`은 게이트 무시 전역 감사용 — 레거시 프로젝트에서 발견 폭주가 정상이며 파이프라인 게이트 용도가 아니다.
- 순환 등 래칫형 검사가 도입되면 기준선은 `.dddjango-web/backstop-baseline.json`(커밋 대상).
- **green 판정**: `py_compile`·`manage.py check`는 문법/시스템 검사다. 화면 슬라이스는 실제 렌더 내용과 브라우저 확인까지 보고한다(implementation-ui §2). 미실행은 미검증으로 남기고 구조 검사 통과와 구별한다. **WP6**는 추가/변경된 잘못된 Django 짧은 주석을 차단한다(유효한 단일줄·comment 블록·verbatim 원문 예시는 제외).
- **CSS 병치 결정**: design_system CSS(tokens.css·motion.css)는 `design_system/foundation/` **병치**가 결정이다 — 화면 CSS(`static/css/`)와 별개다. 병치 파일의 정적 서빙은 커맨드의 web 배선이 해결한다(아래 handoff).
- **호스트 배선 handoff**: 호스트 프로젝트 배선(INSTALLED_APPS·TEMPLATES DIRS·STATICFILES_DIRS 프리픽스 튜플·ROOT_URLCONF include·`ALLOWED_HOSTS`의 "testserver"·vendored JS 설치[htmx — ⓕ·motion.js — 조건 설치])은 **커맨드(Coordinator Phase 0 «web 배선 전제조건 검사»·Phase 2 진입 준비) 소관**이다 — 이 스킬은 배선을 규정하지 않는다.
- **반송 패밀리 → 교정 절 백링크**: WS(구조·골격) → §1 트리·§2 성장·§3 골격 / WI(격리) → §5 / WN(명명) → §4 / WP(순수성) → §5⑤.
- **에이전트 분업**: 러너가 잡는 것(경로·격리·명명·순수성)은 흉내내지 말고 이 문서대로 만들면 통과한다. 러너가 못 보는 **의미 판별 6종**(view/section, 화면 전속, BC 어휘, 영역 귀속, 두 번째 개념, base «거의 빈»)은 `undecidable-web.md`가 판별 절차·배정의 단일 출처다.

## §8. 표기 표준화 — 브라운필드 관행 교정 사전

대상 프로젝트에서 흔히 발견되는 Django 관행을 표준 어휘로 옮기는 교정 사전이다. 적용 경계는 경계 규칙 그대로 — **표기는 파일(모든 새 파일)·구조는 단위(신규 단위부터)**, 기존 파일의 개명·이동을 요구하지 않는다.

| 발견된 관행 | 표준 |
|---|---|
| `views.py` 단일 파일에 화면 누적 | 화면 개념 분해 — 화면마다 `<view>/` 폴더·삼총사(§1·§2) |
| `forms.py` 모음 | `<view>/form/`의 `<view>_form.py` — 입력 form이 있는 화면만(§3·§4) |
| 전역 `templates/<app>/` 트리 | 병치 트리 — 페이지 템플릿은 `view/`, 조각은 `section/`·`widget/`(§1) |
| CBV 관성(TemplateView·ListView 상속) | 함수 뷰 + VM — 표시 판정은 VM으로(§4 view·view_model 행) |
| view에서 context dict 직접 조립 | state dataclass(`<view>_state.py`) — 템플릿은 state만 읽는다(§5⑥) |
| inline `<script>`·커스텀 `.js` | HTMX 속성·CSS 모션·`data-motion` 선언으로 표현(§5⑤ — D12v2) |
| 템플릿·CSS의 색·크기 리터럴 | tokens.css 토큰 — `var()` 참조(§4 tokens 행) |
| 무네임스페이스 static 경로(`static/style.css` 류) | 프리픽스 경로 — STATICFILES_DIRS 프리픽스 튜플 배선 전제(§7 handoff) |

---

각 절은 필요한 절만 읽는다 — `## §N.` 헤더로 grep 가능하다(전체 로드 불필요).
