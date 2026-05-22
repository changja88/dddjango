수정 대상: answer

# code fat-model clean-code basis 수정 계획

## 범위

- `workspace/develop/eval/code/answer/case-code-fat-model.yaml`

## 작업

1. `reference_basis`에서 broad `workspace/develop/eval` 항목을 제거한다.
2. clean-code source/runtime/bundled reference basis를 추가한다.
3. 기존 target behavior와 scoring은 유지한다. 이 case는 code bucket implementation-supporting case이므로 public case나 fixture는 바꾸지 않는다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket code`
- 필요 시 `make eval-one BUCKET=code CASE=case-code-fat-model TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-cleancode-p4 EXTRA_ARGS=--rerun JOBS=1`
