# 행동 시험 기록 — 증거 부채 hook (2026-09-15)

설계 §3의 B1~B4. A8 원본(`~/.herdr/worktrees/spring_dream_server/a8/.dddjango-web`)은 읽기 전용 — 전부 scratchpad 사본에서 실행.

## B1 — 단위·회귀

- `test_evidence_debt.py` 15/15 · `test_evidence_debt_hook.py` 16/16 (RED 확인 후 GREEN — 술어 모듈 부재 `ModuleNotFoundError`에서 출발).
- 검사기 `_source_observation`을 술어에 위임한 뒤 기존 스위트 보존: `test_design_evidence.py` 40/40 · `test_interaction_evidence.py` 45/45 · `test_design_archive.py` 42/42.
- `web_hooks_contract.py --self-test` PASS(정상 fixture 0건 · command 변이 1건 검출 · 스크립트 부재 검출) · 실제 대조 PASS.
- `claude plugin validate dddjango-web --strict` — Validation passed(hooks/hooks.json 포함).

## B2 — A8 전체 빌드 사본 실측 (`scratchpad/b2_runner.py`)

사본 `.dddjango-web/` 폴더 9개(design-input.json 보유 8개). stdin `{"cwd": <사본 루트>}`.

| 이벤트 | 실행 3회 | exit | 결과 |
|---|---|---|---|
| user-prompt | 50 · 46 · 46 ms | 0 | undecided 8 · deferred 0 · observing 0 |
| session-start | 46 · 46 · 49 ms | 0 | `evidence hook active — scanned 8 build(s): undecided 8 …` |

폴더별 줄(전부 `decision required before any run on this folder`): home-bottom-nav 10/10 · user-info-input 8/8 · web-settings 9/9 · web-chat-spine 12/12 · web-chart 3/3 · web-chart-app-bar 12/12 · web-settings-update 9/9 · **web-related-persons 12/12**.

- 합격 기준 «전 빌드 합 ≤250 ms(인터프리터 포함)» 충족 — 약 50 ms. 설계 v1의 검사기 재사용안(0.8 s/빌드)은 폐기됐다.
- 발견: A8의 완료 빌드 8개 전부가 부채다(v1.1.13 이전 판형). 관계인 폴더만의 문제가 아니었다.

## B3 — 실세션 경로 무관 실증

대상: A8 `.dddjango-web/` 전체 사본 프로젝트(`scratchpad/a8-all/project` — 09-15 13:22 재동결 산출물 포함 · git 저장소 아님). 플러그인 = 이 워크트리 `dddjango-web/`(`--plugin-dir`). 발화 = 09-15 실제 요청과 같은 계열: **«관계인 화면 폴더 20260912-1640-web-related-persons 이어서 작업 — 시안이 바뀐 것 같으니 재동결해줘»**(폴더명을 넣어 step 4 폴더 질문 생략). `--allowedTools "Read,Glob,Grep,Bash(ls:*)"` · `--model sonnet` · `--strict-mcp-config` · `--no-session-persistence` · `--output-format stream-json --verbose` · `--debug hooks --debug-file`.

| 회차 | 차이 | 결과 |
|---|---|---|
| 1 | `--settings '{"enabledPlugins":{"dddjango-web@changja88-dddjango":false}}'`로 설치본 비활성 | `Unknown command: /dddjango-web`(0 turn). 단 디버그 로그: 워크트리 `hooks/hooks.json` 로드 · SessionStart hook 실행 · `provided additionalContext (1935 chars)` |
| 2 | settings 없이 | 동일 `Unknown command`(0 turn) — 원인은 커맨드 이름(플러그인 커맨드는 `/dddjango-web:dddjango-web` 네임스페이스) |
| 3 | 프롬프트를 `/dddjango-web:dddjango-web …`로 | **성공** — 7 turn · 185 s · $0.69 |

3회차 판정(`scratchpad/b3r3_analyze.py`·`b3r3_final.py`):

- ① hook 실행: 디자인 로그 `Hook SessionStart (python3 "${CLAUDE_PLUGIN_ROOT}/scripts/evidence_debt_hook.py" session-start) provided additionalContext (1935 chars)` · `Hook UserPromptSubmit (… user-prompt) provided additionalContext (1838 chars)` — 두 이벤트 모두 실행·주입. `${CLAUDE_PLUGIN_ROOT}` 치환 확인. (stream-json에는 SessionStart hook 이벤트만 실리고 UserPromptSubmit은 디버그 로그에만 남는다.)
- ② 배너: assistant 텍스트 3블록 중 마지막(배너)이 **«① 조작 상태 증거 부채 결정 — 이 폴더에 대해 아직 기록된 적이 없습니다 … 세션 시작 훅이 이 폴더를 "12/12 archive case without interaction evidence"로 표시 … 어떤 실행(재동결 포함)도 하기 전에 먼저 기록해야 하는 결정 … ⓐ observe / ⓑ defer»**를 1급 항목으로 올리고 사용자 답을 기다리며 종료. 리터럴 앵커 `[dddjango-web] evidence debt —`는 그대로 옮기지 않고 의역했다(설계 §3 ②의 «리터럴 포함»은 미충족 · 규범 N1-2 «부채 상태 1줄»은 충족). 첫 블록은 «폴더 상태를 확인하겠습니다» 전문이라 «첫 블록에 앵커» 기준도 미충족 — 기준이 배너 위치를 잘못 가정한 것이고, 행동(재동결 전에 결정 요구)은 설계 목표대로다.
- ③ 금지 tool_use 0건 — 6건 전부 Read·`ls`·`cat` Bash·ToolSearch(AskUserQuestion). `archive_design.py`·`--compare-build`·`.dddjango-web/` 쓰기 시도 없음. 09-15 실세션이 «재동결 → 변화 0 → 종료»로 지나간 바로 그 발화에서 이번엔 부채 결정이 먼저 막아섰다.
- 부수: Coordinator가 hook 문구를 «v1 표준 포맷 부재 … 훅이 요구하는 interactions.json v1 포맷»으로 부정확하게 풀어 썼다(관찰 문서 version 2 ↔ interactions.json version 1 혼동). 부채 줄 문구 «(observation v1/absent)»를 더 분명히 할 여지 — 리뷰 대상.

3회차 격리 주석(독립 구현 리뷰 지적): 설계가 적은 격리 `CLAUDE_CONFIG_DIR`은 쓰지 않았다(1회차 `--settings` 비활성은 `Unknown command`를 냈다). 설치본 v1.1.13과의 동명 충돌은 디버그 로그 `:33 Plugin "dddjango-web" from --plugin-dir overrides installed version`과 init 이벤트 `plugins[0] = {source: 'dddjango-web@inline', path: <worktree>/dddjango-web, version: 1.1.13}`으로 워크트리 버전이 로드됐음을 확인했다. 사용자 설정의 허용 규칙 28건(`Bash(git:*)` 포함)이 함께 적용돼 `git status`가 실제로 실행됐다(비git 사본이라 `fatal: not a git repository`).

## B3 4회차 — 수정 라운드 후 재실행

(아래에 기록)

## B3 미실행 변형

`git init`한 사본(재동결 경로가 step 4를 지나 실제 `archive_design.py` 실행까지 가는 판형)은 돌리지 않았다 — 워크트리 격리 세션이라 사본에 git 명령을 내릴 수 없다. 이번 3회차는 «비git → git init 제안» 경로가 아니라 폴더를 읽고 배너까지 간 경로였고(사본에 `config.json`·전 산출물 존재), 결정 요구가 재동결 실행 전에 왔다는 점은 그 판형과 같다.

## B4 — Codex

이번 배치에서 미실행. 이유: Codex 플러그인을 워크트리 버전으로 설치하려면 사용자 Codex 플러그인 상태(`~/.codex`)를 바꿔야 한다(저장소 밖 부작용). `${PLUGIN_ROOT}` 치환·`systemMessage` 수용은 공식 문서 문장(«Plugin commands receive PLUGIN_ROOT and PLUGIN_DATA environment variables» · «Plain text on stdout is added as extra developer context»)에만 근거한다. 미작동이면 세션 시작 시 `evidence hook active` 줄이 없는 것으로 드러나도록 REQUEST_GUIDE·규범에 적었다. 배포 후 사용자 Codex 세션에서 그 줄의 유무로 확인한다.
