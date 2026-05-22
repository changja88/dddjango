수정 대상: case

## 목표

response bucket에 `implementation-django-web` 단일 skill의 P4 direct coverage를 추가한다.

## 수정 순서

1. `workspace/develop/eval/response/cases/plugin/public/case-response-django-web-page.md`를 추가한다.
2. 같은 id의 `workspace/develop/eval/response/answer/case-response-django-web-page.yaml`을 추가한다.
3. answer에는 TemplateView/Generic CBV/FBV, templates/base/includes, static assets, forms, HTMX/CSRF, auth/permission, render acceptance, REST/API/ORM/test-mechanics handoff, validation honesty를 coverage tag와 target behavior로 명시한다.
4. public case에는 oracle field명, private scoring, 이전 run finding을 쓰지 않는다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
- `make eval-one BUCKET=response CASE=case-response-django-web-page TRY_NUMBER=1 SCOPE=targeted TOPIC=django-web-p4 EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- response bucket validator가 direct Django Web coverage를 구조적으로 확인한다.
- targeted eval run id와 status가 inventory에 기록된다.
