수정 대상: answer

# code fat-model expected outcome 수정 계획

## 범위

- `workspace/develop/eval/code/answer/case-code-fat-model.yaml`

## 작업

1. `expected_outcomes.baseline`을 `pass`로 정정한다.
2. `expected_outcomes.expected_delta`를 `neutral`로 정정한다.
3. `expected_outcomes.baseline_pass_ok`를 `true`로 정정한다.
4. with-ddjango expected outcome은 pass 계열 기대를 유지하되, validator가 실제 pass-limited를 허용할 수 있도록 추가 evaluator 변경은 하지 않는다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket code`
- `make eval-one BUCKET=code CASE=case-code-fat-model TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-cleancode-p4 EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- code bucket validator가 통과한다.
- `case-code-fat-model` targeted eval이 expected outcome 충돌 없이 통과한다.
