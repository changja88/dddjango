수정 대상: evaluator

# P5 source semantic validator 수정 계획

## 수정 범위

- `workspace/scripts/validate_eval_bucket_pack.py`

## 순서

1. source eval-traceability answer validator를 추가한다.
2. target behavior/evidence_required에 per-case path/source/run mapping terms가 있는지 확인한다.
3. source bucket validator와 script test를 실행한다.

## 완료 조건

- source eval traceability case가 bucket-level high-level rule만으로 통과하지 않는다.
