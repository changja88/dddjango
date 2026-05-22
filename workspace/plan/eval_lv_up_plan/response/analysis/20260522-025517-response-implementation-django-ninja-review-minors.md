수정 대상: evaluator

# implementation-django-ninja P4 fresh review Minor 분석

## 배경

fresh subagent review 2건을 수거했다.

리뷰 방식: real-subagent
리뷰 결과: Blocker 1, Major 0, 열린 Minor 2

- skill-creator 관점: Blocker 1, Major 0, Minor 1
- 독립 review 관점: Blocker 1, Major 0, Minor 1

공통 Blocker는 두 targeted eval pass evidence 부재이며, 원인은 `sandbox/authorization`이다. 이 Blocker는 agent가 case/answer/evaluator 수정으로 닫을 수 없다.

## Minor 1: DRF answer reference_basis 경로가 과하게 넓음

`case-response-drf-ninja.yaml`의 `reference_basis`에 `workspace/develop/eval` 디렉터리 전체가 들어 있다. 이 answer는 이미 bucket eval goal, implementation-django-ninja source final, runtime SKILL.md, bundled references, source-reference-audit source/runtime basis를 구체적으로 갖고 있으므로 broad directory path는 traceability를 약하게 만든다.

분류: `answer`

## Minor 2: direct implementation-django-ninja coverage gate가 case id shape를 확인하지 않음

`has_implementation_django_ninja_direct_coverage()`는 full P4 tag set과 source/runtime/bundled reference를 요구하지만, Django Web/Python direct coverage gate처럼 case id shape를 제한하지 않는다. 현재 direct case는 `case-response-django-ninja-endpoint`라서 실제 pack은 통과 가능하지만, unrelated response answer가 우연히 full tag/ref set을 가지면 direct coverage로 오인될 수 있다.

분류: `evaluator`

## 수정 방향

- DRF answer의 broad `workspace/develop/eval` reference basis를 제거한다.
- direct Django Ninja coverage gate에 `case-response-django-ninja-` prefix 조건을 추가한다.
- prefix 조건이 없으면 unrelated case가 direct coverage로 인정되지 않는 regression test를 추가한다.

## targeted eval 상태

이 수정 뒤에도 두 targeted eval은 pass evidence가 없다. 승인 거부 이후 같은 unsandboxed targeted eval 요청을 반복하지 않는다.
