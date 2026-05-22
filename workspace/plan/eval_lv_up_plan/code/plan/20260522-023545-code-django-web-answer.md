수정 대상: answer

## 목표

`case-code-web-detail` answer oracle이 `implementation-django-web` source reference와 runtime bundled reference를 정확히 기준으로 삼게 한다.

## 수정 순서

1. `workspace/develop/eval/code/answer/case-code-web-detail.yaml`의 `reference_basis`를 source final, SKILL.md, bundled references, code eval goal로 정리한다.
2. `target_behavior.required`에 TemplateView/view context, template/base/include boundary, static reference, render verification honesty를 보강한다.
3. `coverage_tags`에 `implementation-django-web`, `template-context`, `render-acceptance`, `static-reference` 등 direct tag를 추가한다.
4. deterministic behavior check와 allowed paths는 기존 범위를 유지한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket code`
- `make eval-one BUCKET=code CASE=case-code-web-detail TRY_NUMBER=1 SCOPE=targeted TOPIC=django-web-p4 EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- code bucket validator가 answer 구조를 통과시킨다.
- targeted eval run id와 status가 inventory에 기록된다.
