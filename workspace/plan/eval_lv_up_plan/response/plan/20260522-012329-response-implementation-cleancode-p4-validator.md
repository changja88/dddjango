수정 대상: evaluator

# implementation-cleancode P4 evaluator 수정 계획

## 범위

- `workspace/scripts/validate_eval_bucket_pack.py`
- `workspace/scripts/test_validate_eval_bucket_pack.py`

## 작업

1. `validate_eval_bucket_pack.py`에 `RESPONSE_IMPLEMENTATION_CLEANCODE_P4_COVERAGE_TAGS` 상수를 추가한다.
2. response bucket coverage validation에서 해당 tag 집합을 observed coverage와 비교한다.
3. 누락 메시지는 기존 P4 validator 패턴과 맞춰 `response: implementation-cleancode P4 coverage_tags missing: ...`로 둔다.
4. validator test에 clean-code P4 tag 중 하나를 의도적으로 누락한 fixture를 만들고 failure를 확인한다.

## 검증

- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
