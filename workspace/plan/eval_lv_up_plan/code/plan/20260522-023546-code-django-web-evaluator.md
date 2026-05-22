수정 대상: evaluator

## 목표

code bucket validator가 Django Web direct P4 coverage와 answer source basis를 구조적으로 검증하게 한다.

## 수정 순서

1. `workspace/scripts/validate_eval_bucket_pack.py`에 code Django Web P4 coverage tag set을 추가한다.
2. `validate_implementation_django_web_answer`를 code answer 검증에도 연결한다.
3. `validate_coverage`에서 code bucket direct Django Web coverage 누락을 실패로 보고한다.
4. `workspace/scripts/test_validate_eval_bucket_pack.py`에 누락/충족 테스트를 추가한다.

## 검증

- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket code`

## 완료 조건

- code bucket에서 direct Django Web coverage가 사라지거나 source basis가 틀리면 validator가 실패한다.
