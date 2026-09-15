# rv-F — 설계 v3 적대 검토 (§5 링 정적 검사 · §7 배선 · §8 합격 기준)

등급: BLOCKER 3 · MAJOR 5 · MINOR 5

담당 축: §5·§7·§8. §2·§3·§4·§6은 닿는 지점만 언급한다(§8-3 판정에 §3을 인용).
도구: Serena·Graphify 옵트인 표식(`.serena/project.yml`·`graphify-out/graph.json`)이 이 워크트리에 없어
기본 검색·실행 도구만 썼다.

---

## 0. 먼저 — 설계가 맞힌 것 (실측으로 확인)

이 넷은 반박하지 않는다. 뒤의 지적은 전부 이 바깥이다.

- **§5ⓓ 참** [실측] `python3 dddjango-web/scripts/check_clip_clearance.py ~/.herdr/worktrees/spring_dream_server/a8/web`
  → `exit 2` · `발견 12건 · 인벤토리 20건` · `[FINDING] related_persons.css :: .rpe-scroll (overflow auto) —
  top/right/bottom/left 여유 0px < 확장 3px [확정]` 4변 전부 포함. 설계가 적은 «12건 · .rpe-scroll 4변 확정»과 정확히 일치.
- **배선 4곳 실재** [확인] `dddjango-web/commands/dddjango-web.md:187`(G2 «절단 여유 정적 검사»)·`:220`(패스트트랙 ③)·
  `dddjango-web/agents/discipline-reviewer-web.md:62`(«바깥 링 절단»)·
  `dddjango-web/skills/implementation-ui/references/final.md:214`(«링 여유»). 전부 설계가 적은 내용 그대로다.
- **§5ⓐ 시안 근거 참** [실측] `design-ref/_ds/chunmong-design-system-…/styles.css` 의 `focus` 0건 ·
  `_ds_bundle.js` 의 `createElement("select")` 0건 · 번들의 링은 Dropdown 트리거 한 요소에만
  `boxShadow: … 'var(--focus-ring), var(--field-flat)'`.
- **템플릿 조인은 성립한다(검토 의뢰의 가설이 틀렸다)** [실측] `related_person_editor_step.html:64-75` 는
  `select_field.html` 을 include 하지 않고 인라인 재사용하지만, 그 인라인이 **직접** `<div class="select-field__control">`
  안에 `<select class="select-field__select">` 를 놓는다. `element_span("select-field__control")` 가
  `select_field.html` 과 `related_person_editor_step.html` **양쪽에서** 성립해 blob 에 `<select>` 가 2회 들어온다.
  include 를 따라갈 필요조차 없다.

**§5ⓑ 를 설계 문언 그대로 구현해 A8 에 돌린 결과**(시뮬레이터:
`/private/tmp/claude-501/.../scratchpad/sim_focus_ring.py`, `check_clip_clearance` 를 import 해 작성):

```
전역 링 규칙(ⓑ1)   : base.css :: :focus-visible                                  … 1건
억제 클래스(ⓑ3)    : input-field__input · textarea-field__input                  … 2건
래퍼 링 클래스 K(ⓑ2): input-field__control · textarea-field__control ·
                      choice-pair · select-field__control                        … 4건
판정(ⓑ4):
  FINDING .choice-pair            ← <input class="choice-pair__input">   미억제
  FINDING .input-field__control   ← <button class="icon-button …">       미억제
  FINDING .select-field__control  ← <select class="select-field__select"> 미억제  ← 목표 결함
  pass    .textarea-field__control ← <textarea class="textarea-field__input"> 억제
```

목표 결함은 **잡힌다.** 그러나 같이 나오는 두 건이 §5ⓐ·§8-2 의 주장을 깬다.

---

### [BLOCKER] §5ⓐ의 «select만 누락이다»는 거짓 — 같은 누락이 `.input-field__control`에도 있고, 그래서 §8-2는 실제 출력과 충돌한다

**무엇이 틀렸나.** §5ⓐ(설계 :181-182)는 «`.input-field__input`은 `components.css:323`에 억제가 있어 면제된다 —
**select만 누락**이다»라고 단정한다. 이 문장은 **요소 한 개**에 대해서만 참이고, **부품**에 대해서는 거짓이다.
`.input-field__control` 서브트리에는 억제가 걸리지 않은 포커스 가능 요소가 **또 있다** — 눈(비밀번호 보기) 아이콘 버튼이다.
설계대로 구현하면 `.input-field__control` 이 `.select-field__control` 과 **같은 등급의 발견**으로 뜬다.

**근거** [실측] 위 시뮬레이션 출력 + 실물 CSS·템플릿:

- `~/.herdr/.../a8/web/auth/login/view/login.html:50-56`
  ```html
  <div class="input-field__control">
    <i class="input-field__icon icon-lock" …></i>
    <input class="input-field__input" … type="password" …>
    <span class="input-field__trailing">
      {% include "design_system/component/button/icon_button.html" with icon="eye-off" … %}
    </span>
  </div>
  ```
  `icon_button.html:19·23·27` 이 `<a href=…>`/`<button>` 을 낸다 — 전부 포커스 가능. 같은 판형이
  `auth/signup/section/signup_step.html:118-123` 에도 있다 [실측].
- 억제는 **없다** — `~/.herdr/.../a8/web` 전체에서 `box-shadow: none` 을 가진 `:focus*` 규칙은
  `components.css:323`(`.input-field__input`)·`:392`(`.textarea-field__input`) **2건뿐**이고 `.icon-button` 은
  `components.css:196-206` 에 `:focus*` 규칙이 아예 없다 [실측]. 따라서 전역 `base.css:88-91` 의 링을 그대로 받는다.
- 모서리도 어긋난다 — `.icon-button` 은 `border-radius: var(--radius-pill)`(999px), `.input-field__control` 은
  `var(--radius-field)`(18px) [확인 `tokens.css:177·183`]. §5ⓑ4 의 «모서리 불일치» 문구가 붙는다.

**왜 BLOCKER인가.** §8-2 가 «`.input-field__input`은 **뜨지 않는다**(억제 면제가 작동)»를 합격 조건으로 박았다.
구현자는 두 갈래 중 하나로 간다 — ⓐ 출력 줄을 K(`.input-field__control`) 로 찍어 문자열만 피한다(§8-2 는 통과하지만
배너에는 input-field 가 결함으로 뜬다 → 사용자·리뷰어가 §8-2 와 배너 중 어느 쪽이 맞는지 판정 불가), 또는
ⓑ §8-2 를 만족시키려고 억제 판정을 «부품 안에 억제 규칙이 하나라도 있으면 면제»로 넓힌다 — 그러면
`.select-field__control` 은 그대로 잡히지만(억제 0건) 실무에서 select 하나만 빠뜨린 부품은 통과하게 된다.
**설계는 어느 쪽인지 정하지 않았고, 두 쪽 다 §5ⓐ의 사실 주장과 모순된다.**

**수정 방향.** §5ⓐ 의 «select만 누락»을 실측으로 교체한다 — «A8 에서 미억제 자손은 `.select-field__select` 와
`.input-field__control > .input-field__trailing` 의 `icon-button` 2계열». 그리고 §8-2 를 **요소 단위 화이트리스트**로
다시 쓴다(예: «발견 줄에 `select-field__select` 가 포함되고, `input-field__input`·`textarea-field__input` 은
어떤 발견 줄에도 등장하지 않는다 · `icon-button` 계열은 발견으로 뜨는 것이 **정상**이다»).
`icon-button` 을 결함으로 볼지 말지는 설계 판단이지만, **§7이 신설하려는 규율**(`implementation-ui final.md` —
«전역 `:focus-visible`가 있는 프로젝트는 래퍼 소유 시 자손 억제 의무»)을 문자 그대로 적용하면 결함이 맞다.
그러면 이번 수리는 «결함 1건»이 아니라 «A8 CSS 수정 2계열»을 낳는다 — 계획서에 그 비용을 적어야 한다.

---

### [BLOCKER] §5ⓑ1의 전역 링 정의가 실무 최빈 판형 2종을 통째로 놓친다 — 그 프로젝트에서 배너가 «발견 0»을 거짓 보증한다

**무엇이 틀렸나.** §5ⓑ1 은 전역 링을 «`RING_TRIGGER_RE`에 걸리고 마지막 compound에 타입·클래스·ID가 없는 규칙»으로
정의한다. ⓑ4 는 «전역 링 규칙이 **존재하고**»를 발견의 선행 조건으로 건다. 즉 ⓑ1 이 0건이면 **검사기 전체가 exit 0**이다.
그런데 «전역 포커스 링»을 쓰는 가장 흔한 두 판형이 ⓑ1 정의에 걸리지 않는다.

**근거** [실측] `check_clip_clearance.last_compound`·`CLASS_RE` 를 실제로 호출해 만든 표
(bare = pseudo 를 벗긴 나머지 · 전역? = 설계 ⓑ1 판정):

```
selector                                        last_compound              bare          전역?
:focus-visible                                  :focus-visible             ''            True   ← A8
*:focus-visible                                 *:focus-visible            '*'           True
:where(a, button, input):focus-visible          input):focus-visible       'input)'      False  ← 미탐
:is(a, button):focus-visible                    button):focus-visible      'button)'     False  ← 미탐
input:focus-visible                             input:focus-visible        'input'       False  ← 미탐
select:focus-visible                            select:focus-visible       'select'      False  ← 미탐
.theme-dark :focus-visible                      :focus-visible             ''            True   ← 오탐(스코프 무시)
html :focus-visible                             :focus-visible             ''            True   ← 오탐(스코프 무시)
:focus-visible:not(.no-ring)                    :focus-visible:not(…)      ''            True   ← 오탐(예외 무시)
```

- `last_compound`(`check_clip_clearance.py:124-129`)는 `re.split(r"[>+~]|\s+", …)` 라 **괄호를 모른다**.
  `:where(a, button, input)` 은 쉼표 뒤 공백에서 잘려 `input)` 이라는 조각이 마지막 compound 가 된다 [실측].
  A8 의 `conversation.css:212`(`[data-conversation-mount] :is(.standard-button, .round-button):focus-visible`)도
  `.round-button):focus-visible` 로 잘리고 `.standard-button` 이 **소실**된다 [실측] — 이번엔 결과가 우연히 맞지만
  같은 기계를 ⓑ1 에 그대로 쓰면 판정이 조각에 의존한다.
- 반대 방향도 위험하다. `.theme-dark :focus-visible` 는 스코프 안에서만 사는 링인데 ⓑ1 이 «대상 = 포커스 가능한
  모든 요소»로 승격한다. `:focus-visible:not(.no-ring)` 는 셀렉터가 **명시적으로** 예외를 적어놨는데도 전역으로 본다
  (§5ⓑ3 의 «억제»는 `box-shadow: none` 본문만 보므로 이 예외를 못 받는다).

**왜 BLOCKER인가.** 이 검사기는 §5ⓒ·§7 에 따라 **배너 1급 의무 표기**로 «모든 `web/` 트리»에 항상 돌게 배선된다
(commands:187 의 절단 검사와 같은 지위). 미탐이면 «이중 링: 발견 0» 이 **검증된 사실로** 배너에 오른다 —
결함이 있는데 없다고 적는 것이 결함을 못 잡는 것보다 나쁘다. 그리고 미탐 판형이 예외가 아니라 최빈이다.

**수정 방향.** ⓑ1 을 «마지막 compound» 형태 판정에서 **«대상 집합» 판정**으로 바꾼다 —
링 규칙이 걸리는 대상이 «특정 클래스 집합»으로 좁혀지지 않으면(=타입 셀렉터·`*`·`:is/:where` 안의 타입 목록만으로
구성되면) 전역으로 본다. 최소한 (ⓐ) `split_top` 을 재사용해 `:is()/:where()` 인자를 펼치고, (ⓑ) 타입 나열형
(`input:focus-visible, select:focus-visible, …`)을 «타입 링»으로 따로 수확해 그 타입의 요소에만 적용하고,
(ⓒ) 조상 스코프가 붙은 규칙은 «전역»이 아니라 «스코프 링»으로 분류해 발견 줄에 스코프를 적는다.
`last_compound` 를 그대로 쓸 수 없으므로 **§7 배선표에 `check_clip_clearance.py` 수정이 필요하다**(MAJOR 3 참조).
그리고 «전역 링 0건»을 exit 0 이 아니라 **인벤토리 1줄(«전역 링 규칙을 못 찾음 — 이 프로젝트에서는 이중 링 판정을
수행하지 않았다»)**로 낸다 — 무증상 통과를 없애는 최소 조치다.

---

### [BLOCKER] §8의 네 기준 중 어느 것도 «틀리면 red»가 되는 형태가 아니다 — 2는 항상 참이고, 3·4는 서로 모순이다

**무엇이 틀렸나.** 항목별로.

**§8-1** «절단 12건이 G2 배너에 «링 정적 검사» 항목으로 뜬다 *(이미 성립 — 회귀 확인용)*».
- 12건은 실측으로 참이다(§0). 그러나 **«G2 배너에 … 항목으로 뜬다»는 저장소에서 측정할 수 없다** — 배너는
  Coordinator(LLM)가 `commands/dddjango-web.md:187` 문안을 읽고 만드는 산문이다. 그런데 §8 는
  «1·2는 이 저장소에서 A8 사본으로 즉시 측정한다»(설계 :283)고 적었다. 측정 대상과 측정 수단이 어긋난다.
- 항목 이름도 어긋난다 — 현행 배너 문안은 «**절단 여유** 정적 검사» · «절단 여유: 발견 0» 이다
  [확인 `commands/dddjango-web.md:187`]. §5ⓒ·§8-1 이 쓰는 «링 정적 검사»로 개명하려면 commands:187·:220 ·
  `discipline-reviewer-web.md:62` · `implementation-ui/references/final.md:214` 문안을 고쳐야 하는데
  §7 배선표는 commands 행에 «링 정적 검사 항목에 `check_focus_ring` 합류»만 적고 **개명을 적지 않았다**.
- «12건» 자체를 회귀 기준으로 고정하는 것도 잘못이다(MINOR 5).

**§8-2** «`.select-field__select`가 발견으로 뜨고, `.input-field__input`은 뜨지 않는다».
- **어떤 구현에서도 후반부가 참이 된다.** ⓑ4 의 발견 단위는 K(래퍼 클래스)이고, 억제된 요소는 애초에 발견 줄에
  실리지 않는다. `input-field__input` 이라는 문자열은 발견 줄에 **나올 수가 없다** — 억제되면 빠지고,
  억제가 풀려도 줄에 찍히는 것은 K 이거나 미억제 요소(`icon-button`)다. 즉 이 기준은 **틀린 구현도 통과시킨다.**
- 동시에 실제 출력에는 `.input-field__control` 이 뜬다(BLOCKER 1) — 기준 문언과 배너가 반대말을 한다.

**§8-3·§8-4** «A8이 «재동결 → 관찰 → 원장 승인 → inputs exit 0»으로 진행 가능해진다» / «원장을 지우면 3이 다시 막힌다».
- 이 둘은 **서로 모순이다.** A8 을 현재 막는 발견은 `cases[0..11].source_observation: interaction evidence
  required (version 2 with interactions)` 12건 + `coverage_review` 1건이다
  [rv-C B2 실측 인용 — `design-review/rv-C.md:36-59`]. §3 표 1행은 이 발견 부류를 **원장이 거부**한다고 못박았고,
  유일한 예외 `no_observable_surface` 의 기계 조건은 «`has_design_screen` false 또는 시안 출처가 이미지·PDF» 인데
  A8 은 `.dc.html` 시안 빌드라 **둘 다 불성립**이다 [확인 — `design-ref/관계인.dc.html` 실재].
  → 그러므로 §8-3 의 경로는 **«관찰»이 실제로 성공해 12건이 닫히는 것**뿐이다.
- 그런데 관찰이 성공해 12건이 닫히면 **원장에 등재할 발견이 남는다는 보장이 없다**. 남지 않으면
  §8-3 은 원장 0행으로 통과하고, §8-4(«원장을 지우면 다시 막힌다»)는 **거짓이 된다** — 빈 원장을 지워도 아무 변화가 없다.
  §8-3 이 통과할수록 §8-4 가 측정 불가가 되는 구조다. §8 은 «관찰 후에도 잔여 발견이 남는다»는 전제를 적지 않았다.
- 절차도 없다 — 누가 어느 빌드에서 재동결하는지, «진행 가능»을 무엇으로 판정하는지(exit 코드? 배너?),
  «원장 승인»에 필요한 사용자 원문을 어떻게 얻는지가 §8 에 없다.

**추가로 빠진 것.** §7 은 픽스처 3종(`fixtures_ledger.sh`·`fixtures_focus_ring.sh`·`fixtures_refreeze*.sh`)을
신설·갱신한다고 적었는데 **§8 합격 기준에 픽스처도 `make verify` green 도 없다**. 이 저장소의 규범은
«커밋 전 `make verify` green»이다(`AGENTS.md` «규범 수정» 절). 저장소측에서 red 를 낼 수 있는 유일한 기준이
합격 기준에서 빠져 있다.

**수정 방향.** §8 을 «측정 명령 + 기대 출력» 표로 다시 쓴다. 최소 5행:
1. `bash dddjango-web/scripts/test/run_fixtures.sh` green (신설 `fixtures_focus_ring.sh` 포함) — 저장소 red 채널.
2. `check_clip_clearance.py <A8 web>` → exit 2 · `.rpe-scroll` 4변 «확정» 포함 (문구 고정, 건수 비고정).
3. `check_focus_ring.py <A8 web>` → exit 2 · 발견 줄에 `select-field__select` 포함 ·
   `input-field__input`·`textarea-field__input` 미포함 · **그 외에 어떤 K 가 뜨는 것이 정상인지 전수 명시**
   (`choice-pair` 오탐 처분 · `input-field__control` 처분 — BLOCKER 1·MAJOR 2).
4. `check_design_evidence.py --phase inputs` → **원장 0행에서 exit 2, 원장 N행에서 exit 0** 를 **같은 관찰 상태로**
   비교한다(관찰을 바꾸지 않고 원장만 토글) — 이래야 3·4가 원장의 효과를 분리 측정한다.
5. `make verify` green.

---

### [MAJOR] §5ⓑ3의 «억제 = `box-shadow: none`» 은 A8에 이미 5건 있는 «다른 링으로 덮어쓰기» 판형을 놓친다

**무엇이 틀렸나.** 전역 링을 무효화하는 방법은 `none` 만이 아니다. 더 높은 특이도로 **다른 box-shadow 를 선언**하면
링은 «추가»되지 않고 «교체»된다 — 이중 링이 아니다. §5ⓑ3 은 이것을 억제로 세지 않으므로 오탐이 된다.

**근거** [실측] A8 에 이 판형이 이미 5건 있다(지금은 K 서브트리 밖이라 발화하지 않을 뿐이다):
- `static/css/settings.css:423-428` — `a.settings-display-row:focus-visible, .home-bottom-nav__button:focus-visible,
  .settings-action-button:focus-visible { outline:none; box-shadow: var(--settings-focus-ring); }`
- `static/css/conversation.css:212-215`·`:896-899` — `box-shadow: var(--focus-ring);` 재선언.
- `static/css/related_persons.css:109-112` — `.rp-row:focus-visible { outline:none; box-shadow: var(--focus-ring); }`

`.rp-row` 하나만 `:focus-within` 래퍼 안으로 들어가면 즉시 오탐이다. 특이도·선언 순서도 보지 않는다 —
`components.css:321-322` 의 주석이 «(0,2,0 > 전역 0,1,0)»을 근거로 적어놓은 바로 그 축이다 [확인].
`box-shadow: var(--shadow-none)`(토큰이 `none`이 아니라 `0 0 0 0 transparent` 인 경우)·`all: unset` 도 못 본다
(A8 에 `all:` 리셋은 0건 [실측] — 일반 위험으로만 남는다).

**수정 방향.** ⓑ3 을 «`:focus*` 셀렉터가 그 요소를 잡고 본문에 `box-shadow` 선언이 있으면 억제»로 넓힌다
(값이 `none`이든 다른 그림자든 **교체**이므로 이중 링이 아니다). 그리고 선언 순서 — 같은 파일에서 전역 규칙보다
뒤에 오는지 — 를 최소한 인벤토리로 고지한다.

---

### [MAJOR] 시각적으로 숨긴 입력(`clip: rect(0,0,0,0)`)이 체계적 오탐이다 — A8에서 실제로 1/3이 이 오탐이다

**무엇이 틀렸나.** «래퍼가 링을 소유하고 native 입력은 시각적으로 숨긴다»는 라디오·체크박스·스위치의 **표준 판형**이다.
숨긴 입력은 링을 그릴 수 없으므로 이중 링이 아니다. §5ⓑ4 는 이것을 구별하지 못한다.

**근거** [실측] 위 시뮬레이션의 `FINDING .choice-pair ← <input class="choice-pair__input"> 미억제`.
```css
/* components.css:623-633 — 시각적으로 숨긴 native radio (키보드 포커스·화살표 이동 유지) */
.choice-pair__input { position:absolute; width:1px; height:1px; margin:-1px;
                      padding:0; overflow:hidden; clip: rect(0,0,0,0); border:0; }
```
`clip` 은 절대 배치 요소의 **페인트 전체**(box-shadow 포함)를 잘라낸다 — 링은 화면에 나타나지 않는다.
`.choice-pair:focus-within` 이 래퍼에 링을 주는 것이 의도된 동작이다. **오탐.**
A8 에는 같은 은닉 판형이 `.checkbox__input`·`.radio-option__input` 에도 있다 [실측 — 둘 다 clip 검사기
인벤토리에 «링 보유 요소 없음»으로 이미 등장]. 이 둘에 `:focus-within` 링 래퍼가 붙는 순간 오탐이 3배가 된다.

A8 발화 3건 중 1건이 이 오탐이므로 «실용성 파괴»는 아니다 — 그래서 MAJOR 다. 다만 **이 오탐 부류는 프로젝트마다
컴포넌트 수에 비례해 늘어난다**(디자인 시스템일수록 많다).

**수정 방향.** 은닉 판형을 억제로 인정한다 — 대상 요소 규칙에 `clip: rect(0` · `clip-path: inset(50%)` ·
`width:1px`+`height:1px`+`overflow:hidden` 조합 · `opacity:0` · `appearance:none`+크기 0 중 하나가 있으면
«시각 은닉»으로 분류해 발견에서 빼고 인벤토리로 낸다. `padding_of` 와 같은 판형으로 `check_clip_clearance` 의
`resolve`·`px` 를 재사용할 수 있다.

---

### [MAJOR] §5ⓑ의 «check_clip_clearance를 import 해서 쓴다(중복 구현 금지)» 전제가 절반만 참이다 — 정작 필요한 두 조각이 `main()` 안에 있고, §7 배선표에 그 파일이 없다

**무엇이 틀렸나.** 모듈 import 자체는 성립한다 [실측] — 최상위에 부작용이 없고 `if __name__ == "__main__":` 가드가
있다(`check_clip_clearance.py:394-395`). 지목된 13개 이름(`read_css`·`root_variables`·`resolve`·`shadow_extent`·
`members`·`last_compound`·`template_graph`·`element_span`·`expand`·`px`·`split_top`·`RING_TRIGGER_RE`·
`FOCUSABLE_RE`)도 전부 모듈 최상위에 있다. **그러나 §5ⓑ의 4단계 중 2단계를 지탱하는 코드는 import 할 수 없다.**

**근거** [확인]
- **전역 링 판정**은 함수가 아니다 — `main()` 안의 지역 표현식이다(`check_clip_clearance.py:332-334`,
  `global_ring = max((ext for … if not CLASS_RE.search(last_compound(selector))), …)`). 게다가 판정 기준이
  §5ⓑ1 과 **다르다**(클래스만 본다 → `a:focus-visible` 을 전역으로 본다).
- **요소↔클래스 조인**도 함수가 아니다 — `present(cls)` 는 `main()` 안에 중첩 정의돼 있다(`:351-353`).
  게다가 `present` 는 **blob 전체에 그 클래스가 있는가**만 본다. §5ⓑ4 가 필요한 것은
  «이 포커스 가능 **요소**가 억제 클래스를 갖는가»라는 **요소 단위** 판정인데, 그런 기본 도구가 없다.
- **border-radius 기계는 아예 없다** [실측 — `dir(check_clip_clearance)` 에 radius 관련 이름 0개].
  §5ⓑ4 의 «그 요소의 `border-radius`가 K와 다르면»을 구현하려면 shorthand 4값·`/` 타원 반경·`var()` 해소·
  규칙 간 캐스케이드를 새로 써야 한다. `padding_of` 를 본떠야 하는 분량이다.
- 그런데 **§7 배선표에 `scripts/check_clip_clearance.py` 행이 없다**. 이 파일을 고치면
  `codex-dddjango-web/skills/dddjango-web/scripts/` 와 **byte 동일 미러**를 같이 갱신해야 하고
  (`Makefile:96` `diff -rq --exclude=__pycache__ …`), `fixtures_clip_clearance.sh` 회귀(18+ 케이스)를 다시 돌려야 한다.
  계획에 없는 작업이 §5 의 전제에 숨어 있다.

**수정 방향.** §7 배선표에 `scripts/check_clip_clearance.py` 행을 추가하고 내용을 «`global_ring`·`present` 를
모듈 수준 함수로 추출(동작 보존) + `radius_of` 신설»로 명시한다. 추출은 순수 리팩터라
`fixtures_clip_clearance.sh` 가 그대로 green 이어야 한다 — 그 자체를 §8 의 한 줄로 넣는다.
`__pycache__` 는 `Makefile:96` 에서 이미 제외되므로 문제가 아니다 [확인].

---

### [MAJOR] §5ⓒ의 «배너 한 항목으로 묶는다»가 «exit 1 = 미실행»을 은폐한다 — 그리고 종료 코드 2개의 합성 규칙이 없다

**무엇이 틀렸나.** 현행 배너 항목은 종료 코드와 1:1로 묶여 있다 —
`commands/dddjango-web.md:187` 은 «발견 0이면 «절단 여유: 발견 0» 1줄. **exit 1은 미실행 취급**이다»라고 적는다.
두 명령을 한 항목으로 합치면 «clip exit 2 · focus_ring exit 1» 같은 조합에서 **미실행이 발견 건수에 묻힌다.**
설계는 «배너 줄 수 증가 0»만 적고 합성 규칙을 주지 않았다.

**근거** [확인] `commands/dddjango-web.md:187` 의 절단 항목 원문(발췌):
> **절단 여유 정적 검사(항상 — `web/` 트리가 있으면 시안 유무와 무관)**: … **결과는 배너 1급 의무 표기**이고
> 지위는 compare와 같은 **판단 자료(비차단)**다 — «확정»(여유 0)은 반송 근거로, «경미»(0<여유<확장)는 수락 가능한
> 이탈로 구분해 제시한다. … 발견 0이면 «절단 여유: 발견 0» 1줄. **exit 1은 미실행 취급**이다.

- 두 검사기는 **발견 어휘가 다르다** — clip 은 «확정/경미»(반송 근거 / 수락 가능), focus_ring 은
  «직각 링/모서리 불일치»다. 한 줄로 합치면 «반송 근거인가 아닌가»가 사라진다.
- `commands:220`(패스트트랙 ③)은 `check_clip_clearance.py` 한 명령만 나열하고, 괄호 안 사유가
  «패스트트랙은 «토큰 값 수정»을 포함하므로 padding·overflow 변경이 두 게이트 없이 통과하던 자리다»로 적혀 있다 —
  focus_ring 을 합류시키려면 이 사유 문장도 고쳐야 한다(`border-radius`·`box-shadow` 토큰 수정이 같은 자리다).
  §7 은 «패스트트랙 ③ 합류»만 적고 사유 문안을 안 적었다.
- Codex 미러 `codex-dddjango-web/skills/dddjango-web/SKILL.md:210`·`:243` 이 같은 문안의 의미 미러다 [확인] — 동반 갱신 대상.

**수정 방향.** 항목 문안에 합성 규칙을 명시한다 — «두 명령을 각각 실행한다. **어느 하나라도 exit 1이면 그 명령은
«미실행 + 사유»로 따로 적는다**(건수에 합치지 않는다). 둘 다 실행됐으면 «링 정적 검사: 절단 N건(확정 a·경미 b) ·
이중 링 M건» 한 줄». 줄 수는 그대로 1줄이면서 미실행이 숨지 않는다.

---

### [MAJOR] 조인 한계가 §5ⓒ 계약에 없다 — 부품 단독으로는 결함이 안 보이고, `element_span`은 템플릿당 첫 일치만 본다

**무엇이 틀렸나.** `check_clip_clearance` 는 «조인 실패»를 **명시 출력**하고 마지막에
«조인 한계 — include/extends 만 따라간다(동적 클래스 부착은 못 본다)» 1줄을 항상 낸다(`:348`·`:389`) —
모듈 docstring 이 «조용한 강등은 미탐 통로다»라고 그 이유를 적어놨다 [확인]. §5ⓒ 의 계약에는 그 의무가 없다.
그런데 focus_ring 쪽 조인 한계가 clip 보다 **더 크다.**

**근거** [실측]
- `design_system/component/field/input_field.html:25` 의 trailing 슬롯은 `{{ trailing|safe }}` 다 —
  **정적으로는 비어 있다.** 부품 파일만 보면 `.input-field__control` 은 결함이 없다. 결함은 호출처
  (`login.html:53-55`·`signup_step.html:121-123`)가 `icon_button.html` 을 include 할 때만 보인다.
  호출처가 문자열 변수로 넘기는 판형이면 **미탐**이다.
- `element_span` 은 정규식 `search` 라 **템플릿당 첫 일치만** 본다(`:223-226`). A8 `signup_step.html` 에는
  `.input-field__control` 이 2개 있고(`:90`·`:118`) 둘째만 눈 버튼을 갖는다 — 이번엔 login.html 이 대신 잡아줘서
  결과가 같지만, 한 템플릿에만 존재하는 판형이면 놓친다.
- Django 템플릿의 `class` 속성에는 템플릿 문법이 섞인다 — 나이브 추출이 깨진다(MINOR 3).

**수정 방향.** §5ⓒ 계약에 clip 과 같은 의무를 넣는다 — «조인 실패는 인벤토리로 **명시**한다 · 마지막 줄에 조인 한계를
항상 고지한다 · 슬롯(`{{ … |safe }}`)만 있는 서브트리는 «슬롯 미해소» 인벤토리로 낸다».
`element_span` 을 `finditer` 로 넓히는 것은 clip 과 공유되는 동작 변경이므로 별건으로 분리하고, 이번에는
«첫 일치만 본다»를 고지 문구에 넣는다.

---

### [MINOR] `die()`가 `[clip-clearance]` 접두로 exit 1 한다 — focus_ring의 출력 계약과 어긋나고, CSS 0건 프로젝트가 «발견 0»이 아니라 «미실행»이 된다

`check_clip_clearance.py:69-71` 의 `die()` 는 `print(f"[clip-clearance] {msg}")` 후 `sys.exit(1)` 이다 [확인].
`read_css` 를 import 해 쓰면 `check_focus_ring.py` 가 `[clip-clearance] CSS 규칙이 없다: …` 를 내고 죽는다 —
배너·리뷰어가 접두로 항목을 가른다면 오귀속이다. 또 «CSS 가 하나도 없다»는 focus_ring 에게는 «링 규칙 0 = 발견 0»이
자연스러운데 exit 1(미실행)이 된다. 수정: `read_css` 에 `prefix` 인자를 주거나, focus_ring 이 `RULE_RE` 수확을
직접 감싸 자체 접두로 보고한다.

### [MINOR] `RULE_RE`가 `@media` 블록을 평탄화한다 — 조건부 링 규칙이 무조건 규칙으로 승격된다

`RULE_RE = r"([^{}]+)\{([^{}]*)\}"`(`:42`)는 at-rule 프렐류드를 삼키고 안쪽 규칙만 잡는다.
A8 실측 예: `static/css/app_shell.css:57-64` 의 `@media (max-width:480px) { .app-frame { … box-shadow: none } }` 가
무조건 `.app-frame { box-shadow: none }` 으로 수확된다 [실측]. A8 의 `@media` 는 전부 `max-width`·
`prefers-reduced-motion` 이라 링과 무관하지만, `@media (forced-colors: active)`·`(prefers-contrast: more)` 에
포커스 링을 덮어쓰는 것은 흔한 판형이다. 최소한 `@media` 안의 `:focus*` 규칙을 인벤토리로 고지한다.

### [MINOR] Django 템플릿의 `class` 속성에 템플릿 문법이 섞여 나이브 클래스 추출이 깨진다

[실측] `icon_button.html:19` 의 `class="icon-button icon-button--{{ size|default:'sm' }}{% if variant %} …"` 를
공백 분할하면 `['%}', 'endif', 'icon-button', "size|default:'sm'", '}}{%', …]` 가 나온다.
§5ⓑ4 의 «억제되지 않은 포커스 가능 요소» 판정은 요소별 클래스를 뽑아야 하는데, 이 판형에서 잘못된 토큰을 만든다.
`check_clip_clearance.present()` 가 쓰는 «`class="…"` 안에서 단어 경계로 찾기» 정규식을 요소 단위로 재사용해야 한다.

### [MINOR] §5ⓑ2의 «대상 클래스 K»가 last_compound 클래스인지 셀렉터 전체 클래스인지 정해져 있지 않다

A8 `static/css/user_info.css:131` 의 `.user_info__field .input-field__control:focus-within` 에서 갈린다 —
last_compound 면 K = `input-field__control`(현 시뮬레이션), 전체면 K 에 `user_info__field` 가 추가된다.
후자면 서브트리가 `user_info_hour_field.html` 전체가 돼 `checkbox__input`(시각 은닉)까지 들어와 오탐 1건이 는다
[실측 — 그 서브트리에 포커스 가능 4개]. 설계에 «K = `:focus-within` 이 붙은 compound 의 클래스»라고 못박는다.

### [MINOR] §8-1의 «12건»을 회귀 기준으로 고정하면 무관한 CSS 수정마다 red 가 된다

12 는 A8 의 현재 값이지 불변식이 아니다 — 패딩 한 줄만 고쳐도 11 이 된다. §5ⓓ 가 이미 적은
«`.rpe-scroll` 4변 확정 포함»이 올바른 기준이다. §8-1 의 «12건»을 «`.rpe-scroll` 4변 «확정» 줄이 나오고 exit 2»로
바꾼다(§0 의 실측 출력이 그대로 기대 문자열이 된다).
