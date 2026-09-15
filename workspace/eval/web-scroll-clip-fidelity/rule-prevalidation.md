# 판정 규칙 사전 실증 — 설계 §2를 브라우저에서 돌려본 기록 (2026-09-15)

설계 `workspace/design/2026-09-15-web-clip-fidelity.md` §2의 기하 판정 규칙을 **구현 전에**
실제 Chrome 에서 프로토타입으로 돌린 결과다. 계획 단계는 이 문서의 ⓐ~ⓓ를 구현 요구로 삼는다.

## 재현물

- `repro.html` — A8 `related_person_editor_step.html` overlay=True·step=1 의 중첩 사슬과 마크업을
  그대로 옮긴 정적 페이지. CSS 6종(A8 `web/design_system/foundation/{tokens,motion}.css` ·
  `web/static/css/{base,app_shell,components,related_persons}.css`)을 **원본 그대로** 링크한다.
- `probe.js` — 설계 §2 판정 규칙의 프로토타입(포커스를 주지 않는다).
- 실행: `python3 -m http.server 8777` → Playwright Chrome · viewport 430×900 ·
  `fetch('/probe.js').then(eval)`.

## 결과 — 진짜 양성 / 진짜 음성

| 상태 | 후보 | 클리핑 조상 보유 | **발견** |
|---|---|---|---|
| 현행(패딩 0) | 9 | 9 | **6** |
| `.rpe-scroll { padding: 3px 3px 4px }` | 9 | 9 | **0** |

발견 6건(현행):

| 요소 | 잘린 축 |
|---|---|
| `div.input-field__control` | left 0.0px · right 0.0px < 3px |
| `div.select-field__control` | left 0.0px · right 0.0px < 3px |
| `div.choice-pair--md` | left 0.0px · right 0.0px · bottom 0.0px < 3px |
| `select#relation_kind` | left 1.0px · right 1.0px < 3px |
| `input#gender__female` · `input#gender__male` | left 0.0px < 3px |

**사용자 신고(«보더 좌우가 잘렸다»)와 축까지 일치**하고, 진단이 지목한 세 컴포넌트
(입력·select·choice-pair)를 전부 잡았다. 페이지의 나머지 요소에는 오탐 0.
진단의 «고칠 땐 2px 말고 3px» 권고가 정확히 발견 0 의 경계다.

`.rpe-scroll` 기하: `scrollWidth 300 = clientWidth 300` · `scrollHeight 271 = clientHeight 271`
— 이 표본에서는 양축 모두 «딱딱한 절단»이다.

## 구현 요구 — 실측으로 확정된 4가지

**ⓐ CSSOM 순회에서 «grouping rule 판별을 `rule.cssRules` 존재로 하지 말 것».**
CSS Nesting 이후 Chrome 의 `CSSStyleRule` 도 `cssRules`(길이 0)를 갖는다 — 프로토타입 1차에서
이 판별을 써서 **포커스 규칙 수확이 0건**이 됐다. 다행히 현행 `assets/render_audit.js:186,199`는
이미 올바른 판형(`rule.selectorText && rule.style` 먼저 · 재귀는 `rule.cssRules.length` 확인)이다.
**새 블록은 기존 `walkRules`를 재사용한다** — 별도 순회를 새로 쓰지 않는다.

**ⓑ 그림자 길이 파싱은 색 함수를 먼저 제거하고, 단위 없는 `0`도 길이로 받을 것.**
`0 0 0 3px rgba(208,114,122,.30)`에서 `px` 붙은 토큰만 세면 길이가 `[3]` 하나가 되어
offset-x=3 으로 오인되고 **왼쪽 확장이 −3px** 이 된다(좌측 절단을 영영 못 잡는다).
`--settings-focus-ring`은 `color-mix(in srgb,#D0727A 30%,transparent)`라 `30`도 섞여 들어온다.
→ 색 함수·`#hex`를 먼저 지운 뒤 순서대로 offset-x·offset-y·blur·spread 를 읽는다.

**ⓒ 전역 포커스 규칙의 기반 셀렉터는 빈 문자열이 된다 — 버리지 말 것.**
`base.css :: :focus-visible { box-shadow: var(--focus-ring) }`에서 의사클래스를 떼면 `''`이다.
빈 문자열을 `filter(Boolean)`으로 걸러내면 **후보가 9 → 3 으로 줄고** native control
(select·radio) 절단을 통째로 놓친다. 빈 기반 셀렉터는 표준 포커스 가능 집합으로 대체한다.

**ⓓ 조상·자손 중복 억제가 필요하다.**
`div.select-field__control`(`:focus-within` 링)과 그 안의 `select#relation_kind`(전역 링)이
같은 클리핑 조상에 대해 각각 발견으로 올라온다 — 같은 결함 1건이다.
같은 클리핑 조상 아래 조상-자손 관계면 **바깥쪽 1건만** 낸다(계수는 남긴다).

## 한계

- 이 표본은 step 1 정적 사본이다. 실제 A8 페이지의 4-step·긴 목록에서는 세로축이
  스크롤 가능해져 «딱딱한 절단»이 X 축만일 수 있다 — 규칙은 그때 세로 발견을 내지 않는다(의도대로).
- 프로토타입은 `var()` 해소를 `:root` 기준으로만 한다. 요소별 재정의가 있으면 어긋난다 —
  구현은 후보 요소의 `getComputedStyle`에서 토큰을 읽어야 한다(미검증).

---

## 추가 실측 — 그림자 바깥 확장 공식 (2026-09-15 · 적대 검토 후)

rv-A MAJOR 「`blur + spread`가 CSS 명세의 페인트 범위와 다르다 (2배 과대)」를 실측으로 검증했다.
검은 박스에 그림자 3종을 걸고 흰 배경에서 **실제 페인트 최원점을 픽셀로 측정**했다(Chrome · css scale).

| box-shadow | spread | blur | **실측 바깥 확장** | `spread+blur/2` | `spread+blur` |
|---|---|---|---|---|---|
| `0 0 20px 0` | 0 | 20 | **29px** | 10 | 20 |
| `0 0 0 10px` | 10 | 0 | **10px** | 10 | 10 |
| `0 0 20px 10px` | 10 | 20 | **39px** | 20 | 30 |

**rv-A 의 지적은 방향이 반대다** — `spread + blur` 는 2배 과대가 아니라 **과소**다.
Chrome 은 σ=blur/2 가우시안의 꼬리를 3σ 까지 칠하므로 실측 확장 ≈ `spread + 1.45×blur` 다.
`spread + blur/2` 는 «육안으로 유의미한» 범위이고 «페인트되는» 범위가 아니다.

**그래서 판정 공식을 바꾼다 — 판정 확장 = `spread + |offset|` (blur 제외).**
- 이 수리의 대상은 **링**이고, 이 코드베이스의 링은 전부 `0 0 0 3px`(blur 0)라 영향이 없다.
- blur>0 그림자는 «어디까지가 잘린 것인가»가 연속적이라 결정적 판정에 부적합하다 →
  blur 값을 기록해 **인벤토리로만** 내고 발견으로 올리지 않는다.
- 이러면 rv-A 의 지적도, 위 실측의 모호성도 둘 다 회피한다.
