수정 대상: evaluator

# non-negative expected_delta 검증 계획

## 수정 대상

- `workspace/scripts/validate_eval_run.py`
- `workspace/scripts/test_validate_eval_run.py`

## 절차

1. `validate_expected_outcomes`에서 `expected_delta: non-negative`를 읽는다.
2. baseline과 with-ddjango score가 모두 있으면 with-ddjango score가 baseline보다 낮을 때 finding을 낸다.
3. unit test로 baseline `5 / 5`, with-ddjango `4 / 5`, `expected_delta: non-negative`가 실패하는지 확인한다.
4. 영향을 받은 targeted eval을 다시 실행한다.

## 검증

- `.venv/bin/python -B workspace/scripts/test_validate_eval_run.py`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket code`
- `make eval-one BUCKET=code CASE=case-code-status-migration TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-django-p4 EXTRA_ARGS=--rerun JOBS=1`
- `make eval-one BUCKET=code CASE=case-code-small-rename TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-django-p4 EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- non-negative delta가 실제 점수 역전을 허용하지 않는다.
- 두 affected case의 targeted eval이 current validator로 다시 pass한다.
