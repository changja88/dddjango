# 계획 리뷰 1 — 배선·누락 (2026-09-15)

대상: `workspace/plan/2026-09-15-web-clip-fidelity-plan.md`
기준: 설계 v2 `workspace/design/2026-09-15-web-clip-fidelity.md` · `design-review/verified.md`

**BLOCKER 4 · MAJOR 6 · MINOR 7.**
표기 — «확인» = 내가 명령을 돌려 직접 봤다. «미확인» = 문면 추론이다.

---

### [BLOCKER] B1. Codex byte 미러 목록에 신규 픽스처 2종이 빠졌다 — `make verify`가 RED

**무엇이 빠졌나.** T1 «파일» 절은 미러 대상으로 `check_token_disposition.py` **한 개**만 적는다
(계획 22행). T2는 `check_clip_clearance.py + 미러`만 적고(75행) 픽스처 행(76행)에는 미러를 안 적는다.
그런데 `verify-web`의 미러 대조는 `scripts` **디렉터리 전체 재귀**다 — `scripts/test/` 도 포함된다.

**근거**(확인).
- `Makefile:96` — `diff -rq --exclude=__pycache__ dddjango-web/scripts codex-dddjango-web/skills/dddjango-web/scripts`
- 현재 Codex 미러에 픽스처가 **이미 전부 있다**: `codex-dddjango-web/skills/dddjango-web/scripts/test/fixtures_{assets,audit,backstop,contract,design_evidence,evidence_debt,extract,interactions,motion_spec,refreeze,templates,ui_javascript}.sh` 12종 + `run_fixtures.sh` + `test/fixtures/interaction/**`.
  즉 픽스처는 «배선 불요»가 아니라 **byte 미러 의무 대상**이다.
- 계획 11행이 «`scripts/`는 Codex byte 동일 미러(`Makefile:96-97` `diff -rq` 가 자동 검출)»라고 쓴 것은
  맞지만, «자동 검출»은 **RED로 검출**한다는 뜻이다 — 누락하면 통과가 아니라 실패다.

**수정 방향.** T1·T2의 파일 표에 `codex-dddjango-web/skills/dddjango-web/scripts/test/fixtures_token_disposition.sh`
· `…/fixtures_clip_clearance.sh` 2행을 명시하고, 22행/76행의 «(글롭 자동 수집 — 배선 불요)» 문구는
«run_fixtures 글롭은 자동 · **Codex 미러는 수동 의무**»로 가른다.

---

### [BLOCKER] B2. architect가 byte 고정 판형을 쓸 의무가 **생산자 프롬프트에 없다** → 검사가 영구 `[warn]`

**무엇이 빠졌나.** T1은 파스 앵커를 `| 축 | 처분 | 토큰 |` **byte 고정**으로 잡고, 헤더 미검출은
`[warn]` + **exit 0**으로 처리한다(계획 30-35행). 그런데 T3에서 architect에게 시키는 것은
«기각 사유의 사실성 의무»뿐이다(121행) — **«이 판형으로 적어라»가 어디에도 architect 프롬프트로
내려가지 않는다.** 판형 문장은 `architecture-web/references/final.md:142` 1문장(124행)뿐이다.

**근거**(확인).
- 선례 대조 — 모션 판형 리터럴은 **생산자 프롬프트에 직접** 박혀 있다:
  `dddjango-web/agents/design-architect-web.md:46` — «**처분은 §8의 기계가독 처분 표 판형으로 적는다**
  (헤더 `| note id | 처분 | 분류 | 구현 좌표 | 값 | 근거 |` byte 고정 …)».
  같은 리터럴이 `agents/design-review-web.md:45`, `skills/architecture-web/references/final.md:145`,
  검사기·픽스처까지 **4곳**에 있다(`grep -rn "note id | 처분"`).
- 토큰 축의 현행 산문은 판형이 아니라 **자유 서술**이다. A8 실빌드 3개를 직접 열었다:
  - `20260912-1640-web-related-persons/design-spec.md` — `**spacing (35)**` / `- 채택(20): …` / `- 기각(15): …` / `- 소계: 20 + 15 = 35 ✓`
  - `20260909-1612-web-chart-app-bar/design-spec.md:137` — `| category | 전체 | 채택 key(개수) | 기각(개수)·근거 |` (**다른 헤더**)
  - `20260908-1534-web-chart/design-spec.md:294-301` — 산문 불릿 + «수량 대조: 절단 230 = …»
  → 설계 v2 §1의 «2026-09-09 빌드가 이미 사실상 이 모양으로 쓰고 있다»는 **실물과 다르다**.
- 결과: 판형 의무가 생산자에 없으면 다음 G1에서도 헤더 미검출 → `[warn]` + exit 0. 즉 **본 수리가
  한 번도 발동하지 않는다.**

**수정 방향.** T3에 `agents/design-architect-web.md` 행을 하나 더 두고 `:48`(토큰 전수 연결)에
`:46`과 같은 문장 — «처분은 §8 기계가독 표 판형으로 적는다(헤더 `| 축 | 처분 | 토큰 |` byte 고정 ·
5축 × 채택/기각 10행)» — 을 넣는다. `design-review-web:45 ⓑ`에도 ⓓ처럼 헤더 리터럴을 함께 적는다.
추가로 검사기의 `[warn]` 메시지가 기대 판형 예시를 출력하게 한다(`fixtures_motion_spec.sh:96` 선례).

---

### [BLOCKER] B3. 새 G1 검사의 **발동 조건(플래그)** 이 계획에 없다

**무엇이 빠졌나.** T3의 `commands:168` 행(119행)은 ««같은 시점 — 모션 처분 표 기계 점검» 옆에
토큰 처분 기계 점검 1문장 추가»라고만 쓴다. **어떤 플래그일 때 도는지가 없다.** 이 검사는
`design-tokens.json` 과 `design-ref/` 두 입력을 요구하는데, 둘 다 **조건부 산출물**이다.

**근거**(확인).
- `commands/dddjango-web.md:65` — `has_design_tokens`(«design-tokens.json 추출에 성공했으면 true»)
- `:64` — `has_design_screen`, `:69` — `has_motion_notes`, `:70` — `has_render_audit`
- `:163` — architect 입력 열거가 «`design-tokens.json` 경로(`has_design_tokens`이면) · `design-ref/` 경로(있으면)»
  로 **이미 조건부**다. 즉 시안 없음·이미지 단독·토큰 추출 실패 빌드에서는 두 입력이 없다.
- 선례는 전부 플래그를 명시한다: `:168` 모션 점검 = `(has_motion_notes이면)` · `:187` 렌더 대조 =
  `(has_render_audit이면)` · `:187` 모션 대조 = `(has_motion_notes이면 — has_render_audit과 무관하게)`.
- 조건이 없으면 두 갈래로만 귀결한다 — ① Coordinator가 안 돌린다(조용한 미발동) ② 항상 돌려
  입력 부재 exit 1이 매 빌드 «미실행» 소음으로 쌓인다. 둘 다 집행 실패다.

**수정 방향.** `(has_design_tokens이고 design-ref가 있으면)` 같은 발동 조건을 T3 행 문면에 못박고,
false일 때의 1줄(«토큰 처분 점검: 해당 없음(토큰 추출 없음)»)까지 함께 규정한다
(`:187`의 «`has_motion_notes`가 false면 «모션 처분 대조: 해당 없음(관찰 채널 부재)» 1줄» 선례).

---

### [BLOCKER] B4. 행동 시험 B-1 의 기대값이 계획 자신의 T1c 규칙으로 재현되지 않는다

**무엇이 틀렸나.** 계획 54-58행은 A8 `20260912-1640-web-related-persons` 실측 기대값을
«풀 230 · 기각 134 · 대조 가능 57 · 미대조 77 · **발견 6건**»으로 못박고 B-1을 그 재현으로 정의한다.
내가 같은 빌드에 계획의 T1a/T1b/T1c 규칙을 그대로 적용해 본 결과가 **세 군데에서 다르다.**

**근거**(확인 — A8 원본 무수정 읽기 전용 실행).
1. **풀 230 · 기각 134 는 맞다.**
   `design-tokens.json` = colors 106 · typography 50 · spacing 36 · borderRadius 14 · shadows 24 = **230**,
   `design-spec.md`의 기각 합계 = **134**.
2. **T1a·T1b 발견 3건이 기대값에서 통째로 빠졌다.**
   - 미처분 1건: `--safe-top`(spacing). 명세는 `**spacing (35)**` · `소계: 20 + 15 = 35 ✓`로 닫혀 있는데
     풀은 **36**이다 — 명세의 자기 계수는 green, 기계는 red. 이것이 T1a의 존재 이유 그 자체다.
   - 중복 처분 2건: `--fw-regular` · `--fw-semibold` 가 typography의 **채택·기각 양쪽**에 있다
     (기각 줄은 `기각(28)`이라 선언하지만 백틱 토큰은 **30개**다). T1b의 `채택 ∩ 기각` 발견이다.
3. **T1c 발견도 6이 아니다.** 계획의 규칙(5축 풀 · `^-?[\d.]+px$` · rem/em ×16 · 비변별 9값 제외 ·
   인라인 `style="…"` 대조)을 그대로 돌리면 계획이 적은 6건 외에
   `--fs-display-2`(28px) · `--fs-label`(14px) 이 더 걸린다. 걸리는 자리를 특정하면:
   `28px` → `padding` 선언 1건 · `14px` → `gap` 선언 4건 — 즉 **typography 토큰이 spacing 선언에 걸리는
   축 교차 매칭**이다(→ MAJOR M6). 대조 가능/미대조도 **71 / 60** 이 나와 57/77과 다르다.
4. **커버리지 1줄 자체가 내부 모순이다.** 57 + 77 = 134 = 기각 전체 — 그러면 «비변별 값 제외»
   (계획 49-50행) 버킷이 **0건**이라는 뜻인데, 같은 명세가 `--space-0: 0px`을 기각했다(확인).
   제외분이 어느 칸에 들어가는지 정의가 없다.

**왜 BLOCKER인가.** 「발견 6건」은 B-1의 **합격 기준**이다. 구현자가 이 숫자를 맞추려 하면
(ⓐ) T1a/T1b 발견을 억누르거나 (ⓑ) typography 축을 말없이 대조에서 빼거나 (ⓒ) 안 맞는데 green으로
적는다 — 셋 다 «조용한 미검증»을 만든다.

**수정 방향.** 기대값을 **검사 종류별로 분해**해 다시 적는다(예: T1a 1 · T1b 2 · T1c N)。
T1c의 N은 축 교차 규칙을 확정한 뒤(M6) 다시 실측한다. 커버리지 줄은 `기각 N = 대조가능 M +
미대조 K + 비변별제외 E` 4항으로 정의한다. 기대값의 산출 명령을 계획에 남겨 재현 가능하게 한다.

---

### [MAJOR] M1. Codex 미러 열거가 «agents 대응 SKILL»로 뭉뚱그려져 있다 — 기계 백스톱이 없는 구간

**무엇이 빠졌나.** 126-127행은 Codex 미러를 «`skills/dddjango-web/SKILL.md`(의미 미러) · `agents` 대응
SKILL · `skills/architecture-web/references/final.md`(byte 동일)»로 적는다. 가운데 항목이 **파일명이 없다.**

**근거**(확인). 실제 대상은 3개다 —
`codex-dddjango-web/skills/dddjango-web-design-architect-web/SKILL.md` ·
`…/dddjango-web-design-review-web/SKILL.md` · `…/dddjango-web-discipline-reviewer-web/SKILL.md`.
그리고 **이 3개는 `make verify`가 대조하지 않는다**: `Makefile:96-104`가 보는 것은 `scripts`·`assets`
디렉터리(`diff -rq`)와 references 4종·REQUEST_GUIDE(`cmp -s`)뿐이다. 즉 agent SKILL 미러는
**순수 수동 의무**이고, 빠뜨려도 green이다 — 이름을 적지 않으면 새는 지점이 여기다.

**수정 방향.** T3 하단 미러 문단을 파일 6행 표로 바꾸고, 각 행에 «byte / 의미» 구분과
«verify가 잡음 / 안 잡음»을 같이 적는다.

---

### [MAJOR] M2. exit 1(미실행) 처리가 G1 검사에만 없다 — 조용한 통과 통로

**무엇이 빠졌나.** T3의 `:187` 행(120행)은 «exit 1 은 미실행 취급»을 명시한다. 그런데 `:168` 행(119행)은
«FINDING 은 architect 반송 · [warn] 은 배너 표면화»까지만 적고 **exit 1을 안 적는다.**
T1 계약은 exit 1을 «사용법·파싱(미실행 취급 — 통과 아님)»으로 정의했는데(27행) 그 의미를
**커맨드 문면으로 배선하지 않았다.**

**근거**(확인). 이 검사의 exit 1 유발 경로는 실재한다 — `design-tokens.json` 파싱 실패, `design-ref`
부재(재동결 진행 중 `refreeze.py:32-37 FIXED_DISCARD_FILES`·`FIXED_DISCARD_TREES=('design-ref',)`가
실제로 비우는 구간), 인자 누락. 선례는 같은 줄에서 `extract_contract.py`의 exit 1을 **stderr로 가르는
분기까지** 규정한다(`commands:168`).

**수정 방향.** `:168` 행 문면에 «exit 1은 미실행 취급 — 통과로 간주 금지, stderr 원인을 배너에
미실행 사유로» 를 넣는다(`:186` 백스톱·`:187` compare와 같은 판형).

---

### [MAJOR] M3. 빌드 스펙 정본(D 결정 대장) 갱신이 계획에 없다

**무엇이 빠졌나.** T4는 `docs/DEVELOPMENT.md` §1과 `ontology-adoption-map.html`만 든다.
`workspace/design/2026-08-23-web-presentation-layer-spec.md`(AGENTS.md가 «빌드 스펙 정본»으로 지정)
가 없다.

**근거**(확인). 같은 성격의 선행 작업은 모두 이 파일을 함께 고쳤다 —
`git log -- workspace/design/2026-08-23-web-presentation-layer-spec.md`:
`72854ce3 feat(web): 모션 검증 결정론화 …(D13 v2)` · `9b60ce7a feat(web): 시각 충실도 축 — 렌더 실측 채널·G2 기계 대조 …(D13)`.
현재 `:42`의 D13 행이 렌더 실측·모션 검증 채널을 소유한다. 토큰 처분 집행과 절단 여유 검사는
**새 D 결정**이거나 D13 개정인데 계획에 그 자리가 없다. 설계 v2 §4 표에도 없다(설계와 공유된 누락).

**수정 방향.** T4에 «빌드 스펙 정본 D 행 추가/개정(번호는 기존 D 대장에서 채번)» 항목을 넣거나,
넣지 않기로 한다면 «왜 이 변경은 D 결정이 아닌가»를 계획에 1줄로 남긴다.

---

### [MAJOR] M4. 트리비얼 패스트트랙이 이번 결함 부류를 두 검사 모두 없이 통과시킨다

**무엇이 빠졌나.** 계획은 G1(T1)·G2(T2)에만 검사를 건다. 패스트트랙 경로는 언급조차 없다.

**근거**(확인).
- `commands:215` — «신규 파일 0 + 비구조 diff(문구·**토큰 값**·이미지 교체)일 때 후보가 된다.»
  이번 결함의 수정 대상은 정확히 «`.rpe-scroll`의 `padding` 값 한 줄»이다 — 신규 파일 0 · 토큰 값 diff.
- `commands:220` — 공통 절차 ③은 `backstop.py … --diff-base` + `manage.py check` 뿐이고
  «**별도 G2·미커밋 합치기는 없다**». 즉 `check_clip_clearance.py`가 도는 자리가 없다.
  G1도 없으므로 `check_token_disposition.py`도 안 돈다.
- 결과: 패스트트랙으로 `padding`을 줄이거나 `overflow`를 `hidden`으로 바꾸면 **절단이 두 검사를
  모두 우회한다.** 수리 B의 목적(«구현이 스스로 만든 절단»)이 정확히 이 경로에서 샌다.

**수정 방향.** `:220` ③에 «시안 대상 패스트트랙이 CSS를 건드렸으면 `check_clip_clearance.py <web 루트>`
도 함께 돌리고 결과를 ④ 보고에 넣는다»를 추가하거나, 범위 밖으로 둘 근거를 계획에 명시한다
(검사기가 브라우저·산출물을 안 쓰므로 비용은 1회 실행이다).

---

### [MAJOR] M5. 행동 시험의 «사본» 절차가 규정되지 않았다 — B-1은 동어반복이 될 수 있다

**무엇이 빠졌나.** B-1은 «A8 명세를 사본에서 고정 헤더로 변환한 표본»으로 돌린다고만 쓴다(138-139행).
**어디에 사본을 두는지 · 누가 변환하는지 · 변환이 값 보존인지**가 없다. B-3도 «`.rpe-scroll`에
`padding: 3px 3px 4px`를 넣은 사본»이라고만 쓰고 사본 범위(파일 1개인지 `web/` 트리 전체인지)가 없다.

**근거**(추론 + 확인).
- 확인: A8 원본은 읽기 전용이 지침이고([[a8-final-testbed]]) «분석·행동 시험은 A8 사본(scratchpad
  복제)에서만» 한다. 계획은 그 위치를 안 적었다.
- 확인: 변환이 위험한 이유가 실측으로 드러났다 — 원본 명세에는 미처분 1건(`--safe-top`)과
  중복 처분 2건(`--fw-regular`·`--fw-semibold`)이 **들어 있다**(B4 참조). 검사기를 쓴 사람이 손으로
  표를 다시 조판하면 그 3건은 «정리»되며 사라지고, B-1은 자기가 만든 입력으로 자기 검사기를
  통과시키는 시험이 된다.
- 확인: B-2/B-3의 대상은 실재한다 — `web/static/css/related_persons.css:393 .rpe-scroll` ·
  `web/related_persons/related_person_editor/section/related_person_editor_step.html:56`에
  `class="rpe-scroll"` · `web/design_system/foundation/tokens.css:193 --focus-ring: 0 0 0 3px rgba(208,114,122,.30)`.
  «클리핑 34건»도 개연적이다(내 계수: 정규식 일치 선언 **36건** — 규칙 단위면 34에 수렴).

**수정 방향.** B-1에 ① 사본 경로(scratchpad 절대 경로) ② «변환은 **전사만** — 토큰 문자열·채택/기각
소속·개수를 바꾸지 않는다(diff로 증명)» ③ 변환 전후 토큰 집합 해시 대조 1줄을 넣는다.
B-3은 «`web/` 트리 전체 복제 후 CSS 1줄 수정»으로 범위를 못박는다.

---

### [MAJOR] M6. T1c 값 대조에 축 교차 오탐 규칙이 없다

**무엇이 빠졌나.** T1c는 «기각한 토큰의 **값**이 시안 인라인 선언에 나타나면 발견»이다(43-51행).
제외 규칙은 «비변별 값 9종»뿐이고, **어느 CSS 속성에 나타났는지를 보지 않는다.**

**근거**(확인). A8 실빌드에서 실제로 걸린 것 —
`--fs-label`(typography, 14px) ↔ `gap: …14px…` 4건 · `--fs-display-2`(typography, 28px) ↔ `padding: …28px…` 1건.
«이 폰트 크기 토큰을 기각했는데 시안이 그 값을 쓴다»는 **거짓 명제**다 — 시안이 쓴 것은 간격이다.
길이 축(spacing·borderRadius)끼리도 같은 충돌이 가능하다(`--radius-xs` 8px ↔ `padding: 8px`).

**수정 방향.** 둘 중 하나를 계획이 **선택해서 못박는다** — ⓐ 토큰 축 ↔ CSS 속성군 매핑을 두고
같은 군에서만 대조(typography→`font-size`/`line-height`/`letter-spacing`, spacing→`margin`/`padding`/`gap`,
borderRadius→`border-radius`, shadows→`box-shadow`, colors→색 속성), ⓑ 축 무관 대조를 유지하되
**교차 일치는 `[warn]` 인벤토리**로 내리고 동일 축 일치만 FINDING. 어느 쪽이든 픽스처
(«기각 typography 14px + 시안 `gap: 14px`» 케이스)를 추가한다.

---

### [MINOR] m1. `--spec-only` 가 단일 모드 검사기에서 의미 없는 플래그다

T1의 검사기는 모드가 하나뿐인데 `--spec-only`를 받는다(26행). 선례에서 이 플래그는 **두 모드를
가르는 스위치**다 — `check_motion_spec.py:305-316`은 `--spec-only`(G1) ↔ 3번째 인자 `<web-root>`(G2)를
가른다. 토큰 검사에는 G2 모드가 없으므로 지금은 «미리 만든 확장 지점»(원칙 05)이다.
→ 빼거나, 남긴다면 «선례 판형 일치를 위해 남긴다»를 계획에 1줄로 남긴다.

### [MINOR] m2. `:168` 삽입 위치가 «이 단계를 생략한다»와 결속될 수 있다

`commands:168`은 한 줄(1957자) 안에 ① `server-contract.json` 절단(«openapi 동결본이 있을 때»)
② «동결본이 없으면 … **이 단계를 생략한다**» ③ «같은 시점 — 모션 처분 표 기계 점검»이 이 순서로
들어 있다. 계획은 «③ 옆에»라고만 적어 앞/뒤가 불명이다. ②보다 앞에 끼우면 openapi 없는
정적 시안 빌드에서 토큰 점검까지 생략되는 독해가 생긴다. → «③ 뒤에 별도 문장으로» 로 못박는다.

### [MINOR] m3. G2 «해당 없음» 1줄 규정이 없다

T3의 `:187` 행은 «발견 0이면 «절단 여유: 발견 0» 1줄»까지 규정했지만, 검사를 **돌리지 않는 경우**
(시안 없음·`web/` 부재 등)의 1줄이 없다. 선례는 있다 — `:187` «`has_motion_notes`가 false면
«모션 처분 대조: 해당 없음(관찰 채널 부재)» 1줄». → 대칭 문장을 추가한다.

### [MINOR] m4. `docs/DEVELOPMENT.md` §1의 web 블록은 스크립트를 1개만 싣는다

T4는 «§1 파일 지도에 새 스크립트 2종 행 추가»라고 쓰지만, 현재 §1의 `dddjango-web/` 블록은
`└── scripts/refreeze.py` **한 줄**만 싣는다(:25 — `backstop.py`·`check_motion_spec.py`·
`compare_render_audit.py`는 없다). 2종만 추가하면 «왜 이 둘만 있나»가 생긴다.
→ 블록 전체를 «scripts/ 검사·도구 N종(대표 3)» 형태로 고치든지, 추가 기준을 1줄로 남긴다.

### [MINOR] m5. `make release-web` 의 선행 조건이 계획에 없다

`Makefile:305` — `release-web: verify-web-browser _release`. 그 타깃은
`DDDJANGO_WEB_PLAYWRIGHT_MODULE` 과 (`DDDJANGO_WEB_BROWSER_CHANNEL`|`…_CDP`) **둘 다** env로 요구하고,
없으면 `ERROR:` + exit 1이다(`Makefile:125-126`). 실측 소요 ≈19분([[web-repair-runtime-notes]]).
계획 6절은 «`make release-web`»만 적는다. → env·소요·클린 트리 요구를 순서 절에 적어 둔다.

### [MINOR] m6. 재동결 직후 G1에서 새 검사가 반드시 발동하는 상호작용이 없다

`refreeze.py:32-37`의 폐기 집합에 `design-tokens.json`이 있고 `FIXED_DISCARD_TREES=('design-ref',)`다 —
재동결은 풀을 **다시 뽑는다**. `design-spec.md`는 폐기 대상이 아니므로, 재동결로 풀이 바뀌면
기존 처분 표가 그대로 남아 T1a가 반드시 발견을 낸다(의도된 동작이지만 **architect 재작업이
재동결의 부수 비용으로 붙는다**). 설계 §5 W3은 «다음 G1부터 적용»만 적고 이 상호작용은 없다.
→ 계획에 1줄로 예고하거나, 최소한 배너 문면에서 이 발견의 성격을 구분하게 한다.

### [MINOR] m7. `design-review-web ⓑ` 에 «기계 선검 — 재검 금지» 위임이 빠졌다

T3은 `:45 ⓑ`에 «기각 정당성 리뷰 항목 1구»만 더한다. 그런데 같은 줄 ⓓ에는 선례 문장이 있다 —
«**전수성·판형 자체는 `check_motion_spec --spec-only`가 기계 선검한다 — 재검하지 말고 너는 처분의
의미 타당성을 본다**». ⓑ의 «전수 채택 또는 기각했는가(빈칸 0)»는 이제 기계가 보는 것이므로,
같은 위임 문장이 없으면 리뷰어가 기계와 중복 노동을 하고 «기각 사유의 사실성»이라는 사람 몫이
묻힌다. → ⓑ에도 위임 1구를 넣는다.

---

## 확인했고 문제 없던 것 (계획의 «안 건드린다» 선언 검증)

- **봉인 재발행 불요 — 성립한다**(확인). `manifest_seal.py:51-175`의 봉인 글롭 어디에도
  `dddjango-web/**`·`codex-dddjango-web/**` 가 없다(`dddjango/`·`codex-dddjango/`·`ontology/`·
  `workspace/**`·`Makefile`·두 marketplace.json 뿐). `source_script_tree()`/`mirror_parity()`의
  `MIRROR`도 `("dddjango/scripts", "codex-dddjango/skills/dddjango/scripts")` 고정(:190)이라
  web 스크립트 추가가 `script_trees`를 흔들지 않는다. `release-web`이 고치는 파일은
  `dddjango-web/.claude-plugin/plugin.json` · `codex-dddjango-web/.codex-plugin/plugin.json`
  둘뿐이고(`Makefile:303-304`) 둘 다 봉인 밖이다. `Makefile` 무편집도 유지된다.
- **픽스처 글롭 자동 수집 — 성립한다**(확인). `run_fixtures.sh:10` `for fx in "$HERE"/fixtures_*.sh`.
  실행 권한도 불요(`bash "$fx"`). 단 Codex 미러 의무는 별개다 → B1.
- **`audit_version` 불변 · 재동결 폐기 집합 · `backstop.py` 마커 — 건드릴 필요 없다**(확인).
  새 산출물이 0이고, `backstop.py:32 TOTAL_CHECKS = 26`은 인프로세스 검사 계수라 외부 스크립트
  추가와 무관하다. (여담: `AGENTS.md`는 «검사 24종»이라 적어 실제 26과 어긋나 있다 — 이번 범위 밖.)
- **온톨로지 계열 검증과 무관하다**(확인). `spec_lint.py`·`checker_lint.py`·`corpus_mirror_sync.py`·
  `tree_mirror_check.py` 어디에도 `dddjango-web` 문자열이 없다. `request_guide_contract.py`가 web을
  보지만 REQUEST_GUIDE·매니페스트·marketplace만 검사한다(스크립트 목록 없음).
- **설계 §1~§5 → 계획 대조**: §1 검사 3종·앵커·exit·`[warn]`, §2 4단계·비차단 지위·1단 include 한계,
  §3 기각 항목(할 일 없음), §4 규범 7행 중 6행, §5 W1/W2/미착수 2건 — 모두 태스크로 내려와 있다.
  누락은 §4의 «빌드 스펙 정본»(M3, 설계에도 없음)과 §1의 «architect 의무 = 형식 고정»(B2)이다.
- 시안 대조 대상 실재 확인: `design-ref/관계인.dc.html`의 `padding: 2px 2px 4px` · `padding: 2px 4px 0`,
  `--space-1: 2px` 기각 — 본 결함의 T1c 경로는 실제로 성립한다.

도구 메모: 이 워크트리에 `.serena/project.yml`·`graphify-out/` 표식이 없어 Serena·Graphify는 사용하지 않았다(전역 지침의 opt-in 조건).
