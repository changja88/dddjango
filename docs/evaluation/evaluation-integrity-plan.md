# dddjango Evaluation Integrity Plan

**Goal:** 스킬 개선 전에 dddjango 평가가 실제 목적을 제대로 측정하도록 보정한다.

**Evaluation Purpose:** dddjango는 일반 답변 점수보다 Django/DDD/Django Ninja/TDD/DB 컨벤션 준수를 유도하는 플러그인이다. 평가는 설치 유효성, trigger 정확도, 컨벤션 준수, 실사용성, 비용 대비 효과를 분리해서 봐야 한다.

## Phase 1: Generation Leakage 제거

- [x] `dddjango` variant에만 들어가던 `scoring_focus` 기반 `Focus on:` 지시를 기본 비활성화한다.
- [x] legacy 디버깅용으로만 `--allow-generation-hints`를 둔다.
- [x] positive/negative/ambiguous/conflict trigger 케이스에서 `trigger_type` 기반 정답 행동 주입을 기본 제거한다.
- [x] skill-unit trigger 평가는 positive/ambiguous/conflict에만 로컬 `SKILL.md` 경로를 주입하고, negative trigger는 계속 격리한다. 이는 정답 힌트가 아니라 실제 스킬 적용 가능성을 측정하기 위한 입력이다.

## Phase 2: Skill-unit과 Plugin-real 분리

- [x] `standard` variant set은 `baseline` vs local `dddjango` skill-unit 평가로 유지한다.
- [x] `plugin-real` variant set을 추가해 `baseline` vs `dddjango-plugin`을 생성한다.
- [x] `dddjango-plugin` 실행은 local `SKILL.md` path와 case-specific instruction을 주입하지 않는다.
- [x] `make eval-plugin-real`을 추가한다.

## Phase 3: Grader 보수화

- [x] dddjango positive trigger에 주던 자동 점수 보너스를 제거한다.
- [x] `items/meta`, migration verification, Result Type, query-pattern-first 규칙을 단순 단어 탐지보다 구조적으로 검증한다.
- [x] API/DB/TDD별 구조 검증 규칙을 더 넓힌다.

## Phase 4: 실사용성 평가 확대

- [ ] `real-repo` fixture를 최소 12개로 확대한다.
- [ ] diff 적용, `manage.py check`, pytest 결과를 HTML report 상단 gate로 노출한다.
- [ ] 실패 케이스 10개 이상은 수동 리뷰 notes를 작성한다.

## Phase 5: Gate 재정의

- [x] high-baseline suite에는 +15% lift gate 대신 absolute conformance gate를 적용한다.
- [x] `make eval-conformance`, `make eval-plugin-real`, `make eval-release-gate`가 동일한 conformance release gate를 확인하도록 연결한다.
- [ ] `make release` 자체에 full `plugin-real` 재평가를 강제할지 결정한다. 현재는 릴리즈 시간을 과도하게 늘리지 않기 위해 별도 gate 명령으로 둔다.
- [ ] Claude 평가는 결제 또는 API key 준비 후 같은 목적 체계로 추가한다.

## Phase 6: 평가 운영 자동화

- [x] 긴 평가 중 현재 variant/case 진행률을 stdout에 즉시 출력한다.
- [x] 이전 conformance 실패 케이스에서 residual JSONL suite를 자동 생성한다.
- [x] `make eval-residual`로 실패 케이스만 재측정하고, 실패가 없으면 no-op 처리한다.
- [x] `make eval-release-gate`로 생성된 평가 결과의 gate를 CLI에서도 확인한다.
- [x] residual run artifacts를 gitignore에 추가한다.
- [ ] 전체 `v0.1.9` plugin-real 60-run 재평가를 장시간 실행 가능한 시점에 다시 수행한다.
- [ ] 반복 평가 결과를 버전별 trend report로 누적한다.

## Current Decision

현재까지의 dddjango 점수는 스킬 유효성 신호로는 참고하되, 최종 배포 성능 판단은 보정된 `plugin-real` 평가 이후에 한다.

## 2026-05-05 Targeted Fix Result

- 범위: `trigger-negative-rust-function`, `trigger-positive-migration-transaction`, `trigger-positive-ninja-error-standard`, `trigger-positive-ninja-test-client`, `trigger-ambiguous-api-structure`, `trigger-ambiguous-service-layer`.
- 원인: 로컬 `dddjango` skill-unit trigger 평가가 positive/ambiguous 케이스에도 스킬 경로를 주입하지 않아, 스킬 수정이 타깃 재측정에 반영되지 않았다.
- 조치: `run_prompts.py`에서 negative trigger만 격리하고, positive/ambiguous/conflict trigger는 case metadata 기반 관련 스킬을 읽도록 수정했다.
- 스킬 보강: migration은 조회 패턴 우선, Ninja 에러 표준은 RFC 9457 Problem Details와 `items/meta` envelope, ambiguous service layer는 맥락/가정 고지를 metadata와 초반 규칙에 반영했다.
- 결과: targeted local conformance `100.00`, required rule pass rate `100.00`, critical violations `0`, forbidden patterns `0`.

## 2026-05-05 Local Conformance Rerun Result

- Command: `make eval-conformance`
- Report: `workspace/codex-eval/conformance-rerun-1/report.html`
- Scope: 5 conformance-rerun cases, `baseline` vs local `dddjango` skill-unit.
- Execution: all 10 Codex runs returned `0`.
- Baseline conformance: `87.22`
- dddjango conformance: `100.00`
- Delta: `+12.78`
- dddjango required rule pass rate: `100.00`
- Critical violations: `0`
- Forbidden patterns: `0`
- Release gate: PASS
- Runtime: baseline avg `38.77s` / total `193.87s`; dddjango avg `73.74s` / total `368.71s`.

## 2026-05-05 Published Codex Plugin Real Result

- Release: `v0.1.8`
- Install source: `codex plugin marketplace add changja88/dddjango --ref v0.1.8`
- Installed cache verified: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.8`
- Command: `make eval-plugin-real`
- Report: `workspace/codex-eval/plugin-real-1/report.html`
- Scope: 30 trigger cases, `baseline` vs installed `dddjango-plugin`.
- Execution: all 60 Codex runs returned `0`.
- Baseline conformance: `83.72`
- dddjango-plugin conformance: `96.00`
- Delta: `+12.28`
- dddjango-plugin required rule pass rate: `96.00`
- Critical violations: `0`
- Forbidden patterns: `0`
- Release gate: PASS
- Trigger pass:
  - positive: `10/10`
  - negative: `10/10`
  - ambiguous: `6/6`
  - conflict: `4/4`
- Runtime: baseline avg `26.34s` / total `790.32s`; dddjango-plugin avg `64.43s` / total `1932.85s`.
- Residual follow-up:
  - `trigger-negative-data-analysis`: trigger는 통과했지만 `관련 스킬 참조`에 `dddjango:implementation-python`이 붙어 strict `no_django_contamination` conformance rule에서 실패했다.
  - `trigger-positive-ninja-error-standard`: Problem Details와 `items/meta`는 포함했지만 `Schema` 탐지 규칙 하나가 미통과했다.

## 2026-05-05 Residual Local Fix Result

- 범위: published plugin-real `v0.1.8`에서 남은 두 잔여 케이스의 local skill-unit 재측정.
- 수정:
  - `implementation-python`: pandas/CSV/일반 스크립트/데이터 분석처럼 명확히 비-Django Python 작업이면 Django/DDD/dddjango 언급과 `dddjango:` 접두 관련 스킬 참조를 금지했다.
  - `implementation-django-ninja`: 공통 에러 표준 산출물에 `ProblemDetail(Schema)`, `Router`, `@router.get/post`, `api.add_router()`, `response={...: ProblemDetail}`, `application/problem+json`, `items/meta`를 모두 포함하도록 low-freedom rule을 보강했다.
- Command:
  - `python3 evals/codex/scripts/run_prompts.py --iteration workspace/codex-eval/targeted-residual-1 --variant dddjango --case trigger-negative-data-analysis --keep-going`
  - `python3 evals/codex/scripts/run_prompts.py --iteration workspace/codex-eval/targeted-residual-1 --variant dddjango --case trigger-positive-ninja-error-standard --keep-going`
  - `python3 evals/codex/scripts/grade_conformance.py workspace/codex-eval/targeted-residual-1`
- Result: local targeted conformance `100.00`, required rule pass rate `100.00`, critical violations `0`, forbidden patterns `0`.
- Note: public Codex plugin에 반영하려면 다음 patch release 후 `plugin-real` 재측정이 필요하다.

## 2026-05-05 Published Residual Plugin Real Result

- Release: `v0.1.9`
- Install source: `codex plugin marketplace add changja88/dddjango --ref v0.1.9`
- Installed cache verified: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.9`
- Scope: `v0.1.8`에서 실패했던 두 잔여 케이스만 installed `dddjango-plugin`으로 재측정.
- Cases:
  - `trigger-negative-data-analysis`
  - `trigger-positive-ninja-error-standard`
- Result: installed plugin targeted conformance `100.00`, required rule pass rate `100.00`, critical violations `0`, forbidden patterns `0`.
- Full `make eval-plugin-real` note: 전체 60-run 재평가는 첫 baseline 구간이 과도하게 지연되어 중단했다. 이번 릴리즈 변경 검증은 잔여 실패를 직접 겨냥한 targeted plugin-real 결과로 판단한다.

## 2026-05-06 Evaluation Automation Result

- Added progress logging to `run_prompts.py`:
  - run start: variant, case count, iteration path
  - case start: `[n/total] variant/case: start`
  - case end: return code and duration
  - timeout: timeout seconds and elapsed duration
- Added residual automation:
  - `evals/codex/scripts/build_residual_cases.py`
  - `evals/codex/scripts/run_residual_eval.py`
  - `make eval-residual`
- Added gate automation:
  - `evals/codex/scripts/check_release_gate.py`
  - `make eval-release-gate`
- Expanded structural conformance rules:
  - API: explicit status/response mapping
  - DB: measurement plan such as EXPLAIN, query count, or `QuerySet.explain()`
  - TDD: test structure markers such as Arrange/Act/Assert, fixture, or test client
- Current recommendation:
  - small skill fix: `make eval-residual` first
  - local conformance: `make eval-conformance`
  - installed Codex plugin: `make eval-plugin-real`
  - release decision: `make eval-release-gate`

## 2026-05-06 Documentation Cleanup

- Removed raw evaluation artifacts from Git and kept only summarized results.
- Moved this document from `docs/superpowers/plans/` to `docs/evaluation/`.
- Removed older implementation-plan logs that no longer matched the current
  Makefile and evaluation workflow.
