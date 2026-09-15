# 적대 검토 A — 설계 v1 §2(수리 3) 기하 판정 규칙 (2026-09-15)

대상: `workspace/design/2026-09-15-web-clip-fidelity.md` v1 §2.1~§2.3.
담당 축: 판정 규칙의 거짓음성·거짓양성만. §3(수리 2)·§4(규범 편집)·§5·§6은 다른 검토자 소관이며
여기서는 §2의 규칙이 틀렸다는 논증에 필요한 만큼만 인용한다.

**실측 환경**: 실제 Chrome(`channel: 'chrome'` · Playwright) · 500×600 · 합성 픽스처.
아래에서 «실측»이라고 표시한 수치는 이 세션에서 직접 돌린 값이다. 표시 없는 명세 인용은 CSS 명세 조문이고,
«미확인»은 근거를 못 만든 추정이다.

---

### [BLOCKER] `:focus` 셀렉터에서 출발하는 열거가 진단이 같은 결함으로 지목한 요소 하나를 구조적으로 못 본다

**무엇이 틀렸나.** §2.2는 후보 열거를 «v2가 이미 수집하는 CSSOM `focusSelectors`에서 시작»한다.
`focusSelectors`는 셀렉터에 `:focus` 문자열이 든 규칙만 담는다. 그런데 진단이 «같은 컨테이너의 다른 요소도
같이 잘리고 있다»며 명시한 4건 중 하나가 `:focus`를 전혀 쓰지 않는다:

```css
/* components.css:727-730 */
.radio-option__input:checked + .radio-option__marker {
  border-color: var(--accent);
  box-shadow: var(--focus-ring);   /* ← 바깥 3px 링. 셀렉터에 :focus 없음 */
}
```

이 규칙은 `:checked` + 인접 형제 조합자다. 링 토큰은 `--focus-ring` 그대로인데 발화 조건이 포커스가 아니라
체크 상태다. 진단이 «왼쪽 끝에 붙어 있어 더 심함»이라고 적은 바로 그 요소이고, §2의 규칙대로 구현하면
`focusSelectors`에 없으므로 후보가 되지 않는다 — 영영.

같은 파일의 `.checkbox__input:checked + .checkbox__box { box-shadow: var(--shadow-1) }`(components.css:793-797)도
바깥 그림자(`--shadow-1: 0 1px 2px …, 0 3px 10px …`)를 붙이며 같은 이유로 열거 밖이다.

**근거.**
- `/Users/hyun/Desktop/dddjango/dddjango-web/assets/render_audit.js:197` — `if (rule.selectorText.includes(':focus')) push('focusSelectors', sel);` (다른 상태 규칙은 수집 채널이 없다)
- `/Users/hyun/.herdr/worktrees/spring_dream_server/a8/web/static/css/components.css:727-730`, `:793-797`
- 진단 `diagnosis.md:28` — 이 요소를 같은 결함의 일부로 명시
- 설계 §2.2 1~4단계 전부가 `focusSelectors` 하류다

**수정 방향.** 후보 축을 «포커스 규칙»이 아니라 «바깥 그림자를 선언하는 상태 규칙»으로 잡는다 — 링 토큰
(또는 바깥 box-shadow) 기준으로 CSSOM을 훑고, 상태 의사클래스(`:focus*`·`:checked`·`:hover`·`[aria-*]`·
`.is-*`)를 떼어 기반 셀렉터를 만든다. 아니면 설계가 «이번 결함의 일부(radio checked 링)는 이번 범위 밖»임을
명시적 미착수로 적고 진단과의 차이를 남긴다. 조용히 빠지는 것이 문제다.

---

### [BLOCKER] «딱딱한 절단 축» 정의가 `overflow:hidden`·`overflow:clip`을 soft로 오판해 가장 단단한 클립을 면제한다

**무엇이 틀렸나.** §2.1은 hard를 `scrollSize <= clientSize`로 정의하고, 그 밖의 축은 «브라우저가 포커스를
스크롤로 끌어오»니 결함이 아니라고 면제한다. 그런데 `scrollWidth`/`scrollHeight`는 **스크롤 가능 여부와
무관하게 콘텐츠 크기를 돌려준다**.

실측(실제 Chrome):

| 컨테이너 | computed overflowX | scrollWidth | clientWidth | §2.1 판정 | 실제 |
|---|---|---|---|---|---|
| `overflow:hidden` + 300px 자식 | `hidden` | **300** | 100 | soft → 면제 | 사용자가 휠·터치로 못 민다 |
| `overflow:clip; overflow-clip-margin:8px` + 300px 자식 | `clip` | **300** | 100 | soft → 면제 | 스크롤 박스 자체가 없다 |

`overflow:clip`은 스크롤 박스를 만들지 않는다(CSS Overflow 3 §3 — clip은 scroll container를 생성하지 않음).
그런데도 Chrome은 `scrollWidth` 300을 보고한다. 즉 §2.1의 술어는 **절대로 스크롤로 드러낼 수 없는 축**을
정확히 «스크롤로 드러낼 수 있는 축»으로 분류한다 — 규칙의 의도와 정반대다.

`overflow:hidden`도 마찬가지다. 프로그램적 스크롤은 되지만 사용자 제스처로는 못 민다. «긴 목록이 세로로
잘리는 건 정상»이라는 면제 근거는 `hidden`에 성립하지 않는다.

**근거.** 이 세션 실측(위 표) · CSS Overflow Module Level 3 §3(clip은 scroll container 아님) ·
설계 `2026-09-15-web-clip-fidelity.md:46-48`.

**수정 방향.** hardness를 `scrollSize <= clientSize`가 아니라 **computed `overflow-<axis>` 값**으로 판정한다 —
`hidden`·`clip`은 무조건 hard, `auto`·`scroll`만 soft 후보로 놓고 거기에 크기 조건을 얹는다. `overflow:clip`은
`overflow-clip-margin`(실측 `8px` 파싱 가능)을 클립 가장자리에 더해야 한다.

---

### [BLOCKER] soft 축이어도 시작 변·끝 변의 링은 영구 절단인데 규칙이 통째로 면제한다 — 시안이 준 `4px` 하단 패딩의 근거를 이 검사는 못 잡는다

**무엇이 틀렸나.** box-shadow는 **scrollable overflow에 기여하지 않는다**(진단 `diagnosis.md:14`도 같은 말).
따라서 스크롤 가능한 축이라도:

- 시작 변(LTR의 좌·상): `scrollTop`/`scrollLeft`의 하한이 0이므로 패딩 박스 밖으로 나간 링은 도달 불가.
- 끝 변(우·하): 최대 스크롤 위치에서 마지막 콘텐츠의 바깥 변이 패딩 박스 변과 **정확히 일치**한다. 그 밖의
  링은 스크롤 여지가 없다.

실측(세로 `overflow-y:auto` 120px 뷰 · 40px 아이템 4개 · 마지막 아이템에 `box-shadow: 0 0 0 3px`):

```
scrollHeight 160 · clientHeight 120 · maxScrollTop 40        ← 그림자가 scrollHeight를 늘리지 않음
최대 스크롤 시 last.bottom = 128 · scroller.bottom = 128     ← 여유 0px, 하단 3px 링은 영구 절단
scrollTop 0 에서 first.top = 8 = scroller.top + border 0     ← 상단도 영구 절단
```

§2.1은 이 컨테이너의 세로축을 `scrollHeight(160) > clientHeight(120)`이므로 soft로 보고 **면제**한다.
그런데 진단이 발굴한 시안 인라인 값은 `padding: 2px 2px 4px` — **하단이 4px로 더 크다**. 시안이 하단에 더
준 이유가 바로 이 끝 변 절단이다. 즉 이 규칙은 시안이 명시적으로 해결해 둔 축을 검사 대상에서 제외한다.
`.rpe-scroll`은 실제로 세로 스크롤되는 컨테이너이므로 A8에서 실물로 해당한다.

덧붙여 면제의 명시적 근거(«브라우저가 포커스를 스크롤로 끌어온다»)도 반만 맞다. `scrollIntoView`/포커스
스크롤이 멈추는 자리는 `scroll-padding`(컨테이너)·`scroll-margin`(대상)이 정한다. 둘 다 없으면 대상의
**border box**가 패딩 변에 딱 붙어 링은 여전히 잘린다. A8의 `.rpe-scroll`에는 `scroll-padding`이 없다
(`related_persons.css:393-400` 전문 확인).

**근거.** 이 세션 실측(위) · CSS Overflow 3 §3(scrollable overflow region은 ink overflow인 box-shadow를
포함하지 않음) · CSS Scroll Snap / `scroll-padding` 명세 · `diagnosis.md:14,15,23`.

**수정 방향.** 축 단위 면제를 **변 단위**로 좁힌다. soft 축이라도 시작 변은 항상 판정하고, 끝 변은
«최대 스크롤에서의 여유»(= 컨테이너 end padding)로 판정한다. 중간 변(스크롤 중간에 놓이는 요소)만
면제 대상이다. 또는 면제 조건에 «해당 축에 `scroll-padding`이 링 확장 이상 있을 것»을 넣는다.

---

### [BLOCKER] 전역 `:focus-visible` 대체 집합이 «보이지도 포커스되지도 않는» 요소를 3px 링 보유자로 판정한다 — 멀쩡한 화면을 red로 만든다

**무엇이 틀렸나.** §2.2 3단계는 전역 규칙(A8 `base.css:88-91` `:focus-visible{box-shadow:var(--focus-ring)}`)에
대해 후보를 `a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"]), [contenteditable]`로
대체한다. 이 집합은 실제 화면에서 **링을 절대 그리지 않는 요소**를 대량으로 포함한다.

실측(합성 픽스처 · `overflow-y:auto` 스크롤러 왼쪽 변 x=68):

| 후보 | 실측 rect | §2.1 여유(좌) | 판정 | 실제 |
|---|---|---|---|---|
| `input[type=hidden]` | `{0,0,0,0}` · `display:none` | **−68px** | 발견 | 박스 자체가 없다 |
| `.sr` 시각 은닉 radio (`position:absolute; width:1px; margin:-1px; clip:rect(0,0,0,0)`) | `{x:67,w:1,h:1}` | **−1px** | 발견 | `clip`으로 아무것도 안 그린다 |
| `input[disabled]` | 정상 rect | — | 후보 | `focus()` 해도 `activeElement` 아님(실측 `false`) |

A8 실물에 그대로 있다:
- `related_person_editor_step.html:30-44` — 한 fragment에 `<input type="hidden" … data-carry>` 선언이 **15개**
  (step 1 렌더 시 12개 · 나머지는 `{% if %}`로 빠진다). 전부 `#rpe-step`의 자손이며 `display:none`이라
  rect가 `{0,0,0,0}`이다 → step 1에서만 **12건 허위 발견**.
- `components.css:624-633` `.choice-pair__input { position:absolute; width:1px; height:1px; margin:-1px; clip:rect(0,0,0,0) }` —
  위 실측의 `.sr`와 같은 형상. `margin:-1px` 때문에 정적 위치보다 1px 바깥에 놓인다.
- `components.css:690-700` `.radio-option__input { position:absolute; width:1px; … clip:rect(0,0,0,0) }` 계열도 같은 시각 은닉 관용구.

또한 §2.2는 **캐스케이드를 보지 않는다**. `components.css:323 .input-field__input:focus-visible{box-shadow:none}`와
`:392 .textarea-field__input:focus-visible{box-shadow:none}`는 전역 링을 **명시적으로 끄는** 규칙인데,
링을 끈 요소가 여전히 3px 링 보유자로 판정된다.

**근거.** 이 세션 실측(위 표) · `/Users/hyun/.herdr/worktrees/spring_dream_server/a8/web/related_persons/related_person_editor/section/related_person_editor_step.html:32-46` ·
`…/web/static/css/components.css:323,392,624-633,690-700` · 설계 §2.2 3단계.

**수정 방향.** 후보에 페인트 가능성 필터를 건다 — rect 폭·높이 ≥ 1, `visibility !== hidden`,
`display !== none`(rect 0으로 대체 가능), `clip`/`clip-path`로 0 영역, `opacity: 0`, `disabled` 제외.
`render_audit.js:39-40`의 기존 `visible()` 술어를 재사용하면 된다. 링 확장은 토큰 하드코딩이 아니라
**그 요소의 실제 적용 규칙**(캐스케이드 승자)에서 얻어야 `box-shadow:none` 억제가 반영된다.

---

### [BLOCKER] §3.1과 §6이 서로를 부정한다 — 판정이 어느 URL에서 도는지 설계에 없다

**무엇이 틀렸나.** 두 진술이 동시에 참일 수 없다.

- §3.1(110-112행): «이번 결함의 컨테이너는 **다이얼로그 안**이라 초기 렌더에 존재하지 않는다 — 렌더 실측은
  초기 페이지에서 돌므로 그 컨테이너를 **영영 못 본다**.» ← 수리 2를 정적 추출로 하는 유일한 근거다.
- §6 브리프(182행): 수리 3 단독 열에 «이번 결함 — **잡는다**».

수리 3은 렌더 실측(`render_audit.js`) 위에 얹힌 브라우저 측 검사다. §3.1이 참이면 수리 3도 그 컨테이너를
못 보고, 따라서 §6의 «잡는다»는 근거가 없다.

확인한 사실: A8에는 오버레이가 아닌 **페이지 모드 경로**가 있다.
`related_person_editor_view.py:3-5`가 «HX-Request 면 `#rpe-step` fragment를, 아니면 full page»를 렌더한다고
적고, `related_person_editor.html:16`이 같은 `#rpe-step` section을 `overlay=False`로 include한다 — 즉 그
URL을 직접 열면 `.rpe-scroll`이 초기 DOM에 있다. 반대로 목록 페이지에서는 `#rp-overlay`가 비어 있고
(`related_persons.css:202` `#rp-overlay:not(:empty) ~ .rp-add`가 «비어 있을 수 있음»을 전제) 컨테이너가 없다.

그러니 «잡는다»는 **렌더 실측을 어느 URL에서 도느냐에 달렸고**, 설계 §2 어디에도 그 의무가 없다. A8
구현 캡처는 11장이고 그중 편집기 페이지 모드가 포함됐는지는 **미확인**이다.

**근거.** 설계 `:110-112` vs `:182` · `/Users/hyun/.herdr/worktrees/spring_dream_server/a8/web/related_persons/related_person_editor/view/related_person_editor_view.py:3-5` ·
`…/view/related_person_editor.html:16` · `…/web/static/css/related_persons.css:202`.

**수정 방향.** §2가 «렌더 실측을 도는 화면 집합»을 명시한다 — 최소한 «시안의 각 화면 상태에 대응하는 URL이
있으면 그 URL에서도 실측»을 의무로 적고, 대응 URL이 없는 상태(오버레이 전용)는 `blind_spots`에 남긴다.
그렇지 않으면 §6의 «수리 3 단독으로 잡는다»를 철회하고 §3.1의 전제와 정합시켜야 한다.

---

### [MAJOR] «첫 토큰이 `inset`이 아닌» 필터가 CSSOM·computed 어느 직렬화에서도 성립하지 않는다

**무엇이 틀렸나.** §2.2 1단계는 «바깥 `box-shadow`(첫 토큰이 `inset`이 아닌)를 선언한 포커스 규칙만 남긴다».
실측한 두 직렬화 어디서도 이 술어가 작동하지 않는다.

CSSOM 규칙 스타일(`rule.style.boxShadow`) — **`var()` 원문이 그대로 나온다**:

```
.ctl:focus-within      → "var(--focus-ring), var(--field-flat)"
.press:focus-visible   → "var(--inset-press)"          ← inset 전용인데 첫 토큰은 var(
.nofx:focus-visible    → "none"                        ← 링 억제인데 첫 토큰은 none
.lit:focus-visible     → "red 0px 0px 0px 3px"         ← 리터럴은 색이 먼저
```

computed 값 — **`inset`이 맨 뒤에 붙는다**:

```
getComputedStyle(el).boxShadow  →  "rgba(31, 28, 24, 0.14) 0px 2px 6px 0px inset"
```

즉 «첫 토큰이 `inset`» 검사는 (a) `var()`로 쓴 inset 전용 그림자를 바깥 그림자로 통과시키고, (b)
`box-shadow: none` 억제 규칙도 통과시키며, (c) 리터럴 그림자에서는 첫 토큰이 색이라 아무것도 걸러내지
못한다. A8은 링 12건이 전부 `var()` 기반이라 (a)(b)가 실물에 해당한다
(`components.css:323,392` = `none`, `--shadow-inset-press` 사용처는 `:active` 규칙들).

**근거.** 이 세션 실측(위 4줄 + computed 1줄) · 설계 §2.2 1단계 · `render_audit.js:186-198`.

**수정 방향.** 판정 대상 요소에서 **computed `box-shadow`를 파싱**하되, `inset` 키워드를 위치 무관하게 찾고
(각 top-level 항목 안 어디든), `none`은 명시적으로 배제한다. 규칙 문자열로 거르지 말고 요소의 캐스케이드
결과를 쓴다(그러면 BLOCKER 4의 억제 규칙 문제도 함께 풀린다).

---

### [MAJOR] 링 확장의 출처가 단일 토큰 `--focus-ring` 하드코딩이다 — 프로젝트에 따라 전부 빗나간다

**무엇이 틀렸나.** §2.3 스키마는 `ring: { token: "--focus-ring", value, extents }` — **링이 하나**라고
가정한다. A8만 봐도 아니다.

- `tokens.css:193` `--focus-ring: 0 0 0 3px rgba(208,114,122,.30)`
- `tokens.css:329` `--settings-focus-ring: 0 0 0 3px color-mix(in srgb,#D0727A 30%,transparent)` —
  `settings.css:423-428`(`a.settings-display-row`·`.home-bottom-nav__button`·`.settings-action-button`)가 쓴다.
  이번엔 우연히 같은 `3px`라 결과가 같지만 **다른 이름**이므로 `--focus-ring`만 읽는 구현은 이 3개 셀렉터의
  확장을 0으로(또는 미상으로) 본다.
- 리터럴 링(`box-shadow: 0 0 0 3px red` 꼴)은 토큰이 없다.
- `--focus-ring`을 안 쓰는 프로젝트에서는 토큰 조회가 빈 문자열이다. 그때 거동이 설계에 없다.

**근거.** `…/a8/web/design_system/foundation/tokens.css:193,329` · `…/web/static/css/settings.css:423-428` ·
설계 §2.3 스키마 · 실측(`getComputedStyle(root).getPropertyValue('--settings-focus-ring')` = 위 값 그대로 반환).

**수정 방향.** extent를 전역 토큰이 아니라 **대상 요소별로** 계산한다(그 요소에 적용되는 그림자 목록의
top-level 항목마다 축별 확장을 구해 최대값). `ring` 블록은 요약(관측된 링 토큰 인벤토리)으로 강등하고
판정에는 쓰지 않는다. 토큰을 못 찾거나 파싱 실패하면 exit 1(미실행) — 조용한 extent 0 금지.

---

### [MAJOR] 그림자 문자열 파싱 규격이 설계에 없다 — 실제 토큰 값이 콤마·비길이 숫자를 품고 있다

**무엇이 틀렸나.** §2.1은 확장을 `blur + spread ∓ offset`이라 적을 뿐, 어떻게 파싱하는지 없다. 실제 값은
순진한 파서를 깬다.

- **top-level 콤마 분리**: `--focus-ring: 0 0 0 3px rgba(208,114,122,.30)` — `rgba()` 안에 콤마 3개.
  `.input-field__control:focus-within`은 `box-shadow: var(--focus-ring), var(--field-flat)` — 항목 구분
  콤마와 함수 내부 콤마가 섞인다. 괄호 깊이 추적 없이 `split(',')`하면 파편이 나온다.
- **비길이 숫자 토큰**: `--settings-focus-ring: 0 0 0 3px color-mix(in srgb,#D0727A 30%,transparent)` —
  «숫자가 있는 토큰»을 모으는 파서는 `30%`(와 `#D0727A`·`srgb`의 숫자)를 길이로 오독할 수 있다.
- **`calc()`**: 커스텀 프로퍼티의 computed 값은 `var()`는 치환하지만 `calc()`·`color-mix()`는 **평가하지
  않고 원문 그대로** 남긴다(실측: `color-mix(in srgb,#D0727A 30%,transparent)`가 문자열로 돌아옴).
  `calc(var(--w) * 1px)`를 spread로 쓴 프로젝트는 파싱 불가다. A8에 그런 그림자 토큰이 있는지는 **미확인**.
- **실패 시 거동 미정**: 설계에 없다. 확장 0으로 떨어지면 모든 검사가 통과 — R1이 금지한 «조용한 green»이
  링 파싱 경로에서 재발한다.

**근거.** 위 토큰 원문(실측 반환값 포함) · 설계 §2.1 43행 · 설계 §5 R1(«조용한 green 금지»).

**수정 방향.** 규칙에 «top-level 콤마는 괄호 깊이 0에서만 분리», «길이 토큰은 `<number>px|rem|em` 형태만
채택», «`calc()`/미지원 단위/파싱 실패는 발견이 아니라 `blind_spots` + 미실행 신호»를 못 박는다.
`node --test` 표본(§2.4)에 위 세 값을 그대로 넣는다.

---

### [MAJOR] `blur + spread`가 CSS 명세의 페인트 범위와 다르다 (2배 과대)

**무엇이 틀렸나.** CSS Backgrounds and Borders 3 §7.1.1: 블러 반경은 그림자 가장자리를 중심으로 «안쪽
절반·바깥쪽 절반»에 걸쳐 전이한다 — 즉 바깥으로 나가는 거리는 `blur/2`이지 `blur`가 아니다.
축별 확장의 옳은 형태는 `spread + blur/2 ∓ offset`이다.

포커스 링(`0 0 0 3px`, blur 0)에는 차이가 없어 이번 케이스의 판정은 안 바뀐다. 문제는 §2.3이
`static_shadows`를 «후일 확대의 훅»으로 남긴다는 점이다. 확대하면 `--shadow-1`(blur 2·10)·
`--shadow-3`(blur 12·50)·`--shadow-accent`(blur 18)에서 2배 과대 판정이 나온다 — `--shadow-3`이면
설계 공식으로 50px, 명세로는 25px다.

Chrome/Skia의 실제 페인트 경계(σ = blur/2 · 대략 3σ)는 명세 값과 또 다르다 — **미확인**.

**근거.** CSS Backgrounds and Borders Level 3 §7.1.1 · `…/a8/web/design_system/foundation/tokens.css:186-190` ·
설계 §2.1 43행 · §2.3 `static_shadows` 주석.

**수정 방향.** 공식을 `spread + blur/2 ∓ offset`으로 고치고, 음수는 0으로 클램프한다(오프셋이 큰 그림자는
반대쪽으로 아예 안 나간다). 그리고 판정 임계에 «blur가 0인 하드 링»과 «블러 그림자»를 구분해 둔다 —
블러 꼬리가 1px 잘리는 것과 하드 링이 3px 잘리는 것은 시각 심각도가 다르다.

---

### [MAJOR] `parentElement` 체인은 `position:absolute/fixed` 자손의 클리핑 조상이 아니다

**무엇이 틀렸나.** CSS 2.1 §11.1.1: `overflow`가 `visible`이 아닌 조상의 클립은 **그 조상이 해당 요소의
containing block 사슬에 있을 때만** 적용된다. 절대 위치 요소는 `position:static`인 중간 조상의
`overflow:hidden`에 잘리지 않는다.

실측:

```html
<div style="position:relative">
  <div id="statichid" style="overflow:hidden;width:100px;height:40px;position:static">
    <div id="abs" style="position:absolute;left:150px;width:40px"></div>
  </div>
</div>
```
```
#statichid rect: left 8 … right 108
#abs        rect: left 158 … right 198     ← 조상 박스 완전히 바깥인데 잘리지 않고 그려진다
```

§2.1대로 `parentElement`를 거슬러 «첫 non-visible 조상»을 잡으면 `#statichid`가 지목되고, 여유는
`158 − 108 = −50px`(음수) → 거대한 허위 발견이 된다. 드롭다운·팝오버·툴팁·`.rp-toast` 같은 오버레이
관용구에서 흔한 형상이다. `position:fixed`는 더하다 — `transform`/`filter`/`will-change`/`contain`이
중간에 없으면 containing block이 뷰포트라 어떤 조상도 안 자른다(같은 조문 · 실측 **미확인**).

A8 이번 케이스(`.input-field__control` → `.rpe-fields` → `.rpe-scroll`)는 전부 정적 흐름이라 우연히 맞다.

**근거.** 이 세션 실측(위) · CSS 2.1 §11.1.1 · 설계 §2.1 44-45행 ·
`…/a8/web/static/css/related_persons.css:189,206,213-214,227`(A8에 `position:absolute` 관용구 다수).

**수정 방향.** 조상 순회에 위치 규칙을 넣는다 — 대상의 computed `position`이 `absolute`면 «positioned
조상(또는 클리핑을 만드는 `contain`/`filter`/`transform` 조상)» 이상만 클리퍼로 인정하고, `fixed`면
containing block을 만드는 조상(`transform`·`filter`·`backdrop-filter`·`will-change`·`contain:paint`)까지만
거슬러 올라간다. 판정 불가한 조합은 `blind_spots`에 남긴다.

---

### [MAJOR] «가장 가까운 클리핑 조상» 하나만 본다 — 바깥 클리퍼·뷰포트·둥근 모서리가 빠진다

**무엇이 틀렸나.** §2.1은 클리퍼를 «첫 조상» 하나로 고정한다. 세 가지가 샌다.

1. **중첩 클리퍼**: 가까운 클리퍼가 4px 패딩을 줘서 여유는 충분한데, 그 클리퍼 자신이 더 바깥 클리퍼에
   딱 붙어 있으면 링은 여전히 잘린다. 클립은 사슬 전체의 교집합이다.
2. **뷰포트**: 클리핑 조상이 하나도 없어도 뷰포트가 자른다. 좌측 변에 붙은 full-bleed 컨트롤의 좌측 링은
   `scrollLeft` 하한 0 때문에 도달 불가다. §2.1의 탐색은 `<html>`에서 끝나고 `html`의 overflow는 보통
   `visible`이므로 «클리퍼 없음»으로 끝난다 → 발견 0.
3. **`border-radius`**: 클립은 **둥근** 패딩 박스를 따른다(CSS Backgrounds 3 §5.3 — overflow는 border box의
   곡률을 따라 padding edge에서 잘린다). A8은 `--radius-pill`·`--radius-field`를 광범위하게 쓴다
   (`components.css:284`·`:830`). 모서리 근처 요소는 직사각 계산이 주는 여유보다 실제 여유가 작다.

**근거.** CSS Overflow 3 §3 · CSS Backgrounds 3 §5.3 · 설계 §2.1 44-45행 ·
`…/a8/web/static/css/components.css:284`(`--radius-pill`)·`:830`(`--radius-field`) · `…/related_persons.css:232-250`(`.rp-dialog__panel`이 패딩을
가진 중간 컨테이너 — 이번엔 클리퍼가 아니지만 중첩 구조는 실재).

**수정 방향.** 조상 사슬의 **모든** 클리퍼를 모아 각 축의 최소 여유를 취한다(+ 뷰포트를 마지막 클리퍼로
추가). 곡률은 1차로는 «클리퍼에 `border-radius`가 있고 대상이 모서리 반경 안에 있으면 `blind_spots`»로
보수 처리해도 된다 — 조용히 통과시키지만 않으면 된다.

---

### [MAJOR] `scrollSize`/`clientSize` 정수 반올림이 hard/soft를 0.2px 차이로 뒤집는다

**무엇이 틀렸나.** `Element.scrollWidth`/`clientWidth`는 **정수로 반올림**된다(CSSOM View — 반환 전 round).
분수 레이아웃(퍼센트·flex·`deviceScaleFactor 2`)에서 두 값의 반올림이 엇갈리면 hardness가 뒤집힌다.

실측:

```
#frac  getBoundingClientRect().width = 200.390625   자식 width = 200.59375
       clientWidth = 200 · scrollWidth = 201        → §2.1 판정: soft(면제)
```

0.2px 차이가 «영영 스크롤로 못 드러내는 축»을 «스크롤 가능»으로 바꿔 검사를 통째로 건너뛴다.
`.rpe-scroll`처럼 flex 자식이 컨테이너 폭을 꽉 채우는 구조는 정확히 이 경계에 산다.

반대 방향(진짜 soft인데 hard로 읽혀 허위 발견)도 같은 원리로 가능하다 — 다만 그때는 여유 계산이
`getBoundingClientRect`(분수)라 판정은 실제에 가깝다.

**근거.** 이 세션 실측(위) · CSSOM View Module Level 1(`scrollWidth`/`clientWidth`는 정수 반환) ·
설계 §2.1 46행.

**수정 방향.** hardness를 크기 비교 대신 computed `overflow`로 판정한다(BLOCKER 2의 수정과 같은 방향).
크기 비교를 남긴다면 ε(≥ 1px)을 두고 «ε 안이면 hard로 본다»를 명시한다 — 보수적으로 검사하는 쪽으로.

---

### [MAJOR] hard/soft가 그때의 데이터 상태에 달려 있다 — «결정적»이라는 주장과 충돌한다

**무엇이 틀렸나.** §2.1의 hardness는 그 순간의 `scrollSize`다. 같은 코드가 픽스처에 따라 다르게 판정된다.

- 목록이 비었거나 짧으면 `scrollHeight == clientHeight` → hard → 세로 링 여유 부족이 **발견**.
- 같은 화면에 행이 몇 개 더 있으면 → soft → **발견 0**.

진단이 §2 마지막에 «결정적이고 화면 수에 비례하지 않는다»고 적은 근거가 여기서 깨진다. A8 관계인 목록은
등록 건수에 따라 스크롤 여부가 바뀌므로 실물에 해당한다. §2.4의 결정론 시험(«2회 byte 동일»)은 같은
픽스처 2회이므로 이 비결정성을 못 잡는다.

**근거.** 설계 §2.1 46-48행 · §2.4 98행 · 진단 `diagnosis.md:57`.

**수정 방향.** BLOCKER 2·MAJOR(반올림)의 수정(= `overflow` 값 기반 hardness)을 적용하면 데이터 의존이
사라진다. 그대로 두려면 «이 검사는 데이터 상태에 따라 발견 수가 달라진다»를 설계에 명시하고 배너 문구에
넣어야 한다.

---

### [MAJOR] 기반 셀렉터 생성이 실제 셀렉터 여럿에서 깨진다 (예외·무성 실패·A8 실물 포함)

**무엇이 틀렸나.** §2.2 2단계 «의사클래스를 떼어 기반 셀렉터». 네 가지가 깨진다.

1. **`:not(:focus)` → `:not()`** — 실측: `document.querySelectorAll('.x:not()')`이 **SyntaxError**를 던진다.
   `try/catch`가 없으면 `render_audit.js`의 `catch(e)`에 잡혀 `partial: true`로 실측 전체가 중단된다.
   A8 CSS에는 현재 `:not(:focus)`가 없다(`:not(:disabled)`·`:not(:empty)`만 · 확인). 시안 dc HTML 쪽은 **미확인**.
2. **`::after` 기반 링** — 실측: `querySelectorAll('.x::after')`는 **던지지 않고 0건**을 돌려준다. 링을
   의사요소 오버레이로 그리는 흔한 패턴이 **무성 거짓음성**이 된다(발견 0 = green). A8은 `::after`로 링을
   그리지 않는다(확인).
3. **스코프된 전역** — `.app :focus-visible`에서 `:focus-visible`만 떼면 `.app `(꼬리 결합자)로 무효 셀렉터다.
   A8에는 `[data-conversation-mount] :is(.standard-button, .round-button):focus-visible`
   (`conversation.css:212` · 확인)가 있어 정확히 이 형상에 인접한다.
4. **`:is()` 내부 콤마** — 위 A8 규칙 2건이 그렇다. `selectorText`를 콤마로 먼저 쪼개는 구현이면
   `[data-conversation-mount] :is(.standard-button` / `.round-button):focus-visible`로 갈라져 둘 다 무효다.
   §2.2는 셀렉터 목록을 어떻게 다루는지 적지 않았다.

**근거.** 이 세션 실측(1·2) · `/Users/hyun/.herdr/worktrees/spring_dream_server/a8/web/static/css/conversation.css:212,896`
(`:is()` 내부 콤마를 가진 focus 규칙 2건 · CSS 전수 스캔으로 확인) · 설계 §2.2 2단계.

**수정 방향.** (a) 모든 `querySelectorAll`을 `try/catch`로 감싸고 실패 셀렉터를 `blind_spots`에 남긴다
(무성 통과 금지). (b) 콤마 분리는 괄호 깊이 0에서만. (c) 의사요소(`::`)가 붙은 셀렉터는 «판정 불가»로
분류해 `blind_spots`. (d) 떼어낸 결과가 빈 compound로 끝나면(꼬리 결합자) 그 자리에 `*`를 넣는다.

---

### [MAJOR] `focusSelectors` 재사용은 손실 채널이다 — 120자 절단·100건 캡·box-shadow 값 미수록

**무엇이 틀렸나.** §2.2는 «v2가 이미 수집하는 CSSOM `focusSelectors`에서 시작»한다. 그 필드는 판정용이
아니라 인벤토리용이라 세 가지를 잃는다.

- **120자 절단**: `render_audit.js:188` `const sel = rule.selectorText.slice(0, 120);`. 잘린 셀렉터는
  대개 무효 셀렉터가 되어 예외 또는 0건이다. A8 최장 focus `selectorText`는
  `a.settings-display-row:focus-visible, .home-bottom-nav__button:focus-visible, .settings-action-button:focus-visible`
  = **115자**(확인). 여유 5자 — 클래스 이름 하나만 길어져도 잘린다.
- **100건 캡**: `render_audit.js:26-27` `MOTION_CAPS.focusSelectors = 100`. 초과분은 `caps_hit`에만 남고
  버려진다. A8 focus 규칙은 15건(확인)이라 여유가 있지만, 캡이 걸린 프로젝트에서는 후보 집합이 조용히
  불완전해진다. §5 R2는 «전역 대체 집합»의 `CANDIDATE_CAP`만 다루고 이 상류 캡은 언급하지 않는다.
- **값 미수록**: `focusSelectors`는 **셀렉터 문자열만** 담는다(`render_audit.js:197`). §2.2 1단계가
  요구하는 box-shadow 값이 거기 없다 — «이미 수집하는»이라는 서술이 성립하지 않는다.

**근거.** `/Users/hyun/Desktop/dddjango/dddjango-web/assets/render_audit.js:26-27,188,197` ·
A8 CSS 전수 스캔(focus 규칙 15건 · 최장 selectorText 115자) · 설계 §2.2 59행 · §5 R2.

**수정 방향.** clip 판정용 수집을 별도 채널로 만든다 — 절단 없는 `selectorText`, 캡은 별도 상수, box-shadow
원문 동반. 캡·절단이 걸리면 `caps_hit`/`blind_spots`에 남기고 배너에 «후보 집합 불완전»을 표기한다.

---

### [MINOR] 포커스를 주지 않아 생기는 기하 오차 — `:focus-within`이 클리퍼 자신의 패딩 박스를 움직일 수 있다

**무엇이 틀렸나.** §2.1은 «포커스를 실제로 주지 않는다»고 정하고 여유를 비포커스 기하로 잰다. `:focus-within`은
**조상에도** 매치되므로, 클리핑 조상이 `:focus-within`에서 `border-width`나 `padding`을 바꾸면 판정에 쓰는
패딩 박스가 실제와 다르다. 실측으로 확인한 것: `border-width: 1px→3px` + `padding: 4px→2px`를 `:focus-within`에
건 요소의 **border box는 불변**(110×31)이었다 — 즉 두 선언 모두 적용되고 **패딩 박스만 안쪽으로 2px 이동**한다
(패딩 박스 좌표는 이 실측에서 직접 재지 않았다 — border box 불변 + 적용된 border-width로부터 유도).

A8은 `.input-field__control:focus-within`이 `border-color`만 바꾸고 두께는 그대로라 이번엔 오차가 없다
(`components.css:292-296` 확인). 규칙으로서의 구멍이다.

**근거.** 이 세션 실측 · `…/a8/web/static/css/components.css:292-296` · 설계 §2.1 53-55행.

**수정 방향.** `:focus-within`/`:focus` 규칙이 `border-width`·`padding`·`transform`·`zoom`을 건드리는 경우를
CSSOM에서 미리 탐지해 해당 대상은 `blind_spots`로 돌린다(포커스를 주지 않는다는 계약은 유지).

---

### [MINOR] `overflow-clip-margin`이 클립 가장자리를 패딩 박스 밖으로 밀어낸다

**무엇이 틀렸나.** §2.1은 클립 가장자리를 «패딩 박스»로 고정한다. `overflow: clip`은 `overflow-clip-margin`
만큼 바깥으로 클립 영역을 넓힌다(CSS Overflow 3 §3.3 — overflow clip edge). 실측에서
`getComputedStyle(el).overflowClipMargin`이 `"8px"`로 읽힌다. 8px 여유가 있는데 3px 링을 결함으로
판정하는 거짓양성이 된다. A8에는 `overflow-clip-margin` 사용처가 없다(전수 grep 확인).

**근거.** 이 세션 실측 · CSS Overflow 3 §3.3 · 설계 §2.1 44-45행.

**수정 방향.** 클리퍼가 `overflow*: clip`이면 클립 가장자리를 `패딩 박스 + overflow-clip-margin`으로 계산한다.

---

### [MINOR] `outline` 기반 링은 판정 대상이 아니다

**무엇이 틀렸나.** §2는 `box-shadow`만 본다. `outline`(그리고 `outline-offset`)도 border box 바깥에 그려지고
**동일하게 클리핑된다**. A8은 `base.css:88-91`이 `outline: none`으로 끄고 box-shadow로 대체했지만, 이 검사는
플러그인 전역 규범이 되므로 outline을 쓰는 프로젝트에서는 링 절단을 전혀 못 잡는다(발견 0 = green).
UA 기본 focus ring도 마찬가지다.

**근거.** `…/a8/web/static/css/base.css:88-91` · CSS UI 4(outline은 border edge 바깥에 그려짐) · 설계 §2.

**수정 방향.** 확장 계산에 `outline-width + outline-offset`을 같은 축 확장으로 더한다(둘 다 computed로
읽을 수 있다). 범위 밖으로 남긴다면 §5의 «미착수로 남기는 것»에 명시한다.

---

### [MINOR] §2.2 4단계 «`:focus-within` 규칙은 컨테이너가 링을 진다»는 주어를 잘못 지목할 수 있다

**무엇이 틀렸나.** 링을 지는 것은 «`:focus-within`이 붙은 요소»가 아니라 **규칙의 주어(subject)**다.
`.ctl:focus-within .child { box-shadow: … }`에서 링은 `.child`가 진다. §2.2의 서술을 문자 그대로 구현하면
`.ctl`을 재게 된다. A8에 후손 조합자 focus 규칙이 실재한다 —
`components.css:298 .input-field__control:focus-within .input-field__icon`(다만 `color`만 바꾸고 box-shadow는
없어서 이번엔 무해 · 확인).

**근거.** `…/a8/web/static/css/components.css:298` · Selectors 4(subject = 마지막 compound) · 설계 §2.2 66행.

**수정 방향.** «의사클래스를 뗀 셀렉터 전체를 `querySelectorAll`한 결과가 대상»으로 통일해 적는다
(그러면 `:focus-within` 특례 문장이 필요 없다).

---

### [MINOR] 스크롤바가 있는 클리퍼에서 패딩 박스 ≠ 실제 클립 박스

**무엇이 틀렸나.** 클래식 스크롤바(gutter를 차지하는 스크롤바)가 있으면 스크롤바가 덮는 띠만큼 시각적으로
가려진다. §2.1은 패딩 박스 전체를 가용 영역으로 본다. A8은 `base.css:93-96` `::-webkit-scrollbar{width:0;height:0}`
으로 0폭이라 현재는 무해하다(확인). 데스크톱 기본 스크롤바를 쓰는 프로젝트·`scrollbar-gutter: stable`에서는
어긋난다.

**근거.** `…/a8/web/static/css/base.css:93-96` · CSS Overflow 3(scrollbar gutter) · 설계 §2.1 44-45행.

**수정 방향.** 끝 변 여유를 `clientWidth`/`clientHeight` 기준(스크롤바 제외)으로 재거나, 스크롤바 폭이 0이
아니면 `blind_spots`에 남긴다.

---

## 요약

| 등급 | 개수 |
|---|---|
| BLOCKER | 5 |
| MAJOR | 10 |
| MINOR | 5 |

이 규칙대로 구현하면 §2가 잡는 것은 «`:focus*` 셀렉터로 선언되고, 클리퍼가 정적 흐름 조상이고, 해당 축에
콘텐츠 오버플로가 전혀 없는» 링뿐이다. 진단이 지목한 4개 요소 중 `:checked` 링 1개는 원리상 빠지고,
시안이 하단에 `4px`를 준 이유(끝 변 절단)는 축 전체가 면제돼 영영 안 잡힌다. 반대로 전역 `:focus-visible`
대체 집합은 `display:none` hidden input 12개(A8 실물 · step 1)를 음수 여유로 red 처리한다.
