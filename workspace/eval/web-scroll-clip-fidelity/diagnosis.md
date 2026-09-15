# 진단 — 포커스 링 좌우 절단: 시안 레이아웃 값 누락 + 상태 미대조 (2026-09-15)

수리 1(증거 부채 hook · v1.1.14)과 별건. 같은 A8 관계인 화면에서 사용자가 09-15에 지목한 «보더 좌우가 잘렸다».

## 증상

A8 관계인 편집기 step 1의 이름 입력(`design_system/component/field/input_field.html` · icon=user-round · placeholder «이름을 입력해주세요»)에 **포커스가 들어간 상태**에서 둥근 테두리 바깥의 포커스 링이 좌우로 잘린다. 사용자 스크린샷의 아이콘이 accent 색이라 `:focus-within` 상태임을 알 수 있다.

로그인·사용자정보 화면의 같은 컴포넌트는 멀쩡하다 — 그 입력들은 패딩 있는 패널/카드 안에 있어 링이 놓일 자리가 있다.

## 원인 (Chrome 실측)

- 포커스 시 `components.css:292-296` `.input-field__control:focus-within { box-shadow: var(--focus-ring), … }` · `tokens.css:193` `--focus-ring: 0 0 0 3px rgba(208,114,122,.30)` — **바깥쪽 3px** 그림자.
- 그 입력이 든 스크롤 컨테이너 `related_persons.css:393-400` `.rpe-scroll { overflow-y: auto; }` — CSS 규칙상 한 축이 `visible`이 아니면 다른 축도 `auto`로 계산돼 **가로도 클리핑**된다. 패딩 0이고 `.input-field__control`이 컨테이너 폭을 꽉 채우므로 링 3px가 통째로 잘린다(box-shadow는 스크롤 오버플로에 잡히지 않아 스크롤바도 생기지 않는다).
- **시안은 이 문제를 알고 있었다**: `design-ref/관계인.dc.html:108` — `<div data-cm-dialog-scroll="{{ bodyScroll }}" style="display:flex; flex-direction:column; gap:var(--space-6); padding: 2px 2px 4px;">`.
- 명세 `design-spec.md:446`이 그 컨테이너를 «web `.rp-dialog__body{overflow-y:auto; min-height:0}`»로 옮기면서 **패딩을 빠뜨렸고** coder가 그대로 구현했다(커밋 `7ad4b1f7` S3 에디터 화면 사슬).

실측(실제 CSS + 템플릿 마크업 그대로 · 430×900 · deviceScaleFactor 2 · Chrome):

| 대상 | scroll overflow-x | 패딩 | 링 여유(좌/우) | 결과 |
|---|---|---|---|---|
| 구현 현재 | auto | 0 | 0 / 0 | 링 좌우 절단(사용자 스크린샷과 동일 재현) |
| 시안(`관계인.dc.html` sha `cf2fe3486ca8…`) | auto | 2px 2px 4px | 2 / 2 | 1px만 잘려 사실상 온전 |
| 구현 + `padding: 3px 3px 4px` | auto | 3px 3px 4px | 3 / 3 | 링 온전 |

시안의 2px는 링 spread 3px보다 1px 작다 — 그대로 옮겨도 1px는 잘린다. 고칠 때는 3px를 권한다.

**같은 컨테이너의 다른 요소도 같이 잘리고 있다**: 관계·시·도 `select-field__control:focus-within`(`components.css:838`), 윤달·몰라요 체크박스의 checked 링(`components.css:729` — 왼쪽 끝에 붙어 있어 더 심함), 성별 `choice-pair:focus-within`(`components.css:618`).

## 재현 방법 (scratchpad는 정리됨 — 다시 만들 때 이대로)

1. A8에서 CSS 6개를 scratch로 복사: `web/design_system/foundation/{tokens,motion}.css` · `web/static/css/{base,app_shell,components,related_persons}.css`.
2. `related_person_editor_step.html`의 overlay=True·step=1 마크업을 그대로 옮긴 `repro.html` 작성(`.app-shell > .app-frame > .app-frame__body > .app-frame__content > .rp-page > #rp-overlay > #rpe-step.rp-dialog.rpe-dialog > form.rp-dialog__panel > .rp-dialog__inner > .rpe-scroll > .rpe-fields`).
3. Playwright로 `#display_name` focus 후 `.rpe-scroll`·`.input-field__control`의 `getBoundingClientRect()` 차이(left/right 여유)와 `getComputedStyle(scroll).overflowX/padding`을 읽고 컨트롤 주변을 clip 스크린샷.
4. 시안 쪽은 `design-ref`를 `python3 -m http.server`로 서빙 → `관계인.dc.html` 열고 «관계인 등록하기» 클릭 → 같은 placeholder에 focus 후 같은 계측.
   (Playwright 모듈은 `/Users/hyun/.npm/_npx/9833c18b2d85bc59/node_modules/playwright` · ESM에서는 `+ "/index.js"` 와 `mod.default ?? mod` 필요.)

## 왜 플러그인이 못 잡았나 — 갭 2개

**갭 1 — 시안 컨테이너의 리터럴 레이아웃 값이 전수 연결 그물 밖**
`skills/architecture-web/references/final.md:142` 「크기 전수 연결」은 **토큰**(색·치수 토큰)만 빈칸 0으로 강제한다. 시안 구조 컨테이너에 인라인으로 박힌 `padding`·`gap`·`margin`·`overflow` 같은 리터럴 값은 채택/기각을 요구받은 적이 없다. 그래서 `padding: 2px 2px 4px`는 아무도 처분하지 않고 사라졌다.

**갭 2 — 포커스 상태가 구현 대조(G2)의 case가 아니다**
- G2 대조는 `design-input.json`의 case 단위인데, v1.1.13 계약(`design-evidence.md:310-314`)은 case 의무를 **새 표면을 만드는 step**(`changes.added` 비어 있지 않음 — 메뉴·다이얼로그 열림)에만 걸고 **fill·focus 같은 value-only step은 «의무 없음»으로 명시**한다. 포커스 링은 포커스 상태에서만 보이므로 case로 올라가지 않는다.
- A8 구현 캡처 11장 어디에도 포커스 상태가 없다(`captures/related-390x844-*.png`).
- 렌더 실측 `render-audit.json`은 목록 상태의 `texts`·`pinned`·`motion`만 재고 컨테이너 기하·오버플로를 보지 않는다.
- `motion-notes.md:14` m2가 «focus/press — transition-control + press-scale · CSS · 스캔»으로 채택을 기록했지만 이는 **CSS 규칙의 존재 확인**이지 렌더 결과 확인이 아니다.

수리 1(증거 부채 hook)은 이 둘 중 어느 것도 잡지 못한다 — 조작 상태를 «관찰했는가»는 묻지만 «관찰한 상태가 시안과 같은가»는 다른 축이다.

## 수리 방향 후보 (설계 단계에서 확정)

**수리 2 — 시안 레이아웃 값 전수 연결**
동결 시 dc HTML 구조 컨테이너의 인라인 선언(`padding`·`gap`·`margin`·`overflow`·`min-height` 등 레이아웃 축)을 기계 추출해 표로 만들고, 명세가 행마다 채택/기각을 적게 한다(빈칸 0). 판형 선례 2건: architecture-web 「크기 전수 연결」·`check_motion_spec.py` 처분 표(헤더 행 byte 고정 파스 앵커). 오늘 케이스면 `padding: 2px 2px 4px` 행이 빈칸으로 남아 red.

**수리 3 — 포커스 링 클리핑 결정 검사**
case 의무를 fill까지 넓히지 않는다(모든 빌드의 case 수·비용 상승). 대신 이미 브라우저를 띄우는 렌더 실측에 검사 1종 추가: outer `box-shadow`가 붙는 focus 규칙의 대상마다 포커스시켜 재고, 가장 가까운 `overflow ≠ visible` 조상의 패딩 박스까지 여유가 spread(3px)보다 작으면 결함. 결정적이고 화면 수에 비례하지 않는다.

둘 다 «A8은 먼저 고치지 않는다»([[a8-final-testbed]]) — 플러그인을 고치고 배포한 뒤 A8 세션이 스스로 잡는지가 최종 시험이다.

## 절차

[[web-repair-procedure]]대로: 이 진단 → 설계(`workspace/design/`) → 독립 적대 검토 → 계획 → 계획 리뷰 → 사용자 승인 → 구현(정본+Codex 미러) → 행동 시험 → 독립 구현 리뷰 → `make verify` → 승인 후 커밋·`make release-web`. 수리 1의 규모 선례: Task 4개 · 서브에이전트 리뷰 2회 · A8 드라이런 0회 · release-web 19분(브라우저 스위트 1149초 포함).
