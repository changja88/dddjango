수정 대상: evaluator
리뷰 방식: real-subagent
리뷰 결과: Blocker 1, Major 2, 열린 Minor 0

# workflow P5 combined evaluator 분석

## 배경

P5 workflow 평가는 direct risky-write 조언 조각이 아니라 role decomposition, handoff, integration owner, risky-write consistency가 한 case 안에서 함께 검증되는지 보장해야 한다.

## 현재 증거

- workflow bucket 전체 required tags는 존재하지만 tag가 여러 case에 흩어져 있어도 validator가 통과한다.
- `case-workflow-risky-write`는 현재 direct mode를 허용해 P4 DB/API/Test risky-write direct 평가와 중복될 수 있다.
- `workflow_execution_gate.py`는 실행 mode alignment만 보며 handoff quality 자체는 LLM oracle 평가에 맡긴다. 따라서 bucket pack validator가 최소 하나의 combined P5 oracle shape를 구조적으로 요구해야 한다.

## 원인 분류

원인 분류는 `evaluator`다. Case와 answer를 보강해도 나중에 combined P5 tag/reference/expectation이 분리되거나 사라지는 회귀를 structural validator가 막지 못한다.

## 수정 판단

`validate_eval_bucket_pack.py`에 workflow 전용 combined P5 guard를 추가한다. 최소 하나의 answer가 다음을 동시에 만족해야 한다.

- `risky-write-consistency`, `handoff-contract`, `responsibility-split`, `integration-closure` coverage tag 보유
- `workflow_execution_expectation`이 `direct`를 acceptable mode로 허용하지 않음
- `target_behavior.required`에 aggregate invariant, transaction owner, locking/isolation, uniqueness/idempotency storage, `Idempotency-Key`, side-effect timing, retry/isolation, concurrency/integration test, integration owner 또는 handoff closure를 포함
- workflow owning references인 role map, handoff contract, integration checklist를 reference basis에 포함

## Subagent 리뷰/순차 fallback

Subagent 리뷰: real-subagent. 독립 workflow review sidecar가 combined P5 scenario 부재와 validator undercheck를 Blocker/Major로 보고했고, 메인 판단도 이를 채택한다.

## 검증

- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket workflow`
- 수정 case targeted eval:
  - `make eval-one BUCKET=workflow CASE=case-workflow-risky-write TRY_NUMBER=1 SCOPE=targeted TOPIC=workflow-p5-combined-risky-write EXTRA_ARGS=--rerun JOBS=1`
