수정 대상: evaluator

## 목표

response bucket validator가 `implementation-django-web` direct P4 coverage 부재를 놓치지 않게 한다.

## 수정 순서

1. `workspace/scripts/validate_eval_bucket_pack.py`에 Django Web response P4 coverage tag set을 추가한다.
2. direct coverage 판정은 `case-response-django-web-` prefix, `implementation-django-web` coverage tag, source reference, SKILL.md, bundled reference path를 함께 요구한다.
3. answer별 validator에 `validate_implementation_django_web_answer`를 연결한다.
4. 기존 mixed-boundary `case-response-web-typing`은 P5 또는 mixed-routing 보조 case로 유지하되 direct coverage로 계산하지 않는다.
5. validator unit test에 direct web coverage 누락/충족 사례를 추가한다.

## 검증

- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`

## 완료 조건

- direct Django Web answer가 없으면 response bucket validator가 실패한다.
- 새 direct case와 answer가 있으면 validator가 통과한다.
