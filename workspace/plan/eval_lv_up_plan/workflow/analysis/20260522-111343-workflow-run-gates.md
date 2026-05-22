수정 대상: evaluator
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 2, 열린 Minor 0

# workflow run gate P4 분석

## 배경

P4 기준은 evaluator가 trace honesty와 answer oracle expectation을 실제 run validation에서 강하게 검증해야 한다. 현재 `evaluate_eval_run.py`는 workflow execution hard gate를 점수 0으로 반영하지만, `validate_eval_run.py`는 gate finding을 evaluator verdict가 `pass`일 때만 실패로 처리한다.

또한 answer oracle의 `expected_outcomes.with_dddjango` 선언을 validate 단계에서 직접 비교하지 않아 `with_dddjango: pass` expectation과 실제 non-pass verdict가 충돌해도 놓칠 수 있다.

## 원인

원인 분류는 `evaluator`다. Case와 answer는 expectation을 선언하지만 run validator가 stale or partial oracle 결과를 충분히 막지 못한다.

## 수정 판단

- workflow execution gate finding은 variant verdict가 `fail` 또는 `blocked`가 아닐 때 validator finding으로 올린다.
- `expected_outcomes.with_dddjango`가 `pass`이면 with-ddjango verdict가 `pass`가 아닐 때 finding을 올리고, `pass-or-pass-limited`이면 `pass` 또는 `pass-limited`만 허용한다.

## 검증

- `.venv/bin/python -B workspace/scripts/test_validate_eval_run.py`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket workflow`
