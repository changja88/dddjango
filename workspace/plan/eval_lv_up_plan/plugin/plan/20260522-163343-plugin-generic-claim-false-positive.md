수정 대상: evaluator

# plugin generic execution claim false positive 수정 계획

## 수정 범위

- `workspace/scripts/validate_eval_run.py`

## 순서

1. generic execution claim detector의 non-claim marker에 evidence result와 eval-only wording을 추가한다.
2. `test_validate_eval_run.py`를 실행한다.
3. plugin targeted run validation을 재실행한다.

## 완료 조건

- required evidence wording과 eval-only leakage wording은 허위 실행 claim으로 오탐되지 않는다.
- 실제 실행 완료 claim은 여전히 event evidence가 없으면 실패한다.
