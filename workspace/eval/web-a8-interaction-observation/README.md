# A8 «관계인» 상호작용 관찰 증거 — 평가 기록 (2026-09-13 ~ 09-15)

dddjango-web «상호작용 관찰 증거» SDD(설계 `workspace/design/2026-09-13-web-interaction-evidence.md` · 계획 `workspace/plan/2026-09-13-web-interaction-evidence.md`)의 실측 기록이다. 주장은 «규범이 아니라 기계가 막는다»이고, 이 폴더는 그 주장을 A8 실제 build로 시험한 결과만 담는다. raw transcript·캡처·scratch build는 `/tmp/dddjango-web-interaction-evidence-20260913/`(저장소 밖)에 있고 저장소에는 프롬프트·호출 인자·판정·집계만 둔다(09-06 선례).

## 폴더

| 경로 | 내용 |
|---|---|
| `diagnosis.md` · `before-hashes.json` · `execution-notes.md` | Task 0 진단·보존 |
| `prior/` | 09-13 선행 평가(프롬프트·판정·oracle) — `prior/README.md` |
| `design-review/` | 설계 리뷰 기록 |
| `dryrun/` | 드라이버 드라이런 1~10차(`README.md`·`table.md`·`summary.json`) — 10차 최종 게이트 |
| `refreeze/` | Step 2 재동결 실측 3회(`run-*.json` = `refreeze-diff.json` 사본 · `result.md`) |
| `samples/` | Step 4 A8 밖 표본 2종(`integrity`·`visual-fidelity` · `summary.json`·`result.md`) |
| `native/` | Step 3 native Coordinator 평가(`prompt.txt`·`invocation.json`·`result.md`·`judgement.md`·`judgement.json`·`oracle-summary.json`·`coordinator-final.md`) + 대조군 `native/control/` |

## 절차와 수치(마지막 실행 기준)

환경: 작업 트리 `dddjango-web/`(plugin.json 1.1.12 · 드라이버 tree 4ea5478 — `observe_interactions.pw.js` `4ad627df…` · `interaction_audit.js` `a3c13880…` · `observe_interactions.mjs` `343ece9c…` · `check_design_evidence.py` `ebb8d860…` · `archive_design.py` `cc993cd0…`) · Node v26 · Playwright 1.63.0-alpha(`DDDJANGO_WEB_PLAYWRIGHT_MODULE`) · Google Chrome 152(`--browser-channel chrome`) · 설치 0.

### 1. 검사기 red (A8 build 사본)

A8 원본 `~/.herdr/worktrees/spring_dream_server/a8/.dddjango-web/20260912-1640-web-related-persons/`(402파일 · 12 case · 관찰 전부 version 1)을 사본으로 복사해 `check_design_evidence.py --phase inputs` → **exit 2**: `cases[0..11].source_observation: interaction evidence required (version 2 with interactions)` 12행 + `coverage_review: reviewed-input does not match …` 1행. `--phase prepare`도 exit 2(12행). 원본 무수정.

### 2. 재동결 (`refreeze/result.md`)

기준 manifest `source-manifest.json` sha `bddc54ec…`(22파일 · closure 13). A8에 `_raw-export`가 없어 staging은 `design-ref` 사본이다.

| run | 조건 | 결과 | exit |
|---|---|---|---|
| A | BUILD 밖 staging(바이트 동일) + PNG 4 `--carried` | same 18 · carried 4 | **4** |
| B | `_ds_bundle.js` 1바이트 추가 | same 17 · changed 1 · carried 4 | **3** |
| C | `BUILD/_staging-old/design-ref`를 source로 | carried 22(자동) | **4** |

### 3. native Coordinator 평가 (`native/result.md` · `native/judgement.md`)

`claude --print --plugin-dir <스냅샷> … --output-format stream-json`으로 A8 scratch(워크트리 복제 + `git init/commit`)에서 `/dddjango-web` 기존 화면 «관계인» 재개를 1회 실행. 사전 승인 = ⓐ 재사용·재동결 안 함·없던 채널 신규 동결·G0 승인·Phase 1 이후 비허용·새 결정은 반환. **정답(드롭다운·체크박스·스크림) 미제공.** 대조군 = commands/agents만 v1.1.7 + scripts/assets/references 신판.

| 판정 | native | control |
|---|---|---|
| ① 드라이버 실행(collector sha = 스냅샷) | ○ | ○ |
| ② 잔여 0 ∧ inputs exit 0 | △ 잔여 0 · exit 2(defect 1 = 리뷰어 fail · 기계 결함 0) | × 잔여 0 · exit 2(defect 20 · 기계 결함 18) |
| ③ 예외 0 또는 원문 | ○ 0행 | ○ 6행(기존 원문 인용) |
| ④ 표면 연결(reached_by·sha) | ○ 30/30 | × 12/14 + 미연결 표면 16 |
| ⑤ 독립 리뷰 Agent 호출 | ○ 2회 | ○ 1회 |
| 드라이버 슬라이스(관계인) | 4(잔여 0은 3) · 32분 | 11(잔여 0은 2) · 88분 예산 소진 |
| oracle 도달 | 관계 8·시 12·시·도 17·시·군 153·스크림 1·Esc 2·토글 7·단위 251 | 동일(Esc 7) |
| 소요/턴/비용 | 95분 / 113 / $38.14 | 136분 / 131 / $33.87 |
| 최종 | `design_status=blocked` · 승인 대기 4건 반환 | `design_status=blocked` · 결정 D-A~D-E 반환 |

### 4. A8 밖 표본 (`samples/*/result.md` · 게이트 아님)

| 표본 | exit / 소요 | targets / executed / surfaces | residual / partial / discovery_limits | capabilities |
|---|---|---|---|---|
| ① 정적 HTML+JS 위저드(`web-design-source-integrity/2026-09-07/fixture`) | 0 / 268 s | 10 / 148 / 4 | `[]` / false / `[]` | `{react_props:true, cdp_listeners:true}` |
| ② 이름 등록 대화상자(`web-a8-visual-fidelity/role-browser-app/source.html`) | 0 / 6 s | 2 / 8 / 1 | `[]` / false / `[]` | 동일 |

### 5. 드라이런(`dryrun/README.md` · 컨트롤러 기록)

10차 최종 게이트: 6슬라이스 · step 871 · 대상 223 · 실행 단위 251 · 관계 8 · 시 12 · 시·도 17 · 시·군 153 · 토글 2상태 7 · 잔여 0 · partial:true(`caps_hit: max_minutes`). native·control 모두 같은 도달 수치를 냈다(같은 드라이버 바이트).

## 결론(제약 안에서)

- **검사기가 막았다.** A8의 v1 관찰은 `--phase inputs`에서 exit 2로 거부되고, 두 Coordinator(신·구 규범) 모두 그 메시지와 references를 보고 드라이버를 실행했다. «기존 지침도 통과하면 개선 주장 금지» 규칙대로 «드라이버를 돌리게 한 것»은 Coordinator md 개정의 공으로 세지 않는다. md 개정의 관찰된 차이는 ⓐ 잔여 0 뒤 정지(4 vs 11 슬라이스) ⓑ 새 표면을 case로 잇는 순서(기계 결함 0 vs 18) ⓒ 승인 원문 없는 예외 행을 만들지 않은 것 — 셋뿐이다.
- **완료 선언은 어느 쪽도 하지 못했다.** 남은 defect는 사람 결정(빈 목록·폼 오류 case의 제외 승인 원문)이고, 검사기는 리뷰어 fail을 exit 2로 유지해 `design_status=blocked`가 됐다. 이것이 설계의 의도(«전수·차이 0·완료를 Coordinator가 선언하지 않는다»)와 일치하는지는 이 기록이 판단하지 않는다.
- **native 1회 성공을 전체 성공으로 확대하지 않는다.** 같은 프롬프트·스냅샷 1회 실행이며 병행(CPU 공유)·permissionMode auto·사전 승인 문구 조건의 결과다. 승인 원문을 주었을 때 exit 0이 되는지는 실측하지 않았다.

## 한계

1. 재동결 실측은 `_raw-export` 부재로 «design-ref 사본을 staging으로» 한 것이다 — 원본 재획득(DesignSync 재수집)과 다르다.
2. `related/empty`(4명 연쇄 삭제 뒤 상태)와 `related/form-error`(텍스트만 바뀌는 오류)는 드라이버 관찰로 결속되지 않는다 — 스펙 K2 한계. 두 Coordinator 모두 이 2건에서 사람 결정을 요구했다.
3. 설정(`설정.dc.html`) 드라이버는 `--max-minutes 8` 대비 실제 17~23분이 걸렸고(native 1회 · control 2회 모두), 두 Coordinator 모두 종료 단계 정지를 보고 PID에 SIGTERM을 보냈다(문서·요약은 정상 · exit 3). 상한이 step 사이에서만 검사되는 것으로 보이며 원인은 이 기록이 조사하지 않았다(드라이버 소유).
4. native Coordinator는 case별 `trace.json`을 자체 Node 재생 스크립트(스니펫 `interaction_audit.js` + `render_audit.js`)로 만들었다. 검사기는 trace의 비어 있지 않음만 검사하고 reference_capture·`reached_by`는 드라이버 문서 sha로 묶이므로 게이트 근거는 여전히 드라이버 산출이지만, «Coordinator는 값을 쓰지 않는다» 규범과의 경계는 리뷰 항목이다.
5. 관찰 viewport는 루트 크롭 [390,877](캡션 33px 포함)이라 기존 v5 캡처(390×844)·G2 impl 캡처와 오프셋이 생긴다 — 두 Coordinator 모두 G2 대조 방식 결정을 반환했다.
6. 표본 ②처럼 JS·상태 전이가 없는 화면은 6초에 exit 0으로 끝난다 — `:focus-within` 같은 CSS 시각 상태는 inventory 밖이라 표면·캡처가 생기지 않는다. 검사기 exit 0을 시각 검증으로 읽지 않는다.
7. 표본 ①의 268초는 드라이런 9차와 CPU를 공유한 값이고, native 슬라이스 수(4)도 control과 병행한 값이다 — 절대 기준으로 쓰지 않는다.
8. `claude --print`는 permissionMode `auto`(user 설정)로 돌았고 `--allowedTools`는 선행 판형에 `Bash(node *)`·읽기 전용 git·프로세스 관리 명령을 더한 것이다(`native/invocation.json`). 다른 권한 조건에서의 재현은 하지 않았다.
