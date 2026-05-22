수정 대상: case
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

# workflow validation sharing P4 분석

## 배경

`workflow-dddjango-subagents` P4 기준은 역할 분해, 책임 분배, handoff, critical path와 sidecar 구분, 실제 subagent 승인, sequential fallback, trace 정직성뿐 아니라 validation sharing을 개별 skill 목적 수준에서 검증해야 한다.

현재 workflow bucket은 `dddjango Checks`, result collection evidence, risky write test criteria, validation honesty를 이미 다루지만, public case와 answer oracle이 "역할별 검증 책임을 어떻게 나누고 통합에 넘기는가"를 명시적으로 요구하는 축은 약하다.

## 현재 증거

- `workspace/develop/eval/workflow/eval_goal.md`는 handoff field와 integration closure를 다루지만 validation sharing을 별도 case family 또는 minimum check로 명시하지 않는다.
- `case-workflow-parallel-ownership`은 실제 parallel subagent 사용, disjoint write ownership, result collection, integration owner를 검증하므로 validation sharing을 추가하기에 가장 좁은 case다.
- source/runtime reference는 `handoff-contract.md`의 `dddjango Checks`, `delegation-rules.md`의 validation expectations, `integration-checklist.md`의 Tests and verification 및 Validation Honesty를 기준으로 삼을 수 있다.

## 판단

coverage 부족 원인은 evaluator나 skill 기준 부족이 아니라 case prompt와 answer oracle이 validation sharing을 암묵적으로만 요구하는 데 있다. Public case에는 "각 역할이 맡을 검증 책임과 실행/미실행 검증을 통합에 넘기는 방식"을 제품 수준 표현으로 추가하고, answer oracle은 reference보다 과하지 않게 handoff validation expectations와 integration closure를 요구한다.

## 영향 범위

- 수정 대상 bucket: `workflow`
- 수정 case id: `case-workflow-parallel-ownership`
- targeted eval 필요: public case와 answer oracle이 수정되므로 필요
- validator 필요: `validate_eval_bucket_pack.py --bucket workflow`

## 리뷰 방식

리뷰 방식: not-run

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
