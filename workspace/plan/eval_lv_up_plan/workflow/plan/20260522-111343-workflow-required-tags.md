수정 대상: evaluator

# workflow required coverage tags P4 계획

## 수정 순서

1. `workspace/scripts/validate_eval_bucket_pack.py`의 workflow required coverage tag set에 P4 누락 tag를 추가한다.
2. workflow bucket validator로 현재 13개 case가 required set을 만족하는지 확인한다.
3. `test_validate_eval_bucket_pack.py`로 validator regression을 확인한다.

## 완료 조건

- workflow bucket validator가 통과한다.
- required tag set이 `workspace/develop/eval/workflow/eval_goal.md`의 P4 coverage 축과 모순되지 않는다.
