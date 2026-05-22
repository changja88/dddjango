수정 대상: evaluator
원인 분류: evaluator

## 배경

`validate_eval_bucket_pack.py`는 architecture-api, architecture-db, implementation-django, implementation-django-ninja 등 일부 P4 coverage를 coverage tag로 강제하지만, `implementation-django-web` direct coverage gate는 없다.

## 문제

- response bucket에 `django-web` tag가 하나 있어도 mixed-boundary case만으로 validator가 통과할 수 있다.
- answer가 source reference와 bundled web reference를 실제로 인용하는지 구조적으로 확인하지 않는다.
- TemplateView/CBV/FBV, forms, HTMX/CSRF, auth/permission, render acceptance 같은 direct web 기준이 누락되어도 evaluator가 발견하지 못한다.

## 수정 방향

- `RESPONSE_IMPLEMENTATION_DJANGO_WEB_P4_COVERAGE_TAGS`와 direct coverage 판정 함수를 추가한다.
- `implementation-django-web` answer 검증에서 source reference, SKILL.md, bundled references 중 하나 이상을 요구한다.
- target behavior의 required 블록이 핵심 web 기준을 모두 포함하는지 확인한다.

## 리뷰 기록

리뷰 방식: not-run
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

Subagent 리뷰/순차 fallback: 수정 후 reviewer로 확인한다.
