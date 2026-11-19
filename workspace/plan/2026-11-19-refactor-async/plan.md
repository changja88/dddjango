# 계획 v1.1 — dddjango 2.42.0: 리팩토링 때 난 문제(F4-185 · F4-183 · F4-184)

> 정리본 — 승인된 계획 v1.1(2026-11-19 사용자 «진행»). 실제 진행 · 차이는 `plan-2.42.0.md`.

정본 설계 `design.md`(**v1.3**) · 처분 `DISPOSITION.md`. 판 2.42.0(minor) · dddjango-web 무변. v1 → v1.1: 계획 독립 검토(차단 0 · 중요 8 · 사소 11) 모두 받음 — 끝 절 «검토 반영».

## 1. 단위(맡은 파일이 겹치지 않음 · worktree `S/wt-{p,f,g}` · 산출 `impl/<p|f|g>-r1.diff`)

| 단위 | 맡은 것 | 맡지 않은 것 |
|---|---|---|
| **P 탐침** | `dddjango/scripts/pytest_probe/dddjango_collect_probe.py`(변형 E · D3 넷 · 사유 셋 · `_S["returned"]` 없음) · `dddjango/scripts/behavior_guard.py`(설명 글 · 표시 이름) · `workspace/eval/fixtures/behavior_probe/{cases.py,expected.json}`(기존 8칸 기대 · 새 사례 약 25 · old-13 `--dist each` · 짝 사례 «완료 조건만» · 칸 수 · counts) · `workspace/tools/behavior_probe_fixture_run.py`(머리 «644 칸» 줄) · `probe-fixture-requirements.txt` · `Makefile`(probe-env 확인 줄 `:343` · 주석 `:329`) · DEVELOPMENT §2 probe-env 패키지 나열 · Codex byte 미러 둘 · worktree 안 자기 `.venv-probe` | 그래프 · md · folder_group · pre-gate |
| **F 묶음 도구** | `dddjango/scripts/folder_group.py`(P1 · `lexists` 막음 · `표지` 줄 = perform 반환에서) · `dddjango/scripts/design_pregate.py`(P2 · P3) · folder_group · pre-gate 픽스처와 러너 사례(«이미 있는 묶음 폴더 + 끝 맞춤 이동» · «이미 있는 UTF-8 아닌 · 링크 표지 그대로» · pre-gate «묶음 group» 셋 · 변이 행 · P1 이 고치는 줄을 닻으로 한 기존 변이 `folder_group_fixture_run.py:1329` 맞춤) · Codex byte 미러 둘 | 탐침 · 그래프 · md |
| **G 글 · 그래프** | `ontology/rules/agent-coder.ttl` · `command-dddjango.ttl` · `agent-discipline-reviewer.ttl` · `ontology/wiring/agent-coder.ttl` · `wiring/command-dddjango.ttl`(새 Norm delegatedTo) · ISSUED · 렌더된 md(`commands/dddjango.md` · `agents/coder.md` · `agents/discipline-reviewer.md`) · LEDGER · target-counts · q4 golden · rulepack · `workspace/tools/rulepack_smoke.py`(DRIFT_REVIEWED) · `workspace/plan/2026-09-26-refactor-path-repair/scope-limit-norms.md`(G12 분류 — 같은 폴더 `progress.md` 는 사용자 로컬 · 경로 하나씩) · Codex 뜻 미러(`dddjango-coder/SKILL.md` `:39` · `:44` · `:71` · `dddjango/SKILL.md` `:173` · `:183` · `:329` · `dddjango-discipline-reviewer` `:62`) · README(`:246` · `:319`) · `docs/master/work_flow.spec.json`(노트 · 노드 · 기준 판) → archify 렌더러로 `work_flow.html` 다시 만들기(겹침 확인) · `docs/master/master.html:140` 기준 판 2.42.0 · isort 측정(scratch venv 에 판 고정 · stdin `--check-only` 가 skip 설정을 따르는지 · `--filter-files`) 뒤 글 확정 · R-3760 세 글귀(`기준선 대비 새 진단 0` · `줄 · 칸 번호를 빼고` · `그 파일에 포매터를 돌려 기존 줄을 다시 쓰지 않는다`) 보존 | 스크립트 · 픽스처 |

## 2. 차례

1. P ∥ F ∥ G(같은 단계 안 병렬 · 각자 worktree · 단위 확인 §3 까지).
2. 운영자: 옛 diff 없이 `git apply` 로 main 작업 트리에 넣고 byte 대조 → main 에서 `make probe-env` · `uv pip check` → Makefile verify-base-core 에 되돌아옴 막기 grep 계약 줄(coder · 조정자 · Claude · Codex 네 파일 — `--no-fix --force-exclude` · «정렬 맞춤»)을 운영자가 더함(I6).
3. **행동 시험 넷**(§4 · 새 판 = 합친 작업 트리 scripts 사본 · 옛 판 = `rel/` 63e40084) — 결과를 검토 입력에.
4. 구현 독립 검토 둘(IC 코드 · IT 글 · 질문에 «커밋 뒤에도 같은 결과인가») → 지적 재현 · 처분 → 좁은 재확인(셋째에도 차단이면 멈추고 묻는다). 검토 반영으로 글을 다시 고치면 같은 판 안 Expression 규칙: 새 Expression 없이 이번 판 Expression 글 고침 → 다시 렌더 → 커밋 안 한 LEDGER 행 고침 · 덧붙임 → q4 `--emit` → `make rulepack` → rulepack_smoke.
5. 체크리스트 8(Codex byte 미러 · 검사기 무변이라 골든 해당 확인 · `pregate_symbol_kinds` 재소성 불필요 확인(입력이 check-*.py · checker_target.py 뿐) · 마지막) → 봉인 `manifest_seal.py --write` → `--check --draft`.
6. 커밋(경로 하나씩) → `make verify` 전체 + `make verify-mutation` → 커밋 뒤 행동 시험 1(SSE) 한 번 더(«커밋 뒤 같음»).
7. 문서 · 요청 가이드 확인(§6 · REQUEST_GUIDE «바뀔 것 없음» 을 보고에) → 배포 직전 장부 다시 읽기(기준: mtime 15:05:37 · 마지막 F4-189 · 마지막 발주자 덧붙임 10:5x).
8. push → 깨끗한 클론 `workspace/scratch/release-2.42.0/CL`(`.venv` · `.venv-probe` 링크 · exclude) → `printf '2\ny\n' | make release`(안에서 `claude plugin validate --strict` · make verify) → `gh release edit --notes-file` → `git pull --ff-only` → 봉인 chore(매니페스트 + T2-0b 설치본 칸) → 재봉인(sealed_commit) → `--check --draft`.
9. 판 기록 `workspace/plan/2026-11-19-refactor-async/`(design · plan 정리본 · plan-2.42.0.md) · 작업 리스트(F4-183 · 184 · 185 지움 · D15 탐침 상태 조작을 «현장 보고 밖 후보» 에) · 장부 처분 줄 · 진행표 둘 · 정리(worktree 셋 · 임시 브랜치 · P 의 `.venv-probe` · 일 폴더 `refactor-async-1119/` · `release-2.42.0/` · `/tmp/djr-verify.*` → `git worktree list` · `git branch` · `ls workspace/scratch/` · `ls -d /tmp/djr-*` 확인) · 보고(pre-gate 재예보 필요 레인 · SSE 리팩토링 레인은 새 실행으로 재개).

## 3. 단위 확인 명령

- **P**: `behavior_probe_fixture_run.py` 전체(새 기대 전부 일치) · `--only` old-13 · 짝 사례 20번씩 흔들림 0 · **변이 셋**(Django 판별 순서 뒤집기 · 결속을 코루틴에만 · 반환 때 놓기를 구간 끝으로)을 넣은 scripts 사본마다 `--engine impl=<사본> --only <새 사례>` → 붉음 · `behavior_guard_fixture_run.py` · `pre_route_behavior_smoke` · `test_watch_fixture_run.py` · `python3 dddjango-web/scripts/test/fixtures_test_watch.py`(새 `.venv-probe` 로 · web 무변 근거) · SSE 사본 전체(366 passed · 탐침 bad 0) · 3.12 · 3.15 장난감 판정 같음 · `diff -rq dddjango/scripts codex-dddjango/skills/dddjango/scripts --exclude=__pycache__`.
- **F**: `folder_group_fixture_run.py`(기존 567 + 새 사례) + `--mutation-test` · 3.9 다리 · `pregate_fixture_run.py` + `--mutation-test` · `pregate_transcription_smoke` · `pregate_field_report_smoke` · `registry_gate_smoke` · `behavior_guard_fixture_run` · `refactor_audit_fixture_run` · byte 미러.
- **G**: `make verify-ontology`(worktree 에 `.venv` 링크) · `ontology_rulepack.py --check` · `rulepack_smoke.py`(G12 걸리면 scope-limit-norms 분류 · DRIFT_REVIEWED) · `ontology_structural_check` · `ontology_issued_check` · `ontology_ledger_check` · `ontology_hierarchy_check --with-golden` · `query_golden_check` · Makefile `:197-198` grep 두 줄 · README 대상 명령(§1 사람용 가이드) · archify 렌더 결과 눈 확인.

## 4. 행동 시험(옛 판 = `rel/` 63e40084 · 새 판 = 합친 작업 트리 사본)

1. SSE 사본(레인 출발 커밋): 옛 판 `support --collect` exit 2(사유 426) → 새 판 exit 0(지원) · 엔진 run 모드 결과 증거 366/366.
2. 비동기 공격 장난감(미리 시작 + 삼킴): 옛 판 G0 정지 → 새 판 G0 통과 · G2 red(결과 증거 없음) — «관문만 걷은» 구현과도 가름.
3. 묶음 장난감(일꾼 C base): 옛 판 registry_gate #655 red · I001 → 새 판 apply 가 표지를 만들어 귀속 0 · **렌더된 coder · 조정자 글의 명령을 글자 그대로** 돌아 정렬 맞춤 0C 창 흐름 close · verify · ruff green(글이 실제로 실행 가능한지).
4. pre-gate 장난감: 옛 판 «empty 충돌(실존)» · 새 파일만 묶음 empty 없음 = 예보 green(실제 #655 red) → 새 판 «묶음 창 몫» 문면 · #655 예보.

## 5. 멈출 기준

- 구현 검토 차단이 셋째 좁은 확인에도 안 닫히면 멈추고 사용자에게 묻는다.
- B0 기존 칸이 설계가 말한 8 칸 밖에서 바뀌면 멈추고 원인부터.
- SSE 사본에서 새 판 결과 증거가 366/366 이 아니면 멈춘다(행동 시험 1 — 차례 3 · 6).
- isort 실측 꼴이 설계와 다르면: 글만 맞추면 되는 차이는 G 가 맞추고 처분에 적음 · 동작이 갈리는 차이면 멈추고 운영자 판단.
- make verify 가 흔들림 칸 밖에서 붉으면 고침 커밋을 더해 처음부터 · 봉인 대상(rulepack_smoke · Makefile · 탐침 등)을 다시 고쳤으면 `--write` 를 다시 하고 처음부터.

## 6. 받아들일 한계 · 되돌릴 수 없는 것

- 한계: 설계 §6 열둘(동기와 같은 한계 · 지원 밖 실행기는 G0 정지 · 리팩토링 모드 대상 BC 밖 I001 은 G2 알림 · 포매터 실패는 안 알림 · 중간 #655 는 글로 · 탐침 상태 조작 구멍은 이번 판 밖 등).
- 되돌릴 수 없는 것: 없음.

## 7. 시간(어림)

- 구현 병렬 약 2.5시간 · 행동 시험 · 구현 검토 · 재확인 약 1.5시간 · 체크리스트 · 봉인 · make verify + mutation 약 1시간 · 배포(안의 verify) · 기록 · 정리 약 1.5시간 → **6 ~ 7시간**.

## 검토 반영(계획 독립 검토 · 모두 받음)

- 중요: I1 G 확인 명령(없는 `--check` 지움 · verify-ontology · structural · issued · ledger · hierarchy · Makefile 계약 · 세 글귀) · I2 rulepack_smoke G12 단계 · I3 main `.venv-probe` 다시 깔기 · test_watch 두 곳 · I4 work_flow.html 다시 만들기 · master.html 기준 판 · I5 isort 측정을 G 에 · I6 되돌아옴 막기 grep 계약 줄(합친 뒤 운영자) · I7 행동 시험을 검토 앞에 · 커밋 뒤 한 번 더 · I8 B0 변이 셋 · F `--mutation-test`.
- 사소: S1 v1.3 · S2 wiring 파일 · S3 같은 판 Expression 순서 · S4 장부 기준 시각 · S5 D15 작업 리스트 · 사용자 알림 · S6 요청 가이드 한 줄 · S7 러너 머리 · Makefile 주석 · DEVELOPMENT §2 · S8 행동 시험 4 옛 판 결과 · 시험 3 글자 그대로 · S9 worktree 자리 · 정리 목록 · S10 봉인 다시 · S11 시간.
- 확인만(문제 없음): 단위 겹침 없음 · `pregate_symbol_kinds` 재소성 불필요 · 검사기 골든 무변 · `표지` 줄이 기존 folder_group 기대를 안 깸 · validate 는 release 안 · 봉인 대상 · final.md 소스 미러 해당 없음 · Codex 자리 · D9 다른 자리 없음 · 행동 시험 1 · 2 가 가름.
