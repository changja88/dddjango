수정 대상: evaluator

# implementation-python direct coverage P5 tag exclusion 계획

## 수정 대상

- `workspace/scripts/validate_eval_bucket_pack.py`
- `workspace/scripts/test_validate_eval_bucket_pack.py`

## 절차

1. direct implementation-python coverage excluded tag set에 `role-map-sync`, `subagent-opt-out`, delegation/handoff/integration tags를 추가한다.
2. response direct coverage test에 `role-map-sync`와 `subagent-opt-out` rejection을 추가한다.
3. bucket validator와 unit test를 실행한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`

## 완료 조건

- P5/mixed/workflow adjacent tags가 implementation-python direct P4 coverage로 계산되지 않는다.
