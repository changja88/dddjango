수정 대상: evaluator

# source DRF guardrail validator 계획

## 수정 범위

- `workspace/develop/eval/source/eval_goal.md`
- `workspace/develop/eval/source/answer/case-source-provisional-drf.yaml`
- `workspace/scripts/validate_eval_bucket_pack.py`
- `workspace/scripts/test_validate_eval_bucket_pack.py`

## 절차

1. `test_validate_eval_bucket_pack.py`에 source provisional/DRF answer가 guardrail axes를 빠뜨리면 실패하는 regression test를 추가하고 실패를 확인한다.
2. `validate_eval_bucket_pack.py`에 source bucket 전용 semantic validator를 추가한다.
3. `case-source-provisional-drf.yaml` answer oracle에 source/runtime DRF guardrail axes를 보강한다.
4. `source/eval_goal.md` provisional handling wording을 file existence만이 아니라 substantive coverage까지 요구하도록 수정한다.

## 검증

- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket source`
- `make eval-one BUCKET=source CASE=case-source-provisional-drf TRY_NUMBER=1 SCOPE=targeted TOPIC=provisional-status-stale EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- source validator가 DRF guardrail source/runtime axes 누락을 실패시킨다.
- source bucket validator가 현재 answer를 통과시킨다.
- targeted eval 결과 또는 실패 run artifact와 원인 분류를 남긴다.
