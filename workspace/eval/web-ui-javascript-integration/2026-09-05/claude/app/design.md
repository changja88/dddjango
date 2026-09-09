# ui_lab 통합 화면 설계 명세

대상: `lab` 영역 / 화면 개념 `ui_lab` 1개. 근거 스킬: architecture-web(§1~§8) · discipline-web-houserules(§1~§5·final.md §1~§5) · undecidable-web(§1~§6) · implementation-ui(§5·§7) · implementation-javascript(§1~§6).

## 1. 영역 배치 판정·모드 기록

- **영역 배치 판정**: G0 ① **새 영역 신설 = `lab`** (Coordinator 판정 — undecidable-web §4). 설계자는 이 판정을 파일 경로에 그대로 반영하고 뒤집지 않는다. 화면 개념은 `ui_lab` 1개.
- **계약 모드**: `static_only` — OpenAPI/`server-contract.json` 부재가 승인된 상태이며 업무 API를 소비하지 않는다. 따라서 `client/` BC 폴더·client 함수·response 모델·exception을 만들지 않는다(architecture-web §6 — 없는 API를 가정하지 않는다. 여기서는 «필요한 엔드포인트가 없음»이 아니라 «소비 요구 자체가 없음»이므로 발주 대상도 아니다).
- **형상 근거**: 동결 시안·design-tokens·asset-manifest·motion-notes·render-audit 전부 **미제공**. 승인에 따라 기존 `design_system` 토큰 관례로 자체 설계한다(implementation-ui §2 — "시안이 애초에 없으면 기존 design_system 관례로 자체 설계"). 이탈 표는 시안이 존재해야 성립하므로 **해당 없음**(§9에 명시).
- **host 상태(입력받아 소비)**: `TEMPLATES DIRS = BASE_DIR/"web"` · `STATICFILES_DIRS = [("web", BASE_DIR/"web/static"), ("design_system", BASE_DIR/"web/design_system")]` · `ROOT_URLCONF`이 `web.urls` include · `base/base.html`이 `{% static 'design_system/foundation/tokens.css' %}` link, `{% static 'web/htmx/htmx.min.js' %}` **classic + defer** core(HTMX 2.0.10, 출처·SHA256 검증 완료), 범용 `{% block styles %}`·`{% block scripts %}`·`{% block content %}` 보유. **기능 static 이름은 `web/js/…`·`web/css/…` 프리픽스**를 쓴다(Coordinator 픽스처 교정 반영). `MIDDLEWARE = []`(CSRF·session 미들웨어 없음) — 아래 §6에서 fragment 라우트를 전부 **부작용 없는 GET**으로 확정해 페이지와 동일한 공개·비변경 regime을 유지한다(architecture-web §4 — fragment에 페이지와 같은 auth·CSRF regime, 여기서는 둘 다 공개·state-changing 없음).
- **JS 분류 선언**: native disclosure = **S3**(추가 기능 JS 없음, HTML 소유) / 비밀번호 표시·로컬 이미지 미리보기 = **S1**(승인된 로컬 UI JS — undecidable-web §1 «브라우저 임시 상태»·architecture-web §1 기술 책임). 두 분류는 독립이다 — 다른 기능에 JS가 필요하다는 사실이 disclosure에 JS를 정당화하지 않는다.

## 2. 화면 분해 — 3단 판별(architecture-web §2)

판별은 위에서부터, 처음 해당하는 것이 답.

| 조각 | 질문1 상태 조립 | 질문2 화면 전속 | 결론 | *왜* |
|---|---|---|---|---|
| ui_lab 화면 | **예** — 서버가 revision marker를 생성하고 패널별 표시 판정(어느 패널이 root swap 제어를 갖는가·자식 swap 제어를 갖는가)·dom id·문구를 조립한다 | — | **view 삼총사 + 페이지 템플릿** | 서버 생성 marker와 표시 판정이 있으므로 정적 화면 판례(undecidable-web §1)에 해당하지 않는다 |
| 패널(A/B) | 아니오 — 받은 panel state 렌더만 | 예 — ui_lab state 필드를 안다 | **section** `ui_lab_panel.html` | root swap 단위(hx-target) |
| 비밀번호 필드 그룹 | 아니오 | 예 — panel state 하위 필드 | **section** `ui_lab_password_field.html` | 두 패널이 같은 화면 전속 조각을 재사용(두 번째 *화면*이 아니므로 widget 승격 신호 아님 — architecture-web §5) |
| 미리보기 그룹 | 아니오 | 예 | **section** `ui_lab_preview.html` | 유지되는 패널의 **자식 교체(dependent child swap)** 단위 |
| 노트 노드 | 아니오 | 예 | **section** `ui_lab_note.html` | 미리보기 root 안에 있으나 자원 비종속인 **독립 자식 교체** 단위 |
| widget / design_system component | — | — | **신설 없음** | 두 번째 화면·두 번째 영역 재사용 요구가 없다 — state 렌더로 성립하면 승격 금지(architecture-web §5 역방향 절제). 기존 `design_system/component/`는 실사 결과 `.gitkeep`뿐이라 재사용 후보 0 |

- **"두 번째 개념" 판별(undecidable-web §5)**: 진입 URL은 페이지 1개 + 같은 화면의 fragment 3개뿐이고 표시 상태가 한 묶음이므로 **두 번째 화면 개념 없음** — `ui_lab/` 폴더 1개. 철자는 `.py`·템플릿·urls name 전부 `ui_lab`(어순 고정).
- **base «거의 빈»(undecidable-web §6)**: base.html에 화면 어휘를 넣지 않는다 — **base.html 수정 없음**. 기능 script는 페이지의 범용 `scripts` block에 외부 `{% static %}`로 한 번 둔다.

## 3. 삼총사·form 파일

| 파일 | 주 이름 | 내용 결정 |
|---|---|---|
| `web/lab/ui_lab/view/ui_lab_view.py` | **함수** `ui_lab_view` (+ fragment 함수 3개) | 얇은 진입점 — VM 호출·render만. 판단 금지(architecture-web §3) |
| `web/lab/ui_lab/view/ui_lab.html` | 페이지 템플릿 | `{% extends "base/base.html" %}` — styles/scripts/content block 채움 |
| `web/lab/ui_lab/view_model/ui_lab_view_model.py` | `UiLabViewModel` | 표시 판정의 유일한 자리 — revision marker 생성, 패널별 제어 활성 판정, dom id·문구 확정 |
| `web/lab/ui_lab/state/ui_lab_state.py` | `UiLabState`(+ 중첩 dataclass 4종) | `@dataclass(frozen=True)`·프리미티브와 중첩 dataclass만 |
| `<view>_form.py` | **생성 안 함** | 입력 form이 없다 — 비밀번호·파일 값은 브라우저를 떠나지 않고 서버 검증·제출이 없다(요구 1·2). `form/` 폴더도 만들지 않는다(조건 생성 — houserules final.md §3) |

## 4. 상태(state) 모양 — `ui_lab_state.py`

전부 `@dataclass(frozen=True)`. 템플릿이 아는 유일한 모양이며 패키지 타입 직노출 없음(architecture-web §3). Django Form 예외는 사용하지 않는다(form 없음).

| dataclass | 필드(타입) | 소유 판정 |
|---|---|---|
| `UiLabState` | `page_title: str` · `disclosure_summary: str` · `disclosure_body: str` · `panel_a: UiLabPanelState` · `panel_b: UiLabPanelState` | 페이지 조립 |
| `UiLabPanelState` | `dom_id: str` · `heading: str` · `revision_marker: str` · `root_swap_enabled: bool` · `root_swap_label: str` · `password: UiLabPasswordState` · `preview: UiLabPreviewState` | `root_swap_enabled`는 **VM 판정** — 패널 B만 True(root swap 대상) |
| `UiLabPasswordState` | `dom_id: str` · `input_dom_id: str` · `input_name: str` · `label: str` · `show_label: str` · `hide_label: str` · `autocomplete: str` | 인스턴스 격리를 위해 dom id를 서버가 확정 |
| `UiLabPreviewState` | `dom_id: str` · `input_dom_id: str` · `input_name: str` · `label: str` · `clear_label: str` · `empty_message: str` · `error_message: str` · `revision_marker: str` · `child_swap_enabled: bool` · `child_swap_label: str` · `note: UiLabNoteState` | `child_swap_enabled`는 **VM 판정** — 패널 A만 True |
| `UiLabNoteState` | `dom_id: str` · `text: str` · `revision_marker: str` · `swap_enabled: bool` · `swap_label: str` | `swap_enabled`는 패널 A만 True |

- **revision marker**: VM이 **요청마다 새로 생성**하는 문자열(예: `rev-<uuid4 hex 12자>` 판형) — 응답마다 유일해야 한다. 모듈 수준 카운터·캐시 같은 **상주 상태 금지**(architecture-web §1 무상태 조립기). 패널·미리보기·노트가 각자 자기 marker를 갖는다 — swap 경계별로 "이 HTML이 방금 서버에서 왔다"를 육안·harness가 구별하기 위함(요구 4·I6).
- 템플릿은 state 필드만 읽고 계산·필터링을 하지 않는다(implementation-ui §4).

## 5. 계약 소비 매핑

| 항목 | 결정 |
|---|---|
| 인용 엔드포인트 | **0건** — static_only 승인. 업무 API 소비 없음 |
| client 모듈 | **0개** (`client/` 폴더 생성 안 함) |
| response 모델 | **0개** |
| client exception → 표시 귀결 | **해당 없음** |

수량 대조: 인용 엔드포인트 0 = client 함수 0 = response 모델 0 (누락 0). fragment 라우트는 web 자신의 화면 fragment이며 «업무 API»가 아니다 — static URL을 fragment endpoint로 쓰지 않고 view가 응답을 소유한다(architecture-web §4).

## 6. 라우팅·HTMX 부분 재렌더

리터럴 단일 출처: `web/lab/urls.py`(`app_name = "lab"`). `web/urls.py`는 영역 include 합산만(`path("lab/", include("web.lab.urls"))`). 템플릿은 `{% url 'lab:…' %}` 이름만 참조(architecture-web §7).

| name | path(영역 상대) | view 함수 | 렌더 대상 | swap 경계 |
|---|---|---|---|---|
| `ui_lab` | `ui-lab/` | `ui_lab_view` | `ui_lab.html`(페이지 전체) | — |
| `ui_lab_panel` | `ui-lab/fragment/panel/` | `ui_lab_panel_fragment` | `ui_lab_panel.html` (panel = 패널 B state) | `hx-target="#ui-lab-panel-b"` · `hx-swap="outerHTML"` — **root 교체(완전한 UI 패널)** |
| `ui_lab_preview` | `ui-lab/fragment/preview/` | `ui_lab_preview_fragment` | `ui_lab_preview.html` (preview = 패널 A의 preview state) | `hx-target="#ui-lab-preview-a"` · `hx-swap="outerHTML"` — **유지되는 패널 A의 종속 자식(자원 소유 root) 교체** |
| `ui_lab_note` | `ui-lab/fragment/note/` | `ui_lab_note_fragment` | `ui_lab_note.html` (note = 패널 A preview의 note state) | `hx-target="#ui-lab-note-a"` · `hx-swap="outerHTML"` — **유지되는 미리보기 안의 독립 자식 교체(자원 비종속)** |

- 4개 진입점 모두 **소속 view가 소유**한다 — 새 파일 유형을 만들지 않는다(architecture-web §4). 각 fragment 함수는 같은 `UiLabViewModel`을 지나 state를 조립하므로 페이지 경로와 fragment 경로의 표시 판정이 어긋날 수 없다.
- **전부 GET·부작용 없음**(읽기 전용 픽스처 UI HTML) — 저장·업무 판정·업무 API를 만들지 않는다(요구 4). state-changing이 없으므로 `hx-post`·CSRF 토큰 배선은 대상이 아니다(implementation-ui §5 — CSRF는 state-changing만).
- 허용 htmx 속성만 사용: `hx-get`·`hx-target`·`hx-swap`. `hx-on*`·`js:`·`hx-trigger` 조건식은 금지(houserules final.md §5⑤).
- **DOM id 계약(서버 state가 확정)**: `ui-lab-panel-a` / `ui-lab-panel-b` / `ui-lab-preview-a` / `ui-lab-preview-b` / `ui-lab-note-a` / `ui-lab-note-b` / `ui-lab-password-a` / `ui-lab-password-b`(입력은 `…-input` 접미). coder는 id를 발명하지 않고 state 값으로 렌더한다.

**조각 포함 관계(교체 경계 판별에 필요한 소유 사실 — 형상 서술이 아니라 swap 계약)**

- 패널 root(`[data-ui-lab-panel]`) ⊃ 비밀번호 그룹(`[data-password-visibility]`), 미리보기 그룹(`[data-image-preview]`)
- 미리보기 그룹 ⊃ 파일 입력 + clear 버튼, 출력 이미지(`[data-image-preview-output]`), 파일명 노드(`[data-image-preview-name]`), 오류 노드(`[data-image-preview-error]`), **노트 노드(`[data-ui-lab-note]` — object URL 비종속)**
- 노트 노드가 미리보기 root **안에** 있는 것이 이 픽스처의 핵심이다 — 자식 정리(cleanup)와 소유자 정리를 harness가 구별할 수 있어야 하기 때문이다(요구 4·I8). `detail.elt.closest(root)`만 보고 부모 전체를 정리하는 구현은 여기서 실패한다(implementation-javascript §3).
- 각 swap 트리거 버튼은 **자기 교체 단위 안에** 렌더된다 — 교체 후 새 제어로 반복 실행이 가능해야 하기 때문(I7).

**HTMX 선언 조각의 include 호스트·지배 플래그(1:1 확정 — coder는 배치·조건을 발명하지 않는다)**

| 선언 조각 | include 호스트 템플릿 | 지배 플래그(§4 VM 판정) | 참 인스턴스 | 조건 판형 |
|---|---|---|---|---|
| `static/htmx/ui_lab_panel_swap.html` | `web/lab/ui_lab/section/ui_lab_panel.html` | `panel.root_swap_enabled` | 패널 B만 | `{% if panel.root_swap_enabled %}{% include "static/htmx/ui_lab_panel_swap.html" %}{% endif %}` |
| `static/htmx/ui_lab_preview_swap.html` | `web/lab/ui_lab/section/ui_lab_preview.html` | `preview.child_swap_enabled` | 패널 A의 미리보기만 | `{% if preview.child_swap_enabled %}{% include "static/htmx/ui_lab_preview_swap.html" %}{% endif %}` |
| `static/htmx/ui_lab_note_swap.html` | `web/lab/ui_lab/section/ui_lab_note.html` | `note.swap_enabled` | 패널 A의 노트만 | `{% if note.swap_enabled %}{% include "static/htmx/ui_lab_note_swap.html" %}{% endif %}` |

- **호스트는 언제나 «그 조각이 교체하는 단위 자신»이다** — 페이지 템플릿(`ui_lab.html`)에는 어떤 선언 조각도 include하지 않는다. 페이지에 두면 outerHTML 교체 순간 트리거가 사라져 반복 swap(I7)이 깨진다(architecture-web §4 — 선언 조각은 그 swap 경계를 소유한 section에서 include).
- **조건은 VM이 이미 결정한 bool의 단순 표시 분기**다 — 템플릿은 `A인가 B인가`를 계산하지 않고 §4의 플래그만 읽는다(architecture-web §3·implementation-ui §4). 따라서 패널 A에는 root swap 트리거가, 패널 B의 미리보기·노트에는 자식 swap 트리거가 렌더되지 않는다(요구 4·5의 «유지되는 패널의 종속/독립 자식» 경계).
- 각 선언 조각의 내용은 `hx-get="{% url 'lab:… ' %}"`·`hx-target`·`hx-swap="outerHTML"`를 가진 버튼 1개이며, target id는 §6 DOM id 계약의 고정 문자열(`#ui-lab-panel-b`·`#ui-lab-preview-a`·`#ui-lab-note-a`)을 쓴다 — 조각이 하나의 참 인스턴스에만 렌더되므로 id 계산이 필요 없다.

## 7. UI 동작 계약(architecture-web §1)

| 기능 | 요구 근거 | 담당 기술 | JS/HTMX 파일 | root·대상 | 서버 요청·swap 경계 | 임시 상태·자원 | 키보드·실패·정리 | 검증 행위 |
|---|---|---|---|---|---|---|---|---|
| 비밀번호 표시/숨김 | 요구 1 (I1·I2) — **S1** | HTML + UI JS | `web/static/js/password_visibility.js`; HTMX 필요 없음 | root `[data-password-visibility]` 안 `[data-password-input]`·`[data-password-toggle]` | 요청 없음; 교체되면 동작 시 현재 자식을 조회 | input의 `type` 표시 상태만; 외부 자원 없음 | `<button type="button">` native 키보드(Enter/Space) · `aria-pressed`+`aria-controls` 갱신 · JS 미로드 시 버튼은 `hidden`으로 남아 비밀번호가 노출되지 않음 · 정리 대상 자원 없음 | 마우스·키보드 토글, 두 인스턴스 격리(A 토글이 B를 바꾸지 않음), 패널 B root swap 후 새 버튼 재동작, 반복 클릭 1동작=1효과 |
| 로컬 이미지 미리보기 | 요구 2·5 (I3·I4·I5·I8·I9) — **S1** | HTML + UI JS | `web/static/js/image_preview.js`; HTMX 필요 없음(교체는 아래 3행이 소유) | root `[data-image-preview]` 안 `[data-image-preview-input]`·`[data-image-preview-clear]`·`[data-image-preview-output]`·`[data-image-preview-name]`·`[data-image-preview-error]` | 요청 없음(업로드·저장 없음); root가 통째로 교체될 수 있음 | root별 `WeakMap` 항목 = `{ objectUrl, generation }`; 자원 = `URL.createObjectURL` blob URL | 파일 선택은 native `<input type="file">` 키보드 경로 · 실패(비이미지 type 또는 decode error) → 오류 노드 문구 표시 + 파일명·이미지 비움 · **재선택/clear/소유 노드 제거 시 이전 URL revoke** · 문서 수명 위임 리스너 1회 등록(root마다 리스너 추가 없음) | 두 미리보기 격리, 파일명 리터럴 표시(마크업 미해석), 재선택·clear의 create/revoke 호출 계정, 실패 주입 시 잔여 성공 없음, preview swap 시 해당 root URL만 revoke, note swap 시 유지된 미리보기 URL **미**revoke |
| 안내 펼침(disclosure) | 요구 3 (I10) — **S3** | native `<details>/<summary>` | **필요 없음** — native 요소가 펼침 상태·키보드·접근성 이름을 이미 제공한다(implementation-javascript §1·§6). 기능 JS 파일·핸들러 0 | `<details>`·`<summary>` | 요청·swap 없음 | `open` 속성; 자원 없음 | native 키보드 경로(Enter/Space)·포커스 | 기능 JS 전체 비활성 상태에서 펼침/접힘 동작 |
| 패널 root 교체 | 요구 4·5 (I6·I7·I9) | HTMX 선언 | `web/static/htmx/ui_lab_panel_swap.html` — **include 호스트 = `section/ui_lab_panel.html`**(교체 단위 자신), 조건 `{% if panel.root_swap_enabled %}`; JS 없음 | 트리거는 패널 B 안, 대상 `#ui-lab-panel-b` | `GET {% url 'lab:ui_lab_panel' %}` → `hx-swap="outerHTML"`, 패널 A는 DOM 유지 | 서버 marker 외 임시 상태 없음 | 실패 시 기존 DOM 유지(htmx 기본) · 제거되는 패널 B의 미리보기 URL은 `image_preview.js`의 cleanup 계약이 revoke | 실제 네트워크 요청 발생, 응답의 새 revision marker 표시, 반복 swap 후 중복 노드·중복 효과 없음, 패널 A 비밀번호/미리보기 상태 유지 |
| 종속 자식(미리보기 소유자) 교체 | 요구 4·5 (I7·I9) | HTMX 선언 | `web/static/htmx/ui_lab_preview_swap.html` — **include 호스트 = `section/ui_lab_preview.html`**(교체 단위 자신), 조건 `{% if preview.child_swap_enabled %}`; JS 없음 | 트리거는 미리보기 A 안, 대상 `#ui-lab-preview-a` | `GET {% url 'lab:ui_lab_preview' %}` → `outerHTML`, 패널 A root와 비밀번호 A는 유지 | — | 교체되는 root의 blob URL revoke 후 WeakMap 항목 제거 | 요청·marker 갱신 확인, 교체 후 새 파일 입력이 정상 동작, 같은 패널의 비밀번호 상태 유지, 패널 B 미리보기 무영향 |
| 독립 자식(노트) 교체 | 요구 4·5 (I8) | HTMX 선언 | `web/static/htmx/ui_lab_note_swap.html` — **include 호스트 = `section/ui_lab_note.html`**(교체 단위 자신), 조건 `{% if note.swap_enabled %}`; JS 없음 | 트리거는 노트 A 안, 대상 `#ui-lab-note-a` | `GET {% url 'lab:ui_lab_note' %}` → `outerHTML`, 미리보기 A root는 유지 | — | **정리 없음** — 제거 노드가 blob URL의 실제 종속 노드가 아니므로 revoke 금지 | 노트 marker만 갱신되고 미리보기 A 이미지·파일명·URL이 그대로 유효 |

**수명 메커니즘 확정(coder가 발명하지 않도록 못 박는다 — implementation-javascript §2~§4)**

1. **로드**: 두 기능 JS는 페이지 템플릿 `{% block scripts %}`에서 외부 `{% static 'web/js/…' %}` + `defer`(host classic 정책)로 **페이지당 각 1회**. fragment·HTMX 선언 조각에는 실행 script를 넣지 않는다(요구 6·I11).
2. **초기화**: 두 기능 모두 **document 수준 이벤트 위임 1회 등록**(click / change / capture-phase error) — root마다 리스너를 붙이지 않는다. 따라서 swap 반복이 리스너를 증식시키지 않는다(I7).
3. **가시화 스캔**: JS가 있어야 의미 있는 제어(비밀번호 토글 버튼, 미리보기 clear 버튼)는 서버가 `hidden`으로 렌더하고, `activate(scope)`가 `hidden`을 해제한다. `activate`는 ⓐ `document.readyState === "loading"`이면 `DOMContentLoaded`(once), 아니면 즉시 ⓑ `htmx:load`의 `detail.elt`(자신의 `matches()` + 자손 검색 둘 다) 로 호출한다. 반복 호출은 멱등이다.
4. **자원 소유·정리(`image_preview.js`)**:
   - 새 선택 시 순서 = ① 이 root의 이전 objectUrl revoke ② 파일명·오류·이미지 비움(잔여 성공 제거) ③ 파일 `type`이 `image/`로 시작하지 않으면 오류 상태로 종료(URL 생성 안 함) ④ 아니면 새 URL 생성·`generation` 증가·`img.src` 지정·파일명은 `textContent`로 기입.
   - `load`/`error`는 **capture phase document 리스너**로 받고(`error`는 버블하지 않음), `event.target`이 `[data-image-preview-output]`이며 그 `src`가 그 root에 저장된 현재 URL과 같을 때만 처리한다(늦은 완료·구세대 결과 무효화). `error`면 URL revoke + 오류 문구 표시 + 파일명 비움.
   - clear 버튼: input value 초기화 + 이전 URL revoke + 빈 상태 문구 복귀.
   - **`htmx:beforeCleanupElement`**: `detail.elt`가 어떤 root **자신이거나 그 root를 포함**하면 그 root의 URL을 revoke하고 WeakMap 항목을 제거한다. `detail.elt`가 살아 있는 root의 **내부 노드**일 때는 그 노드가 `[data-image-preview-output]`을 포함(또는 자신)할 때만 revoke한다 — 노트 노드 제거는 정리 대상이 아니다(I8). 반복 정리는 안전(멱등)해야 한다.
   - `load` 직후 무조건 revoke 금지 — URL의 실제 사용 수명(다음 선택·clear·소유 노드 제거)까지 유지한다.
5. **출력 표기**: 파일명·오류 문구는 `textContent`·`value`로만 넣는다 — `innerHTML` 금지(I3의 «파일명 마크업 미해석»).
6. **금지 채널 재확인**: inline 실행 JS·`on*` 속성·`hx-on`·`js:`·`hx-trigger` 조건식·CDN 실행 태그·새 라이브러리 없음. 업무 권한·금액·저장 판정 없음(애초에 업무 계약이 없다).

## 8. design_system·시각 값

**사전 조사 실사 결과**: `web/design_system/component/`는 `.gitkeep`만 존재 → **재사용 가능한 component 0건**(실사 없는 재사용 선언 금지). `foundation/tokens.css`는 아래 9개 토큰 보유, `foundation/motion.css`는 **빈 파일**.

**토큰 전수 연결**(기존 tokens.css 전 항목 — 빈칸 0):

| 토큰 | 처분 | 사용처(요소 결합) |
|---|---|---|
| `--space-sm` | 채택 | 그룹 내부 간격(라벨↔제어, 제어↔출력) |
| `--space-md` | 채택 | 패널 내부 padding·블록 간 간격 |
| `--space-lg` | 채택 | 패널 사이 간격·페이지 외곽 여백 |
| `--text-color` | 채택 | 본문 텍스트 색 + 패널 테두리 색 |
| `--surface-color` | 채택 | 패널 배경 |
| `--error-color` | 채택 | 미리보기 실패 문구 색 |
| `--preview-size` | 채택 | 출력 이미지 최대 크기 |
| `--font-body` | 채택 | 화면 전체 본문 서체 |
| `--line-body` | 채택 | 본문 행간 |

**신규 등록 토큰 1건**(풀 밖 값 — 출처 기록): `--border-width-hairline: 1px` — 출처: 시안 부재로 인한 **자체 설계 결정**(패널 경계선 두께). *왜*: CSS에 생 치수 리터럴을 두지 않기 위해 토큰화한다(architecture-web §8). 색은 기존 `--text-color`를 재사용해 신규 색 토큰을 만들지 않는다.

- 화면 CSS는 `web/static/css/ui_lab.css` 1개, 값은 전부 `var(--…)` 참조. 시각 값은 CSS가 소유하고 JS는 색·간격·애니메이션을 정의하지 않는다(요구 6).
- **신설 component 0건**: 이 화면 밖 재사용 요구가 없고, 만들면 BC 어휘 없는 부품이라도 투기적 자산이 된다(architecture-web §5 역방향 절제). 두 번째 화면이 등장하면 그때 승격한다.
- **이미지 정형 목록**: asset-manifest 미제공·시안 부재 → **대상 0건**. `static/images/`는 골격으로 유지하고 이번 기능에서 파일을 추가하지 않는다.
- **동적 표현 처분**: `motion-notes.md` 미제공 → 처분 표 **비대상**(입력 채널 없음). **러너 채택 0** → `web/static/js/motion.js` **미설치**. `motion.css`는 빈 파일 그대로 두고 base에 link를 추가하지 않는다.
- **렌더 실측 처분·배치 거동**: `render-audit.json` 미제공 → texts/pinned 처분 **비대상**. 고정(sticky/fixed) 요소 **없음**, 스크롤 스킴은 **문서 스크롤**(내부 스크롤 패널 없음)로 확정한다 — 고정 요구가 없으므로 sticky 판형을 도입하지 않는다(implementation-ui §7).
- **웹폰트 검토**: 명명된 서체 요구 없음 → `--font-body`의 `system-ui` 스택 유지. 폰트 파일 미도입(`static/fonts/` 생성 없음).

## 9. 시안 대응과 이탈

시안·토큰 절단·실측이 **전부 부재**하므로 형상 대응 좌표가 존재하지 않는다. 따라서 architecture-web §1 이탈 표는 **해당 없음(행 0)** — 이탈 표는 시안 근거가 있을 때만 성립하며, 시안 없는 자체 설계를 «이탈»로 위장 기록하지 않는다. 자체 설계의 근거는 §8의 토큰 사용과 §1의 승인(native design authorized)이다. 산문 레이아웃 재설계는 작성하지 않았다 — §6의 포함 관계는 swap 소유 계약이지 형상 서술이 아니다.

## 10. 행위 목록(G2 화면 확인 체크리스트 근거)

| # | 외부 관찰 행위 | 연결 |
|---|---|---|
| 1 | 패널 A의 표시 버튼을 마우스로 누르면 A의 비밀번호가 평문으로 보이고 버튼 문구가 숨김 라벨로 바뀐다 | I1 |
| 2 | 같은 조작을 키보드(Tab→Enter/Space)로 해도 동일하게 동작한다 | I2 |
| 3 | A를 표시로 바꿔도 B의 비밀번호는 계속 가려져 있고 값이 변하지 않는다 | I1 |
| 4 | 유효한 로컬 이미지를 고르면 그 이미지와 **파일명 문자열 그대로**가 표시된다(파일명에 태그 문자가 있어도 텍스트로 보인다) | I3 |
| 5 | 두 미리보기가 서로 다른 이미지를 각각 표시하고, 한쪽 선택이 다른 쪽을 바꾸지 않는다 | I3 |
| 6 | 다시 고르거나 clear를 누르면 이전 이미지·파일명이 사라지고 이전 blob URL이 해제된다 | I4 |
| 7 | 잘못된 이미지(디코드 실패/비이미지)를 고르면 오류 문구가 보이고 이전 성공 표시(이미지·파일명)가 남지 않는다 | I5 |
| 8 | 안내를 펼치면 도움말 문구가 보인다 — 기능 JS를 모두 비활성화해도 동작한다 | I10·S3 |
| 9 | 패널 교체 버튼을 누르면 패널 B가 새 HTML로 바뀌고 revision marker 문자열이 바뀐다(네트워크 요청 1건 발생) | I6 |
| 10 | 교체를 반복해도 마커는 매번 새로 바뀌고, 한 번 조작에 한 번 효과만 일어난다(중복 노드·중복 반응 없음) | I7 |
| 11 | 패널 B 교체 후 새 패널의 비밀번호 토글·미리보기가 정상 동작하고, 패널 A의 표시 상태·미리보기는 그대로 유지된다 | I7·I9 |
| 12 | 미리보기 A 교체 버튼을 누르면 미리보기 A만 새 HTML로 바뀌고, 같은 패널의 비밀번호 상태는 유지되며, 교체된 미리보기의 이전 이미지는 사라진다 | I9 |
| 13 | 노트 교체 버튼을 누르면 노트 문구·마커만 바뀌고 **미리보기 A의 이미지·파일명이 그대로 남는다** | I8 |
| 14 | 페이지 전체 텍스트가 `--font-body` 서체·`--line-body` 행간으로 렌더되고, 패널 내부 간격(`--space-sm/md`)과 패널 사이 간격(`--space-lg`)이 일관된다 — 서체·줄간·블록 간 간격 확인 단위 | §8 |
| 15 | 오류 문구가 `--error-color`로, 패널 테두리가 `--text-color`+`--border-width-hairline`로 보인다 | §8 |
| 16 | **위험 항목 확인**: `system-ui` 스택이 실행 환경에서 실제로 해석되어 텍스트가 대체 없이 렌더되는지 육안 확인(시스템 대체 서체 위험 — §11 R1) | §11 R1 |
| 17 | **위험 항목 확인**: 페이지 로드 시 기능 script·htmx core가 각 1회만 네트워크 로드되고, 어떤 fragment 응답 HTML에도 `<script>`가 없다 | I11·요구 6 |
| 18 | **위험 항목 확인**: 브라우저 콘솔·pageerror가 새로 발생하지 않고 `manage.py check`가 baseline(0 issues)을 유지한다 | I12 |

## 11. 위험·미결정

| id | 내용 | 처분 |
|---|---|---|
| R1 | 서체가 `system-ui` 시스템 스택이라 실행 환경에 따라 실제 글리프가 달라진다 | 시안·폰트 요구가 없어 수용. 행위 목록 16번으로 확인 항목화 |
| R2 | host `MIDDLEWARE = []` — CSRF·session 미들웨어 없음 | 이번 화면은 state-changing 요청이 0이라 영향 없음. 향후 POST fragment가 생기면 미들웨어 배선이 선행 조건(Coordinator 소관) |
| R3 | `error` 이벤트 기반 실패 판정은 브라우저 디코더에 의존한다 | 비이미지 MIME 조기 차단 + decode error 두 경로를 모두 명세(§7-4)해 실패 상태를 보장 |

**미해결 blocker: 없음.** 계약 부재(openapi 없음)는 승인된 static_only 모드이므로 발주 대상이 아니다.

## 12. 파일 목록·구조 결정(신규+수정 전체)

**신규**

| # | 경로 | 비고 |
|---|---|---|
| 1 | `web/lab/__init__.py` | 영역 패키지 마커 |
| 2 | `web/lab/urls.py` | 영역 path·name 단일 출처 · `app_name = "lab"` |
| 3 | `web/lab/widget/.gitkeep` | 신규 영역 골격(HTML 전용 폴더 마커) |
| 4 | `web/lab/ui_lab/__init__.py` | 화면 개념 패키지 마커 |
| 5 | `web/lab/ui_lab/view/__init__.py` | |
| 6 | `web/lab/ui_lab/view/ui_lab_view.py` | 함수 `ui_lab_view` + `ui_lab_panel_fragment`·`ui_lab_preview_fragment`·`ui_lab_note_fragment` |
| 7 | `web/lab/ui_lab/view/ui_lab.html` | 페이지 템플릿(`extends "base/base.html"`) |
| 8 | `web/lab/ui_lab/view_model/__init__.py` | |
| 9 | `web/lab/ui_lab/view_model/ui_lab_view_model.py` | `UiLabViewModel` |
| 10 | `web/lab/ui_lab/state/__init__.py` | |
| 11 | `web/lab/ui_lab/state/ui_lab_state.py` | `UiLabState`·`UiLabPanelState`·`UiLabPasswordState`·`UiLabPreviewState`·`UiLabNoteState` |
| 12 | `web/lab/ui_lab/section/ui_lab_panel.html` | root swap 단위 |
| 13 | `web/lab/ui_lab/section/ui_lab_password_field.html` | |
| 14 | `web/lab/ui_lab/section/ui_lab_preview.html` | 종속 자식 swap 단위 |
| 15 | `web/lab/ui_lab/section/ui_lab_note.html` | 독립 자식 swap 단위 |
| 16 | `web/static/js/password_visibility.js` | 기능 1파일 |
| 17 | `web/static/js/image_preview.js` | 기능 1파일 |
| 18 | `web/static/css/ui_lab.css` | 화면 CSS(`var()`만) |
| 19 | `web/static/htmx/ui_lab_panel_swap.html` | HTMX 선언 조각 — include 호스트 `section/ui_lab_panel.html`, 조건 `panel.root_swap_enabled`(§6) |
| 20 | `web/static/htmx/ui_lab_preview_swap.html` | HTMX 선언 조각 — include 호스트 `section/ui_lab_preview.html`, 조건 `preview.child_swap_enabled`(§6) |
| 21 | `web/static/htmx/ui_lab_note_swap.html` | HTMX 선언 조각 — include 호스트 `section/ui_lab_note.html`, 조건 `note.swap_enabled`(§6) |

**수정**

| # | 경로 | 변경 |
|---|---|---|
| 22 | `web/urls.py` | `path("lab/", include("web.lab.urls"))` 합산 1줄 |
| 23 | `web/design_system/foundation/tokens.css` | `--border-width-hairline: 1px` 1건 추가 |

**생성하지 않는 것(명시)**: `form/` 폴더·`ui_lab_form.py`(입력 form 없음) · `client/**`(static_only) · `web/static/js/motion.js`(러너 채택 0) · `design_system/component/**` 신설 · `test/`·테스트 파일(houserules final.md §3 — web 트랙 영구 test 없음) · `base/base.html` 수정 · `static/fonts/`·`static/files/`.

**템플릿 참조 경로**(TEMPLATES DIRS = `web/`): 페이지 `{% extends "base/base.html" %}` · section `{% include "lab/ui_lab/section/ui_lab_panel.html" with panel=state.panel_a only %}` 판형 · HTMX 선언 조각은 **페이지가 아니라 §6 표가 지정한 section에서만** `{% include "static/htmx/<조각>.html" %}`로, 같은 표의 VM 플래그 `{% if %}` 안에서 include한다(호스트·플래그 1:1은 §6·§7 확정). static 인자는 `web/js/…`·`web/css/…`·`design_system/foundation/tokens.css`.

## 13. 자기 점검

**자기모순 스캔** — 판정 소유는 전부 `UiLabViewModel` 단일(§4의 `root_swap_enabled`·`child_swap_enabled`·`swap_enabled`·revision marker)로 §2·§6·§7과 일치. 철자는 모든 절에서 `ui_lab`(어순 고정), dom id 계약은 §6 한 곳에서 확정하고 §7이 그대로 인용. 두 번째 화면 개념 없음(§2). 수량 대조: 인용 엔드포인트 0 = client 함수 0 = response 모델 0 / 절단 토큰 입력 없음(기존 토큰 9건 = 채택 9 + 기각 0) / 신규 토큰 1건 출처 기록 / manifest 항목 0 = 이미지 목록 0 / motion note 행 0 = 처분 행 0 / render-audit 항목 0 = 실측 처분 0 / fragment 라우트 3 = view 함수 3 = section swap 단위 3 = HTMX 선언 파일 3 = include 호스트 3 = 지배 플래그 3(§6 표 — 호스트·조건 1:1, 페이지 include 0). 빈칸 없음.

**백스톱 정합 스캔**(houserules final.md §4 총괄표 직접 대조) — `ui_lab_view.py` → 동명 **함수** `ui_lab_view`(CBV 아님) ✔ / 접두 `ui_lab` = view 파일 stem에서 `_view` 제거 → `ui_lab_view_model.py`·`ui_lab_state.py`·`ui_lab.html` 1:1:1:1, `ui_lab_view_view_model.py` 류 없음 ✔ / 접미사 전체 표기(`_view_model.py`·`_state.py` — 축약 없음) ✔ / section 4종 전부 소속 view 전체 접두 `ui_lab_` ✔ / widget·component 신설 0(따라서 view 이름 등장 없음) ✔ / form 클래스 규칙은 form 미생성으로 비대상 ✔ / 영역 직속은 `urls.py`·`widget/`·화면 개념 폴더·`__init__.py` 마커뿐 ✔ / 화면 개념 폴더 안 `widget/` 없음 ✔ / 종류 4폴더(view·view_model·state·section) 완비 ✔ / Python 패키지 폴더 `__init__.py`·HTML 전용 빈 폴더 `.gitkeep` ✔ / static 기능 파일 평면 snake_case ✔ / 라우트 리터럴은 `web/lab/urls.py` 단독, `web/urls.py`는 include 합산만 ✔ / `web/**`에 `application.`·`framework.` import 0(계약 소비 없음) ✔ / inline·`hx-on`·`js:` 채널 0 ✔.
