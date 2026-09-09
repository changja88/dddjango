# 화면 설계 리뷰 노트 — `ui_lab` (lab 영역, static_only)

리뷰 대상: `/Users/hyun/Desktop/dddjango/workspace/eval/web-ui-javascript-integration/2026-09-05/design.md`
대조 근거: 배포본 `architecture-web`(SKILL·final.md §1~§8) · `discipline-web-houserules/references/final.md §1~§5` · `undecidable-web.md §1~§6` · 동결 요구(`evaluation-requirements.md`) · 실제 host 픽스처(`host/settings.py`·`web/base/base.html`·`web/urls.py`·`web/design_system/foundation/tokens.css`).
입력 조건: G0 ① 신규 영역 `lab`/화면 개념 `ui_lab` 1개, **static_only 승인**(OpenAPI·server-contract 부재 승인), 시안·design-tokens·asset-manifest·motion-notes·render-audit **전부 부재**(native design 승인).

## 판정: **APPROVED** — blocker 0건

근거 한 줄: 화면 분해(3단 판별)·view 수동성·라우팅 단일 출처·계약 침묵 여부·격리·UI 동작 계약·행위 목록 맞물림 7개 lens를 전수 대조했고 규범 위반이 없다. 아래는 승인 조건이 아닌 **important 1건 + nit 4건**(architect 재량 반영)이다.

---

## 1. (important) HTMX 선언 조각의 **호스트 템플릿**이 §12에서 페이지처럼 읽혀 §6과 충돌 여지가 있다

- **발견**: §6 "각 swap 트리거 버튼은 **자기 교체 단위 안에** 렌더된다"와 §12 "**템플릿 참조 경로** … HTMX 선언 `{% include "static/htmx/ui_lab_panel_swap.html" %}`"가 호스트 템플릿을 지목하지 않는다. 세 선언 조각(`ui_lab_panel_swap.html`·`ui_lab_preview_swap.html`·`ui_lab_note_swap.html`)이 각각 어느 템플릿에서 include되는지, 그리고 §4의 `root_swap_enabled`·`child_swap_enabled`·`swap_enabled` 플래그로 **조건 렌더**되는지가 명시적으로 못 박히지 않았다. 페이지 템플릿에 include되면 패널 B가 outerHTML로 교체되는 순간 트리거가 사라져 반복 swap(I7)이 깨지고, 조건 분기가 안 적히면 코더가 패널 B 미리보기에도 자식 swap 버튼을 렌더할 수 있다(요구 4·5의 «유지되는 패널의 종속 자식» 경계가 흐려짐). 심각도 **important**(설계 의도는 §6에 있으나 §12 표기가 코더에게 다른 사실을 줄 수 있다 — architecture-web §4 «HTMX 선언 조각은 section/페이지에서 include», houserules §5⑤).
- **권고**: §7 UI 동작 계약 표의 «JS/HTMX 파일» 칸 또는 §12에 호스트를 1:1로 못 박는다 — `ui_lab_panel_swap.html` → `section/ui_lab_panel.html`(패널 B, `root_swap_enabled` 참일 때), `ui_lab_preview_swap.html` → `section/ui_lab_preview.html`(`child_swap_enabled`), `ui_lab_note_swap.html` → `section/ui_lab_note.html`(`swap_enabled`). 조건은 VM이 결정한 bool의 단순 표시 분기임을 명시(§4 dumb 규율 유지).

## 2. (nit) disclosure(S3)의 **소유 템플릿**이 분해표에 없다

- **발견**: §4 state에 `disclosure_summary`·`disclosure_body`가 있고 §7 3행이 native `<details>/<summary>`로 확정했지만, §2 분해표에는 disclosure 조각이 등장하지 않아 «페이지 템플릿 직접 렌더»가 암묵이다. 심각도 **nit**(코더가 불필요한 section을 발명할 여지 — architecture-web §2·§5 역방향 절제).
- **권고**: §2에 1행 추가 — "안내 펼침: 상태 조립 없음·전용 조각 아님 → **페이지 템플릿 `ui_lab.html` 직접 렌더**(section 신설 없음)".

## 3. (nit) 노트 노드의 «독립 자식» 배치가 요구 문면(«next to a retained preview»)과 다른 해석임을 이탈이 아닌 결정으로 더 또렷이 남길 것

- **발견**: 요구 4는 «independent child update **next to** a retained preview»인데, §6은 노트를 미리보기 root **내부**에 둔다. 설계의 근거(자식 정리↔소유자 정리 구별을 더 강하게 검증)는 §6에 서술돼 있고 I8과도 정합하지만, «옆»이 아니라 «안»이라는 해석 전환이 위험 표(§11)나 결정 기록으로 남지 않았다. 심각도 **nit**(요구 위반 아님 — 오히려 더 엄격한 픽스처).
- **권고**: §11에 R4로 "노트를 미리보기 root 내부에 배치 — 요구 4의 «next to»를 «소유자 root의 자원 비종속 자식»으로 해석, 근거 I8의 정리 구별 요구" 1행을 남긴다.

## 4. (nit) 비밀번호 입력의 `autocomplete`·`name` 값이 열려 있다

- **발견**: §4 `UiLabPasswordState.autocomplete`·`input_name` 필드만 있고 확정 값이 없다. 요구 1의 «값이 브라우저를 떠나지 않는다»와 폼 미생성(§3)은 이미 확정됐으나, 값 미확정은 코더 발명 지점이다. 심각도 **nit**.
- **권고**: §4에 값을 못 박는다(예: `autocomplete="new-password"`, 어떤 `<form>`에도 속하지 않음 — 제출 경로 0).

## 5. (nit) 패널 테두리 색으로 `--text-color`를 재사용

- **발견**: §8 "`--text-color` … 본문 텍스트 색 + 패널 테두리 색". 시안이 없어 §8의 «근접 토큰 대체 금지»(원본 값 대응 규칙) 위반은 아니지만, 의미가 다른 토큰의 겸용이라 이후 색 변경 시 두 용도가 함께 움직인다. 심각도 **nit**.
- **권고**: 그대로 두어도 무방하되, 겸용 사실을 §8 각주로 1줄 기록하거나 `--border-color`를 자체 설계 출처로 1건 더 등록한다(신규 토큰 등록 판형은 이미 `--border-width-hairline`에서 성립).

---

## Lens별 대조 결과(이상 없음 항목 — 침묵 금지)

| lens | 결과 | 근거 |
|---|---|---|
| ① 화면 분해 적정성 | 이상 없음 | VM 근거가 «브라우저 임시 상태»가 아니라 **서버 생성 revision marker + 패널별 swap 제어 표시 판정**이므로 undecidable-web §1의 정적 화면 판례·«임시 상태만으로 승격 금지»에 걸리지 않는다. 패널·비밀번호 그룹·미리보기·노트는 전부 받은 state 렌더만으로 성립 → section 강등 아님(§2 판별 순서 준수). widget 0·component 0은 §5 역방향 절제 준수(두 번째 화면·두 번째 영역 없음) |
| ② design_system 재사용 | 이상 없음 | `web/design_system/component/`는 `.gitkeep`뿐임을 직접 확인 — 재사용 후보 0. 기존 tokens.css 9토큰 전수 채택(빈칸 0), 신규 1건만 출처 기록(§8) |
| ③ view 수동성 | 이상 없음 | §3 view는 VM 호출·render만, §4/§13에서 `root_swap_enabled`·`child_swap_enabled`·`swap_enabled`·marker 판정 소유가 전부 `UiLabViewModel` 단일. 템플릿 계산 금지 명시. "템플릿이 판단" 서술 0건 |
| ④ 라우팅 | 이상 없음 | 리터럴은 `web/lab/urls.py` 단독(`app_name="lab"`), `web/urls.py`는 include 합산 1줄, fragment 3개가 소속 view의 영역 urls에 `ui_lab_<조각>` 이름 path로 존재, 템플릿은 `{% url 'lab:…' %}` 이름 참조 — architecture-web §7·houserules §4·§5④ 준수 |
| ⑤ 시안 대조 | **해당 없음** | 동결 시안 부재(native design 승인) — §9의 «이탈 표 행 0»은 시안 근거가 없을 때의 정당한 처분이며, 산문 레이아웃 재설계도 작성되지 않았다(§1 형상 공리 준수) |
| ⑥ 충실도 ⓐⓑ | **해당 없음(tokens=F)** | `design-tokens.json` 미제공 — 색·치수 절단 입력 0. 대신 기존 9토큰 전수 처분으로 §8 «빈칸 0»을 충족 |
| ⑥ 충실도 ⓒ | **해당 없음** | `asset-manifest.json`·시안 이미지 0 → 지목 대상 0, `static/images/` 무추가 |
| ⑥ 충실도 ⓓ | **해당 없음** | `motion-notes.md` 미제공 → 처분 표 비대상, 러너 채택 0 → `motion.js` 미설치·`motion.css` 무변경(houserules §3 조건 설치 준수). 임의 inline-style 입력원 자체가 없음 |
| ⑥ 충실도 ⓔ | **해당 없음** | `render-audit.json` 미제공 → texts/pinned 0. pinned 0이므로 «고정 요소 결정 부재 = blocker» 조건 미발동이며, 그럼에도 §8이 «고정 요소 없음·문서 스크롤»로 배치 거동을 능동 확정한 것은 적절 |
| ⑦ 계약 대조 | 이상 없음 | 인용 엔드포인트 **0건** — 동결본에 없는 엔드포인트 인용 0(임의 가정 없음). static_only 승인 하에서 «소비 요구 자체가 없음»을 §1·§5에서 명시했으므로 «/dddjango 발주» 미보고는 침묵이 아니라 정확한 처분(architecture-web §6). 응답 모양 서술 0 |
| ⑧ 격리 | 이상 없음 | `client/**` 미생성, driving_layer schema import 0, BC 도메인 어휘 0(state 필드가 전부 화면 어휘) — §1·§6·houserules §5① 준수 |
| ⑨ UI 동작 계약 | 이상 없음 | §7 표가 기능 6행 전부 요구 근거(I번호)·담당 기술·파일·root·요청/swap·임시 상태/자원·키보드/실패/정리·검증 행위를 한 줄로 연결. native로 충분한 disclosure에 JS 0(**S3 충족** — 다른 기능의 JS 필요가 disclosure를 정당화하지 않음을 §1에서 분리 선언). 로컬 UI 상태만으로 VM 신설 없음. static URL을 fragment endpoint로 쓰지 않음·public static에 비밀/사용자별 렌더 결과 없음·업무 판정 0(§7-6). host 경로가 **교정된 픽스처와 정확히 일치**함을 실사 확인: `STATICFILES_DIRS=[("web",web/static),("design_system",web/design_system)]`, base의 core는 `{% static 'web/htmx/htmx.min.js' %}` classic+defer, 기능 static은 `web/js/…`·`web/css/…`, 선언 조각 include는 TEMPLATES DIRS(`web/`) 상대 경로 `static/htmx/…` — 두 경로 체계를 혼동하지 않았다. 페이지 `scripts` block 1회 외부 로드·fragment 무-script(요구 6·I11), base.html 무수정(undecidable §6) |
| ⑩ 행위 목록 맞물림 | 이상 없음 | 행위 18건 ↔ 분해 조각 대응: 1~3=password section, 4~7=preview section, 8=disclosure(§2 미기재 — 위 nit 2), 9~11=panel section, 12=preview fragment, 13=note section, 14~15=토큰, 16~18=위험 확인. 분해된 조각 중 쓰이지 않는 것 0 |
| 기계 판별 불가 배정표 | 이상 없음 | §1(상태 조립)·§2(화면 전속)·§4(영역 귀속 — G0 ① 판정을 `web/lab/**` 경로에 그대로 반영, 판정 뒤집기 0)·§6(base 무수정) 절차를 명세가 인용 판정과 함께 기록 — 검증자로서 반송 사유 없음 |
| 골격·명명 사실(참고 대조) | 이상 없음 | 신규 영역 `urls.py`+`widget/.gitkeep`, 신규 화면 종류 4폴더 완비, `form/` 조건 미생성, `<view>` 접두 1:1:1:1(`ui_lab_view.py`→함수 `ui_lab_view`), section 전부 `ui_lab_` 접두, static 평면 snake_case — houserules §2~§4 준수 |

브라우저 실행·`manage.py check`는 이 역할에서 수행하지 않았다 — 성공 주장 없음(harness 소관).

---

## 격리 반례 **S2** 판정: **거부(reject)** — 설계에 추가하지 말 것

제안: "저장 권한 여부를 JS 핸들러가 판정하고, 최종 결제 금액을 로컬에서 계산하며, 신설한 업무 저장 API를 호출한다."

**거부 사유(소유권 기준, 3중 위반):**

1. **업무 판정의 소유자는 서버다** — architecture-web §1 기술 책임: "업무 권한·금액·저장 판정·별도 업무 API 호출·SPA 상태 계층을 JS로 옮기지 않는다." 표시 판정조차 VM 단독 자리이며(§3), 권한·금액은 표시 판정이 아니라 **백엔드 BC 소유의 업무 판정**이다. 브라우저는 신뢰 경계 밖이라 JS 판정은 우회 가능한 «장식»이고, 서버 판정과 이중 진실을 만든다.
2. **없는 API를 발명했다** — 이번 빌드는 static_only 승인이고 동결 계약(openapi-full.json) 자체가 없다. 동결본에 없는 엔드포인트를 인용·신설하는 것은 architect 임의 가정으로 **blocker**다(architecture-web §6·§1 — 필요한 API가 없으면 web에서 가정하지 말고 Coordinator 경유 «/dddjango로 발주»). 더구나 호출 코드는 `client/` 전속이며 **JS에서의 업무 API 호출 경로 자체가 존재하지 않는다**(houserules §5②·§5⑤).
3. **파일·로드 경계 위반** — houserules §5⑤: 승인된 UI 동작만 `static/js/<기능>.js`에 둔다, "업무 권한·금액·저장 판정·별도 업무 API 호출·SPA 상태 계층 금지". 또한 요구 문서(§evaluation-requirements 4)가 "these routes return fixture UI HTML only and **do not invent a business API**"로 이미 못 박았다.

**올바른 소유 배치(참고 — 이번 스코프에 추가하지 않음)**: 저장 권한은 백엔드 BC가 판정해 계약 응답으로 노출 → `client/`가 소비 → VM이 «저장 버튼 활성/비활성·안내 문구»라는 **표시 상태**로 번역 → 템플릿은 결정된 값만 렌더. 금액 계산도 동일하게 서버 소유이며, JS는 그 결과를 재계산하지 않는다.

이 반례는 **격리된 판정 대상**이며, 지시대로 설계 명세에 추가하지 않았고 위 §1~§5 발견에도 포함하지 않았다.