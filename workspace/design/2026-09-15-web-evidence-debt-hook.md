# 설계 — 증거 부채 hook (dddjango-web 수리 1) · 2026-09-15 · v2

진단: `workspace/eval/web-evidence-debt-hook/diagnosis.md`. 이 문서는 수리 1만 다룬다(보더 절단 갭 1·2는 수리 2·3 별건).
v1 → v2: 1차 적대 검토(`workspace/eval/web-evidence-debt-hook/design-review.md` · BLOCKER 3·MAJOR 9·MINOR 7) 전 항목 반영. 반영 대조는 §7.

## 0. 목표와 비목표

- 목표: 시안 빌드 폴더에 **조작 상태 증거 부채**가 있으면, Coordinator가 어떤 경로를 고르든 **그보다 먼저** 그 사실이 (모델 컨텍스트와 사용자 화면 양쪽에) 들어가고, 그 폴더에 대한 사용자 결정이 기계 기록으로 남게 한다. 규범이 «호출하라»고 시키는 층이 아니라 하네스가 실행하는 층에 둔다.
- 비목표: 드라이버 자동 실행(재수집 사슬은 사용자 결정), case 의무 확장, 기존 호출 지점(≥8, 진단 표) 제거 — 2차 방어선으로 유지, 수리 2·3.
- 관계: hook은 **고지 층**이다. K3 legacy v1 허용(backstop `legacy_v1_allowed`)과 무관하게 v1은 부채로 고지한다. 게이트 판정(exit 2로 막기)은 계속 `check_design_evidence`/backstop이 소유한다.

## 1. 근거 — 두 런타임의 hook 계약 (공식 문서 확인 09-15)

| | Claude Code | Codex CLI 0.154 |
|---|---|---|
| 플러그인 hook 위치 | `<plugin>/hooks/hooks.json` | `<plugin>/hooks/hooks.json`(live) |
| 이벤트 | `SessionStart`(matcher `startup\|resume\|clear\|compact`), `UserPromptSubmit`(matcher 없음) | 동일 이름 |
| 출력 | plain stdout → 모델 컨텍스트만. JSON `{"hookSpecificOutput":{"hookEventName","additionalContext"},"systemMessage"}` → 컨텍스트 + 사용자 화면 | `hookSpecificOutput.additionalContext` 지원. `systemMessage`는 B4에서 확인 |
| 플러그인 루트 | env `CLAUDE_PLUGIN_ROOT`·`CLAUDE_PROJECT_DIR` | env `PLUGIN_ROOT`(호환 `CLAUDE_PLUGIN_ROOT`) |
| stdin | JSON(`cwd`=hook 실행 시점 cwd, `hook_event_name` …) | JSON(`cwd`) |
| 타임아웃 | UserPromptSubmit 기본 30s | — |
| 신뢰 | 플러그인 활성화 시 자동 | 해시 기반 — 새/변경 hook은 `/hooks` 승인 전 skip |

exit는 항상 0(UserPromptSubmit exit 2는 프롬프트를 지운다). 이벤트는 hooks.json이 argv로 넘긴다(`session-start` / `user-prompt`) — stdin 필드명 차이에 의존하지 않는다.

## 2. 구성요소

### P1 술어 `dddjango-web/scripts/evidence_debt.py` (검사기와 단일 출처 · stdlib json만 · 무거운 import 없음)

- `has_interaction_evidence(observed) -> bool` = `isinstance(observed, dict) and observed.get('version') == 2 and 'interactions' in observed`. `check_design_evidence._source_observation`의 version 판정이 이 함수를 호출하도록 바꾼다(동작 동일 — 기존 45 테스트로 보존 확인).
- `build_debt(build: Path) -> BuildDebt | None`:
  - `design-input.json` 읽기 실패 → `BuildDebt(error=...)`.
  - archive 빌드 판정 = `manifests[*]` 중 `collection == "archive"`가 있음(검사기 :1122 동일). archive가 아니면 `None`(정적 시안은 조작 상태 의무 없음).
  - 대상 = `build-state.json`이 있고 `design_status == "ready"`인 빌드만. 그 외(진행 중·미완)는 `None` — 진행 중 빌드는 입력 게이트가 경로 위에 있고(:142·:145), 완료 이력 빌드가 규칙 개정으로 부채가 된 사례(A8)가 이 hook의 대상이다.
  - case별 부채 = `source_observation` 포인터 없음/형식 불량/파일 없음/JSON 불량/`has_interaction_evidence` 거짓. **메시지 grep 없음** — 구조 판정. 바이트 해시·manifest 대조·의존성 파싱 없음.
  - 결과: `cases_total`, `cases_debt`, `decision`(build-state `evidence_debt` 키 — 아래 D1) 또는 `None`.
- 비용: JSON 파일 1 + case 수 만큼 관찰 JSON 헤더 읽기. A8 규모 12 case ≈ 수 ms.

### S1 hook 스크립트 `dddjango-web/scripts/evidence_debt_hook.py` (Codex scripts byte 미러)

- 첫 줄 `sys.dont_write_bytecode = True`. 최상위 try/except — 어떤 예외도 exit 0, stderr 1줄.
- 프로젝트 후보 = `CLAUDE_PROJECT_DIR` → stdin JSON `cwd` → `os.getcwd()`. 각 후보에 대해 ① 상위 탐색(첫 `.dddjango-web/` 보유 디렉터리) ② 후보 자신부터 깊이 ≤2 하향 스캔(`*/.dddjango-web/`, `.git`·`node_modules`·`_history`·`.claude`·`.codex` 제외) — 합집합, 중복 제거(realpath).
- 빌드 = `<x>/.dddjango-web/*/design-input.json`이 있는 폴더(이름 정렬). 각각 `build_debt`.
- 분류: `undecided`(부채>0 · `evidence_debt` 없음) · `deferred`(결정 defer) · `observing`(결정 observe) · `clear`(부채 0 — 결정 키가 남아 있어도 해소로 본다) · `error`.
- 출력(JSON, stdout):
  - `session-start`: **항상** 1줄 — `additionalContext`와 `systemMessage` 모두 `[dddjango-web] evidence hook active — scanned <n> build(s): undecided <u> · deferred <d> · observing <o>`. 이 줄이 없으면 hook 미작동(REQUEST_GUIDE·종료 보고 판형에 명기). undecided/deferred/observing 폴더가 있으면 그 아래 폴더별 줄.
  - `user-prompt`: **undecided가 1개 이상일 때만** — 폴더별 줄 + 결정 요구 1줄. deferred/observing만 있으면 무출력(SessionStart가 compact 후에도 재고지하므로 상태 줄 반복 불필요).
  - 폴더별 줄 판형(리터럴 앵커 `[dddjango-web] evidence debt —` 고정 · 테스트·B3가 grep):
    - undecided: `[dddjango-web] evidence debt — <folder>: <k>/<n> archive case without interaction evidence (observation v1/absent) · decision required before any run on this folder`
    - deferred: `[dddjango-web] evidence debt — <folder>: deferred since <at> — "<quote 앞 20자>"`
    - observing: `[dddjango-web] evidence debt — <folder>: observation pending since <at>`
    - error: `[dddjango-web] evidence debt — <folder>: cannot evaluate (<type>: <msg>)`
  - 결정 요구 1줄(undecided 있을 때): `[dddjango-web] evidence debt: <u> undecided build(s). Record the user's decision in build-state.json evidence_debt (ⓐ observe = re-collect chain: observe ≤90 min → independent review → inputs → visual re-evidence → backstop · ⓑ defer = non-implementation runs only; implementation re-entry requires ⓐ) before any run on that folder, including refreeze-only or scope-only runs.`
  - `systemMessage`(사용자 화면)는 요약 1줄만: `[dddjango-web] evidence debt: undecided <u> · deferred <d> · observing <o>`(error가 있으면 ` · error <e>` 추가 — SessionStart 줄과 같은 판형).
- `.dddjango-web`가 없으면 무출력(session-start도 무출력 — 무관한 프로젝트 소음 0).

### D1 결정 기록 `build-state.json.evidence_debt` (Coordinator가 쓴다 · hook·검사기가 읽는다)

```json
"evidence_debt": {"decision": "observe" | "defer", "at": "<ISO 8601 tz>", "quote": "<사용자 인용 ≥10자>", "reason": "<사유 1줄>", "cases": <결정 시점 부채 case 수>}
```
- Coordinator build-state 스키마 블록(:57-75)에 키 추가. 부채 해소(전 case v2)되면 키를 지운다.
- ⓑ `defer`는 **`interaction_exclusions`가 아니다**(대상 단위 예외·10% 상한·approval_quote 검사기 강제는 그대로). defer는 `--phase inputs`를 열지 않는다 — 재동결·조회 같은 **비구현 실행만** 허용하고, 구현 재진입(Phase 1·수정 모드 편집·coder 호출)은 ⓐ 없이는 기존 입력 게이트 exit 2로 막힌다. 09-13 «예외는 scope 사용자 승인만»과 어휘는 같되 의미(빌드 유보 vs 대상 예외)가 다름을 N1에 적는다.

### H1 `dddjango-web/hooks/hooks.json` · H2 `codex-dddjango-web/hooks/hooks.json`

```json
{"description": "dddjango-web — design evidence debt notice (SessionStart always · UserPromptSubmit when undecided)",
 "hooks": {
  "SessionStart":     [{"matcher": "startup|resume|clear|compact",
                        "hooks": [{"type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/evidence_debt_hook.py\" session-start", "timeout": 10}]}],
  "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/evidence_debt_hook.py\" user-prompt", "timeout": 10}]}]}}
```
H2: 경로 `skills/dddjango-web/scripts/`, 변수는 `${PLUGIN_ROOT}`(B4에서 미치환이면 호환 `${CLAUDE_PLUGIN_ROOT}`로). 그 외 동일. 계약 검사 `workspace/tools/web_hooks_contract.py`가 양쪽을 대조한다.

### N1 규범 (Coordinator `commands/dddjango-web.md` ↔ Codex `SKILL.md` 의미 미러)

1. **Phase 0 step 4(:128) 폴더 확정 질문에 합류** — 결정 앵커는 배너가 아니라 여기다: «컨텍스트에 `[dddjango-web] evidence debt —` 줄이 있는 폴더를 ⓐ 재사용으로 고르면, **그 폴더를 읽는 `ls` 이후 어떤 실행·쓰기(재동결·재수집·조회 포함) 전에** 사용자 결정을 같은 질문에 합류시켜 받는다: ⓐ 지금 조작 상태 수집(재수집 사슬 = 관찰 ≤90분 → 독립 검토 → inputs → visual 재증거 → backstop) / ⓑ 유보(비구현 실행만 · 구현 재진입 시 ⓐ 필수). 결정을 `build-state.json.evidence_debt`(D1)와 `scope.md` 제약 절 인용(≥10자)에 기록한다. **이미 기록된 결정은 재질문하지 않는다**(:122·:143 원칙) — hook이 `deferred`/`observing` 상태 줄만 내는 이유.»
2. G0 배너·종료 보고(재동결만으로 끝나는 실행 포함)에 **확정 폴더의 부채 상태 1줄 + «그 외 k개 폴더 부채(SessionStart 고지 참조)» 1줄** — 반복 표기이지 결정 앵커가 아니다.
3. SessionStart의 `evidence hook active` 줄이 컨텍스트에 없으면 종료 보고에 «evidence hook 미작동(플러그인 hook 비활성 또는 Codex 미신뢰)»을 적는다.
4. 기존 호출 지점(≥8)은 그대로 둔다.
5. REQUEST_GUIDE §4(byte 미러): hook이 하는 일 3줄 + «Codex는 `hooks.json`이 바뀐 버전으로 갱신했을 때 `/hooks`에서 dddjango-web hook을 재신뢰해야 하며, 신뢰 전에는 세션 시작 시 `evidence hook active` 줄이 나오지 않는다 = 미작동».
6. `docs/DEVELOPMENT.md` §1 지도에 `hooks/` 행 · §6 릴리즈에 «hooks.json이 바뀐 릴리즈는 릴리즈 노트에 Codex 재신뢰 1줄» 규칙.

### V1 검증 배선

- `scripts/test/test_evidence_debt.py`(P1 단위: v2/v1/absent/broken JSON/포인터 불량/non-archive/design_status≠ready/결정 키 분류) + `scripts/test/test_evidence_debt_hook.py`(S1: 프로젝트 탐색 상위·하향·`CLAUDE_PROJECT_DIR` 우선·`.dddjango-web` 없음 무출력·session-start 항상 1줄·user-prompt undecided만·JSON 형태·exit 0·예외 시 exit 0) + `fixtures_evidence_debt.sh`(run_fixtures 자동 수집).
- `workspace/tools/web_hooks_contract.py` + `Makefile verify-web` 1줄: 양쪽 `hooks/hooks.json` 존재·JSON·이벤트 2종·argv 2종·스크립트 경로 실재. Makefile은 `protocol` 봉인 그룹 → `manifest_seal.py --write`.

## 3. 행동 시험 — 검증자가 경로를 고르지 않는다

| id | 무엇 | 합격 |
|---|---|---|
| B1 | V1 단위 전부 | green · 기존 45 python 테스트 green(P1 리팩터 동작 보존) |
| B2 | A8 빌드 **사본** 프로젝트(9폴더)에서 `python3 evidence_debt_hook.py user-prompt` ← stdin `{"cwd": <copy>}` | 관계인 빌드 줄 `12/12 archive case without interaction evidence` · **전 빌드 합 ≤250 ms(인터프리터 포함)** |
| B3 | 격리 `CLAUDE_CONFIG_DIR`(설치본 비활성)에서 `claude -p --output-format stream-json --verbose --plugin-dir <worktree>/dddjango-web --allowedTools 'Read,Glob,Grep,Bash(git status:*),Bash(ls:*)'` · 발화 = **09-15 원문 + 폴더명**(step 4 질문 건너뜀) | ① 출력/`--debug hooks`에 UserPromptSubmit hook 실행 기록 ② 첫 assistant 텍스트 블록에 리터럴 `[dddjango-web] evidence debt —` ③ `archive_design.py`·`--compare-build`·`.dddjango-web/` 쓰기 tool_use 0건 — 셋 다 jq/grep으로 판정 |
| B4 | Codex: `codex exec --dangerously-bypass-hook-trust`(가능하면) 동형 · `${PLUGIN_ROOT}` 치환·`systemMessage` 수용 확인 | additionalContext 도달. 미치환이면 H2를 `${CLAUDE_PLUGIN_ROOT}`로 |

## 4. 남는 우회 (명시)

1. hook 비활성(Codex 미신뢰·플러그인 hook 끔·타임아웃 kill) — SessionStart `active` 줄 부재로 사람과 Coordinator가 식별 가능(N1-3). 완전 제거 불가.
2. 사용자가 ⓑ defer를 고르는 것 — 결정이지 우회가 아니다. 구현 재진입은 여전히 exit 2.
3. `.dddjango-web`를 상위·깊이 2 하향 스캔 모두로 못 찾는 배치(깊이 3+) — 무출력. step 4 폴더 확정 시 N1-1이 잡는다(산문 층).
4. hook stdout이 컨텍스트에 있어도 Coordinator가 무시 — `systemMessage`로 사용자가 같은 요약을 본다(사람이 감시 가능).

## 5. 계획 (Task 4개 · 워크트리 브랜치 · Task별 커밋)

| Task | 내용 | 실행 |
|---|---|---|
| T1 | P1 `evidence_debt.py` + 검사기 `_source_observation` 위임 + S1 hook 스크립트 + V1 단위 테스트(RED→GREEN) + Codex scripts 미러 | 인라인 |
| T2 | H1·H2 hooks.json + `web_hooks_contract.py` + Makefile 1줄 + 봉인 재발행 + DEVELOPMENT §1·§6 | 인라인 |
| T3 | N1 규범(Coordinator·Codex SKILL — step 4·배너·종료 보고·build-state 스키마) + REQUEST_GUIDE ×2 byte | 인라인 |
| T4 | B2·B3·B4 → 독립 구현 리뷰 1회(fable · 이 설계 §7 반영 대조 포함) → `make verify-web`·`make verify`·strict validate | 리뷰만 서브에이전트 |

## 6. 진단 정정

집행 지점은 5곳이 아니라 ≥8곳(:142 수집 step의 inputs exit 소비 · :145 입력 게이트 · :177 coder 호출 직전 inputs · :184 G2 직전 backstop · :189 마무리 backstop · :204 수정 모드 freshness inputs · :208 수정 모드 G2 backstop · :211-218 트리비얼 패스트트랙 inputs/backstop). 결론(전부 구현행 경로)은 동일 — 진단 문서 표를 정정했다.

## 7. 1차 적대 검토 반영 대조

| 검토 항목 | 반영 |
|---|---|
| BLOCKER Q1-1 결정 앵커가 배너(도달 미보장) | N1-1: 앵커를 step 4 폴더 확정 질문으로 이동, 배너는 반복 표기 |
| BLOCKER Q1-2 매 프롬프트 동일 명령문 → 재질문/무시 학습·compact 충돌 | D1 기계 기록 + S1 상태별 출력(undecided만 명령문·decided는 SessionStart 상태 줄) |
| BLOCKER Q3 비용 0.8 s/빌드·5 s/프롬프트 | P1 경량 술어(해시·파싱 0) · 무거운 import 회피 · B2 기준 ≤250 ms 전 빌드 합 |
| MAJOR Q1 하위 경로·cwd≠루트 | S1 후보 3 × (상위 + 깊이 2 하향) 합집합 |
| MAJOR Q1 사용자 화면 미표시 | JSON 출력 `additionalContext` + `systemMessage` |
| MAJOR Q2 부채 술어 미정의·coverage_review 소음 | P1 구조 술어 · N_o 출력 안 함 |
| MAJOR Q2 문자열 grep이 최악 빌드를 놓침 | P1 포인터/파일/JSON 불량 = 부채 |
| MAJOR Q2 진행 중 빌드 강제 | 대상 = `design_status == ready` |
| MAJOR Q4 ⓑ가 제2 승인 채널 | D1: defer ≠ exclusions · inputs 안 엶 · 비구현만 |
| MAJOR Q4 ⓐ 비용 미고지 | 결정 요구 줄·N1-1에 재수집 사슬 명기 |
| MAJOR Q5 hook 활성 신호 없음 | SessionStart 항상 `active` 줄 · N1-3 |
| MAJOR Q6 B3 기준 검증 불가 | B3 격리 config·stream-json·3조건 grep·발화에 폴더명 |
| MINOR Q0 집행 지점 5→≥8 | §6·진단 표 정정 |
| MINOR Q1 배너에 전 폴더 | N1-2 확정 폴더 + 요약 1줄 |
| MINOR Q2 legacy_v1 정책 | §0 «고지 층 · v1=부채 · 게이트는 backstop 소유» |
| MINOR Q3 pyc 오염 | `sys.dont_write_bytecode` |
| MINOR Q5 재신뢰 절차 | N1-5·6 REQUEST_GUIDE·DEVELOPMENT §6 |
| MINOR Q5 `${PLUGIN_ROOT}` 미치환 | B4에서 확인 후 H2 확정 |
| MINOR Q6 B2 기준·문구 | B2 갱신 |

2차 설계 재검토는 별도로 돌리지 않고 T4 독립 구현 리뷰에 «§7 반영 대조»를 합류시킨다(토큰 비용 — 사용자 지시).
