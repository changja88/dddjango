수정 대상: evaluator
원인 분류: evaluator

# architecture-ddd P4 expected outcome 검증 분석

## 문제

`case-response-ddd-subscription-boundary`의 answer oracle은 `expected_outcomes.baseline: partial`, `expected_delta: positive`, `baseline_pass_ok: false`를 선언했지만, targeted run의 answer-oracle evaluation은 baseline과 with-dddjango를 모두 `5 / 5`, `pass`로 평가했다. 그런데 `validate_eval_run.py`는 이 충돌을 실패로 처리하지 않고 run을 통과시켰다.

이는 case/answer/evaluator가 같은 목적을 검증해야 한다는 P4 기준과 어긋난다. 평가 case가 baseline도 통과 가능한 direct DDD 설계 검증이라면 answer의 expected outcome을 그에 맞게 써야 하고, uplift를 기대하는 case라면 validator가 실제 평가 결과와 expected outcome 충돌을 잡아야 한다.

## 영향

- non-discriminating case가 `baseline_pass_ok: false`로 남아도 성공 run처럼 보일 수 있다.
- answer oracle의 expected outcome이 실제 oracle evaluation과 충돌해도 validation manifest가 실패하지 않는다.
- P4 종료 조건인 answer over/under-claim 없음과 review Major 0을 증명할 수 없다.

## 수정 방향

- `validate_eval_run.py`가 answer의 `expected_outcomes`와 answer-oracle evaluation 결과를 비교한다.
- `baseline_pass_ok: false`인데 baseline verdict가 pass이면 실패한다.
- `expected_delta: positive`인데 with-ddjango score가 baseline score보다 높지 않으면 실패한다.
- architecture-ddd direct response와 code smoke/regression case는 실제 run 결과에 맞춰 baseline pass를 허용하도록 expected outcome을 정정한다.

## 리뷰 방식

리뷰 방식: real-subagent

skill-creator 관점 최종 리뷰에서 Major로 지적된 validation integrity 문제를 근거로 수정한다.

리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

