# 웹 시안 조작 상태 증거·재동결 기계 대조 — 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: `superpowers:subagent-driven-development`(권장) 또는 `superpowers:executing-plans`로 Task 순서대로 실행한다. 단계는 체크박스(`- [ ]`)로 추적한다. 실행: 계획 독립 적대 리뷰(`…/design-review/plan-review.md` — BLOCKER 1·MAJOR 11 반영 완료) → 사용자 승인 → Task 0~12 순차 → 각 Task 끝의 검증 green(Codex 미러 `diff -rq` 0 포함) → 독립 구현 리뷰 → `make verify` → 사용자 승인 뒤 커밋·`make release-web`. **web 선례 관례대로 현재 작업 트리에서 그대로 작업한다** — 작업 전 파일은 `/tmp/dddjango-web-interaction-evidence-20260913/before/`에 보존했고(`before-hashes.json` 81파일), 커밋·스태시·브랜치 전환으로 사용자 미커밋 변경(v1.1.7 되돌림 18파일·`docs/master.html`·eval lanes md)을 수용하지 않는다. 커밋은 Task 12의 사용자 승인 뒤이며, 그 전 Task 끝의 «기록» 단계는 `git diff --stat`과 변경 파일 hash를 `execution-notes.md`에 남기는 것이다(«기록» 라벨 `feat/docs/build`는 기록용이고 최종 커밋 메시지는 Task 12에서 정한다). 릴리즈·A8 앱 수정은 이 계획의 실행 권한 밖이다.

**Goal:** dddjango-web이 엔진/JSX 시안의 JS 조작 상태(드롭다운·다이얼로그·토글·스크림·Esc·데이터 상태)를 사용자 지목 없이 기계로 발견·실행·동결하고, 재동결 대조를 manifest 기계 대조로만 판정하게 한다.

**Architecture:** 페이지 안 스니펫(열거·identity·context·잔여 순수 함수) + 단일 드라이버 함수(Node/MCP 공용 탐색·재생·캡처) + 증거 검사기 v2(잔여·표면 키 연결·served·루트·수집기 sha) + `archive_design.py --compare-build`(exit 0/3/4). Coordinator·리뷰어 규범은 실행·입력 계약만 바꾸고 판형·역할은 유지한다. 기준선 = 작업 트리(v1.1.7 내용).

**Tech Stack:** Python 표준 라이브러리(검사기·대조), 브라우저 JS(스니펫), Node ≥ 22 ESM(실측 v26.8.2) + 외부 Playwright 모듈(이 머신: `~/.npm/_npx/9833c18b2d85bc59/node_modules/playwright` 1.63.0-alpha) + 설치된 Google Chrome(`channel: 'chrome'` 실측 OK 152.0.7977.83), Bash 픽스처, Markdown 런타임 지침, Claude/Codex 미러.

**Spec:** `workspace/design/2026-09-13-web-interaction-evidence.md`(v2 — K1~K8). 진단 `workspace/eval/web-a8-interaction-observation/diagnosis.md`. 검토 원문 `…/design-review/rv-{A,B,C,R}.md`·`plan-review.md`. 충돌 시 설계 v2가 우선한다.

## Global Constraints

- 변경 범위 = `dddjango-web/`·`codex-dddjango-web/` 미러·`Makefile`·`docs/DEVELOPMENT.md` §2/§5/§6·workspace 계획/평가 기록. `.gitignore`는 바꾸지 않는다(테스트 임시 산출은 OS tempdir). backend dddjango·ontology·A8 앱·사용자 앱·활성 서버/DB 무수정. A8 산출물 폴더는 읽기 전용(사본에서만 실행).
- 1.1.8~1.1.12에서 되돌린 문단은 재도입하지 않는다. 되돌린 design-review-web 문장 «독립 렌더가 필요한 화면·상태만 … 추가»는 쓰지 않는다.
- 플러그인은 Playwright·브라우저를 설치하지 않는다. 드라이버 인자 = `--playwright-module <dir>`(env 폴백 `DDDJANGO_WEB_PLAYWRIGHT_MODULE`) · `--browser-channel chrome`(기본, env `DDDJANGO_WEB_BROWSER_CHANNEL`) 또는 `--cdp <ws>`(env `DDDJANGO_WEB_BROWSER_CDP`). 없으면 exit 1 + 안내. 저장소에 `node_modules`를 만들지 않는다.
- Coordinator의 Bash 도구 상한(≤600초) 때문에 드라이버는 백그라운드 실행 + 호출당 `--max-minutes 8` + exit 3이면 `--resume` 반복. 규범·평가 프롬프트에 같은 지시를 넣는다.
- scripts·assets·test fixtures·references(implementation-ui·architecture-web)는 Claude/Codex byte 미러(각 Task 끝에 `cp` 후 `diff -rq` 0), Coordinator·역할 md는 의미 미러(`${CLAUDE_PLUGIN_ROOT}` ↔ `${SKILL_DIR}`·`spawn_agent` 관례 유지). REQUEST_GUIDE는 byte 미러 + `request_guide_contract.py`(상대 목적지 구문 금지).
- exit 계약: `check_design_evidence.py` 0/1/2 유지. `archive_design.py` 0(same)/1(오류)/3(changed·added·removed)/4(same+carried). design-evidence.md에 «3·4는 archive_design 전용·backstop 미소비» 명기.
- 작성자 면제 필드 없음. 예외는 `interaction_exclusions`(활성 대상의 10% 이하·`approval_quote` 10자 이상 원문 대조·stdout 전량 노출)뿐. 산문 로그 파싱은 테스트 fixture 한정. archive case는 `reached_by` 필수.
- 기본 상한 `--max-minutes 90`(단, 도구 안에서는 8로 분할)·`--max-steps 8000`·`--max-depth 24`, `--resume` 지원. 원격 URL은 `--cdp` origin만.
- raw CLI transcript는 task temp에 두고 저장소에는 프롬프트·호출 인자·판정·집계만 둔다(09-06 선례).
- 검증 수치는 마지막 실행 로그의 것만 적는다(DEVELOPMENT §4).

---

## 파일 구조

| 파일 | 책임 | 상태 |
|---|---|---|
| `dddjango-web/assets/interaction_audit.js` | 페이지 안 스니펫. UMD(`module.exports` 또는 `globalThis.__interactionAudit`). `pure`(정규화·identity·context·stateHash·surfaceKey·requiredActions·residual·linkedSurfaces)와 `dom`(inventory·overlays·clickPoint·outsidePoint·occlusion·live 표식) | 신규(+Codex byte) |
| `dddjango-web/assets/observe_interactions.pw.js` | `export default async function observe(page, opts)` — 탐색·재생·조작·served·캡처·`interactions.json`·resume·CDP 리스너·발견 조작·iframe | 신규(+Codex byte) |
| `dddjango-web/scripts/observe_interactions.mjs` | CLI 래퍼(인자·env 폴백·모듈 해소·channel/CDP 기동·본체 호출·exit 0/1/3) | 신규(+Codex byte) |
| `dddjango-web/scripts/check_design_evidence.py` | source_observation v2·interactions exact-field·잔여·표면 연결·`reached_by` 필수·예외·served·루트·수집기 sha·crop·`carried_from`·`legacy_v1` | 수정(+Codex byte) |
| `dddjango-web/scripts/archive_design.py` | `--compare-build`·`--compare-out`·`--carried`·자동 carried·exit 3/4·`carried_from` | 수정(+Codex byte) |
| `dddjango-web/scripts/backstop.py` | `legacy_v1_allowed()`(추적 파일 ≥1·변경 0·others/ignored 0) | 수정(+Codex byte) |
| `dddjango-web/scripts/test/test_interaction_evidence.py` · `test_design_archive.py` · `test_design_evidence.py` · `test_interaction_audit.mjs` · `test_observe_interactions.mjs` · `fixtures/interaction/{fixture.html,frame.html,expected/*.json,r3-steps.json}` · `fixtures_interactions.sh` | 검사기·대조·backstop·순수 함수·DOM/e2e 테스트 | 신규/수정(+Codex byte) |
| `dddjango-web/skills/implementation-ui/references/design-evidence.md`·`design-acquisition.md` | 스키마·CLI·exit·Limits·재동결·수집 절차 | 수정(+Codex byte) |
| `dddjango-web/commands/dddjango-web.md`·`agents/design-review-web.md`·`REQUEST_GUIDE.md` | 실행·입력 계약·감사 항목·전제조건 | 수정(+Codex 의미/byte) |
| `Makefile`·`docs/DEVELOPMENT.md` | `verify-web` references cmp·`verify-web-browser`·`release-web` 선행(DRY=1은 안내만)·§2 node 필수·§5 표·§6 | 수정 |
| `workspace/eval/web-a8-interaction-observation/{prior,dryrun,native,refreeze,samples,review,verification}/`·`execution-notes.md` | 평가 기록 | 신규 |

---

### Task 0: 작업 전 보존·이관·문서 연결·브라우저 기동 확정

**Files:** `workspace/eval/web-a8-interaction-observation/{prior/,before-hashes.json,execution-notes.md}` · `workspace/plan/2026-09-13-web-a8-interaction-observation.md`

- [x] **Step 1**: 수정 대상 파일 + scripts/assets 전부를 `/tmp/dddjango-web-interaction-evidence-20260913/before/`에 보존, sha256을 `before-hashes.json`에 기록(81파일). 미커밋 사용자 변경은 그대로(브랜치·스태시·커밋 없음). 되돌림 파일은 Claude 9 + Codex 9 = 18파일.
- [x] **Step 2**: `/tmp/dddjango-web-a8-interactions-20260913/` 프롬프트·호출 인자·판정과 oracle을 `prior/`로 이관(39파일), `prior/README.md`에 미이관 사유.
- [x] **Step 3**: 옛 계획 메모 말미 «후속» 절.
- [ ] **Step 4**: 브라우저 기동 방식 고정 — 실측(2026-09-13, `scratchpad/pw-probe.mjs`): 기본 `launch()` FAIL(«Executable doesn't exist … chromium_headless_shell-1243»), `channel:'chrome'` OK(152.0.7977.83·클릭 정상). 결정 = `--browser-channel chrome` 기본·`--cdp` 대안·설치 0. 모듈 경로·버전·채널을 `execution-notes.md`와 Task 11-3 scope 프롬프트에 고정.
- [ ] **Step 5 (기록)**: `git status --short`·`git diff --stat`을 `execution-notes.md`에 «Task 0» 항목으로.

### Task 1: 스니펫 순수 함수(`interaction_audit.js` · `pure`)

**Files:** Create `dddjango-web/assets/interaction_audit.js`, `scripts/test/test_interaction_audit.mjs`, `scripts/test/fixtures/interaction/expected/{doc-register.json,doc-edit.json,doc-cascade.json}`(K7 스키마를 지키는 최소 interactions 문서 3개 — initial+steps 포함)

**Interfaces (Produces):**
```js
pure.normalizeName(s)                       // NFC·NBSP→space·공백 접기·trim·80자
pure.identityOf(fields, collisions)         // {role,name,input_type,owner,owner_items_hash,dom_path}; name=='' 또는 collisions(같은 인벤토리 충돌)일 때만 dom_path 포함 → sha256 앞 12자
pure.stateContext(entries)                  // {ids, checked, faces, valueEmpty, surfaces} (live:true 항목은 ids에 포함, 해시 입력은 stateHash에서 제외)
pure.contextFor(entries, target, docOrder)  // K1 context_T: 트리거→앞선 다른 트리거 face만, 메뉴 항목→owner face 제외, 그 외→face 전체 제외 → sha256 앞 16자
pure.stateHash(entries, url)                // live:true 제외
pure.surfaceKey(entries)                    // face·checked·value·surface·owner_items_hash 제외·live 제외
pure.requiredActions(target, observedStates)// K1 표(click·click@state·focus/fill/blur·select@value·key:Escape·click:outside); 스크림형 오버레이의 click:outside ≡ 자기 click
pure.residual(doc)                          // interactions 문서 → [{target, action, option}]
pure.linkedSurfaces(doc)                    // added≠∅ step의 surface_key 집합
pure.sha256(bytesOrString)                  // 동기 순수 JS(외부 의존 0)
```

- [ ] **Step 1: 실패 테스트**(node:test) — `identity_ignores_value_and_face` · `identity_dom_path_only_on_empty_name_or_collision` · `context_trigger_prior_face_only`(앞 트리거 face 포함·자기/뒤 트리거 face 제외) · `context_menu_item_excludes_owner_face` · `context_button_excludes_all_faces` · `required_actions_toggle_two_states` · `required_scrim_outside_equals_click` · `residual_counts_executed_only`(failed/unreachable/unclickable 제외) · `surface_key_collapses_menu_items_across_owner_hash` · `state_hash_excludes_live_entries` · `linked_surfaces_from_added_steps` · 3개 expected 문서에 대한 residual/surface 기대값 일치.
- [ ] **Step 2**: `node dddjango-web/scripts/test/test_interaction_audit.mjs` → FAIL.
- [ ] **Step 3**: 구현(UMD 래퍼·sha256 내장·규칙은 설계 K1 문장 그대로 주석 인용).
- [ ] **Step 4**: PASS. `cp` → Codex `skills/dddjango-web/{assets,scripts}`, `diff -rq` 0.
- [ ] **Step 5 (기록)**: «feat(web): interaction audit pure functions».

### Task 2: 스니펫 DOM 열거(`interaction_audit.js` · `dom`)

**Files:** Modify `interaction_audit.js`; Create `scripts/test/fixtures/interaction/fixture.html`·`frame.html`; Create `scripts/test/test_observe_interactions.mjs`(`inventory` 그룹)

**Interfaces (Produces):**
```js
dom.markCandidates(rootSelector)   // 루트 서브트리(+오버레이) 가시 요소에 el.__iaIndex = i(JS 확장 속성·DOM 무변) → count
dom.inventory(rootSelector, {declared, excludedRegions, listenerIndexes /* Map index→[types] */, capabilities})
// → {root:{selector,found,fingerprint}, outside_root:{count,sample}, entries:[{id,enabled,checked,face,value_empty,surface,occluded,live,kind,rect,dom_path}],
//    targets:{id:{role,name,input_type,owner,owner_items_hash,dom_path,kind,declared,found_by,live}}, overlays:[id], declared_unmatched:[{selector,reason}]}
dom.clickPoint(id) → {x,y}|null ; dom.outsidePoint(overlayId) → {x,y}|null ; dom.hoverCandidates() → [id] ; dom.scrollContainers() → [{id,scrollHeight,clientHeight}]
```
규칙: 핸들러 보유=대상(후손 무관, found_by 채널 기록) · 의미 컨트롤 · `cursor:pointer` 보조는 `capabilities.cdp_listeners===false`일 때만·자기 cursor≠부모 · `aria-hidden` 제외 · disabled는 enabled:false · `role=status`/`aria-live` 서브트리는 live:true로 **열거** · 오버레이 = role 또는 구조(루트 80%·absolute/fixed·핸들러 또는 z-index) · occlusion = `elementFromPoint(clickPoint)`가 자기/후손 아니면 occluded · same-origin iframe은 `contentDocument`를 같은 규칙으로 순회(dom_path 앞에 `iframe[n]/`) · hover 후보 = mouseenter/mouseover 리스너 또는 `opts.hoverSelectors`(render-audit) 매칭 · 스크롤 컨테이너 = overflow auto/scroll ∧ scrollHeight>clientHeight.

**fixture.html**(외부 의존 0): 부모 스크림(onclick=close)+`stopPropagation` 패널(버튼 2) · label 클릭 토글(체크 span) · label 이름 트리거 2개 cascade(앞 선택값에 따라 뒤 항목 3/2종) · 같은 이름 «다음» 3단계 위저드(`hidden` 토글) · disabled 버튼 · 가림 대상(오버레이 뒤 행 4) · native select 옵션 3 · 이탈 링크(`about:blank`) · `role=status` 토스트 **안 액션 버튼** · hover 전용 메뉴(mouseenter로 열림) · 스크롤 컨테이너(끝에 버튼 1) · same-origin `<iframe src="frame.html">`(버튼 1) · 행 삭제(4명→빈 상태).

- [ ] **Step 1: 실패 테스트** — `inventory` 그룹: 모듈 env 없으면 `SKIP: DDDJANGO_WEB_PLAYWRIGHT_MODULE 미설정`(exit 0), `DDDJANGO_WEB_REQUIRE_BROWSER=1`이면 SKIP 대신 exit 1(정의는 이 테스트 파일이 소유). 단언: 초기 인벤토리에 행 4·«다음» 1·트리거 2·disabled(enabled:false)·토스트 버튼(live:true, 열거됨)·iframe 버튼(dom_path `iframe[0]/…`)·outside_root 0 · 스크림 열림 뒤 행 4 occluded·스크림 overlay·clickPoint가 패널 밖 · hover 후보 1·스크롤 컨테이너 1 · `--excluded-regions`로 루트 밖 요소 제외 시 outside_root 0, 없으면 count>0.
- [ ] **Step 2**: `DDDJANGO_WEB_PLAYWRIGHT_MODULE=… DDDJANGO_WEB_BROWSER_CHANNEL=chrome node …` → FAIL(dom 미구현). **Step 3**: 구현. **Step 4**: PASS + Codex `cp`·`diff -rq` 0. **Step 5 (기록)**.

### Task 3a: 드라이버 골격(래퍼·기동·served·initial·exit)

**Files:** Create `dddjango-web/assets/observe_interactions.pw.js`, `dddjango-web/scripts/observe_interactions.mjs`; Modify `test_observe_interactions.mjs`(`skeleton` 그룹)

**Interfaces (Produces):**
```js
export default async function observe(page, opts)
// opts: {url, rootSelector, browserViewport:[w,h], cropToRoot:true, entrypointSha, archiveSha, out, capturesDir,
//        declared:[], excludedRegions:[], hoverSelectors:[], maxSteps:8000, maxDepth:24, maxMinutes:90, resume:false,
//        snippetPath, driverPath, path:'node'|'mcp', listeners:'cdp'|'none', allowOrigin:null}
// → {targets, executed, residual:[…], surfaces:n, partial, capsHit, environmentError}
```
래퍼 CLI: `node observe_interactions.mjs --url U --root SEL --viewport 560x1040 --crop-root --entrypoint-sha S --archive-sha S --out F [--captures-dir D] [--declared F] [--excluded-regions F] [--hover-selectors F] [--playwright-module DIR] [--browser-channel chrome | --cdp WS] [--max-steps N --max-depth N --max-minutes N] [--resume]` (env 폴백 3종). 모듈 해소 = `createRequire(dir+'/package.json')(dir)`. 기동 = `chromium.launch({channel})` 또는 `chromium.connectOverCDP(ws)`. exit 0 완료 / 3 partial / 1 환경 오류(모듈·브라우저·루트 미발견·외부 스크립트 로드 실패 → `environment_error`·원격 URL 거부). 드라이버는 스니펫을 `import.meta.url` 기준 형제 경로로 찾고 `collector.snippet_sha256`·`driver_sha256`·`path`를 기록.
- [ ] **Step 1: 실패 테스트** — `skeleton` 그룹: 모듈 없는 경로 → exit 1 + «--playwright-module» 안내 · 원격 URL(`http://example.invalid/`) → exit 1 · 루트 selector 미발견 → exit 1 · 정상: `initial.capture` PNG 존재(루트 rect 크기)·`served`에 fixture.html sha·`collector.*` sha가 실제 파일 sha와 일치·`content_crop`=루트 rect·`browser_viewport`=560x1040.
- [ ] **Step 2**: FAIL. **Step 3**: 구현. **Step 4**: PASS + Codex `cp`. **Step 5 (기록)**.

### Task 3b: 탐색·재생·조작·캡처·resume

**Files:** Modify `observe_interactions.pw.js`; Modify `test_observe_interactions.mjs`(`explore` 그룹)

동작: 큐 키 `(identity, action, option, context_T)` · 항목마다 [접두 상태 해시 일치면 생략 | reload+재생(각 대상을 현재 인벤토리에서 identity로 찾아 실제 조작·종점 `before.state_hash` 대조·불일치 `unreachable`)] · 조작 = `page.mouse.click(x,y)`(clickPoint/outsidePoint 없으면 `unclickable`)·`fill`(K2 표본 규칙·`--declared` value 우선)·`focus`/`blur`·`press('Escape')`·`selectOption`(옵션마다) · 안정 대기(MutationObserver 250ms 정적·최대 3s) · 인벤토리 · step 기록 · added≠∅/navigated면 루트 크롭 캡처 · 새 키 큐 추가 · 이탈은 터미널 step · 상한 도달 `partial:true`·`caps_hit` · `--resume`은 out의 steps/큐를 잇되 archive/served sha 불일치면 exit 1.
- [ ] **Step 1: 실패 테스트** — `explore` 그룹(fixture 서빙): `residual.length===0` · «다음» 3단계 모두 executed(context 분기) · cascade 뒤 트리거 항목 5종 전부 executed · 토글 2상태(option=before surface) · 스크림 `click:outside`·`key:Escape` · native select 옵션 3 전부 `select` · 토스트 액션 버튼 executed(live) · 가림 행은 오버레이 context에서 미실행·목록 context에서 executed · 이탈 링크 `navigated`·미큐잉 · 빈 상태 도달(행 대상 0인 after 인벤토리를 가진 executed step 존재) · fill 표본: numeric 입력에 숫자열 · `unclickable` 기록 사례(완전 가림 요소) · 캡처 수 = 1 + added≠∅ step 수(navigated는 after null·PNG 없음 — 3b 판정) · `--max-steps 5` → partial·exit 3 → `--resume` 완료 exit 0 · resume 시 fixture 1바이트 변경 → exit 1 · `--declared` 매칭 → `targets[id].declared:true`, 미매칭 → `declared_unmatched` 1·잔여 밖.
- [ ] **Step 2**: FAIL. **Step 3**: 구현. **Step 4**: PASS + Codex `cp`. **Step 5 (기록)**.

### Task 3c: CDP 리스너·발견 조작·iframe·capabilities

**Files:** Modify `observe_interactions.pw.js`; Modify `test_observe_interactions.mjs`(`discovery` 그룹)

CDP 매핑: `const cdp = await page.context().newCDPSession(page)` → 스니펫 `dom.markCandidates(root)`로 `el.__iaIndex` 부여 → `DOM.getDocument({depth:-1})` → `DOM.querySelectorAll({nodeId, selector: root+' *, '+root})` → nodeId마다 `DOM.resolveNode`→objectId → `Runtime.callFunctionOn({objectId, functionDeclaration:'function(){return this.__iaIndex}'})` → `DOMDebugger.getEventListeners({objectId})` → `listenerIndexes: Map(index→[type])` → `dom.inventory(..., {listenerIndexes, capabilities:{cdp_listeners:true}})`. CDP 불가(`--cdp` 원격 제한 등)면 `capabilities.cdp_listeners:false`로 기록하고 cursor 보조 활성. 발견 조작: `dom.hoverCandidates()`마다 `page.mouse.move` 후 재인벤토리(`discovery:true` step), `dom.scrollContainers()`마다 끝까지 스크롤 후 재인벤토리·`discovery_limits` 기록. iframe: same-origin frame은 `page.frames()`에서 찾아 같은 절차(스니펫 주입·click 좌표는 frame 오프셋 보정).
- [ ] **Step 1: 실패 테스트** — `discovery` 그룹: `capabilities.cdp_listeners===true` · vanilla `addEventListener` 버튼(React 없음)이 found_by `cdp_listener`로 대상화·executed · hover 전용 메뉴 항목 발견·executed · 스크롤 끝 버튼 executed·`discovery_limits` 1 · iframe 버튼 executed(dom_path `iframe[0]/…`).
- [ ] **Step 2**: FAIL. **Step 3**: 구현. **Step 4**: PASS + Codex `cp`. **Step 5 (기록)**.

### Task 4: K1 드라이런 게이트(A8 원본 · 읽기 전용 사본)

**Files:** Create `workspace/eval/web-a8-interaction-observation/dryrun/{README.md,table.md,summary.json}`

- [ ] **Step 1**: A8 `design-ref/`를 scratchpad로 복사해 `python3 -m http.server`로 서빙(원본 무수정). `--browser-channel chrome --viewport 560x1040 --crop-root --root '[data-screen-label="관계인"]' --max-minutes 8`로 **백그라운드** 실행, 로그 폴링, exit 3이면 `--resume` 반복. `--declared` 없이 실행(선언 0 조건).
- [ ] **Step 2**: 표 작성: 발견 대상 수·실행 수·잔여·표면 키 수·소요·캡처 수·`capabilities`·대상별 `found_by` 집계. oracle(`prior/oracle/oracle.json`) 대조 — 관계 8·시 12·시·도 17·시·군 153 항목 executed, 스크림 `click:outside`·Esc, 토글 2상태(윤달·몰라요 2), 빈 목록(행 대상 0 after 상태 존재), 조작군 30 각 행이 어느 step에 대응하는지. «선언 0이므로 전부 스니펫 발견»임을 명기.
- [ ] **Step 3**: 게이트 판정 — 미달·상한 초과·비용(추정 35~120분)이 문제면 규칙(context_T·상한·열거)을 고치고 설계 K1/K2와 이 계획에 «드라이런 결정»으로 적은 뒤 Task 1~3 테스트를 갱신해 재실행. 통과 전 Task 5로 가지 않는다.
- [ ] **Step 4 (기록)**: «eval(web): A8 interaction dry-run gate».

**드라이런 결정(09-14 1차 · 8분 슬라이스 838 step · 대상 803 · 잔여 근사 111 · 시·군 17/153 · 태어난 시 0/12)** — 원인: 컨테이너(구조 오버레이·다이얼로그) identity가 서브트리 텍스트 이름이라 상태마다 바뀌고 owner 연쇄로 안의 대상이 전부 재생성됨(«관계» 트리거 38개·«다음» 58개). D-A: K1 이름 규칙 — «자기 텍스트» 폴백은 항목형 대상(및 대상 후손이 없는 handler)에만, 컨테이너는 aria-label/labelledby 없으면 빈 이름·dom_path. D-B: 클릭 지점이 뷰포트 밖이면 scrollIntoView 복구(상태 해시 불변) 뒤 판정. D-C: hover 발견 후보에서 항목형 kind(menuitem·option·radio·checkbox·switch·tab) 제외(394/838 step이 hover·발견 0). D-B′(4a 실측): 스니펫 인벤토리는 뷰포트 밖 지점을 가림으로 보지 않는다(occluded:false·활성) — 긴 메뉴 항목이 큐에 들도록; 가림 판정은 조작 직전 scrollIntoView 뒤 재인벤토리에서. 반영 = Task 4a(스니펫 accName·hoverCandidates·드라이버 뷰포트 밖 복구·Task 1~3 테스트 갱신) → 리뷰 → 드라이런 재실행. **2차 실측(드라이버 b2bfde1, 2슬라이스 891 step)**: 대상 72·hover 14·unclickable 0·잔여 3(경북·경남·대구)·시·도 9/17·시·군 2/153에서 정체 — 시·도 메뉴가 스크롤 컨테이너라 «끝까지 한 번» 스크롤로는 중간 8항목이 보이지 않고, 복구 재인벤토리(before)는 확장 출처가 아님. D-D: 스크롤 컨테이너는 페이지 단위로 끝까지 훑으며 위치마다 재인벤토리·확장 출처. D-E: 조작 직전 복구 재인벤토리(before)도 확장 출처(acceptState). 반영 = Task 4a 수정 라운드 3 → 재리뷰 → 드라이런 3차. **4차 실측(드라이버 016a2a7, 2슬라이스 868 step)**: 잔여 0·시·도 17/17·시 12/12·수정 흐름 4단계 도달, 시·군 2/153·등록 흐름 4단계 미도달 — 꺼내는 순서 기아(깊은 cascade 트리거·새 context «다음»이 얕은 폼 1단계 재실행 뒤로 밀림). D-F: 순서 = ① 미실행 단위 → ② 트리거의 새 context_T → ③ 재생 불필요(같은 상태 연속 5개 상한) → ④ 접두 상태별 공정성 → ⑤ 얕은 경로 → ⑥ 최신. 반영 = Task 4b(드라이버 순서만) → 스코프 리뷰 → 드라이런 5차. **5차 실측(드라이버 6445bdd, 1슬라이스 251 step)**: 시·군 44/153·시 12/12·시·도 17/17이나 unreachable 50 — 상태 해시 충돌(다른 사람의 수정 폼 3단계가 같은 해시)로 «접두 해시 == 현재 해시» 재생 생략이 계보를 오염. D-G: 재생 생략 조건 = 해시 일치 ∧ 현재 경로 계보 == 항목 부모 경로(K1 문장 보정). 반영 = Task 4c(드라이버) → 스코프 리뷰 → 드라이런 6차. **6차 실측(드라이버 a14d336, 3슬라이스 518 step)**: unreachable 5·시·군 145/153·시 12/12·시·도 17/17·토글 2상태 0·등록 흐름 4단계 미도달. B1: D-E 확장 경로 = 부모 경로(자기 대상 제외). B2: 훑기는 (상태 해시, dom_path)별로 — 전역 dom_path 중복 제거 금지(한계 행만 dom_path당 1회). O1: pop 순위에 «빈 입력(value_empty=true) fill» 칸(②b — 대상 kind input·textarea)을 ② 뒤·③ 앞에. (4d 리뷰 Minor 3 판정: select 단위는 언제나 kind option 대상에 붙어 «빈 입력» 칸에 구조적으로 들 수 없으므로 select 가지는 두지 않는다.) D-H: 이름 있는 handler는 surface 토글형(관찰 surface마다 click 단위) — 스니펫 pure.requiredActions/residual + Python interaction_residual + 두 구현 동일성 fixture 갱신. 반영 = Task 4d(새 opus 구현자: 드라이버 B1·B2·O1 + 스니펫 pure D-H + 검사기 D-H) → 리뷰 → 드라이런 7차(게이트 최종). **6차 문서 재실측(09-14 오후, 7차 전)**: 마지막 슬라이스(run-7 exit 0·3.5분)에서 step 576~3045(2470건)이 전부 «페이지를 다시 열지 못했다: … browser has been closed» unreachable — 정체 판단으로 루프를 중단(12:32:25)할 때 브라우저가 죽자 드라이버가 남은 큐를 1초 안에 전부 unreachable로 비우고 partial:false·exit 0으로 «완주»했다(4차 463·5차 711건도 같은 판형 — 세 라운드의 exit 0은 모두 가짜 완주). D-I: 조작·재생 실패 뒤 `page.isClosed()`면 그 step은 원래 status(failed/unreachable)에 사유 «페이지가 닫혔다: <원문>»으로 적고 루프를 즉시 멈춘다(큐 보존 → partial:true·caps_hit 불변 → exit 3 → `--resume`이 새 브라우저로 잇는다). `--resume` 복원은 «페이지가 닫혔다» step의 키를 처음 한 번은 seen에 넣지 않아 1회 재시도하고, 같은 키가 두 번째로 닫히면 seen에 넣는다(window.close() 버튼의 무한 재시도 방지). 반영 = Task 4d 수정 라운드(드라이버 + 브라우저 테스트 «창 닫기» 라우트 3슬라이스). **7차 실측(드라이버 5923bf1, 슬라이스 2까지 346 step)**: unreachable 0·페이지 소실 0·시·군 153/153·근사 잔여 0. 미달 = 토글 2상태 0: 디자인 시스템 Checkbox는 `<label onClick>` 안 span의 인라인 style(background·border·boxShadow)과 `<i class="icon-check">` 추가로만 켜짐을 그려 루트 tag·class·textContent sha(`surfaceOf`)가 두 상태를 같은 값으로 본다(step 54·86 changes 없음 — 켜진 상태가 어디에도 관찰되지 않음). D-J: surface = 자기 서브트리 모든 요소의 [tag, className, style 속성] 목록 + 자기 텍스트의 sha(K1 갱신). 반영 = Task 4f(스니펫 `dom.surfaceOf` + 브라우저 테스트 «인라인 style 체크박스» 2상태·잔여 0) → 리뷰 → 드라이런 8차(게이트 최종). **8차 실측(드라이버 c9f48ac, 슬라이스 5까지 509 step)**: 관계 8·시 12·시·도 17·시·군 153·토글 2상태 7종·잔여 0·unreachable 0·페이지 소실 0(슬라이스 3에 도달). 미달 = 빈 목록(4명 연쇄 삭제; 최소 관찰 행 수 3). 원인 = ②b(O1)의 빈 «메모» fill이 새 상태마다 최우선(179회·180 context) + ④ 상태별 공정성이 실행 0회인 최신 상태만 선택 → 삭제 연쇄 기아. D-K: ②b 우선권은 identity당 2회까지 · ④ = 단위 공정성(총 실행 수) 뒤 접두 상태 공정성. 반영 = Task 4e 항목 12(드라이버 `rankOf` + 단위 시험 + 브라우저 시험 «삭제 연쇄로 빈 목록 도달») → 9차(게이트 최종 — 빈 목록 미도달이면 한계로 기록하고 진행). **9차 실측(드라이버 3503f20, 슬라이스 1 297 step)**: 대상 31·시 0·시·도 0 — ④a가 진행 버튼(다음·이전, 실행 수↑)을 밀어 폼 3단계 이후 미도달(8차 슬라이스 1은 대상 120·시 12·시·도 17). D-K′: ④a 되돌림(②b 상한만 유지). 빈 목록 = A8 정적 case related/empty로 동결되는 데이터 상태 → 게이트 제외·K2 한계 기록. 반영 = Task 4e 수정 라운드(④a 제거·delete-chain 시험 제거·②b 상한 시험 유지) → 10차(최종 게이트). **10차 실측(드라이버 4ea5478, 6슬라이스 871 step, 48분)**: 관계 8·시 12·시·도 17·시·군 153·토글 2상태 7·스크림/바깥·Esc·잔여 0(세 구현 일치)·unreachable 0·페이지 소실 0 → **Task 4 게이트 통과**(빈 목록 = 정적 case 한계).

### Task 5: 검사기 v2(`check_design_evidence.py`)

**Files:** Modify `check_design_evidence.py`; Create `scripts/test/test_interaction_evidence.py`, `scripts/test/fixtures/interaction/r3-steps.json`

**Interfaces (Produces):**
```python
def validate_inputs(build, project, *, require_review=True, legacy_v1=False) -> tuple[dict, str, list]
def _source_observation(...)   # version 1|2; v2 = v1 필드 + 'interactions'; v1은 legacy_v1일 때만 통과(그 외 'interaction evidence required')
def validate_interactions(build, case, observed, archive_path, reference_root, spec, issues, items) -> None
def interaction_residual(doc: dict) -> list[tuple[str, str, str | None]]   # pure.residual과 동일 결과
def linked_surfaces(doc: dict) -> set[str]
def collector_assets_ok(doc: dict, assets_dir: Path) -> bool    # assets_dir = Path(__file__).resolve().parents[1] / 'assets'
```
검사(K3): exact-field 재귀(K7) · archive_sha256/entrypoint 일치 · 수집기 sha · 루트(`screen-meta.source_sha256 == case.entrypoint.sha256`일 때 selector 정확 일치) · `outside_root.count>0`→`excluded_regions` 필수 · served(entrypoint sha·manifest 행 sha·percent-decode basename; 2xx same-origin만) · `content_crop == case.viewport` · 잔여 ∅(예외 제외) · 표면 연결(added≠∅ surface_key ⊆ cases.reached_by surfaces ∪ 표면 예외) · archive case `reached_by` **필수**(`initial` 또는 step n 존재·`reference_capture.sha256 == after.capture.sha256`) · 예외 행 형식·`approval_quote` 10자 이상·NFC/공백 정규화 원문 대조·앵커 실존·10% 상한·stdout 전량 출력 · `observed_at` tz · `partial`/`caps_hit` 정합 · `environment_error≠null` → exit 1 · manifest 행 `carried_from`(64 hex) 허용·그 외 미지 필드 거부 · design-input `interaction_exclusions`(top)·`reached_by`(case) 허용, 정적/이미지 case의 `reached_by`는 거부 · digest에 interactions·declared·캡처 편입(중복 dedupe).
- [ ] **Step 1: 실패 테스트** — 정상 v2 통과 · 잔여 1 → 2(메시지에 튜플) · failed만 → 2 · partial∧잔여>0 → 2(메시지에 caps_hit·잔여 수) · partial∧잔여 0 → 0 + stdout 한 줄 «partial(caps_hit=…)·잔여 0» · `partial:false`∧`caps_hit≠[]` → 2 · `executed`∧`error≠null` → 2 · path→미존재 step → 2 · 비활성/가림 대상 executed → 2 · `n` 중복 → 2 · `served` 누락 → 2 · served entrypoint sha 불일치(변형본) → 2 · `steps[0].exempt` → 2 · 수집기 sha 불일치 → 2 · 루트 selector 불일치 → 2 · outside_root>0 미선언 → 2 · crop 불일치 → 2 · added≠∅ 표면 미연결 → 2 · `reached_by` 없는 archive case → 2 · reached_by 캡처 sha 불일치 → 2 · 예외 quote 미존재/9자/앵커 없음/11% → 2 · 예외 있을 때 stdout에 전량 출력 · `environment_error` → 1 · `carried_from` 행 통과·`foo` 행 거부 · declared 파일 변경 시 digest 변화 · v1 observation(legacy_v1=False) → 2, True → 통과 · 이미지 단독·정적 HTML 기존 테스트 무변 · **두 구현 동일성**: `expected/*.json` 3개 + `r3-steps.json` + 반례 fixture 전부에 대해 `interaction_residual`이 `node -e` `pure.residual` 출력과 동일(node 부재 시 테스트 실패) · **r3 fixture**: `prior/coordinator-repair` 로그를 옮긴 `r3-steps.json`에서 잔여가 관계 4·시 15·시·군 30 이상.
- [ ] **Step 2**: FAIL. **Step 3**: 구현. **Step 4**: PASS + `fixtures_design_evidence.sh` green + Codex `cp`. **Step 5 (기록)**.

### Task 6: backstop legacy v1 규칙

**Files:** Modify `backstop.py`; Modify `test_design_evidence.py`

`def legacy_v1_allowed(root, build, diff_base) -> bool`: base = diff_base or 'HEAD'; `git ls-files -- <build>` 비어 있지 않음 ∧ `git diff --quiet <base> -- <build>` ∧ `git ls-files --others --ignored --exclude-standard -- <build>` 빈 출력. 순회에서 `validate_inputs(build, root, legacy_v1=…)`; 허용 시 `[info] legacy v1 observation: <build>`.
- [ ] **Step 1: 실패 테스트** — 완료 build(v1·추적·무변경) → green + 통지 · untracked 추가 → BLOCKER · ignored build(`.gitignore`에 `.dddjango-web/`) → BLOCKER · 추적 파일 0 → BLOCKER · diff-base 없이 HEAD 앵커 동일.
- [ ] **Step 2**: FAIL. **Step 3**: 구현. **Step 4**: PASS + Codex `cp`. **Step 5 (기록)**.

### Task 7: `archive_design.py --compare-build`

**Files:** Modify `archive_design.py`; Modify `test_design_archive.py`

```python
def compare_manifests(new: dict, base: dict, carried: set[str], build: Path, out: Path) -> dict
# rows[{local_path,status:same|changed|added|removed|carried,size_bytes,sha12,mtime,carried_from?}], summary, exit 0|3|4
```
CLI `--compare-build BUILD --compare-out PATH [--carried LOCAL_PATH…]`. base = `BUILD/design-input.json` `manifests[0]`. 자동 carried = staging 파일 `source`가 `reference_root`·`BUILD/_history`·**현재 `--out`의 상위 `_staging-<ts>`를 제외한** `BUILD/_staging-*` 하위. 명시 `--carried`는 entrypoint 의존성 closure 밖에만(closure 안 → exit 1 «carried dependency»). carried 행에 `carried_from`. exit 1 오류·missing·carried dependency / 3 / 4 / 0.
- [ ] **Step 1: 실패 테스트** — 전부 same → 0 · 1파일 변경 → 3 · 추가/삭제 → 3 · closure 밖 PNG `--carried` → 4 + `carried_from` · closure 안 carried → 1 · staging source가 reference_root 하위 → 자동 carried 4 · **staging = `BUILD/_staging-<ts>/export`(현재 out의 상위) → 전부 same·exit 0** · `--compare-out` 형식(기준 sha·mtime) · 기존 archive 테스트 무변.
- [ ] **Step 2**: FAIL. **Step 3**: 구현. **Step 4**: PASS + Codex `cp`. **Step 5 (기록)**.

### Task 8: reference 문서(byte 미러)

**Files:** Modify `design-evidence.md`, `design-acquisition.md`; `cp` → Codex

- [ ] **Step 1**: design-evidence.md — source_observation **version 2** · «`interactions.json` version 1» 절(K7 블록 + 필드 의미 + 잔여 단위·표면 키·`reached_by` 필수·예외·served·루트·crop·live·found_by) · design-input `interaction_exclusions`·`reached_by` · manifest `carried_from` · exit 표에 «3·4 = archive_design 전용» · legacy v1 = backstop git 조건 · **«Limits» 소절**(정적 수집 경로 비적용·역순 cascade·hover 전용·cross-origin iframe·가상화·비React+CDP 없음·값만 바뀐 상태 캡처·staging 출처·C#3 후속 후보·motion-notes step 인용 권고).
- [ ] **Step 2**: design-acquisition.md — §2 «재동결» 소절(K4 CLI·exit·carried·`_staging-<ts>`·삭제·`refreeze-diff.json`·실행 시점·**새 기준 설치 순서**: `design-ref` 삭제 → `_staging-<ts>/design-ref` 이동 → manifest 교체) · §3 «6. 조작 상태 수집»(드라이버 인자·백그라운드+`--max-minutes 8`+`--resume`·`--declared`·MCP 트램폴린 `async (page) => (await import('<abs>/observe_interactions.pw.js')).default(page, {...})`·산출·잔여/표면 보완 순서) · §4 v2 포인터.
- [ ] **Step 3**: `cp` → Codex; `cmp` 4파일 동일. **Step 4 (기록)**.

### Task 9: Coordinator·리뷰어·REQUEST_GUIDE(+Codex 의미/byte)

**Files:** `commands/dddjango-web.md`(L134~137 step 5-4 · L140 뒤 · **L142~143 step 5-6 «ready 직전 입력 게이트» 문단** · L168 · L202 · L9/L231), `agents/design-review-web.md`(G0 절), `REQUEST_GUIDE.md`(§5 끝); Codex `skills/dddjango-web/SKILL.md`(L157·L162 뒤·L164·L225·L8/L255), `skills/dddjango-web-design-review-web/SKILL.md`(L24 절), `codex-dddjango-web/REQUEST_GUIDE.md`(byte)

- [ ] **Step 1**: step 5-4 재동결 문장 → K4(요청 시에만·`--compare-build`·exit 0/3/4·`refreeze-diff.json` sha를 `visual-check.md` ①·build-state에 기록·exit 4 배너 선택·차이 시 새 기준 설치 순서). «출력이 유일한 근거다» 한 문장, 금지문 누적 없음.
- [ ] **Step 2**: 동적 표현 관찰 문단 뒤 «**조작 상태 수집**» 문단(K6 첫 항목 + 실행 경계: 모듈 경로·버전·채널/CDP를 scope.md에 기록 · 백그라운드 실행·`--max-minutes 8`·exit 3이면 `--resume` · 환경 부재 시 blocked+사유 enum+G0 배너 · Node 기본·MCP 트램폴린).
- [ ] **Step 3**: 입력 게이트 문단 입력 목록에 `interactions.json`·선언·예외·`refreeze-diff.json` 추가 + «예상 판정·pass 예시를 전달하지 않는다». 경계 절 «직접 쓰는 것»에 기계 산출 3종·서기 1종. Phase 2 ⑤ 커밋 목록. 수정 모드 G0 «재동결 질문» 문장 유지·선택 시 K4 보고.
- [ ] **Step 4**: design-review-web.md G0 — 감사 항목 ①~④ + «같은 핸들러·데이터 변이·같은 인스턴스를 이유로 대상이나 결과 상태를 면제하지 않는다.»
- [ ] **Step 5**: REQUEST_GUIDE §5 끝 한 문단: «엔진/JSX 시안(Claude Design 등)은 Node 22 이상과 Playwright 모듈, 그리고 Google Chrome(또는 CDP로 붙일 브라우저)이 필요합니다. 플러그인은 설치하지 않으며 경로만 알려 주시면 됩니다. 없으면 시안 준비가 blocked로 멈춥니다.» Codex `cp`.
- [ ] **Step 6**: Codex SKILL 두 파일 같은 의미(`${SKILL_DIR}`·`spawn_agent`). `claude plugin validate dddjango-web --strict` exit 0 · `PYTHONUTF8=1 python3 workspace/tools/request_guide_contract.py` exit 0.
- [ ] **Step 7 (기록)**.

### Task 10: Makefile·DEVELOPMENT·픽스처 러너

**Files:** `Makefile`(`verify-web`·신규 `verify-web-browser`·`release-web`·`_release` DRY 안내), `docs/DEVELOPMENT.md`(§2 node 필수·§5 표·§6), `scripts/test/fixtures_interactions.sh`

- [ ] **Step 1**: `fixtures_interactions.sh` = `python3 test_interaction_evidence.py` · `node test_interaction_audit.mjs` · `node test_observe_interactions.mjs`(env 없으면 테스트 파일이 SKIP 출력·exit 0). 임시 캡처는 `fs.mkdtemp(os.tmpdir())`.
- [ ] **Step 2**: `verify-web`에 references `cmp -s` 4행. `verify-web-browser`: `DDDJANGO_WEB_PLAYWRIGHT_MODULE`·(`DDDJANGO_WEB_BROWSER_CHANNEL` 또는 `_CDP`) 필수 → `DDDJANGO_WEB_REQUIRE_BROWSER=1 node test_observe_interactions.mjs`. `release-web: verify-web-browser _release`; `DRY=1`이면 `verify-web-browser`는 안내만 출력(`_release` DRY 안내 [1]~[7]에 «[0] 브라우저 픽스처» 추가).
- [ ] **Step 3**: DEVELOPMENT §2에 «node ≥ 22 필수(verify-web)», §5 표 `make verify-web-browser` 1행, §6 `make release-web` 선행 조건 한 줄.
- [ ] **Step 4**: `make verify-web` exit 0 · `DDDJANGO_WEB_PLAYWRIGHT_MODULE=… DDDJANGO_WEB_BROWSER_CHANNEL=chrome make verify-web-browser` exit 0 · `git diff --check`. **Step 5 (기록)**.

### Task 11: 평가(설계 «검증 및 순서» 1~5)

**Files:** `workspace/eval/web-a8-interaction-observation/{native,refreeze,samples}/…`, `README.md`

- [ ] **Step 1 (검사기 red)**: A8 build 사본에 새 검사기 `--phase inputs` → exit 2 «interaction evidence required» 기록.
- [ ] **Step 2 (재동결)**: A8에 `_raw-export`는 없다(manifest `source_root`만 잔존). `design-ref` 사본을 **BUILD 밖** staging으로 두고 `--compare-build` → exit 4(same 18 + PNG 4 `--carried`) / `_ds_bundle.js` 1바이트 변형 → exit 3 / 이전 `design-ref`를 `BUILD/_staging-old/`에 두고 그 경로를 source로 재보관 → 자동 carried → exit 4. 출력 JSON 보존.
- [ ] **Step 3 (native Coordinator)**: 스냅샷 = 작업 트리 `dddjango-web/` 복사(`--plugin-dir`). scratch A8 = 워크트리 복제 후 `git init && git add -A && git commit -m scratch`(git 앵커·backstop 유지). 호출 = `prior/coordinator-repair/invocation.json` 판형(`--print --plugin-dir … --setting-sources user --strict-mcp-config --mcp-config <playwright MCP 없음 — Node 경로만> --no-session-persistence --output-format stream-json --verbose --tools Read,Grep,Glob,Skill,Bash,Edit,Write,ToolSearch,Agent --allowedTools …,Agent,Bash(node *),… --add-dir <scratch A8> --add-dir <스냅샷>`; dddjango 저장소·`prior/`는 열지 않는다). 프롬프트 = `/dddjango-web` 기존 화면 관계인 재개 + 평가 계정 사전 승인(«기존 폴더 ⓐ 재사용·재동결 안 함·G0 승인·Phase 1 이후 비허용») + 실행 경계(모듈 경로·`--browser-channel chrome`·백그라운드·`--max-minutes 8`·`--resume`) + «평가 폴더·`/tmp` 미접근». 정답(드롭다운·체크박스·스크림) 미제공. 판정: 드라이버 실행·잔여 0·예외 0·표면 연결·독립 G0 리뷰(Agent) 호출·`--phase inputs` exit 0. 대조군 = «구 Coordinator + 신 검사기»(`git show dddjango-web--v1.1.7:dddjango-web/commands/dddjango-web.md` 등 commands/agents만 v1.1.7, scripts/assets/references 신판 혼합 스냅샷) → prepare exit 2에서 멈추는 것을 기록. raw transcript는 task temp(`/tmp/dddjango-web-interaction-evidence-20260913/native/`)에, 저장소엔 프롬프트·invocation·판정·집계만.
- [ ] **Step 4 (A8 밖 표본)**: `workspace/eval/web-design-source-integrity/2026-09-07/fixture`(정적 HTML+JS 위저드)·`web-a8-visual-fidelity/role-browser-app/source.html` 드라이버 실행 → 발견·실행·capabilities·discovery_limits 기록(게이트 아님).
- [ ] **Step 5**: `README.md`(절차·수치·한계·«기존 지침도 통과하면 개선 주장 금지»·native 전체 성공으로 확대 금지). **기록**.

### Task 12: 독립 구현 리뷰·전체 검증·게이트

- [ ] **Step 1**: 독립 구현 리뷰 1기(전체 diff + Task 4·11 증거 + 설계 K1~K8 대조·1.1.8~1.1.12 재도입 검사·미러 정합·before-hashes 밖 파일 무변) → `review/implementation-review.md`. Important 이상은 같은 Task에서 해소·재검토.
- [ ] **Step 2**: `make verify-web` → `… make verify-web-browser` → `make verify`(마지막 로그 `verification/final-verify.log`) → `claude plugin validate dddjango-web --strict` → `git diff --check`. 봉인 재발행 필요 시 DEVELOPMENT §4.
- [ ] **Step 3**: 사용자 결정 게이트(10줄 브리프) — ① 되돌림 18파일을 별도 커밋 `revert(web): restore 1.1.7 runtime as baseline`으로 먼저 기록(기본) 또는 계획 파일만 커밋·나머지 보관 ② `docs/master.html`·lanes md는 보관(사본)→릴리즈→복원·`before-hashes.json`으로 byte 무변 확인(refreeze-resume 선례) ③ 기능 커밋 `fix(web): mechanical interaction evidence and refreeze comparison` ④ `make release-web`(patch 1.1.13) ⑤ A8 재관찰 착수. 승인 전 커밋·릴리즈·설치본은 건드리지 않는다.

---

## 행동 시험과 합격 기준

| 시험 | 입력 | 합격 |
|---|---|---|
| T1 드라이런(Task 4) | A8 design-ref 사본·oracle·선언 0 | 발견≥30 조작군·8/12/17/153·스크림/바깥/Esc·토글 2상태·빈 목록이 스니펫 발견(found_by)으로 집계·잔여 0·상한 안 |
| T2 검사기 검출력(Task 5) | r3 fixture·반례 fixture 전량 | 미클릭 항목 잔여 출력·반례 전부 exit 2(환경 오류는 1)·정상 통과·두 구현 동일 |
| T3 재동결(Task 11-2) | A8 사본 | exit 4 / 변형 3 / 이전 보관본 자동 carried 4 |
| T4 native(Task 11-3) | 신 스냅샷·git scratch A8·사전 승인 프롬프트 | 정답 없이 드라이버 실행(백그라운드·resume)·잔여 0·예외 0·독립 G0(Agent)·inputs exit 0; 대조군은 prepare exit 2 |
| T5 일반화(Task 11-4) | A8 밖 표본 2 | 기록만 |

## 사용자 결정이 필요한 조건(기본값)

- 브라우저 기동 = `--browser-channel chrome`(설치 0), 대안 `--cdp`. 메인테이너 환경에도 chromium 1243을 설치하지 않는다.
- 릴리즈 전 되돌림 18파일 = 별도 `revert(web)` 커밋으로 기록(Task 12 브리프에서 재확인). `docs/master.html`·lanes md = 보관→복원.
- Node 최소 = 22(REQUEST_GUIDE 문구·DEVELOPMENT §2), `make verify`가 node를 필수로 삼는다.
- raw transcript = task temp 보존(저장소 밖). `make release-web DRY=1`은 브라우저 게이트를 안내만 한다.
- Task 4 게이트 미달로 K1/K2 규칙을 바꿔야 할 때·실행 중 모듈 경로 휘발 시 브리프로 보고.

## 현재 상태

2026-09-13 계획 v2(계획 리뷰 반영). Task 0 Step 1~3 완료(보존 81·이관 39·메모 연결), Step 4 브라우저 실측 완료(channel chrome OK). 코드·규범 무접촉. 다음 = 사용자 승인 → Task 0 Step 4~5 기록 → Task 1.
