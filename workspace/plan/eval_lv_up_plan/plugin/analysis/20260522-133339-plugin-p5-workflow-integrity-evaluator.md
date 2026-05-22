수정 대상: evaluator
원인 분류: evaluator

# P5 plugin workflow trace evaluator 분석

## 문제

현재 subagent trace artifact 생성과 `workflow_execution_expectation` hard gate는 `workflow` bucket에만 연결되어 있다. P5 plugin-level case를 `plugin` bucket에 추가하더라도 runner와 evaluator가 plugin run에서 subagent trace를 생성하거나 실행 모드 gate를 적용하지 않으면, 실제 subagent 실행/미실행 claim과 `wait_agent` 또는 `close_agent` result collection evidence를 구조적으로 검증할 수 없다.

## 영향

plugin answer oracle이 trace/result collection을 요구해도 실제 판정은 모델 evaluator의 자연어 판단에만 의존한다. 이는 pending subagent를 completed result로 주장하거나 trace 없는 actual delegation claim을 놓치는 evaluator undercheck가 된다.

## 수정 방향

- `run_eval_bucket.py`가 `workflow`뿐 아니라 `plugin` bucket에서도 subagent trace marker와 case별 trace artifact를 생성하게 한다.
- `evaluate_eval_run.py`가 answer oracle에 `workflow_execution_expectation`이 있으면 bucket과 무관하게 trace artifact를 evaluator prompt에 포함하고 hard gate를 적용하게 한다.
- `validate_eval_run.py`가 `workflow_execution_expectation`이 있는 run에서는 plugin bucket도 trace schema와 workflow execution gate를 검증하게 한다.
- `validate_eval_bucket_pack.py`는 `plugin` answer oracle에 `workflow_execution_expectation`이 있을 경우 동일 schema를 검증한다.
- P5 targeted run의 Test sidecar가 지적한 aggregate trace gap을 닫기 위해 `spawn_agent`로 생성된 agent id와 `wait`/`close`로 수집된 agent id를 비교한다.
- `p5-workflow-integrity` coverage tag가 있는 plugin answer는 `workflow_execution_expectation`을 필수로 요구한다.
- 독립 integration review가 지적한 추가 undercheck: P5 workflow integrity와 actual-subagent-required oracle이 `trace_missing`, `trace_not_captured`, `not_run`을 acceptable로 두면 hard gate의 result collection 요구를 우회한다. 해당 mode는 P5 trace/result-collection 증거로 세지 않도록 oracle과 validator를 함께 강화한다.

## 리뷰

리뷰 방식: real-subagent
리뷰 결과: Blocker 1, Major 2, 열린 Minor 0

Subagent 리뷰/순차 fallback: eval bucket 독립 subagent가 P5 plugin-level workflow eval에 actual trace/result collection evidence가 결합되지 않는다고 보고했다.
독립 integration review는 현재 P5 targeted pass run 부재를 Blocker로, missing/not-run trace mode 허용과 과거 pass run의 aggregate-only result-collection 판단을 Major로 분류했다.

skill-creator 리뷰: 해당 없음. 이 문서는 eval runner/evaluator integrity gap 분석이다.
