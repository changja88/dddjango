수정 대상: case

# implementation-python response 리뷰 후속 계획

## 수정 대상

- `workspace/develop/eval/response/cases/plugin/public/case-response-python-boundaries.md`
- `workspace/scripts/validate_eval_bucket_pack.py`
- `workspace/scripts/test_validate_eval_bucket_pack.py`

## 절차

1. public prompt에 `TypedDict`가 자연스러운 lightweight external JSON shape 판단을 추가한다.
2. public prompt에 `TypeIs`/`TypeGuard` 또는 ordinary `None` check 판단을 요구하는 custom predicate/narrowing 상황을 추가한다.
3. direct implementation-python coverage validator가 mixed/workflow/subagent/role-map tag를 가진 answer를 direct coverage로 인정하지 않게 한다.
4. unit test를 추가해 P5-adjacent tag regression을 잡는다.
5. response bucket validator와 targeted eval `case-response-python-boundaries`를 재실행한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
- `make eval-one BUCKET=response CASE=case-response-python-boundaries TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-python-p4 EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- public case와 answer oracle이 같은 implementation-python 목적을 검증한다.
- direct coverage validator가 P5/mixed case를 direct P4 coverage로 세지 않는다.
- targeted eval에서 required dimensions 누락 없이 pass한다.
