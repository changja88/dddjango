# 계획 적대 검토 (2026-09-15)

대상: `workspace/plan/2026-09-15-web-refreeze-full-rebuild.md`
기준: `workspace/design/2026-09-15-web-refreeze-full-rebuild.md`(v5) · `Makefile` · `docs/DEVELOPMENT.md` · `dddjango-web/scripts/**`
관점: 계획이 설계를 빠짐없이 옮겼는가 · 실행 가능한가. 설계 결정의 옳고 그름은 범위 밖.
도구: Serena·Graphify 모두 워크트리 opt-in 표식 부재(`.serena/project.yml`·`graphify-out/graph.json` 없음) — 기본 검색·읽기 도구로 수행.

## 판정

**실행 진입 불가 (BLOCKER 3 · MAJOR 10 · MINOR 8)**

세 BLOCKER는 모두 «Task 경계»의 문제다 — 계획이 설계를 옮기지 못한 곳(§4.4)이 하나,
Task가 자기 힘으로 만들 수 없는 green을 합격 조건으로 내건 곳이 둘이다. 후자는 이번 판형의
핵심 장치(계약 검사가 열거를 대체)를 **Task 단위로 쪼개면서 검사 단위는 쪼개지 않아** 생겼다.

## 설계 커버리지 대조

| 설계 규정 | 계획 매핑 | 판정 |
|---|---|---|
| §1 정의 ①~④·전량 재실행(design:26-31) | plan:130 T6 S2 | ○ |
| §1 `design_status` ready 유지 · `commands:144` 대체(design:32-35) | plan:131 T6 S3 | ○ |
| §2.1 3겹 포인터 폐기 집합(design:46-55) | plan:58 T1 S1 | ○ |
| §2.1 고정 폐기·교체 대상 목록(design:57-60) | 없음 — T1 S3(plan:60)은 §4.1·§4.2·§4.6만 인용 | △ M-6 |
| §2.2 고아 journal 기록·미폐기(design:68) | plan:58 T1 S1 | ○ |
| §2.2 G0 배너·종료 보고 «k건 지우지 않음» 1줄(design:69) | 없음 | △ m-6 |
| §3-1 begin이 scope 복사·sha 기록(design:85) | plan:58(§4.2 journal 필드)로 간접 | △ |
| §3-2 규범 문장 `<대상 폴더>` 수식(design:86-88) | plan:132 T6 S4 + §8-D3 | ○ |
| §3-3 staging 창 live `scope.md` 쓰기 금지(design:89-90) | plan:130 T6 S2(«§3» 포괄) | ○ |
| §3-4 commit의 live scope sha 대조 → exit 1(design:91-92) | 없음(시험·구현 지시 모두) | △ M-4 |
| §3-5·6 교체·검토 순서(design:93-96) | plan:130 T6 S2 | ○ |
| §4.1 4 서브커맨드·인자·exit(design:102-110) | plan:60 T1 S3 · plan:64 합격 | ○ |
| §4.1 `check --render-audit-skipped`가 유일 주체(design:112-113) | plan:60 «§4.1 인자» 포괄 — 시험 목록(plan:58)엔 없음 | △ |
| §4.2 journal 스키마(design:117-129) | plan:58·60 | ○ |
| §4.3 치환 규칙 + 제외 ①②(design:136-146) | plan:132 T6 S4 · plan:145 T7 S1 | ○ |
| §4.3 `<대상 폴더>` 정의를 «산출물 위치» 절에(design:147) | plan:129 T6 S1 | ○ |
| §4.3 begin이 staging에 복사하는 입력(design:159-161) | 없음(§4.2 `copied_inputs` 필드로만) | △ |
| **§4.4 `check`의 검사 내용(design:163-169)** | **없음** | **✗ BL-3** |
| §4.5 입력 게이트 — staging을 `--build`로(design:171-177) | plan:130 «§4(절차)» + §8-D1 | ○ |
| §4.6-1 planned·sha 대조(design:183-184) | 없음 | △ M-4 |
| §4.6-2·3 discarded·installed(design:185-191) | plan:58 T1 S1 | ○ |
| §4.6-4 verified 실패 되감기(design:192-194) | plan:58 T1 S1 | ○ |
| §4.6-5 done 순서(design:195-197) | 없음(«phase 전이» 포괄) | △ M-4 |
| **§5 이미지 축 — 병행 실행 금지(design:199-207)** | plan:20이 abort 되감기만 · T6 S2 열거에 §5 없음 | **✗ M-1** |
| **R6 `interaction_exclusions` 이월(design:211-215)** | **없음** — T6 S2 열거는 R7·R8·R9뿐 | **✗ M-2** |
| R7 상태 전이·G0 G2 배너(design:217-235) | plan:60 T1 S3 · plan:130 T6 S2 | ○ |
| R8 defer에서 재동결 제거(design:237-242) | plan:89 T3 S3 · plan:130 T6 · plan:147 T7 S3 | ○(순서는 BL-1) |
| R9 hook·backstop 감지(design:246-250) | plan:87 T3 S1 · plan:101 T4 S1 | △ `_prev-*` 누락 M-5 |
| R9 규범 — `commands:171` ⑤ 커밋 전 확인(design:251) | plan:130 포괄 · 편집 위치 미지명 | △ m-5 |
| §7 제거 대상 표(design:255-265) | plan:113 T5 · plan:127 T6 · plan:143 T7 | △ BL-2 · M-6 |
| §8 A·B·C·D1~D4(design:272-280) | plan:68-77 T2 | ○(green 시점은 BL-1) |
| §9 남는 우회(design:284-298) | 작업 아님 — 반영 불요 | ○ |
| §10 B1~B10(design:302-315) | plan:157-171 T8 | △ M-9 · M-10 |

## BLOCKER

### BL-1. 계약 검사 A·B가 Task 경계를 가로지르는데 중간 Task가 단독 green을 합격 조건으로 건다

이번 판형의 전제는 «검사기가 열거를 대체한다»인데, 검사 단위(문서 4곳·잔존 0)가 Task 단위
(스크립트/규범/reference)와 어긋난다. 세 곳에서 **달성 불가능한 합격 조건**이 된다.

**ⓐ Task 3 합격 «계약 검사 A green»(plan:93) — 불가능.**
A는 4곳을 본다(design:274): hook 스크립트 · `REQUEST_GUIDE` · `commands` · Codex `SKILL.md`.
실측 잔존 위치는 넷 다 살아 있다:
- `dddjango-web/scripts/evidence_debt_hook.py:35-39` `DECISION_LINE` — `ⓑ defer = non-implementation runs only (refreeze, inspection, reporting)`
- `dddjango-web/REQUEST_GUIDE.md:116` — «유보는 재동결·조회·보고와 완료 빌드의 마무리만 허용하며»
- `dddjango-web/commands/dddjango-web.md:129` — «**ⓑ defer가 허용하는 것** = 재동결…»
- `codex-dddjango-web/skills/dddjango-web/SKILL.md:151`(같은 절의 Codex 미러)

Task 3 Files(plan:85)는 hook 스크립트 2 + 시험 2 + 미러 4뿐이다. `REQUEST_GUIDE.md`는
Task 7 Step 3(plan:147), `commands:129`와 Codex `SKILL.md`는 Task 6(plan:130·133) 소관이다.
→ Task 3 끝에 A는 **반드시 red**다. 계획대로면 실행자는 ⓐ red를 green이라 적거나 ⓑ Task 3에서
멈춘다. (질문 ⓑ의 재현 — 다만 충돌은 `commands:129` 하나가 아니라 `REQUEST_GUIDE.md`를 포함한
3-way다.)

**ⓑ Task 6 합격 «계약 검사 A·D1~D4 green»(plan:137) — A는 여전히 불가능.**
Task 6 Files(plan:127)는 `commands` + Codex `SKILL.md`뿐이고 `REQUEST_GUIDE.md`는 없다.
A가 처음 green이 될 수 있는 시점은 Task 7 Step 3 이후다. 즉 **A가 두 Task에서 거짓 합격
조건으로 쓰인다.**

**ⓒ Task 5 합격 «계약 검사 B green»(plan:118) — 불가능.**
B는 `--compare-build`·`refreeze-diff`·`carried_from` **잔존 0**(design:275)이다. Task 5
Files(plan:113)는 `archive_design.py`·`check_design_evidence.py`·`test_design_archive.py`
+ 미러 3뿐이다. 규범 쪽 실측 잔존:
- `dddjango-web/commands/dddjango-web.md:70` · `:137` · `:146`
- `dddjango-web/skills/implementation-ui/references/design-acquisition.md:46,53,58,59,62,63,64,67,69,72,78`
- `dddjango-web/skills/implementation-ui/references/design-evidence.md:27,115,336,338,342,343`
- `dddjango-web/agents/design-review-web.md:25`
- 위 전부의 Codex 미러
전부 Task 6·7 소관이다.

### BL-2. `test_interaction_evidence.py`가 Task 5 Files에 없다 — Task 5 이후 `make verify-web`이 red

`dddjango-web/scripts/test/test_interaction_evidence.py:626`
`test_manifest_row_accepts_carried_from_only`이 이렇게 단언한다:

```
expected = 0 if (field, value) == ('carried_from', '4' * 64) else 2
```

즉 «정상 sha의 `carried_from`은 exit 0, 미지 필드는 exit 2». Task 5 Step 3(plan:117)이
`check_design_evidence.py:1142-1143`의 `carried_from` 수용을 제거하면 이 단언이 exit 2로
깨진다. 이 시험은 상시 검증 경로에 있다:
`dddjango-web/scripts/test/fixtures_interactions.sh:9` → `run_fixtures.sh:10` → `Makefile:94`(verify-web).

Task 5 Files(plan:113)와 설계 §7 표(design:255-265) **둘 다** 이 파일과 그 Codex 미러
(`codex-dddjango-web/skills/dddjango-web/scripts/test/test_interaction_evidence.py:626`)를
누락했다. Task 5 합격 «남은 시험 전건 green»(plan:121)이 그대로는 성립하지 않는다.

### BL-3. 설계 §4.4(`check`가 무엇을 검사하는가)가 계획 어디에도 매핑되지 않는다

설계 §4.4(design:163-169)는 `check`의 검사 내용을 규정한다 — staging 실재 7종
(`design-ref/`·`source-manifest.json`·`design-tokens.json`·`asset-manifest.json`·
`screen-meta.json`·`design-input.json`·`render-audit.json` 조건부) + `design-input.json`의
3겹 포인터 해소 + archive 원본이면 case마다 v2 관찰 실재 + **폐기 집합 자기 검사**
(3겹 포인터 ⊆ `discard_set`).

Task 1 Step 1 시험 목록(plan:58)과 Step 3 구현 지시(plan:60)는 §4.1·§4.2·§4.6만 인용한다.
§4.1은 `check`의 **인자와 exit만** 정의한다(design:105). 따라서 `check`가 무엇을 검사하는지가
계획에 없다. `check`는 §4.5 입력 게이트의 선행 조건이자 B1(plan:159)의 합격 축이므로,
§4.4 없이 구현되면 B1·B8이 무의미해진다.

## MAJOR

### M-1. 설계 §5의 «병행 실행 금지»가 규범 편집 지시에 없다

design:207 «재동결 중 같은 프로젝트의 **병행 실행을 금지한다**»는 런타임 규범 문장인데,
Task 6 Step 2의 재작성 범위 열거(plan:130)는 «설계 §1·§2·§3·§4(절차)·R7·R8·R9»로 **§5를
뺐다**. Global Constraints(plan:20)는 도구 동작(abort·verified 실패의 이미지 차집합 되돌리기)만
옮겼고 금지 규범은 아니다. §5의 근거(design:203-205 — 이미지 추가가 완료 빌드의
`implementation_digest`를 stale로 만들어 다른 작업의 backstop이 BLOCKER를 낸다)가 그대로
남아 있으므로, 금지 문장 없이 배포하면 설계가 막으려던 상태가 그대로 가능하다.

### M-2. R6(`interaction_exclusions` 이월)의 Coordinator 절차가 어느 Step에도 없다

design:211-215는 재수집 후 Coordinator가 **새 관찰 문서의 target id 기준으로 행을 다시 짓고**
(`approval_quote`·`scope_ref`는 staging `scope.md`에서 재사용, 단위 키만 새 id에 맞춤),
**10% 상한을 새 분모로 재검증**하고, **대응 단위를 못 찾은 행은 버리지 않고 배너에 올린다**고
규정한다. Task 6 Step 2의 열거(plan:130)에 **R6이 없다**. journal 필드
(`interaction_exclusions`)만 §4.2를 통해 Task 1에 들어가고, 행 재작성 절차는 어디에도 없다.
B6(plan:164)이 시험만 하고 구현 지시가 없는 구조다. 계획의 결정 표(plan:189)가 R6을 «기본값»
으로 언급하는 것이 이 누락을 가린다.

### M-3. 새 단위 시험 `test_refreeze.py`가 어떤 픽스처에도 배선되지 않는다

`Makefile:94`의 verify-web은 `run_fixtures.sh`만 돌고, 그것은 `fixtures_*.sh` 글롭만
실행한다(`dddjango-web/scripts/test/run_fixtures.sh:10`). 기존 파이썬 시험은 전부 대응
`fixtures_*.sh`를 가진다 — `fixtures_design_evidence.sh:5`(test_design_archive) ·
`fixtures_evidence_debt.sh:6-7` · `fixtures_interactions.sh:9`.

Task 1 Files(plan:56)는 `refreeze.py`·`test/test_refreeze.py` + «미러 2»뿐이고,
Task 7 Step 5의 배선(plan:149)은 계약 검사만 Makefile에 붙인다. → `refreeze.py`의 회귀 그물이
상시 검증에서 영구히 빠진다. `fixtures_refreeze.sh`를 더하면 미러도 2가 아니라 3이다.

### M-4. §4.6-1·-5와 §3-4에 시험·구현 지시가 없다

Task 1 Step 1(plan:58)이 명시하는 commit 시험은 «§4.6-2·3의 네 경우»뿐이다. 빠진 것:
- **§4.6-1 / §3-4**(design:183-184·91-92): planned 단계의 live `scope.md` sha 대조 → 불일치면 exit 1.
  설계가 «금지가 없으면 staging 창에 live에 적힌 줄이 commit의 덮어쓰기로 red 없이 증발한다»
  (design:89-90)고 든 유일한 기계 방어다.
- **§4.6-5**(design:195-197): done의 순서 — `build-state.json` 키 갱신 → journal `completed_at`
  기록 → staging 삭제 → `_prev-<ts>` 삭제. 설계가 이 순서를 «`_prev`가 먼저 사라져 abort가
  성공한 재동결을 파괴하는 창»을 없애는 근거로 든다. 순서 시험이 없으면 B7(plan:163)이
  우연히 통과할 수 있다.

Step 3(plan:60)의 «§4.6 swap-plan phase 전이»는 이 둘을 포괄한다고 읽을 수 있으나, Step 1이
시험 목록을 명시적으로 열거하는 판형이라 열거 밖은 시험이 생기지 않는다.

### M-5. R9의 `_prev-*` 감지가 Task 3·4 Step에 없다 — 계획 안에서 자기모순

설계 R9(design:246-247)는 «빌드 폴더에 `_refreeze-*`**/`_prev-*`**가 있으면»으로 양쪽을
요구한다. 그런데:
- Task 3 Step 1(plan:87): «빌드 폴더에 `_refreeze-*`가 있으면»
- Task 4 Step 1(plan:101): «빌드 폴더에 `_refreeze-<ts>/`가 있으면»
- 계획의 파일 구조 표(plan:31): backstop = «잔존 `_refreeze-*`/`_prev-*` 감지»

표와 Step이 어긋난다. 실무상 중요한 차이다 — `commit`이 `installed` 완료 직후 중단되면
staging은 비어 삭제됐을 수 있고 `_prev-<ts>`만 남는다. `_refreeze-*`만 보는 감지는 그 상태를
놓친다. 현행 코드에 `_prev`·`_refreeze` 문자열은 0건(`backstop.py`·`evidence_debt*.py` 실측).

### M-6. `commands:70`의 build-state `refreeze` 키가 어느 Task Files에도 지목되지 않고, Task 6은 B를 green 조건에서 뺐다

`dddjango-web/commands/dddjango-web.md:70`:
```
"refreeze": {"diff": "refreeze-diff.json", "sha256": "<재동결 대조를 실행했을 때만 — …>"},
```
(Codex 미러 `codex-dddjango-web/skills/dddjango-web/SKILL.md:123`도 동일.)

설계 §2.1(design:60)은 `refreeze-diff.json`을 «생성 도구가 사라지므로» 고정 폐기 대상으로
두었고 §8-B가 잔존 0을 요구한다. 그런데 Task 6 Step 1~4(plan:129-132)의 어느 지시도 이
build-state 스키마 키를 가리키지 않고, **Task 6 Step 6(plan:134)의 green 조건은 «A·D1~D4»로
B를 뺐다**. D1은 «자리표시자 + 폐기 대상 이름 인접»만 보므로 이 줄을 잡지 못한다.

결과: 이 잔존은 Task 7 Step 6의 `make verify-web`(plan:150)에서야 드러나는데, 그때 고쳐야 할
파일(`commands` + Codex `SKILL.md`)은 **Task 7 Files(plan:143) 밖**이다. 설계 §7 표의
commands 행(design:260)도 이 키를 열거하지 않았다 — v3·v4를 깨뜨린 «손으로 만든 편집 목록이
샌다»가 여기서 한 번 더 재현된다.

### M-7. `make release-web`이 클린 worktree를 요구한다 — 계획의 Global Constraint와 정면 충돌

`Makefile:328-331`:
```
if [[ -n "$$(git status --porcelain)" ]]; then … die "worktree dirty — 커밋/스태시 후 진행"; fi
```
(DRY=1이 아닌 실제 릴리즈에서.)

계획 머리말(plan:3)은 «커밋·스태시·브랜치 전환으로 사용자 미커밋 변경(`docs/master.html`·
`workspace/eval/field-report-4/…lanes.md`)을 수용하지 않는다»를 못박는다. 현재 작업 트리에는
그 둘과 `workspace/eval/web-refreeze-completeness/diagnosis.md`가 미커밋 상태다.
→ Task 8 Step 11(plan:169)의 `make release-web`이 그 자리에서 die한다. 계획은 이 충돌을
인지하지 않는다.

### M-8. 계획 머리말이 릴리즈를 지시하면서 동시에 권한 밖이라 선언한다

plan:3 같은 문단 안에서:
- «… → `make verify` → 사용자 승인 뒤 커밋·`make release-web`.»
- «**릴리즈·A8 앱 수정은 이 계획의 실행 권한 밖이다.**»

Task 8 Step 11(plan:169)은 «승인 후 커밋 1회 → 봉인 재발행(별도 chore 커밋) → `make release-web`»
으로 릴리즈를 지시한다. 실행자는 릴리즈를 해야 하는지 판단할 근거가 없다.

### M-9. B3·B4의 주입 방법이 없다 — Task 1이 그 수단을 만들지도 않는다

- **B3**(plan:161 · design:306): «`commit`을 `discarded`에서 강제 중단». Task 1의 `refreeze.py`
  명세(plan:54-64)에 중단을 만들 수단이 **하나도 없다** — env 스위치도, `--stop-after <phase>`
  같은 인자도, 시험 훅도. 실행자에게 남는 길은 ⓐ SIGKILL 타이밍 맞히기(비결정적) ⓑ
  `_prev-<ts>/swap-plan.json`을 손으로 조작해 중간 상태를 합성하기인데, 계획은 둘 중
  어느 것도 지시하지 않는다. B3은 «중간 상태에서 hook·backstop 발화»까지 관찰을 요구하므로
  그 중간 상태를 **재현 가능하게** 만드는 방법이 반드시 필요하다.
- **B4**(plan:162 · design:307): «`installed` 이름 충돌 주입». 충돌을 어떻게 성립시키는가
  — `discarded`가 옮기지 않은 live 파일과 staging 산출물의 경로를 어떻게 겹치게 하는가 —
  가 적혀 있지 않다. 설계가 이 시험을 둔 이유(livelock, design:189-191)를 재현하려면
  «staging 쪽 있음 + live 쪽에도 있음»이 실제로 성립해야 한다.
- **B9**(plan:165)만 설계 §10(design:312)의 «`commands`의 인자 줄 하나를 `<산출물 폴더>`로
  되돌린다»로 구체적이다. 되돌린 뒤 복원하라는 지시는 없으나 Step 8의 `make verify`가 잡는다.

### M-10. B1·B2의 실행 주체·전제 조건이 없다

**B1**(plan:159) «A8 사본에서 재동결 완주»는 스크립트가 아니라 **규범(Coordinator 프롬프트)
절차**다 — 사람 또는 에이전트가 새로 쓴 `commands/dddjango-web.md` 본문을 읽고 12 case를
드라이버로 다시 돌려야 한다. 계획에 없는 것:
- 누가·어떤 세션으로 도는가(별도 `/dddjango-web` 세션? 서브에이전트? 실행자 직접?)
- scratchpad 사본이 Django 프로젝트 루트로 성립하는가 — §5가 `<ROOT>/web/static/images/`에
  쓰므로(`fetch_images.py:35,110` 인용, design:201) 사본에 그 트리가 필요하다
- `DDDJANGO_WEB_PLAYWRIGHT_MODULE` + (`DDDJANGO_WEB_BROWSER_CHANNEL` 또는 `_CDP`) env
  (`docs/DEVELOPMENT.md:135`) — 없으면 드라이버가 돌지 않는다
- 비용 — 설계 §9-3(design:286)이 «A8 12 case 기준 수십 분»이라 적었다

**B2**(plan:160 · design:305)의 «드라이버 3번째 case에서 env를 부재 경로로 치환»도 그 시점을
어떻게 잡는지(호출 사이에 바꾸는가) 적혀 있지 않다.

## MINOR

- **m-1** Task 5 합격 «`--compare-build` 참조 0»(plan:121)의 **범위가 무정의**다. 저장소 전체면
  Task 6·7 전까지 불가능(BL-1ⓒ와 같은 문제), 스크립트 한정이면 그렇게 적혀 있지 않다.
- **m-2** `docs/DEVELOPMENT.md` 갱신이 «§1 지도에 신규 2파일 행 추가»(plan:149) 한 줄뿐이다.
  선례는 더 두껍다 — `web_hooks_contract.py`는 §1 지도(`docs/DEVELOPMENT.md:36-37`)에 «이벤트·
  command·timeout을 리터럴 대조»까지 적혀 있고, `request_guide_contract.py`는 §4
  (`docs/DEVELOPMENT.md:120`)에 계약 본문이 한 문단이다. 새 계약 검사기가 «무엇을 보장하는가»를
  어디에 적을지 계획이 정하지 않는다. `dddjango-web/scripts/refreeze.py`를 §1의 dddjango-web
  블록(현재 `REQUEST_GUIDE.md`·`hooks/hooks.json` 2행만 — `docs/DEVELOPMENT.md:26-37`)에
  넣는 것이 맞는지도 미정이다.
- **m-3** `REQUEST_GUIDE.md` 편집 절차가 `docs/DEVELOPMENT.md:69-77`에 성문화돼 있다 —
  Claude 정본 편집 → byte 복사 → `cmp` → `request_guide_contract.py --self-test` →
  본 검사 → `reverse_coverage.py`. Task 7은 `cmp`(Step 4)와 `make verify-web`(Step 6)만 든다.
  verify-web은 web pair에 `--self-test`를 돌리지 않는다(`Makefile:105-106` ·
  `docs/DEVELOPMENT.md:120` «`verify-web`은 web pair 비교 → 실제 계약»).
- **m-4** Codex 역할 SKILL(`codex-dddjango-web/skills/dddjango-web-design-review-web/SKILL.md:28`)은
  **기계 대조가 없는 의미 미러**다(verify-web의 byte 대조 대상은 `scripts`·`assets`·references 4종·
  `REQUEST_GUIDE` — `Makefile:95-104`). Task 6 Step 5(plan:133)는 «같은 턴에서» 장치를 뒀는데
  Task 7은 Files(plan:143)에 이름만 있고 같은 장치가 없다.
- **m-5** `commands:171` ⑤(설계 R9의 «Phase 2 진입 준비 ⑤ 커밋 전 잔존 없음 확인» —
  design:251)가 편집 위치로 지명되지 않았다. Task 6 Step 3은 `:144`·`:227`만 지명한다(plan:131).
- **m-6** §2.2의 «G0 배너와 종료 보고에 미참조 `captures/` 파일 k건 1줄»(design:69)이 Step
  문면에 없다 — Task 6 Step 2(plan:130)는 결과 보고를 «무엇을 다시 동결했는가 목록 + exit»으로만
  규정한다. B1·B10(plan:159·164)이 배너를 합격 조건에 두므로 **시험은 있고 지시가 없다**.
- **m-7** `make release-web`은 `_release` 전에 `verify-web-browser`를 돈다(`Makefile:302` ·
  `docs/DEVELOPMENT.md:147`) — env 없으면 그 자리에서 막힌다. Task 8 Step 11에 이 전제가 없다.
- **m-8** 사용자 상시 지침인 조감도 HTML 갱신이 계획에 없다.
  `workspace/design/ontology-adoption-map.html`이 dddjango-web을 9곳에서 언급한다.

## 확인했으나 문제 없음

- **봉인 순서** — `Makefile`은 봉인 대상이다(`workspace/tools/manifest_seal.py:143`, protocol 군).
  Task 8 Step 11(plan:169)의 «커밋 1회 → 봉인 재발행(별도 chore 커밋) → release»가
  `docs/DEVELOPMENT.md:149`(«봉인 대상 파일을 바꾼 커밋 **뒤에** 별도 chore 커밋»)와 정확히
  일치한다. 신규 `workspace/tools/web_refreeze_contract.py`는 봉인 글롭 밖이므로
  (`manifest_seal.py:117-186` — 선례 `web_hooks_contract.py`도 밖) 등재 불요.
- **Codex `/hooks` 재신뢰 고지** — `docs/DEVELOPMENT.md:151`은 «`hooks/hooks.json`이 바뀐
  릴리즈(command 문자열·이벤트·timeout — **스크립트 본문만 바뀐 경우는 해당 없음**)»로 한정한다.
  계획은 `evidence_debt_hook.py` 본문만 바꾸고 `hooks.json`은 건드리지 않으므로 릴리즈 노트
  1줄이 **불필요하다** — 계획에 없는 것이 옳다.
- **릴리즈 버전** — 현재 `dddjango-web/.claude-plugin/plugin.json:4`·
  `codex-dddjango-web/.codex-plugin/plugin.json:3`이 `1.1.14`이므로 patch = v1.1.15(plan:190)가 맞다.
- **온톨로지 루프 부재가 옳다** — dddjango-web은 코퍼스 밖(AGENTS.md)이고 `ontology/LEDGER.tsv`에
  dddjango-web 행 0건. `ISSUED` 채번·`ontology_render.py --apply`·LEDGER 재기준선이 계획에
  없는 것이 정상이다.
- **문서 파급 없음** — `docs/*.html`·`docs/*.json`·`docs/*.md`와
  `workspace/design/2026-08-23-web-presentation-layer-spec.md`에 «재동결/refreeze/compare-build»
  문자열 0건. work_flow·file_tree_web 갱신 불요.
- **`python3 -m unittest <파일경로>`**(plan:59)는 이 환경(Python 3.14.7)에서 정상 동작 — 실측 확인.
- **Task 4 Step 3의 «marker 판정을 바꾸지 않는다»가 성립한다** — `backstop.py:69-71`이
  `parts[2] in markers`로 판정하므로 `.dddjango-web/<build>/_refreeze-<ts>/design-ref`는
  parts[2]가 `_refreeze-<ts>`라 staging이 별도 빌드로 오인되지 않는다. hook 쪽도
  `evidence_debt_hook.py:109-111`이 `.dddjango-web` **top-level만** `iterdir`한다.
- **R9 «ready 게이트 밖» 요구의 근거가 실재한다** — `discarded` 창에서 `design-input.json`이
  `_prev-`로 옮겨지면 `evidence_debt.py:130-131`이 `None`을 반환해 빌드가 hook 시야에서 사라진다.
  Task 3 Step 1(plan:87)이 «`design-input.json` 없음·`design_status != ready` 두 경우 모두»를
  시험으로 못박은 것이 정확하다. 같은 창에서 `build-state.json`은 보존(§2.2)되므로
  `backstop.py:72-76`이 빌드를 계속 발견한다.
- **Task 2의 D1 정의**(plan:72)가 설계 §8-D1(design:277)과 일치 — 코드 조각 안 자리표시자 +
  폐기 대상 이름 인접, 고정 목록 + `captures` + `--build`.
- **verify-web 배선 지연 주석**(plan:79)의 논리는 맞다 — 계약 검사를 Task 7 끝에 붙이므로
  계약 검사 때문에 verify-web이 red가 되는 구간은 생기지 않는다. (질문 ⓒ: 계획이 인지한 red는
  이것 하나다. 실제로 생기는 red는 BL-2 — Task 5의 `carried_from` 제거가
  `fixtures_interactions.sh`를 깨는 것 — 이고 계획은 그것을 인지하지 않는다.)
- **결정 게이트 판형** — Task 8 Step 10(plan:168) «변경 요약 10줄»이 사용자 관례와 일치.

## 미확인

- **A8 워크트리 실물** — 읽기 전용 지시에 따라 접근하지 않았다. 고아 7건/최대 270건,
  `captures/external/*`의 `status:external`·`local_path:""`는 설계 인용(design:64-66)만 대조했다.
- **`web_refreeze_contract.py`가 실제로 쓸 만한 red 목록을 내는가** — 도구가 아직 없어
  «Task 2 Step 3의 red 목록이 Task 6·7의 지시로 충분한가»(질문 ⓐ)를 **출력으로** 검증하지
  못했다. 문면 기준 판단: D1·D3·D4는 위치를 지목하므로 치환 작업의 지시가 되고, A·B는
  파일만 지목하므로 «무엇을 쓸 것인가»(재동결 절 전면 재작성 본문)는 여전히 설계 §1~R9에서
  옮겨야 한다 — 계획도 그렇게 적었다(plan:130·145-147). 다만 B가 Task 6 green 조건에서
  빠져(M-6) 그물이 한 구간 열려 있다.
- **rv-F B-1 · rv-C N-B1 · N-B2의 실측 위치 전량** — 본 검토에서 파일:행으로 재확인한 것은
  `commands:146`(`--build <산출물 폴더>`)과 `design-acquisition.md`의 `BUILD` 자리표시자
  (`:53` 등)뿐이다. Task 2 합격 조건(plan:77)의 «포함» 판정은 rv 원문 전수 대조가 필요하다.
- **`make verify` / `make verify-web` 실제 실행** — 읽기 전용 검토라 돌리지 않았다.
  BL-2의 red는 시험 소스와 픽스처 배선의 정적 대조로 판정했다.
