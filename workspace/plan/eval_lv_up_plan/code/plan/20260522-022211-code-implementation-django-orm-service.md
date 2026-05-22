수정 대상: case

# implementation-django code positive coverage 계획

## 수정 대상

- `workspace/develop/eval/code/cases/plugin/public/case-code-django-orm-service.md`
- `workspace/develop/eval/code/answer/case-code-django-orm-service.yaml`
- `workspace/develop/eval/code/cases/plugin/code-capture.json`
- `workspace/scripts/validate_eval_bucket_pack.py`
- `workspace/scripts/test_validate_eval_bucket_pack.py`

## 절차

1. public case는 fixture repo에서 Django model/QuerySet/Manager, selector/service, transaction/on_commit, query-count, cache invalidation 구현을 요구한다.
2. answer oracle은 implementation-django source final, SKILL.md, `models-orm.md`, `services-selectors.md`, `transactions-performance-security.md`를 기준으로 둔다.
3. code capture metadata에 subject repo를 `workspace/develop/eval/code/fixtures/django_shop_service`로 추가한다.
4. validator가 code bucket에서 `code-implementation-django` positive coverage tag를 요구하도록 보강한다.
5. targeted eval을 실행한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket code`
- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
- `make eval-one BUCKET=code CASE=case-code-django-orm-service TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-django-p4 EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- code bucket에 implementation-django positive case가 추가된다.
- public case 누설이 없다.
- answer oracle이 source/runtime reference보다 과도하거나 부족한 요구를 하지 않는다.
- targeted eval이 실행된다.
