수정 대상: answer

# P5/P4 restraint scope response 수정 계획

1. P4 individual-skill negative answer files에 `restraint_scope: individual-skill`을 추가한다.
2. `case-response-false-claim.yaml`에 `restraint_scope: plugin-level`과 `p5-plugin-restraint` tag를 추가한다.
3. `case-response-django-web-one-line-edit.yaml`에 `restraint_scope: plugin-level`과 `p5-plugin-restraint` tag를 추가한다.
4. `workspace/scripts/validate_eval_bucket_pack.py`에 known P4/P5 restraint scope 검사를 추가한다.
5. `workspace/scripts/test_validate_eval_bucket_pack.py`에 scope 누락/오분류 검사를 추가한다.
6. response bucket validator와 수정 case targeted eval을 실행한다.
