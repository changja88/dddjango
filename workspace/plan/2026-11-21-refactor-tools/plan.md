# 계획 v1.1 — dddjango 2.44.0: 리팩토링 도구 한계 둘(F4-199 · F4-200) + 동작 보존 장치의 지금 판 구멍

작성 2026-11-21 · 운영자. v1 → v1.1: 계획 검토 T(차단 0 · 중요 1 · 사소 5) · P 셋째(중요 1 · 사소 4) 모두 받음(`op-rev-DISPOSITION.md` 끝 두 절). 설계 = `design.md`(머리 · 결정 D1 ~ D10) + §A `design-a.md`(F4-199 · patch-d) + §B `design-b.md` v2 · `design-b-v3.md` · `design-b-v4.md`(F4-200 · D8 · D9) + 규칙 글 정본 `rules-final.md`. 설계 검토 T · P 처분 `op-rev-DISPOSITION.md`(검토 T 둘째 재확인 차단 · 중요 0 · 검토 P 둘째 재확인 중요 2 는 글 고침 — 이 계획 검토에서 셋째로 좁게 확인). 기준 main = `f2dad56b`(2.43.0 release `3293b498` 뒤 봉인 · 기록 커밋만 — scripts · 그래프 무변) · 옛 판 대조 = `3293b498`(HEAD 금지).

## 1. 단위 · 맡은 파일(겹치지 않게)

| 단위 | 맡은 파일 | 하는 일 | 바탕 |
|---|---|---|---|
| A 장치(F4-199) | `dddjango/scripts/refactor_audit.py` · Codex byte `codex-dddjango/skills/dddjango/scripts/refactor_audit.py` · `workspace/tools/refactor_audit_fixture_run.py`(새 함수 `closed_window_shared_cases` · 변이 표 줄) | 수리판 `repro-a/patch-d/` 를 옮김 + red 꼬리를 `where` 대로 «이 V 인용은 지금 시험 원문으로» / «열린 창 기준선 원문으로»(검토 P 둘째 중요 1) · 사례 `repro-a/cases_draft3.py` 16 → 러너 · 변이 일곱 | design-a §1 · §1-3 · §3 |
| B 장치(F4-200 + D8 · D9) | `dddjango/scripts/behavior_guard.py` · Codex byte 같은 이름 · `workspace/tools/behavior_guard_fixture_run.py`(`norm_checks` · 기존 사례 둘 고침 · `--mutation-test` 변이 줄) | 수리판 `repro-b/v4/scripts/behavior_guard.py` 를 옮김 + 검토 T 둘째 사소 1(`rev-t/v4b-right-shaky.diff` — 오른쪽 · 둘째 인자 불안정 이름 두 쪽) · 사소 2(위치 인자 하나 + `second=` 면 첫 인자도 기대 — 두 자리 모두 `e` · 러너 K1 `assertEqual(200, second=r.status_code)` → 201 멈춤 단언) · 사례(같은 뜻 15 · 반례 25 · V1 ~ V4 · H11 · 검토 T 반례 · L1 ~ L4 · combo · t_ut 46 · t_v3 38 · t_v4 19 · X6r · X6u · K1 · 창 사례 — design-b v2 §7 · v3 §7 · v4 §7) · 기존 러너 사례 92 · 228 고침안(design-b-v3 §7 — d · b 꼴 남기고 a · c 꼴 더함) · 변이 36 + 새 둘 — 새 변이는 **`--only-new norm` 묶음**에 건다(단위 판정 사례 = 정규화 · D8 · D9 · LCS · pin 은 `_setup_refactor` 없이 · 창 처분 사례만 support 준비 · 실패 표지 «FAIL — behavior_guard 새 갈래» · `_NEW_MUTATIONS` 에 `(…, "behavior_guard.py", "norm", …)` — 전체 러너로 돌면 변이 하나에 약 23분) · 머리말 · D 절 주석의 «원문 AST 만 · 정규화 없음» 낡은 글 고침(`:1433` · `:1719` · `:3893` 꼴) · `rev-t/v4b-right-shaky.diff` 는 경로가 `v4/` · `v4b/` 라 손으로 옮김 · K1 은 사례부터 | design-b v2 · v3 · v4 |
| G 글 | `ontology/rules/command-dddjango.ttl`(R-3791 새 · R-3633 rev4) · `ontology/wiring/command-dddjango.ttl`(R-3791 delegatedTo · enforcedBy · R-3633 enforcedBy behavior_guard 더함) · `agent-coder.ttl`(R-3649 rev3) · `agent-design-architect.ttl`(R-3644 rev3) · `agent-discipline-reviewer.ttl`(R-3647 rev2) · 이름표 다섯 · Codex `codex-dddjango/skills/dddjango/SKILL.md`(b13 글자 그대로 — G 가 자기 worktree 에서 `ontology_render.py --apply command-dddjango` 로 렌더한 글을 옮김 · 합친 뒤 운영자가 `runtime_parity_check` 로 대조) · `dddjango-coder` · `dddjango-design-architect` · `dddjango-discipline-reviewer` SKILL(같은 뜻) · `README.md:321` · `docs/master/work_flow.spec.json` · `docs/master/master.html` 기준 판 | `rules-final.md` 문안 그대로 그래프에 · 새 Expression `@<구현일>` · revisionKind amendment · 이름표 · Codex · 문서 | rules-final §1 ~ §7 |
| 운영자 | `ontology/ISSUED`(R-3791 한 줄 손으로) · 렌더 산출물(`dddjango/commands/dddjango.md` · `agents/*.md` · Codex references) · `ontology/LEDGER.tsv`(네 행) · target-counts · q4 golden · `dddjango/scripts/rulepack.json`(두 사본) · 골든(바뀌면 — `findings_count_matrix` · `checker_baseline_matrix` · `gen_pregate_symbol_kinds`) · `workspace/tools/anchor_diff_smoke.py` 등 공용 도구 기대(돌려서 바뀌면) · 파생 문서(`docs/master/work_flow.html` · `file_tree.html` · mkrev2 뒤 decision-record 되돌리기) · 매니페스트 판 · 봉인 | 합치기 뒤 파생물 · 검사 · 배포 | — |

- 구현자는 Claude 서브에이전트 셋(A · B · G), 각자 `workspace/scratch/refactor-tools-1121/wt-<단위>/`(main `f2dad56b` 의 git worktree · 임시 브랜치 `tmp/impl44-<단위>`)에서 일하고 자기 브랜치에 커밋 → 운영자가 diff 를 main 작업 트리에 apply. 지시문 = `IMPL-BRIEF.md`(DEVELOPMENT §7.5 늘 적는 것 · 장치 단위는 §3 체크리스트 8 · 대상 저장소 · 레인 폴더 읽기만 · 읽기 전용 git 포함 명령 금지 · /tmp 금지 · 끝 보고는 본문으로 — 하위 에이전트는 보고 파일을 못 씀).
- 수리판은 배포판 2.43.0 사본 위에서 만든 것이고 main 은 그 뒤 바뀌지 않았다(계획 검토 T 확인 · 구현 시작 때 `git diff 3293b498 f2dad56b -- dddjango/scripts codex-dddjango/skills/dddjango/scripts workspace/tools Makefile ontology` 빈 것 다시 확인).

## 2. 차례

1. worktree 셋 · IMPL-BRIEF.md → 구현자 셋 병렬.
2. 받은 diff 를 main 작업 트리에 `git apply`(시작 시각 뒤 바뀐 파일 목록 = 맡은 파일 대조) · ISSUED.
3. 그래프 파이프라인(운영자): canon_turtle 왕복 → ontology_gate → `ontology_render.py --apply` → LEDGER 네 행 → target-counts(NormShape · WorkShape 3800 · ExpressionShape 4509) → q4 golden → `make rulepack` → corpus_mirror_sync `--write` → `runtime_parity_check`(Coordinator Codex 글자 대조) → 소스 미러 대조.
4. 골든 · 공용 도구 기대: 돌려서 바뀐 것만(바뀌면 그 줄을 재현해 까닭 확인 뒤 받음).
5. 행동 시험(§4 — 옛 판 `3293b498` · 새 판 나란히).
6. 구현 독립 검토 둘(도구 IT · 글 IP — IP 는 rules-final 문안 · 이름표 다섯 · Codex 넷 · README 대조) → 지적 재현 → 고침 → 좁은 재확인.
7. 체크리스트 8 · 봉인 → 커밋(경로 하나씩) → `make verify` 전체 + `make verify-mutation` → 장부 다시 읽기 → push → 깨끗한 클론 `make release`(2.44.0 minor) → 노트 → 봉인 chore 둘 → 판 기록 `workspace/plan/2026-11-21-refactor-tools/`(design · rules-final · plan · plan-2.44.0) → 작업 리스트 · 장부 처분 · 정리 · 보고(요청 가이드 «바뀔 것 없음» — dddjango · dddjango-web 한 줄).

## 3. 확인 명령

- 단위마다: A — `refactor_audit_fixture_run.py` 전부 녹색(새 16 · RD-W1 ~ W15 · 관련 묶음) · 기존 ✓ 줄은 글자 같음(새 사례 줄만 더함 · RD-W3 · W9 red 꼬리는 부분 대조라 ✓ 줄 무변) · B — `behavior_guard_fixture_run.py` 전부 녹색(기존 325 줄은 92 · 228 고침안 말고 글자 같음 · 새 사례) · `--mutation-test` 의 새 변이 모두 red · Codex byte `cmp` · G — ontology_gate · render dry-run 차이가 rules-final 문안과 같음.
- 합친 뒤: `make verify` 전체(6/6) · `make verify-mutation` · `claude plugin validate dddjango --strict` · `PYTHONUTF8=1 python3 workspace/tools/manifest_seal.py --check --draft`.

## 4. 행동 시험(옛 판 결함 재현 · 새 판 해소)

| 보고 · 몫 | 옛 판(3293b498) | 새 판 |
|---|---|---|
| F4-199 | 현장 사본 `changes --gate` red 5 · 장난감 RD-W16 · 24 red | red 0 · digest = 현장 마지막 확정 줄 · 뒤 슬라이스 인용 red 에 고칠 길 꼬리 · 보존 red(W18 · W26) 지킴 |
| F4-200 | 현장 H11 꼴(`T * 5` → `T * SLACK`) 0T · 0F red | 개별 감사 · 값 5 → 6 은 red · V 인용 원소 ① 은 red |
| D8 | mock 키워드 이름 · unittest `assertEqual` 값 바꿈 «변화 없음» | 확정 변화 · 0T · 0F red · 주어 · 메시지만은 같음 |
| D9 | 글자 왼쪽 `in` · `200 == r` · `pytest.raises(E, f)` 기대 바꿈 «변화 없음» · 주어만 바꿈 red | 기대 바꿈 red · 주어만 바꿈 개별 감사 |
| 같은 뜻 | 값 → 상수 · 식 → 상수 · 지역 변수 · 집합 순서 · 이름 바꾸기 red | 개별 감사(기대 의미 그대로) |
| 지킴(퇴행 감시 — 두 판 같아야) | X1 · X6(global · 글자로 받는 주어) · G1 ~ G3 red · L1 · L4 감사 · F4-199 A2-1 green · A3 보존 red | 같음 |
| C2(진행 중 실행에 보이는 유일한 green → red) | 변경 창 V 승인 케이스가 ①~④ 뿐 → 승인 변경 | 승인 변경 미검출 |

현장 사본: F4-199 는 `repro-a/field-proj/`(대상 `.git` 객체 · 트리 일부 사본) · F4-200 H11 은 `repro-b/field/`(시험 파일 사본) — 행동 시험 뒤 정리(§7.4)에서 꼭 지운다(대상 저장소에서는 명령 안 씀 · 읽기만).

## 5. 멈출 기준

- 구현 검토 차단이 셋째 좁은 확인에도 안 닫힘 → 멈추고 묻는다.
- `make verify` · mutation 이 고침 뒤 세 번째에도 붉음 → 멈추고 묻는다.
- 설계에 없는 기존 러너 줄 · 골든 기대가 바뀜(behavior_guard 러너 92 · 228 밖) → 재현해 까닭 확인 전에는 받지 않는다.
- 행동 시험에서 옛 판이 결함을 재현하지 않거나 새 판이 못 풂 → 설계로 돌아간다.

## 6. 진행 중 실행 · 노트 «도는 실행»

- pre-gate: 판정 무관 · 실행 트리 digest 가 바뀌어 도는 실행은 다음 G1′ · G2 전에 재예보(검토 P 중요 6) — 보고에 진행 레인.
- F4-199: 같은 슬라이스 다중 owner 소비 원소 red → green · 뒤 슬라이스 V 의 낡은 인용은 red(꼬리 안내) · 2.43.0 아래 G1′ 이 가장 앞 슬라이스 owner 의 소비된 원소를 지금 글로 다시 썼으면 보존 red.
- F4-200 · D8 · D9: 2.44.0 으로 다시 close 하는 창에서만 · ①~④ red → 개별 감사 · C2(V 승인 케이스 ①~④ 뿐 → 승인 변경 미검출) · 진행 중 레인 하나 mock 키워드 든 단언 12줄 · 현장 비교 원소 8% 열쇠 쪽 바뀜(글자 왼쪽 `in` 주어 이름 바꾸기는 풀리고 글자 편집은 멈춤 · 둘 다 이름인 `in` 404 는 왼쪽만 바꿔도 새로 멈춤) · global · `setattr(sys.modules…)` · unittest 단언 현장 0.

## 7. 받아들인 한계(노트 · 판 기록과 같은 목록)

design.md §3 + design-b-v4 §7 한계 바꿈(사소 1 반영으로 «불안정한 이름» 은 어느 쪽이든 두 쪽 · 사소 2 반영으로 `second=` 꼴 넣음 · 한계 ② 에 «unittest 첫 인자도 같음») · 이번 판 밖(작업 리스트 후보): import 상수 · 열거형 멤버 상수 · 대칭 연산 `200 == r` ↔ `r == 200` 같음 · `pytest.raises(E, f).match(…)` · `django_assert_num_queries` 픽스처 · 새 보고 F4-202(#473 · 11:59 · 다음 판).

## 8. 되돌릴 수 없는 것 · 시간

- 되돌릴 수 없는 것: 없음(배포 · push 는 make 릴리즈 타깃 · 대상 저장소는 읽기만).
- 규모: behavior_guard.py 배포판 대비 약 +490 · 러너 +약 300 · refactor_audit.py 약 +41 · 러너 +약 116 · 그래프 새 1 · 개정 4 · LEDGER 4 · Codex SKILL 4 · byte 미러 2.
- 시간(추정 · 검토 T 고침): 구현 — B 가 길목 5 ~ 6시간(사례 약 200 옮김 · K1 · v4b · 변이 38 묶음 연결 · 전체 러너 두 번 약 24분씩 · `--mutation-test` 한 번 30분 넘게) · A · G 1.5 ~ 2시간 병렬 · 합치기 · 파생물 · 행동 시험 1 ~ 1.5시간 · 구현 검토 1 ~ 1.5시간 · verify(약 85분) · 배포(약 55분) 2.5시간 — 합 10 ~ 12시간.
