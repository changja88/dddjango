# 적대 검토 D — 기존 체계 정합 (설계 `2026-09-15-web-clip-fidelity.md` v1)

담당: 새 설계가 기존 배선·미러·봉인·재동결 체계와 충돌하거나 배선을 빠뜨리는 지점.
설계 수정은 하지 않는다. 등급: BLOCKER 4 · MAJOR 6 · MINOR 4.

---

### [BLOCKER] `CURRENT_VERSION` 2→3 상향이 기존 v2 픽스처 5건을 red로 만든다

**빠진 배선/충돌** — 설계 §2.3은 파급을 «`ACCEPTED_VERSIONS`에 3 추가»로만 적었다.
그러나 `compare_render_audit.py`의 v2 동작은 `ACCEPTED_VERSIONS`가 아니라 **`CURRENT_VERSION`
동등 비교 4곳**에 걸려 있다. `CURRENT_VERSION = 3`이 되는 순간 **기존 v2 동결본에서 motion
축 검증·경고·계수 요약이 전부 조용히 꺼진다** — 설계가 R1에서 금지한 «조용한 green»이 바로
이 파일 안에서 먼저 발생한다.

**근거**
- `dddjango-web/scripts/compare_render_audit.py:44` `CURRENT_VERSION = 2`
- `:81` `if data.get("audit_version") == CURRENT_VERSION:` → v2의 `motion` 필수 필드 검증 진입점
- `:100` `if data.get("audit_version") != CURRENT_VERSION: return []` → `motion_coverage_warns` 전체
- `:194` `if data.get("audit_version") == 2` → `--validate`의 motion 계수 표기 (리터럴 2)
- `:259` `if tver == CURRENT_VERSION and iver == CURRENT_VERSION:` → 「모션 인벤토리」 INFO 행

깨지는 픽스처(`dddjango-web/scripts/test/fixtures_audit.sh`, `verify-web` → `run_fixtures.sh`가 실행):
| assert | 줄 | 의존하는 술어 | v3 상향 후 |
|---|---|---|---|
| `S2 v2 motion 부재 fail-loud` (exit 1 기대) | `:149` | `:81` | motion 검증 스킵 → exit 0 → **FAIL** |
| `Wb 차단 시트 부분성 warn` | `:165` | `:100` | warn 미발화 → **FAIL** |
| `Ws 측정 밖 엔진 warn` | `:169` | `:100` | warn 미발화 → **FAIL** |
| `Wz 시트 0장 비개연 warn` | `:173` | `:100` | warn 미발화 → **FAIL** |
| `A1v2 v2 동일 실측 diff 0` («모션 인벤토리» 문자열 기대) | `:177` | `:259` | INFO 미출력 → **FAIL** |
| `V2 v2 validate 정상` («motion tr 1/kf 1» 기대) | `:145` | `:194` 리터럴 2 | 리터럴을 두면 통과하나 **v3가 «v1(모션 축 없음)»으로 오표기**된다 |

**필요한 조치** — 설계가 「motion 축이 유효한 버전 집합」(예: `MOTION_VERSIONS = {2, 3}`)과
「clip 축이 유효한 버전 집합」을 분리해 명시하고, 위 4곳 각각을 어느 술어로 바꿀지 지정할 것.
`ACCEPTED_VERSIONS`만 언급한 §2.3은 파급 전수가 아니다.

---

### [BLOCKER] `test_clip_audit.mjs`가 어느 경로에서도 실행되지 않는다

**빠진 배선/충돌** — 설계 §2.4는 순수 판정 시험을 `scripts/test/test_clip_audit.mjs`로 두고,
`fixtures_clip_audit.sh`의 내용은 **`check_clip_audit.py`의 negative↔positive 짝 + 결정론**으로만
규정했다. `.mjs`를 어디서 부르는지는 설계 어디에도 없다. 저장소에서 `.mjs`는 **`fixtures_*.sh`가
명시적으로 `node --test`로 부를 때만** 돈다 — 자동 수집 대상이 아니다.

**근거**
- `dddjango-web/scripts/test/run_fixtures.sh:10` `for fx in "$HERE"/fixtures_*.sh; do` — 글롭은
  `fixtures_*.sh` 뿐이고 `.mjs`는 매치되지 않는다
- 선례: `dddjango-web/scripts/test/fixtures_interactions.sh:9-11` 가
  `python3 test_interaction_evidence.py` / `node --test test_interaction_audit.mjs` /
  `node --test test_observe_interactions.mjs` 를 **명시적으로** 부른다
- `Makefile:94` `bash dddjango-web/scripts/test/run_fixtures.sh` — verify-web의 유일한 픽스처 진입점

**필요한 조치** — `fixtures_clip_audit.sh`가 `node --test .../test_clip_audit.mjs`를 명시적으로
부르도록 설계에 못박을 것(또는 `fixtures_interactions.sh`처럼 3종 묶음 러너 판형을 채택).
지금 문면대로 구현하면 순수 판정 회귀가 `make verify`에서 **한 번도 실행되지 않는다**.

---

### [BLOCKER] Makefile 변경에 대한 봉인(seal) 재발행이 설계에 없다 — `make verify`가 red

**빠진 배선/충돌** — 설계 §4 표가 `Makefile` 편집을 계획하는데, `Makefile`은 **manifest 봉인
대상(`protocol` 그룹)**이다. 재봉인 없이 커밋하면 `make verify`의 `verify-base-core` 단이 곧바로
RED가 된다 — `--draft`는 «설치 cache 축»만 면제하고 **그룹 파일 해시 대조(②)는 draft에서도 돈다**.

**근거**
- `workspace/tools/manifest_seal.py` `GROUPS["protocol"]["globs"]`에 `"Makefile"` 등재
- 같은 파일 ②그룹 대조: `for k in changed: fails.append(f"{name}: 봉인 후 변경 — {k}")`
  (draft 분기는 `if draft_ok and k.startswith("cache-")` 뿐 — 그룹 검사에 예외 없음)
- `Makefile:187` `PYTHONUTF8=1 python3 workspace/tools/manifest_seal.py --check --draft` (verify-base-core)
- 절차 정본: `docs/DEVELOPMENT.md` §6 — «봉인은 봉인 대상 파일을 바꾼 커밋 **뒤에** 별도 chore
  커밋으로 재발행한다»
- 선례 2건: `72854ce3`(v1→v2)이 `Makefile`+`workspace/eval/ab/T2-0b-manifest.json` 동시 변경 ·
  최근 `1f05cdb0` «chore: verify 봉인 재발행 (Makefile … 커밋 이후 — sealed_commit 정렬)»

**필요한 조치** — 설계에 «변경 커밋 → 별도 chore 봉인 커밋(`manifest_seal.py --write`) → `make verify`
재실행» 순서를 명기할 것. 또한 §4의 Makefile 편집이 정말 필요한지 먼저 판단할 것(아래 MINOR 참조 —
픽스처 2종은 Makefile 편집 없이 배선된다. 실브라우저 회귀만이 진짜 Makefile 편집 사유다).

---

### [BLOCKER] `clip-containers.md`의 재동결 분류가 없다 — 어느 쪽으로 가도 현재 문면은 깨진다

**빠진 배선/충돌** — 설계 §3.1은 산출 위치를 `<산출물 폴더>/clip-containers.md`로 쓰고
«`motion-notes.md`처럼 architect에게 전달»한다고 적었다. 그런데 `motion-notes.md`는 **보존
(preserved)** 대상이다 — 재동결이 재생성할 수 없는 서기 산출이기 때문이다. `clip-containers.md`는
정반대로 **`design-ref/`에서 기계 추출**되고, `design-ref/`는 재동결이 **트리째 폐기**한다.
분류를 안 하면 재동결 후 «폐기된 소스에서 뽑은 낡은 표»가 살아남아 새 시안을 처분한 척한다.
분류를 폐기로 하면 **지금 문면(`<산출물 폴더>/`)이 `web_refreeze_contract.py` D1에 걸려 verify RED**다.

**근거**
- `dddjango-web/scripts/refreeze.py:32-36` `FIXED_DISCARD_FILES` · `:37` `FIXED_DISCARD_TREES = ('design-ref',)`
  · `:39-40` `REQUIRED_STAGING` (staging 완결성 검사 — `:425-427`)
- `dddjango-web/scripts/refreeze.py:202-211` `orphan_set()`은 `captures/**`만 훑는다 →
  빌드 루트의 미등록 파일은 **고아로도 보고되지 않는다**(조용히 잔존)
- `workspace/tools/web_refreeze_contract.py` `DISCARD_NAMES`·`PRESERVED_NAMES` 닫힌 목록 ·
  `check_d1()` — `<산출물 폴더>/<DISCARD_NAMES 원소>` 패턴이 「산출물 위치」 절 밖에 있으면 RED
- 현행 실측(문면 규율 확인): `commands/dddjango-web.md`의 `<대상 폴더>/design-ref` 6건 ·
  `<산출물 폴더>/design-ref` 1건(「산출물 위치」 절 = D1 면제) · `<산출물 폴더>/motion-notes.md` 3건(보존)
- `dddjango-web/scripts/test/test_refreeze.py:195-198` `test_preserved_never_in_discard`가
  `motion-notes.md`를 보존으로 못박는다 — 새 산출물도 같은 수준의 결정이 필요하다
- `Makefile:111-112` 가 `web_refreeze_contract.py --self-test` → 본검사를 verify-web에서 실행

**필요한 조치** — 설계가 다음 4곳을 한 번에 결정·등재할 것:
① `refreeze.py::FIXED_DISCARD_FILES`에 `clip-containers.md` 추가 여부와 `REQUIRED_STAGING` 편입 여부
② `web_refreeze_contract.py::DISCARD_NAMES`(또는 `PRESERVED_NAMES`) 등재 + 그 `--self-test` fixture
③ `commands/dddjango-web.md`·`design-acquisition.md`의 표기 — 폐기 분류면 산출 경로는
   `<대상 폴더>/clip-containers.md`(Codex SKILL.md 동일), 추출 **입력**도 `<대상 폴더>/design-ref/…`
   (`BUILD/design-ref` 금지 — `TARGET/design-ref`. `design-acquisition.md`의 현행 `TARGET/design-ref` 2건이 판형)
④ `test_refreeze.py`의 discard/preserve 단언에 새 이름 추가

---

### [MAJOR] `fixtures_audit.sh`에 v3 표본이 없다 — v1→v2 판형 미준수

**빠진 배선/충돌** — 설계 §2.3은 «v1→v2 때와 같은 판형»이라고 선언하지만, §4의 편집 대상 표에
`scripts/test/fixtures_audit.sh`가 **없다**. v1→v2 때 실제로 한 일은 스키마 검증기의 픽스처를
같은 커밋에서 확장한 것이다.

**근거**
- `git show --stat 72854ce3` 파일 목록에 `dddjango-web/scripts/test/fixtures_audit.sh`와
  그 Codex 미러가 포함됨(커밋 메시지: «픽스처 41케이스(audit 22·motion_spec 19 — negative/positive 짝)»)
- 현행 v2 표본 블록: `fixtures_audit.sh:130-177` (V2·S2·RV·W1v·MIX·Wb·Ws·Wz·A1v2) + `:180-186` DETv2
- 설계 §4 표에는 `Makefile`·`docs/DEVELOPMENT.md`만 있고 픽스처 파일이 없다

**필요한 조치** — §4 표에 `scripts/test/fixtures_audit.sh`를 넣고 최소 표본을 명기할 것:
V3(v3 validate 정상·clip 계수 표기) · S3(v3인데 `clip` 블록 부재 → fail-loud exit 1) ·
RV3(`--require-version 3`에 v2 → exit 1) · A1v3(v3↔v3 diff 0) · MIX2(v2 target × v3 impl) ·
그리고 **위 BLOCKER 1이 요구하는 «v2는 여전히 motion 검증·warn을 받는다» 회귀 단언**.

---

### [MAJOR] 빌드 스펙 정본(D13 행)이 갱신 대상에서 빠졌다

**빠진 배선/충돌** — `AGENTS.md`가 dddjango-web의 «빌드 스펙 정본»으로 지정한 문서에
`audit_version 2`와 `--require-version 2`가 리터럴로 박혀 있다. v3 상향 후 스펙 정본이 구현과
모순된다. 기계 검사가 없어 **조용히 어긋난다**.

**근거**
- `workspace/design/2026-08-23-web-presentation-layer-spec.md:42` D13 행 — «스니펫 v2(`assets/render_audit.js`
  … `audit_version` 2)» · «신규 동결은 `--require-version 2` 강제·기존 v1 동결본은 하위 호환+warn»
- `AGENTS.md` — «빌드 스펙 정본: `workspace/design/2026-08-23-web-presentation-layer-spec.md`»
- 선례: `72854ce3`가 이 파일을 함께 고쳤다(«스펙 D13 v2 행 교체(사용자 확정 2026-08-25)»)

**필요한 조치** — §4 표에 스펙 정본 행 교체(D13 v3 또는 새 D 행)를 넣고, 사용자 확정이 필요한
결정인지(v1→v2 때는 «사용자 확정»이었다) 명시할 것.

---

### [MAJOR] references는 **byte 미러**인데 설계의 미러 규칙이 이를 «의미 미러»로 분류할 여지를 준다

**빠진 배선/충돌** — 설계 §4 마지막 줄: «Codex 미러: `scripts/`·`assets/`는 byte 동일, 커맨드·
에이전트·**SKILL 본문은 의미 미러**». 그러나 설계가 편집하는 `skills/*/references/*.md` 3종은
`verify-web`이 `cmp -s`로 **byte 동일**을 강제한다. 「SKILL」 범주로 읽어 의미 미러로 처리하면
verify-web이 그 자리에서 RED다.

**근거**
- `Makefile:100` `cmp -s dddjango-web/skills/implementation-ui/references/design-acquisition.md codex-…`
- `Makefile:101` `… implementation-ui/references/final.md …`
- `Makefile:102` `… architecture-web/references/final.md …`
- (`Makefile:99` `design-evidence.md`도 같은 판형 — 이번 설계의 편집 대상은 아니다)
- 설계 §4 표의 편집 대상 `skills/architecture-web/references/final.md` ·
  `skills/implementation-ui/references/{final,design-acquisition}.md` — **3건 모두 byte 미러 대상**

**필요한 조치** — 미러 규칙 문장을 «`scripts/`·`assets/`·`skills/*/references/*.md`는 byte 동일 /
`commands/*.md`·`agents/*.md`만 의미 미러»로 정정할 것. 덧붙여 dddjango-web은 온톨로지 코퍼스 밖이라
`corpus_mirror_sync.py`가 이 파일들을 **갱신하지 않는다**(해당 도구에 `dddjango-web` 문자열 0건) —
손으로 복사하는 것이 정본 절차임을 설계가 밝혀 둘 것.

---

### [MAJOR] Codex 의미 미러 대상이 열거되지 않았고, 그 누락을 잡는 백스톱이 없다

**빠진 배선/충돌** — 설계 §4는 편집할 Claude 정본 5종만 적고, 대응하는 Codex 파일을 열거하지 않는다.
byte 미러(scripts·assets·references)는 `diff -rq`/`cmp`가 자동으로 잡지만, **커맨드·에이전트의 의미
미러는 어떤 검사도 잡지 않는다** — 빼먹으면 verify green인 채로 Codex 사용자만 구 규범을 받는다.

**근거** — 이번 설계가 건드리는 것들의 Codex 대응(정본→미러, 검증 수단):
| Claude 정본 | Codex 미러 | 검증 |
|---|---|---|
| `commands/dddjango-web.md` | `codex-dddjango-web/skills/dddjango-web/SKILL.md` | **없음**(부분적으로 `web_refreeze_contract` A/B/D1/D2만) |
| `agents/design-architect-web.md` | `codex-dddjango-web/skills/dddjango-web-design-architect-web/SKILL.md` | **없음** |
| `agents/design-review-web.md` | `codex-dddjango-web/skills/dddjango-web-design-review-web/SKILL.md` | **없음** |
| `scripts/check_clip_audit.py`·`extract_clip_containers.py`·`check_clip_spec.py` | `codex-dddjango-web/skills/dddjango-web/scripts/` | `Makefile:96` `diff -rq` (자동) |
| `scripts/test/fixtures_clip_audit.sh`·`test_clip_audit.mjs`(+브라우저 픽스처 HTML) | 같은 `scripts/test/` 하위 | `Makefile:96` `diff -rq` (자동) |
| `assets/render_audit.js` | `codex-dddjango-web/skills/dddjango-web/assets/` | `Makefile:97` `diff -rq` (자동) |
- v1→v2 선례(`72854ce3`)가 `codex-dddjango-web/skills/dddjango-web-design-{architect,review}-web/SKILL.md`와
  `…-discipline-reviewer-web/SKILL.md`를 함께 고쳤다

**필요한 조치** — §4 표를 Claude↔Codex 2열로 확장하고, 「자동 검출(diff/cmp)」과 「수동 의무(백스톱 없음)」을
표에서 구분할 것. `scripts/test/**`도 `diff -rq` 범위 안이라는 사실(새 `.mjs`·픽스처 HTML 포함)을 명기할 것.

---

### [MAJOR] 새 실브라우저 회귀의 SKIP/ERROR 의미론·이중 배선이 지정되지 않았다

**빠진 배선/충돌** — 설계 §2.4는 «실브라우저 회귀 1건을 `verify-web-browser`에 더한다»가 전부다.
현행 체계에서 브라우저 스위트는 **두 곳에 배선**돼 있고, **SKIP 의미론을 스위트 파일 자신이 소유**한다.
새 파일이 이 판형을 따르지 않으면 브라우저 없는 개발 머신에서 `make verify`가 RED가 된다.

**근거**
- `Makefile:128` `DDDJANGO_WEB_REQUIRE_BROWSER=1 node --test dddjango-web/scripts/test/test_observe_interactions.mjs`
  — 리터럴 단일 파일. 새 파일은 **여기에 한 줄을 더해야** 돈다(= Makefile 편집 = 봉인 재발행)
- `Makefile:125-126` — `DDDJANGO_WEB_PLAYWRIGHT_MODULE` 필수 + (`…BROWSER_CHANNEL` | `…BROWSER_CDP`) 필수
- `Makefile:121-124` — `DRY=1`이면 통째로 건너뛴다. `release-web`(`Makefile:305`)의 유일한 선행 조건
- `scripts/test/test_observe_interactions.mjs:21-30` — 모듈 env 미설정 시 `SKIP:` + exit 0,
  `DDDJANGO_WEB_REQUIRE_BROWSER=1`이면 `ERROR:` + exit 1. **파일이 스스로 소유**
- `scripts/test/fixtures_interactions.sh:11` — 같은 파일을 `verify-web`에서도 부른다(SKIP 경로)
- 예산: 현행 `verify-web-browser`는 이 한 파일(197KB·Playwright 기동 + 로컬 HTTP 서버)이 전부다.
  별도 `node --test` 프로세스를 추가하면 **브라우저 기동이 1회 늘어난다** — 설계에 실측 수치가 없다

**필요한 조치** — 새 브라우저 파일이 ① 같은 env 게이트·SKIP/ERROR 의미론을 스스로 소유하고
② `fixtures_clip_audit.sh`(verify-web·SKIP 경로)와 `Makefile` `verify-web-browser`(REQUIRE 경로)
**양쪽에 배선**됨을 명기할 것. 기존 `test_observe_interactions.mjs`의 `describe` 그룹으로 붙일지
새 파일로 뗄지도 결정 대상이다(전자면 Makefile 무편집 — 봉인 재발행도 불필요). 추가 소요는
릴리즈 19분 예산에 대한 실측치로 적을 것.

---

### [MAJOR] `render_audit.js`는 UMD 모듈이 아니라 «붙여넣기 IIFE»다 — `interaction_audit.js` 선례가 그대로 이식되지 않는다

**빠진 배선/충돌** — 설계 §2.4는 «`interaction_audit.js`의 선례대로 … `module.exports` 하고
`node --test`로 브라우저 없이 회귀»라고 적는다. 그러나 두 파일은 구조가 다르다.
`interaction_audit.js`는 **로드 시 DOM을 전혀 건드리지 않는 순수 UMD factory**이고,
`render_audit.js`는 **로드 즉시 DOM을 훑고 문자열을 반환하는 IIFE**다. 선례를 문자 그대로 옮겨
UMD factory로 바꾸면 «콘솔에 전문 붙여넣기» 계약이 깨져 **렌더 실측 수집 자체가 안 돈다**.
반대로 그냥 `require()`하면 Node에서 `document`/`location`/`innerWidth` 참조로 즉사한다.

**근거**
- `dddjango-web/assets/interaction_audit.js:49-55` — `(function (root, factory) { if (typeof module === 'object' && module && module.exports) { module.exports = factory(); } else { root.__interactionAudit = factory(); } })(…)`
  · 헤더 `:6` «UMD: Node는 module.exports, 브라우저는 globalThis.__interactionAudit» · 순수 함수만
- `dddjango-web/assets/render_audit.js:22-23` `(() => { 'use strict'; const AUDIT_VERSION = 2;` —
  IIFE. `:53-55` `location`·`innerWidth` 즉시 참조, `:69` `document.querySelectorAll('body *')`,
  말미 `return '[render-audit] …'` + `console.log(json)` + `copy(json)` 부수효과
- 계약: `dddjango-web/commands/dddjango-web.md:143` «대행이어도 **스니펫 전문 실행**이다
  (요약·발췌·자체 재구성 실행 금지)» · «스니펫 `${CLAUDE_PLUGIN_ROOT}/assets/render_audit.js` 내용을
  … DevTools 콘솔에 붙여넣어 실행하게 한다»
- `scripts/test/test_interaction_audit.mjs:16` `const pure = require('../../assets/interaction_audit.js');`
  — 이 한 줄이 성립하는 이유가 위 UMD 구조다

**필요한 조치** — 설계가 셋 중 하나를 명시적으로 고를 것: ⓐ IIFE 선두에 Node 가드
(`if (typeof module === 'object' && module && module.exports) { module.exports = {…}; return; }`)를 두고
브라우저 경로는 그대로 — 붙여넣기 계약 보존 ⓑ 순수 기하를 별도 파일로 떼고 스니펫에는 **인라인 사본**
(중복을 감수) ⓒ 브라우저 회귀만으로 커버(순수 `.mjs` 포기). 「선례대로」는 이 파일에 대해 성립하지 않는다.

---

### [MINOR] `verify-web`에 픽스처 2종을 «더한다»는 것은 배선이 아니라 중복이다

**빠진 배선/충돌** — 설계 §4 Makefile 행의 «`verify-web`에 새 픽스처 2종». `run_fixtures.sh`가
`fixtures_*.sh`를 **자동 수집**하므로 `fixtures_clip_audit.sh`는 파일을 두는 것만으로 돈다.
Makefile에 명시 호출을 더하면 이중 실행이 되고, **불필요한 봉인 재발행 사유**만 만든다.

**근거**
- `dddjango-web/scripts/test/run_fixtures.sh:2-4` 헤더 주석 — «fixtures_*.sh 글롭 전부 실행 …
  추가되면 존재하는 것만 자동으로 실행한다» · `:10` 글롭 루프
- 실증: `fixtures_evidence_debt.sh`(09-15)·`fixtures_refreeze.sh`(09-15)는 Makefile 무편집으로 등재됨
- 설계 §2.4가 예고한 픽스처 파일명도 `fixtures_clip_audit.sh` — 글롭에 자동 매치

**필요한 조치** — §4 Makefile 행을 **실브라우저 회귀 1건으로 한정**하고, 픽스처는 «파일 생성만»으로
정정할 것. 그러면 위 BLOCKER 3(봉인)의 범위도 명확해진다.

---

### [MINOR] `docs/DEVELOPMENT.md`는 §1보다 §4·§5가 진짜 등재 자리다

**빠진 배선/충돌** — 설계 §4는 «§1 지도에 새 스크립트 3개»만 적는다. §1의 dddjango-web 블록은
**스크립트 대장이 아니라 선택적 주석 지도**다(현재 `REQUEST_GUIDE.md`·`hooks/hooks.json`·
`scripts/refreeze.py` 3줄뿐 — `backstop.py`·`compare_render_audit.py`·`check_motion_spec.py`도 없다).
반면 §4 「검사기(백스톱)·도구 수정」은 verify-web이 부르는 각 도구의 계약을 소유하고, §5는
`verify-web-browser`의 범위를 소유한다.

**근거**
- `docs/DEVELOPMENT.md` §1 dddjango-web 블록 — 3항목만 열거
- 같은 문서 §4 — `web_refreeze_contract.py`·`request_guide_contract.py`·`reverse_coverage.py`·봉인 규율
- 같은 문서 §5 표 — `make verify-web-browser` 행(«K3 상호작용 관찰 브라우저 스위트»)
- 선례: `72854ce3`(v1→v2)은 `docs/DEVELOPMENT.md`를 **건드리지 않았다** — §1 등재가 관례가 아니다

**필요한 조치** — §1 등재는 선택, §5 `verify-web-browser` 설명 갱신(스위트가 K3 단일이 아니게 됨)은
필수로 구분할 것. `clip-containers.md`를 재동결 폐기 대상으로 정하면 §4의 `web_refreeze_contract.py`
설명(DISCARD 목록)도 함께 갱신 대상이다.

---

### [MINOR] `backstop.py`의 빌드 폴더 마커는 **손대지 않는 것**이 맞다 — 설계가 명시적으로 비결정을 남길 것

**빠진 배선/충돌** — 과제에서 지목한 마커 집합에 `clip-containers.md`를 넣으면, **`design-ref`가
없는데 파생 표만 남은 폴더**가 «소스 보유 빌드»로 오인된다. 넣지 않아도 손실이 없다 —
`design-ref`가 이미 마커이고 `clip-containers.md`는 그것에서 파생되므로 항상 공존한다.

**근거**
- `dddjango-web/scripts/backstop.py:65` `markers = {'design-ref', 'design-input.json', 'source-manifest.json', 'render-audit.json'}`
- 같은 함수 `:70-73` — `parts[2] in markers`면 `builds.add(...)`

**필요한 조치** — 설계에 «마커 집합 무변경» 한 줄을 남길 것(리뷰어가 매번 재판단하지 않도록).

---

### [MINOR] 조감도 HTML·인수 기록 갱신이 §4 표에 없다

**빠진 배선/충돌** — 사용자 상시 지침이 작업 마무리마다 `ontology-adoption-map.html` 갱신을
요구하고, v1→v2 선례도 같은 커밋에서 이를 갱신하며 인수 기록 문서를 남겼다.

**근거**
- `git show --stat 72854ce3` — `workspace/design/ontology-adoption-map.html` ·
  `workspace/design/2026-08-25-web-motion-determinism-acceptance.md` 포함
- 사용자 상시 지침(전역 메모리): «작업 마무리마다 로컬 독립 HTML `ontology-adoption-map.html` 갱신 필수»

**필요한 조치** — §4 표에 조감도 갱신과 인수 기록 산출을 «구현 후 의무» 항목으로 넣을 것.

---

## 부록 — 자동으로 걸리는 것 / 수동 의무인 것 (구현자 체크리스트)

| 변경 | 걸리는 배선 | 자동? |
|---|---|---|
| `scripts/check_clip_audit.py` 외 신규 .py 2종 | `Makefile:96` `diff -rq … scripts` | ✅ 자동 RED(미러 없으면) |
| `scripts/test/fixtures_clip_audit.sh` | `run_fixtures.sh:10` 글롭 + `Makefile:96` | ✅ 자동 실행·자동 미러 검출 |
| `scripts/test/test_clip_audit.mjs` | — | ❌ **어디서도 안 돈다**(BLOCKER 2) |
| `assets/render_audit.js` v3 | `Makefile:97` `diff -rq … assets` | ✅ 미러는 자동 / 픽스처는 ❌(BLOCKER 1·MAJOR 5) |
| `skills/*/references/*.md` 3종 | `Makefile:100-102` `cmp -s` | ✅ 자동 RED |
| `commands/dddjango-web.md` · `agents/*.md` | — | ❌ Codex 의미 미러 수동(MAJOR 8) |
| `Makefile` | `manifest_seal.py --check --draft`(`Makefile:187`) | ✅ 자동 RED — **재봉인 필수**(BLOCKER 3) |
| `clip-containers.md` 신설 | `web_refreeze_contract.py`(`Makefile:112`) D1 | ⚠️ 등재하면 자동, 안 하면 **조용한 잔존**(BLOCKER 4) |
| 빌드 스펙 D13 행 | — | ❌ 검사 없음(MAJOR 6) |
