수정 대상: case

# implementation-django P4 평가 개선 계획

## 수정 대상

- `workspace/develop/eval/response/cases/plugin/public/case-response-django-orm-service.md`
- `workspace/develop/eval/response/answer/case-response-django-orm-service.yaml`
- `workspace/develop/eval/response/cases/plugin/public/case-response-django-drf-maintenance.md`
- `workspace/develop/eval/response/answer/case-response-django-drf-maintenance.yaml`
- `workspace/develop/eval/response/answer/case-response-operational-migration.yaml`
- `workspace/develop/eval/response/answer/case-response-simple-rename.yaml`
- `workspace/develop/eval/code/answer/case-code-status-migration.yaml`
- `workspace/develop/eval/code/answer/case-code-small-rename.yaml`
- `workspace/scripts/validate_eval_bucket_pack.py`
- `workspace/scripts/test_validate_eval_bucket_pack.py`

## 절차

1. `response` positive public case 2개를 추가하되 public prompt에는 answer schema, oracle, private 기준을 넣지 않는다.
2. answer oracle은 `workspace/reference/implementation-django/reference/final.md`, `dddjango/skills/implementation-django/SKILL.md`, 필요한 bundled reference만 basis로 둔다.
3. 기존 migration/restraint answer의 reference basis와 coverage tag를 implementation-django 목적에 맞게 보강한다.
4. evaluator에 implementation-django P4 coverage tag set과 answer validator를 추가한다.
5. validator unit test를 추가해 coverage gap과 reference basis 누락을 실패로 만든다.
6. 관련 validator와 targeted eval을 실행한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket code`
- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
- targeted eval:
  - `make eval-one BUCKET=response CASE=case-response-django-orm-service TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-django-p4 EXTRA_ARGS=--rerun JOBS=1`
  - `make eval-one BUCKET=response CASE=case-response-django-drf-maintenance TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-django-p4 EXTRA_ARGS=--rerun JOBS=1`
  - `make eval-one BUCKET=response CASE=case-response-operational-migration TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-django-p4 EXTRA_ARGS=--rerun JOBS=1`
  - `make eval-one BUCKET=response CASE=case-response-simple-rename TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-django-p4 EXTRA_ARGS=--rerun JOBS=1`
  - `make eval-one BUCKET=code CASE=case-code-status-migration TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-django-p4 EXTRA_ARGS=--rerun JOBS=1`
  - `make eval-one BUCKET=code CASE=case-code-small-rename TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-django-p4 EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- implementation-django positive/negative coverage가 source reference와 runtime bundled reference에 trace된다.
- public case에 oracle/schema/private finding 누설이 없다.
- response/code bucket validator가 통과한다.
- 수정한 모든 case의 targeted eval이 실행된다.
- independent review 후 Blocker 0, Major 0, 열린 Minor 0 상태다.
