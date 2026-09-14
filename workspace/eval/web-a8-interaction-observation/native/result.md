# native Coordinator 평가 — A8 «관계인» G0 입력 준비 재개 (Task 11 Step 3)

실행일 2026-09-14 21:03 ~ 2026-09-15 00:18(KST). raw transcript(stream-json)·드라이버 로그·scratch build는 `/tmp/dddjango-web-interaction-evidence-20260913/native/`(저장소 밖). 이 폴더에는 프롬프트·호출 인자·판정·집계만 둔다.

## 구성

| 항목 | native(피험군) | control(대조군) |
|---|---|---|
| plugin 스냅샷(`--plugin-dir`) | 작업 트리 `dddjango-web/` 전체 복사(`diff -rq` 동일 · plugin.json 1.1.12 · 드라이버 3파일 = 드라이런 최종 tree 4ea5478과 `cmp` 동일: `observe_interactions.pw.js` `4ad627df…` · `interaction_audit.js` `a3c13880…` · `observe_interactions.mjs` `343ece9c…`) | 같은 복사본에서 `commands/dddjango-web.md`·`agents/*.md` 4개만 `git show dddjango-web--v1.1.7:…`로 교체(실제 차이 3파일: command · design-review-web · discipline-reviewer-web; coder-web·design-architect-web는 동일). scripts·assets·references·검사기는 신판 |
| A8 scratch(cwd) | `~/.herdr/worktrees/spring_dream_server/a8` rsync(`.venv`·`.git`·캐시 제외 · 670M) → `git init && git add -A && git commit -m scratch`(HEAD `60943b3` · 12674 파일 · build 폴더 402 파일 추적) | 커밋 뒤 `cp -R`한 동일 사본(HEAD 동일) |
| 호출 | `/opt/homebrew/bin/claude --print --plugin-dir <스냅샷> --setting-sources user --strict-mcp-config --mcp-config mcp.json({"mcpServers":{}}) --no-session-persistence --output-format stream-json --verbose --tools Read,Grep,Glob,Skill,Bash,Edit,Write,ToolSearch,Agent --allowedTools …(`invocation.json`) --add-dir <scratch> --add-dir <스냅샷>` · 프롬프트는 stdin · env `DDDJANGO_WEB_PLAYWRIGHT_MODULE`·`DDDJANGO_WEB_BROWSER_CHANNEL=chrome` · Claude Code 2.1.270 · 모델 `claude-opus-5[1m]` · permissionMode `auto`(user 설정) · MCP 서버 0(init `mcp_servers: []` · Playwright MCP 없음) | 동일(플러그인 경로만 control-snapshot) |
| 프롬프트 | `prompt.txt` — 기존 화면 «관계인» ⓐ 재개 + 사전 승인(ⓐ 재사용·재동결 안 함·없던 채널 신규 동결 승인·G0 승인·Phase 1 이후 비허용·새 결정은 반환) + 실행 경계(모듈 경로·`--browser-channel chrome`·백그라운드·`--max-minutes 8`·`--resume`·서빙 포트 제외·평가 폴더·`/tmp` 타 폴더 미접근). **정답(드롭다운·체크박스·스크림) 미제공** | `control/prompt.txt` — 동일. 유일 차이 = native에 «포트 8733 제외 + 이름 기반 전역 `pkill -f`/`pgrep -f` 금지» 1행 추가(대조군과 병행 실행 때문 · `diff` 2행) |
| 활성화 probe | `--tools ""` 읽기 전용 호출: 스냅샷 플러그인 `dddjango-web@inline 1.1.12` 로드 · 반환 «`observe_interactions.mjs` · `--max-minutes 8`» · 7 s | — |

병행: control은 21:03 단독 시작, native는 22:42에 병행 시작(컨트롤러 중간 지시) — 22:42~23:19 사이 두 Chrome이 CPU를 나눴다.

## 타임라인·수치

| 지표 | native | control |
|---|---|---|
| 소요 / 턴 / 비용 | 5707 s(95분) / 113 / $38.14 | 8154 s(136분) / 131 / $33.87 |
| claude exit | 0 | 0 |
| 첫 검사기 실행 | `--phase inputs` exit 2(12 case «interaction evidence required» + coverage 불일치) | `--phase prepare` exit 2(12 case 동일 메시지) |
| 드라이버 호출(관계인) | 4슬라이스(run1~4 · `--resume` 3회) · 각 8m02~8m06s · residual 9→3→**0**→0 · steps 188→329→440→612 · targets 162→222→222→223 · 표면 19→24→24→25 | 11슬라이스(`--resume` 10회 · 예산 90분 소진) · residual 10→**0**(슬라이스 2)→0… · steps 185→…→1600 · targets 223 · 표면 28 |
| 드라이버 호출(설정) | 1슬라이스 · targets 30 · executed 178 · residual 0 · 표면 8 · **wall 16m58s**(상한 8분) | 2슬라이스 · executed 178→366 · residual 0 · 표면 12 · wall 23m18s / 19m14s |
| 드라이버 인자 | `--root '[data-screen-label="관계인"]' --viewport 560x1040 --crop-root --entrypoint-sha cf2fe348… --archive-sha bddc54ec… --playwright-module <경로> --browser-channel chrome --max-minutes 8`, 서빙 `http.server 8747` | 동일 형태 + `--hover-selectors ["a:hover"]`, 서빙 `8733` |
| interactions.json | `captures/related-persons-interactions.json`(steps 614 = executed 612 + unclickable 2 · partial · caps_hit max_minutes · discovery_limits 3 · capabilities `{react_props:true, cdp_listeners:true}` · 캡처 328) · `captures/preferences-interactions.json`(steps 239 = executed 178 + unreachable 21 + unclickable 40 · discovery_limits 5) | `captures/related-interactions.json`(steps 1602 · executed 1600 · unclickable 2 · 표면 28 · 캡처 751) · `captures/settings-interactions.json`(steps 484 · unreachable 46 · unclickable 72) |
| collector sha | driver `4ad627df…` · snippet `a3c13880…` = 스냅샷 파일 sha(judge ①) | 동일 |
| oracle 도달(`prior/oracle` · 드라이런 `summarize.py`) | 관계 8/8 · 시 12/12 · 시·도 17/17 · 시·군 153/153 · 스크림 1 · Esc 2 · 토글 2상태 7 · 실행 단위 **251** · 미실행 활성 대상 0 | 관계 8 · 시 12 · 시·도 17 · 시·군 153 · 스크림 1 · Esc 7 · 토글 2상태 7 · 실행 단위 **251** · 미실행 0 |
| design-input.json 재구성 | **30 case**(관계인 25 · 설정 5) 전부 v2 관찰 · `reached_by` 30/30(캡처 sha 일치) · viewport [390,877](루트 크롭) · `interaction_exclusions` **0** · v5 12 중 10 재결속 + 신규 16(드롭다운 열림 표면: 관계 메뉴·시 메뉴·시·도 메뉴·시·군 메뉴 9·등록 빈값·삭제/저장 뒤 목록·설정 Dialog 4) · `related/empty`·`related/form-error` 2건은 case에서 빼고 **승인 원문 필요로 반환** | 14 case(v2 12 + **v1 잔존 2**: `related/empty`·`related/form-error`) · `reached_by` 12/14 · `interaction_exclusions` 6행(설정 Dialog · 기존 원문 «설정 나머지 무변…» 인용) · 새 표면 16 미연결 |
| 독립 리뷰(Agent) | `dddjango-web:design-review-web` **2회** 호출(1차 fail → Coordinator 소관 2건 반영 → 2차 fail: 유일 근거 = 미결 ①②) · 원문 `coverage-review.md`(reviewed-input `5f19cddf…` · review-result fail) · 1차 원문 `_history/v6-review-round1/` | **1회** 호출 · review-result fail · reviewed-input none(prepare exit 2) |
| prepare | exit 0 × 2(digest `888492ac…` → `5f19cddf…`) | exit 2(최종: 새 표면 미연결 16 + v1 잔존 2) |
| **최종 `--phase inputs`(Coordinator 실행)** | **exit 2 · defect 1** = `coverage_review: independent review-result: pass required` | **exit 2 · defect 20** = 새 표면 미연결 16 + v1 2 + coverage 2 |
| 평가자 재실행(`judge.py` · 스냅샷 검사기) | exit 2 · 동일 1건 | exit 2 · 동일 20건 |
| 최종 상태 | `design_status: ready → blocked` · `implementation_visual: pass → unverified` · 승인 대기 4건 반환(①related/empty ②related/form-error ③신규 case 13건 case 유지 vs 예외 ④viewport 877 G2 대조) | `design_status = blocked` · 결정 D-A~D-E 반환(빈 목록·오류·드롭다운 표면 12 예외 vs case·설정 Dialog·삭제 뒤 목록) |
| 쓰기 범위 | scratch `git status`: build 폴더 밖 변경 **0**(404 경로 전부 `.dddjango-web/20260912-1640-web-related-persons/` 안) · 드라이버·서버 로그는 `/tmp/dddjango-web-a8-g0-logs-20260914-2248/`(프롬프트 «임시 서버 로그» 허용 범위로 해석) | 밖 변경 0(800 경로 전부 build 안 · `_staging-20260914-2112-interactions/`에 스크립트·로그) |
| 정리 | http.server 8747·드라이버 PID 종료 확인(평가자 `lsof`·`ps` 0) | 8733 종료·프로세스 0 |

## 결과 요약

- 두 Coordinator 모두 **첫 검사기 exit 2를 보고 스스로 드라이버를 실행**했고, 잔여 0에 도달했으며(native 슬라이스 3 · control 슬라이스 2), 독립 리뷰어(Agent)를 실제 호출했다. 어느 쪽도 `--phase inputs` exit 0에 이르지 못했다 — 남은 결함은 **사람 결정이 필요한 항목**(빈 목록·폼 오류 등 데이터/텍스트 상태의 case 제외 승인)이며, 두 Coordinator 모두 이를 대신 결정하지 않고 반환했다.
- native는 기계 결함 0(잔여·표면 연결·served·크롭·exact-field 전부 통과)이고 유일 defect가 리뷰어 fail이다. control은 기계 결함 18(새 표면 16 미연결 + v1 잔존 2)이 남았다 — 구 규범은 «새 표면 → case 추가 → 예외» 순서를 몰라 표면 16개를 «사용자 예외 결정 D-C~D-E»로 넘겼다.
- control의 드라이버 예산: 잔여 0 뒤에도 «partial ∧ 잔여 0 = 통과» 규범이 없어 11슬라이스(88분)를 전부 썼다(native 4슬라이스 32분).
