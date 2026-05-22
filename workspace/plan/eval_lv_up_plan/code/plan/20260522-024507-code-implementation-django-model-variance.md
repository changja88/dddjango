수정 대상: answer

# implementation-django code expected outcome 수정 계획

## 수정 대상

- `workspace/develop/eval/code/answer/case-code-django-orm-service.yaml`
- `workspace/develop/eval/code/answer/case-code-status-migration.yaml`
- `workspace/scripts/validate_eval_bucket_pack.py`
- `workspace/scripts/test_validate_eval_bucket_pack.py`

## 절차

1. positive implementation answer에서 baseline pass를 허용할 때 `baseline_pass_ok_reason`을 요구하도록 validator를 보강한다.
2. 두 code answer에 model-variance와 command-honesty 기준의 baseline pass 허용 사유를 적는다.
3. positive ORM/service case의 expected delta는 `non-negative`로 맞추고, control/honesty/restraint case는 `variable`로 둔다.
4. code bucket validator와 targeted eval을 다시 실행한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket code`
- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
- `make eval-one BUCKET=code CASE=case-code-django-orm-service TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-django-p4 EXTRA_ARGS=--rerun JOBS=1`
- `make eval-one BUCKET=code CASE=case-code-status-migration TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-django-p4 EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- baseline pass 허용이 무근거로 열려 있지 않다.
- targeted eval이 pass한다.
