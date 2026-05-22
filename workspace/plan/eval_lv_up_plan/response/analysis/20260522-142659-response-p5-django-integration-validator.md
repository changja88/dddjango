수정 대상: evaluator
원인 분류: evaluator

# response P5 Django integration validator 분석

## 문제

P5 integration review에서 `case-response-django-implementation-handoff` answer oracle은 API/Ninja, DB/Django, Web/Python, Clean Code, TDD/Test 책임 경계를 요구하지만, response bucket validator는 P4 direct coverage 위주로만 확인하고 response P5 boundary matrix를 deterministic하게 강제하지 않는다고 지적했다.

## 영향

`p5-django-implementation-integration` tag가 있는 response case가 구조적으로 얕아져도 bucket pack validation이 통과할 수 있다. 그러면 P4 direct case를 P5 완료 근거로 잘못 세는 evaluator undercheck가 남는다.

## 조치 방향

- response P5 Django implementation integration helper를 추가한다.
- `case-response-django-implementation-handoff`가 필수 P5 tags, source/runtime reference basis, target_behavior boundary matrix를 유지하는지 검사한다.
- response bucket coverage에도 P5 integration case 존재를 별도 요구한다.
- unit test는 fragmented tag-only answer를 reject하고 full boundary matrix answer를 accept하도록 둔다.

## 리뷰

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

Subagent 리뷰/순차 fallback: `Noether` subagent가 response P5 integration evaluator undercheck를 Major로 보고했다.

skill-creator 리뷰: 해당 없음. 이 문서는 eval bucket validator 보강 분석이다.
