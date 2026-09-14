# 계획 적대 검토 — 웹 시안 조작 상태 증거·재동결 기계 대조 구현 계획

- 대상: `workspace/plan/2026-09-13-web-interaction-evidence.md`(이하 «P», 행 번호는 이 파일). 설계 v2 `workspace/design/2026-09-13-web-interaction-evidence.md`(«D», K1 L41~48 · K2 L52~63 · K3 L67~76 · K4 L80~91 · K5 L95~98 · K6 L102~107 · K7 L111~132 · K8 L136~147 · 검증 L151~158 · 한계 L162~165). 진단 `diagnosis.md`, 검토 4건 `rv-{A,B,C,R}.md`, 선례 계획 4건, `docs/DEVELOPMENT.md` §4~§6, `AGENTS.md`, `Makefile`.
- 계획이 지목한 실제 파일은 현재 작업 트리 내용으로 대조했다(`commands/dddjango-web.md`·`agents/design-review-web.md`·`REQUEST_GUIDE.md`·Codex SKILL 2·`check_design_evidence.py`·`archive_design.py`·`backstop.py`·테스트 2·`run_fixtures.sh`·`fixtures_design_evidence.sh`·`render_audit.js`·`request_guide_contract.py`·`.gitignore`·references 2). A8 원본·`/tmp` 평가 폴더·`~/.npm`·`~/Library/Caches`는 읽기만 했다. `make verify`·서버·브라우저·`plugin validate`는 실행하지 않았다(MCP `browser_run_code_unsafe`는 스키마만 조회).
- 심각도 BLOCKER / MAJOR(=Important) / MINOR / 검증됨. 3축 **정합**(현행 검사기·규범·미러·선례) · **일반화**(A8 밖) · **무손실**(거짓 통과·보장 손실 없음). «추측»은 파일로 확인하지 못한 판단이다. Serena·Graphify는 워크트리에 opt-in 표식이 없어 쓰지 않았다.

---

## ① 설계 대응 표 — D의 K 문장 → P의 Task/Step

판정: ✓ = 명시된 Task/Step이 문장을 구현한다 · **부분** = 위치는 있으나 정의·테스트·미러가 빠짐(→ ②의 번호) · **누락** = 어느 Task에도 없음.

### K1 탐색 키·잔여·상한

| D 문장 | P 위치 | 판정 |
|---|---|---|
| L41 identity = `{role,name,input_type,owner,owner_items_hash}` sha12 · name 우선순위 · 빈 이름만 dom_path | T1 L67 `identityOf`, 테스트 L79~80 | ✓ |
| L41 «한 인벤토리에서 identity 충돌하면 그때만 dom_path 추가(순번 접미 없음)» | — | **누락**(m10) |
| L42 인벤토리 항목 7필드 · 활성 = enabled ∧ ¬occluded | T2 L98 entries | ✓ |
| L43 state context(활성 identity·checked·surface·value_empty·face) | T1 L68 `stateContext` | ✓ |
| L44 큐 키 `(identity, action, option, context_T)` · 트리거=앞 트리거 face만 · 메뉴 항목=owner face 제외 · 그 밖 face 전체 제외 | T1 L69 `contextFor`, 테스트 L81(트리거·버튼) | **부분** — 메뉴 항목 규칙 테스트 없음(m10) |
| L45 잔여 단위 `(identity, action, option)` · failed/unreachable/unclickable 미계수 · `click:outside`≡스크림 `click` | T1 L73 `residual`·테스트 L83, T5 L148 `interaction_residual` | **부분** — 동치 규칙 테스트 없음(m10) |
| L46 한 표·두 구현·fixture 짝 4종 | T1 L86 expected.json, T5 L154 «두 구현 동일성» | **부분** — 입력 형식 불일치(M11) |
| L47 상한 90/8000/24 · `partial`·`caps_hit` · `--resume`(archive/served sha 동일) · 접두 해시 최적화 | T3 L124~125, 테스트 L127(`--max-steps 5`·resume) | **부분** — max-minutes·max-depth·sha 불일치 resume 거부 테스트 없음(M6) |
| L48 A8 드라이런 게이트(oracle 30/8/12/17/153·스니펫 발견 vs 선언 구별) | T4 L134~137 | ✓(집계 정의는 m9) |

### K2 대상 열거

| D 문장 | P 위치 | 판정 |
|---|---|---|
| L52 루트 selector · 범위 = 루트 ∪ 오버레이 · 루트 미발견 실패 | T2 L97 root, T3 L124 exit 1 | ✓ |
| L53 핸들러 보유=대상 · 감지 3채널(React props·onclick·CDP `DOMDebugger.getEventListeners`) · cursor 보조 조건 · 의미 컨트롤 목록 · aria-hidden 제외 · disabled/aria-disabled/inert · `capabilities` | T2 L103(props·onclick·listenerIds·cursor), T3 L121 `listeners:'cdp'` | **부분** — 의미 컨트롤 목록·`inert`·CDP backendNodeId→요소 매핑 방법·CDP 채널 테스트 없음(M8) |
| L54 가림 `elementFromPoint` | T2 L109, 테스트 L107 | ✓ |
| L55 클릭 지점 3×3+모서리 · 없으면 `unclickable` | T2 L100 | **부분** — unclickable 테스트 없음(M6) |
| L56 오버레이 role/구조(80%·absolute/fixed·핸들러/z-index) · `click:outside`+`key:Escape` · 스크림형/비스크림형 지점 · 무변화 정상 | T2 L101·L109, T3 테스트 L127(스크림) | **부분** — 비스크림형(메뉴) 바깥 클릭 테스트 없음(m10) |
| L57 토글 checked/surface · 두 상태 실행 | T1 L82, T3 L127 | ✓ |
| L58 native select 옵션 = 대상(owner=select, action=select) | T3 L125 `selectOption`, fixture L105 | **부분** — 옵션 3 전부 executed 단언 없음(M6) |
| L59 발견 조작 hover/스크롤 · `discovery_limits` · 새 대상 큐 진입 | T3 L125 «`discovery:true` step» 한 구절 | **부분** — 규칙(`:hover` 매칭·overflow 컨테이너)·fixture·테스트 전무(m2) |
| L60 이탈 터미널 step · loopback 기본 · `--cdp` origin 허용 | T3 L124~125, 테스트 L127(이탈 링크) | **부분** — 원격 URL 거부 테스트 없음(M6) |
| L61 fill 표본 규칙 · 빈 값도 executed·`changes.values` | T3 L125 | **부분** — 테스트 없음(M6) |
| L62 `--declared` 늘리기만 · `declared_unmatched` · digest 편입 | T2 L99·L96, T3 L124, T5 L152 | **부분** — 드라이버·검사기 테스트 전무(m3) |
| L63 same-origin iframe 순회 · cross-origin/가상화 `discovery_limits` · 외부 스크립트 실패 `environment_error`→검사기 exit 1 | T3 L124 exit 1, T5 L152 | **부분** — iframe 순회는 어느 Task에도 없음(M8) · environment_error→exit 1 테스트 없음(M6) |

### K3 검사기 신뢰 경계·동결 연결·v1

| D 문장 | P 위치 | 판정 |
|---|---|---|
| L67 수집기 sha byte 대조 | T5 L152·L154·L155(`parents[1]/'assets'`) | ✓ |
| L68 루트 규칙(`screen-meta.source_sha256 == entrypoint.sha256`일 때) · fingerprint · `outside_root`→`excluded_regions` | T5 L152, 테스트 L154 | ✓ |
| L69 served(entrypoint sha·manifest 행·percent-decode basename·404/외부 제외) | T3 L125, T5 L152, 테스트 L154 | ✓ |
| L70 `browser_viewport`·`content_crop == case.viewport` · viewport별 파일 | T3 L124 `--viewport --crop-root`, T5 L152 | ✓ |
| L71 state_hash 정의 · `role=status`·`aria-live` 제외 · 재생 종점 불일치 `unreachable` | T1 L70, T3 L125 | **부분** — 제외를 «열거 자체»로 옮김(M5) |
| L72 exact-field 재귀 · 반례 10종 | T5 L152·L154 | **부분** — 반례 6종 테스트 누락(M6) |
| L73 예외 행 형식 · approval_quote ≥10자·NFC·앵커·10% · stdout 전량 · G0 배너 1급 · scope_ref 사용자 출처 | T5 L152·L154, T9 L194 | **부분** — 10자 규칙·stdout 테스트 없음(m14·M6) |
| L74 표면 키 정의 · added≠∅ 표면마다 `reached_by`/예외 · `reference_capture.sha256 == after.capture.sha256` · 캡처는 initial·added·navigated만 · 빈 목록 UI 도달 | T1 L71·L74, T5 L152, T3 L127(캡처 수·빈 상태) | **부분** — `reached_by` 없는 archive case의 처분 미정(M4) |
| L75 prepare/inputs는 v2만 · backstop 순회 git 무변경 legacy(`--diff-base` 또는 HEAD) | T5 L146, T6 L161~164 | **부분** — 무시/미추적 build 통과(M7) |
| L76 design-input `interaction_exclusions`·`reached_by` allowed · manifest 행 `carried_from` 허용 | T5 L152 | **부분** — 허용 테스트·기타 필드 거부 테스트 없음(M6) |

### K4 재동결

| D 문장 | P 위치 | 판정 |
|---|---|---|
| L81~86 CLI · 기준 `manifests[0]` · `refreeze-diff.json` 내용 · visual-check ①·build-state에 sha | T7 L172~175, T8 L185 | **부분** — visual-check/build-state 기록 지시 없음(m6) |
| L87 exit 0/3/4/1 | T7 L175·L177 | ✓ |
| L88 carried: source가 reference_root·**이전** `_staging-*`·`_history` 하위 · `--carried` closure 밖 · `carried_from` · staging 위치 · `_staging-*` 삭제 · 출처 한계·mtime 표 | T7 L175, T8 L185 | **부분** — «이전» 조건 누락(M2) |
| L89 요청 시에만 · step 4 질문 v1.1.7 그대로 | T9 L193·L195 | ✓ |
| L90 exit 4 배너 선택 · 차이(3) → 새 기준 설치 → 같은 라운드 재관찰 | T9 L193 | **부분** — «새 기준 설치» 절차 미정(m6) |
| L91 `_history/vN` 비규범 | P L16 재도입 금지(간접) | **부분** — 문장으로 명시 없음(m11) |

### K5 실행 환경

| D 문장 | P 위치 | 판정 |
|---|---|---|
| L95 단일 함수 파일 · 래퍼 · MCP 트램폴린(`filename` 불사용) · 양 경로 `driver_sha256` · LLM 루프 없음 · Node 기본 · resume | T3 L119~125, T8 L185, T9 L194 | **부분** — `collector.path`(node/mcp) 판별 입력 없음(m4) · Bash 타임아웃 대책 없음(M3) |
| L96 미설치 · 경로·버전·기동 방식 scope.md 기록 · blocked enum · REQUEST_GUIDE · node_modules 금지 | T9 L194·L197, P L17 | **부분** — scope.md 기록 문장 없음(m5) · Node 버전 문장 근거 없음(m12) |
| L97 순수 함수 항상 · DOM fixture 목록 · SKIP 로그 · `verify-web-browser`(SKIP=실패) · `release-web` 선행 · DEVELOPMENT §6 | T2 L105, T10 L205~207 | **부분** — `_release` DRY 안내·DRY=1 동작 미정(m13) · fixture에 hover/스크롤 없음(m2) |
| L98 검사기 반례 손 fixture · r3 로그 = 테스트 fixture 한정 | T5 L154, P L20 | ✓ |

### K6 규범·역할·미러 / K7 / K8 / 검증 및 순서 / 한계

| D 문장 | P 위치 | 판정 |
|---|---|---|
| K6 L102 step 5-4 재동결 문장 교체 · «조작 상태 수집» 문단 · 보완 의무 · visual-check ① 수치 | T9 L193~194 | ✓(앵커는 m1) |
| K6 L103 step 5-7 입력 · «예상 판정 미전달» | T9 L195 | ✓ |
| K6 L104 리뷰어 감사 ①~④ · 면제 금지 문장 · 1.1.11 문장 미사용 | T9 L196 | ✓ |
| K6 L105 경계 절 «직접 쓰는 것» · Phase 2 ⑤ · 수정 모드 G0 | T9 L195 | ✓ |
| K6 L106 `${CLAUDE_PLUGIN_ROOT}`/`${SKILL_DIR}` · `import.meta.url` · references cmp | T9 L198, T10 L206 | ✓ |
| K6 L107 정적 경로 한계 · C#3 후속 후보 기록 · motion-notes 인용 권고 | — | **누락**(m11) |
| K7 스키마 = 단일 출처 | T8 L184, T5 L152 | ✓ |
| K8 12건 채택 | P L248 | ✓ |
| 검증 1~6 | T4·T5·T11·T12 | ✓(대조군 구성 방법은 m8, 호출 인자는 M9) |
| 한계 4항 문서화 | — | **부분** — 어느 reference에 적는지 없음(m11) |

명시 확인 요청 항목의 요약: hover/스크롤 **부분** · `declared_unmatched` **부분** · `excluded_regions` ✓(검사기)/부분(드라이버 테스트) · `environment_error` **부분** · exit 1/3 매핑 ✓ · `carried_from` 검사기 허용 ✓/테스트 누락 · `reached_by` sha ✓/필수 여부 **미정** · 예외 stdout ✓/테스트 누락 · MCP 트램폴린 ✓ · `verify-web` cmp ✓ · DEVELOPMENT ✓(§2 node 누락) · Codex 미러 = SKILL 2·REQUEST_GUIDE·references ✓, **scripts·assets 복사 단계는 어느 Task에도 없음**(m16 — `make verify-web`이 잡는다).

---

## ② 발견 목록(심각도순)

### B1. [BLOCKER · 일반화·정합] 브라우저 실행 경로가 미확정이고, 이 머신의 유일한 Playwright 모듈은 설치된 브라우저와 맞지 않는다

근거:
- P L17 «드라이버는 `--playwright-module <dir>` 또는 `NODE_PATH`로 외부 모듈을 해소», P L108 «모듈 없음이면 Task 4 전에 모듈 경로를 확보한다 — `~/.npm/_npx/*/node_modules`의 playwright는 휘발성». 계획은 «모듈»만 말하고 **브라우저 바이너리**를 말하지 않는다.
- 실측: `~/.npm/_npx/9833c18b2d85bc59/node_modules/playwright/package.json` = `1.63.0-alpha-2026-08-31`, 같은 폴더 `playwright-core/browsers.json`의 chromium revision = **1243**. `~/Library/Caches/ms-playwright`에는 `chromium-1223`·`chromium-1234`·`chromium_headless_shell-1223/1234`·`ffmpeg-1011`뿐이다. 즉 `chromium.launch()`는 «Executable doesn't exist» 계열로 실패한다(**추측** — Playwright의 리비전 고정 규칙에 따른 귀결이며 실행하지 않았다).
- rv-C #19(L204)가 이미 «`EPERM ~/Library/Caches/ms-playwright`·CDP 50234 우회»를 실측으로 적었고, `coordinator-live/invocation.json`은 전용 Chrome + CDP였다. A8 `build-state.json`의 «Node Playwright chromium1234»는 다른 설치본의 기록이다.
- 영향: Task 2 Step 2·Task 3 end-to-end·Task 4 게이트·Task 10 `verify-web-browser`·Task 11-3 native 전부가 브라우저 기동에 걸린다. 계획대로면 Task 2 Step 2에서 멈추고 «확보한다»는 실행자 재량이 된다.

권고(실행 진입 조건): Task 0에 «브라우저 기동 방식 확정» 단계를 넣고 셋 중 하나를 사용자 결정으로 고른다 — ⓐ `--cdp <ws>`로 전용 Chrome에 붙는다(선례 `coordinator-live`; K2 L60·K5 L95와 정합, 저장소·플러그인 설치 0) ⓑ 드라이버에 `--channel chrome` 옵션을 두어 설치된 Google Chrome을 쓴다(브라우저 캐시 불필요) ⓒ 메인테이너 환경에 한해 `PLAYWRIGHT_BROWSERS_PATH`를 지정해 1243을 설치한다(사용자 앱·저장소 밖). 선택 결과(모듈 경로·`package.json` 실값·브라우저 실행 파일·기동 방식)를 Task 0 `execution-notes.md`와 Task 11-3 scope 프롬프트에 고정한다. `verify-web-browser`의 요구 env에 브라우저 지정 변수(예: `DDDJANGO_WEB_BROWSER_CDP` 또는 `…_CHANNEL`)를 추가한다.

### M1. [MAJOR · 정합] `.pw-cache/`를 `scripts/test/` 아래 두면 `verify-web`의 byte 미러 `diff -rq`가 red다 — `.gitignore`로는 막지 못한다

근거: P L207 «`.gitignore`에 `dddjango-web/scripts/test/.pw-cache/`(드라이버 테스트 임시 캡처)». `Makefile` L96 `diff -rq --exclude=__pycache__ dddjango-web/scripts codex-dddjango-web/skills/dddjango-web/scripts`는 `.pw-cache`를 제외하지 않으므로 한쪽에만 생긴 디렉터리가 «Only in …»으로 exit 1이다. `make verify` → `verify-web` → `run_fixtures.sh` → `fixtures_interactions.sh` → (모듈이 있으면) DOM 테스트가 캡처를 쓴 **직후** 같은 타깃의 L96이 실행된다(L94→L96 순서). 현행 Python 테스트는 전부 `tempfile.TemporaryDirectory`를 쓴다(`test_design_evidence.py` L31, `test_design_archive.py` L23).

권고: 테스트 임시 캡처는 OS 임시 폴더(`fs.mkdtemp(os.tmpdir())`)에 쓰고 `.gitignore` 항목을 만들지 않는다. 저장소 안 경로를 고집하면 L96·L97 두 줄에 `--exclude=.pw-cache`를 함께 추가하고 Codex 쪽 경로도 ignore한다.

### M2. [MAJOR · 정합·무손실] Task 7의 자동 carried 조건이 «이전» staging을 빠뜨려 현재 staging 파일 전부가 carried가 된다(rv-R R5 재현)

근거: P L175 «자동 carried = staging 파일 `source`가 `reference_root`·`BUILD/_staging-*`·`BUILD/_history` 하위». D K4 L88은 «**이전** `_staging-*`»이다. K4 L81~83대로 `--source-root STAGING`이 `BUILD/_staging-<ts>/…`이면 새 manifest의 모든 `source`가 `BUILD/_staging-*` 하위 → 22파일 carried·exit 4·«미확인 22» 배너. Task 7 테스트(L177)는 «staging source가 reference_root 하위 → 자동 carried»만 있어 이 오탐을 잡지 못하고, Task 11-2(L216)는 staging을 «BUILD 밖»으로 옮겨 실행하므로 평가에서도 드러나지 않는다.

권고: 조건을 «`reference_root` · `BUILD/_history` · 현재 `--out`의 상위 `_staging-<ts>`를 **제외한** `BUILD/_staging-*`»로 고치고, Task 7 테스트에 «staging = `BUILD/_staging-<ts>/export` → 전부 same·exit 0»을 추가한다.

### M3. [MAJOR · 무손실·일반화] Node 경로의 드라이버 실행이 Coordinator의 Bash 도구 상한(최대 600초)을 넘는데 규범·평가 프롬프트에 대책이 없다

근거: K1 L47 기본 `--max-minutes 90`; rv-R ②-4 추정 35~120분(추측 표기). native `claude --print` 안에서 Coordinator가 `node observe_interactions.mjs …`를 Bash로 부르면 도구 타임아웃(기본 120초·최대 600초)에 걸려 프로세스가 죽는다 — 이 환경의 Bash 도구 규격이며 `prior/*/invocation.json`의 `--allowedTools Bash(node *)`도 같은 도구다. P L194(Task 9 Step 2)·L217(Task 11-3)에 백그라운드 실행·분할(`--max-minutes ≤ 8` + `--resume` 반복)·완료 대기 지시가 없다. 결과: T4 «드라이버 실행 여부·잔여 0»이 구조적으로 실패하거나, Coordinator가 산문 로그로 회귀한다(진단 §3의 실패 형태). Task 4 드라이런도 실행자가 백그라운드로 돌리지 않으면 같은 상한에 걸린다.

권고: Task 9 Step 2 문단에 «드라이버는 백그라운드로 실행하고 종료 코드 3이면 `--resume`으로 잇는다(호출 1회당 `--max-minutes`는 실행 환경의 도구 상한 아래)»를 넣고, Task 11-3 프롬프트 경계에 같은 지시와 `--max-minutes` 값을 적는다. Task 4 Step 1에 «백그라운드 실행·로그 폴링»을 명시한다.

### M4. [MAJOR · 무손실] `reached_by`가 «허용 필드»로만 정의돼 archive case가 그것 없이 손 캡처로 통과한다 — K8-7이 기계로 강제되지 않는다

근거: P L152 «design-input `interaction_exclusions`·case `reached_by` 허용» · «`reached_by` step 존재·`reference_capture.sha256 == after.capture.sha256`»(있을 때 검사). D K3 L74 «archive case는 `reached_by`를 **갖고** … 원본 캡처는 전부 드라이버가 저장한 루트 크롭 바이트»와 L76 «case 선택 필드 `reached_by`를 `allowed`에 추가»가 충돌하는데 계획은 후자만 옮겼다. `reached_by`가 없는 case에 대해 검사기가 침묵하면 12 case 전부 수동 캡처 + `interactions.json` 1개로 inputs가 통과한다 — K8-7(«기존 수동 캡처는 무효»)이 빈말이 된다. Task 5 테스트 목록(L154)에 «reached_by 없는 archive case → 2»가 없다.

권고: v2 규칙에서 «archive case는 `reached_by` 필수(초기 상태는 `initial`)·미존재 exit 2»로 못 박고 테스트를 추가한다. D L76의 «allowed 추가»는 «design-input version 1 유지 하에서 필드 허용»의 의미로만 남긴다.

### M5. [MAJOR · 무손실·정합] `role=status`·`aria-live` 서브트리를 state_hash가 아니라 **열거**에서 제외해 토스트 안 버튼이 대상에서 빠진다

근거: P L70 «`pure.stateHash(entries, url)` // role=status/aria-live 제외는 dom 쪽에서 entries에 안 넣는다». D K3 L71은 «state_hash … `role=status`·`aria-live` 서브트리 제외»(해시 입력에서 제외)이고 K2 L53은 «핸들러 보유 = 대상(후손 유무 무관)»이다. A8 Toast는 `role: "status"` 컨테이너 안에 `onClick` 액션 버튼을 가진다(rv-A V1 «Toast action `button onClick`(1430행)», rv-R V4). 계획대로면 그 버튼은 인벤토리에 없어 잔여도 없고 실행도 없다 — 발견 규칙의 약함이 잔여 0으로 통과하는 바로 그 경로다.

권고: 인벤토리에는 넣되 `live:true` 표식을 두고 `stateHash`·`surfaceKey` 계산에서만 제외한다. fixture의 `role=status` 토스트에 액션 버튼을 넣어 «열거되고 실행된다»를 단언한다.

### M6. [MAJOR · 무손실] Task 5·Task 3 테스트 목록이 설계의 반례·규칙을 다 덮지 않아 «반례 전부 exit 2» 합격 기준이 증명되지 않는다

근거: D K3 L72 반례 10종 중 P L154에 없는 것 — `partial:false`∧`caps_hit≠[]` · `executed`∧`error≠null` · `path`가 가리키는 step 미존재 · 비활성/가림 대상의 `executed` · `n` 중복 · `served` 누락(불일치만 있음). 그 밖에 테스트가 없는 검사 항목: `environment_error` → exit 1(K2 L63) · manifest 행 `carried_from` 허용/그 외 필드 거부(K3 L76·`check_design_evidence.py` L304~306) · `declared` 파일 digest 편입(K2 L62) · 예외 stdout 전량 노출(K3 L73) · `approval_quote` 10자 미만 거부. 드라이버 쪽(P L127)도 `unclickable` 기록 · native select 옵션 3 전부 executed · fill 표본 규칙 · 원격 URL 거부 · `--resume` sha 불일치 거부 · `--max-depth`/`--max-minutes` 도달이 없다. T2·T1 합격 기준(P L233~234)은 이 항목들 없이는 «검출력 증명»이 아니다(DEVELOPMENT §4 L115 «계약을 바꾸면 해당 검출력 fixture도 함께 유지한다»).

권고: Task 5 Step 1과 Task 3 Step 1 목록에 위 항목을 열거한다(각 1단언). 

### M7. [MAJOR · 무손실] Task 6 `legacy_v1_allowed`는 git이 무시하거나 추적하지 않는 build를 «무변경»으로 판정해 v1 면제를 준다

근거: P L161 «`git diff --quiet <base> -- <build>` 성공 ∧ `git ls-files --others --exclude-standard -- <build>` 빈 출력». 프로젝트가 `.dddjango-web/`를 `.gitignore`에 두면 diff는 비어 있고 `--exclude-standard`는 무시 파일을 숨겨 둘 다 참 → 수정 중인 v1 build가 legacy로 통과한다. 추적 파일이 0인 build도 같다. D K3 L75의 의도(«git 추적 변경 0·untracked 0»)는 «추적되고 있으며 변경이 없다»이다. Task 6 테스트(L163)에 무시/미추적 사례가 없다.

권고: 조건에 «`git ls-files -- <build>` 비어 있지 않음(추적 파일 ≥1)»을 추가하고 `--others`에 `--ignored`를 함께 쓴다. 테스트 «전부 untracked 또는 ignored build → v2 요구(exit 2)»를 추가한다.

### M8. [MAJOR · 정합] Task 3이 한 리뷰 게이트로 감당할 크기가 아니고, K2의 same-origin iframe 순회·CDP 리스너 매핑·hover/스크롤 발견이 «구현» 한 단어 뒤에 숨어 있다

근거: P L113~128 한 Task에 CLI 인자·모듈 해소·브라우저 기동/CDP·served 수집·초기 인벤토리·큐/context 키·reload+재생·접두 해시 최적화·6종 조작·안정 대기·루트 크롭 캡처·step 기록·resume·상한·이탈·CDP `getEventListeners`→요소 매핑(P L103 «`opts.listenerIds` Set을 받아 `id` 매칭» — CDP backendNodeId를 스니펫의 identity로 바꾸는 방법이 없다)·hover/스크롤 발견이 들어가고 end-to-end 단언이 12개다(L127). D K2 L63 «same-origin iframe은 순회한다»는 계획 어디에도 없다. P L128 «**Step 3**: 구현.» 한 단어다. 선례 09-06 Task 1도 검사기 하나에 12단계 순서를 적었다.

권고: 3a(래퍼·기동/CDP·served·초기 인벤토리·initial 캡처·exit 계약) / 3b(큐·context·재생·조작·안정 대기·캡처·resume·상한·이탈) / 3c(CDP 리스너 매핑·hover/스크롤 발견·iframe·`discovery_limits`·`capabilities`)로 나누고 각 Task에 단언을 배분한다. iframe·CDP 매핑 방법을 인터페이스에 적는다(예: `page.context().newCDPSession` → `DOM.getDocument`+`DOM.querySelector`/`DOM.resolveNode`로 `data-ia-id` 없이 backendNodeId↔element를 잇는 절차).

### M9. [MAJOR · 무손실·정합] Task 11-3 native 호출 명세가 판정 기준을 스스로 무력화한다(`Agent` 도구 누락·사전 승인 부재·`.git` 제외·`--add-dir` 미명시)

근거:
- P L217 `--tools Read,Grep,Glob,Skill,Bash,Edit,Write,ToolSearch` — 서브에이전트 호출 도구(`Agent`)가 없다. 판정 항목 «독립 G0 리뷰 호출»은 `dddjango-web:design-review-web` 호출이 있어야 성립한다(`commands/dddjango-web.md` L143). `prior/coordinator-repair/invocation.json`은 `--tools …,Agent`·`--allowedTools … Agent`였다.
- `--print` 모드에서 G0 배너·«외부 진실 재동결?»(L132·L202) 같은 사용자 게이트는 답을 받을 수 없다. 프롬프트에 «평가 계정의 사전 승인: 기존 폴더 ⓐ 재사용·재동결 안 함·G0 승인» 문구가 없으면 Coordinator가 멈추거나 임의로 진행한다(09-06 계획 L74 «scope와 단계 진행은 평가 계정이 사전 승인» 선례).
- «A8 워크트리를 scratch로 복제(`.git` 제외)» — Coordinator는 `git rev-parse HEAD`(L168)·`git_snapshot`·backstop을 쓰고, Task 6의 legacy 판정은 git 앵커다. 비git 사본에서는 backstop이 «git 저장소 아님 — 전역 퇴화»(backstop.py L193~196)로 흘러 판정이 의미를 잃는다.
- `--add-dir`·`--mcp-config`가 없다. scratch A8·플러그인 스냅샷만 `--add-dir`로 열고 dddjango 저장소(`workspace/eval/…/prior/oracle` 포함)는 열지 않아야 «평가 폴더 미접근»이 기계로 보장된다.

권고: 호출 인자를 `prior/coordinator-repair/invocation.json` 그대로 인용하고(`Agent` 포함), 프롬프트 사전 승인 문구·`--add-dir` 2개·`--strict-mcp-config`(Playwright MCP는 넣지 않거나 넣는 이유 명시)를 적는다. scratch는 `git init && git add -A && git commit`으로 최소 이력을 만든다.

### M10. [MAJOR · 정합·선례] 릴리즈 경로가 작업 트리 상태와 모순이다 — `_release`는 dirty 트리를 거부하는데 계획이 손대지 않는 되돌림 파일이 남는다

근거: `Makefile` L304~306 `git status --porcelain` 비어 있지 않으면 `die "worktree dirty — 커밋/스태시 후 진행"`. 현재 `git status --short`: `dddjango-web/` 9 + `codex-dddjango-web/` 9 + `docs/master.html` + `workspace/eval/field-report-4/…lanes.md` = 20 수정(web 18파일 = HEAD 대비 −219/+77 = v1.1.7 되돌림; 태그 대비 차이는 `plugin.json` 2개뿐). 계획이 수정하는 파일은 그중 6(+Codex)이고 `coder-web.md`·`design-architect-web.md`·`discipline-reviewer-web.md`·`architecture-web/references/final.md`·`implementation-ui/references/final.md`(+Codex 5)는 손대지 않는다. P L3·L22 «커밋·스태시·브랜치 전환 없음 … 커밋은 Task 12 승인 뒤 한 번», L225 «최종 검증된 파일만 경로 명시 커밋 … `make release-web`». 이 셋은 동시에 성립하지 않는다. 또 계획이 수정하는 파일의 커밋은 그 파일 안의 1.1.8~1.1.12 되돌림을 **함께** git에 넣는다(사용자 결정 ③의 함의지만 «되돌림을 커밋한다»는 결정 문장이 없다). 선례: `2026-09-13-web-refreeze-resume.md` L67~69 «커밋 → 기존 두 문서 미커밋 변경 보관 → `make release-web` → 변경 복원».

권고: Task 12 Step 3 브리프에 두 결정을 올린다 — ① 되돌림 18파일 전체를 별도 커밋(`revert(web): …`)으로 먼저 기록할지, 계획 파일 6+6만 커밋하고 나머지 10을 보관·복원할지 ② `docs/master.html`·lanes md 보관·복원. 그리고 «릴리즈 직전에만 사용자 승인 하에 보관(stash 또는 사본)·릴리즈 뒤 복원·`before-hashes.json`으로 byte 무변 확인» 절차를 적는다. P L54의 «v1.1.7 되돌림 10파일»은 실제 18파일(Claude 9·Codex 9)로 정정한다.

### M11. [MAJOR · 정합] «두 구현 동일성» 테스트의 입력이 정의상 맞지 않는다 — `pure.residual(doc)`은 interactions 문서를 받는데 `expected.json`은 인벤토리 3개다

근거: P L73 `pure.residual(doc) // interactions.json 객체 → …`, P L86 «`expected.json`에 fixture 인벤토리 3개 … 기대 id/context/surface 값», P L154 «`expected.json` 인벤토리와 `r3-steps.json`에 대해 `interaction_residual`이 `node -e "…pure.residual"` 출력과 같다». 인벤토리만으로는 steps가 없어 잔여 = 필요 조작 전부가 되고, 의미 있는 대조(K1 L46 «같은 identity·다른 context 짝»)가 되지 않는다. Python 쪽은 identity/context를 계산하지 않으므로(T5 인터페이스 L145~150) 기대 id/context 값은 JS 테스트에서만 쓰인다.

권고: `expected.json`을 «최소 interactions 문서 3개(initial+steps 포함, K7 스키마 준수)»로 정의하고, 동일성 테스트 입력을 그 3개 + `r3-steps.json` + Task 5 반례 fixture 전부로 명시한다. Python 테스트가 `node`에 의존하므로 node 부재 시 정책(실패)을 적는다(m12와 연결).

### m1. [MINOR · 정합] 규범 앵커 일부가 어긋난다

P L191 «L142~144 step 5-7»: `commands/dddjango-web.md` L142~143은 «6. 준비 판정» 아래 «ready 직전 입력 게이트» 문단이고 L144는 «7. 출처 없음 = Claude 자체 설계»다(무관). Codex L164도 «6.» 아래 문단이다. «step 5-7 입력 게이트» 표기를 «step 5-6의 입력 게이트 문단»으로 고친다. L134~137·L140·L168·L202·L231과 Codex L157·L162·L225·L255, Codex 리뷰어 L24(«## G0 입력범위 모드»)는 정확하다(검증됨 V1).

### m2. [MINOR · 일반화] hover/스크롤 발견 조작(K2 L59·K8-4)이 규칙·fixture·테스트 없이 «`discovery:true` step» 한 구절로 남았다

`:hover` 규칙 매칭(render-audit `hoverSelectors` 재사용 여부)·overflow 컨테이너 판정·`discovery_limits` 형식이 없고 fixture(P L105)에 hover 전용 메뉴·스크롤 컨테이너가 없다. Task 3(또는 3c)에 규칙 2줄과 fixture 2요소·단언 2개를 추가한다.

### m3. [MINOR · 무손실] `--declared`·`declared_unmatched`·`excluded_regions`의 드라이버 테스트가 없다

P L127 end-to-end 목록에 선언 파일을 주는 사례가 없어 «선언은 늘리기만 한다»·«미매칭은 `declared_unmatched`·잔여 밖»(K2 L62)이 검증되지 않는다. 각 1단언(선언 매칭 → `targets[id].declared:true`·미매칭 → `declared_unmatched` 1·`--excluded-regions` → `outside_root` 0)을 추가한다.

### m4. [MINOR · 정합] 모듈 경로 전달 방식이 셋(`--playwright-module`·`NODE_PATH`·`DDDJANGO_WEB_PLAYWRIGHT_MODULE`)이고 `collector.path`(node|mcp) 판별 입력이 없다

CLI가 env를 읽는지, Coordinator가 경로를 어디서 얻는지(scope.md 실행 경계) 미정. 하나로 통일하고(권고: CLI 플래그 + 같은 이름의 env 폴백), `observe(page, opts)`에 `opts.path`를 두어 래퍼가 `node`, 트램폴린이 `mcp`를 넣게 한다.

### m5. [MINOR · 정합] K5 L96 «모듈 경로·버전·기동 방식을 scope.md 실행 경계에 기록» 문장이 Task 9 Step 2에 없다.

### m6. [MINOR · 정합] K4의 «`refreeze-diff.json` sha를 visual-check ①·build-state에 적는다»와 «차이(3)면 새 기준 설치» 절차(`design-ref`/manifest 교체·이전 바이트는 git)가 Task 9 Step 1에 없다. «새 기준 설치»는 `archive_design.py` L155~156(«use a fresh output directory») 때문에 `--out`을 `design-ref`로 직접 줄 수 없으므로 «`_staging-<ts>/design-ref` → `design-ref` 교체(rm+mv)·manifest 교체» 순서를 적어야 한다.

### m7. [MINOR · 선례] raw transcript 보존 정책이 계획 안에서 모순이다

P L55 «대용량(raw.jsonl·build 사본·캡처)은 복사하지 않고 README에 사유» vs P L217 «raw transcript는 `native/<run>/raw.jsonl`로 보존». 09-06 계획 L70은 «raw CLI trace는 task temp에 둔다». 하나로 정하고 `.gitignore`(현재 `*.claude.log`만)와 맞춘다.

### m8. [MINOR · 정합] 대조군 «구 Coordinator(v1.1.7 스냅샷)+신 검사기»의 스냅샷 구성 방법이 없다

commands/agents는 v1.1.7, scripts/assets/references는 신판인 혼합 디렉터리를 어떻게 만드는지(`git show dddjango-web--v1.1.7:…` 추출)를 Task 11-3에 적는다. 구 Coordinator는 `--phase prepare`에서 exit 2를 받고 멈추므로 «exit 2 예상» 판정만 남는다는 점도 명시한다.

### m9. [MINOR · 정합] Task 4 집계 표의 «빈 목록 도달»·«선언으로 닫힘»이 기계 정의가 없다

빈 목록은 대상이 아니라 상태다(«행 대상 0인 after 인벤토리를 가진 executed step 존재»로 정의). 선언은 Task 4가 `--declared` 없이 돌면 정의상 0이다 — 표에 «declared=0 실행» 조건을 적고, 오라클 항목별 «발견 채널(react_props|cdp|semantic|structure)»을 targets에서 집계한다(K2 L53 `capabilities`와 별개로 대상별 채널 기록이 K7에 없으니 필요하면 K7 `targets[id].found_by`를 사용자 결정 없이 추가 가능한지 확인).

### m10. [MINOR · 무손실] K1 세부 규칙 3개가 Task 1 인터페이스·테스트에 없다

identity 충돌 시 dom_path 추가(L41) · 메뉴 항목 context = owner face 제외(L44) · `click:outside` ≡ 스크림 자기 `click` 동치(L45). 각 1테스트.

### m11. [MINOR · 정합] «한계» 4항·정적 경로 범위 밖·C#3 후속 후보·motion-notes 인용 권고의 기재 위치가 없다

design-evidence.md에 «Limits» 소절로, Coordinator에는 넣지 않는다(런타임 본문 오염 금지 — AGENTS.md «플러그인 작성 원칙»).

### m12. [MINOR · 일반화·정합] Node 버전·`.pw.js` 로딩·`make verify`의 node 의존이 근거 없이 정해졌다

P L9 «Node ≥ 20 ESM», P L197 REQUEST_GUIDE «Node 20 이상». `observe_interactions.pw.js`는 `.js` 확장자에 `export default`(K5 L95)이고 플러그인에 `package.json`이 없으므로 Node의 모듈 구문 자동 감지에 기댄다 — 기본 활성 버전은 22.7(20.x 백포트 여부·정확한 경계는 **추측**). 또 `verify-web`이 node를 처음으로 필수 의존으로 삼는데(현행 fixtures_*.sh에 node 사용 0·`docs/DEVELOPMENT.md`에 node 언급 0) §2 환경 절에 기재가 없다. 권고: 실측 버전(v26.8.2)에서 확인한 뒤 «Node ≥ 22»로 통일하고 DEVELOPMENT §2·§5에 node 필수를 적는다. MCP 트램폴린은 MCP 서버 프로세스의 Node로 import되므로 그 버전도 같은 조건이다.

### m13. [MINOR · 정합] `verify-web-browser`가 `_release`의 DRY 안내 [1]~[7](Makefile L358~365)·«▶ n/7» 단계 표시에 반영되지 않고, `make release-web DRY=1`(DEVELOPMENT §6 «미리보기 — 변경 없음»)이 모듈 없이는 exit 1이 된다

`release-web: verify-web-browser _release`는 DRY 여부와 무관하게 선행된다. «DRY=1이면 브라우저 게이트도 안내만»으로 할지 결정하고 안내 문구를 갱신한다.

### m14. [MINOR · 정합] `approval_quote` 10자 이상(K3 L73)·`observed_at` 형식이 Task 5 항목에 없다.

### m15. [MINOR · 정합] Task 10 «SKIP 불가 모드(`DDDJANGO_WEB_REQUIRE_BROWSER=1`)»의 소유가 테스트 파일인지 러너인지 없다 — Task 2 Step 1의 SKIP 문구 정의와 같은 파일(`test_observe_interactions.mjs`)에 두고 러너는 env만 넘긴다고 적는다.

### m16. [MINOR · 정합] scripts·assets·fixtures의 Codex byte 미러 복사 단계가 어느 Task에도 없다

파일 구조 표(P L30~42)의 신규 `.js`·`.mjs`·`.py`·fixtures 행에 «(+Codex byte 미러)» 표기가 없고 Task 1~7·10 어디에도 `cp`가 없다. `make verify-web` L96~97이 red로 잡으므로 거짓 통과는 아니지만, 각 Task «검증 green» 조건에 «Codex 미러 복사 후 `diff -rq` 0»을 넣지 않으면 Task 10까지 red를 안고 간다.

### m17. [MINOR · 선례] 각 Task «기록» 항목 라벨(`feat(web)`·`docs(web)`·`build(web)`)과 최종 단일 커밋 `fix(web): …`(P L225)이 어긋난다 — 라벨은 기록용임을 P L22에 한 줄로 밝힌다.

---

## ③ 검증됨(공격했으나 견딘 항목)

- **V1 앵커 대부분 정확.** «재동결은 새 staging에 수집/검증하고 성공한 기준을 함께 교체한다 …» 문장은 `commands/dddjango-web.md` L135(P L134~137 범위 안)·Codex L157에 실존. «Phase 2 ⑤ 커밋 목록»은 L168·Codex L191의 ⑤(«원본 captures[있는 것 전부; 민감 raw 증거는 공개 커밋 제외]»). L140 동적 표현 문단·L202 수정 모드 G0·L231 경계 절·Codex L225·L255 정확. `Makefile` L91~101·L274~278 정확. Codex 리뷰어 L24 = «## G0 입력범위 모드».
- **V2 `carried_from` 허용이 실제로 필요하다.** `check_design_evidence.py` L304~306은 `required_row` + `requested_source` 외 필드를 «invalid source-manifest row fields»로 거부한다 — Task 5가 허용을 명시한 것은 맞다(테스트 누락은 M6).
- **V3 `Path(__file__).resolve().parents[1] / 'assets'`는 두 설치 배치에서 같다.** Claude `dddjango-web/scripts/…`→`dddjango-web/assets`, Codex `codex-dddjango-web/skills/dddjango-web/scripts/…`→`…/dddjango-web/assets`(Makefile L97이 그 경로를 미러한다).
- **V4 MCP 트램폴린 판단이 스키마와 맞다.** `browser_run_code_unsafe`는 `code`(«page 하나를 인자로 호출되는 함수»)와 `filename`(«code 무시»)만 받는다 — `filename`에는 opts를 넘길 자리가 없으므로 «트램폴린만»(K5·P L185)이 옳다.
- **V5 Task 4 게이트를 Task 5 전에 두는 순서는 성립한다.** 게이트 수치(발견·실행·잔여·표면 키 수)는 Task 1의 `pure.residual`·`pure.linkedSurfaces`만으로 계산되고, Task 5의 «두 구현 동일성»이 Python 판과의 분기를 뒤에서 고정한다. 표면 연결 의무·예외 10%는 게이트 조건이 아니다.
- **V6 `run_fixtures.sh` 글롭 자동 포함.** L10 `for fx in "$HERE"/fixtures_*.sh` — `fixtures_interactions.sh`는 추가 배선 없이 실행된다.
- **V7 REQUEST_GUIDE 문단은 계약을 지킨다.** `request_guide_contract.py` L87~91의 검사는 권위 문구·상대 목적지 구문·README 토큰뿐이며 P L197 문단에는 링크·경로 구문이 없다.
- **V8 `test_design_archive.py` `prepare()`(L50)가 실존**해 Task 5의 판형 재사용이 가능하다.
- **V9 references cmp는 현재 green에서 시작한다.** implementation-ui 3·architecture-web 1 모두 `cmp` 동일(실측).
- **V10 커밋 정책은 선례와 정합.** «현재 작업 트리·`/tmp/…/before/` 보존·커밋/스태시/브랜치 전환 금지»는 09-05 계획 L16, «Task 12 승인 뒤 커밋 1회»는 09-13 refreeze-resume L3·visual-fidelity L52 판형이다(릴리즈 경로만 M10).
- **V11 A8 읽기 전용이 모든 Task에서 지켜진다.** Task 4 scratchpad 사본(L134), Task 11-1/2 «A8 사본(scratchpad)»(L215~216), Task 11-3 «scratch로 복제»(L217), Task 0 Step 2는 `/tmp` 읽기뿐. A8은 git 추적 402·`status --porcelain` 빈 출력(실측)이라 사본 대조가 가능하다.
- **V12 1.1.8~1.1.12 재도입 방지가 계획 문장으로 있다.** P L16 금지·L196 «독립 렌더가 필요한 …» 문장 배제·Task 12 Step 1 «재도입 검사».
- **V13 Task 0 자료가 실존한다.** `/tmp/dddjango-web-a8-interactions-20260913/{baseline,g0-normal-negative,g0-observed-review,coordinator-repair,coordinator-live}`(prompt.txt·invocation.json·result/review.md)·`/tmp/a8-interaction-evaluator-20260913/{oracle.json,oracle.sha256}` 확인.
- **V14 Task 11-4 표본이 실존한다.** `workspace/eval/web-design-source-integrity/2026-09-07/fixture/source-positive/{index.html,steps.js,…}`·`workspace/eval/web-a8-visual-fidelity/role-browser-app/source.html`.
- **V15 T3 기대치 «same 18·carried 4»의 산술은 맞다.** A8 `source-manifest.json` files 22(PNG 4 · 나머지 18) · dependencies 29(ok 23·external 6·image 0) → PNG 4는 closure 밖. 단 `_raw-export`는 A8에 **없다**(`ls` 실측 — manifest `source_root`만 남음) — 아래 ④ 조건 ③.
- **V16 A8 legacy 조건 성립.** Task 6 규칙은 A8 현재 build(추적·무변경)에 대해 참이다(rv-R V6 재확인).

---

## ④ 한 줄 총평

**실행 진입 불가(조건부)** — B1(브라우저 기동 방식 미확정·유일한 npx 모듈이 요구하는 chromium 1243이 캐시에 없음)을 사용자 결정으로 닫기 전에는 Task 2 Step 2에서 멈춘다. 진입 조건: ① B1 결정(`--cdp` 전용 Chrome / `--channel chrome` / 메인테이너 한정 설치)을 Task 0에 고정 ② M3(백그라운드·`--resume` 분할 지시)·M9(native 호출 인자 = `prior/coordinator-repair/invocation.json` 판형 + `Agent` + 사전 승인 + git 사본)·M10(릴리즈 전 되돌림 18파일 처분 = 사용자 결정) ③ Task 11-2 입력을 «`design-ref` 사본을 BUILD 밖 staging으로 + PNG 4 `--carried` 명시»로 정정(`_raw-export` 부재) ④ M1(임시 캡처 tempdir)·M2(«이전» staging)·M4(`reached_by` 필수)·M5(status 서브트리는 해시에서만 제외)·M6(반례 목록 보강)·M7(추적 파일 ≥1)·M8(Task 3 분할·iframe·CDP 매핑)·M11(동일성 입력 정의)을 계획 문장으로 고친다. 설계 K1~K8 자체를 바꾸는 발견은 없다(M4·M5는 D가 이미 말한 것을 P가 잘못 옮긴 경우).

숨은 사용자 결정(P «사용자 결정이 필요한 조건» L241~244에 없음): (a) 브라우저 기동 방식과 메인테이너 환경 설치 허용 여부(B1) (b) 되돌림 18파일을 git에 커밋할지·보관/복원할지(M10) (c) 사용자 대면 문장 «Node 20 이상»의 실제 최소 버전(m12) (d) `make verify` 상시 node 의존(m12) (e) raw.jsonl 저장소 보존(m7) (f) `make release-web DRY=1`이 브라우저 게이트를 요구할지(m13). 릴리즈 patch 1.1.13·`before` 보존 위치는 게이트/선례 안에 있어 문제없다.

## 요약

- 발견 29건: BLOCKER 1 · MAJOR 11 · MINOR 17 · 검증됨 16(별도).
- BLOCKER: B1 브라우저 실행 경로 미확정(npx playwright 1.63.0-alpha ↔ 캐시 chromium 1223/1234 불일치).
- MAJOR: M1 `.pw-cache` byte 미러 diff red · M2 자동 carried «이전» 누락(전 파일 carried) · M3 Bash 도구 상한 vs 90분 드라이버(백그라운드·resume 지시 없음) · M4 `reached_by` 선택 필드 = 손 캡처 통과 · M5 `role=status` 서브트리 열거 제외(토스트 버튼 손실) · M6 반례·규칙 테스트 누락 묶음 · M7 legacy 판정이 무시/미추적 build 통과 · M8 Task 3 크기·iframe·CDP 매핑 부재 · M9 native 호출 인자(Agent 누락·사전 승인·`.git` 제외·`--add-dir`) · M10 릴리즈 vs dirty 트리(되돌림 18파일 처분 미결) · M11 두 구현 동일성 입력 형식 불일치.
