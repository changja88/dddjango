# 계획 v1.1 — dddjango 2.43.0: 리팩토링 막힘 여덟 줄(F4-35 · 133 · 188 · 190 ~ 198)

작성 2026-11-20 · 운영자. 설계 = `design.md` v1.3(검토 P · T 처분 · 좁은 확인 차단 0). v1 → v1.1: 계획 검토(검토 T · 차단 0 · 중요 2 — 주인 없는 공용 도구 · 파생 문서 / matrix 확인 환경) 반영 · ISSUED 는 patch 에서 뺌 · 구현 검토 뒤 다시 돌기 · 시간 고침. 기준 main = `ee60b20d`(2.42.0 release `2cdfa49c` 뒤 문서 커밋만) · 옛 판 대조 = `2cdfa49c`(HEAD 금지).

## 1. 단위 · 맡은 파일(겹치지 않게)

| 단위 | 맡은 파일 | 하는 일 | 새 규범 번호 |
|---|---|---|---|
| G-a 글(API) | `ontology/rules/architecture-api-final.ttl` · `implementation-django-ninja-final.ttl` · `implementation-django-ninja-skill.ttl` · 그 wiring · `workspace/reference/`(architecture-api · ninja) · `codex-dddjango/skills/dddjango-implementation-django-ninja/SKILL.md` · ISSUED(자기 번호 줄만) | 설계 §2.1 · §3 · §4 글 · §12 의 API 행 | R-3785 스트리밍 응답 설명서 꼴(Obligation) · R-3786 인증 틀 뒤 인증 실패(Exception) · R-3787 스트림 설명서 openapi_extra(Permission) |
| G-b 글(에이전트 · 조정자 · ddd · cleancode · 시험) | `ontology/rules/agent-*.ttl` · `command-dddjango.ttl` · `architecture-ddd-final.ttl` · `discipline-cleancode-final.ttl` · `implementation-test-final.ttl`(R-1763) · `implementation-test-skill.ttl`(R-3011 · R-3019) · 그 wiring · `workspace/reference/`(ddd · cleancode · implementation-test) · Codex 뜻 미러(`codex-dddjango/skills/dddjango` · `dddjango-coder` · `-design-architect` · `-design-review-api` · `-discipline-reviewer` · `-acceptance-tester` · `-implementation-test`) · 문서(`docs/master/mkrev2.py` · `workspace/design/2026-08-08-tree-revision-spec.md` · `README.md` · `docs/master/work_flow.spec.json` · `docs/master/master.html`) · ISSUED(자기 번호 줄만) | 설계 §2.1 의 에이전트 · 조정자 줄(`--auth-failure` 렌더 · slot 10 «인증 실패(Ninja 401)» · 참조 한 구) · §5 · §6 글 · §7.1 · §11 문서 · §12 의 나머지 행 | R-3788 포트 자료 번역은 어댑터(Obligation) · R-3789 유스케이스 사이 흐름 중복(Exception) · R-3790 옮김 행(Obligation) |
| C 검사기(API) | `dddjango/scripts/check-api-error-controller-contract.py` · `check-openapi-error-declaration.py` · Codex byte 둘 · `workspace/tools/api_error_backstop_matrix.py`(사례만 · 돌리기는 운영자) | 설계 §2.2 · §4 · `--auth-failure` 는 `--event-value` 처럼(`--anchor-baseline` 에서 BC 대조 건너뜀 · `anchor_diff._alias_argv` 로 충분한지 확인) | — |
| P 검사기(포트) | `dddjango/scripts/check-port-adapter-pairing.py` · Codex byte · `workspace/eval/fixtures/port_adapter_pairing/` | 설계 §6 검사기 · 픽스처 | — |
| B 장치 | `dddjango/scripts/behavior_guard.py` · `behavior_support.py` · `refactor_audit.py` · Codex byte 셋 · `workspace/tools/behavior_guard_fixture_run.py` · `refactor_audit_fixture_run.py` · `workspace/eval/fixtures/` 아래 그 둘이 쓰는 자리 | 설계 §5 의 refactor_audit 픽스처 · §7.2 ~ §7.4 · §8 | — |
| 운영자 | `ontology/ISSUED`(R-3785 ~ R-3790 여섯 줄 손으로 — 두 G 단위 patch 에서 뺌) · 렌더 산출물(`dddjango/skills/*/references/final.md` · agents · commands · Codex references) · `ontology/LEDGER.tsv` · target-counts · q4 golden · `dddjango/scripts/rulepack.json` · `findings_count_matrix.py` · `checker_baseline_matrix.py` 골든 · `pregate_symbol_kinds.json`(gen 이 Codex 미러까지) · **공용 도구 기대**(`fixture_matrix.py` · `checker_cross_matrix.py` · `field_report_checker_smoke.py` · `anchor_diff_smoke.py` · `pre_route_canonical_check.py` · `reverse_coverage.py` · `construct_drift_report.py` · `checker_lint.py` · `spec_lint.py` · `adapter_layout_smoke.py` · `pregate_field_report_smoke.py` · `bc_registry_smoke.py` — 단위는 돌려 차이만 보고) · **파생 문서**(`docs/master/file_tree.html` = mkrev2 산출 · `docs/master/work_flow.html` = spec.json 렌더 · mkrev2 뒤 `workspace/design/2026-08-07-decision-record.md` 되돌리기) · **matrix 확인**(`api_error_backstop_matrix.py` 는 code-json 레인이 `git ls-files` 를 써 임시 폴더가 저장소 안이면 환경 실패 — 합친 뒤 `make verify` 안에서) · 매니페스트 판 · 봉인 | 합치기 뒤 파생물 다시 짓기 · 검사 · 배포 | — |

- 구현자는 Claude 서브에이전트 다섯, 각자 `workspace/scratch/refactor-blockers-1120/wt-<단위>/`(main `ee60b20d` 의 git worktree · 임시 브랜치)에서 일하고 patch 를 낸다. 지시문 = `IMPL-BRIEF.md`(DEVELOPMENT §7.5 의 늘 적는 것 · 검사기 단위는 §3 체크리스트 8 그대로 · 대상 저장소 · 레인 폴더 읽기만 · 읽기 전용 git 포함 명령 금지 · /tmp 금지 · 커밋은 자기 worktree 브랜치에만 · 끝 보고는 본문으로).
- G-a · G-b 는 ttl 을 고친 뒤 자기 worktree 에서 gate · render 로 확인만 하고, 렌더 산출물 · LEDGER · target-counts · rulepack 은 patch 에 넣지 않는다(운영자가 합친 뒤 한 번에 다시 짓는다 — 두 단위가 같은 파생 파일을 다투지 않게).

## 2. 차례

1. worktree 다섯 · IMPL-BRIEF.md → 구현자 다섯 병렬.
2. 받은 patch 를 main 작업 트리에 `git apply`(시작 시각 뒤 바뀐 파일 목록 = 맡은 파일 대조) · ISSUED 합치기.
3. 그래프 파이프라인(운영자): canon_turtle 왕복 → ontology_gate → `ontology_render.py --apply` → LEDGER 재기준선 → target-counts → q4 golden → `make rulepack` → corpus_mirror_sync `--write` → 소스 미러 대조.
4. 골든: `findings_count_matrix` · `checker_baseline_matrix --emit-expected` · `gen_pregate_symbol_kinds`.
5. 행동 시험(설계 §10 — 옛 판 `2cdfa49c` · 새 판 나란히 · 장난감 · 현장 사본 · `repro-*` · `rev-t` 재료).
6. 구현 독립 검토 둘(도구 IT · 글 IP) → 지적 재현 → 고침 → 바뀐 단위 몫만 3 ~ 5 다시 → 좁은 재확인.
7. 체크리스트 8(검사기 고침) · 봉인 → 커밋(경로 하나씩) → `make verify` 전체 + `make verify-mutation` → 장부 다시 읽기 → push → 깨끗한 클론 `make release`(2.43.0) → 노트 → 봉인 chore 둘 → 판 기록 `workspace/plan/2026-11-20-refactor-blockers/`(design · plan · plan-2.43.0) → 작업 리스트 · 장부 처분 · 정리 · 보고.

## 3. 확인 명령

- 단위마다: 맡은 검사기 · 장치의 픽스처 러너(`behavior_guard_fixture_run.py` · `refactor_audit_fixture_run.py` · `api_error_backstop_matrix.py` · 포트 픽스처) 녹색 · Codex byte `cmp`.
- 합친 뒤: `make verify` 전체(6/6) · `make verify-mutation` · `claude plugin validate dddjango --strict` · `PYTHONUTF8=1 python3 workspace/tools/manifest_seal.py --check --draft`.

## 4. 행동 시험(옛 판 결함 재현 · 새 판 해소)

| 보고 | 옛 판 | 새 판 |
|---|---|---|
| F4-194 | 0T 나누기 red 5 | 옮김 행 있으면 녹색 · 행 없으면 red · 적대 다섯 red(픽스처 conftest 드나듦 · autouse · 묶임 다름 · 데코레이터 바꿈 · 같은 이름 둘) |
| F4-195 | 0T red 4 | 옮김 행으로 녹색 |
| F4-196 | 현장 재연 red 11 | 0 · 반례(접두 겹침 · 바꿔치기 · 기준 판 이름 · F 꼴) red |
| 정규화 지도 | 변경 창 V 옛 키 red | close · verify 녹색(새 키로 적어도 녹색) |
| F4-197 | field-m1 #228 6 | 0 · 애그리거트 · 엔티티 · 꾸러미 · `ast.Import` red |
| F4-192 | `raise AuthenticationError()` cj #125 | `--auth-failure` 그 클래스면 통과 · 없거나 다른 예외 · 튜플이면 red |
| F4-198 | field ⓓ 7 · 가림 | ⓓ 0 · 가림 #63 · 오류 칸 같은 모듈 상수 판정 |
| F4-190 · 191 · 193 | 글 | 렌더 결과에 새 문장 · 감사 렌즈 절에 실림 · 새 Exception «제외» 가 refactor_audit 를 지남 |

## 5. 멈출 기준

- 구현 검토 차단이 셋째 좁은 확인에도 안 닫힘 → 멈추고 묻는다.
- `make verify` · mutation 이 고침 뒤 세 번째에도 붉음 → 멈추고 묻는다.
- 설계 §1 에 없는 기존 픽스처 · 골든 기대가 바뀜 → 그 줄을 재현해 까닭을 확인하기 전에는 받지 않는다.
- 행동 시험에서 옛 판이 결함을 재현하지 않거나 새 판이 못 풂 → 설계로 돌아간다.

## 6. 되돌릴 수 없는 것 · 시간

- 되돌릴 수 없는 것: 없음(배포 · push 는 make 릴리즈 타깃 · 대상 저장소는 읽기만).
- 시간(추정 · 검토 T 고침): 구현 — B 가 길목 4 ~ 6시간(§7.2 꼴 확인 1~7 · §7.3 지도 · §7.4 · §8 · 적대 픽스처 · 픽스처 러너 한 번 약 15분) · 나머지 넷 2 ~ 3시간 병렬 · 합치기 · 파생물 · 행동 시험 1 ~ 1.5시간 · 구현 검토 1 ~ 1.5시간 · verify · 배포 1 ~ 1.5시간 — 합 8 ~ 10시간.
