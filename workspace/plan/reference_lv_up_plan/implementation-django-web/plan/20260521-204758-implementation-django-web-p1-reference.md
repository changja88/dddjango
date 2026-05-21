# implementation-django-web P1 reference 개선 계획

## 수정 이유

`implementation-django-web`은 Django Web 전용 skill이지만 dedicated source reference가 없다. P1 종료 조건을 만족하려면 TemplateView, templates, base template, component includes, static files, CSS/JS, HTMX, CSRF for AJAX, web forms, view auth/permission, render acceptance checks를 source reference에서 직접 판단할 수 있어야 한다.

## 수정 범위

- 생성: `workspace/reference/implementation-django-web/reference/final.md`
- 유지: `workspace/reference/implementation-django/reference/final.md`는 fallback 근거로만 참조하고 수정하지 않는다.
- 기록: `workspace/plan/reference_lv_up_plan/implementation-django-web/analysis/20260521-204758-implementation-django-web-p1-reference.md`

## 수정하지 말아야 할 범위

- `workspace/develop/eval/**` 아래 eval case, answer, evaluator는 수정하지 않는다.
- source reference 문제를 skill 문구만 바꿔서 덮지 않는다.
- REST API, ORM/마이그레이션/트랜잭션, pytest fixture 구현 상세를 Django Web reference가 소유하지 않는다.
- runtime cache sync는 reference 생성 후 별도 `runtime-sync` 분석/계획으로 분류한다.

## 작업 체크리스트

- [x] `workspace/reference/implementation-django-web/reference/final.md`를 생성한다.
- [x] Django Web 책임 범위와 다른 skill로 넘길 handoff 기준을 명시한다.
- [x] TemplateView, templates, base template, includes/components, static CSS/JS, HTMX, CSRF-aware AJAX, web forms, view auth/permission, render acceptance checks 기준을 모두 포함한다.
- [x] optional display value, static asset wiring, render/browser/collectstatic/check --deploy 실행 보고 기준을 source reference에 포함한다.
- [x] 수정 후 reference 충분성을 재평가하고 analysis 문서의 리뷰 결과를 갱신한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- Dedicated source reference가 존재한다.
- P1 기준의 Django Web 판단 축을 source reference만으로 설명할 수 있다.
- source reference와 skill/runtime guidance 사이에 unsupported claim이 남지 않는다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0으로 갱신된다.
