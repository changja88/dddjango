# 계획 v1.1 — dddjango 2.45.0: F4-181 · 182 · 189 · 201 · 203

상태: 계획 검토 닫힘(재확인 둘째 차단 0 · 중요 0 · 사소 0 · 11-22 22시 27분) · 사용자 «진행» · 구현 뒤 바뀐 것은 `plan-2.45.0.md` «독립 검토 반영» 이 정본. 정본 설계 = `design.md` v2.1. 옛 판 = 2.44.1 `77a1ed54ea28eee0eb1edea785e53ae7265c2e1a`.
dddjango-web 무변. 이 계획은 설계를 바꾸지 않는다 — 어긋나면 설계가 이기고, 계획을 고친다.

## 1. 바뀌는 동작

| 보고 | 전 | 후 | 절 |
|---|---|---|---|
| F4-181 | 승인한 main 들임의 ⓓ 줄이 «신규» 로 섞여 줄마다 닫음 | «신규» 와 «승인 유입» 을 따로 · 유입은 감사에 묶음 한 물음 | 설계 §1 |
| F4-182 | `__pycache__` · 캐시만 남은 폴더가 BC → 거짓 red | BC 로 세지 않음 | 설계 §2 |
| F4-189 | `-I` · `-P` · `PYTHONSAFEPATH` 에서 검사기가 죽고 게이트가 가릴 수 있음 | 정상 실행 | 설계 §3 |
| F4-201 | 정규식 제외 경로의 생성 문서에 나지 않는 503 | 새 칸 `exempt_pattern` 으로 뺌 · 옛 칸 · 옛 사본 무변 | 설계 §4 |
| F4-203 | e2e 행 타입을 다는 길이 글에 없음 | `Protocol` + `.create()` 한 문장 · 검사기 무변 | 설계 §5 |

## 2. 단위 · 맡은 파일

Claude 쪽 scripts 를 고친 단위가 Codex 짝도 byte 로 맞춘다. 일꾼은 커밋하지 않고 worktree(이 일 폴더 안 `wt-c` · `wt-p`)에서 `git add -N -- <맡은 경로>` 뒤 맡은 경로만 diff 로 낸다(새 파일 포함). 운영자가 worktree 둘에 `.venv` · `.venv-probe` 링크를 먼저 둔다(플러그인 폴더는 링크하지 않는다). 새 옛 판 대조는 `_released_gate(td, "<77a1ed54 전체 SHA>")`(scripts 통째) — `HEAD` 금지.

### 단위 C — §1 → §2 → §3(한 사람 · 이 차례)

- `dddjango/scripts/`: `registry_gate.py` · `business_vocab.py` · `design_pregate.py`(기준선 BC 한 줄) · `behavior_guard.py` · `regen_core.py` · `refactor_audit.py` · `check-*.py` 27.
- 그 가운데 `check-openapi-error-declaration.py` 는 **§2 열거 한 줄 + 기존 `try` 묶음(`:46-48`) 안 `import business_vocab as vocab` · §3 머리 import 만**(`__import__` 꼴을 쓰지 않는다 · 다른 자리에 import 하면 P 와 충돌). 이 파일은 diff 에 섞지 않고 고친 파일째 따로 낸다.
- `checker_target.py` 코드 무변(`joint_bc_names` 의 이름 거름 그대로 — 시제품 `op3/x` 의 그 줄은 옮기지 않는다). 캐시만 남은 BC 는 `server_bc_dirs` 를 따라 G0 목록에서도 빠진다.
- `workspace/tools/`: `registry_gate_smoke.py`(F4-181 · pre-gate 예보 · 도구 셋의 `-I` 시험과 변이) · `field_report_checker_smoke.py` · `fixture_matrix.py`(1278 행 F4-147 변이를 `bc_folder` 이름 거름 변이로 옮김) · `checker_lint.py` + 픽스처.

### 단위 P — §4

- `dddjango/scripts/`: `pre_route_responses_canonical.py` · 새 `pre_route_responses_canonical_2_38_0.py`(= 2.44.1 자산 byte) · `check-openapi-error-declaration.py`(§4 구역만 — C 의 두 자리는 건드리지 않음). `_2_37_0.py` 무변.
- `workspace/tools/`: `api_error_backstop_matrix.py` · `pre_route_behavior_smoke.py` · `pre_route_canonical_check.py` · `manifest_seal.py`(목록) · `reverse_coverage.py`(분류) · 픽스처의 정본 사본 셋(`openapi_decl_missing` 둘 · `openapi_error_declaration` 하나) · `workspace/eval/fixtures/pre_route_behavior/`(toy · tables).
- `pregate_fixture_run.py` 는 P 만 — 먼저 돌려 보고, 고칠 게 생기면 고치기 전에 보고. `anchor_diff_smoke.py` 도 같다.
- §4 변이는 영구 표에 넣지 않는다. scripts 사본에서 한 번 돌려 변이마다 명령 · 붉은 사례 이름을 낸다.

### 운영자

- 합치기: 두 diff `git apply`. openapi 검사기는 **`git merge-file -p <C 파일> <2.44.1 파일> <P 파일> > <결과>`(이 차례 — 바탕을 첫 인자로 주면 exit 0 인데 C 의 고침이 사라진다 · 실측)** → exit 0 · `sys.path.insert` 1 · `bc_folder` 1 · `exempt_pattern` 구역 있음을 확인 → 두 런타임에 복사.
- 그래프 — 리비전 13(ExpressionShape +13 · Codex 짝 줄마다):

| 파일 | 규범 | 자리 |
|---|---|---|
| `command-dddjango.ttl` | R-0284 · 3664 · 3725 · **3440** · 3727 | 커맨드 167 · 170 · 231 · **233(G2 배너)** · 255 |
| `agent-discipline-reviewer.ttl` | R-1011 · 1074 · 1075 | 100 · 111 |
| `implementation-django-ninja-final.ttl` | R-3749 · 3750 + 코드 블록 | §6.2 |
| `implementation-test-final.ttl` | R-3752 | §19.2.1 행 시험 |
| `agent-design-review-api.ttl` | R-2686 | 12번 |
| `discipline-houserules-skill.ttl` | R-3148 | §4 |

- 무변: 커맨드 229(위반 유입) · 255 의 «신규분만 blocker» · 306(BC 점검 예외). 306 이 인용하는 «ⓓ 신규(N′∖L′)» 글자는 167 에 남긴다.
- 산물: render → LEDGER → 계수표 → q4 → rulepack → `workspace/reference` 소스 미러 → `corpus_mirror_sync` → Codex 조정자 · 역할 · 스킬 같은 뜻.
- G12: 새 이름표가 식에 걸리는 규범만 `scope-limit-norms.md` 에 분류 → `rulepack_smoke.py` `DRIFT_REVIEWED`.
- 글 계약: render · Codex 글 뒤 `field_report_checker_smoke.py` 에 방아쇠 넷 + G2 배너(Claude · Codex) — 2.44.1 글에서 붉음을 먼저 본다.
- 골든: `findings_count_matrix` · `checker_baseline_matrix` · `checker_cross_matrix` · `construct_drift_report` · `gen_pregate_symbol_kinds --root <트리>`(마지막 · 일꾼은 쓰기 모드 금지). 설명 못 하는 차이는 갱신하지 않는다.
- 문서: README 297(제외 경로 한 구) · `docs/master/master.html` 기준 판 2.45.0 · 요청 가이드는 확인만(바뀔 칸 없음으로 보임).

## 3. 차례와 확인 명령

| 단계 | 하는 일 | 지나는 조건 |
|---|---|---|
| 1 | worktree · venv 링크 → C ∥ P. 새 시험을 2.44.1 에서 먼저 | 새 시험 붉음을 봄 |
| 2 | C: `registry_gate_smoke` · `field_report_checker_smoke` · `fixture_matrix` + 세 도구의 변이 모드 · `checker_lint` · `pregate_fixture_run` · `pregate_field_report_smoke` · `behavior_guard_fixture_run` · `behavior_probe_fixture_run` · `refactor_audit_fixture_run` · `regen_loop_smoke` · `folder_group_fixture_run`(+ `/usr/bin/python3` 로 `--require 3.9`) | exit 0 · 설계 §1 ~ §3 변이가 죽음 · 27종 세 꼴 81/81 |
| 3 | P: `api_error_backstop_matrix` · `pre_route_behavior_smoke` · `reverse_coverage` · `anchor_diff_smoke` · `pregate_fixture_run` · `field_report_checker_smoke` · `fixture_matrix` + §4 한 번 변이 | exit 0 · 변이가 죽음(`pre_route_canonical_check` 는 render 뒤 운영자) |
| 4 | 합치기 → 그래프 파이프라인 → G12 · 글 계약 → 골든 | `ontology_gate` · render sync · `ontology_ledger_check` · `query_golden_check` · `rulepack_smoke` · `runtime_parity_check` · `corpus_lint` · `corpus_mirror_sync --check` · `pre_route_canonical_check` · `reverse_coverage` · `refactor_audit_fixture_run` · `field_report_checker_smoke` · `gen_pregate_symbol_kinds --check` |
| 5 | 합친 판 행동 시험(§4) | 표대로 |
| 6 | 구현 독립 검토(새 눈 · «커밋 뒤에도 같은가» 포함) → 재현 · 처분 → 좁은 재확인 | 차단 0 |
| 7 | 문서 고침 → 봉인 ① → 커밋 → `make verify` · `make verify-mutation` · README 면 DEVELOPMENT §1 대상 명령 | exit 0 |
| 8 | 장부 다시 읽기 → push | 새 항목은 이름 적음 |
| 9 | 깨끗한 클론 `release-2.45.0/CL` → `make release`(minor) → 노트 → 봉인 chore 둘(T2-0b 설계 문서 판 칸 포함) | strict 봉인 대조 |
| 10 | 판 기록 `workspace/plan/2026-11-22-small-fixes/` · 작업 리스트(넷 지움 · F4-204 · 205 · 설계 §7 후보 더함) · 장부 처분 · 진행표 둘 · 정리(현장 사본 · scratch 안 CLAUDE.md 사본이 든 폴더 포함) · 보고 | 잔재 0 |

## 4. 행동 시험 — 옛 2.44.1 ↔ 합친 판, 같은 입력

| 입력 | 옛 | 새 |
|---|---|---|
| F4-181 `a/toy` c1 + 목록 | ⓓ 신규 5 | 신규 1 · 유입 4 · exit 0 그대로 |
| F4-181 `a/toy` c2 + 목록 | 신규 5 | 신규 2 · 유입 3 |
| F4-181 `a/toy` c3 + 목록 | 신규 1 | 신규 1 · stdout byte 같음 |
| F4-181 c1 ~ c3 목록 없음 | — | stdout byte 같음(툴체인 행 밖) · sidecar 는 `_mask_sidecar` 뒤 같음 |
| F4-181 `rev/g_cross.py`(표를 레인이 고침) | 신규 | 유입 절 · sidecar 에 남음 |
| F4-181 `rev/g_moves.py` | legacy 3 · 해소 0 | legacy 3 · 해소 0 · 유입 1 |
| F4-182 캐시 이름 — 직접 실행 | 거짓 red | 0(게이트는 옛 판도 green) |
| F4-182 캐시만 남은 BC 자리 — 게이트 | 거짓 red | 0 · 가리던 #365 되살아남 |
| F4-182 `rev/c_keep.py` `.gitkeep` 새 BC | red 17 | red 17 |
| F4-182 앵커 `.gitkeep` · gitlink · P8 · guard_zero · build · dist · 지운 · 옮긴 BC · pre-gate 예보 | — | 설계 §2 시험 그대로 |
| F4-182 `checker_target.py --joint-list` · 캐시만 남은 `ghost` | 목록에 듦 · `--bc ghost` exit 0 | 목록에서 빠짐 · `--bc ghost` exit 1 «BC 없음» |
| F4-182 빈 폴더 · `.DS_Store` 동반 | red | red(받아들인 한계) |
| F4-189 27종 × `-I` · `-P` · `PYTHONSAFEPATH=1` | 0/81 | 81/81 |
| F4-189 세 도구 함수 안 import · 심은 `json.py` | 죽음 | 정상 · 안 읽음 |
| F4-189 c1 + `PYTHONSAFEPATH=1` · 목록 없음 게이트 | exit 0(거짓 green) | exit 2 · 귀속 5 |
| F4-201 `c/toy` 에서 `files/[^/]+` 줄을 뺀 사본 + 새 칸 | 문서 503 11 · 어긋남 5 | 7 · 어긋남 1(`\d+` 는 남음) |
| F4-201 `c/toy` 그대로 + 새 칸(글이 금지한 설정 · 대조) | 어긋남 5 | 어긋남 2 — `files/{name}` 은 문서 모자람 |
| F4-201 깨진 정규식 · 글자 `.` | — | 실패 그대로 · 글자 칸 무변 |
| F4-201 옛 사본 둘 × 옛 칸 | 받음 | 같음 |
| F4-201 옛 사본 + 새 칸 | 모르는 칸 | #63 «지금 판 정본이라야» |
| F4-203 하우스룰 예 | — | 27종 · mypy strict · pytest 통과 · 검사기 출력 무변 |
| 픽스처 전 뿌리 | — | 설계가 바꾸는 줄 밖 차이 0 |

## 5. 멈출 기준

- 설계에 없는 새 red 가 기존 픽스처 · 옛 사본 · 옛 표에 하나라도 서고 구현 잘못이 아니면 멈추고 사용자에게 보인다.
- §2(캐시 이름 · 캐시만 남은 BC 자리) · §3(`-I` · `-P` · `PYTHONSAFEPATH`) 조건이 없는 입력에서, 승인 목록이 없거나 ⓓ 유입 0 인 게이트 출력이 바뀌면(툴체인 행 밖) 합치지 않는다.
- 이 계획에 없는 파일 · 새 술어 · 새 규칙 번호가 필요해지면 그 단위를 멈추고 계획부터 고친다.
- 좁은 재확인 셋째에도 차단이 남으면 멈추고 묻는다.
- 장부에 이번 다섯의 전제를 뒤집는 덧붙임이 오면 멈춘다.

## 6. 판 밖

- **F4-204**(옮김 뒤 지원 확인을 다시 뜨면 옮긴 시험 대조 원점이 바뀜) · **F4-205**(G1 변경판 digest 가 처방 글 · 슬라이스 계획을 덮지 않음) — 11-22 20:20 · 21:04 등록 · 재현 `e/probe.py` · **다음 판**. 이번 다섯이 고치는 규칙 · 문단 · 판정 줄과 겹치지 않고, G1′ 승인 범위라는 따로 정할 설계가 든다.
- 설계 §7 후보(작업 리스트로).

## 7. 한계 · 되돌릴 수 없는 것 · 시간

- 한계 = 설계 §7. 묶음 물음은 읽어야 보이는 판정이고, 정규식 ↔ 템플릿은 검사기가 값을 읽지 않는다.
- 2.18.2 시험 기대 하나(`registry_gate_smoke` `cache_bc`)를 뒤집는다 — 판 기록에 적는다.
- 되돌릴 수 없는 자료 변경 없음. 공개 태그 · 릴리즈는 남고, 잘못되면 다음 판으로 되돌린다.
- 진행 중 실행: pre-gate 실행 트리 digest 가 바뀌어 재예보.
- 시간(추정): 승인 뒤 **9 ~ 12시간** — 구현 · 무거운 시험 3 ~ 4 · 그래프 · 골든 1 ~ 1.5 · 구현 검토 · 고침 2 ~ 3 · verify · mutation · release 3 ~ 3.5. `registry_gate_smoke` 한 번이 부하 때 40분쯤이다.
