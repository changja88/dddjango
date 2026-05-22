수정 대상: answer

# status migration expected outcome 수정 계획

## 수정 대상

- `workspace/develop/eval/code/answer/case-code-status-migration.yaml`

## 절차

1. `expected_outcomes.baseline`을 `pass-or-partial`로 조정한다.
2. `expected_outcomes.with_dddjango`를 `pass-or-pass-limited`로 조정한다.
3. `expected_outcomes.expected_delta`를 `non-negative`로 조정한다.
4. `expected_outcomes.baseline_pass_ok`를 `true`로 조정한다.
5. code bucket validator와 targeted eval을 다시 실행한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket code`
- `make eval-one BUCKET=code CASE=case-code-status-migration TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-django-p4 EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- answer oracle이 reference보다 과도한 positive delta를 요구하지 않는다.
- targeted eval이 pass한다.
