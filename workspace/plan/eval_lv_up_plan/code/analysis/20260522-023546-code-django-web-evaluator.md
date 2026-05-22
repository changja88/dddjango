수정 대상: evaluator
원인 분류: evaluator

## 배경

code bucket validator는 bucket-level required tag로 `django-web` 존재만 확인하고, direct `implementation-django-web` code-backed case가 source/reference/runtime 기준을 갖췄는지 확인하지 않는다.

## 문제

- `case-code-web-detail` answer가 잘못된 reference basis를 가져도 validator가 잡지 못한다.
- Django Web code case에서 display fallback, template/static/render acceptance 기준을 target behavior에 담았는지 구조적으로 확인하지 않는다.

## 수정 방향

- code bucket용 Django Web P4 coverage tag set을 추가한다.
- `implementation-django-web` answer validator를 response/code 공통으로 사용하되, code case에서는 source final, SKILL.md, bundled references, 핵심 target terms를 요구한다.
- unit test로 잘못된 reference basis와 누락된 direct coverage를 확인한다.

## 리뷰 기록

리뷰 방식: not-run
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

Subagent 리뷰/순차 fallback: 수정 후 reviewer로 확인한다.
