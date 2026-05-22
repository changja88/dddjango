수정 대상: evaluator

# implementation-django-ninja P4 리뷰 후속 수정 계획

## 목표

implementation-django-ninja P4 response answer/evaluator가 bucket evidence 기준, P5 제외 조건, paired semantic dimensions를 직접 검증하게 한다.

## 작업

1. `case-response-drf-ninja.yaml`의 `evidence_required`를 response bucket goal의 run artifact 기준과 맞춘다.
2. `validate_eval_bucket_pack.py`에 Django Ninja direct coverage exclusion tag set을 추가한다.
3. Django Ninja answer semantic check를 paired dimension 기준으로 강화한다.
4. `test_validate_eval_bucket_pack.py`에 P5 tag exclusion과 paired dimension regression test를 추가한다.
5. plan/eval/skill validators와 response bucket validator/tests를 재실행한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`

## 완료 기준

- repo-side Major/Minor가 닫힌다.
- targeted eval pass run은 여전히 별도 evidence로 필요하며, 없으면 P4 complete가 아니다.
