수정 대상: evaluator

# plugin targeted eval prompt-input validator 계획

## 수정 범위

- 수정: `workspace/scripts/validate_eval_run.py`
- 수정: `workspace/scripts/test_validate_eval_run.py`

## 절차

1. 현재 실패한 prompt-input artifact shape을 기준으로 회귀 테스트를 먼저 추가한다.
2. 실패를 확인한 뒤 prompt-input artifact 검증만 JSON object 또는 JSON array를 허용하도록 고친다.
3. `load_json_object`를 사용하는 oracle/trace/schema 검증은 변경하지 않는다.
4. `test_validate_eval_run.py`와 필수 공통 validator를 실행한다.
5. 실패했던 plugin targeted run을 다시 `validate_eval_run.py` 또는 `make eval-one`으로 확인한다.

## 검증

- `.venv/bin/python -B workspace/scripts/test_validate_eval_run.py`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `make eval-one BUCKET=plugin CASE=case-plugin-provisional-overclaim TRY_NUMBER=1 SCOPE=targeted TOPIC=source-status-stale EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- prompt-input debug output이 JSON array일 때도 run validation이 통과한다.
- JSON missing/empty/invalid/scalar artifact는 계속 실패한다.
- plugin targeted eval이 artifact validation까지 통과한다.
