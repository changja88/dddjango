# 적대 검토 C — 범위·비용 (설계 v1 `workspace/design/2026-09-15-web-clip-fidelity.md`)

검토자: 독립 적대 검토 C. 자세: «이 설계는 과잉이다»의 입증.
A8 워크트리는 **읽기만** 했다(수정 0). 실측은 전부 아래 명령으로 재현 가능하다.

발견: **BLOCKER 3 · MAJOR 3 · MINOR 3**

---

### [BLOCKER] 수리 3은 이 결함을 못 잡는다 — 설계 §2와 §3.1이 서로를 반박한다

**주장**
설계의 본 수리(§2 수리 3)는 `clip` 판정 블록을 `assets/render_audit.js`에 넣는다.
그 스크립트는 **목표 페이지 1개의 초기 렌더**에서 돈다. 이번 결함의 컨테이너
`.rpe-scroll`은 HTMX로만 들어오는 다이얼로그 안이라 그 DOM에 **없다**.
따라서 `querySelectorAll(기반 셀렉터)`는 0건을 반환하고 `clip.findings`는 빈 배열이 된다.
설계 §6 브리프의 «수리 3 단독 / 이번 결함 = 잡는다»는 **사실과 다르며**, 그 표가 곧
사용자 승인 게이트에 올라가는 수치다.

설계는 이 사실을 **자기가 이미 적었다**. §3.1(110–112행):
> «이번 결함의 컨테이너는 **다이얼로그 안**이라 초기 렌더에 존재하지 않는다 — 렌더 실측은
> 초기 페이지에서 돌므로 그 컨테이너를 영영 못 본다.»

같은 문장이 §2.1(49–51행)의 «이번 케이스는 정확히 이 규칙에 걸린다»를 무효화한다.
수리 2를 정적 추출로 돌린 바로 그 이유가 수리 3에는 적용되지 않은 채 남아 있다.

**근거**

1) 렌더 실측은 URL 1개다 — `commands/dddjango-web.md:31`
   > `렌더 실측 동결 → <산출물 폴더>/render-audit.json (목표 페이지 — Phase 0 step 5-5)`

2) A8 구현 실측의 URL과 내용:
```
$ python3 -c "import json;d=json.load(open('/Users/hyun/.herdr/worktrees/spring_dream_server/a8/.dddjango-web/20260912-1640-web-related-persons/render-audit-impl.json'));print(d['audit_version'],d['url'],len(d['texts']))"
2 http://127.0.0.1:8891/related-persons/ 13
```
   texts 13건 전부 목록 화면 문구다 — `관계인` · `관계인 등록하기` · `김서연` · `등록한 사람 4명` …
   편집기 step 문구(`이름을 입력해주세요` 등)는 **0건**.

3) 목록 뷰의 오버레이 마운트는 **빈 div**다 —
   `/Users/hyun/.herdr/worktrees/spring_dream_server/a8/web/related_persons/related_person_list/view/related_person_list.html`
```html
<div id="rp-overlay"></div>
```
   `.rpe-scroll`의 유일한 출처는
   `web/related_persons/related_person_editor/section/related_person_editor_step.html:56`
   이고, 목록 템플릿 트리에서 그 파일을 include하는 곳은 없다:
```
$ grep -rn 'related_person_editor_step' .../related_person_list/     # 결과 0
```

4) CSSOM에서 온 `focusSelectors`에는 `.input-field__control:focus-within`이 **있다**(9건).
   그러나 §2.2 step 4는 그 셀렉터로 `querySelectorAll`을 돈다 — 목록 페이지에 입력 필드는
   0개다. CSSOM 존재와 DOM 존재를 혼동한 설계다.

**더 싼 대안**
아래 [BLOCKER] 정적 검사로 갈아탄다 — DOM 존재 여부와 무관하므로 이 구멍이 구조적으로 없다.
정 브라우저 경로를 유지하려면 최소한 «편집기 dual-mode full-page URL(`state.add_url`)도
실측 대상에 넣는다»를 설계에 명시해야 하는데, 그건 Coordinator 계약(실측 URL 1개→N개)
변경이라 설계 §4 규범 편집표에 없다. 어느 쪽이든 v1 상태로는 미완이다.

---

### [BLOCKER] 브라우저·스키마 버전 없이 정적 CSS만으로 같은 결함을 잡는다 — 스크립트 1개

**주장**
이 결함은 «스크롤러 규칙의 가로 패딩 < 포커스 링 확장»이라는 **정적 CSS 사실**이다.
동결 CSS와 템플릿만으로 판정된다. 설계가 요구하는 `audit_version 3` 올림 ·
순수/DOM 분리 · `node --test` 표본 · 실브라우저 회귀 · v1/v2 호환 특례가 **전부 불요**하다.
그리고 앞의 BLOCKER와 달리 다이얼로그 안이어도 잡는다.

**근거** (A8 web CSS 14개 전수 — 9빌드치 누적 구현)

`overflow: auto|scroll`을 선언하는 규칙은 전 저장소에 **11건**뿐이다:
```
$ python3 - <<'PY'   # 요약 — 전문은 이 보고 하단 «재현 명령» C4
CSS rules with overflow auto|scroll across ALL 14 A8 web CSS files: 11
   app_shell.css:42     .app-frame__content               ['-y:auto'] padding=None
   chart.css:1135       .chart-major-fortunes__strip      ['-x:auto'] padding=2px 0 10px
   conversation.css:348 …bottom-sheet__content            ['-y:auto'] padding=None
   conversation.css:539 …conversation-ledger              ['-y:auto'] padding=var(--chat-ledger-padding)
   conversation.css:613 …conversation-composer            ['-y:auto'] padding=var(--chat-composer-input-padding)
   conversation.css:1059…conversation-candidates          ['-x:auto'] padding=var(--chat-carousel-padding)
   conversation.css:1192…conversation-rooms               ['-y:auto'] padding=var(--chat-rooms-padding)
   conversation.css:1632…record-detail__body              ['-y:auto'] padding=var(--space-6) var(--gutter)
   related_persons.css:293  .rp-detail__body              ['-y:auto'] padding=None
   related_persons.css:391  .rpe-scroll                   ['-y:auto'] padding=None   ← 결함
   user_info.css:200        .user_info__sheet-body        ['-y:auto'] padding=None
of these, padding absent or 0 on the horizontal axis: 5
```
- **이번 빌드의 화면 CSS(`related_persons.css`)만 보면 후보는 2행**이다. 판정 표가 2행이다.
- 링 확장은 정적으로 읽힌다 — `web/design_system/foundation/tokens.css:193`
  `--focus-ring: 0 0 0 3px rgba(208,114,122,.30)`.
- 「서브트리에 포커스 가능 요소가 있는가」 조인도 정적이다:
  `.rpe-scroll`은 `related_person_editor_step.html:56`에 있고 같은 파일 안에
  `<select …>`(67) · `input_field.html` include(76·86) · `pair_choice.html`(79·88) ·
  `<input type="checkbox">`(92)가 있다 — 전부 `:focus-within` 링 보유 컴포넌트다
  (`components.css:290·613·833` — 아래 MINOR의 12건 실측).

판정 규칙: **«화면/DS CSS에서 `overflow`가 `auto|scroll`인 규칙의 가로 패딩이 링 확장(3px)보다
작고, 그 클래스를 다는 템플릿 서브트리에 포커스 링 보유 요소가 있으면 red.»**

비용 비교(설계 §6 브리프 판형):

| | 설계 수리 3 | 이 정적 검사 |
|---|---|---|
| 새 스크립트 | 1 | 1 |
| audit_version 올림 | 2→3 (+`ACCEPTED_VERSIONS`·`--require-version 3`·v2 미실행 특례) | 없음 |
| 순수/DOM 분리 + `node --test` 표본 | 필요 | 불요 |
| 실브라우저 회귀(`verify-web-browser`) | +1건 | 0 |
| 다이얼로그 안 컨테이너 | **못 잡음** | 잡음 |
| 이번 결함 | **못 잡음** | 잡음(후보 2행) |

**더 싼 대안**
위 검사 하나. 설계 §4의 규범 편집도 `commands/dddjango-web.md`(G2 실행+배너) 1파일 +
`Makefile`(픽스처 1종)로 줄어든다 — 8파일 → 2파일.

---

### [BLOCKER] §1의 «결정적 반증»이 사실과 다르다 — 「크기 전수 연결」은 고갈된 게 아니라 **위반됐다**

**주장**
설계 §1(21–24행)은 «2px·4px가 이미 토큰으로 처분됐으므로 토큰 축 확대로는 이 결함을
못 잡는다»를 근거로 진단의 수리 2를 기각하고 새 처분 축(클리핑 컨테이너)을 신설한다.
그 전제가 틀렸다. 이 빌드는 `--space-1`(=2px)을 **«미사용»이라는 거짓 사유로 기각**했다.
즉 기존 규범이 소진된 것이 아니라 **집행되지 않아 틀린 답이 통과**한 것이다.
그리고 토큰 처분에는 **기계 검사가 아직 하나도 없다**. 있는 규범을 집행해 보기 전에
세 번째 처분 축을 신설하는 것이 설계의 실제 제안이다.

**근거**

1) 토큰은 설계 주장대로 존재한다 — `20260912-1640-web-related-persons/design-tokens.json`
```
/spacing/--space-1 = 2px
/spacing/--space-2 = 4px
```

2) 그러나 `design-spec.md:468`:
```
- 기각(15): …,`--space-0`,`--space-1`,`--space-3`,`--space-10`,… — 프레임 치수(…)·미사용 space 단계.
```
   `--space-1`이 **기각**이고 사유가 «미사용 space 단계»다. 2px는 이 빌드의 동결 dc HTML
   인라인 레이아웃 선언에 **4회** 나온다 — 그중 하나가 문제의 `padding: 2px 2px 4px`
   (`design-ref/관계인.dc.html:108`):
```
$ python3 …  # 재현 명령 C3
--space-1   2px    4  padding:2px 4px 0; gap:2px; padding:2px 2px 4px; padding:0 2px
```

3) «기각 사유가 미사용인 토큰의 값이 인라인 **레이아웃-길이** 선언에 나타나는가» 검사의
   노이즈는 **3/15**다(전 토큰 풀 229 기준 3행):
```
--space-1   2px    4 hits   ← 결함 적중
--space-10  40px   2 hits
--space-13  80px   1 hit
나머지 12개 기각 토큰  0 hits
```
   (단순히 «값 문자열이 파일에 나타나는가»로 세면 9/15로 노이즈가 크다 — `hint-size="100%,80px"`
   같은 캔버스 힌트 속성 때문. `style=` 안의 길이 계열 선언으로 좁히면 3/15가 된다.)

4) 토큰 처분 검사기는 존재하지 않는다:
```
$ grep -rln 'design-tokens' scripts/ assets/
scripts/refreeze.py  scripts/extract_design.py  scripts/extract_dc.py  scripts/test/…
$ grep -n '토큰\|채택\|기각' scripts/backstop.py scripts/check_design_evidence.py
(결과 0)
```
   `skills/architecture-web/references/final.md:142` 「크기 전수 연결(설계자 소유)」는
   **산문 의무일 뿐** 기계 백스톱이 0이다. 이번 결함은 그 규범의 **부재**가 아니라
   **미집행**의 결과다.

**더 싼 대안**
새 처분 축을 만들기 전에 **있는 축을 집행한다**: 기존 §9.1 처분 표에 대해
«기각 토큰의 값이 동결 dc의 인라인 레이아웃-길이 선언에 있으면 red» 1종.
스크립트 1개·규범 편집 0(의무는 이미 final.md:142에 있다)·표 3행.
그래도 남는 구멍(«좌표가 없다»)은 위 [BLOCKER] 정적 CSS 검사가 구현측에서 닫는다.
두 검사의 합이 설계의 3스크립트·8파일보다 싸고, 이번 결함을 **양쪽에서** 잡는다.

---

### [MAJOR] 수리 2의 «감당 가능» 근거가 잘못된 분모다 — 빌드당 중앙값 3이 아니라 **33**

**주장**
설계 §1 표 3행과 §3(106행)은 클리핑 컨테이너가 «행 수 중앙값 3·최대 28»이므로
「동적 표현 전수」와 «같은 판형으로 감당된다»고 한다. 그런데 처분 표의 실제 단위는
**파일이 아니라 빌드**다 — `design-spec.md`에 표가 1개 서고 그 빌드의 dc 전부를 덮는다.
빌드 단위로 다시 세면 중앙값 **33**·최대 **50**이고, 비교 대상인 motion-notes는
빌드당 7~24행(중앙값 9~10)이다. **3.5배**다.

**근거**
```
$ # 재현 명령 C5 — 빌드(산출물 폴더)별 집계
build                                files elems decl-all decl-len  CLIP
20260905-2018-web-auth-screens           1    47      155       71     3
20260907-2249-home-bottom-nav            7   815     2550     1226    41
20260907-2302-user-info-input            1    12       43       20     1
20260908-0055-web-settings               8   902     2825     1368    50
20260908-0143-web-chat-spine             8   862     2650     1248    33
20260908-1534-web-chart                  8   863     2649     1248    33
20260909-1612-web-chart-app-bar         12   884     2787     1320    42
20260909-1616-web-settings-update       12   884     2786     1319    42
20260912-1640-web-related-persons        2    40      118       49     3
PER-BUILD clip elems   median=33.0  max=50   (n=9)
```
motion-notes 실측(같은 9빌드):
```
$ for f in …/*/motion-notes.md; do grep -cE '^\|\s*m[0-9]+\s*\|' "$f"; done
24 9 10 10 9 9 7 10 9      → 중앙값 9~10 · 최대 24
```
이번 관계인 빌드가 3행인 것은 dc가 2개뿐인 **가장 작은 빌드**라서다. 설계는 그 표본으로
일반 판형을 주장했다.

**더 싼 대안**
§3.1의 신호를 «인라인 `overflow ≠ visible` ∪ `data-*scroll*`»에서 **«스크롤러만»**
(`auto|scroll` — `hidden`·`text-overflow` 제외)으로 더 좁히면 위 [BLOCKER]의 11건 규모가
된다. 혹은 §6 브리프의 «추정 규모» 행을 실제 분모로 고쳐 사용자에게 다시 올린다 —
지금 숫자로는 사용자가 «모션 처분만큼»이라고 읽는다.

---

### [MAJOR] §1 표가 재현되지 않는다 — 추출 술어가 문서에 없다

**주장**
§1 표는 이 설계의 **유일한 결정 근거**이고 `extract_clip_containers.py`의 판정 규칙
정본이기도 하다. 그런데 «어느 속성 집합인가 · 요소를 세는가 선언을 세는가 ·
`hint-size` 같은 비-`style` 속성은 제외하는가 · 59개는 어떻게 고른 표본인가»가 없다.
내가 두 가지 합리적 해석으로 세었으나 어느 쪽도 표와 맞지 않는다. 결론(R1 기각·R3 채택)은
바뀌지 않지만, 구현자가 같은 수를 못 낸다.

**근거** (HTMLParser 기반 · 59파일 · 재현 명령 C1·C2)

| 후보 | 설계 주장 | 내 실측(요소) | 내 실측(선언) |
|---|---|---|---|
| 모든 인라인 레이아웃 | 39 / 1287 | 13 / 439 | 47 / 1322 (좁은 목록이면 38 / 1168) |
| 생 리터럴만 | 12 / 510 | **12** / 435 | 26 / 729 |
| 클리핑 신호 | 3 / 28 | **2 / 22** | — |

- 「생 리터럴」 중앙값 12는 **요소 수**로 세었을 때만 맞고 최대 510은 맞지 않는다.
- 클리핑 신호 최대는 28이 아니라 **22**다(중앙값 3이 아니라 2). 설계에 **유리한 쪽으로**
  틀렸다 — 실제 규모는 주장보다 작다. 그래도 근거 수치가 틀린 것은 틀린 것이다.
- `data-cm-scroll`: 설계 «66» vs 내 실측 요소 **68** / 문자열 출현 **90**
  (차이는 `dc-props` 속성값·스크립트 안의 출현 — 파서를 안 쓰면 24가 더 잡힌다).
  이 차이가 곧 추출기의 오탐 축이다.

**더 싼 대안**
§1에 술어를 그대로 적는다 — 속성 화이트리스트 · 「요소 1행」 규칙 ·
`style=` 밖(예: `hint-size`·`dc-props`) 제외 · 표본 «59 = 69 − `_history` 8 − `_refreeze` 2».
5줄이면 되고, 그게 없으면 검사기 구현자가 설계를 다시 추측한다.

---

### [MAJOR] `static_shadows` 인벤토리는 «미리 만든 확장 지점»이다 — 63건을 영구 적재한다

**주장**
§2.3 스키마의 `static_shadows: [ … ] // 비판정 참고 인벤토리 — 후일 확대의 훅`은
**판정도 소비자도 없는 데이터**를 모든 동결본에 영구히 싣는다. 프로젝트 지침
(`AGENTS.md` «불필요한 추상화나 미리 만든 확장 지점을 추가하지 않는다»)과 전역 원칙 05
(«아직 쓰이지 않는 기능·옵션·확장 지점은 만들지 않는다»)에 정면으로 어긋난다.
게다가 버전 게이트된 스키마라 나중에 빼려면 v4가 또 필요하다 — 훅이 아니라 자물쇠다.

**근거**
A8 web CSS 전수에서 판정 대상(포커스 outer shadow)은 12건인데
정적 outer box-shadow 규칙은 **63건**이다 — **5.25배**를 미판정 상태로 싣는다.
```
$ python3 …   # 재현 명령 C6
STATIC outer box-shadow rules (non-focus): 63
focus/checked rules WITH box-shadow: 14  → box-shadow:none 2건 제외 = 12   ← 설계 §1의 «12건» 정확
```
(설계의 구현측 «12건»과 «base.css :: :focus-visible 1건이 전역» 주장은 **정확히 맞다** —
`base.css:85` `:focus-visible { box-shadow: var(--focus-ring) }`. 이 부분은 반증 없음.)

**더 싼 대안**
넣지 않는다. 정적 그림자 판정을 실제로 착수하는 날 그 산출물과 함께 추가한다.

---

### [MINOR] `audit_version 3` 올림이 사는 값이 없다

**주장** v3의 유일한 내용이 `clip` 블록인데 첫 BLOCKER대로 그 블록은 이번 결함에
빈 배열을 낸다. 대가는 작지 않다: `ACCEPTED_VERSIONS = {1,2}` → `{1,2,3}` ·
`--require-version 3` · §5 R1의 «v2 동결본 미실행 보고» 특례 ·
A8 진행 중 재동결(`_refreeze-20260915-200029`, v2)과의 충돌 처리.

**근거** `compare_render_audit.py`는 이미 `CURRENT_VERSION` 분기가 43·70·72·81·100·194행에
흩어져 있다. v3는 그 분기를 한 단계 더 늘린다 — 판정 하나 추가의 대가로는 비싸다.

**더 싼 대안** clip 판정을 audit 스키마 **밖 별도 산출물**로 내면 버전 올림이 0이다.
또는 두 번째 BLOCKER대로 아예 정적 검사로 옮긴다.

---

### [MINOR] 실브라우저 회귀 1건은 우리 규범이 아니라 브라우저 API를 시험한다

**주장** §2.4는 `verify-web-browser`에 `repro.html` 회귀 1건을 더한다. 그 시험이 확인하는
명제는 «패딩 0이면 여유 0, 패딩 3px면 여유 3px»다 — 이건 `getBoundingClientRect`와
computed padding의 동작 시험이지 우리 판정 규칙의 시험이 아니다.
판정 규칙 자체는 §2.4가 이미 순수 함수로 떼어 `node --test`로 덮는다.

**근거** `release-web`은 `verify-web-browser`를 경유하고(`Makefile:305`) 브라우저
스위트는 1149초다(진단 §절차 63행). 1149초짜리 관문에 «못 잡는 검사의 자기 확인»을
더한다.

**더 싼 대안** 순수 함수 표본만 남긴다. 브라우저 회귀는 clip 판정이 실제로 결함을 잡는
경로가 확정된 뒤에 넣는다.

---

### [MINOR] «59개 파일 전수»의 표본 정의가 없다

**주장** `find`로 세면 **69개**다. 59는 `_history/v1~v4` 8개와 `_refreeze-…` 2개를 뺀 수다.
설계는 «전수»라고만 쓰고 제외를 밝히지 않아 재현자가 10개 어긋난 수를 낸다.

**근거**
```
$ find …/.dddjango-web -path '*/design-ref/*.dc.html' -type f | wc -l
69
$ find …/.dddjango-web -path '*/design-ref/*.dc.html' -not -path '*_history*' -not -path '*_refreeze*' | wc -l
59
```

**더 싼 대안** §1 첫 줄에 «(`_history`·`_refreeze` 제외)» 한 구절.

---

## 설계가 «하지 않기로 한 것» 판단

**정적 그림자(카드 drop-shadow) 절단 판정 미착수 — 옳다.** 판정 대상이 12건에서 63건으로
5배 커지고, 정적 그림자는 «잘려도 무방»한 디자인(카드가 컨테이너 가장자리에 붙는 배치)이
흔해 판정 규칙이 아직 없다. 규칙 없이 범위만 늘리면 고무도장이 된다 — 원칙 05에 맞다.
곧 또 수리하게 될 징후도 없다: 사용자가 지목한 결함 계열은 **포커스 링**이고, 정적 그림자
절단이 보고된 적은 없다.

**단, 인벤토리까지 미리 싣는 것은 «미착수»가 아니다** — 위 MAJOR 3.

---

## 재현 명령

작업 스크립트는 scratchpad에 두었다(저장소·A8 워크트리 수정 0).
`/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/5d88d7d2-4bb6-412e-83fa-56580ac7b33b/scratchpad/{count_clip.py,count2.py}`

- **C1** 표본 수 — `find <A8>/.dddjango-web -path '*/design-ref/*.dc.html' -type f | wc -l` → 69,
  `-not -path '*_history*' -not -path '*_refreeze*'` → 59
- **C2** §1 표 재계수(HTMLParser) — `count2.py`
- **C3** 기각 토큰 값의 인라인 레이아웃 출현 — 본문 [BLOCKER] 3번 블록
- **C4** 스크롤러 규칙 전수 — A8 `web/**/*.css`에서 `overflow: auto|scroll` 규칙 추출 → 11건
- **C5** 빌드별 집계 — 본문 [MAJOR] 1번 블록
- **C6** 포커스/정적 outer box-shadow 계수 — 12건 / 63건
- **C7** 실측 URL — `python3 -c "import json;d=json.load(open('…/render-audit-impl.json'));print(d['url'])"`

## 도구 사용

Serena 미사용 — 이 워크트리 루트에 `.serena/project.yml` 없음(opt-in 표식 부재).
Graphify 미사용 — `graphify-out/graph.json` 없음. 전부 기본 읽기·검색 도구로 수행했다.
