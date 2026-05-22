수정 대상: evaluator

# P5 plugin workflow trace evaluator 계획

## 수정 범위

- 수정: `workspace/scripts/run_eval_bucket.py`
- 수정: `workspace/scripts/evaluate_eval_run.py`
- 수정: `workspace/scripts/validate_eval_run.py`
- 수정: `workspace/scripts/validate_eval_bucket_pack.py`
- 필요 시 수정: 관련 unit test

## 절차

1. trace-enabled bucket을 `workflow`, `plugin`으로 확장한다.
2. plugin bucket에서도 `SUBAGENT_TRACE_CAPTURE.json`과 `raw/<case>-<variant>-subagent-trace.json`을 생성한다.
3. answer oracle에 `workflow_execution_expectation`이 있는 경우 evaluator prompt에 trace artifact를 포함한다.
4. answer oracle에 `workflow_execution_expectation`이 있는 경우 workflow execution hard gate를 bucket과 무관하게 적용한다.
5. run validator도 `workflow_execution_expectation`이 있는 case에서 trace schema와 hard gate를 확인한다.
6. trace extractor가 spawned agent id와 collected agent id를 비교해 일부만 수집된 실행을 `actual_subagent_incomplete`로 분류하게 한다.
7. `p5-workflow-integrity` plugin answer는 `workflow_execution_expectation`이 없으면 bucket validator가 실패하게 한다.
8. P5 actual-subagent trace/integrity case의 `acceptable_modes`에서 `trace_missing`, `trace_not_captured`, `not_run`을 금지한다.
9. unit test와 plugin bucket validator를 실행한다.

## 검증

- `.venv/bin/python -B workspace/scripts/test_validate_eval_run.py`
- `.venv/bin/python -B workspace/scripts/test_run_eval_bucket.py`
- `.venv/bin/python -B workspace/scripts/test_evaluate_eval_run.py`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket plugin`
- 새 plugin P5 case targeted eval pass run

## 완료 조건

- plugin P5 case run artifact에 subagent trace summary가 생성된다.
- trace 없는 actual delegation claim, 일부만 수집된 actual delegation, 또는 forbidden execution mode가 hard gate로 fail된다.
- P5 result-collection case가 missing/not-run trace mode를 pass evidence로 세지 않는다.
- 기존 workflow bucket trace gate 동작은 유지된다.
