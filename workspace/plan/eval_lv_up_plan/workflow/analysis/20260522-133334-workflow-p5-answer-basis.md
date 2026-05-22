수정 대상: answer
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 2, 열린 Minor 0

# workflow P5 answer basis 분석

## 배경

P5 composite/risky-write 평가에서는 workflow case가 단일 skill 품질이 아니라 역할 분해, handoff, integration owner, 실제 subagent 실행 정직성, risky write consistency를 함께 검증해야 한다.

## 현재 증거

- `case-workflow-parallel-ownership`은 실제 병렬 subagent 사용을 요구하면서도 subagent trace capture 불가, missing trace, not-run을 acceptable mode로 둔다. 그러나 `expected_outcomes.with_dddjango`는 `pass`만 허용해, 명시적 runtime 제한을 `pass-limited`로 평가할 수 없다.
- `case-workflow-positive-composite`는 Handoff Contract, Integration Checklist, Risky Write Consistency Block을 요구하지만 `reference_basis`가 `role-map.md` 중심이고 `handoff-contract.md`, `integration-checklist.md`, `delegation-rules.md`를 직접 근거로 들지 않는다.
- 같은 flagship case의 `coverage_tags`가 risky-write, responsibility split, delegation honesty, integration closure를 직접 표시하지 않아 P5 integration coverage가 좁게 보인다.

## 원인 분류

원인 분류는 `answer`다. Public case 자체는 P5 흐름을 유도하지만 answer oracle의 expected outcome과 reference basis가 runtime 제한 및 owning reference를 충분히 표현하지 못한다.

## 수정 판단

- `case-workflow-parallel-ownership`은 명시적 runtime 제한이 있는 경우 `pass-limited`를 허용하도록 `expected_outcomes.with_dddjango`를 `pass-or-pass-limited`로 낮추고, scoring text도 `partial` 대신 `pass-limited`로 맞춘다.
- `case-workflow-positive-composite`는 owning workflow references를 직접 추가하고 P5 integration tags를 보강한다.

## Subagent 리뷰/순차 fallback

Subagent 리뷰: real-subagent. skill-creator 관점 sidecar가 answer overclaim과 positive composite basis 부족을 Major로 보고했고, 메인 판단도 이를 채택한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket workflow`
- 수정 case targeted eval:
  - `make eval-one BUCKET=workflow CASE=case-workflow-parallel-ownership TRY_NUMBER=1 SCOPE=targeted TOPIC=workflow-p5-answer-basis EXTRA_ARGS=--rerun JOBS=1`
  - `make eval-one BUCKET=workflow CASE=case-workflow-positive-composite TRY_NUMBER=1 SCOPE=targeted TOPIC=workflow-p5-answer-basis EXTRA_ARGS=--rerun JOBS=1`
