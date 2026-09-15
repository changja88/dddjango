# 독립 계획 리뷰 2 — 검사기 판정 계약 (2026-09-15)

대상: `workspace/plan/2026-09-15-web-clip-fidelity-plan.md` T1(`check_token_disposition.py`)·T2(`check_clip_clearance.py`).
축: 두 계약이 **오탐·미탐을 내는 구체적 입력**만. T3·T4·순서 게이트는 다른 리뷰어 소관.

**재현 환경.** 프로토타입 2종을 계획 문면 그대로 구현해 A8 실물에 돌렸다 —
`/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/5d88d7d2-4bb6-412e-83fa-56580ac7b33b/scratchpad/pr2/{proto_t1.py,proto_t2.py,proto_t2b.py}`.
입력은 읽기 전용 A8(`/Users/hyun/.herdr/worktrees/spring_dream_server/a8/`) — **원본 무수정**(T2 B-3 재현만 scratchpad 사본에서).
브라우저 실측 1건은 실제 Chrome(Playwright)로 직접 측정했다. 아래 «측정»은 전부 이 세션에서 돌린 값이다.

---

## T1 — `check_token_disposition.py`

### [BLOCKER] A8 «발견 6건» 중 실제 결함은 1건 — 나머지 5건은 값 우연 일치·화면 밖·캔버스 크롬이다

**오탐을 내는 입력.** 계획의 6건을 내 프로토타입이 **정확히 재현**했다(아래 명령·출력). 그 6건을 실물로 하나씩 되짚으면:

| 발견 | 값 | 시안에서 걸린 자리 | 판정 |
|---|---|---|---|
| `--space-1` | 2px | `관계인.dc.html:108` `padding: 2px 2px 4px` · `:74` `padding: 2px 4px 0` | **진짜 결함** ✓ |
| `--radius-sm` | 12px | `gap: 12px` · `padding: 96px 12px 0` · `padding: 0 0 12px` | **오탐** — radius 토큰이 gap/padding 값에 걸렸다. 12px는 **채택** `--space-5`·`--stack`과 같은 값 |
| `--radius-xs` | 8px | `padding: 8px 0` · `padding: 8px var(--gutter) calc(…)` | **오탐** — 8px는 **채택** `--inline`·`--space-4`·`--stack-tight`와 같은 값 |
| `--radius-xl` | 28px | `설정.dc.html` `calc(var(--tabbar-h) + 28px)` | **오탐** — 이번 화면(관계인)이 아니고, 용도도 radius 아님 |
| `--space-10` | 40px | `관계인.dc.html:36` `padding: 40px`(최외곽 캔버스 래퍼 · 390×844 프레임 **바깥**) | **오탐** — A8 명세 §8이 캔버스 크롬을 «호스트 프레임 소유 · 재현 안 함»으로 이미 기각한 영역 |
| `--space-13` | 80px | `calc(var(--safe-bottom) * .4 + 80px)` | 약한 발견 — calc 피연산자. 판단 불가로 남겨야 할 부류 |

즉 **6건 중 4건 확정 오탐 · 1건 판단 불가 · 1건 진짜**. 계획은 이 6건을 «판단 자료가 아니라 **반송 근거**»로 못박았으므로,
계약대로면 architect 는 멀쩡한 기각 4건에 대해 다시 답해야 한다.

**근거(측정).**

```
$ python3 …/scratchpad/pr2/proto_t1.py           # 계획 T1c 문면 그대로
풀 = 230  (colors 106 · typography 50 · spacing 36 · borderRadius 14 · shadows 24)
T1c 발견 6건: --radius-sm(12px) --radius-xl(28px) --radius-xs(8px) --space-1(2px) --space-10(40px) --space-13(80px)
```

값 귀속이 원리상 불가능한 규모를 셌다 — A8 풀에서 **채택 토큰과 기각 토큰이 같은 값을 공유하는 경우가 11건**:

```
채택·기각이 같은 px 를 공유: 6 → ['8px','12px','16px','22px','34px','44px']
채택·기각이 같은 #hex 를 공유: 5 → ['#4f8a6c','#8c2d27','#a29a8e','#b95a64','#f6f1e8']
   예) #b95a64: --accent-hover(채택) · --blossom-600(채택) · --text-accent(기각) · --text-link(기각)
   예) 8px → --inline(채택) · --space-4(채택) · --stack-tight(채택) · --radius-xs(기각)
```

이 11개 값이 시안에 한 번이라도 나오면 «기각 토큰이 쓰였다»는 결론은 **논리적으로 도출 불가**다 — 채택 쌍둥이가 쓴 것과 구별할 수단이 없다.

**수정 방향.** 세 가지를 같이 넣어야 이번 결함 1건만 남는다.
1. **동값 채택 토큰 소거** — 같은 값을 가진 채택 토큰이 하나라도 있으면 발견이 아니라 «귀속 불가» 인벤토리 줄. (측정: 이 필터만으로 `--radius-sm`·`--radius-xs` 2건이 빠진다.)
2. **축별 CSS 속성 제한** — `borderRadius` 는 `border-radius`/`border-*-radius` 선언 안에서만, `spacing` 은 `padding|margin|gap|inset|top|right|bottom|left|width|height` 안에서만, `typography` 의 px 는 `font-size`/`font` 안에서만 대조. (`--radius-xl` 도 여기서 빠진다.)
3. **시안 본문 스코프** — `source-manifest.json` 의 `entrypoint`(A8 = `관계인.dc.html`)로 한정. 측정: 전 html 52개 style 속성 → entrypoint 36개, 발견 6 → 5.

---

### [BLOCKER] 헤더 미검출 → `[warn]` + exit 0 이 **무조건** 탈출구다 — 선례인 `check_motion_spec` 에는 있는 대칭 가드가 없다

**미탐을 내는 입력.** 고정 헤더 `| 축 | 처분 | 토큰 |` 를 쓰지 않은 명세 전부. **A8 실명세가 정확히 그 상태다**
(`design-spec.md:454-481` 은 `- 채택(38): …` / `- 기각(68): …` 산문). 계획 자신이 §5 B-1에서 «판형이 A8 산문이라 헤더 미검출 →
`[warn]` 경로가 먼저 걸리므로 변환한 표본으로 돌린다»고 적는다. 즉 **A8 원본을 그대로 넣으면 이 결함은 exit 0 · 발견 0**이다.

**근거.** 선례 `check_motion_spec.py:29-31`(docstring)은 같은 판형에 **대칭 가드**를 둔다:

> 헤더 미검출(레거시 산문 판형)은 [warn]+exit 0 (합법 재빌드 비차단) — **단 notes가 표 판형이고 모션 행이 있는데 spec에 표가 없으면 그것은 전수 처분 누락(FINDING)이다.**

T1 에는 그 «단 …» 절이 없다. 그런데 T1 은 대조쌍이 더 강하다 — `design-tokens.json` 은 **항상 존재하고 토큰이 0이면 `extract_design.py` 가 이미 exit 1** 로 죽는다(`extract_design.py:26-27`). 즉 «토큰 N>0 인데 처분 표 0» 은 무조건 전수 처분 누락이다.

**수정 방향.** `design-tokens.json` 파스 성공 + dict 절 키 ≥1 + 처분 표 미검출 → **FINDING(exit 2)**. 산문 명세 호환이 필요하면 유예 기간을 배너에 명시하되, 조용한 exit 0 은 금지.

---

### [MAJOR] 실측 기대값 «기각 134 · 대조 가능 57 · 미대조 77» 이 leaky 파스의 산물이라 재현 불가 — B-1 합격 기준이 서지 않는다

**입력.** A8 명세 자신이 선언한 수는 **기각 132**(68+28+15+6+15) · **풀 229**(spacing 35)다(`design-spec.md:454`·`:481`).
JSON 실제 풀은 **230**(spacing 36). 계획은 «풀 230 · 기각 134».

**근거(측정).** 백틱 정규식으로 산문을 파스하면 사유 문장의 백틱이 새어 들어온다:

```
기각(68) 파스 69개     ← 사유 «`--track-off`는 진행바 …» 가 다시 잡힘
기각(28) 파스 32개     ← 사유 «(`--fw-semibold`/`--fw-regular`는 채택 …)» 등
채택 97 · 기각 134 · 합 231 ← 계획의 134 와 정확히 일치
T1b 중복(채택∩기각): 2 ['--fw-regular','--fw-semibold']   ← 순수 파서 인공물이 «발견»으로
T1a 미처분: 1 ['--safe-top']                               ← 이건 진짜(A8 spacing 35 vs JSON 36)
```

커버리지 수치도 마찬가지다 — `typography` 값이 `{"size": "16px"}` **dict** 라 언랩 여부가 갈랐다:

```
언랩X: 기각 134 · 대조가능 57 · 미대조 77   ← 계획 수치와 정확히 일치
언랩O: 기각 134 · 대조가능 69 · 미대조 65
```

즉 계획의 기대값은 «표 변환 시 사유 백틱을 포함하고, typography dict 를 언랩하지 않는다»는 **미명시 구현**에 고정돼 있다.
B-1 이 무엇을 재현해야 성공인지 결정되지 않는다. 그리고 계획이 세지 않은 발견 2종(`--safe-top` 미처분 · 중복 2)이 실제로는 더 나온다.

**수정 방향.** 표 변환 규칙을 계획에 못박는다 — 토큰 셀은 «백틱 인용 목록 전용, 사유는 별도 칼럼». 그리고 A8 기대값은 «T1a 1 · T1b 0 · T1c N» 처럼 검사별로 쪼개 적는다.

---

### [MAJOR] `typography` 절 50개가 전부 조용히 미대조 — 색 토큰이 여기 산다

**입력.** `design-tokens.json` 의 `typography` 값은 `{"size": …}` 중첩 dict 다(`extract_design.py:47` `typography: Dict[str, Dict[str,str]]`).
계획의 값 정규식(`^-?[\d.]+px$` · `^#[0-9a-fA-F]{3,8}$`)은 dict 를 문자열화한 값에 절대 안 맞는다 → **복합 값 미대조** 로 계수된다.
A8 기각 typography 28개 전부가 여기로 빠지고, 그 안에는 **색 토큰**이 있다:

```
--text-info    = {'size': '#48586A'}   (소속: typography)
--text-danger  = {'size': '#A93A32'}
--fs-label     = {'size': '14px'}
```

즉 «색 대조»라고 적은 규칙이 실제 색 토큰의 절반을 못 본다. 축 칼럼을 이름으로 판단하면 더 틀린다 — `--text-*` 는 이름이 색인데 JSON 절은 typography 다.

**수정 방향.** dict 값은 `size` 를 꺼내 대조하고, 축은 **이름이 아니라 JSON 절**을 정본으로 삼는다.

---

### [MAJOR] 색 대조가 `#hex` 한정 — A8 색 값의 43%가 대조 밖(`color-mix()`·`rgb()`가 실재한다)

**근거(측정 · colors 106 + typography 50 = 156):**

```
#hex 66 · color-mix() 39 · 기타 22 · px 10 · number 9 · rgb()/rgba() 6 · gradient 4
   예) --blob-blossom = color-mix(in srgb,#DF9095 38%,transparent)
   예) --glass-rim    = rgba(255,255,255,.72)
   예) --focus-ring   = 0 0 0 3px color-mix(in srgb,#D0727A 30%,transparent)   ← «기타»
```

`#hex` 아닌 115−66 = **49개**(31%)가 무조건 미대조, dict 미언랩까지 겹치면 색 축 커버리지는 더 떨어진다.

**수정 방향.** ① `#RGB`→`#RRGGBB` 정규화, 8자리는 alpha 절단 후 비교. ② `rgb()/rgba()` → hex 환산(선례: `compare_render_audit.py:52` `RGB_RE` + `#rrggbbaa` 정규화 — 그대로 쓸 수 있다). ③ `color-mix(in srgb,#X N%,…)` 는 **기저 hex 만** 뽑아 대조하되 «근사» 표시.

---

### [MAJOR] `var(--토큰)` 절이 계약에 있는데 기대값 6건에 반영돼 있지 않다 — 구현하면 A8에서 3건이 더 뜨고 전부 오탐이다

**입력.** 계약 «`var(--토큰)` 직접 인용도 사용으로 본다». 이 절을 구현하면:

```
var() 인용 기각 토큰: 3 → ['--info', '--tabbar-h', '--text-info']
   var(--info)      ← 설정.dc.html  "font-size: 18px; color: var(--info);"
   var(--tabbar-h)  ← 설정.dc.html  "padding: 12px var(--gutter) calc(var(--tabbar-h) + 28px);"
   var(--text-info) ← 설정.dc.html  "font: var(--type-caption); … color: var(--text-info);"
```

3건 모두 **설정 화면**(이번 빌드 범위 밖)에서 나왔다. 계획의 기대값 6건에는 이 3건이 없다 → 계약과 기대값이 서로를 부정한다.
게다가 `--tabbar-h` 의 A8 기각 사유는 «프레임 치수 — app_shell/재사용 컴포넌트 소유»로 **참**이다(아래 사유 항목 참조).

**수정 방향.** entrypoint 스코프를 먼저 넣고, 그 위에서 var() 절을 살릴지 계획이 명시적으로 결정한다(둘 중 하나는 지워야 한다).

---

### [MAJOR] 기각 «사유»가 표 판형에 없어 T1c 술어가 소유권 기각에 오작동한다

**입력.** A8 spacing 기각 사유는 **한 문장이 15개 토큰을 덮고 근거가 2종**이다(`design-spec.md:468`):

> `--app-content-max`,…,`--space-13` — 프레임 치수(app-*·appbar-h·tabbar-h는 app_shell/재사용 컴포넌트 소유)·미사용 space 단계.

앞 8개는 «다른 소유자» 기각(값이 시안에 있어도 **정당**), 뒤 7개만 «미사용» 기각(T1c 로 검증 가능).
계획의 술어 «기각한 토큰의 값이 동결 시안에 실제로 쓰이면 발견»은 둘을 구분하지 못한다. 계획 자신이 T3에서
`agents/design-architect-web.md:48` 에 «**«미사용»을 쓰려면** 그 값이 동결 시안에 없어야 한다»고 적어 구분의 필요를 인정하는데,
검사기 표 판형에는 그 구분을 담을 칸이 없다.

**수정 방향.** 표를 `| 축 | 처분 | 사유유형 | 토큰 |` 로 하고 `사유유형 ∈ 미사용|타소유|중복|대체`. T1c 는 `미사용` 행에만 발동.
`check_motion_spec` 의 `DISPOSITIONS`·`KINDS` 화이트리스트가 그대로 선례다.

---

### [MAJOR] 시안 본문 정의가 플러그인 자기 추출기보다 좁다 — 컴포넌트 인스턴스 21개가 통째로 안 보인다

**입력.** 계획: «시안 본문 = `design-ref/**/*.html` 의 인라인 `style="…"` 선언 전체».
그런데 풀을 만든 `extract_design.py:13` 은 «**인라인 style·`<style>` 블록**·tailwind config»에서 값을 모은다 — 풀과 사용 본문이 비대칭이다.

A8 실물이 더 나쁘다. `관계인.dc.html` 의 화면 본체는 **`x-import` 컴포넌트 인스턴스 21개**로 구성되고, 그 스타일은
`design-ref/_ds/chunmong-…/_ds_bundle.js`(**115,341 바이트**)에 있다. T1c 가 보는 것은 래퍼 div 의 `style` 속성 36개뿐이다.
`2px` 가 잡힌 것은 그것이 우연히 래퍼 div 에 있었기 때문이다.

계획이 던진 시나리오들에 대한 실물 답:

- **`padding: 2px` 대신 컴포넌트 속성** — 이미 실재한다: `관계인.dc.html:61` `<x-import … padding="4px 12px" …>`. `style=` 이 아니라 prop.
- **`<style>` 블록** — `관계인.dc.html` 의 `<style>`(570자)가 바로 이 결함의 **원본 선언**을 담는다:
  `[data-cm-dialog-scroll="true"] { flex:1 1 auto; min-height:0; overflow-y:auto }`. 구현 `.rpe-scroll` 은 그 속성을 그대로 달고 있다.
- **JS 스타일 객체** — `관계인.dc.html` 인라인 `<script>`: `checkboxRow.style = { minHeight: 44, padding: '0 2px' }` · `deleteBtn.style = { marginRight: -6 }`. **단위 없는 숫자**(44 → 44px).
- **Tailwind 임의값 `p-[2px]`** — `extract_design.py:17` 이 이미 `arbitraryValues` 로 모은다. 그런데 **계획의 T1a 풀이 그 절을 제외**한다(dict 절 5종만). 즉 임의값은 영영 미처분·미검사다. A8은 `arbitraryValues: []` 라 오늘은 0건.

**수정 방향(함정 포함).** 본문을 «인라인 style + `<style>` 블록»까지 넓혀 추출기와 대칭을 맞춘다. 단 **속성 전수 스캔으로 넓히면 안 된다** —
`hint-size="390px,844px"` · `"100%,52px"` 가 `--app-width`·`--app-height`·`--appbar-h`(전부 정당한 소유권 기각)를 오탐으로 만든다.
`arbitraryValues` 는 풀에 넣어 전수 처분 대상으로 올린다.

---

### [MINOR] 비변별 값 목록은 «넓/좁»이 아니라 **잘못된 축**을 막고 있다

**근거(측정).** A8 기각 134개 중 목록(`0·0px·none·auto·transparent·inherit·initial·1·100%`)에 걸리는 값은 `--shadow-0: none` **1개**뿐이고,
계획이 이유로 든 `--space-0: 0px` 은 **애초에 시안 인라인 style 에 `margin: 0` 이 없다**(A8 시안의 0은 `padding: 0`·`padding: 0 4px` 형태). 목록은 A8에서 사실상 무효다.
실제 폭발원은 위에서 센 **동값 토큰 11건**이다. 목록을 손대는 것보다 동값 소거가 효과가 크다. 목록 자체는 유지해도 무해.

### [MINOR] `rem`→px ×16 과 `em` 환산

- A8 은 `base.css:32-34` `html { -webkit-text-size-adjust: 100% }` 뿐 — `font-size` 선언이 없어 UA 16px. **이번엔 무해**.
- `html{font-size:62.5%}`(10px) 관용구 프로젝트에서는 60% 빗나간다.
- `em` 은 **요소 자신의 font-size** 기준이라 루트 16 환산은 원리상 틀리다(중첩 요소에서 항상 오차).
- 수정: 시안의 `html`/`:root` `font-size` 를 읽어 쓰고 없으면 16 + `[warn]`. `em` 은 환산하지 말고 미대조 계수.

### [MINOR] 표 파서 — 이스케이프 파이프·백틱·축 오타·중복 축

- **이스케이프 파이프**: 토큰명·축·처분에 `|` 가 나올 수 없어 이번 판형엔 무해. `check_motion_spec.split_row`(`ESC_PIPE` placeholder) 이식이면 공짜로 해결되므로 굳이 빼지 말 것.
- **백틱 없는 토큰명**: 위 «기각 134» 항목의 반대면. 백틱 정규식이면 백틱 없는 토큰은 **조용히 증발**하고, 전수성 검사가 «미처분»으로 잡아 준다 — 다만 발화 문면이 원인(백틱 누락)을 가리키지 않는다. 토큰 셀 안에서 «`--` 로 시작하는 백틱 밖 단어» 를 판형 위반 FINDING 으로.
- **축 이름 오타**(`shadow` vs `shadows`): 그 행 전체가 증발하고 전수성만 red. `check_motion_spec` 의 `KINDS` 화이트리스트 검증 선례를 그대로 — 축 값 위반은 FINDING.
- **같은 토큰이 두 축에 등장**: T1a/T1b 가 set union 이라 **축 칼럼이 판정에 전혀 쓰이지 않는다**. 축을 판정에 쓰려면(위 오탐 수정 ②) JSON 절과 대조해 «선언 축 ≠ JSON 절» 을 FINDING 으로.
- **자기 계수 칼럼 부재**: A8 산문은 `채택(38)`/`기각(68)` 로 자기 계수를 남기는데 `| 축 | 처분 | 토큰 |` 에는 그 자리가 없다. 셀에서 토큰이 조용히 빠지면 전수성으로만 잡힌다.

---

## T2 — `check_clip_clearance.py`

### [BLOCKER] 1단계 «축별 최대 확장»을 전역으로 잡으면 장식 그림자가 임계를 지배한다 — S = [5,5,3,8]px, **시안이 준 값도 계획의 B-3 양성 대조도 통과하지 못한다**

**오탐을 내는 입력.** A8 링 규칙 12건 중 11건은 `0 0 0 3px`(확장 3px)인데, 12번째가 이것이다:

```css
/* components.css:793-797 */
.checkbox__input:checked + .checkbox__box { … box-shadow: var(--shadow-1); }
/* tokens.css:186  --shadow-1: 0 1px 2px rgba(31,28,24,.06), 0 3px 10px rgba(31,28,24,.06); */
```

계획 공식(`spread + blur/2`)으로 이 한 건의 확장은 L5 · R5 · T2 · B8 이다. 전역 최대를 취하면:

```
1단계 링 규칙 12건 · 전역 최대 확장 S(L,R,T,B) = [5.0, 5.0, 3.0, 8.0]
```

이건 포커스 링이 아니라 **체크된 체크박스의 고도 그림자**다(rv-A BLOCKER 1이 «바깥 그림자를 선언하는 상태 규칙»으로 축을 넓히라 한 결과가 여기서 역풍이 됐다).
그 한 토큰이 클리핑 규칙 34건 전부의 임계를 3px → 8px 로 올린다.

**결정적 귀결 — 계획의 B-3 양성 대조가 통과할 수 없다.** A8 사본에 계획이 적은 그대로 패치해 돌렸다:

```
$ # scratchpad 사본에 .rpe-scroll { … padding: 3px 3px 4px; } 추가 (계획 §5 B-3)
$ python3 proto_t2.py …/a8copy/web
1단계 링 규칙 12건 · 전역 최대 확장 S(L,R,T,B) = [5.0, 5.0, 3.0, 8.0]
3단계 여유 부족 후보 30건
   related_persons.css :: .rpe-scroll  axes=['y'] pad=[3.0, 3.0, 3.0, 4.0] 부족=['bottom']   ← 4 < 8
```

B-3 은 «발견 0» 을 기대하는데 **발견이 남는다**. 시안 원본 값 `padding: 2px 2px 4px` 는 더 나쁘다(2<5 · 2<3 · 4<8).
즉 이 계약대로 만들면 **동결 시안을 정확히 구현한 코드를 반송한다**. 그리고 계획의 CC6 픽스처(«`0 0 0 3px` → 좌·우 모두 3px»)는
전역 최대가 실제 임계인 이상 판정에 쓰이지 않는 수치를 고정한다.

**수정 방향.** 확장을 **전역 최대가 아니라 대상별**로 잡는다 — 4단계에서 찾은 «그 서브트리에 실제로 있는 링 규칙»의 확장만 쓴다.
최소한 링을 `blur == 0 && spread > 0`(하드 링)으로 한정하고 블러 그림자는 별도 등급·별도 임계로 분리한다.

---

### [BLOCKER] 3단계 축 판정이 `overflow-y:auto` 의 **가로축 전파**를 놓쳐 이번 결함의 절반을 못 본다 — 잘린 상태를 green 으로 승인한다

**미탐을 내는 입력.** `.rpe-scroll { overflow-y: auto }`(`related_persons.css:393-400`) — 계획의 2단계는 `axes={'y'}` 로 읽고 3단계는 T/B 만 본다.
그런데 CSS Overflow 3 §3: **한 축이 `visible` 이고 다른 축이 아니면 `visible` 은 `auto` 로 계산된다.**

**실측(실제 Chrome · Playwright · 직접 측정).** `overflow-y:auto` 만 준 200px 스크롤러 + `padding: 3px 0 4px`:

```
specified: overflow-y:auto only
computed_overflowX: "auto"     computed_overflowY: "auto"
scroller_left 0 / right 200 · input_left 0 / right 200
left_clearance: 0     right_clearance: 0        ← 3px 링은 좌·우 영구 절단
```

시안이 준 값이 `padding: 2px **2px** 4px` 인 이유가 바로 이 가로 전파다. 계획의 검사기는 그 가로 2px 의 근거를 원리상 못 본다.

**귀결.** 계획의 B-3 를 `padding: 3px 0 4px`(가로 0) 로 바꿔도 3단계는 **똑같이 y축만 본다** — 링이 좌우로 잘리는 상태가 «발견 0»으로 통과한다.
이 검사기의 존재 이유인 결함의 절반을 구조적으로 승인하는 경로다.

**수정 방향.** `overflow`/`overflow-x`/`overflow-y` 중 하나라도 `auto|scroll|hidden|clip` 이면 **두 축 모두** 클리핑으로 본다
(`visible→auto` · `clip 상대는 hidden` 전파). 픽스처에 «`overflow-y:auto` + 가로 패딩 0 + 서브트리 input → exit 2» 를 추가한다.

---

### [MAJOR] 4단계 발견 6건 중 2건이 오탐 — 설계자가 **이미 여유를 준** 컨테이너를 반송한다

**측정.** 내 프로토타입이 계획 4단계를 구현해 돌린 결과:

```
4단계 → 발견 6 · 인벤토리 24
  related_persons.css :: .rpe-scroll        ← 목표 ✓ (서브트리 a·button·input·select·textarea)
  user_info.css       :: .user_info__sheet-body
  home.css            :: .home-bottom-nav
  chart.css           :: .chart-major-fortunes__strip      ← 오탐
  conversation.css    :: .conversation-rooms               ← 오탐(1px)
  conversation.css    :: .conversation-candidate
```

- **`.chart-major-fortunes__strip`**(`chart.css:1137`) — `overflow-x:auto` + **`padding: 2px 0 10px`**. 계획은 L/R 부족으로 발견.
  그런데 바로 다음 규칙이 `.chart-major-fortunes__labels { position: sticky; left: 0 }` 이고, 파일 주석이
  «스트립(overflow-x auto)이 의도된 가로 스크롤포트라 left 앵커 성립» 이라 적는다 — **좌우 패딩을 넣으면 sticky 좌열이 어긋난다.**
  세로 2/10 은 설계자가 이미 그림자 여유로 준 값이다. 검사기는 «여유를 고려한 설계»와 «누락»을 구분하지 못한다.
- **`.conversation-rooms`**(`conversation.css:1194-1201`) — `padding: var(--chat-rooms-padding)` = **`2px 0 14px`**(`tokens.css:600`).
  부족은 **top 만, 2px vs 3px = 1px**. 허용치(ε)가 계약에 없다.

덧붙여 `.conversation-candidate`(`:1072`)·`.home-bottom-nav`(`home.css:54`)는 `border-radius`(panel/pill) **마스크**용 `overflow:hidden` 이라
«패딩을 늘려라» 가 성립하지 않는 형상이다 — 발견 자체는 실물일 수 있으나 검사기가 제시할 수리 방향이 없다.

**수정 방향.** ① ε ≥ 1px 명시. ② «해당 축에 이미 링 확장 이상 패딩이 있는 컨테이너»는 다른 축이 부족해도 등급을 낮춘다(설계 고려 흔적). ③ `position:sticky` 자손을 가진 스크롤포트는 `blind_spots`.

---

### [MAJOR] 4단계 템플릿 조인이 **앱 전역 스크롤러**를 구조적으로 못 본다 — `{% extends %}`/`{% block %}` 은 include 가 아니다

**미탐을 내는 입력.**

```html
<!-- base/base.html:22 -->
<main class="app-frame__content">{% block content %}{% endblock content %}</main>
```
```css
/* app_shell.css:44-48 */
.app-frame__content { flex: 1 1 auto; min-height: 0; overflow-y: auto; }   /* 패딩 0 */
```

이것이 A8 **전 페이지의 스크롤 컨테이너**다. 계획의 4단계는 «클래스명이 나오는 템플릿을 찾고 그 요소 서브트리에 링 요소가 있는 것만 발견» 인데,
`base.html` 의 서브트리에는 `{% block %}` 슬롯뿐이라 링 요소가 0이다. 측정 결과 `.app-frame`·`.app-frame__bg`·`.app-frame__content` 는 모두
**인벤토리로 강등**됐다(위 출력의 인벤토리 24건 첫 3줄).

계획은 한계를 «include 1단» 으로 적었지만 이건 깊이 문제가 아니다 — 기전이 다르다. include 를 2단·3단으로 늘려도 영영 못 본다.
`settings.css:528` `.app-frame__body:has([data-logout-dialog]:not([hidden])) .app-frame__content` 도 같은 이유로 인벤토리다.

**수정 방향.** 조인을 `{% extends %}`/`{% block %}` 상속 그래프까지 넓히거나, «블록 슬롯만 담은 컨테이너» 는 인벤토리가 아니라
별도 **«판정 불가»** 등급으로 배너에 올린다(조용한 강등 금지 — R1).

---

### [MAJOR] «A8 실측 여유 부족 27건» 이 재현되지 않는다 — 계약대로면 30건

2단계는 정확히 재현된다(선언 36 → **규칙 34**; `conversation.css:548-549`·`1064-1065` 가 한 규칙에 2선언).
3단계는 S 를 무엇으로 잡든 **30건**이다:

```
전 상태규칙(계획대로)  S=[5.0, 5.0, 3.0, 8.0]  → 후보 30건
포커스 규칙만          S=[3.0, 3.0, 3.0, 3.0]  → 후보 30건
S=3 균일                                        → 후보 30건
계획S − 포커스S 차집합: []
```

27 이 나오는 조건이 계약 문면에 없다. B-2 행동 시험의 합격 기준이 서지 않는다(픽스처가 아니라 A8 사본 기대값이므로 «대략»으로 넘길 수 없다).

---

### [MAJOR] 그림자 확장 `spread + blur/2` 는 명세 문면엔 맞지만 실제 페인트를 ~3배 과소평가한다 — 그리고 **미탐 방향**이다

**측정.** CSS box-shadow 와 같은 σ = blur/2 가우시안 규약을 쓰는 canvas 2D `shadowBlur` 로 재현해 흰 배경 알파 프로파일을 읽었다
(페이지 픽셀 직접 판독이 아니라 동일 규약 재현임을 밝힌다):

```
css_blur 10px → 계획 확장 5px
가장자리에서의 잉크 강도: 1px→112 · 3px→75 · 5px→45(18%) · 8px→17 · 12px→3 · 15px→0
잉크 0 도달 거리: 15px
```

즉 명세가 말하는 «전이 구간의 중심» 은 blur/2 가 맞지만, 그 지점에 아직 **18%의 잉크**가 남아 눈에 보인다.
rv-A 가 «`blur` 전체는 2배 과대» 라 한 것을 계획이 그대로 채택했는데, **여유 검사에서 과대는 안전한 방향**이다.
`blur/2` 로 내린 것은 판정을 미탐 쪽으로 옮긴 변경이고, 계획의 CC8 픽스처(«blur 만 있는 그림자 → 확장 blur/2»)가 그 과소 값을 계약으로 못박는다.
포커스 링(blur 0)에는 무영향이라 **이번 결함의 판정은 안 바뀐다** — 문제는 고정될 계약이다.

**수정 방향.** 하드 링(blur 0)과 블러 그림자를 분리한다. 블러 그림자는 `spread + blur`(보수) 또는 `blind_spots` 로 남기고, 임계를 blur/2 로 단일화하지 않는다.

---

### [MAJOR] 인라인 `style` · `<style>` 블록 · JS 로 붙는 overflow — A8 `web/` 이 0건이라 «통과»가 증거가 안 된다

**전수 확인(A8 `web/`).**

```
style="…overflow…"  → 0건
템플릿 <style> 블록  → 0건
UI JS(htmx 제외)의 overflow → 0건
```

그러나 **동결 시안 쪽에는 실재하고, 그것이 이 결함의 원본 선언이다** — `관계인.dc.html` 의 `<style>` 블록:

```css
[data-cm-dialog-scroll="true"] { flex: 1 1 auto; min-height: 0; overflow-y: auto; }
```

구현 `related_person_editor_step.html:56` 은 `<div class="rpe-scroll" data-cm-dialog-scroll="true">` 로 그 속성을 그대로 달고 있다.
즉 «오늘 A8 web/ 에 0건» 은 이 형식이 무해하다는 증거가 아니라, **다음 빌드에서 시안 판형이 그대로 옮겨오면 곧바로 미탐** 이라는 뜻이다.

**수정 방향.** web 루트의 템플릿 `<style>` 블록·`style=` 속성에 `overflow` 선언이 있으면 최소 `[warn]` + 배너 표면화(조용한 0건 금지).

---

### [MAJOR] `:root` 중복 정의에 승자 규칙이 없다 — A8에 **11건** 실재

**측정.**

```
:root 정의 토큰 538 · 중복 정의 11
  --dur-instant  90ms / 0ms      --press-scale  .972 / 1
  --dur-fast    150ms / 0ms      --settings-appbar-fill   color-mix(…) / var(--settings-glass-tint-bar)
  --dur-base    240ms / 0ms      --settings-appbar-border 1px solid … / var(--settings-glass-border)
  … (@media prefers-reduced-motion 등 게이트 블록 유래)
```

계획은 «`var()` 는 `:root` 선언에서 해소(깊이 6)» 라고만 적는다. 첫 정의 우선(내 프로토타입)과 마지막 정의 우선(CSS 캐스케이드)이 다른 답을 준다.
지금은 링 토큰이 중복이 아니라 결과가 안 바뀌지만, `@media (forced-colors: active)`·다크모드에서 `--focus-ring` 을 재정의하는 프로젝트에서는 임계가 임의로 정해진다 — 그리고 그 차이가 출력에 샌다.

**수정 방향.** `@media` **밖** `:root` 선언만 채택하고, 게이트 안 정의가 값을 바꾸면 `blind_spots` + `[warn]`.

---

### [MINOR] 캐스케이드로 패딩이 갈라진 경우 — A8엔 0건이지만 규칙 단위 판정이라 갈라지면 즉시 오탐

**전수 확인.** 클리핑 선언을 가진 셀렉터가 **다른 규칙**에서 padding 을 받는 사례 **0건**(전부 같은 규칙 안 — `.glass-panel`(`components.css:412-423`)은 한 규칙에 `padding: var(--card-pad)` + `overflow: hidden`).
후보 요소의 **동반 클래스(BEM 코-클래스)** 가 padding 을 주는 사례도 **0건**. 중복 셀렉터는 10개 있으나(`.app-frame` 2회 등) 어느 쪽도 padding 을 나눠 선언하지 않는다.

**수정 방향(공짜).** 선언 수집을 규칙 단위가 아니라 **정규화 셀렉터 단위로 병합**(문서 순서로 합침)하면 이 부류가 통째로 막힌다.

### [MINOR] 논리 속성(`padding-inline`/`padding-block`) 미지원 — 수리한 코드를 반송하게 된다

A8 전수 grep: `padding-inline`·`padding-block`·`margin-inline` **0건**. 그러나 계획이 제시하는 수리 예시 `padding: 3px 3px 4px` 를
모던 CSS 습관대로 `padding-block: 3px 4px; padding-inline: 3px` 로 쓰면 검사기가 패딩을 **못 읽어** red 가 그대로 남는다(고쳐도 반송).
`padding-inline(-start/-end)`·`padding-block(-start/-end)` 를 논리→물리 매핑(LTR 가정 + `direction: rtl` 이면 `blind_spots`)으로 읽어야 한다.

### [MINOR] `calc()` spread 가 조용히 0으로 떨어진다

계획 «색 함수·`#hex` 를 먼저 제거» 를 구현하면 함수 제거가 `calc()` 도 함께 지운다:

```
'0 0 0 calc(var(--r) * 1px) #000'  → 잔여 토큰 ['0','0','0']   ← spread 가 조용히 0
```

`color-mix(in srgb, rgb(208,114,122) 30%, transparent)`(2중 중첩)는 정상 제거되므로 CC7 픽스처 자체는 건전하다.
문제는 실패 거동이다 — rv-A MAJOR(파싱 규격)가 지적한 «조용한 green» 이 정적 경로에도 그대로 남아 있다.
**수정**: 길이 자리에 `<number>px|rem|em` 이 아닌 토큰이 오면 확장 0 이 아니라 `blind_spots` + 배너 표기.

### [MINOR] 결정론 누수 경로 4곳

1. **파일 순회** — `rglob` 은 OS readdir 순서. 선례 `check_motion_spec.check_impl`(`sorted(root.rglob("*.css"))`)를 반드시 따를 것.
2. **`:root` 변수 사전의 삽입 순서**가 파일 순회 순서에 의존(위 중복 11건과 결합하면 임계가 흔들린다).
3. **한 클래스가 여러 템플릿에 나온다** — 측정: `conversation-candidate` 가 **2개 템플릿**
   (`conversation_character_card.html`·`conversation_live_templates.html`). «첫 히트 break» 구현이면 순회 순서가 출력 문면(인용 템플릿)을 바꾼다.
4. **조인 키가 될 클래스의 선택 규칙 부재** — `[data-conversation-mount] .conversation-rooms` ·
   `.app-frame__body:has([data-logout-dialog]:not([hidden])) .app-frame__content` 에서 어느 클래스를 쓰는지 계약에 없다.
   전 클래스를 쓰면 `.app-frame__body` 까지 조인돼 오탐, 마지막 compound 만 쓰면 `[data-*]` 스코프가 버려져 다른 화면의 동명 클래스에 붙는다.
   **수정**: 「subject compound 의 마지막 클래스」로 명문화 + 발견/인벤토리 목록 정렬 키(파일·셀렉터) 고정.

---

## 요약

| 등급 | 개수 |
|---|---|
| BLOCKER | 4 |
| MAJOR | 11 |
| MINOR | 6 |

**BLOCKER 4건**
1. T1c — A8 «발견 6건» 중 실제 결함은 1건, 4건 확정 오탐(값 우연 일치·화면 밖·캔버스 크롬). 이 6건이 «반송 근거» 다.
2. T1 — 헤더 미검출 → `[warn]` + exit 0 이 무조건 탈출구. A8 실명세가 그 상태이고, `check_motion_spec` 에 있는 대칭 가드가 없다.
3. T2 — 1단계 전역 최대 확장에 장식 그림자(`--shadow-1`)가 섞여 S = [5,5,3,8]. **시안 값도 계획의 B-3 양성 대조도 통과하지 못한다**(측정 확인).
4. T2 — 3단계 축 판정이 `overflow-y:auto` 의 가로축 전파를 놓쳐, 좌우 링이 잘리는 상태를 «발견 0» 으로 승인한다(Chrome 실측 확인).

**이 계약대로 만들면**: T1 은 A8 에서 오탐 4 : 진탐 1 로 architect 를 반송하고(그마저도 산문 명세면 exit 0),
T2 는 시안을 정확히 구현한 `.rpe-scroll` 을 반송하면서 동시에 그 결함의 가로축 절반과 앱 전역 스크롤러를 못 본다.
