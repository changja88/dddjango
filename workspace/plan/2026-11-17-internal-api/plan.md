# dddjango 2.41.0 계획 — F4-150 내부 API 객체의 표준 자리(계획 v1.2 · 2026-11-18)

v1.2 = v1.1 + 좁은 재확인 사소 둘(가림 줄 글자 · 시험 사례 자리). v1.1 = v1(`plan-v1.md`) + 계획 독립 검토 처분(검토자 P 차단 1 · 중요 8 · 사소 6 · 모두 받음 — `op-rev/DISPOSITION.md` 끝 절). 설계: `design.md`(확정 v1.3). 사용자 결정: 별도 API 객체 · `/internal/`(11-09 «나.») · 내부 창구 인증 의무 줄 없음(11-18 Q1 «나.») · 사설망 http 허용 한 줄(11-18 Q2 «가»).

## 1. 무엇을 왜

한 BC 가 손님용 창구와 앞단이 인터넷에 열지 않는 창구(SSE 서버 · 워커가 부름)를 함께 가질 때 둘째 API 객체를 둘 표준 자리가 없어, 현장 레인이 검사기 막힘(#429 · #107 · #109)을 빚으로 넘기고 내부 scope 렌더는 «분석 불능»(exit 1 · 빚 불가)으로 멈춘다(배포판 2.40.0 재현 · 설계 §1). 표준 자리(`<project>/internal_api.py` · `register_<bc>_internal_api` · `/internal/`)를 열고, 그 자리 밖의 둘째 객체(R-0717)는 계속 막는다.

## 2. 단위 · 맡은 파일

구현은 Claude 구현자가 일 폴더 안 worktree(`impl/wt-<단위>` — 저장소 원본에서 `git worktree add` · 임시 브랜치)에서 전체 diff 를 내고 운영자가 main 에 넣는다(고침 회차는 옛 diff `git apply -R` 뒤 새 diff · main 과 worktree byte 대조). **C ∥ G 는 맡은 파일이 겹치지 않는다 · T 는 C · G 를 넣은 뒤 차례로 그 파일들도 고친다.**

**C · G 공통 지시**: 새 글 · 메시지 · 시험 기대에 «트리 N행»(N ≥ 167)을 쓰지 않는다(새 168행 인용은 T 가 넣음). 런타임 글에 설계 근거 · 메타 코멘트를 넣지 않는다. 앵커 차분 시험에서 `TMPDIR` 을 저장소 안으로 바꾸지 않는다.

### C 검사기
- 맡은 파일: `dddjango/scripts/check-composition-root.py` · `check-layer-skeleton.py` · `check-openapi-error-declaration.py` · `check-api-error-controller-contract.py` · `check-context-isolation.py` · `check-usecase-dto-placement.py` + Codex byte 미러 · `workspace/tools/api_error_backstop_matrix.py` · `anchor_diff_smoke.py` · `registry_gate_smoke.py` · `field_report_checker_smoke.py` · `fixture_matrix.py` · `workspace/eval/fixtures/`(새 usecase-dto 사례 픽스처 폴더 · skeleton good_bc · good_cross · good_grouped · good_promoted · good_promoted_flows · folder_group good · skeleton bad_grouped 에 빈 `config/internal_api.py`).
- 할 일: 설계 §4 그대로(정본은 설계 문장). 출발점 = 시제품 P4(`rv-c/proto4/scripts`) — **P4 에서 버릴 것 · 없는 것**: 공개 mount `api/` 고정(:3254 — 걷음) · 함수 이름의 «legacy»(checker_lint #591) · #437 overlap 없음(`_OVERLAP_RULES` 에 #437 · discriminant = 파일 단위) · `_PROTO_ROOT` 전역 · 부를 때마다 rglob · #15 의 파일 이름만 보는 판정 · #431 · usecase-dto · API 표면 판정 덤 경로(`check-composition-root.py:2773` · `check-usecase-dto-placement.py:249` · `:287`) 고침 없음(새로 함 · #431 메시지와 골든 포함).
- 시험 사례(적대 꼴 영구 자리 = `api_error_backstop_matrix` composition 절 · #431 사례는 같은 파일 `context_cases` · usecase-dto 사례는 그 하네스가 못 돌려(`TARGET_ONLY_CHECKERS` 밖) `fixture_matrix` + 새 픽스처 폴더): 설계 §4 끝 «꼴별 기대» 전부(V1 ~ V22 중 막아야 할 것 · V20 · V21 = 0 · 빈 `internal_api.py` = 0 · 빈 모듈을 `--api-module` = 사용 오류) · 단일 API `path("api/v1/", api.urls)` = 0 · T3 공개 렌더 #437 한 줄 · `internal_api.py` 에 `import application.x` → #431 + #437 · usecase-dto API 표면 판정 사례.
- **기존 계약 뒤집음 셋**: ① `anchor_diff_smoke` test_R7(«#16 preserve 2.22.2 와 같음» 거둠) ② `NewScopeApiModuleRegression` 을 `_main` 에 넣고(2.33.0 뒤 verify 가 안 돌던 묶음) reg05 기대에 #63 기존분 · reg16 을 `register_lesson_internal_api` 로 · #440 하위 사례 ③ `registry_gate_smoke` same_as_released 넷(test_A1 × 2 · test_A6 · test_B11) — 대조에서 가리는 것은 layer-skeleton 표 행(`| check-layer-skeleton.py | n | m |`) · legacy 머리 총수(`== legacy 잔존(L∩N) n건 …`) · legacy 의 `check-layer-skeleton.py: n` 줄(한쪽에만 있어도)뿐(검토자 P 실측 `rv-p/out/p4b-rgs-fulldiff.log` · sidecar 는 같음).

### G 그래프 · 글
- 맡은 파일: `ontology/rules/*.ttl`(implementation-django-ninja-final · skill · architecture-api-final(R-2025) · discipline-houserules-final(R-3216 · R-3217 · #441 글 · broker 한 줄 — TREE 블록 · 행 번호는 손대지 않음) · skill · agent-design-architect · agent-design-review-api · agent-discipline-reviewer · agent-coder · agent-acceptance-tester · command-dddjango · implementation-test(:2417 뜻)) · `ontology/ISSUED` · wiring · `LEDGER.tsv` · target-counts · q4 골든 · `make rulepack`(+ Codex byte) · 렌더 md · `workspace/reference` 미러 · `corpus_mirror_sync` · Codex 같은 뜻 미러 · `README.md` · `docs/master/master.html` · `dddjango/REQUEST_GUIDE.md`(+ Codex byte 미러) · `docs/DEVELOPMENT.md` §7.5(TMPDIR 함정).
- 할 일: 설계 §3 규칙 문장(최종 문장은 구현자 · 검토가 봄) · DEVELOPMENT §3 체크리스트 1 ~ 6 · corpus_lint ⑤(한 문서 안 40자 넘는 같은 문장)를 피해 «빈 `internal_api.py` 는 surface 아님» 을 자리마다 다른 문장으로.

### T 트리 다시 매김(C · G 를 main 에 넣은 뒤)
- 맡은 파일: `docs/master/mkrev2.py` → `file_tree.html`(mkrev2 가 다시 쓰는 `workspace/design/2026-08-07-decision-record.md` 는 되돌림) · `dddjango/scripts/standard_tree.py`(`tree_mirror_check --write`) · houserules TREE 리터럴 · 제목 «182행» · prefLabel R-0338 · R-1683 · R-3112 · 그래프 · 렌더의 «182행» · «172~182행»(architect · discipline-reviewer · command · architecture-ddd · implementation-django final) · Codex SKILL.md 같은 뜻(dddjango-design-architect · dddjango-discipline-reviewer 등) · 살아 있는 «트리 N행» 인용 전부 · 검사기 메시지 하드코딩(`check-layer-skeleton.py:88` · `:907-911` · `check-context-isolation.py:3127` · `check-test-config.py:647`) · scripts docstring · 주석(`check-test-config.py:48` · `check-public-surface-annotation.py:69` · `checker_target.py:63` · `check-app-container.py:36` · `:72` · `:273` · `check-layer-skeleton.py:4` · `:12` · `:18` · `standard_tree.py:3` · `reverse_coverage.py:11` · `:113`) · C 가 더한 골든의 행 번호(`fixture_matrix.py` 는 손으로 · 나머지는 체크리스트 8) · `tree_mirror_check.py`(183) · `spec_lint.py`(`TREE_ROW_MAX` 183 · 새 168행을 가리키는 규칙 행 자리 — #437 «트리 167 · 168행» 등) · tree-revision-spec 행 · mkrev2 WHAT[167] · `:461` 글 · **`workspace/tools/section-path-map.tsv:6` 172 → 173**(`derive_path_globs --check` green 확인 · 쓰기 모드로 덮지 않음) · `docs/DEVELOPMENT.md` §3 트리 개정 순서(T 가 겪은 차례로).
- 할 일: 새 168행 `internal_api.py` · 168 ~ 182 → +1 · 대응표(168 ~ 182 · «172~182» → «173~183» · «167~169» 같은 범위는 끝 +1 · 살아 있는 «182행» → «183») · 제외 목록(`workspace/plan/**` · decision-record · LEDGER 기존 행 · 옛 행 수 뜻 «트리 171행 그대로» · spec #609 · 규칙 «#182» · 파일 행 수 «{n}행») · 숫자 참조 손목록(mkrev2 `WHAT` · `NAMES` · `_NMR` · `_st` 오프셋 `mkrev2.py:2229` · `:2248` · section-path-map) · 그래프를 바꾸면 체크리스트 2 ~ 6(gate → render `--apply` → LEDGER → target-counts · q4(새 Expression 이면) → `make rulepack` + Codex byte → reference 미러 → `corpus_mirror_sync` → Codex 같은 뜻) · **일회 대조 스크립트**(살아 있는 «트리 N행»(N ≥ 167) ↔ 새 `standard_tree` 칸 이름 · 범위 = 플러그인 · Codex 미러 · workspace/tools · scripts 주석) green.

운영자 몫: 단위 diff 넣기 · 재현 · 체크리스트 8(Codex byte 미러 → `findings_count_matrix --emit-expected` 바뀐 행만 · `checker_baseline_matrix` · `checker_cross_matrix --emit-expected`(바뀔 행 = #488 +1 여섯: composition_root · context_isolation · mechanism_ownership · ninja_boundary_middleware · test_config · test_config_entrance — 그 밖이 바뀌면 멈춤) · `construct_drift_report --emit-expected` · `gen_pregate_symbol_kinds.py` 마지막) · 봉인 · 커밋 · 검사 · 배포 · 진행표 둘.

## 3. 차례

1. C ∥ G 구현 → 운영자가 넣을 때마다 재현 · 아래 5 «넣을 때마다» 검사.
2. 구현 독립 검토(코드 · 글 둘) → 지적 재현 · 처분 → 좁은 재확인.
3. T 트리 다시 매김(합친 main 위) → 대조 스크립트 · `derive_path_globs --check` · `tree_mirror_check` · `spec_lint` green → T 짧은 검토.
4. 체크리스트 8 → 봉인 `--write` · `--check --draft` → 커밋(경로 하나씩) → `make verify` · `make verify-mutation` → 장부 다시 읽기(배포 직전) → push → 깨끗한 클론 `make release`(minor → 2.41.0) → 노트 · 봉인 chore(json + T2-0b 설계 문서 둘) → 판 기록 · 장부 처분 · 작업 리스트 · 진행표 · 정리(일 폴더 · `impl/wt-*` worktree 와 임시 브랜치 · `work-a/wt-lane` · 리허설 없음).

## 4. 행동 시험(옛 판 = 3b6d470a 고정 · 새 판 = 합친 main)

- 장난감 `work-a/toys` · 적대 꼴 `rv-c/adv`: 설계 §4 끝 «꼴별 기대» 그대로(옛 판은 재현 표 R1 ~ R10 그대로) · 단일 API `api/v1/` = 0.
- 현장 사본 `field/`: positional — #429 · #107 · #109 사라지고 `[#440] urls.py:86` 하나 · 내부 #16 `--anchor HEAD~1` exit 0(앵커 기존분) · 현장 사본의 진행 레인 worktree 에서 registry_gate 귀속 34 → 33.
- `api_error_backstop_matrix` 기존 사례 불일치 0(새 사례 더함).
- F4-151 한계 둘(L1 · L2) 닫힘 · F4-168 그대로 닫힘.

## 5. 검사

- **넣을 때마다**: 바뀐 검사기 단위 시험 · `fixture_matrix` · `api_error_backstop_matrix` · `anchor_diff_smoke` · `registry_gate_smoke` · `field_report_checker_smoke` · pre-gate 셋 · `checker_cross_matrix` · `findings_count_matrix` · `adapter_layout_smoke` · `folder_group_fixture_run`(3.15 · 3.9) · `checker_lint` · `pre_route_canonical_check` · (G) `ontology_gate` · `ontology_render_sync` · `ontology_ledger` · issued · structural · hierarchy · `query_golden_check` · `ontology_rulepack --check` · `derive_path_globs --check` · `rulepack_smoke` · `corpus_lint` · `corpus_mirror_sync --check` · `request_guide_contract` + cmp · `runtime_parity` · (T) `tree_mirror_check` · `spec_lint` · `reverse_coverage`.
- 주의: `anchor_diff_smoke` · `registry_gate_smoke` 는 unittest 가 하나라도 실패하면 표 부분을 돌지 않는다 — 계약 뒤집음을 끝내기 전에는 표 쪽 붉음이 가려진다.
- 커밋 뒤 push 전: `make verify`(6/6) · `make verify-mutation`(exit 0). 배포는 깨끗한 클론의 `make release` 안 `make verify`.

## 6. 멈출 기준

- 구현 검토 차단이 좁은 재확인 셋째에도 안 닫히면 멈추고 묻는다.
- `api_error_backstop_matrix` · `fixture_matrix` · `registry_gate_smoke` · `checker_cross_matrix` 의 기존 사례가 위 2 에 적은 뒤집음 · 바뀔 행 밖의 까닭으로 바뀌면 멈추고 원인부터.
- 트리 대조 스크립트 · `derive_path_globs --check` 가 설명 못 하는 어긋남을 내면 다시 매김을 넣지 않는다.
- 현장 사본에서 설계 §4 밖의 새 줄이 생기면 멈추고 원인부터.

## 7. 받아들인 한계 · 되돌릴 수 없는 것

- 한계: 설계 §6(앞단 차단 · 인증 의무 없음 · 기존 `/api/internal/…` · `application/**` 안 API 생성 · 공개 API 아래 새 내부 창구 · 오류 식별자 공유 · 비표준 루트 API 의 #63 되풀이 · pre-gate 빈칸 · 진행 레인 명세의 «트리 N행» 인용 낡음 · 채택 프로젝트마다 `internal_api.py` 없음 #488 옛 빚 한 줄 · V3 재대입 렌더 exit 1) + 레인 빚 목록의 `=` 줄에 «트리 N행»(N ≥ 168)이 글자로 들어 있으면 배포 뒤 그 빚이 귀속으로 바뀜(배포 보고에 적음).
- 되돌릴 수 없는 것: 없음(대상 저장소 쓰기 없음).
- 진행 레인: `dddjango/scripts` 가 바뀌어 pre-gate 재예보 필요.

## 8. 장부 새 항목 · 다음 판

- 계획 확정 때 장부 다시 읽음(승인 요청 직전에 한 번 더): 마지막 F4-185. F4-150 판을 연 뒤 붙은 F4-181 ~ 185 는 이번 판에 넣지 않는다(F4-150 과 무관 · 이 판이 이미 60 ~ 70 파일).
- 다음 판 제안: **F4-185**(리팩토링 입구 비동기 시험 지원 밖 · 높음 · 작업 리스트 «새 보고») + 작은 넷(F4-181 · 182 · 183 · 184) — 재현부터.
- 현장 보고 밖 후보(작업 리스트 끝)도 이번 판에 넣지 않는다.

## 9. 걸릴 시간(어림)

구현 C · G 병렬 2 ~ 3시간 · 구현 검토 · 고침 1 ~ 2시간 · 트리 다시 매김 1 ~ 1.5시간 · 체크리스트 8 · 봉인 · 커밋 30분 · verify + mutation 60분 안팎(+ 붉음 고침 1 ~ 2회 여유) · release 약 50분 · 마무리 30분 — 합 8 ~ 10시간.
